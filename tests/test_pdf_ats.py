import os
import sys
import asyncio
from typing import Dict, Any
from reportlab.platypus import SimpleDocTemplate
from PyPDF2 import PdfReader

# Ajouter le répertoire racine au PYTHONPATH
sys.path.insert(0, os.path.dirname(__file__))

from core.cv_pdf_generator import generate_cv_pdf

# Données de test
cv_data_test = {
  "full_name": "Jean Dupont",
  "title": "Ingénieur Logiciel",
  "email": "jean@test.com",
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
      "bullets": ["Création d'APIs REST utilisant FastAPI."]
    }
  ],
  "skills": {
    "Langages": ["Python", "JavaScript"]
  }
}

async def test_extraction():
    # Tester reverse_sidebar qui échouait avant car la colonne de droite était dessinée en premier visuellement
    pdf_bytes = generate_cv_pdf(cv_data_test, theme_id="modern") # modern utilise reverse_sidebar
    
    with open("test_extract.pdf", "wb") as f:
        f.write(pdf_bytes)
        
    print("PDF généré. Test d'extraction :")
    reader = PdfReader("test_extract.pdf")
    text = reader.pages[0].extract_text()
    
    print("-" * 50)
    print(text.encode('cp1252', 'replace').decode('cp1252'))
    print("-" * 50)
    
    # Vérification empirique sur la nouvelle structure 'text'
    # Dans la couche invisible, c'est "Jean Dupont" puis plus tard "Python"
    text_lower = text.lower()
    name_pos = text_lower.find("jean dupont")
    skills_pos = text_lower.find("python")
    
    if name_pos < skills_pos and name_pos != -1:
        print("SUCCES : L'ordre de lecture ATS Dual-Layer (Nom -> Competences) est valide et conserve.")
    else:
        print("ECHEC : L'ordre ATS Dual-Layer ne fonctionne pas.")

if __name__ == "__main__":
    asyncio.run(test_extraction())
