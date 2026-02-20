"""Classe de base abstraite pour tous les agents."""
import asyncio
import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from loguru import logger
from pydantic.v1 import BaseModel, Field

from llm.unified_client import UnifiedLLMClient
from llm.prompt_templates import PromptTemplates


class AgentStatus(str, Enum):
    """Statuts possibles d'un agent."""
    IDLE = "idle"
    THINKING = "thinking"
    ACTING = "acting"
    LEARNING = "learning"
    ERROR = "error"
    STOPPED = "stopped"


class AgentMessage(BaseModel):
    """Message échangé entre agents."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    sender_id: str
    receiver_id: Optional[str] = None  # None = broadcast
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)


class AgentMemory(BaseModel):
    """Mémoire locale d'un agent."""
    short_term: List[Dict[str, Any]] = Field(default_factory=list, description="Mémoire à court terme")
    long_term: List[Dict[str, Any]] = Field(default_factory=list, description="Mémoire à long terme")
    context: Dict[str, Any] = Field(default_factory=dict, description="Contexte actuel")
    
    def add_to_short_term(self, item: Dict[str, Any], max_items: int = 10):
        """Ajoute un élément à la mémoire court terme."""
        self.short_term.append(item)
        if len(self.short_term) > max_items:
            # Déplacer les anciens items vers long terme
            self.long_term.extend(self.short_term[:-max_items])
            self.short_term = self.short_term[-max_items:]
    
    def get_recent_context(self, n: int = 5) -> List[Dict[str, Any]]:
        """Récupère les n derniers éléments du contexte."""
        return self.short_term[-n:] if self.short_term else []


class BaseAgent(ABC):
    """Classe de base abstraite pour tous les agents."""
    
    def __init__(
        self,
        agent_id: Optional[str] = None,
        name: Optional[str] = None,
        agent_type: str = "base",
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ):
        """
        Initialise l'agent.
        
        Args:
            agent_id: ID unique de l'agent
            name: Nom de l'agent
            agent_type: Type d'agent (researcher, coder, etc.)
            model: Modèle Ollama à utiliser
            temperature: Température de génération
            max_tokens: Nombre maximum de tokens
        """
        self.agent_id = agent_id or str(uuid.uuid4())
        self.name = name or f"{agent_type}_{self.agent_id[:8]}"
        self.agent_type = agent_type
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        # État de l'agent
        self.status = AgentStatus.IDLE
        self.memory = AgentMemory()
        self.message_queue: asyncio.Queue = asyncio.Queue()
        
        # Client LLM Unifié
        self.llm_client: Optional[UnifiedLLMClient] = None
        
        # Statistiques
        self.stats = {
            "tasks_completed": 0,
            "tasks_failed": 0,
            "messages_sent": 0,
            "messages_received": 0,
            "created_at": datetime.now(),
        }
        
        logger.info(f"🤖 Agent créé: {self.name} ({self.agent_type}) - ID: {self.agent_id}")
    
    async def initialize(self):
        """Initialise l'agent (connexion LLM, etc.)."""
        self.llm_client = UnifiedLLMClient()
        mode = "OpenRouter" if self.llm_client.openrouter_client else "Local"
        logger.info(f"✅ Agent {self.name} initialisé (Mode: {mode})")
    
    async def shutdown(self):
        """Arrête proprement l'agent."""
        self.status = AgentStatus.STOPPED
        if self.llm_client:
            await self.llm_client.close()
        logger.info(f"🛑 Agent {self.name} arrêté")
    
    @abstractmethod
    async def think(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Phase de réflexion: analyse la tâche et planifie l'action.
        
        Args:
            task: Tâche à analyser
        
        Returns:
            Plan d'action
        """
        pass
    
    @abstractmethod
    async def act(self, action_plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Phase d'action: exécute le plan.
        
        Args:
            action_plan: Plan d'action à exécuter
        
        Returns:
            Résultat de l'action
        """
        pass
    
    async def learn(self, result: Dict[str, Any]):
        """
        Phase d'apprentissage: apprend de l'expérience.
        
        Args:
            result: Résultat de l'action
        """
        self.status = AgentStatus.LEARNING
        
        # Stocker l'expérience en mémoire
        experience = {
            "timestamp": datetime.now().isoformat(),
            "result": result,
            "success": result.get("success", False),
        }
        self.memory.add_to_short_term(experience)
        
        # Mettre à jour les stats
        if result.get("success"):
            self.stats["tasks_completed"] += 1
        else:
            self.stats["tasks_failed"] += 1
        
        logger.debug(f"📚 Agent {self.name} a appris de l'expérience")
    
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Exécute une tâche complète (think -> act -> learn).
        
        Args:
            task: Tâche à exécuter
        
        Returns:
            Résultat de la tâche
        """
        try:
            logger.info(f"🎯 Agent {self.name} commence la tâche: {task.get('description', 'Sans description')}")
            
            # Phase 1: Réflexion
            self.status = AgentStatus.THINKING
            action_plan = await self.think(task)
            
            # Phase 2: Action
            self.status = AgentStatus.ACTING
            result = await self.act(action_plan)
            
            # Phase 3: Apprentissage
            await self.learn(result)
            
            self.status = AgentStatus.IDLE
            logger.success(f"✅ Agent {self.name} a terminé la tâche")
            
            return result
        
        except Exception as e:
            self.status = AgentStatus.ERROR
            logger.error(f"❌ Erreur dans l'agent {self.name}: {e}")
            
            error_result = {
                "success": False,
                "error": str(e),
                "agent_id": self.agent_id,
            }
            await self.learn(error_result)
            
            return error_result
    
    async def send_message(self, content: str, receiver_id: Optional[str] = None, metadata: Optional[Dict] = None):
        """
        Envoie un message à un autre agent ou en broadcast.
        
        Args:
            content: Contenu du message
            receiver_id: ID du destinataire (None = broadcast)
            metadata: Métadonnées additionnelles
        """
        message = AgentMessage(
            sender_id=self.agent_id,
            receiver_id=receiver_id,
            content=content,
            metadata=metadata or {}
        )
        self.stats["messages_sent"] += 1
        logger.debug(f"📤 {self.name} envoie un message: {content[:50]}...")
        return message
    
    async def receive_message(self, message: AgentMessage):
        """
        Reçoit un message d'un autre agent.
        
        Args:
            message: Message reçu
        """
        await self.message_queue.put(message)
        self.stats["messages_received"] += 1
        logger.debug(f"📥 {self.name} reçoit un message de {message.sender_id}")
    
    async def generate_response(self, prompt: str, system: Optional[str] = None) -> str:
        """
        Génère une réponse avec le LLM.
        
        Args:
            prompt: Prompt à envoyer
            system: Message système optionnel
        
        Returns:
            Réponse générée
        """
        if not self.llm_client:
            raise RuntimeError(f"Agent {self.name} n'est pas initialisé")
        
        # Utiliser le prompt système par défaut si non fourni
        if system is None:
            system = PromptTemplates.get_system_prompt(self.agent_type)
        
        response = await self.llm_client.generate(
            prompt=prompt,
            system=system,
            model=self.model,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )
        
        return response
    
    def get_status(self) -> Dict[str, Any]:
        """Retourne l'état actuel de l'agent."""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "type": self.agent_type,
            "status": self.status.value,
            "stats": self.stats,
            "memory_size": len(self.memory.short_term) + len(self.memory.long_term),
        }
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.name} ({self.status.value})>"
