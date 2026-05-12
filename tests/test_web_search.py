"""Test de recherche web réelle."""
import asyncio
import sys
from pathlib import Path

# Force UTF-8 encoding for Windows console
sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, str(Path(__file__).parent))

from core.orchestrator import orchestrator


EXEMPLE_CV = """
Jean Dupont - Développeur Python

COMPÉTENCES:
- Python, JavaScript, React, SQL, Git, Docker

EXPÉRIENCE:
- 1 an de projets universitaires

FORMATION:
- Baccalauréat en informatique (en cours)

LANGUES:
- Français, Anglais
"""


async def test_web_search():
    """Test de recherche web réelle."""
    print("="*70)
    print("🌐 Test de Recherche Web RÉELLE")
    print("="*70)
    
    await orchestrator.start()
    
    task = {
        "id": "web-search-001",
        "description": "Recherche RÉELLE de stages informatique au Québec",
        "agent_type": "job_searcher",
        "cv_text": EXEMPLE_CV,
        "filters": {
            "location": "Québec",
            "job_type": "stage",
            "domain": "informatique"
        }
    }
    
    print(f"\n🔍 Recherche sur Indeed et Jobboom...")
    print(f"📍 Localisation: {task['filters']['location']}")
    print(f"🎯 Type: {task['filters']['job_type']}")
    
    result = await orchestrator.execute_task(task)
    
    print("\n" + "="*70)
    print("📊 RÉSULTATS")
    print("="*70)
    
    if result.get("success"):
        print(f"\n✅ {result['total_jobs_found']} offres trouvées")
        print(f"🎯 Top {len(result['matched_jobs'])} recommandations:\n")
        
        for i, job in enumerate(result["matched_jobs"][:5], 1):
            print(f"{i}. {job['title']}")
            print(f"   📍 {job['company']} - {job['location']}")
            print(f"   🎯 Score: {job['match_score']}%")
            print(f"   🌐 Source: {job.get('source', 'Test')}")
            print(f"   🔗 {job.get('url', 'N/A')[:60]}...")
            print()
    
    await orchestrator.stop()
    print("✅ Test terminé!")


if __name__ == "__main__":
    asyncio.run(test_web_search())
