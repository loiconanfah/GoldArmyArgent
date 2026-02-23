"""Agent de recherche d'emploi grandement simplifié.
Renvoie les données brutes des APIs de recherche sans aucun filtrage IA strict.
"""
from typing import Any, Dict, List
import asyncio
from loguru import logger

from core.agent_base import BaseAgent
from config.settings import settings


class JobSearchAgent(BaseAgent):
    """Agent proxy pour les APIs de recherche d'emploi. Sans filtre."""
    
    def __init__(self, **kwargs):
        """Initialise l'agent simplifié."""
        kwargs.setdefault("agent_type", "job_searcher")
        kwargs.setdefault("name", "JobSearcher")
        kwargs.setdefault("temperature", 0.1) # Bas pour extractions basiques
        kwargs.setdefault("max_tokens", 1024)
        super().__init__(**kwargs)
    
    async def think(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extrait les mots-clés de base à partir de la requête.
        """
        logger.info(f"🚀 JobSearchAgent Simplifié - Think: {task.get('message', '')}")
        
        query = task.get("query", "") or task.get("message", "")
        cv_text = task.get("cv_text", "")
        limit = int(task.get("nb_results") or 10)
        
        # Extraction du profil CV si présent
        cv_profile = {"skills": [], "target_roles": [], "experience_years": 0}
        if cv_text:
            logger.info("📄 Analyse du CV avec le modèle IA...")
            cv_profile = await self._analyze_cv(cv_text)
            logger.info(f"CV Profil: {cv_profile.get('target_roles')} - {cv_profile.get('experience_years')} ans exp")
        else:
            cv_profile["target_roles"] = [query]
            cv_profile["skills"] = [query]
        
        # Extraction TRES BASIQUE via LLM des mots clés et location
        prompt = f"""
        Extrait le titre du poste (keywords) et la ville (location) de cette requête: "{query}"
        Réponds UNIQUEMENT en JSON avec les clés 'keywords' et 'location'.
        Si tu ne trouves pas de ville, mets "Québec".
        """
        
        criteria = {"keywords": query, "location": "Québec"} # Valeurs par défaut robustes
        
        try:
            resp = await self.generate_response(prompt)
            # Nettoyage et tentative de parse
            import json, re
            match = re.search(r'\{.*\}', resp.replace('\n', ''), re.S)
            if match:
                parsed = json.loads(match.group(0))
                if "keywords" in parsed and parsed["keywords"]:
                    criteria["keywords"] = parsed["keywords"]
                if "location" in parsed and parsed["location"]:
                    criteria["location"] = parsed["location"]
                    
            # Priorité de la recherche au CV si "query" est générique
            if cv_profile.get("target_roles") and not query:
                 criteria["keywords"] = cv_profile["target_roles"][0]
        except Exception as e:
            logger.warning(f"Fallback LLM extraction failed: {e}. Using raw query.")
            
        action_plan = {
            "task_id": task.get("id", "unknown"),
            "criteria": criteria,
            "cv_profile": cv_profile,
            "limit": limit,
            "original_query": query
        }
        
        logger.info(f"✅ Plan de recherche: {action_plan['criteria']}")
        return action_plan
    
    async def act(self, action_plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Exécute la recherche sur TOUTES les APIs et renvoie tout sans filtrer.
        """
        criteria = action_plan.get("criteria", {})
        keywords = str(criteria.get("keywords", "informatique"))
        location = str(criteria.get("location", "Québec"))
        limit = action_plan.get("limit", 10)
        
        logger.info(f"🔍 ACT: Recherche brute pour '{keywords}' à '{location}' (Limit: {limit})")
        
        all_jobs = []
        
        # 1. Jooble
        if settings.jooble_api_key:
            try:
                from tools.jooble_searcher import JoobleSearcher
                jooble = JoobleSearcher(api_key=settings.jooble_api_key)
                j_jobs = await jooble.search_jobs(keywords=keywords, location=location, limit=limit)
                if j_jobs:
                    logger.info(f"🟢 Jooble a trouvé {len(j_jobs)} offres.")
                    all_jobs.extend(j_jobs)
            except Exception as e:
                logger.error(f"🔴 Erreur Jooble: {e}")

        # 2. JSearch (RapidAPI)
        if settings.rapidapi_key:
            try:
                from tools.jsearch_searcher import JSearchSearcher
                jsearch = JSearchSearcher(api_key=settings.rapidapi_key)
                search_query = f"{keywords} in {location}"
                pages = max(1, (limit // 10) + (1 if limit % 10 > 0 else 0))
                r_jobs = await jsearch.search_jobs(query=search_query, num_pages=pages)
                if r_jobs:
                    logger.info(f"🟢 JSearch a trouvé {len(r_jobs)} offres.")
                    all_jobs.extend(r_jobs)
            except Exception as e:
                logger.error(f"🔴 Erreur JSearch: {e}")

        # 3. Web Searcher (JobBank fallback)
        try:
            from tools.web_searcher import web_searcher
            w_jobs = await web_searcher.search_jobs(keywords=keywords, location=location, max_results=limit)
            if w_jobs:
                logger.info(f"🟢 Web/JobBank a trouvé {len(w_jobs)} offres.")
                all_jobs.extend(w_jobs)
        except Exception as e:
            logger.error(f"🔴 Erreur WebSearcher: {e}")

        # Nettoyage basique (anti-doublons par ID ou URL)
        unique_jobs = []
        seen_urls = set()
        for idx, job in enumerate(all_jobs):
            url = job.get("url", f"temp-{idx}")
            if url not in seen_urls:
                seen_urls.add(url)
                
                # S'assurer que les champs requis pour le front sont là
                safe_job = {
                    "id": job.get("id", f"job-{idx}"),
                    "title": job.get("title", "Poste sans titre"),
                    "company": job.get("company", "Entreprise anonyme"),
                    "location": job.get("location", location),
                    "description": job.get("description", job.get("snippet", "Aucune description.")),
                    "url": job.get("url", "#"),
                    "source": job.get("source", "Web"),
                    "posted_date": job.get("posted_date", ""),
                    "salary": job.get("salary", ""),
                    "job_type": job.get("job_type", "Temps plein"),
                    "required_skills": job.get("required_skills", [keywords]),
                    "match_score": 85, # Score arbitraire élevé pour le front
                    "match_justification": "Trouvé via moteur de recherche externe."
                }
                unique_jobs.append(safe_job)
                
        # --- BATCH AI EVALUATION ---
        cv_profile = action_plan.get("cv_profile", {})
        if unique_jobs:
            logger.info("🧠 Évaluation de la pertinence des offres en bloc...")
            final_jobs = await self._evaluate_jobs_batch(unique_jobs, cv_profile)
        else:
            final_jobs = []
            
        # Limiter au nombre demandé
        final_jobs = final_jobs[:limit]
        logger.info(f"📨 Renvoi de {len(final_jobs)} offres pertinentes au Frontend.")
        
        return {
            "success": True,
            "total_jobs_found": len(final_jobs),
            "matched_jobs": final_jobs,
            "cv_profile": cv_profile,
            "search_criteria": {
                "keywords": [keywords],
                "location": location,
                "domain": "IT"
            }
        }

    async def _analyze_cv(self, cv_text: str) -> Dict[str, Any]:
        """Analyse le CV pour en extraire les informations clés."""
        prompt = f"""
        Analyse ce CV et extrais les informations clés.
        Règles IMPÉRATIVES:
        1. Tu dois chercher quel type de poste le candidat vise ("Développeur Web", "Conseiller aux ventes", etc).
        2. Extrait les années d'expérience (nombre).
        3. Extrait les compétences techniques.
        Réponds UNIQUEMENT avec un JSON pur. Aucune autre phrase.
        {{
            "target_roles": ["Titre Poste 1", "Titre Poste 2"],
            "experience_years": 2,
            "skills": ["Python", "Vente", ...]
        }}
        
        CV:
        {cv_text[:3000]}
        """
        
        try:
            resp = await self.generate_response(prompt)
            import json, re
            match = re.search(r'\{.*\}', resp.replace('\n', ''), re.S)
            if match:
                return json.loads(match.group(0))
        except Exception as e:
            logger.error(f"Erreur d'analyse CV: {e}")
            
        return {"target_roles": [], "skills": [], "experience_years": 0}

    async def _evaluate_jobs_batch(self, jobs: List[Dict], cv_profile: Dict) -> List[Dict]:
        """Évalue la compatibilité d'un lot d'offres d'emploi en une seule requête."""
        if not cv_profile.get("target_roles") and not cv_profile.get("skills"):
            return jobs # Pas de profil pertinent, on passe
            
        prompt = f"""
        Tu es un recruteur expert. Évalue la compatibilité des offres suivantes par rapport au profil du candidat.
        
        PROFIL CANDIDAT:
        Rôles cibles: {cv_profile.get('target_roles', [])}
        Expérience: {cv_profile.get('experience_years', 0)} ans
        Compétences: {cv_profile.get('skills', [])}
        
        OFFRES D'EMPLOIS (À évaluer):
        """
        
        for job in jobs[:50]: # On envoie max 50 offres pour pas surcharger
            prompt += f"\n- ID: '{job.get('id')}' | Poste: '{job.get('title')}' | Snippet: {job.get('description', '')[:100]}"
            
        prompt += """\n
        INSTRUCTIONS:
        Pour chaque offre, retourne un tableau JSON de ce format exact, sans formatage markdown '```json':
        [
            {"id": "id_de_loffre", "score": 85, "justification": "Max 10 mots sur pourquoi ça fit ou pas"}
        ]
        Le score doit être 0 si c'est Senior et le candidat est Junior, ou si les compétences n'ont RIEN à voir.
        """
        
        try:
            resp = await self.generate_response(prompt)
            import json, re
            
            clean_resp = resp.replace("```json", "").replace("```", "").strip()
            
            # Tenter de parser directement
            evaluations = None
            try:
                parsed = json.loads(clean_resp)
                if isinstance(parsed, list):
                    evaluations = parsed
                elif isinstance(parsed, dict):
                    # Essayer de trouver une clé qui contient une liste
                    for v in parsed.values():
                        if isinstance(v, list):
                            evaluations = v
                            break
            except json.JSONDecodeError:
                # Fallback Regex
                match = re.search(r'\[.*\]', clean_resp, re.DOTALL)
                if match:
                    evaluations = json.loads(match.group(0))
                    
            if evaluations:
                eval_map = {str(e.get("id")): e for e in evaluations if "id" in e}
                
                for job in jobs:
                    if str(job.get("id")) in eval_map:
                        e = eval_map[str(job.get("id"))]
                        job["match_score"] = int(e.get("score", 85))
                        job["match_justification"] = e.get("justification", "Évaluation IA générique")
                
                return sorted([j for j in jobs if j.get("match_score", 85) > 20], key=lambda x: x.get("match_score", 85), reverse=True)
                
        except Exception as e:
            logger.error(f"Évaluation Batch Echouée, Fallback sur score basique: {e}")
            
        return jobs
