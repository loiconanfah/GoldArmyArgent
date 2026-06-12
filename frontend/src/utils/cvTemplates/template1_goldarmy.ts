/**
 * Template 1 – "GoldArmy"
 * En-tête: Bannière sombre + barre contact orange
 * Corps: Format classique 1 colonne
 */
import { CvTemplate, CvData, ParsedAudit } from './types';
import { escHtml, extractCvFields, buildContactItems } from './helpers';

function build(cvData: CvData, parsedAudit: ParsedAudit | null): string {
  const f = extractCvFields(cvData, parsedAudit);
  const ACCENT = '#FF6B35';

  const secTitle = (label: string) =>
    `<div class="sec-title"><span class="sec-line"></span><span class="sec-label">${label}</span><span class="sec-line"></span></div>`;

  const expHtml = f.experiences.map(exp => `
    <div class="block">
      <div class="block-header">
        <div>
          <span class="block-title">${escHtml(exp.title)}</span>
          <span class="block-sub"> — ${escHtml(exp.company)}${exp.location ? ` · ${escHtml(exp.location)}` : ''}</span>
        </div>
        <span class="block-dates">${[exp.start_date, exp.end_date].filter(Boolean).map(escHtml).join(' – ')}</span>
      </div>
      ${Array.isArray(exp.bullets) && exp.bullets.length ? `<ul class="bullets">${exp.bullets.map((b: string) => `<li>${escHtml(b)}</li>`).join('')}</ul>` : ''}
    </div>`).join('');

  const projHtml = f.projects.map(p => `
    <div class="block">
      <div class="block-title">${escHtml(p.name)}</div>
      ${p.description ? `<div class="block-desc">${escHtml(p.description)}</div>` : ''}
      ${Array.isArray(p.bullets) && p.bullets.length ? `<ul class="bullets">${p.bullets.map((b: string) => `<li>${escHtml(b)}</li>`).join('')}</ul>` : ''}
    </div>`).join('');

  const eduHtml = f.education.map(ed => `
    <div class="block edu-block">
      <div class="block-header">
        <div>
          <span class="block-title">${escHtml(ed.degree)}</span>
          <span class="block-sub"> — ${escHtml(ed.institution || ed.school || '')}</span>
        </div>
        <span class="block-dates">${escHtml(ed.year || ed.location || '')}</span>
      </div>
    </div>`).join('');

  let skillsHtml = '';
  if (cvData.skills && typeof cvData.skills === 'object' && !Array.isArray(cvData.skills)) {
    skillsHtml = Object.entries(cvData.skills as Record<string, string[]>)
      .filter(([, items]) => Array.isArray(items) && items.length > 0)
      .map(([cat, items]) =>
        `<span class="skill-cat">${escHtml(cat)} :</span> ${items.map(s => `<span class="pill">${escHtml(s)}</span>`).join(' ')}`
      ).join('<br/>');
  } else if (Array.isArray(cvData.skills)) {
    skillsHtml = (cvData.skills as string[]).map(s => `<span class="pill">${escHtml(s)}</span>`).join(' ');
  }

  const langHtml = f.languages.map(l => `<span class="pill">${escHtml(l)}</span>`).join(' ');
  const certHtml = f.certifications.map(c => `<div class="cert-item">▸ ${escHtml(c)}</div>`).join('');

  return `<!DOCTYPE html>
<html lang="fr"><head><meta charset="utf-8"/>
<style>
*{margin:0;padding:0;box-sizing:border-box;}
body{font-family:system-ui,sans-serif;background:#F0EFEA;font-size:11px;line-height:1.6;-webkit-print-color-adjust:exact;print-color-adjust:exact;}
.page{max-width:860px;margin:0 auto;background:#FAFAF8;}
/* ── EN-TÊTE GOLDARMY ── */
.banner{background:#1a1a1a;color:#fff;padding:36px 40px 28px;position:relative;overflow:hidden;}
.banner::before{content:'';position:absolute;top:-40px;right:-40px;width:200px;height:200px;background:rgba(255,107,53,.15);border-radius:50%;}
.banner-inner{position:relative;z-index:1;}
.first-name{font-size:13px;font-weight:400;letter-spacing:6px;color:rgba(255,255,255,.65);text-transform:uppercase;}
.last-name{font-size:40px;font-weight:800;letter-spacing:4px;line-height:1;text-transform:uppercase;}
.job-title{font-size:12px;color:rgba(255,255,255,.7);letter-spacing:2px;margin-top:6px;}
.contact-bar{background:${ACCENT};padding:10px 40px;display:flex;flex-wrap:wrap;gap:14px;}
.contact-item{display:flex;align-items:center;gap:5px;font-size:10px;color:#fff;font-weight:500;}
.ci{font-size:11px;}
/* ── CORPS CLASSIQUE ── */
.body{padding:28px 40px;}
.sec-title{display:flex;align-items:center;gap:8px;margin:22px 0 10px;}
.sec-title:first-child{margin-top:0;}
.sec-line{flex:1;height:1px;background:#ddd;}
.sec-label{font-size:9px;font-weight:700;letter-spacing:2.5px;text-transform:uppercase;color:#888;white-space:nowrap;}
.summary-text{font-size:11px;color:#444;line-height:1.75;}
.block{margin-bottom:14px;page-break-inside:avoid;break-inside:avoid;}
.block-header{display:flex;justify-content:space-between;align-items:baseline;flex-wrap:wrap;gap:4px;margin-bottom:3px;}
.block-title{font-size:12px;font-weight:700;color:#1a1a1a;}
.block-sub{font-size:11px;color:${ACCENT};font-weight:500;}
.block-dates{font-size:10px;color:#888;white-space:nowrap;flex-shrink:0;}
.block-desc{font-size:11px;color:#555;margin:2px 0;}
.bullets{list-style:none;padding:0;margin-top:4px;}
.bullets li{padding-left:14px;position:relative;margin-bottom:3px;font-size:11px;color:#444;line-height:1.55;page-break-inside:avoid;break-inside:avoid;}
.bullets li::before{content:'▸';position:absolute;left:0;color:${ACCENT};font-weight:700;}
.edu-block{margin-bottom:8px;}
.skill-cat{font-weight:700;color:#1a1a1a;}
.pill{display:inline-block;background:#fff;border:1px solid #ddd;border-radius:3px;padding:2px 8px;font-size:10px;color:#333;margin:2px 2px;}
.cert-item{font-size:10px;color:#444;margin-bottom:3px;padding-left:4px;}
.inline-row{display:flex;flex-wrap:wrap;gap:4px;}
</style></head><body>
<div class="page">
  <div class="banner">
    <div class="banner-inner">
      <div class="first-name">${escHtml(f.firstName)}</div>
      <div class="last-name">${escHtml(f.lastName)}</div>
      ${f.jobTitle ? `<div class="job-title">— ${escHtml(f.jobTitle)}</div>` : ''}
    </div>
  </div>
  ${(f.email || f.phone || f.location || f.linkedin || f.github) ? `<div class="contact-bar">${buildContactItems(f)}</div>` : ''}
  <div class="body">
    ${f.summary ? `${secTitle('Profil')}<p class="summary-text">${escHtml(f.summary)}</p>` : ''}
    ${expHtml ? `${secTitle('Expériences')}${expHtml}` : ''}
    ${projHtml ? `${secTitle('Projets')}${projHtml}` : ''}
    ${eduHtml ? `${secTitle('Formation')}${eduHtml}` : ''}
    ${skillsHtml ? `${secTitle('Compétences')}<div style="line-height:1.9">${skillsHtml}</div>` : ''}
    ${langHtml ? `${secTitle('Langues')}<div class="inline-row">${langHtml}</div>` : ''}
    ${certHtml ? `${secTitle('Certifications')}${certHtml}` : ''}
  </div>
</div>
</body></html>`;
}

export const templateGoldArmy: CvTemplate = {
  id: 'goldarmy',
  label: 'GoldArmy',
  description: 'Sombre & orangé — style corporate premium',
  accentColor: '#FF6B35',
  build,
};
