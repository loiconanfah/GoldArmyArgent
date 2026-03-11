"""
Core Database Manager pour GoldArmy Agent V2 (MongoDB Atlas).
Fournit une connexion asynchrone centralisée via motor et initialise les index.
"""
import os
from loguru import logger
from motor.motor_asyncio import AsyncIOMotorClient
from config.settings import settings

# Global MongoDB Client
_client = None

def get_db_client():
    """Initialise et retourne le client MongoDB global."""
    global _client
    if _client is None:
        try:
            _client = AsyncIOMotorClient(
                settings.mongodb_uri,
                serverSelectionTimeoutMS=5000,
                tz_aware=True,
                tlsAllowInvalidCertificates=True
            )
            logger.info("✅ Client MongoDB Atlas initialisé!")
        except Exception as e:
            logger.error(f"❌ Erreur de connexion MongoDB: {e}")
            raise
    return _client

def get_db():
    """Retourne l'instance de la base de données configurée."""
    client = get_db_client()
    return client[settings.mongodb_db_name]

async def init_db():
    """Initialise les index critiques pour la base MongoDB."""
    logger.info("🗄️ Initialisation des index MongoDB (SaaS)...")
    db = get_db()
    
    try:
        # Index Collections Users
        await db.users.create_index("email", unique=True)
        await db.users.create_index("google_id")
        
        # Index Collections Contacts (CRM OSINT)
        await db.contacts.create_index("user_id")
        await db.contacts.create_index([("user_id", 1), ("company_name", 1)])
        
        # Index Collections Applications (Suivi Candidatures)
        await db.applications.create_index("user_id")
        
        # Index Collections Usage Logs (SaaS Limits Enforcement)
        await db.usage_logs.create_index("user_id")
        await db.usage_logs.create_index([("user_id", 1), ("feature", 1), ("used_at", 1)])
        
        # Index Collections Interview Sessions (History + Free Tier Gating)
        await db.interview_sessions.create_index("user_id")
        await db.interview_sessions.create_index([("user_id", 1), ("created_at", -1)])
        
        logger.info("✅ Index MongoDB vérifiés et créés avec succès.")
    except Exception as e:
        logger.error(f"❌ Erreur lors de la création des index MongoDB: {e}")

# Note: In a fully async FastAPI app, init_db() should be called in the lifespan event of main.py
