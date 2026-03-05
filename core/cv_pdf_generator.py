"""
Service de génération de CV en format PDF optimisé ATS V2 (Modèle 2 colonnes Premium).
Utilise ReportLab Platypus.
"""
import io
import json
from typing import Dict, Any, List

from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, HRFlowable, 
    FrameBreak, NextPageTemplate
)

# ── Système de Thèmes Premium ───────────────────────────
THEMES = {
    "midnight": {
        "name": "Midnight Pro",
        "sidebar_bg": "#1e293b", "accent": "#38bdf8", "text_sidebar": "#f8fafc",
        "text_main": "#334155", "title_main": "#0f172a", "line": "#e2e8f0",
        "font_main": "Helvetica", "font_bold": "Helvetica-Bold"
    },
    "emerald": {
        "name": "Emerald Leader",
        "sidebar_bg": "#064e3b", "accent": "#10b981", "text_sidebar": "#ecfdf5",
        "text_main": "#1f2937", "title_main": "#064e3b", "line": "#d1fae5",
        "font_main": "Helvetica", "font_bold": "Helvetica-Bold"
    },
    "modern": {
        "name": "Modern Startup",
        "sidebar_bg": "#4c1d95", "accent": "#8b5cf6", "text_sidebar": "#f5f3ff",
        "text_main": "#1e293b", "title_main": "#4c1d95", "line": "#ede9fe",
        "font_main": "Helvetica", "font_bold": "Helvetica-Bold"
    },
    "minimal": {
        "name": "Executive Minimal",
        "sidebar_bg": "#f8fafc", "accent": "#0f172a", "text_sidebar": "#334155",
        "text_main": "#334155", "title_main": "#000000", "line": "#f1f5f9",
        "font_main": "Times-Roman", "font_bold": "Times-Bold"
    },
    "bold": {
        "name": "Creative Bold",
        "sidebar_bg": "#000000", "accent": "#f43f5e", "text_sidebar": "#ffffff",
        "text_main": "#000000", "title_main": "#000000", "line": "#ffe4e6",
        "font_main": "Courier", "font_bold": "Courier-Bold"
    },
    "banker": {
        "name": "Trustworthy Banker",
        "sidebar_bg": "#1e3a8a", "accent": "#1e40af", "text_sidebar": "#ffffff",
        "text_main": "#000000", "title_main": "#1e3a8a", "line": "#dbeafe",
        "font_main": "Helvetica", "font_bold": "Helvetica-Bold"
    },
    "tech": {
        "name": "Tech God Mode",
        "sidebar_bg": "#000000", "accent": "#22c55e", "text_sidebar": "#22c55e",
        "text_main": "#1f2937", "title_main": "#000000", "line": "#dcfce7",
        "font_main": "Courier", "font_bold": "Courier-Bold"
    },
    "classic": {
        "name": "Classic Academic",
        "sidebar_bg": "#451a03", "accent": "#92400e", "text_sidebar": "#fff7ed",
        "text_main": "#451a03", "title_main": "#451a03", "line": "#ffedd5",
        "font_main": "Times-Roman", "font_bold": "Times-Bold"
    },
    "vibrant": {
        "name": "Vibrant Energy",
        "sidebar_bg": "#991b1b", "accent": "#ea580c", "text_sidebar": "#fef2f2",
        "text_main": "#450a0a", "title_main": "#991b1b", "line": "#fee2e2",
        "font_main": "Helvetica", "font_bold": "Helvetica-Bold"
    },
    "luxury": {
        "name": "Elegant Luxury",
        "sidebar_bg": "#000000", "accent": "#ca8a04", "text_sidebar": "#fefce8",
        "text_main": "#1c1917", "title_main": "#000000", "line": "#fef9c3",
        "font_main": "Times-Roman", "font_bold": "Times-Bold"
    }
}

def _get_colors(theme_id="midnight"):
    t = THEMES.get(theme_id, THEMES["midnight"])
    return {
        "SIDEBAR_BG": HexColor(t["sidebar_bg"]),
        "ACCENT": HexColor(t["accent"]),
        "SIDEBAR_TEXT": HexColor(t["text_sidebar"]),
        "MAIN_TEXT": HexColor(t["text_main"]),
        "MAIN_TITLE": HexColor(t["title_main"]),
        "LINE": HexColor(t["line"]),
        "FONT": t["font_main"],
        "FONT_BOLD": t["font_bold"]
    }

def _is_dark(color):
    """Calcul du contraste pour choisir entre texte blanc ou noir."""
    # Luminance relative (0.299*R + 0.587*G + 0.114*B)
    return (color.red * 0.299 + color.green * 0.587 + color.blue * 0.114) < 0.5

