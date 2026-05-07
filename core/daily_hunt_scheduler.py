import asyncio
import schedule
import time
from datetime import datetime, time as dtime
from loguru import logger
from core.database import get_db
from agents.daily_hunt_agent import DailyHuntAgent
from core.email_service import email_service

class DailyHuntScheduler:
    def __init__(self):
        self.running = False

    async def start(self):
        if self.running: return
        self.running = True
        asyncio.create_task(self._loop())
        logger.info("🚀 Scheduler Daily Hunt démarré (Cible: 07:00 tous les matins)")

    async def _loop(self):
        while self.running:
            try:
                now = datetime.now()
                # On ne lance le scan qu'entre 07:00 et 07:30
                if now.hour == 7 and now.minute < 30:
                    await self.process_daily_hunts()
                    # On attend 45 min pour éviter de relancer dans la même heure
                    await asyncio.sleep(45 * 60)
                else:
                    await asyncio.sleep(60) # Vérifie chaque minute
            except Exception as e:
                logger.error(f"[DailyHunt Scheduler] Erreur boucle: {e}")
                await asyncio.sleep(60)

    async def process_daily_hunts(self):
        """Parcourt tous les utilisateurs ayant activé la chasse quotidienne."""
        db = get_db()
        logger.info("🌅 Démarrage de la chasse quotidienne collective...")
        
        # On cherche les configs Daily Hunt actives
        cursor = db.daily_hunt_config.find({"enabled": True})
        configs = await cursor.to_list(length=None)
        
        agent = DailyHuntAgent()
        
        for cfg in configs:
            user_id = cfg["user_id"]
            last_run = cfg.get("last_run")
            
            # Vérifier si on a déjà fait la chasse aujourd'hui
            today_str = datetime.now().strftime("%Y-%m-%d")
            if last_run == today_str:
                continue
                
            try:
                # 1. Récupérer les infos utilisateur
                user = await db.users.find_one({"id": user_id})
                if not user: continue
                
                # 2. Lancer le scan (IA uniquement sur le top 5 final)
                jobs = await agent.run_daily_scan(
                    user_id=user_id,
                    query=cfg.get("query", "Développeur"),
                    location=cfg.get("location", "Montreal, QC"),
                    cv_text=user.get("cv_text")
                )
                
                if jobs:
                    # 3. Envoi Email / Notification
                    subject = f"🎯 GoldArmy : Vos 5 pépites du jour ({datetime.now().strftime('%d/%m')})"
                    html = self._format_email(jobs, user.get("full_name", "Aventurier"))
                    await email_service.send_email(user["email"], subject, html)
                    
                    # 4. Notification DB
                    await db.notifications.insert_one({
                        "user_id": user_id,
                        "title": "Chasse du matin terminée !",
                        "message": f"Nous avons trouvé {len(jobs)} opportunités parfaites pour vous ce matin.",
                        "type": "success",
                        "action_url": "/dashboard",
                        "is_read": False,
                        "created_at": datetime.utcnow().isoformat()
                    })
                
                # 5. Marquer comme fait aujourd'hui
                await db.daily_hunt_config.update_one(
                    {"user_id": user_id},
                    {"$set": {"last_run": today_str}}
                )
                
            except Exception as e:
                logger.error(f"[DailyHunt] Erreur pour l'utilisateur {user_id}: {e}")

    def _format_email(self, jobs, name):
        job_rows = ""
        for j in jobs:
            job_rows += f"""
            <div style="padding: 15px; border: 1px solid #eee; border-radius: 10px; margin-bottom: 10px;">
                <h3 style="margin: 0; color: #1e293b;">{j.get('title')}</h3>
                <p style="margin: 5px 0; color: #64748b; font-size: 14px;">{j.get('company')} - {j.get('location')}</p>
                <p style="color: #4f46e5; font-weight: bold; margin: 5px 0;">Score de match : {j.get('match_score')}%</p>
                <p style="font-size: 12px; font-style: italic;">{j.get('match_justification')}</p>
                <a href="{j.get('url')}" style="display: inline-block; padding: 8px 15px; background: #000; color: #fff; text-decoration: none; border-radius: 5px; font-size: 12px; margin-top: 10px;">Voir l'offre</a>
            </div>
            """
            
        return f"""
        <div style="font-family: sans-serif; max-width: 600px; margin: 0 auto; color: #333;">
            <h1 style="color: #000;">Bonjour {name} ! 👋</h1>
            <p>Voici votre sélection exclusive de ce matin, dénichée par GoldArmy.</p>
            {job_rows}
            <p style="margin-top: 30px; font-size: 12px; color: #999;">Vous recevez cet email car vous avez activé la Chasse Quotidienne dans votre dashboard GoldArmy.</p>
        </div>
        """

daily_hunt_scheduler = DailyHuntScheduler()
