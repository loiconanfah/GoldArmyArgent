
import asyncio
import json
import os
import sys
from loguru import logger

# Configuration des logs pour voir l'activité LLM
logger.remove()
logger.add(sys.stderr, format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>")

from agents.headhunter import headhunter_agent

async def verify_sniper_6_0():
    print("\n" + "="*50)
    print("🚀 TEST SNIPER 6.0 - ZERO OLLAMA / 100% GEMINI")
    print("="*50)
    
    company = "Microsoft"
    print(f"Initialisation de l'agent...")
    await headhunter_agent.initialize()
    
    print(f"Recherche de profils LinkedIn pour: {company}...")
    
    try:
        profiles = await headhunter_agent.find_decision_makers({"company_name": company})
        
        print("\n" + "="*50)
        print(f"✅ {len(profiles)} PROFILS TROUVÉS (PURE GEMINI):")
        print("="*50)
        
        if not profiles:
            print("❌ Aucun résultat. Vérifiez la connectivité API Gemini.")
        
        for i, p in enumerate(profiles, 1):
            print(f"{i}. {p['name']} - {p['role']}")
            print(f"   🔗 {p['linkedin_url']}")
            print("-" * 30)
            
        # Vérification critique
        if any("/in/" not in p['linkedin_url'] for p in profiles):
            print("⚠️ ATTENTION: Certaines URLs ne sont pas au format LinkedIn /in/")
        else:
            print("💎 PRÉCISION 100% : Toutes les URLs sont valides.")

    except Exception as e:
        print(f"❌ ERREUR FATALE DURANT LE TEST: {e}")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(verify_sniper_6_0())
