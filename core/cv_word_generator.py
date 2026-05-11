import io
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.shared import OxmlElement
from docx.oxml.ns import qn
from typing import Dict, Any

def get_theme_color(theme_id: str) -> RGBColor:
    themes = {
        "goldarmy": RGBColor(245, 158, 11),     # Amber
        "minimaliste": RGBColor(15, 23, 42),    # Slate
        "executive": RGBColor(30, 58, 138),     # Blue
        "creatif": RGBColor(16, 185, 129),      # Emerald
        "classique": RGBColor(0, 0, 0),         # Black
        "neon_tech": RGBColor(139, 92, 246),    # Violet
        "scandinave": RGBColor(14, 165, 233),   # Sky
        "timeline": RGBColor(236, 72, 153),     # Pink
    }
    return themes.get(theme_id, themes["goldarmy"])

def get_theme_bg_color(theme_id: str) -> str:
    """Retourne la couleur hexadécimale pâle pour le fond de la sidebar"""
    themes_bg = {
        "goldarmy": "FEF3C7",     # Amber 100
        "executive": "DBEAFE",    # Blue 100
        "creatif": "D1FAE5",      # Emerald 100
        "neon_tech": "EDE9FE",    # Violet 100
        "scandinave": "E0F2FE",   # Sky 100
    }
    return themes_bg.get(theme_id, "F8FAFC") # Default Slate 50

def set_cell_background(cell, hex_color: str):
    """Ajoute une couleur de fond (shading) à une cellule de tableau Word"""
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), hex_color)
    tcPr.append(shd)

def set_heading_style(heading, color: RGBColor):
    for run in heading.runs:
        run.font.name = 'Arial'
        run.font.color.rgb = color

def add_contact_info(container, cv_data: Dict[str, Any], is_horizontal: bool = False):
    contact_parts = []
    if cv_data.get("email"): contact_parts.append(cv_data["email"])
    if cv_data.get("phone"): contact_parts.append(cv_data["phone"])
    if cv_data.get("location"): contact_parts.append(cv_data["location"])
    if cv_data.get("linkedin"): contact_parts.append(cv_data["linkedin"])
    if cv_data.get("github"): contact_parts.append(cv_data["github"])
    
    if contact_parts:
        p = container.add_paragraph()
        if is_horizontal:
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = p.add_run(" | ".join(contact_parts))
        else:
            run = p.add_run("\n".join(contact_parts))
        run.font.size = Pt(10)

def add_skills(container, cv_data: Dict[str, Any], theme_color: RGBColor):
    skills = cv_data.get("skills", {})
    if not skills: return
    
    head = container.add_paragraph("COMPÉTENCES", style='Heading 2')
    set_heading_style(head, theme_color)
    
    if isinstance(skills, dict):
        for category, items in skills.items():
            p = container.add_paragraph()
            run_cat = p.add_run(f"{category} : ")
            run_cat.bold = True
            if isinstance(items, list):
                p.add_run(", ".join(str(i) for i in items))
            else:
                p.add_run(str(items))
    elif isinstance(skills, list):
         container.add_paragraph(", ".join(str(s) for s in skills))

def add_languages(container, cv_data: Dict[str, Any], theme_color: RGBColor):
    languages = cv_data.get("languages", [])
    if not languages: return
    
    head = container.add_paragraph("LANGUES", style='Heading 2')
    set_heading_style(head, theme_color)
    
    for lang in languages:
        if isinstance(lang, str):
            p = container.add_paragraph(lang, style='List Bullet')
        elif isinstance(lang, dict):
            l_name = lang.get("language", "")
            l_prof = lang.get("proficiency", "")
            if l_name:
                p = container.add_paragraph(f"{l_name} - {l_prof}" if l_prof else l_name, style='List Bullet')
        if 'p' in locals():
            p.paragraph_format.left_indent = Inches(0.25)

def add_certifications(container, cv_data: Dict[str, Any], theme_color: RGBColor):
    certs = cv_data.get("certifications", [])
    if not certs: return
    
    head = container.add_paragraph("CERTIFICATIONS", style='Heading 2')
    set_heading_style(head, theme_color)
    
    for cert in certs:
        if isinstance(cert, str):
            p = container.add_paragraph(cert, style='List Bullet')
        elif isinstance(cert, dict):
            c_name = cert.get("name", "")
            c_iss = cert.get("issuer", "")
            c_year = cert.get("year", "")
            text = c_name
            if c_iss: text += f" ({c_iss})"
            if c_year: text += f" - {c_year}"
            p = container.add_paragraph(text, style='List Bullet')
        if 'p' in locals():
            p.paragraph_format.left_indent = Inches(0.25)

def add_summary(container, cv_data: Dict[str, Any], theme_color: RGBColor):
    summary = cv_data.get("summary", "")
    if summary:
        head = container.add_paragraph("PROFIL PROFESSIONNEL", style='Heading 2')
        set_heading_style(head, theme_color)
        container.add_paragraph(summary)

def add_experiences(container, cv_data: Dict[str, Any], theme_color: RGBColor):
    experiences = cv_data.get("experiences", [])
    if not experiences: return
    
    head = container.add_paragraph("EXPÉRIENCES PROFESSIONNELLES", style='Heading 2')
    set_heading_style(head, theme_color)
    
    for exp in experiences:
        if isinstance(exp, str):
            container.add_paragraph(exp, style='List Bullet')
            continue
            
        p = container.add_paragraph()
        run_title = p.add_run(exp.get("title", "") + " ")
        run_title.bold = True
        
        company = exp.get("company", "")
        start = exp.get("start_date", "")
        end = exp.get("end_date", "")
        date_str = f" | {start} - {end}" if start or end else ""
        
        p.add_run(f"chez {company}{date_str}")
        
        for bullet in exp.get("bullets", []):
            pb = container.add_paragraph(bullet, style='List Bullet')
            pb.paragraph_format.left_indent = Inches(0.25)
    container.add_paragraph() # spacer

