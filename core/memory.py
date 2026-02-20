"""Système de mémoire partagée pour les agents."""
import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional
from pathlib import Path

from loguru import logger

try:
    import chromadb
    from chromadb.config import Settings as ChromaSettings
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False
    logger.warning("ChromaDB non disponible - mémoire vectorielle désactivée")

from config.settings import settings


class MemorySystem:
    """Système de mémoire partagée entre agents."""
    
    def __init__(self, persist_dir: Optional[Path] = None):
        """
        Initialise le système de mémoire.
        
        Args:
            persist_dir: Répertoire de persistance ChromaDB
        """
        self.persist_dir = persist_dir or settings.chroma_persist_dir
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        
        # Mémoire en RAM (toujours disponible)
        self.ram_memory: Dict[str, List[Dict[str, Any]]] = {}
        self.shared_context: Dict[str, Any] = {}
        
        # ChromaDB (optionnel)
        self.chroma_client = None
        self.collection = None
        
        if CHROMA_AVAILABLE:
            self._init_chromadb()
        
        logger.info(f"💾 Système de mémoire initialisé (ChromaDB: {CHROMA_AVAILABLE})")
    
    def _init_chromadb(self):
        """Initialise ChromaDB."""
        try:
            self.chroma_client = chromadb.PersistentClient(
                path=str(self.persist_dir),
                settings=ChromaSettings(anonymized_telemetry=False)
            )
            
            # Créer ou récupérer la collection
            self.collection = self.chroma_client.get_or_create_collection(
                name="agent_memory",
                metadata={"description": "Mémoire partagée des agents"}
            )
            
            logger.success("✅ ChromaDB initialisé")
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'initialisation de ChromaDB: {e}")
            self.chroma_client = None
            self.collection = None
    
    async def store(
        self,
        agent_id: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        use_vector: bool = True
    ):
        """
        Stocke une information en mémoire.
        
        Args:
            agent_id: ID de l'agent
            content: Contenu à stocker
            metadata: Métadonnées additionnelles
            use_vector: Utiliser la base vectorielle si disponible
        """
        memory_item = {
            "agent_id": agent_id,
            "content": content,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat(),
        }
        
        # Stocker en RAM
        if agent_id not in self.ram_memory:
            self.ram_memory[agent_id] = []
        self.ram_memory[agent_id].append(memory_item)
        
        # Stocker dans ChromaDB si disponible
        if use_vector and self.collection:
            try:
                doc_id = f"{agent_id}_{datetime.now().timestamp()}"
                self.collection.add(
                    documents=[content],
                    metadatas=[{
                        "agent_id": agent_id,
                        "timestamp": memory_item["timestamp"],
                        **(metadata or {})
                    }],
                    ids=[doc_id]
                )
                logger.debug(f"💾 Mémoire vectorielle stockée pour {agent_id}")
            except Exception as e:
                logger.error(f"Erreur lors du stockage vectoriel: {e}")
    
    async def retrieve(
        self,
        agent_id: str,
        n_results: int = 5,
        use_vector: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Récupère les souvenirs d'un agent.
        
        Args:
            agent_id: ID de l'agent
            n_results: Nombre de résultats à retourner
            use_vector: Utiliser la recherche vectorielle
        
        Returns:
            Liste de souvenirs
        """
        if use_vector and self.collection:
            try:
                results = self.collection.get(
                    where={"agent_id": agent_id},
                    limit=n_results
                )
                return [
                    {
                        "content": doc,
                        "metadata": meta
                    }
                    for doc, meta in zip(results["documents"], results["metadatas"])
                ]
            except Exception as e:
                logger.error(f"Erreur lors de la récupération vectorielle: {e}")
        
        # Fallback sur RAM
        memories = self.ram_memory.get(agent_id, [])
        return memories[-n_results:] if memories else []
    
    async def search(
        self,
        query: str,
        n_results: int = 5,
        agent_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Recherche sémantique dans la mémoire.
        
        Args:
            query: Requête de recherche
            n_results: Nombre de résultats
            agent_id: Filtrer par agent (optionnel)
        
        Returns:
            Résultats de recherche
        """
        if not self.collection:
            logger.warning("Recherche vectorielle non disponible")
            return []
        
        try:
            where_filter = {"agent_id": agent_id} if agent_id else None
            
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=where_filter
            )
            
            if not results["documents"] or not results["documents"][0]:
                return []
            
            return [
                {
                    "content": doc,
                    "metadata": meta,
                    "distance": dist
                }
                for doc, meta, dist in zip(
                    results["documents"][0],
                    results["metadatas"][0],
                    results["distances"][0]
                )
            ]
        except Exception as e:
            logger.error(f"Erreur lors de la recherche: {e}")
            return []
    
    async def set_shared_context(self, key: str, value: Any):
        """
        Définit un contexte partagé entre tous les agents.
        
        Args:
            key: Clé du contexte
            value: Valeur
        """
        self.shared_context[key] = {
            "value": value,
            "timestamp": datetime.now().isoformat(),
        }
        logger.debug(f"🔄 Contexte partagé mis à jour: {key}")
    
    async def get_shared_context(self, key: str) -> Optional[Any]:
        """
        Récupère un contexte partagé.
        
        Args:
            key: Clé du contexte
        
        Returns:
            Valeur du contexte ou None
        """
        context = self.shared_context.get(key)
        return context["value"] if context else None
    
    async def clear_agent_memory(self, agent_id: str):
        """
        Efface la mémoire d'un agent.
        
        Args:
            agent_id: ID de l'agent
        """
        # Effacer RAM
        if agent_id in self.ram_memory:
            del self.ram_memory[agent_id]
        
        # Effacer ChromaDB
        if self.collection:
            try:
                self.collection.delete(where={"agent_id": agent_id})
                logger.info(f"🗑️ Mémoire de {agent_id} effacée")
            except Exception as e:
                logger.error(f"Erreur lors de l'effacement: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques de la mémoire."""
        ram_count = sum(len(memories) for memories in self.ram_memory.values())
        
        vector_count = 0
        if self.collection:
            try:
                vector_count = self.collection.count()
            except:
                pass
        
        return {
            "ram_memories": ram_count,
            "vector_memories": vector_count,
            "agents_tracked": len(self.ram_memory),
            "shared_contexts": len(self.shared_context),
            "chroma_available": CHROMA_AVAILABLE,
        }


# Instance globale
memory_system = MemorySystem()
