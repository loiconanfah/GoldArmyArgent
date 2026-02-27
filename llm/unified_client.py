"""Client Unifié pour la gestion des modèles LLM (Priorité Strict Gemini)."""
import asyncio
from typing import Optional, Dict, List, Any
from loguru import logger

from llm.ollama_client import OllamaClient
from llm.openrouter_client import OpenRouterClient
from config.settings import settings


class UnifiedLLMClient:
    """
    Client centralisé qui gère la stratégie de sélection de modèle.
    FORCE SNIPER 6.0 : Si Gemini est configuré, AUCUN FALLBACK n'est autorisé.
    """
    
    def __init__(self):
        self.ollama_client = OllamaClient()
        self.openrouter_client = None
        self.gemini_client = None
        
        if settings.gemini_api_key:
            from llm.gemini_client import GeminiClient
            self.gemini_client = GeminiClient()
            logger.info("🧠 Client Unifié: Google Gemini activé (MODE EXCLUSIF SNIPER 6.0)")
        elif settings.openrouter_api_key:
            self.openrouter_client = OpenRouterClient()
            logger.info("🌐 Client Unifié: OpenRouter activé")
        else:
            logger.info("🏠 Client Unifié: Mode Local uniquement (Ollama)")
            
    async def initialize(self):
        pass

    async def close(self):
        await self.ollama_client.close()
        if self.openrouter_client:
            await self.openrouter_client.close()
        if self.gemini_client:
            await self.gemini_client.close()

    async def generate(self, prompt: str, **kwargs) -> str:
        """Génère une réponse. Priorité exclusive à Gemini si configuré."""
        requested_model = kwargs.pop("model", None)
        # Remove None values so concrete clients use their defaults
        clean_kwargs = {k: v for k, v in kwargs.items() if v is not None}

        # SI GEMINI EST ACTIVÉ -> AUCUN AUTRE MODÈLE NE DOIT ÊTRE UTILISÉ
        if self.gemini_client:
            try:
                # Si requested_model est None, on ne le passe pas
                if requested_model:
                    clean_kwargs["model"] = requested_model
                return await self.gemini_client.generate(prompt, **clean_kwargs)
            except Exception as e:
                logger.error(f"❌ échec Critique Gemini (Fallback Impossible): {e}")
                raise Exception(f"Désolé, une erreur technique sur Gemini empêche de garantir la précision à 100%. Fallback Ollama désactivé. Erreur: {e}")

        # Sinon, pour les autres modes sans Gemini
        if self.openrouter_client:
            try:
                model = requested_model or settings.openrouter_default_model
                return await self.openrouter_client.generate(prompt, model=model, **kwargs)
            except Exception as e:
                logger.warning(f"⚠️ Échec OpenRouter ({e})... Bascule sur Ollama Local.")
        
        try:
            model = settings.ollama_default_model
            return await self.ollama_client.generate(prompt, model=model, **kwargs)
        except Exception as e:
            logger.error(f"❌ Échec Critique LLM: {e}")
            raise e

    async def generate_with_sources(self, prompt: str, **kwargs) -> tuple:
        """Génère une réponse avec grounding sources (Gemini EXCLUSIF)."""
        if self.gemini_client:
            try:
                return await self.gemini_client.generate_with_sources(prompt, **kwargs)
            except Exception as e:
                logger.error(f"❌ Échec Grounding Gemini: {e}")
                raise Exception(f"Erreur Grounding Gemini : {e}")
        
        # Impossible de faire du grounding sans Gemini 2.0
        raise Exception("Le mode Grounding (Sniper) requiert Gemini API.")

    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Mode Chat unifié."""
        if self.gemini_client:
            try:
                return await self.gemini_client.chat(messages, **kwargs)
            except Exception as e:
                logger.error(f"❌ Échec Gemini Chat: {e}")
                raise e

        if self.openrouter_client:
            try:
                model = kwargs.get("model") or settings.openrouter_default_model
                # Simplification logic
                conv = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
                return await self.openrouter_client.generate(conv, model=model)
            except Exception as e:
                pass

        return await self.ollama_client.chat(messages, **kwargs)
