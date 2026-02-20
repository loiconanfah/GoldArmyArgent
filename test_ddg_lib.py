
import asyncio
from duckduckgo_search import AsyncDDGS
import sys

# Configure IO for Windows
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

async def test_ddg():
    print("Testing AsyncDDGS...")
    try:
        results = await AsyncDDGS().text("python jobs quebec", max_results=5)
        print(f"Found {len(results)} results")
        for r in results:
            print(f"- {r['title']}: {r['href']}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_ddg())
