"""
Économie de jetons « Gold ».

Le Gold est un crédit consommable : gagné (inscription, recharge mensuelle,
parrainage, packs boutique, sponsoring organisation) et dépensé à chaque usage
de fonctionnalité. Remplace progressivement le gating par abonnement.

Solde stocké sur users.gold_balance (initialisé depuis l'ancien bonus_credits).
Journal des mouvements dans la collection gold_transactions.
"""
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from core.database import get_db

GOLD_SIGNUP_BONUS = 50
GOLD_MONTHLY_FREE = 20

# Packs vendus en boutique (paiement unique). Prix en EUR.
GOLD_PACKS: List[Dict[str, Any]] = [
    {"key": "discovery", "name": "Découverte", "gold": 100, "price_eur": 4.99},
    {"key": "popular", "name": "Populaire", "gold": 300, "price_eur": 12.99, "badge": "best", "bonus": 20},
    {"key": "pro", "name": "Pro", "gold": 750, "price_eur": 24.99, "bonus": 100},
    {"key": "mega", "name": "Méga", "gold": 2000, "price_eur": 59.99, "bonus": 400},
]
PACK_BY_KEY = {p["key"]: p for p in GOLD_PACKS}

# Coût en Gold par fonctionnalité (à caler sur le coût marginal réel).
GOLD_COSTS: Dict[str, int] = {
    "cv_audit": 3,
    "follow_up": 2,
    "cover_letter": 4,
    "sniper_search": 5,
    "cv_adaptation": 8,
    "headhunter": 8,
    "hr_interview": 10,
    "network_access": 5,
    "portfolio": 15,
    "sniper_apply": 20,
}


def pack_total_gold(pack: Dict[str, Any]) -> int:
    return int(pack.get("gold", 0)) + int(pack.get("bonus", 0))


async def get_balance(user_id: str) -> int:
    """Solde Gold. Migre paresseusement l'ancien bonus_credits au premier accès."""
    db = get_db()
    u = await db.users.find_one({"id": user_id}, {"_id": 0, "gold_balance": 1, "bonus_credits": 1})
    if not u:
        return 0
    if "gold_balance" in u and u["gold_balance"] is not None:
        return int(u["gold_balance"])
    seed = int(u.get("bonus_credits", 0) or 0)
    await db.users.update_one({"id": user_id}, {"$set": {"gold_balance": seed}})
    return seed


async def _log(user_id: str, tx_type: str, amount: int, reason: str, balance_after: int, meta: Optional[dict] = None):
    db = get_db()
    await db.gold_transactions.insert_one({
        "user_id": user_id,
        "type": tx_type,          # "grant" | "spend"
        "amount": int(amount),
        "reason": reason,          # ex: "signup", "pack:popular", "feature:cv_adaptation", "org_monthly"
        "balance_after": int(balance_after),
        "meta": meta or {},
        "created_at": datetime.now(timezone.utc),
    })


async def grant_gold(user_id: str, amount: int, reason: str, meta: Optional[dict] = None) -> int:
    """Crédite du Gold et journalise. Retourne le nouveau solde."""
    if amount <= 0:
        return await get_balance(user_id)
    db = get_db()
    await get_balance(user_id)  # garantit l'existence du champ
    doc = await db.users.find_one_and_update(
        {"id": user_id}, {"$inc": {"gold_balance": int(amount)}}, return_document=True
    )
    new_balance = int((doc or {}).get("gold_balance", amount))
    await _log(user_id, "grant", amount, reason, new_balance, meta)
    return new_balance


async def spend_gold(user_id: str, amount: int, reason: str, meta: Optional[dict] = None) -> Dict[str, Any]:
    """Débite du Gold si le solde suffit. Retourne {ok, balance, cost}."""
    amount = int(amount)
    balance = await get_balance(user_id)
    if amount <= 0:
        return {"ok": True, "balance": balance, "cost": 0}
    if balance < amount:
        return {"ok": False, "balance": balance, "cost": amount}
    db = get_db()
    doc = await db.users.find_one_and_update(
        {"id": user_id, "gold_balance": {"$gte": amount}},
        {"$inc": {"gold_balance": -amount}},
        return_document=True,
    )
    if not doc:  # course entre deux dépenses simultanées
        return {"ok": False, "balance": balance, "cost": amount}
    new_balance = int(doc.get("gold_balance", 0))
    await _log(user_id, "spend", amount, reason, new_balance, meta)
    return {"ok": True, "balance": new_balance, "cost": amount}


async def recent_transactions(user_id: str, limit: int = 30) -> List[Dict[str, Any]]:
    db = get_db()
    cursor = db.gold_transactions.find({"user_id": user_id}, {"_id": 0}).sort("created_at", -1).limit(limit)
    return await cursor.to_list(length=limit)
