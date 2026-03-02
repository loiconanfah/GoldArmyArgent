import asyncio
import os
import sys
from loguru import logger

# Ajouter le répertoire racine au chemin
sys.path.append(os.path.abspath(os.path.curdir))

from llm.gemini_client import GeminiClient

async def test_presidents():
    # Initialisation du client
    client = GeminiClient()
    
    # Utilisation de 2.0-flash (le modèle standard pour Sniper Pass 2)
    model = "gemini-2.0-flash"
    prompt = "Donne-moi la liste chronologique des présidents des États-Unis avec leurs dates de mandat (les 10 premiers sous forme de liste courte)."
    
    logger.info(f"📡 Envoi de la requête à Gemini ({model}) pour la liste des présidents...")
    
    try:
        response = await client.generate(prompt, model=model)
        
        print("\n=== RÉPONSE DE GEMINI ===")
        print(response)
        print("=========================\n")
        
        logger.success("✅ Gemini a répondu avec succès !")
        
    except Exception as e:
        logger.error(f"❌ Échec de la requête : {e}")

if __name__ == "__main__":
    asyncio.run(test_presidents())
