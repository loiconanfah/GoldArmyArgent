from typing import Dict, Any, List
import json
import re
import time
from loguru import logger
from core.agent_base import BaseAgent
from llm.prompt_templates import PromptTemplates


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
            
            image_data = user_input.get("image_data")
            return await self._generate_portfolio(cv_text, theme=theme, image_data=image_data)
        else:
             return {"status": "error", "type": "chat", "content": f"Action inconnue: {action}"}

    async def act(self, action_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Phase d'action: non utilisée pour le mentor direct."""
        return {"status": "success", "message": "Action non supportée directement."}

    async def _audit_and_rewrite_cv(self, cv_text: str) -> Dict[str, Any]:
        """Audite et réécrit le CV en une seule passe pour l'optimisation ATS + feedback."""
        logger.info("[Mentor] Audit + Réécriture ATS du CV (Mode Rapide & Exhaustif)...")

        prompt = f"""Tu es un expert RH senior et un maître en optimisation ATS 2.0.
Ta mission est d'auditer et réécrire ce CV avec un niveau "God Mode".

**OBJECTIFS DE RÉÉCRITURE (CV_DATA) :**
1. **Expertise Adaptative :** Adapte dynamiquement la structure et le ton au profil (Santé, Tech, Management, etc.). Pour la santé, intègre massivement les mots-clés (**Loi 90, PDSB, PCI**).
2. **Score ATS Réel & Critique :** Fournis un score ATS **honnête et sévère**. Ne donne PAS de "faux espoir". Si le CV manque de chiffres, de résultats ou de mots-clés critiques, le score DOIT être bas (ex: 30-50%). Sois impitoyable sur la qualité pour forcer l'excellence.
3. **Optimisation Sémantique :** Utilise des mots-clés LSI pour dominer les recherches sémantiques.
4. **Humanisation (Anti-AI) :** Évite les structures prévisibles. Ton percutant et humain.

**NOTE IMPORTANTE :** Aucun méta-commentaire IA. Réponse JSON pur.

**STRUCTURE DU JSON :**
{{
  "audit": {{
    "ats_score": 45,  // SCORE RÉEL ET CRITIQUE (Soyez sévère)
    "candidate_name": "...",
    "candidate_title": "...",
    "scores": {{ "mots_cles": 40, "impact_resultats": 20, "mise_en_forme": 70, "lisibilite": 60, "experience_pertinence": 50 }},
    "failles": ["Failles réelles"],
    "actions": ["Actions correctrices"],
    "tech_manquantes": ["..."],
    "points_forts": ["..."]
  }},
  "cv_data": {{
    "full_name": "...",
    "title": "...",
    "email": "...",
    "phone": "...",
    "location": "...",
    "linkedin": "...",
    "github": "...",
    "summary": "Résumé adapté au profil.",
    "experiences": [
      {{
        "title": "...",
        "company": "...",
        "location": "...",
        "start_date": "...",
        "end_date": "...",
        "bullets": ["Impact et résultats réels"]
      }}
    ],
    "skills": {{ "Langages/Expertises": ["..."], "Outils/Certifs": ["..."] }},
    "education": [ {{ "degree": "...", "institution": "...", "location": "...", "year": "..." }} ],
    "certifications": ["..."],
    "languages": ["..."]
  }}
}}

CV à traiter :
{cv_text[:5000]}

Réponse JSON pur uniquement:"""

        logger.debug(f"[Mentor] Prompt envoyé (taille: {len(prompt)})")
        response = await self.generate_response(prompt, max_tokens=8192, json_mode=True)
        
        if not response:
            raise Exception("L'API Gemini n'a retourné aucune réponse (Surcharge serveur 503 probable).")
            
        logger.debug(f"[Mentor] Réponse brute reçue (taille: {len(response)})")
        
        try:
            # Chercher le premier '{' et le dernier '}'
            start_index = response.find('{')
            end_index = response.rfind('}')
            
            if start_index != -1 and end_index != -1 and end_index > start_index:
                cleaned_response = response[start_index:end_index+1]
            else:
                cleaned_response = response.strip()
                # Retirer les backticks markdown si présents
                cleaned_response = re.sub(r'```json\s*', '', cleaned_response)
                cleaned_response = re.sub(r'```\s*', '', cleaned_response)

            parsed = json.loads(cleaned_response)
            audit_data = parsed.get("audit", {})
            cv_data = parsed.get("cv_data", {})
            
            # Ensure cv_data is a dict before dumping
            if isinstance(cv_data, str):
                try: cv_data = json.loads(cv_data)
                except: cv_data = {}
                
            cv_json = json.dumps(cv_data, ensure_ascii=False)

            logger.success("[Mentor] Audit JSON décodé avec succès.")
            return {
                "status": "success",
                "type": "cv_audit_rewrite",
                "audit": audit_data,   # dict avec ats_score, scores, failles, actions...
                "content": cv_json,    # JSON string du CV réécrit (pour download)
            }
        except Exception as e:
            logger.error(f"[Mentor] Échec critique du parsing JSON: {e}")
            logger.debug(f"[Mentor] Début de la réponse problématique: {response[:200]}...")
            
            # Fallback Chat mais avec un message d'explication
            return {
                "status": "success",
                "type": "chat",
                "content": f"⚠️ Désolé, l'analyse détaillée a rencontré une erreur technique de formatage. \n\nVoici néanmoins l'analyse brute générée :\n\n{response}"
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

        response = await self.generate_response(prompt, max_tokens=8192, json_mode=True)
        
        # Nettoyage ultra-robuste avec Regex pour extraire le JSON même entouré de texte ou de Markdown
        import re
        try:
            # Chercher le premier '{' et le dernier '}'
            start_index = response.find('{')
            end_index = response.rfind('}')
            
            if start_index != -1 and end_index != -1 and end_index > start_index:
                cleaned_response = response[start_index:end_index+1]
            else:
                cleaned_response = response.strip()
                # Retirer les backticks markdown si présents
                cleaned_response = re.sub(r'```json\s*', '', cleaned_response)
                cleaned_response = re.sub(r'```\s*', '', cleaned_response)

            cv_data = json.loads(cleaned_response)
            logger.success("[Mentor] Réécriture CV décodée avec succès.")
            return {
                "status": "success",
                "type": "cv_rewrite",
                "content": cleaned_response,   # JSON string pour le frontend
                "cv_data": cv_data             # Dict Python pour usage interne
            }
        except Exception as e:
            logger.error(f"[Mentor] Erreur critique parsing réécriture CV: {e}")
            logger.debug(f"[Mentor] Réponse brute: {response[:200]}...")
            return {
                "status": "success",
                "type": "chat",
                "content": f"⚠️ Le moteur IA a retourné un format inattendu pour la réécriture. Voici le résultat brut :\n\n{response}"
            }

    async def _generate_portfolio(self, cv_text: str, theme: str = "GoldArmy Premium", image_data: str = None) -> Dict[str, Any]:
        """Generates a structured portfolio project (HTML/CSS/JS) in JSON format."""
        logger.info(f"[Mentor] Generating multi-file Portfolio project with theme: {theme}...")
        
        # Prompt construit par concaténation (pas de f-string) pour éviter tout conflit avec {} du JS/CSS
        image_line = ("- INSPIRATION IMAGE : Je t'ai fourni une image de design en pièce jointe. "
                      "IGNORE le thème ci-dessus si l'image propose une direction plus moderne ou pertinente. "
                      "Inspire-toi FORTEMENT de ses couleurs, de son layout et de son ambiance.") if image_data else ""

        prompt = (
            "Tu es un Senior Web Architect & Lead UX Designer chez GoldArmy.\n"
            "Ta mission : Créer un Portfolio \"GOD MODE\" (Ultra-Premium, Moderne, Futuriste) basé sur ce CV :\n"
            + cv_text[:4000] +
            "\n\n[DESIGN_SYSTEM_MANDATORY]\n"
            "- Thème : " + theme + "\n"
            "- Styles : Glassmorphism, Mesh Gradients, Bento Grid (si pertinent).\n"
            + (image_line + "\n" if image_line else "") +
            "- Typographie : Utilise Google Fonts (ex: Inter, Montserrat, Syne) via @import dans le CSS.\n"
            "- Couleurs : Palettes vibrantes et contrastées adaptées au thème.\n"
            "\n[TECHNICAL_STACK]\n"
            "- Structure : HTML5 Sémantique.\n"
            "- Styling : Tailwind CSS (via CDN) + CSS Custom pour les animations complexes (@keyframes).\n"
            "- Interactivité : JavaScript Vanille OBLIGATOIRE (Minimum 50 lignes). Implémente :\n"
            "    1. Un système de \"Reveal on Scroll\" via Intersection Observer pour chaque section.\n"
            "    2. Un effet de parallax ou de curseur personnalisé si le thème s'y prête.\n"
            "    3. Une gestion de filtrage pour les compétences ou les projets.\n"
            "    4. Un système de navigation fluide (Smooth Scroll) manuel si nécessaire.\n"
            "\n[INSTRUCTIONS_CRUCIALES]\n"
            "- Réponds UNIQUEMENT avec les balises [SECTION]. Aucun texte en dehors.\n"
            "- N'utilise PAS de blocs de code markdown (pas de ```) à l'intérieur des balises, mets le code BRUT.\n"
            "- Images : Utilise des images Unsplash (ex: https://images.unsplash.com/photo-1460925895917-afdab827c52f?q=80&w=2426) pour un rendu pro.\n"
            "- JavaScript : Le code DOIT être complet, commenté et fonctionnel. INTERDICTION de cloner des éléments DOM lors du clic ou du scroll.\n"
            "- Navigation : Chaque lien de la navbar (ex: href=\"#about\") DOIT correspondre à un ID unique sur une section. "
            "Le JS doit gérer le smooth scroll via element.scrollIntoView({behavior: 'smooth'}) sans modifier la structure du document. "
            "NE JAMAIS utiliser href=\"#\" vide ou de liens relatifs.\n"
            "- Sécurité : Interdiction formelle d'accéder à window.top, window.parent ou de modifier window.location.\n"
            "\n[PERSONALITY_ANALYSIS]\n"
            "(Analyse pro ultra-courte + Choix de la direction artistique)\n"
            "\n[HTML_CODE]\n"
            "(Code HTML complet - Inclut les scripts et styles via balises standard)\n"
            "\n[CSS_CODE]\n"
            "(Animations @keyframes et styles spécifiques non-Tailwind)\n"
            "\n[JS_CODE]\n"
            "(Logique d'animation et interactions réelles. Pas de commentaire vide !)\n"
        )
        response = await self.generate_response(prompt, max_tokens=8192, image_data=image_data)
        
        # Extraction par Regex unifiée et insensible à la casse
        def extract_section(tag, text):
            pattern = rf"\[{tag}\](.*?)(\[\w+_CODE\]|\[\w+_ANALYSIS\]|\[\w+_CRUCIALES\]|$)"
            match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
            if not match: return ""
            # Nettoyage profond (Markdown blocks)
            content = match.group(1).strip()
            content = re.sub(r'```[a-z]*\n?', '', content, flags=re.IGNORECASE)
            content = re.sub(r'```$', '', content)
            return content.strip()

        try:
            analysis = extract_section("PERSONALITY_ANALYSIS", response)
            html = extract_section("HTML_CODE", response)
            css = extract_section("CSS_CODE", response)
            js = extract_section("JS_CODE", response)
            
            project = {
                "personality_analysis": analysis or "Profil innovant et professionnel.",
                "html": html or "<h1>Erreur : Flux de données interrompu. Réessaie.</h1>",
                "css": css or "/* Standard Style */",
                "js": js or "// Standard Interactivity",
                "theme_applied": theme
            }
            
            return {
                "status": "success", 
                "type": "portfolio_project", 
                "project": project,
                "content": project["html"],
                "message": f"Analyse : {project['personality_analysis']}"
            }
        except Exception as e:
            logger.error(f"[Mentor] Erreur extraction projet portfolio: {e}")
            logger.debug(f"[Mentor] Réponse brute : {response[:200]}...")
            return {
                "status": "error",
                "type": "chat",
                "content": "⚠️ Une erreur est survenue lors de la structuration de ton projet. Réessaie avec une demande plus courte ou contacte le support."
            }
