import asyncio
from duckduckgo_search import DDGS
from loguru import logger

async def test_ddgs():
    query = 'site:linkedin.com/in/ "google" recruteur OR RH OR "Talent Acquisition"'
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=5))
            print(f"Found {len(results)} results")
            for r in results:
                print(f"- {r.get('href')}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_ddgs())
