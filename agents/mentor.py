from typing import Dict, Any, List
import asyncio
import json
import re
import time
from loguru import logger
import httpx
from bs4 import BeautifulSoup
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
        
        linkedin_text = user_input.get("linkedin_text") or user_input.get("linkedin_profile", "")
        if not cv_text and not linkedin_text:
             return {
                 "status": "error", 
                 "type": "chat",
                 "content": "❌ Un CV ou un profil LinkedIn est requis pour utiliser cette fonctionnalité."
             }
             
        # audit_cv et rewrite_cv fusionnés en un seul outil
        if action in ["audit_cv", "rewrite_cv"]:
            return await self._audit_and_rewrite_cv(
                cv_text,
                job_text=user_input.get("job_text"),
                job_url=user_input.get("job_url")
            )
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
        elif action == "social_sniper":
            company = user_input.get("company", "l'entreprise")
            job = user_input.get("job", "le poste")
            return await self._generate_social_sniper_kit(cv_text, company, job)
        elif action == "post_interview_analysis":
            company = user_input.get("company", "l'entreprise")
            job = user_input.get("job", "le poste")
            debrief = user_input.get("debrief", {})
            return await self._generate_post_interview_kit(cv_text, company, job, debrief)
        elif action == "gold_profile_audit":
            linkedin_text = user_input.get("linkedin_text") or user_input.get("linkedin_profile", "")
            return await self._generate_gold_profile_audit(cv_text, linkedin_text)
        elif action == "gold_profile_plan":
            cv_text = user_input.get("cv_text", "")
            linkedin_text = user_input.get("linkedin_text", "")
            start_day = user_input.get("start_day", 1)
            days_count = user_input.get("days_count", 15)
            return await self._generate_gold_profile_plan(cv_text, linkedin_text, start_day=start_day, days_count=days_count)
        elif action == "gold_profile_post":
            topic = user_input.get("topic", "")
            format_type = user_input.get("format", "Text")
            linkedin_text = user_input.get("linkedin_text") or user_input.get("linkedin_profile", "")
            return await self._generate_gold_profile_post(cv_text, topic, format_type, linkedin_text)
        else:
             return {"status": "error", "type": "chat", "content": f"Action inconnue: {action}"}

    async def act(self, action_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Phase d'action: non utilisée pour le mentor direct."""
        return {"status": "success", "message": "Action non supportée directement."}

    async def _scrape_job_url(self, url: str) -> str:
        """Scrape the text content of a job offer URL."""
        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    "Accept": "text/html,application/xhtml+xml",
                    "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
                }
                resp = await client.get(url, headers=headers)
                resp.raise_for_status()
                html_content = resp.text
            
            soup = BeautifulSoup(html_content, "html.parser")
            page_title = soup.title.string if soup.title else ""
            
            # Remove scripts, styles, navigations, footers
            for script in soup(["script", "style", "nav", "footer", "header", "noscript"]):
                script.decompose()
            text_content = soup.get_text(separator=" ", strip=True)
            return f"Titre de l'offre : {page_title}\n\nContenu de l'offre :\n{text_content[:15000]}"
        except Exception as e:
            logger.error(f"Error scraping job url {url}: {e}")
            return ""

    async def _audit_and_rewrite_cv(self, cv_text: str, job_text: str = None, job_url: str = None) -> Dict[str, Any]:
        """Audite et réécrit le CV en 3 passes internes pour garantir un score ATS > 80, éventuellement adapté à une offre."""
        if job_url and not job_text:
            logger.info(f"[Mentor] Scraping de l'offre d'emploi depuis l'URL : {job_url}")
            job_text = await self._scrape_job_url(job_url)

        if job_text:
            logger.info(f"[Mentor] Adaptation du CV par rapport à l'offre d'emploi : {job_text[:100]}...")
            
        logger.info("[Mentor] Démarrage de l'Optimisation Multi-Passes (Triple Check)...")
        
        current_cv_data = {}
        last_audit = {}
        original_ats_score = 0
        original_failles = []
        iterations = 3
        
        for i in range(1, iterations + 1):
            logger.info(f"[Mentor] Passe {i}/{iterations} en cours...")
            
            if i == 1:
                # PHASE 1: DIAGNOSTIC ONLY
                if job_text:
                    phase_instruction = "PHASE 1 : Diagnostic strict du CV original PAR RAPPORT À L'OFFRE D'EMPLOI FOURNIE. Tu DOIS évaluer le CV, lister ses failles réelles et identifier les écarts (mots-clés manquants, expériences non valorisées) par rapport aux exigences de l'offre d'emploi. Ne génère AUCUN `cv_data`."
                    context_data = f"[OFFRE_D_EMPLOI]\n{job_text}\n\n[INPUT_CV_ORIGINAL]\n{cv_text[:6000]}"
                else:
                    phase_instruction = "PHASE 1 : Diagnostic strict du CV original. Tu DOIS UNIQUEMENT évaluer le CV fourni et lister ses failles réelles. Ne génère AUCUN `cv_data`."
                    context_data = f"[INPUT_CV_ORIGINAL]\n{cv_text[:6000]}"
                json_structure = """{
  "audit": {
    "ats_score": 0,
    "candidate_name": "...",
    "candidate_title": "...",
    "scores": { "mots_cles": 0, "impact_resultats": 0, "mise_en_forme": 0, "lisibilite": 0, "experience_pertinence": 0 },
    "failles": ["Failles trouvées dans le CV original"],
    "mot_cles_manquants": ["Mots-clés importants absents"]
  }
}"""
            elif i == 2:
                # PHASE 2: FIRST DRAFT REWRITE
                if job_text:
                    phase_instruction = f"""PHASE 2 : Réécriture Hyperprofessionnelle Adaptée à l'Offre (Draft 1).
Objectif : Produire un CV parfaitement adapté à l'offre d'emploi fournie et digne d'un TOP recruteur FAANG — zéro faute, impact maximal. Met en valeur les expériences et les compétences pour correspondre aux exigences de l'offre d'emploi.
Basé sur les failles et écarts détectés : {original_failles}

OBLIGATIONS ABSOLUES :
[A] CHAQUE bullet point DOIT contenir UN KPI/métrique chiffré(e) obligatoire.
    Format imposé : Verbe d'action + Contexte technique + Résultat quantifié
    Exemples CORRECTS :
    - "Développé 12 microservices FastAPI réduisant la latence P99 de 340ms à 180ms (-47%)"
    - "Automatisé le pipeline CI/CD GitHub Actions → 0 downtime deploy, fréquence x3"
    - "Conçu un cache Redis multicouche atteignant 98% hit-rate, économie 40% coûts DB"
    Si tu ne connais PAS le chiffre exact, estime-le intelligemment à partir du contexte.
    UN BULLET SANS KPI = ÉCHEC.
[B] ZÉRO faute d'orthographe ou de grammaire — AUTO-VÉRIFIE chaque bullet avant de l'écrire.
    Checklist obligatoire pour chaque phrase :
    - Accord sujet/verbe correct ? (ex: "les APIs sont" pas "les APIs est")
    - Accents corrects ? (développé, créé, géré, intégré, déployé, amélioré)
    - Verbe à l'infinitif ou participe passé uniformément dans la section ?
    - Aucun anglicisme mal accordé ? ("performantes" pas "performants" si féminin)
    - Technologies capitalisées ? (Python, Docker, AWS, React, PostgreSQL)
[C] Injecte massivement les mots-clés techniques requis par l'offre d'emploi et ceux identifiés en Phase 1.
    Chaque poste doit nommer AU MOINS 3-4 technologies différentes dans ses bullets.
[D] Conserve TOUS les contacts, dates, lieux sans exception.
[E] ZÉRO RÉPETTION — Règle anti-rebrassage STRICTE :
    - Chaque bullet DOIT commencer par un verbe d'action DIFFÉRENT des autres bullets du même poste.
    - Banque de verbes imposée (varie obligatoirement) : Développé, Conçu, Architecturé, Optimisé,
      Déployé, Automatisé, Réduit, Augmenté, Piloté, Intégré, Refactorisé, Implémenté,
      Migré, Sécurisé, Coordonné, Livré, Encadré, Amélioré, Standardisé, Monitoré.
    - INTERDIT : répéter le même verbe dans le même poste.
    - INTERDIT : répéter les mêmes formulations génériques ("gérer", "assurer", "améliorer") 2x ou +.
[G] ADAPTATION DES EXPÉRIENCES : Oriente et reformule le contenu de chaque expérience professionnelle pour résonner directement avec le secteur d'activité, les problématiques et les missions décrits dans l'offre d'emploi. Si l'offre met l'accent sur un sujet particulier (ex: la scalabilité, la sécurité, l'UI/UX, le management d'équipe, ou une stack spécifique), oriente les réalisations passées pour montrer comment tu as déjà résolu des problèmes similaires. N'invente pas de fausses entreprises ou de fausses dates, mais valorise et adapte les angles d'attaque de tes expériences réelles pour coller aux besoins du poste.
[F] AUTO-RÉVISION OBLIGATOIRE avant de retourner le JSON :
    Parcours mentalement chaque bullet et vérifie :
    1. Verbes d'action tous différents dans un même poste ? Si non → remplace.
    2. Fautes d'accord ou d'accent ? Si oui → corrige.
    3. Bullets sans KPI ? Si oui → ajoute un chiffre.
    4. Les descriptions d'expériences sont-elles bien orientées et adaptées pour répondre aux besoins clés de l'offre d'emploi ? Si non → réoriente les angles.
    Seulement si ces tests sont OK → retourne le JSON."""
                    context_data = f"[OFFRE_D_EMPLOI]\n{job_text}\n\n[INPUT_CV_ORIGINAL]\n{cv_text[:6000]}"
                else:
                    phase_instruction = f"""PHASE 2 : Réécriture Hyperprofessionnelle (Draft 1).
Objectif : Produire un CV digne d'un TOP recruteur FAANG — zéro faute, impact maximal.
Basé sur les failles détectées : {original_failles}

OBLIGATIONS ABSOLUES :
[A] CHAQUE bullet point DOIT contenir UN KPI/métrique chiffré(e) obligatoire.
    Format imposé : Verbe d'action + Contexte technique + Résultat quantifié
    Exemples CORRECTS :
    - "Développé 12 microservices FastAPI réduisant la latence P99 de 340ms à 180ms (-47%)"
    - "Automatisé le pipeline CI/CD GitHub Actions → 0 downtime deploy, fréquence x3"
    - "Conçu un cache Redis multicouche atteignant 98% hit-rate, économie 40% coûts DB"
    Si tu ne connais PAS le chiffre exact, estime-le intelligemment à partir du contexte.
    UN BULLET SANS KPI = ÉCHEC.
[B] ZÉRO faute d'orthographe ou de grammaire — AUTO-VÉRIFIE chaque bullet avant de l'écrire.
    Checklist obligatoire pour chaque phrase :
    - Accord sujet/verbe correct ? (ex: "les APIs sont" pas "les APIs est")
    - Accents corrects ? (développé, créé, géré, intégré, déployé, amélioré)
    - Verbe à l'infinitif ou participe passé uniformément dans la section ?
    - Aucun anglicisme mal accordé ? ("performantes" pas "performants" si féminin)
    - Technologies capitalisées ? (Python, Docker, AWS, React, PostgreSQL)
[C] Injecte massivement les mots-clés techniques manquants identifiés en Phase 1.
    Chaque poste doit nommer AU MOINS 3-4 technologies différentes dans ses bullets.
[D] Conserve TOUS les contacts, dates, lieux sans exception.
[E] ZÉRO RÉPÉTITION — Règle anti-rebrassage STRICTE :
    - Chaque bullet DOIT commencer par un verbe d'action DIFFÉRENT des autres bullets du même poste.
    - Banque de verbes imposée (varie obligatoirement) : Développé, Conçu, Architecturé, Optimisé,
      Déployé, Automatisé, Réduit, Augmenté, Piloté, Intégré, Refactorisé, Implémenté,
      Migré, Sécurisé, Coordonné, Livré, Encadré, Amélioré, Standardisé, Monitoré.
    - INTERDIT : répéter le même verbe dans le même poste.
    - INTERDIT : répéter les mêmes formulations génériques ("gérer", "assurer", "améliorer") 2x ou +.
[F] AUTO-RÉVISION OBLIGATOIRE avant de retourner le JSON :
    Parcours mentalement chaque bullet et vérifie :
    1. Verbes d'action tous différents dans un même poste ? Si non → remplace.
    2. Fautes d'accord ou d'accent ? Si oui → corrige.
    3. Bullets sans KPI ? Si oui → ajoute un chiffre.
    Seulement si les 3 tests sont OK → retourne le JSON."""
                    context_data = f"[INPUT_CV_ORIGINAL]\n{cv_text[:6000]}"
                json_structure = """{
  "cv_data": {
    "full_name": "...", "title": "...", "email": "...", "phone": "...", "location": "...", "linkedin": "...", "github": "...",
    "summary": "Résumé percutant riche en mots-clés...",
    "experiences": [ { "title": "...", "company": "...", "location": "...", "start_date": "...", "end_date": "...", "bullets": ["Verbe d'action + contexte + Résultat/KPI"] } ],
    "projects": [ { "name": "...", "description": "...", "bullets": [] } ],
    "skills": { "Catégorie 1 (ex: Langages)": ["..."], "Catégorie 2 (ex: Outils)": ["..."], "Catégorie 3": ["..."] },
    "education": [], "languages": [], "certifications": []
  }
}"""
            else:
                # PHASE 3: FINAL SCORING AND MAPPING
                if job_text:
                    phase_instruction = f"""PHASE 3 : Vérification Finale & Scoring du CV OPTIMISÉ PAR RAPPORT À L'OFFRE.
Tu analyses le CV que tu viens de réécrire (Draft 1) par rapport à l'offre d'emploi fournie, PAS le CV original.
Ce CV a déjà été optimisé et adapté.

ÉVALUATION DU NOUVEAU CV PAR RAPPORT À L'OFFRE (attendu entre 80-99/100) :
- `mots_cles` : Tous les mots-clés techniques de l'offre d'emploi sont présents ? (attendu : 85-99)
- `impact_resultats` : Tous les bullets ont des KPIs chiffrés ? (attendu : 85-99)
- `mise_en_forme` : Structure ATS-friendly, sections claires ? (attendu : 85-99)
- `lisibilite` : Langage professionnel, zéro faute, cohérent ? (attendu : 85-99)
- `experience_pertinence` : Expériences bien décrites et pertinentes par rapport à l'offre ? (attendu : 85-99)

Génère le `correction_mapping` listant une faille/écart d'origine par clé et sa correction/adaptation appliquée dans le nouveau CV."""
                    context_data = f"[OFFRE_D_EMPLOI]\n{job_text}\n\n[CV_OPTIMISÉ_DRAFT1]\n{json.dumps(current_cv_data, ensure_ascii=False)[:5000]}"
                else:
                    phase_instruction = f"""PHASE 3 : Vérification Finale & Scoring du CV OPTIMISÉ.

Tu analyses le CV que tu viens de réécrire (Draft 1), PAS le CV original.
Ce CV a déjà été optimisé avec : mots-clés injectés, KPIs ajoutés, verbes d'action forts, mise en forme ATS.
Failles originales corrigées : {original_failles}

ÉVALUATION DU NOUVEAU CV (attendu entre 80-99/100) :
- `mots_cles` : Tous les mots-clés techniques sont présents ? (attendu : 85-99)
- `impact_resultats` : Tous les bullets ont des KPIs chiffrés ? (attendu : 85-99)
- `mise_en_forme` : Structure ATS-friendly, sections claires ? (attendu : 85-99)
- `lisibilite` : Langage professionnel, zéro faute, cohérent ? (attendu : 85-99)
- `experience_pertinence` : Expériences bien décrites et pertinentes ? (attendu : 85-99)

Génère le `correction_mapping` listant UNE faille par clé et sa correction appliquée dans le nouveau CV."""
                    context_data = f"[CV_OPTIMISÉ_DRAFT1]\n{json.dumps(current_cv_data, ensure_ascii=False)[:5000]}"
                json_structure = """{
  "audit": {
    "ats_score": 92,
    "scores": { "mots_cles": 90, "impact_resultats": 88, "mise_en_forme": 95, "lisibilite": 93, "experience_pertinence": 91 },
    "correction_mapping": { "[Faille 1 trouvée en Phase 1]": "[Comment elle est corrigée dans le nouveau CV]", "[Faille 2]": "[Correction 2]" },
    "tech_ajoutees": ["Technologies injectées dans le CV optimisé"]
  }
}"""

            if job_text:
                prompt = f"""Tu es l'Expert Recruteur Tech \"GoldArmy Mentor\" — mode Optimisation Triple Pass et Adaptation d'Offre.
{phase_instruction}

**RÈGLES D'OR ABSOLUES :**
1. **Score Honnête (Phase 1) :** Basé STRICTEMENT sur le CV fourni par rapport à l'offre (généralement 25-55/100). Jamais inventé.
2. **KPI OBLIGATOIRE sur chaque bullet :** Chaque réalisation DOIT montrer un impact chiffré.
   Formule : [Verbe fort] + [Technologie(s)] + [Résultat % / $ / x / ms / jours].
   Si absent dans l'original : estime intelligemment. AUCUN bullet sans métrique = rejeté.
3. **ATS Max :** Mots-clés techniques, frameworks, outils, certifications de l'offre d'emploi. Min. 3 techs par bullet.
4. **GRAMMAIRE & ORTHOGRAPHE — PRIORITÉ #1 — AUTO-VÉRIFICATION PHRASE PAR PHRASE :**
   ✓ Accents obligatoires : développé, intégré, réalisé, géré, déployé, amélioré, créé
   ✓ Accord correct : sujet/verbe, adjectifs (ex: "APIs performantes" pas "performants")
   ✓ Temps verbal uniforme dans chaque section (infinitif OU passé composé, pas les deux)
   ✓ Majuscules technos : Python, FastAPI, Docker, Kubernetes, AWS, GCP, React, TypeScript
   ✓ Zéro gallicisme mal formé, zéro anglicisme non accordé
   ✓ Avant de finaliser : relis mentalement chaque bullet comme si tu étais le correcteur
5. **Conservation totale :** Contacts, emails, téléphones, dates, lieux — rien ne disparaît.
6. **Structure :** Summary → Experiences → Projects → Skills → Education → Languages → Certs.

**JSON ATTENDU :**
{json_structure}

**CONTEXTE :**
{context_data}

Réponds UNIQUEMENT en JSON pur. Aucun texte avant ou après.
"""
            else:
                prompt = f"""Tu es l'Expert Recruteur Tech \"GoldArmy Mentor\" — mode Optimisation Triple Pass.
{phase_instruction}

**RÈGLES D'OR ABSOLUES :**
1. **Score Honnête (Phase 1) :** Basé STRICTEMENT sur le CV fourni (généralement 25-55/100). Jamais inventé.
2. **KPI OBLIGATOIRE sur chaque bullet :** Chaque réalisation DOIT montrer un impact chiffré.
   Formule : [Verbe fort] + [Technologie(s)] + [Résultat % / $ / x / ms / jours].
   Si absent dans l'original : estime intelligemment. AUCUN bullet sans métrique = rejeté.
3. **ATS Max :** Mots-clés techniques, frameworks, outils, certifications. Min. 3 techs par bullet.
4. **GRAMMAIRE & ORTHOGRAPHE — PRIORITÉ #1 — AUTO-VÉRIFICATION PHRASE PAR PHRASE :**
   ✓ Accents obligatoires : développé, intégré, réalisé, géré, déployé, amélioré, créé
   ✓ Accord correct : sujet/verbe, adjectifs (ex: "APIs performantes" pas "performants")
   ✓ Temps verbal uniforme dans chaque section (infinitif OU passé composé, pas les deux)
   ✓ Majuscules technos : Python, FastAPI, Docker, Kubernetes, AWS, GCP, React, TypeScript
   ✓ Zéro gallicisme mal formé, zéro anglicisme non accordé
   ✓ Avant de finaliser : relis mentalement chaque bullet comme si tu étais le correcteur
5. **Conservation totale :** Contacts, emails, téléphones, dates, lieux — rien ne disparaît.
6. **Structure :** Summary → Experiences → Projects → Skills → Education → Languages → Certs.

**JSON ATTENDU :**
{json_structure}

**CONTEXTE :**
{context_data}
Réponds UNIQUEMENT en JSON pur. Aucun texte avant ou après.
"""
            response = await self.generate_response(prompt, max_tokens=8192, json_mode=True)
            
            try:
                # Extraction & Parsing
                start_index = response.find('{')
                end_index = response.rfind('}')
                if start_index != -1 and end_index != -1:
                    cleaned = response[start_index:end_index+1]
                else:
                    cleaned = response

                parsed = json.loads(cleaned)
                
                if i == 1:
                    phase1_audit = parsed.get("audit", {})
                    last_audit = phase1_audit.copy()
                    original_ats_score = phase1_audit.get("ats_score", 0)
                    original_failles = phase1_audit.get("failles", [])
                elif i == 2:
                    current_cv_data = parsed.get("cv_data", {})
                else:
                    # Phase 3: scores du CV OPTIMISÉ — on remplace les scores Phase 1 avec ceux du CV optimisé
                    phase3_audit = parsed.get("audit", {})
                    # Conserver les failles originales et le nom du candidat de Phase 1
                    phase3_audit["original_failles"] = original_failles
                    phase3_audit["candidate_name"] = last_audit.get("candidate_name", "")
                    phase3_audit["candidate_title"] = last_audit.get("candidate_title", "")
                    phase3_audit["mot_cles_manquants"] = last_audit.get("mot_cles_manquants", [])
                    last_audit = phase3_audit
                
                logger.debug(f"[Mentor] Passe {i} terminée. Score ATS reporté: {parsed.get('audit', {}).get('ats_score')}")
                
            except Exception as e:
                logger.error(f"[Mentor] Erreur parsing passe {i}: {e}")
                if i == 1:
                    return {"status": "error", "type": "chat", "content": "Désolé, l'optimisation a échoué au premier cycle."}
                elif i == 3:
                    # Passe 3 optionnelle — on continue avec le draft de la passe 2
                    logger.warning("[Mentor] Passe 3 échouée (rate-limit probable) — on utilise le draft de la passe 2.")
                    break

            # Pause minimale entre les passes car nous utilisons un modèle rapide et stable (Gemini 2.5 Flash)
            if i < iterations:
                await asyncio.sleep(1)

        # Finalisation
        last_audit["original_ats_score"] = original_ats_score
        last_audit["original_failles"] = original_failles
        cv_json = json.dumps(current_cv_data, ensure_ascii=False)
        logger.success(f"[Mentor] Optimisation terminée. Score final: {last_audit.get('ats_score')} (Initial: {original_ats_score})")
        
        return {
            "status": "success",
            "type": "cv_audit_rewrite",
            "audit": last_audit,
            "content": cv_json,
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
- Langage professionnel, concis, ZERO FAUTE (corrige impérativement toute faute de grammaire/orthographe du CV original)
- Format de contact standardisé pour une extraction ATS (ex: email explicite, téléphone au format international si possible)

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
            "    5. Le Smooth scroll via element.scrollIntoView({behavior: 'smooth'}) sans modifier la structure du document.\n"
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

    async def _generate_social_sniper_kit(self, cv_text: str, company: str, job: str) -> Dict[str, Any]:
        """Génère un kit d'approche complet (Social Sniper)."""
        logger.info(f"[Mentor] Génération Social Sniper Kit pour {company}...")
        
        prompt = f"""Tu es un expert en Networking Stratégique. Génère un kit d'approche pour ce poste.
ENTREPRISE: {company}
POSTE: {job}
MON CV: {cv_text[:3000]}

Génère 4 éléments percutants au format JSON:
1. "linkedin_hook": Une demande de connexion LinkedIn de moins de 300 caractères.
2. "expert_comment": Un commentaire intelligent à poster sous une publication de l'entreprise.
3. "follow_up": Un message de relance si la personne accepte mais ne répond pas.
4. "power_argument": Un argument massue basé sur une réussite de mon CV pour prouver ma valeur.

Réponds UNIQUEMENT en JSON."""

        try:
            from llm.unified_client import UnifiedLLMClient
            llm = UnifiedLLMClient()
            response = await llm.generate(prompt, json_mode=True)
            
            # Nettoyage
            match = re.search(r'\{.*\}', response, re.DOTALL)
            clean = match.group(0) if match else response
            data = json.loads(clean)
            
            return {
                "status": "success",
                "type": "social_sniper_kit",
                "data": data
            }
        except Exception as e:
            logger.error(f"[Mentor] Erreur Social Sniper: {e}")
            return {"status": "error", "content": "Échec de génération du kit."}

    async def _generate_post_interview_kit(self, cv_text: str, company: str, job: str, debrief: Dict[str, Any]) -> Dict[str, Any]:
        """Génère un email de remerciement stratégique et une analyse de debrief."""
        logger.info(f"[Mentor] Analyse Post-Interview pour {company}...")
        
        feel = debrief.get("feel", "Neutre")
        hard_question = debrief.get("hard_question", "N/A")
        key_need = debrief.get("key_need", "N/A")

        prompt = f"""Tu es un Coach en Recrutement Senior. Analyse l'entretien qui vient d'avoir lieu.
ENTREPRISE: {company}
POSTE: {job}
MON CV: {cv_text[:2500]}

DEBRIEF DU CANDIDAT:
- Ressenti: {feel}
- Question difficile: {hard_question}
- Besoin clé identifié: {key_need}

Génère un JSON avec:
1. "thank_you_email": Un email de remerciement stratégique (pas bateau) qui réaffirme la valeur du candidat par rapport au besoin clé identifié.
2. "analysis": Une analyse courte des chances de succès et des points à améliorer pour la suite.
3. "follow_up_plan": Un conseil sur quand relancer si pas de réponse.

Réponds UNIQUEMENT en JSON."""

        try:
            from llm.unified_client import UnifiedLLMClient
            llm = UnifiedLLMClient()
            response = await llm.generate(prompt, json_mode=True)
            
            match = re.search(r'\{.*\}', response, re.DOTALL)
            clean = match.group(0) if match else response
            data = json.loads(clean)
            
            return {
                "status": "success",
                "type": "post_interview_kit",
                "data": data
            }
        except Exception as e:
            logger.error(f"[Mentor] Erreur Post-Interview: {e}")
            return {"status": "error", "content": "Échec de l'analyse post-entretien."}

    async def _generate_gold_profile_audit(self, cv_text: str, linkedin_text: str = "") -> Dict[str, Any]:
        """Génère un audit d'optimisation complet du profil LinkedIn (basé sur CV et/ou profil réel)."""
        source_context = ""
        if cv_text:
            source_context += f"--- CONTENU CV ---\n{cv_text[:3000]}\n"
        if linkedin_text:
            source_context += f"\n--- PROFIL LINKEDIN ACTUEL ---\n{linkedin_text[:3000]}\n"

        if not source_context:
            source_context = "Aucun CV ni profil fourni."

        prompt = f"""Tu es le N°1 mondial en Personal Branding & Stratégie LinkedIn.
Analyse le profil / CV ci-dessous et génère un kit d'optimisation pour maximiser la visibilité auprès des recruteurs et clients.

{source_context}

Génère un JSON respectant scrupuleusement la structure :
{{
  "profile_score": 85,
  "headline": "Titre LinkedIn percutant (< 220 chars) incluant la proposition de valeur et mots-clés SEO",
  "about": "Section 'À propos' captivante en storytelling (Accroche, Mission, Impact, Compétences clés, CTA)",
  "field_optimizations": [
     {{"field": "Titre Profil", "current": "Titre actuel", "suggestion": "Nouveau titre optimisé SEO"}},
     {{"field": "Section À Propos", "current": "Texte actuel", "suggestion": "Storytelling avec structure en sauts de ligne"}},
     {{"field": "Compétences", "suggestion": "Top 5 compétences algorithmiques indispensables"}}
  ],
  "top_skills": ["Skill 1", "Skill 2", "Skill 3", "Skill 4", "Skill 5"]
}}

Réponds UNIQUEMENT en JSON valide."""
        return await self._call_llm_json(prompt, "gold_profile_audit")

    async def _generate_gold_profile_plan(self, cv_text: str, linkedin_text: str = "", start_day: int = 1, days_count: int = 15) -> Dict[str, Any]:
        """Génère un plan de contenu structuré en funnel TOFU / MOFU / BOFU avec formats adaptés."""
        source_context = ""
        if cv_text:
            source_context += f"--- CONTENU CV ---\n{cv_text[:1500]}\n"
        if linkedin_text:
            source_context += f"\n--- PROFIL LINKEDIN ---\n{linkedin_text[:1500]}\n"

        end_day = start_day + days_count - 1
        prompt = f"""Tu es un stratège de contenu LinkedIn d'élite.
Génère la suite de la matrice éditoriale du Jour {start_day} au Jour {end_day} ({days_count} jours de publications stratégiques) basée sur ce profil.

{source_context}

Consignes :
1. Structurer du Jour {start_day} au Jour {end_day} (Funnel: TOFU, MOFU, BOFU).
2. Formats : "Text", "Carousel PDF", "Poll", "Story".
3. Rédiger des angles ultra-courts (1 phrase max, < 15 mots).

Génère un JSON strict et valide :
{{
  "plan": [
    {{
      "day": {start_day},
      "topic": "Titre court",
      "angle": "Angle en 1 phrase",
      "funnel_stage": "TOFU",
      "format": "Carousel PDF"
    }}
  ]
}}

Réponds UNIQUEMENT en JSON valide."""
        return await self._call_llm_json(prompt, "gold_profile_plan")

    async def _generate_gold_profile_post(self, cv_text: str, topic: str, format_type: str = "Text", linkedin_text: str = "") -> Dict[str, Any]:
        """Génère un post LinkedIn hautement viral avec score de viralité et carrousel si nécessaire."""
        source_context = ""
        if cv_text:
            source_context += f"--- PROFIL / CV ---\n{cv_text[:1500]}\n"
        if linkedin_text:
            source_context += f"\n{linkedin_text[:1500]}\n"

        prompt = f"""Tu es le rédacteur de posts LinkedIn le plus viral au monde.
Rédige une publication LinkedIn haute performance sur le sujet : "{topic}" (Format préconisé : {format_type}).

{source_context}

Consignes de Viralité & Copywriting :
1. Accroche (Hook) : Doit forcer l'utilisateur à cliquer sur "Voir plus" dans la ligne 1 ou 2.
2. Corps du texte : Phrases courtes, aérées, sauts de lignes fréquents pour lecture mobile.
3. CTA Comment Bait : Inciter à commenter.
4. Score de viralité : De 1 à 100 avec 2 conseils d'optimisation.
5. Si le format est "Carousel PDF", inclure 4 diapositives simples.

Génère un JSON strict :
{{
  "post_content": "Texte du post...",
  "hook": "Accroche 2 lignes",
  "cta_comment_bait": "Appel à l'action",
  "hashtags": ["#Hashtag1", "#Hashtag2"],
  "viral_score": 92,
  "viral_tips": ["Conseil 1", "Conseil 2"],
  "carousel_slides": [
    {{"slide_number": 1, "title": "Titre Slide 1", "content": "Contenu court"}},
    {{"slide_number": 2, "title": "Titre Slide 2", "content": "Contenu court"}}
  ]
}}

Réponds UNIQUEMENT en JSON valide."""
        return await self._call_llm_json(prompt, "gold_profile_post")

    async def _call_llm_json(self, prompt: str, action_name: str) -> Dict[str, Any]:
        try:
            from llm.unified_client import UnifiedLLMClient
            llm = UnifiedLLMClient()
            response = await llm.generate(prompt, json_mode=True)
            
            # Nettoyer les marqueurs markdown ```json ... ```
            clean_raw = re.sub(r'```json\s*', '', response)
            clean_raw = re.sub(r'```\s*', '', clean_raw)

            match = re.search(r'\{.*\}', clean_raw, re.DOTALL)
            clean = match.group(0) if match else clean_raw

            # Enlever les virgules superflues avant ] ou }
            clean = re.sub(r',\s*([\]}])', r'\1', clean)
            
            data = None
            # Essai 1: Standard json.loads avec strict=False
            try:
                data = json.loads(clean, strict=False)
            except Exception:
                pass
                
            # Essai 2: Échappement des sauts de ligne réels dans les chaînes
            if data is None:
                try:
                    clean_fixed = re.sub(r'(?<!\\)\n', r'\\n', clean)
                    data = json.loads(clean_fixed, strict=False)
                except Exception:
                    pass

            # Essai 3: Réparation si le JSON a été tronqué en fin de réponse LLM
            if data is None:
                try:
                    truncated_fix = clean.strip()
                    last_obj_idx = truncated_fix.rfind('{')
                    if last_obj_idx > 0:
                        truncated_fix = truncated_fix[:last_obj_idx].rstrip(', \n\t')
                        if not truncated_fix.endswith(']'):
                            truncated_fix += ']'
                        if not truncated_fix.endswith('}'):
                            truncated_fix += '}'
                        data = json.loads(truncated_fix, strict=False)
                except Exception:
                    pass

            # Essai 4: Parsing via ast.literal_eval si le LLM a renvoyé de la syntaxe Python dict
            if data is None:
                try:
                    import ast
                    data = ast.literal_eval(clean)
                except Exception:
                    pass

            if data is not None and isinstance(data, dict):
                return {"status": "success", "type": action_name, "data": data}

            logger.error(f"[Mentor] Échec parsing JSON pour {action_name}. Extrait brut: {response[:300]}")
            return {"status": "error", "content": f"Échec de l'action {action_name} (Format JSON invalide)."}
        except Exception as e:
            logger.error(f"[Mentor] Erreur {action_name}: {e}")
            return {"status": "error", "content": f"Échec de l'action {action_name}."}






