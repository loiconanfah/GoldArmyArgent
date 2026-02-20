
import urllib.request
import ssl
from bs4 import BeautifulSoup

ssl_context = ssl._create_unverified_context()
url = "https://www.jobbank.gc.ca/jobsearch/jobsearch?searchstring=python&locationstring=QC"
headers = {"User-Agent": "Mozilla/5.0"}

print(f"Fetching {url}...")
try:
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, context=ssl_context) as response:
        html = response.read().decode('utf-8')
        soup = BeautifulSoup(html, 'html.parser')
        
        rss_links = soup.find_all("link", type="application/rss+xml")
        print(f"Found {len(rss_links)} RSS links:")
        for link in rss_links:
            print(f"- {link.get('href')}")
            
        # Also check 'a' tags with 'rss' in href
        a_rss = soup.find_all("a", href=lambda h: h and "rss" in h)
        for a in a_rss:
            print(f"Link with RSS: {a.get('href')}")
            
except Exception as e:
    print(f"Error: {e}")
