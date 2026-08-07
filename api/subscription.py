from datetime import datetime, date
from typing import Dict, Any, Optional
from core.database import get_db
import uuid

# Configuration des limites
# Format: { 'tier': { 'feature': { 'limit': N, 'period': 'day'|'month'|'total' } } }
SUBSCRIPTION_LIMITS = {
    'FREE': {
        'sniper_search': {'limit': 2, 'period': 'day'},
        'cv_audit': {'limit': 5, 'period': 'total'},
        'hr_interview': {'limit': 1, 'period': 'total'},
        'follow_up': {'limit': 10, 'period': 'total'},
        'cv_adaptation': {'limit': 5, 'period': 'total'},
        'cover_letter': {'limit': 2, 'period': 'total'},
        'headhunter': {'limit': 0, 'period': 'total'},
        'address_book': {'limit': 0, 'period': 'total'},
        'portfolio': {'limit': 0, 'period': 'total'},
        'network_access': {'limit': 0, 'period': 'total'},
        'auto_apply': {'limit': 0, 'period': 'total'},
        'post_interview': {'limit': 0, 'period': 'total'},
        'morning_sourcing': {'limit': 0, 'period': 'total'},
        'sniper_apply': {'limit': 0, 'period': 'total'},
    },
    'ESSENTIAL': {
        'sniper_search': {'limit': 99999, 'period': 'month'},
        'cv_audit': {'limit': 99999, 'period': 'month'},
        'hr_interview': {'limit': 99999, 'period': 'month'},
        'follow_up': {'limit': 99999, 'period': 'month'},
        'cv_adaptation': {'limit': 99999, 'period': 'month'},
        'cover_letter': {'limit': 99999, 'period': 'month'},
        'headhunter': {'limit': 99999, 'period': 'month'},
        'address_book': {'limit': 99999, 'period': 'total'},
        'portfolio': {'limit': 99999, 'period': 'total'},
        'network_access': {'limit': 99999, 'period': 'total'},
        'auto_apply': {'limit': 99999, 'period': 'total'},
        'post_interview': {'limit': 99999, 'period': 'total'},
        'morning_sourcing': {'limit': 99999, 'period': 'total'},
        'sniper_apply': {'limit': 99999, 'period': 'day'},
    },
    'PRO': {
        'sniper_search': {'limit': 99999, 'period': 'month'},
        'cv_audit': {'limit': 99999, 'period': 'month'},
        'hr_interview': {'limit': 99999, 'period': 'month'},
        'follow_up': {'limit': 99999, 'period': 'month'},
        'cv_adaptation': {'limit': 99999, 'period': 'month'},
        'cover_letter': {'limit': 99999, 'period': 'month'},
        'headhunter': {'limit': 99999, 'period': 'month'},
        'address_book': {'limit': 99999, 'period': 'total'},
        'portfolio': {'limit': 99999, 'period': 'total'},
        'network_access': {'limit': 99999, 'period': 'total'},
        'auto_apply': {'limit': 99999, 'period': 'total'},
        'post_interview': {'limit': 99999, 'period': 'total'},
        'morning_sourcing': {'limit': 99999, 'period': 'total'},
        'sniper_apply': {'limit': 99999, 'period': 'day'},
    },
    'ADMIN': {
        'sniper_search': {'limit': 999999, 'period': 'month'},
        'cv_audit': {'limit': 999999, 'period': 'month'},
        'hr_interview': {'limit': 999999, 'period': 'month'},
        'follow_up': {'limit': 999999, 'period': 'month'},
        'cv_adaptation': {'limit': 999999, 'period': 'month'},
        'cover_letter': {'limit': 999999, 'period': 'month'},
        'headhunter': {'limit': 999999, 'period': 'month'},
        'address_book': {'limit': 999999, 'period': 'total'},
        'portfolio': {'limit': 999999, 'period': 'total'},
        'network_access': {'limit': 999999, 'period': 'total'},
        'auto_apply': {'limit': 999999, 'period': 'total'},
        'post_interview': {'limit': 999999, 'period': 'total'},
        'morning_sourcing': {'limit': 999999, 'period': 'total'},
        'sniper_apply': {'limit': 999999, 'period': 'day'},
    }
}

async def check_subscription_limit(user_id: str, feature: str) -> Dict[str, Any]:
    """
    Vérifie l'accès à une fonctionnalité :
    1. Déverrouillage par forfait (certaines fonctions réservées Essentiel/Pro).
    2. Coût en Gold (le solde doit couvrir le coût).
    ADMIN : accès total gratuit.
    Retourne {'allowed', 'current', 'limit', 'message', 'mode'?, 'need_upgrade'?, 'required_tier'?}
    """
    db = get_db()
    try:
        user = await db.users.find_one({"id": user_id})
        tier = user.get('subscription_tier', 'FREE') if user else 'FREE'

        if tier == 'ADMIN':
            return {'allowed': True, 'current': 0, 'limit': 999999}

        from core.gold import GOLD_COSTS, FEATURE_MIN_TIER, TIER_RANK, get_balance

        # 1. Déverrouillage par forfait
        min_tier = FEATURE_MIN_TIER.get(feature)
        if min_tier and TIER_RANK.get(tier, 0) < TIER_RANK.get(min_tier, 99):
            return {
                'allowed': False, 'need_upgrade': True, 'required_tier': min_tier,
                'message': f"Fonctionnalité réservée au forfait {min_tier}. Améliorez votre abonnement pour la débloquer."
            }

        # 2. Coût en Gold
        cost = GOLD_COSTS.get(feature)
        if not cost:
            return {'allowed': True}  # fonctionnalité gratuite (non facturée)
        balance = await get_balance(user_id)
        if balance < cost:
            return {
                'allowed': False, 'current': balance, 'limit': cost, 'mode': 'gold',
                'message': f"Gold insuffisant ({balance}/{cost}). Rechargez dans la Boutique pour continuer."
            }
        return {'allowed': True, 'current': balance, 'limit': cost, 'mode': 'gold'}
    except Exception as e:
        from loguru import logger
        logger.error(f"Erreur vérification accès: {e}")
        return {'allowed': False, 'message': "Erreur interne de vérification de l'accès."}


async def log_usage(user_id: str, feature: str, count: int = 1):
    """Consomme le Gold correspondant à l'usage (sauf ADMIN)."""
    db = get_db()
    try:
        user = await db.users.find_one({"id": user_id}, {"_id": 0, "subscription_tier": 1})
        if (user or {}).get('subscription_tier') == 'ADMIN':
            return
        from core.gold import GOLD_COSTS, spend_gold
        cost = GOLD_COSTS.get(feature)
        if cost:
            await spend_gold(user_id, cost * max(1, count), f"feature:{feature}")
    except Exception as e:
        from loguru import logger
        logger.error(f"Erreur consommation Gold: {e}")