def add_education(container, cv_data: Dict[str, Any], theme_color: RGBColor):
    education = cv_data.get("education", [])
    if not education: return
    
    head = container.add_paragraph("FORMATION", style='Heading 2')
    set_heading_style(head, theme_color)
    
    for edu in education:
        if isinstance(edu, str):
            container.add_paragraph(edu, style='List Bullet')
            continue
            
        p = container.add_paragraph()
        run_deg = p.add_run(edu.get("degree", "") + " ")
        run_deg.bold = True
        
        inst = edu.get("institution", "")
        year = edu.get("year", "")
        if inst: p.add_run(f"- {inst}")
        if year: p.add_run(f" ({year})")
    container.add_paragraph()

def build_1_column_cv(document: Document, cv_data: Dict[str, Any], theme_color: RGBColor):
    name = cv_data.get("full_name", "Candidat").upper()
    p_name = document.add_paragraph()
    p_name.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_name = p_name.add_run(name)
    run_name.bold = True
    run_name.font.size = Pt(20)
    run_name.font.color.rgb = theme_color
    
    title = cv_data.get("title", "")
    if title:
        p_title = document.add_paragraph()
        p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run_title = p_title.add_run(title)
        run_title.font.size = Pt(14)
        run_title.font.color.rgb = RGBColor(80, 80, 80)
        
    add_contact_info(document, cv_data, is_horizontal=True)
    document.add_paragraph()
    
    add_summary(document, cv_data, theme_color)
    add_experiences(document, cv_data, theme_color)
    add_education(document, cv_data, theme_color)
    add_skills(document, cv_data, theme_color)
    add_languages(document, cv_data, theme_color)
    add_certifications(document, cv_data, theme_color)

def build_2_column_cv(document: Document, cv_data: Dict[str, Any], theme_id: str, theme_color: RGBColor):
    name = cv_data.get("full_name", "Candidat").upper()
    title = cv_data.get("title", "")
    
    # 1. Header with Name & Title
    p_name = document.add_paragraph()
    run_name = p_name.add_run(name)
    run_name.bold = True
    run_name.font.size = Pt(24)
    run_name.font.color.rgb = theme_color
    
    if title:
        p_title = document.add_paragraph()
        run_title = p_title.add_run(title)
        run_title.font.size = Pt(14)
        run_title.font.color.rgb = RGBColor(80, 80, 80)
        
    document.add_paragraph()
    
    # 2. Table for 2-column layout (Sidebar & Main Content)
    table = document.add_table(rows=1, cols=2)
    # Removing table borders is default in normal templates, but let's be sure.
    table.autofit = False
    
    # Set widths (approximate for A4 with 1-inch margins)
    table.columns[0].width = Inches(2.2)
    table.columns[1].width = Inches(4.3)
    
    cell_left = table.cell(0, 0)
    cell_right = table.cell(0, 1)
    
    # Set left cell width explicitly on the cell
    cell_left.width = Inches(2.2)
    cell_right.width = Inches(4.3)
    
    # Apply background color to sidebar
    bg_hex = get_theme_bg_color(theme_id)
    set_cell_background(cell_left, bg_hex)
    
    # Populate Left Cell (Contact, Skills, Languages, Certs)
    # Note: cell_left already has an empty paragraph, we can write to it or add new ones.
    cell_left.paragraphs[0].text = "CONTACT"
    cell_left.paragraphs[0].runs[0].bold = True
    cell_left.paragraphs[0].runs[0].font.color.rgb = theme_color
    
    add_contact_info(cell_left, cv_data, is_horizontal=False)
    cell_left.add_paragraph()
    
    add_skills(cell_left, cv_data, theme_color)
    add_languages(cell_left, cv_data, theme_color)
    add_certifications(cell_left, cv_data, theme_color)
    
    # Populate Right Cell (Summary, Experiences, Education)
    cell_right.paragraphs[0].text = "PROFIL PROFESSIONNEL"
    cell_right.paragraphs[0].runs[0].bold = True
    cell_right.paragraphs[0].runs[0].font.color.rgb = theme_color
    
    summary = cv_data.get("summary", "")
    if summary:
        cell_right.add_paragraph(summary)
        
    cell_right.add_paragraph()
    add_experiences(cell_right, cv_data, theme_color)
    add_education(cell_right, cv_data, theme_color)


def generate_cv_word(cv_data: Dict[str, Any], theme_id: str = "goldarmy") -> bytes:
    """
    Génère un CV au format Word (.docx) à partir des données JSON.
    Applique la couleur et la structure (1 col vs 2 col) du thème sélectionné.
    """
    document = Document()
    theme_color = get_theme_color(theme_id)
    
    # --- Styles basiques ---
    style = document.styles['Normal']
    font = style.font
    font.name = 'Arial'
    font.size = Pt(10)
    
    # Adjust margins to maximize space
    sections = document.sections
    for section in sections:
        section.top_margin = Inches(0.5)
        section.bottom_margin = Inches(0.5)
        section.left_margin = Inches(0.5)
        section.right_margin = Inches(0.5)
        
    # Thèmes avec 2 colonnes
    two_column_themes = ["goldarmy", "executive", "creatif", "neon_tech", "scandinave"]
    
    if theme_id in two_column_themes:
        build_2_column_cv(document, cv_data, theme_id, theme_color)
    else:
        build_1_column_cv(document, cv_data, theme_color)
    
    # Save to memory
    file_stream = io.BytesIO()
    document.save(file_stream)
    file_stream.seek(0)
    
    return file_stream.read()
