"""Script de debug pour le scraping."""
import asyncio
import aiohttp
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
}

async def debug_indeed():
    print("--- Debug Indeed ---")
    url = "https://ca.indeed.com/jobs?q=developpeur+junior&l=Quebec"
    print(f"Fetching {url}...")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=HEADERS) as response:
                print(f"Status: {response.status}")
                if response.status == 200:
                    html = await response.text()
                    print(f"HTML length: {len(html)}")
                    soup = BeautifulSoup(html, 'lxml')
                    
                    # Test selectors
                    cards = soup.find_all('div', class_='job_seen_beacon')
                    print(f"Found {len(cards)} job cards with 'job_seen_beacon'")
                    
                    if not cards:
                        # Try alternative selectors
                        print("Trying alternative selectors...")
                        cards = soup.find_all('td', class_='resultContent')
                        print(f"Found {len(cards)} job cards with 'resultContent'")
                        
                        # Save HTML for inspection if 0 results
                        with open("indeed_debug.html", "w", encoding="utf-8") as f:
                            f.write(html)
                        print("Saved indeed_debug.html")
                else:
                    print("Error: Non-200 status")
    except Exception as e:
        print(f"Exception: {e}")

async def debug_jobboom():
    print("\n--- Debug Jobboom ---")
    url = "https://www.jobboom.com/recherche/emplois?keywords=developpeur&location=Quebec"
    print(f"Fetching {url}...")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=HEADERS) as response:
                print(f"Status: {response.status}")
                if response.status == 200:
                    html = await response.text()
                    print(f"HTML length: {len(html)}")
                    soup = BeautifulSoup(html, 'lxml')
                    
                    listings = soup.find_all('article', class_='job-listing')
                    print(f"Found {len(listings)} listings")
                else:
                    print("Error: Non-200 status")
    except Exception as e:
        print(f"Exception: {e}")

async def debug_jobbank():
    print("\n--- Debug Job Bank (Guichet Emplois) ---")
    # Recherche "développeur" à "Québec"
    url = "https://www.guichetemplois.gc.ca/jobsearch/jobsearch?searchstring=developpeur&locationstring=Quebec"
    print(f"Fetching {url}...")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=HEADERS) as response:
                print(f"Status: {response.status}")
                if response.status == 200:
                    html = await response.text()
                    print(f"HTML length: {len(html)}")
                    soup = BeautifulSoup(html, 'lxml')
                    
                    # Sélecteurs Job Bank
                    articles = soup.find_all('article')
                    print(f"Found {len(articles)} articles")
                    
                    # Chercher les résultats spécifiques
                    results = soup.find_all('a', class_='result-job-item-link')
                    print(f"Found {len(results)} job links")
                    
                    if results:
                        print(f"Example link: {results[0].get('href')}")
                        print(f"Example title: {results[0].get_text(strip=True)}")
                else:
                    print("Error: Non-200 status")
    except Exception as e:
        print(f"Exception: {e}")

async def main():
    await debug_indeed()
    await debug_jobboom()
    await debug_jobbank()

if __name__ == "__main__":
    asyncio.run(main())
