"""Orchestrateur principal pour gérer l'armée d'agents."""
import asyncio
from typing import Any, Dict, List, Optional, Type
from datetime import datetime
import yaml

from loguru import logger
from pathlib import Path

from core.agent_base import BaseAgent, AgentStatus
from core.memory import memory_system
from core.communication import communication_bus
from agents import ResearcherAgent, CoderAgent, PlannerAgent, JobSearchAgent, HeadhunterAgent
from config.settings import settings


class Orchestrator:
    """Orchestrateur central pour coordonner les agents."""
    
    def __init__(self):
        """Initialise l'orchestrateur."""
        self.agents: Dict[str, BaseAgent] = {}
        self.agent_types: Dict[str, Type[BaseAgent]] = {
            "researcher": ResearcherAgent,
            "coder": CoderAgent,
            "planner": PlannerAgent,
            "job_searcher": JobSearchAgent,
            "headhunter": HeadhunterAgent,
        }
        self.task_queue: asyncio.Queue = asyncio.Queue()
        self.running = False
        
        # Charger la configuration des agents
        self.agents_config = self._load_agents_config()
        
        logger.info("🎭 Orchestrateur initialisé")
    
    def _load_agents_config(self) -> Dict[str, Any]:
        """Charge la configuration des agents depuis le YAML."""
        config_path = settings.project_root / "config" / "agents_config.yaml"
        
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        
        logger.warning("Configuration des agents non trouvée, utilisation des valeurs par défaut")
        return {"agents": {}, "global": {}}
    
    async def create_agent(
        self,
        agent_type: str,
        agent_id: Optional[str] = None,
        **kwargs
    ) -> BaseAgent:
        """
        Crée un nouvel agent.
        
        Args:
            agent_type: Type d'agent à créer
            agent_id: ID personnalisé (optionnel)
            **kwargs: Paramètres additionnels
        
        Returns:
            Agent créé
        """
        if agent_type not in self.agent_types:
            raise ValueError(f"Type d'agent inconnu: {agent_type}")
        
        # Récupérer la config pour ce type d'agent
        agent_config = self.agents_config.get("agents", {}).get(agent_type, {})
        
        # Fusionner avec les kwargs
        config = {
            "model": agent_config.get("model"),
            "temperature": agent_config.get("temperature", 0.7),
            "max_tokens": agent_config.get("max_tokens", 2048),
            **kwargs
        }
        
        # Créer l'agent
        agent_class = self.agent_types[agent_type]
        agent = agent_class(agent_id=agent_id, **config)
        
        # Initialiser l'agent
        await agent.initialize()
        
        # Enregistrer l'agent
        self.agents[agent.agent_id] = agent
        
        logger.success(f"✅ Agent créé: {agent.name} ({agent_type})")
        return agent
    
    async def remove_agent(self, agent_id: str):
        """
        Supprime un agent.
        
        Args:
            agent_id: ID de l'agent à supprimer
        """
        if agent_id in self.agents:
            agent = self.agents[agent_id]
            await agent.shutdown()
            del self.agents[agent_id]
            logger.info(f"🗑️ Agent supprimé: {agent.name}")
    
    async def submit_task(self, task: Dict[str, Any]) -> str:
        """
        Soumet une tâche à l'orchestrateur.
        
        Args:
            task: Tâche à exécuter
        
        Returns:
            ID de la tâche
        """
        import uuid
        
        task_id = task.get("id") or str(uuid.uuid4())
        task["id"] = task_id
        task["submitted_at"] = datetime.now().isoformat()
        task["status"] = "pending"
        
        await self.task_queue.put(task)
        logger.info(f"📥 Tâche soumise: {task_id}")
        
        return task_id
    
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Exécute une tâche avec l'agent approprié.
        
        Args:
            task: Tâche à exécuter
        
        Returns:
            Résultat de la tâche
        """
        agent_type = task.get("agent_type", "researcher")
        
        # Ensure task has an ID
        if "id" not in task:
            import uuid
            task["id"] = str(uuid.uuid4())
        
        # Créer ou récupérer un agent
        agent = await self._get_or_create_agent(agent_type)
        
        # Exécuter la tâche
        logger.info(f"🚀 Exécution de la tâche {task['id']} avec {agent.name}")
        result = await agent.execute_task(task)
        
        # Stocker en mémoire
        await memory_system.store(
            agent_id=agent.agent_id,
            content=f"Tâche: {task.get('description', '')} | Résultat: {result.get('success', False)}",
            metadata={"task_id": task["id"], "type": "task_result"}
        )
        
        return result
    
    async def _get_or_create_agent(self, agent_type: str) -> BaseAgent:
        """Récupère un agent existant ou en crée un nouveau."""
        # Chercher un agent idle du bon type
        for agent in self.agents.values():
            if agent.agent_type == agent_type and agent.status == AgentStatus.IDLE:
                return agent
        
        # Créer un nouvel agent si nécessaire
        if len(self.agents) < settings.max_agents:
            return await self.create_agent(agent_type)
        
        # Attendre qu'un agent se libère
        logger.warning(f"Limite d'agents atteinte ({settings.max_agents}), attente...")
        while True:
            for agent in self.agents.values():
                if agent.agent_type == agent_type and agent.status == AgentStatus.IDLE:
                    return agent
            await asyncio.sleep(1)
    
    async def process_queue(self):
        """Traite la file de tâches en continu."""
        logger.info("🔄 Traitement de la file de tâches démarré")
        
        while self.running:
            try:
                # Attendre une tâche (timeout pour vérifier self.running)
                task = await asyncio.wait_for(self.task_queue.get(), timeout=1.0)
                
                # Exécuter la tâche
                result = await self.execute_task(task)
                
                logger.info(f"✅ Tâche {task['id']} terminée: {result.get('success', False)}")
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"❌ Erreur lors du traitement de la file: {e}")
    
    async def start(self):
        """Démarre l'orchestrateur."""
        self.running = True
        logger.success("🎬 Orchestrateur démarré")
        
        # Lancer le traitement de la file
        asyncio.create_task(self.process_queue())
    
    async def stop(self):
        """Arrête l'orchestrateur."""
        self.running = False
        
        # Arrêter tous les agents
        for agent_id in list(self.agents.keys()):
            await self.remove_agent(agent_id)
        
        logger.info("🛑 Orchestrateur arrêté")
    
    def get_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques de l'orchestrateur."""
        agent_stats = {
            agent_id: agent.get_status()
            for agent_id, agent in self.agents.items()
        }
        
        return {
            "total_agents": len(self.agents),
            "agents_by_type": self._count_agents_by_type(),
            "queue_size": self.task_queue.qsize(),
            "running": self.running,
            "agents": agent_stats,
            "memory_stats": memory_system.get_stats(),
            "communication_stats": communication_bus.get_stats(),
        }
    
    def _count_agents_by_type(self) -> Dict[str, int]:
        """Compte les agents par type."""
        counts = {}
        for agent in self.agents.values():
            counts[agent.agent_type] = counts.get(agent.agent_type, 0) + 1
        return counts


# Instance globale
orchestrator = Orchestrator()
