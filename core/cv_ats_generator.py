"""
ATS-Optimized CV PDF Generator — Premium Designs (Canva/Novoresume/Dribbble Style)

Architecture (fixes all previous visibility issues):
  • ALL text lives in the ReportLab story (Paragraph flowables) → always readable
  • Canvas onPage only draws DECORATIVE elements (color bars, backgrounds) — NO text
  • White or near-white body background → text is ALWAYS dark on light
  • Header area uses a *light tint* background with DARK text (no contrast issue)
  • 10 distinct themes across 3 design families

Design families:
  A) "Clean Corporate" — white bg, name top-left in dark, contact info as row under title,
     section headers are bold uppercase + full-width accent line
  B) "Left-Bar Modern" — thin 5pt left accent stripe, white body, clean typography
  C) "Top-Band Tinted" — subtle light-tinted header area (NOT dark), dark text on it,
     strong visual structure with accent lines

ATS text order: Name → Email → Phone → Address → Summary →
Experience → Projects → Education → Skills → Languages → Certifications
"""
import io, re
from typing import Dict, Any, List

from reportlab.lib.pagesizes import LETTER
from reportlab.lib.colors import HexColor, black, white
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.lib.units import inch
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer,
    HRFlowable, KeepTogether, Table, TableStyle
)

# ─────────────────────────────────────────────────────────────────────────────
# LANGUAGE DETECTION
# ─────────────────────────────────────────────────────────────────────────────
_FR_MARKERS = [
    r"\bje\b", r"\bles\b", r"\bdes\b", r"\bune\b", r"\bdans\b",
    r"\bavec\b", r"\bpour\b", r"\bsur\b", r"\bdu\b", r"\ben\b",
    r"d'expérience", r"d'expertise", r"logiciel", r"développeur",
    r"\bde\b", r"\bla\b", r"expérience", r"compétences", r"formation",
]

def _detect_lang(cv_data: Dict[str, Any]) -> str:
    lang_field = str(cv_data.get("language", "") or cv_data.get("lang", "")).lower()
    if any(x in lang_field for x in ["fr", "french", "fran"]):
        return "fr"
    if any(x in lang_field for x in ["en", "english"]):
        return "en"
    sample = " ".join([
        cv_data.get("summary", "") or "",
        cv_data.get("title",   "") or "",
        " ".join(cv_data.get("languages", [])),
    ]).lower()
    fr_hits = sum(1 for p in _FR_MARKERS if re.search(p, sample))
    return "fr" if fr_hits >= 3 else "en"

SECTION_LABELS = {
    "fr": {
        "summary": "Profil Professionnel", "experience": "Expériences Professionnelles",
        "projects": "Projets & Réalisations", "education": "Formation",
        "skills": "Compétences Techniques", "languages": "Langues",
        "certs": "Certifications",
        "email": "E-mail", "phone": "Téléphone", "address": "Adresse",
        "linkedin": "LinkedIn", "github": "GitHub",
    },
    "en": {
        "summary": "Professional Summary", "experience": "Work Experience",
        "projects": "Projects & Achievements", "education": "Education",
        "skills": "Technical Skills", "languages": "Languages",
        "certs": "Certifications",
        "email": "Email", "phone": "Phone", "address": "Address",
        "linkedin": "LinkedIn", "github": "GitHub",
    },
}

