from datetime import datetime, date
from typing import Dict, Any, Optional
from core.database import get_db_connection
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
    }
}

async def check_subscription_limit(user_id: str, feature: str) -> Dict[str, Any]:
    """
    Vérifie si un utilisateur a atteint sa limite pour une fonctionnalité donnée.
    Retourne {'allowed': bool, 'current': int, 'limit': int, 'message': str}
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        # 1. Récupérer le tier de l'utilisateur
        cursor.execute("SELECT subscription_tier FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        tier = row['subscription_tier'] if row else 'FREE'
        
        limits = SUBSCRIPTION_LIMITS.get(tier, SUBSCRIPTION_LIMITS['FREE'])
        config = limits.get(feature)
        
        if not config:
            return {'allowed': True} # Feature non limitée
            
        limit = config['limit']
        period = config['period']
        
        # 2. Compter l'usage actuel
        count = 0
        if period == 'day':
            cursor.execute(
                "SELECT SUM(count) FROM usage_logs WHERE user_id = ? AND feature = ? AND used_at = CURRENT_DATE",
                (user_id, feature)
            )
            res = cursor.fetchone()
            count = res[0] or 0
        elif period == 'month':
            # Format YYYY-MM
            month_str = date.today().strftime("%Y-%m") + "%"
            cursor.execute(
                "SELECT SUM(count) FROM usage_logs WHERE user_id = ? AND feature = ? AND used_at LIKE ?",
                (user_id, feature, month_str)
            )
            res = cursor.fetchone()
            count = res[0] or 0
        elif period == 'total':
             # Cas spécial pour address_book qui compte les lignes réelles
            if feature == 'address_book':
                cursor.execute("SELECT COUNT(*) FROM contacts WHERE user_id = ?", (user_id,))
                count = cursor.fetchone()[0]
            else:
                cursor.execute(
                    "SELECT SUM(count) FROM usage_logs WHERE user_id = ? AND feature = ?",
                    (user_id, feature)
                )
                res = cursor.fetchone()
                count = res[0] or 0

        if count >= limit:
            return {
                'allowed': False,
                'current': count,
                'limit': limit,
                'message': f"Limite atteinte pour {feature} ({count}/{limit}). Passez au forfait supérieur !"
            }
            
        return {'allowed': True, 'current': count, 'limit': limit}
    finally:
        conn.close()

async def log_usage(user_id: str, feature: str, count: int = 1):
    """Enregistre une utilisation de fonctionnalité."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        log_id = str(uuid.uuid4())
        # On vérifie s'il existe déjà une ligne pour aujourd'hui pour ce user/feature
        cursor.execute(
            "SELECT id, count FROM usage_logs WHERE user_id = ? AND feature = ? AND used_at = CURRENT_DATE",
            (user_id, feature)
        )
        row = cursor.fetchone()
        if row:
            cursor.execute(
                "UPDATE usage_logs SET count = count + ? WHERE id = ?",
                (count, row['id'])
            )
        else:
            cursor.execute(
                "INSERT INTO usage_logs (id, user_id, feature, count, used_at) VALUES (?, ?, ?, ?, CURRENT_DATE)",
                (log_id, user_id, feature, count)
            )
        conn.commit()
    finally:
        conn.close()
