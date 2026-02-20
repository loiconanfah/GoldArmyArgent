
import asyncio
from tools.web_searcher import web_searcher
from loguru import logger
import sys

# Configure logger
logger.remove()
logger.add(sys.stderr, level="INFO")

async def verify_robustness():
    print("Testing Search Robustness (Simulating AV Block)...")
    
    # This should attempt Job Bank -> Playwright (Fail) -> DDG -> Fallback
    jobs = await web_searcher.search_jobs("boulanger", "Québec", max_results=5)
    
    print(f"\nFinal Result: Found {len(jobs)} jobs.")
    for j in jobs:
        print(f"- [{j['source']}] {j['title']} ({j['company']})")
        
    if len(jobs) > 0:
        print("\nSuccess: The agent returned jobs despite the AV block on Playwright.")
    else:
        print("\nFailure: No jobs returned.")

if __name__ == "__main__":
    asyncio.run(verify_robustness())
