"""
Service de génération de CV en format PDF – Layouts Premium V3.
Chaque modèle est soigneusement organisé avec une hiérarchie visuelle claire.
Maximum 2 pages strictement respecté.
"""
import io
from typing import Dict, Any, List

from reportlab.lib.pagesizes import LETTER
from reportlab.lib.colors import HexColor, white, black, Color
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer,
    HRFlowable, FrameBreak, NextPageTemplate, Table, TableStyle
)
from reportlab.lib import colors as rl_colors

# ─────────────────────────────────────────────────────────────────────────────
# THÈMES
# ─────────────────────────────────────────────────────────────────────────────
THEMES = {
    "midnight": {
        "name": "Midnight Pro", "layout": "modern_sidebar",
        "sidebar_bg": "#0f172a", "accent": "#38bdf8",
        "text_sidebar": "#e2e8f0", "text_main": "#1e293b",
        "title_main": "#0f172a", "line": "#38bdf8",
        "font_main": "Helvetica", "font_bold": "Helvetica-Bold"
    },
    "emerald": {
        "name": "Emerald Leader", "layout": "modern_sidebar",
        "sidebar_bg": "#064e3b", "accent": "#34d399",
        "text_sidebar": "#d1fae5", "text_main": "#1e293b",
        "title_main": "#064e3b", "line": "#34d399",
        "font_main": "Helvetica", "font_bold": "Helvetica-Bold"
    },
    "modern": {
        "name": "Modern Startup", "layout": "reverse_sidebar",
        "sidebar_bg": "#2e1065", "accent": "#a78bfa",
        "text_sidebar": "#ede9fe", "text_main": "#1e293b",
        "title_main": "#2e1065", "line": "#a78bfa",
        "font_main": "Helvetica", "font_bold": "Helvetica-Bold"
    },
    "minimal": {
        "name": "Executive Minimal", "layout": "classic_single",
        "sidebar_bg": "#ffffff", "accent": "#1e40af",
        "text_sidebar": "#1e293b", "text_main": "#1e293b",
        "title_main": "#0f172a", "line": "#cbd5e1",
        "font_main": "Times-Roman", "font_bold": "Times-Bold"
    },
    "bold": {
        "name": "Creative Bold", "layout": "grid_bento",
        "sidebar_bg": "#18181b", "accent": "#f43f5e",
        "text_sidebar": "#f4f4f5", "text_main": "#18181b",
        "title_main": "#18181b", "line": "#f43f5e",
        "font_main": "Helvetica", "font_bold": "Helvetica-Bold"
    },
    "banker": {
        "name": "Trustworthy Banker", "layout": "executive_band",
        "sidebar_bg": "#1e3a5f", "accent": "#3b82f6",
        "text_sidebar": "#ffffff", "text_main": "#1e293b",
        "title_main": "#1e3a5f", "line": "#93c5fd",
        "font_main": "Helvetica", "font_bold": "Helvetica-Bold"
    },
    "tech": {
        "name": "Tech God Mode", "layout": "terminal_code",
        "sidebar_bg": "#0a0a0a", "accent": "#00ff7f",
        "text_sidebar": "#00ff7f", "text_main": "#e2ffe8",
        "title_main": "#00ff7f", "line": "#14532d",
        "font_main": "Courier", "font_bold": "Courier-Bold"
    },
    "classic": {
        "name": "Classic Academic", "layout": "centered_minimal",
        "sidebar_bg": "#ffffff", "accent": "#7c2d12",
        "text_sidebar": "#3b1a0a", "text_main": "#1c1917",
        "title_main": "#3b1a0a", "line": "#d6b89a",
        "font_main": "Times-Roman", "font_bold": "Times-Bold"
    },
    "vibrant": {
        "name": "Vibrant Energy", "layout": "split_equal",
        "sidebar_bg": "#7f1d1d", "accent": "#fb923c",
        "text_sidebar": "#ffffff", "text_main": "#1c0a0a",
        "title_main": "#7f1d1d", "line": "#fca5a5",
        "font_main": "Helvetica", "font_bold": "Helvetica-Bold"
    },
    "luxury": {
        "name": "Elegant Luxury", "layout": "compact_tight",
        "sidebar_bg": "#1c1917", "accent": "#d97706",
        "text_sidebar": "#fef3c7", "text_main": "#1c1917",
        "title_main": "#1c1917", "line": "#fbbf24",
        "font_main": "Times-Roman", "font_bold": "Times-Bold"
    }
}

