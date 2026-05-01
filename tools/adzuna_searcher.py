"""
Client Adzuna — API gratuite, 1000 req/jour, excellente couverture Canada/France/UK/USA.
Inscription gratuite sur: https://developer.adzuna.com
Variables .env requises: ADZUNA_APP_ID et ADZUNA_API_KEY
"""
import aiohttp
from typing import List, Dict, Any
from loguru import logger


class AdzunaSearcher:
    """Client pour l'API Adzuna Job Search."""

    # Mapping localisation -> code pays Adzuna
    COUNTRY_MAP = {
        "ca": ["canada", "montreal", "québec", "quebec", "toronto", "vancouver", "ottawa", "calgary", "qc"],
        "fr": ["france", "paris", "lyon", "marseille", "bordeaux", "nantes", "lille"],
        "gb": ["uk", "london", "manchester", "birmingham", "england"],
        "us": ["usa", "united states", "new york", "california", "texas", "chicago", "boston", "seattle", "silicon valley"],
        "be": ["belgique", "bruxelles", "belgium"],
        "de": ["allemagne", "germany", "berlin", "munich"],
        "au": ["australia", "sydney", "melbourne"],
    }

    def __init__(self, app_id: str, api_key: str):
        self.app_id = app_id
        self.api_key = api_key

    def _get_country_code(self, location: str) -> str:
        loc = location.lower()
        for code, keywords in self.COUNTRY_MAP.items():
            if any(kw in loc for kw in keywords):
                return code
        return "ca"  # Canada par défaut

    async def search_jobs(self, keywords: str, location: str, limit: int = 50, **kwargs) -> List[Dict[str, Any]]:
        """Recherche des offres sur Adzuna."""
        country = self._get_country_code(location)
        city = location.split(",")[0].strip() if location else ""

        params = {
            "app_id": self.app_id,
            "app_key": self.api_key,
            "what": keywords,
            "where": city,
            "results_per_page": min(limit, 50),  # Max 50 par page Adzuna
            "content-type": "application/json",
            "sort_by": "date",
        }

        url = f"https://api.adzuna.com/v1/api/jobs/{country}/search/1"

        try:
            logger.info(f"🍁 Adzuna ({country.upper()}): '{keywords}' @ '{city}'")
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url,
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=15),
                    ssl=False
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        jobs = data.get("results", [])
                        normalized = self._normalize(jobs)
                        logger.info(f"🍁 Adzuna: {len(normalized)} offres pour '{keywords}'")
                        return normalized
                    else:
                        text = await response.text()
                        logger.warning(f"⚠️ Adzuna {response.status}: {text[:200]}")
                        return []
        except Exception as e:
            logger.error(f"Adzuna Error: {e}")
            return []

    def _normalize(self, raw_jobs: List[Dict]) -> List[Dict[str, Any]]:
        """Convertit les résultats Adzuna au format standard GoldArmy."""
        normalized = []
        for job in raw_jobs:
            try:
                title = job.get("title") or ""
                company = (job.get("company") or {}).get("display_name") or "Confidentiel"
                location_data = job.get("location") or {}
                location = location_data.get("display_name") or "Non spécifié"
                description = job.get("description") or f"Poste: {title}. Voir le lien pour les détails."
                url = job.get("redirect_url") or ""
                salary_min = job.get("salary_min")
                salary_max = job.get("salary_max")
                salary = f"${int(salary_min)}–${int(salary_max)}" if salary_min and salary_max else "Non spécifié"
                posted = job.get("created") or ""

                if not title:
                    continue

                normalized.append({
                    "id": f"adzuna-{job.get('id', hash(url))}",
                    "title": title,
                    "company": company,
                    "location": location,
                    "description": description[:1000],
                    "url": url,
                    "source": "Adzuna",
                    "posted_date": posted,
                    "salary": salary,
                    "job_type": job.get("contract_type") or "Non spécifié",
                    "match_score": 0,
                })
            except Exception as e:
                logger.warning(f"Adzuna normalize error: {e}")
                continue
        return normalized
