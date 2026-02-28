import stripe
import os
from loguru import logger
from config.settings import settings
from core.database import get_db

stripe.api_key = settings.stripe_api_key
STRIPE_WEBHOOK_SECRET = settings.stripe_webhook_secret

def create_checkout_session(user_id: str, email: str, tier: str):
    """Crée une session Stripe Checkout pour un forfait spécifique."""
    
    price_ids = {
        "ESSENTIAL": "price_1T5Xf6PvxExBNm38EHU1rkhq",
        "PRO": "price_1T5Xf7PvxExBNm38iixC2ipQ"
    }
    
    if tier not in price_ids:
        raise ValueError("Tier invalide pour Stripe")

    try:
        session = stripe.checkout.Session.create(
            customer_email=email,
            payment_method_types=['card'],
            line_items=[{
                'price': price_ids[tier],
                'quantity': 1,
            }],
            mode='subscription',
            success_url='http://localhost:5173/settings?status=success',
            cancel_url='http://localhost:5173/settings?status=cancel',
            metadata={
                'user_id': user_id,
                'tier': tier
            }
        )
        return session.url
    except Exception as e:
        logger.error(f"Erreur Stripe Session: {e}")
        return None

async def handle_webhook_payload(payload, sig_header):
    """Gère les événements envoyés par Stripe (Webhooks)."""
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        # Invalid payload
        return False, "Payload invalide"
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return False, "Signature invalide"

    # Handle the event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        await update_user_subscription(session)
    elif event['type'] == 'customer.subscription.deleted':
        subscription = event['data']['object']
        await cancel_user_subscription(subscription)


        
    return True, "Event processed"

async def update_user_subscription(session):
    """Met à jour l'utilisateur après un paiement réussi."""
    user_id = session.get('metadata', {}).get('user_id')
    tier = session.get('metadata', {}).get('tier')
    stripe_sub_id = session.get('subscription')
    stripe_cust_id = session.get('customer')

    if not user_id or not tier:
        return

    db = get_db()
    try:
        await db.users.update_one(
            {"id": user_id},
            {
                "$set": {
                    "subscription_tier": tier,
                    "stripe_customer_id": stripe_cust_id,
                    "stripe_subscription_id": stripe_sub_id
                }
            }
        )
        logger.info(f"✅ Abonnement mis à jour (Stripe) pour {user_id}: {tier}")
    except Exception as e:
        logger.error(f"❌ Erreur DB Webhook: {e}")

async def cancel_user_subscription(subscription):
    """Réinitialise l'utilisateur au forfait GRATUIT si l'abonnement est annulé."""
    stripe_cust_id = subscription.get('customer')
    
    db = get_db()
    try:
        await db.users.update_one(
            {"stripe_customer_id": stripe_cust_id},
            {
                "$set": {
                    "subscription_tier": "FREE",
                    "stripe_subscription_id": None
                }
            }
        )
        logger.info(f"⚠️ Abonnement résilié (Stripe) pour client {stripe_cust_id}")
    except Exception as e:
        logger.error(f"❌ Erreur DB Webhook Cancel: {e}")

