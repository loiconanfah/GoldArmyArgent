
import urllib.request
import urllib.parse
import ssl

ssl_context = ssl._create_unverified_context()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Content-Type": "application/x-www-form-urlencoded",
    "Referer": "https://lite.duckduckgo.com/"
}
url = "https://lite.duckduckgo.com/lite/"
data = urllib.parse.urlencode({'q': 'python jobs quebec', 'kl': 'ca-fr'}).encode('utf-8')

print(f"POST to {url}...")
try:
    req = urllib.request.Request(url, data=data, headers=headers, method='POST')
    with urllib.request.urlopen(req, context=ssl_context) as response:
        html = response.read().decode('utf-8')
        print(f"Length: {len(html)}")
        print(html[:1000])
        
        if "No results." in html:
            print("No results found.")
        elif "captcha" in html.lower() or "challenge" in html.lower():
            print("Blocked by Captcha/Challenge.")
        else:
            print("Success! Found content.")
            
            # Try to find results
            if "result-link" in html:
                print("Found result-link class.")
            
            # Save dump
            with open("ddg_lite_dump.html", "w", encoding="utf-8") as f:
                f.write(html)
except Exception as e:
    print(f"Error: {e}")
