"""
ATS-Optimized CV PDF Generator — 10 Premium Dribbble-Inspired Designs.

Key design principles from modern CV design trends (Dribbble/Freepik):
  • Generous white space and margins (15-20mm)
  • Clear typographic hierarchy: Name (26pt) > Title (13pt) > Section (11pt) > Body (10pt)
  • Section headers: UPPERCASE + bold + HR separator underneath
  • Contact info: Each field on its own labeled line (Email:, Phone:, Address:)
  • Skills: Categorized, not dumped in one list
  • Strong accent colors used sparingly for section markers and dividers

Single-column layout ensures 100% ATS parsing compatibility.
Text flows perfectly: Name → Contact → Summary → Experience → Projects →
Education → Skills → Languages → Certifications
"""
import io, re
from typing import Dict, Any, List

from reportlab.lib.pagesizes import LETTER, A4
from reportlab.lib.colors import HexColor, black, white, Color
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.lib.units import inch, mm
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer,
    HRFlowable, KeepTogether, NextPageTemplate, Table, TableStyle
)
from reportlab.lib import colors as rl_colors


# ─────────────────────────────────────────────────────────────────────────────
# LANGUAGE DETECTION & BILINGUAL SECTION LABELS
# ─────────────────────────────────────────────────────────────────────────────
_FR_MARKERS = [
    r"\bje\b", r"\bles\b", r"\bdes\b", r"\bune\b", r"\bdans\b",
    r"\bavec\b", r"\bpour\b", r"\bsur\b", r"\bdu\b", r"\ben\b",
    r"d'expérience", r"d'expertise", r"logiciel", r"développeur",
    r"\bde\b", r"\bla\b", r"expérience", r"compétences", r"formation",
]


def _detect_lang(cv_data: Dict[str, Any]) -> str:
    """
    Detect whether the CV is in French or English.
    Returns 'fr' or 'en'.
    """
    # 1. Check explicit language field
    lang_field = str(cv_data.get("language", "") or cv_data.get("lang", "")).lower()
    if "fr" in lang_field or "french" in lang_field or "fran" in lang_field:
        return "fr"
    if "en" in lang_field or "english" in lang_field:
        return "en"

    # 2. Scan summary + title for French keywords
    sample = " ".join([
        cv_data.get("summary", "") or "",
        cv_data.get("title",   "") or "",
        " ".join(cv_data.get("languages", [])),
    ]).lower()

    fr_hits = sum(1 for p in _FR_MARKERS if re.search(p, sample))
    return "fr" if fr_hits >= 3 else "en"


