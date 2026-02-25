"""Scraper Google Jobs - récupère les offres d'emploi directement depuis Google.
Utilise le endpoint Google Jobs (htl;jobs) qui retourne des fiches structurées.
"""
import aiohttp
import asyncio
import re
import ssl
import json
import urllib.parse
from typing import List, Dict, Any
from loguru import logger

ssl_ctx = ssl._create_unverified_context()

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Linux; Android 10; K) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.6261.119 Mobile Safari/537.36"
    ),
    "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.7",
    "Accept": "text/html,application/xhtml+xml",
}


class GoogleJobsSearcher:
    """Scrape Google Jobs pour obtenir des offres avec descriptions complètes."""

    def __init__(self):
        self.headers = HEADERS

    async def search_jobs(self, keywords: str, location: str, limit: int = 10) -> List[Dict[str, Any]]:
        clean_kw = keywords.replace('"', '').strip()
        logger.info(f"🌐 Google Jobs: '{clean_kw}' @ '{location}'")

        jobs = await self._try_google_jobs_api(clean_kw, location, limit)

        if not jobs:
            jobs = await self._try_google_html_scrape(clean_kw, location, limit)

        if not jobs:
            jobs = self._fallback_links(clean_kw, location)

        return jobs[:limit]

    async def _try_google_jobs_api(self, keywords: str, location: str, limit: int) -> List[Dict[str, Any]]:
        """
        Tente l'API publique Google Jobs via le paramètre ibp=htl;jobs.
        Retourne des offres structurées en JSON-LD intégrées dans le HTML.
        """
        query = f"{keywords} {location} emploi"
        q_enc = urllib.parse.quote_plus(query)
        url = f"https://www.google.com/search?q={q_enc}&ibp=htl;jobs&hl=fr&gl=fr"

        try:
            async with aiohttp.ClientSession(headers=self.headers) as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=15), ssl=ssl_ctx) as resp:
                    if resp.status != 200:
                        raise Exception(f"HTTP {resp.status}")
                    html = await resp.text()

            return self._parse_google_jobs_html(html, location, limit)

        except Exception as e:
            logger.debug(f"Google Jobs API attempt failed: {e}")
            return []

    async def _try_google_html_scrape(self, keywords: str, location: str, limit: int) -> List[Dict[str, Any]]:
        """
        Scrape Google Search classique pour les extraits d'emploi.
        """
        query = f"{keywords} emploi {location}"
        q_enc = urllib.parse.quote_plus(query)
        url = f"https://www.google.com/search?q={q_enc}&hl=fr&gl=fr&num=20"

        try:
            async with aiohttp.ClientSession(headers=self.headers) as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=15), ssl=ssl_ctx) as resp:
                    if resp.status != 200:
                        raise Exception(f"HTTP {resp.status}")
                    html = await resp.text()

            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, "html.parser")
            jobs = []

            # Chercher les blocs JSON-LD avec des offres d'emploi
            for script in soup.find_all("script", type="application/ld+json"):
                try:
                    data = json.loads(script.string or "")
                    if isinstance(data, list):
                        for item in data:
                            job = self._parse_jsonld_job(item, location)
                            if job:
                                jobs.append(job)
                    elif isinstance(data, dict):
                        job = self._parse_jsonld_job(data, location)
                        if job:
                            jobs.append(job)
                except:
                    continue

            # Aussi chercher les résultats de recherche normaux
            if not jobs:
                results = soup.find_all("div", class_=re.compile(r"^g$|tF2Cxc"))
                for i, div in enumerate(results[:limit]):
                    link = div.find("a", href=True)
                    title = div.find("h3")
                    snippet = div.find("div", class_=re.compile(r"IsZvec|VwiC3b|yXK7lf"))
                    if not link or not title:
                        continue
                    href = link.get("href", "")
                    t = title.get_text(strip=True)
                    # Filtrer les résultats non pertinents
                    if not any(w in t.lower() for w in ["emploi", "job", "poste", "recrutement", "offre", keywords.lower()[:10]]):
                        continue
                    jobs.append({
                        "id": f"google-{i}",
                        "title": t,
                        "company": "Via Google",
                        "location": location,
                        "url": href if href.startswith("http") else f"https://www.google.com{href}",
                        "description": snippet.get_text(strip=True)[:300] if snippet else "",
                        "source": "Google Search",
                        "match_score": 0,
                    })

            return jobs[:limit]

        except Exception as e:
            logger.debug(f"Google HTML scrape failed: {e}")
            return []

    def _parse_google_jobs_html(self, html: str, location: str, limit: int) -> List[Dict[str, Any]]:
        """Parse les blocs d'emploi intégrés dans la page Google Jobs."""
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, "html.parser")
            jobs = []

            # Google Jobs structure : blocs avec data dans les scripts
            for script in soup.find_all("script"):
                text = script.string or ""
                if "JobPosting" not in text and "htichips" not in text:
                    continue
                try:
                    # Tentative JSON-LD
                    data = json.loads(text)
                    if isinstance(data, dict):
                        job = self._parse_jsonld_job(data, location)
                        if job:
                            jobs.append(job)
                except:
                    # Extraction regex comme fallback
                    titles = re.findall(r'"title"\s*:\s*"([^"]+)"', text)
                    companies = re.findall(r'"name"\s*:\s*"([^"]+)"', text)
                    urls = re.findall(r'"url"\s*:\s*"(https?://[^"]+)"', text)
                    descriptions = re.findall(r'"description"\s*:\s*"([^"]{20,300})"', text)
                    for i, title in enumerate(titles[:limit]):
                        jobs.append({
                            "id": f"google-jobs-{i}",
                            "title": title,
                            "company": companies[i] if i < len(companies) else "Confidentiel",
                            "location": location,
                            "url": urls[i] if i < len(urls) else f"https://www.google.com/search?q={urllib.parse.quote_plus(title)}",
                            "description": descriptions[i].replace("\\n", " ").replace("\\u", " ")[:300] if i < len(descriptions) else "",
                            "source": "Google Jobs",
                            "match_score": 0,
                        })

            return jobs[:limit]
        except Exception as e:
            logger.debug(f"Google Jobs parse error: {e}")
            return []

    def _parse_jsonld_job(self, data: dict, location: str) -> Dict | None:
        """Parse une offre depuis un bloc JSON-LD JobPosting."""
        if data.get("@type") not in ("JobPosting", "jobPosting"):
            return None
        title = data.get("title", "")
        if not title:
            return None
        company = data.get("hiringOrganization", {})
        if isinstance(company, dict):
            company = company.get("name", "Confidentiel")
        loc = data.get("jobLocation", {})
        if isinstance(loc, dict):
            addr = loc.get("address", {})
            if isinstance(addr, dict):
                loc = f"{addr.get('addressLocality', '')}, {addr.get('addressCountry', '')}".strip(", ")
            else:
                loc = location
        url = data.get("url", data.get("sameAs", ""))
        description = data.get("description", "")
        # Nettoyer la description HTML
        description = re.sub(r"<[^>]+>", " ", description)
        description = re.sub(r"\s+", " ", description).strip()[:400]
        return {
            "id": f"google-jsonld-{hash(title + company)}",
            "title": title,
            "company": company,
            "location": str(loc) or location,
            "url": url,
            "description": description,
            "source": "Google Jobs",
            "match_score": 0,
        }

    def _fallback_links(self, keywords: str, location: str) -> List[Dict[str, Any]]:
        kw_enc = urllib.parse.quote_plus(f"{keywords} emploi {location}")
        return [{
            "id": "google-link",
            "title": f"Voir '{keywords}' sur Google Jobs",
            "company": "Google Jobs",
            "location": location,
            "url": f"https://www.google.com/search?q={kw_enc}&ibp=htl;jobs",
            "description": "Voir toutes les offres sur Google Jobs",
            "source": "Google Jobs",
            "match_score": 0,
        }]
