"""
ATS-Optimized CV PDF Generator — Clean Single-Column Layout.
This generator creates a clean, linear, ATS-friendly PDF document.
It avoids columns, tables (for content), images, and multi-frame layouts.
All text flows in a perfectly readable order: Name -> Contact -> Summary ->
Experience -> Projects -> Education -> Skills -> Languages -> Certifications.
"""
import io
from typing import Dict, Any, List, Optional

from reportlab.lib.pagesizes import LETTER
from reportlab.lib.colors import HexColor, black, white
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.units import inch
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer,
    HRFlowable, KeepTogether
)
from reportlab.lib import colors as rl_colors

# ─────────────────────────────────────────────────────────────────────────────
# ATS THEMES — Clean color palettes for the premium visible look
# Each theme maintains perfect ATS compatibility (no columns, no tables)
# ─────────────────────────────────────────────────────────────────────────────
ATS_THEMES = {
    "midnight": {
        "name": "Midnight Pro",
        "accent": "#38bdf8",
        "header_bg": "#0f172a",
        "header_text": "#ffffff",
        "text": "#1e293b",
        "section_title": "#0f172a",
        "line": "#38bdf8",
        "font_body": "Helvetica",
        "font_bold": "Helvetica-Bold",
    },
    "emerald": {
        "name": "Emerald Leader",
        "accent": "#34d399",
        "header_bg": "#064e3b",
        "header_text": "#d1fae5",
        "text": "#1e293b",
        "section_title": "#064e3b",
        "line": "#34d399",
        "font_body": "Helvetica",
        "font_bold": "Helvetica-Bold",
    },
    "modern": {
        "name": "Modern Startup",
        "accent": "#a78bfa",
        "header_bg": "#2e1065",
        "header_text": "#ede9fe",
        "text": "#1e293b",
        "section_title": "#2e1065",
        "line": "#a78bfa",
        "font_body": "Helvetica",
        "font_bold": "Helvetica-Bold",
    },
    "minimal": {
        "name": "Executive Minimal",
        "accent": "#1e40af",
        "header_bg": "#f8fafc",
        "header_text": "#0f172a",
        "text": "#1e293b",
        "section_title": "#0f172a",
        "line": "#cbd5e1",
        "font_body": "Times-Roman",
        "font_bold": "Times-Bold",
    },
    "bold": {
        "name": "Creative Bold",
        "accent": "#f43f5e",
        "header_bg": "#18181b",
        "header_text": "#f4f4f5",
        "text": "#18181b",
        "section_title": "#18181b",
        "line": "#f43f5e",
        "font_body": "Helvetica",
        "font_bold": "Helvetica-Bold",
    },
    "banker": {
        "name": "Trustworthy Banker",
        "accent": "#3b82f6",
        "header_bg": "#1e3a5f",
        "header_text": "#ffffff",
        "text": "#1e293b",
        "section_title": "#1e3a5f",
        "line": "#93c5fd",
        "font_body": "Helvetica",
        "font_bold": "Helvetica-Bold",
    },
    "tech": {
        "name": "Tech God Mode",
        "accent": "#00ff7f",
        "header_bg": "#0a0a0a",
        "header_text": "#00ff7f",
        "text": "#1c1c1c",
        "section_title": "#0a0a0a",
        "line": "#00ff7f",
        "font_body": "Courier",
        "font_bold": "Courier-Bold",
    },
    "classic": {
        "name": "Classic Academic",
        "accent": "#7c2d12",
        "header_bg": "#ffffff",
        "header_text": "#1c1917",
        "text": "#1c1917",
        "section_title": "#3b1a0a",
        "line": "#d6b89a",
        "font_body": "Times-Roman",
        "font_bold": "Times-Bold",
    },
    "vibrant": {
        "name": "Vibrant Energy",
        "accent": "#fb923c",
        "header_bg": "#7f1d1d",
        "header_text": "#ffffff",
        "text": "#1c0a0a",
        "section_title": "#7f1d1d",
        "line": "#fca5a5",
        "font_body": "Helvetica",
        "font_bold": "Helvetica-Bold",
    },
    "luxury": {
        "name": "Elegant Luxury",
        "accent": "#d97706",
        "header_bg": "#1c1917",
        "header_text": "#fef3c7",
        "text": "#1c1917",
        "section_title": "#1c1917",
        "line": "#fbbf24",
        "font_body": "Times-Roman",
        "font_bold": "Times-Bold",
    },
}


