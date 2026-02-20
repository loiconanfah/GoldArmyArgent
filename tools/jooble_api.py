"""Client Jooble REST API (recherche d'emplois).

Ne pas mettre la clé API en dur. Utiliser la variable d'environnement JOOBLE_API_KEY
(via config.settings.settings).
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional
import urllib.request
import urllib.error
import ssl

from loguru import logger

# Désactiver la vérification SSL pour simplifier (cohérent avec web_searcher)
ssl_context = ssl._create_unverified_context()


class JoobleClient:
    """Client minimal pour la Jooble REST API."""

    def __init__(self, api_key: str, host: str = "jooble.org"):
        self.api_key = (api_key or "").strip()
        self.host = host

    def is_configured(self) -> bool:
        return bool(self.api_key)

    async def search_jobs(
        self,
        keywords: str,
        location: str,
        page: int = 1,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """Recherche des offres via Jooble.

        Jooble accepte un JSON du type:
        {"keywords":"...", "location":"..."}

        Notes:
        - La structure exacte de la réponse peut varier selon le plan Jooble.
        - On normalise ensuite vers notre format interne.
        """
        if not self.is_configured():
            return []

        payload: Dict[str, Any] = {
            "keywords": keywords,
            "location": location,
            "page": page,
            "limit": limit,
        }

        url = f"https://{self.host}/api/{self.api_key}"
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "GoldArmyArgent/1.0",
        }

        body = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=body, headers=headers, method="POST")

        import asyncio

        def _do_request() -> bytes:
            with urllib.request.urlopen(req, context=ssl_context, timeout=20) as resp:
                return resp.read()

        try:
            loop = asyncio.get_event_loop()
            raw = await loop.run_in_executor(None, _do_request)
            data = json.loads(raw.decode("utf-8", errors="ignore") or "{}")
            return self._normalize_response(data)
        except urllib.error.HTTPError as e:
            try:
                body = e.read().decode("utf-8", errors="ignore")
            except Exception:
                body = ""
            logger.warning(f"⚠️ Jooble HTTPError {e.code}: {body[:400]}")
            return []
        except urllib.error.URLError as e:
            logger.warning(f"⚠️ Jooble URLError: {e}")
            return []
        except Exception as e:
            logger.warning(f"⚠️ Jooble API error: {e}")
            return []

    def _normalize_response(self, data: Any) -> List[Dict[str, Any]]:
        """Normalise la réponse Jooble vers le format interne."""
        # Jooble retourne souvent {"jobs": [...]} ou directement une liste.
        jobs_raw: Optional[Any] = None
        if isinstance(data, dict):
            jobs_raw = data.get("jobs") or data.get("data") or data.get("result")
        if jobs_raw is None:
            jobs_raw = data

        if not isinstance(jobs_raw, list):
            return []

        normalized: List[Dict[str, Any]] = []
        for idx, j in enumerate(jobs_raw):
            if not isinstance(j, dict):
                continue

            title = j.get("title") or j.get("position") or "Offre"
            company = j.get("company") or j.get("companyname") or j.get("employer") or "Entreprise"
            location = j.get("location") or j.get("region") or j.get("city") or ""
            url = j.get("link") or j.get("url") or j.get("applyLink") or ""
            snippet = j.get("snippet") or j.get("description") or j.get("summary") or ""

            normalized.append(
                {
                    "id": j.get("id") or f"jooble-{idx}",
                    "title": title,
                    "company": company,
                    "location": location,
                    "url": url,
                    "description": snippet,
                    "source": "Jooble",
                    "required_skills": [],
                    "match_score": 0,
                    "scraped": False,
                }
            )

        return normalized
