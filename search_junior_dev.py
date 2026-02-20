"""Recherche d'offres pour développeur junior."""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from core.orchestrator import orchestrator


# CV pour développeur junior
CV_DEV_JUNIOR = """
Alexandre Martin
Développeur Junior - Passionné de technologie

FORMATION:
- Baccalauréat en génie logiciel, Université Laval (2025)
- DEC en informatique, Cégep de Sainte-Foy (2022)

COMPÉTENCES TECHNIQUES:
- Langages: Python, JavaScript, Java, C++, SQL
- Web: React, Node.js, HTML, CSS, Express
- Bases de données: PostgreSQL, MongoDB, MySQL
- Outils: Git, GitHub, Docker, VS Code, Linux
- Méthodologies: Agile, Scrum

PROJETS:
- Application web de gestion de tâches (React + Node.js) - 8 mois
- API REST pour e-commerce (Python/Flask) - 6 mois
- Bot Discord en Python - 4 mois
- Site web portfolio personnel - Ongoing

EXPÉRIENCE:
- Stage développeur web (4 mois) - Startup locale
- Projets universitaires collaboratifs - 2 ans
- Contributions open source sur GitHub

LANGUES:
- Français: Langue maternelle
- Anglais: Avancé (lu, écrit, parlé)

INTÉRÊTS:
- Développement full-stack
- Intelligence artificielle
- DevOps et automatisation
- Contribution open source
"""


async def search_junior_dev_jobs():
    """Recherche d'offres pour développeur junior."""
    print("="*80)
    print("🎯 RECHERCHE D'EMPLOI - DÉVELOPPEUR JUNIOR")
    print("="*80)
    
    await orchestrator.start()
    
    # Tâche de recherche
    task = {
        "id": "junior-dev-search",
        "description": "Rechercher des postes de développeur junior au Québec",
        "agent_type": "job_searcher",
        "cv_text": CV_DEV_JUNIOR,
        "filters": {
            "location": "Québec",
            "job_type": "junior",  # Développeur junior
            "domain": "développeur"
        }
    }
    
    print("\n👤 PROFIL:")
    print("-" * 80)
    print("Nom: Alexandre Martin")
    print("Poste recherché: Développeur Junior")
    print("Compétences clés: Python, JavaScript, React, Node.js, SQL")
    print("Expérience: Stage 4 mois + Projets 2 ans")
    print("Localisation: Québec")
    print("-" * 80)
    
    print("\n🔍 LANCEMENT DE LA RECHERCHE...")
    print("📍 Localisation: Québec")
    print("💼 Type de poste: Développeur Junior")
    print("🌐 Sources: Indeed Canada + Jobboom")
    print()
    
    # Exécuter la recherche
    result = await orchestrator.execute_task(task)
    
    # Afficher les résultats
    print("\n" + "="*80)
    print("📊 RÉSULTATS DE LA RECHERCHE")
    print("="*80)
    
    if result.get("success"):
        total = result['total_jobs_found']
        matched = len(result['matched_jobs'])
        
        print(f"\n✅ Recherche réussie!")
        print(f"📈 {total} offres trouvées")
        print(f"🎯 {matched} offres compatibles avec votre profil")
        
        # Profil extrait
        print("\n" + "-"*80)
        print("👤 PROFIL ANALYSÉ:")
        print("-"*80)
        cv_profile = result.get("cv_profile", {})
        skills = cv_profile.get('skills', [])
        print(f"✅ Compétences détectées ({len(skills)}): {', '.join(skills[:10])}")
        print(f"📅 Expérience: {cv_profile.get('experience_years', 0)} an(s)")
        print(f"🎓 Formation: {cv_profile.get('education', 'N/A')}")
        print(f"🗣️ Langues: {', '.join(cv_profile.get('languages', []))}")
        
        # Top offres
        print("\n" + "="*80)
        print(f"🏆 TOP {min(10, matched)} OFFRES RECOMMANDÉES")
        print("="*80)
        
        for i, job in enumerate(result["matched_jobs"][:10], 1):
            print(f"\n{'='*80}")
            print(f"#{i} - {job['title']}")
            print(f"{'='*80}")
            print(f"🏢 Entreprise: {job['company']}")
            print(f"📍 Localisation: {job['location']}")
            print(f"🎯 Score de compatibilité: {job['match_score']}% {'🔥' if job['match_score'] >= 80 else '✅' if job['match_score'] >= 60 else '⚠️'}")
            
            # Compétences matchées
            matched_skills = job.get('matched_skills', [])
            if matched_skills:
                print(f"✅ Compétences matchées ({len(matched_skills)}): {', '.join(matched_skills[:8])}")
            
            # Justification
            justification = job.get('match_justification', '')
            if justification:
                print(f"💡 Analyse: {justification[:200]}...")
            
            # Source et lien
            print(f"🌐 Source: {job.get('source', 'Test')}")
            print(f"🔗 Lien: {job.get('url', 'N/A')}")
            
            # Description courte
            desc = job.get('description', '')
            if desc:
                print(f"📝 Description: {desc[:150]}...")
        
        # Statistiques
        print("\n" + "="*80)
        print("📊 STATISTIQUES")
        print("="*80)
        
        scores = [j['match_score'] for j in result['matched_jobs']]
        if scores:
            avg_score = sum(scores) / len(scores)
            max_score = max(scores)
            excellent = len([s for s in scores if s >= 80])
            good = len([s for s in scores if 60 <= s < 80])
            
            print(f"📈 Score moyen: {avg_score:.1f}%")
            print(f"🔥 Meilleur score: {max_score}%")
            print(f"⭐ Offres excellentes (≥80%): {excellent}")
            print(f"✅ Offres bonnes (60-79%): {good}")
        
        # Conseils
        print("\n" + "="*80)
        print("💡 PROCHAINES ÉTAPES")
        print("="*80)
        print("1. 📧 Postuler aux offres avec score ≥ 80%")
        print("2. 📝 Personnaliser CV/lettre pour chaque offre")
        print("3. 🔍 Rechercher l'entreprise sur LinkedIn")
        print("4. 📞 Préparer questions pour entrevue")
        print("5. 🔄 Relancer la recherche dans 2-3 jours")
    
    else:
        print(f"\n❌ Erreur: {result.get('error', 'Inconnue')}")
    
    print("\n" + "="*80)
    
    await orchestrator.stop()
    print("\n✅ Recherche terminée! Bonne chance! 🍀")


if __name__ == "__main__":
    print("\n🚀 Démarrage de la recherche d'emploi...")
    print("⏱️ Cela peut prendre 10-30 secondes...\n")
    asyncio.run(search_junior_dev_jobs())
