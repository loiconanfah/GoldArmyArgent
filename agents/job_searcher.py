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
    
    # Villes/regions connues -> string precis pour les APIs (support mondial)
    LOCATION_MAP = {
        # Canada
        "qc": "Quebec, QC, Canada",
        "quebec": "Quebec, QC, Canada",
        "montreal": "Montreal, QC, Canada",
        "laval": "Laval, QC, Canada",
        "longueuil": "Longueuil, QC, Canada",
        "gatineau": "Gatineau, QC, Canada",
        "sherbrooke": "Sherbrooke, QC, Canada",
        "saguenay": "Saguenay, QC, Canada",
        "ontario": "Ontario, Canada",
        "toronto": "Toronto, ON, Canada",
        "ottawa": "Ottawa, ON, Canada",
        "on": "Ontario, Canada",
        "bc": "British Columbia, Canada",
        "vancouver": "Vancouver, BC, Canada",
        "alberta": "Alberta, Canada",
        "calgary": "Calgary, AB, Canada",
        "edmonton": "Edmonton, AB, Canada",
        "canada": "Canada",
        # France
        "france": "France",
        "paris": "Paris, France",
        "lyon": "Lyon, France",
        "marseille": "Marseille, France",
        "toulouse": "Toulouse, France",
        "bordeaux": "Bordeaux, France",
        "nantes": "Nantes, France",
        "lille": "Lille, France",
        "strasbourg": "Strasbourg, France",
        "grenoble": "Grenoble, France",
        "nice": "Nice, France",
        "rennes": "Rennes, France",
        "montpellier": "Montpellier, France",
        # Belgique
        "belgique": "Belgique",
        "belgium": "Belgium",
        "bruxelles": "Bruxelles, Belgique",
        "brussels": "Brussels, Belgium",
        # Suisse
        "suisse": "Suisse",
        "switzerland": "Switzerland",
        "geneve": "Geneve, Suisse",
        "geneva": "Geneva, Switzerland",
        "zurich": "Zurich, Switzerland",
        # UK
        "uk": "United Kingdom",
        "united kingdom": "United Kingdom",
        "london": "London, United Kingdom",
        "manchester": "Manchester, United Kingdom",
        # USA
        "usa": "United States",
        "us": "United States",
        "united states": "United States",
        "new york": "New York, NY, United States",
        "san francisco": "San Francisco, CA, United States",
        "los angeles": "Los Angeles, CA, United States",
        "seattle": "Seattle, WA, United States",
        "austin": "Austin, TX, United States",
        # Allemagne
        "allemagne": "Germany",
        "germany": "Germany",
        "berlin": "Berlin, Germany",
        "munich": "Munich, Germany",
        "hamburg": "Hamburg, Germany",
        # Maroc
        "maroc": "Maroc",
        "morocco": "Morocco",
        "casablanca": "Casablanca, Maroc",
        "rabat": "Rabat, Maroc",
        # Autres
        "luxembourg": "Luxembourg",
        "amsterdam": "Amsterdam, Netherlands",
        "barcelone": "Barcelona, Spain",
        "barcelona": "Barcelona, Spain",
        "madrid": "Madrid, Spain",
        "dubai": "Dubai, UAE",
    }

    # Mots-cles pays -> code ISO 2 lettres pour JSearch
    COUNTRY_CODE_MAP = {
        "canada": "ca",
        "france": "fr",
        "belgique": "be", "belgium": "be",
        "suisse": "ch", "switzerland": "ch",
        "united kingdom": "gb", "uk": "gb",
        "united states": "us", "usa": "us",
        "germany": "de", "allemagne": "de",
        "maroc": "ma", "morocco": "ma",
        "luxembourg": "lu",
        "netherlands": "nl", "pays-bas": "nl",
        "espagne": "es", "spain": "es",
        "uae": "ae",
    }

    def _normalize_location(self, loc: str) -> str:
        """Normalise une localisation pour les APIs - support mondial."""
        if not loc:
            return "Quebec, QC, Canada"
        normalized = self.LOCATION_MAP.get(loc.lower().strip())
        if normalized:
            return normalized
        # Si deja structure (avec virgule), conserver tel quel
        if "," in loc:
            return loc
        # IMPORTANT: ne pas ajouter Canada systematiquement - retourner tel quel
        return loc

    def _get_country_code(self, location: str) -> str:
        """Determine le code pays ISO 2 lettres a partir d'une localisation."""
        loc_lower = location.lower()
        for keyword, code in self.COUNTRY_CODE_MAP.items():
            if keyword in loc_lower:
                return code
        # Defaut: Canada si rien trouve (comportement precedent conserve)
        return "ca"

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
        
        explicit_location = task.get("location", "")
        # Normalize the location to be as precise as possible
        base_location = self._normalize_location(explicit_location) if explicit_location else "Québec, QC, Canada"
        
        # --- Détection du type d'emploi (stage, internship, temps plein, etc.) ---
        query_lower = query.lower()
        job_type = "emploi"  # Défaut
        target_level = "junior" # Niveau par défaut
        
        stage_keywords = ["stage", "internship", "intern", "coop", "co-op", "apprenti", "apprentissage", "alternance"]
        senior_keywords = ["senior", "principal", "staff", "lead", "sr.", "manager", "directeur", "director"]
        
        if any(kw in query_lower for kw in stage_keywords):
            job_type = "stage"
            target_level = "stage"
        elif any(kw in query_lower for kw in senior_keywords):
            target_level = "senior"
        
        # Si l'utilisateur tape "stage", on garde le mot dans les keywords pour que les APIs cherchent des stages
        # On ne laisse pas le LLM supprimer ce mot important
        keywords_for_search = query  # Base: la query brute
        
        prompt = f"""
        L'utilisateur cherche: "{query}"
        
        Consignes:
        1. Génère une LISTE de 3 à 4 variations de mots-clés de recherche (synonymes, anglais/français, tech stack) pour maximiser les résultats.
           EX: Pour "dev logiciel", génère ["développeur logiciel", "software engineer", "fullstack developer"].
           IMPORTANT: Si c'est un stage, inclus "stage" ou "internship" dans CHAQUE variation.
        2. Extrais la ville/région s'il y en a une dans la recherche. Sinon retourne null.
        
        Réponds UNIQUEMENT en JSON avec les clés 'keywords_list' (liste de strings) et 'location' (string ou null).
        """
        
        criteria = {"keywords_list": [keywords_for_search], "location": base_location, "job_type": job_type}
        
        try:
            if query:
                resp = await self.generate_response(prompt)
                import json, re
                match = re.search(r'\{.*\}', resp.replace('\n', ''), re.S)
                if match:
                    parsed = json.loads(match.group(0))
                    if "keywords_list" in parsed and isinstance(parsed["keywords_list"], list):
                        criteria["keywords_list"] = parsed["keywords_list"]
                        
                        # S'assurer que le type (stage) est bien présent partout si c'est un stage
                        if job_type == "stage":
                            new_list = []
                            for kw in criteria["keywords_list"]:
                                if not any(skw in kw.lower() for skw in stage_keywords):
                                    new_list.append(f"stage {kw}")
                                else:
                                    new_list.append(kw)
                            criteria["keywords_list"] = list(set(new_list)) # Dedup
                            
                    # Only use LLM location if user didn't explicitly provide one
                    if not explicit_location and parsed.get("location") and parsed["location"] != "null":
                        criteria["location"] = self._normalize_location(parsed["location"])
                        
            elif cv_profile.get("target_roles"):
                 criteria["keywords_list"] = [cv_profile["target_roles"][0]]
        except Exception as e:
            logger.warning(f"Fallback LLM extraction failed: {e}. Using raw query variations.")
            # Fallback simple si l'IA échoue
            if job_type == "stage":
                 criteria["keywords_list"] = [f"stage {query}", f"internship {query}", query]
            
        # Injecter les infos critiques dans le profil pour l'évaluateur AI
        cv_profile["target_location"] = base_location
        cv_profile["target_level"] = target_level
        
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
        Exécute la recherche Multi-Pass sur toutes les APIs. 
        Teste plusieurs variations de mots-clés pour maximiser le pool initial.
        """
        criteria = action_plan.get("criteria", {})
        keywords_list = criteria.get("keywords_list", ["informatique"])
        location = str(criteria.get("location", "Québec"))
        job_type = criteria.get("job_type", "emploi")
        limit = action_plan.get("limit", 10)
        
        logger.info(f"🔍 ACT: Recherche Multi-Pass à '{location}' pour: {keywords_list}")
        
        all_raw_jobs = []
        seen_dedup = set() # Pour éviter les doublons exacts par titre/compagnie
        
        # 1. Boucle sur les variations de mots-clés
        for kw in keywords_list:
            logger.info(f"📡 Tentative avec mot-clé: '{kw}'")
            
            # --- JOOBLE ---
            if settings.jooble_api_key:
                try:
                    from tools.jooble_searcher import JoobleSearcher
                    jooble = JoobleSearcher(api_key=settings.jooble_api_key)
                    # On demande plus de résultats par pass pour avoir du choix
                    j_jobs = await jooble.search_jobs(keywords=kw, location=location, limit=40)
                    if j_jobs:
                        for job in j_jobs:
                            key = f"{job.get('title')}-{job.get('company')}".lower()
                            if key not in seen_dedup:
                                seen_dedup.add(key)
                                all_raw_jobs.append(job)
                except Exception as e:
                    logger.error(f"🔴 Erreur Jooble sur '{kw}': {e}")
            
            # --- JSEARCH ---
            if settings.rapidapi_key: # Changed from settings.jsearch_api_key to settings.rapidapi_key based on original code
                try:
                    from tools.jsearch_searcher import JSearchSearcher
                    jsearch = JSearchSearcher(api_key=settings.rapidapi_key)
                    js_jobs = await jsearch.search_jobs(query=f"{kw} in {location}", limit=40)
                    if js_jobs:
                        for job in js_jobs:
                            key = f"{job.get('title')}-{job.get('company')}".lower()
                            if key not in seen_dedup:
                                seen_dedup.add(key)
                                all_raw_jobs.append(job)
                except Exception as e:
                    logger.error(f"🔴 Erreur JSearch sur '{kw}': {e}")
                    
        logger.info(f"✅ Pool initial collecté: {len(all_raw_jobs)} offres brutes.")
        
        # 3. Web Searcher (JobBank fallback) - This part was removed from the loop and should be executed once.
        # The original instruction implies keeping the Web Searcher part after the loop, but before the enrichment.
        # Let's re-add it here, outside the keyword loop, as it was in the original code.
        try:
            from tools.web_searcher import web_searcher
            # For Web Searcher, we use the primary keyword from the list or the first one if multiple
            primary_keyword = keywords_list[0] if keywords_list else "informatique"
            w_jobs = await web_searcher.search_jobs(keywords=primary_keyword, location=location, max_results=limit)
            if w_jobs:
                logger.info(f"🟢 Web/JobBank a trouvé {len(w_jobs)} offres.")
                for job in w_jobs:
                    key = f"{job.get('title')}-{job.get('company')}".lower()
                    if key not in seen_dedup:
                        seen_dedup.add(key)
                        all_raw_jobs.append(job)
        except Exception as e:
            logger.error(f"🔴 Erreur WebSearcher: {e}")

        unique_jobs = []
        seen_urls = set()
        
        # Préparation finale et dédoublonnage par URL
        for idx, job in enumerate(all_raw_jobs):
            url = job.get("url", f"temp-{idx}")
            if url not in seen_urls:
                seen_urls.add(url)
                
                # S'assurer que les champs requis pour le front sont là (Safe Job)
                safe_job = {
                    "id": job.get("id", f"job-{idx}"),
                    "title": job.get("title", "Poste sans titre"),
                    "company": job.get("company", "Entreprise anonyme"),
                    "location": job.get("location", location),
                    "description": job.get("description", job.get("snippet", job.get("job_description", "Aucune description."))),
                    "url": job.get("url", "#"),
                    "source": job.get("source", "Web"),
                    "posted_date": job.get("posted_date", ""),
                    "salary": job.get("salary", ""),
                    "job_type": job.get("job_type", "Temps plein"),
                    "required_skills": job.get("required_skills", []),
                    "match_score": 0,
                    "match_justification": "En attente d'évaluation...",
                    "company_website": job.get("company_website", ""),
                    "apply_email": job.get("apply_email", ""),
                    "phone": job.get("phone", "")
                }
                unique_jobs.append(safe_job)
                
        # --- BATCH AI EVALUATION (Chunked) ---
        cv_profile = action_plan.get("cv_profile", {})
        if unique_jobs:
            logger.info(f"🧠 Évaluation de la pertinence pour {len(unique_jobs)} offres...")
            final_jobs = await self._evaluate_jobs_batch(unique_jobs, cv_profile)
        else:
            final_jobs = []
            
        # --- ENRICHISSEMENT FINAL (Seulement pour les gagnants) ---
        if final_jobs:
            logger.info(f"⚡ Enrichissement final pour les {len(final_jobs)} meilleures offres...")
            try:
                from tools.web_searcher import web_searcher
                enrich_tasks = []
                # On ne fait que l'enrichissement de base (scraping page), PAS d'OSINT DDG massif ici
                for j in final_jobs:
                    if j.get('source') != "Guichet Emplois":
                        enrich_tasks.append(web_searcher.enrich_job_details(j))
                
                if enrich_tasks:
                    import asyncio
                    # Timeout plus court pour pas bloquer
                    enriched_results = await asyncio.gather(*[asyncio.wait_for(t, timeout=10.0) for t in enrich_tasks], return_exceptions=True)
                    # Mise à jour
                    for i, res in enumerate(enriched_results):
                        if not isinstance(res, Exception) and res:
                            final_jobs[i].update(res)
            except Exception as e:
                logger.error(f"🔴 Erreur Enrichissement Final: {e}")
            
        # Limiter au nombre demandé
        final_jobs = final_jobs[:limit]
        logger.info(f"📨 Renvoi de {len(final_jobs)} offres pertinentes au Frontend.")
        
        return {
            "success": True,
            "total_jobs_found": len(final_jobs),
            "matched_jobs": final_jobs,
            "cv_profile": cv_profile,
            "search_criteria": {
                "keywords": keywords_list,
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
        """Évalue la compatibilité d'un lot d'offres en plusieurs sous-lots (chunks) pour plus de fiabilité."""
        if not jobs:
            return []
            
        if not cv_profile.get("target_roles") and not cv_profile.get("skills"):
            return jobs
            
        # Filtre de sécurité PRÉ-IA (Python)
        target_level = cv_profile.get("target_level", "junior")
        if target_level == "stage":
            rejection_keywords = ["senior", "principal", "staff", "lead", "sr.", "manager", "directeur", "director", "expert"]
            filtered_jobs = []
            for j in jobs:
                title_lower = j.get("title", "").lower()
                if any(kw in title_lower for kw in rejection_keywords) and "stage" not in title_lower and "intern" not in title_lower:
                    logger.warning(f"🚫 Filtre pré-IA: Rejet de '{j.get('title')}' (Senior pour Stage)")
                    continue
                filtered_jobs.append(j)
            jobs = filtered_jobs
            
        if not jobs:
            return []

        # ÉVALUATION PAR CHUNKS (Lots de 10 max pour garantir la qualité)
        chunk_size = 10
        all_evaluations = []
        
        for i in range(0, len(jobs), chunk_size):
            chunk = jobs[i:i + chunk_size]
            logger.info(f"🧠 Évaluation du lot intelligent {i//chunk_size + 1}/{(len(jobs)-1)//chunk_size + 1}...")
            
            prompt = f"""
            Tu es un recruteur expert en TECH. Évalue la compatibilité des offres suivantes par rapport au profil du candidat.
            
            PROFIL CANDIDAT:
            Rôles cibles: {cv_profile.get('target_roles', [])}
            Expérience: {cv_profile.get('experience_years', 0)} ans
            Compétences: {cv_profile.get('skills', [])}
            Localisation ciblée: {cv_profile.get('target_location', 'Non spécifiée')}
            Niveau cible: {cv_profile.get('target_level', 'Junior/Emploi')}
            
            OFFRES D'EMPLOIS (Le lot actuel):
            """
            
            for job in chunk:
                prompt += f"\n- ID: '{job.get('id')}' | Poste: '{job.get('title')}' | Ville/Pays: '{job.get('location')}' | Snippet: {job.get('description', '')[:150]}"
                
            prompt += """\n
            INSTRUCTIONS:
            Retourne un tableau JSON pur (sans markdown):
            [
                {"id": "id_de_loffre", "score": 85, "justification": "Max 10 mots sur pourquoi ça fit ou pas"}
            ]
            
            RÈGLES DE SCORING MÉCHANTES (Strictes):
            1. SCORE 0 si le domaine ne correspond pas. EX: Si l'utilisateur veut 'Développeur Logiciel', rejette les mécaniciens, les techniciens IT (support), les secrétaires, ou les commerciaux, MÊME s'ils utilisent 'des logiciels' (Excel, Word, CAO). Un Développeur CRÉE le logiciel, il ne l'utilise pas.
            2. SCORE 0 si la localisation (pays) ne correspond pas du tout.
            3. SCORE 0 si le niveau est Senior alors qu'on veut un Stage.
            4. SCORE 0 si le titre du poste est trop éloigné (ex: Comptable vs Développeur).
            5. Le score doit refléter la compatibilité réelle avec les COMPÉTENCES du CV (Skills).
            6. Sois très critique pour le 0, mais si le domaine est bon (Développement), donne un score honnête même s'il est bas (ex: 35%).
            """
            
            try:
                resp = await self.generate_response(prompt)
                import json, re
                clean_resp = resp.replace("```json", "").replace("```", "").strip()
                
                eval_chunk = None
                try:
                    parsed = json.loads(clean_resp)
                    if isinstance(parsed, list):
                        eval_chunk = parsed
                    elif isinstance(parsed, dict):
                        for v in parsed.values():
                            if isinstance(v, list):
                                eval_chunk = v
                                break
                except:
                    # Fallback Regex
                    match = re.search(r'\[.*\]', clean_resp, re.DOTALL)
                    if match:
                        eval_chunk = json.loads(match.group(0))
                
                if eval_chunk:
                    all_evaluations.extend(eval_chunk)
            except Exception as e:
                logger.error(f"Erreur chunk evaluation: {e}")
                
        # Application des résultats
        eval_map = {str(e.get("id")): e for e in all_evaluations if "id" in e}
        
        scored_jobs = []
        for job in jobs:
            job_id = str(job.get("id"))
            if job_id in eval_map:
                eval_data = eval_map[job_id]
                job["match_score"] = int(eval_data.get("score", 0))
                job["match_justification"] = eval_data.get("justification", "Évaluation IA effectuée.")
            
            # Seuil de filtrage ajusté à 30% selon souhait utilisateur
            if job.get("match_score", 0) >= 30:
                scored_jobs.append(job)
                
        return sorted(scored_jobs, key=lambda x: x.get("match_score", 0), reverse=True)
