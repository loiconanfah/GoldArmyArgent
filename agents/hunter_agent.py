"""Agent Hunter spécialisé dans la traque d'opportunités sur les APIs."""
import asyncio
from typing import List, Dict, Any
from loguru import logger
from core.agent_base import BaseAgent
from config.settings import settings

class HunterAgent(BaseAgent):
    """Agent chargé de requêter les APIs de recherche d'emploi en parallèle."""
    
    def __init__(self, **kwargs):
        kwargs.setdefault("agent_type", "hunter")
        kwargs.setdefault("name", "Hunter")
        super().__init__(**kwargs)

    async def think(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Prépare la stratégie de recherche (APIs à utiliser, mots-clés)."""
        criteria = task.get("criteria", {})
        keywords_list = criteria.get("keywords_list", [])
        exclude_list = criteria.get("exclude_list", [])
        location = criteria.get("location", "Paris, France")
        loc_lower = location.lower()
        loc_lower = loc_lower.replace("califormie", "california").replace("californie", "california")
        
        # Sources de base (disponibles partout)
        apis_to_use = ["jooble", "jsearch", "google_jobs", "findwork"]
        
        # Sources spécifiques France / Europe
        if any(w in loc_lower for w in ["france", "paris", "lyon", "marseille", "bordeaux", "nantes", "lille", "europe", "suisse", "belgique", "uk", "london", "allemagne", "berlin", "espagne", "madrid", "italie", "rome"]):
            apis_to_use += ["linkedin", "indeed_fr", "glassdoor", "gov"]
        # Sources spécifiques Amériques
        elif any(w in loc_lower for w in ["usa", "united states", "california", "new york", "texas", "canada", "montreal", "toronto", "vancouver", "chicago", "seattle", "boston", "silicon valley", "florida"]):
            apis_to_use += ["linkedin", "indeed"]
        # Reste du monde
        else:
            apis_to_use += ["linkedin", "indeed_fr"]
            
        return {
            "keywords": keywords_list,
            "exclude": exclude_list,
            "location": location,
            "apis": apis_to_use,
            "limit": task.get("limit", 10),
            "job_type": criteria.get("job_type", "emploi")
        }

    async def act(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Exécute les recherches en parallèle sur toutes les APIs sélectionnées."""
        keywords = plan.get("keywords", [])
        location = plan.get("location", "")
        apis = plan.get("apis", [])
        
        # SNIPER SWARM 7.0: Pool massif pour maximiser les opportunités.
        limit = plan.get("limit", 10)
        api_limit = max(200, limit * 20) 
        job_type = plan.get("job_type", "emploi")
        exclude = [e.lower().strip() for e in plan.get("exclude", [])]
        
        all_jobs = []
        
        # Stratégie de Swarm : On découpe les mots-clés par petits groupes pour paralléliser l'appel aux APIs
        logger.info(f"🚀 SWARM ACTIVÉ: Traque massive sur {len(apis)} sources | Localisation: {location}")
        logger.info(f"📝 Mots-clés: {keywords} | Exclusions locales: {exclude[:5]}...")

        # Sémaphores pour stabiliser Render
        semaphore = asyncio.Semaphore(15)

        async def _swarm_search(kw: str, api: str):
            async with semaphore:
                search_queries = [kw]
                if job_type in ["alternance", "stage"]:
                    search_queries.append(f"{kw} {job_type}")
                
                tasks = []
                for sq in search_queries:
                    if api == "jooble" and settings.jooble_api_key:
                        tasks.append(self._search_jooble(sq, location, api_limit))
                    elif api == "jsearch" and settings.rapidapi_key:
                        tasks.append(self._search_jsearch(sq, location, api_limit))
                    elif api == "glassdoor" and settings.rapidapi_key:
                        tasks.append(self._search_glassdoor(sq, location, api_limit))
                    elif api == "indeed":
                        tasks.append(self._search_indeed(sq, location, api_limit))
                    elif api == "gov":
                        tasks.append(self._search_gov(kw, location, api_limit))
                    elif api == "findwork":
                        tasks.append(self._search_findwork(sq, location, api_limit))
                    elif api == "linkedin":
                        tasks.append(self._search_linkedin(kw, location, api_limit))
                    elif api == "indeed_fr":
                        tasks.append(self._search_indeed_fr(kw, location, api_limit))
                    elif api == "google_jobs":
                        tasks.append(self._search_google_jobs(kw, location, api_limit))
                
                if not tasks:
                    return []
                
                results = await asyncio.gather(*tasks, return_exceptions=True)
                jobs = []
                for res in results:
                    if isinstance(res, list):
                        jobs.extend(res)
                return jobs

        # Déclenchement du Swarm
        swarm_tasks = []
        for kw in keywords:
            for api in apis:
                swarm_tasks.append(_swarm_search(kw, api))

        if not swarm_tasks:
            logger.warning("⚠️ Aucune tâche de recherche lancée (Clés API manquantes ?)")
            return {"success": False, "jobs": []}

        # Exécution du Swarm
        swarm_results = await asyncio.gather(*swarm_tasks, return_exceptions=True)
        
        for res in swarm_results:
            if isinstance(res, list):
                all_jobs.extend(res)
            elif isinstance(res, Exception):
                logger.error(f"🔴 Erreur Swarm: {res}")

        
        # 1. Filtrage par exclusions (côté client)
        if exclude:
            before = len(all_jobs)
            all_jobs = self._filter_by_exclusions(all_jobs, exclude)
            logger.info(f"🧹 Exclusion filtrée: {before} → {len(all_jobs)} offres")

        # 1.b Filtrage par localisation
        all_jobs = self._filter_strict_precision(all_jobs, location, job_type)

        # 2. Dédoublonnage par titre+company
        unique_jobs = []
        seen = set()
        for job in all_jobs:
            key = f"{job.get('title', '')}-{job.get('company', '')}".lower()
            if key not in seen:
                seen.add(key)
                unique_jobs.append(job)

        logger.info(f"🎯 Swarm a ramené {len(unique_jobs)} offres brutes uniques.")
        return {"success": True, "jobs": unique_jobs}


    def _filter_by_exclusions(self, jobs: list, exclude: list) -> list:
        """Filtre les offres dont le titre ou la description contient un terme exclu."""
        result = []
        for job in jobs:
            text = f"{job.get('title', '')} {job.get('description', '')}".lower()
            # Un job est rejeté si son titre/description contient un terme exclu
            if not any(ex in text for ex in exclude):
                result.append(job)
        return result

    async def _search_jooble(self, kw, loc, limit):
        try:
            from tools.jooble_searcher import JoobleSearcher
            searcher = JoobleSearcher(api_key=settings.jooble_api_key)
            return await searcher.search_jobs(keywords=kw, location=loc, limit=limit)
        except Exception as e:
            logger.error(f"Jooble Error: {e}")
            return []

    async def _search_findwork(self, kw, loc, limit):
        """Recherche via FindWork.dev API."""
        try:
            from tools.findwork_searcher import FindWorkSearcher
            searcher = FindWorkSearcher(api_key=settings.findwork_api_key)
            return await searcher.search_jobs(keywords=kw, location=loc, limit=limit)
        except Exception as e:
            logger.error(f"FindWork Error: {e}")
            return []
            
    def _filter_strict_precision(self, jobs: list, expected_location: str, expected_job_type: str) -> list:
        """
        Filtre impitoyable garanti sans hallucination.
        Si l'user demande un "stage", on supprime tout ce qui ressemble de loin à un CDI.
        Si l'user demande "toronto", on supprime ce qui est en France ou UK.
        """
        result = []
        loc_lower = expected_location.lower()
        type_lower = expected_job_type.lower()
        
        # Désormais, la lourde responsabilité du filtrage strict est déléguée au JudgeAgent (Gemini 3.1 Pro)
        # pour éviter les faux-positifs algorithmiques qui suppriment de vraies offres.
        return jobs

    async def _search_jsearch(self, kw, loc, limit):
        try:
            from tools.jsearch_searcher import JSearchSearcher
            searcher = JSearchSearcher(api_key=settings.rapidapi_key)
            return await searcher.search_jobs(query=f"{kw} in {loc}", limit=limit)
        except Exception as e:
            logger.error(f"JSearch Error: {e}")
            return []
            
    async def _search_glassdoor(self, kw, loc, limit):
        try:
            from tools.glassdoor_searcher import GlassdoorSearcher
            searcher = GlassdoorSearcher(api_key=settings.rapidapi_key)
            return await searcher.search_jobs(query=kw, location=loc, limit=limit)
        except Exception as e:
            logger.error(f"Glassdoor Error: {e}")
            return []

    async def _search_gov(self, kw, loc, limit):
        try:
            from tools.gov_searcher import GovSearcher
            searcher = GovSearcher()
            return await searcher.search_jobs(keywords=kw, location=loc, limit=limit)
        except Exception as e:
            logger.error(f"GovSearcher Error: {e}")
            return []

    async def _search_linkedin(self, kw, loc, limit):
        """Recherche LinkedIn Jobs (priorité élevée pour France et Amériques)."""
        try:
            from tools.linkedin_jobs_searcher import LinkedInJobsSearcher
            searcher = LinkedInJobsSearcher()
            results = await searcher.search_jobs(keywords=kw, location=loc, limit=limit)
            logger.info(f"💼 LinkedIn: {len(results)} offres pour '{kw}'")
            return results
        except Exception as e:
            logger.error(f"LinkedIn Error: {e}")
            return []

    async def _search_indeed(self, kw, loc, limit):
        """Recherche Indeed (principalement USA/Canada, liens directs d'offres)."""
        import aiohttp
        import urllib.parse
        import ssl
        import re
        try:
            kw_enc = urllib.parse.quote_plus(kw.replace('"', ''))
            loc_enc = urllib.parse.quote_plus(loc)
            url = f"https://www.indeed.com/jobs?q={kw_enc}&l={loc_enc}&sort=date"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
                "Accept-Language": "en-US,en;q=0.9",
            }
            ssl_ctx = ssl._create_unverified_context()
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=8), ssl=ssl_ctx) as resp:
                    if resp.status != 200:
                        raise Exception(f"HTTP {resp.status}")
                    html = await resp.text()

            
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, "html.parser")
            jobs = []
            cards = soup.find_all("div", class_=re.compile("job_seen_beacon|resultContent"))
            for i, card in enumerate(cards[:limit]):
                title_tag = card.find("h2", class_=re.compile("jobTitle")) or card.find("h2")
                company_tag = card.find(class_=re.compile("companyName|company"))
                loc_tag = card.find(class_=re.compile("companyLocation"))
                link = card.find("a", href=True)
                href = link.get("href", "") if link else ""
                if href and not href.startswith("http"):
                    href = f"https://www.indeed.com{href}"
                title = title_tag.get_text(strip=True) if title_tag else ""
                if not title:
                    continue
                jobs.append({
                    "id": f"indeed-{i}",
                    "title": title,
                    "company": company_tag.get_text(strip=True) if company_tag else "Confidentiel",
                    "location": loc_tag.get_text(strip=True) if loc_tag else "Non spécifié",
                    "url": href or f"https://www.indeed.com/jobs?q={kw_enc}",
                    "description": "",
                    "source": "Indeed",
                    "match_score": 0,
                })
            logger.info(f"🔍 Indeed: {len(jobs)} offres pour '{kw}'")
            return jobs
        except Exception as e:
            logger.debug(f"Indeed Error: {e}")
            return []

    async def _search_indeed_fr(self, kw, loc, limit):
        """Recherche Indeed France/Europe (fr.indeed.com, be.indeed.com, etc.)."""
        try:
            from tools.indeed_searcher import IndeedMultiSearcher
            searcher = IndeedMultiSearcher()
            results = await searcher.search_jobs(keywords=kw, location=loc, limit=limit)
            logger.info(f"🔍 Indeed FR/EU: {len(results)} offres pour '{kw}'")
            return results
        except Exception as e:
            logger.error(f"Indeed FR Error: {e}")
            return []

    async def _search_google_jobs(self, kw, loc, limit):
        """Recherche Google Jobs (offres structurées avec descriptions)."""
        try:
            from tools.google_jobs_searcher import GoogleJobsSearcher
            searcher = GoogleJobsSearcher()
            results = await searcher.search_jobs(keywords=kw, location=loc, limit=limit)
            logger.info(f"🌐 Google Jobs: {len(results)} offres pour '{kw}'")
            return results
        except Exception as e:
            logger.error(f"Google Jobs Error: {e}")
            return []
