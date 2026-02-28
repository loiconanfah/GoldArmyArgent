from typing import Dict, Any, List
import json
import re
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
            
            image_data = user_input.get("image_data")
            return await self._generate_portfolio(cv_text, theme=theme, image_data=image_data)
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

    async def _generate_portfolio(self, cv_text: str, theme: str = "GoldArmy Premium", image_data: str = None) -> Dict[str, Any]:
        """Generates a structured portfolio project (HTML/CSS/JS) in JSON format."""
        logger.info(f"[Mentor] Generating multi-file Portfolio project with theme: {theme}...")
        
        prompt = f"""Tu es un Senior Web Architect & Lead UX Designer chez GoldArmy.
Ta mission : Créer un Portfolio "GOD MODE" (Ultra-Premium, Moderne, Futuriste) basé sur ce CV :
{cv_text[:4000]}

[DESIGN_SYSTEM_MANDATORY]
- Thème : {theme}
- Styles : Glassmorphism, Mesh Gradients, Bento Grid (si pertinent).
{"- INSPIRATION IMAGE : Je t'ai fourni une image de design en pièce jointe. IGNORE le thème ci-dessus si l'image propose une direction plus moderne ou pertinente. Inspire-toi FORTEMENT de ses couleurs, de son layout et de son ambiance." if image_data else ""}
- Typographie : Utilise Google Fonts (ex: Inter, Montserrat, Syne) via @import dans le CSS.
- Couleurs : Palettes vibrantes et contrastées adaptées au thème.

[TECHNICAL_STACK]
- Structure : HTML5 Sémantique.
- Styling : Tailwind CSS (via CDN) + CSS Custom pour les animations complexes (@keyframes).
- Interactivité : JavaScript Vanille OBLIGATOIRE (Minimum 50 lignes). Implémente :
    1. Un système de "Reveal on Scroll" via Intersection Observer pour chaque section.
    2. Un effet de Parrelative ou de curseur personnalisé si le thème s'y prête.
    3. Une gestion de filtrage pour les compétences ou les projets.
    4. Un système de navigation fluide (Smooth Scroll) manuel si nécessaire.

[INSTRUCTIONS_CRUCIALES]
- Réponds UNIQUEMENT avec les balises [SECTION]. Aucun texte en dehors.
- N'utilise PAS de blocs de code markdown (pas de ```) à l'intérieur des balises, mets le code BRUT.
- Images : Utilise des images Unsplash (ex: https://images.unsplash.com/photo-1460925895917-afdab827c52f?q=80&w=2426) pour un rendu pro.
- JavaScript : Le code DOIT être complet, commenté et fonctionnel dès l'ouverture.

[PERSONALITY_ANALYSIS]
(Analyse pro ultra-courte + Choix de la direction artistique)

[HTML_CODE]
(Code HTML complet - Inclut les scripts et styles via balises standard)

[CSS_CODE]
(Animations @keyframes et styles spécifiques non-Tailwind)

[JS_CODE]
(Logique d'animation et interactions réelles. Pas de commentaire vide !)
"""
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
