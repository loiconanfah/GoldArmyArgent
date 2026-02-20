"""Agent développeur spécialisé."""
from typing import Any, Dict

from loguru import logger

from core.agent_base import BaseAgent
from llm.prompt_templates import PromptTemplates


class CoderAgent(BaseAgent):
    """Agent spécialisé dans l'écriture et le débogage de code."""
    
    def __init__(self, **kwargs):
        """Initialise l'agent coder."""
        kwargs.setdefault("agent_type", "coder")
        kwargs.setdefault("name", "Coder")
        kwargs.setdefault("model", "codellama")
        kwargs.setdefault("temperature", 0.3)
        kwargs.setdefault("max_tokens", 4096)
        super().__init__(**kwargs)
    
    async def think(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyse la tâche de développement et planifie l'implémentation.
        
        Args:
            task: Tâche de développement
        
        Returns:
            Plan d'implémentation
        """
        logger.info(f"💻 {self.name} analyse la tâche de développement...")
        
        # Construire le prompt de planification
        prompt = PromptTemplates.render_task_prompt(
            agent_type="coder",
            task_description=task.get("description", ""),
            context=task.get("context", ""),
            language=task.get("language", "python"),
            existing_code=task.get("existing_code", "")
        )
        
        # Générer le plan avec le LLM
        plan_text = await self.generate_response(prompt)
        
        action_plan = {
            "task_id": task.get("id", "unknown"),
            "implementation_plan": plan_text,
            "language": task.get("language", "python"),
            "files_to_modify": task.get("files", []),
        }
        
        logger.debug(f"📋 Plan d'implémentation créé")
        return action_plan
    
    async def act(self, action_plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Implémente le code selon le plan.
        
        Args:
            action_plan: Plan d'implémentation
        
        Returns:
            Code généré et résultats
        """
        logger.info(f"⚙️ {self.name} génère le code...")
        
        # Le code est déjà dans le plan d'implémentation
        code = self._extract_code(action_plan.get("implementation_plan", ""))
        
        results = {
            "success": True,
            "code": code,
            "language": action_plan.get("language", "python"),
            "explanation": action_plan.get("implementation_plan", ""),
        }
        
        logger.success(f"✅ Code généré")
        return results
    
    def _extract_code(self, text: str) -> str:
        """Extrait le code d'un texte contenant des blocs de code markdown."""
        import re
        
        # Chercher les blocs de code markdown
        code_blocks = re.findall(r"```(?:\w+)?\n(.*?)```", text, re.DOTALL)
        
        if code_blocks:
            return "\n\n".join(code_blocks)
        
        return text
