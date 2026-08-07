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

# Recharge mensuelle de Gold selon le forfait de l'abonné (auto, une fois par mois).
MONTHLY_REFILL = {"FREE": 100, "ESSENTIAL": 200, "PRO": 500}
GOLD_MONTHLY_FREE = MONTHLY_REFILL["FREE"]

# Incrémente ce numéro chaque fois que tu changes les montants ci-dessus :
# tous les utilisateurs seront rechargés au nouveau montant dès leur prochaine visite
# (au lieu d'attendre la fin de leur cycle de 30 jours).
REFILL_VERSION = 2

# Fonctionnalités réservées à un forfait (déverrouillage) — en plus du coût en Gold.
TIER_RANK = {"FREE": 0, "ESSENTIAL": 1, "PRO": 2, "ADMIN": 3}
FEATURE_MIN_TIER = {
    # Espace Réseau → Essentiel
    "network_access": "ESSENTIAL",
    "headhunter": "ESSENTIAL",
    "address_book": "ESSENTIAL",
    # Fonctions avancées → Pro
    "portfolio": "PRO",
    "morning_sourcing": "PRO",
    "post_interview": "PRO",
    "sniper_apply": "PRO",
    "auto_apply": "PRO",
}

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
    "cv_audit": 10,
    "follow_up": 5,
    "sniper_search": 15,
    "cv_adaptation": 18,
    "hr_interview": 10,
    "portfolio": 15,
    # Autres fonctionnalités (valeurs alignées)
    "cover_letter": 8,
    "headhunter": 15,
    "network_access": 5,
    "morning_sourcing": 15,
    "post_interview": 10,
    "sniper_apply": 25,
    "auto_apply": 25,
    # address_book : consultation gratuite (non facturée)
}

# Recharge mensuelle gratuite (jours entre deux recharges)
FREE_REFILL_DAYS = 30


async def maybe_monthly_refill(user_id: str) -> int:
    """Recharge mensuelle paresseuse selon le forfait (FREE 20 / ESSENTIAL 200 / PRO 500).

    Idempotent (> 30 j), sans cron : appelé à l'ouverture de la boutique / check du solde.
    """
    from datetime import timedelta
    db = get_db()
    u = await db.users.find_one({"id": user_id}, {"_id": 0, "last_free_refill": 1, "subscription_tier": 1, "refill_version": 1})
    if not u:
        return await get_balance(user_id)
    tier = u.get("subscription_tier", "FREE")
    amount = MONTHLY_REFILL.get(tier, MONTHLY_REFILL["FREE"])
    last = u.get("last_free_refill")
    now = datetime.now(timezone.utc)

    # Recharge due si : montants modifiés (nouvelle version), jamais rechargé, ou cycle de 30 j écoulé
    due = (u.get("refill_version") != REFILL_VERSION) or (last is None)
    if last and not due:
        try:
            if last.tzinfo is None:
                last = last.replace(tzinfo=timezone.utc)
            due = (now - last) >= timedelta(days=FREE_REFILL_DAYS)
        except Exception:
            due = True

    if due:
        await db.users.update_one(
            {"id": user_id},
            {"$set": {"last_free_refill": now, "refill_version": REFILL_VERSION}},
        )
        reason = "monthly_free" if tier == "FREE" else f"monthly_{tier.lower()}"
        return await grant_gold(user_id, amount, reason)
    return await get_balance(user_id)


# Alias rétro-compatibilité
maybe_monthly_free_refill = maybe_monthly_refill


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
