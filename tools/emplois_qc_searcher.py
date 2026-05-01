"""
Client Emplois Québec (Gouvernement du Québec) — API publique gratuite.
Offres officielles publiées par le gouvernement du Québec.
Endpoint: https://placement.emploiquebec.gouv.qc.ca
"""
import aiohttp
import urllib.parse
from typing import List, Dict, Any
from loguru import logger


class EmploisQcSearcher:
    """Client pour les offres d'emploi du Gouvernement du Québec."""

    # API officielle Emplois Québec (IMT / Placement en ligne)
    BASE_URL = "https://placement.emploiquebec.gouv.qc.ca/mbe/ut/rechroffr/lstoffr.asp"
    # Fallback: flux RSS public
    RSS_URL = "https://placement.emploiquebec.gouv.qc.ca/mbe/ut/rechroffr/xsl/offr.rss"

    async def search_jobs(self, keywords: str, location: str, limit: int = 25, **kwargs) -> List[Dict[str, Any]]:
        """Récupère les offres via le flux RSS public d'Emplois Québec."""
        try:
            kw_enc = urllib.parse.quote_plus(keywords)
            city = location.split(",")[0].strip()
            city_enc = urllib.parse.quote_plus(city)

            rss_url = f"https://placement.emploiquebec.gouv.qc.ca/mbe/ut/rechroffr/xsl/offr.rss?typerechr=0&motcle={kw_enc}&reg=&mrc=&muncp={city_enc}&nb_offr={min(limit, 50)}&langue=FRANC"

            headers = {
                "User-Agent": "GoldArmy/1.0 (aggregateur emploi)",
                "Accept": "application/rss+xml, application/xml, text/xml",
            }

            logger.info(f"🏛️ Emplois Québec: '{keywords}' @ '{city}'")
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.get(
                    rss_url,
                    timeout=aiohttp.ClientTimeout(total=12),
                    ssl=False
                ) as response:
                    if response.status != 200:
                        logger.warning(f"⚠️ Emplois Québec {response.status}")
                        return []
                    text = await response.text(encoding="utf-8", errors="replace")

            jobs = self._parse_rss(text, limit)
            logger.info(f"🏛️ Emplois Québec: {len(jobs)} offres pour '{keywords}'")
            return jobs

        except Exception as e:
            logger.error(f"EmploisQc Error: {e}")
            return []

    def _parse_rss(self, xml_text: str, limit: int) -> List[Dict[str, Any]]:
        """Parse le flux RSS XML d'Emplois Québec."""
        jobs = []
        try:
            import xml.etree.ElementTree as ET
            root = ET.fromstring(xml_text)
            channel = root.find("channel")
            if channel is None:
                return []

            items = channel.findall("item")
            for i, item in enumerate(items[:limit]):
                title = (item.findtext("title") or "").strip()
                description = (item.findtext("description") or "").strip()
                url = (item.findtext("link") or "").strip()
                pub_date = (item.findtext("pubDate") or "").strip()

                if not title:
                    continue

                # Extraction du nom d'entreprise depuis le titre (format "Titre - Entreprise - Ville")
                parts = title.split(" - ")
                job_title = parts[0].strip() if parts else title
                company = parts[1].strip() if len(parts) > 1 else "Confidentiel"
                city = parts[2].strip() if len(parts) > 2 else "Québec"

                # Nettoyage HTML de la description
                import re
                description = re.sub(r"<[^>]+>", " ", description)[:800].strip()

                jobs.append({
                    "id": f"emploisqc-{i}-{hash(url)}",
                    "title": job_title,
                    "company": company,
                    "location": f"{city}, Québec",
                    "description": description or f"Poste: {job_title}. Entreprise: {company}.",
                    "url": url,
                    "source": "Emplois Québec (Gouvernement)",
                    "posted_date": pub_date,
                    "salary": "Non spécifié",
                    "job_type": "Non spécifié",
                    "match_score": 0,
                })
        except Exception as e:
            logger.warning(f"EmploisQc RSS parse error: {e}")
        return jobs
