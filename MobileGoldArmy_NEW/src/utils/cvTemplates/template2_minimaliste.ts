/**
 * Template 2 – "Minimaliste" : Blanc pur, ligne fine bleue, typographie épurée.
 * Style: Clean & Modern
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
*{margin:0;padding:0;box-sizing:border-box;}
body{font-family:system-ui,sans-serif;background:#fff;font-size:11px;line-height:1.55;-webkit-print-color-adjust:exact;print-color-adjust:exact;}
.page{max-width:860px;margin:0 auto;background:#fff;padding:40px 48px;}
.name-row{border-bottom:3px solid ${ACCENT};padding-bottom:12px;margin-bottom:16px;}
.full-name{font-size:36px;font-weight:800;color:#111;letter-spacing:1px;text-transform:uppercase;}
.job-title{font-size:13px;color:${ACCENT};font-weight:600;letter-spacing:2px;margin-top:4px;}
.contact-bar{display:flex;flex-wrap:wrap;gap:18px;margin-bottom:24px;}
.contact-item{display:flex;align-items:center;gap:5px;font-size:10px;color:#555;}
.ci{font-size:11px;color:${ACCENT};}
.section-title{font-size:10px;font-weight:800;letter-spacing:3px;text-transform:uppercase;color:${ACCENT};border-bottom:1.5px solid ${ACCENT};padding-bottom:3px;margin:20px 0 10px;}
.summary-text{font-size:11px;color:#444;line-height:1.7;}
.body-layout{display:grid;grid-template-columns:1fr 260px;gap:32px;}
.exp-block{margin-bottom:18px;page-break-inside:avoid;break-inside:avoid;}
.exp-header{display:flex;justify-content:space-between;align-items:baseline;}
.exp-title{font-size:12px;font-weight:700;color:#111;}
.exp-dates{font-size:9px;color:#888;white-space:nowrap;margin-left:8px;}
.exp-company{font-size:11px;color:${ACCENT};font-weight:600;margin-bottom:5px;}
.exp-loc{color:#888;font-weight:400;}
.bullet-row{display:flex;align-items:flex-start;gap:7px;margin-bottom:3px;page-break-inside:avoid;break-inside:avoid;}
.bullet-dot{width:4px;height:4px;border-radius:50%;background:${ACCENT};margin-top:5px;flex-shrink:0;}
.bullet-text{font-size:11px;color:#444;flex:1;line-height:1.55;}
.proj-block{margin-bottom:14px;page-break-inside:avoid;break-inside:avoid;}
.proj-name{font-size:12px;font-weight:700;color:#111;margin-bottom:2px;}
.proj-desc{font-size:11px;color:#555;}
.edu-block{margin-bottom:10px;page-break-inside:avoid;break-inside:avoid;}
.edu-degree{font-size:11px;font-weight:700;color:#111;}
.edu-school{font-size:10px;color:#555;}
.edu-meta{font-size:10px;color:#888;}
.skill-cat{font-size:9px;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;color:${ACCENT};margin:8px 0 4px;}
.skill-pills{display:flex;flex-wrap:wrap;gap:4px;margin-bottom:4px;page-break-inside:avoid;break-inside:avoid;}
.pill{background:#EFF6FF;border:1px solid #BFDBFE;border-radius:4px;padding:2px 8px;font-size:10px;color:#1D4ED8;font-weight:500;}
.lang-item{font-size:10px;color:#333;margin-bottom:4px;padding-left:10px;border-left:2px solid ${ACCENT};page-break-inside:avoid;break-inside:avoid;}
.cert-item{font-size:10px;color:#444;margin-bottom:4px;padding-left:10px;border-left:2px solid #ddd;page-break-inside:avoid;break-inside:avoid;}
</style></head><body>
<div class="page">
  <div class="name-row">
    <div class="full-name">${escHtml(f.firstName)} <strong>${escHtml(f.lastName)}</strong></div>
    ${f.jobTitle ? `<div class="job-title">${escHtml(f.jobTitle)}</div>` : ''}
  </div>
  <div class="contact-bar">${buildContactItems(f, `color:${ACCENT}`)}</div>
  ${f.summary ? `<p class="summary-text">${escHtml(f.summary)}</p>` : ''}
  <div class="body-layout">
    <div>
      ${f.experiences.length > 0 ? `<div class="section-title">Expériences</div>${buildExperiencesHtml(f.experiences, ACCENT)}` : ''}
      ${f.projects.length > 0 ? `<div class="section-title">Projets</div>${buildProjectsHtml(f.projects, ACCENT)}` : ''}
    </div>
    <div>
      ${f.education.length > 0 ? `<div class="section-title">Formation</div>${buildEducationHtml(f.education)}` : ''}
      ${f.skillsHtml ? `<div class="section-title">Compétences</div>${f.skillsHtml}` : ''}
      ${f.languages.length > 0 ? `<div class="section-title">Langues</div>${f.languages.map(l => `<div class="lang-item">${escHtml(l)}</div>`).join('')}` : ''}
      ${f.certifications.length > 0 ? `<div class="section-title">Certifications</div>${f.certifications.map(c => `<div class="cert-item">${escHtml(c)}</div>`).join('')}` : ''}
    </div>
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
