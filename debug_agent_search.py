
import asyncio
import sys
from loguru import logger
from agents.job_searcher import JobSearchAgent
from config.settings import settings

# Force UTF-8 for Windows console
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Rediriger les logs vers stdout de manière safe
logger.remove()
logger.add(sys.stdout, format="{time} {level} {message}", level="INFO", enqueue=True)

async def debug_agent():
    print("DEBUG: Starting agent debug...")
    
    # Vérifier la config
    print(f"Jooble Key Configured: {bool(settings.jooble_api_key)}")
    print(f"RapidAPI Key Configured: {bool(settings.rapidapi_key)}")
    if settings.rapidapi_key:
        print(f"   Key: {settings.rapidapi_key[:5]}...")
    else:
        print("   X RapidAPI Key missing in settings!")

    agent = JobSearchAgent()
    
    # Mock des méthodes LLM pour éviter l'erreur d'initialisation
    async def mock_think(task):
        return {
            "task_id": task.get("id"),
            "cv_profile": {"target_roles": ["Python Developer", "Backend Engineer"]},
            "filters": task.get("filters"),
            "search_strategy": "Test Strategy",
            "keywords": ["Python", "Developer"]
        }
    
    agent.think = mock_think
    
    # Simuler l'input d'une tâche
    task = {
        "id": "debug-task",
        "filters": {
            "location": "Québec",
            "keywords": ["Python"]
        }
    }
    
    # 1. Think
    print("\nAGENT THINKING...")
    action_plan = await agent.think(task)
    print("Action Plan:", action_plan)
    
    # 2. Act
    print("\nAGENT ACTING (Search)...")
    results = await agent.act(action_plan)
    
    if results.get("success"):
        jobs = results.get("matched_jobs", [])
        print(f"\nSUCCESS: {len(jobs)} jobs found total.")
        
        sources = {}
        for job in jobs:
            src = job.get("source", "Unknown")
            sources[src] = sources.get(src, 0) + 1
            
        print("Source Distribution:")
        for src, count in sources.items():
            print(f"   - {src}: {count}")
    else:
        print(f"\nERROR: {results.get('error')}")

if __name__ == "__main__":
    asyncio.run(debug_agent())
