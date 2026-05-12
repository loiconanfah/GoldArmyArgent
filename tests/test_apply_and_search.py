
import asyncio
from tools.web_searcher import web_searcher
from agents.job_searcher import JobSearchAgent

async def test_features():
    print("1. Testing DuckDuckGo Search (Real)...")
    try:
        # Recherche plus large
        jobs = await web_searcher._search_general_web("boulanger", "Québec", 3)
        print(f"Found {len(jobs)} jobs via DDG.")
        for j in jobs:
            print(f"- {j['title']} ({j['company']}) -> {j['url']}")
            
        if not jobs:
            print("⚠️ No jobs found via DDG (Check internet/blocking).")
    except Exception as e:
        print(f"❌ DDG Search Failed: {e}")

    print("\n2. Testing Cover Letter Generation...")
    try:
        agent = JobSearchAgent()
        await agent.initialize() # Essential!
        
        mock_job = {
            "title": "Boulanger Artisan",
            "company": "Au Pain Doré",
            "description": "Nous cherchons un boulanger passionné...",
            "required_skills": ["pétrissage", "cuisson", "rigueur"]
        }
        
        mock_cv = {
            "skills": ["pétrissage", "levain", "ponctualité"],
            "experience_years": 5,
            "education": "DEP Boulangerie"
        }
        
        letter = await agent.generate_cover_letter(mock_job, mock_cv)
        print(f"Letter generated (Length: {len(letter)} chars).")
        print("Preview:")
        print(letter[:200] + "...")
        
    except Exception as e:
        print(f"❌ Cover Letter Failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_features())