def _sidebar_styles(c):
    base = getSampleStyleSheet()
    sb_bg = HexColor(THEMES["midnight"]["sidebar_bg"]) # Default if needed
    try:
        sb_bg = HexColor(c["SIDEBAR_BG"].hexval() if hasattr(c["SIDEBAR_BG"], 'hexval') else c["SIDEBAR_BG"])
    except:
        pass
        
    return {
        "heading": ParagraphStyle(
            "sb_heading", parent=base["Normal"],
            fontName=c["FONT_BOLD"], fontSize=11, leading=14,
            textColor=white if _is_dark(c["SIDEBAR_BG"]) else black, 
            spaceBefore=15, spaceAfter=4,
            textTransform="uppercase"
        ),
        "label": ParagraphStyle(
            "sb_label", parent=base["Normal"],
            fontName=c["FONT_BOLD"], fontSize=9.5, leading=12,
            textColor=c["ACCENT"], spaceBefore=6, spaceAfter=1
        ),
        "body": ParagraphStyle(
            "sb_body", parent=base["Normal"],
            fontName=c["FONT"], fontSize=9, leading=12,
            textColor=c["SIDEBAR_TEXT"], spaceBefore=1, spaceAfter=1
        ),
        "bullet": ParagraphStyle(
            "sb_bullet", parent=base["Normal"],
            fontName=c["FONT"], fontSize=9, leading=12,
            textColor=c["SIDEBAR_TEXT"], leftIndent=12, firstLineIndent=-12,
            spaceBefore=1, spaceAfter=1,
            bulletFontName=c["FONT"], bulletFontSize=9, bulletColor=c["ACCENT"]
        )
    }

def _main_styles(c):
    base = getSampleStyleSheet()
    return {
        "name": ParagraphStyle(
            "name", parent=base["Normal"],
            fontName=c["FONT_BOLD"], fontSize=26, leading=30,
            textColor=c["ACCENT"], spaceBefore=0, spaceAfter=4,
            textTransform="uppercase"
        ),
        "contact": ParagraphStyle(
            "contact", parent=base["Normal"],
            fontName=c["FONT"], fontSize=9.5, leading=14,
            textColor=c["MAIN_TEXT"], spaceBefore=4, spaceAfter=15
        ),
        "section_head": ParagraphStyle(
            "section_head", parent=base["Normal"],
            fontName=c["FONT_BOLD"], fontSize=12, leading=14,
            textColor=c["MAIN_TITLE"], spaceBefore=16, spaceAfter=4,
            textTransform="uppercase"
        ),
        "job_title": ParagraphStyle(
            "job_title", parent=base["Normal"],
            fontName=c["FONT_BOLD"], fontSize=11, leading=14,
            textColor=c["MAIN_TITLE"], spaceBefore=10, spaceAfter=2
        ),
        "job_meta": ParagraphStyle(
            "job_meta", parent=base["Normal"],
            fontName=c["FONT"], fontSize=9.5, leading=12,
            textColor=c["ACCENT"], spaceBefore=1, spaceAfter=4
        ),
        "body": ParagraphStyle(
            "body", parent=base["Normal"],
            fontName=c["FONT"], fontSize=10, leading=14,
            textColor=c["MAIN_TEXT"], spaceBefore=2, spaceAfter=2
        ),
        "bullet": ParagraphStyle(
            "bullet", parent=base["Normal"],
            fontName=c["FONT"], fontSize=10, leading=14,
            textColor=c["MAIN_TEXT"], leftIndent=15, firstLineIndent=-10,
            spaceBefore=2, spaceAfter=2,
            bulletFontName=c["FONT"], bulletFontSize=10, bulletColor=c["ACCENT"]
        )
    }


def draw_sidebar_bg(canvas, doc, colors):
    """Dessine le fond de la colonne de gauche sur chaque page."""
    canvas.saveState()
    sidebar_w = doc.pagesize[0] * 0.34
    canvas.setFillColor(colors["SIDEBAR_BG"])
    canvas.rect(0, 0, sidebar_w, doc.pagesize[1], fill=1, stroke=0)
    canvas.restoreState()


