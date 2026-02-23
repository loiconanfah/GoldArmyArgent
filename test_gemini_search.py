import asyncio
import aiohttp
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

async def test_search():
    print(f"Loaded API KEY starting with: {str(api_key)[:10] if api_key else 'NONE'}")
    if not api_key:
        print("API KEY IS MISSING!")
        return
        
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
    payload = {
        "contents": [{"parts": [{"text": "Cherche sur Google le profil LinkedIn du directeur des ressources humaines de CGI Montreal. Donne moi le lien exact."}]}],
        "tools": [{"googleSearch": {}}]
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as resp:
            data = await resp.json()
            try:
                print(data["candidates"][0]["content"]["parts"][0]["text"])
                if "groundingMetadata" in data["candidates"][0]:
                    print("✅ Search Grounding Triggered!")
            except Exception as e:
                import json
                print("Error parsing response:")
                print(json.dumps(data, indent=2))

if __name__ == "__main__":
    asyncio.run(test_search())
