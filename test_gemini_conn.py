
import asyncio
import aiohttp
import sys
import os
from dotenv import load_dotenv

load_dotenv()

async def main():
    print("Testing Direct Connectivity to Google API...")
    api_key = os.getenv("GEMINI_API_KEY")
    model = "gemini-1.5-pro"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    
    payload = {
        "contents": [{"parts": [{"text": "Hello, respond with 'OK' if you see this."}]}]
    }
    
    print(f"Requesting: {url.split('key=')[0]}key=XXX")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as resp:
                print(f"Status: {resp.status}")
                text = await resp.text()
                print(f"Response: {text[:200]}")
    except Exception as e:
        print(f"CONNECTIVITY ERROR: {e}")
        print(f"Error type: {type(e)}")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
