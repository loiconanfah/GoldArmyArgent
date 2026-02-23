"""
Service de génération de CV en format PDF optimisé ATS.
Utilise ReportLab Platypus pour une mise en page propre et professionnelle.
"""
import io
import json
from typing import Dict, Any, List

from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor, black, white
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, HRFlowable,
    Table, TableStyle
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib import colors


# ── Palette de couleurs ────────────────────────────────────────────────────
BLUE_DARK   = HexColor("#1F497D")  # Bleu titres sections
BLUE_MED    = HexColor("#2E74B5")  # Bleu texte secondaire
GREY_TEXT   = HexColor("#4A4A4A")  # Texte courant
GREY_LIGHT  = HexColor("#E8E8E8")  # Ligne de séparation
BLACK       = HexColor("#111111")


def _styles():
    """Retourne un dict de styles ReportLab personnalisés."""
    base = getSampleStyleSheet()

    styles = {}

    styles["name"] = ParagraphStyle(
        "name",
        parent=base["Normal"],
        fontName="Helvetica-Bold",
        fontSize=22,
        textColor=BLUE_DARK,
        alignment=TA_CENTER,
        spaceAfter=2,
    )
    styles["title"] = ParagraphStyle(
        "title",
        parent=base["Normal"],
        fontName="Helvetica",
        fontSize=12,
        textColor=BLUE_MED,
        alignment=TA_CENTER,
        spaceAfter=4,
    )
    styles["contact"] = ParagraphStyle(
        "contact",
        parent=base["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        textColor=GREY_TEXT,
        alignment=TA_CENTER,
        spaceAfter=10,
    )
    styles["section_head"] = ParagraphStyle(
        "section_head",
        parent=base["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10,
        textColor=BLUE_DARK,
        spaceBefore=12,
        spaceAfter=2,
    )
    styles["job_title"] = ParagraphStyle(
        "job_title",
        parent=base["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10,
        textColor=BLACK,
        spaceBefore=6,
        spaceAfter=0,
    )
    styles["job_meta"] = ParagraphStyle(
        "job_meta",
        parent=base["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=9,
        textColor=GREY_TEXT,
        spaceBefore=0,
        spaceAfter=2,
    )
    styles["bullet"] = ParagraphStyle(
        "bullet",
        parent=base["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        textColor=GREY_TEXT,
        leftIndent=12,
        spaceBefore=1,
        spaceAfter=1,
        bulletIndent=0,
        bulletFontName="Helvetica",
        bulletFontSize=9.5,
        bulletColor=BLUE_MED,
    )
    styles["body"] = ParagraphStyle(
        "body",
        parent=base["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        textColor=GREY_TEXT,
        spaceBefore=2,
        spaceAfter=2,
    )
    styles["skill_label"] = ParagraphStyle(
        "skill_label",
        parent=base["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9.5,
        textColor=BLACK,
        spaceBefore=2,
        spaceAfter=1,
    )
    return styles


def _section(title: str, styles: dict) -> list:
    """Retourne le titre de section + ligne horizontale."""
    return [
        Paragraph(title.upper(), styles["section_head"]),
        HRFlowable(width="100%", thickness=1.2, color=BLUE_DARK, spaceAfter=4),
    ]


def generate_cv_pdf(cv_data: Dict[str, Any]) -> bytes:
    """
    Génère un fichier PDF ATS-optimisé à partir des données structurées du CV.
    Retourne les bytes du fichier.
    """
    buffer = io.BytesIO()
    S = _styles()
    story = []

    # ── Marges ────────────────────────────────────────────────────────────
    doc = SimpleDocTemplate(
        buffer,
        pagesize=LETTER,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
    )

    # ═══════════════════════════════════════════════════════════════════════
    # EN-TÊTE
    # ═══════════════════════════════════════════════════════════════════════
    name = cv_data.get("full_name", "Candidat")
    title = cv_data.get("title", "")
    story.append(Paragraph(name, S["name"]))
    if title:
        story.append(Paragraph(title, S["title"]))

    contact_parts = []
    for f in ["email", "phone", "location", "linkedin", "github"]:
        v = cv_data.get(f, "")
        if v and v.lower() not in ["", "n/a", "null", "none"]:
            contact_parts.append(v)
    if contact_parts:
        story.append(Paragraph("  |  ".join(contact_parts), S["contact"]))

    story.append(HRFlowable(width="100%", thickness=1.5, color=BLUE_DARK, spaceAfter=6))

    # ═══════════════════════════════════════════════════════════════════════
    # RÉSUMÉ
    # ═══════════════════════════════════════════════════════════════════════
    summary = cv_data.get("summary", "")
    if summary:
        story += _section("Résumé Professionnel", S)
        story.append(Paragraph(summary, S["body"]))
        story.append(Spacer(1, 4))

    # ═══════════════════════════════════════════════════════════════════════
    # EXPÉRIENCES
    # ═══════════════════════════════════════════════════════════════════════
    experiences = cv_data.get("experiences", [])
    if experiences:
        story += _section("Expériences Professionnelles", S)
        for exp in experiences:
            job_line = exp.get("title", "")
            company = exp.get("company", "")
            if company:
                job_line += f"  —  {company}"
            story.append(Paragraph(job_line, S["job_title"]))

            meta_parts = []
            start = exp.get("start_date", "")
            end = exp.get("end_date", "Présent")
            loc = exp.get("location", "")
            if start:
                meta_parts.append(f"{start} – {end}")
            if loc:
                meta_parts.append(loc)
            if meta_parts:
                story.append(Paragraph("  |  ".join(meta_parts), S["job_meta"]))

            for b in exp.get("bullets", []):
                clean = b.lstrip("•").lstrip("- ").strip()
                if clean:
                    story.append(Paragraph(f"• {clean}", S["bullet"]))
            story.append(Spacer(1, 4))

    # ═══════════════════════════════════════════════════════════════════════
    # COMPÉTENCES
    # ═══════════════════════════════════════════════════════════════════════
    skills = cv_data.get("skills", {})
    if skills:
        story += _section("Compétences Techniques", S)
        for cat, items in skills.items():
            if not items:
                continue
            vals = ", ".join(items) if isinstance(items, list) else str(items)
            story.append(Paragraph(f"<b>{cat}:</b>  {vals}", S["body"]))
        story.append(Spacer(1, 4))

    # ═══════════════════════════════════════════════════════════════════════
    # FORMATION
    # ═══════════════════════════════════════════════════════════════════════
    education = cv_data.get("education", [])
    if education:
        story += _section("Formation", S)
        for edu in education:
            degree = edu.get("degree", "")
            story.append(Paragraph(degree, S["job_title"]))
            meta = []
            if edu.get("institution"):
                meta.append(edu["institution"])
            if edu.get("location"):
                meta.append(edu["location"])
            if edu.get("year"):
                meta.append(edu["year"])
            if meta:
                story.append(Paragraph("  |  ".join(meta), S["job_meta"]))
        story.append(Spacer(1, 4))

    # ═══════════════════════════════════════════════════════════════════════
    # CERTIFICATIONS
    # ═══════════════════════════════════════════════════════════════════════
    certs = cv_data.get("certifications", [])
    if certs:
        story += _section("Certifications", S)
        for c in certs:
            if c.strip():
                story.append(Paragraph(f"• {c.strip()}", S["bullet"]))
        story.append(Spacer(1, 4))

    # ═══════════════════════════════════════════════════════════════════════
    # LANGUES
    # ═══════════════════════════════════════════════════════════════════════
    langs = cv_data.get("languages", [])
    if langs:
        story += _section("Langues", S)
        story.append(Paragraph("  |  ".join(langs), S["body"]))

    # ── Compiler ──────────────────────────────────────────────────────────
    doc.build(story)
    buffer.seek(0)
    return buffer.read()
