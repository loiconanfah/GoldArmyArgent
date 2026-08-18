"""Agent Orchestrateur pour la recherche d'emploi.
Coordonne un essaim (swarm) d'agents spécialisés pour le profiling, la traque et le jugement.
"""
from typing import Any, Dict, List
import asyncio
from loguru import logger

from core.agent_base import BaseAgent
from core.cache import cache
from config.settings import settings


class JobSearchAgent(BaseAgent):
    """Orchestrateur central du Swarm Sniper."""
    
    def __init__(self, **kwargs):
        """Initialise l'orchestrateur."""
        kwargs.setdefault("agent_type", "job_searcher")
        kwargs.setdefault("name", "SniperOrchestrator")
        kwargs.setdefault("temperature", 0.1)
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
        "vancouver": "Vancouver, BC, Canada",
        "calgary": "Calgary, AB, Canada",
        # France
        "france": "France",
        "paris": "Paris, France",
        "lyon": "Lyon, France",
        "marseille": "Marseille, France",
        "toulouse": "Toulouse, France",
        "bordeaux": "Bordeaux, France",
        "nantes": "Nantes, France",
        "lille": "Lille, France",
        "nice": "Nice, France",
        "rennes": "Rennes, France",
        "strasbourg": "Strasbourg, France",
        "grenoble": "Grenoble, France",
        "montpellier": "Montpellier, France",
        # USA  
        "usa": "United States",
        "us": "United States",
        "america": "United States",
        "etats-unis": "United States",
        "california": "California, USA",
        "californie": "California, USA",
        "califormie": "California, USA",  # typo courant
        "califormia": "California, USA",  # typo courant
        "new york": "New York, USA",
        "new-york": "New York, USA",
        "texas": "Texas, USA",
        "florida": "Florida, USA",
        "washington": "Washington, USA",
        "seattle": "Seattle, WA, USA",
        "boston": "Boston, MA, USA",
        "chicago": "Chicago, IL, USA",
        "los angeles": "Los Angeles, CA, USA",
        "san francisco": "San Francisco, CA, USA",
        "silicon valley": "Silicon Valley, CA, USA",
        # Autres pays
        "belgique": "Belgique",
        "bruxelles": "Bruxelles, Belgique",
        "suisse": "Suisse",
        "zurich": "Zurich, Suisse",
        "geneve": "Genève, Suisse",
        "uk": "United Kingdom",
        "london": "London, UK",
        "maroc": "Maroc",
        "luxembourg": "Luxembourg",
        "espagne": "Spain",
        "madrid": "Madrid, Spain",
        "barcelona": "Barcelona, Spain",
        "allemagne": "Germany",
        "berlin": "Berlin, Germany",
        # Cameroun
        "cameroun": "Cameroun",
        "cameroon": "Cameroun",
        "yaoundé": "Yaoundé, Cameroun",
        "yaounde": "Yaoundé, Cameroun",
        "douala": "Douala, Cameroun",
        "garoua": "Garoua, Cameroun",
        "bafoussam": "Bafoussam, Cameroun",
    }

    def _normalize_location(self, loc: str) -> str:
        """Normalise une localisation avec correction de fautes courantes."""
        if not loc:
            return "Montreal, QC, Canada"
        # Nettoyage et correction de fautes
        clean = loc.lower().strip()
        clean = clean.replace("califormie", "california").replace("californie", "california")
        clean = clean.replace("etats-unis", "usa").replace("united-states", "usa")
        normalized = self.LOCATION_MAP.get(clean)
        if normalized:
            return normalized
        # Si le terme original (sans corrections) est dans la map
        original = self.LOCATION_MAP.get(loc.lower().strip())
        if original:
            return original
        return loc

    async def think(self, task: Dict[str, Any], cv_text: str = None) -> Dict[str, Any]:
        """
        Phase de réflexion : Analyse le besoin et le profil via le ProfileAgent.
        """
        logger.info("🧠 Orchestrateur: Phase de planification...")
        from agents.profile_agent import ProfileAgent
        profiler = ProfileAgent()
        await profiler.initialize()
        
        # BUG FIX: Use cv_text from the task dict if the parameter is not provided
        resolved_cv_text = cv_text or task.get("cv_text") or None
        raw_query = task.get("query", "")

        # Le ProfileAgent extrait le profil et prépare les mots-clés
        analysis_task = {
            "cv_text": resolved_cv_text,
            "query": raw_query,
            "location": task.get("location", "")
        }
        
        profile_data = await profiler.act(await profiler.think(analysis_task))
        
        explicit_location = task.get("location", "")
        # Normalisation obligatoire pour éviter les ambiguïtés (ex: Paris, TX)
        base_location = self._normalize_location(explicit_location)

        # BUG FIX: The user's explicit query MUST anchor the search.
        # If the LLM-generated keywords don't contain the query's key term,
        # prepend it to avoid the CV profile hijacking the search intent.
        generated_keywords = profile_data.get("keywords_list", [raw_query])
        query_lower = raw_query.lower().strip()
        # Check if any generated keyword contains the main query term
        query_anchor = raw_query.split()[0].lower() if raw_query.split() else ""
        has_query_anchor = any(query_anchor in kw.lower() for kw in generated_keywords) if query_anchor else True
        if not has_query_anchor and raw_query:
            # The CV profile has overridden the query intent — fix by prepending the raw query
            logger.warning(f"⚠️ Keywords bias detected! Query '{raw_query}' not in {generated_keywords}. Anchoring to user query.")
            generated_keywords = [raw_query] + generated_keywords[:4]  # Raw query first, limit to 5 total
        
        action_plan = {
            "task_id": task.get("id", "unknown"),
            "query": raw_query,
            "criteria": {
                "keywords_list": generated_keywords,
                "exclude_list": profile_data.get("exclude_list", []),
                "location": base_location,
                "job_type": profile_data.get("job_type", "emploi")
            },
            "cv_profile": profile_data.get("cv_profile", {}),
            "limit": task.get("nb_results") or task.get("limit") or 10,
            # Filtres de source (ex: ["linkedin"], ["direct"], ["indeed","direct"]…)
            "sources": [s.lower() for s in (task.get("sources") or []) if s],
        }
        
        logger.info(f"✅ Orchestration prête: {len(action_plan['criteria']['keywords_list'])} variations pour {base_location}")
        logger.info(f"🔑 Keywords finaux: {action_plan['criteria']['keywords_list']}")
        return action_plan

    async def act(self, action_plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Phase d'action : Coordonne les agents Hunter et Judge par vagues optimisées.
        Cache Redis : si la même recherche (keywords + location) a été faite dans les 3h,
        on retourne le résultat mis en cache sans rappeler les APIs.
        """
        logger.info("Orchestrateur: Phase d'execution du Swarm (Waves Strategy)...")

        # --- CACHE CHECK ---
        criteria = action_plan.get("criteria", {})
        # BUG FIX: Include the raw user query in the cache key so that
        # "préposé" and "développeur" NEVER share a cached result.
        raw_query = action_plan.get("query", "")
        cache_key = cache.make_key(
            raw_query,
            "|".join(sorted(criteria.get("keywords_list", []))),
            criteria.get("location", ""),
            criteria.get("job_type", "emploi"),
            "src:" + "|".join(sorted(action_plan.get("sources", []))),
        )
        cached = await cache.get(cache_key)
        if cached:
            logger.info(f"Cache HIT — retour instantane de {len(cached.get('matched_jobs', []))} offres")
            return cached
        
        all_apis = action_plan.get("criteria", {}).get("apis", [])
        # Vague 1 : APIs Ultra-Rapides (Jooble, JSearch, Findwork, Emploi.cm, etc.)
        wave_1_apis = [api for api in all_apis if api in ["jooble", "jsearch", "findwork", "gov", "emploi_cm"]]
        # Vague 2 : APIs Profondes ou plus lentes
        wave_2_apis = [api for api in all_apis if api not in wave_1_apis]

        from agents.hunter_agent import HunterAgent
        from agents.judge_agent import JudgeAgent
        hunter = HunterAgent()
        judge = JudgeAgent()
        await asyncio.gather(hunter.initialize(), judge.initialize())

        # --- VAGUE 1 : TRAQUE RAPIDE ---
        logger.info(f"🌊 VAGUE 1 : {wave_1_apis}")
        plan_v1 = action_plan.copy()
        plan_v1["criteria"] = action_plan["criteria"].copy()
        plan_v1["criteria"]["apis"] = wave_1_apis
        
        # On attend la vague 1 car elle est la base du premier feedback rapide
        hunt_v1 = await hunter.act(await hunter.think(plan_v1))
        jobs_v1 = hunt_v1.get("jobs", [])
        
        cv_profile = action_plan.get("cv_profile", {})
        criteria_loc = action_plan.get("criteria", {})
        cv_profile["target_location"] = criteria_loc.get("location", "Montreal, QC, Canada")  # BUG FIX: was hardcoded "Paris, France"
        cv_profile["target_job_type"] = criteria_loc.get("job_type", "emploi")
        cv_profile["search_query"] = action_plan.get("query", "")
        
        # --- PARALLÉLISME MASSIF : JUDGE 1 + HUNTER 2 ---
        logger.info("⚡ Lancement concurrent du Jugement Vague 1 et de la Traque Vague 2...")
        
        async def run_judge_v1():
            if not jobs_v1: return []
            res = await judge.act({"jobs": jobs_v1, "cv_profile": cv_profile})
            return res.get("evaluated_jobs", [])

        async def run_hunt_v2():
            if not wave_2_apis: return []
            plan_v2 = action_plan.copy()
            plan_v2["criteria"] = action_plan["criteria"].copy()
            plan_v2["criteria"]["apis"] = wave_2_apis
            hunt = await hunter.act(await hunter.think(plan_v2))
            return hunt.get("jobs", [])

        # On lance les deux en même temps
        judged_v1_task = asyncio.create_task(run_judge_v1())
        hunt_v2_task = asyncio.create_task(run_hunt_v2())
        
        # On attend que les deux soient prêts
        judged_v1, jobs_v2 = await asyncio.gather(judged_v1_task, hunt_v2_task)

        # --- JUGEMENT VAGUE 2 ---
        judged_v2 = []
        if jobs_v2:
            logger.info("⚖️ Jugement Vague 2 en cours...")
            res_v2 = await judge.act({"jobs": jobs_v2, "cv_profile": cv_profile})
            judged_v2 = res_v2.get("evaluated_jobs", [])

        # Fusion et Dédoublonnage final (pas de post-filtre type contrat : le Judge a déjà scoré)
        all_results = judged_v1 + judged_v2
        unique_final = []
        seen = set()
        for j in all_results:
            if j.get("match_score", 0) <= 0:
                continue
            key = f"{j.get('title')}-{j.get('company')}".lower()
            if key not in seen:
                seen.add(key)
                unique_final.append(j)

        # --- SOURCE : étiquette chaque offre (linkedin/indeed/direct/…) ---
        from core.ats_harvester import harvest_companies, detect_source
        for j in unique_final:
            if not j.get("source"):
                j["source"] = detect_source(j.get("url") or j.get("apply_url") or j.get("link") or "")

        # --- DIRECT-TO-COMPANY : offres récupérées directement sur les ATS des
        # entreprises repérées (offres souvent absentes des plateformes). ---
        sources_filter = [s.lower() for s in (action_plan.get("sources") or []) if s]
        want_direct = (not sources_filter) or ("direct" in sources_filter)
        if want_direct:
            try:
                top_companies = []
                for j in sorted(unique_final, key=lambda x: x.get("match_score", 0), reverse=True):
                    c = (j.get("company") or "").strip()
                    if c and c.lower() not in [x.lower() for x in top_companies]:
                        top_companies.append(c)
                    if len(top_companies) >= 10:
                        break
                kw_list = list(criteria.get("keywords_list", [])) + [raw_query]
                direct_jobs = await asyncio.wait_for(
                    harvest_companies(top_companies, keywords=kw_list, location=criteria.get("location")),
                    timeout=10.0,
                )
                kwn = [k.lower() for k in kw_list if k]
                for dj in direct_jobs:
                    blob = f"{dj.get('title','')} {dj.get('description','')}".lower()
                    hits = sum(1 for k in kwn if k and k in blob)
                    dj["match_score"] = min(100, 55 + hits * 12)  # base élevée : offre à la source
                    dj["source"] = "direct"
                    key = f"{dj.get('title')}-{dj.get('company')}".lower()
                    if key not in seen:
                        seen.add(key)
                        unique_final.append(dj)
                logger.success(f"🏢 Direct-to-company : {len(direct_jobs)} offres ATS ajoutées")
            except asyncio.TimeoutError:
                logger.warning("[Sniper] Harvest ATS interrompu (budget temps dépassé)")
            except Exception as e:
                logger.warning(f"[Sniper] Harvest ATS ignoré: {e}")

        # --- FILTRES DE SOURCE (ex: uniquement LinkedIn, ou uniquement direct) ---
        if sources_filter:
            unique_final = [j for j in unique_final if (j.get("source") or "other").lower() in sources_filter]
            logger.info(f"🔎 Filtre sources={sources_filter} → {len(unique_final)} offres")

        # Tri final par pertinence
        unique_final.sort(key=lambda x: x.get("match_score", 0), reverse=True)
        
        # Limite finale : respecte nb_results demandé par l'utilisateur (défaut 50)
        target_limit = min(500, action_plan.get("limit") or 50)
        top_jobs = unique_final[:target_limit]
        
        # --- ENRICHISSEMENT FINAL (Détails pour les meilleurs matchs) ---
        if top_jobs:
            logger.info(f"✨ Enrichissement des descriptions pour les {min(25, len(top_jobs))} meilleurs résultats...")
            top_jobs = await hunter.enrich_jobs(top_jobs, limit=25)
        
        logger.success(f"💎 Sniper Swarm terminé : {len(top_jobs)} offres pertinentes sur {len(unique_final)} trouvées.")

        
        result = {
            "success": True,
            "total_jobs_found": len(top_jobs),
            "matched_jobs": top_jobs,
            "cv_profile": cv_profile,
            "search_criteria": action_plan.get("criteria")
        }

        # --- CACHE SET (TTL 3h) ---
        if top_jobs:
            await cache.set(cache_key, result, ttl=10800)
            logger.info(f"Resultats en cache (3h) — {len(top_jobs)} offres")

        return result



