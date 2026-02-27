
import urllib.request
import urllib.parse
import ssl
from bs4 import BeautifulSoup

ssl_context = ssl._create_unverified_context()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def test_scrape(query):
    print(f"Testing query: {query}")
    encoded_query = urllib.parse.quote_plus(query)
    url = f"https://lite.duckduckgo.com/lite/?q={encoded_query}"
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, context=ssl_context, timeout=10) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            
        with open("search_debug_html.html", "w", encoding="utf-8") as f:
            f.write(html)
            
        soup = BeautifulSoup(html, 'html.parser')
        
        # In Lite, results are often in tables
        links = soup.find_all('a', class_='result-link')
        print(f"Found {len(links)} result-link tags.")
        
        if not links:
            # Fallback to all links
            links = soup.select('a')
            print(f"Total links found: {len(links)}")
            
        with open("search_results.txt", "w", encoding="utf-8") as f:
            for link in links:
                href = link.get('href', '')
                text = link.get_text(strip=True)
                f.write(f"TEXT: {text}\nURL: {href}\n\n")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_scrape('site:linkedin.com/in/ "Google" ("Recruteur" OR "Recruit")')
