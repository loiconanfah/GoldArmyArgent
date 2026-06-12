/**
 * Template 3 – "Executive" : Tons sombres anthracite, accent vert sauge, look CFO/CTO.
 * Style: Executive Dark (Format classique 1 colonne)
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
  const ACCENT = '#6EE7B7'; // emerald-300
  const DARK   = '#1F2937';
  const MID    = '#374151';

  return `<!DOCTYPE html>
<html lang="fr"><head><meta charset="utf-8"/>
<style>
@page{size:A4;margin:0;}
*{margin:0;padding:0;box-sizing:border-box;}
html,body{width:210mm;height:297mm;overflow:hidden;}
body{font-family:system-ui,sans-serif;background:${DARK};font-size:9.5px;line-height:1.45;-webkit-print-color-adjust:exact;print-color-adjust:exact;}
.page{width:210mm;height:297mm;overflow:hidden;background:${DARK};display:flex;flex-direction:column;}
.banner{padding:20px 32px;border-bottom:2px solid ${ACCENT};flex-shrink:0;}
.full-name{font-size:30px;font-weight:800;color:#fff;letter-spacing:2px;text-transform:uppercase;}
.job-title{font-size:10px;color:${ACCENT};letter-spacing:3px;margin-top:4px;}
.contact-bar{background:${MID};padding:7px 32px;display:flex;flex-wrap:wrap;gap:12px;flex-shrink:0;}
.contact-item{display:flex;align-items:center;gap:4px;font-size:8.5px;color:#9CA3AF;}
.ci{font-size:9px;color:${ACCENT};}
.body{padding:14px 32px;background:${DARK};flex:1;overflow:hidden;}
.section-title{font-size:8px;font-weight:700;letter-spacing:3px;text-transform:uppercase;color:${ACCENT};margin:10px 0 6px;border-bottom:1px solid #374151;padding-bottom:3px;}
.section-title:first-child{margin-top:0;}
.summary-text{font-size:9.5px;color:#9CA3AF;line-height:1.5;}
.exp-block{margin-bottom:10px;page-break-inside:avoid;break-inside:avoid;}
.exp-header{display:flex;justify-content:space-between;align-items:baseline;}
.exp-title{font-size:10.5px;font-weight:700;color:#fff;}
.exp-dates{font-size:8px;color:#6B7280;margin-left:8px;white-space:nowrap;}
.exp-company{font-size:9.5px;color:${ACCENT};font-weight:600;margin-bottom:3px;}
.exp-loc{color:#6B7280;font-weight:400;}
.bullet-row{display:flex;align-items:flex-start;gap:6px;margin-bottom:2px;page-break-inside:avoid;break-inside:avoid;}
.bullet-dot{width:3.5px;height:3.5px;border-radius:1px;background:${ACCENT};margin-top:4px;flex-shrink:0;}
.bullet-text{font-size:9px;color:#9CA3AF;flex:1;line-height:1.45;}
.proj-block{margin-bottom:8px;page-break-inside:avoid;break-inside:avoid;}
.proj-name{font-size:10px;font-weight:700;color:#E5E7EB;margin-bottom:1px;}
.proj-desc{font-size:9px;color:#6B7280;}
.edu-degree{font-size:9.5px;font-weight:700;color:#E5E7EB;margin-bottom:1px;}
.edu-school{font-size:8.5px;color:#9CA3AF;}
.edu-meta{font-size:8.5px;color:#6B7280;}
.edu-block{margin-bottom:6px;page-break-inside:avoid;break-inside:avoid;}
.skill-cat{font-size:8px;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;color:${ACCENT};margin:5px 0 3px;}
.skill-pills{display:flex;flex-wrap:wrap;gap:3px;margin-bottom:3px;page-break-inside:avoid;break-inside:avoid;}
.pill{background:#374151;border:1px solid #4B5563;border-radius:4px;padding:1px 6px;font-size:8.5px;color:#E5E7EB;margin:1px 1px;display:inline-block;}
.inline-row{display:flex;flex-wrap:wrap;gap:3px;}
.lang-item{font-size:8.5px;color:#9CA3AF;margin-bottom:3px;padding-left:6px;border-left:2px solid ${ACCENT};page-break-inside:avoid;break-inside:avoid;}
.cert-item{font-size:8.5px;color:#9CA3AF;margin-bottom:3px;padding-left:6px;border-left:2px solid #4B5563;page-break-inside:avoid;break-inside:avoid;}
</style></head><body>
<div class="page">
  <div class="banner">
    <div class="full-name">${escHtml(f.firstName)} ${escHtml(f.lastName)}</div>
    ${f.jobTitle ? `<div class="job-title">// ${escHtml(f.jobTitle)}</div>` : ''}
  </div>
  ${(f.email || f.phone || f.location || f.linkedin || f.github) ? `<div class="contact-bar">${buildContactItems(f, `color:${ACCENT}`)}</div>` : ''}
  <div class="body">
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

export const templateExecutive: CvTemplate = {
  id: 'executive',
  label: 'Executive',
  description: 'Fond sombre anthracite, accent émeraude — style tech/finance',
  accentColor: '#6EE7B7',
  build,
};
