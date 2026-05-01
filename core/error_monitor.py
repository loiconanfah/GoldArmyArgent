"""
Monitoring d'erreurs — stockage dans MongoDB Atlas (100% gratuit).
Remplace Sentry pour les projets qui ont déjà MongoDB.

Usage:
    from core.error_monitor import monitor
    monitor.capture(exc, context={"user_id": "...", "route": "..."})
"""
import traceback
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from loguru import logger


class ErrorMonitor:
    """Enregistre les exceptions dans la collection MongoDB 'error_logs'."""

    _MAX_STACK_LEN = 4000  # Tronquer les stack traces trop longues

    async def capture(
        self,
        exc: Exception,
        context: Optional[Dict[str, Any]] = None,
        level: str = "error",
    ) -> Optional[str]:
        """
        Capture une exception et la sauvegarde dans MongoDB.
        Retourne l'ID du document créé, ou None si échec.
        """
        try:
            from core.database import get_db
            db = get_db()

            stack = traceback.format_exc()
            if len(stack) > self._MAX_STACK_LEN:
                stack = stack[-self._MAX_STACK_LEN:]  # Garder la fin (le plus utile)

            doc = {
                "level": level,
                "error_type": type(exc).__name__,
                "message": str(exc)[:500],
                "stack_trace": stack,
                "context": context or {},
                "timestamp": datetime.now(timezone.utc),
                "resolved": False,
            }

            result = await db.error_logs.insert_one(doc)
            logger.debug(f"[Monitor] Erreur capturee: {type(exc).__name__} — ID: {result.inserted_id}")
            return str(result.inserted_id)
        except Exception as monitor_err:
            # Le monitoring ne doit JAMAIS faire crasher l'app
            logger.warning(f"[Monitor] Echec capture erreur: {monitor_err}")
            return None

    async def get_recent(self, limit: int = 50, level: str = None) -> list:
        """Récupère les erreurs récentes (pour un dashboard admin)."""
        try:
            from core.database import get_db
            db = get_db()
            query = {}
            if level:
                query["level"] = level
            cursor = db.error_logs.find(query, {"_id": 1, "level": 1, "error_type": 1, "message": 1, "timestamp": 1, "context": 1, "resolved": 1}) \
                                   .sort("timestamp", -1).limit(limit)
            docs = await cursor.to_list(length=limit)
            for d in docs:
                d["_id"] = str(d["_id"])
            return docs
        except Exception as e:
            logger.warning(f"[Monitor] get_recent failed: {e}")
            return []

    async def resolve(self, error_id: str) -> bool:
        """Marque une erreur comme résolue."""
        try:
            from bson import ObjectId
            from core.database import get_db
            db = get_db()
            await db.error_logs.update_one(
                {"_id": ObjectId(error_id)},
                {"$set": {"resolved": True, "resolved_at": datetime.now(timezone.utc)}}
            )
            return True
        except Exception:
            return False


# Instance globale
monitor = ErrorMonitor()