def generate_cv_pdf(cv_data: Dict[str, Any], theme_id: str = "midnight") -> bytes:
    buffer = io.BytesIO()
    colors = _get_colors(theme_id)
    
    PAGE_WIDTH, PAGE_HEIGHT = LETTER
    LEFT_WIDTH = PAGE_WIDTH * 0.34
    RIGHT_WIDTH = PAGE_WIDTH - LEFT_WIDTH

    # Configuration des Frames
    frame_left = Frame(
        0, 0, LEFT_WIDTH, PAGE_HEIGHT, id='left',
        leftPadding=inch * 0.4, rightPadding=inch * 0.3, 
        topPadding=inch * 0.5, bottomPadding=inch * 0.5
    )
    frame_right = Frame(
        LEFT_WIDTH, 0, RIGHT_WIDTH, PAGE_HEIGHT, id='right',
        leftPadding=inch * 0.4, rightPadding=inch * 0.5, 
        topPadding=inch * 0.5, bottomPadding=inch * 0.5
    )

    doc = BaseDocTemplate(buffer, pagesize=LETTER)
    
    # Template avec 2 colonnes
    on_page = lambda canv, d: draw_sidebar_bg(canv, d, colors)
    pt_first = PageTemplate(id='First', frames=[frame_left, frame_right], onPage=on_page)
    pt_later = PageTemplate(id='Later', frames=[frame_right], onPage=on_page)
    
    doc.addPageTemplates([pt_first, pt_later])

    SB = _sidebar_styles(colors)
    M = _main_styles(colors)
    story = []

    # =========================================================================
    # COLONNE DE GAUCHE (LEFT FRAME)
    # =========================================================================
    
    # COMPÉTENCES
    skills = cv_data.get("skills", {})
    if skills:
        story.append(Paragraph("COMPÉTENCES", SB["heading"]))
        story.append(HRFlowable(width="100%", thickness=1, color=colors["ACCENT"], spaceAfter=8, spaceBefore=4))
        for cat, items in skills.items():
            if items:
                story.append(Paragraph(cat, SB["label"]))
                vals = ", ".join(items) if isinstance(items, list) else str(items)
                story.append(Paragraph(vals, SB["body"]))
    
    # LANGUES
    langs = cv_data.get("languages", [])
    if langs:
        story.append(Paragraph("LANGUES", SB["heading"]))
        story.append(HRFlowable(width="100%", thickness=1, color=colors["ACCENT"], spaceAfter=8, spaceBefore=4))
        for lang in langs:
            story.append(Paragraph(f"<bullet>•</bullet>{lang}", SB["bullet"]))

    # CERTIFICATIONS
    certs = cv_data.get("certifications", [])
    if certs:
        story.append(Paragraph("CERTIFICATIONS", SB["heading"]))
        story.append(HRFlowable(width="100%", thickness=1, color=colors["ACCENT"], spaceAfter=8, spaceBefore=4))
        for cert in certs:
            story.append(Paragraph(f"<bullet>•</bullet>{cert}", SB["bullet"]))
            
    story.append(NextPageTemplate('Later'))
    story.append(FrameBreak())

    # =========================================================================
    # COLONNE DE DROITE (RIGHT FRAME)
    # =========================================================================

    # NOM & CONTACT
    name = cv_data.get("full_name", "Candidat")
    title = cv_data.get("title", "")
    story.append(Paragraph(name, M["name"]))
    if title:
        story.append(Paragraph(f"<font color='{colors['SIDEBAR_BG']}'>{title}</font>", M["body"]))
        
    story.append(Spacer(1, 10))
    contact_parts = []
    for f in ["email", "phone", "location", "linkedin", "github"]:
        v = cv_data.get(f, "")
        if v and v.lower() not in ["", "n/a", "null", "none"]:
            contact_parts.append(v)
    if contact_parts:
        story.append(Paragraph("  |  ".join(contact_parts), M["contact"]))

    # PROFIL PROFESSIONNEL
    summary = cv_data.get("summary", "")
    if summary:
        story.append(Paragraph("PROFIL PROFESSIONNEL", M["section_head"]))
        story.append(HRFlowable(width="100%", thickness=1, color=colors["LINE"], spaceAfter=8, spaceBefore=4))
        story.append(Paragraph(summary, M["body"]))

    # PARCOURS PROFESSIONNEL
    experiences = cv_data.get("experiences", [])
    if experiences:
        story.append(Paragraph("PARCOURS PROFESSIONNEL", M["section_head"]))
        story.append(HRFlowable(width="100%", thickness=1, color=colors["LINE"], spaceAfter=8, spaceBefore=4))
        for exp in experiences:
            job_line = f"{exp.get('title', '')}"
            company = exp.get("company", "")
            if company:
                job_line += f" <font color='#64748b'>—</font> {company}"
            story.append(Paragraph(job_line, M["job_title"]))

            meta_parts = []
            start = exp.get("start_date", "")
            end = exp.get("end_date", "Présent")
            loc = exp.get("location", "")
            if start:
                meta_parts.append(f"{start} – {end}")
            if loc:
                meta_parts.append(loc)
            if meta_parts:
                story.append(Paragraph(" | ".join(meta_parts), M["job_meta"]))

            for b in exp.get("bullets", []):
                clean = b.lstrip("•").lstrip("- ").strip()
                if clean:
                    story.append(Paragraph(f"<bullet>•</bullet>{clean}", M["bullet"]))
            story.append(Spacer(1, 6))

    # FORMATION
    education = cv_data.get("education", [])
    if education:
        story.append(Paragraph("FORMATION", M["section_head"]))
        story.append(HRFlowable(width="100%", thickness=1, color=colors["LINE"], spaceAfter=8, spaceBefore=4))
        for edu in education:
            degree = edu.get("degree", "")
            story.append(Paragraph(degree, M["job_title"]))
            meta = []
            if edu.get("institution"): meta.append(edu["institution"])
            if edu.get("location"): meta.append(edu["location"])
            if edu.get("year"): meta.append(edu["year"])
            if meta:
                story.append(Paragraph(" | ".join(meta), M["job_meta"]))
        story.append(Spacer(1, 4))

    doc.build(story)
    buffer.seek(0)
    return buffer.read()