# ─────────────────────────────────────────────────────────────────────────────
# UTILITAIRES COULEURS
# ─────────────────────────────────────────────────────────────────────────────
def _get_colors(theme_id="midnight"):
    t = THEMES.get(theme_id, THEMES["midnight"])
    return {k: HexColor(v) if isinstance(v, str) and v.startswith("#") else v
            for k, v in {
                "SIDEBAR_BG":   t["sidebar_bg"],
                "ACCENT":       t["accent"],
                "SIDEBAR_TEXT": t["text_sidebar"],
                "MAIN_TEXT":    t["text_main"],
                "MAIN_TITLE":   t["title_main"],
                "LINE":         t["line"],
                "FONT":         t["font_main"],
                "FONT_BOLD":    t["font_bold"],
            }.items()}

def _lum(color: HexColor) -> float:
    def f(v):
        v = v / 255.0
        return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
    return 0.2126*f(int(color.red*255)) + 0.7152*f(int(color.green*255)) + 0.0722*f(int(color.blue*255))

def _on(bg: HexColor) -> HexColor:
    """Retourne blanc ou noir selon le fond pour un contraste optimal."""
    return white if _lum(bg) < 0.25 else black

# ─────────────────────────────────────────────────────────────────────────────
# STYLES TYPOGRAPHIQUES
# ─────────────────────────────────────────────────────────────────────────────
def _get_styles(c):
    base = getSampleStyleSheet()
    LEAD = 1.3   # leading multiplier — compact but readable

    # ── Sidebar styles ──
    SB = {
        "name": ParagraphStyle(
            "sb_name", parent=base["Normal"],
            fontName=c["FONT_BOLD"], fontSize=22, leading=26,
            textColor=_on(c["SIDEBAR_BG"]), spaceBefore=0, spaceAfter=4,
            textTransform="uppercase"
        ),
        "subtitle": ParagraphStyle(
            "sb_sub", parent=base["Normal"],
            fontName=c["FONT"], fontSize=11, leading=15,
            textColor=c["ACCENT"], spaceBefore=0, spaceAfter=6
        ),
        "contact_label": ParagraphStyle(
            "sb_cl", parent=base["Normal"],
            fontName=c["FONT_BOLD"], fontSize=8, leading=10,
            textColor=c["ACCENT"], spaceBefore=2, spaceAfter=0,
            textTransform="uppercase"
        ),
        "contact_value": ParagraphStyle(
            "sb_cv", parent=base["Normal"],
            fontName=c["FONT"], fontSize=8.5, leading=11,
            textColor=_on(c["SIDEBAR_BG"]), spaceBefore=0, spaceAfter=4
        ),
        "section_head": ParagraphStyle(
            "sb_sh", parent=base["Normal"],
            fontName=c["FONT_BOLD"], fontSize=9, leading=12,
            textColor=c["ACCENT"], spaceBefore=14, spaceAfter=5,
            textTransform="uppercase", letterSpacing=1.5
        ),
        "body": ParagraphStyle(
            "sb_body", parent=base["Normal"],
            fontName=c["FONT"], fontSize=8.5, leading=8.5*LEAD,
            textColor=_on(c["SIDEBAR_BG"]), spaceAfter=2
        ),
        "bullet": ParagraphStyle(
            "sb_bul", parent=base["Normal"],
            fontName=c["FONT"], fontSize=8.5, leading=8.5*LEAD,
            textColor=_on(c["SIDEBAR_BG"]),
            leftIndent=10, firstLineIndent=-10,
            spaceAfter=3
        ),
    }

    # ── Main column styles ──
    M = {
        "name": ParagraphStyle(
            "m_name", parent=base["Normal"],
            fontName=c["FONT_BOLD"], fontSize=30, leading=34,
            textColor=c["MAIN_TITLE"], spaceBefore=0, spaceAfter=3,
            textTransform="uppercase"
        ),
        "subtitle": ParagraphStyle(
            "m_sub", parent=base["Normal"],
            fontName=c["FONT"], fontSize=13, leading=17,
            textColor=c["ACCENT"], spaceBefore=0, spaceAfter=5
        ),
        "contact": ParagraphStyle(
            "m_contact", parent=base["Normal"],
            fontName=c["FONT"], fontSize=8.5, leading=13,
            textColor=HexColor("#64748b"), spaceAfter=8
        ),
        "section_head": ParagraphStyle(
            "m_sh", parent=base["Normal"],
            fontName=c["FONT_BOLD"], fontSize=10, leading=14,
            textColor=_on(c["MAIN_TITLE"]),
            backColor=c["MAIN_TITLE"],
            spaceBefore=8, spaceAfter=6,
            textTransform="uppercase", letterSpacing=1.5,
            leftIndent=-6, rightIndent=-6,
            borderPadding=(3, 6, 3, 6)
        ),
        "job_title": ParagraphStyle(
            "m_jt", parent=base["Normal"],
            fontName=c["FONT_BOLD"], fontSize=10.5, leading=14,
            textColor=c["MAIN_TITLE"], spaceBefore=4, spaceAfter=1
        ),
        "job_meta": ParagraphStyle(
            "m_jm", parent=base["Normal"],
            fontName=c["FONT"], fontSize=8.5, leading=12,
            textColor=c["ACCENT"], spaceAfter=4
        ),
        "body": ParagraphStyle(
            "m_body", parent=base["Normal"],
            fontName=c["FONT"], fontSize=9.5, leading=9.5*LEAD,
            textColor=c["MAIN_TEXT"], spaceBefore=2, spaceAfter=2
        ),
        "bullet": ParagraphStyle(
            "m_bul", parent=base["Normal"],
            fontName=c["FONT"], fontSize=9.5, leading=9.5*LEAD,
            textColor=c["MAIN_TEXT"],
            leftIndent=13, firstLineIndent=-10,
            spaceBefore=2, spaceAfter=2
        ),
        "skill_cat": ParagraphStyle(
            "m_scat", parent=base["Normal"],
            fontName=c["FONT_BOLD"], fontSize=8.5, leading=12,
            textColor=c["ACCENT"], spaceBefore=3, spaceAfter=1,
            textTransform="uppercase"
        ),
        "skill_val": ParagraphStyle(
            "m_sval", parent=base["Normal"],
            fontName=c["FONT"], fontSize=9, leading=11,
            textColor=c["MAIN_TEXT"], spaceBefore=0, spaceAfter=3
        ),
    }
    return {"SB": SB, "M": M}

