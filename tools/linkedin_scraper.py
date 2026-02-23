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
        query = f'site:ca.linkedin.com/in OR site:linkedin.com/in "Recrutement" OR "Recrutement tech" OR "RH" OR "Recruteur" OR "Recruiter" OR "Talent Acquisition" "{company_name}"'
        encoded_query = urllib.parse.quote_plus(query)
        url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
        
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
            
            results = soup.find_all('a', class_='result__url')
            titles = soup.find_all('h2', class_='result__title')
            snippets = soup.find_all('a', class_='result__snippet')
            
            for i, res in enumerate(results):
                if len(profiles) >= limit:
                    break
                    
                href = res.get('href', '')
                if 'linkedin.com/in/' in href:
                    # Nettoyage de l'URL duckduckgo
                    if href.startswith('//'): href = 'https:' + href
                    
                    title = titles[i].get_text(strip=True) if i < len(titles) else "Profil LinkedIn"
                    snippet = snippets[i].get_text(strip=True) if i < len(snippets) else ""
                    
                    # Nettoyage du titre (Enlever " - LinkedIn" etc)
                    name = title.replace(" | LinkedIn", "").replace(" - LinkedIn", "").split("-")[0].strip()
                    
                    profiles.append({
                        "name": name,
                        "url": href,
                        "snippet": snippet
                    })
                    
        except Exception as e:
            logger.warning(f"⚠️ Erreur Scraping LinkedIn (Captchas probables): {e}")
            
        # Fallback Links if nothing found or captcha blocked
        if not profiles:
            logger.info("ℹ️ Création de liens de recherche LinkedIn manuelle (Fallback).")
            direct_search_url = f"https://www.linkedin.com/search/results/people/?keywords={urllib.parse.quote_plus('RH OR Recrutement OR Talent OR Recruiter ' + company_name)}"
            profiles.append({
                "name": "Recherche Manuelle (Nécessite connexion)",
                "url": direct_search_url,
                "snippet": f"Cliquez pour rechercher les recruteurs de {company_name} directement sur LinkedIn."
            })
            
        return profiles

linkedin_scraper = LinkedInScraper()
