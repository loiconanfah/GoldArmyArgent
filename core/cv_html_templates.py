"""
CV HTML Templates — Python port of the 8 TypeScript mobile templates.
Each build_* function returns a full HTML string for Playwright→PDF conversion.
"""
import html as _html

# ── helpers ──────────────────────────────────────────────────────────────────

def esc(v) -> str:
    if isinstance(v, list):
        return ", ".join(esc(i) for i in v)
    return _html.escape(str(v or ""))

def _fields(d: dict) -> dict:
    raw = d
    linkedin = (d.get("linkedin") or raw.get("linkedin_url") or
                raw.get("linkedinUrl") or raw.get("linkedin_profile") or "")
    github   = d.get("github") or raw.get("github_url") or ""
    skills_html = _build_skills(d.get("skills", {}))
    return dict(
        full_name = d.get("full_name") or "Prénom Nom",
        job_title = d.get("title") or "",
        email     = d.get("email") or "",
        phone     = d.get("phone") or "",
        location  = d.get("location") or "",
        linkedin  = linkedin,
        github    = github,
        summary   = d.get("summary") or "",
        experiences   = d.get("experiences") or [],
        projects      = d.get("projects") or [],
        education     = d.get("education") or [],
        languages     = [str(x) for x in (d.get("languages") or [])],
        certifications= [str(x) for x in (d.get("certifications") or [])],
        skills_html   = skills_html,
    )

def _build_skills(skills) -> str:
    if isinstance(skills, dict):
        out = ""
        for cat, items in skills.items():
            if isinstance(items, list) and items:
                out += f'<div class="skill-cat">{esc(cat)}</div>'
                out += '<div class="skill-pills">' + "".join(f'<span class="pill">{esc(s)}</span>' for s in items) + '</div>'
        return out
    if isinstance(skills, list):
        return '<div class="skill-pills">' + "".join(f'<span class="pill">{esc(s)}</span>' for s in skills) + '</div>'
    return ""

def _contact_items(f: dict, icon_color="#333") -> str:
    parts = []
    if f["phone"]:    parts.append(f'<span class="ci-ic" style="color:{icon_color}">☎</span>{esc(f["phone"])}')
    if f["email"]:    parts.append(f'<span class="ci-ic" style="color:{icon_color}">✉</span>{esc(f["email"])}')
    if f["location"]: parts.append(f'<span class="ci-ic" style="color:{icon_color}">⌖</span>{esc(f["location"])}')
    if f["linkedin"]: parts.append(f'<span class="ci-ic" style="color:{icon_color}">in</span>{esc(f["linkedin"])}')
    if f["github"]:   parts.append(f'<span class="ci-ic" style="color:{icon_color}">⌾</span>{esc(f["github"])}')
    return "".join(f'<div class="ci">{p}</div>' for p in parts)

def _exp_blocks(experiences, bullet_color="#333") -> str:
    out = ""
    for e in experiences:
        dates = " – ".join(filter(None, [e.get("start_date",""), e.get("end_date","")]))
        bullets = "".join(
            f'<div class="bullet-row"><div class="bdot" style="background:{bullet_color}">▸</div><div>{esc(b)}</div></div>'
            for b in (e.get("bullets") or [])
        )
        loc = f' <span class="exp-loc">· {esc(e.get("location",""))}</span>' if e.get("location") else ""
        out += f'''<div class="exp-block">
          <div class="exp-top"><span class="exp-title">{esc(e.get("title",""))}</span><span class="exp-dates">{esc(dates)}</span></div>
          <div class="exp-co">{esc(e.get("company",""))}{loc}</div>{bullets}</div>'''
    return out

def _proj_blocks(projects, bullet_color="#333") -> str:
    out = ""
    for p in projects:
        bullets = "".join(
            f'<div class="bullet-row"><div class="bdot" style="background:{bullet_color}">▸</div><div>{esc(b)}</div></div>'
            for b in (p.get("bullets") or [])
        )
        desc = f'<div class="proj-desc">{esc(p.get("description",""))}</div>' if p.get("description") else ""
        out += f'<div class="proj-block"><div class="proj-name">{esc(p.get("name",""))}</div>{desc}{bullets}</div>'
    return out

def _edu_blocks(education) -> str:
    out = ""
    for e in education:
        meta = " · ".join(filter(None, [e.get("location",""), e.get("year","")]))
        out += f'''<div class="edu-block">
          <div class="edu-degree">{esc(e.get("degree",""))}</div>
          <div class="edu-school">{esc(e.get("institution") or e.get("school",""))}</div>
          <div class="edu-meta">{esc(meta)}</div></div>'''
    return out

# ── REGISTRY ─────────────────────────────────────────────────────────────────

TEMPLATES = {}

def register(tid, label, description, accent):
    def decorator(fn):
        TEMPLATES[tid] = {"id": tid, "label": label, "description": description,
                          "accent": accent, "build": fn}
        return fn
    return decorator

# ── 1. GoldArmy ───────────────────────────────────────────────────────────────

