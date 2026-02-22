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
            
        # Utilisation de Gemini 3.x (Preview/Pro) sur demande
        self.default_model = "gemini-3.1-pro-preview"
        
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
            
        gen_config = {"responseMimeType": "application/json"}
        if "temperature" in kwargs:
            gen_config["temperature"] = kwargs["temperature"]
        if "max_tokens" in kwargs:
            gen_config["maxOutputTokens"] = kwargs["max_tokens"]
            
        if gen_config:
            payload["generationConfig"] = gen_config

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={self.api_key}"
        
        async with aiohttp.ClientSession() as session:
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
        gen_config = {"responseMimeType": "application/json"}
        if "temperature" in kwargs:
            gen_config["temperature"] = kwargs["temperature"]
        if "max_tokens" in kwargs:
            gen_config["maxOutputTokens"] = kwargs["max_tokens"]
        if gen_config:
            payload["generationConfig"] = gen_config

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={self.api_key}"
        
        async with aiohttp.ClientSession() as session:
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
