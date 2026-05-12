
import aiohttp
import asyncio
import os
import json
from dotenv import load_dotenv

load_dotenv()

async def test_search_tool():
    print("Testing Gemini 2.0 Flash with Google Search Tool...")
    api_key = os.getenv("GEMINI_API_KEY")
    model = "gemini-2.0-flash"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    
    # Try with BOTH formats just to be sure
    payloads = [
        {
            "contents": [{"parts": [{"text": "Find LinkedIn profiles of recruiters at Google."}]}],
            "tools": [{"google_search": {}}]
        },
        {
            "contents": [{"parts": [{"text": "Find LinkedIn profiles of recruiters at Google."}]}],
            "tools": [{"googleSearch": {}}]
        }
    ]
    
    async with aiohttp.ClientSession() as session:
        for i, payload in enumerate(payloads):
            print(f"\nAttempt {i+1} with tool: {list(payload['tools'][0].keys())[0]}")
            try:
                async with session.post(url, json=payload, timeout=20) as resp:
                    print(f"Status: {resp.status}")
                    text = await resp.text()
                    if resp.status == 200:
                        data = json.loads(text)
                        print("SUCCESS!")
                        # Check for grounding metadata
                        grounding = data["candidates"][0].get("groundingMetadata", {})
                        if grounding:
                            print(f"Grounding found: {len(grounding.get('groundingChunks', []))} chunks.")
                        else:
                            print("No grounding metadata in response.")
                    else:
                        print(f"Error: {text}")
            except Exception as e:
                print(f"Exception: {e}")

if __name__ == "__main__":
    asyncio.run(test_search_tool())
