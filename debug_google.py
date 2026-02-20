import urllib.request
import urllib.parse
import ssl
from bs4 import BeautifulSoup

def debug_google():
    query = 'site:indeed.com/viewjob "Développeur React" "Québec"'
    # query = 'Développeur React Québec Indeed'
    query = urllib.parse.quote_plus(query)
    url = f"https://www.google.com/search?q={query}&num=20"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    
    print(f"Fetching {url}...")
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, context=context) as response:
            html = response.read().decode('utf-8')
            
        soup = BeautifulSoup(html, 'html.parser')
        
        # Google search results are usually in 'div.g' or 'div.tF2Cxc'
        # Links are in 'a' tags with href starting with http (and not google owned usually)
        
        results = soup.select('div.g')
        print(f"Found {len(results)} raw blocks.")
        
        for i, res in enumerate(results):
            link = res.find('a', href=True)
            if link:
                href = link['href']
                title = link.find('h3')
                title_text = title.text if title else "No Title"
                print(f"  {i}. {title_text} | {href}")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_google()
