import asyncio
import sys
import urllib.request
import urllib.parse
import ssl
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
ssl_context = ssl._create_unverified_context()

def test_ddg_raw():
    query_str = 'site:ca.indeed.com/rc/clk "developpeur mobile" "Montréal"'
    url = "https://lite.duckduckgo.com/lite/"
    data = urllib.parse.urlencode({'q': query_str, 'kl': 'ca-fr'}).encode('utf-8')
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Content-Type": "application/x-www-form-urlencoded",
        "Referer": "https://lite.duckduckgo.com/"
    }
    req = urllib.request.Request(url, data=data, headers=headers, method='POST')
    with urllib.request.urlopen(req, context=ssl_context, timeout=15) as response:
        html = response.read().decode('utf-8')
        
    print(html[6000:10000])

if __name__ == "__main__":
    test_ddg_raw()
