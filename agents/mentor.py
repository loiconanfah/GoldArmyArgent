from typing import Dict, Any, List
import json
from loguru import logger
from core.agent_base import BaseAgent

class MentorAgent(BaseAgent):
    """
    Agent responsible for coaching, CV auditing, Interview preparation, 
    and Portfolio generation.
    """
    
    def __init__(self):
        super().__init__()
        self.agent_name = "Mentor IA"
        # We can dynamically inject this into the base SYSTEM_PROMPT logic later
        # For now we use custom prompts
        
    async def think(self, user_input: Dict[str, Any]) -> Dict[str, Any]:
        """Entry point for the mentor flow."""
        action = user_input.get("action")
        cv_text = user_input.get("cv_text", "")
        
        if not cv_text:
             return {"status": "error", "message": "Un CV est requis pour utiliser le Mentor IA."}
             
        if action == "audit_cv":
            return await self._audit_cv(cv_text)
        elif action == "generate_portfolio":
            return await self._generate_portfolio(cv_text)
        else:
             return {"status": "error", "message": f"Action inconnue: {action}"}

    async def act(self, action_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Phase d'action: non utilisée pour le mentor direct, tout est dans think()"""
        return {"status": "success", "message": "Action non supportée directement."}

    async def _audit_cv(self, cv_text: str) -> Dict[str, Any]:
        """Provides a harsh, actionable critique of the CV."""
        logger.info("[Mentor] Auditing CV...")
        prompt = f"""Tu es un CTO impitoyable mais bienveillant. 
Analyse ce CV et donne un audit sous forme de points d'action concrets.
Sois direct. Ne fais pas de compliments inutiles.
1. Les 3 plus grandes failles (ce qui va disqualifier le candidat).
2. 3 actions clés à faire ce week-end pour améliorer le profil.
3. Les technologies manquantes selon le marché actuel.

CV:
{cv_text[:2000]}

Réponds au format Markdown clair."""
        
        response = await self.generate_response(prompt)
        return {"status": "success", "type": "audit", "content": response}

    async def _generate_portfolio(self, cv_text: str) -> Dict[str, Any]:
        """Generates a fully functional responsive HTML/CSS/JS portfolio based on the CV."""
        logger.info("[Mentor] Generating Web Portfolio from CV...")
        prompt = f"""Tu es un Développeur Web Front-End Senior et un Designer UX expert.
Je te fournis le texte brut d'un CV.
Ta mission est de générer le code source COMPLET d'un mini-site web Portfolio (Landing Page) "One-Page" ultra-moderne, esthétique et responsive.

Règles de design "Premium":
- Utilise Tailwind CSS via CDN (`<script src="https://cdn.tailwindcss.com"></script>`).
- Doit avoir un "Dark Mode" ou un thème sombre premium (Glassmorphism, dégradés subtils).
- Animations fluides au scroll ou au hover (CSS pur).
- Structure : Hero Section (Nom & Titre métier) -> À Propos (bio courte) -> Compétences (barres ou tags) -> Expériences (Timeline) -> Contact.
- Extrait toutes les infos utiles du CV ci-dessous pour remplir les textes. Ne mets pas de "Lorem Ipsum". Remplis avec les vraies données.
- Si le CV manque d'infos, invente des "Placeholders pertinents" (ex: [Lien vers mon GitHub]).

Renvoie UNIQUEMENT le code HTML final (commençant par `<!DOCTYPE html>`), prêt à être sauvegardé dans un fichier `index.html`. Ne mets PAS de balises markdown ```html autour.

Texte du CV:
{cv_text[:3000]}
"""
        response = await self.generate_response(prompt)
        
        # Clean up in case the LLM wrapped it in markdown anyway
        if response.startswith("```html"):
             response = response[7:]
        if response.endswith("```"):
             response = response[:-3]
             
        response = response.strip()
        
        return {
            "status": "success", 
            "type": "portfolio_html", 
            "content": response,
            "message": "Voici le code source de ton Portfolio. Tu peux le sauvegarder en 'index.html' et l'ouvrir dans ton navigateur."
        }
