import asyncio
import sys
import urllib.request
import urllib.parse
import ssl
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
ssl_context = ssl._create_unverified_context()

def test_jb_raw():
    keywords = "developpeur logiciel"
    location = "Montréal, QC"
    base_url = "https://www.jobbank.gc.ca/jobsearch/jobsearch"
    params = {
        "searchstring": keywords,
        "locationstring": location,
        "sort": "M" 
    }
    url = f"{base_url}?{urllib.parse.urlencode(params)}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, context=ssl_context, timeout=10) as response:
        html = response.read().decode('utf-8')
        
    print(html[8000:15000])

if __name__ == "__main__":
    test_jb_raw()
