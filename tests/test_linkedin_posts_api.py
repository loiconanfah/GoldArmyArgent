import http.client
import json
import urllib.parse

conn = http.client.HTTPSConnection("fresh-linkedin-profile-data-api.p.rapidapi.com")

headers = {
    'x-rapidapi-key': "c30011fc96mshf54e01fc16d71a0p190dbbjsna557b0fa3efc",
    'x-rapidapi-host': "fresh-linkedin-profile-data-api.p.rapidapi.com"
}

val = urllib.parse.quote("développeur logiciel")
for param in ["keyword", "query", "q", "search"]:
    print(f"\n--- Testing with ?{param}={val} ---")
    conn.request("GET", f"/api/search/posts?{param}={val}", headers=headers)
    res = conn.getresponse()
    data = res.read().decode("utf-8")
    try:
        print(json.dumps(json.loads(data), indent=2))
    except Exception:
        print(data)
