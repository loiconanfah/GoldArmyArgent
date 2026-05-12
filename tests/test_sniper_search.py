
import asyncio
from duckduckgo_search import AsyncDDGS
import sys

# Configure IO for Windows
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

async def test_sniper_search(company="Google"):
    print(f"--- Testing Sniper Search for {company} ---")
    query = f'site:linkedin.com/in/ "{company}" ("Recruteur" OR "Recruit" OR "Talent" OR "HR")'
    print(f"Query: {query}")
    
    try:
        async with AsyncDDGS() as ddgs:
            results = [r async for r in ddgs.text(query, max_results=5)]
            print(f"Found {len(results)} results")
            for r in results:
                print(f"- {r['title']}: {r['href']}")
                
        if not results:
            print("No LinkedIn profiles found. Trying simpler query...")
            query_simple = f'site:linkedin.com/in/ {company} recruiters'
            async with AsyncDDGS() as ddgs:
                results_s = [r async for r in ddgs.text(query_simple, max_results=5)]
                for r in results_s:
                    print(f"- {r['title']}: {r['href']}")
                    
    except Exception as e:
        print(f"Error during search: {e}")

if __name__ == "__main__":
    asyncio.run(test_sniper_search())
