"""Test de l'agent de recherche d'emploi."""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from core.orchestrator import orchestrator


# Exemple de CV
EXEMPLE_CV = """
Jean Dupont
Étudiant en informatique - Baccalauréat

FORMATION:
- Baccalauréat en informatique, Université Laval (en cours)
- DEC en informatique, Cégep de Sainte-Foy

COMPÉTENCES TECHNIQUES:
- Langages: Python, JavaScript, Java, SQL, HTML, CSS
- Frameworks: React, Node.js, Flask
- Outils: Git, Docker, Linux
- Bases de données: PostgreSQL, MongoDB

EXPÉRIENCE:
- Projet universitaire: Application web de gestion (Python/React) - 6 mois
- Projet personnel: Bot Discord en Python - 3 mois

LANGUES:
- Français: Langue maternelle
- Anglais: Intermédiaire

INTÉRÊTS:
- Développement web
- Intelligence artificielle
- Open source
"""


async def test_job_search():
    """Test de recherche d'emploi avec CV."""
    print("="*70)
    print("🎯 Test de Recherche d'Emploi - Agent JobSearcher")
    print("="*70)
    
    await orchestrator.start()
    
    # Créer la tâche de recherche
    task = {
        "id": "job-search-001",
        "description": "Rechercher des stages en informatique au Québec adaptés à mon CV",
        "agent_type": "job_searcher",
        "cv_text": EXEMPLE_CV,
        "filters": {
            "location": "Québec",
            "job_type": "stage",
            "domain": "informatique"
        }
    }
    
    print(f"\n📝 CV fourni:")
    print("-" * 70)
    print(EXEMPLE_CV[:200] + "...")
    print("-" * 70)
    
    print(f"\n🔍 Critères de recherche:")
    print(f"  - Localisation: {task['filters']['location']}")
    print(f"  - Type: {task['filters']['job_type']}")
    print(f"  - Domaine: {task['filters']['domain']}")
    
    print(f"\n🚀 Lancement de la recherche...\n")
    
    # Exécuter la recherche
    result = await orchestrator.execute_task(task)
    
    # Afficher les résultats
    print("\n" + "="*70)
    print("📊 RÉSULTATS DE LA RECHERCHE")
    print("="*70)
    
    if result.get("success"):
        print(f"\n✅ Recherche réussie!")
        print(f"📈 {result['total_jobs_found']} offres trouvées")
        print(f"🎯 {len(result['matched_jobs'])} offres matchées\n")
        
        # Profil extrait
        print("👤 PROFIL EXTRAIT DU CV:")
        print("-" * 70)
        cv_profile = result.get("cv_profile", {})
        print(f"Compétences: {', '.join(cv_profile.get('skills', [])[:8])}")
        print(f"Expérience: {cv_profile.get('experience_years', 0)} an(s)")
        print(f"Formation: {cv_profile.get('education', 'N/A')}")
        print(f"Langues: {', '.join(cv_profile.get('languages', []))}")
        
        # Top offres
        print(f"\n🏆 TOP {min(5, len(result['matched_jobs']))} OFFRES RECOMMANDÉES:")
        print("="*70)
        
        for i, job in enumerate(result["matched_jobs"][:5], 1):
            print(f"\n{i}. {job['title']}")
            print(f"   📍 {job['company']} - {job['location']}")
            print(f"   🎯 Score de compatibilité: {job['match_score']}%")
            print(f"   ✅ Compétences matchées: {', '.join(job.get('matched_skills', [])[:5])}")
            print(f"   💡 {job.get('match_justification', 'N/A')[:150]}...")
            print(f"   🔗 {job.get('url', 'N/A')}")
    else:
        print(f"\n❌ Erreur: {result.get('error', 'Inconnue')}")
    
    print("\n" + "="*70)
    
    await orchestrator.stop()
    print("\n✅ Test terminé!")


if __name__ == "__main__":
    asyncio.run(test_job_search())
