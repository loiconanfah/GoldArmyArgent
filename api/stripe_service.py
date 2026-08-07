import stripe
import os
import asyncio
from datetime import datetime, timezone
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

def create_customer_portal_session(customer_id: str = None, email: str = None):
    """Crée une session du portail client Stripe pour gérer les abonnements et factures."""
    try:
        if not customer_id and email:
            customers = stripe.Customer.list(email=email, limit=1)
            if customers and customers.data:
                customer_id = customers.data[0].id

        if not customer_id:
            logger.warning("Aucun customer_id Stripe trouvé pour ouvrir le portail")
            return None

        session = stripe.billing_portal.Session.create(
            customer=customer_id,
            return_url=f"{settings.frontend_url}/settings",
        )
        return session.url
    except Exception as e:
        logger.error(f"Erreur Stripe Customer Portal: {e}")
        return None

# ─────────────────────────────────────────────────────────────────────────────
# Facturation par siège des Organisations (1 $/mois par membre, admin exclu)
# ─────────────────────────────────────────────────────────────────────────────

PRICE_PER_SEAT_USD = 1  # 1 $ par membre / mois


def create_org_seat_checkout(org_id: str, admin_user_id: str, email: str, quantity: int):
    """Crée une session Checkout d'abonnement par siège pour une organisation.

    La quantité correspond au nombre de membres facturables (hors administrateur).
    Nécessite settings.stripe_price_org_seat (prix récurrent 1$/mois « par unité »).
    """
    if not settings.stripe_price_org_seat:
        logger.error("stripe_price_org_seat non configuré")
        return None
    try:
        session = stripe.checkout.Session.create(
            customer_email=email,
            payment_method_types=['card'],
            line_items=[{
                'price': settings.stripe_price_org_seat,
                'quantity': max(1, int(quantity)),
            }],
            mode='subscription',
            success_url=f"{settings.frontend_url}/organisation/facturation?status=success",
            cancel_url=f"{settings.frontend_url}/organisation/facturation?status=cancel",
            metadata={'org_id': org_id, 'admin_user_id': admin_user_id, 'type': 'org_seats'},
            subscription_data={'metadata': {'org_id': org_id, 'type': 'org_seats'}},
        )
        return session.url
    except Exception as e:
        logger.error(f"Erreur Stripe Org Checkout: {e}")
        return None


def create_gold_pack_checkout(user_id: str, email: str, pack: dict):
    """Crée un Checkout Stripe PAIEMENT UNIQUE pour un pack de Gold (boutique).

    Prix défini en ligne (price_data) : aucun produit à créer d'avance.
    """
    from core.gold import pack_total_gold
    total_gold = pack_total_gold(pack)
    amount_cents = int(round(float(pack["price_eur"]) * 100))
    try:
        session = stripe.checkout.Session.create(
            customer_email=email,
            payment_method_types=['card'],
            mode='payment',
            line_items=[{
                'price_data': {
                    'currency': 'eur',
                    'unit_amount': amount_cents,
                    'product_data': {'name': f"GoldArmy — {total_gold} Gold ({pack.get('name', pack['key'])})"},
                },
                'quantity': 1,
            }],
            success_url=f"{settings.frontend_url}/boutique?status=success",
            cancel_url=f"{settings.frontend_url}/boutique?status=cancel",
            metadata={'user_id': user_id, 'type': 'gold_pack', 'pack': pack['key'], 'gold': str(total_gold)},
        )
        return session.url
    except Exception as e:
        logger.error(f"Erreur Stripe Gold Pack Checkout: {e}")
        return None


async def credit_gold_pack(session):
    """Crédite le Gold après paiement réussi d'un pack (webhook)."""
    meta = session.get('metadata', {}) or {}
    user_id = meta.get('user_id')
    gold = int(meta.get('gold', 0) or 0)
    if not user_id or gold <= 0:
        return
    from core.gold import grant_gold
    await grant_gold(user_id, gold, f"pack:{meta.get('pack','?')}", meta={"stripe_session": session.get('id')})
    logger.info(f"🪙 {gold} Gold crédités à {user_id} (pack {meta.get('pack')})")


def create_org_plan_checkout(org_id: str, admin_user_id: str, email: str,
                             plan: str, plan_name: str, amount: int, interval: str,
                             currency: str = "cad"):
    """Crée une session Checkout d'abonnement pour un FORFAIT Organisation.

    Le prix est défini EN LIGNE (price_data) : aucun produit/prix à créer d'avance
    dans le dashboard Stripe — seule la clé API suffit.
    """
    if not amount:
        logger.error(f"Montant invalide pour le forfait {plan}/{interval}")
        return None
    stripe_interval = "year" if interval == "annual" else "month"
    try:
        session = stripe.checkout.Session.create(
            customer_email=email,
            payment_method_types=['card'],
            mode='subscription',
            line_items=[{
                'price_data': {
                    'currency': currency,
                    'unit_amount': int(amount) * 100,
                    'recurring': {'interval': stripe_interval},
                    'product_data': {'name': f"GoldArmy Organisation — {plan_name} ({'annuel' if interval=='annual' else 'mensuel'})"},
                },
                'quantity': 1,
            }],
            success_url=f"{settings.frontend_url}/organisation/facturation?status=success",
            cancel_url=f"{settings.frontend_url}/organisation/facturation?status=cancel",
            metadata={'org_id': org_id, 'admin_user_id': admin_user_id, 'type': 'org_plan', 'plan': plan, 'interval': interval},
            subscription_data={'metadata': {'org_id': org_id, 'type': 'org_plan', 'plan': plan, 'interval': interval}},
        )
        return session.url
    except Exception as e:
        logger.error(f"Erreur Stripe Org Plan Checkout: {e}")
        return None


