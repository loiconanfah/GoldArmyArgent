import urllib.request
import ssl
from bs4 import BeautifulSoup

ssl_context = ssl._create_unverified_context()
url = "https://www.jobbank.gc.ca/jobsearch/jobsearch?searchstring=python&locationstring=Qu%C3%A9bec%2C+QC&sort=M"
headers = {"User-Agent": "Mozilla/5.0"}
req = urllib.request.Request(url, headers=headers)
with urllib.request.urlopen(req, context=ssl_context) as response:
    html = response.read().decode('utf-8')
soup = BeautifulSoup(html, 'html.parser')
articles = soup.find_all('article')
print(f"Found {len(articles)} articles")
for a in articles:
    loc_tag = a.find(class_='location')
    loc_text = " ".join(loc_tag.get_text().split()) if loc_tag else "No loc"
    print(loc_text)