def _clean(s: str) -> str:
    """Strip whitespace and return empty string for None."""
    return (s or "").strip()


def _fmt(item) -> str:
    """Format a bullet or list item, removing leading bullet chars."""
    if isinstance(item, str):
        return item.strip().lstrip("•-–—").strip()
    return str(item)


def _build_styles(theme: dict) -> dict:
    """Build all ReportLab paragraph styles for this theme."""
    font_body = theme["font_body"]
    font_bold = theme["font_bold"]
    accent    = HexColor(theme["accent"])
    txt       = HexColor(theme["text"])
    sec_title = HexColor(theme["section_title"])

    base = getSampleStyleSheet()

    NAME = ParagraphStyle(
        "ats_name",
        parent=base["Normal"],
        fontName=font_bold,
        fontSize=22,
        leading=27,
        textColor=HexColor(theme["header_text"]),
        spaceAfter=2,
        textTransform="uppercase",
    )
    TITLE = ParagraphStyle(
        "ats_title",
        parent=base["Normal"],
        fontName=font_body,
        fontSize=12,
        leading=16,
        textColor=HexColor(theme["header_text"]),
        spaceAfter=4,
    )
    CONTACT = ParagraphStyle(
        "ats_contact",
        parent=base["Normal"],
        fontName=font_body,
        fontSize=9,
        leading=13,
        textColor=HexColor(theme["header_text"]),
        spaceAfter=0,
    )
    SECTION = ParagraphStyle(
        "ats_section",
        parent=base["Normal"],
        fontName=font_bold,
        fontSize=11,
        leading=14,
        textColor=sec_title,
        spaceBefore=10,
        spaceAfter=4,
        textTransform="uppercase",
        letterSpacing=1.2,
        borderPadding=(0, 0, 4, 0),
    )
    JOB_TITLE = ParagraphStyle(
        "ats_job_title",
        parent=base["Normal"],
        fontName=font_bold,
        fontSize=10,
        leading=14,
        textColor=txt,
        spaceBefore=5,
        spaceAfter=1,
    )
    JOB_META = ParagraphStyle(
        "ats_job_meta",
        parent=base["Normal"],
        fontName=font_body,
        fontSize=9,
        leading=12,
        textColor=HexColor("#64748b"),
        spaceAfter=3,
    )
    BODY = ParagraphStyle(
        "ats_body",
        parent=base["Normal"],
        fontName=font_body,
        fontSize=9.5,
        leading=13.5,
        textColor=txt,
        spaceAfter=3,
    )
    BULLET = ParagraphStyle(
        "ats_bullet",
        parent=base["Normal"],
        fontName=font_body,
        fontSize=9.5,
        leading=13.5,
        textColor=txt,
        spaceAfter=2,
        leftIndent=14,
        firstLineIndent=-10,
    )
    SKILL_LINE = ParagraphStyle(
        "ats_skill_line",
        parent=base["Normal"],
        fontName=font_body,
        fontSize=9.5,
        leading=13,
        textColor=txt,
        spaceAfter=2,
    )
    return {
        "NAME": NAME,
        "TITLE": TITLE,
        "CONTACT": CONTACT,
        "SECTION": SECTION,
        "JOB_TITLE": JOB_TITLE,
        "JOB_META": JOB_META,
        "BODY": BODY,
        "BULLET": BULLET,
        "SKILL_LINE": SKILL_LINE,
    }