# ─────────────────────────────────────────────────────────────────────────────
# HELPERS DE FORMATAGE
# ─────────────────────────────────────────────────────────────────────────────
def _fmt(item) -> str:
    if isinstance(item, dict):
        if "language" in item:
            lang = item.get("language", "")
            prof = item.get("proficiency", "") or item.get("level", "")
            return f"<b>{lang}</b>" + (f" — {prof}" if prof else "")
        if "name" in item:
            name   = item.get("name", "")
            issuer = item.get("issuer", "") or item.get("organization", "")
            year   = item.get("year", "") or item.get("date", "")
            r = f"<b>{name}</b>"
            if issuer: r += f" · {issuer}"
            if year:   r += f" ({year})"
            return r
    return str(item)

def _dot_sep(*parts):
    return "  ·  ".join(p for p in parts if p)

def _clean(v): return (v or "").strip().lower() not in ["", "n/a", "null", "none"]

# ─────────────────────────────────────────────────────────────────────────────
# BLOCS DE CONTENU — SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
def _sidebar_header(cv_data, story, SB, c):
    """Nom + titre + coordonnées pour la sidebar."""
    story.append(Paragraph(cv_data.get("full_name", "").upper(), SB["name"]))
    if cv_data.get("title"):
        story.append(Paragraph(cv_data["title"], SB["subtitle"]))
    story.append(HRFlowable(width="100%", thickness=1, color=c["ACCENT"],
                            spaceBefore=4, spaceAfter=8))
    # Coordonnées
    for label, key in [("Email", "email"), ("Tél.", "phone"),
                       ("Ville", "location"), ("LinkedIn", "linkedin"),
                       ("GitHub", "github")]:
        v = cv_data.get(key, "")
        if _clean(v):
            story.append(Paragraph(label.upper(), SB["contact_label"]))
            story.append(Paragraph(v, SB["contact_value"]))

def _sidebar_skills(cv_data, story, SB, c):
    """Compétences dans la sidebar."""
    skills = cv_data.get("skills", {})
    if not skills:
        return
    story.append(Paragraph("COMPÉTENCES", SB["section_head"]))
    story.append(HRFlowable(width="100%", thickness=0.6, color=c["ACCENT"],
                            spaceBefore=2, spaceAfter=5))
    for cat, items in skills.items():
        story.append(Paragraph(cat.upper(), SB["contact_label"]))
        vals = "  ·  ".join(items) if isinstance(items, list) else str(items)
        story.append(Paragraph(vals, SB["body"]))
        story.append(Spacer(1, 3))

def _sidebar_languages(cv_data, story, SB, c):
    langs = cv_data.get("languages", [])
    if not langs:
        return
    story.append(Paragraph("LANGUES", SB["section_head"]))
    story.append(HRFlowable(width="100%", thickness=0.6, color=c["ACCENT"],
                            spaceBefore=2, spaceAfter=5))
    for item in langs:
        story.append(Paragraph(f"• {_fmt(item)}", SB["bullet"]))

def _sidebar_certs(cv_data, story, SB, c):
    certs = cv_data.get("certifications", [])
    if not certs:
        return
    story.append(Paragraph("CERTIFICATIONS", SB["section_head"]))
    story.append(HRFlowable(width="100%", thickness=0.6, color=c["ACCENT"],
                            spaceBefore=2, spaceAfter=5))
    for item in certs:
        story.append(Paragraph(f"• {_fmt(item)}", SB["bullet"]))

