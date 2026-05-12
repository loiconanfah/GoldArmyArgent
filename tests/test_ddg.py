import urllib.request
import urllib.parse
import ssl
from bs4 import BeautifulSoup

def test_ddg():
    dork_query = 'site:linkedin.com/in CGI Montreal HR OR Recruiter OR "Talent Acquisition" OR CTO OR CEO OR Director'
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(dork_query)}"
    req = urllib.request.Request(
        url, 
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
    )
    
    print(f"Fetching from: {url}")
    with urllib.request.urlopen(req, context=ctx, timeout=10) as response:
        html = response.read().decode('utf-8')
        
    soup = BeautifulSoup(html, 'html.parser')
    results = soup.find_all('div', class_='result')
    print(f"Found {len(results)} div.result elements")
    
    for div in results[:3]:
        a_tag = div.find('a', class_='result__url')
        print("-------------")
        print(div.get_text()[:200])
        if a_tag:
            print(f"URL: {a_tag.get('href')}")
            
if __name__ == '__main__':
    test_ddg()
