
import asyncio
from agents.job_searcher import JobSearchAgent

async def test_synergy():
    agent = JobSearchAgent()
    
    # CV Mock: Profil Python Junior
    cv_text = "Junior Python Developer with SQL experience."
    
    # Mock LLM response to avoid initialization error
    async def mock_generate_response(prompt):
        import json
        return json.dumps({
            "skills": ["python", "sql", "html", "css", "git"],
            "experience_years": 1,
            "education": "DEC Informatique",
            "languages": ["français"],
            "domains": ["informatique"],
            "target_roles": ["Développeur Python", "Développeur Web"]
        })
    
    agent.generate_response = mock_generate_response

    # Profil déduit attendu qui doit contenir "Développeur Python"
    print("Analyzing CV...")
    cv_profile = await agent._analyze_cv(cv_text)
    print("Profile extracted:", cv_profile)
    
    # Offres Mocks
    good_job = {
        "title": "Développeur Python Junior",
        "description": "Nous cherchons un expert Python avec 1 an d'expérience. Maitrise SQL.",
        "required_skills": ["python", "sql"],
        "required_experience": 1,
        "location": "Québec"
    }
    
    bad_job = {
        "title": "Infirmier Auxiliaire",
        "description": "Soin des patients.",
        "required_skills": ["soins", "santé"],
        "required_experience": 3,
        "location": "Montréal"
    }
    
    print("\nCalculating synergy scores...")
    
    score_good = agent._calculate_match_score(good_job, cv_profile)
    print(f"Good Job Score: {score_good}/100 (Expected: > 70)")
    
    score_bad = agent._calculate_match_score(bad_job, cv_profile)
    print(f"Bad Job Score: {score_bad}/100 (Expected: < 30)")
    
    if score_good > score_bad + 40:
        print("\nSUCCESS: Synergy logic works! AI correctly discriminates jobs.")
    else:
        print("\nFAILURE: Score difference not significant enough.")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_synergy())
