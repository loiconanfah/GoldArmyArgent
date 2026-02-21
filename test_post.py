import urllib.request
import json
url = "http://127.0.0.1:8000/api/chat"
data = json.dumps({"message": "developper web", "cv_text": "", "nb_results": 10}).encode('utf-8')
req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
try:
    with urllib.request.urlopen(req) as response:
        with open("test_output.json", "w", encoding="utf-8") as f:
            f.write(response.read().decode())
        print("SUCCESS: Output written to test_output.json")
except urllib.error.HTTPError as e:
    with open("test_error.json", "w", encoding="utf-8") as f:
        f.write(e.read().decode())
    print(f"HTTP Error {e.code}: Error written to test_error.json")
