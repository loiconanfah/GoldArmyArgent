"""Outil de recherche web robuste et asynchrone pour offres d'emploi."""
import aiohttp
import asyncio
from typing import List, Dict, Any
import re
from loguru import logger
from bs4 import BeautifulSoup
import ssl
import urllib.parse

class JobWebSearcher:
    """Recherche web spécialisée pour l'emploi (offres individuelles uniquement)."""
    
    def __init__(self):
        self.semaphore = asyncio.Semaphore(5) # Limiter à 5 requêtes simultanées
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
        }

    async def search_jobs(self, keywords: str, location: str = "Québec", job_type: str = "stage", max_results: int = 20) -> List[Dict[str, Any]]:
        """Recherche des offres d'emploi individuelles."""
        logger.info(f"🌐 Recherche Web Parallèle: '{keywords}' à '{location}'")
        
        tasks = [
            self._search_jobbank(keywords, location, max_results),
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        all_jobs = []
        for res in results:
            if isinstance(res, list): all_jobs.extend(res)
            
        unique_jobs = []
        seen_urls = set()
        for job in all_jobs:
            url = job.get("url")
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_jobs.append(job)
                
        unique_jobs = unique_jobs[:max_results]
        
        # Enrichissement délibérément limité pour éviter les bans
        enrich_tasks = [self.enrich_job_details(job) for job in unique_jobs]
        enriched_jobs = await asyncio.gather(*enrich_tasks, return_exceptions=True)
        
        return [j for j in enriched_jobs if isinstance(j, dict)]

    async def enrich_job_details(self, job: Dict[str, Any]) -> Dict[str, Any]:
        """Enrichit les détails d'une offre d'emploi (Non-Blocking)."""
        url = job.get('url', '')
        if not url or 'jobbank.gc.ca' in url: # Déjà riche
            return job
            
        async with self.semaphore:
            try:
                # SSL False pour éviter les erreurs de certificat sur certains sites
                async with aiohttp.ClientSession(headers=self.headers) as session:
                    async with session.get(url, timeout=10, ssl=False) as response:
                        if response.status == 200:
                            html = await response.text()
                            soup = BeautifulSoup(html, 'html.parser')
                            return self._scrape_generic_details(soup, job)
            except Exception:
                pass
        return job

    def _scrape_generic_details(self, soup: BeautifulSoup, job: Dict[str, Any]) -> Dict[str, Any]:
        """Extrait les infos de base sans faire d'OSINT."""
        try:
            text = soup.get_text(separator=' ', strip=True)
            emails = re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', text)
            if emails:
                job['apply_email'] = emails[0].lower()
            job['scraped'] = True
        except:
            pass
        return job

    async def _search_jobbank(self, keywords: str, location: str, max_results: int) -> List[Dict[str, Any]]:
        """Scrape Job Bank de manière asynchrone."""
        base_url = "https://www.jobbank.gc.ca/jobsearch/jobsearch"
        params = {"searchstring": keywords, "locationstring": location, "sort": "M"}
        
        # Correction encodage URL
        query_string = urllib.parse.urlencode(params)
        url = f"{base_url}?{query_string}"
        
        async with aiohttp.ClientSession(headers=self.headers) as session:
            try:
                async with session.get(url, timeout=10, ssl=False) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        articles = soup.find_all('article')
                        jobs = []
                        for i, article in enumerate(articles[:max_results]):
                            link = article.find('a', class_='resultJobItem')
                            if not link: continue
                            
                            title_tag = article.find(class_='noctitle')
                            business_tag = article.find(class_='business')
                            location_tag = article.find(class_='location')
                            
                            jobs.append({
                                "id": f"jb-{i}",
                                "title": title_tag.get_text(strip=True) if title_tag else "Titre inconnu",
                                "company": business_tag.get_text(strip=True) if business_tag else "Confidentiel",
                                "location": location_tag.get_text(strip=True) if location_tag else location,
                                "url": f"https://www.jobbank.gc.ca{link.get('href')}",
                                "source": "Guichet Emplois"
                            })
                        return jobs
            except Exception as e:
                logger.error(f"❌ Erreur JobBank Async: {e}")
        return []

    async def find_official_website_and_contact(self, company_name: str, location: str = "") -> Dict[str, Any]:
        """Version simplifiée sans DuckDuckGo pour éviter les hangs."""
        return {"company_name": company_name, "site_url": "", "emails": [], "phone": ""}

    def _generate_fallback_links(self, keywords: str, location: str) -> List[Dict[str, Any]]:
        """Génère des liens de recherche directs."""
        k_enc = urllib.parse.quote_plus(keywords)
        l_enc = urllib.parse.quote_plus(location)
        
        return [
            {
                "id": "search-guichet",
                "title": f"Guichet Emplois: {keywords}",
                "company": "Gouvernement du Canada",
                "location": "Non spécifié",
                "url": f"https://www.guichetemplois.gc.ca/jobsearch/jobsearch?searchstring={k_enc}&locationstring={l_enc}",
                "source": "Search Link",
                "match_score": 50
            }
        ]

# Instance globale unique
web_searcher = JobWebSearcher()
