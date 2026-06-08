"""Client Unifié — Stratégie Gemini → OpenRouter (fallback automatique sur 429/erreur)."""
import asyncio
from typing import Optional, Dict, List, Any
from loguru import logger

from llm.ollama_client import OllamaClient
from llm.openrouter_client import OpenRouterClient
from config.settings import settings


# Modèles OpenRouter gratuits performants pour le fallback
OPENROUTER_FALLBACK_MODELS = [
    "openrouter/auto",                           # Auto-routage premium (choisit le meilleur rapport qualité/prix)
    "google/gemini-2.5-flash",                   # Ultra rapide et pas cher
    "meta-llama/llama-3.3-70b-instruct",         # Très intelligent et fiable
    "anthropic/claude-3.5-haiku",                # Excellent pour la logique et très rapide
]

# Mots-clés détectés dans les exceptions Gemini qui déclenchent le fallback
RATE_LIMIT_SIGNALS = ["429", "rate limit", "quota", "resource_exhausted", "tentatives"]


def _is_rate_limit_error(exc: Exception) -> bool:
    """Retourne True si l'exception est un rate limit (429) Gemini."""
    msg = str(exc).lower()
    return any(signal in msg for signal in RATE_LIMIT_SIGNALS)


class UnifiedLLMClient:
    """
    Client centralisé avec stratégie de fallback intelligente:
    1. Gemini (priorité maximale — précision Sniper)
    2. OpenRouter (fallback automatique sur 429 ou erreur Gemini)
    3. Ollama local (fallback ultime)
    """

    def __init__(self):
        self.ollama_client = OllamaClient()
        self.openrouter_client = None
        self.gemini_client = None

        if settings.gemini_api_key:
            from llm.gemini_client import GeminiClient
            self.gemini_client = GeminiClient()
            logger.info("🧠 Client Unifié: Gemini activé (primaire)")

        if settings.openrouter_api_key:
            self.openrouter_client = OpenRouterClient()
            if self.gemini_client:
                logger.info("🔀 Client Unifié: OpenRouter activé (fallback automatique sur 429)")
            else:
                logger.info("🌐 Client Unifié: OpenRouter activé (primaire)")

        if not self.gemini_client and not self.openrouter_client:
            logger.info("🏠 Client Unifié: Mode Local uniquement (Ollama)")

    async def initialize(self):
        pass

    async def close(self):
        await self.ollama_client.close()
        if self.openrouter_client:
            await self.openrouter_client.close()
        if self.gemini_client:
            await self.gemini_client.close()

    async def _openrouter_generate(self, prompt: str, **kwargs) -> str:
        """Appelle OpenRouter avec rotation sur les modèles gratuits."""
        clean_kwargs = {k: v for k, v in kwargs.items() if k not in ("model",)}
        # On force un modèle gratuit pour le fallback
        for model in OPENROUTER_FALLBACK_MODELS:
            try:
                result = await self.openrouter_client.generate(prompt, model=model, **clean_kwargs)
                if result:
                    logger.info(f"🔀 OpenRouter fallback OK ({model})")
                    return result
            except Exception as e:
                logger.debug(f"OpenRouter model {model} failed: {e}")
                continue
        raise Exception("Tous les modèles OpenRouter ont échoué.")

    async def generate(self, prompt: str, **kwargs) -> str:
        """
        Génère une réponse avec fallback automatique :
        Gemini → OpenRouter → Ollama
        """
        requested_model = kwargs.pop("model", None)
        clean_kwargs = {k: v for k, v in kwargs.items() if v is not None}
        if requested_model:
            clean_kwargs["model"] = requested_model

        # 1. Tentative Gemini
        if self.gemini_client:
            try:
                return await self.gemini_client.generate(prompt, **clean_kwargs)
            except Exception as e:
                if _is_rate_limit_error(e):
                    logger.warning(f"⚡ Gemini 429 — bascule automatique sur OpenRouter...")
                else:
                    logger.error(f"❌ Gemini erreur: {e} — tentative OpenRouter...")

                # 2. Fallback OpenRouter si disponible
                if self.openrouter_client:
                    try:
                        return await self._openrouter_generate(prompt, **{k: v for k, v in clean_kwargs.items() if k != "model"})
                    except Exception as or_err:
                        logger.warning(f"⚠️ OpenRouter aussi en échec: {or_err} — fallback Ollama...")
                else:
                    # Pas d'OpenRouter configuré → re-raise
                    raise Exception(f"Gemini failed ({e}) and OpenRouter is not configured.")

        # 3. OpenRouter seul (sans Gemini)
        elif self.openrouter_client:
            try:
                model = requested_model or settings.openrouter_default_model
                return await self.openrouter_client.generate(prompt, model=model, **kwargs)
            except Exception as e:
                logger.warning(f"⚠️ Échec OpenRouter ({e}) — bascule sur Ollama local...")

        # 4. Ollama local (dernier recours)
        try:
            model = settings.ollama_default_model
            return await self.ollama_client.generate(prompt, model=model, **kwargs)
        except Exception as e:
            logger.error(f"❌ Échec total LLM (Gemini + OpenRouter + Ollama): {e}")
            raise e

    async def generate_with_sources(self, prompt: str, **kwargs) -> tuple:
        """Génère une réponse avec grounding (Gemini EXCLUSIF — pas de fallback possible)."""
        if self.gemini_client:
            try:
                return await self.gemini_client.generate_with_sources(prompt, **kwargs)
            except Exception as e:
                logger.error(f"❌ Échec Grounding Gemini: {e}")
                raise Exception(f"Erreur Grounding Gemini : {e}")

        raise Exception("Le mode Grounding (Sniper web) requiert Gemini API.")

    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Mode Chat unifié avec fallback Gemini → OpenRouter."""
        # 1. Gemini
        if self.gemini_client:
            try:
                return await self.gemini_client.chat(messages, **kwargs)
            except Exception as e:
                if _is_rate_limit_error(e):
                    logger.warning(f"⚡ Gemini Chat 429 — bascule OpenRouter...")
                else:
                    logger.error(f"❌ Gemini Chat erreur: {e}")

                if self.openrouter_client:
                    try:
                        conv = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
                        return await self._openrouter_generate(conv)
                    except Exception as or_err:
                        logger.warning(f"OpenRouter Chat aussi en échec: {or_err}")
                else:
                    raise e

        # 2. OpenRouter seul
        if self.openrouter_client:
            try:
                conv = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
                model = kwargs.get("model") or settings.openrouter_default_model
                return await self.openrouter_client.generate(conv, model=model)
            except Exception as e:
                logger.warning(f"OpenRouter Chat failed: {e}")

        # 3. Ollama local
        return await self.ollama_client.chat(messages, **kwargs)
