import io
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from typing import Dict, Any

def generate_cv_word(cv_data: Dict[str, Any]) -> bytes:
    """
    Génère un CV au format Word (.docx) à partir des données JSON.
    Retourne les bytes du fichier.
    """
    document = Document()
    
    # --- Styles basiques ---
    style = document.styles['Normal']
    font = style.font
    font.name = 'Arial'
    font.size = Pt(11)
    
    # --- En-tête (Nom + Titre + Contact) ---
    name = cv_data.get("full_name", "Candidat").upper()
    title = cv_data.get("title", "")
    
    # Nom
    p_name = document.add_paragraph()
    p_name.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_name = p_name.add_run(name)
    run_name.bold = True
    run_name.font.size = Pt(20)
    
    # Titre
    if title:
        p_title = document.add_paragraph()
        p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run_title = p_title.add_run(title)
        run_title.font.size = Pt(14)
        run_title.font.color.rgb = RGBColor(80, 80, 80)
        
    # Contact
    contact_parts = []
    if cv_data.get("email"): contact_parts.append(cv_data["email"])
    if cv_data.get("phone"): contact_parts.append(cv_data["phone"])
    if cv_data.get("location"): contact_parts.append(cv_data["location"])
    if cv_data.get("linkedin"): contact_parts.append(cv_data["linkedin"])
    if cv_data.get("github"): contact_parts.append(cv_data["github"])
    
    if contact_parts:
        p_contact = document.add_paragraph()
        p_contact.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run_contact = p_contact.add_run(" | ".join(contact_parts))
        run_contact.font.size = Pt(10)
        
    document.add_paragraph() # Espace
    
    # --- Résumé ---
    summary = cv_data.get("summary", "")
    if summary:
        p_sum_head = document.add_heading("PROFIL PROFESSIONNEL", level=2)
        p_sum_head.runs[0].font.name = 'Arial'
        document.add_paragraph(summary)
        document.add_paragraph()
        
    # --- Expériences ---
    experiences = cv_data.get("experiences", [])
    if experiences:
        p_exp_head = document.add_heading("EXPÉRIENCES PROFESSIONNELLES", level=2)
        p_exp_head.runs[0].font.name = 'Arial'
        
        for exp in experiences:
            if isinstance(exp, str):
                document.add_paragraph(exp, style='List Bullet')
                continue
                
            p_exp = document.add_paragraph()
            # Titre du poste
            run_title = p_exp.add_run(exp.get("title", "") + " ")
            run_title.bold = True
            
            # Entreprise & Date
            company = exp.get("company", "")
            start = exp.get("start_date", "")
            end = exp.get("end_date", "")
            date_str = ""
            if start or end:
                date_str = f" | {start} - {end}"
            
            p_exp.add_run(f"chez {company}{date_str}")
            
            # Bullets
            for bullet in exp.get("bullets", []):
                p_bullet = document.add_paragraph(bullet, style='List Bullet')
                p_bullet.paragraph_format.left_indent = Inches(0.25)
        document.add_paragraph()
        
    # --- Formations ---
    education = cv_data.get("education", [])
    if education:
        p_edu_head = document.add_heading("FORMATION", level=2)
        p_edu_head.runs[0].font.name = 'Arial'
        
        for edu in education:
            if isinstance(edu, str):
                document.add_paragraph(edu, style='List Bullet')
                continue
                
            p_edu = document.add_paragraph()
            run_deg = p_edu.add_run(edu.get("degree", "") + " ")
            run_deg.bold = True
            
            inst = edu.get("institution", "")
            year = edu.get("year", "")
            if inst:
                run_inst = p_edu.add_run(f"- {inst}")
            if year:
                p_edu.add_run(f" ({year})")
        document.add_paragraph()
        
    # --- Compétences ---
    skills = cv_data.get("skills", {})
    if skills:
        p_skills_head = document.add_heading("COMPÉTENCES", level=2)
        p_skills_head.runs[0].font.name = 'Arial'
        
        if isinstance(skills, dict):
            for category, items in skills.items():
                p_cat = document.add_paragraph()
                run_cat = p_cat.add_run(f"{category} : ")
                run_cat.bold = True
                
                if isinstance(items, list):
                    p_cat.add_run(", ".join(str(i) for i in items))
                else:
                    p_cat.add_run(str(items))
        elif isinstance(skills, list):
             p_skills = document.add_paragraph(", ".join(str(s) for s in skills))
             
        document.add_paragraph()
        
    # --- Langues & Certifications ---
    languages = cv_data.get("languages", [])
    if languages:
        p_lang_head = document.add_heading("LANGUES", level=2)
        p_lang_head.runs[0].font.name = 'Arial'
        
        for lang in languages:
            if isinstance(lang, str):
                p_lang = document.add_paragraph(lang, style='List Bullet')
                p_lang.paragraph_format.left_indent = Inches(0.25)
            elif isinstance(lang, dict):
                l_name = lang.get("language", "")
                l_prof = lang.get("proficiency", "")
                if l_name:
                    p_lang = document.add_paragraph(f"{l_name} - {l_prof}" if l_prof else l_name, style='List Bullet')
                    p_lang.paragraph_format.left_indent = Inches(0.25)
        document.add_paragraph()
                
    certs = cv_data.get("certifications", [])
    if certs:
        p_cert_head = document.add_heading("CERTIFICATIONS", level=2)
        p_cert_head.runs[0].font.name = 'Arial'
        
        for cert in certs:
            if isinstance(cert, str):
                p_cert = document.add_paragraph(cert, style='List Bullet')
                p_cert.paragraph_format.left_indent = Inches(0.25)
            elif isinstance(cert, dict):
                c_name = cert.get("name", "")
                c_iss = cert.get("issuer", "")
                c_year = cert.get("year", "")
                text = c_name
                if c_iss: text += f" ({c_iss})"
                if c_year: text += f" - {c_year}"
                p_cert = document.add_paragraph(text, style='List Bullet')
                p_cert.paragraph_format.left_indent = Inches(0.25)
    
    # Save to memory
    file_stream = io.BytesIO()
    document.save(file_stream)
    file_stream.seek(0)
    
    return file_stream.read()
