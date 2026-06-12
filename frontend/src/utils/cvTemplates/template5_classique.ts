/**
 * Template 5 – "Classique" : Noir & blanc, typographie sériale, style avocat/consultant.
 * Style: Classic / Traditional
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

  return `<!DOCTYPE html>
<html lang="fr"><head><meta charset="utf-8"/>
<style>
*{margin:0;padding:0;box-sizing:border-box;}
body{font-family:Georgia,serif;background:#fff;font-size:11px;line-height:1.6;-webkit-print-color-adjust:exact;print-color-adjust:exact;color:#111;}
.page{max-width:860px;margin:0 auto;background:#fff;padding:44px 52px;}
.name-block{text-align:center;border-bottom:2px solid #111;padding-bottom:14px;margin-bottom:12px;}
.full-name{font-size:30px;font-weight:700;letter-spacing:4px;text-transform:uppercase;}
.job-title{font-size:12px;font-style:italic;color:#444;margin-top:4px;letter-spacing:1px;}
.contact-bar{display:flex;justify-content:center;flex-wrap:wrap;gap:14px;margin-bottom:20px;padding-bottom:12px;border-bottom:1px solid #ccc;}
.contact-item{display:flex;align-items:center;gap:4px;font-size:10px;color:#444;}
.ci{font-size:10px;}
.section-title{font-size:11px;font-weight:700;letter-spacing:3px;text-transform:uppercase;border-bottom:1px solid #111;padding-bottom:3px;margin:18px 0 10px;}
.body-layout{display:grid;grid-template-columns:1fr 220px;gap:28px;}
.summary-text{font-size:11px;color:#333;line-height:1.75;font-style:italic;}
.exp-block{margin-bottom:18px;page-break-inside:avoid;break-inside:avoid;}
.exp-header{display:flex;justify-content:space-between;align-items:baseline;}
.exp-title{font-size:12px;font-weight:700;color:#111;}
.exp-dates{font-size:9px;color:#555;margin-left:8px;white-space:nowrap;}
.exp-company{font-size:11px;color:#333;font-style:italic;margin-bottom:5px;}
.exp-loc{color:#888;}
.bullet-row{display:flex;align-items:flex-start;gap:8px;margin-bottom:3px;page-break-inside:avoid;break-inside:avoid;}
.bullet-dot{width:4px;height:4px;border-radius:50%;background:#111;margin-top:5px;flex-shrink:0;}
.bullet-text{font-size:11px;color:#333;flex:1;line-height:1.6;}
.proj-block{margin-bottom:14px;page-break-inside:avoid;break-inside:avoid;}
.proj-name{font-size:12px;font-weight:700;color:#111;margin-bottom:2px;}
.proj-desc{font-size:11px;color:#555;font-style:italic;}
.edu-degree{font-size:11px;font-weight:700;}
.edu-school{font-size:10px;color:#444;font-style:italic;}
.edu-meta{font-size:10px;color:#888;}
.edu-block{margin-bottom:10px;page-break-inside:avoid;break-inside:avoid;}
.skill-cat{font-size:9px;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;color:#333;margin:8px 0 4px;}
.skill-pills{display:flex;flex-wrap:wrap;gap:4px;margin-bottom:4px;page-break-inside:avoid;break-inside:avoid;}
.pill{background:#F3F4F6;border:1px solid #D1D5DB;border-radius:2px;padding:2px 7px;font-size:10px;color:#111;}
.lang-item{font-size:10px;color:#333;margin-bottom:4px;page-break-inside:avoid;break-inside:avoid;}
.cert-item{font-size:10px;color:#444;margin-bottom:4px;font-style:italic;page-break-inside:avoid;break-inside:avoid;}
</style></head><body>
<div class="page">
  <div class="name-block">
    <div class="full-name">${escHtml(f.firstName)} ${escHtml(f.lastName)}</div>
    ${f.jobTitle ? `<div class="job-title">${escHtml(f.jobTitle)}</div>` : ''}
  </div>
  <div class="contact-bar">${buildContactItems(f)}</div>
  ${f.summary ? `<div class="section-title">Profil Professionnel</div><p class="summary-text">${escHtml(f.summary)}</p>` : ''}
  <div class="body-layout">
    <div>
      ${f.experiences.length > 0 ? `<div class="section-title">Expériences</div>${buildExperiencesHtml(f.experiences, '#111')}` : ''}
      ${f.projects.length > 0 ? `<div class="section-title">Projets</div>${buildProjectsHtml(f.projects, '#111')}` : ''}
    </div>
    <div>
      ${f.education.length > 0 ? `<div class="section-title">Formation</div>${buildEducationHtml(f.education)}` : ''}
      ${f.skillsHtml ? `<div class="section-title">Compétences</div>${f.skillsHtml}` : ''}
      ${f.languages.length > 0 ? `<div class="section-title">Langues</div>${f.languages.map(l => `<div class="lang-item">• ${escHtml(l)}</div>`).join('')}` : ''}
      ${f.certifications.length > 0 ? `<div class="section-title">Certifications</div>${f.certifications.map(c => `<div class="cert-item">• ${escHtml(c)}</div>`).join('')}` : ''}
    </div>
  </div>
</div>
</body></html>`;
}

export const templateClassique: CvTemplate = {
  id: 'classique',
  label: 'Classique',
  description: 'Noir & blanc, police sériale — consultant, juriste, finance',
  accentColor: '#1a1a1a',
  build,
};
