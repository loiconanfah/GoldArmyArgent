import asyncio
import os
import sys
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')

# Ensure we're in the right directory
load_dotenv()

async def main():
    print("🚀 Test HeadhunterAgent - OSINT LinkedIn Dorking")
    from agents.headhunter import headhunter_agent
    await headhunter_agent.initialize()
    
    print("\n🔍 Recherche de décideurs chez 'CGI Montreal'...")
    profiles = await headhunter_agent.find_decision_makers({
        "company_name": "CGI Montreal"
    })
    
    print("\n=== RÉSULTATS GEMINI PARSED ===")
    for idx, p in enumerate(profiles):
        print(f"{idx+1}. {p.get('name')} | {p.get('role')}")
        print(f"   Lien: {p.get('linkedin_url')}")
        
    print(f"\n✅ Total trouvés: {len(profiles)}")

if __name__ == "__main__":
    asyncio.run(main())
