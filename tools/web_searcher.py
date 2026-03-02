"""Outil de recherche web robuste et asynchrone pour offres d'emploi."""
import aiohttp
import asyncio
from typing import List, Dict, Any
import re
from loguru import logger
from bs4 import BeautifulSoup
import ssl
import urllib.parse

# Mots-clés prioritaires pour emails RH / recrutement
HR_EMAIL_PATTERNS = [
    r"recrutement@", r"rh@", r"jobs@", r"careers@", r"emploi@",
    r"recruitment@", r"hr@", r"talent@", r"contact@", r"info@",
    r"carrieres@", r"emplois@", r"recrutement\.",
]

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
                    async with session.get(url, timeout=10) as response:
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
                async with session.get(url, timeout=10) as response:
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
        """
        Trouve le site officiel de l'entreprise et extrait les emails RH / contact.
        Utilise DuckDuckGo (AsyncDDGS) + scraping de la page pour maximiser la précision.
        """
        if not company_name or company_name.lower() in ("confidentiel", "anonyme", "incognito", "non spécifié"):
            return {"company_name": company_name, "site_url": "", "emails": [], "phone": ""}

        site_url = ""
        emails = []
        phone = ""

        try:
            results = []
            try:
                from duckduckgo_search import AsyncDDGS
                query = f'"{company_name}" site officiel'
                if location:
                    query += f" {location}"
                async with AsyncDDGS() as ddgs:
                    async for r in ddgs.text(query, max_results=5):
                        results.append(r)
                        if len(results) >= 5:
                            break
            except Exception as ddg_err:
                logger.debug(f"AsyncDDGS fallback: {ddg_err}")
                from duckduckgo_search import DDGS
                loop = asyncio.get_event_loop()
                def _sync_search():
                    with DDGS() as ddgs:
                        return list(ddgs.text(f'"{company_name}" site officiel', max_results=5))
                results = await loop.run_in_executor(None, _sync_search)

            for r in results:
                href = r.get("href", "")
                title = (r.get("title") or "").lower()
                if not href or not href.startswith("http"):
                    continue
                if any(skip in href for skip in ["linkedin.com", "facebook.com", "twitter.com", "instagram.com", "youtube.com", "wikipedia.org", "indeed.", "glassdoor.", "jobboom", "guichetemplois", "monster."]):
                    continue
                site_url = href.split("?")[0].rstrip("/")
                break

            if not site_url:
                return {"company_name": company_name, "site_url": "", "emails": [], "phone": ""}

            async with self.semaphore:
                async with aiohttp.ClientSession(headers=self.headers) as session:
                    try:
                        async with session.get(site_url, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                            if resp.status != 200:
                                return {"company_name": company_name, "site_url": site_url, "emails": [], "phone": ""}
                            html = await resp.text()
                            soup = BeautifulSoup(html, "html.parser")
                            text = soup.get_text(separator=" ", strip=True)
                            all_emails = re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)
                            seen = set()
                            for e in all_emails:
                                e_lower = e.lower()
                                if e_lower in seen:
                                    continue
                                seen.add(e_lower)
                                if any(re.search(p, e_lower) for p in HR_EMAIL_PATTERNS):
                                    emails.insert(0, e_lower)
                                elif "noreply" not in e_lower and "no-reply" not in e_lower and "mailer" not in e_lower:
                                    emails.append(e_lower)
                            emails = list(dict.fromkeys(emails))[:5]
                            phones = re.findall(r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{2,4}\)?[-.\s]?\d{2,4}[-.\s]?\d{2,4}[-.\s]?\d{0,4}", text)
                            if phones:
                                phone = phones[0].strip()[:20]
                    except Exception as e:
                        logger.debug(f"Enrich contact {company_name}: {e}")

            return {"company_name": company_name, "site_url": site_url, "emails": emails, "phone": phone}
        except Exception as e:
            logger.warning(f"find_official_website_and_contact ({company_name}): {e}")
            return {"company_name": company_name, "site_url": site_url or "", "emails": emails, "phone": phone}

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
