"""
ATS-Optimized CV PDF Generator — Premium Single-Column Layout.
Produces a visually polished, professionally designed CV that is
ALSO perfectly parseable by every ATS system (single linear text flow).

Layout: Full-width colored header band + clean single column body.
NO multi-column frames, NO tables for content, NO image layers.
All text reads top-to-bottom in perfect ATS order.
"""
import io
from typing import Dict, Any, List

from reportlab.lib.pagesizes import LETTER
from reportlab.lib.colors import HexColor, black, white
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.lib.units import inch
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer,
    HRFlowable, KeepTogether, NextPageTemplate
)
from reportlab.lib import colors as rl_colors

# ─────────────────────────────────────────────────────────────────────────────
# COLOR THEMES — 10 premium palettes
# ─────────────────────────────────────────────────────────────────────────────
ATS_THEMES = {
    "midnight": {
        "name": "Midnight Pro",
        "header_bg": "#0f172a", "header_text": "#ffffff", "header_sub": "#94a3b8",
        "accent": "#38bdf8", "body_text": "#1e293b", "section_color": "#0f172a",
        "stripe": "#38bdf8",
        "font_body": "Helvetica", "font_bold": "Helvetica-Bold",
    },
    "emerald": {
        "name": "Emerald Leader",
        "header_bg": "#064e3b", "header_text": "#d1fae5", "header_sub": "#6ee7b7",
        "accent": "#34d399", "body_text": "#1e293b", "section_color": "#064e3b",
        "stripe": "#34d399",
        "font_body": "Helvetica", "font_bold": "Helvetica-Bold",
    },
    "modern": {
        "name": "Modern Startup",
        "header_bg": "#2e1065", "header_text": "#ede9fe", "header_sub": "#c4b5fd",
        "accent": "#a78bfa", "body_text": "#1e293b", "section_color": "#2e1065",
        "stripe": "#a78bfa",
        "font_body": "Helvetica", "font_bold": "Helvetica-Bold",
    },
    "minimal": {
        "name": "Executive Minimal",
        "header_bg": "#f1f5f9", "header_text": "#0f172a", "header_sub": "#475569",
        "accent": "#1e40af", "body_text": "#1e293b", "section_color": "#0f172a",
        "stripe": "#1e40af",
        "font_body": "Times-Roman", "font_bold": "Times-Bold",
    },
    "bold": {
        "name": "Creative Bold",
        "header_bg": "#18181b", "header_text": "#f4f4f5", "header_sub": "#a1a1aa",
        "accent": "#f43f5e", "body_text": "#18181b", "section_color": "#18181b",
        "stripe": "#f43f5e",
        "font_body": "Helvetica", "font_bold": "Helvetica-Bold",
    },
    "banker": {
        "name": "Trustworthy Banker",
        "header_bg": "#1e3a5f", "header_text": "#ffffff", "header_sub": "#93c5fd",
        "accent": "#3b82f6", "body_text": "#1e293b", "section_color": "#1e3a5f",
        "stripe": "#3b82f6",
        "font_body": "Helvetica", "font_bold": "Helvetica-Bold",
    },
    "tech": {
        "name": "Tech God Mode",
        "header_bg": "#0a0a0a", "header_text": "#00ff7f", "header_sub": "#4ade80",
        "accent": "#00ff7f", "body_text": "#1c1c1c", "section_color": "#0a0a0a",
        "stripe": "#00ff7f",
        "font_body": "Courier", "font_bold": "Courier-Bold",
    },
    "classic": {
        "name": "Classic Academic",
        "header_bg": "#ffffff", "header_text": "#1c1917", "header_sub": "#57534e",
        "accent": "#7c2d12", "body_text": "#1c1917", "section_color": "#3b1a0a",
        "stripe": "#7c2d12",
        "font_body": "Times-Roman", "font_bold": "Times-Bold",
    },
    "vibrant": {
        "name": "Vibrant Energy",
        "header_bg": "#7f1d1d", "header_text": "#ffffff", "header_sub": "#fca5a5",
        "accent": "#fb923c", "body_text": "#1c0a0a", "section_color": "#7f1d1d",
        "stripe": "#fb923c",
        "font_body": "Helvetica", "font_bold": "Helvetica-Bold",
    },
    "luxury": {
        "name": "Elegant Luxury",
        "header_bg": "#1c1917", "header_text": "#fef3c7", "header_sub": "#fbbf24",
        "accent": "#d97706", "body_text": "#1c1917", "section_color": "#1c1917",
        "stripe": "#d97706",
        "font_body": "Times-Roman", "font_bold": "Times-Bold",
    },
}


