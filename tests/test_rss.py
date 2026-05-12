
import urllib.request
import urllib.parse
import ssl
import xml.etree.ElementTree as ET

# RSS URL for "Python" in "Quebec"
# https://www.jobbank.gc.ca/jobsearch/feed/rss?searchstring=python&locationstring=quebec&sort=M

keywords = "python"
location = "quebec"

params = {
    "searchstring": keywords,
    "locationstring": location,
    "sort": "M"
}

urls = [
    f"https://www.jobbank.gc.ca/jobsearch/feed/rss?{urllib.parse.urlencode(params)}",
    f"https://www.guichetemplois.gc.ca/jobsearch/feed/rss?{urllib.parse.urlencode(params)}",
]

ssl_context = ssl._create_unverified_context()
headers = {
    "User-Agent": "Mozilla/5.0"
}

for url in urls:
    print(f"Fetching RSS: {url}...")

    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, context=ssl_context) as response:
            xml_data = response.read()
            print(f"Got {len(xml_data)} bytes")
            
            # Simple check if valid XML
            if b"<?xml" in xml_data or b"<rss" in xml_data:
                root = ET.fromstring(xml_data)
                
                # Parse items
                # RSS 2.0: channel -> item
                channel = root.find("channel")
                items = channel.findall("item") if channel is not None else []
                
                print(f"Found {len(items)} items")
                
                for item in items[:3]:
                    title = item.find("title").text if item.find("title") is not None else "No Title"
                    link = item.find("link").text if item.find("link") is not None else "#"
                    desc = item.find("description").text if item.find("description") is not None else "No Desc"
                    
                    print(f"- {title}")
                    print(f"  Link: {link}")
                    print(f"  Desc: {desc[:100]}...")
            else:
                print("Not valid XML")
                
    except Exception as e:
        print(f"Error: {e}")
