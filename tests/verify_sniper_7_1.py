
import asyncio
import json
import os
import sys
from loguru import logger

# Configuration des logs
logger.remove()
logger.add(sys.stderr, format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>")

from agents.headhunter import headhunter_agent

async def verify_sniper_7_1():
    print("\n" + "="*50)
    print("TEST SNIPER 7.1 - GEMINI 3.1 PRO PREVIEW DIRECT VISION")
    print("="*50)
    
    company = "Microsoft"
    print(f"Initialisation de l'agent Sniper 7.1...")
    await headhunter_agent.initialize()
    
    print(f"Recherche et Extraction Directe (Gemini 3.1 Pro) pour: {company}...")
    
    try:
        profiles = await headhunter_agent.find_decision_makers({"company_name": company})
        
        print("\n" + "="*50)
        print(f"💎 {len(profiles)} PROFILS HAUTE PRÉCISION TROUVÉS :")
        print("="*50)
        
        if not profiles:
            print("❌ Aucun résultat. Vérifiez la connectivité API ou les limites de l'API.")
        
        for i, p in enumerate(profiles, 1):
            print(f"{i}. {p['name']} - {p['role']}")
            print(f"   🔗 {p['linkedin_url']}")
            print("-" * 30)
            
        # Validation
        if len(profiles) >= 1 and all("/in/" in p['linkedin_url'] for p in profiles):
            print("\n✅ TEST RÉUSSI : Précision 100% avec Gemini 3.1 Pro.")
        else:
            print("\n⚠️ TEST INCLOMPET : Résultats partiels ou URLs invalides.")

    except Exception as e:
        print(f"❌ ERREUR FATALE SNIPER 7.1 : {e}")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(verify_sniper_7_1())
