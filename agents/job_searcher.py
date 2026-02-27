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
        Phase d'action : Coordonne les agents Hunter et Judge.
        """
        logger.info("🎬 Orchestrateur: Phase d'exécution du Swarm...")
        
        # 1. Traque (Hunting)
        from agents.hunter_agent import HunterAgent
        hunter = HunterAgent()
        await hunter.initialize()
        hunt_results = await hunter.act(await hunter.think(action_plan))
        raw_jobs = hunt_results.get("jobs", [])
        
        if not raw_jobs:
            logger.warning("📭 Aucun job trouvé par le Hunter.")
            return {
                "success": True, 
                "total_jobs_found": 0, 
                "matched_jobs": [], 
                "cv_profile": action_plan.get("cv_profile", {})
            }

        # 2. Jugement (Judging)
        from agents.judge_agent import JudgeAgent
        judge = JudgeAgent()
        await judge.initialize()
        
        # Passer la localisation cible au Judge pour le scoring
        cv_profile = action_plan.get("cv_profile", {})
        cv_profile["target_location"] = action_plan.get("criteria", {}).get("location", "Paris, France")
        
        judgment_task = {
            "jobs": raw_jobs,
            "cv_profile": cv_profile
        }
        judge_results = await judge.act(await judge.think(judgment_task))
        final_jobs = judge_results.get("evaluated_jobs", [])
        
        # 3. Finalisation : On garde toutes les offres qui ne sont pas un rejet absolu (score > 0)
        valid_final_jobs = [j for j in final_jobs if j.get("match_score", 0) > 0]
        
        limit = action_plan.get("limit", 10)
        # Si l'utilisateur veut "pousser au max", on renvoie jusqu'à 3x sa limite ou un plafond de 100
        display_limit = max(limit, min(100, limit * 3))
        top_jobs = valid_final_jobs[:display_limit]
        
        logger.info(f"📨 Orchestration terminée: {len(top_jobs)} offres pertinentes trouvées.")
        
        return {
            "success": True,
            "total_jobs_found": len(top_jobs),
            "matched_jobs": top_jobs,
            "cv_profile": action_plan.get("cv_profile", {}),
            "search_criteria": action_plan.get("criteria")
        }
