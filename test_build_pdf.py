import asyncio
import json
import httpx

async def test_pdf_generation():
    cv_json_payload = {
        "full_name": "JOHN DOE TEST",
        "title": "Ingénieur Logiciel Full-Stack",
        "email": "john.test@example.com",
        "phone": "+33 6 12 34 56 78",
        "location": "Paris, France",
        "linkedin": "linkedin.com/in/johndoe",
        "github": "github.com/johndoe",
        "summary": "Développeur passionné avec 5 ans d'expérience dans la création d'applications web scalables et ergonomiques. Habitué aux environnements agiles et à l'optimisation des performances.",
        "experiences": [
            {
                "title": "Développeur Full-Stack Senior",
                "company": "Tech Innovators",
                "start_date": "2020-01",
                "end_date": "Présent",
                "location": "Paris",
                "bullets": [
                    "Conception et développement d'une architecture microservices avec FastAPI et Vue.js.",
                    "Amélioration des performances de la base de données PostgreSQL réduisant les requêtes lentes de 40%."
                ]
            }
        ],
        "projects": [
            {
                "name": "Plateforme e-commerce",
                "description": "Création from scratch d'une boutique en ligne avec gestion de panier et paiement Stripe.",
                "bullets": ["Stack: Vue 3, TailwindCSS, Node.js", "Déploiement sur AWS EC2"]
            }
        ],
        "education": [
            {
                "degree": "Master en Informatique",
                "institution": "Université Paris-Saclay",
                "year": "2019",
                "location": "Paris"
            }
        ],
        "skills": {
            "Langages": ["Python", "JavaScript", "TypeScript"],
            "Frameworks": ["Vue.js", "FastAPI", "React"],
            "Outils": ["Git", "Docker", "AWS"]
        },
        "languages": [
            {"language": "Français", "proficiency": "Maternel"},
            {"language": "Anglais", "proficiency": "Courant (C1)"}
        ],
        "certifications": [
            {"name": "AWS Certified Solutions Architect", "issuer": "Amazon Web Services", "year": "2022"}
        ]
    }

    url = "http://127.0.0.1:8000/api/generate-cv-pdf"
    
    # We send cv_json as a JSON string, which is what the frontend does.
    payload = {
        "cv_json": json.dumps(cv_json_payload),
        "filename": "test_layout_midnight",
        "theme_id": "midnight"
    }

    print(f"Envoi requête avec payload de type {type(payload['cv_json'])} à {url}...")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload, timeout=10)
            if response.status_code == 200:
                with open("test_output_cv.pdf", "wb") as f:
                    f.write(response.content)
                print("✅ Succès ! Le PDF a été généré : test_output_cv.pdf")
            else:
                print(f"❌ Erreur {response.status_code}: {response.text}")
        except Exception as e:
            print(f"Erreur de connexion : {e}")

if __name__ == "__main__":
    asyncio.run(test_pdf_generation())