def _build_sidebar(cv_data, story, SB, c, include_header=True):
    """Assemble le contenu complet d'une sidebar."""
    if include_header:
        _sidebar_header(cv_data, story, SB, c)
        story.append(Spacer(1, 6))
    _sidebar_skills(cv_data, story, SB, c)
    _sidebar_languages(cv_data, story, SB, c)
    _sidebar_certs(cv_data, story, SB, c)

# ─────────────────────────────────────────────────────────────────────────────
# BLOCS DE CONTENU — COLONNE PRINCIPALE
# ─────────────────────────────────────────────────────────────────────────────
def _main_header(cv_data, story, M, c):
    """En-tête pleine largeur: nom + titre + contacts."""
    story.append(Paragraph(cv_data.get("full_name", "").upper(), M["name"]))
    if cv_data.get("title"):
        story.append(Paragraph(cv_data["title"], M["subtitle"]))
    parts = [cv_data.get(f, "") for f in ["email", "phone", "location", "linkedin", "github"]
             if _clean(cv_data.get(f, ""))]
    if parts:
        story.append(Paragraph("  ·  ".join(parts), M["contact"]))
    story.append(HRFlowable(width="100%", thickness=1.5, color=c["ACCENT"],
                            spaceBefore=2, spaceAfter=8))

def _section_title(story, title, M, c):
    story.append(Paragraph(title, M["section_head"]))

def _main_summary(cv_data, story, M, c):
    if not cv_data.get("summary"):
        return
    _section_title(story, "PROFIL PROFESSIONNEL", M, c)
    story.append(Paragraph(cv_data["summary"], M["body"]))
    story.append(Spacer(1, 4))

def _main_experiences(cv_data, story, M, c):
    exps = cv_data.get("experiences", [])
    if not exps:
        return
    _section_title(story, "EXPÉRIENCES PROFESSIONNELLES", M, c)
    for exp in exps:
        # Titre du poste + entreprise sur la même ligne
        title_txt = f"<b>{exp.get('title', '')}</b>"
        if exp.get("company"):
            title_txt += f"  <font color='#64748b'>@ {exp['company']}</font>"
        story.append(Paragraph(title_txt, M["job_title"]))
        # Méta: dates + lieu
        meta = []
        start = exp.get("start_date", "")
        end   = exp.get("end_date", "Présent")
        if start:
            meta.append(f"{start} → {end}")
        if exp.get("location"):
            meta.append(exp["location"])
        if meta:
            story.append(Paragraph("  ·  ".join(meta), M["job_meta"]))
        for b in exp.get("bullets", []):
            story.append(Paragraph(f"• {b}", M["bullet"]))
        story.append(Spacer(1, 4))

def _main_projects(cv_data, story, M, c):
    projs = cv_data.get("projects", [])
    if not projs:
        return
    _section_title(story, "PROJETS & RÉALISATIONS", M, c)
    for proj in projs:
        story.append(Paragraph(f"<b>{proj.get('name', 'Projet')}</b>", M["job_title"]))
        if proj.get("description"):
            story.append(Paragraph(proj["description"], M["body"]))
        for b in proj.get("bullets", []):
            story.append(Paragraph(f"• {b}", M["bullet"]))
        story.append(Spacer(1, 4))

def _main_education(cv_data, story, M, c):
    educs = cv_data.get("education", [])
    if not educs:
        return
    _section_title(story, "FORMATION", M, c)
    for edu in educs:
        title_txt = f"<b>{edu.get('degree', '')}</b>"
        if edu.get("institution"):
            title_txt += f"  <font color='#64748b'>— {edu['institution']}</font>"
        story.append(Paragraph(title_txt, M["job_title"]))
        meta = [edu.get(f) for f in ["year", "location"] if edu.get(f)]
        if meta:
            story.append(Paragraph("  ·  ".join(meta), M["job_meta"]))
        story.append(Spacer(1, 3))

def _main_skills_inline(cv_data, story, M, c):
    """Compétences en grille compacte dans la colonne principale."""
    skills = cv_data.get("skills", {})
    if not skills:
        return
    _section_title(story, "COMPÉTENCES", M, c)
    for cat, items in skills.items():
        vals = "  ·  ".join(items) if isinstance(items, list) else str(items)
        story.append(Paragraph(f"<b>{cat.upper()}</b>  —  {vals}", M["skill_val"]))
    story.append(Spacer(1, 4))

def _main_languages_inline(cv_data, story, M, c):
    langs = cv_data.get("languages", [])
    if not langs:
        return
    _section_title(story, "LANGUES", M, c)
    for item in langs:
        story.append(Paragraph(f"• {_fmt(item)}", M["bullet"]))
    story.append(Spacer(1, 4))

def _main_certs_inline(cv_data, story, M, c):
    certs = cv_data.get("certifications", [])
    if not certs:
        return
    _section_title(story, "CERTIFICATIONS", M, c)
    for item in certs:
        story.append(Paragraph(f"• {_fmt(item)}", M["bullet"]))
    story.append(Spacer(1, 4))

