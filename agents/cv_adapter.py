import json
import re
from loguru import logger
from typing import Dict, Any

from core.agent_base import BaseAgent

class CVAdapterAgent(BaseAgent):
    """
    Agent spécialisé dans l'adaptation de CV et la génération de projets 
    pour combler les lacunes d'expérience via Gemini 3.1 Pro.
    """
    def __init__(self):
        super().__init__(name="CVAdapterAgent")
        from llm.unified_client import UnifiedLLMClient
        self.llm = UnifiedLLMClient()

    async def think(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Méthode abstraite requise par BaseAgent"""
        return {}
        
    async def act(self, action_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Méthode abstraite requise par BaseAgent"""
        return {}
        
    async def adapt(self, job_title: str, job_desc: str, cv_text: str) -> Dict[str, Any]:
        """
        Analyse l'offre et le CV, puis génère un CV adapté en Markdown 
        et des projets recommandés en JSON.
        """
        
        system_prompt = """Tu es un expert en recrutement technique de classe mondiale.
Ton but est d'analyser le CV d'un candidat par rapport à une offre d'emploi spécifique.
Tu vas réécrire un résumé percutant (en Markdown) pour le candidat qui met en valeur ses forces exactes pour CE poste.
Ensuite, tu vas identifier ce qui lui manque (expériences, technos) et lui proposer 2 à 3 projets ultra-concrets à coder ce week-end pour bluffer le recruteur.

Réponds TOUJOURS au format JSON strict avec EXACTEMENT cette structure (sans balises markdown ```json autour):
{
  "markdown": "## Résumé Executif\\n\\nIci ton résumé pro...\\n\\n### Points Forts pour le Poste\\n- Point 1...",
  "projects": [
    {
      "title": "Nom du Projet",
      "desc": "Description d'1 phrase du projet à faire et pourquoi il comble la lacune."
    }
  ]
}
"""

        user_prompt = f"""
OFFRE D'EMPLOI ({job_title}):
{job_desc[:3000]}

CV DU CANDIDAT:
{cv_text[:3000]}

Génère ton analyse JSON maintenant.
"""
        
        try:
            # We explicitly use gemini by forcing the model tag or relying on UnifiedClient priority
            logger.info(f"🧠 Lancement de l'Adaptation CV pour: {job_title}")
            response = await self.llm.generate(prompt=user_prompt, system=system_prompt)
            
            # Nettoyage robuste pour du JSON
            clean_resp = response.replace("```json", "").replace("```", "").strip()
            
            # Parsing direct
            try:
                data = json.loads(clean_resp)
                return data
            except json.JSONDecodeError:
                logger.warning("Échec du parsing JSON direct. Tentative de récupération via regex.")
                # Essayer d'extraire un bloc json si encodé bizarrement
                # (Dans ce contexte on cherche d'abord la racine {})
                match = re.search(r'\{.*\}', clean_resp, re.DOTALL)
                if match:
                    return json.loads(match.group(0))
                else:
                    logger.warning("Regex n'a pas pu extraire de JSON.")
                    return {
                        "markdown": "## Résumé\n\nErreur de formatage de l'IA (JSON invalide).",
                        "projects": []
                    }

        except Exception as e:
            logger.error(f"❌ Erreur critique CVAdapterAgent: {e}")
            return {
                "markdown": "## Résumé Temporaire\n\nUne erreur est survenue lors de l'adaptation avec Gemini 3. Veuillez réessayer.",
                "projects": [
                    {
                        "title": "Debug API",
                        "desc": "Le serveur IA a rencontré une surcharge ou une erreur de parsing."
                    }
                ]
            }
