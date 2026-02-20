
import asyncio
import os
from dotenv import load_dotenv
from tools.jooble_searcher import JoobleSearcher

# Charger les variables d'environnement
load_dotenv()

async def test_jooble():
    api_key = os.getenv("JOOBLE_API_KEY")
    if not api_key:
        print("❌ JOOBLE_API_KEY non trouvée dans .env")
        return

    print(f"API Key found: {api_key[:5]}...")
    
    searcher = JoobleSearcher(api_key=api_key)
    
    print("Test search: 'Python' in 'Quebec'...")
    try:
        jobs = await searcher.search_jobs(keywords="Python", location="Quebec")
        
        if jobs:
            print(f"Success! {len(jobs)} jobs found.")
            for job in jobs[:3]:
                print(f"  - {job['title']} at {job['company']}")
                print(f"    Source: {job['source']}")
                print(f"    URL: {job['url']}")
                print("---")
        else:
            print("No jobs found (but no execution error).")
            
    except Exception as e:
        print(f"Error during test: {e}")

if __name__ == "__main__":
    asyncio.run(test_jooble())