def _sync_seats_sync(subscription_id: str, quantity: int) -> bool:
    """Met à jour la quantité (nombre de sièges) de l'abonnement Stripe (appel bloquant)."""
    try:
        sub = stripe.Subscription.retrieve(subscription_id)
        item_id = sub['items']['data'][0]['id']
        stripe.SubscriptionItem.modify(
            item_id, quantity=max(1, int(quantity)), proration_behavior='none'
        )
        return True
    except Exception as e:
        logger.warning(f"Sync sièges Stripe échoué ({subscription_id}): {e}")
        return False


async def sync_org_seat_quantity(org_id: str):
    """Synchronise le nombre de sièges facturés avec le nombre réel de membres."""
    db = get_db()
    org = await db.organizations.find_one({"id": org_id})
    if not org or not org.get("stripe_subscription_id") or org.get("billing_status") != "active":
        return
    count = await db.users.count_documents({"organization_id": org_id, "role": "member"})
    await asyncio.to_thread(_sync_seats_sync, org["stripe_subscription_id"], count)


async def update_org_billing(session):
    """Active la facturation d'une organisation après un paiement réussi."""
    meta = session.get('metadata', {}) or {}
    org_id = meta.get('org_id')
    if not org_id:
        return
    db = get_db()
    fields = {
        "billing_status": "active",
        "stripe_subscription_id": session.get('subscription'),
        "stripe_customer_id": session.get('customer'),
        "billing_activated_at": datetime.now(timezone.utc),
    }
    if meta.get('plan'):
        fields["billing_plan"] = meta['plan']
    if meta.get('interval'):
        fields["billing_interval"] = meta['interval']
    await db.organizations.update_one({"id": org_id}, {"$set": fields})
    logger.info(f"✅ Facturation organisation activée: {org_id} (plan={meta.get('plan')})")
    # Recharge immédiate en Gold des membres sponsorisés au niveau du nouveau palier
    try:
        from core.organizations import monthly_org_refill
        await monthly_org_refill(org_id)
    except Exception as e:
        logger.warning(f"Recharge Gold sponsorisés échouée: {e}")


async def cancel_org_billing(subscription):
    """Désactive la facturation d'une organisation après résiliation."""
    org_id = subscription.get('metadata', {}).get('org_id')
    db = get_db()
    query = {"id": org_id} if org_id else {"stripe_subscription_id": subscription.get('id')}
    # Récupère l'id AVANT la mise à jour (qui vide stripe_subscription_id)
    if not org_id:
        target = await db.organizations.find_one(query, {"_id": 0, "id": 1})
        org_id = target.get("id") if target else None
    await db.organizations.update_one(
        query, {"$set": {"billing_status": "canceled", "stripe_subscription_id": None, "billing_plan": None}}
    )
    # Note : le Gold déjà crédité reste acquis ; seules les recharges mensuelles futures s'arrêtent.
    logger.info(f"⚠️ Facturation organisation résiliée: {org_id or subscription.get('id')}")


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

    etype = event['type']
    obj = event['data']['object']
    meta_type = (obj.get('metadata') or {}).get('type')

    # Handle the event
    if etype == 'checkout.session.completed':
        if meta_type in ('org_seats', 'org_plan'):
            await update_org_billing(obj)
        elif meta_type == 'gold_pack':
            await credit_gold_pack(obj)
        else:
            await update_user_subscription(obj)
    elif etype == 'customer.subscription.deleted':
        if meta_type in ('org_seats', 'org_plan'):
            await cancel_org_billing(obj)
        else:
            await cancel_user_subscription(obj)

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

        # Crédite immédiatement les tokens mensuels du forfait (Essentiel 200 / Pro 500)
        try:
            from core.gold import MONTHLY_REFILL, grant_gold
            from datetime import datetime as _dt, timezone as _tz
            amount = MONTHLY_REFILL.get(tier, 0)
            if amount:
                await grant_gold(user_id, amount, f"subscription_{tier.lower()}")
                await db.users.update_one({"id": user_id}, {"$set": {"last_free_refill": _dt.now(_tz.utc)}})
        except Exception as ge:
            logger.warning(f"Crédit tokens abonnement échoué: {ge}")

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
                "created_at": datetime.now(timezone.utc).isoformat()
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
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            await db.notifications.insert_one(new_notif)

    except Exception as e:
        logger.error(f"❌ Erreur DB Webhook Cancel: {e}")
