import asyncio
import sys
import json
from pathlib import Path

# Force UTF-8
sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, str(Path(__file__).parent))

from agents.orchestrator import OrchestratorAgent

async def test_search():
    print("🚀 Test E2E API with 'developper c#' (and a simulated Sales CV)")
    orchestrator = OrchestratorAgent()
    await orchestrator.initialize()
    
    # Simuler le payload reçu par l'API
    # Un CV de vendeur, mais une requête explicite de "developper c#"
    task = {
        "message": "developper c#",
        "query": "developper c#",
        "cv_text": "Conseiller en vente depuis 5 ans chez Subaru. Spécialiste du service client et des ventes au détail.",
        "nb_results": 5
    }
    
    response = await orchestrator.think(task)
    
    print("\n--- JSON OUTPUT TO VUE ---")
    print(json.dumps(response, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    asyncio.run(test_search())
