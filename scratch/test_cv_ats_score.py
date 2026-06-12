import asyncio
import os
import sys
import fitz  # PyMuPDF

# Configurer stdout pour UTF-8 sur Windows
if sys.platform.startswith('win'):
    sys.stdout.reconfigure(encoding='utf-8')

# Ajouter le PYTHONPATH
sys.path.insert(0, os.getcwd())

from core.cv_html_templates import build_html
from api.main import _ats_rule_score

cv_data_test = {
  "full_name": "Jean Dupont",
  "title": "Ingénieur Logiciel",
  "email": "jean.dupont@test.com",
  "phone": "+33 6 12 34 56 78",
  "location": "Paris, France",
  "summary": "Développeur passionné avec 5 ans d'expérience.",
  "experiences": [
    {
      "title": "Développeur Backend",
      "company": "Tech SA",
      "location": "Paris",
      "start_date": "Jan 2020",
      "end_date": "Présent",
      "bullets": [
        "Création d'APIs REST utilisant FastAPI et Python.",
        "Mise en place de CI/CD et déploiement cloud sur AWS.",
        "Optimisation des requêtes de base de données PostgreSQL."
      ]
    }
  ],
  "skills": {
    "Langages": ["Python", "JavaScript", "SQL"],
    "Frameworks": ["FastAPI", "Vue.js"]
  },
  "education": [
    {
      "degree": "Master en Informatique",
      "institution": "Université de Paris",
      "year": "2018",
      "location": "Paris"
    }
  ],
  "languages": ["Français", "Anglais"],
  "certifications": ["AWS Certified Cloud Practitioner"]
}

def _generate_pdf_sync(html: str) -> bytes:
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        browser = pw.chromium.launch(args=["--no-sandbox", "--disable-setuid-sandbox"])
        page = browser.new_page()
        page.set_content(html, wait_until="load", timeout=20000)
        p_bytes = page.pdf(format="A4", print_background=True, margin={"top": "0", "bottom": "0", "left": "0", "right": "0"})
        browser.close()
        return p_bytes

async def test_score():
    for template_id in ["goldarmy", "minimaliste", "executive", "creatif", "neon_tech", "timeline", "classique", "scandinave"]:
        print(f"\n================= TEMPLATE: {template_id} =================")
        html = build_html(template_id, cv_data_test)
        
        pdf_bytes = await asyncio.to_thread(_generate_pdf_sync, html)
        
        # Charger le PDF en mémoire
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        text = doc[0].get_text()
        doc.close()
        
        print(f"--- TEXTE EXTRAIT ({len(text)} chars) ---")
        print(text[:1000])
        print("---------------------------------------")
        
        # Calculer le score ATS
        score = _ats_rule_score(text)
        print(f"SCORE ATS OBTENU: {score}/100")
        
        # Diagnostics détaillés
        t = text.lower().strip()
        sections = [
            "expérience", "experience", "formation", "education", "études",
            "compétences", "competences", "skills", "compétence",
            "résumé", "resume", "summary", "profil", "objectif"
        ]
        found_sections = [s for s in sections if s in t]
        print(f"Sections trouvées: {found_sections} (Score max 35)")
        
        bullets_found = t.count("\n•") + t.count("\n-") + t.count("\n*") + t.count("•")
        print(f"Bullet points trouvés: {bullets_found} (Score max 25)")
        
        print(f"Longueur du texte: {len(text)} (Score max 20)")
        
        has_email = "@" in text or "email" in t
        has_phone = any(c.isdigit() for c in text) and ("tél" in t or "phone" in t or "06" in text or "07" in text)
        print(f"Email trouvé: {has_email}, Téléphone trouvé: {has_phone} (Score max 20)")

if __name__ == "__main__":
    asyncio.run(test_score())
