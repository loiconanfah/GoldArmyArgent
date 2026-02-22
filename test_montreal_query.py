import asyncio
import sys
import json
from pathlib import Path

# Force UTF-8
sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, str(Path(__file__).parent))

from agents.orchestrator import OrchestratorAgent

async def test_search():
    print("🚀 Test E2E API with 'developper logiciel montreal'")
    orchestrator = OrchestratorAgent()
    await orchestrator.initialize()
    
    task = {
        "message": "developper logiciel montreal",
        "query": "developper logiciel montreal",
        "cv_text": "",
        "nb_results": 10
    }
    
    response = await orchestrator.think(task)
    
    print("\n--- JSON OUTPUT TO VUE ---")
    print(json.dumps(response, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    asyncio.run(test_search())
