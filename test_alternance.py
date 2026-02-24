"""Script de test pour vérifier le support alternance IA sur Paris."""
import asyncio
import sys
import os

sys.path.append(os.getcwd())

from agents.job_searcher import JobSearchAgent
from loguru import logger

async def test_alternance_ia_paris():
    logger.info("🚀 Démarrage du test Alternance IA sur Paris...")
    
    agent = JobSearchAgent()
    
    task = {
        "id": "test-alternance-ia",
        "query": "alternance développer IA",
        "location": "Paris",
        "limit": 10
    }
    
    # Phase Think
    plan = await agent.think(task, cv_text="Étudiant en Master IA, cherche alternance en Python/ML.")
    
    # Phase Act
    results = await agent.act(plan)
    
    logger.success(f"🏁 Test terminé ! Jobs trouvés: {len(results.get('matched_jobs', []))}")
    
    for i, job in enumerate(results.get('matched_jobs', [])):
        print(f"[{i+1}] {job.get('title')} @ {job.get('company')} ({job.get('location')}) - Score: {job.get('match_score')}")
        print(f"    Justification: {job.get('match_justification')}")
        print(f"    URL: {job.get('url')[:50]}...")

if __name__ == "__main__":
    asyncio.run(test_alternance_ia_paris())
