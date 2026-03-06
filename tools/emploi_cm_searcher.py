"""
Scraper pour Emploi.cm — récupère les offres d'emploi depuis recherche-jobs-cameroun.
Retourne le format standard GoldArmy avec description complète (page de détail si disponible).
"""
import asyncio
import aiohttp
import re
from typing import List, Dict, Any, Optional
from loguru import logger
from bs4 import BeautifulSoup


BASE_URL = "https://www.emploi.cm"
SEARCH_URL = f"{BASE_URL}/recherche-jobs-cameroun"

# User-Agent commun
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
}


class EmploiCmSearcher:
    """Récupère les offres d'emploi depuis Emploi.cm (Cameroun), avec détails complets."""

    def __init__(self, timeout: int = 25):
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.session = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(timeout=self.timeout)
        return self.session

    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()

    def _is_detail_url(self, url: str) -> bool:
        """Vrai si l'URL pointe vers une page d'offre (détail), pas la liste."""
        if not url or url.strip() == SEARCH_URL:
            return False
        u = url.lower().strip()
        if "recherche-jobs" in u or "recruteur" in u:
            return False
        return "/offre-emploi-cameroun/" in u or "/node/" in u or "/offre" in u or (BASE_URL in u and u != SEARCH_URL.lower())

    async def _fetch_detail_page(self, session: aiohttp.ClientSession, url: str) -> Optional[Dict[str, Any]]:
        """Charge la page de détail d'une offre et en extrait le contenu complet."""
        if not self._is_detail_url(url):
            return None
        try:
            full_url = url if url.startswith("http") else f"{BASE_URL}{url}"
            async with session.get(full_url, headers=HEADERS) as resp:
                if resp.status != 200:
                    return None
                html = await resp.text()
        except Exception as e:
            logger.debug(f"Emploi.cm detail fetch error {url}: {e}")
            return None
        soup = BeautifulSoup(html, "html.parser")
        # Zones de contenu typiques Drupal / contenu principal
        main = (
            soup.select_one(".node__content")
            or soup.select_one(".field-name-body")
            or soup.select_one(".content .field")
            or soup.select_one("article .content")
            or soup.select_one("[class*='field-name-body']")
            or soup.select_one(".region-content")
            or soup.select_one("main")
        )
        if not main:
            main = soup.find("body")
        text_parts = []
        if main:
            for node in main.select(".field-item, .field__item, p, li, div"):
                t = (node.get_text(separator=" ", strip=True) or "").strip()
                if t and len(t) > 2:
                    text_parts.append(t)
        if not text_parts:
            text_parts = [main.get_text(separator="\n", strip=True)] if main else [soup.get_text(separator="\n", strip=True)]
        full_text = "\n\n".join(t for t in text_parts if t)[:15000]
        # Extraire compétences / mots-clés si présents (liste de tags)
        skills = []
        for tag in soup.select(".field-name-field-competences .field-item, .field--name-field-competences a, [class*='tag']"):
            s = (tag.get_text(strip=True) or "").strip()
            if s and len(s) < 80:
                skills.append(s)
        return {"description": full_text, "required_skills": skills[:30]}

    async def search_jobs(
        self,
        keywords: str = "",
        location: str = "",
        limit: int = 50,
        full_details: bool = True,
        **kwargs,
    ) -> List[Dict[str, Any]]:
        """
        Scrape la page recherche-jobs-cameroun et retourne les offres au format standard.
        Si full_details=True (défaut), charge chaque page de détail pour avoir la description complète.
        """
        jobs = []
        try:
            session = await self._get_session()
            async with session.get(SEARCH_URL, headers=HEADERS) as response:
                if response.status != 200:
                    logger.warning(f"Emploi.cm HTTP {response.status}")
                    return []
                html = await response.text()

            soup = BeautifulSoup(html, "html.parser")

            # Stratégie 1 : structure réelle du site (card.card-job avec data-href, h3, .card-job-description, ul li, time)
            blocks = (
                soup.select(".card.card-job")
                or soup.select(".card-job")
                or soup.select(".view-content .views-row")
                or soup.select(".views-row")
                or soup.select("article.job")
                or soup.select(".job-item")
                or soup.select(".search-result")
                or soup.select("[class*='job']")
            )

            if not blocks:
                # Stratégie 2 : blocs délimités par chaque h2/h3 (titre de poste)
                blocks = self._extract_blocks_by_headings(soup)

            for node in blocks[: max(limit, 60)]:
                job = self._parse_job_node(node)
                if job and job.get("title"):
                    job["source"] = "Emploi.cm"
                    job["id"] = job.get("id") or f"emploi-cm-{abs(hash(job.get('url', '') + job.get('title', '')))}"
                    jobs.append(job)

            if not jobs:
                jobs = self._parse_fallback(html, limit)

            # Enrichir avec les détails complets (page de détail) si demandé
            if full_details and jobs:
                jobs = await self._enrich_with_full_details(session, jobs, limit)

            logger.info(f"📄 Emploi.cm: {len(jobs)} offres récupérées (détails complets: {full_details})")
        except Exception as e:
            logger.error(f"Emploi.cm scraper error: {e}")
        return jobs[: limit if limit else 50]

    async def _enrich_with_full_details(
        self, session: aiohttp.ClientSession, jobs: List[Dict[str, Any]], limit: int
    ) -> List[Dict[str, Any]]:
        """Charge la page de détail pour chaque offre et met à jour description (et skills)."""
        semaphore = asyncio.Semaphore(3)
        to_fetch = [j for j in jobs if self._is_detail_url(j.get("url", ""))]
        if not to_fetch:
            return jobs
        # On limite le nombre de requêtes détail pour ne pas surcharger le site
        to_fetch = to_fetch[: min(limit or 50, 30)]

        async def fetch_one(job: Dict[str, Any]) -> None:
            async with semaphore:
                detail = await self._fetch_detail_page(session, job.get("url", ""))
                if detail and detail.get("description"):
                    job["description"] = detail["description"]
                    if detail.get("required_skills"):
                        job["required_skills"] = detail["required_skills"]

        await asyncio.gather(*[fetch_one(j) for j in to_fetch])
        return jobs

    def _extract_blocks_by_headings(self, soup: BeautifulSoup) -> List:
        """Extrait des blocs : chaque h2/h3 + contenu jusqu'au prochain h2/h3 (sans modifier l'arbre)."""
        blocks = []
        # Titres de section à ignorer (pas des intitulés de poste)
        skip_titles = ("rechercher un emploi", "offres d'emploi trouvées", "tous les emplois", "emplois commercial", "emplois it", "emplois management")
        headings = soup.find_all(["h2", "h3"])
        for i, h in enumerate(headings):
            title_text = (h.get_text() or "").strip()
            if len(title_text) < 3 or len(title_text) > 250:
                continue
            if any(skip in title_text.lower() for skip in skip_titles):
                continue
            # Contenu du bloc : ce titre + frères suivants jusqu'au prochain h2/h3
            parts = [str(h)]
            sib = h.find_next_sibling()
            while sib and sib.name not in ("h2", "h3"):
                parts.append(str(sib))
                sib = sib.find_next_sibling()
            block_html = "<div>" + "".join(parts) + "</div>"
            blocks.append(BeautifulSoup(block_html, "html.parser"))
        return blocks

    def _parse_job_node(self, node) -> Optional[Dict[str, Any]]:
        """Parse un nœud HTML (ex: .card.card-job) selon la structure réelle du site."""
        if isinstance(node, str):
            return None
        soup = node if isinstance(node, BeautifulSoup) else BeautifulSoup(str(node), "html.parser")
        root = soup.find() if hasattr(soup, "find") else soup
        if root is None:
            root = soup

        title = ""
        company = "N.C."
        description = ""
        location = "Cameroun"
        contract = ""
        posted_date = ""
        url = SEARCH_URL
        required_skills = []

        # 1) URL de la page détail : data-href sur la card, ou lien du titre (h3 a)
        data_href = root.get("data-href") if hasattr(root, "get") else None
        if data_href and ("/offre-emploi-cameroun/" in (data_href or "")):
            url = (data_href or "").strip()
            if url and not url.startswith("http"):
                url = f"{BASE_URL}{url}"
        if url == SEARCH_URL:
            a_detail = root.select_one("h3 a[href*='/offre-emploi-cameroun/']") or root.select_one("a[href*='/offre-emploi-cameroun/']")
            if a_detail and a_detail.get("href"):
                raw = (a_detail["href"] or "").strip()
                if raw and "recruteur" not in raw:
                    url = raw if raw.startswith("http") else f"{BASE_URL}{raw}"

        # 2) Titre : h3 > a (texte du lien)
        title_el = root.select_one("h3 a") or root.select_one("h2 a")
        if title_el:
            title = (title_el.get_text(strip=True) or "").strip()

        # 3) Entreprise : .card-job-company ou .company-name (lien recruteur)
        company_el = root.select_one(".card-job-company, .company-name") or root.select_one("a[href*='/recruteur/']")
        if company_el:
            company = (company_el.get_text(strip=True) or "").strip() or "N.C."

        # 4) Description : .card-job-description p
        desc_el = root.select_one(".card-job-description p") or root.select_one(".card-job-description")
        if desc_el:
            description = desc_el.get_text(separator=" ", strip=True)[:5000]
        if not description:
            desc_el = root.select_one(".field-name-body .field-item, .description, .job-description, .body")
            if desc_el:
                description = desc_el.get_text(separator=" ", strip=True)[:5000]

        # 5) Métadonnées : ul li (Niveau d'études, Niveau d'expérience, Contrat, Région, Compétences clés)
        for li in root.select("ul li"):
            raw_li = (li.get_text() or "").strip()
            strong = li.select_one("strong")
            value = (strong.get_text(strip=True) or "").strip() if strong else raw_li
            if "Région de" in raw_li and value:
                location = value.replace("&amp;", "&").strip()
            elif "Contrat proposé" in raw_li and value:
                contract = value.replace("&amp;", "&").strip()
            elif "Niveau d'études requis" in raw_li or "Niveau d´études requis" in raw_li:
                pass  # optionnel : garder dans description ou champ dédié
            elif "Niveau d'expérience" in raw_li:
                pass
            elif "Compétences clés" in raw_li and value:
                required_skills = [s.strip() for s in re.split(r"\s*[-–]\s*", value) if s.strip()][:30]

        # 6) Date : time (datetime ou texte)
        time_el = root.select_one("time")
        if time_el:
            posted_date = (time_el.get("datetime") or time_el.get_text(strip=True) or "").strip()

        # Fallback métadonnées par regex si pas trouvé dans ul/li
        text = root.get_text(separator="\n", strip=True) if hasattr(root, "get_text") else ""
        if not location or location == "Cameroun":
            m = re.search(r"Région de\s*:\s*([^\n<]+)", text)
            if m:
                location = m.group(1).strip().replace("&amp;", "&")
        if not contract:
            m = re.search(r"Contrat proposé\s*:\s*([^\n<]+)", text)
            if m:
                contract = m.group(1).strip().replace("&amp;", "&")
        if not posted_date and re.search(r"\d{2}\.\d{2}\.\d{4}", text):
            m = re.search(r"(\d{2}\.\d{2}\.\d{4})", text)
            if m:
                posted_date = m.group(1)
        if not title and text:
            lines = [l.strip() for l in text.split("\n") if len(l.strip()) > 5]
            if lines:
                title = lines[0][:200]

        return {
            "id": None,
            "title": title or "Offre Emploi.cm",
            "company": company,
            "location": location,
            "description": description or (text[:5000] if text else ""),
            "url": url,
            "posted_date": posted_date,
            "job_type": contract or "Non spécifié",
            "salary": "Non spécifié",
            "required_skills": required_skills,
            "scraped": True,
        }

    def _parse_fallback(self, html: str, limit: int) -> List[Dict[str, Any]]:
        """Fallback : découper par h3 (titres d'offres) dans le texte extrait du HTML."""
        jobs = []
        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text(separator="\n", strip=True)
        # Découper par lignes qui ressemblent à un titre (pas trop long, avant "Région" / "N.C.")
        h3s = soup.find_all("h3")
        for h3 in h3s[:limit]:
            title = (h3.get_text() or "").strip()
            if len(title) < 5 or len(title) > 200:
                continue
            company = "N.C."
            link = h3.find_parent("a") or h3.find("a")
            if link and link.get("href", "").find("/recruteur/") >= 0:
                company = (link.get_text() or "N.C.").strip()
            next_el = h3.find_next_sibling()
            block_text = ""
            while next_el and next_el.name not in ("h2", "h3"):
                block_text += (next_el.get_text(separator=" ", strip=True) or "") + "\n"
                next_el = next_el.find_next_sibling()
            loc = "Cameroun"
            m = re.search(r"Région de\s*:\s*([^\n-]+)", block_text)
            if m:
                loc = m.group(1).strip()
            date_match = re.search(r"(\d{2}\.\d{2}\.\d{4})", block_text)
            posted = date_match.group(1) if date_match else ""
            company_in_block = re.search(r"\[([^\]]+)\]\(https://www\.emploi\.cm/recruteur", block_text)
            if company_in_block:
                company = company_in_block.group(1).strip()
            jobs.append({
                "id": f"emploi-cm-{abs(hash(title + company))}",
                "title": title,
                "company": company,
                "location": loc,
                "description": block_text[:1500],
                "url": SEARCH_URL,
                "posted_date": posted,
                "job_type": "Non spécifié",
                "salary": "Non spécifié",
                "required_skills": [],
                "source": "Emploi.cm",
                "scraped": True,
            })
        return jobs
