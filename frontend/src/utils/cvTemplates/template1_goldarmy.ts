/**
 * Template 1 – "GoldArmy" : Dark banner + orange accent + cream sidebar.
 * Style: Corporate Premium
 * Page-break fix: sidebar uses explicit background so it repeats on page 2.
 */
import { CvTemplate, CvData, ParsedAudit } from './types';
import {
  escHtml,
  extractCvFields,
  buildContactItems,
  buildExperiencesHtml,
  buildProjectsHtml,
  buildEducationHtml,
} from './helpers';

function build(cvData: CvData, parsedAudit: ParsedAudit | null): string {
  const f = extractCvFields(cvData, parsedAudit);
  const ACCENT = '#FF6B35';
  const SIDEBAR_BG = '#F3EEE6';

  return `<!DOCTYPE html>
<html lang="fr"><head><meta charset="utf-8"/>
<style>
*{margin:0;padding:0;box-sizing:border-box;}
body{font-family:system-ui,sans-serif;background:#F0EFEA;font-size:11px;line-height:1.5;-webkit-print-color-adjust:exact;print-color-adjust:exact;}
.page{max-width:860px;margin:0 auto;background:#FAFAF8;}
.banner{background:#1a1a1a;color:#fff;padding:36px 40px 28px;position:relative;overflow:hidden;}
.banner::before{content:'';position:absolute;top:-40px;right:-40px;width:200px;height:200px;background:rgba(255,107,53,.15);border-radius:50%;}
.banner-inner{display:flex;justify-content:space-between;align-items:flex-end;position:relative;z-index:1;}
.first-name{font-size:13px;font-weight:400;letter-spacing:6px;color:rgba(255,255,255,.65);text-transform:uppercase;}
.last-name{font-size:40px;font-weight:800;letter-spacing:4px;line-height:1;text-transform:uppercase;}
.job-title{font-size:12px;color:rgba(255,255,255,.7);letter-spacing:2px;margin-top:6px;}
.contact-bar{background:${ACCENT};padding:10px 40px;display:flex;flex-wrap:wrap;gap:14px;}
.contact-item{display:flex;align-items:center;gap:5px;font-size:10px;color:#fff;font-weight:500;}
.ci{font-size:11px;}
/* Two-column layout via table for proper page-break background repeat */
.body-layout{display:table;width:100%;table-layout:fixed;}
.sidebar{display:table-cell;width:230px;background:${SIDEBAR_BG};padding:26px 20px;vertical-align:top;}
.section-head{display:flex;align-items:center;gap:8px;margin:18px 0 8px;}
.section-head:first-child{margin-top:0;}
.section-line{flex:1;height:1px;background:#ccc;}
.section-label{font-size:9px;font-weight:700;letter-spacing:2.5px;text-transform:uppercase;color:#888;white-space:nowrap;}
.edu-block{margin-bottom:10px;page-break-inside:avoid;break-inside:avoid;}
.edu-degree{font-size:11px;font-weight:700;color:#1a1a1a;}
.edu-school{font-size:10px;color:#555;}
.edu-meta{font-size:10px;color:#888;}
.skill-cat{font-size:9px;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;color:${ACCENT};margin:8px 0 4px;}
.skill-pills{display:flex;flex-wrap:wrap;gap:4px;margin-bottom:4px;page-break-inside:avoid;break-inside:avoid;}
.pill{background:#fff;border:1px solid #ddd;border-radius:3px;padding:2px 7px;font-size:10px;color:#333;font-weight:500;}
.lang-item{display:flex;align-items:center;gap:6px;margin-bottom:4px;font-size:10px;color:#333;page-break-inside:avoid;break-inside:avoid;}
.lang-dot{width:6px;height:6px;border-radius:50%;background:${ACCENT};flex-shrink:0;}
.cert-item{font-size:10px;color:#444;margin-bottom:4px;padding-left:8px;border-left:2px solid ${ACCENT};page-break-inside:avoid;break-inside:avoid;}
.main{display:table-cell;background:#FAFAF8;padding:26px 30px;vertical-align:top;}
.summary-text{font-size:11px;line-height:1.7;color:#444;}
.exp-block{margin-bottom:20px;page-break-inside:avoid;break-inside:avoid;}
.exp-header{display:flex;justify-content:space-between;align-items:baseline;}
.exp-title{font-size:12px;font-weight:700;color:#1a1a1a;}
.exp-dates{font-size:9px;color:#888;margin-left:8px;white-space:nowrap;}
.exp-company{font-size:11px;color:${ACCENT};font-weight:600;margin-bottom:5px;}
.exp-loc{color:#888;font-weight:400;}
.bullet-row{display:flex;align-items:flex-start;gap:7px;margin-bottom:3px;page-break-inside:avoid;break-inside:avoid;}
.bullet-dot{width:5px;height:5px;border-radius:1px;background:${ACCENT};margin-top:4px;flex-shrink:0;}
.bullet-text{font-size:11px;color:#444;flex:1;line-height:1.55;}
.proj-block{margin-bottom:14px;page-break-inside:avoid;break-inside:avoid;}
.proj-name{font-size:12px;font-weight:700;color:#1a1a1a;margin-bottom:2px;}
.proj-desc{font-size:11px;color:#555;line-height:1.55;}
</style></head><body>
<div class="page">
  <div class="banner">
    <div class="banner-inner">
      <div>
        <div class="first-name">${escHtml(f.firstName)}</div>
        <div class="last-name">${escHtml(f.lastName)}</div>
        ${f.jobTitle ? `<div class="job-title">— ${escHtml(f.jobTitle)}</div>` : ''}
      </div>
    </div>
  </div>
  ${(f.email || f.phone || f.location || f.linkedin || f.github) ? `
  <div class="contact-bar">${buildContactItems(f)}</div>` : ''}
  <div class="body-layout">
    <div class="sidebar">
      ${f.education.length > 0 ? `<div class="section-head"><span class="section-line"></span><span class="section-label">Formation</span><span class="section-line"></span></div>${buildEducationHtml(f.education)}` : ''}
      ${f.skillsHtml ? `<div class="section-head"><span class="section-line"></span><span class="section-label">Compétences</span><span class="section-line"></span></div>${f.skillsHtml}` : ''}
      ${f.languages.length > 0 ? `<div class="section-head"><span class="section-line"></span><span class="section-label">Langues</span><span class="section-line"></span></div>${f.languages.map(l => `<div class="lang-item"><div class="lang-dot"></div>${escHtml(l)}</div>`).join('')}` : ''}
      ${f.certifications.length > 0 ? `<div class="section-head"><span class="section-line"></span><span class="section-label">Certifications</span><span class="section-line"></span></div>${f.certifications.map(c => `<div class="cert-item">${escHtml(c)}</div>`).join('')}` : ''}
    </div>
    <div class="main">
      ${f.summary ? `<div class="section-head"><span class="section-line"></span><span class="section-label">Profil</span><span class="section-line"></span></div><p class="summary-text">${escHtml(f.summary)}</p>` : ''}
      ${f.experiences.length > 0 ? `<div class="section-head"><span class="section-line"></span><span class="section-label">Expériences</span><span class="section-line"></span></div>${buildExperiencesHtml(f.experiences, ACCENT)}` : ''}
      ${f.projects.length > 0 ? `<div class="section-head"><span class="section-line"></span><span class="section-label">Projets</span><span class="section-line"></span></div>${buildProjectsHtml(f.projects, ACCENT)}` : ''}
    </div>
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