def _clean(s) -> str:
    return (s or "").strip()


def _fmt(item) -> str:
    if isinstance(item, str):
        return item.strip().lstrip("•-–—").strip()
    return str(item)


def _build_styles(theme: dict) -> dict:
    fb = theme["font_body"]
    fbd = theme["font_bold"]
    acc = HexColor(theme["accent"])
    txt = HexColor(theme["body_text"])
    sec = HexColor(theme["section_color"])
    hdr_txt = HexColor(theme["header_text"])
    hdr_sub = HexColor(theme["header_sub"])

    base = getSampleStyleSheet()

    return {
        # ── Header styles (on colored band) ──────────────────────────────────
        "NAME": ParagraphStyle(
            "cv_name", parent=base["Normal"],
            fontName=fbd, fontSize=26, leading=30,
            textColor=hdr_txt, spaceAfter=3, textTransform="uppercase",
        ),
        "TITLE": ParagraphStyle(
            "cv_title", parent=base["Normal"],
            fontName=fb, fontSize=12, leading=16,
            textColor=hdr_sub, spaceAfter=5,
        ),
        "CONTACT_LABEL": ParagraphStyle(
            "cv_contact_label", parent=base["Normal"],
            fontName=fbd, fontSize=8.5, leading=13,
            textColor=acc, spaceAfter=0,
        ),
        "CONTACT": ParagraphStyle(
            "cv_contact", parent=base["Normal"],
            fontName=fb, fontSize=8.5, leading=13,
            textColor=hdr_txt, spaceAfter=2,
        ),
        # ── Body section header ───────────────────────────────────────────────
        "SECTION": ParagraphStyle(
            "cv_section", parent=base["Normal"],
            fontName=fbd, fontSize=10, leading=13,
            textColor=sec, spaceBefore=12, spaceAfter=3,
            textTransform="uppercase", letterSpacing=1.5,
        ),
        # ── Job / Education entry ─────────────────────────────────────────────
        "JOB_TITLE": ParagraphStyle(
            "cv_job_title", parent=base["Normal"],
            fontName=fbd, fontSize=10.5, leading=14,
            textColor=txt, spaceBefore=6, spaceAfter=1,
        ),
        "JOB_META": ParagraphStyle(
            "cv_job_meta", parent=base["Normal"],
            fontName=fb, fontSize=8.5, leading=12,
            textColor=HexColor("#64748b"), spaceAfter=3,
        ),
        # ── Body text & bullets ───────────────────────────────────────────────
        "BODY": ParagraphStyle(
            "cv_body", parent=base["Normal"],
            fontName=fb, fontSize=9.5, leading=14,
            textColor=txt, spaceAfter=3,
        ),
        "BULLET": ParagraphStyle(
            "cv_bullet", parent=base["Normal"],
            fontName=fb, fontSize=9.5, leading=14,
            textColor=txt, spaceAfter=2,
            leftIndent=14, firstLineIndent=-10,
        ),
        "SKILL_CAT": ParagraphStyle(
            "cv_skill_cat", parent=base["Normal"],
            fontName=fbd, fontSize=9.5, leading=13,
            textColor=sec, spaceAfter=1,
        ),
        "SKILL_VAL": ParagraphStyle(
            "cv_skill_val", parent=base["Normal"],
            fontName=fb, fontSize=9.5, leading=13,
            textColor=txt, spaceAfter=4,
        ),
    }


