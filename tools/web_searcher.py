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
        keywords = str(keywords or "")
        location = str(location or "Québec")
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
                
        unique_jobs = unique_jobs[:max_results]
        
        logger.info(f"🔍 Enrichissement asynchrone de {len(unique_jobs)} offres pour extraire les e-mails/sites web...")
        enrich_tasks = [self.enrich_job_details(job) for job in unique_jobs]
        enriched_jobs = await asyncio.gather(*enrich_tasks, return_exceptions=True)
        
        final_jobs = []
        for job in enriched_jobs:
            if isinstance(job, dict):
                final_jobs.append(job)
                
        logger.info(f"📊 Résultats finaux enrichis: {len(final_jobs)} offres")
        return final_jobs

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
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
            }
            
            try:
                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req, context=ssl_context, timeout=15) as response:
                    html = response.read().decode('utf-8')
                    
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(html, 'html.parser')
                
                # Extraction selon la source
                enriched_job = job
                if 'indeed.com' in url:
                    enriched_job = self._scrape_indeed_details(soup, job)
                elif 'linkedin.com' in url:
                    enriched_job = self._scrape_linkedin_details(soup, job)
                elif 'jobbank.gc.ca' in url:
                    enriched_job = self._scrape_jobbank_details(soup, job)
                else:
                    enriched_job = self._scrape_generic_details(soup, job)
                    
            except Exception as e:
                logger.warning(f"⚠️ Scraping bloqué pour {url} ({e}). Tentative Regex sur snippet...")
                import re
                desc_text = job.get('description', '')
                emails_found = re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', desc_text)
                if emails_found:
                    job['emails'] = list(set([e.lower() for e in emails_found]))
                    job['apply_email'] = job['emails'][0]
                enriched_job = job
                
            # Phase 5: Sauvegarde automatique du contact réseau
            try:
                from core.contacts import contacts_manager
                company = enriched_job.get('company')
                website = enriched_job.get('company_website', '')
                emails = enriched_job.get('emails', [])
                if company and company.lower() not in ["confidentiel", "entreprise confidentielle"] and (website or emails):
                    contacts_manager.save_contact(
                        company_name=company,
                        site_url=website,
                        emails=emails,
                        source_job=enriched_job.get('title', '')
                    )
            except Exception as e:
                logger.error(f"❌ Erreur de sauvegarde du contact: {e}")
                
            return enriched_job
                
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
            
            job['apply_email'] = ""
            job['apply_url'] = ""
            
            if howto_elem:
                desc_text += "\n\nComment postuler:\n" + howto_elem.get_text(separator=' ', strip=True)
                
                # Cherche s'il y a des liens mailto:
                import re
                mailto_links = howto_elem.find_all('a', href=re.compile(r'^mailto:'))
                if mailto_links:
                    job['apply_email'] = mailto_links[0]['href'].replace('mailto:', '').strip()
                else:
                    # Cherche le header "Par email"
                    email_header = howto_elem.find(string=re.compile(r'Par email', re.IGNORECASE))
                    if email_header:
                        block = email_header.find_parent('div') or email_header.find_parent('p')
                        if block:
                            emails = re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', block.get_text())
                            if emails: job['apply_email'] = emails[0].lower()
                                
                # Cherche s'il y a un lien "En ligne"
                online_header = howto_elem.find(string=re.compile(r'En ligne', re.IGNORECASE))
                if online_header:
                    block = online_header.find_parent('div') or online_header.find_parent('p') or online_header.find_parent('ul')
                    if block:
                        link = block.find('a', href=re.compile(r'^http'))
                        if link:
                            job['apply_url'] = link['href']
                        else:
                            urls = re.findall(r'https?://[^\s<>"]+|www\.[^\s<>"]+', block.get_text())
                            if urls: job['apply_url'] = urls[0]

            # Fallback général Email extraction
            import re
            emails_found = set()
            for email in re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', soup.get_text()):
                emails_found.add(email.lower())
                
            # Email links explicitly
            email_links = soup.find_all('a', href=lambda href: href and href.startswith('mailto:'))
            for link in email_links:
                email = link['href'].replace('mailto:', '').split('?')[0]
                emails_found.add(email.lower())
                desc_text += f"\nEmail: {email}"
                
            if emails_found:
                job['emails'] = list(emails_found)
                
            # Extraction du site Web de l'entreprise
            website_elem = soup.find('a', {'property': 'url'}) or soup.find(id=lambda x: x and 'website' in str(x).lower())
            if website_elem and website_elem.has_attr('href'):
                if not website_elem['href'].startswith('#'):
                    job['company_website'] = website_elem['href']
                    
            # Extraction Description Entreprise par défaut
            job['company_description'] = company_elem.get_text(strip=True) if company_elem else "Information confidentielle."
                
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
                
            # Extraction Email agressive
            import re
            emails_found = set()
            main_content = soup.find('main') or soup.find('body') or soup
            for email in re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', main_content.get_text()):
                emails_found.add(email.lower())
                
            email_links = soup.find_all('a', href=lambda href: href and href.startswith('mailto:'))
            for link in email_links:
                emails_found.add(link['href'].replace('mailto:', '').split('?')[0].lower())
                
            if emails_found:
                job['emails'] = list(emails_found)
                job['apply_email'] = list(emails_found)[0]
            
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
        """Recherche via DuckDuckGo Lite (HTML) avec scraping individuel des offres."""
        keywords = str(keywords or "")
        location = str(location or "Québec")
        logger.info(f"🔎 Recherche DDG Lite: {keywords} à {location}")
        jobs = []
        
        # Requêtes ciblées pour trouver des offres spécifiques
        queries = [
            f'site:ca.indeed.com/rc/clk "{keywords}" "{location}"',
            f'site:ca.linkedin.com/jobs/view "{keywords}" "{location}"',
            f'site:jobbank.gc.ca/job "{keywords}" "{location}"'
        ]
        
        # DuckDuckGo Lite bloque désormais souvent avec un Captcha (anomaly validation)
        # On passe directement aux liens de fallback pour ne pas bloquer l'agent.
        logger.warning(f"⚠️ Recherche DDG désactivée (Captcha). Utilisation des liens de fallback.")
        return []

    async def find_official_website_and_contact(self, company_name: str, location: str = "") -> Dict[str, Any]:
        """Tente de trouver le site officiel d'une entreprise via DuckDuckGo et d'y extraire un contact."""
        if not company_name or company_name.lower() in ["confidentiel", "anonyme"]:
            return {}
            
        logger.info(f"🕵️ OSINT: Recherche du site officiel pour '{company_name}'...")
        import urllib.parse
        import urllib.request
        from bs4 import BeautifulSoup
        import re
        
        query = urllib.parse.quote_plus(f"{company_name} {location} official site contact")
        url = f"https://html.duckduckgo.com/html/?q={query}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        result_contact = {"company_name": company_name, "site_url": "", "emails": [], "phone": ""}
        
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, context=ssl_context, timeout=10) as response:
                html = response.read().decode('utf-8')
                
            soup = BeautifulSoup(html, 'html.parser')
            # Chercher le premier lien externe valide (pas DDG/Yelp/LinkedIn)
            links = soup.find_all('a', class_='result__url')
            
            official_url = ""
            for a in links:
                href = a.get('href', '')
                if href.startswith('//'):
                    href = "https:" + href
                
                # Ignorer les agrégateurs connus
                ignored_domains = ['linkedin.com', 'yelp.', 'yellowpages.', 'indeed.com', 'glassdoor.', 'facebook.', 'instagram.', 'duckduckgo.']
                if href and not any(d in href.lower() for d in ignored_domains):
                    official_url = a.get_text(strip=True)
                    if not official_url.startswith('http'):
                        official_url = "https://" + official_url
                    break
                    
            if not official_url:
                logger.warning(f"⚠️ OSINT: Aucun site officiel trouvé pour {company_name}")
                return result_contact
                
            result_contact["site_url"] = official_url
            logger.info(f"🎯 OSINT: Site trouvé -> {official_url}. Scraping profond...")
            
            # Scraper ce site officiel pour emails / numéros de téléphone
            try:
                site_req = urllib.request.Request(official_url, headers=headers)
                with urllib.request.urlopen(site_req, context=ssl_context, timeout=10) as site_response:
                    site_html = site_response.read().decode('utf-8')
                    site_soup = BeautifulSoup(site_html, 'html.parser')
                    text_content = site_soup.get_text()
                    
                    # Regex Emails
                    emails_found = set()
                    for email in re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', text_content):
                        # Eviter les faux positifs comme les images .png
                        if not any(email.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp']):
                            emails_found.add(email.lower())
                            
                    # Regex Numéros de Téléphone (format basique Nord-Américain / Européen)
                    phones_found = set()
                    for phone in re.findall(r'(?:\+?(\d{1,3}))?[-. (]*(\d{3})[-. )]*(\d{3})[-. ]*(\d{4})(?: *x(\d+))?', text_content):
                        # Assemble just the main parts
                        if phone[1] and phone[2] and phone[3]:
                            assembled = f"{phone[1]}-{phone[2]}-{phone[3]}"
                            phones_found.add(assembled)
                            
                    result_contact["emails"] = list(emails_found)
                    if phones_found:
                        result_contact["phone"] = list(phones_found)[0]
                        
                    logger.info(f"✅ OSINT: Données extraites: {len(emails_found)} e-mails, {len(phones_found)} téléphones.")
            except Exception as se:
                logger.warning(f"⚠️ OSINT: Impossible de scraper le site trouvé ({official_url}): {se}")
                
        except Exception as e:
            logger.warning(f"⚠️ OSINT DuckDuckGo bloqué ou erreur: {e}")
            
        return result_contact

    def _generate_fallback_links(self, keywords: str, location: str) -> List[Dict[str, Any]]:
        """Génère des liens de recherche directs en dernier recours."""
        keywords = str(keywords or "")
        location = str(location or "Québec")
        
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
