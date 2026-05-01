"""
Client RemoteOK — API publique JSON gratuite, aucune clé requise.
Spécialisé dans les offres remote tech (dev, data, design).
Doc: https://remoteok.com/api
"""
import aiohttp
from typing import List, Dict, Any
from loguru import logger


class RemoteOKSearcher:
    """Client pour l'API publique RemoteOK."""

    BASE_URL = "https://remoteok.com/api"

    async def search_jobs(self, keywords: str, location: str = "", limit: int = 50, **kwargs) -> List[Dict[str, Any]]:
        """
        Récupère les offres remote depuis RemoteOK.
        L'API ne supporte pas le filtrage par localisation (tout est remote).
        On filtre côté client par mots-clés dans le titre/tags.
        """
        headers = {
            "User-Agent": "GoldArmy/1.0 (job aggregator - contact: support@goldarmyai.com)"
        }

        try:
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.get(
                    self.BASE_URL,
                    timeout=aiohttp.ClientTimeout(total=15),
                    ssl=False
                ) as response:
                    if response.status != 200:
                        logger.warning(f"⚠️ RemoteOK {response.status}")
                        return []

                    data = await response.json(content_type=None)
                    # Le premier élément est un header de l'API, on le retire
                    jobs = [j for j in data if isinstance(j, dict) and j.get("id")]

                    # Filtrage par mots-clés
                    kw_lower = keywords.lower()
                    kw_parts = kw_lower.replace("-", " ").split()
                    filtered = []
                    for job in jobs:
                        title = (job.get("position") or "").lower()
                        tags = " ".join(job.get("tags") or []).lower()
                        text = f"{title} {tags}"
                        if any(part in text for part in kw_parts):
                            filtered.append(job)
                        if len(filtered) >= limit:
                            break

                    normalized = self._normalize(filtered)
                    logger.info(f"🌍 RemoteOK: {len(normalized)} offres pour '{keywords}'")
                    return normalized

        except Exception as e:
            logger.error(f"RemoteOK Error: {e}")
            return []

    def _normalize(self, raw_jobs: List[Dict]) -> List[Dict[str, Any]]:
        """Convertit les résultats RemoteOK au format standard GoldArmy."""
        normalized = []
        for job in raw_jobs:
            try:
                title = job.get("position") or ""
                company = job.get("company") or "Confidentiel"
                tags = ", ".join(job.get("tags") or [])
                description = job.get("description") or f"Poste remote: {title}. Tags: {tags}. Voir le lien."
                url = job.get("url") or f"https://remoteok.com/l/{job.get('id', '')}"
                posted = job.get("date") or ""
                salary_min = job.get("salary_min")
                salary_max = job.get("salary_max")
                salary = f"${salary_min}–${salary_max}" if salary_min and salary_max else "Non spécifié"

                if not title:
                    continue

                normalized.append({
                    "id": f"remoteok-{job.get('id', hash(url))}",
                    "title": title,
                    "company": company,
                    "location": "Remote / Télétravail",
                    "description": description[:1000],
                    "url": url,
                    "source": "RemoteOK",
                    "posted_date": posted,
                    "salary": salary,
                    "job_type": "Remote",
                    "match_score": 0,
                })
            except Exception as e:
                logger.warning(f"RemoteOK normalize error: {e}")
                continue
        return normalized
