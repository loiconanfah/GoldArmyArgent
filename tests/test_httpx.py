import asyncio
import httpx
import urllib.parse
from bs4 import BeautifulSoup

async def main():
    dork_query = 'CGI Montreal HR OR Recruiter OR "Talent Acquisition" OR CTO OR CEO OR Director LinkedIn'
    url = "https://lite.duckduckgo.com/lite/"
    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {'q': dork_query}
    
    async with httpx.AsyncClient(verify=False, follow_redirects=True) as client:
        response = await client.post(url, headers=headers, data=data, timeout=15.0)
        html = response.text
        
    print(f"Status: {response.status_code}")
    print(html[:1000])

if __name__ == '__main__':
    asyncio.run(main())
