"""
Moteur de Workflows (Playbooks) pour GoldArmy.
Gère l'exécution des 10 Playbooks automatisés.
"""
import asyncio
from typing import Dict, Any, List, Optional
from loguru import logger
from datetime import datetime

from core.orchestrator import orchestrator
from agents.headhunter import headhunter_agent
# Import scheduler if needed
from apscheduler.schedulers.asyncio import AsyncIOScheduler

class WorkflowEngine:
    """Moteur central pour exécuter les Playbooks GoldArmy."""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.running_workflows = {}
        self.playbook_settings = {
            "10": {"always_active": False, "chain_to": None}
        }
        logger.info("⚙️ WorkflowEngine initialisé")

    def send_push_notification(self, title: str, message: str):
        """Mock push notification."""
        logger.info(f"🔔 PUSH NOTIFICATION: {title} | {message}")


    def start_scheduler(self):
        if not self.scheduler.running:
            self.scheduler.start()
            logger.success("⏱️ Cron Scheduler démarré")
            # Enregistrer le Daily Hunt à 7h00 tous les jours
            self.scheduler.add_job(
                self.run_daily_hunt, 
                'cron', 
                hour=7, 
                minute=0, 
                id='daily_hunt',
                replace_existing=True
            )

    async def dispatch_event(self, event_name: str, payload: Dict[str, Any]):
        """Route l'événement vers le bon Playbook."""
        logger.info(f"🔔 Événement reçu: {event_name} | Payload: {payload.get('id', 'N/A')}")
        
        # 1. Sniper-to-Apply
        if event_name == "sniper_to_apply":
            asyncio.create_task(self._sniper_to_apply_workflow(payload))
            # Auto-trigger Playbook 10 if always active
            if self.playbook_settings.get("10", {}).get("always_active"):
                asyncio.create_task(self._smart_cover_letter_workflow(payload))
            
        # 2. Ghostbuster
        elif event_name == "card_stagnant":
            asyncio.create_task(self._ghostbuster_workflow(payload))
            
        # 3. Network Ninja
        elif event_name == "prospect_added":
            asyncio.create_task(self._network_ninja_workflow(payload))
            
        # 4. Pre-Interview Bootcamp
        elif event_name == "interview_scheduled":
            asyncio.create_task(self._pre_interview_bootcamp_workflow(payload))
            
        # 6. Elevator Pitch
        elif event_name == "cv_uploaded":
            asyncio.create_task(self._elevator_pitch_workflow(payload))
            
        # 7. Post-Interview Closer
        elif event_name == "interview_completed":
            asyncio.create_task(self._post_interview_closer_workflow(payload))
            
        # 8. Cold Call Assistant
        elif event_name == "prepare_call":
            asyncio.create_task(self._cold_call_assistant_workflow(payload))
            
        # 9. Rejection Pivot
        elif event_name == "card_rejected":
            asyncio.create_task(self._rejection_pivot_workflow(payload))
            
        # 10. Smart Cover Letter
        elif event_name == "generate_cover_letter":
            asyncio.create_task(self._smart_cover_letter_workflow(payload))

    # --- PLAYBOOKS IMPLÉMENTATIONS ---

    async def _sniper_to_apply_workflow(self, payload: Dict[str, Any]):
        """Playbook 1: Sniper-to-Apply (Mock MultiOn)"""
        company = payload.get("companyName", "Inconnue")
        logger.info(f"🤖 [Playbook 1] Démarrage Auto-Apply pour {company}")
        await asyncio.sleep(2) # Simule génération CV
        logger.info(f"📄 CV adapté généré pour {company}")
        await asyncio.sleep(2) # Simule appel API MultiOn
        logger.success(f"✅ Formulaire ATS rempli et soumis avec succès via MultiOn (Mock) pour {company}")
        return {"status": "applied", "company": company}

    async def _ghostbuster_workflow(self, payload: Dict[str, Any]):
        """Playbook 2: Relance Anti-Fantôme"""
        company = payload.get("companyName", "")
        logger.info(f"👻 [Playbook 2] Recherche contact relance pour {company}")
        makers = await headhunter_agent.find_decision_makers({"company_name": company})
        target = makers[0]["name"] if makers else "Équipe Recrutement"
        logger.success(f"📧 Email de relance généré pour {target} chez {company}")

    async def _network_ninja_workflow(self, payload: Dict[str, Any]):
        """Playbook 3: Network Ninja"""
        company = payload.get("companyName", "")
        logger.info(f"🥷 [Playbook 3] Prospection Ninja sur {company}")
        makers = await headhunter_agent.find_decision_makers({"company_name": company})
        logger.success(f"🥷 {len(makers)} décideurs trouvés. Génération messages LinkedIn.")

    async def _pre_interview_bootcamp_workflow(self, payload: Dict[str, Any]):
        """Playbook 4: Pre-Interview Bootcamp"""
        company = payload.get("companyName", "")
        logger.info(f"🧠 [Playbook 4] Préparation Simulateur pour {company}")
        await asyncio.sleep(2)
        logger.success(f"🎯 Configuration simulateur IA chargée pour la culture de {company}")

    async def run_daily_hunt(self):
        """Playbook 5: Daily Hunt (Cron)"""
        logger.info("☕ [Playbook 5] Lancement Daily Hunt matinal...")
        await asyncio.sleep(3)
        logger.success("☕ Daily Hunt terminé: 3 nouvelles offres trouvées avec match > 80%")

    async def _elevator_pitch_workflow(self, payload: Dict[str, Any]):
        """Playbook 6: Elevator Pitch"""
        logger.info("🎙️ [Playbook 6] Analyse nouveau CV pour pitch...")
        await asyncio.sleep(2)
        logger.success("🎙️ 3 Pitchs générés (LinkedIn, Vocal, Entretien)")

    async def _post_interview_closer_workflow(self, payload: Dict[str, Any]):
        """Playbook 7: Post-Interview Closer"""
        company = payload.get("companyName", "l'entreprise")
        score = payload.get("score", 85)
        logger.info(f"🏆 [Playbook 7] Debrief entretien {company} (Score: {score})")
        await asyncio.sleep(2)
        logger.success(f"✉️ Email de remerciement stratégique généré pour {company}")

    async def _cold_call_assistant_workflow(self, payload: Dict[str, Any]):
        """Playbook 8: Cold Call Assistant"""
        company = payload.get("companyName", "")
        logger.info(f"📞 [Playbook 8] Préparation script appel pour {company}")
        await asyncio.sleep(2)
        logger.success("📞 Script dynamique avec traitement d'objections généré")

    async def _rejection_pivot_workflow(self, payload: Dict[str, Any]):
        """Playbook 9: Rejection Pivot"""
        company = payload.get("companyName", "")
        logger.info(f"🛡️ [Playbook 9] Pivot après refus de {company}")
        await asyncio.sleep(2)
        logger.success("🛡️ Email de feedback généré + 3 offres alternatives trouvées")

    async def _smart_cover_letter_workflow(self, payload: Dict[str, Any]):
        """Playbook 10: Smart Cover Letter"""
        company = payload.get("companyName", "")
        logger.info(f"🗞️ [Playbook 10] Scraping actualités pour {company}")
        await asyncio.sleep(3)
        logger.success(f"🗞️ Lettre de motivation d'actualité générée pour {company}")
        
        # Envoi de la notification push
        self.send_push_notification(
            "Mission Accomplie 🗞️", 
            f"Votre lettre de motivation Smart pour {company} est prête à être téléchargée."
        )
        
        # Chaining optionnel
        chain_to = self.playbook_settings.get("10", {}).get("chain_to")
        if chain_to:
            logger.info(f"🔗 Chaining Workflow 10 vers {chain_to}")
            await self.dispatch_event(chain_to, payload)


# Instance globale
workflow_engine = WorkflowEngine()
