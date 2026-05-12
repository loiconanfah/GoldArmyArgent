"""Script de test pour vérifier le Swarm Sniper sur Paris."""
import asyncio
import sys
import os

# Ajouter le dossier racine au path
sys.path.append(os.getcwd())

from agents.job_searcher import JobSearchAgent
from loguru import logger

async def test_paris_search():
    logger.info("🚀 Démarrage du test Swarm sur Paris...")
    
    agent = JobSearchAgent()
    
    # Simulation d'une tâche venant du frontend
    task = {
        "id": "test-paris",
        "query": "développeur logiciel",
        "location": "Paris",
        "limit": 5
    }
    
    # Phase Think (Planning via ProfileAgent)
    plan = await agent.think(task, cv_text="Développeur Python avec 3 ans d'expérience.")
    
    # Phase Act (Execution via Hunter & Judge)
    results = await agent.act(plan)
    
    logger.success(f"🏁 Test terminé ! Jobs trouvés: {len(results.get('matched_jobs', []))}")
    
    for i, job in enumerate(results.get('matched_jobs', [])):
        print(f"[{i+1}] {job.get('title')} @ {job.get('company')} ({job.get('location')}) - Score: {job.get('match_score')}")
        print(f"    Source: {job.get('source')} | URL: {job.get('url')[:50]}...")

if __name__ == "__main__":
    asyncio.run(test_paris_search())
