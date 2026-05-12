import asyncio
import os
import sys
import json
from loguru import logger

# Add project root to path
sys.path.append(os.path.abspath(os.path.curdir))

from agents.headhunter import headhunter_agent

async def test_headhunter(company_name):
    logger.info(f"🧪 Testing Headhunter for: {company_name}")
    try:
        await headhunter_agent.initialize()
        profiles = await headhunter_agent.find_decision_makers({"company_name": company_name})
        
        print("\n--- RESULTS ---")
        print(json.dumps(profiles, indent=2, ensure_ascii=False))
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
