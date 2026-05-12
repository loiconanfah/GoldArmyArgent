"""Test de l'intégration du HeadhunterAgent dans l'orchestrateur."""
import asyncio
import sys
from pathlib import Path

# Ajouter le répertoire au path
sys.path.insert(0, str(Path(__file__).parent))

from core.orchestrator import orchestrator

async def test_linkedin_routing():
    print("Starting orchestrator...")
    await orchestrator.start()
    
    print("\nSending LinkedIn search task...")
    task = {
        "id": "linkedin-test-001",
        "description": "Trouve moi des recruteurs chez Google sur LinkedIn",
        "agent_type": "headhunter" # On force le type pour le premier test
    }
    
    print(f"Executing task with HeadhunterAgent...")
    result = await orchestrator.execute_task(task)
    
    print("\n" + "="*70)
    print("RESULT:")
    print("="*70)
    print(f"Success: {result.get('success', False)}")
    
    if result.get('success'):
        profiles = result.get('profiles', [])
        print(f"Number of profiles found: {len(profiles)}")
        for i, p in enumerate(profiles[:3], 1):
            print(f"\nProfile {i}:")
            print(f"  Name: {p.get('name')}")
            print(f"  Role: {p.get('role')}")
            print(f"  URL: {p.get('linkedin_url')}")
    else:
        print(f"Error: {result.get('error')}")
    
    print("="*70)
    
    await orchestrator.stop()
    print("\nTest completed!")

if __name__ == "__main__":
    asyncio.run(test_linkedin_routing())
