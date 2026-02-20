
import urllib.request
import urllib.parse
import ssl
from bs4 import BeautifulSoup
import re

ssl_context = ssl._create_unverified_context()

def search_jobbank(keywords, location):
    print(f"Searching Job Bank for '{keywords}' in '{location}'...")
    
    # Construct URL
    base_url = "https://www.jobbank.gc.ca/jobsearch/jobsearch"
    params = {
        "searchstring": keywords,
        "locationstring": location,
        "sort": "M" 
    }
    url = f"{base_url}?{urllib.parse.urlencode(params)}"
    print(f"URL: {url}")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, context=ssl_context) as response:
            html = response.read().decode('utf-8')
            soup = BeautifulSoup(html, 'html.parser')
            
            articles = soup.find_all('article')
            print(f"Found {len(articles)} articles")
            
            jobs = []
            for article in articles[:5]:
                # Find the main link/container
                link_tag = article.find('a', class_='resultJobItem')
                if not link_tag: continue
                
                # Title
                title_tag = article.find(class_='noctitle')
                title = title_tag.get_text(strip=True) if title_tag else "Unknown Title"
                
                # Link
                href = link_tag.get('href')
                full_url = f"https://www.jobbank.gc.ca{href}"
                
                # Metadata
                company = "Unknown"
                location_text = "Unknown"
                date_text = "Unknown"
                
                business_tag = article.find(class_='business')
                if business_tag: company = business_tag.get_text(strip=True)
                
                location_tag = article.find(class_='location')
                if location_tag: 
                    # Location often has spacing/newlines
                    location_text = " ".join(location_tag.get_text().split())
                    
                date_tag = article.find(class_='date')
                if date_tag: date_text = date_tag.get_text(strip=True)
                
                jobs.append({
                    "title": title,
                    "company": company,
                    "location": location_text,
                    "date": date_text,
                    "url": full_url
                })
                
            return jobs
            
    except Exception as e:
        print(f"Error: {e}")
        return []

# Test
results = search_jobbank("python", "quebec")
for job in results:
    print(f"{job['title']} | {job['company']}")
    print(f"  {job['url']}")
    print("-" * 20)
