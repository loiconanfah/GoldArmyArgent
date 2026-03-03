"""
Service de génération de CV en format PDF optimisé ATS V2 (Modèle 2 colonnes Premium).
Utilise ReportLab Platypus.
"""
import io
import json
from typing import Dict, Any, List

from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, white
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, HRFlowable, 
    FrameBreak, NextPageTemplate
)

# ── Palette de couleurs (Design 3 - Grey/Orange) ───────────────────────────
SIDEBAR_BG    = HexColor("#374151")  # Slate 700 - Gris foncé
ACCENT_ORANGE = HexColor("#f59e0b")  # Amber 500 - Orange élégant
SIDEBAR_TEXT  = HexColor("#f8fafc")  # Slate 50
MAIN_TEXT     = HexColor("#334155")  # Slate 700
MAIN_TITLE    = HexColor("#0f172a")  # Slate 900
LINE_COLOR    = HexColor("#e2e8f0")  # Slate 200


def _sidebar_styles():
    base = getSampleStyleSheet()
    return {
        "heading": ParagraphStyle(
            "sb_heading", parent=base["Normal"],
            fontName="Helvetica-Bold", fontSize=11, leading=14,
            textColor=white, spaceBefore=15, spaceAfter=4,
            textTransform="uppercase"
        ),
        "label": ParagraphStyle(
            "sb_label", parent=base["Normal"],
            fontName="Helvetica-Bold", fontSize=9.5, leading=12,
            textColor=ACCENT_ORANGE, spaceBefore=6, spaceAfter=1
        ),
        "body": ParagraphStyle(
            "sb_body", parent=base["Normal"],
            fontName="Helvetica", fontSize=9, leading=12,
            textColor=SIDEBAR_TEXT, spaceBefore=1, spaceAfter=1
        ),
        "bullet": ParagraphStyle(
            "sb_bullet", parent=base["Normal"],
            fontName="Helvetica", fontSize=9, leading=12,
            textColor=SIDEBAR_TEXT, leftIndent=12, firstLineIndent=-12,
            spaceBefore=1, spaceAfter=1,
            bulletFontName="Helvetica", bulletFontSize=9, bulletColor=ACCENT_ORANGE
        )
    }

def _main_styles():
    base = getSampleStyleSheet()
    return {
        "name": ParagraphStyle(
            "name", parent=base["Normal"],
            fontName="Helvetica-Bold", fontSize=26, leading=30,
            textColor=ACCENT_ORANGE, spaceBefore=0, spaceAfter=4,
            textTransform="uppercase"
        ),
        "contact": ParagraphStyle(
            "contact", parent=base["Normal"],
            fontName="Helvetica", fontSize=9.5, leading=14,
            textColor=MAIN_TEXT, spaceBefore=4, spaceAfter=15
        ),
        "section_head": ParagraphStyle(
            "section_head", parent=base["Normal"],
            fontName="Helvetica-Bold", fontSize=12, leading=14,
            textColor=MAIN_TITLE, spaceBefore=16, spaceAfter=4,
            textTransform="uppercase"
        ),
        "job_title": ParagraphStyle(
            "job_title", parent=base["Normal"],
            fontName="Helvetica-Bold", fontSize=11, leading=14,
            textColor=MAIN_TITLE, spaceBefore=10, spaceAfter=2
        ),
        "job_meta": ParagraphStyle(
            "job_meta", parent=base["Normal"],
            fontName="Helvetica", fontSize=9.5, leading=12,
            textColor=ACCENT_ORANGE, spaceBefore=1, spaceAfter=4
        ),
        "body": ParagraphStyle(
            "body", parent=base["Normal"],
            fontName="Helvetica", fontSize=10, leading=14,
            textColor=MAIN_TEXT, spaceBefore=2, spaceAfter=2
        ),
        "bullet": ParagraphStyle(
            "bullet", parent=base["Normal"],
            fontName="Helvetica", fontSize=10, leading=14,
            textColor=MAIN_TEXT, leftIndent=15, firstLineIndent=-10,
            spaceBefore=2, spaceAfter=2,
            bulletFontName="Helvetica", bulletFontSize=10, bulletColor=ACCENT_ORANGE
        )
    }


def draw_sidebar_bg(canvas, doc):
    """Dessine le fond gris foncé de la colonne de gauche sur chaque page."""
    canvas.saveState()
    # PAGE_WIDTH = doc.pagesize[0] => LEFT_WIDTH = 34%
    sidebar_w = doc.pagesize[0] * 0.34
    canvas.setFillColor(SIDEBAR_BG)
    canvas.rect(0, 0, sidebar_w, doc.pagesize[1], fill=1, stroke=0)
    canvas.restoreState()


