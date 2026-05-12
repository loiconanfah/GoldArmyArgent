import asyncio
from agents.orchestrator import OrchestratorAgent

async def test():
    orch = OrchestratorAgent()
    await orch.initialize()
    task = {
        "query": "Audite et réécris mon CV pour les ATS",
        "cv_text": "Développeur backend très expérimenté en C# et Python.",
        "cv_filename": "CV_Yvan.pdf",
        "action": "",
        "session_id": "test_script_1"
    }
    print("Sending task...")
    res = await orch.think(task)
    print("RESULT:")
    import json
    print(json.dumps(res, indent=2))

if __name__ == "__main__":
    asyncio.run(test())
