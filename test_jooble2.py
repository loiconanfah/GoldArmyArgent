import asyncio
import aiohttp
from config.settings import settings

async def test_raw_jooble():
    api_key = settings.jooble_api_key
    url = f"https://jooble.org/api/{api_key}"
    
    payload = {
        "keywords": "développeur logiciel",
        "location": "Toronto"
    }
    
    headers = {"Content-Type": "application/json"}
    
    print(f"Testing raw Jooble API: {url.replace(api_key, 'REDACTED')}...")
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as resp:
            print(f"Status: {resp.status}")
            text = await resp.text()
            print(f"Raw Response: {text[:500]}...")

if __name__ == "__main__":
    asyncio.run(test_raw_jooble())
