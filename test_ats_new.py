import sys, io
sys.path.insert(0, '.')

from core.cv_ats_generator import generate_ats_cv_pdf
from PyPDF2 import PdfReader

cv_data = {
    'full_name': 'Jean Dupont',
    'title': 'Ingenieur Logiciel Senior',
    'email': 'jean@test.com',
    'phone': '+33 6 12 34 56 78',
    'location': 'Montreal, QC',
    'summary': 'Expert backend avec 5 ans experience FastAPI, microservices, CI/CD',
    'experiences': [
        {
            'title': 'Dev Backend Senior',
            'company': 'Tech SA',
            'location': 'Paris',
            'start_date': 'Jan 2020',
            'end_date': 'Present',
            'bullets': [
                'Developpe 12 microservices FastAPI reduisant latence de 40 pct',
                'Automatise CI/CD avec GitHub Actions, 0 downtime deployments'
            ]
        }
    ],
    'skills': {
        'Langages': ['Python', 'TypeScript', 'Go'],
        'Frameworks': ['FastAPI', 'React', 'Docker'],
        'Bases de donnees': ['PostgreSQL', 'MongoDB', 'Redis']
    },
    'education': [
        {'degree': 'Bac. Genie Info', 'institution': 'Polytechnique Montreal', 'year': '2019'}
    ],
    'certifications': ['AWS Solutions Architect Associate (2023)'],
    'languages': ['Francais (natif)', 'Anglais (courant)']
}

pdf = generate_ats_cv_pdf(cv_data, theme_id='midnight')

with open('test_ats_new.pdf', 'wb') as f:
    f.write(pdf)

reader = PdfReader(io.BytesIO(pdf))
text = reader.pages[0].extract_text()
text_lower = text.lower()

name_pos  = text_lower.find('jean dupont')
exp_pos   = text_lower.find('dev backend')
skill_pos = text_lower.find('python')

print("=== ATS Text Extraction (first 600 chars) ===")
print(text[:600])
print("---")
print(f"Name at pos  : {name_pos}")
print(f"Exp at pos   : {exp_pos}")
print(f"Skills at pos: {skill_pos}")

if name_pos != -1 and exp_pos != -1 and skill_pos != -1 and name_pos < exp_pos < skill_pos:
    print("PERFECT: Nom -> Experience -> Skills - Ordre ATS 100% parfait")
elif name_pos != -1 and skill_pos != -1 and name_pos < skill_pos:
    print("GOOD: Nom before Skills - Acceptable ATS order")
else:
    print("FAIL: Wrong order")

print(f"PDF size: {len(pdf)} bytes")
