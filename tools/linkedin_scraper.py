"""
Scraper OSINT pour trouver les profils LinkedIn des recruteurs (RH) d'une entreprise.
Utilise DuckDuckGo HTML pour contourner partiellement les restrictions.
"""
import re
import urllib.request
import urllib.parse
import ssl
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from loguru import logger
import asyncio

ssl_context = ssl._create_unverified_context()

class LinkedInScraper:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "fr,fr-FR;q=0.8,en;q=0.5,en-US;q=0.3"
        }

    async def find_hr_profiles(self, company_name: str, limit: int = 5) -> List[Dict[str, str]]:
        """Cherche les profils LinkedIn (RH/Recrutement) pour une entreprise donnée."""
        if not company_name or company_name.lower() in ["confidentiel", "anonyme", "incognito", "non spécifié"]:
            return []
            
        logger.info(f"🔎 LinkedIn RH pour: {company_name}")
        profiles = []

        # 1. AsyncDDGS en premier (rapide, ~2-4s)
        try:
            from duckduckgo_search import AsyncDDGS
            query = f'site:linkedin.com/in/ "{company_name}" recruteur OR RH OR "Talent Acquisition"'
            seen = set()
            async with AsyncDDGS() as ddgs:
                async for r in ddgs.text(query, max_results=limit):
                    href = r.get("href", "")
                    if "linkedin.com/in/" in href:
                        href = href.split("?")[0].rstrip("/")
                        if href and href not in seen:
                            seen.add(href)
                            profiles.append({
                                "name": (r.get("title") or "Profil LinkedIn").replace(" | LinkedIn", ""),
                                "url": href,
                                "snippet": (r.get("body") or "")[:120] or f"Profil chez {company_name}"
                            })
                            if len(profiles) >= limit:
                                break
        except Exception as ddg_err:
            logger.debug(f"AsyncDDGS: {ddg_err}")

        # 2. Fallback DDG Lite HTML si vide
        if not profiles:
            try:
                query = f'site:linkedin.com/in/ "{company_name}" Recrutement OR RH OR Recruteur'
                encoded = urllib.parse.quote_plus(query)
                req = urllib.request.Request(f"https://lite.duckduckgo.com/lite/?q={encoded}", headers=self.headers)
                loop = asyncio.get_event_loop()
                html = await asyncio.wait_for(loop.run_in_executor(None, lambda: urllib.request.urlopen(req, context=ssl_context, timeout=8).read().decode()), timeout=10)
                soup = BeautifulSoup(html, "html.parser")
                seen = set()
                for a in soup.find_all("a", href=True):
                    if len(profiles) >= limit:
                        break
                    href = a.get("href", "")
                    if "uddg=" in href:
                        try:
                            href = urllib.parse.unquote(href.split("uddg=")[-1].split("&")[0])
                        except Exception:
                            pass
                    if "linkedin.com/in/" in href:
                        href = href.split("?")[0].rstrip("/")
                        if href not in seen:
                            seen.add(href)
                            title = a.get_text(strip=True).replace(" | LinkedIn", "").replace(" - LinkedIn", "")
                            name = re.split(r" - | \| |: ", title)[0].strip() if title else "Profil LinkedIn"
                            profiles.append({"name": name, "url": href, "snippet": f"Profil: {title[:80]}"})
            except Exception as e:
                logger.debug(f"DDG Lite: {e}")

        if not profiles:
            logger.info("ℹ️ Fallback LinkedIn Search Link.")
            direct_search_url = f"https://www.linkedin.com/search/results/people/?keywords={urllib.parse.quote_plus('recruteur ' + company_name)}"
            profiles.append({
                "name": f"Chercher '{company_name}' sur LinkedIn",
                "url": direct_search_url,
                "snippet": "Profils non extraits automatiquement. Cliquez pour voir sur LinkedIn."
            })
            
        return profiles

linkedin_scraper = LinkedInScraper()
