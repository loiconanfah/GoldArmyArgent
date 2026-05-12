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
email_pos = text_lower.find('email:')
phone_pos = text_lower.find('phone:')
addr_pos  = text_lower.find('address:')
exp_pos   = text_lower.find('dev backend')
skill_pos = text_lower.find('python')

# Write result to UTF-8 file to avoid console encoding issues
with open('test_ats_result.txt', 'w', encoding='utf-8') as out:
    out.write("=== ATS Text Extraction (first 600 chars) ===\n")
    out.write(text[:600])
    out.write("\n\n---\n")
    out.write(f"Name at pos    : {name_pos}\n")
    out.write(f"Email: at pos  : {email_pos}\n")
    out.write(f"Phone: at pos  : {phone_pos}\n")
    out.write(f"Address: at pos: {addr_pos}\n")
    out.write(f"Exp at pos     : {exp_pos}\n")
    out.write(f"Skills at pos  : {skill_pos}\n")
    out.write(f"PDF size       : {len(pdf)} bytes\n\n")

    ok = (name_pos == 0 and email_pos != -1 and phone_pos != -1 
          and addr_pos != -1 and name_pos < exp_pos < skill_pos)
    if ok:
        out.write("PERFECT: Nom, Email, Phone, Address -> Experience -> Skills - ORDER 100% CORRECT\n")
    else:
        out.write("FAIL: ATS order is wrong\n")
        if email_pos == -1:
            out.write("  - Email NOT found!\n")
        if phone_pos == -1:
            out.write("  - Phone NOT found!\n")
        if addr_pos == -1:
            out.write("  - Address NOT found!\n")

print("Done. See test_ats_result.txt for results.")
