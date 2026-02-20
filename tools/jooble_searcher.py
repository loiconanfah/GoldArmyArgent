"""
Module pour la recherche d'emploi via l'API Jooble.
"""
import aiohttp
import json
from typing import List, Dict, Any
from loguru import logger
from datetime import datetime

class JoobleSearcher:
    """Client pour l'API Jooble."""
    
    BASE_URL = "https://jooble.org/api/"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.url = f"{self.BASE_URL}{self.api_key}"
        
    async def search_jobs(self, keywords: str, location: str, page: int = 1, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Recherche des offres sur Jooble.
        
        Args:
            keywords: Mots-clés de recherche
            location: Localisation
            page: Numéro de page (Jooble utilise un offset, mais on simplifie)
            limit: Nombre de résultats (max 20 souvent)
            
        Returns:
            Liste des offres standardisées
        """
        payload = {
            "keywords": keywords,
            "location": location,
            "page": page,
            "resultonpage": limit
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.url, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        jobs = data.get("jobs", [])
                        return self._normalize_jobs(jobs)
                    elif response.status == 401:
                        logger.error("❌ Erreur Jooble: Clé API invalide")
                        return []
                    else:
                        logger.error(f"❌ Erreur Jooble {response.status}: {await response.text()}")
                        return []
                        
        except Exception as e:
            logger.error(f"⚠️ Exception Jooble: {str(e)}")
            return []
            
    def _normalize_jobs(self, raw_jobs: List[Dict]) -> List[Dict]:
        """Convertit les résultats Jooble au format standard GoldArmy."""
        normalized = []
        
        for job in raw_jobs:
            try:
                # Jooble fields: title, location, snippet, salary, source, type, link, company, updated
                
                # Nettoyage du HTML dans le snippet
                snippet = job.get("snippet", "")
                snippet = snippet.replace("&nbsp;", " ").replace("<b>", "").replace("</b>", "")
                
                normalized_job = {
                    "id": f"jooble-{job.get('id', hash(job.get('link', '')))}",
                    "title": job.get("title", "Titre non spécifié"),
                    "company": job.get("company", "Confidentiel"),
                    "location": job.get("location", "Non spécifié"),
                    "description": snippet, # Description courte initale
                    "url": job.get("link"),
                    "source": "Jooble",
                    "posted_date": job.get("updated", datetime.now().isoformat()),
                    "salary": job.get("salary", "Non spécifié"),
                    "job_type": job.get("type", "Non spécifié"),
                    "scraped": False # Indique qu'on n'a pas encore le contenu complet
                }
                normalized.append(normalized_job)
                
            except Exception as e:
                logger.warning(f"⚠️ Erreur parsing job Jooble: {e}")
                continue
                
        return normalized

# Instance par défaut (sera configurée si clé présente)
jooble_searcher = None
