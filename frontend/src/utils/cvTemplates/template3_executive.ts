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
*{margin:0;padding:0;box-sizing:border-box;}
body{font-family:system-ui,sans-serif;background:${DARK};font-size:11px;line-height:1.55;-webkit-print-color-adjust:exact;print-color-adjust:exact;}
.page{max-width:860px;margin:0 auto;background:${DARK};}
.banner{padding:36px 40px;border-bottom:2px solid ${ACCENT};}
.full-name{font-size:38px;font-weight:800;color:#fff;letter-spacing:2px;text-transform:uppercase;}
.job-title{font-size:12px;color:${ACCENT};letter-spacing:3px;margin-top:6px;}
.contact-bar{background:${MID};padding:10px 40px;display:flex;flex-wrap:wrap;gap:16px;}
.contact-item{display:flex;align-items:center;gap:5px;font-size:10px;color:#9CA3AF;}
.ci{font-size:11px;color:${ACCENT};}
.body{padding:28px 40px;background:${DARK};}
.section-title{font-size:10px;font-weight:700;letter-spacing:3px;text-transform:uppercase;color:${ACCENT};margin:22px 0 10px;border-bottom:1px solid #374151;padding-bottom:4px;}
.section-title:first-child{margin-top:0;}
.summary-text{font-size:11px;color:#9CA3AF;line-height:1.7;}
.exp-block{margin-bottom:20px;page-break-inside:avoid;break-inside:avoid;}
.exp-header{display:flex;justify-content:space-between;align-items:baseline;}
.exp-title{font-size:12px;font-weight:700;color:#fff;}
.exp-dates{font-size:9px;color:#6B7280;margin-left:8px;white-space:nowrap;}
.exp-company{font-size:11px;color:${ACCENT};font-weight:600;margin-bottom:5px;}
.exp-loc{color:#6B7280;font-weight:400;}
.bullet-row{display:flex;align-items:flex-start;gap:7px;margin-bottom:3px;page-break-inside:avoid;break-inside:avoid;}
.bullet-dot{width:4px;height:4px;border-radius:1px;background:${ACCENT};margin-top:5px;flex-shrink:0;}
.bullet-text{font-size:11px;color:#9CA3AF;flex:1;line-height:1.55;}
.proj-block{margin-bottom:14px;page-break-inside:avoid;break-inside:avoid;}
.proj-name{font-size:12px;font-weight:700;color:#E5E7EB;margin-bottom:2px;}
.proj-desc{font-size:11px;color:#6B7280;}
.edu-degree{font-size:11px;font-weight:700;color:#E5E7EB;margin-bottom:2px;}
.edu-school{font-size:10px;color:#9CA3AF;}
.edu-meta{font-size:10px;color:#6B7280;}
.edu-block{margin-bottom:10px;page-break-inside:avoid;break-inside:avoid;}
.skill-cat{font-size:9px;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;color:${ACCENT};margin:8px 0 4px;}
.skill-pills{display:flex;flex-wrap:wrap;gap:4px;margin-bottom:4px;page-break-inside:avoid;break-inside:avoid;}
.pill{background:#374151;border:1px solid #4B5563;border-radius:4px;padding:2px 8px;font-size:10px;color:#E5E7EB;margin:2px 2px;display:inline-block;}
.inline-row{display:flex;flex-wrap:wrap;gap:4px;}
.lang-item{font-size:10px;color:#9CA3AF;margin-bottom:4px;padding-left:8px;border-left:2px solid ${ACCENT};page-break-inside:avoid;break-inside:avoid;}
.cert-item{font-size:10px;color:#9CA3AF;margin-bottom:4px;padding-left:8px;border-left:2px solid #4B5563;page-break-inside:avoid;break-inside:avoid;}
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
