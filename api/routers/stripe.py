"""Routes de paiement Stripe : checkout, portail client, webhook."""
from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel

from api.auth import get_current_user

router = APIRouter()


class CheckoutRequest(BaseModel):
    tier: str


@router.post("/api/stripe/create-checkout-session")
async def stripe_checkout(req: CheckoutRequest, current_user: dict = Depends(get_current_user)):
    """Crée une session de paiement Stripe."""
    from api.stripe_service import create_checkout_session
    url = create_checkout_session(
        user_id=current_user["id"],
        email=current_user["email"],
        tier=req.tier
    )
    if not url:
        raise HTTPException(status_code=500, detail="Impossible de créer la session Stripe")

    return {"status": "success", "url": url}


@router.post("/api/stripe/create-portal-session")
async def stripe_portal(current_user: dict = Depends(get_current_user)):
    """Ouvre le portail client Stripe pour consulter les factures et gérer la carte bancaire."""
    from api.stripe_service import create_customer_portal_session
    url = create_customer_portal_session(
        customer_id=current_user.get("stripe_customer_id"),
        email=current_user.get("email")
    )
    if not url:
        raise HTTPException(status_code=400, detail="Portail Stripe non disponible. Aucun abonnement actif trouvé.")
    return {"status": "success", "url": url}


@router.post("/api/stripe/webhook")
async def stripe_webhook(request: Request):
    """Handler pour les webhooks Stripe."""
    from api.stripe_service import handle_webhook_payload
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    success, message = await handle_webhook_payload(payload, sig_header)
    if not success:
        raise HTTPException(status_code=400, detail=message)

    return {"status": "success"}