@register("goldarmy", "GoldArmy", "Dark / Orange", "#FF6B35")
def build_goldarmy(cv_data: dict) -> str:
    f = _fields(cv_data)
    name_parts = f["full_name"].split()
    fn, ln = (name_parts[0], " ".join(name_parts[1:])) if len(name_parts) > 1 else (f["full_name"], "")
    contact = _contact_items(f, "#FF6B35")
    exp_html = _exp_blocks(f["experiences"], "#FF6B35")
    proj_html = _proj_blocks(f["projects"], "#FF6B35")
    edu_html = _edu_blocks(f["education"])
    langs = "".join(f'<div class="lang-item">• {esc(l)}</div>' for l in f["languages"])
    certs = "".join(f'<div class="cert-item">{esc(c)}</div>' for c in f["certifications"])
    return f"""<!DOCTYPE html><html lang="fr"><head><meta charset="utf-8"/>
<style>
@page{size: A4; margin: 0;}
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{font-family:'Inter',sans-serif;font-size:11px;line-height:1.5;background:#fff;-webkit-print-color-adjust:exact;print-color-adjust:exact;width:210mm;min-height:297mm;}}
body::before{{content:'';position:fixed;top:0;left:0;bottom:0;width:220px;background:#1A1A2E;z-index:-1;}}
.page{{display:flex;width:100%;min-height:100%;}}
.sidebar{{width:220px;padding:28px 18px;flex-shrink:0;}}
.main{{flex:1;padding:28px 26px;}}
.initials{{width:66px;height:66px;border-radius:50%;background:#FF6B35;display:flex;align-items:center;justify-content:center;font-size:20px;font-weight:800;color:#fff;margin:0 auto 12px;}}
.name-first{{font-size:11px;color:#FF6B35;letter-spacing:3px;text-transform:uppercase;text-align:center;}}
.name-last{{font-size:20px;font-weight:800;color:#fff;text-align:center;}}
.job-title{{font-size:10px;color:#B0B0CC;text-align:center;margin-top:3px;letter-spacing:1px;text-transform:uppercase;}}
.ci{{display:flex;align-items:flex-start;gap:6px;font-size:9.5px;color:#A0A0BB;margin-bottom:5px;word-break:break-all;}}
.ci-ic{{font-size:11px;flex-shrink:0;font-weight:700;}}
.sb-title{{font-size:9px;letter-spacing:2.5px;text-transform:uppercase;color:#FF6B35;margin:16px 0 6px;border-bottom:1px solid #FF6B3533;padding-bottom:3px;}}
.edu-degree{{font-size:10px;font-weight:600;color:#E0E0FF;}} .edu-school{{font-size:10px;color:#8080AA;}} .edu-meta{{font-size:9px;color:#6060AA;}} .edu-block{{margin-bottom:8px;}}
.skill-cat{{font-size:9px;letter-spacing:1px;text-transform:uppercase;color:#FF6B35;margin:6px 0 3px;}}
.skill-pills{{display:flex;flex-wrap:wrap;gap:3px;}}
.pill{{background:#27274A;border:1px solid #FF6B3533;border-radius:2px;padding:2px 6px;font-size:9px;color:#C0C0FF;}}
.lang-item{{font-size:10px;color:#A0A0BB;margin-bottom:3px;}} .cert-item{{font-size:10px;color:#A0A0BB;margin-bottom:3px;border-left:2px solid #FF6B35;padding-left:6px;}}
.sec-head{{display:flex;align-items:center;gap:8px;margin:16px 0 8px;}} .sec-head:first-child{{margin-top:0;}}
.sec-bar{{width:3px;height:14px;background:#FF6B35;border-radius:2px;flex-shrink:0;}}
.sec-label{{font-size:9px;letter-spacing:3px;text-transform:uppercase;color:#1A1A2E;font-weight:700;}}
.summary-text{{font-size:11px;color:#444;line-height:1.7;}}
.exp-block{{margin-bottom:14px;padding-left:10px;border-left:2px solid #F0EDE8;}}
.exp-top{{display:flex;justify-content:space-between;}} .exp-title{{font-size:12px;font-weight:700;color:#111;}} .exp-dates{{font-size:9px;color:#FF6B35;}}
.exp-co{{font-size:10px;color:#666;margin-bottom:4px;}} .exp-loc{{color:#AAA;font-weight:400;}}
.bullet-row{{display:flex;gap:6px;margin-bottom:2px;font-size:10px;color:#555;}}
.bdot{{flex-shrink:0;font-size:9px;margin-top:1px;}}
.proj-block{{margin-bottom:12px;padding:8px 10px;border:1px solid #F0EDE8;border-radius:4px;}}
.proj-name{{font-size:11px;font-weight:700;color:#111;margin-bottom:3px;}} .proj-desc{{font-size:10px;color:#666;margin-bottom:4px;}}
</style></head><body><div class="page">
<div class="sidebar">
  <div class="initials">{esc(fn[:1])}{esc(ln[:1])}</div>
  <div class="name-first">{esc(fn)}</div>
  <div class="name-last">{esc(ln)}</div>
  {f'<div class="job-title">{esc(f["job_title"])}</div>' if f["job_title"] else ""}
  <div style="margin-top:12px">{contact}</div>
  {f'<div class="sb-title">Formation</div>{edu_html}' if f["education"] else ""}
  {f'<div class="sb-title">Compétences</div>{f["skills_html"]}' if f["skills_html"] else ""}
  {f'<div class="sb-title">Langues</div>{langs}' if langs else ""}
  {f'<div class="sb-title">Certifications</div>{certs}' if certs else ""}
</div>
<div class="main">
  {f'<div class="sec-head"><div class="sec-bar"></div><div class="sec-label">Profil</div></div><p class="summary-text">{esc(f["summary"])}</p>' if f["summary"] else ""}
  {f'<div class="sec-head"><div class="sec-bar"></div><div class="sec-label">Expériences</div></div>{exp_html}' if exp_html else ""}
  {f'<div class="sec-head"><div class="sec-bar"></div><div class="sec-label">Projets</div></div>{proj_html}' if proj_html else ""}
</div></div></body></html>"""

# ── 2. Minimaliste ────────────────────────────────────────────────────────────

