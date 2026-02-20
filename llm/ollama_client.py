"""Client Ollama pour GoldArmyArgent."""
import asyncio
from typing import AsyncGenerator, Dict, List, Optional, Any
import httpx
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential

from config.settings import settings


class OllamaClient:
    """Client asynchrone pour interagir avec Ollama."""
    
    def __init__(self, host: Optional[str] = None, model: Optional[str] = None):
        """
        Initialise le client Ollama.
        
        Args:
            host: URL de l'API Ollama (défaut: depuis settings)
            model: Modèle par défaut à utiliser (défaut: depuis settings)
        """
        self.host = host or settings.ollama_host
        self.default_model = model or settings.ollama_default_model
        self.client = httpx.AsyncClient(timeout=300.0)
        logger.info(f"OllamaClient initialisé: {self.host} | Modèle: {self.default_model}")
    
    async def __aenter__(self):
        """Context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        await self.close()
    
    async def close(self):
        """Ferme le client HTTP."""
        await self.client.aclose()
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    async def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        stream: bool = False,
        **kwargs
    ) -> str | AsyncGenerator[str, None]:
        """
        Génère une réponse avec Ollama.
        
        Args:
            prompt: Le prompt à envoyer
            model: Modèle à utiliser (défaut: self.default_model)
            system: Message système optionnel
            temperature: Température de génération (0-1)
            max_tokens: Nombre maximum de tokens
            stream: Si True, retourne un générateur asynchrone
            **kwargs: Paramètres additionnels
        
        Returns:
            Réponse générée (str) ou générateur asynchrone si stream=True
        """
        model = model or self.default_model
        
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": stream,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
                **kwargs
            }
        }
        
        if system:
            payload["system"] = system
        
        logger.debug(f"Génération avec {model}: {prompt[:100]}...")
        
        try:
            if stream:
                return self._stream_generate(payload)
            else:
                response = await self.client.post(
                    f"{self.host}/api/generate",
                    json=payload
                )
                response.raise_for_status()
                result = response.json()
                return result.get("response", "")
        
        except httpx.HTTPError as e:
            logger.error(f"Erreur HTTP Ollama: {e}")
            raise
        except Exception as e:
            logger.error(f"Erreur lors de la génération: {e}")
            raise
    
    async def _stream_generate(self, payload: Dict[str, Any]) -> AsyncGenerator[str, None]:
        """Génère une réponse en streaming."""
        async with self.client.stream(
            "POST",
            f"{self.host}/api/generate",
            json=payload
        ) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line:
                    import json
                    data = json.loads(line)
                    if "response" in data:
                        yield data["response"]
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs
    ) -> str:
        """
        Mode chat avec historique de conversation.
        
        Args:
            messages: Liste de messages [{"role": "user/assistant", "content": "..."}]
            model: Modèle à utiliser
            temperature: Température de génération
            max_tokens: Nombre maximum de tokens
            **kwargs: Paramètres additionnels
        
        Returns:
            Réponse générée
        """
        model = model or self.default_model
        
        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
                **kwargs
            }
        }
        
        try:
            response = await self.client.post(
                f"{self.host}/api/chat",
                json=payload
            )
            response.raise_for_status()
            result = response.json()
            return result.get("message", {}).get("content", "")
        
        except httpx.HTTPError as e:
            logger.error(f"Erreur HTTP Ollama chat: {e}")
            raise
    
    async def list_models(self) -> List[Dict[str, Any]]:
        """Liste les modèles disponibles."""
        try:
            response = await self.client.get(f"{self.host}/api/tags")
            response.raise_for_status()
            result = response.json()
            return result.get("models", [])
        except httpx.HTTPError as e:
            logger.error(f"Erreur lors de la récupération des modèles: {e}")
            return []
    
    async def pull_model(self, model: str) -> bool:
        """
        Télécharge un modèle.
        
        Args:
            model: Nom du modèle à télécharger
        
        Returns:
            True si succès, False sinon
        """
        try:
            logger.info(f"Téléchargement du modèle {model}...")
            response = await self.client.post(
                f"{self.host}/api/pull",
                json={"name": model},
                timeout=600.0  # 10 minutes pour le téléchargement
            )
            response.raise_for_status()
            logger.success(f"Modèle {model} téléchargé avec succès")
            return True
        except Exception as e:
            logger.error(f"Erreur lors du téléchargement de {model}: {e}")
            return False
    
    async def is_available(self) -> bool:
        """Vérifie si Ollama est disponible."""
        try:
            response = await self.client.get(f"{self.host}/api/tags", timeout=5.0)
            return response.status_code == 200
        except:
            return False


# Test du client
async def test_ollama_client():
    """Test basique du client Ollama."""
    async with OllamaClient() as client:
        # Vérifier la disponibilité
        if not await client.is_available():
            logger.error("❌ Ollama n'est pas disponible!")
            return False
        
        logger.success("✅ Ollama est disponible")
        
        # Lister les modèles
        models = await client.list_models()
        logger.info(f"Modèles disponibles: {[m['name'] for m in models]}")
        
        # Test de génération
        response = await client.generate(
            prompt="Dis bonjour en une phrase courte.",
            temperature=0.7,
            max_tokens=50
        )
        logger.success(f"Réponse: {response}")
        
        return True


if __name__ == "__main__":
    asyncio.run(test_ollama_client())
