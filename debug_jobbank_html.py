
import urllib.request
import ssl

ssl_context = ssl._create_unverified_context()
url = "https://www.jobbank.gc.ca/jobsearch/jobsearch?searchstring=python&locationstring=QC&sort=M"
headers = {"User-Agent": "Mozilla/5.0"}

print(f"Fetching {url}...")
try:
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, context=ssl_context) as response:
        html = response.read().decode('utf-8')
        print(f"Length: {len(html)}")
        
        with open("jobbank_dump.html", "w", encoding="utf-8") as f:
            f.write(html)
        print("Saved to jobbank_dump.html")
            
except Exception as e:
    print(f"Error: {e}")
