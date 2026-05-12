"""Test rapide de GoldArmyArgent avec Ollama."""
import asyncio
import sys
from pathlib import Path

# Ajouter le répertoire au path
sys.path.insert(0, str(Path(__file__).parent))

from core.orchestrator import orchestrator


async def test_agent():
    """Test un agent avec Ollama."""
    print("🚀 Démarrage de l'orchestrateur...")
    await orchestrator.start()
    
    print("\n📝 Création d'une tâche de test...")
    task = {
        "id": "test-001",
        "description": "Explique-moi en 2 phrases ce qu'est l'intelligence artificielle",
        "agent_type": "researcher",
        "context": "Test du système"
    }
    
    print(f"\n🎯 Exécution de la tâche avec un agent {task['agent_type']}...")
    result = await orchestrator.execute_task(task)
    
    print("\n" + "="*70)
    print("📋 RÉSULTAT:")
    print("="*70)
    print(f"Succès: {result.get('success', False)}")
    print(f"\nRésultats:")
    print(result.get('findings', 'N/A'))
    print("="*70)
    
    await orchestrator.stop()
    print("\n✅ Test terminé!")


if __name__ == "__main__":
    asyncio.run(test_agent())
