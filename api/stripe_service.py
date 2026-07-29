import stripe
import os
import asyncio
from datetime import datetime
from loguru import logger
from config.settings import settings
from core.database import get_db
from core.email_service import email_service
from api.notifications import send_expo_push_notification

stripe.api_key = settings.stripe_api_key
STRIPE_WEBHOOK_SECRET = settings.stripe_webhook_secret

def create_checkout_session(user_id: str, email: str, tier: str):
    """Crée une session Stripe Checkout pour un forfait spécifique."""
    
    price_ids = {
        "ESSENTIAL": settings.stripe_price_essential,
        "PRO": settings.stripe_price_pro
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
            success_url=f"{settings.frontend_url}/settings?status=success",
            cancel_url=f"{settings.frontend_url}/settings?status=cancel",
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
    """Met à jour l'utilisateur après un paiement réussi, envoie email et notifications."""
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

        # Récupérer l'utilisateur pour l'e-mail et les notifications
        user = await db.users.find_one({"id": user_id})
        if user:
            user_email = user.get("email") or session.get("customer_details", {}).get("email")
            tier_label = "Essentiel" if tier == "ESSENTIAL" else "Pro"

            # 1. Envoi de l'e-mail de confirmation
            if user_email:
                asyncio.create_task(email_service.send_subscription_confirmation(user_email, tier))

            # 2. Création de la notification in-app
            notif_title = "🎉 Abonnement Activé !"
            notif_msg = f"Félicitations ! Votre forfait GoldArmy {tier_label} a été activé."
            new_notif = {
                "user_id": user_id,
                "title": notif_title,
                "message": notif_msg,
                "type": "success",
                "action_url": "/settings",
                "is_read": False,
                "created_at": datetime.utcnow().isoformat()
            }
            await db.notifications.insert_one(new_notif)

            # 3. Envoi de la notification Push (Expo)
            push_tokens = user.get("push_tokens", [])
            for token in push_tokens:
                asyncio.create_task(
                    send_expo_push_notification(
                        token=token,
                        title=notif_title,
                        body=notif_msg,
                        data={"url": "/settings"}
                    )
                )

    except Exception as e:
        logger.error(f"❌ Erreur DB Webhook: {e}")

async def cancel_user_subscription(subscription):
    """Réinitialise l'utilisateur au forfait GRATUIT si l'abonnement est annulé et informe l'utilisateur."""
    stripe_cust_id = subscription.get('customer')
    
    db = get_db()
    try:
        user = await db.users.find_one({"stripe_customer_id": stripe_cust_id})

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

        if user:
            user_id = user.get("id")
            user_email = user.get("email")

            # 1. Envoi de l'e-mail de résiliation
            if user_email:
                asyncio.create_task(email_service.send_subscription_cancellation(user_email))

            # 2. Création de la notification in-app
            notif_title = "Abonnement Résilié"
            notif_msg = "Votre abonnement GoldArmy a pris fin. Vous êtes de retour en formule Gratuit."
            new_notif = {
                "user_id": user_id,
                "title": notif_title,
                "message": notif_msg,
                "type": "warning",
                "action_url": "/settings",
                "is_read": False,
                "created_at": datetime.utcnow().isoformat()
            }
            await db.notifications.insert_one(new_notif)

    except Exception as e:
        logger.error(f"❌ Erreur DB Webhook Cancel: {e}")
