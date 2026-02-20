"""Agent de recherche spécialisé."""
from typing import Any, Dict

from loguru import logger

from core.agent_base import BaseAgent
from llm.prompt_templates import PromptTemplates


class ResearcherAgent(BaseAgent):
    """Agent spécialisé dans la recherche et l'analyse d'informations."""
    
    def __init__(self, **kwargs):
        """Initialise l'agent researcher."""
        kwargs.setdefault("agent_type", "researcher")
        kwargs.setdefault("name", "Researcher")
        kwargs.setdefault("temperature", 0.7)
        super().__init__(**kwargs)
    
    async def think(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyse la tâche de recherche et planifie l'approche.
        
        Args:
            task: Tâche de recherche
        
        Returns:
            Plan de recherche
        """
        logger.info(f"🔍 {self.name} analyse la tâche de recherche...")
        
        # Construire le prompt de planification
        prompt = PromptTemplates.render_task_prompt(
            agent_type="researcher",
            task_description=task.get("description", ""),
            context=task.get("context", "Aucun contexte fourni")
        )
        
        # Générer le plan avec le LLM
        plan_text = await self.generate_response(prompt)
        
        action_plan = {
            "task_id": task.get("id", "unknown"),
            "approach": plan_text,
            "steps": self._extract_steps(plan_text),
            "estimated_time": "unknown",
        }
        
        logger.debug(f"📋 Plan de recherche créé avec {len(action_plan['steps'])} étapes")
        return action_plan
    
    async def act(self, action_plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Exécute la recherche selon le plan.
        
        Args:
            action_plan: Plan de recherche
        
        Returns:
            Résultats de recherche
        """
        logger.info(f"🎯 {self.name} exécute la recherche...")
        
        # Pour l'instant, simulation de recherche
        # TODO: Intégrer des outils de recherche réels (web search, etc.)
        
        results = {
            "success": True,
            "findings": action_plan.get("approach", ""),
            "sources": [],
            "confidence": 0.8,
        }
        
        logger.success(f"✅ Recherche terminée")
        return results
    
    def _extract_steps(self, plan_text: str) -> list:
        """Extrait les étapes d'un plan textuel."""
        # Simple extraction basée sur les lignes numérotées
        steps = []
        for line in plan_text.split("\n"):
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith("-") or line.startswith("*")):
                steps.append(line)
        return steps if steps else ["Recherche générale"]
