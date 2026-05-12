import asyncio
import os
import sys

# Ajouter le répertoire racine au PYTHONPATH
sys.path.insert(0, os.path.dirname(__file__))

from agents.mentor import MentorAgent
from loguru import logger

async def test_mentor_audit():
    logger.info("Démarrage du test d'audit CV ATS...")
    
    cv_text = """
    John Doe
    Développeur
    Contact: john@example.com
    
    Expérience:
    - Développeur chez TechCorp. J'ai codé des trucs. J'ai utilisé javascript et html.
    - Stagiaire. J'ai aidé l'équipe.
    
    Formation:
    - Bac en ingénierie.
    """
    
    mentor = MentorAgent()
    await mentor.initialize()
    
    result = await mentor.think({
        "action": "audit_cv",
        "cv_text": cv_text
    })
    
    import json
    # Print the full result to see the output
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    asyncio.run(test_mentor_audit())
