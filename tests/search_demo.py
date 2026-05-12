"""Recherche d'emploi STANDALONE - Fonctionne SANS dépendances externes."""
import asyncio
from typing import List, Dict


# Données de test - Offres d'emploi Québec
MOCK_JOBS = [
    {
        "id": "job-001",
        "title": "Stage développeur Python/React - Junior",
        "company": "TechCorp Québec",
        "location": "Québec",
        "job_type": "stage",
        "required_skills": ["python", "react", "javascript", "sql", "git"],
        "required_experience": 0,
        "description": "Stage de 4 mois en développement web full-stack avec Python et React",
        "url": "https://ca.indeed.com/job/dev-python-001",
        "source": "Indeed"
    },
    {
        "id": "job-002",
        "title": "Développeur Junior - JavaScript/Node.js",
        "company": "WebSolutions Inc",
        "location": "Montréal",
        "job_type": "junior",
        "required_skills": ["javascript", "node", "react", "mongodb", "git"],
        "required_experience": 0,
        "description": "Poste junior en développement backend Node.js",
        "url": "https://www.jobboom.com/emploi/dev-node-002",
        "source": "Jobboom"
    },
    {
        "id": "job-003",
        "title": "Stage Data Science - Python",
        "company": "DataLab QC",
        "location": "Québec",
        "job_type": "stage",
        "required_skills": ["python", "sql", "data science", "machine learning"],
        "required_experience": 1,
        "description": "Stage en analyse de données et machine learning",
        "url": "https://ca.indeed.com/job/data-science-003",
        "source": "Indeed"
    },
    {
        "id": "job-004",
        "title": "Développeur Full-Stack Junior",
        "company": "StartupTech",
        "location": "Québec",
        "job_type": "junior",
        "required_skills": ["python", "javascript", "react", "docker", "sql"],
        "required_experience": 0,
        "description": "Développeur full-stack pour startup en croissance",
        "url": "https://www.jobboom.com/emploi/fullstack-004",
        "source": "Jobboom"
    },
    {
        "id": "job-005",
        "title": "Stage DevOps",
        "company": "CloudTech",
        "location": "Remote",
        "job_type": "stage",
        "required_skills": ["docker", "kubernetes", "linux", "git", "python"],
        "required_experience": 1,
        "description": "Stage en infrastructure cloud et déploiement",
        "url": "https://ca.indeed.com/job/devops-005",
        "source": "Indeed"
    },
]


def calculate_match_score(job: Dict, cv_profile: Dict) -> int:
    """Calcule le score de compatibilité (0-100)."""
    score = 0
    
    # Compétences (40 points)
    cv_skills = set(s.lower() for s in cv_profile.get("skills", []))
    job_skills = set(s.lower() for s in job.get("required_skills", []))
    
    if job_skills:
        skill_match = len(cv_skills & job_skills) / len(job_skills)
        score += int(skill_match * 40)
    
    # Expérience (25 points)
    cv_exp = cv_profile.get("experience_years", 0)
    job_exp = job.get("required_experience", 0)
    
    if cv_exp >= job_exp:
        score += 25
    elif cv_exp >= job_exp * 0.7:
        score += 15
    
    # Formation (20 points)
    if cv_profile.get("education"):
        score += 20
    
    # Localisation (10 points)
    if job.get("location", "").lower() in ["québec", "montreal", "remote"]:
        score += 10
    
    # Langues (5 points)
    if "français" in cv_profile.get("languages", []):
        score += 5
    
    return min(score, 100)


def get_matched_skills(job: Dict, cv_profile: Dict) -> List[str]:
    """Retourne les compétences matchées."""
    cv_skills = set(s.lower() for s in cv_profile.get("skills", []))
    job_skills = set(s.lower() for s in job.get("required_skills", []))
    return list(cv_skills & job_skills)


