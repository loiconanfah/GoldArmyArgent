import sys
import os

sys.path.append(r'c:\Users\Utilisateur\PycharmProjects\GoldArmyArgent')

from core.cv_word_generator import generate_cv_word

# Realistic mock CV data
mock_cv = {
    "full_name": "Jean Dupont",
    "title": "Ingénieur DevOps / Cloud Architect",
    "email": "jean.dupont@email.com",
    "phone": "+33 6 12 34 56 78",
    "location": "Paris, France",
    "linkedin": "linkedin.com/in/jeandupont",
    "github": "github.com/jeandupont",
    "summary": "Ingénieur DevOps passionné avec plus de 5 ans d'expérience dans la conception, le déploiement et l'optimisation d'infrastructures cloud hautement disponibles et évolutives. Expert en automatisation CI/CD, conteneurisation (Kubernetes, Docker) et Infrastructure as Code (Terraform). Engagé à améliorer la vélocité des équipes de développement tout en garantissant la sécurité et la stabilité de la production.",
    "experiences": [
        {
            "title": "Lead DevOps Engineer",
            "company": "CloudTech Solutions",
            "location": "Paris, France",
            "start_date": "2023-01",
            "end_date": "Présent",
            "bullets": [
                "Conception et migration d'une infrastructure monolithique vers une architecture microservices sur AWS EKS, réduisant les coûts de serveurs de 35%.",
                "Mise en place de pipelines CI/CD complexes avec GitHub Actions et ArgoCD, réduisant le temps de déploiement de 45 minutes à 8 minutes.",
                "Automatisation complète du provisionnement des environnements avec Terraform et Ansible (Infrastructure as Code).",
                "Encadrement d'une équipe de 3 ingénieurs DevOps juniors et animation de workshops techniques."
            ]
        },
        {
            "title": "Ingénieur DevOps",
            "company": "SaaS Factory",
            "location": "Lyon, France",
            "start_date": "2020-06",
            "end_date": "2022-12",
            "bullets": [
                "Gestion et optimisation de clusters Kubernetes en production hébergeant plus de 50 applications critiques.",
                "Déploiement de solutions de monitoring et d'alerting (Prometheus, Grafana, ELK Stack), réduisant le MTTR (Mean Time to Resolution) de 40%.",
                "Renforcement de la sécurité de la chaîne d'approvisionnement logicielle via l'intégration de scans de vulnérabilités (Trivy, SonarQube) dans les pipelines de build."
            ]
        }
    ],
    "projects": [
        {
            "name": "KubeGuard - Open Source Kubernetes Operator",
            "description": "Opérateur Kubernetes custom codé en Go pour automatiser le nettoyage des ressources orphelines.",
            "bullets": [
                "Plus de 500 stars sur GitHub et utilisé par plus de 20 entreprises en production.",
                "Implémentation de patterns d'architecture de réconciliation robustes avec le controller-runtime Go."
            ]
        }
    ],
    "education": [
        {
            "degree": "Master en Informatique - Spécialité Cloud & Réseaux",
            "institution": "Université de Technologie de Paris",
            "location": "Paris",
            "year": "2020"
        }
    ],
    "skills": {
        "Cloud & Infrastructures": ["AWS", "Google Cloud", "Terraform", "Ansible", "Kubernetes", "Docker"],
        "CI/CD & Automatisation": ["GitHub Actions", "GitLab CI", "ArgoCD", "Jenkins"],
        "Développement & Scripts": ["Python", "Go", "Bash", "SQL"],
        "Monitoring & Logging": ["Prometheus", "Grafana", "Elasticsearch", "Loki"]
    },
    "languages": [
        {"language": "Français", "proficiency": "Langue maternelle"},
        {"language": "Anglais", "proficiency": "Professionnel (C1 - Score TOEIC 945)"}
    ],
    "certifications": [
        "AWS Certified Solutions Architect – Professional (2024)",
        "Certified Kubernetes Administrator (CKA) (2023)"
    ]
}

def test_themes():
    themes = ["goldarmy", "minimaliste", "executive", "creatif", "classique", "neon_tech", "scandinave", "timeline"]
    os.makedirs("scratch/output_cvs", exist_ok=True)
    
    for theme in themes:
        print(f"Generating CV for theme: {theme}...")
        try:
            docx_bytes = generate_cv_word(mock_cv, theme_id=theme)
            out_path = f"scratch/output_cvs/cv_{theme}.docx"
            with open(out_path, "wb") as f:
                f.write(docx_bytes)
            print(f"Saved: {out_path}")
        except Exception as e:
            print(f"Error for {theme}: {e}")

if __name__ == "__main__":
    test_themes()