@register("minimaliste", "Minimaliste", "Blanc / Bleu", "#2563EB")
def build_minimaliste(cv_data: dict) -> str:
    f = _fields(cv_data)
    contact_str = " · ".join(filter(None, [esc(f["email"]), esc(f["phone"]), esc(f["location"]),
                                            f'LinkedIn: {esc(f["linkedin"])}' if f["linkedin"] else "",
                                            f'GitHub: {esc(f["github"])}' if f["github"] else ""]))
    exp_html = _exp_blocks(f["experiences"], "#2563EB")
    proj_html = _proj_blocks(f["projects"], "#2563EB")
    edu_html = _edu_blocks(f["education"])
    langs = " · ".join(esc(l) for l in f["languages"])
    certs = " · ".join(esc(c) for c in f["certifications"])
    sec = lambda label: f'<div style="font-size:9px;letter-spacing:3px;text-transform:uppercase;color:#2563EB;font-weight:700;margin:18px 0 8px;border-bottom:2px solid #2563EB;padding-bottom:3px;">{label}</div>'
    return f"""<!DOCTYPE html><html lang="fr"><head><meta charset="utf-8"/>
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
@page{size: A4; margin: 0;}
*{{margin:0;padding:0;box-sizing:border-box;}} body{{font-family:'Inter',sans-serif;font-size:11px;background:#fff;color:#222;-webkit-print-color-adjust:exact;print-color-adjust:exact;width:210mm;min-height:297mm;}}
.page{{width:100%;min-height:100%;padding:48px 52px;}}
h1{{font-size:32px;font-weight:700;color:#111;letter-spacing:-1px;}} .subtitle{{font-size:13px;color:#2563EB;letter-spacing:2px;text-transform:uppercase;margin-top:4px;}}
.contact{{font-size:10px;color:#666;margin-top:10px;}} .summary-text{{font-size:11.5px;color:#444;line-height:1.75;}}
.exp-block,.proj-block{{margin-bottom:14px;}} .exp-top{{display:flex;justify-content:space-between;}} .exp-title{{font-size:12px;font-weight:700;}} .exp-dates{{font-size:9px;color:#2563EB;}}
.exp-co{{font-size:10px;color:#666;margin-bottom:4px;}} .exp-loc{{color:#AAA;}}
.bullet-row{{display:flex;gap:6px;font-size:10px;color:#555;margin-bottom:2px;}} .bdot{{flex-shrink:0;color:#2563EB;font-size:9px;margin-top:1px;}}
.proj-name{{font-size:11px;font-weight:700;}} .proj-desc{{font-size:10px;color:#666;}}
.edu-degree{{font-size:11px;font-weight:600;}} .edu-school{{font-size:10px;color:#666;}} .edu-meta{{font-size:9px;color:#AAA;}}
.bottom{{display:grid;grid-template-columns:1fr 1fr;gap:24px;margin-top:4px;}}
.skill-cat{{font-size:9px;text-transform:uppercase;color:#2563EB;font-weight:700;margin:6px 0 3px;}}
.skill-pills{{display:flex;flex-wrap:wrap;gap:3px;}} .pill{{border:1px solid #ddd;border-radius:2px;padding:2px 7px;font-size:9px;color:#444;}}
</style></head><body><div class="page">
<h1>{esc(f["full_name"])}</h1>
{f'<div class="subtitle">{esc(f["job_title"])}</div>' if f["job_title"] else ""}
{f'<div class="contact">{contact_str}</div>' if contact_str else ""}
{f'{sec("Profil")}<p class="summary-text">{esc(f["summary"])}</p>' if f["summary"] else ""}
{f'{sec("Expériences")}{exp_html}' if exp_html else ""}
{f'{sec("Projets")}{proj_html}' if proj_html else ""}
{f'{sec("Formation")}{edu_html}' if edu_html else ""}
<div class="bottom">
  {f'<div>{sec("Compétences")}{f["skills_html"]}</div>' if f["skills_html"] else "<div></div>"}
  <div>
    {f'{sec("Langues")}<p style="font-size:10px;color:#555;">{langs}</p>' if langs else ""}
    {f'{sec("Certifications")}<p style="font-size:10px;color:#555;">{certs}</p>' if certs else ""}
  </div>
</div>
</div></body></html>"""

# ── 3. Executive ──────────────────────────────────────────────────────────────

@register("executive", "Executive", "Sombre / Émeraude", "#6EE7B7")
def build_executive(cv_data: dict) -> str:
    f = _fields(cv_data)
    contact = _contact_items(f, "#6EE7B7")
    exp_html = _exp_blocks(f["experiences"], "#6EE7B7")
    proj_html = _proj_blocks(f["projects"], "#6EE7B7")
    edu_html = _edu_blocks(f["education"])
    langs = "".join(f'<div style="font-size:10px;color:#A0A0CC;margin-bottom:3px;">– {esc(l)}</div>' for l in f["languages"])
    certs = "".join(f'<div style="font-size:10px;color:#A0A0CC;margin-bottom:3px;border-left:2px solid #6EE7B7;padding-left:5px;">{esc(c)}</div>' for c in f["certifications"])
    sec = lambda t: f'<div style="font-size:9px;letter-spacing:3px;text-transform:uppercase;color:#6EE7B7;margin:16px 0 8px;border-bottom:1px solid #6EE7B733;padding-bottom:4px;">{t}</div>'
    return f"""<!DOCTYPE html><html lang="fr"><head><meta charset="utf-8"/>
<style>
@page{size: A4; margin: 0;}
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');
*{{margin:0;padding:0;box-sizing:border-box;}} body{{font-family:'Inter',sans-serif;font-size:11px;background:#0D1117;color:#E0E0FF;-webkit-print-color-adjust:exact;print-color-adjust:exact;width:210mm;min-height:297mm;}}
body::before{{content:'';position:fixed;top:0;left:0;bottom:0;width:220px;background:#161B22;border-right:1px solid #6EE7B722;z-index:-1;}}
.page{{display:flex;width:100%;min-height:100%;}}
.sidebar{{width:220px;flex-shrink:0;padding:28px 18px;}}
.main{{flex:1;padding:28px 26px;}}
.sb-name{{font-size:20px;font-weight:800;color:#fff;text-align:center;}} .sb-title{{font-size:10px;color:#6EE7B7;text-transform:uppercase;letter-spacing:2px;text-align:center;margin-top:4px;}}
.ci{{display:flex;align-items:flex-start;gap:6px;font-size:9.5px;color:#9090BB;margin-bottom:5px;word-break:break-all;}} .ci-ic{{color:#6EE7B7;font-weight:700;flex-shrink:0;}}
.sb-sec{{font-size:9px;letter-spacing:2.5px;text-transform:uppercase;color:#6EE7B7;margin:16px 0 6px;border-bottom:1px solid #6EE7B733;padding-bottom:3px;}}
.edu-degree{{font-size:10px;font-weight:600;color:#E0E0FF;}} .edu-school{{font-size:10px;color:#7070AA;}} .edu-meta{{font-size:9px;color:#5050AA;}} .edu-block{{margin-bottom:8px;}}
.skill-cat{{font-size:9px;text-transform:uppercase;color:#6EE7B7;margin:6px 0 3px;}}
.skill-pills{{display:flex;flex-wrap:wrap;gap:3px;}} .pill{{background:#1A2030;border:1px solid #6EE7B733;border-radius:2px;padding:2px 6px;font-size:9px;color:#C0C0FF;}}
.summary-text{{font-size:11px;color:#B0B0CC;line-height:1.7;}}
.exp-block{{margin-bottom:14px;padding-left:10px;border-left:2px solid #1A2030;}}
.exp-top{{display:flex;justify-content:space-between;}} .exp-title{{font-size:12px;font-weight:700;color:#fff;}} .exp-dates{{font-size:9px;color:#6EE7B7;}}
.exp-co{{font-size:10px;color:#6EE7B7;margin-bottom:4px;}} .exp-loc{{color:#506070;font-weight:400;}}
.bullet-row{{display:flex;gap:6px;font-size:10px;color:#A0A0CC;margin-bottom:2px;}} .bdot{{flex-shrink:0;font-size:9px;margin-top:1px;}}
.proj-block{{margin-bottom:12px;padding:8px 10px;border:1px solid #1A2030;border-radius:4px;background:#161B22;}}
.proj-name{{font-size:11px;font-weight:700;color:#fff;margin-bottom:3px;}} .proj-desc{{font-size:10px;color:#7070AA;}}
</style></head><body><div class="page">
<div class="sidebar">
  <div style="margin-bottom:14px;">
    <div class="sb-name">{esc(f["full_name"])}</div>
    {f'<div class="sb-title">{esc(f["job_title"])}</div>' if f["job_title"] else ""}
  </div>
  {contact}
  {f'<div class="sb-sec">Formation</div>{edu_html}' if edu_html else ""}
  {f'<div class="sb-sec">Compétences</div>{f["skills_html"]}' if f["skills_html"] else ""}
  {f'<div class="sb-sec">Langues</div>{langs}' if langs else ""}
  {f'<div class="sb-sec">Certifications</div>{certs}' if certs else ""}
</div>
<div class="main">
  {f'{sec("Profil")}<p class="summary-text">{esc(f["summary"])}</p>' if f["summary"] else ""}
  {f'{sec("Expériences")}{exp_html}' if exp_html else ""}
  {f'{sec("Projets")}{proj_html}' if proj_html else ""}
</div></div></body></html>"""

