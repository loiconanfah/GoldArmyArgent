"""Bus de communication asynchrone entre agents."""
import asyncio
from typing import Any, Callable, Dict, List, Optional, Set
from datetime import datetime

from loguru import logger
from pydantic import BaseModel

from core.agent_base import AgentMessage


class CommunicationBus:
    """Bus de communication pub/sub pour les agents."""
    
    def __init__(self):
        """Initialise le bus de communication."""
        self.subscribers: Dict[str, Set[Callable]] = {}
        self.message_history: List[AgentMessage] = []
        self.max_history = 1000
        
        logger.info("📡 Bus de communication initialisé")
    
    def subscribe(self, topic: str, callback: Callable):
        """
        S'abonne à un topic.
        
        Args:
            topic: Nom du topic
            callback: Fonction de callback async
        """
        if topic not in self.subscribers:
            self.subscribers[topic] = set()
        
        self.subscribers[topic].add(callback)
        logger.debug(f"📌 Nouvel abonné au topic '{topic}'")
    
    def unsubscribe(self, topic: str, callback: Callable):
        """
        Se désabonne d'un topic.
        
        Args:
            topic: Nom du topic
            callback: Fonction de callback
        """
        if topic in self.subscribers:
            self.subscribers[topic].discard(callback)
            logger.debug(f"📍 Désabonnement du topic '{topic}'")
    
    async def publish(self, topic: str, message: AgentMessage):
        """
        Publie un message sur un topic.
        
        Args:
            topic: Nom du topic
            message: Message à publier
        """
        logger.debug(f"📢 Publication sur '{topic}': {message.content[:50]}...")
        
        # Stocker dans l'historique
        self.message_history.append(message)
        if len(self.message_history) > self.max_history:
            self.message_history = self.message_history[-self.max_history:]
        
        # Notifier les abonnés
        if topic in self.subscribers:
            tasks = []
            for callback in self.subscribers[topic]:
                tasks.append(callback(message))
            
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
    
    async def send_direct(self, message: AgentMessage, receiver_callback: Callable):
        """
        Envoie un message direct à un agent.
        
        Args:
            message: Message à envoyer
            receiver_callback: Callback du destinataire
        """
        logger.debug(f"📨 Message direct de {message.sender_id} à {message.receiver_id}")
        
        self.message_history.append(message)
        if len(self.message_history) > self.max_history:
            self.message_history = self.message_history[-self.max_history:]
        
        await receiver_callback(message)
    
    def get_history(
        self,
        sender_id: Optional[str] = None,
        receiver_id: Optional[str] = None,
        limit: int = 50
    ) -> List[AgentMessage]:
        """
        Récupère l'historique des messages.
        
        Args:
            sender_id: Filtrer par expéditeur
            receiver_id: Filtrer par destinataire
            limit: Nombre maximum de messages
        
        Returns:
            Liste de messages
        """
        filtered = self.message_history
        
        if sender_id:
            filtered = [m for m in filtered if m.sender_id == sender_id]
        
        if receiver_id:
            filtered = [m for m in filtered if m.receiver_id == receiver_id]
        
        return filtered[-limit:]
    
    def get_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques du bus."""
        return {
            "total_messages": len(self.message_history),
            "topics": list(self.subscribers.keys()),
            "total_subscribers": sum(len(subs) for subs in self.subscribers.values()),
        }
    
    def clear_history(self):
        """Efface l'historique des messages."""
        self.message_history.clear()
        logger.info("🗑️ Historique des messages effacé")


# Instance globale
communication_bus = CommunicationBus()
