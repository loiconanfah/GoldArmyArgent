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
body{{font-family:'Inter',sans-serif;font-size:9.5px;line-height:1.45;background:#fff;-webkit-print-color-adjust:exact;print-color-adjust:exact;width:210mm;min-height:297mm;color:#333;}}
.page-table{{width:100%;border-collapse:collapse;}}
.header-space{{height:35px;}}
.footer-space{{height:35px;}}
.page{{width:100%;padding:0 44px;}}
.header{{background:#111827;padding:20px 24px;border-radius:6px;margin-bottom:16px;}}
.header-main{{display:flex;align-items:center;gap:16px;}}
.initials{{width:48px;height:48px;border-radius:50%;background:#FF6B35;display:flex;align-items:center;justify-content:center;font-size:16px;font-weight:800;color:#fff;flex-shrink:0;}}
.header-name{{display:flex;flex-direction:column;}}
.name-first{{font-size:10px;color:#FF6B35;text-transform:uppercase;font-weight:600;letter-spacing:1px;}}
.name-last{{font-size:22px;font-weight:800;color:#fff;line-height:1.1;}}
.job-title{{font-size:10px;color:#9CA3AF;margin-top:2px;text-transform:uppercase;font-weight:600;letter-spacing:1px;}}
.contact-row{{display:flex;flex-wrap:wrap;gap:12px;margin-top:12px;padding-top:12px;border-top:1px solid #ffffff15;}}
.ci{{display:flex;align-items:center;gap:4px;font-size:9px;color:#9CA3AF;}}
.ci-ic{{font-size:10px;color:#FF6B35;font-weight:700;}}
.sec-head{{display:flex;align-items:center;gap:6px;margin:14px 0 8px;page-break-after:avoid;break-after:avoid;}}
.sec-bar{{width:3px;height:12px;background:#FF6B35;border-radius:2px;flex-shrink:0;}}
.sec-label{{font-size:10px;text-transform:uppercase;color:#111827;font-weight:800;letter-spacing:0.5px;}}
.summary-text{{font-size:9.5px;color:#4B5563;line-height:1.6;margin-bottom:8px;}}
.exp-block{{margin-bottom:10px;padding-left:10px;border-left:2px solid #E5E7EB;page-break-inside:avoid;break-inside:avoid;}}
.exp-top{{display:flex;justify-content:space-between;align-items:baseline;}}
.exp-title{{font-size:10.5px;font-weight:700;color:#111827;}}
.exp-dates{{font-size:9px;color:#FF6B35;font-weight:600;}}
.exp-co{{font-size:9.5px;color:#4B5563;margin-bottom:3px;font-weight:600;}}
.exp-loc{{color:#9CA3AF;font-weight:400;}}
.bullet-row{{display:flex;gap:5px;margin-bottom:1.5px;font-size:9px;color:#4B5563;}}
.bdot{{flex-shrink:0;font-size:9px;margin-top:0.5px;}}
.proj-block{{margin-bottom:10px;padding:8px 12px;border:1px solid #E5E7EB;border-radius:4px;page-break-inside:avoid;break-inside:avoid;}}
.proj-name{{font-size:10px;font-weight:700;color:#111827;margin-bottom:2px;}}
.proj-desc{{font-size:9px;color:#4B5563;margin-bottom:3px;}}
.edu-block{{margin-bottom:8px;page-break-inside:avoid;break-inside:avoid;}}
.edu-degree{{font-size:10px;font-weight:700;color:#111827;}}
.edu-school{{font-size:9.5px;color:#4B5563;}}
.edu-meta{{font-size:8.5px;color:#9CA3AF;}}
.skills-section{{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:8px;page-break-inside:avoid;break-inside:avoid;}}
.skill-cat{{font-size:8.5px;text-transform:uppercase;color:#FF6B35;font-weight:700;width:100%;margin-top:2px;}}
.skill-pills{{display:flex;flex-wrap:wrap;gap:3px;}}
.pill{{background:#F3F4F6;border:1px solid #FF6B3522;border-radius:2px;padding:1px 5px;font-size:8.5px;color:#111827;font-weight:600;}}
.bottom-sections{{display:flex;gap:24px;margin-top:8px;page-break-inside:avoid;break-inside:avoid;}}
.bottom-col{{flex:1;}}
.lang-item{{font-size:9.5px;color:#4B5563;margin-bottom:2px;page-break-inside:avoid;break-inside:avoid;}}
.cert-item{{font-size:9.5px;color:#4B5563;margin-bottom:2px;border-left:2px solid #FF6B35;padding-left:5px;page-break-inside:avoid;break-inside:avoid;}}
</style></head><body>
<table class="page-table">
  <thead><tr><td><div class="header-space"></div></td></tr></thead>
  <tbody><tr><td>
    <div class="page">
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
      </div>
    </div>
  </td></tr></tbody>
  <tfoot><tr><td><div class="footer-space"></div></td></tr></tfoot>
</table>
</body></html>"""

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
    sec = lambda label: f'<div class="sec-head" style="font-size:10px;text-transform:uppercase;color:#2563EB;font-weight:700;margin:14px 0 8px;border-bottom:1.5px solid #2563EB;padding-bottom:2px;page-break-after:avoid;break-after:avoid;">{label}</div>'
    return f"""<!DOCTYPE html><html lang="fr"><head><meta charset="utf-8"/>
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
@page{{size: A4; margin: 0;}}
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{font-family:'Inter',sans-serif;font-size:9.5px;line-height:1.45;background:#fff;color:#1F2937;-webkit-print-color-adjust:exact;print-color-adjust:exact;width:210mm;min-height:297mm;}}
.page-table{{width:100%;border-collapse:collapse;}}
.header-space{{height:35px;}}
.footer-space{{height:35px;}}
.page{{width:100%;padding:0 48px;}}
h1{{font-size:24px;font-weight:700;color:#111827;letter-spacing:-0.5px;}}
.subtitle{{font-size:11px;color:#2563EB;text-transform:uppercase;margin-top:2px;font-weight:600;letter-spacing:0.5px;}}
.contact{{font-size:9px;color:#4B5563;margin-top:6px;}}
.summary-text{{font-size:9.5px;color:#4B5563;line-height:1.6;}}
.exp-block,.proj-block{{margin-bottom:10px;page-break-inside:avoid;break-inside:avoid;}}
.exp-top{{display:flex;justify-content:space-between;}}
.exp-title{{font-size:10.5px;font-weight:700;color:#111827;}}
.exp-dates{{font-size:9px;color:#2563EB;font-weight:600;}}
.exp-co{{font-size:9.5px;color:#4B5563;margin-bottom:3px;font-weight:600;}}
.exp-loc{{color:#9CA3AF;}}
.bullet-row{{display:flex;gap:5px;font-size:9px;color:#4B5563;margin-bottom:1.5px;}}
.bdot{{flex-shrink:0;color:#2563EB;font-size:9px;margin-top:0.5px;}}
.proj-name{{font-size:10px;font-weight:700;color:#111827;}}
.proj-desc{{font-size:9px;color:#4B5563;}}
.edu-block{{margin-bottom:8px;page-break-inside:avoid;break-inside:avoid;}}
.edu-degree{{font-size:10px;font-weight:700;color:#111827;}}
.edu-school{{font-size:9.5px;color:#4B5563;}}
.edu-meta{{font-size:8.5px;color:#9CA3AF;}}
.skill-cat{{font-size:8.5px;text-transform:uppercase;color:#2563EB;font-weight:700;margin:4px 0 2px;}}
.skill-pills{{display:flex;flex-wrap:wrap;gap:3px;}}
.pill{{border:1px solid #E5E7EB;border-radius:2px;padding:1px 5px;font-size:8.5px;color:#374151;background:#F9FAFB;}}
.skills-section{{page-break-inside:avoid;break-inside:avoid;}}
</style></head><body>
<table class="page-table">
  <thead><tr><td><div class="header-space"></div></td></tr></thead>
  <tbody><tr><td>
    <div class="page">
      <h1>{esc(f["full_name"])}</h1>
      {f'<div class="subtitle">{esc(f["job_title"])}</div>' if f["job_title"] else ""}
      {f'<div class="contact">{contact_str}</div>' if contact_str else ""}
      {f'{sec("Profil")}<p class="summary-text">{esc(f["summary"])}</p>' if f["summary"] else ""}
      {f'{sec("Expériences")}{exp_html}' if exp_html else ""}
      {f'{sec("Projets")}{proj_html}' if proj_html else ""}
      {f'{sec("Formation")}{edu_html}' if edu_html else ""}
      {f'{sec("Compétences")}<div class="skills-section">{f["skills_html"]}</div>' if f["skills_html"] else ""}
      {f'{sec("Langues")}<p style="font-size:9.5px;color:#4B5563;">{langs}</p>' if langs else ""}
      {f'{sec("Certifications")}<p style="font-size:9.5px;color:#4B5563;">{certs}</p>' if certs else ""}
    </div>
  </td></tr></tbody>
  <tfoot><tr><td><div class="footer-space"></div></td></tr></tfoot>
</table>
</body></html>"""

# ── 3. Executive ──────────────────────────────────────────────────────────────

@register("executive", "Executive", "Sombre / Émeraude", "#6EE7B7")
def build_executive(cv_data: dict) -> str:
    f = _fields(cv_data)
    contact = _contact_items(f, "#10B981")
    exp_html = _exp_blocks(f["experiences"], "#10B981")
    proj_html = _proj_blocks(f["projects"], "#10B981")
    edu_html = _edu_blocks(f["education"])
    langs = "".join(f'<div class="lang-item">• {esc(l)}</div>' for l in f["languages"])
    certs = "".join(f'<div class="cert-item">{esc(c)}</div>' for c in f["certifications"])
    sec = lambda t: f'<div class="sec-head" style="font-size:10px;text-transform:uppercase;color:#10B981;margin:14px 0 8px;border-bottom:1px solid #10B98133;padding-bottom:3px;page-break-after:avoid;break-after:avoid;font-weight:700;letter-spacing:0.5px;">{t}</div>'
    return f"""<!DOCTYPE html><html lang="fr"><head><meta charset="utf-8"/>
<style>
@page{{size: A4; margin: 0;}}
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{font-family:'Inter',sans-serif;font-size:9.5px;background:#0F172A;color:#E2E8F0;-webkit-print-color-adjust:exact;print-color-adjust:exact;width:210mm;min-height:297mm;line-height:1.45;}}
.page-table{{width:100%;border-collapse:collapse;}}
.header-space{{height:35px;}}
.footer-space{{height:35px;}}
.page{{width:100%;padding:0 44px;}}
.header{{background:#1E293B;padding:20px 24px;border:1px solid #10B98133;border-radius:6px;margin-bottom:16px;}}
.hdr-name{{font-size:22px;font-weight:800;color:#fff;line-height:1.1;}}
.hdr-title{{font-size:10.5px;color:#10B981;text-transform:uppercase;letter-spacing:0.5px;margin-top:2px;font-weight:600;}}
.contact-row{{display:flex;flex-wrap:wrap;gap:12px;margin-top:12px;padding-top:12px;border-top:1px solid #10B98115;}}
.ci{{display:flex;align-items:center;gap:4px;font-size:9px;color:#94A3B8;}}
.ci-ic{{color:#10B981;font-weight:700;}}
.summary-text{{font-size:9.5px;color:#94A3B8;line-height:1.6;margin-bottom:8px;}}
.exp-block{{margin-bottom:10px;padding-left:10px;border-left:2px solid #1E293B;page-break-inside:avoid;break-inside:avoid;}}
.exp-top{{display:flex;justify-content:space-between;align-items:baseline;}}
.exp-title{{font-size:10.5px;font-weight:700;color:#fff;}}
.exp-dates{{font-size:9px;color:#10B981;font-weight:600;}}
.exp-co{{font-size:9.5px;color:#10B981;margin-bottom:3px;font-weight:600;}}
.exp-loc{{color:#64748B;font-weight:400;}}
.bullet-row{{display:flex;gap:5px;margin-bottom:1.5px;font-size:9px;color:#94A3B8;}}
.bdot{{flex-shrink:0;font-size:9px;margin-top:0.5px;}}
.proj-block{{margin-bottom:10px;padding:8px 12px;border:1px solid #1E293B;border-radius:4px;background:#1E293B;page-break-inside:avoid;break-inside:avoid;}}
.proj-name{{font-size:10px;font-weight:700;color:#fff;margin-bottom:2px;}}
.proj-desc{{font-size:9px;color:#94A3B8;margin-bottom:3px;}}
.edu-block{{margin-bottom:8px;page-break-inside:avoid;break-inside:avoid;}}
.edu-degree{{font-size:10px;font-weight:700;color:#fff;}}
.edu-school{{font-size:9.5px;color:#94A3B8;}}
.edu-meta{{font-size:8.5px;color:#64748B;}}
.skills-section{{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:8px;page-break-inside:avoid;break-inside:avoid;}}
.skill-cat{{font-size:8.5px;text-transform:uppercase;color:#10B981;font-weight:700;width:100%;margin-top:2px;}}
.pill{{background:#1E293B;border:1px solid #10B98133;border-radius:2px;padding:1px 5px;font-size:8.5px;color:#E2E8F0;font-weight:600;}}
.lang-item{{font-size:9.5px;color:#94A3B8;margin-bottom:2px;page-break-inside:avoid;break-inside:avoid;}}
.cert-item{{font-size:9.5px;color:#94A3B8;margin-bottom:2px;border-left:2px solid #10B981;padding-left:5px;page-break-inside:avoid;break-inside:avoid;}}
</style></head><body>
<table class="page-table">
  <thead><tr><td><div class="header-space"></div></td></tr></thead>
  <tbody><tr><td>
    <div class="page">
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
      </div>
    </div>
  </td></tr></tbody>
  <tfoot><tr><td><div class="footer-space"></div></td></tr></tfoot>
</table>
</body></html>"""

# ── 4. Créatif ────────────────────────────────────────────────────────────────

@register("creatif", "Créatif", "Violet / Rose", "#EC4899")
def build_creatif(cv_data: dict) -> str:
    f = _fields(cv_data)
    contact = _contact_items(f, "#EC4899")
    exp_html = _exp_blocks(f["experiences"], "#EC4899")
    proj_html = _proj_blocks(f["projects"], "#EC4899")
    edu_html = _edu_blocks(f["education"])
    langs = "".join(f'<div class="lang-item">• {esc(l)}</div>' for l in f["languages"])
    certs = "".join(f'<div class="cert-item">{esc(c)}</div>' for c in f["certifications"])
    sec = lambda t: f'<div class="sec-head" style="font-size:10px;text-transform:uppercase;color:#EC4899;margin:14px 0 8px;border-bottom:1px solid #EC489933;padding-bottom:3px;page-break-after:avoid;break-after:avoid;font-weight:700;letter-spacing:0.5px;">{t}</div>'
    return f"""<!DOCTYPE html><html lang="fr"><head><meta charset="utf-8"/>
<style>
@page{{size: A4; margin: 0;}}
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@300;400;600;700;800&display=swap');
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{font-family:'Nunito',sans-serif;font-size:9.5px;background:#18181B;color:#F4F4F5;-webkit-print-color-adjust:exact;print-color-adjust:exact;width:210mm;min-height:297mm;line-height:1.45;}}
.page-table{{width:100%;border-collapse:collapse;}}
.header-space{{height:35px;}}
.footer-space{{height:35px;}}
.page{{width:100%;padding:0 44px;}}
.header{{background:linear-gradient(135deg, #4F46E5 0%, #EC4899 100%);padding:20px 24px;border-radius:6px;margin-bottom:16px;}}
.hdr-name{{font-size:22px;font-weight:800;color:#fff;line-height:1.1;}}
.hdr-title{{font-size:10.5px;color:#fff;text-transform:uppercase;letter-spacing:0.5px;margin-top:2px;font-weight:600;opacity:0.9;}}
.contact-row{{display:flex;flex-wrap:wrap;gap:12px;margin-top:12px;padding-top:12px;border-top:1px solid #ffffff20;}}
.ci{{display:flex;align-items:center;gap:4px;font-size:9px;color:#fff;opacity:0.8;}}
.ci-ic{{color:#fff;font-weight:700;}}
.summary-text{{font-size:9.5px;color:#D4D4D8;line-height:1.6;margin-bottom:8px;}}
.exp-block{{margin-bottom:10px;padding-left:10px;border-left:2px solid #27272A;page-break-inside:avoid;break-inside:avoid;}}
.exp-top{{display:flex;justify-content:space-between;align-items:baseline;}}
.exp-title{{font-size:10.5px;font-weight:700;color:#fff;}}
.exp-dates{{font-size:9px;color:#EC4899;font-weight:600;}}
.exp-co{{font-size:9.5px;color:#EC4899;margin-bottom:3px;font-weight:600;}}
.exp-loc{{color:#71717A;font-weight:400;}}
.bullet-row{{display:flex;gap:5px;margin-bottom:1.5px;font-size:9px;color:#D4D4D8;}}
.bdot{{flex-shrink:0;font-size:9px;margin-top:0.5px;}}
.proj-block{{margin-bottom:10px;padding:8px 12px;border:1px solid #27272A;border-radius:4px;background:#27272A;page-break-inside:avoid;break-inside:avoid;}}
.proj-name{{font-size:10px;font-weight:700;color:#fff;margin-bottom:2px;}}
.proj-desc{{font-size:9px;color:#A1A1AA;margin-bottom:4px;}}
.edu-block{{margin-bottom:8px;page-break-inside:avoid;break-inside:avoid;}}
.edu-degree{{font-size:10px;font-weight:700;color:#fff;}}
.edu-school{{font-size:9.5px;color:#A1A1AA;}}
.edu-meta{{font-size:8.5px;color:#71717A;}}
.skills-section{{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:8px;page-break-inside:avoid;break-inside:avoid;}}
.skill-cat{{font-size:8.5px;text-transform:uppercase;color:#EC4899;font-weight:700;width:100%;margin-top:2px;}}
.pill{{background:#27272A;border:1px solid #EC489933;border-radius:2px;padding:1px 5px;font-size:8.5px;color:#F4F4F5;font-weight:600;}}
.lang-item{{font-size:9.5px;color:#D4D4D8;margin-bottom:2px;page-break-inside:avoid;break-inside:avoid;}}
.cert-item{{font-size:9.5px;color:#D4D4D8;margin-bottom:2px;border-left:2px solid #EC4899;padding-left:5px;page-break-inside:avoid;break-inside:avoid;}}
</style></head><body>
<table class="page-table">
  <thead><tr><td><div class="header-space"></div></td></tr></thead>
  <tbody><tr><td>
    <div class="page">
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
      </div>
    </div>
  </td></tr></tbody>
  <tfoot><tr><td><div class="footer-space"></div></td></tr></tfoot>
</table>
</body></html>"""

# ── 5. Classique ──────────────────────────────────────────────────────────────

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
    certs = "".join(f'<div style="font-size:9.5px;color:#333;margin-bottom:2px;page-break-inside:avoid;break-inside:avoid;">• {esc(c)}</div>' for c in f["certifications"])
    sec = lambda t: f'<div class="sec-head" style="font-size:9.5px;text-transform:uppercase;color:#1a1a1a;font-weight:700;margin:14px 0 6px;border-bottom:1.5px solid #1a1a1a;padding-bottom:2px;page-break-after:avoid;break-after:avoid;">{t}</div>'
    return f"""<!DOCTYPE html><html lang="fr"><head><meta charset="utf-8"/>
<style>
@page{{size: A4; margin: 0;}}
@import url('https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400;0,600;1,400&family=Inter:wght@400;600&display=swap');
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{font-family:'EB Garamond',serif;font-size:10.5px;background:#fff;color:#111;-webkit-print-color-adjust:exact;print-color-adjust:exact;width:210mm;min-height:297mm;line-height:1.45;}}
.page-table{{width:100%;border-collapse:collapse;}}
.header-space{{height:40px;}}
.footer-space{{height:40px;}}
.page{{width:100%;padding:0 52px;}}
.hdr{{text-align:center;margin-bottom:16px;border-bottom:1.5px solid #1a1a1a;padding-bottom:12px;}}
h1{{font-size:28px;font-weight:600;text-transform:uppercase;}}
.hdr-title{{font-size:12px;font-style:italic;color:#555;margin-top:2px;}}
.contact{{font-size:9px;color:#444;font-family:'Inter',sans-serif;margin-top:6px;}}
.summary-text{{font-size:10.5px;line-height:1.6;color:#333;font-style:italic;}}
.exp-block{{margin-bottom:10px;page-break-inside:avoid;break-inside:avoid;}}
.exp-top{{display:flex;justify-content:space-between;align-items:baseline;}}
.exp-title{{font-size:10.5px;font-weight:600;}}
.exp-dates{{font-size:9px;color:#666;font-family:'Inter',sans-serif;}}
.exp-co{{font-size:10px;color:#444;font-style:italic;margin-bottom:3px;}}
.exp-loc{{color:#888;}}
.bullet-row{{display:flex;gap:5px;font-size:9.5px;color:#333;margin-bottom:1.5px;}}
.bdot{{flex-shrink:0;font-size:9px;margin-top:0.5px;}}
.proj-block{{margin-bottom:10px;page-break-inside:avoid;break-inside:avoid;}}
.proj-name{{font-size:10.5px;font-weight:600;}}
.proj-desc{{font-size:9.5px;color:#555;font-style:italic;}}
.edu-degree{{font-size:10px;font-weight:600;}}
.edu-school{{font-size:10px;color:#444;font-style:italic;}}
.edu-meta{{font-size:8.5px;color:#888;font-family:'Inter',sans-serif;}}
.edu-block{{margin-bottom:8px;page-break-inside:avoid;break-inside:avoid;}}
.bottom{{display:grid;grid-template-columns:1fr 1fr;gap:24px;page-break-inside:avoid;break-inside:avoid;}}
.skill-cat{{font-size:8.5px;text-transform:uppercase;color:#1a1a1a;font-weight:600;margin:4px 0 2px;font-family:'Inter',sans-serif;}}
.skill-pills{{display:flex;flex-wrap:wrap;gap:3px;}}
.pill{{border:1px solid #ddd;border-radius:2px;padding:1px 5px;font-size:8.5px;color:#333;}}
</style></head><body>
<table class="page-table">
  <thead><tr><td><div class="header-space"></div></td></tr></thead>
  <tbody><tr><td>
    <div class="page">
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
          {f'{sec("Langues")}<p style="font-size:9.5px;color:#444;">{langs}</p>' if langs else ""}
          {f'{sec("Certifications")}{certs}' if certs else ""}
        </div>
      </div>
    </div>
  </td></tr></tbody>
  <tfoot><tr><td><div class="footer-space"></div></td></tr></tfoot>
</table>
</body></html>"""

# ── 6. Néon Tech ──────────────────────────────────────────────────────────────

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
    sec = lambda t: f'<div class="sec-head" style="font-size:10px;text-transform:uppercase;color:#FF00A0;margin:14px 0 8px;border-bottom:1px solid #FF00A033;padding-bottom:3px;font-family:\'Share Tech Mono\',monospace;page-break-after:avoid;break-after:avoid;">{t}</div>'
    return f"""<!DOCTYPE html><html lang="fr"><head><meta charset="utf-8"/>
<style>
@page{{size: A4; margin: 0;}}
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Inter:wght@300;400;600;700;800&display=swap');
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{font-family:'Inter',sans-serif;font-size:9.5px;background:#090D16;color:#E2E8F0;-webkit-print-color-adjust:exact;print-color-adjust:exact;width:210mm;min-height:297mm;line-height:1.45;}}
.page-table{{width:100%;border-collapse:collapse;}}
.header-space{{height:35px;}}
.footer-space{{height:35px;}}
.page{{width:100%;padding:0 44px;}}
.header{{background:#111128;padding:20px 24px;border:1px solid #00E5FF33;border-radius:6px;margin-bottom:16px;display:flex;flex-direction:column;gap:12px;}}
.header-main{{display:flex;align-items:center;gap:16px;}}
.avatar{{width:48px;height:48px;border-radius:50%;border:2px solid #00E5FF;box-shadow:0 0 10px #00E5FF33;display:flex;align-items:center;justify-content:center;background:#1A1A35;font-family:'Share Tech Mono',monospace;font-size:16px;color:#00E5FF;flex-shrink:0;}}
.header-name{{display:flex;flex-direction:column;}}
.nm-first{{font-size:9.5px;color:#00E5FF;letter-spacing:1px;text-transform:uppercase;font-family:'Share Tech Mono',monospace;}}
.nm-last{{font-size:22px;font-weight:800;color:#fff;line-height:1.1;}}
.nm-title{{font-size:10px;color:#FF00A0;letter-spacing:0.5px;text-transform:uppercase;font-family:'Share Tech Mono',monospace;margin-top:2px;font-weight:600;}}
.contact-row{{display:flex;flex-wrap:wrap;gap:12px;padding-top:12px;border-top:1px solid #00E5FF15;}}
.ci{{display:flex;align-items:center;gap:4px;font-size:9px;color:#8F90A6;}}
.ci-ic{{color:#00E5FF;font-weight:700;font-family:'Share Tech Mono',monospace;}}
.summary-text{{font-size:9.5px;color:#C0C0D8;line-height:1.6;margin-bottom:8px;}}
.exp-block{{margin-bottom:10px;padding-left:10px;border-left:2px solid #1A1A3A;page-break-inside:avoid;break-inside:avoid;}}
.exp-top{{display:flex;justify-content:space-between;align-items:baseline;}}
.exp-title{{font-size:10.5px;font-weight:700;color:#fff;}}
.exp-dates{{font-size:9px;color:#00E5FF;font-family:'Share Tech Mono',monospace;}}
.exp-co{{font-size:9.5px;color:#FF00A0;margin-bottom:3px;font-weight:600;}}
.exp-loc{{color:#60608F;font-weight:400;}}
.bullet-row{{display:flex;gap:5px;margin-bottom:1.5px;font-size:9px;color:#C0C0D8;}}
.bdot{{flex-shrink:0;font-size:9px;margin-top:0.5px;}}
.proj-block{{margin-bottom:10px;padding:8px 12px;border:1px solid #1A1A3A;border-radius:4px;background:#111128;page-break-inside:avoid;break-inside:avoid;}}
.proj-name{{font-size:10px;font-weight:700;color:#fff;margin-bottom:2px;}}
.proj-desc{{font-size:9px;color:#8F90A6;margin-bottom:3px;}}
.edu-block{{margin-bottom:8px;page-break-inside:avoid;break-inside:avoid;}}
.edu-degree{{font-size:10px;font-weight:700;color:#fff;}}
.edu-school{{font-size:9.5px;color:#8F90A6;}}
.edu-meta{{font-size:8.5px;color:#404070;}}
.skills-section{{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:8px;page-break-inside:avoid;break-inside:avoid;}}
.skill-cat{{font-size:8.5px;text-transform:uppercase;color:#00E5FF;font-weight:700;width:100%;margin-top:2px;font-family:'Share Tech Mono',monospace;}}
.pill{{background:#1A1A3A;border:1px solid #00E5FF33;border-radius:2px;padding:1px 5px;font-size:8.5px;color:#C0C0FF;font-weight:600;}}
.lang-item{{font-size:9.5px;color:#8F90A6;margin-bottom:2px;page-break-inside:avoid;break-inside:avoid;}}
.cert-item{{font-size:9.5px;color:#8F90A6;margin-bottom:2px;border-left:2px solid #FF00A0;padding-left:5px;page-break-inside:avoid;break-inside:avoid;}}
</style></head><body>
<table class="page-table">
  <thead><tr><td><div class="header-space"></div></td></tr></thead>
  <tbody><tr><td>
    <div class="page">
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
        {f'<div class="sec-head">{sec("Profil")}</div><p class="summary-text">{esc(f["summary"])}</p>' if f["summary"] else ""}
        {f'<div class="sec-head">{sec("Expériences")}</div>{exp_html}' if exp_html else ""}
        {f'<div class="sec-head">{sec("Projets")}</div>{proj_html}' if proj_html else ""}
        {f'<div class="sec-head">{sec("Formation")}</div>{edu_html}' if edu_html else ""}
        {f'<div class="sec-head">{sec("Compétences")}</div><div class="skills-section">{f["skills_html"]}</div>' if f["skills_html"] else ""}
        {f'<div class="sec-head">{sec("Langues")}</div>{langs}' if langs else ""}
        {f'<div class="sec-head">{sec("Certifications")}</div>{certs}' if certs else ""}
      </div>
    </div>
  </td></tr></tbody>
  <tfoot><tr><td><div class="footer-space"></div></td></tr></tfoot>
</table>
</body></html>"""

# ── 7. Scandinave ─────────────────────────────────────────────────────────────

@register("scandinave", "Scandinave", "Épuré / Nordic", "#4A7C59")
def build_scandinave(cv_data: dict) -> str:
    f = _fields(cv_data)
    contact_str = " · ".join(filter(None, [
        f'Email: {esc(f["email"])}' if f["email"] else "",
        f'Tél: {esc(f["phone"])}' if f["phone"] else "",
        esc(f["location"]),
        f'LinkedIn: {esc(f["linkedin"])}' if f["linkedin"] else ""
    ]))
    sec = lambda t: f'<div class="sec-head" style="display:flex;align-items:center;gap:10px;margin:14px 0 8px;page-break-after:avoid;break-after:avoid;"><span style="font-size:9px;text-transform:uppercase;font-weight:700;color:#1A1A1A;white-space:nowrap;">{t}</span><div style="flex:1;height:1px;background:#ddd;"></div></div>'
    exp_out = ""
    for e in f["experiences"]:
        dates = " – ".join(filter(None,[e.get("start_date",""),e.get("end_date","")]))
        bullets = "".join(f'<li style="padding-left:10px;margin-bottom:2px;font-size:9.5px;color:#444;position:relative;list-style:none;"><span style="position:absolute;left:0;color:#4A7C59;font-weight:700;">•</span>{esc(b)}</li>' for b in (e.get("bullets") or []))
        exp_out += f'<div style="margin-bottom:10px;page-break-inside:avoid;break-inside:avoid;"><div style="display:flex;justify-content:space-between;align-items:baseline;"><div><span style="font-size:10.5px;font-weight:600;color:#1A1A1A;">{esc(e.get("title",""))}</span><span style="color:#BBB;"> — </span><span style="font-size:9.5px;color:#4A7C59;">{esc(e.get("company",""))}</span></div><span style="font-size:9px;color:#888;">{esc(dates)}</span></div><ul style="padding:0;margin-top:2px;">{bullets}</ul></div>'
    edu_out = "".join(f'<div style="display:flex;justify-content:space-between;margin-bottom:6px;page-break-inside:avoid;break-inside:avoid;"><span style="font-size:10px;font-weight:600;color:#1A1A1A;">{esc(e.get("degree",""))}</span><span style="font-size:9.5px;color:#666;font-style:italic;">{esc(e.get("institution") or e.get("school",""))}</span></div>' for e in f["education"])
    langs = " – ".join(esc(l) for l in f["languages"])
    certs = "".join(f'<div style="font-size:9.5px;color:#444;border-left:2px solid #4A7C59;padding-left:5px;margin-bottom:3px;page-break-inside:avoid;break-inside:avoid;">{esc(c)}</div>' for c in f["certifications"])
    return f"""<!DOCTYPE html><html lang="fr"><head><meta charset="utf-8"/>
<style>
@page{{size: A4; margin: 0;}}
@import url('https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,400;0,600;1,400&family=DM+Sans:wght@300;400;500;600&display=swap');
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{font-family:'DM Sans',sans-serif;background:#FAFAF7;color:#2B2B2B;font-size:9.5px;line-height:1.5;-webkit-print-color-adjust:exact;print-color-adjust:exact;width:210mm;min-height:297mm;}}
.page-table{{width:100%;border-collapse:collapse;}}
.header-space{{height:40px;}}
.footer-space{{height:40px;}}
.page{{width:100%;padding:0 52px;}}
h1{{font-family:'Lora',serif;font-size:28px;font-weight:600;color:#1A1A1A;}}
.hdr-title{{font-size:11px;font-weight:300;color:#4A7C59;text-transform:uppercase;margin-top:2px;letter-spacing:0.5px;}}
.contact{{font-size:9px;color:#666;margin-top:6px;}}
.summary-text{{font-size:10px;color:#444;line-height:1.7;font-style:italic;font-family:'Lora',serif;}}
.skill-cat{{font-size:8.5px;text-transform:uppercase;color:#4A7C59;margin:4px 0 2px;font-weight:600;}}
.skill-pills{{display:flex;flex-wrap:wrap;gap:3px;}}
.pill{{border:1px solid #ddd;border-radius:2px;padding:1px 5px;font-size:8.5px;color:#444;background:#fff;}}
.bottom{{display:grid;grid-template-columns:1fr 1fr;gap:24px;page-break-inside:avoid;break-inside:avoid;}}
</style></head><body>
<table class="page-table">
  <thead><tr><td><div class="header-space"></div></td></tr></thead>
  <tbody><tr><td>
    <div class="page">
      <div style="text-align:center;margin-bottom:20px;">
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
          {f'{sec("Langues")}<p style="font-size:9.5px;color:#444;">{langs}</p>' if langs else ""}
          {f'{sec("Certifications")}{certs}' if certs else ""}
        </div>
      </div>
    </div>
  </td></tr></tbody>
  <tfoot><tr><td><div class="footer-space"></div></td></tr></tfoot>
</table>
</body></html>"""

# ── 8. Timeline ───────────────────────────────────────────────────────────────

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
        
    sec = lambda t: f'<div class="sec-head" style="font-size:10px;text-transform:uppercase;color:#E85D4A;margin:14px 0 8px;border-bottom:1px solid #E85D4A33;padding-bottom:3px;font-weight:700;page-break-after:avoid;break-after:avoid;">{t}</div>'
    
    return f"""<!DOCTYPE html><html lang="fr"><head><meta charset="utf-8"/>
<style>
@page{{size: A4; margin: 0;}}
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@300;400;600;700;800&family=Playfair+Display:wght@700&display=swap');
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{font-family:'Nunito',sans-serif;background:#F9F5F0;color:#2D2D2D;font-size:9.5px;line-height:1.45;-webkit-print-color-adjust:exact;print-color-adjust:exact;width:210mm;min-height:297mm;}}
.page-table{{width:100%;border-collapse:collapse;}}
.header-space{{height:35px;}}
.footer-space{{height:35px;}}
.page{{width:100%;padding:0 44px;}}
.header{{background:#2D2D2D;padding:20px 24px;border-radius:6px;margin-bottom:16px;color:#fff;}}
.hdr-name{{font-family:'Playfair Display',serif;font-size:24px;color:#fff;line-height:1.1;}}
.hdr-title{{font-size:10.5px;color:#E85D4A;text-transform:uppercase;letter-spacing:0.5px;margin-top:2px;font-weight:600;}}
.contact-row{{display:flex;flex-wrap:wrap;gap:12px;margin-top:12px;padding-top:12px;border-top:1px solid #ffffff15;}}
.ci{{display:flex;align-items:center;gap:4px;font-size:9px;color:#BBBBBB;}}
.ci-ic{{color:#E85D4A;font-weight:700;}}
.summary-text{{font-size:9.5px;color:#444;line-height:1.6;font-style:italic;margin-bottom:8px;padding-left:8px;border-left:3px solid #E85D4A;}}
.tl-container{{position:relative;border-left:2px solid #E85D4A33;margin-left:8px;padding-left:18px;margin-bottom:10px;}}
.tl-card{{position:relative;margin-bottom:12px;background:#fff;border-radius:6px;padding:10px 14px;box-shadow:0 1px 4px rgba(0,0,0,0.03);page-break-inside:avoid;break-inside:avoid;}}
.tl-dot{{position:absolute;left:-25px;top:10px;width:12px;height:12px;border-radius:50%;background:#E85D4A;color:#fff;display:flex;align-items:center;justify-content:center;font-size:7px;font-weight:800;}}
.tl-dates{{font-size:9px;color:#E85D4A;font-weight:700;margin-bottom:2px;}}
.tl-title{{font-size:10.5px;font-weight:700;color:#2D2D2D;}}
.tl-sub{{font-size:9.5px;color:#666;margin-bottom:3px;font-weight:600;}}
.tl-desc{{font-size:9px;color:#555;margin-bottom:3px;}}
.bullet-row{{display:flex;gap:5px;margin-bottom:1.5px;font-size:9px;color:#555;}}
.bdot{{flex-shrink:0;font-size:9px;margin-top:0.5px;}}
.edu-block{{margin-bottom:8px;page-break-inside:avoid;break-inside:avoid;}}
.edu-degree{{font-size:10px;font-weight:700;color:#2D2D2D;}}
.edu-school{{font-size:9.5px;color:#666;}}
.edu-meta{{font-size:8.5px;color:#888;}}
.skills-section{{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:8px;page-break-inside:avoid;break-inside:avoid;}}
.skill-cat{{font-size:8.5px;text-transform:uppercase;color:#E85D4A;font-weight:700;width:100%;margin-top:2px;}}
.pill{{background:#fff;border:1px solid #E85D4A33;border-radius:2px;padding:1px 5px;font-size:8.5px;color:#555;font-weight:600;}}
.lang-item{{font-size:9.5px;color:#555;margin-bottom:2px;page-break-inside:avoid;break-inside:avoid;}}
.cert-item{{font-size:9.5px;color:#555;margin-bottom:2px;border-left:2px solid #E85D4A;padding-left:5px;page-break-inside:avoid;break-inside:avoid;}}
</style></head><body>
<table class="page-table">
  <thead><tr><td><div class="header-space"></div></td></tr></thead>
  <tbody><tr><td>
    <div class="page">
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
      </div>
    </div>
  </td></tr></tbody>
  <tfoot><tr><td><div class="footer-space"></div></td></tr></tfoot>
</table>
</body></html>"""



def build_html(template_id: str, cv_data: dict) -> str | None:
    """Returns HTML string for the given template_id, or None if not found."""
    entry = TEMPLATES.get(template_id)
    if entry:
        return entry["build"](cv_data)
    return None
