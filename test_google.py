import urllib.request
import urllib.parse
import ssl
from bs4 import BeautifulSoup

ssl_context = ssl._create_unverified_context()
q_enc = urllib.parse.quote_plus('site:ca.indeed.com/rc/clk "python" "quebec"')
url = f"https://www.google.com/search?q={q_enc}&num=20&hl=fr"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
req = urllib.request.Request(url, headers=headers)
try:
    with urllib.request.urlopen(req, context=ssl_context) as response:
        html = response.read().decode('utf-8')
    soup = BeautifulSoup(html, 'html.parser')
    results = soup.select('div.tF2Cxc') or soup.select('div.g')
    print(f"Found {len(results)} results")
    if not results:
        print(html[:1000])# Print some of the HTML to see if it's a captcha
except Exception as e:
    print(f"Error: {e}")