def _build_main_full(cv_data, story, M, c):
    """Contenu principal complet (layouts colonne unique sans sidebar)."""
    _main_header(cv_data, story, M, c)
    _main_summary(cv_data, story, M, c)
    _main_experiences(cv_data, story, M, c)
    _main_projects(cv_data, story, M, c)
    _main_skills_inline(cv_data, story, M, c)
    _main_education(cv_data, story, M, c)
    _main_languages_inline(cv_data, story, M, c)
    _main_certs_inline(cv_data, story, M, c)

def _build_main_nosidebar_info(cv_data, story, M, c):
    """Contenu principal sans compétences/langues/certs (déjà dans sidebar)."""
    _main_header(cv_data, story, M, c)
    _main_summary(cv_data, story, M, c)
    _main_experiences(cv_data, story, M, c)
    _main_projects(cv_data, story, M, c)
    _main_education(cv_data, story, M, c)

# ─────────────────────────────────────────────────────────────────────────────
# LAYOUTS
# ─────────────────────────────────────────────────────────────────────────────

def _render_modern_sidebar(cv_data, doc, story, styles, c):
    """Sidebar GAUCHE (32%) | Colonne principale (68%). Multi-page stable."""
    SB, M = styles["SB"], styles["M"]
    PW, PH = LETTER
    SW = PW * 0.32

    def on_page(canvas, d):
        canvas.saveState()
        canvas.setFillColor(c["SIDEBAR_BG"])
        canvas.rect(0, 0, SW, PH, fill=1, stroke=0)
        canvas.restoreState()

    f_sb   = Frame(0,  0, SW,      PH, leftPadding=22, rightPadding=14, topPadding=28, bottomPadding=24, id='sb')
    f_main = Frame(SW, 0, PW - SW, PH, leftPadding=22, rightPadding=28, topPadding=28, bottomPadding=24, id='main')
    f_p2   = Frame(SW, 0, PW - SW, PH, leftPadding=22, rightPadding=28, topPadding=24, bottomPadding=24, id='main_p2')

    doc.addPageTemplates([
        PageTemplate(id='P1', frames=[f_sb, f_main], onPage=on_page),
        PageTemplate(id='P2', frames=[f_p2],         onPage=on_page)
    ])

    # Sidebar: header (nom + contacts) + compétences + langues + certifs
    _build_sidebar(cv_data, story, SB, c, include_header=True)

    story.append(FrameBreak())
    story.append(NextPageTemplate('P2'))

    # Main: profil + expériences + projets + formation
    _build_main_nosidebar_info(cv_data, story, M, c)


def _render_reverse_sidebar(cv_data, doc, story, styles, c):
    """Colonne principale (68%) | Sidebar DROITE (32%). Multi-page stable."""
    SB, M = styles["SB"], styles["M"]
    PW, PH = LETTER
    SW = PW * 0.32

    def on_page(canvas, d):
        canvas.saveState()
        canvas.setFillColor(c["SIDEBAR_BG"])
        canvas.rect(PW - SW, 0, SW, PH, fill=1, stroke=0)
        canvas.restoreState()

    f_main = Frame(0,       0, PW - SW, PH, leftPadding=28, rightPadding=22, topPadding=28, bottomPadding=24, id='main')
    f_sb   = Frame(PW - SW, 0, SW,      PH, leftPadding=14, rightPadding=20, topPadding=28, bottomPadding=24, id='sb')
    f_p2   = Frame(0,       0, PW - SW, PH, leftPadding=28, rightPadding=22, topPadding=24, bottomPadding=24, id='main_p2')

    doc.addPageTemplates([
        PageTemplate(id='P1', frames=[f_main, f_sb], onPage=on_page),
        PageTemplate(id='P2', frames=[f_p2],         onPage=on_page)
    ])

    _build_main_nosidebar_info(cv_data, story, M, c)
    story.append(NextPageTemplate('P2'))
    story.append(FrameBreak())
    _build_sidebar(cv_data, story, SB, c, include_header=True)


