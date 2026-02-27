
import asyncio
import sys
import os
from dotenv import load_dotenv

# Ensure project root is in path
sys.path.append(os.getcwd())
load_dotenv()

from agents.headhunter import headhunter_agent

async def main():
    print("--- Sniper 3.1 (Improved Grounding) Final Verification ---")
    
    await headhunter_agent.initialize()
    company = "Google"
    print(f"Recherche de décideurs pour: {company}...")
    
    try:
        results = await headhunter_agent.find_decision_makers({"company_name": company})
        
        print(f"\nRésultats ({len(results)} trouvés):")
        for r in results:
            print(f"Nom: {r['name']}")
            print(f"Rôle: {r['role']}")
            print(f"LinkedIn: {r['linkedin_url']}")
            print("-" * 30)

        if not results:
            print("Échec : Aucun profil trouvé. Vérifiez les logs pour plus de détails.")
            
    except Exception as e:
        print(f"Erreur fatale : {e}")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
