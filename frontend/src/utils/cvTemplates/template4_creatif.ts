/**
 * Template 4 – "Créatif" : Violet foncé + rose accent, format classique monocolonne.
 * Style: Creative / Design (Format classique 1 colonne)
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
  const ACCENT  = '#EC4899'; // pink-500
  const PURPLE  = '#5B21B6'; // violet-800

  return `<!DOCTYPE html>
<html lang="fr"><head><meta charset="utf-8"/>
<style>
*{margin:0;padding:0;box-sizing:border-box;}
body{font-family:system-ui,sans-serif;background:#fff;font-size:11px;line-height:1.55;-webkit-print-color-adjust:exact;print-color-adjust:exact;}
.page{max-width:860px;margin:0 auto;background:#fff;}
.header{background:${PURPLE};color:#fff;padding:32px 40px;position:relative;overflow:hidden;}
.header::after{content:'';position:absolute;right:-60px;top:-60px;width:250px;height:250px;border-radius:50%;background:rgba(236,72,153,0.2);}
.header-inner{position:relative;z-index:1;}
.first-name{font-size:14px;font-weight:300;letter-spacing:8px;text-transform:uppercase;color:rgba(255,255,255,0.65);}
.last-name{font-size:38px;font-weight:900;letter-spacing:3px;text-transform:uppercase;}
.job-title{font-size:12px;color:${ACCENT};letter-spacing:2px;font-weight:600;margin-top:6px;}
.pink-bar{background:${ACCENT};height:4px;}
.contact-bar{background:#F9FAFB;padding:10px 40px;display:flex;flex-wrap:wrap;gap:16px;border-bottom:1px solid #E5E7EB;}
.contact-item{display:flex;align-items:center;gap:5px;font-size:10px;color:#555;}
.ci{font-size:11px;color:${ACCENT};}
.body{padding:28px 40px;background:#ffffff;}
.exp-section-title{font-size:10px;font-weight:800;letter-spacing:2px;text-transform:uppercase;color:${PURPLE};border-bottom:2px solid ${ACCENT};padding-bottom:3px;margin:20px 0 10px;}
.exp-section-title:first-child{margin-top:0;}
.summary-text{font-size:11px;color:#444;line-height:1.7;}
.exp-block{margin-bottom:20px;page-break-inside:avoid;break-inside:avoid;}
.exp-header{display:flex;justify-content:space-between;align-items:baseline;}
.exp-title{font-size:12px;font-weight:700;color:${PURPLE};}
.exp-dates{font-size:9px;color:#888;margin-left:8px;white-space:nowrap;}
.exp-company{font-size:11px;color:${ACCENT};font-weight:600;margin-bottom:5px;}
.exp-loc{color:#888;font-weight:400;}
.bullet-row{display:flex;align-items:flex-start;gap:7px;margin-bottom:3px;page-break-inside:avoid;break-inside:avoid;}
.bullet-dot{width:5px;height:5px;border-radius:50%;background:${ACCENT};margin-top:4px;flex-shrink:0;}
.bullet-text{font-size:11px;color:#444;flex:1;line-height:1.55;}
.proj-block{margin-bottom:14px;page-break-inside:avoid;break-inside:avoid;}
.proj-name{font-size:12px;font-weight:700;color:${PURPLE};margin-bottom:2px;}
.proj-desc{font-size:11px;color:#555;}
.edu-degree{font-size:11px;font-weight:700;color:${PURPLE};}
.edu-school{font-size:10px;color:#555;}
.edu-meta{font-size:10px;color:#888;}
.edu-block{margin-bottom:10px;page-break-inside:avoid;break-inside:avoid;}
.skill-cat{font-size:9px;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;color:${ACCENT};margin:8px 0 4px;}
.skill-pills{display:flex;flex-wrap:wrap;gap:4px;margin-bottom:4px;page-break-inside:avoid;break-inside:avoid;}
.pill{background:#fff;border:1.5px solid ${PURPLE};border-radius:12px;padding:2px 9px;font-size:10px;color:${PURPLE};font-weight:600;margin:2px 2px;display:inline-block;}
.inline-row{display:flex;flex-wrap:wrap;gap:4px;}
.cert-item{font-size:10px;color:#555;margin-bottom:4px;padding-left:8px;border-left:2px solid #DDD6FE;page-break-inside:avoid;break-inside:avoid;}
</style></head><body>
<div class="page">
  <div class="header">
    <div class="header-inner">
      <div class="first-name">${escHtml(f.firstName)}</div>
      <div class="last-name">${escHtml(f.lastName)}</div>
      ${f.jobTitle ? `<div class="job-title">✦ ${escHtml(f.jobTitle)}</div>` : ''}
    </div>
  </div>
  <div class="pink-bar"></div>
  ${(f.email || f.phone || f.location || f.linkedin || f.github) ? `<div class="contact-bar">${buildContactItems(f, `color:${ACCENT}`)}</div>` : ''}
  <div class="body">
    ${f.summary ? `<div class="exp-section-title">Profil</div><p class="summary-text">${escHtml(f.summary)}</p>` : ''}
    ${f.experiences.length > 0 ? `<div class="exp-section-title">Expériences</div>${buildExperiencesHtml(f.experiences, ACCENT)}` : ''}
    ${f.projects.length > 0 ? `<div class="exp-section-title">Projets</div>${buildProjectsHtml(f.projects, ACCENT)}` : ''}
    ${f.education.length > 0 ? `<div class="exp-section-title">Formation</div>${buildEducationHtml(f.education)}` : ''}
    ${f.skillsHtml ? `<div class="exp-section-title">Compétences</div>${f.skillsHtml}` : ''}
    ${f.languages.length > 0 ? `<div class="exp-section-title">Langues</div><div class="inline-row">${f.languages.map(l => `<span class="pill">${escHtml(l)}</span>`).join('')}</div>` : ''}
    ${f.certifications.length > 0 ? `<div class="exp-section-title">Certifications</div>${f.certifications.map(c => `<div class="cert-item">${escHtml(c)}</div>`).join('')}` : ''}
  </div>
</div>
</body></html>`;
}

export const templateCreatif: CvTemplate = {
  id: 'creatif',
  label: 'Créatif',
  description: 'Violet & rose — idéal pour les métiers créatifs & design',
  accentColor: '#EC4899',
  build,
};