# ── 4–8: Créatif, Classique, Néon Tech, Scandinave, Timeline ──────────────────

@register("creatif", "Créatif", "Violet / Rose", "#EC4899")
def build_creatif(cv_data: dict) -> str:
    f = _fields(cv_data)
    contact = _contact_items(f, "#EC4899")
    exp_html = _exp_blocks(f["experiences"], "#EC4899")
    proj_html = _proj_blocks(f["projects"], "#EC4899")
    edu_html = _edu_blocks(f["education"])
    langs = "".join(f'<div style="font-size:10px;color:#C0A0CC;margin-bottom:3px;">✦ {esc(l)}</div>' for l in f["languages"])
    certs = "".join(f'<div style="font-size:10px;color:#C0A0CC;margin-bottom:3px;border-left:2px solid #EC4899;padding-left:5px;">{esc(c)}</div>' for c in f["certifications"])
    sec = lambda t: f'<div style="font-size:9px;letter-spacing:3px;text-transform:uppercase;color:#EC4899;margin:16px 0 8px;border-bottom:1px solid #EC489933;padding-bottom:3px;">{t}</div>'
    return f"""<!DOCTYPE html><html lang="fr"><head><meta charset="utf-8"/>
<style>
@page{size: A4; margin: 0;}
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@300;400;600;700;800&display=swap');
*{{margin:0;padding:0;box-sizing:border-box;}} body{{font-family:'Nunito',sans-serif;font-size:11px;background:#1A0A2E;color:#E0D0FF;-webkit-print-color-adjust:exact;print-color-adjust:exact;width:210mm;min-height:297mm;}}
body::before{{content:'';position:fixed;top:0;left:0;bottom:0;width:220px;background:#0F0718;z-index:-1;}}
.page{{display:flex;width:100%;min-height:100%;}}
.sidebar{{width:220px;padding:28px 18px;flex-shrink:0;}}
.main{{flex:1;padding:28px 24px;}}
.hdr-name{{font-size:22px;font-weight:800;color:#fff;text-align:center;}} .hdr-title{{font-size:10px;color:#EC4899;text-transform:uppercase;letter-spacing:2px;text-align:center;margin-top:4px;}}
.ci{{display:flex;align-items:flex-start;gap:6px;font-size:9.5px;color:#9070AA;margin-bottom:5px;word-break:break-all;}} .ci-ic{{color:#EC4899;font-weight:700;flex-shrink:0;}}
.sb-sec{{font-size:9px;letter-spacing:2.5px;text-transform:uppercase;color:#EC4899;margin:16px 0 6px;border-bottom:1px solid #EC489933;padding-bottom:3px;}}
.edu-degree{{font-size:10px;font-weight:700;color:#E0D0FF;}} .edu-school{{font-size:10px;color:#9070AA;}} .edu-meta{{font-size:9px;color:#704080;}} .edu-block{{margin-bottom:8px;}}
.skill-cat{{font-size:9px;text-transform:uppercase;color:#EC4899;margin:6px 0 3px;}}
.skill-pills{{display:flex;flex-wrap:wrap;gap:3px;}} .pill{{background:#25103A;border:1px solid #EC489933;border-radius:10px;padding:2px 7px;font-size:9px;color:#D0B0EE;}}
.summary-text{{font-size:11px;color:#C0A0E0;line-height:1.75;}}
.exp-block{{margin-bottom:14px;padding-left:10px;border-left:2px solid #25103A;}}
.exp-top{{display:flex;justify-content:space-between;}} .exp-title{{font-size:12px;font-weight:700;color:#fff;}} .exp-dates{{font-size:9px;color:#EC4899;}}
.exp-co{{font-size:10px;color:#EC4899;margin-bottom:4px;}} .exp-loc{{color:#70408080;font-weight:400;}}
.bullet-row{{display:flex;gap:6px;font-size:10px;color:#B090CC;margin-bottom:2px;}} .bdot{{flex-shrink:0;font-size:9px;margin-top:1px;}}
.proj-block{{margin-bottom:12px;padding:8px 10px;border:1px solid #25103A;border-radius:6px;background:#0F0718;}}
.proj-name{{font-size:11px;font-weight:700;color:#fff;margin-bottom:3px;}} .proj-desc{{font-size:10px;color:#9070AA;}}
</style></head><body><div class="page">
<div class="sidebar">
  <div style="margin-bottom:14px;">
    <div class="hdr-name">{esc(f["full_name"])}</div>
    {f'<div class="hdr-title">{esc(f["job_title"])}</div>' if f["job_title"] else ""}
  </div>
  {contact}
  {f'<div class="sb-sec">Formation</div>{edu_html}' if edu_html else ""}
  {f'<div class="sb-sec">Compétences</div>{f["skills_html"]}' if f["skills_html"] else ""}
  {f'<div class="sb-sec">Langues</div>{langs}' if langs else ""}
  {f'<div class="sb-sec">Certifications</div>{certs}' if certs else ""}
</div>
<div class="main">
  {f'{sec("Profil")}<p class="summary-text">{esc(f["summary"])}</p>' if f["summary"] else ""}
  {f'{sec("Expériences")}{exp_html}' if exp_html else ""}
  {f'{sec("Projets")}{proj_html}' if proj_html else ""}
</div></div></body></html>"""

