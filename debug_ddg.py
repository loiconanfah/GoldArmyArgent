
import urllib.request
import urllib.parse
import ssl

ssl_context = ssl._create_unverified_context()

def debug_lite():
    url = "https://lite.duckduckgo.com/lite/"
    params = {
        "q": "site:indeed.com python quebec"
    }
    data = urllib.parse.urlencode(params).encode('ascii')
    
    req = urllib.request.Request(url, data=data, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, context=ssl_context, timeout=5) as response:
            html = response.read().decode('utf-8')
            print(f"Lite Page Length: {len(html)}")
            with open("debug_lite.html", "w", encoding="utf-8") as f:
                f.write(html)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_lite()
