import asyncio
import sys
import json
from pathlib import Path

# Force UTF-8
sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, str(Path(__file__).parent))

from agents.orchestrator import OrchestratorAgent

async def test_e2e_api():
    print("🚀 Test E2E API (Simulating Vue Frontend)")
    orchestrator = OrchestratorAgent()
    await orchestrator.initialize()
    
    # Simuler le payload reçu par l'API
    task = {
        "message": "je cherche un stage développeur logiciel à Montréal",
        "query": "je cherche un stage développeur logiciel à Montréal",
        "cv_text": "Compétences: Python, Vue, Tailwind. 1 an d'expérience.",
        "nb_results": 3
    }
    
    response = await orchestrator.think(task)
    
    print("\n--- JSON OUTPUT TO VUE ---")
    print(json.dumps(response, indent=2, ensure_ascii=False))
    
    if "content" in response and isinstance(response["content"], dict) and "matched_jobs" in response["content"]:
        jobs = response["content"]["matched_jobs"]
        print(f"\n✅ SUCCESS! L'API a retourné un objet avec une liste de {len(jobs)} jobs structurés.")
    else:
        print("\n❌ ERREUR: Le format JSON attendu n'est pas correct.")

if __name__ == "__main__":
    asyncio.run(test_e2e_api())
