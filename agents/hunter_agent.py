"""Agent Hunter spécialisé dans la traque d'opportunités sur les APIs."""
import asyncio
from typing import List, Dict, Any
from loguru import logger
from core.agent_base import BaseAgent
from config.settings import settings

class HunterAgent(BaseAgent):
    """Agent chargé de requêter les APIs de recherche d'emploi en parallèle."""
    
    def __init__(self, **kwargs):
        kwargs.setdefault("agent_type", "hunter")
        kwargs.setdefault("name", "Hunter")
        super().__init__(**kwargs)

    async def think(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Prépare la stratégie de recherche (APIs à utiliser, mots-clés)."""
        criteria = task.get("criteria", {})
        keywords_list = criteria.get("keywords_list", [])
        location = criteria.get("location", "Paris, France")
        
        # Sélection des APIs basées sur la localisation
        apis_to_use = ["jooble", "jsearch"]
        if "france" in location.lower() or "paris" in location.lower():
            apis_to_use.append("glassdoor")
            
        return {
            "keywords": keywords_list,
            "location": location,
            "apis": apis_to_use,
            "limit": task.get("limit", 10)
        }

    async def act(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Exécute les recherches en parallèle sur toutes les APIs sélectionnées."""
        keywords = plan.get("keywords", [])
        location = plan.get("location", "")
        apis = plan.get("apis", [])
        limit = plan.get("limit", 10)
        
        all_jobs = []
        tasks = []
        
        logger.info(f"🏹 Hunter lance la traque sur {len(apis)} sources pour {location}")
        logger.info(f"📝 Mots-clés: {keywords}")

        # On lance une tâche par API et par mot-clé (ou groupe)
        for kw in keywords:
            if "jooble" in apis and settings.jooble_api_key:
                logger.debug(f"Calling Jooble for: {kw}")
                tasks.append(self._search_jooble(kw, location, limit))
            if "jsearch" in apis and settings.rapidapi_key:
                logger.debug(f"Calling JSearch for: {kw}")
                tasks.append(self._search_jsearch(kw, location, limit))
            if "glassdoor" in apis and settings.rapidapi_key:
                logger.debug(f"Calling Glassdoor for: {kw}")
                tasks.append(self._search_glassdoor(kw, location, limit))

        if not tasks:
            logger.warning("⚠️ Aucune tâche de recherche lancée (Clés API manquantes ?)")
            return {"success": False, "jobs": []}

        # Exécution parallèle
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for res in results:
            if isinstance(res, list):
                logger.info(f"✅ Lot de {len(res)} jobs reçu.")
                all_jobs.extend(res)
            elif isinstance(res, Exception):
                logger.error(f"🔴 Erreur Hunter durant une recherche: {res}")

        # Dédoublonnage sommaire par URL/Titre
        unique_jobs = []
        seen = set()
        for job in all_jobs:
            key = f"{job.get('title')}-{job.get('company')}".lower()
            if key not in seen:
                seen.add(key)
                unique_jobs.append(job)

        logger.info(f"🎯 Hunter a ramené {len(unique_jobs)} offres brutes.")
        return {"success": True, "jobs": unique_jobs}

    async def _search_jooble(self, kw, loc, limit):
        try:
            from tools.jooble_searcher import JoobleSearcher
            searcher = JoobleSearcher(api_key=settings.jooble_api_key)
            return await searcher.search_jobs(keywords=kw, location=loc, limit=limit)
        except Exception as e:
            logger.error(f"Jooble Error: {e}")
            return []

    async def _search_jsearch(self, kw, loc, limit):
        try:
            from tools.jsearch_searcher import JSearchSearcher
            searcher = JSearchSearcher(api_key=settings.rapidapi_key)
            return await searcher.search_jobs(query=f"{kw} in {loc}", limit=limit)
        except Exception as e:
            logger.error(f"JSearch Error: {e}")
            return []
            
    async def _search_glassdoor(self, kw, loc, limit):
        try:
            from tools.glassdoor_searcher import GlassdoorSearcher
            searcher = GlassdoorSearcher(api_key=settings.rapidapi_key)
            return await searcher.search_jobs(query=kw, location=loc, limit=limit)
        except Exception as e:
            logger.error(f"Glassdoor Error: {e}")
            return []
