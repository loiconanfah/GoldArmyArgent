"""
GoldArmy — Ghostbuster Agent (Workflow #2)
==========================================
Détecte les candidatures sans réponse depuis > N jours ouvrables
et génère automatiquement un email de relance + message LinkedIn.
"""

from __future__ import annotations

import asyncio
from datetime import datetime, date, timedelta
from typing import Any, Dict, List, Optional

from loguru import logger


# ---------------------------------------------------------------------------
# Jours fériés fixes (France + Québec combinés — conservative approach)
# ---------------------------------------------------------------------------
def _public_holidays(year: int) -> set[date]:
    """Retourne un ensemble de jours fériés pour l'année donnée (France + Québec)."""
    from datetime import date as d
    holidays = {
        d(year, 1, 1),   # Jour de l'An
        d(year, 5, 1),   # Fête du Travail
        d(year, 5, 8),   # Victoire 1945 (France)
        d(year, 7, 14),  # Fête nationale (France)
        d(year, 8, 15),  # Assomption (France)
        d(year, 11, 1),  # Toussaint (France)
        d(year, 11, 11), # Armistice (France)
        d(year, 12, 25), # Noël
        d(year, 6, 24),  # Saint-Jean-Baptiste (Québec)
        d(year, 7, 1),   # Fête du Canada
        d(year, 9, 1),   # Fête du Travail (Québec — 1er lundi, approx)
    }
    return holidays


def calculate_working_days(start_date: datetime) -> int:
    """
    Calcule le nombre de jours ouvrables écoulés depuis start_date jusqu'à aujourd'hui.
    Exclut samedis, dimanches et jours fériés.
    """
    if not start_date:
        return 0

    start = start_date.date() if isinstance(start_date, datetime) else start_date
    today = date.today()

    if start >= today:
        return 0

    working_days = 0
    current = start + timedelta(days=1)  # On ne compte pas le jour de dépôt lui-même

    # Pré-calculer les jours fériés pour les années couvertes
    years = set(range(start.year, today.year + 1))
    all_holidays: set[date] = set()
    for y in years:
        all_holidays.update(_public_holidays(y))

    while current <= today:
        if current.weekday() < 5 and current not in all_holidays:  # Lun–Ven, non férié
            working_days += 1
        current += timedelta(days=1)

    return working_days


