"""
Cache Redis pour GoldArmy — Fallback gracieux si Redis est absent.
Si Redis n'est pas disponible, le système continue sans cache (pas de crash).
"""
import hashlib
import json
from typing import Any, Optional
from loguru import logger


class RedisCache:
    """Cache Redis avec fallback silencieux."""

    def __init__(self):
        self._client = None
        self._available = False
        self._init_attempted = False

    async def _init(self):
        """Initialisation paresseuse — ne crée la connexion qu'au premier appel."""
        if self._init_attempted:
            return
        self._init_attempted = True
        try:
            import redis.asyncio as aioredis
            from config.settings import settings

            url = settings.redis_url or f"redis://{settings.redis_host}:{settings.redis_port}/{settings.redis_db}"
            self._client = aioredis.from_url(url, socket_connect_timeout=2, socket_timeout=2)
            # Test de connexion
            await self._client.ping()
            self._available = True
            logger.info(f"Redis cache connecte: {url}")
        except Exception as e:
            self._available = False
            logger.warning(f"Redis non disponible (mode sans cache): {e}")

    @staticmethod
    def make_key(*args) -> str:
        """Génère une clé de cache MD5 à partir des arguments."""
        raw = "|".join(str(a) for a in args).lower().strip()
        return f"goldarmy:sniper:{hashlib.md5(raw.encode()).hexdigest()}"

    async def get(self, key: str) -> Optional[Any]:
        """Récupère une valeur du cache. Retourne None si absente ou Redis down."""
        await self._init()
        if not self._available:
            return None
        try:
            raw = await self._client.get(key)
            if raw:
                logger.debug(f"Cache HIT: {key[:40]}...")
                return json.loads(raw)
            return None
        except Exception as e:
            logger.debug(f"Cache GET error: {e}")
            return None

    async def set(self, key: str, value: Any, ttl: int = 10800) -> bool:
        """
        Stocke une valeur en cache.
        ttl = 10800 secondes (3 heures) par défaut.
        """
        await self._init()
        if not self._available:
            return False
        try:
            await self._client.setex(key, ttl, json.dumps(value, default=str))
            logger.debug(f"Cache SET: {key[:40]}... (TTL={ttl}s)")
            return True
        except Exception as e:
            logger.debug(f"Cache SET error: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Invalide une entrée du cache."""
        await self._init()
        if not self._available:
            return False
        try:
            await self._client.delete(key)
            return True
        except Exception:
            return False

    async def close(self):
        if self._client:
            try:
                await self._client.aclose()
            except Exception:
                pass


# Instance globale partagée
cache = RedisCache()
