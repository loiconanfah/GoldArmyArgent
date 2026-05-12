
import asyncio
import os
from dotenv import load_dotenv
from tools.jsearch_searcher import JSearchSearcher

# Charger les variables d'environnement
load_dotenv()

async def test_jsearch():
    api_key = os.getenv("RAPIDAPI_KEY")
    if not api_key:
        print("RAPIDAPI_KEY not found in .env")
        return

    print(f"API Key found: {api_key[:5]}...")
    
    searcher = JSearchSearcher(api_key=api_key)
    
    print("Testing JSearch: 'Python Developer' in 'Montreal'...")
    try:
        jobs = await searcher.search_jobs(query="Python Developer", location="Montreal")
        
        if jobs:
            print(f"Success! {len(jobs)} jobs found.")
            for job in jobs[:3]:
                print(f"  - {job['title']} at {job['company']}")
                print(f"    Location: {job['location']}")
                print(f"    Source: {job['source']}")
                print(f"    URL: {job['url']}")
                print("---")
        else:
            print("No jobs found (but no execution error).")
            
    except Exception as e:
        print(f"Error during test: {e}")

if __name__ == "__main__":
    asyncio.run(test_jsearch())
