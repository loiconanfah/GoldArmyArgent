
"""Client OpenRouter pour GoldArmyArgent."""
import asyncio
from typing import AsyncGenerator, Dict, List, Optional, Any
import httpx
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential  # kept for potential future use

from config.settings import settings


class OpenRouterClient:
    """Client asynchrone pour interagir avec OpenRouter API."""
    
    BASE_URL = "https://openrouter.ai/api/v1"
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Initialise le client OpenRouter.
        """
        self.api_key = api_key or settings.openrouter_api_key
        self.default_model = model or settings.openrouter_default_model
        
        if not self.api_key:
            logger.warning("⚠️ Aucune clé API OpenRouter fournie!")
            
        self.client = httpx.AsyncClient(
            timeout=120.0,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "HTTP-Referer": "https://goldarmyargent.local", # Requis par OpenRouter
                "X-Title": "GoldArmyArgent Agent",
            }
        )
        logger.info(f"OpenRouterClient initialisé | Modèle: {self.default_model}")
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
    
    async def close(self):
        await self.client.aclose()
    
    async def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs
    ) -> str:
        """Génère une réponse via OpenRouter avec retry automatique sur rate-limit."""
        model = model or self.default_model
        
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        json_mode = kwargs.pop("json_mode", False)
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            **kwargs
        }
        
        if json_mode:
            payload["response_format"] = {"type": "json_object"}
        
        # Retry with exponential backoff — longer wait for 429 rate limits
        max_attempts = 5
        for attempt in range(1, max_attempts + 1):
            try:
                response = await self.client.post(
                    f"{self.BASE_URL}/chat/completions",
                    json=payload
                )
                response.raise_for_status()
                result = response.json()
                return result["choices"][0]["message"]["content"]
                
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:
                    # Rate limit — wait longer before retry
                    wait_time = min(15 * (2 ** (attempt - 1)), 120)  # 15s, 30s, 60s, 120s...
                    logger.warning(f"⏳ OpenRouter 429 rate-limit (tentative {attempt}/{max_attempts}). Attente {wait_time}s...")
                    if attempt < max_attempts:
                        await asyncio.sleep(wait_time)
                        continue
                    else:
                        logger.error(f"❌ OpenRouter: trop de 429 après {max_attempts} tentatives.")
                        raise
                else:
                    logger.error(f"❌ Erreur HTTP OpenRouter: {e}")
                    if e.response is not None:
                        logger.error(f"Détails: {e.response.text}")
                    raise
            except httpx.HTTPError as e:
                logger.error(f"❌ Erreur HTTP OpenRouter: {e}")
                raise
            except Exception as e:
                logger.error(f"❌ Erreur OpenRouter: {e}")
                raise

    async def list_models(self) -> List[Dict[str, Any]]:
        """Liste les modèles disponibles sur OpenRouter."""
        try:
            response = await self.client.get(f"{self.BASE_URL}/models")
            response.raise_for_status()
            data = response.json()
            return data.get("data", [])
        except Exception as e:
            logger.error(f"Erreur listing modèles OpenRouter: {e}")
            return []

    async def is_available(self) -> bool:
        """Vérifie si la clé est valide et le service accessible."""
        if not self.api_key:
            return False
        try:
            response = await self.client.get(f"{self.BASE_URL}/auth/key")
            return response.status_code == 200
        except:
            return False
