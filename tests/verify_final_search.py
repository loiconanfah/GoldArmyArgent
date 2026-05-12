
import asyncio
import sys
import os

# Ensure project root is in path
sys.path.append(os.getcwd())

from tools.web_searcher import web_searcher

async def main():
    print("Testing WebSearcher (Job Bank)...")
    try:
        jobs = await web_searcher.search_jobs("python", "quebec")
        print(f"Found {len(jobs)} jobs")
        for j in jobs[:5]:
            print(f"- {j['title']} | {j['company']} ({j['source']})")
            print(f"  URL: {j['url']}")
            
        if not jobs:
            print("No jobs found (Fallback check needed)")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
