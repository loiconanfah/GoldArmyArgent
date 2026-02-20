"""Module LLM pour GoldArmyArgent."""
from llm.ollama_client import OllamaClient
from llm.prompt_templates import PromptTemplates

__all__ = ["OllamaClient", "PromptTemplates"]
