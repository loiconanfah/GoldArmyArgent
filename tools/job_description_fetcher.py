"""
Récupère la description complète d'une offre depuis l'URL de la page.
Utilisé pour enrichir les offres dont la description est vide ou très courte.
"""
import re
import asyncio
from typing import Optional
from loguru import logger

# Sélecteurs courants pour la description sur les sites d'emploi
DESCRIPTION_SELECTORS = [
    "[data-job-description]",
    "[data-description]",
    ".job-description",
    ".job_description",
    ".job-description__content",
    ".description",
    ".job-details",
    ".job-detail",
    ".job-content",
    ".job-body",
    "#job-description",
    "#jobDescription",
    "#description",
    "article.job-description",
    "article.description",
    ".vacancy-description",
    ".offer-description",
    ".posting-description",
    "[class*='jobDescription']",
    "[class*='job-description']",
    "[class*='description__text']",
    ".show-more-less-html__markup",
    ".jobs-description",
    ".job-view-description",
    "section.description",
    ".content__body",
    ".rich-text",
]

# Balises de contenu principal (fallback)
CONTENT_FALLBACK = ["article", "main", ".content", ".main-content", "[role='main']"]


async def fetch_description_from_url(url: str, source_hint: str = "") -> Optional[str]:
    """
    Récupère la description d'une offre depuis l'URL.
    Essaie plusieurs sélecteurs CSS courants sur les sites d'emploi.
    Retourne None en cas d'échec ou si la page ne contient pas de description.
    """
    if not url or not url.startswith("http"):
        return None
    try:
        import aiohttp
        from bs4 import BeautifulSoup

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml",
            "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
        }
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=12), ssl=False) as resp:
                if resp.status != 200:
                    return None
                html = await resp.text()
        soup = BeautifulSoup(html, "html.parser")
        # Retirer scripts/styles pour éviter du bruit
        for tag in soup(["script", "style", "nav", "footer", "header", "noscript", "iframe"]):
            tag.decompose()

        text = ""
        # 1) Essayer les sélecteurs dédiés description
        for selector in DESCRIPTION_SELECTORS:
            try:
                el = soup.select_one(selector)
                if el:
                    for t in el.find_all(["button", "script", "style", "a"]):
                        t.decompose()
                    raw = el.get_text(separator=" ", strip=True)
                    if len(raw) > 80:
                        text = re.sub(r"\s+", " ", raw)[:3500]
                        break
            except Exception:
                continue
        # 2) Fallback: première zone article/main avec assez de texte
        if not text or len(text) < 100:
            for sel in CONTENT_FALLBACK:
                try:
                    el = soup.select_one(sel)
                    if el:
                        raw = el.get_text(separator=" ", strip=True)
                        if 150 < len(raw) < 15000:
                            text = re.sub(r"\s+", " ", raw)[:3500]
                            break
                except Exception:
                    continue
        if text and len(text) >= 80:
            return text
        return None
    except asyncio.CancelledError:
        raise
    except Exception as e:
        logger.debug(f"job_description_fetcher: {url[:50]}… → {e}")
        return None
