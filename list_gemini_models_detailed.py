
import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('GEMINI_API_KEY')
url = f'https://generativelanguage.googleapis.com/v1beta/models?key={api_key}'

try:
    r = requests.get(url)
    if r.status_code == 200:
        models = r.json().get('models', [])
        print("Available Models:")
        for m in models:
            print(f"NAME: {m['name']}")
            print(f"DISPLAY_NAME: {m.get('displayName', 'N/A')}")
            print(f"DESCRIPTION: {m.get('description', 'N/A')}")
            print("-" * 30)
    else:
        print(f"Error {r.status_code}: {r.text}")
except Exception as e:
    print(f"Exception: {e}")