@register("classique", "Classique", "Noir & Blanc", "#1a1a1a")
def build_classique(cv_data: dict) -> str:
    f = _fields(cv_data)
    contact_str = " | ".join(filter(None, [esc(f["email"]), esc(f["phone"]), esc(f["location"]),
                                           f'LinkedIn: {esc(f["linkedin"])}' if f["linkedin"] else ""]))
    exp_html = _exp_blocks(f["experiences"], "#1a1a1a")
    proj_html = _proj_blocks(f["projects"], "#1a1a1a")
    edu_html = _edu_blocks(f["education"])
    langs = " | ".join(esc(l) for l in f["languages"])
    certs = "".join(f'<div style="font-size:10px;color:#333;margin-bottom:3px;">• {esc(c)}</div>' for c in f["certifications"])
    sec = lambda t: f'<div style="font-size:9px;letter-spacing:3px;text-transform:uppercase;color:#1a1a1a;font-weight:700;margin:18px 0 6px;border-bottom:2px solid #1a1a1a;padding-bottom:3px;">{t}</div>'
    return f"""<!DOCTYPE html><html lang="fr"><head><meta charset="utf-8"/>
<style>
@page{size: A4; margin: 0;}
@import url('https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400;0,600;1,400&family=Inter:wght@400;600&display=swap');
*{{margin:0;padding:0;box-sizing:border-box;}} body{{font-family:'EB Garamond',serif;font-size:12px;background:#fff;color:#111;-webkit-print-color-adjust:exact;print-color-adjust:exact;width:210mm;min-height:297mm;}}
.page{{width:100%;padding:50px 60px;}}
.hdr{{text-align:center;margin-bottom:20px;border-bottom:2px solid #1a1a1a;padding-bottom:16px;}}
h1{{font-size:34px;font-weight:600;letter-spacing:3px;text-transform:uppercase;}}
.hdr-title{{font-size:13px;font-style:italic;color:#666;margin-top:4px;}}
.contact{{font-size:10px;color:#555;font-family:'Inter',sans-serif;margin-top:8px;}}
.summary-text{{font-size:12px;line-height:1.8;color:#333;font-style:italic;}}
.exp-block{{margin-bottom:14px;}} .exp-top{{display:flex;justify-content:space-between;align-items:baseline;}}
.exp-title{{font-size:12px;font-weight:600;}} .exp-dates{{font-size:10px;color:#888;font-family:'Inter',sans-serif;}}
.exp-co{{font-size:11px;color:#555;font-style:italic;margin-bottom:4px;}} .exp-loc{{color:#AAA;}}
.bullet-row{{display:flex;gap:6px;font-size:11px;color:#444;margin-bottom:2px;}} .bdot{{flex-shrink:0;font-size:10px;margin-top:1px;}}
.proj-block{{margin-bottom:12px;}} .proj-name{{font-size:12px;font-weight:600;}} .proj-desc{{font-size:11px;color:#666;font-style:italic;}}
.edu-degree{{font-size:11px;font-weight:600;}} .edu-school{{font-size:11px;color:#555;font-style:italic;}} .edu-meta{{font-size:10px;color:#AAA;font-family:'Inter',sans-serif;}} .edu-block{{margin-bottom:8px;}}
.bottom{{display:grid;grid-template-columns:1fr 1fr;gap:32px;}}
.skill-cat{{font-size:9px;text-transform:uppercase;color:#1a1a1a;font-weight:600;margin:6px 0 3px;font-family:'Inter',sans-serif;}}
.skill-pills{{display:flex;flex-wrap:wrap;gap:3px;}} .pill{{border:1px solid #ddd;border-radius:2px;padding:2px 7px;font-size:10px;color:#333;}}
</style></head><body><div class="page">
<div class="hdr">
  <h1>{esc(f["full_name"])}</h1>
  {f'<div class="hdr-title">{esc(f["job_title"])}</div>' if f["job_title"] else ""}
  {f'<div class="contact">{contact_str}</div>' if contact_str else ""}
</div>
{f'{sec("Profil")}<p class="summary-text">{esc(f["summary"])}</p>' if f["summary"] else ""}
{f'{sec("Expériences")}{exp_html}' if exp_html else ""}
{f'{sec("Projets")}{proj_html}' if proj_html else ""}
{f'{sec("Formation")}{edu_html}' if edu_html else ""}
<div class="bottom">
  {f'<div>{sec("Compétences")}{f["skills_html"]}</div>' if f["skills_html"] else "<div></div>"}
  <div>
    {f'{sec("Langues")}<p style="font-size:11px;color:#555;">{langs}</p>' if langs else ""}
    {f'{sec("Certifications")}{certs}' if certs else ""}
  </div>
</div>
</div></body></html>"""

