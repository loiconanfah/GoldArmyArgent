from typing import Dict, Any, List
import json
from loguru import logger
from core.agent_base import BaseAgent


class MentorAgent(BaseAgent):
    """
    Agent responsible for coaching, CV auditing, Interview preparation, 
    Portfolio generation, and ATS-optimized CV rewriting.
    """
    
    def __init__(self):
        super().__init__()
        self.agent_name = "Mentor IA"
        
    async def think(self, user_input: Dict[str, Any]) -> Dict[str, Any]:
        """Entry point for the mentor flow."""
        action = user_input.get("action")
        cv_text = user_input.get("cv_text", "")
        
        if not cv_text:
             return {
                 "status": "error", 
                 "type": "chat",
                 "content": "❌ Un CV est requis. Uploade ton PDF via le bouton **'Ajouter CV (PDF)'** en haut à droite."
             }
             
        # audit_cv et rewrite_cv fusionnés en un seul outil
        if action in ["audit_cv", "rewrite_cv"]:
            return await self._audit_and_rewrite_cv(cv_text)
        elif action == "generate_portfolio":
            # Extraire le thème potentiel de la requête
            query = user_input.get("query", "").lower()
            theme = "GoldArmy Premium"
            if "matrix" in query: theme = "Matrix Hacker"
            elif "moderne" in query: theme = "Modern Professional"
            elif "minimaliste" in query: theme = "Minimalist Clean"
            elif "futuriste" in query: theme = "Cyber Futurism"
            elif "élégant" in query: theme = "Elegant Luxury"
            
            return await self._generate_portfolio(cv_text, theme=theme)
        else:
             return {"status": "error", "type": "chat", "content": f"Action inconnue: {action}"}

    async def act(self, action_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Phase d'action: non utilisée pour le mentor direct."""
        return {"status": "success", "message": "Action non supportée directement."}

    async def _audit_and_rewrite_cv(self, cv_text: str) -> Dict[str, Any]:
        """Audite et réécrit le CV en une seule passe pour l'optimisation ATS + feedback."""
        logger.info("[Mentor] Audit + Réécriture ATS du CV...")

        prompt = f"""Tu es un expert RH senior, recruteur tech et optimiseur ATS de haut niveau.
Tu as reçu un CV. Tu dois faire DEUX choses :
1. **AUDIT GRAPHIQUE** avec scores numériques précis.
2. **RÉÉCRITURE ATS** : Version restructurée et optimisée.

**Renvoie UNIQUEMENT ce JSON valide (sans texte avant/après, sans markdown) :**
{{
  "audit": {{
    "ats_score": 72,
    "candidate_name": "Yvan Loic Nanfah",
    "candidate_title": "Développeur C#",
    "scores": {{
      "mots_cles": 65,
      "impact_resultats": 45,
      "mise_en_forme": 80,
      "lisibilite": 70,
      "experience_pertinence": 75
    }},
    "failles": [
      "Aucun résultat quantifié (chiffres, %, délais) dans les expériences",
      "Résumé absent ou trop générique — perd des mots-clés ATS cruciaux",
      "Technologies clés manquantes par rapport au marché 2025"
    ],
    "actions": [
      "Ajouter 2-3 chiffres concrets par poste (ex: 'réduit le temps de déploiement de 40%')",
      "Réécrire le résumé avec 5+ mots-clés techniques ciblés",
      "Ajouter CI/CD, Docker, Azure/AWS dans la section compétences"
    ],
    "tech_manquantes": ["Docker", "Kubernetes", "CI/CD", "Azure", "React"],
    "points_forts": [
      "Stack technique solide (C#, .NET)",
      "Expérience en développement logiciel démontrée"
    ]
  }},
  "cv_data": {{
    "full_name": "Prénom Nom",
    "title": "Titre professionnel",
    "email": "email@example.com",
    "phone": "+1 (514) xxx-xxxx",
    "location": "Ville, Province",
    "linkedin": "linkedin.com/in/xxx",
    "github": "github.com/xxx",
    "summary": "Résumé 3-4 phrases percutantes riche en mots-clés ATS",
    "experiences": [
      {{
        "title": "Titre du poste",
        "company": "Entreprise",
        "location": "Ville, Province",
        "start_date": "Mois YYYY",
        "end_date": "Présent",
        "bullets": [
          "Développé X fonctionnalité avec Y technologie, améliorant Z de N%",
          "Optimisé le pipeline CI/CD, réduisant le temps de build de 30%"
        ]
      }}
    ],
    "skills": {{
      "Langages": ["C#", "Python", "JavaScript"],
      "Frameworks": [".NET", "React", "FastAPI"],
      "Outils": ["Git", "Docker", "Azure DevOps"],
      "Bases de données": ["SQL Server", "PostgreSQL"]
    }},
    "education": [
      {{
        "degree": "Bac. en Informatique",
        "institution": "Université X",
        "location": "Ville, Province",
        "year": "2023"
      }}
    ],
    "certifications": ["Certification - Émetteur (Année)"],
    "languages": ["Français (natif)", "Anglais (avancé)"]
  }}
}}

**Règles ATS pour la réécriture :** verbes d'action forts, résultats quantifiés, mots-clés techniques, mono-colonne, pas de tableau.

CV à analyser :
{cv_text[:4000]}

RÉPONSE : JSON uniquement, rien d'autre."""

        response = await self.generate_response(prompt, json_mode=True)

        # Nettoyage robuste avec Regex pour extraire le JSON même entouré de texte
        import re
        match = re.search(r'\{.*\}', response, re.DOTALL)
        if match:
            response = match.group(0)
        else:
            response = response.strip()
            
        # Retirer d'éventuels backticks résiduels
        response = response.replace("```json", "").replace("```", "").strip()

        try:
            parsed = json.loads(response)
            audit_data = parsed.get("audit", {})
            cv_data = parsed.get("cv_data", {})
            
            # Ensure cv_data is a dict before dumping (in case the LLM returned a string somehow)
            if isinstance(cv_data, str):
                try: cv_data = json.loads(cv_data)
                except: cv_data = {}
                
            cv_json = json.dumps(cv_data, ensure_ascii=False)

            return {
                "status": "success",
                "type": "cv_audit_rewrite",
                "audit": audit_data,   # dict avec ats_score, scores, failles, actions...
                "content": cv_json,    # JSON string du CV réécrit (pour download)
            }
        except json.JSONDecodeError as e:
            logger.error(f"[Mentor] Parsing JSON échoué: {e}")
            return {
                "status": "success",
                "type": "chat",
                "content": response
            }

    async def _rewrite_cv(self, cv_text: str) -> Dict[str, Any]:
        """Rewrites the CV with ATS-optimized formatting and returns structured JSON."""
        logger.info("[Mentor] Réécriture CV ATS...")
        
        prompt = f"""Tu es un expert en recrutement technique et optimisation ATS (Applicant Tracking System).
Ta mission : réécrire ce CV pour qu'il soit PARFAIT pour passer les filtres ATS des grandes entreprises tech.

**Règles ATS obligatoires que tu dois appliquer :**
- Utilise des mots-clés techniques précis (langages, frameworks, outils)
- Bullet points avec verbes d'action forts (Développé, Optimisé, Déployé, Conçu, etc.)
- Quantifie les réalisations (%, chiffres, délais) quand possible ou ajoute [À quantifier]
- Sections standardisées : Résumé, Expériences, Compétences, Formation, Certifications
- Pas de tableaux, pas de colonnes, pas d'images (les ATS ne lisent pas ça)
- Langage professionnel, concis, sans faute

**Renvoie ta réponse UNIQUEMENT en JSON valide avec cette structure exacte :**
{{
  "full_name": "Prénom Nom",
  "title": "Titre professionnel (ex: Développeur Full-Stack Senior)",
  "email": "email@example.com",
  "phone": "+1 (514) xxx-xxxx",
  "location": "Ville, Province",
  "linkedin": "linkedin.com/in/xxx",
  "github": "github.com/xxx",
  "summary": "Résumé professionnel de 3-4 phrases percutantes et riche en mots-clés",
  "experiences": [
    {{
      "title": "Titre du poste",
      "company": "Nom entreprise",
      "location": "Ville, Province",
      "start_date": "Mois YYYY",
      "end_date": "Mois YYYY ou Présent",
      "bullets": [
        "• Verbe d'action + contexte + résultat quantifié",
        "• Verbe d'action + technologie utilisée + impact"
      ]
    }}
  ],
  "skills": {{
    "Langages": ["Python", "C#", "JavaScript"],
    "Frameworks": ["React", ".NET", "FastAPI"],
    "Outils": ["Git", "Docker", "Azure"],
    "Bases de données": ["PostgreSQL", "MongoDB"]
  }},
  "education": [
    {{
      "degree": "Bac. en Génie Informatique",
      "institution": "Université X",
      "location": "Ville, Province",
      "year": "2023"
    }}
  ],
  "certifications": ["Certification 1 - Émetteur (Année)"],
  "languages": ["Français (natif)", "Anglais (avancé)"]
}}

CV original à réécrire :
{cv_text[:4000]}

IMPORTANT: Réponds UNIQUEMENT avec le JSON, sans texte avant ni après, sans balises markdown."""

        response = await self.generate_response(prompt, json_mode=True)
        
        # Nettoyage robuste avec Regex pour extraire le JSON même entouré de texte
        import re
        match = re.search(r'\{.*\}', response, re.DOTALL)
        if match:
            response = match.group(0)
        else:
            response = response.strip()
            
        # Retirer d'éventuels backticks résiduels
        response = response.replace("```json", "").replace("```", "").strip()
        
        # Valider que c'est du JSON
        try:
            cv_data = json.loads(response)
            return {
                "status": "success",
                "type": "cv_rewrite",
                "content": response,   # JSON string pour le frontend
                "cv_data": cv_data     # Dict Python pour usage interne
            }
        except json.JSONDecodeError as e:
            logger.error(f"[Mentor] Erreur parsing JSON CV: {e} | Response: {response[:200]}")
            # Fallback: retourner quand même en demandant de réessayer
            return {
                "status": "error",
                "type": "chat",
                "content": f"⚠️ Le moteur IA a retourné un format inattendu. Réessaie en tapant **'Réécris mon CV'**.\n\nDétail technique: {str(e)}"
            }

    async def _generate_portfolio(self, cv_text: str, theme: str = "GoldArmy Premium") -> Dict[str, Any]:
        """Generates a fully functional responsive HTML/CSS/JS portfolio based on the CV."""
        import random
        
        # Variabilité de design pour éviter la répétition
        design_variants = [
            "Use a layout with a sticky side navigation bar on desktop.",
            "Use a centered bento-box grid for the projects section.",
            "Use large, bold typography (Serif for headings) with a minimalist aesthetic.",
            "Implement a split-screen hero section: Image/Graphic on one side, text on the other.",
            "Use floating glassmorphism cards with subtle parallax effects."
        ]
        chosen_variant = random.choice(design_variants)
        
        logger.info(f"[Mentor] Generating Web Portfolio with theme: {theme}...")
        
        prompt = f"""Tu es un Tech Lead & Designer UX Expert réputé pour tes créations 'GoldArmy Premium'.
Ta mission est de générer le code source pur (HTML/CSS/JS) d'un portfolio ultra-premium.

CONTENU : Utilise les infos de ce CV :
{cv_text[:4000]}

DIRECTIVES DE DESIGN :
- Thème demandé : {theme}
- Framework : Tailwind CSS (via CDN) + CSS Custom pour les effets.
- Bibliothèques recommandées : AOS (Animate On Scroll) et FontAwesome.
- Variabilité imposée : {chosen_variant}
- Assure une navigation fluide, un menu mobile burger, et un design 'Pixel Perfect'.

IMPORTANT - FORMAT DE RÉPONSE :
Renvoie UNIQUEMENT le code HTML complet (<!DOCTYPE html> ... </html>).
NE FAIS PAS de préambule, pas de commentaires de discussion, pas de résumé de tes choix.
L'utilisateur injecte ta réponse directement dans un moteur de rendu, donc tout texte en dehors des balises HTML cassera le site.
"""
        response = await self.generate_response(prompt)
        
        # Nettoyage HTML Robuste par Regex
        import re
        html_match = re.search(r'<!DOCTYPE html>.*</html>', response, re.DOTALL | re.IGNORECASE)
        if html_match:
            clean_html = html_match.group(0)
        else:
            # Fallback si DOCTYPE manquant mais <html> présent
            html_tag_match = re.search(r'<html.*</html>', response, re.DOTALL | re.IGNORECASE)
            if html_tag_match:
                clean_html = "<!DOCTYPE html>\n" + html_tag_match.group(0)
            else:
                # Si vraiment pas de balise html, on nettoie les backticks et on espère le mieux
                clean_html = response.replace("```html", "").replace("```", "").strip()
        
        return {
            "status": "success", 
            "type": "portfolio_html", 
            "content": clean_html,
            "message": f"Voici ton Portfolio généré avec le thème {theme}. Vérifie l'aperçu dans ton Workspace !"
        }
