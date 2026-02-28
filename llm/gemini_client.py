"""Client pour l'API Google Gemini native - Version Sniper 6.0 Hardened."""
import aiohttp
import json
import traceback
from typing import Dict, List, Any, Optional
from loguru import logger

from config.settings import settings

class GeminiClient:
    """Client robuste pour interagir avec l'API Google Gemini nativement."""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or settings.gemini_api_key
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY non configurée")
            
        # SNIPER 7.1 : Gemini 3.1 Pro Preview par défaut pour une précision maximale
        self.default_model = "gemini-3.1-pro-preview"
        logger.debug(f"GeminiClient Sniper 7.1 initialized ({self.default_model})")
        
    async def generate(self, prompt: str, system: str = None, **kwargs) -> str:
        """Génère une réponse texte via Google Gemini REST API."""
        model = kwargs.get("model") or self.default_model
        
        payload = {
            "contents": [{"parts": [{"text": prompt}]}]
        }

        # Support VISION : ajout de l'image si présente
        image_data = kwargs.get("image_data")
        if image_data:
            # Nettoyer le préfixe data:image/...;base64, si présent
            if "," in image_data:
                image_data = image_data.split(",")[1]
            
            payload["contents"][0]["parts"].append({
                "inlineData": {
                    "mimeType": "image/png", # Par défaut PNG, Gemini détecte souvent le reste
                    "data": image_data
                }
            })
        
        if system:
            payload["systemInstruction"] = {"parts": [{"text": system}]}
            
        # Nettoyage des tools pour éviter les conflits d'API
        if "tools" in kwargs:
            payload["tools"] = kwargs["tools"]
            
        gen_config = {}
        if kwargs.get("json_mode"):
            gen_config["responseMimeType"] = "application/json"
            
        if "temperature" in kwargs:
            gen_config["temperature"] = kwargs["temperature"]
        if "max_tokens" in kwargs:
            gen_config["maxOutputTokens"] = kwargs["max_tokens"]
            
        if gen_config:
            payload["generationConfig"] = gen_config

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={self.api_key}"
        logger.debug(f"DEBUG GEMINI URL: {url.replace(self.api_key, 'REDACTED')}")
        timeout = aiohttp.ClientTimeout(total=120) # Timeout à 120s pour les recherches Deep Pro
        
        try:
            # SSL=False est requis car certains environnements (Windows) ont des problèmes de certs
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(url, json=payload, ssl=False) as response:
                    text = await response.text()
                    if response.status != 200:
                        logger.error(f"❌ Gemini Error {response.status}: {text}")
                        raise Exception(f"Erreur API Gemini: {response.status}")
                    data = json.loads(text)
                    return data["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            import traceback
            with open("gemini_crash.txt", "w", encoding="utf-8") as f:
                f.write(f"Exception Type: {type(e)}\n")
                f.write(traceback.format_exc())
            logger.error(f"Gemini generate error: {e}")
            raise e

    async def generate_with_sources(self, prompt: str, system: str = None, **kwargs) -> tuple:
        """Génère une réponse et retourne les sources de grounding (Gemini 2.0)."""
        model = kwargs.get("model", self.default_model)
        
        payload = {
            "contents": [{"parts": [{"text": prompt}]}]
        }
        if system:
            payload["systemInstruction"] = {"parts": [{"text": system}]}
        
        # SNIPER ENFORCEMENT : Toujours utiliser google_search en mode grounding
        payload["tools"] = [{"google_search": {}}]

        gen_config = {}
        # Gemini 3.1 Pro supporte le json_mode avec grounding !
        if kwargs.get("json_mode"):
            gen_config["responseMimeType"] = "application/json"
            
        if "max_tokens" in kwargs:
            gen_config["maxOutputTokens"] = kwargs["max_tokens"]
        if "temperature" in kwargs:
            gen_config["temperature"] = kwargs["temperature"]

        if gen_config:
            payload["generationConfig"] = gen_config

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={self.api_key}"
        timeout = aiohttp.ClientTimeout(total=120) # 120s pour la fusion Search + JSON
        
        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(url, json=payload, ssl=False) as response:
                    text = await response.text()
                    try:
                        data = json.loads(text)
                    except Exception as je:
                        logger.error(f"❌ JSON Parse Error (len={len(text)}): {str(je)[:100]}")
                        # Tentative de récupération partielle si possible ou log pour debug
                        with open("gemini_error_dump.json", "w", encoding="utf-8") as f:
                            f.write(text)
                        raise je
                    
                    # Extraction du texte
                    text_out = ""
                    try: 
                        text_out = data["candidates"][0]["content"]["parts"][0]["text"]
                    except: pass

                    # Extraction OSINT des sources
                    source_urls = []
                    try:
                        grounding = data["candidates"][0].get("groundingMetadata", {})
                        # On ratisse large pour ne rater aucune URL LinkedIn
                        for chunk in grounding.get("groundingChunks", []):
                            uri = chunk.get("web", {}).get("uri")
                            if uri and uri not in source_urls: source_urls.append(uri)
                        
                        for sup in grounding.get("groundingSupport", []):
                            u = sup.get("segment", {}).get("uri") or sup.get("web", {}).get("uri")
                            if u and u not in source_urls: source_urls.append(u)
                    except: pass

                    return text_out, source_urls
        except Exception as e:
            logger.error(f"Gemini Grounding error: {e}")
            raise e

    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Simulation mode chat."""
        model = kwargs.get("model", self.default_model)
        contents = [{"role": "user" if m["role"] == "user" else "model", "parts": [{"text": m["content"]}]} for m in messages if m["role"] != "system"]
        system_text = next((m["content"] for m in messages if m["role"] == "system"), None)
        
        payload = {"contents": contents}
        if system_text:
            payload["systemInstruction"] = {"parts": [{"text": system_text}]}
            
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={self.api_key}"
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, ssl=False) as response:
                data = await response.json()
                return data["candidates"][0]["content"]["parts"][0]["text"]

    async def close(self): pass
