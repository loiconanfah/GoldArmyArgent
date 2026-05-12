"""Recherche d'emploi RAPIDE sans dépendance Ollama pour l'analyse CV."""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from agents.job_searcher import JobSearchAgent


# CV développeur junior
CV_DEV_JUNIOR = """
Alexandre Martin - Développeur Junior

COMPÉTENCES: Python, JavaScript, React, Node.js, SQL, Git, Docker
EXPÉRIENCE: 4 mois de stage
FORMATION: Baccalauréat en informatique
LANGUES: Français, Anglais
"""


async def quick_search():
    """Recherche rapide sans Ollama."""
    print("="*80)
    print("🎯 RECHERCHE RAPIDE - DÉVELOPPEUR JUNIOR")
    print("="*80)
    
    # Créer l'agent directement
    agent = JobSearchAgent()
    
    # Tâche simplifiée
    task = {
        "id": "quick-search",
        "description": "Recherche développeur junior Québec",
        "cv_text": CV_DEV_JUNIOR,
        "filters": {
            "location": "Québec",
            "job_type": "junior",
            "domain": "développeur"
        }
    }
    
    print("\n👤 PROFIL: Alexandre Martin")
    print("💼 Poste: Développeur Junior")
    print("📍 Localisation: Québec\n")
    
    print("🔍 Recherche en cours...")
    
    # Exécuter sans passer par l'orchestrateur (évite Ollama)
    # On va directement chercher et matcher
    from tools.web_searcher import JobWebSearcher
    
    searcher = JobWebSearcher()
    
    # Recherche web
    print("🌐 Recherche sur Indeed et Jobboom...")
    try:
        jobs = await searcher.search_jobs(
            keywords="développeur junior python",
            location="Québec",
            job_type="junior",
            max_results=20
        )
        
        if not jobs:
            print("📦 Utilisation des données de test...")
            jobs = agent._get_mock_jobs(task["filters"])
    except Exception as e:
        print(f"⚠️ Erreur web search: {e}")
        print("📦 Utilisation des données de test...")
        jobs = agent._get_mock_jobs(task["filters"])
    
    # Profil simple (sans LLM)
    cv_profile = {
        "skills": ["python", "javascript", "react", "node", "sql", "git", "docker"],
        "experience_years": 0,  # Junior
        "education": "Baccalauréat",
        "languages": ["français", "anglais"]
    }
    
    # Matcher
    print(f"🎯 Matching de {len(jobs)} offres...\n")
    
    matched = []
    for job in jobs:
        score = agent._calculate_match_score(job, cv_profile)
        matched_skills = agent._get_matched_skills(job, cv_profile)
        
        matched.append({
            **job,
            "match_score": score,
            "matched_skills": matched_skills,
            "match_justification": f"Score basé sur {len(matched_skills)} compétences matchées"
        })
    
    # Trier
    matched.sort(key=lambda x: x["match_score"], reverse=True)
    
    # Afficher résultats
    print("="*80)
    print(f"📊 RÉSULTATS: {len(matched)} offres trouvées")
    print("="*80)
    
    for i, job in enumerate(matched[:10], 1):
        print(f"\n#{i} - {job['title']}")
        print(f"🏢 {job['company']} - {job['location']}")
        print(f"🎯 Score: {job['match_score']}% {'🔥' if job['match_score'] >= 80 else '✅'}")
        print(f"✅ Compétences: {', '.join(job['matched_skills'][:5])}")
        print(f"🌐 Source: {job.get('source', 'Test')}")
        print(f"🔗 {job.get('url', 'N/A')[:70]}...")
    
    # Stats
    print("\n" + "="*80)
    scores = [j['match_score'] for j in matched]
    print(f"📈 Score moyen: {sum(scores)/len(scores):.1f}%")
    print(f"🔥 Meilleur: {max(scores)}%")
    print(f"⭐ Excellentes (≥80%): {len([s for s in scores if s >= 80])}")
    print("="*80)
    
    print("\n✅ Recherche terminée!")


if __name__ == "__main__":
    print("\n🚀 Recherche RAPIDE (sans Ollama)...\n")
    asyncio.run(quick_search())
