import asyncio
from datetime import datetime, timedelta
from loguru import logger
from core.database import get_db
from core.email_service import email_service
from agents.pre_interview_agent import pre_interview_agent

class PreInterviewScheduler:
    """Gère la planification des simulations : préparation IA et notifications par mail."""

    def __init__(self):
        self.is_running = False

    async def start(self):
        if self.is_running:
            return
        self.is_running = True
        asyncio.create_task(self.loop())
        logger.info("[Pre-Interview] Scheduler démarré")

    async def loop(self):
        while self.is_running:
            try:
                await self.process_simulations()
            except Exception as e:
                logger.error(f"[Pre-Interview] Erreur boucle scheduler: {e}")
            await asyncio.sleep(60)  # Vérifie toutes les minutes

    async def process_simulations(self):
        db = get_db()
        now = datetime.utcnow()

        # 1. Préparation IA (2h avant)
        threshold_prep = now + timedelta(hours=2)
        cursor_prep = db.simulations.find({
            "status": "PENDING",
            "simulation_date": {"$lte": threshold_prep}
        })
        
        async for sim in cursor_prep:
            try:
                # Récupérer le CV de l'utilisateur
                user = await db.users.find_one({"id": sim["user_id"]}, {"cv_text": 1})
                cv_text = user.get("cv_text", "") if user else ""
                
                # Générer la préparation
                prep_data = await pre_interview_agent.prepare_simulation(
                    sim["company_name"], 
                    sim["job_title"],
                    cv_text
                )
                
                await db.simulations.update_one(
                    {"id": sim["id"]},
                    {"$set": {"prep_data": prep_data, "status": "PREPARED"}}
                )
                logger.success(f"[Pre-Interview] Simulation {sim['id']} préparée pour {sim['company_name']}")
            except Exception as e:
                logger.error(f"[Pre-Interview] Échec préparation simulation {sim['id']}: {e}")

        # 2. Notification Email (15 min avant)
        threshold_notify = now + timedelta(minutes=15)
        cursor_notify = db.simulations.find({
            "status": "PREPARED",
            "simulation_date": {"$lte": threshold_notify}
        })

        async for sim in cursor_notify:
            try:
                user = await db.users.find_one({"id": sim["user_id"]}, {"email": 1})
                if user and user.get("email"):
                    # Construire l'email
                    subject = f"🚀 Prêt pour votre entretien chez {sim['company_name']} ?"
                    link = f"https://goldarmyai.com/interview?sim_id={sim['id']}"
                    
                    html = f"""
                    <h2>Votre simulation est prête !</h2>
                    <p>Votre session de préparation pour le poste de <strong>{sim['job_title']}</strong> chez <strong>{sim['company_name']}</strong> commence dans quelques minutes.</p>
                    <p>L'IA a généré des questions spécifiques et des points STAR pour vous.</p>
                    <a href="{link}" style="padding: 10px 20px; background: #E85D3E; color: white; text-decoration: none; border-radius: 8px; font-weight: bold;">Accéder à ma préparation</a>
                    """
                    
                    await email_service.send_email(user["email"], subject, html)
                    
                    # 3. Notification DB & Push
                    try:
                        from api.notifications import send_expo_push_notification
                        notif_body = f"Votre entretien chez {sim['company_name']} commence dans 15 min !"
                        
                        # Enregistrement en DB pour la cloche de notification
                        await db.notifications.insert_one({
                            "user_id": sim["user_id"],
                            "title": "Interview imminente !",
                            "message": notif_body,
                            "type": "warning",
                            "action_url": link,
                            "is_read": False,
                            "created_at": datetime.utcnow().isoformat()
                        })

                        # Envoi Push (si token présent)
                        if "push_tokens" in user:
                            for token in user["push_tokens"]:
                                await send_expo_push_notification(
                                    token=token,
                                    title="Interview imminente !",
                                    body=notif_body,
                                    data={"url": link}
                                )
                    except Exception as e:
                        logger.error(f"[Pre-Interview] Erreur push simulation {sim['id']}: {e}")

                    await db.simulations.update_one(
                        {"id": sim["id"]},
                        {"$set": {"status": "NOTIFIED"}}
                    )
                    logger.info(f"[Pre-Interview] Email de rappel envoyé à {user['email']} pour {sim['company_name']}")
            except Exception as e:
                logger.error(f"[Pre-Interview] Échec notification simulation {sim['id']}: {e}")

pre_interview_scheduler = PreInterviewScheduler()
