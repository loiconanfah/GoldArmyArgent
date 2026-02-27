
import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('GEMINI_API_KEY')
url = f'https://generativelanguage.googleapis.com/v1beta/models?key={api_key}'

try:
    r = requests.get(url)
    with open("gemini_models_listing.json", "w", encoding="utf-8") as f:
        json.dump(r.json(), f, indent=2)
    print(f"Success! Status {r.status_code}. saved to gemini_models_listing.json")
except Exception as e:
    print(f"Exception: {e}")
