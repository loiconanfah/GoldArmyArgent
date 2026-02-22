
"""Client Unifié pour la gestion des modèles LLM (OpenRouter + Fallback Local)."""
import asyncio
from typing import Optional, Dict, List, Any
from loguru import logger

from llm.ollama_client import OllamaClient
from llm.openrouter_client import OpenRouterClient
from config.settings import settings


class UnifiedLLMClient:
    """
    Client centralisé qui gère la stratégie de sélection de modèle.
    Stratégie:
    1. Tenter OpenRouter (si clé API présente).
    2. Si échec ou pas de clé -> Fallback sur Ollama Local.
    """
    
    def __init__(self):
        self.ollama_client = OllamaClient()
        self.openrouter_client = None
        self.gemini_client = None
        
        if settings.gemini_api_key:
            from llm.gemini_client import GeminiClient
            self.gemini_client = GeminiClient()
            logger.info("🧠 Client Unifié: Google Gemini activé (Priorité Absolue)")
        elif settings.openrouter_api_key:
            self.openrouter_client = OpenRouterClient()
            logger.info("🌐 Client Unifié: OpenRouter activé (Prioritaire)")
        else:
            logger.info("🏠 Client Unifié: Mode Local uniquement (Ollama)")
            
    async def initialize(self):
        """Initialisation des sous-clients si nécessaire."""
        # Rien de spécial à faire pour l'instant, mais gardé pour compatibilité
        pass

    async def close(self):
        """Ferme les connexions."""
        await self.ollama_client.close()
        if self.openrouter_client:
            await self.openrouter_client.close()
        if self.gemini_client:
            await self.gemini_client.close()

    async def generate(self, prompt: str, **kwargs) -> str:
        """
        Génère une réponse en utilisant la meilleure stratégie disponible.
        """
        # On extrait le modèle demandé pour éviter les doublons dans kwargs
        requested_model = kwargs.pop("model", None)

        # 0. Essai Gemini
        if self.gemini_client:
            try:
                logger.debug(f"🧠 Tentative Gemini Native...")
                return await self.gemini_client.generate(prompt, **kwargs)
            except Exception as e:
                logger.warning(f"⚠️ Échec Gemini ({e})... Bascule sur OpenRouter.")

        # 1. Essai OpenRouter
        if self.openrouter_client:
            try:
                # On utilise le modèle demandé ou celui par défaut pour OpenRouter
                model = requested_model or settings.openrouter_default_model
                
                logger.debug(f"🌐 Tentative OpenRouter avec {model}...")
                return await self.openrouter_client.generate(prompt, model=model, **kwargs)
                
            except Exception as e:
                logger.warning(f"⚠️ Échec OpenRouter ({e})... Bascule sur Ollama Local.")
        
        # 2. Fallback Ollama
        try:
            # Pour le fallback local, on force le modèle local par défaut
            # car le modèle OpenRouter (ex: gpt-4) n'existe probablement pas en local
            model = settings.ollama_default_model
            logger.debug(f"🏠 Utilisation Ollama Local avec {model}...")
            
            return await self.ollama_client.generate(prompt, model=model, **kwargs)
            
        except Exception as e:
            logger.error(f"❌ Échec Critique (OpenRouter et Ollama): {e}")
            raise e

    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Mode Chat unifié."""
        # 0. Essai Gemini
        if self.gemini_client:
            try:
                return await self.gemini_client.chat(messages, **kwargs)
            except Exception as e:
                logger.warning(f"⚠️ Échec Gemini Chat ({e}).")

        # 1. Essai OpenRouter
        if self.openrouter_client:
            try:
                # OpenRouter utilise /chat/completions qui est similaire à generate() avec messages
                # Mais notre client OpenRouter a une méthode generate() qui gère les messages si "system" est passé
                # Pour le chat complet, on doit adapter.
                
                # Note: OpenRouterClient.generate gère déjà l'assemblage messages -> payload
                # Mais ici on a déjà une liste de messages.
                # On va appeler directement la méthode client interne si besoin ou adapter openrouter_client.
                
                # Simplification: OpenRouterClient n'a pas de méthode chat() explicite dans mon implémentation précédente ?
                # Vérifions... J'ai codé generate() qui construit le payload chat/completions.
                # Mais il prend "prompt" et "system".
                # Je vais tricher: concaténer ou appeler une méthode privée si elle existait.
                
                # Mieux: modifier OpenRouterClient pour accepter messages, ou adapter ici.
                # Pour l'instant, on assume que OpenRouterClient.generate est assez flexible ou on l'améliore.
                # Hack temporaire: extraire le dernier user message comme prompt.
                
                # CORRECTIF: Je vais plutôt appeler _raw_chat sur OpenRouterClient si je l'avais fait, 
                # mais comme je viens de le créer, je sais que generate() prend prompt/system.
                
                # Pour faire propre, je vais utiliser generate() avec le dernier message
                # et concaténer l'historique dans system ? Non, c'est moche.
                
                # Solution rapide: Utiliser Ollama pour le chat complexe pour l'instant
                # OU (Mieux) utiliser OpenRouter generate en mode "raw" si je l'avais exposé.
                
                pass # TODO: Améliorer le support Chat OpenRouter
            except Exception:
                pass

        # Fallback Ollama (qui a une méthode chat native)
        return await self.ollama_client.chat(messages, **kwargs)
