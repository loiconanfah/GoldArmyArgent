
import asyncio
import os
import json
import aiohttp
from dotenv import load_dotenv

load_dotenv()

async def test_model(model_name):
    api_key = os.getenv('GEMINI_API_KEY')
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
    
    payload = {
        "contents": [{"parts": [{"text": "Who is the CEO of Google?"}]}],
        "tools": [{"google_search": {}}]
    }
    
    print(f"Testing model: {model_name}...")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, ssl=False) as response:
                status = response.status
                text = await response.text()
                print(f"Status: {status}")
                if status == 200:
                    print("SUCCESS!")
                else:
                    print(f"Error: {text[:200]}")
    except Exception as e:
        print(f"Exception: {e}")

async def main():
    # On teste les variantes possibles
    await test_model("gemini-3.1-pro-preview")
    await test_model("gemini-2.5-pro")
    await test_model("gemini-2.0-flash") # Notre référence qui fonctionne

if __name__ == "__main__":
    asyncio.run(main())
