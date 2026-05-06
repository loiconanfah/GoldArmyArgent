import os
import io
from fpdf import FPDF
from typing import Dict, Any

class CoverLetterPDF(FPDF):
    def header(self):
        # Header can be added here if needed
        pass

    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def generate_cover_letter_pdf(data: Dict[str, Any], is_premium: bool = False) -> bytes:
    """
    Génère un PDF pour une lettre de motivation.
    """
    pdf = CoverLetterPDF()
    pdf.add_page()
    
    # Ajout du Logo GoldArmy
    try:
        # On tente de trouver le logo dans les chemins communs
        logo_paths = ["frontend/public/logo.png", "public/logo.png", "logo.png"]
        for lp in logo_paths:
            if os.path.exists(lp):
                pdf.image(lp, x=170, y=10, w=25)
                break
    except Exception:
        pass
    
    # En-tête : Info Candidat
    pdf.set_font('helvetica', 'B', 16)
    if is_premium:
        # Version Premium : Info réelles du candidat
        pdf.cell(0, 10, data.get('full_name', 'Candidat'), ln=True)
        pdf.set_font('helvetica', '', 10)
        pdf.cell(0, 5, data.get('email', ''), ln=True)
        pdf.cell(0, 5, data.get('phone', ''), ln=True)
    else:
        # Version Standard : Branding GoldArmy
        pdf.set_text_color(30, 58, 138) # Indigo-900
        pdf.cell(0, 10, "Candidat GoldArmy", ln=True)
        pdf.set_font('helvetica', '', 10)
        pdf.cell(0, 5, "contact@goldarmy.com", ln=True)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 5, "(Document généré par l'IA GoldArmy - Version Standard)", ln=True)
        pdf.set_text_color(0, 0, 0)
    
    pdf.ln(15)
    
    # Corps de la lettre
    pdf.set_font('helvetica', '', 11)
    
    import re
    content = data.get('letter', '')
    # Nettoyage des phrases d'intro de l'IA
    content = re.sub(r'^(Absolument|Voici|Bien sûr|Certainement|Bonjour).*?[\n\r]+', '', content, flags=re.IGNORECASE | re.MULTILINE)
    
    # Nettoyage Markdown de base pour FPDF
    content = content.replace('**', '').replace('###', '').replace('##', '').replace('#', '').strip()
    
    pdf.multi_cell(0, 6, content)
    
    # Signature de marque en bas si non-premium
    if not is_premium:
        pdf.set_y(-30)
        pdf.set_font('helvetica', 'B', 9)
        pdf.set_text_color(232, 93, 62) # Orange GoldArmy
        pdf.cell(0, 10, "Passez à GoldArmy Premium pour supprimer cette signature.", 0, 1, 'C')
        pdf.set_font('helvetica', 'I', 8)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 5, "https://goldarmyai.com", 0, 0, 'C')

    return pdf.output()