def _render_classic_single(cv_data, doc, story, styles, c):
    """Colonne unique classique, bien hiérarchisée."""
    M = styles["M"]
    frame = Frame(50, 36, LETTER[0] - 100, LETTER[1] - 72,
                  leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    doc.addPageTemplates([PageTemplate(id='L', frames=[frame])])
    _build_main_full(cv_data, story, M, c)


def _render_executive_band(cv_data, doc, story, styles, c):
    """Bandeau header en haut, puis 2 colonnes en dessous."""
    SB, M = styles["SB"], styles["M"]
    PW, PH = LETTER
    SW    = PW * 0.33
    HD    = 88   # hauteur du bandeau

    def on_p1(canvas, d):
        canvas.saveState()
        canvas.setFillColor(c["SIDEBAR_BG"])
        canvas.rect(0, PH - HD, PW, HD, fill=1, stroke=0)
        # Ligne décorative sous le bandeau
        canvas.setStrokeColor(c["ACCENT"])
        canvas.setLineWidth(2)
        canvas.line(0, PH - HD, PW, PH - HD)
        canvas.restoreState()

    def on_p2(canvas, d):
        pass  # Pas de bandeau sur page 2

    BODY_H  = PH - HD - 36   # hauteur disponible sous bandeau
    BODY_Y  = 24              # marge basse

    f_hdr    = Frame(0,  PH - HD, PW,          HD,     leftPadding=36, rightPadding=36, topPadding=12, bottomPadding=8)
    f_left   = Frame(24, BODY_Y,  SW,           BODY_H, leftPadding=12, rightPadding=12, topPadding=16, bottomPadding=16, id='bl')
    f_right  = Frame(24 + SW + 8, BODY_Y, PW - SW - 48, BODY_H, leftPadding=12, rightPadding=12, topPadding=16, bottomPadding=16, id='br')
    f_p2 = Frame(28, 24, PW - 56, PH - 48, leftPadding=16, rightPadding=16, topPadding=24, bottomPadding=24)

    doc.addPageTemplates([
        PageTemplate(id='P1', frames=[f_hdr, f_left, f_right], onPage=on_p1),
        PageTemplate(id='P2', frames=[f_p2], onPage=on_p2)
    ])

    on_hdr = _on(c["SIDEBAR_BG"])
    s_hdr_name = ParagraphStyle("hbn", parent=M["name"],
                                textColor=on_hdr, alignment=TA_CENTER, fontSize=24, leading=28, spaceAfter=2)
    s_hdr_sub  = ParagraphStyle("hbs", parent=M["subtitle"],
                                textColor=c["ACCENT"] if on_hdr == white else c["MAIN_TITLE"], alignment=TA_CENTER, fontSize=11, leading=14)
    s_hdr_con  = ParagraphStyle("hbc", parent=M["contact"],
                                textColor=on_hdr, alignment=TA_CENTER, fontSize=8, leading=11, spaceAfter=0)

    story.append(Paragraph(cv_data.get("full_name", "").upper(), s_hdr_name))
    if cv_data.get("title"):
        story.append(Paragraph(cv_data["title"], s_hdr_sub))
    parts = [cv_data.get(f, "") for f in ["email", "phone", "location", "linkedin", "github"]
             if _clean(cv_data.get(f, ""))]
    if parts:
        story.append(Paragraph("  ·  ".join(parts), s_hdr_con))

    # Colonne Gauche (fond BLANC): compétences + langues + certifs avec styles foncés
    story.append(FrameBreak())
    story.append(NextPageTemplate('P2'))
    # Pour la colonne gauche sur fond blanc, on utilise les styles M (texte foncé)
    _main_skills_inline(cv_data, story, M, c)
    _main_languages_inline(cv_data, story, M, c)
    _main_certs_inline(cv_data, story, M, c)

    # Colonne Droite: profil + expériences + projets + formation
    story.append(FrameBreak())
    _main_summary(cv_data, story, M, c)
    _main_experiences(cv_data, story, M, c)
    _main_projects(cv_data, story, M, c)
    _main_education(cv_data, story, M, c)


def _render_terminal_code(cv_data, doc, story, styles, c):
    """Style terminal complet sur fond noir."""
    M = styles["SB"]
    PW, PH = LETTER

    def on_page(canvas, d):
        canvas.saveState()
        canvas.setFillColor(HexColor("#0a0a0a"))
        canvas.rect(0, 0, PW, PH, fill=1, stroke=0)
        canvas.restoreState()

    frame = Frame(28, 28, PW - 56, PH - 56,
                  leftPadding=16, rightPadding=16, topPadding=16, bottomPadding=16)
    doc.addPageTemplates([PageTemplate(id='L', frames=[frame], onPage=on_page)])

    ACCENT_C = c["ACCENT"]
    GREEN    = HexColor("#00ff7f")

    s_prompt  = ParagraphStyle("tp", parent=M["name"],    fontName="Courier-Bold", fontSize=16, textColor=ACCENT_C, spaceAfter=2)
    s_sys     = ParagraphStyle("ts", parent=M["body"],    fontName="Courier",      fontSize=9,  textColor=HexColor("#4ade80"), spaceAfter=2)
    s_section = ParagraphStyle("th", parent=M["section_head"] if "section_head" in M else M["name"],
                               fontName="Courier-Bold", fontSize=10, textColor=ACCENT_C,
                               spaceBefore=10, spaceAfter=4, textTransform="uppercase")
    s_body    = ParagraphStyle("tb", parent=M["body"],    fontName="Courier",      fontSize=9,  textColor=HexColor("#d1fae5"), spaceAfter=3, leading=12)
    s_bullet  = ParagraphStyle("tbu", parent=M["bullet"], fontName="Courier",      fontSize=9,  textColor=HexColor("#d1fae5"), spaceAfter=2, leading=12, leftIndent=14, firstLineIndent=-10)

    story.append(Paragraph(f"> BOOT CANDIDATE '{cv_data.get('full_name','').upper()}'", s_prompt))
    story.append(Paragraph(f"> ROLE: {cv_data.get('title', 'N/A')}", s_sys))
    parts = [cv_data.get(f, "") for f in ["email","phone","location","linkedin","github"] if _clean(cv_data.get(f,""))]
    if parts:
        story.append(Paragraph(f"> CONTACT: {' | '.join(parts)}", s_sys))
    story.append(HRFlowable(width="100%", thickness=1, color=ACCENT_C, spaceBefore=6, spaceAfter=10))

    if cv_data.get("summary"):
        story.append(Paragraph("> LOADING PROFILE.exe...", s_section))
        story.append(Paragraph(cv_data["summary"], s_body))

    exps = cv_data.get("experiences", [])
    if exps:
        story.append(Paragraph("> QUERY EXPERIENCES --all", s_section))
        for exp in exps:
            co   = exp.get("company", "")
            role = exp.get("title", "")
            story.append(Paragraph(f"[{exp.get('start_date','??')}→{exp.get('end_date','NOW')}]  <b>{role}</b> @ {co}", s_body))
            for b in exp.get("bullets", []):
                story.append(Paragraph(f"  ↳ {b}", s_bullet))

    skills = cv_data.get("skills", {})
    if skills:
        story.append(Paragraph("> IMPORT SKILLS --verbose", s_section))
        for cat, items in skills.items():
            vals = ", ".join(items) if isinstance(items, list) else str(items)
            story.append(Paragraph(f"{cat.upper()}: {vals}", s_body))

    educs = cv_data.get("education", [])
    if educs:
        story.append(Paragraph("> SELECT * FROM EDUCATION", s_section))
        for edu in educs:
            story.append(Paragraph(f"[{edu.get('year','')}] {edu.get('degree','')} — {edu.get('institution','')}",s_body))

    langs = cv_data.get("languages", [])
    if langs:
        story.append(Paragraph("> RUNTIME LANGUAGES", s_section))
        for item in langs:
            story.append(Paragraph(f"  · {_fmt(item)}", s_body))

    story.append(Paragraph("> STATUS: READY FOR HIRE", s_section))


def _render_grid_bento(cv_data, doc, story, styles, c):
    """2 colonnes égales page 1 (Creative Bold)."""
    M, SB = styles["M"], styles["SB"]
    PW, PH = LETTER
    half = PW / 2.0

    f_l  = Frame(24,      24, half - 28,  PH - 48, leftPadding=18, rightPadding=10, topPadding=24, bottomPadding=24, id='l')
    f_r  = Frame(half + 4, 24, half - 28,  PH - 48, leftPadding=10, rightPadding=18, topPadding=24, bottomPadding=24, id='r')
    f_p2 = Frame(24,      24, PW - 48,    PH - 48, leftPadding=18, rightPadding=18, topPadding=28, bottomPadding=24)

    doc.addPageTemplates([
        PageTemplate(id='P1', frames=[f_l, f_r]),
        PageTemplate(id='P2', frames=[f_p2])
    ])

    # Col gauche: en-tête + profil + expériences
    _main_header(cv_data, story, M, c)
    _main_summary(cv_data, story, M, c)
    _main_experiences(cv_data, story, M, c)

    story.append(FrameBreak())
    story.append(NextPageTemplate('P2'))

    # Col droite: projets + compétences + formation + langues
    _main_projects(cv_data, story, M, c)
    _main_skills_inline(cv_data, story, M, c)
    _main_education(cv_data, story, M, c)
    _main_languages_inline(cv_data, story, M, c)
    _main_certs_inline(cv_data, story, M, c)


def _render_centered_minimal(cv_data, doc, story, styles, c):
    """Colonne unique centrée, style académique sobre."""
    M = styles["M"]
    # Override name style: centré
    s_name = ParagraphStyle("cn", parent=M["name"], alignment=TA_CENTER, fontSize=26, leading=30)
    s_sub  = ParagraphStyle("cs", parent=M["subtitle"], alignment=TA_CENTER)
    s_con  = ParagraphStyle("cc", parent=M["contact"], alignment=TA_CENTER)

    frame = Frame(48, 36, LETTER[0] - 96, LETTER[1] - 72,
                  leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    doc.addPageTemplates([PageTemplate(id='L', frames=[frame])])

    story.append(Paragraph(cv_data.get("full_name", "").upper(), s_name))
    if cv_data.get("title"):
        story.append(Paragraph(cv_data["title"], s_sub))
    parts = [cv_data.get(f, "") for f in ["email", "phone", "location", "linkedin", "github"]
             if _clean(cv_data.get(f, ""))]
    if parts:
        story.append(Paragraph("  |  ".join(parts), s_con))
    story.append(HRFlowable(width="100%", thickness=1.5, color=c["ACCENT"], spaceBefore=4, spaceAfter=8))

    _main_summary(cv_data, story, M, c)
    _main_experiences(cv_data, story, M, c)
    _main_projects(cv_data, story, M, c)
    _main_skills_inline(cv_data, story, M, c)
    _main_education(cv_data, story, M, c)
    _main_languages_inline(cv_data, story, M, c)
    _main_certs_inline(cv_data, story, M, c)


def _render_split_equal(cv_data, doc, story, styles, c):
    """
    Vibrant Energy — 50/50 plein écran.
    GAUCHE (fond rouge): Nom + Titre + Contacts + Compétences + Langues + Certifs
    DROITE (blanc): Profil + Expériences + Projets + Formation
    """
    SB, M = styles["SB"], styles["M"]
    PW, PH = LETTER
    half = PW / 2.0

    def on_p1(canvas, d):
        canvas.saveState()
        canvas.setFillColor(c["SIDEBAR_BG"])
        canvas.rect(0, 0, half, PH, fill=1, stroke=0)
        canvas.restoreState()

    def on_p2(canvas, d):
        pass

    f_l  = Frame(0,    0, half,     PH, leftPadding=26, rightPadding=16, topPadding=32, bottomPadding=28, id='l')
    f_r  = Frame(half, 0, half,     PH, leftPadding=16, rightPadding=26, topPadding=32, bottomPadding=28, id='r')
    f_p2 = Frame(28,  28, PW - 56, PH - 56, leftPadding=20, rightPadding=20, topPadding=24, bottomPadding=24)

    doc.addPageTemplates([
        PageTemplate(id='P1', frames=[f_l, f_r], onPage=on_p1),
        PageTemplate(id='P2', frames=[f_p2],     onPage=on_p2)
    ])

    # ── Colonne GAUCHE: identité + infos contact + compétences/langues/certifs ──
    _build_sidebar(cv_data, story, SB, c, include_header=True)

    # ── Colonne DROITE: tout le contenu professionnel ──
    story.append(FrameBreak())
    story.append(NextPageTemplate('P2'))

    _main_summary(cv_data, story, M, c)
    _main_experiences(cv_data, story, M, c)
    _main_projects(cv_data, story, M, c)
    _main_education(cv_data, story, M, c)


def _render_compact_tight(cv_data, doc, story, styles, c):
    """Elegant Luxury — colonne unique très compacte, raffinée."""
    SB, M = styles["SB"], styles["M"]
    PW, PH = LETTER

    def on_page(canvas, d):
        # Bandeau latéral gauche fin (barre décorative)
        canvas.saveState()
        canvas.setFillColor(c["SIDEBAR_BG"])
        canvas.rect(0, 0, 6, PH, fill=1, stroke=0)
        canvas.setFillColor(c["ACCENT"])
        canvas.rect(6, 0, 3, PH, fill=1, stroke=0)
        canvas.restoreState()

    frame = Frame(22, 28, PW - 50, PH - 56,
                  leftPadding=20, rightPadding=20, topPadding=20, bottomPadding=20)
    doc.addPageTemplates([PageTemplate(id='L', frames=[frame], onPage=on_page)])

    _build_main_full(cv_data, story, M, c)


# ─────────────────────────────────────────────────────────────────────────────
# DISPATCHER PRINCIPAL
# ─────────────────────────────────────────────────────────────────────────────
def generate_cv_pdf(cv_data: Dict[str, Any], theme_id: str = "midnight") -> bytes:
    buffer = io.BytesIO()
    theme  = THEMES.get(theme_id, THEMES["midnight"])
    c      = _get_colors(theme_id)
    styles = _get_styles(c)

    doc   = BaseDocTemplate(buffer, pagesize=LETTER)
    story: List = []

    layout_map = {
        "modern_sidebar":  _render_modern_sidebar,
        "reverse_sidebar": _render_reverse_sidebar,
        "classic_single":  _render_classic_single,
        "executive_band":  _render_executive_band,
        "grid_bento":      _render_grid_bento,
        "centered_minimal":_render_centered_minimal,
        "terminal_code":   _render_terminal_code,
        "split_equal":     _render_split_equal,
        "compact_tight":   _render_compact_tight,
    }

    render = layout_map.get(theme["layout"], _render_modern_sidebar)
    render(cv_data, doc, story, styles, c)

    doc.build(story)
    buffer.seek(0)
    return buffer.read()
