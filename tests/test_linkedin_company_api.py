import http.client
import json
import urllib.parse

conn = http.client.HTTPSConnection("fresh-linkedin-profile-data-api.p.rapidapi.com")

headers = {
    'x-rapidapi-key': "c30011fc96mshf54e01fc16d71a0p190dbbjsna557b0fa3efc",
    'x-rapidapi-host': "fresh-linkedin-profile-data-api.p.rapidapi.com"
}

# Test with a real company like 'google'
conn.request("GET", "/api/job/company/google?count=20", headers=headers)

res = conn.getresponse()
data = res.read()

try:
    print(json.dumps(json.loads(data.decode("utf-8")), indent=2))
except Exception:
    print(data.decode("utf-8"))
