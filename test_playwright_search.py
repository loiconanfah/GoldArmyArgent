
import asyncio
from tools.web_searcher import JobWebSearcher
from loguru import logger
import sys

# Configure logger to see output
logger.remove()
logger.add(sys.stderr, level="INFO")

async def test_pw():
    searcher = JobWebSearcher()
    
    print("Testing Playwright Search for 'boulanger' in 'Québec'...")
    try:
        # Test direct Playwright method
        jobs = await searcher._search_with_playwright("boulanger", "Québec", 5)
        
        print(f"\nFound {len(jobs)} jobs via Playwright:")
        for j in jobs:
            print(f"- [{j['source']}] {j['title']} @ {j['company']} ({j['location']})")
            print(f"  Url: {j['url']}")
            
        if not jobs:
            print("\n⚠️ No jobs found. check if browser launched and selectors matched.")
            
    except Exception as e:
        print(f"\nPlaywright Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_pw())