SECTION_LABELS = {
    "fr": {
        "summary":   "Profil Professionnel",
        "experience":"Expériences Professionnelles",
        "projects":  "Projets & Réalisations",
        "education": "Formation",
        "skills":    "Compétences Techniques",
        "languages": "Langues",
        "certs":     "Certifications",
        # Contact labels
        "email":     "E-mail",
        "phone":     "Téléphone",
        "address":   "Adresse",
        "linkedin":  "LinkedIn",
        "github":    "GitHub",
    },
    "en": {
        "summary":   "Professional Summary",
        "experience":"Work Experience",
        "projects":  "Projects & Achievements",
        "education": "Education",
        "skills":    "Technical Skills",
        "languages": "Languages",
        "certs":     "Certifications",
        # Contact labels
        "email":     "Email",
        "phone":     "Phone",
        "address":   "Address",
        "linkedin":  "LinkedIn",
        "github":    "GitHub",
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# 10 PREMIUM THEMES
# ─────────────────────────────────────────────────────────────────────────────
ATS_THEMES = {
    # 1. Clean Navy Executive — dark navy header, white body, gold accent
    "midnight": {
        "name": "Navy Executive",
        "header_bg":   "#112240",   # deep navy
        "header_text": "#CCD6F6",   # light lavender-white
        "header_sub":  "#8892B0",   # muted blue-grey
        "accent":      "#64FFDA",   # teal-mint accent
        "body_bg":     "#FFFFFF",
        "body_text":   "#1A1A2E",   # almost black
        "section_title": "#112240", # matches header
        "hr_color":    "#64FFDA",
        "font_name":   "Helvetica-Bold",
        "font_body":   "Helvetica",
        "font_bold":   "Helvetica-Bold",
    },
    # 2. Emerald Success — dark green header, clean white body
    "emerald": {
        "name": "Emerald Executive",
        "header_bg":   "#044D37",
        "header_text": "#ECFDF5",
        "header_sub":  "#6EE7B7",
        "accent":      "#10B981",
        "body_bg":     "#FFFFFF",
        "body_text":   "#1F2937",
        "section_title":"#044D37",
        "hr_color":    "#10B981",
        "font_name":   "Helvetica-Bold",
        "font_body":   "Helvetica",
        "font_bold":   "Helvetica-Bold",
    },
    # 3. Violet Modern — rich purple header, clean body
    "modern": {
        "name": "Violet Modern",
        "header_bg":   "#3B0764",
        "header_text": "#F5F3FF",
        "header_sub":  "#C4B5FD",
        "accent":      "#8B5CF6",
        "body_bg":     "#FFFFFF",
        "body_text":   "#1E1B4B",
        "section_title":"#3B0764",
        "hr_color":    "#8B5CF6",
        "font_name":   "Helvetica-Bold",
        "font_body":   "Helvetica",
        "font_bold":   "Helvetica-Bold",
    },
    # 4. Clean Professional — light grey header, strong blue accent (ATS #1 pick)
    "minimal": {
        "name": "Clean Professional",
        "header_bg":   "#F8FAFC",
        "header_text": "#0F172A",
        "header_sub":  "#475569",
        "accent":      "#1D4ED8",
        "body_bg":     "#FFFFFF",
        "body_text":   "#1E293B",
        "section_title":"#1D4ED8",
        "hr_color":    "#1D4ED8",
        "font_name":   "Times-Bold",
        "font_body":   "Times-Roman",
        "font_bold":   "Times-Bold",
    },
    # 5. Rose Creative — dark charcoal header, rose-red accent
    "bold": {
        "name": "Rose Creative",
        "header_bg":   "#1C1C1E",
        "header_text": "#F9FAFB",
        "header_sub":  "#9CA3AF",
        "accent":      "#E11D48",
        "body_bg":     "#FFFFFF",
        "body_text":   "#111827",
        "section_title":"#1C1C1E",
        "hr_color":    "#E11D48",
        "font_name":   "Helvetica-Bold",
        "font_body":   "Helvetica",
        "font_bold":   "Helvetica-Bold",
    },
    # 6. Corporate Blue — steel blue header, professional look
    "banker": {
        "name": "Corporate Blue",
        "header_bg":   "#1E3A5F",
        "header_text": "#EFF6FF",
        "header_sub":  "#93C5FD",
        "accent":      "#2563EB",
        "body_bg":     "#FFFFFF",
        "body_text":   "#1E293B",
        "section_title":"#1E3A5F",
        "hr_color":    "#2563EB",
        "font_name":   "Helvetica-Bold",
        "font_body":   "Helvetica",
        "font_bold":   "Helvetica-Bold",
    },
    # 7. Tech Terminal — pure black header, neon green accent
    "tech": {
        "name": "Tech Terminal",
        "header_bg":   "#090909",
        "header_text": "#39FF14",
        "header_sub":  "#4ADE80",
        "accent":      "#22C55E",
        "body_bg":     "#FAFAFA",
        "body_text":   "#111827",
        "section_title":"#090909",
        "hr_color":    "#22C55E",
        "font_name":   "Courier-Bold",
        "font_body":   "Courier",
        "font_bold":   "Courier-Bold",
    },
    # 8. Classic Ivory — white header, burgundy/deep red accent, serif
    "classic": {
        "name": "Classic Ivory",
        "header_bg":   "#FFFDF7",
        "header_text": "#1C1917",
        "header_sub":  "#78716C",
        "accent":      "#9B2335",
        "body_bg":     "#FFFFFF",
        "body_text":   "#1C1917",
        "section_title":"#9B2335",
        "hr_color":    "#9B2335",
        "font_name":   "Times-Bold",
        "font_body":   "Times-Roman",
        "font_bold":   "Times-Bold",
    },
    # 9. Sunset Vibrant — deep red header, warm orange accent
    "vibrant": {
        "name": "Sunset Vibrant",
        "header_bg":   "#7F1D1D",
        "header_text": "#FFF7ED",
        "header_sub":  "#FCA5A5",
        "accent":      "#F97316",
        "body_bg":     "#FFFFFF",
        "body_text":   "#1C0A00",
        "section_title":"#7F1D1D",
        "hr_color":    "#F97316",
        "font_name":   "Helvetica-Bold",
        "font_body":   "Helvetica",
        "font_bold":   "Helvetica-Bold",
    },
    # 10. Gold Luxury — near-black header, warm gold accent, serif body
    "luxury": {
        "name": "Gold Luxury",
        "header_bg":   "#1A1208",
        "header_text": "#FEF3C7",
        "header_sub":  "#FCD34D",
        "accent":      "#D97706",
        "body_bg":     "#FFFBF0",
        "body_text":   "#1C1208",
        "section_title":"#92400E",
        "hr_color":    "#D97706",
        "font_name":   "Times-Bold",
        "font_body":   "Times-Roman",
        "font_bold":   "Times-Bold",
    },
}


def _c(s) -> str:
    """Strip and return empty string for None."""
    return (s or "").strip()


def _fmt_bullet(item) -> str:
    """Strip leading bullet chars from a bullet string."""
    if isinstance(item, str):
        return item.strip().lstrip("•·▸▹-–—").strip()
    return str(item)


def _build_styles(theme: dict) -> dict:
    """Build all paragraph styles from the theme config."""
    fb  = theme["font_body"]
    fbd = theme["font_bold"]
    fn  = theme["font_name"]        # name/display font
    acc = HexColor(theme["accent"])
    txt = HexColor(theme["body_text"])
    sec = HexColor(theme["section_title"])
    h_txt = HexColor(theme["header_text"])
    h_sub = HexColor(theme["header_sub"])

    base = getSampleStyleSheet()
    N    = base["Normal"]

    return {
        # ── Header area (sits on top colored band) ────────────────────────────
        "NAME": ParagraphStyle("ats_name", parent=N,
            fontName=fn, fontSize=28, leading=33,
            textColor=h_txt, spaceAfter=4,
            textTransform="uppercase", letterSpacing=2,
        ),
        "JOB_TITLE_HDR": ParagraphStyle("ats_job_hdr", parent=N,
            fontName=fb, fontSize=13, leading=17,
            textColor=h_sub, spaceAfter=8,
            letterSpacing=0.5,
        ),
        "CONTACT_LINE": ParagraphStyle("ats_contact", parent=N,
            fontName=fb, fontSize=9, leading=14,
            textColor=h_txt, spaceAfter=1,
        ),
        # ── Section title ─────────────────────────────────────────────────────
        "SECTION": ParagraphStyle("ats_section", parent=N,
            fontName=fbd, fontSize=10.5, leading=13,
            textColor=sec, spaceBefore=14, spaceAfter=2,
            textTransform="uppercase", letterSpacing=2,
        ),
        # ── Experience entry ──────────────────────────────────────────────────
        "EXP_TITLE": ParagraphStyle("ats_exp_title", parent=N,
            fontName=fbd, fontSize=10.5, leading=14,
            textColor=txt, spaceBefore=7, spaceAfter=1,
        ),
        "EXP_COMPANY": ParagraphStyle("ats_company", parent=N,
            fontName=fb, fontSize=9.5, leading=13,
            textColor=HexColor("#4B5563"), spaceAfter=2,
        ),
        "EXP_META": ParagraphStyle("ats_meta", parent=N,
            fontName=fb, fontSize=8.5, leading=12,
            textColor=HexColor("#6B7280"), spaceAfter=3,
        ),
        # ── Body text & bullet ────────────────────────────────────────────────
        "BODY": ParagraphStyle("ats_body", parent=N,
            fontName=fb, fontSize=10, leading=15,
            textColor=txt, spaceAfter=3,
        ),
        "BULLET": ParagraphStyle("ats_bullet", parent=N,
            fontName=fb, fontSize=9.5, leading=14,
            textColor=txt, spaceAfter=2,
            leftIndent=12, firstLineIndent=-8,
        ),
        # ── Skill category & values ───────────────────────────────────────────
        "SKILL_CAT": ParagraphStyle("ats_skill_cat", parent=N,
            fontName=fbd, fontSize=9.5, leading=13,
            textColor=sec, spaceBefore=4, spaceAfter=1,
        ),
        "SKILL_VAL": ParagraphStyle("ats_skill_val", parent=N,
            fontName=fb, fontSize=9.5, leading=13,
            textColor=txt, spaceAfter=5,
        ),
    }


def generate_ats_cv_pdf(cv_data: Dict[str, Any], theme_id: str = "midnight") -> bytes:
    """
    Generate a premium, single-column ATS-compatible PDF CV.

    Visual design (Dribbble-inspired):
      ┌───────────────────────────────────────────────────────────┐
      │  ██████  HEADER BAND (name, title, labeled contacts)     │
      │  ██████  Background: theme header_bg color               │
      ├─ accent line ─────────────────────────────────────────────┤
      │                                                           │
      │  PROFESSIONAL SUMMARY                                     │
      │  ─────────────────────                                    │
      │  Body text...                                             │
      │                                                           │
      │  WORK EXPERIENCE                                          │
      │  ─────────────────────                                    │
      │  Job Title          Company       Date Range             │
      │  • Bullet with strong action verb + tech + metric         │
      │                                                           │
      │  TECHNICAL SKILLS                                         │
      │  ─────────────────────                                    │
      │  CATEGORY: Item · Item · Item                            │
      └───────────────────────────────────────────────────────────┘

    ATS text order: Name → Email → Phone → Address → Summary →
    Experience → Projects → Education → Skills → Languages → Certs
    """
    theme  = ATS_THEMES.get(theme_id, ATS_THEMES["midnight"])
    styles = _build_styles(theme)

    buf    = io.BytesIO()
    PAGE_W, PAGE_H = LETTER

    # ── Layout measurements ────────────────────────────────────────────────────
    MAR_L    = 0.7  * inch
    MAR_R    = 0.7  * inch
    MAR_T    = 0.5  * inch
    MAR_B    = 0.5  * inch
    HEADER_H = 1.45 * inch     # colored band height on page 1
    ACCENT_BAR = 3             # bottom accent bar of header

    acc_c    = HexColor(theme["accent"])
    hdr_bg_c = HexColor(theme["header_bg"])
    body_bg_c = HexColor(theme["body_bg"])

    # ── Page background + header callbacks ────────────────────────────────────
    def _page1(canvas, doc):
        canvas.saveState()
        # Body background (for ivory/tech themes with non-white body)
        canvas.setFillColor(body_bg_c)
        canvas.rect(0, 0, PAGE_W, PAGE_H - HEADER_H - ACCENT_BAR, fill=1, stroke=0)
        # Header band
        canvas.setFillColor(hdr_bg_c)
        canvas.rect(0, PAGE_H - HEADER_H, PAGE_W, HEADER_H, fill=1, stroke=0)
        # Accent stripe under header
        canvas.setFillColor(acc_c)
        canvas.rect(0, PAGE_H - HEADER_H - ACCENT_BAR, PAGE_W, ACCENT_BAR, fill=1, stroke=0)
        canvas.restoreState()

    def _page2(canvas, doc):
        canvas.saveState()
        canvas.setFillColor(body_bg_c)
        canvas.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
        # Subtle top accent line on continuation pages
        canvas.setFillColor(acc_c)
        canvas.rect(0, PAGE_H - 4, PAGE_W, 4, fill=1, stroke=0)
        canvas.restoreState()

    # ── Frames ────────────────────────────────────────────────────────────────
    body_x = MAR_L
    body_w = PAGE_W - MAR_L - MAR_R

    frame_p1 = Frame(
        body_x, MAR_B, body_w, PAGE_H - MAR_T - MAR_B,
        leftPadding=0, rightPadding=0,
        topPadding=HEADER_H + ACCENT_BAR + 8,
        bottomPadding=0, id="f_p1",
    )
    frame_p2 = Frame(
        body_x, MAR_B, body_w, PAGE_H - MAR_T - MAR_B,
        leftPadding=0, rightPadding=0,
        topPadding=12, bottomPadding=0, id="f_p2",
    )

    doc = BaseDocTemplate(
        buf, pagesize=LETTER,
        leftMargin=MAR_L, rightMargin=MAR_R,
        topMargin=MAR_T, bottomMargin=MAR_B,
    )
    doc.addPageTemplates([
        PageTemplate(id="P1", frames=[frame_p1], onPage=_page1),
        PageTemplate(id="P2", frames=[frame_p2], onPage=_page2),
    ])

    # Detect language and wire section labels
    lang = _detect_lang(cv_data)
    lbl  = SECTION_LABELS[lang]

    story: List = []

    # ═══════════════════════════════════════════════════════════════════
    # 1. HEADER — Name + Job Title + Labeled Contacts (language-aware)
    # Each contact on its own labeled line for maximum ATS detection
    # ═══════════════════════════════════════════════════════════════════
    name  = _c(cv_data.get("full_name", ""))
    title = _c(cv_data.get("title", ""))

    story.append(Paragraph(name.upper(), styles["NAME"]))
    if title:
        story.append(Paragraph(title, styles["JOB_TITLE_HDR"]))

    # Individual labeled contact lines — CRITICAL for ATS detection
    contact_map = [
        (lbl["email"],    cv_data.get("email",    "")),
        (lbl["phone"],    cv_data.get("phone",    "")),
        (lbl["address"],  cv_data.get("location", "")),
        (lbl["linkedin"], cv_data.get("linkedin", "")),
        (lbl["github"],   cv_data.get("github",   "")),
    ]
    for label, val in contact_map:
        if _c(val):
            story.append(Paragraph(f"{label}: {_c(val)}", styles["CONTACT_LINE"]))

    story.append(Spacer(1, 12))

    # ── Section separator helper ───────────────────────────────────────────────
    def add_section(title_text: str):
        story.append(Paragraph(title_text, styles["SECTION"]))
        story.append(HRFlowable(
            width="100%", thickness=1.0, color=acc_c,
            spaceBefore=2, spaceAfter=6,
        ))

    # ════════════════════════════════════════════
    # 2. PROFESSIONAL SUMMARY
    # ════════════════════════════════════════════
    summary = _c(cv_data.get("summary", ""))
    if summary:
        add_section(lbl["summary"])
        story.append(Paragraph(summary, styles["BODY"]))
        story.append(Spacer(1, 4))

    # ════════════════════════════════════════════
    # 3. WORK EXPERIENCE
    # ════════════════════════════════════════════
    experiences = cv_data.get("experiences", [])
    if experiences:
        add_section(lbl["experience"])
        for exp in experiences:
            role    = _c(exp.get("title",      ""))
            company = _c(exp.get("company",    ""))
            loc     = _c(exp.get("location",   ""))
            start   = _c(exp.get("start_date", ""))
            end     = _c(exp.get("end_date",   ""))
            bullets = exp.get("bullets", [])

            date_range = f"{start} – {end}" if start and end else start or end

            block = []
            # Row 1: Job title |  date range right-aligned
            if date_range:
                # Use a two-column mini-table for title + date alignment
                title_para = Paragraph(f"<b>{role}</b>", styles["EXP_TITLE"])
                date_para  = Paragraph(date_range, ParagraphStyle(
                    "exp_date_r", parent=styles["EXP_META"],
                    alignment=TA_RIGHT, spaceBefore=8, spaceAfter=1,
                ))
                tbl = Table([[title_para, date_para]],
                            colWidths=[body_w * 0.68, body_w * 0.32])
                tbl.setStyle(TableStyle([
                    ("VALIGN",      (0, 0), (-1, -1), "BOTTOM"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING",(0, 0), (-1, -1), 0),
                    ("TOPPADDING",  (0, 0), (-1, -1), 0),
                    ("BOTTOMPADDING",(0, 0),(-1, -1), 0),
                ]))
                block.append(tbl)
            else:
                block.append(Paragraph(f"<b>{role}</b>", styles["EXP_TITLE"]))

            # Row 2: Company + location
            co_line = company
            if loc:
                co_line += f"  ·  {loc}" if co_line else loc
            if co_line:
                block.append(Paragraph(co_line, styles["EXP_COMPANY"]))

            # Bullets
            for b in bullets:
                clean_b = _fmt_bullet(b)
                if clean_b:
                    block.append(Paragraph(f"▸  {clean_b}", styles["BULLET"]))
            block.append(Spacer(1, 5))
            story.append(KeepTogether(block))

    # ════════════════════════════════════════════
    # 4. PROJECTS
    # ════════════════════════════════════════════
    projects = cv_data.get("projects", [])
    if projects:
        add_section(lbl["projects"])
        for proj in projects:
            pname    = _c(proj.get("name",        ""))
            pdesc    = _c(proj.get("description", ""))
            pbullets = proj.get("bullets", [])
            block = [Paragraph(f"<b>{pname}</b>", styles["EXP_TITLE"])]
            if pdesc:
                block.append(Paragraph(pdesc, styles["BODY"]))
            for b in pbullets:
                clean_b = _fmt_bullet(b)
                if clean_b:
                    block.append(Paragraph(f"▸  {clean_b}", styles["BULLET"]))
            block.append(Spacer(1, 5))
            story.append(KeepTogether(block))

    # ════════════════════════════════════════════
    # 5. EDUCATION
    # ════════════════════════════════════════════
    education = cv_data.get("education", [])
    if education:
        add_section(lbl["education"])
        for edu in education:
            deg    = _c(edu.get("degree",      ""))
            school = _c(edu.get("institution", ""))
            yr     = _c(edu.get("year",        ""))
            eloc   = _c(edu.get("location",    ""))

            block = []
            if yr:
                deg_para  = Paragraph(f"<b>{deg}</b>", styles["EXP_TITLE"])
                yr_para   = Paragraph(yr, ParagraphStyle(
                    "edu_yr", parent=styles["EXP_META"],
                    alignment=TA_RIGHT, spaceBefore=8, spaceAfter=1,
                ))
                tbl = Table([[deg_para, yr_para]],
                            colWidths=[body_w * 0.72, body_w * 0.28])
                tbl.setStyle(TableStyle([
                    ("VALIGN",       (0, 0), (-1, -1), "BOTTOM"),
                    ("LEFTPADDING",  (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                    ("TOPPADDING",   (0, 0), (-1, -1), 0),
                    ("BOTTOMPADDING",(0, 0), (-1, -1), 0),
                ]))
                block.append(tbl)
            else:
                block.append(Paragraph(f"<b>{deg}</b>", styles["EXP_TITLE"]))

            co_line = school
            if eloc:
                co_line += f"  ·  {eloc}" if co_line else eloc
            if co_line:
                block.append(Paragraph(co_line, styles["EXP_COMPANY"]))
            block.append(Spacer(1, 5))
            story.append(KeepTogether(block))

    # ════════════════════════════════════════════
    # 6. TECHNICAL SKILLS
    # ════════════════════════════════════════════
    skills = cv_data.get("skills", {})
    if skills:
        add_section(lbl["skills"])
        if isinstance(skills, dict):
            for cat, items in skills.items():
                if not items:
                    continue
                vals = "  ·  ".join([_fmt_bullet(i) for i in items]) \
                       if isinstance(items, list) else str(items)
                block = [
                    Paragraph(f"<b>{cat.upper()}</b>", styles["SKILL_CAT"]),
                    Paragraph(vals, styles["SKILL_VAL"]),
                ]
                story.append(KeepTogether(block))
        elif isinstance(skills, list):
            story.append(Paragraph(
                "  ·  ".join([_fmt_bullet(i) for i in skills]),
                styles["SKILL_VAL"]
            ))
        story.append(Spacer(1, 4))

    # ════════════════════════════════════════════
    # 7. LANGUAGES
    # ════════════════════════════════════════════
    languages = cv_data.get("languages", [])
    if languages:
        add_section(lbl["languages"])
        for lang in languages:
            story.append(Paragraph(f"▸  {_fmt_bullet(lang)}", styles["BULLET"]))
        story.append(Spacer(1, 4))

    # ════════════════════════════════════════════
    # 8. CERTIFICATIONS
    # ════════════════════════════════════════════
    certs = cv_data.get("certifications", [])
    if certs:
        add_section(lbl["certs"])
        for cert in certs:
            story.append(Paragraph(f"▸  {_fmt_bullet(cert)}", styles["BULLET"]))
        story.append(Spacer(1, 4))

    doc.build(story)
    return buf.getvalue()
