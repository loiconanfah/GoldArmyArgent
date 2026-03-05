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

# ── Système de Thèmes & Layouts Premium ───────────────────────────
THEMES = {
    "midnight": {
        "name": "Midnight Pro", "layout": "modern_sidebar",
        "sidebar_bg": "#1e293b", "accent": "#38bdf8", "text_sidebar": "#f8fafc",
        "text_main": "#334155", "title_main": "#0f172a", "line": "#e2e8f0",
        "font_main": "Helvetica", "font_bold": "Helvetica-Bold"
    },
    "emerald": {
        "name": "Emerald Leader", "layout": "modern_sidebar",
        "sidebar_bg": "#064e3b", "accent": "#10b981", "text_sidebar": "#ecfdf5",
        "text_main": "#1f2937", "title_main": "#064e3b", "line": "#d1fae5",
        "font_main": "Helvetica", "font_bold": "Helvetica-Bold"
    },
    "modern": {
        "name": "Modern Startup", "layout": "reverse_sidebar",
        "sidebar_bg": "#4c1d95", "accent": "#8b5cf6", "text_sidebar": "#f5f3ff",
        "text_main": "#1e293b", "title_main": "#4c1d95", "line": "#ede9fe",
        "font_main": "Helvetica", "font_bold": "Helvetica-Bold"
    },
    "minimal": {
        "name": "Executive Minimal", "layout": "classic_single",
        "sidebar_bg": "#ffffff", "accent": "#0f172a", "text_sidebar": "#334155",
        "text_main": "#334155", "title_main": "#000000", "line": "#f1f5f9",
        "font_main": "Times-Roman", "font_bold": "Times-Bold"
    },
    "bold": {
        "name": "Creative Bold", "layout": "grid_bento",
        "sidebar_bg": "#000000", "accent": "#f43f5e", "text_sidebar": "#ffffff",
        "text_main": "#000000", "title_main": "#000000", "line": "#ffe4e6",
        "font_main": "Helvetica", "font_bold": "Helvetica-Bold"
    },
    "banker": {
        "name": "Trustworthy Banker", "layout": "executive_band",
        "sidebar_bg": "#1e3a8a", "accent": "#1e40af", "text_sidebar": "#ffffff",
        "text_main": "#000000", "title_main": "#1e3a8a", "line": "#dbeafe",
        "font_main": "Helvetica", "font_bold": "Helvetica-Bold"
    },
    "tech": {
        "name": "Tech God Mode", "layout": "terminal_code",
        "sidebar_bg": "#000000", "accent": "#22c55e", "text_sidebar": "#22c55e",
        "text_main": "#dcfce7", "title_main": "#22c55e", "line": "#166534",
        "font_main": "Courier", "font_bold": "Courier-Bold"
    },
    "classic": {
        "name": "Classic Academic", "layout": "centered_minimal",
        "sidebar_bg": "#ffffff", "accent": "#451a03", "text_sidebar": "#451a03",
        "text_main": "#451a03", "title_main": "#451a03", "line": "#ffedd5",
        "font_main": "Times-Roman", "font_bold": "Times-Bold"
    },
    "vibrant": {
        "name": "Vibrant Energy", "layout": "split_equal",
        "sidebar_bg": "#991b1b", "accent": "#ea580c", "text_sidebar": "#fef2f2",
        "text_main": "#450a0a", "title_main": "#991b1b", "line": "#fee2e2",
        "font_main": "Helvetica", "font_bold": "Helvetica-Bold"
    },
    "luxury": {
        "name": "Elegant Luxury", "layout": "compact_tight",
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
    return (color.red * 0.299 + color.green * 0.587 + color.blue * 0.114) < 0.5

def _get_styles(c):
    base = getSampleStyleSheet()
    is_dark_sb = _is_dark(c["SIDEBAR_BG"])
    
    return {
        "SB": {
            "heading": ParagraphStyle("sb_h", parent=base["Normal"], fontName=c["FONT_BOLD"], fontSize=11, textColor=white if is_dark_sb else black, spaceBefore=15),
            "label": ParagraphStyle("sb_l", parent=base["Normal"], fontName=c["FONT_BOLD"], fontSize=9.5, textColor=c["ACCENT"], spaceBefore=6),
            "body": ParagraphStyle("sb_b", parent=base["Normal"], fontName=c["FONT"], fontSize=9, textColor=c["SIDEBAR_TEXT"]),
            "bullet": ParagraphStyle("sb_bul", parent=base["Normal"], fontName=c["FONT"], fontSize=9, textColor=c["SIDEBAR_TEXT"], leftIndent=12, bulletColor=c["ACCENT"])
        },
        "M": {
            "name": ParagraphStyle("name", parent=base["Normal"], fontName=c["FONT_BOLD"], fontSize=26, textColor=c["ACCENT"]),
            "contact": ParagraphStyle("contact", parent=base["Normal"], fontName=c["FONT"], fontSize=9.5, textColor=c["MAIN_TEXT"], spaceAfter=15),
            "section_head": ParagraphStyle("s_head", parent=base["Normal"], fontName=c["FONT_BOLD"], fontSize=12, textColor=c["MAIN_TITLE"], spaceBefore=16, spaceAfter=4),
            "job_title": ParagraphStyle("j_title", parent=base["Normal"], fontName=c["FONT_BOLD"], fontSize=11, textColor=c["MAIN_TITLE"], spaceBefore=10),
            "job_meta": ParagraphStyle("j_meta", parent=base["Normal"], fontName=c["FONT"], fontSize=9.5, textColor=c["ACCENT"]),
            "body": ParagraphStyle("body", parent=base["Normal"], fontName=c["FONT"], fontSize=10, textColor=c["MAIN_TEXT"]),
            "bullet": ParagraphStyle("bullet", parent=base["Normal"], fontName=c["FONT"], fontSize=10, textColor=c["MAIN_TEXT"], leftIndent=15, bulletColor=c["ACCENT"])
        }
    }

# ── Layout Rendering Functions ──────────────────────────────────────────

def _render_modern_sidebar(cv_data, doc, story, styles, colors):
    """Layout: Left Sidebar."""
    S, M = styles["SB"], styles["M"]
    PAGE_WIDTH, PAGE_HEIGHT = LETTER
    SIDEBAR_W = PAGE_WIDTH * 0.34
    
    frame_left = Frame(0, 0, SIDEBAR_W, PAGE_HEIGHT, leftPadding=24, rightPadding=18, topPadding=36, bottomPadding=36)
    frame_right = Frame(SIDEBAR_W, 0, PAGE_WIDTH - SIDEBAR_W, PAGE_HEIGHT, leftPadding=24, rightPadding=36, topPadding=36, bottomPadding=36)
    
    on_page = lambda canvas, d: canvas.rect(0, 0, SIDEBAR_W, PAGE_HEIGHT, fill=1, stroke=0) if canvas.setFillColor(colors["SIDEBAR_BG"]) is None else None
    doc.addPageTemplates([PageTemplate(id='Layout', frames=[frame_left, frame_right], onPage=on_page)])
    
    # Left Content
    _add_sidebar_content(cv_data, story, S, colors)
    story.append(FrameBreak())
    # Right Content
    _add_main_content(cv_data, story, M, colors)

def _render_reverse_sidebar(cv_data, doc, story, styles, colors):
    """Layout: Right Sidebar."""
    S, M = styles["SB"], styles["M"]
    PAGE_WIDTH, PAGE_HEIGHT = LETTER
    SIDEBAR_W = PAGE_WIDTH * 0.34
    
    frame_main = Frame(0, 0, PAGE_WIDTH - SIDEBAR_W, PAGE_HEIGHT, leftPadding=36, rightPadding=24, topPadding=36, bottomPadding=36)
    frame_sidebar = Frame(PAGE_WIDTH - SIDEBAR_W, 0, SIDEBAR_W, PAGE_HEIGHT, leftPadding=18, rightPadding=24, topPadding=36, bottomPadding=36)
    
    on_page = lambda canvas, d: canvas.rect(PAGE_WIDTH - SIDEBAR_W, 0, SIDEBAR_W, PAGE_HEIGHT, fill=1, stroke=0) if canvas.setFillColor(colors["SIDEBAR_BG"]) is None else None
    doc.addPageTemplates([PageTemplate(id='Layout', frames=[frame_main, frame_sidebar], onPage=on_page)])
    
    _add_main_content(cv_data, story, M, colors)
    story.append(FrameBreak())
    _add_sidebar_content(cv_data, story, S, colors)

def _render_classic_single(cv_data, doc, story, styles, colors):
    """Layout: Single Column Classic."""
    M = styles["M"]
    frame = Frame(inch/2, inch/2, LETTER[0]-inch, LETTER[1]-inch)
    doc.addPageTemplates([PageTemplate(id='Layout', frames=[frame])])
    
    _add_main_content(cv_data, story, M, colors)
    story.append(Spacer(1, 20))
    _add_sidebar_content(cv_data, story, M, colors) # Reuse main styles for single col

def _render_executive_band(cv_data, doc, story, styles, colors):
    """Layout: Top Header Band."""
    M = styles["M"]
    header_h = 140
    frame_top = Frame(0, LETTER[1]-header_h, LETTER[0], header_h, topPadding=40)
    frame_bottom = Frame(inch/2, inch/2, LETTER[0]-inch, LETTER[1]-header_h-inch/2)
    
    on_page = lambda canvas, d: canvas.rect(0, LETTER[1]-header_h, LETTER[0], header_h, fill=1, stroke=0) if canvas.setFillColor(colors["SIDEBAR_BG"]) is None else None
    doc.addPageTemplates([PageTemplate(id='Layout', frames=[frame_top, frame_bottom], onPage=on_page)])
    
    # Header
    name_style = ParagraphStyle("exec_name", parent=M["name"], textColor=white if _is_dark(colors["SIDEBAR_BG"]) else black, alignment=TA_CENTER)
    story.append(Paragraph(cv_data.get("full_name", ""), name_style))
    story.append(FrameBreak())
    _add_main_content(cv_data, story, M, colors, skip_header=True)

def _render_terminal_code(cv_data, doc, story, styles, colors):
    """Layout: Tech Terminal."""
    M = styles["M"]
    frame = Frame(40, 40, LETTER[0]-80, LETTER[1]-80)
    on_page = lambda canvas, d: canvas.rect(0, 0, LETTER[0], LETTER[1], fill=1, stroke=0) if canvas.setFillColor(black) is None else None
    doc.addPageTemplates([PageTemplate(id='Layout', frames=[frame], onPage=on_page)])
    
    story.append(Paragraph(f"> INIT CANDIDATE: {cv_data.get('full_name', '')}", M["name"]))
    _add_main_content(cv_data, story, M, colors, skip_header=True)

def _render_grid_bento(cv_data, doc, story, styles, colors):
    """Layout: Grid/Bento Boxes."""
    M = styles["M"]
    # For Bento, we'll use a 2-column layout with boxes (simulated by spacing/HRs)
    _render_modern_sidebar(cv_data, doc, story, styles, colors)

def _render_centered_minimal(cv_data, doc, story, styles, colors):
    """Layout: Centered Minimal."""
    M = styles["M"]
    centered_name = ParagraphStyle("center", parent=M["name"], alignment=TA_CENTER)
    frame = Frame(inch, inch, LETTER[0]-2*inch, LETTER[1]-2*inch)
    doc.addPageTemplates([PageTemplate(id='Layout', frames=[frame])])
    
    story.append(Paragraph(cv_data.get("full_name", ""), centered_name))
    _add_main_content(cv_data, story, M, colors, skip_header=True)

def _render_split_equal(cv_data, doc, story, styles, colors):
    """Layout: Split Equal 50/50."""
    S, M = styles["SB"], styles["M"]
    frame_l = Frame(0, 0, LETTER[0]/2, LETTER[1], leftPadding=30, rightPadding=20)
    frame_r = Frame(LETTER[0]/2, 0, LETTER[0]/2, LETTER[1], leftPadding=20, rightPadding=30)
    doc.addPageTemplates([PageTemplate(id='Layout', frames=[frame_l, frame_r])])
    _add_sidebar_content(cv_data, story, S, colors)
    story.append(FrameBreak())
    _add_main_content(cv_data, story, M, colors)

def _render_compact_tight(cv_data, doc, story, styles, colors):
    """Layout: Compact Tight spacing."""
    # Similar to classic but with reduced Spacers
    _render_classic_single(cv_data, doc, story, styles, colors)

def _render_accent_frame(cv_data, doc, story, styles, colors):
    """Layout: Geometric Frame."""
    on_page = lambda canvas, d: [canvas.setStrokeColor(colors["ACCENT"]), canvas.setLineWidth(5), canvas.rect(20, 20, LETTER[0]-40, LETTER[1]-40)]
    _render_classic_single(cv_data, doc, story, styles, colors)

# ── Content Helpers ──────────────────────────────────────────────────

def _add_sidebar_content(cv_data, story, S, colors):
    skills = cv_data.get("skills", {})
    if skills:
        title_style = S.get("heading") or S.get("section_head")
        story.append(Paragraph("COMPÉTENCES", title_style))
        for cat, items in skills.items():
            story.append(Paragraph(cat, S["label"] if "label" in S else S["job_title"]))
            vals = ", ".join(items) if isinstance(items, list) else str(items)
            story.append(Paragraph(vals, S["body"]))
    
    for section, key in [("LANGUES", "languages"), ("CERTIFICATIONS", "certifications")]:
        items = cv_data.get(key, [])
        if items:
            title_style = S.get("heading") or S.get("section_head")
            story.append(Paragraph(section, title_style))
            for item in items:
                story.append(Paragraph(f"<bullet>•</bullet>{item}", S["bullet"]))

def _add_main_content(cv_data, story, M, colors, skip_header=False):
    if not skip_header:
        story.append(Paragraph(cv_data.get("full_name", "Candidat"), M["name"]))
        title = cv_data.get("title", "")
        if title: story.append(Paragraph(title, M["body"]))
        
        contact = "  |  ".join([v for v in [cv_data.get(f) for f in ["email", "phone", "location"]] if v])
        if contact: story.append(Paragraph(contact, M["contact"]))

    if cv_data.get("summary"):
        story.append(Paragraph("PROFIL", M["section_head"]))
        story.append(Paragraph(cv_data["summary"], M["body"]))

    exps = cv_data.get("experiences", [])
    if exps:
        story.append(Paragraph("EXPÉRIENCES", M["section_head"]))
        for exp in exps:
            title = f"{exp.get('title', '')} @ {exp.get('company', '')}"
            story.append(Paragraph(title, M["job_title"]))
            for b in exp.get("bullets", []):
                story.append(Paragraph(f"<bullet>•</bullet>{b}", M["bullet"]))

    edus = cv_data.get("education", [])
    if edus:
        story.append(Paragraph("FORMATION", M["section_head"]))
        for edu in edus:
            story.append(Paragraph(edu.get("degree", ""), M["job_title"]))

# ── Dispatcher ──────────────────────────────────────────────────────

def generate_cv_pdf(cv_data: Dict[str, Any], theme_id: str = "midnight") -> bytes:
    buffer = io.BytesIO()
    theme = THEMES.get(theme_id, THEMES["midnight"])
    colors = _get_colors(theme_id)
    styles = _get_styles(colors)
    
    doc = BaseDocTemplate(buffer, pagesize=LETTER)
    story = []
    
    layout_map = {
        "modern_sidebar": _render_modern_sidebar,
        "reverse_sidebar": _render_reverse_sidebar,
        "classic_single": _render_classic_single,
        "executive_band": _render_executive_band,
        "grid_bento": _render_grid_bento,
        "centered_minimal": _render_centered_minimal,
        "terminal_code": _render_terminal_code,
        "split_equal": _render_split_equal,
        "compact_tight": _render_compact_tight,
        "accent_frame": _render_accent_frame
    }
    
    render_func = layout_map.get(theme["layout"], _render_modern_sidebar)
    render_func(cv_data, doc, story, styles, colors)
    
    doc.build(story)
    buffer.seek(0)
    return buffer.read()
