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
    if f["phone"]:    parts.append(f'<span class="ci-ic" style="color:{icon_color}">☎</span> Tél: {esc(f["phone"])}')
    if f["email"]:    parts.append(f'<span class="ci-ic" style="color:{icon_color}">✉</span> Email: {esc(f["email"])}')
    if f["location"]: parts.append(f'<span class="ci-ic" style="color:{icon_color}">⌖</span> {esc(f["location"])}')
    if f["linkedin"]: parts.append(f'<span class="ci-ic" style="color:{icon_color}">in</span> LinkedIn: {esc(f["linkedin"])}')
    if f["github"]:   parts.append(f'<span class="ci-ic" style="color:{icon_color}">⌾</span> GitHub: {esc(f["github"])}')
    return "".join(f'<div class="ci">{p}</div>' for p in parts)

def _exp_blocks(experiences, bullet_color="#333") -> str:
    out = ""
    for e in experiences:
        dates = " – ".join(filter(None, [e.get("start_date",""), e.get("end_date","")]))
        bullets = "".join(
            f'<div class="bullet-row"><div class="bdot" style="color:{bullet_color}">•</div><div>{esc(b)}</div></div>'
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
            f'<div class="bullet-row"><div class="bdot" style="color:{bullet_color}">•</div><div>{esc(b)}</div></div>'
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
@page{{size: A4; margin: 0;}}
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{font-family:'Inter',sans-serif;font-size:11px;line-height:1.5;background:#fff;-webkit-print-color-adjust:exact;print-color-adjust:exact;width:210mm;min-height:297mm;color:#333;}}
.page{{width:100%;padding:40px 48px;}}
.header{{background:#1A1A2E;padding:24px 32px;border-radius:6px;margin-bottom:24px;}}
.header-main{{display:flex;align-items:center;gap:20px;}}
.initials{{width:56px;height:56px;border-radius:50%;background:#FF6B35;display:flex;align-items:center;justify-content:center;font-size:18px;font-weight:800;color:#fff;flex-shrink:0;}}
.header-name{{display:flex;flex-direction:column;}}
.name-first{{font-size:12px;color:#FF6B35;text-transform:uppercase;font-weight:600;}}
.name-last{{font-size:24px;font-weight:800;color:#fff;line-height:1.1;}}
.job-title{{font-size:11px;color:#B0B0CC;margin-top:4px;text-transform:uppercase;font-weight:600;}}
.contact-row{{display:flex;flex-wrap:wrap;gap:14px;margin-top:16px;padding-top:14px;border-top:1px solid #ffffff15;}}
.ci{{display:flex;align-items:center;gap:6px;font-size:10px;color:#A0A0BB;}}
.ci-ic{{font-size:11px;color:#FF6B35;font-weight:700;}}
.sec-head{{display:flex;align-items:center;gap:8px;margin:20px 0 10px;}}
.sec-bar{{width:3px;height:14px;background:#FF6B35;border-radius:2px;flex-shrink:0;}}
.sec-label{{font-size:10px;text-transform:uppercase;color:#1A1A2E;font-weight:800;}}
.summary-text{{font-size:11px;color:#444;line-height:1.7;margin-bottom:12px;}}
.exp-block{{margin-bottom:16px;padding-left:12px;border-left:2px solid #F0EDE8;}}
.exp-top{{display:flex;justify-content:space-between;align-items:baseline;}}
.exp-title{{font-size:12px;font-weight:700;color:#1A1A2E;}}
.exp-dates{{font-size:9.5px;color:#FF6B35;font-weight:600;}}
.exp-co{{font-size:10px;color:#555;margin-bottom:4px;font-weight:600;}}
.exp-loc{{color:#888;font-weight:400;}}
.bullet-row{{display:flex;gap:6px;margin-bottom:2px;font-size:10px;color:#444;}}
.bdot{{flex-shrink:0;font-size:10px;margin-top:1px;}}
.proj-block{{margin-bottom:14px;padding:10px 14px;border:1px solid #F0EDE8;border-radius:4px;}}
.proj-name{{font-size:11px;font-weight:700;color:#1A1A2E;margin-bottom:3px;}}
.proj-desc{{font-size:10px;color:#555;margin-bottom:4px;}}
.edu-block{{margin-bottom:10px;}}
.edu-degree{{font-size:11px;font-weight:700;color:#1A1A2E;}}
.edu-school{{font-size:10px;color:#555;}}
.edu-meta{{font-size:9px;color:#888;}}
.skills-section{{display:flex;flex-wrap:wrap;gap:12px;margin-bottom:12px;}}
.skill-cat{{font-size:9px;text-transform:uppercase;color:#FF6B35;font-weight:700;width:100%;margin-top:4px;}}
.skill-pills{{display:flex;flex-wrap:wrap;gap:4px;}}
.pill{{background:#F0EDE8;border:1px solid #FF6B3533;border-radius:2px;padding:2px 7px;font-size:9px;color:#1A1A2E;font-weight:600;}}
.bottom-sections{{display:flex;gap:32px;margin-top:12px;}}
.bottom-col{{flex:1;}}
.lang-item{{font-size:10px;color:#444;margin-bottom:3px;}}
.cert-item{{font-size:10px;color:#444;margin-bottom:3px;border-left:2px solid #FF6B35;padding-left:6px;}}
</style></head><body><div class="page">
<div class="header">
  <div class="header-main">
    <div class="initials">{esc(fn[:1])}{esc(ln[:1])}</div>
    <div class="header-name">
      <div class="name-first">{esc(fn)}</div>
      <div class="name-last">{esc(ln)}</div>
      {f'<div class="job-title">{esc(f["job_title"])}</div>' if f["job_title"] else ""}
    </div>
  </div>
  <div class="contact-row">{contact}</div>
</div>
<div class="main">
  {f'<div class="sec-head"><div class="sec-bar"></div><div class="sec-label">Profil</div></div><p class="summary-text">{esc(f["summary"])}</p>' if f["summary"] else ""}
  {f'<div class="sec-head"><div class="sec-bar"></div><div class="sec-label">Expériences</div></div>{exp_html}' if exp_html else ""}
  {f'<div class="sec-head"><div class="sec-bar"></div><div class="sec-label">Projets</div></div>{proj_html}' if proj_html else ""}
  {f'<div class="sec-head"><div class="sec-bar"></div><div class="sec-label">Formation</div></div>{edu_html}' if edu_html else ""}
  {f'<div class="sec-head"><div class="sec-bar"></div><div class="sec-label">Compétences</div></div><div class="skills-section">{f["skills_html"]}</div>' if f["skills_html"] else ""}
  <div class="bottom-sections">
    {f'<div class="bottom-col"><div class="sec-head"><div class="sec-bar"></div><div class="sec-label">Langues</div></div>{langs}</div>' if langs else ""}
    {f'<div class="bottom-col"><div class="sec-head"><div class="sec-bar"></div><div class="sec-label">Certifications</div></div>{certs}</div>' if certs else ""}
  </div>
</div></div></body></html>"""

# ── 2. Minimaliste ────────────────────────────────────────────────────────────

@register("minimaliste", "Minimaliste", "Blanc / Bleu", "#2563EB")
def build_minimaliste(cv_data: dict) -> str:
    f = _fields(cv_data)
    contact_str = " · ".join(filter(None, [
        f'Email: {esc(f["email"])}' if f["email"] else "",
        f'Tél: {esc(f["phone"])}' if f["phone"] else "",
        esc(f["location"]),
        f'LinkedIn: {esc(f["linkedin"])}' if f["linkedin"] else "",
        f'GitHub: {esc(f["github"])}' if f["github"] else ""
    ]))
    exp_html = _exp_blocks(f["experiences"], "#2563EB")
    proj_html = _proj_blocks(f["projects"], "#2563EB")
    edu_html = _edu_blocks(f["education"])
    langs = " · ".join(esc(l) for l in f["languages"])
    certs = " · ".join(esc(c) for c in f["certifications"])
    sec = lambda label: f'<div style="font-size:9px;text-transform:uppercase;color:#2563EB;font-weight:700;margin:18px 0 8px;border-bottom:2px solid #2563EB;padding-bottom:3px;">{label}</div>'
    return f"""<!DOCTYPE html><html lang="fr"><head><meta charset="utf-8"/>
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
@page{{size: A4; margin: 0;}}
*{{margin:0;padding:0;box-sizing:border-box;}} body{{font-family:'Inter',sans-serif;font-size:11px;background:#fff;color:#222;-webkit-print-color-adjust:exact;print-color-adjust:exact;width:210mm;min-height:297mm;}}
.page{{width:100%;min-height:100%;padding:48px 52px;}}
h1{{font-size:32px;font-weight:700;color:#111;letter-spacing:-1px;}} .subtitle{{font-size:13px;color:#2563EB;text-transform:uppercase;margin-top:4px;}}
.contact{{font-size:10px;color:#666;margin-top:10px;}} .summary-text{{font-size:11.5px;color:#444;line-height:1.75;}}
.exp-block,.proj-block{{margin-bottom:14px;}} .exp-top{{display:flex;justify-content:space-between;}} .exp-title{{font-size:12px;font-weight:700;}} .exp-dates{{font-size:9px;color:#2563EB;}}
.exp-co{{font-size:10px;color:#666;margin-bottom:4px;}} .exp-loc{{color:#AAA;}}
.bullet-row{{display:flex;gap:6px;font-size:10px;color:#555;margin-bottom:2px;}} .bdot{{flex-shrink:0;color:#2563EB;font-size:9px;margin-top:1px;}}
.proj-name{{font-size:11px;font-weight:700;}} .proj-desc{{font-size:10px;color:#666;}}
.edu-degree{{font-size:11px;font-weight:600;}} .edu-school{{font-size:10px;color:#666;}} .edu-meta{{font-size:9px;color:#AAA;}}
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
{f'{sec("Compétences")}{f["skills_html"]}' if f["skills_html"] else ""}
{f'{sec("Langues")}<p style="font-size:10px;color:#555;">{langs}</p>' if langs else ""}
{f'{sec("Certifications")}<p style="font-size:10px;color:#555;">{certs}</p>' if certs else ""}
</div></body></html>"""

@register("executive", "Executive", "Sombre / Émeraude", "#6EE7B7")
def build_executive(cv_data: dict) -> str:
    f = _fields(cv_data)
    contact = _contact_items(f, "#6EE7B7")
    exp_html = _exp_blocks(f["experiences"], "#6EE7B7")
    proj_html = _proj_blocks(f["projects"], "#6EE7B7")
    edu_html = _edu_blocks(f["education"])
    langs = "".join(f'<div class="lang-item">• {esc(l)}</div>' for l in f["languages"])
    certs = "".join(f'<div class="cert-item">{esc(c)}</div>' for c in f["certifications"])
    sec = lambda t: f'<div style="font-size:9px;text-transform:uppercase;color:#6EE7B7;margin:16px 0 8px;border-bottom:1px solid #6EE7B733;padding-bottom:4px;">{t}</div>'
    return f"""<!DOCTYPE html><html lang="fr"><head><meta charset="utf-8"/>
<style>
@page{{size: A4; margin: 0;}}
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{font-family:'Inter',sans-serif;font-size:11px;background:#0D1117;color:#E0E0FF;-webkit-print-color-adjust:exact;print-color-adjust:exact;width:210mm;min-height:297mm;line-height:1.5;}}
.page{{width:100%;padding:40px 48px;}}
.header{{background:#161B22;padding:24px 32px;border:1px solid #6EE7B722;border-radius:6px;margin-bottom:24px;}}
.hdr-name{{font-size:24px;font-weight:800;color:#fff;line-height:1.1;}}
.hdr-title{{font-size:11px;color:#6EE7B7;text-transform:uppercase;letter-spacing:1px;margin-top:4px;font-weight:600;}}
.contact-row{{display:flex;flex-wrap:wrap;gap:14px;margin-top:16px;padding-top:14px;border-top:1px solid #6EE7B715;}}
.ci{{display:flex;align-items:center;gap:6px;font-size:9.5px;color:#9090BB;}}
.ci-ic{{color:#6EE7B7;font-weight:700;}}
.summary-text{{font-size:11px;color:#B0B0CC;line-height:1.7;margin-bottom:12px;}}
.exp-block{{margin-bottom:16px;padding-left:12px;border-left:2px solid #1A2030;}}
.exp-top{{display:flex;justify-content:space-between;align-items:baseline;}}
.exp-title{{font-size:12px;font-weight:700;color:#fff;}}
.exp-dates{{font-size:9.5px;color:#6EE7B7;font-weight:600;}}
.exp-co{{font-size:10px;color:#6EE7B7;margin-bottom:4px;font-weight:600;}}
.exp-loc{{color:#506070;font-weight:400;}}
.bullet-row{{display:flex;gap:6px;margin-bottom:2px;font-size:10px;color:#A0A0CC;}}
.bdot{{flex-shrink:0;font-size:10px;margin-top:1px;}}
.proj-block{{margin-bottom:14px;padding:10px 14px;border:1px solid #1A2030;border-radius:4px;background:#161B22;}}
.proj-name{{font-size:11px;font-weight:700;color:#fff;margin-bottom:3px;}}
.proj-desc{{font-size:10px;color:#7070AA;margin-bottom:4px;}}
.edu-block{{margin-bottom:10px;}}
.edu-degree{{font-size:11px;font-weight:700;color:#fff;}}
.edu-school{{font-size:10px;color:#7070AA;}}
.edu-meta{{font-size:9px;color:#5050AA;}}
.skills-section{{display:flex;flex-wrap:wrap;gap:12px;margin-bottom:12px;}}
.skill-cat{{font-size:9px;text-transform:uppercase;color:#6EE7B7;font-weight:700;width:100%;margin-top:4px;}}
.pill{{background:#1A2030;border:1px solid #6EE7B733;border-radius:2px;padding:2px 7px;font-size:9px;color:#C0C0FF;font-weight:600;}}
.lang-item{{font-size:10px;color:#A0A0CC;margin-bottom:3px;}}
.cert-item{{font-size:10px;color:#A0A0CC;margin-bottom:3px;border-left:2px solid #6EE7B7;padding-left:6px;}}
</style></head><body><div class="page">
<div class="header">
  <div class="hdr-name">{esc(f["full_name"])}</div>
  {f'<div class="hdr-title">{esc(f["job_title"])}</div>' if f["job_title"] else ""}
  <div class="contact-row">{contact}</div>
</div>
<div class="main">
  {f'{sec("Profil")}<p class="summary-text">{esc(f["summary"])}</p>' if f["summary"] else ""}
  {f'{sec("Expériences")}{exp_html}' if exp_html else ""}
  {f'{sec("Projets")}{proj_html}' if proj_html else ""}
  {f'{sec("Formation")}{edu_html}' if edu_html else ""}
  {f'{sec("Compétences")}<div class="skills-section">{f["skills_html"]}</div>' if f["skills_html"] else ""}
  {f'{sec("Langues")}{langs}' if langs else ""}
  {f'{sec("Certifications")}{certs}' if certs else ""}
</div></div></body></html>"""

# ── 4–8: Créatif, Classique, Néon Tech, Scandinave, Timeline ──────────────────

@register("creatif", "Créatif", "Violet / Rose", "#EC4899")
def build_creatif(cv_data: dict) -> str:
    f = _fields(cv_data)
    contact = _contact_items(f, "#EC4899")
    exp_html = _exp_blocks(f["experiences"], "#EC4899")
    proj_html = _proj_blocks(f["projects"], "#EC4899")
    edu_html = _edu_blocks(f["education"])
    langs = "".join(f'<div class="lang-item">• {esc(l)}</div>' for l in f["languages"])
    certs = "".join(f'<div class="cert-item">{esc(c)}</div>' for c in f["certifications"])
    sec = lambda t: f'<div style="font-size:9px;text-transform:uppercase;color:#EC4899;margin:20px 0 10px;border-bottom:1px solid #EC489933;padding-bottom:4px;">{t}</div>'
    return f"""<!DOCTYPE html><html lang="fr"><head><meta charset="utf-8"/>
<style>
@page{{size: A4; margin: 0;}}
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@300;400;600;700;800&display=swap');
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{font-family:'Nunito',sans-serif;font-size:11px;background:#1A0A2E;color:#E0D0FF;-webkit-print-color-adjust:exact;print-color-adjust:exact;width:210mm;min-height:297mm;line-height:1.5;}}
.page{{width:100%;padding:40px 48px;}}
.header{{background:#0F0718;padding:24px 32px;border:1px solid #EC489922;border-radius:6px;margin-bottom:24px;}}
.hdr-name{{font-size:24px;font-weight:800;color:#fff;line-height:1.1;}}
.hdr-title{{font-size:11px;color:#EC4899;text-transform:uppercase;letter-spacing:1px;margin-top:4px;font-weight:600;}}
.contact-row{{display:flex;flex-wrap:wrap;gap:14px;margin-top:16px;padding-top:14px;border-top:1px solid #EC489915;}}
.ci{{display:flex;align-items:center;gap:6px;font-size:9.5px;color:#B090CC;}}
.ci-ic{{color:#EC4899;font-weight:700;}}
.summary-text{{font-size:11px;color:#C0A0E0;line-height:1.7;margin-bottom:12px;}}
.exp-block{{margin-bottom:16px;padding-left:12px;border-left:2px solid #25103A;}}
.exp-top{{display:flex;justify-content:space-between;align-items:baseline;}}
.exp-title{{font-size:12px;font-weight:700;color:#fff;}}
.exp-dates{{font-size:9.5px;color:#EC4899;font-weight:600;}}
.exp-co{{font-size:10px;color:#EC4899;margin-bottom:4px;font-weight:600;}}
.exp-loc{{color:#704080;font-weight:400;}}
.bullet-row{{display:flex;gap:6px;margin-bottom:2px;font-size:10px;color:#B0A0CC;}}
.bdot{{flex-shrink:0;font-size:10px;margin-top:1px;}}
.proj-block{{margin-bottom:14px;padding:10px 14px;border:1px solid #25103A;border-radius:4px;background:#0F0718;}}
.proj-name{{font-size:11px;font-weight:700;color:#fff;margin-bottom:3px;}}
.proj-desc{{font-size:10px;color:#9070AA;margin-bottom:4px;}}
.edu-block{{margin-bottom:10px;}}
.edu-degree{{font-size:11px;font-weight:700;color:#fff;}}
.edu-school{{font-size:10px;color:#9070AA;}}
.edu-meta{{font-size:9px;color:#704080;}}
.skills-section{{display:flex;flex-wrap:wrap;gap:12px;margin-bottom:12px;}}
.skill-cat{{font-size:9px;text-transform:uppercase;color:#EC4899;font-weight:700;width:100%;margin-top:4px;}}
.pill{{background:#25103A;border:1px solid #EC489933;border-radius:2px;padding:2px 7px;font-size:9px;color:#E0D0FF;font-weight:600;}}
.lang-item{{font-size:10px;color:#C0A0CC;margin-bottom:3px;}}
.cert-item{{font-size:10px;color:#C0A0CC;margin-bottom:3px;border-left:2px solid #EC4899;padding-left:6px;}}
</style></head><body><div class="page">
<div class="header">
  <div class="hdr-name">{esc(f["full_name"])}</div>
  {f'<div class="hdr-title">{esc(f["job_title"])}</div>' if f["job_title"] else ""}
  <div class="contact-row">{contact}</div>
</div>
<div class="main">
  {f'{sec("Profil")}<p class="summary-text">{esc(f["summary"])}</p>' if f["summary"] else ""}
  {f'{sec("Expériences")}{exp_html}' if exp_html else ""}
  {f'{sec("Projets")}{proj_html}' if proj_html else ""}
  {f'{sec("Formation")}{edu_html}' if edu_html else ""}
  {f'{sec("Compétences")}<div class="skills-section">{f["skills_html"]}</div>' if f["skills_html"] else ""}
  {f'{sec("Langues")}{langs}' if langs else ""}
  {f'{sec("Certifications")}{certs}' if certs else ""}
</div></div></body></html>"""

@register("classique", "Classique", "Noir & Blanc", "#1a1a1a")
def build_classique(cv_data: dict) -> str:
    f = _fields(cv_data)
    contact_str = " | ".join(filter(None, [
        f'Email: {esc(f["email"])}' if f["email"] else "",
        f'Tél: {esc(f["phone"])}' if f["phone"] else "",
        esc(f["location"]),
        f'LinkedIn: {esc(f["linkedin"])}' if f["linkedin"] else ""
    ]))
    exp_html = _exp_blocks(f["experiences"], "#1a1a1a")
    proj_html = _proj_blocks(f["projects"], "#1a1a1a")
    edu_html = _edu_blocks(f["education"])
    langs = " | ".join(esc(l) for l in f["languages"])
    certs = "".join(f'<div style="font-size:10px;color:#333;margin-bottom:3px;">• {esc(c)}</div>' for c in f["certifications"])
    sec = lambda t: f'<div style="font-size:9px;text-transform:uppercase;color:#1a1a1a;font-weight:700;margin:18px 0 6px;border-bottom:2px solid #1a1a1a;padding-bottom:3px;">{t}</div>'
    return f"""<!DOCTYPE html><html lang="fr"><head><meta charset="utf-8"/>
<style>
@page{{size: A4; margin: 0;}}
@import url('https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400;0,600;1,400&family=Inter:wght@400;600&display=swap');
*{{margin:0;padding:0;box-sizing:border-box;}} body{{font-family:'EB Garamond',serif;font-size:12px;background:#fff;color:#111;-webkit-print-color-adjust:exact;print-color-adjust:exact;width:210mm;min-height:297mm;}}
.page{{width:100%;padding:50px 60px;}}
.hdr{{text-align:center;margin-bottom:20px;border-bottom:2px solid #1a1a1a;padding-bottom:16px;}}
h1{{font-size:34px;font-weight:600;text-transform:uppercase;}}
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
    proj_html = _proj_blocks(f["projects"], "#00E5FF")
    edu_html = _edu_blocks(f["education"])
    langs = "".join(f'<div class="lang-item">• {esc(l)}</div>' for l in f["languages"])
    certs = "".join(f'<div class="cert-item">{esc(c)}</div>' for c in f["certifications"])
    fn_parts = f["full_name"].split(); fn = fn_parts[0]; ln = " ".join(fn_parts[1:])
    sec = lambda t: f'<div style="font-size:9px;text-transform:uppercase;color:#FF00A0;margin:20px 0 10px;border-bottom:1px solid #FF00A033;padding-bottom:4px;font-family:\'Share Tech Mono\',monospace;">{t}</div>'
    return f"""<!DOCTYPE html><html lang="fr"><head><meta charset="utf-8"/>
<style>
@page{{size: A4; margin: 0;}}
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Inter:wght@300;400;600;700;800&display=swap');
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{font-family:'Inter',sans-serif;font-size:11px;background:#0D0D1A;color:#E0E0FF;-webkit-print-color-adjust:exact;print-color-adjust:exact;width:210mm;min-height:297mm;line-height:1.5;}}
.page{{width:100%;padding:40px 48px;}}
.header{{background:#111128;padding:24px 32px;border:1px solid #00E5FF33;border-radius:6px;margin-bottom:24px;display:flex;flex-direction:column;gap:16px;}}
.header-main{{display:flex;align-items:center;gap:20px;}}
.avatar{{width:56px;height:56px;border-radius:50%;border:2px solid #00E5FF;box-shadow:0 0 14px #00E5FF55;display:flex;align-items:center;justify-content:center;background:#1A1A35;font-family:'Share Tech Mono',monospace;font-size:18px;color:#00E5FF;flex-shrink:0;}}
.header-name{{display:flex;flex-direction:column;}}
.nm-first{{font-size:11px;color:#00E5FF;letter-spacing:2px;text-transform:uppercase;font-family:'Share Tech Mono',monospace;}}
.nm-last{{font-size:24px;font-weight:800;color:#fff;line-height:1.1;}}
.nm-title{{font-size:11px;color:#FF00A0;letter-spacing:1px;text-transform:uppercase;font-family:'Share Tech Mono',monospace;margin-top:4px;font-weight:600;}}
.contact-row{{display:flex;flex-wrap:wrap;gap:14px;padding-top:14px;border-top:1px solid #00E5FF15;}}
.ci{{display:flex;align-items:center;gap:6px;font-size:9.5px;color:#8080AA;}}
.ci-ic{{color:#00E5FF;font-weight:700;font-family:'Share Tech Mono',monospace;}}
.summary-text{{font-size:11px;color:#C0C0E0;line-height:1.7;margin-bottom:12px;}}
.exp-block{{margin-bottom:16px;padding-left:12px;border-left:2px solid #1A1A3A;}}
.exp-top{{display:flex;justify-content:space-between;align-items:baseline;}}
.exp-title{{font-size:12px;font-weight:700;color:#fff;}}
.exp-dates{{font-size:9.5px;color:#00E5FF;font-family:'Share Tech Mono',monospace;}}
.exp-co{{font-size:10px;color:#FF00A0;margin-bottom:4px;font-weight:600;}}
.exp-loc{{color:#6060AA;font-weight:400;}}
.bullet-row{{display:flex;gap:6px;margin-bottom:2px;font-size:10px;color:#C0C0E0;}}
.bdot{{flex-shrink:0;font-size:10px;margin-top:1px;}}
.proj-block{{margin-bottom:14px;padding:10px 14px;border:1px solid #1A1A3A;border-radius:4px;background:#111128;}}
.proj-name{{font-size:11px;font-weight:700;color:#fff;margin-bottom:3px;}}
.proj-desc{{font-size:10px;color:#8080AA;margin-bottom:4px;}}
.edu-block{{margin-bottom:10px;}}
.edu-degree{{font-size:11px;font-weight:700;color:#fff;}}
.edu-school{{font-size:10px;color:#6060AA;}}
.edu-meta{{font-size:9px;color:#404080;}}
.skills-section{{display:flex;flex-wrap:wrap;gap:12px;margin-bottom:12px;}}
.skill-cat{{font-size:9px;text-transform:uppercase;color:#00E5FF;font-weight:700;width:100%;margin-top:4px;font-family:'Share Tech Mono',monospace;}}
.pill{{background:#1A1A3A;border:1px solid #00E5FF33;border-radius:2px;padding:2px 7px;font-size:9px;color:#C0C0FF;font-weight:600;}}
.lang-item{{font-size:10px;color:#8080CC;margin-bottom:3px;}}
.cert-item{{font-size:10px;color:#8080CC;margin-bottom:3px;border-left:2px solid #FF00A0;padding-left:6px;}}
</style></head><body><div class="page">
<div class="header">
  <div class="header-main">
    <div class="avatar">{esc(fn[:1])}{esc(ln[:1])}</div>
    <div class="header-name">
      <div class="nm-first">{esc(fn)}</div>
      <div class="nm-last">{esc(ln)}</div>
      {f'<div class="nm-title">{esc(f["job_title"])}</div>' if f["job_title"] else ""}
    </div>
  </div>
  <div class="contact-row">{contact}</div>
</div>
<div class="main">
  {f'{sec("Profil")}<p class="summary-text">{esc(f["summary"])}</p>' if f["summary"] else ""}
  {f'{sec("Expériences")}{exp_html}' if exp_html else ""}
  {f'{sec("Projets")}{proj_html}' if proj_html else ""}
  {f'{sec("Formation")}{edu_html}' if edu_html else ""}
  {f'{sec("Compétences")}<div class="skills-section">{f["skills_html"]}</div>' if f["skills_html"] else ""}
  {f'{sec("Langues")}{langs}' if langs else ""}
  {f'{sec("Certifications")}{certs}' if certs else ""}
</div></div></body></html>"""

@register("scandinave", "Scandinave", "Épuré / Nordic", "#4A7C59")
def build_scandinave(cv_data: dict) -> str:
    f = _fields(cv_data)
    contact_str = " · ".join(filter(None, [
        f'Email: {esc(f["email"])}' if f["email"] else "",
        f'Tél: {esc(f["phone"])}' if f["phone"] else "",
        esc(f["location"]),
        f'LinkedIn: {esc(f["linkedin"])}' if f["linkedin"] else ""
    ]))
    sec = lambda t: f'<div style="display:flex;align-items:center;gap:10px;margin:20px 0 10px;"><span style="font-size:9px;text-transform:uppercase;font-weight:700;color:#1A1A1A;white-space:nowrap;">{t}</span><div style="flex:1;height:1px;background:#ddd;"></div></div>'
    exp_out = ""
    for e in f["experiences"]:
        dates = " – ".join(filter(None,[e.get("start_date",""),e.get("end_date","")]))
        bullets = "".join(f'<li style="padding-left:10px;margin-bottom:2px;font-size:11px;color:#555;position:relative;list-style:none;"><span style="position:absolute;left:0;color:#4A7C59;font-weight:700;">•</span>{esc(b)}</li>' for b in (e.get("bullets") or []))
        exp_out += f'<div style="margin-bottom:14px;"><div style="display:flex;justify-content:space-between;align-items:baseline;"><div><span style="font-size:12px;font-weight:600;">{esc(e.get("title",""))}</span><span style="color:#BBB;"> — </span><span style="font-size:11px;color:#4A7C59;">{esc(e.get("company",""))}</span></div><span style="font-size:10px;color:#999;">{esc(dates)}</span></div><ul style="padding:0;margin-top:4px;">{bullets}</ul></div>'
    edu_out = "".join(f'<div style="display:flex;justify-content:space-between;margin-bottom:7px;"><span style="font-size:11px;font-weight:600;">{esc(e.get("degree",""))}</span><span style="font-size:11px;color:#888;font-style:italic;">{esc(e.get("institution") or e.get("school",""))}</span></div>' for e in f["education"])
    langs = " – ".join(esc(l) for l in f["languages"])
    certs = "".join(f'<div style="font-size:10px;color:#555;border-left:2px solid #4A7C59;padding-left:6px;margin-bottom:4px;">{esc(c)}</div>' for c in f["certifications"])
    return f"""<!DOCTYPE html><html lang="fr"><head><meta charset="utf-8"/>
<style>
@page{{size: A4; margin: 0;}}
@import url('https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,400;0,600;1,400&family=DM+Sans:wght@300;400;500;600&display=swap');
*{{margin:0;padding:0;box-sizing:border-box;}} body{{font-family:'DM Sans',sans-serif;background:#FAFAF7;color:#2B2B2B;font-size:11px;line-height:1.6;-webkit-print-color-adjust:exact;print-color-adjust:exact;width:210mm;min-height:297mm;}}
.page{{width:100%;padding:52px 60px;}}
h1{{font-family:'Lora',serif;font-size:36px;font-weight:600;color:#1A1A1A;}}
.hdr-title{{font-size:13px;font-weight:300;color:#4A7C59;text-transform:uppercase;margin-top:4px;}}
.contact{{font-size:10px;color:#888;margin-top:10px;}}
.summary-text{{font-size:11.5px;color:#444;line-height:1.8;font-style:italic;font-family:'Lora',serif;}}
.skill-cat{{font-size:9px;text-transform:uppercase;color:#4A7C59;margin:8px 0 4px;font-weight:600;}}
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
    contact = _contact_items(f, "#E85D4A")
    edu_html = _edu_blocks(f["education"])
    langs = "".join(f'<div class="lang-item">• {esc(l)}</div>' for l in f["languages"])
    certs = "".join(f'<div class="cert-item">{esc(c)}</div>' for c in f["certifications"])
    
    tl_items = []
    for e in f["experiences"]:
        dates = " – ".join(filter(None,[e.get("start_date",""),e.get("end_date","")]))
        bullets = "".join(f'<div class="bullet-row"><div class="bdot" style="color:#E85D4A">•</div><div>{esc(b)}</div></div>' for b in (e.get("bullets") or []))
        tl_items.append({"type":"exp","title":e.get("title",""),"sub":e.get("company",""),"dates":dates,"bullets":bullets})
    for p in f["projects"]:
        bullets = "".join(f'<div class="bullet-row"><div class="bdot" style="color:#E85D4A">•</div><div>{esc(b)}</div></div>' for b in (p.get("bullets") or []))
        desc = p.get("description") or ""
        tl_items.append({"type":"proj","title":p.get("name",""),"sub":"","dates":"","desc":desc,"bullets":bullets})
        
    tl_html = ""
    for item in tl_items:
        icon = "●" if item["type"] == "exp" else "★"
        tl_html += f"""
        <div class="tl-card">
          <div class="tl-dot">{icon}</div>
          {f'<div class="tl-dates">{esc(item["dates"])}</div>' if item["dates"] else ""}
          <div class="tl-title">{esc(item["title"])}</div>
          {f'<div class="tl-sub">{esc(item["sub"])}</div>' if item["sub"] else ""}
          {f'<div class="tl-desc">{esc(item.get("desc",""))}</div>' if item.get("desc") else ""}
          {item["bullets"]}
        </div>
        """
        
    sec = lambda t: f'<div style="font-size:9px;text-transform:uppercase;color:#E85D4A;margin:20px 0 10px;border-bottom:1px solid #E85D4A33;padding-bottom:4px;font-weight:700;">{t}</div>'
    
    return f"""<!DOCTYPE html><html lang="fr"><head><meta charset="utf-8"/>
<style>
@page{{size: A4; margin: 0;}}
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@300;400;600;700;800&family=Playfair+Display:wght@700&display=swap');
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{font-family:'Nunito',sans-serif;background:#F9F5F0;color:#2D2D2D;font-size:11px;line-height:1.5;-webkit-print-color-adjust:exact;print-color-adjust:exact;width:210mm;min-height:297mm;}}
.page{{width:100%;padding:40px 48px;}}
.header{{background:#2D2D2D;padding:24px 32px;border-radius:6px;margin-bottom:24px;color:#fff;}}
.hdr-name{{font-family:'Playfair Display',serif;font-size:26px;color:#fff;line-height:1.1;}}
.hdr-title{{font-size:11px;color:#E85D4A;text-transform:uppercase;letter-spacing:1px;margin-top:4px;font-weight:600;}}
.contact-row{{display:flex;flex-wrap:wrap;gap:14px;margin-top:16px;padding-top:14px;border-top:1px solid #ffffff15;}}
.ci{{display:flex;align-items:center;gap:6px;font-size:9.5px;color:#BBBBBB;}}
.ci-ic{{color:#E85D4A;font-weight:700;}}
.summary-text{{font-size:11.5px;color:#555;line-height:1.75;font-style:italic;margin-bottom:12px;padding-left:12px;border-left:3px solid #E85D4A;}}
.tl-container{{position:relative;border-left:2px solid #E85D4A33;margin-left:10px;padding-left:24px;margin-bottom:16px;}}
.tl-card{{position:relative;margin-bottom:20px;background:#fff;border-radius:6px;padding:12px 16px;box-shadow:0 2px 8px rgba(0,0,0,0.04);}}
.tl-dot{{position:absolute;left:-31px;top:12px;width:14px;height:14px;border-radius:50%;background:#E85D4A;color:#fff;display:flex;align-items:center;justify-content:center;font-size:8px;font-weight:800;}}
.tl-dates{{font-size:9.5px;color:#E85D4A;font-weight:700;margin-bottom:3px;}}
.tl-title{{font-size:12px;font-weight:700;color:#2D2D2D;}}
.tl-sub{{font-size:10px;color:#888;margin-bottom:4px;font-weight:600;}}
.tl-desc{{font-size:10px;color:#666;margin-bottom:4px;}}
.bullet-row{{display:flex;gap:6px;margin-bottom:2px;font-size:10px;color:#555;}}
.bdot{{flex-shrink:0;font-size:10px;margin-top:1px;}}
.edu-block{{margin-bottom:10px;}}
.edu-degree{{font-size:11px;font-weight:700;color:#2D2D2D;}}
.edu-school{{font-size:10px;color:#666;}}
.edu-meta{{font-size:9px;color:#888;}}
.skills-section{{display:flex;flex-wrap:wrap;gap:12px;margin-bottom:12px;}}
.skill-cat{{font-size:9px;text-transform:uppercase;color:#E85D4A;font-weight:700;width:100%;margin-top:4px;}}
.pill{{background:#fff;border:1px solid #E85D4A33;border-radius:2px;padding:2px 7px;font-size:9px;color:#555;font-weight:600;}}
.lang-item{{font-size:10px;color:#555;margin-bottom:3px;}}
.cert-item{{font-size:10px;color:#555;margin-bottom:3px;border-left:2px solid #E85D4A;padding-left:6px;}}
</style></head><body><div class="page">
<div class="header">
  <div class="hdr-name">{esc(f["full_name"])}</div>
  {f'<div class="hdr-title">{esc(f["job_title"])}</div>' if f["job_title"] else ""}
  <div class="contact-row">{contact}</div>
</div>
<div class="main">
  {f'{sec("Profil")}<p class="summary-text">{esc(f["summary"])}</p>' if f["summary"] else ""}
  {f'{sec("Parcours")}<div class="tl-container">{tl_html}</div>' if tl_html else ""}
  {f'{sec("Formation")}{edu_html}' if edu_html else ""}
  {f'{sec("Compétences")}<div class="skills-section">{f["skills_html"]}</div>' if f["skills_html"] else ""}
  {f'{sec("Langues")}{langs}' if langs else ""}
  {f'{sec("Certifications")}{certs}' if certs else ""}
</div></div></body></html>"""


def build_html(template_id: str, cv_data: dict) -> str | None:
    """Returns HTML string for the given template_id, or None if not found."""
    entry = TEMPLATES.get(template_id)
    if entry:
        return entry["build"](cv_data)
    return None
