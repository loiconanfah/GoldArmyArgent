"""Outil de recherche d'emploi via l'API FindWork.dev."""
import aiohttp
from typing import List, Dict, Any
from loguru import logger
import urllib.parse
from config.settings import settings

class FindWorkSearcher:
    """Client pour l'API FindWork.dev."""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or getattr(settings, "findwork_api_key", None)
        self.base_url = "https://findwork.dev/api/jobs/"
        
    async def search_jobs(self, keywords: str, location: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Recherche des offres sur FindWork."""
        if not self.api_key:
            logger.warning("Clé API FindWork non configurée.")
            return []
            
        headers = {
            "Authorization": f"Token {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Préparation des paramètres
        # FindWork utilise 'search' pour le texte et 'location' pour la ville
        search_query = urllib.parse.quote_plus(keywords)
        location_query = urllib.parse.quote_plus(location)
        
        # Trier par pertinence si possible, sinon laisser le tri par date par défaut
        url = f"{self.base_url}?search={search_query}&location={location_query}&sort_by=relevance"
        
        jobs = []
        try:
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as response:
                    if response.status != 200:
                        logger.error(f"FindWork API Error {response.status}: {await response.text()}")
                        return []
                        
                    try:
                        data = await response.json()
                        results = data.get("results", [])
                        
                        for i, item in enumerate(results[:limit]):
                            jobs.append({
                                "id": f"findwork-{item.get('id', i)}",
                                "title": item.get("role", "Titre Non Spécifié"),
                                "company": item.get("company_name", "Entreprise Anonyme"),
                                "location": item.get("location", location),
                                "url": item.get("url", ""), # Assuming 'url' field exists or we link to the platform
                                "description": (item.get("text", "") or item.get("description", "") or "").strip() or f"Poste : {item.get('role', 'Offre')}. Entreprise : {item.get('company_name', '')}. Consultez le lien pour la description complète.",
                                "source": "FindWork.dev",
                                "match_score": 0,
                                "raw_contract_type": item.get("employment_type", ""), # To help local filtering
                            })
                            
                    except Exception as e:
                        logger.error(f"❌ Erreur parsing JSON FindWork: {e}")
                        return []
                        
            logger.info(f"🌐 FindWork: {len(jobs)} offres trouvées pour '{keywords}' à '{location}'")
            return jobs
            
        except Exception as e:
            logger.error(f"Erreur lors de la recherche FindWork: {e}")
            return []
