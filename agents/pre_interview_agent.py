import json
import re
from typing import Dict, Any, List
from loguru import logger
from llm.unified_client import unified_client

class PreInterviewAgent:
    """Agent chargé de préparer les simulations d'entretien."""

    async def prepare_simulation(self, company_name: str, job_title: str, user_cv: str = "") -> Dict[str, Any]:
        """Génère un plan de préparation personnalisé (Questions, STAR, Conseils)."""
        logger.info(f"[Pre-Interview] Préparation pour {job_title} chez {company_name}")

        prompt = f"""Tu es un coach en recrutement expert. Prépare un candidat pour un entretien.
ENTREPRISE: {company_name}
POSTE: {job_title}
CV CANDIDAT: {user_cv[:2000]}

Génère un plan de préparation structuré en JSON avec:
1. "top_questions": Une liste de 5 questions probables pour ce poste.
2. "star_points": 3 points clés à aborder avec la méthode STAR (Situation, Task, Action, Result) basés sur le profil.
3. "company_insider": 2 conseils spécifiques sur la culture de {company_name} (ou du secteur si inconnu).
4. "elevator_pitch": Un pitch de 30 secondes pour se présenter.

RETOURNE UNIQUEMENT LE JSON."""

        try:
            response = await unified_client.generate(
                prompt,
                system="Tu es un expert en recrutement. Réponds exclusivement en JSON.",
                json_mode=True
            )
            # Nettoyage JSON au cas où
            raw = re.sub(r"^[^{\[\]]*", "", response.strip())
            raw = re.sub(r"[^{\[\]]*$", "", raw)
            data = json.loads(raw)
            return data
        except Exception as e:
            logger.error(f"[Pre-Interview] Erreur préparation IA: {e}")
            return {
                "top_questions": ["Présentez-vous", "Pourquoi nous rejoindre ?", "Quelle est votre plus grande réussite ?"],
                "star_points": ["Expérience passée", "Gestion de conflit", "Résultat chiffré"],
                "company_insider": ["Recherchez les dernières news", "Soyez vous-même"],
                "elevator_pitch": "Bonjour, je suis passionné par ce secteur..."
            }

pre_interview_agent = PreInterviewAgent()
