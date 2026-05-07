import json
import re
from typing import Dict, Any, List
from loguru import logger
from llm.unified_client import UnifiedLLMClient
unified_client = UnifiedLLMClient()

class PreInterviewAgent:
    """Agent chargé de préparer les simulations d'entretien."""

    async def prepare_simulation(self, company_name: str, job_title: str, user_cv: str = "") -> Dict[str, Any]:
        """Génère un plan de préparation personnalisé (Questions, STAR, Conseils)."""
        logger.info(f"[Pre-Interview] Préparation pour {job_title} chez {company_name}")

        prompt = f"""Tu es un coach en recrutement expert. Prépare un candidat pour un entretien chez {company_name} pour le poste de {job_title}.
CV CANDIDAT: {user_cv[:2500]}

Génère un plan de préparation structuré EXACTEMENT au format JSON suivant:
{{
  "top_questions": ["Question 1", "Question 2", "Question 3", "Question 4", "Question 5"],
  "star_points": ["Point STAR 1", "Point STAR 2", "Point STAR 3"],
  "company_insider": ["Conseil 1", "Conseil 2"],
  "elevator_pitch": "Le pitch de 30 secondes..."
}}

CONSIGNES:
- Les questions doivent être techniques et comportementales.
- Les points STAR doivent s'appuyer sur les expériences réelles du CV.
- Ne retourne RIEN d'autre que le JSON. Pas de blabla, pas de markdown."""

        try:
            response = await unified_client.generate(
                prompt,
                system="Tu es un expert en recrutement. Réponds exclusivement en JSON pur, sans balises markdown.",
                json_mode=True
            )
            
            # Nettoyage JSON robuste
            clean_json = response.strip()
            # Retirer les blocs de code markdown si présents
            clean_json = re.sub(r'```json\s*', '', clean_json, flags=re.IGNORECASE)
            clean_json = re.sub(r'```\s*', '', clean_json)
            
            # Extraire uniquement le contenu entre les premières et dernières accolades
            match = re.search(r'\{.*\}', clean_json, re.DOTALL)
            if match:
                clean_json = match.group(0)
            
            data = json.loads(clean_json)
            return data
        except Exception as e:
            logger.error(f"[Pre-Interview] Erreur préparation IA (Parsing): {e}")
            logger.debug(f"[Pre-Interview] Réponse brute problématique: {response[:500]}...")
            
            # Fallback structuré mais dynamique
            return {
                "top_questions": [f"Pourquoi voulez-vous rejoindre {company_name} ?", "Parlez-moi de votre expérience technique.", "Comment gérez-vous le stress ?"],
                "star_points": ["Une situation où vous avez résolu un bug critique.", "Un projet mené à bien en équipe.", "Une initiative personnelle pour améliorer un process."],
                "company_insider": [f"Renseignez-vous sur les derniers produits de {company_name}.", "Préparez des questions sur l'organisation technique."],
                "elevator_pitch": f"Bonjour, je suis un expert passionné et je souhaite mettre mes compétences au service de {company_name} en tant que {job_title}."
            }

pre_interview_agent = PreInterviewAgent()