@register("neon_tech", "Néon Tech", "Dark / Cyber", "#00E5FF")
def build_neon_tech(cv_data: dict) -> str:
    f = _fields(cv_data)
    contact = _contact_items(f, "#00E5FF")
    exp_html = _exp_blocks(f["experiences"], "#00E5FF")
    edu_html = _edu_blocks(f["education"])
    langs = "".join(f'<div style="font-size:10px;color:#8080CC;margin-bottom:3px;"><span style="color:#FF00A0;">●</span> {esc(l)}</div>' for l in f["languages"])
    certs = "".join(f'<div style="font-size:10px;color:#8080CC;border-left:2px solid #FF00A0;padding-left:5px;margin-bottom:3px;">{esc(c)}</div>' for c in f["certifications"])
    fn_parts = f["full_name"].split(); fn = fn_parts[0]; ln = " ".join(fn_parts[1:])
    return f"""<!DOCTYPE html><html lang="fr"><head><meta charset="utf-8"/>
<style>
@page{size: A4; margin: 0;}
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Inter:wght@300;400;600;700&display=swap');
*{{margin:0;padding:0;box-sizing:border-box;}} body{{font-family:'Inter',sans-serif;background:#0D0D1A;color:#E0E0FF;font-size:11px;-webkit-print-color-adjust:exact;print-color-adjust:exact;width:210mm;min-height:297mm;}}
body::before{{content:'';position:fixed;top:0;left:0;bottom:0;width:230px;background:#111128;border-right:1px solid #00E5FF22;z-index:-1;}}
.page{{display:flex;width:100%;min-height:100%;}}
.sidebar{{width:230px;padding:28px 18px;flex-shrink:0;}}
.main{{flex:1;padding:28px 24px;background:#0D0D1A;}}
.avatar{{width:66px;height:66px;border-radius:50%;border:2px solid #00E5FF;box-shadow:0 0 14px #00E5FF55;display:flex;align-items:center;justify-content:center;margin:0 auto 12px;background:#1A1A35;font-family:'Share Tech Mono',monospace;font-size:20px;color:#00E5FF;}}
.nm-first{{font-size:10px;color:#00E5FF;letter-spacing:3px;text-transform:uppercase;text-align:center;}} .nm-last{{font-size:18px;font-weight:700;color:#fff;text-align:center;}} .nm-title{{font-size:9px;color:#FF00A0;letter-spacing:2px;text-transform:uppercase;text-align:center;margin-top:3px;}}
.ci{{display:flex;align-items:flex-start;gap:6px;font-size:9.5px;color:#8080AA;margin-bottom:5px;word-break:break-all;}} .ci-ic{{color:#00E5FF;font-weight:700;flex-shrink:0;font-family:'Share Tech Mono',monospace;}}
.sb-sec{{font-size:9px;letter-spacing:2.5px;text-transform:uppercase;color:#FF00A0;margin:16px 0 6px;border-bottom:1px solid #FF00A033;padding-bottom:3px;}}
.edu-degree{{font-size:10px;font-weight:600;color:#E0E0FF;}} .edu-school{{font-size:10px;color:#6060AA;}} .edu-meta{{font-size:9px;color:#404080;}} .edu-block{{margin-bottom:8px;}}
.skill-cat{{font-size:9px;text-transform:uppercase;color:#00E5FF;margin:6px 0 3px;}} .skill-pills{{display:flex;flex-wrap:wrap;gap:3px;}} .pill{{background:#1A1A3A;border:1px solid #00E5FF33;border-radius:2px;padding:2px 6px;font-size:9px;color:#C0C0FF;}}
.sec-head{{display:flex;align-items:center;gap:8px;margin:16px 0 8px;}} .sec-head:first-child{{margin-top:0;}}
.sec-bar{{width:3px;height:14px;background:linear-gradient(#00E5FF,#FF00A0);border-radius:2px;flex-shrink:0;}}
.sec-label{{font-size:9px;letter-spacing:3px;text-transform:uppercase;color:#00E5FF;font-family:'Share Tech Mono',monospace;}}
.summary-text{{font-size:11px;color:#C0C0E0;line-height:1.7;}}
.exp-block{{margin-bottom:14px;padding-left:10px;border-left:2px solid #1A1A3A;}}
.exp-top{{display:flex;justify-content:space-between;}} .exp-title{{font-size:12px;font-weight:700;color:#fff;}} .exp-dates{{font-size:9px;color:#00E5FF;font-family:'Share Tech Mono',monospace;}}
.exp-co{{font-size:10px;color:#FF00A0;font-weight:600;margin-bottom:4px;}} .exp-loc{{color:#6060AA;font-weight:400;}}
.bullet-row{{display:flex;gap:6px;font-size:10px;color:#C0C0E0;margin-bottom:2px;}} .bdot{{flex-shrink:0;font-size:9px;margin-top:1px;}}
</style></head><body><div class="page">
<div class="sidebar">
  <div class="avatar">{esc(fn[:1])}{esc(ln[:1])}</div>
  <div class="nm-first">{esc(fn)}</div><div class="nm-last">{esc(ln)}</div>
  {f'<div class="nm-title">{esc(f["job_title"])}</div>' if f["job_title"] else ""}
  <div style="margin-top:10px;">{contact}</div>
  {f'<div class="sb-sec">Formation</div>{edu_html}' if edu_html else ""}
  {f'<div class="sb-sec">Compétences</div>{f["skills_html"]}' if f["skills_html"] else ""}
  {f'<div class="sb-sec">Langues</div>{langs}' if langs else ""}
  {f'<div class="sb-sec">Certifications</div>{certs}' if certs else ""}
</div>
<div class="main">
  {f'<div class="sec-head"><div class="sec-bar"></div><div class="sec-label">Profil</div></div><p class="summary-text">{esc(f["summary"])}</p>' if f["summary"] else ""}
  {f'<div class="sec-head"><div class="sec-bar"></div><div class="sec-label">Expériences</div></div>{exp_html}' if exp_html else ""}
</div></div></body></html>"""