# ---------------------------------------------------------------------------
# GhostbusterAgent
# ---------------------------------------------------------------------------
class GhostbusterAgent:
    """Agent qui scanne le CRM à la recherche de candidatures fantômes."""

    def __init__(self, working_days_threshold: int = 15):
        self.threshold = working_days_threshold

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def scan_and_generate(
        self,
        user_id: str,
        chain_to: Optional[str] = None,
        force_regenerate: bool = False,
    ) -> Dict[str, Any]:
        """
        Scanne les candidatures de l'utilisateur, détecte celles éligibles
        (> N jours ouvrables sans réponse) et génère email + LinkedIn si nécessaire.

        Returns:
            {
                "eligible": [<ApplicationResult>, ...],
                "total_scanned": int,
                "threshold_days": int,
                "generated_at": str,
            }
        """
        from core.database import get_db
        db = get_db()

        # Récupère le profil user (pour personnaliser les relances)
        user_data = await db.users.find_one({"id": user_id}, {"_id": 0}) or {}
        user_name = user_data.get("full_name") or user_data.get("email", "le candidat")
        cv_text = user_data.get("cv_text", "")

        # Candidatures à statut "envoyée" : APPLIED ou FOLLOW_UP
        # On ne filtre PAS sur applied_at — beaucoup d'entrées n'ont pas ce champ.
        # Le fallback vers created_at est géré dans la boucle Python ci-dessous.
        cursor = db.applications.find(
            {
                "user_id": user_id,
                "status": {"$in": ["APPLIED", "FOLLOW_UP", "SENT"]},
            },
            {"_id": 0},
        ).sort("created_at", 1)  # sort par created_at qui est toujours présent

        apps: List[Dict] = await cursor.to_list(length=500)  # limite à 500 max
        total_scanned = len(apps)
        eligible = []

        for app in apps:
            try:
                # Priorité : applied_at → created_at → skip
                applied_at_raw = app.get("applied_at") or app.get("created_at")
                if not applied_at_raw:
                    logger.debug(f"[Ghostbuster] App {app.get('id')} ignorée : pas de date")
                    continue

                # Normaliser en datetime naive UTC
                if isinstance(applied_at_raw, datetime):
                    applied_at = applied_at_raw
                elif isinstance(applied_at_raw, str):
                    try:
                        applied_at = datetime.fromisoformat(applied_at_raw.replace("Z", "+00:00"))
                    except ValueError:
                        logger.debug(f"[Ghostbuster] App {app.get('id')} : date invalide '{applied_at_raw}'")
                        continue
                else:
                    # Type inconnu (ex: int timestamp)
                    try:
                        applied_at = datetime.utcfromtimestamp(float(applied_at_raw))
                    except Exception:
                        continue

                # Retirer le tzinfo pour comparer avec date.today()
                if applied_at.tzinfo is not None:
                    applied_at = applied_at.replace(tzinfo=None)

                working_days_elapsed = calculate_working_days(applied_at)

                if working_days_elapsed < self.threshold:
                    continue  # Pas encore éligible

                app_id = app.get("id", "")

                # Vérifier si une relance existe déjà (évite les doublons)
                has_relance = bool(app.get("relance_email"))
                if has_relance and not force_regenerate:
                    # Relance déjà générée → on la retourne sans re-générer
                    eligible.append({
                        "app_id": app_id,
                        "job_title": app.get("job_title", "Poste inconnu"),
                        "company_name": app.get("company_name", "Entreprise inconnue"),
                        "applied_at": applied_at.isoformat(),
                        "working_days_elapsed": working_days_elapsed,
                        "relance_email": app.get("relance_email", ""),
                        "relance_linkedin": app.get("relance_linkedin", ""),
                        "relance_sent_at": app.get("relance_sent_at"),
                        "relance_sent_via": app.get("relance_sent_via"),
                        "already_generated": True,
                    })
                    continue

                # Générer email + LinkedIn
                logger.info(f"[Ghostbuster] Génération relance pour {app.get('company_name')} ({working_days_elapsed}j ouvrables)")
                pack = await self._generate_followup_pack(
                    job_title=app.get("job_title", "le poste"),
                    company_name=app.get("company_name", "l'entreprise"),
                    notes=app.get("notes", ""),
                    user_name=user_name,
                    cv_text=cv_text,
                    working_days_elapsed=working_days_elapsed,
                    follow_up_count=app.get("follow_up_count", 0) + 1,
                )

                # Persister les relances générées dans MongoDB
                update_payload: Dict[str, Any] = {
                    "relance_email": pack["email"],
                    "relance_linkedin": pack["linkedin"],
                    "ghostbuster_checked_at": datetime.utcnow(),
                    "ghostbuster_eligible": True,
                }
                if app.get("status") != "FOLLOW_UP":
                    update_payload["status"] = "FOLLOW_UP"

                await db.applications.update_one(
                    {"id": app_id, "user_id": user_id},
                    {"$set": update_payload, "$inc": {"follow_up_count": 1}},
                )

                eligible.append({
                    "app_id": app_id,
                    "job_title": app.get("job_title", "Poste inconnu"),
                    "company_name": app.get("company_name", "Entreprise inconnue"),
                    "applied_at": applied_at.isoformat(),
                    "working_days_elapsed": working_days_elapsed,
                    "relance_email": pack["email"],
                    "relance_linkedin": pack["linkedin"],
                    "relance_sent_at": None,
                    "relance_sent_via": None,
                    "already_generated": False,
                })

            except Exception as e:
                logger.warning(f"[Ghostbuster] Erreur traitement app {app.get('id')}: {e}")
                continue

        logger.info(
            f"[Ghostbuster] Scan terminé pour user {user_id}: "
            f"{total_scanned} candidatures, {len(eligible)} éligibles."
        )

        return {
            "eligible": eligible,
            "total_scanned": total_scanned,
            "threshold_days": self.threshold,
            "generated_at": datetime.utcnow().isoformat(),
        }

    async def mark_sent(
        self,
        user_id: str,
        app_id: str,
        via: str = "manual",  # "email" | "linkedin" | "manual"
    ) -> bool:
        """Marque une relance comme envoyée dans MongoDB."""
        from core.database import get_db
        db = get_db()
        result = await db.applications.update_one(
            {"id": app_id, "user_id": user_id},
            {
                "$set": {
                    "relance_sent_at": datetime.utcnow(),
                    "relance_sent_via": via,
                    "status": "FOLLOW_UP",
                }
            },
        )
        return result.modified_count > 0

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    async def _generate_followup_pack(
        self,
        job_title: str,
        company_name: str,
        notes: str,
        user_name: str,
        cv_text: str,
        working_days_elapsed: int,
        follow_up_count: int,
    ) -> Dict[str, str]:
        """Génère un email de relance + un message LinkedIn via le LLM."""
        from llm.unified_client import UnifiedLLMClient

        llm = UnifiedLLMClient()

        # --- Email de relance ---
        tone_note = (
            "Ton légèrement plus direct, rappeler poliment qu'il s'agit d'une 2e relance."
            if follow_up_count > 1
            else "Ton professionnel et chaleureux, premier contact de relance."
        )

        email_prompt = (
            "Tu rédiges un email de relance professionnel COMPLET en français.\n"
            "Le mail doit contenir dans l'ordre :\n"
            "1) Objet: [sujet clair et percutant]\n"
            "2) Formule d'appel (ex: Bonjour, ou Bonjour Madame/Monsieur,)\n"
            "3) Corps (4 à 5 phrases) : rappeler la candidature (poste + entreprise), "
            "réaffirmer l'intérêt et la motivation, demander poliment où en est le processus.\n"
            "4) Formule de politesse (Cordialement,) puis [Prénom].\n\n"
            f"Contexte :\n"
            f"- Candidat : {user_name}\n"
            f"- Poste visé : {job_title}\n"
            f"- Entreprise : {company_name}\n"
            f"- Candidature envoyée il y a : {working_days_elapsed} jours ouvrables\n"
            f"- Notes supplémentaires : {notes or 'Aucune'}\n"
            f"- Ton : {tone_note}\n\n"
            "Réponds UNIQUEMENT par le texte complet de l'email, rien d'autre."
        )

        # --- Message LinkedIn ---
        linkedin_prompt = (
            "Tu rédiges un message de relance LinkedIn court et professionnel en français.\n"
            "Maximum 5 lignes. Aucune formule de politesse longue.\n"
            "Structure :\n"
            "- 1 phrase d'accroche (référencer la candidature)\n"
            "- 1-2 phrases sur l'intérêt et la valeur ajoutée du candidat\n"
            "- 1 question directe sur l'avancement du processus\n\n"
            f"Contexte :\n"
            f"- Candidat : {user_name}\n"
            f"- Poste visé : {job_title}\n"
            f"- Entreprise : {company_name}\n"
            f"- Délai : {working_days_elapsed} jours ouvrables sans retour\n\n"
            "Réponds UNIQUEMENT par le texte du message LinkedIn, rien d'autre."
        )

        try:
            # On lance les deux en parallèle pour aller plus vite
            email_task = llm.chat(
                [{"role": "user", "content": email_prompt}],
                model="gemini-2.0-flash",
                max_tokens=1024,
                temperature=0.65,
                timeout=90,
            )
            linkedin_task = llm.chat(
                [{"role": "user", "content": linkedin_prompt}],
                model="gemini-2.0-flash",
                max_tokens=400,
                temperature=0.65,
                timeout=90,
            )
            email_text, linkedin_text = await asyncio.gather(email_task, linkedin_task)

        except Exception as e:
            logger.error(f"[Ghostbuster] Erreur LLM: {e}")
            email_text = (
                f"Objet: Suivi de candidature — {job_title} chez {company_name}\n\n"
                f"Bonjour,\n\n"
                f"Je me permets de revenir vers vous concernant ma candidature pour le poste de {job_title} "
                f"que j'ai soumise il y a {working_days_elapsed} jours ouvrables.\n\n"
                f"Toujours très intéressé(e) par cette opportunité, je souhaitais savoir si vous aviez "
                f"pu prendre connaissance de mon dossier et où en est le processus de recrutement.\n\n"
                f"Je reste disponible pour tout complément d'information.\n\n"
                f"Cordialement,\n{user_name}"
            )
            linkedin_text = (
                f"Bonjour, je reviens vers vous concernant ma candidature pour le poste de {job_title} "
                f"chez {company_name}, envoyée il y a {working_days_elapsed} jours ouvrables. "
                f"Seriez-vous disponible pour un échange ? Merci d'avance."
            )

        return {
            "email": (email_text or "").strip(),
            "linkedin": (linkedin_text or "").strip(),
        }


# Singleton
ghostbuster_agent = GhostbusterAgent(working_days_threshold=15)