def generate_cv_pdf(cv_data: Dict[str, Any]) -> bytes:
    buffer = io.BytesIO()
    
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

    # Création du document avec 2 templates (Le contenu gauche ne va que sur la page 1)
    doc = BaseDocTemplate(buffer, pagesize=LETTER)
    
    # Template avec 2 colonnes (sert pour la première page qui a le sidebar)
    pt_first = PageTemplate(id='First', frames=[frame_left, frame_right], onPage=draw_sidebar_bg)
    # Dans un CV, la colonne de gauche déborde rarement, mais si ça arrive, on force la suite à droite
    pt_later = PageTemplate(id='Later', frames=[frame_right], onPage=draw_sidebar_bg)
    
    doc.addPageTemplates([pt_first, pt_later])

    SB = _sidebar_styles()
    M = _main_styles()
    story = []

    # =========================================================================
    # COLONNE DE GAUCHE (LEFT FRAME)
    # =========================================================================
    
    # COMPÉTENCES
    skills = cv_data.get("skills", {})
    if skills:
        story.append(Paragraph("COMPÉTENCES", SB["heading"]))
        story.append(HRFlowable(width="100%", thickness=1, color=ACCENT_ORANGE, spaceAfter=8, spaceBefore=4))
        for cat, items in skills.items():
            if items:
                story.append(Paragraph(cat, SB["label"]))
                vals = ", ".join(items) if isinstance(items, list) else str(items)
                story.append(Paragraph(vals, SB["body"]))
    
    # LANGUES
    langs = cv_data.get("languages", [])
    if langs:
        story.append(Paragraph("LANGUES", SB["heading"]))
        story.append(HRFlowable(width="100%", thickness=1, color=ACCENT_ORANGE, spaceAfter=8, spaceBefore=4))
        for lang in langs:
            story.append(Paragraph(f"<bullet>•</bullet>{lang}", SB["bullet"]))

    # CERTIFICATIONS
    certs = cv_data.get("certifications", [])
    if certs:
        story.append(Paragraph("CERTIFICATIONS", SB["heading"]))
        story.append(HRFlowable(width="100%", thickness=1, color=ACCENT_ORANGE, spaceAfter=8, spaceBefore=4))
        for cert in certs:
            story.append(Paragraph(f"<bullet>•</bullet>{cert}", SB["bullet"]))
            
    # Bascule vers la colonne de droite
    story.append(NextPageTemplate('Later'))  # Les futures pages n'auront que la colonne droite
    story.append(FrameBreak())

    # =========================================================================
    # COLONNE DE DROITE (RIGHT FRAME)
    # =========================================================================

    # NOM & CONTACT
    name = cv_data.get("full_name", "Candidat")
    title = cv_data.get("title", "")
    story.append(Paragraph(name, M["name"]))
    if title:
        story.append(Paragraph(f"<font color='#374151'>{title}</font>", M["body"]))
        
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
        story.append(HRFlowable(width="100%", thickness=1, color=LINE_COLOR, spaceAfter=8, spaceBefore=4))
        story.append(Paragraph(summary, M["body"]))

    # PARCOURS PROFESSIONNEL
    experiences = cv_data.get("experiences", [])
    if experiences:
        story.append(Paragraph("PARCOURS PROFESSIONNEL", M["section_head"]))
        story.append(HRFlowable(width="100%", thickness=1, color=LINE_COLOR, spaceAfter=8, spaceBefore=4))
        for exp in experiences:
            # Titre + Entreprise
            job_line = f"{exp.get('title', '')}"
            company = exp.get("company", "")
            if company:
                job_line += f" <font color='#64748b'>—</font> {company}"
            story.append(Paragraph(job_line, M["job_title"]))

            # Date + Lieu
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

            # Bullets
            for b in exp.get("bullets", []):
                clean = b.lstrip("•").lstrip("- ").strip()
                if clean:
                    story.append(Paragraph(f"<bullet>•</bullet>{clean}", M["bullet"]))
            story.append(Spacer(1, 6))

    # FORMATION
    education = cv_data.get("education", [])
    if education:
        story.append(Paragraph("FORMATION", M["section_head"]))
        story.append(HRFlowable(width="100%", thickness=1, color=LINE_COLOR, spaceAfter=8, spaceBefore=4))
        for edu in education:
            degree = edu.get("degree", "")
            story.append(Paragraph(degree, M["job_title"]))
            meta = []
            if edu.get("institution"):
                meta.append(edu["institution"])
            if edu.get("location"):
                meta.append(edu["location"])
            if edu.get("year"):
                meta.append(edu["year"])
            if meta:
                story.append(Paragraph(" | ".join(meta), M["job_meta"]))
        story.append(Spacer(1, 4))

    doc.build(story)
    buffer.seek(0)
    return buffer.read()
