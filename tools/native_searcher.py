"""Outil de recherche web natif (sans dépendances externes sauf BS4 si dispo)."""
import urllib.request
import urllib.parse
from typing import List, Dict, Any
import re
import ssl

# Désactiver vérification SSL
ssl_context = ssl._create_unverified_context()

class NativeWebSearcher:
    """Recherche web utilisant uniquement la librairie standard Python."""
    
    def search_jobs(self, keywords: str, location: str = "Québec") -> List[Dict[str, Any]]:
        print(f"🌐 Recherche native (urllib): '{keywords}' à {location}")
        
        jobs = []
        try:
            # 1. Tenter de scraper DuckDuckGo HTML
            # Requête simplifiée pour maximiser les résultats
            query = f"{keywords} {location}"
            encoded_query = urllib.parse.quote_plus(query)
            url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            
            print(f"🔍 Fetching: {url}")
            req = urllib.request.Request(url, headers=headers)
            
            links = []
            
            with urllib.request.urlopen(req, context=ssl_context) as response:
                html = response.read().decode('utf-8')
                
                try:
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(html, 'html.parser')
                    print(f"Page Title: {soup.title.string if soup.title else 'No Title'}")
                    
                    # Stratégie 1: Sélecteurs DDG connus
                    links = soup.select('.result__a')
                    
                    # Stratégie 2: Tout lien contenant des mots clés d'emploi
                    if not links:
                        print("Fallback: Scanning all links...")
                        all_tags = soup.find_all('a')
                        for tag in all_tags:
                            href = tag.get('href', '')
                            # Décoder l'URL DDG (/l/?uddg=...)
                            if "uddg=" in href:
                                try:
                                    from urllib.parse import unquote
                                    href = unquote(href.split("uddg=")[1].split("&")[0])
                                except:
                                    pass
                            
                            # Filtrer pour les sites d'emploi
                            if any(site in href for site in ["indeed", "jobboom", "guichet", "linkedin", "glassdoor"]):
                                links.append(tag)
                                
                except ImportError:
                    print("⚠️ BS4 non trouvé, impossible de parser.")
            
            print(f"Found {len(links)} potential job links")
            
            # Traiter les liens trouvés
            for i, link in enumerate(links[:15]):
                title = link.get_text(strip=True)
                href = link.get('href', '')
                
                # Nettoyage URL DDG
                if "uddg=" in href:
                    from urllib.parse import unquote
                    try:
                        href = unquote(href.split("uddg=")[1].split("&")[0])
                    except:
                        pass
                
                if not title:
                    title = "Offre d'emploi"
                
                # Déterminer la source
                source = "Web"
                if "indeed" in href: source = "Indeed"
                elif "jobboom" in href: source = "Jobboom"
                elif "guichetemplois" in href: source = "Job Bank"
                elif "linkedin" in href: source = "LinkedIn"
                
                jobs.append({
                    "id": f"native-{i}",
                    "title": title,
                    "company": "Recrutement", # Difficile à extraire sans sélecteur précis
                    "location": "Non spécifié",
                    "url": href,
                    "source": source,
                    "description": f"Offre trouvée sur {source}: {title}",
                    "required_skills": ["python"], # Placeholder pour matcher
                    "match_score": 0
                })

            # 2. Si aucun résultat, générer des liens de recherche directs (Fallback Utile)
            if not jobs:
                print("⚠️ Aucun résultat direct -> Génération de liens de recherche")
                
                # Indeed
                jobs.append({
                    "id": "search-indeed",
                    "title": f"Voir les offres '{keywords}' sur Indeed",
                    "company": "Indeed Canada",
                    "location": "Non spécifié",
                    "url": f"https://ca.indeed.com/jobs?q={urllib.parse.quote_plus(keywords)}&l={urllib.parse.quote_plus(location)}",
                    "source": "Search Link",
                    "description": "Cliquez ici pour voir toutes les offres sur Indeed (Scraping bloqué)",
                    "required_skills": ["python", "java"], # Fake skills pour matcher
                    "match_score": 100
                })
                
                # Jobboom
                jobs.append({
                    "id": "search-jobboom",
                    "title": f"Voir les offres '{keywords}' sur Jobboom",
                    "company": "Jobboom",
                    "location": "Non spécifié",
                    "url": f"https://www.jobboom.com/recherche/emplois?keywords={urllib.parse.quote_plus(keywords)}&location={urllib.parse.quote_plus(location)}",
                    "source": "Search Link",
                    "description": "Cliquez ici pour voir toutes les offres sur Jobboom",
                    "required_skills": ["rubriques"],
                    "match_score": 90
                })
                
                # Guichet Emplois
                jobs.append({
                    "id": "search-guichet",
                    "title": f"Voir les offres '{keywords}' sur Guichet Emplois",
                    "company": "Gouvernement du Canada",
                    "location": "Non spécifié",
                    "url": f"https://www.guichetemplois.gc.ca/jobsearch/jobsearch?searchstring={urllib.parse.quote_plus(keywords)}&locationstring={urllib.parse.quote_plus(location)}",
                    "source": "Search Link",
                    "description": "Source officielle du gouvernement",
                    "required_skills": ["français"],
                    "match_score": 85
                })
                
        except Exception as e:
            print(f"❌ Erreur Native Search: {e}")
            
        return jobs

if __name__ == "__main__":
    s = NativeWebSearcher()
    # Test
    res = s.search_jobs("développeur junior")
    for r in res:
        print(f"- {r['title']} ({r['url']})")
