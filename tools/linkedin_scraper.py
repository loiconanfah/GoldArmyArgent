"""
Scraper OSINT pour trouver les profils LinkedIn des recruteurs (RH) d'une entreprise.
Utilise DuckDuckGo HTML pour contourner partiellement les restrictions.
"""
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
            
        logger.info(f"🔎 Dorking LinkedIn RH pour: {company_name}")
        
        # Requête ciblée (dorking)
        query = f'site:linkedin.com/in/ "{company_name}" "Recrutement" OR "RH" OR "Recruteur" OR "Talent Acquisition"'
        encoded_query = urllib.parse.quote_plus(query)
        # Use Lite version
        url = f"https://lite.duckduckgo.com/lite/?q={encoded_query}"
        
        profiles = []
        
        try:
            req = urllib.request.Request(url, headers=self.headers)
            # Run in executor to avoid blocking the event loop
            loop = asyncio.get_event_loop()
            
            def fetch_url():
                with urllib.request.urlopen(req, context=ssl_context, timeout=10) as response:
                    return response.read().decode('utf-8')
                    
            html = await loop.run_in_executor(None, fetch_url)
            soup = BeautifulSoup(html, 'html.parser')
            
            # Lite DDG result links
            results = soup.find_all('a', class_='result-link')
            
            for res in results:
                if len(profiles) >= limit:
                    break
                    
                href = res.get('href', '')
                if not href: continue

                # Unwrap DDG redirect
                if 'uddg=' in href:
                    try:
                        href = urllib.parse.unquote(href.split('uddg=')[-1].split('&')[0])
                    except:
                        pass
                
                if 'linkedin.com/in/' in href:
                    # Clean URL
                    href = href.split('?')[0].rstrip('/')
                    
                    title = res.get_text(strip=True)
                    # Nettoyage pro du nom et rôle
                    clean_title = title.replace(" | LinkedIn", "").replace(" - LinkedIn", "")
                    name_parts = re.split(r' - | \| |: ', clean_title)
                    name = name_parts[0].strip()
                    
                    profiles.append({
                        "name": name,
                        "url": href,
                        "snippet": f"Profil identifié: {clean_title}"
                    })
                    
        except Exception as e:
            logger.warning(f"⚠️ Scraping LinkedIn: {e}")
            
        # Fallback Links if nothing found
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