async def search_jobs():
    """Recherche et matching d'offres."""
    print("="*80)
    print("🎯 RECHERCHE D'EMPLOI - DÉVELOPPEUR JUNIOR (DEMO)")
    print("="*80)
    
    # Profil CV
    cv_profile = {
        "skills": ["python", "javascript", "react", "node", "sql", "git", "docker"],
        "experience_years": 0,  # Junior
        "education": "Baccalauréat en informatique",
        "languages": ["français", "anglais"]
    }
    
    print("\n👤 PROFIL:")
    print("-" * 80)
    print("Nom: Alexandre Martin")
    print("Poste recherché: Développeur Junior")
    print(f"Compétences: {', '.join(cv_profile['skills'])}")
    print(f"Expérience: {cv_profile['experience_years']} an(s)")
    print(f"Formation: {cv_profile['education']}")
    print(f"Langues: {', '.join(cv_profile['languages'])}")
    print("-" * 80)
    
    print(f"\n🔍 Analyse de {len(MOCK_JOBS)} offres...\n")
    
    # Matcher les offres
    matched = []
    for job in MOCK_JOBS:
        score = calculate_match_score(job, cv_profile)
        matched_skills = get_matched_skills(job, cv_profile)
        
        matched.append({
            **job,
            "match_score": score,
            "matched_skills": matched_skills
        })
    
    # Trier par score
    matched.sort(key=lambda x: x["match_score"], reverse=True)
    
    # Afficher résultats
    print("="*80)
    print(f"📊 RÉSULTATS: {len(matched)} OFFRES TROUVÉES")
    print("="*80)
    
    for i, job in enumerate(matched, 1):
        emoji = "🔥" if job['match_score'] >= 80 else "✅" if job['match_score'] >= 60 else "⚠️"
        
        print(f"\n{'='*80}")
        print(f"#{i} - {job['title']} {emoji}")
        print(f"{'='*80}")
        print(f"🏢 Entreprise: {job['company']}")
        print(f"📍 Localisation: {job['location']}")
        print(f"🎯 Score de compatibilité: {job['match_score']}%")
        print(f"✅ Compétences matchées ({len(job['matched_skills'])}): {', '.join(job['matched_skills'])}")
        print(f"🌐 Source: {job['source']}")
        print(f"🔗 Lien: {job['url']}")
        print(f"📝 Description: {job['description']}")
    
    # Statistiques
    print("\n" + "="*80)
    print("📊 STATISTIQUES")
    print("="*80)
    
    scores = [j['match_score'] for j in matched]
    avg_score = sum(scores) / len(scores)
    max_score = max(scores)
    excellent = len([s for s in scores if s >= 80])
    good = len([s for s in scores if 60 <= s < 80])
    
    print(f"📈 Score moyen: {avg_score:.1f}%")
    print(f"🔥 Meilleur score: {max_score}%")
    print(f"⭐ Offres excellentes (≥80%): {excellent}")
    print(f"✅ Offres bonnes (60-79%): {good}")
    
    # Recommandations
    print("\n" + "="*80)
    print("💡 RECOMMANDATIONS")
    print("="*80)
    
    top_jobs = [j for j in matched if j['match_score'] >= 80]
    if top_jobs:
        print(f"\n🎯 POSTULER EN PRIORITÉ ({len(top_jobs)} offres):")
        for job in top_jobs:
            print(f"  • {job['title']} chez {job['company']} ({job['match_score']}%)")
    
    print("\n📧 PROCHAINES ÉTAPES:")
    print("  1. Personnaliser CV/lettre pour chaque offre")
    print("  2. Rechercher l'entreprise sur LinkedIn")
    print("  3. Préparer questions pour entrevue")
    print("  4. Postuler aux offres ≥80% en premier")
    
    print("\n" + "="*80)
    print("✅ Recherche terminée! Bonne chance! 🍀")
    print("="*80)


if __name__ == "__main__":
    print("\n🚀 Démarrage de la recherche...\n")
    asyncio.run(search_jobs())
