import asyncio
from tools.web_searcher import JobWebSearcher
from loguru import logger
import sys

# Configure logger
logger.remove()
logger.add(sys.stderr, level="DEBUG")

async def test_scraping():
    searcher = JobWebSearcher()
    
    print("\n--- Testing DDG HTML Scraper (New Logic) ---")
    # Test with a specific query that should yield results
    ddg_results = await searcher._search_general_web("Développeur React", "Québec", 5)
    
    print(f"Items found: {len(ddg_results)}")
    for i, job in enumerate(ddg_results):
        print(f"[{i}] Title: {job.get('title')}")
        print(f"    URL: {job.get('url')}")
        print(f"    Desc: {job.get('description')[:100]}...")
        print("-" * 50)

if __name__ == "__main__":
    asyncio.run(test_scraping())
