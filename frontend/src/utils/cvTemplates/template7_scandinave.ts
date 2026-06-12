/**
 * Template 7 — Scandinave
 * Minimalist Nordic design: warm off-white (#FAFAF7), charcoal text,
 * thin horizontal rules, small caps section titles, generous white space.
 * No sidebar — single full-width column. Very clean & elegant.
 */
import { CvTemplate, CvData, ParsedAudit } from './types';
import { escHtml, extractCvFields } from './helpers';

export const templateScandinave: CvTemplate = {
  id: 'scandinave',
  label: 'Scandinave',
  description: 'Épuré / Nordic',
  accentColor: '#4A7C59',
  build(cvData: CvData, parsedAudit: ParsedAudit | null): string {
    const f = extractCvFields(cvData, parsedAudit);
    const { firstName, lastName, jobTitle, email, phone, location, linkedin, github, summary,
            experiences, projects, education, languages, certifications, skillsHtml } = f;

    const contactParts = [
      email    ? escHtml(email) : '',
      phone    ? escHtml(phone) : '',
      location ? escHtml(location) : '',
      linkedin ? `<span class="li-link">linkedin: ${escHtml(linkedin)}</span>` : '',
      github   ? `<span class="li-link">github: ${escHtml(github)}</span>` : '',
    ].filter(Boolean).join(' &nbsp;·&nbsp; ');

    const sec = (label: string) =>
      `<div class="rule-sec"><span class="sec-txt">${label}</span><div class="rule-line"></div></div>`;

    const expHtml = experiences.map(exp => `
      <div class="exp-block">
        <div class="exp-row">
          <div>
            <span class="exp-title">${escHtml(exp.title || '')}</span>
            <span class="exp-sep"> — </span>
            <span class="exp-co">${escHtml(exp.company || '')}</span>
            ${exp.location ? `<span class="exp-loc">, ${escHtml(exp.location)}</span>` : ''}
          </div>
          <div class="exp-dates">${[exp.start_date, exp.end_date].filter(Boolean).map(escHtml).join(' – ')}</div>
        </div>
        <ul class="bullet-list">
          ${Array.isArray(exp.bullets) && exp.bullets.length ? exp.bullets.map((b: string) => `<li>${escHtml(b)}</li>`).join('') : ''}
        </ul>
      </div>`).join('');

    const projHtml = projects.map(p => `
      <div class="exp-block">
        <div class="proj-name">${escHtml(p.name || '')}</div>
        ${p.description ? `<p class="proj-desc">${escHtml(p.description)}</p>` : ''}
        <ul class="bullet-list">
          ${Array.isArray(p.bullets) && p.bullets.length ? p.bullets.map((b: string) => `<li>${escHtml(b)}</li>`).join('') : ''}
        </ul>
      </div>`).join('');

    const eduHtml = education.map(ed => `
      <div class="edu-row">
        <div class="edu-degree">${escHtml(ed.degree || '')}</div>
        <div class="edu-school">${escHtml(ed.institution || ed.school || '')} ${ed.year ? `<span class="edu-year">${escHtml(ed.year)}</span>` : ''}</div>
      </div>`).join('');

    return `<!DOCTYPE html><html lang="fr"><head><meta charset="utf-8"/>
<style>
@import url('https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,400;0,600;1,400&family=DM+Sans:wght@300;400;500;600&display=swap');
*{margin:0;padding:0;box-sizing:border-box;}
body{font-family:'DM Sans',sans-serif;background:#FAFAF7;color:#2B2B2B;font-size:11px;line-height:1.6;-webkit-print-color-adjust:exact;print-color-adjust:exact;}
.page{max-width:820px;margin:0 auto;padding:52px 60px;}
/* Header */
.hdr{text-align:center;margin-bottom:28px;}
.hdr-name{font-family:'Lora',serif;font-size:38px;font-weight:600;color:#1A1A1A;letter-spacing:2px;}
.hdr-title{font-size:13px;font-weight:300;color:#4A7C59;letter-spacing:4px;text-transform:uppercase;margin-top:4px;}
.hdr-contact{font-size:10px;color:#888;margin-top:12px;line-height:1.8;}
.li-link{color:#4A7C59;}
/* Section rule */
.rule-sec{display:flex;align-items:center;gap:12px;margin:24px 0 12px;}
.sec-txt{font-size:10px;letter-spacing:3px;text-transform:uppercase;color:#1A1A1A;white-space:nowrap;font-weight:600;}
.rule-line{flex:1;height:1px;background:#DDD;}
/* Summary */
.summary-text{font-size:11.5px;line-height:1.8;color:#444;font-style:italic;font-family:'Lora',serif;}
/* Experience */
.exp-block{margin-bottom:18px;page-break-inside:avoid;break-inside:avoid;}
.exp-row{display:flex;justify-content:space-between;align-items:baseline;margin-bottom:4px;}
.exp-title{font-size:12px;font-weight:600;color:#1A1A1A;}
.exp-sep{color:#BBB;}
.exp-co{font-size:11px;font-weight:500;color:#4A7C59;}
.exp-loc{font-size:11px;color:#888;}
.exp-dates{font-size:10px;color:#999;white-space:nowrap;flex-shrink:0;margin-left:12px;}
.bullet-list{list-style:none;padding:0;}
.bullet-list li{padding-left:12px;margin-bottom:3px;font-size:11px;color:#555;position:relative;page-break-inside:avoid;break-inside:avoid;}
.bullet-list li::before{content:'—';position:absolute;left:0;color:#4A7C59;font-weight:600;}
/* Projects */
.proj-name{font-size:12px;font-weight:600;color:#1A1A1A;margin-bottom:3px;}
.proj-desc{font-size:11px;color:#666;margin-bottom:4px;}
/* Education */
.edu-row{display:flex;justify-content:space-between;align-items:baseline;margin-bottom:8px;page-break-inside:avoid;break-inside:avoid;}
.edu-degree{font-size:11px;font-weight:600;color:#1A1A1A;}
.edu-school{font-size:11px;color:#888;}
.edu-year{color:#4A7C59;font-weight:500;font-size:10px;margin-left:6px;}
/* Skills */
.skill-cat{font-size:9px;letter-spacing:1.5px;text-transform:uppercase;color:#4A7C59;margin:8px 0 4px;font-weight:600;}
.skill-pills{display:flex;flex-wrap:wrap;gap:4px;page-break-inside:avoid;break-inside:avoid;}
.pill{border:1px solid #DDD;border-radius:2px;padding:2px 8px;font-size:10px;color:#444;background:#fff;}
/* 2-col bottom grid */
.bottom-grid{display:grid;grid-template-columns:1fr 1fr;gap:32px;margin-top:0;page-break-inside:avoid;break-inside:avoid;}
.lang-item{display:flex;align-items:center;gap:6px;margin-bottom:4px;font-size:10px;color:#555;page-break-inside:avoid;break-inside:avoid;}
.lang-dash{color:#4A7C59;font-weight:700;}
.cert-item{font-size:10px;color:#555;margin-bottom:4px;padding-left:8px;border-left:2px solid #4A7C59;page-break-inside:avoid;break-inside:avoid;}
</style></head><body>
<div class="page">
  <div class="hdr">
    <div class="hdr-name">${escHtml(firstName)} ${escHtml(lastName)}</div>
    ${jobTitle ? `<div class="hdr-title">${escHtml(jobTitle)}</div>` : ''}
    ${contactParts ? `<div class="hdr-contact">${contactParts}</div>` : ''}
  </div>
  ${summary ? `${sec('Profil')}<p class="summary-text">${escHtml(summary)}</p>` : ''}
  ${expHtml ? `${sec('Expériences')}${expHtml}` : ''}
  ${projHtml ? `${sec('Projets')}${projHtml}` : ''}
  ${eduHtml ? `${sec('Formation')}${eduHtml}` : ''}
  <div class="bottom-grid">
    ${skillsHtml ? `<div>${sec('Compétences')}${skillsHtml}</div>` : '<div></div>'}
    <div>
      ${languages.length ? `${sec('Langues')}${languages.map(l => `<div class="lang-item"><span class="lang-dash">–</span>${escHtml(l)}</div>`).join('')}` : ''}
      ${certifications.length ? `${sec('Certifications')}${certifications.map(c => `<div class="cert-item">${escHtml(c)}</div>`).join('')}` : ''}
    </div>
  </div>
</div>
</body></html>`;
  }
};
