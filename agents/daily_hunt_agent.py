"""
DailyHuntAgent — Chasseur d'offres quotidien économe en tokens.
Scanne massivement sans IA, puis filtre et utilise l'IA uniquement sur le top results.
"""
from typing import Any, Dict, List
import asyncio
from loguru import logger
from agents.job_searcher import JobSearchAgent
from agents.hunter_agent import HunterAgent
from agents.judge_agent import JudgeAgent

class DailyHuntAgent(JobSearchAgent):
    def __init__(self, **kwargs):
        kwargs.setdefault("agent_type", "daily_hunt")
        kwargs.setdefault("name", "DailyHunter")
        super().__init__(**kwargs)

    async def run_daily_scan(self, user_id: str, query: str, location: str, cv_text: str = None) -> List[Dict[str, Any]]:
        """Exécute la chasse quotidienne optimisée."""
        logger.info(f"[DailyHunt] Démarrage du scan pour {user_id} (Query: {query})")
        
        # 1. Recherche massive via Hunter (Blind Scan)
        hunter = HunterAgent()
        await hunter.initialize()
        
        # On définit des critères larges basés sur la query
        search_plan = {
            "criteria": {
                "keywords_list": [query], # On reste simple pour économiser
                "location": location or "Montreal, QC, Canada",
                "job_type": "emploi",
                "apis": ["jooble", "jsearch", "findwork"] # APIs rapides
            },
            "limit": 100 # On prend beaucoup de résultats bruts
        }
        
        hunt_results = await hunter.act(search_plan)
        raw_jobs = hunt_results.get("jobs", [])
        
        if not raw_jobs:
            logger.warning("[DailyHunt] Aucun résultat trouvé lors du scan brut.")
            return []

        # 2. Filtrage Local (Anti-Token-Waste)
        # On score localement sans IA pour dégrossir
        scored_jobs = self._local_scoring(raw_jobs, query)
        
        # On ne garde que le top 15 pour l'IA
        top_candidates = scored_jobs[:15]
        
        # 3. Jugement IA (Le "Final 5")
        judge = JudgeAgent()
        await judge.initialize()
        
        # On prépare un profil minimal si le CV est absent
        cv_profile = {"search_query": query, "target_location": location}
        
        # Appel IA uniquement sur le top 15
        logger.info(f"[DailyHunt] Envoi du top {len(top_candidates)} à l'IA pour évaluation finale.")
        judged_res = await judge.act({"jobs": top_candidates, "cv_profile": cv_profile})
        final_jobs = judged_res.get("evaluated_jobs", [])
        
        # On retourne les 5 meilleurs
        return final_jobs[:5]

    def _local_scoring(self, jobs: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
        """Score les offres par mots-clés (sans IA) pour éliminer le bruit."""
        query_words = set(query.lower().split())
        
        for job in jobs:
            score = 0
            title = job.get("title", "").lower()
            company = job.get("company", "").lower()
            
            # Bonus si le mot clé est dans le titre (très important)
            for word in query_words:
                if word in title:
                    score += 40
                if word in job.get("description", "").lower():
                    score += 10
            
            job["local_score"] = score
            
        # Tri par score local
        return sorted(jobs, key=lambda x: x.get("local_score", 0), reverse=True)