def generate_ats_cv_pdf(cv_data: Dict[str, Any], theme_id: str = "midnight") -> bytes:
    """
    Generate a premium-looking, perfectly ATS-compatible single-column CV PDF.
    
    Structure:
      - Full-width colored header band (name, title, contacts)
      - Left accent stripe running the full page height
      - Clean single-column body with section headers + HR separators
    
    Text flows 100% linearly top-to-bottom -> perfect ATS parsing.
    """
    theme = ATS_THEMES.get(theme_id, ATS_THEMES["midnight"])
    styles = _build_styles(theme)

    buf = io.BytesIO()
    PAGE_W, PAGE_H = LETTER

    # Layout constants
    STRIPE_W     = 4          # accent left stripe width (points)
    LEFT_MARGIN  = 0.65 * inch
    RIGHT_MARGIN = 0.65 * inch
    TOP_MARGIN   = 0.5  * inch
    BOT_MARGIN   = 0.5  * inch
    HEADER_H     = 1.3  * inch   # height of the colored header band

    accent_c    = HexColor(theme["accent"])
    header_bg_c = HexColor(theme["header_bg"])
    stripe_c    = HexColor(theme["stripe"])
    body_txt_c  = HexColor(theme["body_text"])

    # ── Contact line ──────────────────────────────────────────────────────────
    contact_fields = ["email", "phone", "location", "linkedin", "github"]
    contact_parts  = [_clean(cv_data.get(f, "")) for f in contact_fields
                      if _clean(cv_data.get(f, ""))]

    # ── Page callbacks ────────────────────────────────────────────────────────
    def draw_page_p1(canvas, doc):
        canvas.saveState()
        # 1. Colored header band
        canvas.setFillColor(header_bg_c)
        canvas.rect(0, PAGE_H - HEADER_H, PAGE_W, HEADER_H, fill=1, stroke=0)
        # 2. Accent bottom border of header
        canvas.setFillColor(accent_c)
        canvas.rect(0, PAGE_H - HEADER_H - 3, PAGE_W, 3, fill=1, stroke=0)
        # 3. Left accent stripe for the body area
        canvas.setFillColor(stripe_c)
        canvas.rect(0, 0, STRIPE_W, PAGE_H - HEADER_H - 3, fill=1, stroke=0)
        canvas.restoreState()

    def draw_page_p2(canvas, doc):
        canvas.saveState()
        # Thin top accent stripe for continuation pages
        canvas.setFillColor(accent_c)
        canvas.rect(0, PAGE_H - 6, PAGE_W, 6, fill=1, stroke=0)
        # Left accent stripe
        canvas.setFillColor(stripe_c)
        canvas.rect(0, 0, STRIPE_W, PAGE_H - 6, fill=1, stroke=0)
        canvas.restoreState()

    # ── Frames ────────────────────────────────────────────────────────────────
    body_x = LEFT_MARGIN + STRIPE_W + 4   # shift content right of stripe
    body_w = PAGE_W - body_x - RIGHT_MARGIN

    frame_p1 = Frame(
        body_x, BOT_MARGIN, body_w, PAGE_H - BOT_MARGIN - TOP_MARGIN,
        leftPadding=0, rightPadding=0,
        topPadding=HEADER_H + 4,   # push below the colored band
        bottomPadding=0,
        id="body_p1",
    )
    frame_p2 = Frame(
        body_x, BOT_MARGIN, body_w, PAGE_H - BOT_MARGIN - TOP_MARGIN,
        leftPadding=0, rightPadding=0,
        topPadding=10, bottomPadding=0,
        id="body_p2",
    )

    doc = BaseDocTemplate(
        buf, pagesize=LETTER,
        leftMargin=LEFT_MARGIN, rightMargin=RIGHT_MARGIN,
        topMargin=TOP_MARGIN,   bottomMargin=BOT_MARGIN,
    )
    doc.addPageTemplates([
        PageTemplate(id="P1", frames=[frame_p1], onPage=draw_page_p1),
        PageTemplate(id="P2", frames=[frame_p2], onPage=draw_page_p2),
    ])

    story: List = []

    # ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  1. HEADER  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
    name = _clean(cv_data.get("full_name", "")).upper()
    title = _clean(cv_data.get("title", ""))
    story.append(Paragraph(name, styles["NAME"]))
    if title:
        story.append(Paragraph(title, styles["TITLE"]))

    # ── Each contact field on its OWN LINE with label — critical for ATS parsers ──
    email    = _clean(cv_data.get("email", ""))
    phone    = _clean(cv_data.get("phone", ""))
    location = _clean(cv_data.get("location", ""))
    linkedin = _clean(cv_data.get("linkedin", ""))
    github   = _clean(cv_data.get("github", ""))

    if email:
        story.append(Paragraph(f"Email: {email}", styles["CONTACT"]))
    if phone:
        story.append(Paragraph(f"Phone: {phone}", styles["CONTACT"]))
    if location:
        story.append(Paragraph(f"Address: {location}", styles["CONTACT"]))
    if linkedin:
        story.append(Paragraph(f"LinkedIn: {linkedin}", styles["CONTACT"]))
    if github:
        story.append(Paragraph(f"GitHub: {github}", styles["CONTACT"]))

    story.append(Spacer(1, 10))

    # Helper: section separator
    def sec_header(label: str):
        story.append(Paragraph(label, styles["SECTION"]))
        story.append(HRFlowable(
            width="100%", thickness=1.2, color=accent_c, spaceBefore=1, spaceAfter=5
        ))

    # ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  2. SUMMARY  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
    summary = _clean(cv_data.get("summary", ""))
    if summary:
        sec_header("PROFESSIONAL SUMMARY")
        story.append(Paragraph(summary, styles["BODY"]))
        story.append(Spacer(1, 4))

    # ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  3. WORK EXPERIENCE  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
    experiences = cv_data.get("experiences", [])
    if experiences:
        sec_header("WORK EXPERIENCE")
        for exp in experiences:
            job_t  = _clean(exp.get("title", ""))
            co     = _clean(exp.get("company", ""))
            loc    = _clean(exp.get("location", ""))
            start  = _clean(exp.get("start_date", ""))
            end    = _clean(exp.get("end_date", ""))
            bullets = exp.get("bullets", [])

            title_line = f"<b>{job_t}</b>"
            if co:
                title_line += f"  <font color='#64748b'>@ {co}</font>"

            meta = []
            if start:
                meta.append(f"{start} – {end}" if end else start)
            if loc:
                meta.append(loc)

            block = [Paragraph(title_line, styles["JOB_TITLE"])]
            if meta:
                block.append(Paragraph("   ·   ".join(meta), styles["JOB_META"]))
            for b in bullets:
                clean_b = _fmt(b)
                if clean_b:
                    block.append(Paragraph(f"•  {clean_b}", styles["BULLET"]))
            block.append(Spacer(1, 4))
            story.append(KeepTogether(block))

    # ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  4. PROJECTS  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
    projects = cv_data.get("projects", [])
    if projects:
        sec_header("PROJECTS & ACHIEVEMENTS")
        for proj in projects:
            pname   = _clean(proj.get("name", ""))
            pdesc   = _clean(proj.get("description", ""))
            pbullets = proj.get("bullets", [])
            block = [Paragraph(f"<b>{pname}</b>", styles["JOB_TITLE"])]
            if pdesc:
                block.append(Paragraph(pdesc, styles["BODY"]))
            for b in pbullets:
                clean_b = _fmt(b)
                if clean_b:
                    block.append(Paragraph(f"•  {clean_b}", styles["BULLET"]))
            block.append(Spacer(1, 4))
            story.append(KeepTogether(block))

    # ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  5. EDUCATION  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
    education = cv_data.get("education", [])
    if education:
        sec_header("EDUCATION")
        for edu in education:
            deg  = _clean(edu.get("degree", ""))
            sch  = _clean(edu.get("institution", ""))
            yr   = _clean(edu.get("year", ""))
            eloc = _clean(edu.get("location", ""))
            hdr  = f"<b>{deg}</b>"
            if sch:
                hdr += f"  <font color='#64748b'>— {sch}</font>"
            meta = [p for p in [yr, eloc] if p]
            block = [Paragraph(hdr, styles["JOB_TITLE"])]
            if meta:
                block.append(Paragraph("   ·   ".join(meta), styles["JOB_META"]))
            block.append(Spacer(1, 4))
            story.append(KeepTogether(block))

    # ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  6. SKILLS  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
    skills = cv_data.get("skills", {})
    if skills:
        sec_header("TECHNICAL SKILLS")
        if isinstance(skills, dict):
            for cat, items in skills.items():
                if items:
                    vals = "  ·  ".join([_fmt(i) for i in items]) if isinstance(items, list) else str(items)
                    block = [
                        Paragraph(f"<b>{cat.upper()}</b>", styles["SKILL_CAT"]),
                        Paragraph(vals, styles["SKILL_VAL"]),
                    ]
                    story.append(KeepTogether(block))
        elif isinstance(skills, list):
            skill_text = "  ·  ".join([_fmt(i) for i in skills])
            story.append(Paragraph(skill_text, styles["SKILL_VAL"]))
        story.append(Spacer(1, 4))

    # ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  7. LANGUAGES  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
    languages = cv_data.get("languages", [])
    if languages:
        sec_header("LANGUAGES")
        for lang in languages:
            story.append(Paragraph(f"•  {_fmt(lang)}", styles["BULLET"]))
        story.append(Spacer(1, 4))

    # ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  8. CERTIFICATIONS  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
    certs = cv_data.get("certifications", [])
    if certs:
        sec_header("CERTIFICATIONS")
        for cert in certs:
            story.append(Paragraph(f"•  {_fmt(cert)}", styles["BULLET"]))
        story.append(Spacer(1, 4))

    doc.build(story)
    return buf.getvalue()