@register("scandinave", "Scandinave", "Épuré / Nordic", "#4A7C59")
def build_scandinave(cv_data: dict) -> str:
    f = _fields(cv_data)
    contact_str = " · ".join(filter(None, [esc(f["email"]), esc(f["phone"]), esc(f["location"]),
                                           f'LinkedIn: {esc(f["linkedin"])}' if f["linkedin"] else ""]))
    sec = lambda t: f'<div style="display:flex;align-items:center;gap:10px;margin:20px 0 10px;"><span style="font-size:9px;letter-spacing:3px;text-transform:uppercase;font-weight:700;color:#1A1A1A;white-space:nowrap;">{t}</span><div style="flex:1;height:1px;background:#ddd;"></div></div>'
    exp_out = ""
    for e in f["experiences"]:
        dates = " – ".join(filter(None,[e.get("start_date",""),e.get("end_date","")]))
        bullets = "".join(f'<li style="padding-left:10px;margin-bottom:2px;font-size:11px;color:#555;position:relative;list-style:none;"><span style="position:absolute;left:0;color:#4A7C59;font-weight:700;">–</span>{esc(b)}</li>' for b in (e.get("bullets") or []))
        exp_out += f'<div style="margin-bottom:14px;"><div style="display:flex;justify-content:space-between;align-items:baseline;"><div><span style="font-size:12px;font-weight:600;">{esc(e.get("title",""))}</span><span style="color:#BBB;"> — </span><span style="font-size:11px;color:#4A7C59;">{esc(e.get("company",""))}</span></div><span style="font-size:10px;color:#999;">{esc(dates)}</span></div><ul style="padding:0;margin-top:4px;">{bullets}</ul></div>'
    edu_out = "".join(f'<div style="display:flex;justify-content:space-between;margin-bottom:7px;"><span style="font-size:11px;font-weight:600;">{esc(e.get("degree",""))}</span><span style="font-size:11px;color:#888;font-style:italic;">{esc(e.get("institution") or e.get("school",""))}</span></div>' for e in f["education"])
    langs = " – ".join(esc(l) for l in f["languages"])
    certs = "".join(f'<div style="font-size:10px;color:#555;border-left:2px solid #4A7C59;padding-left:6px;margin-bottom:4px;">{esc(c)}</div>' for c in f["certifications"])
    return f"""<!DOCTYPE html><html lang="fr"><head><meta charset="utf-8"/>
<style>
@page{size: A4; margin: 0;}
@import url('https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,400;0,600;1,400&family=DM+Sans:wght@300;400;500;600&display=swap');
*{{margin:0;padding:0;box-sizing:border-box;}} body{{font-family:'DM Sans',sans-serif;background:#FAFAF7;color:#2B2B2B;font-size:11px;line-height:1.6;-webkit-print-color-adjust:exact;print-color-adjust:exact;width:210mm;min-height:297mm;}}
.page{{width:100%;padding:52px 60px;}}
h1{{font-family:'Lora',serif;font-size:36px;font-weight:600;letter-spacing:2px;color:#1A1A1A;}}
.hdr-title{{font-size:13px;font-weight:300;color:#4A7C59;letter-spacing:4px;text-transform:uppercase;margin-top:4px;}}
.contact{{font-size:10px;color:#888;margin-top:10px;}}
.summary-text{{font-size:11.5px;color:#444;line-height:1.8;font-style:italic;font-family:'Lora',serif;}}
.skill-cat{{font-size:9px;letter-spacing:1.5px;text-transform:uppercase;color:#4A7C59;margin:8px 0 4px;font-weight:600;}}
.skill-pills{{display:flex;flex-wrap:wrap;gap:4px;}} .pill{{border:1px solid #ddd;border-radius:2px;padding:2px 8px;font-size:10px;color:#444;background:#fff;}}
.bottom{{display:grid;grid-template-columns:1fr 1fr;gap:32px;}}
</style></head><body><div class="page">
<div style="text-align:center;margin-bottom:28px;">
  <h1>{esc(f["full_name"])}</h1>
  {f'<div class="hdr-title">{esc(f["job_title"])}</div>' if f["job_title"] else ""}
  {f'<div class="contact">{contact_str}</div>' if contact_str else ""}
</div>
{f'{sec("Profil")}<p class="summary-text">{esc(f["summary"])}</p>' if f["summary"] else ""}
{f'{sec("Expériences")}{exp_out}' if exp_out else ""}
{f'{sec("Formation")}{edu_out}' if edu_out else ""}
<div class="bottom">
  {f'<div>{sec("Compétences")}{f["skills_html"]}</div>' if f["skills_html"] else "<div></div>"}
  <div>
    {f'{sec("Langues")}<p style="font-size:10px;color:#555;">{langs}</p>' if langs else ""}
    {f'{sec("Certifications")}{certs}' if certs else ""}
  </div>
</div>
</div></body></html>"""

