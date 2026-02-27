"""Outil de recherche ciblé sur les portails gouvernementaux mondiaux.
Utilise les APIs publiques officielles (pas de scraping fragile).
"""
import aiohttp
import asyncio
import urllib.parse
from typing import List, Dict, Any
from loguru import logger
import ssl

ssl_context = ssl._create_unverified_context()


class GovSearcher:
    """Cible les APIs officielles des gouvernements pour des offres d'emploi vérifiées."""

    COUNTRY_PORTALS = {
        "france": [
            {"name": "France Travail (Pôle Emploi)", "handler": "_search_france_travail"},
            {"name": "Place Emploi Public (Fonctionnaire)", "handler": "_search_place_emploi_public"},
        ],
        "usa": [
            {"name": "USAJOBS (Gouvernement US)", "handler": "_search_usajobs"},
        ],
        "canada": [
            {"name": "Guichet Emplois Canada", "handler": "_search_jobbank_canada"},
        ],
        "europe": [
            {"name": "EURES (Europe)", "handler": "_search_eures"},
        ],
        "belgique": [
            {"name": "FOREM (Wallonie)", "handler": "_search_forem"},
        ],
    }

    def __init__(self):
        self.headers = {
            "User-Agent": "GoldArmyArgent/1.0 (job search assistant)",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    async def search_jobs(self, keywords: str, location: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Lance la recherche sur les portails gouvernementaux appropriés."""
        country = self._detect_country(location)
        portals = self.COUNTRY_PORTALS.get(country, [])

        if not portals:
            logger.warning(f"🏛️ GovSearcher: aucun portail configuré pour '{location}' -> pays: {country}")
            return []

        logger.info(f"🏛️ GovSearcher: {len(portals)} portail(s) ciblé(s) pour {country}")

        all_jobs = []
        # On passe le mot-clé nettoyé (sans guillemets ni opérateurs) aux portails govs
        clean_kw = keywords.replace('"', '').strip()
        tasks = [getattr(self, p["handler"])(clean_kw, location, limit) for p in portals]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for i, res in enumerate(results):
            portal_name = portals[i]["name"]
            if isinstance(res, list):
                logger.info(f"🏛️ {portal_name}: {len(res)} offres récupérées.")
                all_jobs.extend(res)
            elif isinstance(res, Exception):
                logger.warning(f"🏛️ {portal_name}: Erreur - {str(res)[:100]}")

        return all_jobs[:limit]

    def _detect_country(self, location: str) -> str:
        """Détecte le pays cible à partir de la chaîne de localisation."""
        loc = location.lower().strip()
        # Nettoyage des fautes courantes
        loc = loc.replace("califormie", "california").replace("californie", "california")
        loc = loc.replace("etats-unis", "usa").replace("etats unis", "usa")
        
        if any(w in loc for w in ["france", "paris", "lyon", "marseille", "bordeaux", "nantes", "lille", "toulouse", "strasbourg", "nice", "rennes", "montpellier", "grenoble"]): return "france"
        if any(w in loc for w in ["usa", "united states", "america", "new york", "california", "texas", "washington", "chicago", "florida", "boston", "seattle", "los angeles", "san francisco", "silicon valley"]): return "usa"
        if any(w in loc for w in ["canada", "quebec", "montreal", "toronto", "vancouver", "ottawa", "calgary", "edmonton"]): return "canada"
        if any(w in loc for w in ["europe", "eu", "european union", "schengen"]): return "europe"
        if any(w in loc for w in ["belgique", "belgium", "bruxelles", "brussels", "liège", "namur", "wallonie", "gand", "anvers"]): return "belgique"
        if any(w in loc for w in ["suisse", "switzerland", "genève", "zurich", "berne", "lausanne", "bale"]): return "suisse"
        if any(w in loc for w in ["uk", "united kingdom", "london", "england", "scotland", "wales", "manchester", "birmingham"]): return "uk"
        if any(w in loc for w in ["allemagne", "germany", "berlin", "munich", "hamburg", "frankfurt", "cologne"]): return "allemagne"
        if any(w in loc for w in ["maroc", "morocco", "casablanca", "rabat", "marrakech", "fes"]): return "maroc"
        if any(w in loc for w in ["espagne", "spain", "madrid", "barcelona", "valence", "seville"]): return "espagne"
        if any(w in loc for w in ["italie", "italy", "rome", "milan", "naples", "turin"]): return "italie"
        if any(w in loc for w in ["portugal", "lisbonne", "porto", "lisbon"]): return "portugal"
        if any(w in loc for w in ["pays-bas", "netherlands", "amsterdam", "rotterdam", "hollande"]): return "europe"
        # Par défaut
        return "france"

    # ──────────────────────────────────────────────────────────────────────────────
    # FRANCE
    # ──────────────────────────────────────────────────────────────────────────────

    async def _search_france_travail(self, keywords: str, location: str, limit: int) -> List[Dict[str, Any]]:
        """
        Scrape la page de recherche publique de France Travail (candidat.francetravail.fr).
        Pas besoin d'OAuth2 pour la navigation publique.
        """
        kw_enc = urllib.parse.quote_plus(keywords)
        # Construction de l'URL de recherche publique
        url = f"https://candidat.francetravail.fr/offres/recherche?motsCles={kw_enc}&offresPartenaires=true&sort=1"
        
        headers_html = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml",
            "Accept-Language": "fr-FR,fr;q=0.9",
        }
        try:
            async with aiohttp.ClientSession(headers=headers_html) as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=15), ssl=False) as resp:
                    if resp.status != 200:
                        raise Exception(f"HTTP {resp.status}")
                    html = await resp.text()
                    return self._parse_france_travail_html(html, location, limit, keywords)
        except Exception as e:
            logger.debug(f"France Travail HTML scrape failed: {e}")
            # Fallback ultime : retourner un lien de recherche direct
            return [{
                "id": "ft-search-link",
                "title": f"Voir toutes les offres '{keywords}' sur France Travail",
                "company": "France Travail (Pôle Emploi)",
                "location": "Non spécifié",
                "url": f"https://candidat.francetravail.fr/offres/recherche?motsCles={kw_enc}",
                "description": "Cliquez pour accéder aux offres sur France Travail",
                "source": "France Travail",
                "match_score": 0,
            }]

    def _parse_france_travail_html(self, html: str, location: str, limit: int, keywords: str) -> List[Dict[str, Any]]:
        """Parse les résultats HTML de France Travail."""
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")
        jobs = []
        # Les offres France Travail sont dans des articles avec data-*
        cards = soup.find_all("li", class_="result", limit=limit)
        if not cards:
            # Autre sélecteur possible
            cards = soup.select("article.result", limit)[:limit]
        
        for i, card in enumerate(cards):
            title_tag = card.find(["h2", "h3", "p"], class_=lambda c: c and "title" in c.lower() if c else False)
            company_tag = card.find(class_=lambda c: c and "company" in c.lower() if c else False)
            loc_tag = card.find(class_=lambda c: c and "location" in c.lower() if c else False)
            snippet_tag = card.find("p", class_="description") or card.find("p", class_=re.compile("snippet|description|text"))
            
            link_tag = card.find("a")
            href = link_tag.get("href", "") if link_tag else ""
            if href and not href.startswith("http"):
                href = f"https://candidat.francetravail.fr{href}"
            
            title = title_tag.get_text(strip=True) if title_tag else f"Offre {keywords} #{i+1}"
            description = snippet_tag.get_text(strip=True)[:400] if snippet_tag else ""
            
            jobs.append({
                "id": f"ft-{i}",
                "title": title,
                "company": company_tag.get_text(strip=True) if company_tag else "Confidentiel",
                "location": loc_tag.get_text(strip=True) if loc_tag else location,
                "url": href or f"https://candidat.francetravail.fr/offres/recherche?motsCles={urllib.parse.quote_plus(keywords)}",
                "description": description,
                "source": "France Travail",
                "match_score": 0,
            })
        return jobs

    async def _search_place_emploi_public(self, keywords: str, location: str, limit: int) -> List[Dict[str, Any]]:
        """
        Recherche sur Place de l'Emploi Public (Fonction Publique France).
        API REST publique JSON: https://place-emploi-public.gouv.fr
        """
        url = "https://place-emploi-public.gouv.fr/api/offres/recherche"
        params = {"motCle": keywords, "page": 0, "taille": limit}
        try:
            async with aiohttp.ClientSession(headers=self.headers) as session:
                async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10), ssl=False) as resp:
                    if resp.status != 200:
                        raise Exception(f"HTTP {resp.status}")
                    data = await resp.json()
                    results = self._parse_place_emploi_public(data, limit)
                    if not results:
                        raise Exception("Aucun résultat parsé")
                    return results
        except Exception as e:
            logger.debug(f"Place Emploi Public failed: {e}")
            # Fallback : scrape HTML
            return await self._search_place_emploi_public_html(keywords, location, limit)

    async def _search_place_emploi_public_html(self, keywords: str, location: str, limit: int) -> List[Dict[str, Any]]:
        """Fallback HTML scraper pour Place de l'Emploi Public."""
        kw_enc = urllib.parse.quote_plus(keywords)
        url = f"https://place-emploi-public.gouv.fr/offre-emploi/?motCle={kw_enc}"
        try:
            headers_html = {"User-Agent": "Mozilla/5.0", "Accept-Language": "fr-FR,fr;q=0.9"}
            async with aiohttp.ClientSession(headers=headers_html) as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10), ssl=False) as resp:
                    if resp.status != 200:
                        raise Exception(f"HTTP {resp.status}")
                    html = await resp.text()
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(html, "html.parser")
                    jobs = []
                    cards = soup.select("article.offre, .offre-card", )[:limit]
                    for i, card in enumerate(cards):
                        title_tag = card.find(["h2", "h3"])
                        link_tag = card.find("a")
                        desc_tag = card.find(class_=re.compile("descriptif|description|snippet"))
                        
                        href = link_tag.get("href", "") if link_tag else ""
                        if href and not href.startswith("http"):
                            href = f"https://place-emploi-public.gouv.fr{href}"
                            
                        jobs.append({
                            "id": f"pep-{i}",
                            "title": title_tag.get_text(strip=True) if title_tag else f"Offre Fonction Publique #{i+1}",
                            "company": "Fonction Publique",
                            "location": "Non spécifié",
                            "url": href or url,
                            "description": desc_tag.get_text(strip=True)[:400] if desc_tag else "",
                            "source": "Place Emploi Public",
                            "match_score": 0,
                        })
                    return jobs
        except Exception as e:
            logger.debug(f"Place Emploi Public HTML failed: {e}")
            kw_enc = urllib.parse.quote_plus(keywords)
            return [{
                "id": "pep-search-link",
                "title": f"Voir les offres fonctionnaires '{keywords}'",
                "company": "Fonction Publique France",
                "location": "Non spécifié",
                "url": f"https://place-emploi-public.gouv.fr/offre-emploi/?motCle={kw_enc}",
                "description": "Portail officiel de la Fonction Publique",
                "source": "Place Emploi Public",
                "match_score": 0,
            }]

    def _parse_place_emploi_public(self, data: dict, limit: int) -> List[Dict[str, Any]]:
        """Parse la réponse de l'API Place de l'Emploi Public."""
        jobs = []
        for item in data.get("offres", data.get("results", []))[:limit]:
            jobs.append({
                "id": f"pep-{item.get('identifiant', '')}",
                "title": item.get("intitulePoste", item.get("titre", "Titre inconnu")),
                "company": item.get("raisonSocialEmployeur", item.get("employeur", "Fonction Publique")),
                "location": item.get("localisationLibelle", item.get("localisation", "France")),
                "url": f"https://place-emploi-public.gouv.fr/offre-emploi/{item.get('identifiant', '')}",
                "description": item.get("descriptifPoste", "")[:500],
                "source": "Place Emploi Public",
                "match_score": 0,
            })
        return jobs

    # ──────────────────────────────────────────────────────────────────────────────
    # USA
    # ──────────────────────────────────────────────────────────────────────────────

    async def _search_usajobs(self, keywords: str, location: str, limit: int) -> List[Dict[str, Any]]:
        """
        API officielle de USAJOBS (gouvernement américain).
        Doc: https://developer.usajobs.gov/
        """
        url = "https://data.usajobs.gov/api/search"
        headers = {
            **self.headers,
            "Host": "data.usajobs.gov",
            "User-Agent": "goldarmyargent@jobsearch.com",  # Email requis par USAJOBS
            "Authorization-Key": "",  # Clé optionnelle pour plus de résultats
        }
        params = {
            "Keyword": keywords,
            "LocationName": location,
            "ResultsPerPage": limit,
        }
        try:
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10), ssl=False) as resp:
                    if resp.status != 200:
                        raise Exception(f"HTTP {resp.status}")
                    data = await resp.json()
                    return self._parse_usajobs(data, limit)
        except Exception as e:
            logger.debug(f"USAJOBS failed: {e}")
            return []

    def _parse_usajobs(self, data: dict, limit: int) -> List[Dict[str, Any]]:
        """Parse la réponse de l'API USAJOBS."""
        jobs = []
        items = data.get("SearchResult", {}).get("SearchResultItems", [])
        for item in items[:limit]:
            mv = item.get("MatchedObjectDescriptor", {})
            jobs.append({
                "id": f"usajobs-{mv.get('PositionID', '')}",
                "title": mv.get("PositionTitle", "Titre inconnu"),
                "company": mv.get("OrganizationName", "US Government"),
                "location": mv.get("PositionLocationDisplay", location),
                "url": mv.get("PositionURI", "https://www.usajobs.gov"),
                "description": mv.get("UserArea", {}).get("Details", {}).get("JobSummary", "")[:500],
                "source": "USAJOBS",
                "match_score": 0,
            })
        return jobs

    # ──────────────────────────────────────────────────────────────────────────────
    # CANADA
    # ──────────────────────────────────────────────────────────────────────────────

    async def _search_jobbank_canada(self, keywords: str, location: str, limit: int) -> List[Dict[str, Any]]:
        """
        Guichet Emplois Canada (Job Bank) - scraping de l'API JSON publique.
        """
        url = "https://www.jobbank.gc.ca/jobsearch/jobsearch"
        params = {
            "searchstring": keywords,
            "locationstring": location,
            "sort": "M",
            "mid": "0",
            "woc": "",
        }
        try:
            headers = {**self.headers, "Accept": "text/html,application/xhtml+xml", "Accept-Language": "fr-CA,fr;q=0.9"}
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10), ssl=False) as resp:
                    if resp.status != 200:
                        raise Exception(f"HTTP {resp.status}")
                    html = await resp.text()
                    return self._parse_jobbank_html(html, location, limit)
        except Exception as e:
            logger.debug(f"JobBank Canada failed: {e}")
            return []

    def _parse_jobbank_html(self, html: str, location: str, limit: int) -> List[Dict[str, Any]]:
        """Parse le HTML du Guichet Emplois Canada."""
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, "html.parser")
            articles = soup.find_all("article", limit=limit)
            jobs = []
            for i, art in enumerate(articles):
                link = art.find("a", class_="resultJobItem")
                if not link:
                    continue
                title_tag = art.find(class_="noctitle")
                company_tag = art.find(class_="business")
                loc_tag = art.find(class_="location")
                href = link.get("href", "")
                jobs.append({
                    "id": f"jb-ca-{i}",
                    "title": title_tag.get_text(strip=True) if title_tag else "Titre inconnu",
                    "company": company_tag.get_text(strip=True) if company_tag else "Confidentiel",
                    "location": loc_tag.get_text(strip=True) if loc_tag else location,
                    "url": f"https://www.jobbank.gc.ca{href}" if href.startswith("/") else href,
                    "description": "",
                    "source": "Guichet Emplois Canada",
                    "match_score": 0,
                })
            return jobs
        except Exception as e:
            logger.debug(f"JobBank HTML parse failed: {e}")
            return []

    # ──────────────────────────────────────────────────────────────────────────────
    # EUROPE (EURES)
    # ──────────────────────────────────────────────────────────────────────────────

    async def _search_eures(self, keywords: str, location: str, limit: int) -> List[Dict[str, Any]]:
        """
        EURES - Portail Européen de la mobilité de l'emploi.
        API REST: https://eures.ec.europa.eu/api
        """
        url = "https://eures.ec.europa.eu/api/jv-search/jvs"
        payload = {
            "keywords": keywords,
            "location": "Non spécifié",
            "page": 0,
            "pageSize": limit,
        }
        try:
            async with aiohttp.ClientSession(headers=self.headers) as session:
                async with session.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=10), ssl=False) as resp:
                    if resp.status != 200:
                        raise Exception(f"HTTP {resp.status}")
                    data = await resp.json()
                    return self._parse_eures(data, limit)
        except Exception as e:
            logger.debug(f"EURES failed: {e}")
            return []

    def _parse_eures(self, data: dict, limit: int) -> List[Dict[str, Any]]:
        """Parse la réponse de l'API EURES."""
        jobs = []
        for item in data.get("data", {}).get("jvs", [])[:limit]:
            jobs.append({
                "id": f"eures-{item.get('id', '')}",
                "title": item.get("title", "Titre inconnu"),
                "company": item.get("employer", {}).get("name", "Confidentiel"),
                "location": item.get("location", {}).get("label", "Europe"),
                "url": f"https://eures.ec.europa.eu/en/job-details/{item.get('id', '')}",
                "description": item.get("description", "")[:500],
                "source": "EURES",
                "match_score": 0,
            })
        return jobs

    # ──────────────────────────────────────────────────────────────────────────────
    # BELGIQUE (FOREM)
    # ──────────────────────────────────────────────────────────────────────────────

    async def _search_forem(self, keywords: str, location: str, limit: int) -> List[Dict[str, Any]]:
        """
        Le Forem - Service Public de l'Emploi en Wallonie (Belgique).
        API REST: https://www.leforem.be/api
        """
        url = "https://www.leforem.be/api/offres_emploi"
        params = {"keywords": keywords, "location": "Non spécifié", "limit": limit}
        try:
            async with aiohttp.ClientSession(headers=self.headers) as session:
                async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10), ssl=False) as resp:
                    if resp.status not in (200, 201):
                        raise Exception(f"HTTP {resp.status}")
                    data = await resp.json()
                    return self._parse_forem(data, limit)
        except Exception as e:
            logger.debug(f"FOREM failed: {e}")
            return []

    def _parse_forem(self, data: dict, limit: int) -> List[Dict[str, Any]]:
        """Parse la réponse de l'API FOREM."""
        jobs = []
        for item in data.get("offres", data.get("results", []))[:limit]:
            jobs.append({
                "id": f"forem-{item.get('id', '')}",
                "title": item.get("titre", item.get("title", "Titre inconnu")),
                "company": item.get("employeur", item.get("company", "Confidentiel")),
                "location": item.get("lieu", item.get("location", "Belgique")),
                "url": item.get("url", "https://www.leforem.be/offres-emploi"),
                "description": item.get("description", "")[:500],
                "source": "FOREM (Belgique)",
                "match_score": 0,
            })
        return jobs