def generate_ats_cv_pdf(cv_data: Dict[str, Any], theme_id: str = "midnight") -> bytes:
    """
    Generate a clean, single-column, ATS-optimized CV PDF.
    Text flows linearly: Header -> Contact -> Summary -> Experience ->
    Projects -> Education -> Skills -> Languages -> Certifications.
    No columns, no frames switching — maximally parseable by all ATS software.
    """
    theme = ATS_THEMES.get(theme_id, ATS_THEMES["midnight"])
    styles = _build_styles(theme)

    buffer = io.BytesIO()
    PAGE_W, PAGE_H = LETTER
    MARGIN = 0.65 * inch

    # Colored header band drawn on every page 1
    header_bg = HexColor(theme["header_bg"])
    accent_c  = HexColor(theme["accent"])
    HEADER_HEIGHT = 1.15 * inch  # visual header band height

    # Build contact parts for header
    contact_parts = [
        cv_data.get(f, "") for f in ["email", "phone", "location", "linkedin", "github"]
        if _clean(cv_data.get(f, ""))
    ]

    def on_page_p1(canvas, doc):
        """Draw the colored header band on page 1."""
        canvas.saveState()
        # Header background
        canvas.setFillColor(header_bg)
        canvas.rect(0, PAGE_H - HEADER_HEIGHT, PAGE_W, HEADER_HEIGHT, fill=1, stroke=0)
        # Accent bottom border of header
        canvas.setFillColor(accent_c)
        canvas.rect(0, PAGE_H - HEADER_HEIGHT - 3, PAGE_W, 3, fill=1, stroke=0)
        canvas.restoreState()

    def on_page_p2(canvas, doc):
        """Subtle accent line on page 2+."""
        canvas.saveState()
        canvas.setFillColor(accent_c)
        canvas.rect(0, PAGE_H - 8, PAGE_W, 8, fill=1, stroke=0)
        canvas.restoreState()

    # Single content frame — the full page minus margins
    # We push the top margin down on page 1 to account for the header band
    frame_p1 = Frame(
        MARGIN,
        MARGIN,
        PAGE_W - 2 * MARGIN,
        PAGE_H - 2 * MARGIN,
        leftPadding=0,
        rightPadding=0,
        topPadding=HEADER_HEIGHT,   # push content below the colored header
        bottomPadding=0,
        id="body_p1",
    )
    frame_p2 = Frame(
        MARGIN,
        MARGIN,
        PAGE_W - 2 * MARGIN,
        PAGE_H - 2 * MARGIN,
        leftPadding=0,
        rightPadding=0,
        topPadding=0,
        bottomPadding=0,
        id="body_p2",
    )

    doc = BaseDocTemplate(
        buffer,
        pagesize=LETTER,
        leftMargin=MARGIN,
        rightMargin=MARGIN,
        topMargin=MARGIN,
        bottomMargin=MARGIN,
    )
    doc.addPageTemplates([
        PageTemplate(id="P1", frames=[frame_p1], onPage=on_page_p1),
        PageTemplate(id="P2", frames=[frame_p2], onPage=on_page_p2),
    ])

    story: List = []

    # ── 1. HEADER: Name + Title + Contact ─────────────────────────────────────
    # These sit visually inside the colored band via top padding offset
    story.append(Paragraph(_clean(cv_data.get("full_name", "")).upper(), styles["NAME"]))
    if _clean(cv_data.get("title", "")):
        story.append(Paragraph(_clean(cv_data.get("title", "")), styles["TITLE"]))
    if contact_parts:
        story.append(Paragraph("  |  ".join(contact_parts), styles["CONTACT"]))

    story.append(Spacer(1, 12))

    # ── 2. PROFESSIONAL SUMMARY ───────────────────────────────────────────────
    summary = _clean(cv_data.get("summary", ""))
    if summary:
        story.append(Paragraph("PROFESSIONAL SUMMARY", styles["SECTION"]))
        story.append(HRFlowable(width="100%", thickness=1.2, color=accent_c, spaceBefore=2, spaceAfter=5))
        story.append(Paragraph(summary, styles["BODY"]))
        story.append(Spacer(1, 4))

    # ── 3. WORK EXPERIENCE ────────────────────────────────────────────────────
    experiences = cv_data.get("experiences", [])
    if experiences:
        story.append(Paragraph("WORK EXPERIENCE", styles["SECTION"]))
        story.append(HRFlowable(width="100%", thickness=1.2, color=accent_c, spaceBefore=2, spaceAfter=5))
        for exp in experiences:
            job_title = _clean(exp.get("title", ""))
            company   = _clean(exp.get("company", ""))
            location  = _clean(exp.get("location", ""))
            start_d   = _clean(exp.get("start_date", ""))
            end_d     = _clean(exp.get("end_date", ""))
            bullets   = exp.get("bullets", [])

            header_line = f"<b>{job_title}</b>"
            if company:
                header_line += f"  –  {company}"
            meta_parts = []
            if start_d:
                meta_parts.append(f"{start_d} – {end_d}" if end_d else start_d)
            if location:
                meta_parts.append(location)

            block = [Paragraph(header_line, styles["JOB_TITLE"])]
            if meta_parts:
                block.append(Paragraph("  ·  ".join(meta_parts), styles["JOB_META"]))
            for b in bullets:
                clean_b = _fmt(b)
                if clean_b:
                    block.append(Paragraph(f"\u2022  {clean_b}", styles["BULLET"]))
            block.append(Spacer(1, 4))
            story.append(KeepTogether(block))

    # ── 4. PROJECTS ───────────────────────────────────────────────────────────
    projects = cv_data.get("projects", [])
    if projects:
        story.append(Paragraph("PROJECTS & ACHIEVEMENTS", styles["SECTION"]))
        story.append(HRFlowable(width="100%", thickness=1.2, color=accent_c, spaceBefore=2, spaceAfter=5))
        for proj in projects:
            name = _clean(proj.get("name", ""))
            desc = _clean(proj.get("description", ""))
            bullets = proj.get("bullets", [])
            block = [Paragraph(f"<b>{name}</b>", styles["JOB_TITLE"])]
            if desc:
                block.append(Paragraph(desc, styles["BODY"]))
            for b in bullets:
                clean_b = _fmt(b)
                if clean_b:
                    block.append(Paragraph(f"\u2022  {clean_b}", styles["BULLET"]))
            block.append(Spacer(1, 4))
            story.append(KeepTogether(block))

    # ── 5. EDUCATION ──────────────────────────────────────────────────────────
    education = cv_data.get("education", [])
    if education:
        story.append(Paragraph("EDUCATION", styles["SECTION"]))
        story.append(HRFlowable(width="100%", thickness=1.2, color=accent_c, spaceBefore=2, spaceAfter=5))
        for edu in education:
            degree  = _clean(edu.get("degree", ""))
            school  = _clean(edu.get("institution", ""))
            year    = _clean(edu.get("year", ""))
            loc     = _clean(edu.get("location", ""))
            header  = f"<b>{degree}</b>"
            if school:
                header += f"  –  {school}"
            meta = [p for p in [year, loc] if p]
            block = [Paragraph(header, styles["JOB_TITLE"])]
            if meta:
                block.append(Paragraph("  ·  ".join(meta), styles["JOB_META"]))
            block.append(Spacer(1, 4))
            story.append(KeepTogether(block))

    # ── 6. SKILLS ─────────────────────────────────────────────────────────────
    skills = cv_data.get("skills", {})
    if skills:
        story.append(Paragraph("SKILLS", styles["SECTION"]))
        story.append(HRFlowable(width="100%", thickness=1.2, color=accent_c, spaceBefore=2, spaceAfter=5))
        if isinstance(skills, dict):
            for cat, items in skills.items():
                if items:
                    vals = "  ·  ".join([_fmt(i) for i in items]) if isinstance(items, list) else str(items)
                    story.append(Paragraph(f"<b>{cat.upper()}</b>:  {vals}", styles["SKILL_LINE"]))
        elif isinstance(skills, list):
            story.append(Paragraph("  ·  ".join([_fmt(i) for i in skills]), styles["SKILL_LINE"]))
        story.append(Spacer(1, 4))

    # ── 7. LANGUAGES ──────────────────────────────────────────────────────────
    languages = cv_data.get("languages", [])
    if languages:
        story.append(Paragraph("LANGUAGES", styles["SECTION"]))
        story.append(HRFlowable(width="100%", thickness=1.2, color=accent_c, spaceBefore=2, spaceAfter=5))
        for lang in languages:
            story.append(Paragraph(f"\u2022  {_fmt(lang)}", styles["BULLET"]))
        story.append(Spacer(1, 4))

    # ── 8. CERTIFICATIONS ─────────────────────────────────────────────────────
    certs = cv_data.get("certifications", [])
    if certs:
        story.append(Paragraph("CERTIFICATIONS", styles["SECTION"]))
        story.append(HRFlowable(width="100%", thickness=1.2, color=accent_c, spaceBefore=2, spaceAfter=5))
        for cert in certs:
            story.append(Paragraph(f"\u2022  {_fmt(cert)}", styles["BULLET"]))
        story.append(Spacer(1, 4))

    doc.build(story)
    return buffer.getvalue()
