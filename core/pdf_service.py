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

def generate_cover_letter_pdf(data: Dict[str, Any]) -> bytes:
    """
    Génère un PDF pour une lettre de motivation.
    data: { "name": "...", "email": "...", "letter": "Markdown content..." }
    """
    pdf = CoverLetterPDF()
    pdf.add_page()
    
    # Fonts
    pdf.set_font('helvetica', 'B', 16)
    pdf.cell(0, 10, data.get('full_name', 'Candidat GoldArmy'), ln=True)
    
    pdf.set_font('helvetica', '', 10)
    pdf.cell(0, 5, data.get('email', ''), ln=True)
    pdf.cell(0, 5, data.get('phone', ''), ln=True)
    pdf.ln(10)
    
    # Body
    pdf.set_font('helvetica', '', 11)
    # Basic markdown cleanup for fpdf (since fpdf doesn't support full markdown)
    content = data.get('letter', '').replace('**', '').replace('###', '').replace('##', '').replace('#', '')
    
    pdf.multi_cell(0, 6, content)
    
    return pdf.output()
