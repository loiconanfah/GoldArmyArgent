import asyncio
from tools.jooble_searcher import JoobleSearcher
from config.settings import settings

async def main():
    print(f"Testing Jooble API...")
    print(f"API Key configured: {'Yes' if settings.jooble_api_key else 'No'}")
    
    if not settings.jooble_api_key:
        print("Cannot test: No Jooble API key in settings (.env)")
        return
        
    searcher = JoobleSearcher(api_key=settings.jooble_api_key)
    jobs = await searcher.search_jobs(keywords="développeur logiciel", location="Toronto", limit=5)
    
    print(f"\nResults found: {len(jobs)}")
    for j in jobs:
        print(f"- {j.get('title')} @ {j.get('company')} ({j.get('location')})")

if __name__ == "__main__":
    asyncio.run(main())
