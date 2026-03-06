"""Agent Orchestrateur pour la recherche d'emploi.
Coordonne un essaim (swarm) d'agents spécialisés pour le profiling, la traque et le jugement.
"""
from typing import Any, Dict, List
import asyncio
from loguru import logger

from core.agent_base import BaseAgent
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
        
        # Le ProfileAgent extrait le profil et prépare les mots-clés
        analysis_task = {
            "cv_text": cv_text,
            "query": task.get("query", ""),
            "location": task.get("location", "")
        }
        
        profile_data = await profiler.act(await profiler.think(analysis_task))
        
        explicit_location = task.get("location", "")
        # Normalisation obligatoire pour éviter les ambiguïtés (ex: Paris, TX)
        base_location = self._normalize_location(explicit_location)
        
        action_plan = {
            "task_id": task.get("id", "unknown"),
            "criteria": {
                "keywords_list": profile_data.get("keywords_list", [task.get("query")]),
                "exclude_list": profile_data.get("exclude_list", []),
                "location": base_location,
                "job_type": profile_data.get("job_type", "emploi")
            },
            "cv_profile": profile_data.get("cv_profile", {}),
            "limit": task.get("nb_results") or task.get("limit") or 10
        }
        
        logger.info(f"✅ Orchestration prête: {len(action_plan['criteria']['keywords_list'])} variations pour {base_location}")
        return action_plan

    async def act(self, action_plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Phase d'action : Coordonne les agents Hunter et Judge par vagues optimisées.
        """
        logger.info("🎬 Orchestrateur: Phase d'exécution du Swarm (Waves Strategy)...")
        
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
        cv_profile["target_location"] = criteria_loc.get("location", "Paris, France")
        cv_profile["target_job_type"] = criteria_loc.get("job_type", "emploi")
        
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

        # Tri final par pertinence
        unique_final.sort(key=lambda x: x.get("match_score", 0), reverse=True)
        
        # Limite finale (Max 200)
        top_jobs = unique_final[:200]
        
        # --- ENRICHISSEMENT FINAL (Détails pour les meilleurs matchs) ---
        # On ne le fait que pour les 15 premiers pour la vitesse
        if top_jobs:
            logger.info(f"✨ Enrichissement des {min(15, len(top_jobs))} meilleurs résultats...")
            top_jobs = await hunter.enrich_jobs(top_jobs, limit=15)
        
        logger.success(f"💎 Sniper Swarm terminé : {len(top_jobs)} offres pertinentes sur {len(unique_final)} trouvées.")

        
        return {
            "success": True,
            "total_jobs_found": len(top_jobs),
            "matched_jobs": top_jobs,
            "cv_profile": cv_profile,
            "search_criteria": action_plan.get("criteria")
        }


