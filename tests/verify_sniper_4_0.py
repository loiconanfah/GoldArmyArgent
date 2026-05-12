
import asyncio
import sys
import os
import json
from dotenv import load_dotenv

# Ensure project root is in path
sys.path.append(os.getcwd())
load_dotenv()

from agents.headhunter import headhunter_agent

async def verify():
    print("--- Sniper 4.0 Architecture Verification ---")
    
    # Initialize agent (this loads the LLM client)
    await headhunter_agent.initialize()
    
    company = "Google"
    print(f"Recherche de profils LinkedIn pour: {company}...")
    
    try:
        results = await headhunter_agent.find_decision_makers({"company_name": company})
        
        print(f"\n✅ {len(results)} profils trouvés:")
        print("="*50)
        for i, r in enumerate(results, 1):
            print(f"{i}. {r['name']}")
            print(f"   Poste: {r['role']}")
            print(f"   URL: {r['linkedin_url']}")
            print(f"   Info: {r.get('snippet', '')}")
            print("-" * 50)
            
        if not results:
            print("❌ Aucun résultat. Vérifiez la connectivité réseau ou le dorking.")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    await headhunter_agent.llm_client.close()

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(verify())
