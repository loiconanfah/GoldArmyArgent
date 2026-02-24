"""Script de test pour vérifier le nettoyage de query et l'exclusion de bruit."""
import asyncio
import sys
import os

sys.path.append(os.getcwd())

from agents.job_searcher import JobSearchAgent
from loguru import logger

async def test_precision_fix():
    logger.info("🚀 Démarrage du test de précision (Nettoyage + Exclusions)...")
    
    agent = JobSearchAgent()
    
    # On simule la requête avec la faute de frappe "Iogiciel"
    task = {
        "id": "test-precision",
        "query": "développer Iogiciel",
        "location": "France",
        "limit": 10
    }
    
    # Phase Think (doit nettoyer "Iogiciel" et générer des exclusions)
    plan = await agent.think(task, cv_text="Développeur Fullstack Python/React, expert en génie logiciel.")
    
    logger.info(f"🔍 Stratégie générée: {plan.get('criteria')}")
    
    # Phase Act
    results = await agent.act(plan)
    
    logger.success(f"🏁 Test terminé ! Jobs trouvés: {len(results.get('matched_jobs', []))}")
    
    for i, job in enumerate(results.get('matched_jobs', [])):
        print(f"[{i+1}] {job.get('title')} @ {job.get('company')} - Score: {job.get('match_score')}")
        print(f"    Justification: {job.get('match_justification')}")

if __name__ == "__main__":
    asyncio.run(test_precision_fix())
