"""Client pour l'API Google Gemini native."""
import aiohttp
import json
from typing import Dict, List, Any, Optional
from loguru import logger

from config.settings import settings

class GeminiClient:
    """Client pour interagir avec l'API Google Gemini nativement."""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or settings.gemini_api_key
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY non configurée")
            
        # Utilisation de Gemini 2.0 Flash (rapide et capable)
        self.default_model = getattr(settings, 'gemini_default_model', 'gemini-2.0-flash')
        
    async def generate(self, prompt: str, system: str = None, **kwargs) -> str:
        """Génère une réponse texte via Google Gemini REST API."""
        model = kwargs.get("model", self.default_model)
        
        payload = {
            "contents": [
                {
                    "parts": [{"text": prompt}]
                }
            ]
        }
        
        if system:
            payload["systemInstruction"] = {
                "parts": [{"text": system}]
            }
            
        if "tools" in kwargs:
            payload["tools"] = kwargs["tools"]
            
        gen_config = {}
        if "temperature" in kwargs:
            gen_config["temperature"] = kwargs["temperature"]
        if "max_tokens" in kwargs:
            gen_config["maxOutputTokens"] = kwargs["max_tokens"]
            
        if gen_config:
            payload["generationConfig"] = gen_config

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={self.api_key}"
        
        timeout = aiohttp.ClientTimeout(total=60)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(url, json=payload) as response:
                if response.status != 200:
                    text = await response.text()
                    logger.error(f"❌ Erreur Gemini {response.status}: {text}")
                    raise Exception(f"Erreur API Gemini: {response.status} - {text}")
                    
                data = await response.json()
                try:
                    return data["candidates"][0]["content"]["parts"][0]["text"]
                except (KeyError, IndexError) as e:
                    logger.error(f"Unexpected response format from Gemini: {data}")
                    raise Exception(f"Format de réponse inattendu: {e}")

    async def generate_with_sources(self, prompt: str, system: str = None, **kwargs) -> tuple:
        """
        Identique à generate(), mais retourne également les URLs sources de Google Grounding.
        Returns: (text: str, sources: List[str])
        """
        model = kwargs.get("model", self.default_model)
        
        payload = {
            "contents": [{"parts": [{"text": prompt}]}]
        }
        if system:
            payload["systemInstruction"] = {"parts": [{"text": system}]}
        if "tools" in kwargs:
            payload["tools"] = kwargs["tools"]

        gen_config = {}
        if "temperature" in kwargs:
            gen_config["temperature"] = kwargs["temperature"]
        if "max_tokens" in kwargs:
            gen_config["maxOutputTokens"] = kwargs["max_tokens"]
        if gen_config:
            payload["generationConfig"] = gen_config

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={self.api_key}"
        timeout = aiohttp.ClientTimeout(total=90)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(url, json=payload) as response:
                if response.status != 200:
                    text = await response.text()
                    raise Exception(f"Erreur API Gemini: {response.status} - {text}")
                data = await response.json()
                
                text_out = ""
                try:
                    text_out = data["candidates"][0]["content"]["parts"][0]["text"]
                except Exception:
                    pass

                # Extract grounding source URLs from metadata
                source_urls = []
                try:
                    grounding = data["candidates"][0].get("groundingMetadata", {})
                    chunks = grounding.get("groundingChunks", [])
                    for chunk in chunks:
                        uri = chunk.get("web", {}).get("uri", "")
                        if uri:
                            source_urls.append(uri)
                    # Also check groundingSupport -> retrievedContext
                    supports = grounding.get("groundingSupport", [])
                    for sup in supports:
                        uri = sup.get("web", {}).get("uri", "") or sup.get("retrievedContext", {}).get("uri", "")
                        if uri and uri not in source_urls:
                            source_urls.append(uri)
                except Exception as ex:
                    logger.debug(f"Grounding metadata parse: {ex}")

                return text_out, source_urls

    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Simulation simple de mode chat (adapte les messages OpenAI-style -> Gemini)."""
        model = kwargs.get("model", self.default_model)
        contents = []
        system_text = None
        
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            if role == "system":
                system_text = content
                continue
                
            gemini_role = "user" if role == "user" else "model"
            contents.append({
                "role": gemini_role,
                "parts": [{"text": content}]
            })
            
        payload = {"contents": contents}
        
        if system_text:
            payload["systemInstruction"] = {
                "parts": [{"text": system_text}]
            }
            
        # Configuration
        gen_config = {}
        if "temperature" in kwargs:
            gen_config["temperature"] = kwargs["temperature"]
        if "max_tokens" in kwargs:
            gen_config["maxOutputTokens"] = kwargs["max_tokens"]
        if gen_config:
            payload["generationConfig"] = gen_config

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={self.api_key}"
        
        timeout = aiohttp.ClientTimeout(total=60)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(url, json=payload) as response:
                if response.status != 200:
                    text = await response.text()
                    logger.error(f"❌ Erreur Gemini Chat {response.status}: {text}")
                    raise Exception(f"Erreur API Gemini: {response.status} - {text}")
                    
                data = await response.json()
                try:
                    return data["candidates"][0]["content"]["parts"][0]["text"]
                except (KeyError, IndexError):
                    raise Exception("Format de réponse inattendu (Chat)")

    async def close(self):
        """Clean up."""
        pass
