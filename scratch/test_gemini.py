import urllib.request
import json

api_key = "AIzaSyBVRksYtbv_ubxW-9P-YFmJxGdC99MZxUU"
url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"

data = {
    "contents": [
        {"parts": [{"text": "Hello"}]}
    ]
}
req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers={'Content-Type': 'application/json'})

try:
    with urllib.request.urlopen(req) as response:
        print("Status Code:", response.getcode())
        print("Response:", response.read().decode('utf-8')[:200])
except urllib.error.HTTPError as e:
    print("HTTP Error:", e.code)
    print("Error Reason:", e.read().decode('utf-8'))
except Exception as e:
    print("Exception:", str(e))
