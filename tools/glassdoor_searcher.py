"""Outil de recherche d'emploi via l'API Glassdoor (RapidAPI)."""
import aiohttp
import asyncio
from typing import List, Dict, Any
import urllib.parse
from loguru import logger
from config.settings import settings

class GlassdoorSearcher:
    """Interface pour l'API Glassdoor Real-Time sur RapidAPI."""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or settings.rapidapi_key
        self.host = settings.glassdoor_api_host
        self.headers = {
            "x-rapidapi-key": self.api_key,
            "x-rapidapi-host": self.host
        }
        self.base_url = f"https://{self.host}"

    async def search_jobs(self, query: str, location: str = None, limit: int = 20) -> List[Dict[str, Any]]:
        """Recherche des offres d'emploi sur Glassdoor."""
        if not self.api_key:
            logger.error("❌ Clé RapidAPI manquante pour Glassdoor.")
            return []

        # Construction de l'URL
        params = {"query": query}
        if location:
            params["location"] = location
            
        url = f"{self.base_url}/jobs/search?{urllib.parse.urlencode(params)}"
        
        logger.info(f"📡 Glassdoor API: Recherche '{query}' à '{location}'")
        
        async with aiohttp.ClientSession(headers=self.headers) as session:
            try:
                async with session.get(url, timeout=15) as response:
                    if response.status == 200:
                        try:
                            data = await response.json()
                            logger.debug(f"Glassdoor API Data: {str(data)[:200]}...")
                            results = self._map_results(data, limit)
                            logger.info(f"🟢 Glassdoor a trouvé {len(results)} offres.")
                            return results
                        except Exception as e:
                            logger.error(f"❌ Erreur parsing JSON Glassdoor: {e}")
                            return []
                    else:
                        error_text = await response.text()
                        logger.error(f"🔴 Erreur Glassdoor API ({response.status}): {error_text}")
            except Exception as e:
                logger.error(f"🔴 Exception Glassdoor API: {e}")
        
        return []

    def _map_results(self, data: Any, limit: int) -> List[Dict[str, Any]]:
        """Normalise les résultats de Glassdoor au format standard."""
        jobs = []
        raw_jobs = []
        
        # Inspection de la structure
        if isinstance(data, dict):
            logger.debug(f"Keys in Glassdoor data: {list(data.keys())}")
            if "data" in data:
                inner_data = data["data"]
                if isinstance(inner_data, dict):
                    logger.debug(f"Keys in Glassdoor inner data: {list(inner_data.keys())}")
                    raw_jobs = inner_data.get("jobListings", inner_data.get("hits", inner_data.get("jobs", [])))
            else:
                raw_jobs = data.get("jobListings", data.get("hits", data.get("jobs", [])))
        elif isinstance(data, list):
            raw_jobs = data
            
        if not raw_jobs and isinstance(data, dict) and "data" in data:
            # Parfois le format est bizarre sur RapidAPI
            raw_jobs = data["data"] if isinstance(data["data"], list) else []

        for job in raw_jobs[:limit]:
            # Mapping flexible
            title = job.get('job_title') or job.get('title') or job.get('jobTitle') or "Sans titre"
            company = job.get('company_name') or job.get('company') or job.get('employerName') or "Inconnue"
            
            jobs.append({
                "id": f"gd-{job.get('job_id') or job.get('id') or 'unknown'}",
                "title": title,
                "company": company,
                "location": job.get("location") or job.get("jobLocation") or "N/A",
                "url": job.get("job_url") or job.get("url") or job.get("jobLink") or "",
                "source": "Glassdoor",
                "description": job.get("job_description") or job.get("snippet") or job.get("description", ""),
                "posted_date": job.get("posted_at") or job.get("posted_date") or "",
                "salary": job.get("salary_range") or job.get("salary") or "",
            })
            
        return jobs

# Instance globale
glassdoor_searcher = GlassdoorSearcher()
