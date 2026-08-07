"""Routes Boutique & Gold : solde, historique, catalogue de packs, achat."""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from api.auth import get_current_user
from core import gold as gold_mod

router = APIRouter(tags=["Shop"])


@router.get("/api/gold/balance")
async def get_gold_balance(current_user: dict = Depends(get_current_user)):
    # Recharge mensuelle gratuite paresseuse (si due), puis renvoie le solde
    balance = await gold_mod.maybe_monthly_free_refill(current_user["id"])
    return {"status": "success", "data": {"balance": balance}}


@router.get("/api/gold/transactions")
async def get_gold_transactions(current_user: dict = Depends(get_current_user)):
    txs = await gold_mod.recent_transactions(current_user["id"])
    return {"status": "success", "data": txs}


@router.get("/api/shop/packs")
async def list_packs():
    """Catalogue public des packs de Gold."""
    packs = []
    for p in gold_mod.GOLD_PACKS:
        packs.append({
            "key": p["key"],
            "name": p["name"],
            "gold": p["gold"],
            "bonus": p.get("bonus", 0),
            "total_gold": gold_mod.pack_total_gold(p),
            "price_eur": p["price_eur"],
            "badge": p.get("badge"),
        })
    return {"status": "success", "data": packs}


class PackCheckoutRequest(BaseModel):
    pack: str


@router.post("/api/shop/checkout")
async def shop_checkout(req: PackCheckoutRequest, current_user: dict = Depends(get_current_user)):
    """Crée une session de paiement Stripe pour l'achat d'un pack de Gold."""
    pack = gold_mod.PACK_BY_KEY.get(req.pack)
    if not pack:
        raise HTTPException(status_code=400, detail="Pack inconnu.")
    from api.stripe_service import create_gold_pack_checkout
    url = create_gold_pack_checkout(current_user["id"], current_user.get("email", ""), pack)
    if not url:
        raise HTTPException(status_code=500, detail="Boutique indisponible (Stripe non configuré).")
    return {"status": "success", "url": url}
