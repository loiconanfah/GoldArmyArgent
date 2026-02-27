
import asyncio
import os
import json
import aiohttp
from dotenv import load_dotenv

load_dotenv()

async def test_json_search(model_name):
    api_key = os.getenv('GEMINI_API_KEY')
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
    
    payload = {
        "contents": [{"parts": [{"text": "Return a JSON object with the CEO of Microsoft. Use Google Search to verify."}]}],
        "tools": [{"google_search": {}}],
        "generationConfig": {
            "responseMimeType": "application/json"
        }
    }
    
    print(f"Testing Gemini 3 JSON + SEARCH: {model_name}...")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, ssl=False) as response:
                status = response.status
                text = await response.text()
                print(f"Status: {status}")
                if status == 200:
                    print("SUCCESS! Response received.")
                    # print(text[:500])
                else:
                    print(f"Error: {text[:200]}")
    except Exception as e:
        print(f"Exception: {e}")

async def main():
    await test_json_search("gemini-3.1-pro-preview")
    await test_json_search("gemini-2.0-flash")

if __name__ == "__main__":
    asyncio.run(main())
