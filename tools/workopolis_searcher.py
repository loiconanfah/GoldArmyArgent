"""
Scraper Workopolis — Portail emploi canadien, fort volume Québec/Ontario.
Utilise le flux JSON public de Workopolis (aucune clé requise).
"""
import aiohttp
import re
import urllib.parse
from typing import List, Dict, Any
from loguru import logger


class WorkopolisSearcher:
    """Scraper léger pour Workopolis (Canada)."""

    BASE_URL = "https://www.workopolis.com/jobsearch/find-jobs"

    async def search_jobs(self, keywords: str, location: str, limit: int = 25, **kwargs) -> List[Dict[str, Any]]:
        """Scrape les offres Workopolis via leur API interne JSON."""
        kw_enc = urllib.parse.quote_plus(keywords)
        loc_enc = urllib.parse.quote_plus(location.split(",")[0].strip())

        # Workopolis expose une API JSON non officielle via ce paramètre
        api_url = f"https://www.workopolis.com/jobsearch/find-jobs?ak={kw_enc}&l={loc_enc}&lg=en&pn=1"

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "fr-CA,fr;q=0.9,en;q=0.8",
        }

        try:
            logger.info(f"🍁 Workopolis: '{keywords}' @ '{location}'")
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.get(
                    api_url,
                    timeout=aiohttp.ClientTimeout(total=12),
                    ssl=False
                ) as response:
                    if response.status != 200:
                        logger.warning(f"⚠️ Workopolis {response.status}")
                        return []
                    html = await response.text()

            # Extraction des données JSON embarquées dans le HTML (pattern Workopolis)
            jobs = self._extract_from_html(html, keywords, location, limit)
            logger.info(f"🍁 Workopolis: {len(jobs)} offres pour '{keywords}'")
            return jobs

        except Exception as e:
            logger.error(f"Workopolis Error: {e}")
            return []

    def _extract_from_html(self, html: str, keywords: str, location: str, limit: int) -> List[Dict]:
        """Extrait les offres depuis le HTML de Workopolis via regex sur le JSON embarqué."""
        jobs = []
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, "html.parser")

            # Workopolis injecte les données dans un script JSON
            script_tags = soup.find_all("script", type="application/ld+json")
            for script in script_tags:
                try:
                    import json
                    data = json.loads(script.string or "")
                    if isinstance(data, list):
                        for item in data:
                            if item.get("@type") == "JobPosting":
                                jobs.append(self._parse_jsonld(item))
                    elif data.get("@type") == "JobPosting":
                        jobs.append(self._parse_jsonld(data))
                except Exception:
                    continue

            # Fallback : extraction HTML directe si JSON LD absent
            if not jobs:
                cards = soup.find_all("article", class_=re.compile("job|posting|card", re.I))
                for i, card in enumerate(cards[:limit]):
                    title_el = card.find(["h2", "h3", "h4"]) or card.find(class_=re.compile("title", re.I))
                    company_el = card.find(class_=re.compile("company|employer", re.I))
                    loc_el = card.find(class_=re.compile("location|city", re.I))
                    link_el = card.find("a", href=True)
                    title = title_el.get_text(strip=True) if title_el else ""
                    if not title:
                        continue
                    href = link_el["href"] if link_el else ""
                    if href and not href.startswith("http"):
                        href = f"https://www.workopolis.com{href}"
                    jobs.append({
                        "id": f"workopolis-{i}",
                        "title": title,
                        "company": company_el.get_text(strip=True) if company_el else "Confidentiel",
                        "location": loc_el.get_text(strip=True) if loc_el else location,
                        "description": f"Poste: {title}. Voir le lien Workopolis pour les détails.",
                        "url": href or f"https://www.workopolis.com/jobsearch/find-jobs?ak={urllib.parse.quote_plus(keywords)}",
                        "source": "Workopolis",
                        "posted_date": "",
                        "salary": "Non spécifié",
                        "job_type": "Non spécifié",
                        "match_score": 0,
                    })
        except Exception as e:
            logger.warning(f"Workopolis HTML parse error: {e}")
        return jobs[:limit]

    def _parse_jsonld(self, item: dict) -> dict:
        """Parse un item JSON-LD JobPosting Workopolis."""
        title = item.get("title") or ""
        company = (item.get("hiringOrganization") or {}).get("name") or "Confidentiel"
        loc_data = item.get("jobLocation") or {}
        address = (loc_data.get("address") or {})
        location = address.get("addressLocality") or address.get("addressRegion") or "Canada"
        url = item.get("url") or ""
        description = item.get("description") or f"Poste: {title}."
        # Nettoyer le HTML dans la description
        description = re.sub(r"<[^>]+>", " ", description)[:1000]
        posted = item.get("datePosted") or ""
        salary_data = item.get("baseSalary") or {}
        salary_value = (salary_data.get("value") or {})
        sal_min = salary_value.get("minValue")
        sal_max = salary_value.get("maxValue")
        salary = f"${sal_min}–${sal_max}" if sal_min and sal_max else "Non spécifié"

        return {
            "id": f"workopolis-{hash(url)}",
            "title": title,
            "company": company,
            "location": location,
            "description": description,
            "url": url,
            "source": "Workopolis",
            "posted_date": posted,
            "salary": salary,
            "job_type": item.get("employmentType") or "Non spécifié",
            "match_score": 0,
        }