@register("timeline", "Timeline", "Infographique", "#E85D4A")
def build_timeline(cv_data: dict) -> str:
    f = _fields(cv_data)
    contact_r = "".join(filter(None,[
        f'<div style="display:flex;align-items:center;gap:5px;font-size:10px;color:#BBBBBB;margin-bottom:4px;justify-content:flex-end;"><span style="color:#E85D4A;font-weight:700;min-width:14px;text-align:center;">✉</span>{esc(f["email"])}</div>' if f["email"] else "",
        f'<div style="display:flex;align-items:center;gap:5px;font-size:10px;color:#BBBBBB;margin-bottom:4px;justify-content:flex-end;"><span style="color:#E85D4A;font-weight:700;min-width:14px;text-align:center;">☎</span>{esc(f["phone"])}</div>' if f["phone"] else "",
        f'<div style="display:flex;align-items:center;gap:5px;font-size:10px;color:#BBBBBB;margin-bottom:4px;justify-content:flex-end;"><span style="color:#E85D4A;font-weight:700;min-width:14px;text-align:center;">⌖</span>{esc(f["location"])}</div>' if f["location"] else "",
        f'<div style="display:flex;align-items:flex-start;gap:5px;font-size:10px;color:#BBBBBB;margin-bottom:4px;justify-content:flex-end;"><span style="color:#E85D4A;font-weight:700;min-width:14px;text-align:center;">in</span><span style="color:#E85D4A;font-size:9px;word-break:break-all;">{esc(f["linkedin"])}</span></div>' if f["linkedin"] else "",
    ]))
    tl_items = []
    for e in f["experiences"]:
        dates = " – ".join(filter(None,[e.get("start_date",""),e.get("end_date","")]))
        bullets = "".join(f'<li style="font-size:10px;color:#666;margin-bottom:2px;padding-left:8px;position:relative;list-style:none;"><span style="position:absolute;left:0;color:#E85D4A;font-weight:700;">›</span>{esc(b)}</li>' for b in (e.get("bullets") or []))
        tl_items.append({"type":"exp","title":e.get("title",""),"sub":e.get("company",""),"dates":dates,"bullets":bullets})
    for p in f["projects"]:
        tl_items.append({"type":"proj","title":p.get("name",""),"desc":p.get("description",""),"bullets":""})
    tl_html = ""
    for i, item in enumerate(tl_items):
        side = "left" if i%2==0 else "right"
        card = f'''<div style="background:#fff;border-radius:6px;padding:12px 14px;box-shadow:0 2px 10px rgba(0,0,0,0.07);margin-bottom:16px;">
          {f'<div style="font-size:9px;color:#E85D4A;font-weight:700;letter-spacing:1px;text-transform:uppercase;margin-bottom:3px;">{esc(item.get("dates",""))}</div>' if item.get("dates") else ""}
          <div style="font-size:12px;font-weight:700;color:#2D2D2D;">{esc(item["title"])}</div>
          {f'<div style="font-size:10px;color:#888;margin-bottom:5px;">{esc(item["sub"])}</div>' if item.get("sub") else ""}
          {f'<div style="font-size:11px;color:#666;margin-bottom:4px;">{esc(item["desc"])}</div>' if item.get("desc") else ""}
          <ul style="padding:0;margin-top:4px;">{item["bullets"]}</ul></div>'''
        left_content = card if side=="left" else ""
        right_content = card if side=="right" else ""
        tl_html += f'''<div style="display:flex;align-items:flex-start;">
          <div style="flex:1;padding:0 20px;text-align:right;">{left_content}</div>
          <div style="width:50px;flex-shrink:0;display:flex;flex-direction:column;align-items:center;position:relative;">
            <div style="width:28px;height:28px;border-radius:50%;background:#E85D4A;color:#fff;display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:800;box-shadow:0 2px 8px rgba(232,93,74,0.4);position:relative;z-index:1;">{"●" if item["type"]=="exp" else "★"}</div>
          </div>
          <div style="flex:1;padding:0 20px;">{right_content}</div>
        </div>'''
    skills_cell = f'<div><div style="font-size:9px;letter-spacing:2px;text-transform:uppercase;color:#E85D4A;font-weight:700;margin-bottom:8px;">Compétences</div>{f["skills_html"]}</div>' if f["skills_html"] else "<div></div>"
    edu_out = "".join(f'<div style="margin-bottom:8px;"><div style="font-size:10px;font-weight:600;">{esc(e.get("degree",""))}</div><div style="font-size:10px;color:#888;">{esc(e.get("institution") or e.get("school",""))}</div></div>' for e in f["education"])
    langs = "".join(f'<div style="font-size:10px;color:#666;margin-bottom:3px;">— {esc(l)}</div>' for l in f["languages"])
    return f"""<!DOCTYPE html><html lang="fr"><head><meta charset="utf-8"/>
<style>
@page{size: A4; margin: 0;}
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@300;400;600;700;800&family=Playfair+Display:wght@700&display=swap');
*{{margin:0;padding:0;box-sizing:border-box;}} body{{font-family:'Nunito',sans-serif;background:#F9F5F0;color:#2D2D2D;font-size:11px;-webkit-print-color-adjust:exact;print-color-adjust:exact;width:210mm;min-height:297mm;}}
.skill-cat{{font-size:9px;text-transform:uppercase;color:#E85D4A;margin:6px 0 3px;}} .skill-pills{{display:flex;flex-wrap:wrap;gap:3px;}} .pill{{background:#fff;border:1px solid #ddd;border-radius:10px;padding:2px 7px;font-size:9px;color:#555;}}
</style></head><body>
<div style="width:100%;">
  <div style="background:#2D2D2D;padding:28px 40px;display:flex;justify-content:space-between;align-items:center;">
    <div>
      <div style="font-family:'Playfair Display',serif;font-size:32px;color:#fff;">{esc(f["full_name"])}</div>
      {f'<div style="font-size:12px;color:#E85D4A;letter-spacing:3px;text-transform:uppercase;margin-top:4px;">{esc(f["job_title"])}</div>' if f["job_title"] else ""}
    </div>
    <div style="text-align:right;">{contact_r}</div>
  </div>
  {f'<div style="background:#fff;border-left:4px solid #E85D4A;padding:14px 40px;font-size:11.5px;color:#555;line-height:1.75;font-style:italic;">{esc(f["summary"])}</div>' if f["summary"] else ""}
  <div style="display:flex;background:#F0EBE3;">
    {skills_cell}
    {f'<div style="flex:1;padding:18px 22px;border-left:1px solid #E5DDD5;"><div style="font-size:9px;letter-spacing:2px;text-transform:uppercase;color:#E85D4A;font-weight:700;margin-bottom:8px;">Langues</div>{langs}</div>' if langs else ""}
    {f'<div style="flex:1;padding:18px 22px;border-left:1px solid #E5DDD5;"><div style="font-size:9px;letter-spacing:2px;text-transform:uppercase;color:#E85D4A;font-weight:700;margin-bottom:8px;">Formation</div>{edu_out}</div>' if edu_out else ""}
  </div>
  {f'<div style="padding:28px 0;"><div style="text-align:center;margin-bottom:18px;font-size:11px;letter-spacing:4px;text-transform:uppercase;color:#E85D4A;font-weight:700;">Parcours</div>{tl_html}</div>' if tl_html else ""}
</div></body></html>"""


def build_html(template_id: str, cv_data: dict) -> str | None:
    """Returns HTML string for the given template_id, or None if not found."""
    entry = TEMPLATES.get(template_id)
    if entry:
        return entry["build"](cv_data)
    return None
