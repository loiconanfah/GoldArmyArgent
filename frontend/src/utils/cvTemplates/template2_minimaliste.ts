/**
 * Template 2 – "Minimaliste" : Blanc pur, ligne fine bleue, typographie épurée.
 * Style: Clean & Modern (Format classique 1 colonne)
 */
import { CvTemplate, CvData, ParsedAudit } from './types';
import {
  escHtml,
  extractCvFields,
  buildExperiencesHtml,
  buildProjectsHtml,
  buildEducationHtml,
  buildContactItems,
} from './helpers';

function build(cvData: CvData, parsedAudit: ParsedAudit | null): string {
  const f = extractCvFields(cvData, parsedAudit);
  const ACCENT = '#2563EB';

  return `<!DOCTYPE html>
<html lang="fr"><head><meta charset="utf-8"/>
<style>
@page{size:A4;margin:0;}
*{margin:0;padding:0;box-sizing:border-box;}
html,body{width:210mm;height:297mm;overflow:hidden;}
body{font-family:system-ui,sans-serif;background:#fff;font-size:9.5px;line-height:1.45;-webkit-print-color-adjust:exact;print-color-adjust:exact;}
.page{width:210mm;height:297mm;overflow:hidden;background:#fff;padding:28px 36px;display:flex;flex-direction:column;}
.name-row{border-bottom:3px solid ${ACCENT};padding-bottom:8px;margin-bottom:10px;flex-shrink:0;}
.full-name{font-size:28px;font-weight:800;color:#111;letter-spacing:1px;text-transform:uppercase;}
.job-title{font-size:10px;color:${ACCENT};font-weight:600;letter-spacing:2px;margin-top:3px;}
.contact-bar{display:flex;flex-wrap:wrap;gap:12px;margin-bottom:10px;flex-shrink:0;}
.contact-item{display:flex;align-items:center;gap:4px;font-size:8.5px;color:#555;}
.ci{font-size:9px;color:${ACCENT};}
.section-title{font-size:8px;font-weight:800;letter-spacing:3px;text-transform:uppercase;color:${ACCENT};border-bottom:1.5px solid ${ACCENT};padding-bottom:2px;margin:10px 0 6px;}
.section-title:first-child{margin-top:0;}
.summary-text{font-size:9.5px;color:#444;line-height:1.5;}
.body-layout{display:block;flex:1;overflow:hidden;}
.exp-block{margin-bottom:10px;page-break-inside:avoid;break-inside:avoid;}
.exp-header{display:flex;justify-content:space-between;align-items:baseline;}
.exp-title{font-size:10.5px;font-weight:700;color:#111;}
.exp-dates{font-size:8px;color:#888;white-space:nowrap;margin-left:8px;}
.exp-company{font-size:9.5px;color:${ACCENT};font-weight:600;margin-bottom:3px;}
.exp-loc{color:#888;font-weight:400;}
.bullet-row{display:flex;align-items:flex-start;gap:6px;margin-bottom:2px;page-break-inside:avoid;break-inside:avoid;}
.bullet-dot{width:3.5px;height:3.5px;border-radius:50%;background:${ACCENT};margin-top:4px;flex-shrink:0;}
.bullet-text{font-size:9px;color:#444;flex:1;line-height:1.45;}
.proj-block{margin-bottom:8px;page-break-inside:avoid;break-inside:avoid;}
.proj-name{font-size:10px;font-weight:700;color:#111;margin-bottom:1px;}
.proj-desc{font-size:9px;color:#555;}
.edu-block{margin-bottom:6px;page-break-inside:avoid;break-inside:avoid;}
.edu-degree{font-size:9.5px;font-weight:700;color:#111;}
.edu-school{font-size:8.5px;color:#555;}
.edu-meta{font-size:8.5px;color:#888;}
.skill-cat{font-size:8px;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;color:${ACCENT};margin:5px 0 3px;}
.skill-pills{display:flex;flex-wrap:wrap;gap:3px;margin-bottom:3px;page-break-inside:avoid;break-inside:avoid;}
.pill{background:#EFF6FF;border:1px solid #BFDBFE;border-radius:4px;padding:1px 6px;font-size:8.5px;color:#1D4ED8;font-weight:500;margin:1px 1px;display:inline-block;}
.inline-row{display:flex;flex-wrap:wrap;gap:3px;}
.lang-item{font-size:8.5px;color:#333;margin-bottom:3px;padding-left:8px;border-left:2px solid ${ACCENT};page-break-inside:avoid;break-inside:avoid;}
.cert-item{font-size:8.5px;color:#444;margin-bottom:3px;padding-left:8px;border-left:2px solid #ddd;page-break-inside:avoid;break-inside:avoid;}
</style></head><body>
<div class="page">
  <div class="name-row">
    <div class="full-name">${escHtml(f.firstName)} <strong>${escHtml(f.lastName)}</strong></div>
    ${f.jobTitle ? `<div class="job-title">${escHtml(f.jobTitle)}</div>` : ''}
  </div>
  <div class="contact-bar">${buildContactItems(f, `color:${ACCENT}`)}</div>
  <div class="body-layout">
    ${f.summary ? `<div class="section-title">Profil</div><p class="summary-text">${escHtml(f.summary)}</p>` : ''}
    ${f.experiences.length > 0 ? `<div class="section-title">Expériences</div>${buildExperiencesHtml(f.experiences, ACCENT)}` : ''}
    ${f.projects.length > 0 ? `<div class="section-title">Projets</div>${buildProjectsHtml(f.projects, ACCENT)}` : ''}
    ${f.education.length > 0 ? `<div class="section-title">Formation</div>${buildEducationHtml(f.education)}` : ''}
    ${f.skillsHtml ? `<div class="section-title">Compétences</div>${f.skillsHtml}` : ''}
    ${f.languages.length > 0 ? `<div class="section-title">Langues</div><div class="inline-row">${f.languages.map(l => `<span class="pill">${escHtml(l)}</span>`).join('')}</div>` : ''}
    ${f.certifications.length > 0 ? `<div class="section-title">Certifications</div>${f.certifications.map(c => `<div class="cert-item">${escHtml(c)}</div>`).join('')}` : ''}
  </div>
</div>
</body></html>`;
}

export const templateMinimaliste: CvTemplate = {
  id: 'minimaliste',
  label: 'Minimaliste',
  description: 'Blanc épuré, typographie claire et bleue',
  accentColor: '#2563EB',
  build,
};
