"""Scraper pour Indeed France et Indeed Europe (FR/UK/DE/BE/CH).
Retourne de vraies offres avec descriptions courtes.
"""
import aiohttp
import asyncio
import re
import ssl
import urllib.parse
from typing import List, Dict, Any
from loguru import logger

ssl_ctx = ssl._create_unverified_context()

# Mapping pays -> domaine Indeed
INDEED_DOMAINS = {
    "france":    ("fr.indeed.com",  "fr"),
    "belgique":  ("be.indeed.com",  "fr"),
    "suisse":    ("ch.indeed.com",  "fr"),
    "uk":        ("uk.indeed.com",  "en"),
    "allemagne": ("de.indeed.com",  "de"),
    "espagne":   ("es.indeed.com",  "es"),
    "italie":    ("it.indeed.com",  "it"),
    "canada":    ("ca.indeed.com",  "fr"),
    "usa":       ("www.indeed.com", "en"),
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.7",
    "Accept": "text/html,application/xhtml+xml",
    "Referer": "https://www.google.com/",
}


class IndeedMultiSearcher:
    """Recherche Indeed sur plusieurs domaines européens/mondiaux."""

    def __init__(self):
        self.headers = HEADERS

    def _detect_country(self, location: str) -> str:
        loc = location.lower()
        loc = loc.replace("califormie", "california").replace("californie", "california")
        if any(w in loc for w in ["france", "paris", "lyon", "marseille", "bordeaux", "nantes", "lille", "toulouse", "strasbourg", "nice", "rennes"]): return "france"
        if any(w in loc for w in ["usa", "united states", "california", "new york", "texas", "chicago", "florida", "seattle", "boston", "silicon valley"]): return "usa"
        if any(w in loc for w in ["canada", "montreal", "toronto", "vancouver", "quebec", "ottawa"]): return "canada"
        if any(w in loc for w in ["belgique", "belgium", "bruxelles"]): return "belgique"
        if any(w in loc for w in ["suisse", "switzerland", "genève", "zurich", "lausanne"]): return "suisse"
        if any(w in loc for w in ["uk", "united kingdom", "london", "england"]): return "uk"
        if any(w in loc for w in ["allemagne", "germany", "berlin", "munich"]): return "allemagne"
        if any(w in loc for w in ["espagne", "spain", "madrid", "barcelona"]): return "espagne"
        if any(w in loc for w in ["italie", "italy", "rome", "milan"]): return "italie"
        return "france"

    async def search_jobs(self, keywords: str, location: str, limit: int = 10) -> List[Dict[str, Any]]:
        # Nettoyage du mot-clé (enlever les guillemets et opérateurs)
        clean_kw = keywords.replace('"', '').strip()
        country = self._detect_country(location)
        domain, lang = INDEED_DOMAINS.get(country, ("fr.indeed.com", "fr"))

        logger.info(f"🔍 Indeed ({domain}): '{clean_kw}' @ '{location}'")

        kw_enc = urllib.parse.quote_plus(clean_kw)
        loc_enc = urllib.parse.quote_plus(location)
        url = f"https://{domain}/emplois?q={kw_enc}&l={loc_enc}&sort=date"
        if lang == "en":
            url = f"https://{domain}/jobs?q={kw_enc}&l={loc_enc}&sort=date"

        try:
            async with aiohttp.ClientSession(headers=self.headers) as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=15), ssl=ssl_ctx) as resp:
                    if resp.status != 200:
                        raise Exception(f"HTTP {resp.status}")
                    html = await resp.text()
            return self._parse(html, location, domain, limit)

        except Exception as e:
            logger.debug(f"Indeed {domain} failed: {e}")
            # Fallback : lien de recherche direct
            return [self._make_search_link(clean_kw, location, domain, lang)]

    def _parse(self, html: str, location: str, domain: str, limit: int) -> List[Dict[str, Any]]:
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, "html.parser")
            jobs = []

            # Sélecteurs Indeed (layout 2024 - plusieurs variantes)
            cards = (
                soup.find_all("div", class_=re.compile(r"job_seen_beacon")) or
                soup.find_all("div", class_=re.compile(r"resultContent")) or
                soup.find_all("li", class_=re.compile(r"css-.*resultado"))
            )

            for i, card in enumerate(cards[:limit]):
                title_el = (
                    card.find("h2", class_=re.compile(r"jobTitle")) or
                    card.find("span", attrs={"title": True}) or
                    card.find("h2")
                )
                company_el = (
                    card.find("span", class_=re.compile(r"companyName")) or
                    card.find(class_=re.compile(r"company"))
                )
                loc_el = card.find(class_=re.compile(r"companyLocation"))
                snippet_el = (
                    card.find("div", class_=re.compile(r"job-snippet|jobSnippet|underShelf")) or
                    card.find("ul", class_=re.compile(r"css-.*snippet"))
                )
                link_el = card.find("a", href=True)

                title = title_el.get_text(strip=True) if title_el else ""
                # Indeed double parfois le titre comme "nouveau" -> nettoyer
                title = re.sub(r"^nouveau\s*", "", title, flags=re.IGNORECASE).strip()
                if not title or len(title) < 3:
                    continue

                href = link_el.get("href", "") if link_el else ""
                if href and not href.startswith("http"):
                    href = f"https://{domain}{href}"
                # Garder seulement le lien propre sans les traqueurs
                href = href.split("?")[0] if "/pagead/" not in href else href

                description = snippet_el.get_text(separator=" ", strip=True)[:300] if snippet_el else ""

                jobs.append({
                    "id": f"indeed-{domain}-{i}",
                    "title": title,
                    "company": company_el.get_text(strip=True) if company_el else "Confidentiel",
                    "location": loc_el.get_text(strip=True) if loc_el else location,
                    "url": href or f"https://{domain}/emplois?q={urllib.parse.quote_plus(title)}",
                    "description": description,
                    "source": f"Indeed ({domain})",
                    "match_score": 0,
                })
            return jobs
        except Exception as e:
            logger.debug(f"Indeed parse error: {e}")
            return []

    def _make_search_link(self, keywords: str, location: str, domain: str, lang: str) -> Dict:
        kw_enc = urllib.parse.quote_plus(keywords)
        loc_enc = urllib.parse.quote_plus(location)
        path = "emplois" if lang == "fr" else "jobs"
        return {
            "id": f"indeed-{domain}-link",
            "title": f"Voir toutes les offres '{keywords}' sur Indeed",
            "company": f"Indeed ({domain})",
            "location": location,
            "url": f"https://{domain}/{path}?q={kw_enc}&l={loc_enc}",
            "description": "Cliquez pour voir toutes les offres correspondantes.",
            "source": f"Indeed ({domain})",
            "match_score": 0,
        }