# ─────────────────────────────────────────────────────────────────────────────
# 10 THEMES — 3 design families
# ─────────────────────────────────────────────────────────────────────────────
# Design family key: "A" = Clean Corporate, "B" = Left-Bar, "C" = Tinted Header
THEMES = {
    # ── FAMILY A: Clean Corporate (bright white, dark text, accent on sections) ──
    "midnight": {
        "family": "A",
        "name_color":    "#0F172A",  # near-black navy
        "title_color":   "#1E40AF",  # blue
        "contact_color": "#374151",
        "section_color": "#0F172A",
        "hr_color":      "#1E40AF",
        "body_text":     "#1F2937",
        "meta_color":    "#6B7280",
        "accent":        "#1E40AF",
        "body_bg":       "#FFFFFF",
        "header_tint":   "#F0F4FF",  # very light blue tint for header area
        "left_bar":      None,
        "font_name":     "Helvetica-Bold",
        "font_body":     "Helvetica",
        "font_bold":     "Helvetica-Bold",
    },
    "emerald": {
        "family": "A",
        "name_color":    "#064E3B",
        "title_color":   "#059669",
        "contact_color": "#374151",
        "section_color": "#064E3B",
        "hr_color":      "#059669",
        "body_text":     "#1F2937",
        "meta_color":    "#6B7280",
        "accent":        "#059669",
        "body_bg":       "#FFFFFF",
        "header_tint":   "#ECFDF5",
        "left_bar":      None,
        "font_name":     "Helvetica-Bold",
        "font_body":     "Helvetica",
        "font_bold":     "Helvetica-Bold",
    },
    "modern": {
        "family": "A",
        "name_color":    "#2E1065",
        "title_color":   "#7C3AED",
        "contact_color": "#374151",
        "section_color": "#2E1065",
        "hr_color":      "#7C3AED",
        "body_text":     "#1F2937",
        "meta_color":    "#6B7280",
        "accent":        "#7C3AED",
        "body_bg":       "#FFFFFF",
        "header_tint":   "#F5F3FF",
        "left_bar":      None,
        "font_name":     "Helvetica-Bold",
        "font_body":     "Helvetica",
        "font_bold":     "Helvetica-Bold",
    },
    "classic": {
        "family": "A",
        "name_color":    "#1C1917",
        "title_color":   "#9B2335",
        "contact_color": "#44403C",
        "section_color": "#9B2335",
        "hr_color":      "#9B2335",
        "body_text":     "#1C1917",
        "meta_color":    "#78716C",
        "accent":        "#9B2335",
        "body_bg":       "#FFFFFF",
        "header_tint":   "#FFF7F7",
        "left_bar":      None,
        "font_name":     "Times-Bold",
        "font_body":     "Times-Roman",
        "font_bold":     "Times-Bold",
    },
    # ── FAMILY B: Left-Bar Modern ─────────────────────────────────────────────
    "bold": {
        "family": "B",
        "name_color":    "#111827",
        "title_color":   "#E11D48",
        "contact_color": "#374151",
        "section_color": "#111827",
        "hr_color":      "#E11D48",
        "body_text":     "#1F2937",
        "meta_color":    "#6B7280",
        "accent":        "#E11D48",
        "body_bg":       "#FFFFFF",
        "header_tint":   "#FFFFFF",
        "left_bar":      "#E11D48",
        "font_name":     "Helvetica-Bold",
        "font_body":     "Helvetica",
        "font_bold":     "Helvetica-Bold",
    },
    "banker": {
        "family": "B",
        "name_color":    "#1E3A5F",
        "title_color":   "#2563EB",
        "contact_color": "#374151",
        "section_color": "#1E3A5F",
        "hr_color":      "#2563EB",
        "body_text":     "#1E293B",
        "meta_color":    "#6B7280",
        "accent":        "#2563EB",
        "body_bg":       "#FFFFFF",
        "header_tint":   "#FFFFFF",
        "left_bar":      "#1E3A5F",
        "font_name":     "Helvetica-Bold",
        "font_body":     "Helvetica",
        "font_bold":     "Helvetica-Bold",
    },
    "vibrant": {
        "family": "B",
        "name_color":    "#7F1D1D",
        "title_color":   "#F97316",
        "contact_color": "#374151",
        "section_color": "#7F1D1D",
        "hr_color":      "#F97316",
        "body_text":     "#1C1917",
        "meta_color":    "#78716C",
        "accent":        "#F97316",
        "body_bg":       "#FFFFFF",
        "header_tint":   "#FFFFFF",
        "left_bar":      "#F97316",
        "font_name":     "Helvetica-Bold",
        "font_body":     "Helvetica",
        "font_bold":     "Helvetica-Bold",
    },
    # ── FAMILY C: Tinted Header (light tint bg on header, dark text) ──────────
    "minimal": {
        "family": "C",
        "name_color":    "#0F172A",
        "title_color":   "#475569",
        "contact_color": "#374151",
        "section_color": "#1D4ED8",
        "hr_color":      "#1D4ED8",
        "body_text":     "#1E293B",
        "meta_color":    "#6B7280",
        "accent":        "#1D4ED8",
        "body_bg":       "#FFFFFF",
        "header_tint":   "#F1F5F9",  # slate-100
        "left_bar":      None,
        "font_name":     "Times-Bold",
        "font_body":     "Times-Roman",
        "font_bold":     "Times-Bold",
    },
    "tech": {
        "family": "C",
        "name_color":    "#022C22",
        "title_color":   "#15803D",
        "contact_color": "#374151",
        "section_color": "#15803D",
        "hr_color":      "#15803D",
        "body_text":     "#111827",
        "meta_color":    "#6B7280",
        "accent":        "#15803D",
        "body_bg":       "#FFFFFF",
        "header_tint":   "#F0FDF4",  # green-50
        "left_bar":      None,
        "font_name":     "Courier-Bold",
        "font_body":     "Courier",
        "font_bold":     "Courier-Bold",
    },
    "luxury": {
        "family": "C",
        "name_color":    "#1C1208",
        "title_color":   "#92400E",
        "contact_color": "#44403C",
        "section_color": "#92400E",
        "hr_color":      "#D97706",
        "body_text":     "#1C1208",
        "meta_color":    "#78716C",
        "accent":        "#D97706",
        "body_bg":       "#FFFDF5",
        "header_tint":   "#FEF3C7",  # amber-100
        "left_bar":      None,
        "font_name":     "Times-Bold",
        "font_body":     "Times-Roman",
        "font_bold":     "Times-Bold",
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def _c(s) -> str:
    return (s or "").strip()

def _fmt(item) -> str:
    if isinstance(item, str):
        return item.strip().lstrip("•·▸▹-–—").strip()
    return str(item)

def _styles(t: dict) -> dict:
    fb  = t["font_body"]
    fbd = t["font_bold"]
    fn  = t["font_name"]
    N   = getSampleStyleSheet()["Normal"]
    txt = HexColor(t["body_text"])
    sec = HexColor(t["section_color"])
    met = HexColor(t["meta_color"])
    nmc = HexColor(t["name_color"])
    tic = HexColor(t["title_color"])
    ctc = HexColor(t["contact_color"])

    return {
        # ── Header block ──────────────────────────────────────────────────────
        "NAME": ParagraphStyle("cv_name", parent=N,
            fontName=fn, fontSize=28, leading=32,
            textColor=nmc, spaceAfter=4,
            textTransform="uppercase", letterSpacing=1.5,
        ),
        "JOB_TITLE": ParagraphStyle("cv_job_hdr", parent=N,
            fontName=fbd, fontSize=13, leading=17,
            textColor=tic, spaceAfter=6,
        ),
        "CONTACT_ITEM": ParagraphStyle("cv_contact_item", parent=N,
            fontName=fb, fontSize=9, leading=13,
            textColor=ctc, spaceAfter=1,
        ),
        "CONTACT_INLINE": ParagraphStyle("cv_contact_inline", parent=N,
            fontName=fb, fontSize=9, leading=13,
            textColor=ctc, spaceAfter=0,
        ),
        # ── Section title ─────────────────────────────────────────────────────
        "SECTION": ParagraphStyle("cv_section", parent=N,
            fontName=fbd, fontSize=11, leading=14,
            textColor=sec, spaceBefore=14, spaceAfter=1,
            textTransform="uppercase", letterSpacing=1.8,
        ),
        # ── Experience entry ──────────────────────────────────────────────────
        "EXP_TITLE": ParagraphStyle("cv_exp", parent=N,
            fontName=fbd, fontSize=11, leading=15,
            textColor=txt, spaceBefore=7, spaceAfter=1,
        ),
        "EXP_META": ParagraphStyle("cv_meta", parent=N,
            fontName=fb, fontSize=9, leading=12,
            textColor=met, spaceAfter=3,
        ),
        # ── Body ──────────────────────────────────────────────────────────────
        "BODY": ParagraphStyle("cv_body", parent=N,
            fontName=fb, fontSize=10, leading=15,
            textColor=txt, spaceAfter=3,
        ),
        "BULLET": ParagraphStyle("cv_bullet", parent=N,
            fontName=fb, fontSize=9.5, leading=14,
            textColor=txt, spaceAfter=2,
            leftIndent=14, firstLineIndent=-10,
        ),
        # ── Skills ────────────────────────────────────────────────────────────
        "SKILL_CAT": ParagraphStyle("cv_skill_cat", parent=N,
            fontName=fbd, fontSize=9.5, leading=13,
            textColor=sec, spaceBefore=4, spaceAfter=1,
        ),
        "SKILL_VAL": ParagraphStyle("cv_skill_val", parent=N,
            fontName=fb, fontSize=9.5, leading=13,
            textColor=txt, spaceAfter=4,
        ),
    }


# ─────────────────────────────────────────────────────────────────────────────
# MAIN GENERATOR
# ─────────────────────────────────────────────────────────────────────────────
def generate_ats_cv_pdf(cv_data: Dict[str, Any], theme_id: str = "midnight") -> bytes:
    """
    Generate a premium ATS-compatible PDF CV.

    ALL text flows through the story (ReportLab Paragraph flowables) — never
    drawn on canvas — so every theme is guaranteed readable.

    Canvas onPage only adds lightweight decorative elements:
    Family A: light tinted rectangle behind name/header area
    Family B: thin 5pt colored vertical bar on the left edge
    Family C: same light tinted rectangle + thin bottom accent line
    """
    t      = THEMES.get(theme_id, THEMES["midnight"])
    S      = _styles(t)
    lang   = _detect_lang(cv_data)
    lbl    = SECTION_LABELS[lang]
    family = t["family"]

    buf    = io.BytesIO()
    PAGE_W, PAGE_H = LETTER

    # ── Margins ───────────────────────────────────────────────────────────────
    MAR_L  = 0.7 * inch
    MAR_R  = 0.7 * inch
    MAR_T  = 0.5 * inch
    MAR_B  = 0.55 * inch
    BAR_W  = 5           # left bar width for family B (points)

    acc_c      = HexColor(t["accent"])
    body_bg_c  = HexColor(t["body_bg"])
    tint_c     = HexColor(t["header_tint"])
    bar_c      = HexColor(t["left_bar"]) if t["left_bar"] else None

    # Estimated header height = name(32) + title(17) + contacts(13 * up to 5) + spacers
    HEADER_H = 1.55 * inch    # visual header block height (used for tint rect only)

    # ── Page decorations (NO text on canvas) ─────────────────────────────────
    def _decorate_p1(canvas, doc):
        canvas.saveState()
        # Full page body background
        canvas.setFillColor(body_bg_c)
        canvas.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)

        if family in ("A", "C"):
            # Light tinted header area rectangle
            canvas.setFillColor(tint_c)
            canvas.rect(0, PAGE_H - HEADER_H - MAR_T, PAGE_W, HEADER_H + MAR_T, fill=1, stroke=0)
            if family == "C":
                # Accent bottom border of header tint
                canvas.setFillColor(acc_c)
                canvas.rect(0, PAGE_H - HEADER_H - MAR_T - 3, PAGE_W, 3, fill=1, stroke=0)
        elif family == "B" and bar_c:
            # Thin vertical left bar — full page height
            canvas.setFillColor(bar_c)
            canvas.rect(0, 0, BAR_W, PAGE_H, fill=1, stroke=0)
        canvas.restoreState()

    def _decorate_p2(canvas, doc):
        canvas.saveState()
        canvas.setFillColor(body_bg_c)
        canvas.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
        # Thin accent top bar on continuation pages
        canvas.setFillColor(acc_c)
        canvas.rect(0, PAGE_H - 4, PAGE_W, 4, fill=1, stroke=0)
        if family == "B" and bar_c:
            canvas.setFillColor(bar_c)
            canvas.rect(0, 0, BAR_W, PAGE_H, fill=1, stroke=0)
        canvas.restoreState()

    # ── Frames ────────────────────────────────────────────────────────────────
    content_x = MAR_L + (BAR_W + 4 if family == "B" else 0)
    content_w = PAGE_W - content_x - MAR_R

    frame_p1 = Frame(content_x, MAR_B, content_w, PAGE_H - MAR_T - MAR_B,
                     leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0, id="p1")
    frame_p2 = Frame(content_x, MAR_B, content_w, PAGE_H - MAR_T - MAR_B,
                     leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0, id="p2")

    doc = BaseDocTemplate(buf, pagesize=LETTER,
                          leftMargin=MAR_L, rightMargin=MAR_R,
                          topMargin=MAR_T, bottomMargin=MAR_B)
    doc.addPageTemplates([
        PageTemplate(id="P1", frames=[frame_p1], onPage=_decorate_p1),
        PageTemplate(id="P2", frames=[frame_p2], onPage=_decorate_p2),
    ])

    story: List = []

    # ═══════════════════════════════════════════════════════
    # HEADER — Name, Title, Contacts (all inside story)
    # ═══════════════════════════════════════════════════════
    name        = _c(cv_data.get("full_name", ""))
    job_title   = _c(cv_data.get("title", ""))
    email       = _c(cv_data.get("email",    ""))
    phone       = _c(cv_data.get("phone",    ""))
    location    = _c(cv_data.get("location", ""))
    linkedin    = _c(cv_data.get("linkedin", ""))
    github      = _c(cv_data.get("github",   ""))

    story.append(Paragraph(name.upper(), S["NAME"]))
    if job_title:
        story.append(Paragraph(job_title, S["JOB_TITLE"]))

    # Contact info: compact two-column table for Families A,C; vertical list for B
    contact_items = []
    if email:    contact_items.append(f"{lbl['email']}: {email}")
    if phone:    contact_items.append(f"{lbl['phone']}: {phone}")
    if location: contact_items.append(f"{lbl['address']}: {location}")
    if linkedin: contact_items.append(f"{lbl['linkedin']}: {linkedin}")
    if github:   contact_items.append(f"{lbl['github']}: {github}")

    if contact_items:
        if family in ("A", "C") and len(contact_items) >= 2:
            # 2-column contact table (max 3 items per column)
            left_col  = contact_items[:3]
            right_col = contact_items[3:]
            rows = max(len(left_col), len(right_col))
            data = []
            for i in range(rows):
                l = Paragraph(left_col[i],  S["CONTACT_INLINE"]) if i < len(left_col)  else Paragraph("", S["CONTACT_INLINE"])
                r = Paragraph(right_col[i], S["CONTACT_INLINE"]) if i < len(right_col) else Paragraph("", S["CONTACT_INLINE"])
                data.append([l, r])
            ct = Table(data, colWidths=[content_w * 0.52, content_w * 0.48])
            ct.setStyle(TableStyle([
                ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING",  (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING",   (0, 0), (-1, -1), 1),
                ("BOTTOMPADDING",(0, 0), (-1, -1), 1),
            ]))
            story.append(ct)
        else:
            for item in contact_items:
                story.append(Paragraph(item, S["CONTACT_ITEM"]))

    story.append(Spacer(1, 14))

    # ── Section separator ─────────────────────────────────────────────────────
    def add_section(label: str):
        story.append(Paragraph(label, S["SECTION"]))
        story.append(HRFlowable(width="100%", thickness=1.2, color=acc_c,
                                spaceBefore=2, spaceAfter=7))

    # ─────────────────────────────────────────────────────
    # PROFESSIONAL SUMMARY
    # ─────────────────────────────────────────────────────
    summary = _c(cv_data.get("summary", ""))
    if summary:
        add_section(lbl["summary"])
        story.append(Paragraph(summary, S["BODY"]))
        story.append(Spacer(1, 4))

    # ─────────────────────────────────────────────────────
    # WORK EXPERIENCE
    # ─────────────────────────────────────────────────────
    experiences = cv_data.get("experiences", [])
    if experiences:
        add_section(lbl["experience"])
        for exp in experiences:
            role    = _c(exp.get("title", ""))
            company = _c(exp.get("company", ""))
            loc     = _c(exp.get("location", ""))
            start   = _c(exp.get("start_date", ""))
            end     = _c(exp.get("end_date", ""))
            bullets = exp.get("bullets", [])
            date_str = f"{start} – {end}" if start and end else start or end

            block = []
            # Title + date on same row (table for right-alignment of date)
            t_para = Paragraph(f"<b>{role}</b>", S["EXP_TITLE"])
            d_para = Paragraph(date_str, ParagraphStyle("exp_date", parent=S["EXP_META"],
                                alignment=TA_RIGHT, spaceBefore=8, spaceAfter=1))
            if date_str:
                tbl = Table([[t_para, d_para]], colWidths=[content_w * 0.65, content_w * 0.35])
                tbl.setStyle(TableStyle([
                    ("VALIGN", (0,0),(-1,-1),"BOTTOM"),
                    ("LEFTPADDING", (0,0),(-1,-1),0),
                    ("RIGHTPADDING",(0,0),(-1,-1),0),
                    ("TOPPADDING",  (0,0),(-1,-1),0),
                    ("BOTTOMPADDING",(0,0),(-1,-1),0),
                ]))
                block.append(tbl)
            else:
                block.append(t_para)

            # Company · Location
            co_meta = "  ·  ".join(filter(None, [company, loc]))
            if co_meta:
                block.append(Paragraph(co_meta, S["EXP_META"]))

            for b in bullets:
                txt_b = _fmt(b)
                if txt_b:
                    block.append(Paragraph(f"▸  {txt_b}", S["BULLET"]))
            block.append(Spacer(1, 5))
            story.append(KeepTogether(block))

    # ─────────────────────────────────────────────────────
    # PROJECTS
    # ─────────────────────────────────────────────────────
    projects = cv_data.get("projects", [])
    if projects:
        add_section(lbl["projects"])
        for proj in projects:
            pname = _c(proj.get("name", ""))
            pdesc = _c(proj.get("description", ""))
            block = [Paragraph(f"<b>{pname}</b>", S["EXP_TITLE"])]
            if pdesc:
                block.append(Paragraph(pdesc, S["BODY"]))
            for b in proj.get("bullets", []):
                txt_b = _fmt(b)
                if txt_b:
                    block.append(Paragraph(f"▸  {txt_b}", S["BULLET"]))
            block.append(Spacer(1, 5))
            story.append(KeepTogether(block))

    # ─────────────────────────────────────────────────────
    # EDUCATION
    # ─────────────────────────────────────────────────────
    education = cv_data.get("education", [])
    if education:
        add_section(lbl["education"])
        for edu in education:
            deg   = _c(edu.get("degree", ""))
            school= _c(edu.get("institution", ""))
            yr    = _c(edu.get("year", ""))
            eloc  = _c(edu.get("location", ""))

            d_para = Paragraph(f"<b>{deg}</b>", S["EXP_TITLE"])
            y_para = Paragraph(yr, ParagraphStyle("edu_yr", parent=S["EXP_META"],
                               alignment=TA_RIGHT, spaceBefore=8, spaceAfter=1))

            block = []
            if yr:
                tbl = Table([[d_para, y_para]], colWidths=[content_w * 0.72, content_w * 0.28])
                tbl.setStyle(TableStyle([
                    ("VALIGN",(0,0),(-1,-1),"BOTTOM"),
                    ("LEFTPADDING",(0,0),(-1,-1),0),
                    ("RIGHTPADDING",(0,0),(-1,-1),0),
                    ("TOPPADDING",(0,0),(-1,-1),0),
                    ("BOTTOMPADDING",(0,0),(-1,-1),0),
                ]))
                block.append(tbl)
            else:
                block.append(d_para)

            co_meta = "  ·  ".join(filter(None, [school, eloc]))
            if co_meta:
                block.append(Paragraph(co_meta, S["EXP_META"]))
            block.append(Spacer(1, 5))
            story.append(KeepTogether(block))

    # ─────────────────────────────────────────────────────
    # TECHNICAL SKILLS
    # ─────────────────────────────────────────────────────
    skills = cv_data.get("skills", {})
    if skills:
        add_section(lbl["skills"])
        if isinstance(skills, dict):
            for cat, items in skills.items():
                if not items:
                    continue
                vals = "  ·  ".join([_fmt(i) for i in items]) if isinstance(items, list) else str(items)
                story.append(KeepTogether([
                    Paragraph(f"<b>{cat.upper()}</b>", S["SKILL_CAT"]),
                    Paragraph(vals, S["SKILL_VAL"]),
                ]))
        elif isinstance(skills, list):
            story.append(Paragraph("  ·  ".join([_fmt(i) for i in skills]), S["SKILL_VAL"]))
        story.append(Spacer(1, 4))

    # ─────────────────────────────────────────────────────
    # LANGUAGES
    # ─────────────────────────────────────────────────────
    languages = cv_data.get("languages", [])
    if languages:
        add_section(lbl["languages"])
        for lang_item in languages:
            story.append(Paragraph(f"▸  {_fmt(lang_item)}", S["BULLET"]))
        story.append(Spacer(1, 4))

    # ─────────────────────────────────────────────────────
    # CERTIFICATIONS
    # ─────────────────────────────────────────────────────
    certs = cv_data.get("certifications", [])
    if certs:
        add_section(lbl["certs"])
        for cert in certs:
            story.append(Paragraph(f"▸  {_fmt(cert)}", S["BULLET"]))
        story.append(Spacer(1, 4))

    doc.build(story)
    return buf.getvalue()
