from datetime import datetime, date
from typing import Dict, Any, Optional
from core.database import get_db
import uuid

# Configuration des limites
# Format: { 'tier': { 'feature': { 'limit': N, 'period': 'day'|'month'|'total' } } }
SUBSCRIPTION_LIMITS = {
    'FREE': {
        'sniper_search': {'limit': 2, 'period': 'day'},
        'cv_audit': {'limit': 2, 'period': 'day'},
        'hr_interview': {'limit': 1, 'period': 'day'},
        'follow_up': {'limit': 5, 'period': 'day'},
        'cv_adaptation': {'limit': 3, 'period': 'day'},
        'headhunter': {'limit': 0, 'period': 'total'},
        'address_book': {'limit': 0, 'period': 'total'},
    },
    'ESSENTIAL': {
        'sniper_search': {'limit': 25, 'period': 'month'},
        'cv_audit': {'limit': 10, 'period': 'month'},
        'hr_interview': {'limit': 10, 'period': 'month'},
        'follow_up': {'limit': 9999, 'period': 'month'}, # Illimité en pratique
        'cv_adaptation': {'limit': 9999, 'period': 'month'},
        'headhunter': {'limit': 10, 'period': 'month'},
        'address_book': {'limit': 25, 'period': 'total'},
    },
    'PRO': {
        'sniper_search': {'limit': 99999, 'period': 'month'},
        'cv_audit': {'limit': 20, 'period': 'month'},
        'hr_interview': {'limit': 15, 'period': 'month'},
        'follow_up': {'limit': 99999, 'period': 'month'},
        'cv_adaptation': {'limit': 99999, 'period': 'month'},
        'headhunter': {'limit': 99999, 'period': 'month'},
        'address_book': {'limit': 99999, 'period': 'total'},
    },
    'ADMIN': {
        'sniper_search': {'limit': 999999, 'period': 'month'},
        'cv_audit': {'limit': 999999, 'period': 'month'},
        'hr_interview': {'limit': 999999, 'period': 'month'},
        'follow_up': {'limit': 999999, 'period': 'month'},
        'cv_adaptation': {'limit': 999999, 'period': 'month'},
        'headhunter': {'limit': 999999, 'period': 'month'},
        'address_book': {'limit': 999999, 'period': 'total'},
    }
}

async def check_subscription_limit(user_id: str, feature: str) -> Dict[str, Any]:
    """
    Vérifie si un utilisateur a atteint sa limite pour une fonctionnalité donnée.
    Retourne {'allowed': bool, 'current': int, 'limit': int, 'message': str}
    """
    db = get_db()
    try:
        # 1. Récupérer le tier de l'utilisateur
        user = await db.users.find_one({"id": user_id})
        tier = user.get('subscription_tier', 'FREE') if user else 'FREE'
        
        # Bypass pour l'ADMIN
        if tier == 'ADMIN':
            return {'allowed': True, 'current': 0, 'limit': 999999}

        limits = SUBSCRIPTION_LIMITS.get(tier, SUBSCRIPTION_LIMITS['FREE'])
        config = limits.get(feature)
        
        if not config:
            return {'allowed': True} # Feature non limitée
            
        limit = config['limit']
        period = config['period']
        
        # 2. Compter l'usage actuel
        count = 0
        
        if period == 'day':
            today_str = date.today().isoformat()
            pipeline = [
                {"$match": {"user_id": user_id, "feature": feature, "used_at": today_str}},
                {"$group": {"_id": None, "total": {"$sum": "$count"}}}
            ]
            result = await db.usage_logs.aggregate(pipeline).to_list(length=1)
            count = result[0]["total"] if result else 0

        elif period == 'month':
            month_str = date.today().strftime("%Y-%m")
            pipeline = [
                {"$match": {
                    "user_id": user_id, 
                    "feature": feature, 
                    "used_at": {"$regex": f"^{month_str}"}
                }},
                {"$group": {"_id": None, "total": {"$sum": "$count"}}}
            ]
            result = await db.usage_logs.aggregate(pipeline).to_list(length=1)
            count = result[0]["total"] if result else 0

        elif period == 'total':
             # Cas spécial pour address_book qui compte les lignes réelles
            if feature == 'address_book':
                count = await db.contacts.count_documents({"user_id": user_id})
            else:
                pipeline = [
                    {"$match": {"user_id": user_id, "feature": feature}},
                    {"$group": {"_id": None, "total": {"$sum": "$count"}}}
                ]
                result = await db.usage_logs.aggregate(pipeline).to_list(length=1)
                count = result[0]["total"] if result else 0

        if count >= limit:
            return {
                'allowed': False,
                'current': count,
                'limit': limit,
                'message': f"Limite atteinte pour {feature} ({count}/{limit}). Passez au forfait supérieur !"
            }
            
        return {'allowed': True, 'current': count, 'limit': limit}
    except Exception as e:
        from loguru import logger
        logger.error(f"Erreur vérification limite: {e}")
        return {'allowed': False, 'message': 'Erreur interne de vérification des limites.'}

async def log_usage(user_id: str, feature: str, count: int = 1):
    """Enregistre une utilisation de fonctionnalité."""
    db = get_db()
    try:
        today_str = date.today().isoformat()
        
        # Upsert: if a log for today exists, increment it. Otherwise, create it.
        await db.usage_logs.update_one(
            {"user_id": user_id, "feature": feature, "used_at": today_str},
            {
                "$inc": {"count": count},
                "$setOnInsert": {"id": str(uuid.uuid4())}
            },
            upsert=True
        )
    except Exception as e:
        from loguru import logger
        logger.error(f"Erreur lors de l'enregistrement de l'utilisation SaaS: {e}")
