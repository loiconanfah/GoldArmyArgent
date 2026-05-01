"""
Client pour l'API TheirStack — agrège 30+ sources (Greenhouse, Lever, Ashby, Workday, etc.)
Doc: https://api.theirstack.com
"""
import aiohttp
from typing import List, Dict, Any
from loguru import logger


class TheirStackSearcher:
    """Client pour l'API TheirStack Job Postings."""

    BASE_URL = "https://api.theirstack.com/v1/jobs/search"

    def __init__(self, api_key: str):
        self.api_key = api_key

    async def search_jobs(self, keywords: str, location: str, limit: int = 25, **kwargs) -> List[Dict[str, Any]]:
        """
        Recherche des offres via TheirStack.
        TheirStack couvre Greenhouse, Lever, Ashby, Workday, SmartRecruiters, etc.
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        # Construction du payload TheirStack v1
        payload = {
            "job_title_or": [keywords],  # Liste de titres à chercher (OR)
            "job_country_code_or": self._location_to_country(location),
            "page": 0,
            "limit": min(limit, 100),
            "order_by": [{"desc": True, "field": "date_posted"}],
            "include_total_results": False,
        }

        # Ajout de la ville si possible
        city = location.split(",")[0].strip() if location else ""
        if city:
            payload["job_location_pattern_or"] = [city]

        try:
            logger.info(f"🏗️ TheirStack: '{keywords}' @ '{location}'")
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.BASE_URL,
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=20),
                    ssl=False
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        jobs = data.get("data", [])
                        normalized = self._normalize(jobs)
                        logger.info(f"🏗️ TheirStack: {len(normalized)} offres pour '{keywords}'")
                        return normalized
                    else:
                        text = await response.text()
                        logger.warning(f"⚠️ TheirStack {response.status}: {text[:200]}")
                        return []
        except Exception as e:
            logger.error(f"TheirStack Error: {e}")
            return []

    def _location_to_country(self, location: str) -> List[str]:
        """Convertit une localisation textuelle en code(s) pays ISO pour TheirStack."""
        loc = location.lower()
        if any(w in loc for w in ["canada", "montreal", "québec", "quebec", "toronto", "vancouver", "ottawa", "qc"]):
            return ["CA"]
        if any(w in loc for w in ["france", "paris", "lyon", "marseille"]):
            return ["FR"]
        if any(w in loc for w in ["usa", "united states", "new york", "california", "texas", "chicago", "boston", "seattle"]):
            return ["US"]
        if any(w in loc for w in ["uk", "london", "manchester", "england"]):
            return ["GB"]
        if any(w in loc for w in ["belgique", "bruxelles", "belgium"]):
            return ["BE"]
        if any(w in loc for w in ["suisse", "switzerland", "zurich", "genève"]):
            return ["CH"]
        if any(w in loc for w in ["allemagne", "germany", "berlin", "munich"]):
            return ["DE"]
        # Fallback : Canada + France comme valeurs par défaut
        return ["CA", "FR"]

    def _normalize(self, raw_jobs: List[Dict]) -> List[Dict[str, Any]]:
        """Convertit les résultats TheirStack au format standard GoldArmy."""
        normalized = []
        for job in raw_jobs:
            try:
                title = job.get("job_title") or job.get("title") or ""
                company = (job.get("company") or {}).get("name") or job.get("company_name") or "Confidentiel"
                location = job.get("job_location") or job.get("location") or "Non spécifié"
                url = job.get("url") or job.get("job_url") or ""
                description = job.get("job_description_text") or job.get("description") or ""
                posted = job.get("date_posted") or job.get("posted_at") or ""

                if not title:
                    continue

                normalized.append({
                    "id": f"theirstack-{job.get('id', hash(url))}",
                    "title": title,
                    "company": company,
                    "location": location,
                    "description": description[:1000] if description else f"Poste: {title}. Entreprise: {company}. Voir le lien.",
                    "url": url,
                    "source": "TheirStack",
                    "posted_date": posted,
                    "salary": job.get("salary") or "Non spécifié",
                    "job_type": job.get("employment_type") or "Non spécifié",
                    "match_score": 0,
                })
            except Exception as e:
                logger.warning(f"TheirStack normalize error: {e}")
                continue
        return normalized
