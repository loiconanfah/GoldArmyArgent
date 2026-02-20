"""Agent de recherche d'emploi spécialisé."""
from typing import Any, Dict, List
import re
import os
from urllib.parse import urlparse

from loguru import logger

from core.agent_base import BaseAgent
from llm.prompt_templates import PromptTemplates
from config.settings import settings


class JobSearchAgent(BaseAgent):
    """Agent spécialisé dans la recherche d'emploi et le matching CV/offres."""
    
    def __init__(self, **kwargs):
        """Initialise l'agent job searcher."""
        kwargs.setdefault("agent_type", "job_searcher")
        kwargs.setdefault("name", "JobSearcher")
        kwargs.setdefault("temperature", 0.2)  # Encore plus précis pour le matching strict
        kwargs.setdefault("max_tokens", 3072)
        super().__init__(**kwargs)
    
    async def think(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyse la tâche de recherche d'emploi et planifie l'approche.
        
        Args:
            task: Tâche de recherche avec CV et critères
        
        Returns:
            Plan de recherche
        """
        logger.info(f"Checking job search request for: {self.name}...")
        
        # Extraire les informations
        cv_text = task.get("cv_text", "")
        filters = task.get("filters", {})
        
        # Si les filtres sont vides, essayer d'extraire depuis la description
        if not filters and task.get("description"):
            logger.info("Extracting criteria from description...")
            filters = await self._extract_criteria_from_text(task.get("description"))
            
        # Analyser le CV avec le LLM
        cv_analysis = await self._analyze_cv(cv_text) if cv_text else {}
        
        # Créer le plan de recherche
        search_prompt = self._build_search_prompt(cv_analysis, filters)
        logger.info("Developing search strategy (this may take time)...")
        search_strategy = await self.generate_response(search_prompt)
        
        action_plan = {
            "task_id": task.get("id", "unknown"),
            "cv_profile": cv_analysis,
            "filters": filters,
            "search_strategy": search_strategy,
            "keywords": self._extract_keywords(cv_analysis, filters),
        }
        
        logger.debug(f"Search plan created with {len(action_plan['keywords'])} keywords")
        return action_plan
    
    async def act(self, action_plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Exécute la recherche d'emploi et le matching.
        
        Args:
            action_plan: Plan de recherche
        
        Returns:
            Offres triées par pertinence
        """
        logger.info(f"Searching for jobs with: {self.name}...")
        
        # Essayer la recherche web réelle
        jobs = await self._search_jobs_online(action_plan)

        # Filtrer strictement les vraies offres (exclure liens de recherche + URLs factices)
        def _is_valid_job_url(u: str) -> bool:
            if not u or not isinstance(u, str):
                return False
            u = u.strip()
            if not (u.startswith("http://") or u.startswith("https://")):
                return False
            if "example.com" in u.lower():
                return False
            try:
                parsed = urlparse(u)
                return bool(parsed.netloc)
            except Exception:
                return False

        real_jobs = []
        for job in jobs:
            if job.get("source") == "Search Link":
                continue
            if not _is_valid_job_url(job.get("url", "")):
                continue
            real_jobs.append(job)

        if not real_jobs:
            logger.warning("No real jobs found (blocked sources or no data).")
            return {
                "success": False,
                "error": "Aucune offre réelle trouvée. Les sources peuvent bloquer le scraping (Google/Indeed/LinkedIn) ou la requête est trop restrictive. Essaie avec d'autres mots-clés/localisation.",
                "total_jobs_found": 0,
                "matched_jobs": [],
                "cv_profile": action_plan.get("cv_profile", {}),
                "search_criteria": action_plan.get("filters", {}),
            }

        jobs = real_jobs
        logger.info(f"Found {len(real_jobs)} real jobs (URLs validated)")
        
        # Get requested limit or default to 10
        requested_limit = action_plan["filters"].get("limit", 10)
        
        # Pré-matching pour identifier les offres à enrichir
        logger.info(f"Pre-analyzing {len(jobs)} jobs...")
        pre_matched = []
        for job in jobs:
            score = self._calculate_match_score(job, action_plan["cv_profile"])
            job["match_score"] = score
            pre_matched.append(job)
            
        pre_matched.sort(key=lambda x: x["match_score"], reverse=True)
        # Enrichir un peu plus que la limite pour avoir de la marge après filtrage profond
        candidates = pre_matched[:requested_limit + 5]
        
        # Enrichissement des détails (Scraping profond) pour les meilleures offres
        # Uniquement si ce sont des vraies offres (pas mock ou fallback links)
        logger.info(f"Enriching details for {len(candidates)} jobs (Parallel)...")
        from tools.web_searcher import web_searcher
        import asyncio
        
        enrichment_tasks = []
        for job in candidates:
            # Vérifier que ce n'est pas un lien de recherche général
            if not job.get("source") == "Search Link":
                enrichment_tasks.append(web_searcher.enrich_job_details(job))
            else:
                logger.warning(f"Skipping search link: {job.get('title')}")
                enrichment_tasks.append(asyncio.sleep(0, result=job))
        
        enriched_results = await asyncio.gather(*enrichment_tasks, return_exceptions=True)
        
        enriched_jobs = []
        for res in enriched_results:
            if isinstance(res, dict):
                enriched_jobs.append(res)
            elif isinstance(res, Exception):
                logger.warning(f"Enrichment error: {res}")
            else:
                enriched_jobs.append(res) # Should be the job dict from sleep
            
        # Matching final approfondi
        logger.info(f"Final matching of {len(enriched_jobs)} jobs with profile...")
        matched_jobs = await self._match_jobs(enriched_jobs, action_plan["cv_profile"])
        
        # Trier par score et couper à la limite demandée
        matched_jobs.sort(key=lambda x: x["match_score"], reverse=True)
        final_jobs = matched_jobs[:requested_limit]
        
        results = {
            "success": True,
            "total_jobs_found": len(jobs),
            "matched_jobs": final_jobs,
            "cv_profile": action_plan["cv_profile"],
            "search_criteria": action_plan["filters"],
        }
        
        logger.success(f"Search completed: {len(final_jobs)} jobs matched")
        return results
    
    async def _search_jobs_online(self, action_plan: Dict) -> List[Dict]:
        """Recherche des offres sur internet et enrichit avec le contenu réel."""
        try:
            # Liste pour accumuler tous les résultats
            all_jobs = []
            requested_limit = action_plan["filters"].get("limit", 10)
            
            # 0) Jooble REST API (priorité car fiable et structuré)
            if settings.jooble_api_key:
                try:
                    from tools.jooble_searcher import JoobleSearcher
                    
                    filters = action_plan["filters"]
                    keywords = " ".join(action_plan.get("keywords", ["informatique"]))
                    
                    # Force "Stage" keyword if requested
                    if filters.get("job_type", "").lower() == "stage":
                         if "stage" not in keywords.lower():
                             keywords = f"Stage {keywords}"
                    
                    location = filters.get("location", "Québec")
                    
                    # Initialiser le client avec la clé configurée
                    jooble = JoobleSearcher(api_key=settings.jooble_api_key)
                    
                    logger.info(f"Jooble API configured. Search: {keywords} @ {location}")
                    jooble_jobs = await jooble.search_jobs(
                        keywords=keywords,
                        location=location,
                        limit=requested_limit # Dynamique
                    )
                    
                    if jooble_jobs:
                        logger.info(f"Jooble: {len(jooble_jobs)} jobs retrieved")
                        all_jobs.extend(jooble_jobs)
                    else:
                        logger.warning("Jooble: 0 results.")
                        
                except ImportError:
                    logger.error("Cannot import JoobleSearcher")
                except Exception as e:
                    logger.warning(f"Jooble Error: {e}")

            # 0.5) JSearch API (RapidAPI)
            if settings.rapidapi_key:
                try:
                    from tools.jsearch_searcher import JSearchSearcher
                    
                    # Utiliser les Target Roles du CV pour la query si dispos, sinon keywords
                    cv_roles = action_plan.get("cv_profile", {}).get("target_roles", [])
                    
                    # Base Query Construction
                    if cv_roles:
                        base_query = cv_roles[0] # Prendre le premier rôle cible
                    else:
                        base_query = " ".join(action_plan.get("keywords", ["informatique"]))
                    
                    # Force "Stage" keyword for JSearch
                    if action_plan["filters"].get("job_type", "").lower() == "stage":
                        query = f"Stage {base_query}"
                        # JSearch works better with "Intern" sometimes depending on region, but "Stage" for Quebec is good.
                        if "intern" not in query.lower() and "stage" not in query.lower():
                             query = f"Stage {base_query}"
                    else:
                        query = base_query
                        
                    location = action_plan["filters"].get("location", "Québec")
                    
                    jsearch = JSearchSearcher(api_key=settings.rapidapi_key)
                    logger.info(f"JSearch API activated. Query: {query} @ {location}")
                    
                    # Logique de pagination JSearch (10 résultats par page par défaut)
                    # Si on veut 20 résultats, on demande 2 pages.
                    estimated_pages = max(1, -(-requested_limit // 10)) # Ceiling division
                    
                    jsearch_jobs = await jsearch.search_jobs(
                        query=query,
                        location=location,
                        num_pages=estimated_pages
                    )
                    
                    if jsearch_jobs:
                         logger.info(f"JSearch: {len(jsearch_jobs)} jobs retrieved")
                         all_jobs.extend(jsearch_jobs)
                    else:
                        logger.warning("JSearch: 0 results.")
                        
                except Exception as e:
                    logger.warning(f"JSearch Error: {e}")



            # 1) Recherche Web Scraping (Fallback ou Complément)
            try:
                from tools.web_searcher import web_searcher
                
                filters = action_plan["filters"]
                keywords = " ".join(action_plan.get("keywords", ["informatique"]))
                
                logger.info(f"Web Search fallback: {keywords}")
                
                web_jobs = await web_searcher.search_jobs(
                    keywords=keywords,
                    location=filters.get("location", "Québec"),
                    job_type=filters.get("job_type", "stage"),
                    max_results=max(5, int(requested_limit / 2)) # Un peu moins que la limite totale
                )
                
                if web_jobs:
                    logger.info(f"Web Search: {len(web_jobs)} jobs retrieved")
                    all_jobs.extend(web_jobs)
                    
            except Exception as e:
                 logger.warning(f"Web Search Error: {e}")

            # Si aucune offre trouvée au total
            if not all_jobs:
                return []

            # --- FILTRAGE STRICT POST-SEARCH (GLOBAL) ---
            # Appliqué à toutes les sources (Jooble, JSearch, Web)
            
            job_type_filter = action_plan["filters"].get("job_type", "").lower()
            keywords_text = " ".join(action_plan.get("keywords", [])).lower()
            raw_desc = action_plan.get("description", "").lower() # Raw user query
            
            is_internship_or_junior = any(k in job_type_filter for k in ["stage", "intern", "junior"]) or \
                                      any(k in keywords_text for k in ["stage", "junior"]) or \
                                      any(k in raw_desc for k in ["stage", "junior"])
            
            if is_internship_or_junior:
                logger.info("🕵️ Mode Stage/Junior activé: Filtrage strict des seniors...")
                filtered_jobs = []
                
                # Use regex to strictly match whole words
                import re
                
                non_intern_titles = [r"\bsenior\b", r"\bprincipal\b", r"\blead\b", r"\bstaff\b", r"\bmanager\b", r"\barchitect\b", r"\bhead of\b", r"\bdirector\b", r"\bexpert\b", r"\bchef\b", r"\bsr\.?\b"]
                intern_keywords = [r"\bstage\b", r"\bstagiaire\b", r"\bintern\b", r"\binternship\b", r"\bco-op\b", r"\bstudent\b", r"\bétudiant\b", r"\betudiant\b", r"\bjunior\b", r"\bsummer\b", r"\bpfe\b", r"\bentry.?level\b", r"\bdébutant\b", r"\bgrad\b", r"\bgraduate\b"] 
                
                for job in all_jobs:
                    title = job.get("title", "").lower()
                    desc = job.get("description", "").lower()
                    
                    # 1. Exclusion Seniors using regex
                    if any(re.search(bad, title) for bad in non_intern_titles):
                        logger.debug(f"Skipping Senior role: {job.get('title')}")
                        continue
                        
                    # 2. Inclusion Stricte et intelligente
                    in_title = any(re.search(k, title) for k in intern_keywords)
                    in_desc = any(re.search(k, desc) for k in intern_keywords)
                    
                    if not in_title:
                        # Le titre ne mentionne pas "Stage/Intern". C'est TRÈS SUSPECT.
                        # Cela peut être une pollution de description (autres offres suggérées en bas de page).
                        
                        # A. S'il n'y a pas non plus le mot dans la description -> Poubelle
                        if not in_desc:
                            logger.debug(f"Skipping unclear role (no intern keyword anywhere): {job.get('title')}")
                            continue
                            
                        # B. Si le mot y est, mais qu'il demande des années d'expérience (ex: "5+ years", "3 ans") -> Poubelle
                        # Regex : "2 à 99" + optionnel "+" + "ans/years"
                        exp_match = re.search(r"\b([2-9]|[1-9][0-9])\+?\s*(?:ans?|years?)\b(?!\s*(?:d'études?|of university|of studies|of college|bachelor))", desc)
                        if exp_match:
                            logger.debug(f"Skipping non-intern title '{job.get('title')}' due to exp requirement: {exp_match.group(0)}")
                            continue
                            
                        # C. On vérifie la densité du mot "stage" ou "intern" pour prouver que ce n'est pas juste un lien en bas de page
                        # Si le mot n'apparait qu'une fois dans une tres longue description, c'est probablement du bruit.
                        # Mais restons prudents, on l'accepte si on est arrivé ici.

                    filtered_jobs.append(job)
                
                if len(filtered_jobs) < len(all_jobs):
                    logger.warning(f"🧹 Filtrage terminé: {len(all_jobs)} -> {len(filtered_jobs)} offres pertinentes conservées.")
                    all_jobs = filtered_jobs

            logger.info(f"Total combined: {len(all_jobs)} results. Enriching...")
            
            # Dédoublonnage basé sur l'URL ou le titre+ref
            unique_jobs = {j.get("url"): j for j in all_jobs if j.get("url")}.values()
            jobs = list(unique_jobs)
            
            # 2. Enrichissement Profond (Scraping du contenu pour les Top N)
            # On trie d'abord sommairement pour ne pas scraper n'importe quoi
            
            # Prioriser les résultats Jooble qui ont souvent un snippet mais pas de description complète
            # Mais Jooble bloque souvent le scraping direct de ses liens de redirection.
            # On va tenter d'enrichir uniquement ceux qui semblent scrapables.
            
            priority_jobs = []
            key_terms = [k.lower() for k in action_plan.get("keywords", [])]
            
            for job in jobs:
                score = 0
                title = job.get("title", "").lower()
                if any(k in title for k in key_terms): score += 1
                
                # Bonus pour les APIs payantes/fiables
                if job.get("source") in ["Jooble", "JSearch"]: score += 0.5
                
                job["_temp_score"] = score
            
            jobs.sort(key=lambda x: x.get("_temp_score", 0), reverse=True)
            
            # On garde les Top N + Marge pour le scraping profond ou l'affichage
            jobs_to_process = jobs[:requested_limit + 10]
            
            async def enrich_job(job):
                # Si c'est du Jooble, l'URL est souvent une redirection. 
                # Le scraping direct peut échouer ou être bloqué.
                # On tente quand même si ce n'est pas déjà fait.
                if job.get("url") and not job.get("scraped"):
                    # Petit hack: si c'est jooble, on considère le snippet comme description temporaire suffisant
                    # pour éviter de se faire bannir par trop de requêtes sur leurs liens de tracking.
                    if job.get("source") == "Jooble":
                         job["scraped"] = True # On marque comme traité
                         # On laisse le snippet comme description par défaut
                    else:
                        try:
                            content = await web_searcher.scrape_page_content(job["url"])
                            if len(content) > 500:
                                job["description"] = content
                                job["scraped"] = True
                        except:
                            pass
                return job

            # Exécution parallèle
            import asyncio
            enriched_jobs = await asyncio.gather(*[enrich_job(j) for j in jobs_to_process])
            
            return enriched_jobs
        
        except Exception as e:
            logger.warning(f"Global Search Error: {e}")
            return []
    
    async def _analyze_cv(self, cv_text: str) -> Dict[str, Any]:
        """Analyse un CV avec le LLM."""
        prompt = f"""Analyse ce CV et extrais les informations clés au format JSON:

CV:
{cv_text}

Extrais:
1. Compétences techniques (liste)
2. Années d'expérience (nombre)
3. Formation (diplôme le plus élevé)
4. Langues (liste)
3. Formation (diplôme le plus élevé)
4. Langues (liste)
5. Domaines d'expertise (liste)
6. Postes visés (liste de 2-3 titres de poste idéaux déduits du profil)

Réponds UNIQUEMENT avec un JSON structuré."""
        
        response = await self.generate_response(prompt)
        
        # Parser la réponse (simple extraction pour démo)
        return {
            "skills": self._extract_skills_from_text(cv_text),
            "experience_years": self._extract_experience(cv_text),
            "education": self._extract_education(cv_text),
            "languages": self._extract_languages(cv_text),
            "domains": ["informatique", "développement"],
            "target_roles": self._extract_target_roles(cv_text),
        }
    
    async def _extract_criteria_from_text(self, text: str) -> Dict[str, Any]:
        """Extrait les critères de recherche depuis un texte libre."""
        prompt = f"""Analyse cette demande de recherche d'emploi et extrais les critères au format JSON.
        
Demande: "{text}"

Extrais:
1. location (ex: Québec, Montréal, Remote)
2. job_type (ex: stage, emploi, contrat)
3. domain (ex: informatique, marketing)
4. keywords (liste de mots-clés techniques ou roles)

Réponds UNIQUEMENT avec un JSON structuré."""

        try:
            response = await self.generate_response(prompt)
            if not response or not response.strip():
                raise ValueError("Réponse vide du LLM")
                
            # Extraction robuste du JSON via Regex
            import json
            import re
            
            # Chercher le premier bloc JSON valide { ... }
            json_match = re.search(r'\{.*\}', response.strip(), re.DOTALL)
            
            if json_match:
                json_str = json_match.group(0)
                data = json.loads(json_str)
                return data
            else:
                # Tentative de nettoyage manuel si regex échoue
                json_str = response.strip()
                if json_str.startswith("```json"):
                    json_str = json_str[7:-3]
                elif json_str.startswith("```"):
                    json_str = json_str[3:-3]
                data = json.loads(json_str)
                return data
                
        except Exception as e:
            logger.warning(f"⚠️ Extraction critères échouée (fallback activé): {e}")
            
            # Fallback amélioré (filtrage des stop words)
            stop_words = {"le", "la", "les", "un", "une", "des", "à", "de", "pour", "moi", "je", "trouve", "offre", "offres", "job", "jobs", "en", "sur", "dans", "et", "ou"}
            raw_words = text.lower().split()
            cleaned_keywords = [w for w in raw_words if w not in stop_words]
            
            return {
                "location": "Québec" if "québec" in text.lower() else "Montréal",
                "job_type": "stage" if "stage" in text.lower() else "emploi",
                "domain": "informatique",
                "keywords": cleaned_keywords
            }
    
    async def _match_jobs(self, jobs: List[Dict], cv_profile: Dict) -> List[Dict]:
        """Matche les offres avec le profil CV (Optimisé)."""
        matched = []
        
        # 1. Calculer les scores heuristiques pour TOUTES les offres
        for job in jobs:
            # S'assurer que required_skills est peuplé
            if not job.get("required_skills"):
                 job_desc = job.get("description", "") or job.get("snippet", "")
                 if job_desc:
                     job["required_skills"] = self._extract_skills_from_text(job_desc)
            
            score = self._calculate_match_score(job, cv_profile)
            job["match_score"] = score
            job["matched_skills"] = self._get_matched_skills(job, cv_profile)
            matched.append(job)
            
        # 2. Trier par score décroissant
        matched.sort(key=lambda x: x["match_score"], reverse=True)
        
        # --- NEW LAYER 3: DEEP AI EVALUATION FOR NOISE CULLING ---
        # Si le profil est vide (pas de CV fourni), on garde tout mais on justifie
        valid_matched = []
        import asyncio
        for job in matched:
            # Si le score heuristique est DÉSASTREUX (ex: < 35), on le lâche direct sans payer d'API
            if score < 30 and cv_profile.get("skills"):
                 logger.debug(f"🗑️ Dropping very low heuristic score job: {job.get('title')} (Score: {score})")
                 continue
                 
            try:
                justification = await self._get_match_justification(job, cv_profile)
                job["match_justification"] = justification
                
                # Le LLM est instruit à commencer sa justification par [OUI] ou [NON]
                if "[NON]" in justification.upper() or "ne correspond pas" in justification.lower() or "incompatible" in justification.lower():
                     logger.debug(f"🗑️ AI Deep Reject: {job.get('title')} - {justification}")
                     # On le drop complètement s'il y a un CV (sinon on garde)
                     if cv_profile.get("skills"):
                         continue
                         
            except Exception:
                job["match_justification"] = "Analyse détaillée non disponible."
                
            valid_matched.append(job)
        
        return valid_matched
    
    
    def _calculate_match_score(self, job: Dict, cv_profile: Dict) -> int:
        """Calcule un score de compatibilité avancé (0-100)."""
        score = 0
        total_weight = 0
        
        # 1. Correspondance Titre (30 points) - CRITIQUE
        # Si le titre du job contient des mots clés des "postes visés"
        job_title = job.get("title", "").lower()
        target_roles = [r.lower() for r in cv_profile.get("target_roles", [])]
        
        title_match_score = 0
        if target_roles:
            # Vérifier si un des rôles cibles est dans le titre de l'offre
            for role in target_roles:
                # Token matching simple
                role_tokens = set(role.split())
                title_tokens = set(job_title.split())
                if role in job_title:
                    title_match_score = 1.0 # Match exact ou sous-chaine forte
                    break
                elif len(role_tokens & title_tokens) >= len(role_tokens) * 0.7:
                     title_match_score = max(title_match_score, 0.8)
                elif len(role_tokens & title_tokens) > 0:
                     title_match_score = max(title_match_score, 0.4)
        else:
            # Fallback si pas de roles cibles (mot clé générique)
            if "développeur" in job_title or "developer" in job_title or "ingénieur" in job_title:
                title_match_score = 0.5
        
        score += title_match_score * 30
        total_weight += 30
        
        # 2. Compétences (35 points)
        cv_skills = set(s.lower() for s in cv_profile.get("skills", []))
        # Extraire aussi les skills de la description si required_skills est vide/pauvre
        job_desc = job.get("description", "").lower()
        job_skills = set(s.lower() for s in job.get("required_skills", []))
        
        # Si pas de skills explicites, on cherche les skills du CV dans la description
        if not job_skills and job_desc:
            found_desc_skills = [s for s in cv_skills if s in job_desc]
            if found_desc_skills:
                skill_match = len(found_desc_skills) / min(len(cv_skills), 10) # Ratio par rapport au CV
                score += min(skill_match * 35, 35)
        elif job_skills:
            # Intersection pondérée
            common = cv_skills & job_skills
            if not job_skills:
                skill_match = 0
            else:
                skill_match = len(common) / len(job_skills)
            score += min(skill_match * 35, 35)
            
        total_weight += 35

        # 3. Expérience (20 points)
        cv_exp = cv_profile.get("experience_years", 0)
        # Tenter d'extraire l'expérience de la description si non structurée
        job_exp = job.get("required_experience", 0)
        if job_exp == 0 and job_desc:
             job_exp = self._extract_experience(job_desc)
        
        # Logique de pénalité/bonus seniorité
        if cv_exp >= job_exp:
            score += 20 # Qualifié
        elif cv_exp >= job_exp * 0.7:
            score += 10 # Presque qualifié
        elif job_exp > 5 and cv_exp < 2:
            score -= 10 # Junior postulant à Senior (Pénalité)
        else:
            score += 5 # Tentable
            
        total_weight += 20
        
        # 4. Localisation (10 points)
        if job.get("location", "").lower() in ["québec", "montreal", "remote"] or "télétravail" in job.get("location", "").lower():
            score += 10
        total_weight += 10
        
        # 5. Langues (5 points)
        # Bonus gratuit souvent
        score += 5
        total_weight += 5
        
        return min(int(score), 100)
    
    def _get_matched_skills(self, job: Dict, cv_profile: Dict) -> List[str]:
        """Retourne les compétences matchées."""
        cv_skills = set(s.lower() for s in cv_profile.get("skills", []))
        job_skills = set(s.lower() for s in job.get("required_skills", []))
        return list(cv_skills & job_skills)
    
    async def _get_match_justification(self, job: Dict, cv_profile: Dict) -> str:
        """Génère une justification du match avec le LLM."""
        prompt = f"""Tu es un recruteur expert impitoyable.
Évalue si le candidat suivant A LES COMPÉTENCES ET L'EXPÉRIENCE REQUISES pour le poste.
Si le poste demande 5 ans d'expérience et le candidat en a 0, le match est [NON].
Si le poste demande Azure et IA, et le candidat a seulement Python basique, c'est [NON].

Ton analyse DOIT commencer obligatoirement par "[OUI]" si le profil est qualifié, ou "[NON]" si le profil est disqualifié (manque d'expérience évidente, etc.).
Ensuite, justifie en 1 ou 2 phrases concises.

Profil du Candidat:
- Compétences: {', '.join(cv_profile.get('skills', [])[:10])}
- Expérience: {cv_profile.get('experience_years', 0)} ans
- Postes visés: {', '.join(cv_profile.get('target_roles', []))}

Poste:
- Titre: {job.get('title', 'N/A')}
- Description courte: {job.get('description', '')[:200]}...
- Compétences requises de l'offre: {', '.join(job.get('required_skills', [])[:10])}
- Expérience de l'offre (généralement estimée): {job.get('required_experience', 'Non spécifiée')} ans
"""
        
        return await self.generate_response(prompt)
    
    async def generate_cover_letter(self, job: Dict, cv_profile: Dict) -> str:
        """Génère une lettre de motivation personnalisée."""
        logger.info(f"✍️ Rédaction de la lettre pour {job.get('company', 'l\'entreprise')}...")
        
        prompt = f"""Rédige une lettre de motivation professionnelle et percutante pour ce poste.
        
        CANDIDAT:
        - Compétences: {', '.join(cv_profile.get('skills', []))}
        - Expérience: {cv_profile.get('experience_years', 0)} ans
        - Éducation: {cv_profile.get('education', 'Non spécifié')}
        
        POSTE VISÉ:
        - Titre: {job.get('title', 'N/A')}
        - Entreprise: {job.get('company', 'N/A')}
        - Description: {job.get('description', '')[:500]}...
        - Compétences requises: {', '.join(job.get('required_skills', []))}
        
        INSTRUCTIONS:
        - Ton: Professionnel, motivé, mais direct.
        - Langue: Français.
        - Format: Markdown (sans les balises ```markdown).
        - Structure: En-tête (Nom, Date), Introduction (accroche), Corps (pourquoi moi + pourquoi vous), Conclusion (dispo entretien).
        - Ne pas inventer d'adresse ou de téléphone, utiliser des placeholders [Téléphone], [Email].
        """
        
        return await self.generate_response(prompt)

    async def adapt_cv(self, original_cv_text: str, job_description: str) -> str:
        """
        Adapte le CV pour qu'il corresponde mieux à une offre spécifique.
        """
        logger.info("🎨 Adaptation du CV en cours...")
        
        prompt = f"""
        Ton objectif est de réécrire ce CV pour qu'il matche PARFAITEMENT l'offre d'emploi ci-dessous.
        
        OFFRE CIBLE:
        {job_description[:1500]}...
        
        CV ORIGINAL:
        {original_cv_text}
        
        INSTRUCTIONS:
        1. Garde la vérité (ne pas inventer d'expériences).
        2. Reformule les expériences pour utiliser les mots-clés de l'offre.
        3. Mets en avant les compétences requises par l'offre.
        4. Supprime les détails non pertinents.
        5. Structure le CV de manière professionnelle (Markdown).
        
        IMPORTANT: RENDS UNIQUEMENT LE CONTENU DU CV EN MARKDOWN. 
        NE METS PAS DE TEXTE AVANT OU APRÈS (PAS DE "Voici le CV...", PAS DE CODE BLOCK ```markdown).
        COMMENCE DIRECTEMENT PAR LE TITRE OU LE NOM.

        Le résultat doit être le CV complet réécrit.
        """
        
        return await self.generate_response(prompt)

    def _extract_contact_info(self, text: str) -> Dict[str, str]:
        """Extrait les emails et numéros de téléphone du texte."""
        contacts = {"email": "", "phone": ""}
        if not text:
            return contacts
            
        # Regex Email
        email_match = re.search(r'[\w.+-]+@[\w-]+\.[a-zA-Z0-9-.]+', text)
        if email_match:
            contacts["email"] = email_match.group(0)
            
        # Regex Phone (Format Nord-Américain et International basique)
        # Ex: 555-555-5555, (555) 555-5555, +1 555...
        phone_match = re.search(r'(\+?\d{1,2}\s?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}', text)
        if phone_match:
            contacts["phone"] = phone_match.group(0)
            
        return contacts

    async def generate_application_email(self, job: Dict, cv_profile: Dict, application_type: str = "emploi") -> Dict[str, str]:
        """
        Génère un email de candidature personnalisé.
        application_type: 'stage' ou 'emploi'
        """
        company = job.get('company', 'l\'entreprise')
        logger.info(f"📧 Génération email ({application_type}) pour {company}...")
        
        # Contexte spécifique selon le type
        if application_type == "stage":
            context_prompt = "Ceci est une demande de STAGE. Insiste sur la soif d'apprendre, la formation académique en cours et la disponibilité."
        else:
            context_prompt = "Ceci est une candidature pour un EMPLOI. Insiste sur l'expérience, l'autonomie et la valeur ajoutée immédiate."

        # Récupération infos candidat pour signature (extraction du CV ou générique)
        # Note: Dans une version idéale, on passerait l'objet User complet. Ici on extrait du CV analysis.
        candidate_name = cv_profile.get("name", "[Votre Nom]")
        candidate_phone = cv_profile.get("phone", "[Votre Téléphone]")
        candidate_email = cv_profile.get("email", "[Votre Email]")

        prompt = f"""Rédige un email de candidature professionnel.
        
        CONTEXTE:
        - Type: {application_type.upper()}
        - {context_prompt}
        
        CANDIDAT:
        - Compétences: {', '.join(cv_profile.get('skills', []))}
        - Expérience: {cv_profile.get('experience_years', 0)} ans
        
        OFFRE CIBLE:
        - Poste: {job.get('title', 'N/A')}
        - Entreprise: {company}
        - Points Forts (IA): {job.get('match_justification', '')}
        - Description clé: {job.get('description', '')[:400]}...
        
        INSTRUCTIONS:
        1. Sujet accrocheur (ex: Candidature [Poste] - [Nom]).
        2. Ton: Professionnel, courtois, direct.
        3. Corps: 
           - Salutation (à recruteur spécifique si nom trouvé, sinon générique).
           - Accroche (pourquoi cette entreprise/ce poste).
           - Pourquoi moi (lien compétences/besoin).
           - Utilise les "Points Forts (IA)" pour personnaliser l'argumentaire.
           - Call to action (dispo pour entrevue).
           - Signature formelle.
        
        Format de réponse attendu (JSON):
        {{
            "subject": "Sujet de l'email",
            "body": "Corps de l'email (format texte brut avec sauts de ligne, PAS de markdown, prêt à copier-coller)"
        }}
        """
        
        response = await self.generate_response(prompt)
        
        # Tentative de parsing JSON simple
        import json
        try:
            # Nettoyage basique
            clean_resp = response.replace("```json", "").replace("```", "").strip()
            start = clean_resp.find("{")
            end = clean_resp.rfind("}") + 1
            if start >= 0 and end > start:
                data = json.loads(clean_resp[start:end])
                return data
        except Exception:
            pass
            
        # Fallback
        return {
            "subject": f"Candidature {application_type.capitalize()} - {job.get('title')}",
            "body": response
        }

    def _build_search_prompt(self, cv_analysis: Dict, filters: Dict) -> str:
        """Construit le prompt de stratégie de recherche."""
        return f"""Crée une stratégie de recherche d'emploi basée sur:

Profil:
{cv_analysis}

Critères:
- Localisation: {filters.get('location', 'Québec')}
- Type: {filters.get('job_type', 'stage')}
- Domaine: {filters.get('domain', 'informatique')}

Suggère les meilleurs mots-clés et plateformes à cibler."""
    
    def _extract_keywords(self, cv_analysis: Dict, filters: Dict) -> List[str]:
        """Extrait les mots-clés de recherche de manière robuste."""
        raw_keywords = []
        
        # Helper pour aplatir les listes imbriquées (robustesse)
        def add_items(items):
            if isinstance(items, list):
                for item in items:
                    add_items(item)
            elif isinstance(items, str):
                raw_keywords.append(items)
            elif items is not None:
                raw_keywords.append(str(items))

        # 1. Mots-clés de la description (priorité)
        if filters.get("keywords"):
             add_items(filters["keywords"])
        
        # 2. Domaine
        if filters.get("domain"): 
            add_items(filters["domain"])
        
        # 3. Compétences du CV
        skills = cv_analysis.get("skills", [])
        if isinstance(skills, list):
            add_items(skills[:3]) # Top 3
        
        # Nettoyage et dédoublonnage
        seen = set()
        clean_keywords = []
        
        for k in raw_keywords:
            if not k or not k.strip(): continue
            
            k_clean = k.strip()
            k_lower = k_clean.lower()
            
            if k_lower not in seen:
                seen.add(k_lower)
                clean_keywords.append(k_clean)
                
        return clean_keywords

    def _extract_target_roles(self, text: str) -> List[str]:
        """Déduit des titres de postes basés sur le CV."""
        roles = []
        text_lower = text.lower()
        
        # Déductions simples par mots clés
        if "python" in text_lower: roles.append("Développeur Python")
        if "vendeur" in text_lower or "vente" in text_lower: roles.append("Conseiller aux ventes") # Adapté au CV
        if "service client" in text_lower: roles.append("Service à la clientèle")
        if "react" in text_lower or "node" in text_lower: roles.append("Développeur Web")
        if "data" in text_lower and "science" in text_lower: roles.append("Data Scientist")
        
        # Si rien trouvé, générique
        if not roles: roles.append("Emploi")
        
        return roles
    
    def _extract_skills_from_text(self, text: str) -> List[str]:
        """Extrait les compétences techniques du texte."""
        # Liste de compétences communes en informatique
        common_skills = [
            "python", "java", "javascript", "c++", "c#", "sql", "html", "css",
            "react", "angular", "vue", "node", "django", "flask", "spring",
            "git", "docker", "kubernetes", "aws", "azure", "linux", "windows",
            "machine learning", "ai", "data science", "web", "mobile", "api"
        ]
        
        text_lower = text.lower()
        found_skills = [skill for skill in common_skills if skill in text_lower]
        return found_skills[:10]  # Top 10
    
    def _extract_experience(self, text: str) -> int:
        """Extrait les années d'expérience."""
        # Chercher des patterns comme "2 ans", "3 years", etc.
        patterns = [
            r"(\d+)\s*ans?\s+d[''']expérience",
            r"(\d+)\s+years?\s+(?:of\s+)?experience",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                return int(match.group(1))
        
        return 0  # Débutant par défaut
    
    def _extract_education(self, text: str) -> str:
        """Extrait le niveau d'éducation."""
        text_lower = text.lower()
        
        if "doctorat" in text_lower or "phd" in text_lower:
            return "Doctorat"
        elif "maîtrise" in text_lower or "master" in text_lower:
            return "Maîtrise"
        elif "baccalauréat" in text_lower or "bachelor" in text_lower:
            return "Baccalauréat"
        elif "dec" in text_lower or "collégial" in text_lower:
            return "DEC"
        
        return "Non spécifié"
    
    def _extract_languages(self, text: str) -> List[str]:
        """Extrait les langues parlées."""
        text_lower = text.lower()
        languages = []
        
        if "français" in text_lower or "french" in text_lower:
            languages.append("français")
        if "anglais" in text_lower or "english" in text_lower:
            languages.append("anglais")
        if "espagnol" in text_lower or "spanish" in text_lower:
            languages.append("espagnol")
        
        return languages if languages else ["français"]  # Défaut Québec
    
    def _get_mock_jobs(self, filters: Dict) -> List[Dict]:
        """Génère des offres de test pour démonstration."""
        location = filters.get("location", "Québec")
        
        return [
            {
                "id": "job-001",
                "title": "Stage en développement web - Python/React",
                "company": "TechCorp Québec",
                "location": "Québec",
                "job_type": "stage",
                "required_skills": ["python", "react", "javascript", "sql", "git"],
                "required_experience": 0,
                "description": "Stage de 4 mois en développement web full-stack",
                "url": "https://example.com/job1"
            },
            {
                "id": "job-002",
                "title": "Stagiaire développeur Java",
                "company": "Solutions Inc",
                "location": "Montréal",
                "job_type": "stage",
                "required_skills": ["java", "spring", "sql", "git"],
                "required_experience": 0,
                "description": "Stage en développement backend Java",
                "url": "https://example.com/job2"
            },
            {
                "id": "job-003",
                "title": "Stage en science des données",
                "company": "DataLab QC",
                "location": "Québec",
                "job_type": "stage",
                "required_skills": ["python", "machine learning", "sql", "data science"],
                "required_experience": 1,
                "description": "Stage en analyse de données et ML",
                "url": "https://example.com/job3"
            },
            {
                "id": "job-004",
                "title": "Développeur mobile iOS/Android - Stage",
                "company": "MobileApps Québec",
                "location": "Québec",
                "job_type": "stage",
                "required_skills": ["swift", "kotlin", "mobile", "api"],
                "required_experience": 0,
                "description": "Stage développement applications mobiles",
                "url": "https://example.com/job4"
            },
            {
                "id": "job-005",
                "title": "Stage DevOps",
                "company": "CloudTech",
                "location": "Remote",
                "job_type": "stage",
                "required_skills": ["docker", "kubernetes", "linux", "git", "aws"],
                "required_experience": 1,
                "description": "Stage en infrastructure et déploiement",
                "url": "https://example.com/job5"
            },
        ]
