import asyncio
import os
import sys

# Ajouter le répertoire courant au path pour les imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from loguru import logger
from agents.job_searcher import JobSearchAgent
from core.contacts import contacts_manager

async def main():
    logger.info("Démarrage du test d'extraction parallèle massif...")
    
    # Nettoyer les contacts existants pour le test (optionnel)
    # contacts_manager.contacts = [] 
    
    agent = JobSearchAgent()
    
    action_plan = {
        "criteria": {"keywords": "developpeur", "location": "Montreal"},
        "limit": 5, # Petit test
        "cv_profile": {}
    }
    
    logger.info("Lancement de agent.act()...")
    result = await agent.act(action_plan)
    
    logger.info(f"Recherche terminée. Jobs retournés: {result.get('total_jobs_found')}")
    for job in result.get('matched_jobs', []):
        logger.info(f"- {job.get('title')} @ {job.get('company')} | Source: {job.get('source')} | Email: {job.get('apply_email')} | Scraped: {job.get('scraped')}")
        
    logger.info(f"Total contacts in DB: {len(contacts_manager.get_all_contacts())}")

asyncio.run(main())
