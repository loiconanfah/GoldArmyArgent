"""Script de test pour vérifier l'intégration des portails gouvernementaux."""
import asyncio
import sys
import os

sys.path.append(os.getcwd())

from agents.job_searcher import JobSearchAgent
from loguru import logger

async def test_gov_search_france():
    logger.info("🚀 Démarrage du test GovSearcher sur la France...")
    
    agent = JobSearchAgent()
    
    task = {
        "id": "test-gov-france",
        "query": "développeur python",
        "location": "Paris",
        "limit": 5
    }
    
    # Phase Think
    plan = await agent.think(task, cv_text="Développeur Python expérimenté.")
    
    # Phase Act
    results = await agent.act(plan)
    
    logger.success(f"🏁 Test terminé ! Jobs trouvés: {len(results.get('matched_jobs', []))}")
    
    gov_results = [j for j in results.get('matched_jobs', []) if "Gouvernement" in j.get('source', '')]
    if gov_results:
        logger.success(f"🏛️ {len(gov_results)} offres gouvernementales trouvées !")
    else:
        logger.warning("🏛️ Aucune offre gouvernementale trouvée (Vérifier les logs HunterAgent).")
    
    for i, job in enumerate(results.get('matched_jobs', [])):
        print(f"[{i+1}] {job.get('title')} @ {job.get('company')} - Source: {job.get('source')}")
        print(f"    URL: {job.get('url')[:100]}...")

if __name__ == "__main__":
    asyncio.run(test_gov_search_france())
