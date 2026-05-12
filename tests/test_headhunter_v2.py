import asyncio
import os
import sys
import json
import aiohttp
from loguru import logger

# Add project root to path
sys.path.append(os.path.abspath(os.path.curdir))

from agents.headhunter import headhunter_agent

async def check_url(url):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10, allow_redirects=True) as response:
                return response.status
    except Exception as e:
        return str(e)

async def test_headhunter(company_name):
    logger.info(f"🧪 Testing Headhunter for: {company_name}")
    try:
        await headhunter_agent.initialize()
        profiles = await headhunter_agent.find_decision_makers({"company_name": company_name})
        
        print("\n--- RESULTS ---")
        for p in profiles:
            url = p.get("linkedin_url")
            status = await check_url(url)
            print(f"Name: {p.get('name')}")
            print(f"URL: {url}")
            print(f"Status: {status}")
            print("-" * 20)
        print("--- END RESULTS ---\n")
        
        if not profiles:
            logger.error("❌ No profiles found!")
        else:
            logger.success(f"✅ Found {len(profiles)} profiles.")
            
    except Exception as e:
        logger.error(f"💥 Error: {e}")

if __name__ == "__main__":
    query = sys.argv[1] if len(sys.argv) > 1 else "cgi"
    asyncio.run(test_headhunter(query))
