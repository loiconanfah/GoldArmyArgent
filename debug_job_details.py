
import urllib.request
import urllib.parse
import ssl

ssl_context = ssl._create_unverified_context()

def debug_location():
    # Test Location URL
    base_url = "https://www.jobbank.gc.ca/jobsearch/jobsearch"
    params = {
        "searchstring": "python",
        "locationstring": "Québec, QC",
        "sort": "M" 
    }
    url = f"{base_url}?{urllib.parse.urlencode(params)}"
    print(f"Testing Search URL: {url}")
    
    headers = {"User-Agent": "Mozilla/5.0"}
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, context=ssl_context) as response:
        html = response.read().decode('utf-8')
        print(f"Search Page Length: {len(html)}")
        
        # Check if we are seeing "Results for Canada" or "Results for Québec, QC"
        if "Québec, QC" in html:
            print("Page seems to acknowledge location.")
        else:
            print("Page might be ignoring location.")
            
        with open("search_debug.html", "w", encoding="utf-8") as f:
            f.write(html)

def debug_details():
    # Test a specific job URL (from previous output or random valid one)
    # Using a known valid URL structure, but I need a real ID. 
    # Let's use the one from the fail log if possible or search first
    print("\nFetching a job link first...")
    
    # Quick search to get a link
    import sys
    from bs4 import BeautifulSoup
    
    # Reuse valid logic
    base_url = "https://www.jobbank.gc.ca/jobsearch/jobsearch?searchstring=python&locationstring=Quebec%2C+QC&sort=M"
    headers = {"User-Agent": "Mozilla/5.0"}
    req = urllib.request.Request(base_url, headers=headers)
    with urllib.request.urlopen(req, context=ssl_context) as response:
        html = response.read().decode('utf-8')
        soup = BeautifulSoup(html, 'html.parser')
        link = soup.find('a', class_='resultJobItem')
        if link:
            href = link.get('href')
            full_url = f"https://www.jobbank.gc.ca{href}"
            print(f"Found Job URL: {full_url}")
            
            # Now fetch details
            req_det = urllib.request.Request(full_url, headers=headers)
            with urllib.request.urlopen(req_det, context=ssl_context) as resp_det:
                html_det = resp_det.read().decode('utf-8')
                print(f"Details Page Length: {len(html_det)}")
                with open("job_debug.html", "w", encoding="utf-8") as f:
                    f.write(html_det)
        else:
            print("Could not find any job to text details.")

if __name__ == "__main__":
    try:
        debug_location()
        debug_details()
    except Exception as e:
        print(f"Error: {e}")
