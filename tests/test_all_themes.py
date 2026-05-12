"""Test all 10 CV themes for: PDF generation success + ATS text extraction."""
import sys, io
sys.path.insert(0, '.')

from core.cv_ats_generator import generate_ats_cv_pdf, THEMES
from PyPDF2 import PdfReader

cv_data = {
    'full_name': 'Jean Dupont',
    'title': 'Ingénieur Logiciel Senior',
    'email': 'jean@test.com',
    'phone': '+33 6 12 34 56 78',
    'location': 'Montréal, QC, Canada',
    'linkedin': 'linkedin.com/in/jean-dupont',
    'summary': 'Expert backend avec 5 ans d\'expérience en développement FastAPI, microservices, et CI/CD.',
    'experiences': [
        {
            'title': 'Développeur Backend Senior',
            'company': 'Tech SA',
            'location': 'Paris',
            'start_date': 'Jan 2020',
            'end_date': 'Présent',
            'bullets': [
                'Développé 12 microservices FastAPI réduisant la latence P99 de 340ms à 180ms (-47%)',
                'Automatisé le pipeline CI/CD avec GitHub Actions, atteignant 0 downtime deploiement, fréquence x3',
            ]
        }
    ],
    'skills': {
        'Langages': ['Python', 'TypeScript', 'Go'],
        'Frameworks': ['FastAPI', 'React', 'Docker'],
    },
    'education': [
        {'degree': 'B.Sc. Génie Informatique', 'institution': 'Polytechnique Montréal', 'year': '2019'}
    ],
    'certifications': ['AWS Solutions Architect Associate (2023)'],
    'languages': ['Français (natif)', 'Anglais (courant)'],
}

results = []
all_pass = True

for theme_id in THEMES:
    try:
        pdf = generate_ats_cv_pdf(cv_data, theme_id=theme_id)
        reader = PdfReader(io.BytesIO(pdf))
        text = reader.pages[0].extract_text().lower()

        name_pos  = text.find('jean dupont')
        # Support both EN labels (email, phone, address) and FR labels (e-mail, téléphone, adresse)
        email_pos = max(text.find('email'), text.find('e-mail'))
        phone_pos = max(text.find('phone'), text.find('t'), text.find('téléphone'))
        # For phone, search specifically
        for token in ['phone', 'téléphone', 'tél']:
            p = text.find(token)
            if p != -1:
                phone_pos = p
                break
        else:
            phone_pos = -1
        # For address
        for token in ['address', 'adresse']:
            p = text.find(token)
            if p != -1:
                addr_pos = p
                break
        else:
            addr_pos = -1

        # Skills and experience
        for token in ['développeur', 'dev backend', 'backend']:
            p = text.find(token)
            if p != -1:
                exp_pos = p
                break
        else:
            exp_pos = -1
        skill_pos = text.find('python')

        ok_order = (name_pos == 0 and email_pos != -1 and phone_pos != -1
                    and addr_pos != -1 and name_pos < exp_pos < skill_pos)
        status = "✅ PASS" if ok_order else "❌ FAIL"
        if not ok_order:
            all_pass = False

        family = THEMES[theme_id]["family"]
        results.append(
            f"{status}  [{family}] {theme_id:12s}  "
            f"name={name_pos:3d}  email={email_pos:3d}  phone={phone_pos:3d}  "
            f"addr={addr_pos:3d}  exp={exp_pos:3d}  skills={skill_pos:3d}  "
            f"size={len(pdf):5d}b"
        )
    except Exception as e:
        all_pass = False
        results.append(f"❌ CRASH  {theme_id:12s}  ERROR: {e}")

with open('test_all_themes.txt', 'w', encoding='utf-8') as f:
    f.write("╔══════════════════════════════════════════════════════════════════════════════╗\n")
    f.write("║           ALL 10 CV THEMES — ATS EXTRACTION TEST RESULTS                  ║\n")
    f.write("╠══════════════════════════════════════════════════════════════════════════════╣\n")
    for r in results:
        f.write(r + "\n")
    f.write("╠══════════════════════════════════════════════════════════════════════════════╣\n")
    verdict = "✅ ALL 10 THEMES PASSED" if all_pass else "❌ SOME THEMES FAILED — SEE ABOVE"
    f.write(f"║  {verdict}\n")
    f.write("╚══════════════════════════════════════════════════════════════════════════════╝\n")

print("Done. See test_all_themes.txt")
