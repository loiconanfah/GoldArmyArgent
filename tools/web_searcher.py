"""Outil de recherche web robuste pour offres d'emploi individuelles."""
import urllib.request
import urllib.parse
import ssl
import asyncio
from typing import List, Dict, Any
import re
from loguru import logger

# Désactiver vérification SSL pour simplifier
ssl_context = ssl._create_unverified_context()

class JobWebSearcher:
    """Recherche web spécialisée pour l'emploi (offres individuelles uniquement)."""
    
    async def search_jobs(self, keywords: str, location: str = "Québec", job_type: str = "stage", max_results: int = 20) -> List[Dict[str, Any]]:
        """Recherche des offres d'emploi individuelles."""
        import asyncio
        logger.info(f"🌐 Recherche Web Parallèle: '{keywords}' à '{location}'")
        
        all_jobs = []
        
        # Lancement parallèle des recherches
        tasks = [
            self._search_jobbank(keywords, location, max_results),
            self._search_general_web(keywords, location, max_results)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for res in results:
            if isinstance(res, list):
                all_jobs.extend(res)
            elif isinstance(res, Exception):
                logger.warning(f"⚠️ Une source de recherche a échoué: {res}")
                
        # Deduplication simple par URL
        unique_jobs = []
        seen_urls = set()
        
        for job in all_jobs:
            url = job.get("url")
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_jobs.append(job)
            elif not url:
                unique_jobs.append(job)
                
        logger.info(f"📊 Résultats uniques: {len(unique_jobs)} offres")
        return unique_jobs[:max_results]

    async def enrich_job_details(self, job: Dict[str, Any]) -> Dict[str, Any]:
        """Enrichit les détails d'une offre d'emploi spécifique."""
        logger.info(f"📄 Enrichissement de l'offre: {job.get('title', 'Unknown')}")
        
        try:
            url = job.get('url', '')
            if not url:
                return job
                
            # Vérifier si c'est une URL de recherche générale
            if any(path in url.lower() for path in ['/jobs?', '/search?', '/jobsearch?', '/jobs/search']):
                logger.warning(f"⚠️ Ignoring search page URL: {url}")
                return job
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, context=ssl_context, timeout=15) as response:
                html = response.read().decode('utf-8')
                
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')
            
            # Extraction selon la source
            if 'indeed.com' in url:
                return self._scrape_indeed_details(soup, job)
            elif 'linkedin.com' in url:
                return self._scrape_linkedin_details(soup, job)
            elif 'jobbank.gc.ca' in url:
                return self._scrape_jobbank_details(soup, job)
            else:
                return self._scrape_generic_details(soup, job)
                
        except Exception as e:
            logger.error(f"❌ Erreur enrichissement {job.get('source', 'Unknown')}: {e}")
            return job

    async def scrape_page_content(self, url: str, max_chars: int = 6000) -> str:
        """Récupère le texte principal d'une page (best-effort)."""
        try:
            if not url or not isinstance(url, str):
                return ""

            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            req = urllib.request.Request(url, headers=headers)

            def _fetch() -> str:
                with urllib.request.urlopen(req, context=ssl_context, timeout=15) as response:
                    raw = response.read()
                # Best effort decode
                try:
                    return raw.decode("utf-8", errors="ignore")
                except Exception:
                    return raw.decode(errors="ignore")

            loop = asyncio.get_event_loop()
            html = await loop.run_in_executor(None, _fetch)

            from bs4 import BeautifulSoup

            soup = BeautifulSoup(html, "html.parser")

            # Remove obvious noise
            for tag in soup(["script", "style", "noscript", "header", "footer", "nav"]):
                tag.decompose()

            # Try common main containers first
            main = soup.find("main") or soup.find("article")
            text = ""
            if main:
                text = main.get_text(" ", strip=True)
            else:
                text = soup.get_text(" ", strip=True)

            text = re.sub(r"\s+", " ", text).strip()
            if max_chars and len(text) > max_chars:
                text = text[:max_chars]

            return text
        except Exception as e:
            logger.warning(f"⚠️ scrape_page_content error: {e}")
            return ""
    
    def _scrape_indeed_details(self, soup, job):
        """Scrape les détails d'une offre Indeed."""
        try:
            # Titre
            title_elem = soup.find('h1', class_='jobsearch-JobInfoHeader-title')
            if title_elem:
                job['title'] = title_elem.get_text(strip=True)
            
            # Entreprise
            company_elem = soup.find('div', {'data-testid': 'inlineHeader-companyName'})
            if company_elem:
                job['company'] = company_elem.get_text(strip=True)
            
            # Localisation
            location_elem = soup.find('div', {'data-testid': 'text-location'})
            if location_elem:
                job['location'] = location_elem.get_text(strip=True)
            
            # Description
            desc_elem = soup.find('div', {'id': 'jobDescriptionText'})
            if desc_elem:
                job['description'] = desc_elem.get_text(strip=True)
            
            # Compétences
            desc_text = job.get('description', '').lower()
            skills = []
            common_skills = ['python', 'java', 'javascript', 'react', 'node.js', 'sql', 'aws', 'docker', 'git', 'agile']
            for skill in common_skills:
                if skill in desc_text:
                    skills.append(skill)
            job['required_skills'] = skills
            
            job['scraped'] = True
            logger.debug(f"✅ Indeed scraped: {job['title']}")
            
        except Exception as e:
            logger.warning(f"⚠️ Indeed scraping error: {e}")
            
        return job
    
    def _scrape_linkedin_details(self, soup, job):
        """Scrape les détails d'une offre LinkedIn."""
        try:
            # Titre
            title_elem = soup.find('h1', class_='top-card-layout__title')
            if title_elem:
                job['title'] = title_elem.get_text(strip=True)
            
            # Entreprise
            company_elem = soup.find('a', class_='topcard__org-name-link')
            if company_elem:
                job['company'] = company_elem.get_text(strip=True)
            
            # Localisation
            location_elem = soup.find('span', class_='topcard__flavor--bullet')
            if location_elem:
                job['location'] = location_elem.get_text(strip=True)
            
            # Description
            desc_elem = soup.find('div', class_='show-more-less-html__markup')
            if desc_elem:
                job['description'] = desc_elem.get_text(strip=True)
            
            # Compétences
            desc_text = job.get('description', '').lower()
            skills = []
            common_skills = ['python', 'java', 'javascript', 'react', 'node.js', 'sql', 'aws', 'docker', 'git', 'agile']
            for skill in common_skills:
                if skill in desc_text:
                    skills.append(skill)
            job['required_skills'] = skills
            
            job['scraped'] = True
            logger.debug(f"✅ LinkedIn scraped: {job['title']}")
            
        except Exception as e:
            logger.warning(f"⚠️ LinkedIn scraping error: {e}")
            
        return job
    
    def _scrape_jobbank_details(self, soup, job):
        """Scrape les détails d'une offre Job Bank."""
        try:
            # Titre
            title_elem = soup.find('h1')
            if title_elem:
                job['title'] = title_elem.get_text(strip=True)
            
            # Entreprise
            company_elem = soup.find('span', {'property': 'name'})
            if company_elem:
                job['company'] = company_elem.get_text(strip=True)
            
            # Localisation
            location_elem = soup.find('span', {'property': 'addressLocality'})
            if location_elem:
                job['location'] = location_elem.get_text(strip=True)
            
            # Description
            desc_elem = soup.find('div', {'property': 'description'})
            desc_text = ""
            if desc_elem:
                desc_text = desc_elem.get_text(strip=True)
                
            # Comment postuler (How to apply - pour les emails)
            howto_elem = soup.find('div', id='howtoapply') or soup.find(id=lambda x: x and 'howtoapply' in x.lower())
            if howto_elem:
                desc_text += "\n\nComment postuler:\n" + howto_elem.get_text(separator=' ', strip=True)
                
            # Email links explicitly
            email_links = soup.find_all('a', href=lambda href: href and href.startswith('mailto:'))
            for link in email_links:
                email = link['href'].replace('mailto:', '').split('?')[0]
                desc_text += f" Email: {email}"
                
            if desc_text:
                job['description'] = desc_text
            
            # Compétences
            desc_text = job.get('description', '').lower()
            skills = []
            common_skills = ['python', 'java', 'javascript', 'react', 'node.js', 'sql', 'aws', 'docker', 'git', 'agile']
            for skill in common_skills:
                if skill in desc_text:
                    skills.append(skill)
            job['required_skills'] = skills
            
            job['scraped'] = True
            logger.debug(f"✅ JobBank scraped: {job['title']}")
            
        except Exception as e:
            logger.warning(f"⚠️ JobBank scraping error: {e}")
            
        return job
    
    def _scrape_generic_details(self, soup, job):
        """Scrape générique pour autres sites."""
        try:
            # Titre
            title_elem = soup.find('h1') or soup.find('h2')
            if title_elem:
                job['title'] = title_elem.get_text(strip=True)
            
            # Description
            desc_candidates = soup.find_all('p') + soup.find_all('div')
            best_desc = ""
            for elem in desc_candidates:
                text = elem.get_text(strip=True)
                if len(text) > 100 and len(text) > len(best_desc):
                    best_desc = text
            
            if best_desc:
                job['description'] = best_desc
            
            # Compétences
            desc_text = job.get('description', '').lower()
            skills = []
            common_skills = ['python', 'java', 'javascript', 'react', 'node.js', 'sql', 'aws', 'docker', 'git', 'agile']
            for skill in common_skills:
                if skill in desc_text:
                    skills.append(skill)
            job['required_skills'] = skills
            
            job['scraped'] = True
            logger.debug(f"✅ Generic scraped: {job['title']}")
            
        except Exception as e:
            logger.warning(f"⚠️ Generic scraping error: {e}")
            
        return job

    async def _search_jobbank(self, keywords: str, location: str, max_results: int) -> List[Dict[str, Any]]:
        """Scrape les résultats HTML de Job Bank."""
        logger.debug(f"🔍 Scraping Job Bank pour: {keywords} {location}")
        
        # Gestion précise de la localisation
        loc_param = location
        strict_city_filter = None
        
        if location.lower() in ["québec", "quebec"]:
            loc_param = "Québec, QC" 
            strict_city_filter = ["québec", "quebec", "lévis", "levis", "sainte-foy"]
        elif location.lower() in ["montréal", "montreal"]:
            loc_param = "Montréal, QC"
            strict_city_filter = ["montréal", "montreal", "laval", "longueuil"]
            
        base_url = "https://www.jobbank.gc.ca/jobsearch/jobsearch"
        clean_keywords = keywords.lower().replace(f" à {location.lower()}", "").replace(f" in {location.lower()}", "").strip()
        
        params = {
            "searchstring": clean_keywords if clean_keywords else keywords,
            "locationstring": loc_param,
            "sort": "M" 
        }
        url = f"{base_url}?{urllib.parse.urlencode(params)}"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        jobs = []
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, context=ssl_context, timeout=10) as response:
                html = response.read().decode('utf-8')
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(html, 'html.parser')
                
                articles = soup.find_all('article')
                logger.debug(f"🔍 Articles trouvés: {len(articles)}")
                
                for i, article in enumerate(articles): 
                    if len(jobs) >= max_results: break
                    
                    link_tag = article.find('a', class_='resultJobItem')
                    if not link_tag: continue
                    
                    title = article.find(class_='noctitle').get_text(strip=True)
                    href = link_tag.get('href', '')
                    full_url = f"https://www.jobbank.gc.ca{href}"
                    
                    company = "Entreprise confidentielle"
                    business_tag = article.find(class_='business')
                    if business_tag: company = business_tag.get_text(strip=True)
                        
                    loc_text = location
                    loc_tag = article.find(class_='location')
                    if loc_tag: 
                        loc_text = " ".join(loc_tag.get_text().split())
                    
                    # Filtrage strict
                    if strict_city_filter:
                        is_valid_loc = any(city in loc_text.lower() for city in strict_city_filter)
                        if not is_valid_loc:
                            continue
                    
                    date_text = ""
                    date_tag = article.find(class_='date')
                    if date_tag: date_text = date_tag.get_text(strip=True)
                        
                    job = {
                        "id": f"jb-{i}",
                        "title": title,
                        "company": company,
                        "location": loc_text,
                        "url": full_url,
                        "source": "Guichet Emplois",
                        "description": f"{title} chez {company}. {loc_text}. Publié: {date_text}",
                        "required_skills": [keywords], 
                        "match_score": 0
                    }
                    jobs.append(job)
        except Exception as e:
            logger.error(f"❌ Erreur Job Bank: {e}")
            
        return jobs

    async def _search_general_web(self, keywords: str, location: str, max_results: int) -> List[Dict[str, Any]]:
        """Recherche via Google HTML avec scraping individuel des offres."""
        logger.info(f"🔎 Recherche Google HTML: {keywords} à {location}")
        jobs = []
        
        # Requêtes ciblées pour trouver des offres spécifiques
        sites = [
            ("Indeed", f'site:ca.indeed.com/rc/clk "{keywords}" "{location}"'),
            ("LinkedIn", f'site:ca.linkedin.com/jobs/view "{keywords}" "{location}"'), 
            ("JobBank", f'site:jobbank.gc.ca/job "{keywords}" "{location}"')
        ]
        
        loop = asyncio.get_event_loop()
        
        def _scrape_google(source_name, query_str):
            found_jobs = []
            try:
                q_enc = urllib.parse.quote_plus(query_str)
                url = f"https://www.google.com/search?q={q_enc}&num=20&hl=fr"
                
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                }

                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req, context=ssl_context, timeout=10) as response:
                    html = response.read().decode('utf-8')
                
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(html, 'html.parser')
                
                results = soup.select('div.tF2Cxc') 
                if not results:
                     results = soup.select('div.g')
                
                logger.debug(f"  [{source_name}] Raw blocks found: {len(results)}")

                for i, res in enumerate(results):
                    if len(found_jobs) >= 5: break
                    
                    link_tag = res.find('a', href=True)
                    if not link_tag: continue
                    
                    href = link_tag['href']
                    title_tag = res.find('h3')
                    title = title_tag.get_text(strip=True) if title_tag else "Offre"
                    
                    snippet_tag = res.select_one('div.VwiC3b') 
                    snippet = snippet_tag.get_text(strip=True) if snippet_tag else ""
                    
                    # Filtres stricts - exclure les pages de recherche
                    if not href.startswith("http"): continue
                    if "google.com" in href: continue
                    
                    # Filtrer les URLs de recherche généraux
                    if any(path in href.lower() for path in ['/jobs?', '/search?', '/jobsearch?', '/jobs/search', '/j2jk']):
                        logger.debug(f"  Ignoring search page: {href}")
                        continue
                    
                    # Nettoyage du titre
                    clean_title = title
                    if " - " in title:
                        parts = title.split(" - ")
                        clean_title = parts[0]
                    
                    # Extraction du nom de l'entreprise
                    company = source_name
                    if " chez " in snippet.lower():
                        parts = snippet.lower().split(" chez ")
                        if len(parts) > 1:
                            company_part = parts[1].split()[0] if parts[1].split() else ""
                            if company_part:
                                company = company_part.capitalize()
                    
                    job = {
                        "id": f"gg-{source_name}-{i}",
                        "title": clean_title,
                        "company": company,
                        "location": location,
                        "description": snippet,
                        "url": href,
                        "source": source_name,
                        "required_skills": [],
                        "match_score": 0,
                        "scraped": False
                    }
                    found_jobs.append(job)
                    
            except Exception as e:
                logger.error(f"⚠️ Erreur Google Scraper ({source_name}): {e}")
            
            return found_jobs

        # Exécution parallèle
        tasks = []
        for src, q in sites:
            tasks.append(loop.run_in_executor(None, _scrape_google, src, q))
            
        results_list = await asyncio.gather(*tasks)
        
        for src_res in results_list:
            jobs.extend(src_res)
            
        return jobs

    def _generate_fallback_links(self, keywords: str, location: str) -> List[Dict[str, Any]]:
        """Génère des liens de recherche directs en dernier recours."""
        params = urllib.parse.quote_plus(f"{keywords} {location}")
        k_enc = urllib.parse.quote_plus(keywords)
        l_enc = urllib.parse.quote_plus(location)
        
        return [
            {
                "id": "search-guichet",
                "title": f"Voir les offres '{keywords}' sur Guichet Emplois",
                "company": "Gouvernement du Canada",
                "location": location,
                "url": f"https://www.guichetemplois.gc.ca/jobsearch/jobsearch?searchstring={k_enc}&locationstring={l_enc}",
                "source": "Search Link",
                "description": "Source officielle. Cliquez pour voir les résultats détaillés.",
                "required_skills": ["Navigation Web"],
                "match_score": 85
            },
            {
                "id": "search-indeed",
                "title": f"Voir les offres '{keywords}' sur Indeed",
                "company": "Indeed",
                "location": location,
                "url": f"https://ca.indeed.com/jobs?q={k_enc}&l={l_enc}",
                "source": "Search Link",
                "description": "Agrégateur d'emplois populaire.",
                "required_skills": ["Navigation Web"],
                "match_score": 80
            },
            {
                "id": "search-linkedin",
                "title": f"Voir les offres '{keywords}' sur LinkedIn",
                "company": "LinkedIn",
                "location": location,
                "url": f"https://www.linkedin.com/jobs/search?keywords={k_enc}&location={l_enc}",
                "source": "Search Link",
                "description": "Réseau professionnel.",
                "required_skills": ["Navigation Web"],
                "match_score": 75
            }
        ]

# Instance globale
web_searcher = JobWebSearcher()
