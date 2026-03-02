"""Outil de recherche d'emplois LinkedIn Jobs (public, sans authentification requise).
Cible directement l'API publique de LinkedIn Jobs pour retrouver des offres.
"""
import aiohttp
import asyncio
import re
import urllib.parse
from typing import List, Dict, Any
from loguru import logger
import ssl

ssl_context = ssl._create_unverified_context()


class LinkedInJobsSearcher:
    """Cherche des offres sur LinkedIn Jobs via l'API publique."""

    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml",
            "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.7",
            "Referer": "https://www.linkedin.com/",
        }

    async def search_jobs(self, keywords: str, location: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Recherche des offres sur LinkedIn Jobs."""
        # Nettoyage des opérateurs de recherche et guillemets (non compatibles avec LinkedIn)
        clean_kw = keywords.replace('"', '').strip()
        
        logger.info(f"💼 LinkedIn Jobs: recherche '{clean_kw}' à '{location}'")
        
        # Essai 1: API publique JSON de LinkedIn Jobs
        jobs = await self._search_linkedin_json_api(clean_kw, location, limit)
        
        if not jobs:
            # Essai 2: Scraping HTML de la page de recherche
            jobs = await self._scrape_linkedin_html(clean_kw, location, limit)
        
        if not jobs:
            # Fallback : liens de recherche directs
            jobs = self._generate_linkedin_search_links(clean_kw, location)
        
        return jobs[:limit]

    async def _search_linkedin_json_api(self, keywords: str, location: str, limit: int) -> List[Dict[str, Any]]:
        """Tente l'API JSON publique de LinkedIn Jobs."""
        kw_enc = urllib.parse.quote_plus(keywords)
        loc_enc = urllib.parse.quote_plus(location)
        # Endpoint public LinkedIn Jobs (sans authentification)
        url = f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={kw_enc}&location={loc_enc}&start=0&count={limit}&sortBy=R"
        
        try:
            async with aiohttp.ClientSession(headers=self.headers) as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=12)) as resp:
                    if resp.status != 200:
                        raise Exception(f"HTTP {resp.status}")
                    html = await resp.text()
                    return self._parse_linkedin_job_cards(html, location)
        except Exception as e:
            logger.debug(f"LinkedIn JSON API failed: {e}")
            return []

    async def _scrape_linkedin_html(self, keywords: str, location: str, limit: int) -> List[Dict[str, Any]]:
        """Scrape la page LinkedIn Jobs publique."""
        kw_enc = urllib.parse.quote_plus(keywords)
        loc_enc = urllib.parse.quote_plus(location)
        url = f"https://www.linkedin.com/jobs/search/?keywords={kw_enc}&location={loc_enc}&sortBy=R&f_TPR=r86400"
        
        try:
            async with aiohttp.ClientSession(headers=self.headers) as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=12)) as resp:
                    if resp.status != 200:
                        raise Exception(f"HTTP {resp.status}")
                    html = await resp.text()
                    return self._parse_linkedin_job_cards(html, location, limit)
        except Exception as e:
            logger.debug(f"LinkedIn HTML scrape failed: {e}")
            return []

    def _parse_linkedin_job_cards(self, html: str, location: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Parse les job cards LinkedIn depuis le HTML."""
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, "html.parser")
            jobs = []
            
            # Sélecteurs LinkedIn Jobs (layout 2024)
            cards = soup.find_all("li")
            
            for i, card in enumerate(cards):
                if len(jobs) >= limit:
                    break
                
                # Titre du poste
                title_tag = card.find("h3", class_=lambda c: c and "title" in str(c).lower()) or \
                            card.find("a", class_=lambda c: c and "title" in str(c).lower()) or \
                            card.find("h3") or card.find("h2")
                
                # Entreprise
                company_tag = card.find(class_=lambda c: c and "company" in str(c).lower() if c else False) or \
                              card.find("h4")
                
                # Lien direct vers l'offre
                link_tag = card.find("a", href=lambda h: h and "/jobs/view/" in str(h))
                if not link_tag:
                    link_tag = card.find("a", href=lambda h: h and "linkedin.com/jobs" in str(h))
                
                if not title_tag:
                    continue
                
                href = ""
                if link_tag:
                    href = link_tag.get("href", "")
                    if href and not href.startswith("http"):
                        href = f"https://www.linkedin.com{href}"
                    # Nettoyage des paramètres superflus
                    href = href.split("?")[0] if href else ""
                
                title = title_tag.get_text(strip=True)
                company = company_tag.get_text(strip=True) if company_tag else "Confidentiel"
                
                if not title or len(title) < 3:
                    continue
                
                # Localisation
                loc_tag = card.find(class_=lambda c: c and "location" in str(c).lower() if c else False)
                job_location = loc_tag.get_text(strip=True) if loc_tag else "Non spécifié"
                
                # Description courte (Snippet)
                snippet_tag = card.find("p", class_=re.compile("snippet|description")) or \
                              card.find(class_=re.compile("job-search-card__snippet"))
                snippet = snippet_tag.get_text(strip=True) if snippet_tag else ""
                
                jobs.append({
                    "id": f"linkedin-{i}",
                    "title": title,
                    "company": company,
                    "location": job_location,
                    "url": href or f"https://www.linkedin.com/jobs/search/?keywords={urllib.parse.quote_plus(title)}",
                    "description": snippet,
                    "source": "LinkedIn Jobs",
                    "match_score": 0,
                })


            
            return jobs
        except Exception as e:
            logger.debug(f"LinkedIn card parsing failed: {e}")
            return []

    async def fetch_full_description(self, url: str) -> str:
        """Récupère la description complète depuis la page de l'offre."""
        if not url or "linkedin.com" not in url:
            return ""
        try:
            async with aiohttp.ClientSession(headers=self.headers) as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10), ssl=ssl_context) as resp:
                    if resp.status != 200:
                        return ""
                    html = await resp.text()
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(html, "html.parser")
                    # Sélecteurs pour la description LinkedIn publique
                    desc_tag = soup.find(class_=re.compile("description__text|show-more-less-html__markup"))
                    if desc_tag:
                        # Nettoyer le HTML
                        for tag in desc_tag.find_all(["button", "script", "style"]):
                            tag.decompose()
                        return desc_tag.get_text(separator=" ", strip=True)[:2000]
        except Exception as e:
            logger.debug(f"LinkedIn detail fetch failed: {e}")
        return ""

    def _generate_linkedin_search_links(self, keywords: str, location: str) -> List[Dict[str, Any]]:

        """Génère un lien de recherche LinkedIn direct (fallback garanti)."""
        kw_enc = urllib.parse.quote_plus(keywords)
        loc_enc = urllib.parse.quote_plus(location)
        return [{
            "id": "linkedin-search",
            "title": f"Offres '{keywords}' sur LinkedIn",
            "company": "LinkedIn Jobs",
            "location": "Non spécifié",
            "url": f"https://www.linkedin.com/jobs/search/?keywords={kw_enc}&location={loc_enc}&sortBy=R",
            "description": "Voir toutes les offres sur LinkedIn",
            "source": "LinkedIn Jobs",
            "match_score": 0,
        }]
