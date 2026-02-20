"""Agent planificateur spécialisé."""
from typing import Any, Dict, List

from loguru import logger

from core.agent_base import BaseAgent
from llm.prompt_templates import PromptTemplates


class PlannerAgent(BaseAgent):
    """Agent spécialisé dans la décomposition de tâches complexes."""
    
    def __init__(self, **kwargs):
        """Initialise l'agent planner."""
        kwargs.setdefault("agent_type", "planner")
        kwargs.setdefault("name", "Planner")
        kwargs.setdefault("temperature", 0.5)
        kwargs.setdefault("max_tokens", 3072)
        super().__init__(**kwargs)
    
    async def think(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyse l'objectif et commence la décomposition.
        
        Args:
            task: Objectif à planifier
        
        Returns:
            Analyse initiale
        """
        logger.info(f"📊 {self.name} analyse l'objectif...")
        
        # Construire le prompt de planification
        prompt = PromptTemplates.render_task_prompt(
            agent_type="planner",
            objective=task.get("objective", ""),
            context=task.get("context", ""),
            constraints=task.get("constraints", "Aucune contrainte spécifiée")
        )
        
        # Générer l'analyse avec le LLM
        analysis = await self.generate_response(prompt)
        
        action_plan = {
            "task_id": task.get("id", "unknown"),
            "analysis": analysis,
            "objective": task.get("objective", ""),
        }
        
        logger.debug(f"📋 Analyse initiale créée")
        return action_plan
    
    async def act(self, action_plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Crée le plan d'action détaillé.
        
        Args:
            action_plan: Analyse initiale
        
        Returns:
            Plan d'action structuré
        """
        logger.info(f"🎯 {self.name} crée le plan d'action...")
        
        # Extraire les tâches du plan
        tasks = self._parse_plan(action_plan.get("analysis", ""))
        
        results = {
            "success": True,
            "plan": action_plan.get("analysis", ""),
            "tasks": tasks,
            "total_tasks": len(tasks),
            "estimated_complexity": self._estimate_complexity(tasks),
        }
        
        logger.success(f"✅ Plan créé avec {len(tasks)} tâches")
        return results
    
    def _parse_plan(self, plan_text: str) -> List[Dict[str, Any]]:
        """Parse un plan textuel en liste de tâches structurées."""
        tasks = []
        current_task = None
        
        for line in plan_text.split("\n"):
            line = line.strip()
            
            # Détecter les tâches (lignes numérotées ou avec bullets)
            if line and (line[0].isdigit() or line.startswith("-") or line.startswith("*")):
                if current_task:
                    tasks.append(current_task)
                
                current_task = {
                    "description": line.lstrip("0123456789.-* "),
                    "status": "pending",
                    "dependencies": [],
                }
        
        if current_task:
            tasks.append(current_task)
        
        return tasks if tasks else [{"description": "Tâche générale", "status": "pending"}]
    
    def _estimate_complexity(self, tasks: List[Dict[str, Any]]) -> str:
        """Estime la complexité globale du plan."""
        num_tasks = len(tasks)
        
        if num_tasks <= 3:
            return "faible"
        elif num_tasks <= 7:
            return "moyenne"
        else:
            return "élevée"
