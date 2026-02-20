"""
Module pour la recherche d'emploi via l'API JSearch (RapidAPI).
"""
import aiohttp
import json
import os
from typing import List, Dict, Any
from loguru import logger
from datetime import datetime

class JSearchSearcher:
    """Client pour l'API JSearch via RapidAPI."""
    
    BASE_URL = "https://jsearch.p.rapidapi.com/search"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.host = os.getenv("RAPIDAPI_HOST", "jsearch.p.rapidapi.com")
        
    async def search_jobs(self, query: str, location: str = "Canada", page: int = 1, num_pages: int = 1) -> List[Dict[str, Any]]:
        """
        Recherche des offres sur JSearch.
        
        Args:
            query: Mots-clés de recherche (ex: "Python developer")
            location: Localisation (sera concaténée à la query si pertinente)
            page: Numéro de page
            num_pages: Nombre de pages à récupérer
            
        Returns:
            Liste des offres standardisées
        """
        # Construction de la query composée
        full_query = f"{query} in {location}"
        
        headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": self.host
        }
        
        params = {
            "query": full_query,
            "page": str(page),
            "num_pages": str(num_pages),
            "country": "ca", # Focus Canada pour ce projet, ou 'us' par défaut
            "date_posted": "month" # Offres récentes
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.BASE_URL, headers=headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        jobs = data.get("data", [])
                        return self._normalize_jobs(jobs)
                    elif response.status == 429:
                        logger.warning("⚠️ Limite API JSearch atteinte (429)")
                        return []
                    elif response.status == 403: # Clé invalide souvent
                        logger.error("❌ Erreur JSearch: Clé API invalide ou non autorisée")
                        return []
                    else:
                        logger.error(f"❌ Erreur JSearch {response.status}: {await response.text()}")
                        return []
                        
        except Exception as e:
            logger.error(f"⚠️ Exception JSearch: {str(e)}")
            return []
            
    def _normalize_jobs(self, raw_jobs: List[Dict]) -> List[Dict]:
        """Convertit les résultats JSearch au format standard GoldArmy."""
        normalized = []
        
        if not raw_jobs:
            return []
            
        for job in raw_jobs:
            try:
                # JSearch fields: job_title, employer_name, job_city, job_country, job_description, job_apply_link
                
                normalized_job = {
                    "id": f"jsearch-{job.get('job_id', hash(job.get('job_apply_link', '')))}",
                    "title": job.get("job_title", "Titre non spécifié"),
                    "company": job.get("employer_name", "Confidentiel"),
                    "location": f"{job.get('job_city', '')}, {job.get('job_country', '')}".strip(', '),
                    "description": job.get("job_description", ""),
                    "url": job.get("job_apply_link", job.get("job_google_link")),
                    "source": "JSearch",
                    "posted_date": job.get("job_posted_at_datetime_utc", datetime.now().isoformat()),
                    "salary": self._format_salary(job),
                    "job_type": job.get("job_employment_type", "Non spécifié"),
                    "required_skills": job.get("job_highlights", {}).get("Qualifications", []),
                    "scraped": True # JSearch donne souvent une description complète
                }
                normalized.append(normalized_job)
                
            except Exception as e:
                logger.warning(f"⚠️ Erreur parsing job JSearch: {e}")
                continue
                
        return normalized

    def _format_salary(self, job: Dict) -> str:
        """Formate le salaire si disponible."""
        min_sal = job.get("job_min_salary")
        max_sal = job.get("job_max_salary")
        currency = job.get("job_salary_currency", "CAD")
        period = job.get("job_salary_period", "year")
        
        if min_sal and max_sal:
            return f"{min_sal}-{max_sal} {currency}/{period}"
        return "Non spécifié"
