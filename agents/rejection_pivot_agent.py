"""
GoldArmy — Rejection Pivot Agent (Workflow #9)
=============================================
Aide l'utilisateur à rebondir après un refus :
1. Génère un email de demande de feedback.
2. Trouve 3 offres alternatives similaires.
3. Propose une micro-stratégie d'ajustement.
"""

import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional
from loguru import logger

from llm.unified_client import UnifiedLLMClient
from agents.job_searcher import JobSearchAgent

class RejectionPivotAgent:
    """Agent spécialisé dans le rebond post-refus."""

    def __init__(self):
        self.llm = UnifiedLLMClient()
        self.job_searcher = JobSearchAgent()

    async def initialize(self):
        """Initialise les composants nécessaires."""
        await self.job_searcher.initialize()

    async def run_pivot(self, user_id: str, app_id: str) -> Dict[str, Any]:
        """
        Exécute le workflow complet de pivot pour une candidature donnée.
        """
        from core.database import get_db
        db = get_db()

        # 1. Charger les données
        app = await db.applications.find_one({"id": app_id, "user_id": user_id}, {"_id": 0})
        if not app:
            logger.error(f"[RejectionPivot] Application {app_id} introuvable.")
            return {"status": "error", "message": "Candidature introuvable."}

        user = await db.users.find_one({"id": user_id}, {"_id": 0}) or {}
        user_name = user.get("full_name") or user.get("email", "le candidat")
        cv_text = user.get("cv_text", "")

        company_name = app.get("company_name", "l'entreprise")
        job_title = app.get("job_title", "le poste")

        logger.info(f"🛡️ [RejectionPivot] Pivot en cours pour {job_title} chez {company_name}")

        # 2. Exécution parallèle des tâches
        feedback_task = self.generate_feedback_email(user_name, company_name, job_title)
        offers_task = self.find_alternative_offers(job_title, user.get("location", "Montreal, QC"))
        strategy_task = self.generate_pivot_strategy(job_title, company_name, cv_text)

        feedback_email, alt_offers, pivot_tip = await asyncio.gather(
            feedback_task, offers_task, strategy_task
        )

        # 3. Préparation du résultat
        result = {
            "app_id": app_id,
            "company_name": company_name,
            "job_title": job_title,
            "feedback_email": feedback_email,
            "alternative_offers": alt_offers[:3], # Top 3
            "pivot_tip": pivot_tip,
            "processed_at": datetime.utcnow().isoformat()
        }

        # 4. Persistance (optionnelle, peut être stockée dans l'application)
        await db.applications.update_one(
            {"id": app_id, "user_id": user_id},
            {"$set": {
                "rejection_pivot_data": result,
                "status": "REJECTED" # S'assure que le statut est bien marqué
            }}
        )

        return result

    async def generate_feedback_email(self, user_name: str, company_name: str, job_title: str) -> str:
        """Génère un email pour demander du feedback constructif."""
        prompt = (
            "Tu rédiges un email professionnel et élégant pour demander du feedback suite à un refus.\n"
            "Le ton doit être humble, reconnaissant et axé sur l'amélioration continue.\n\n"
            f"Contexte :\n"
            f"- Candidat : {user_name}\n"
            f"- Entreprise : {company_name}\n"
            f"- Poste : {job_title}\n\n"
            "Structure :\n"
            "1. Remercier pour la réponse et pour le temps accordé.\n"
            "2. Exprimer sa déception tout en respectant la décision.\n"
            "3. Demander poliment s'il est possible d'avoir 1 ou 2 points d'amélioration spécifiques sur le profil ou l'entretien.\n"
            "4. Souhaiter une bonne continuation.\n\n"
            "Réponds UNIQUEMENT par le texte de l'email."
        )
        try:
            return await self.llm.chat([{"role": "user", "content": prompt}], model="gemini-2.0-flash")
        except Exception as e:
            logger.error(f"[RejectionPivot] Erreur feedback email: {e}")
            return f"Bonjour,\n\nMerci pour votre retour concernant ma candidature pour le poste de {job_title}.\n\nPourriez-vous me donner quelques pistes d'amélioration ?\n\nCordialement,\n{user_name}"

    async def find_alternative_offers(self, job_title: str, location: str) -> List[Dict[str, Any]]:
        """Trouve des offres similaires pour rebondir."""
        try:
            search_task = {
                "query": job_title,
                "location": location,
                "nb_results": 5
            }
            # On utilise le job_searcher qui gère déjà le cache et le multi-API
            search_result = await self.job_searcher.execute_task(search_task)
            return search_result.get("matched_jobs", [])
        except Exception as e:
            logger.error(f"[RejectionPivot] Erreur recherche offres: {e}")
            return []

    async def generate_pivot_strategy(self, job_title: str, company_name: str, cv_text: str) -> str:
        """Génère un conseil stratégique pour le prochain essai."""
        prompt = (
            "Tu es un coach en carrière expert. Un candidat vient d'être refusé pour le poste de "
            f"'{job_title}' chez '{company_name}'.\n"
            "Analyse brièvement son profil (CV ci-dessous) et donne UN SEUL conseil percutant (2 phrases max) "
            "pour 'pivoter' vers sa prochaine candidature pour ce type de poste.\n\n"
            f"CV (extrait) :\n{cv_text[:2000]}\n\n"
            "Réponds avec un conseil direct et actionnable."
        )
        try:
            return await self.llm.chat([{"role": "user", "content": prompt}], model="gemini-2.0-flash")
        except Exception as e:
            logger.error(f"[RejectionPivot] Erreur pivot strategy: {e}")
            return "Misez davantage sur vos réalisations chiffrées lors de vos prochains entretiens pour démontrer votre impact direct."

# Singleton
rejection_pivot_agent = RejectionPivotAgent()
