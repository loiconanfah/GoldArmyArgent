/**
 * Template 5 – "Classique" : Noir & blanc, typographie sériale, style avocat/consultant.
 * Style: Classic / Traditional (Format classique 1 colonne)
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
@page{size:A4;margin:0;}
*{margin:0;padding:0;box-sizing:border-box;}
html,body{width:210mm;height:297mm;overflow:hidden;}
body{font-family:Georgia,serif;background:#fff;font-size:9.5px;line-height:1.5;-webkit-print-color-adjust:exact;print-color-adjust:exact;color:#111;}
.page{width:210mm;height:297mm;overflow:hidden;background:#fff;padding:28px 40px;display:flex;flex-direction:column;}
.name-block{text-align:center;border-bottom:2px solid #111;padding-bottom:10px;margin-bottom:8px;flex-shrink:0;}
.full-name{font-size:24px;font-weight:700;letter-spacing:4px;text-transform:uppercase;}
.job-title{font-size:10px;font-style:italic;color:#444;margin-top:3px;letter-spacing:1px;}
.contact-bar{display:flex;justify-content:center;flex-wrap:wrap;gap:10px;margin-bottom:10px;padding-bottom:8px;border-bottom:1px solid #ccc;flex-shrink:0;}
.contact-item{display:flex;align-items:center;gap:4px;font-size:8.5px;color:#444;}
.ci{font-size:8.5px;}
.section-title{font-size:9px;font-weight:700;letter-spacing:3px;text-transform:uppercase;border-bottom:1px solid #111;padding-bottom:2px;margin:10px 0 6px;}
.section-title:first-child{margin-top:0;}
.body-layout{display:block;flex:1;overflow:hidden;}
.summary-text{font-size:9.5px;color:#333;line-height:1.6;font-style:italic;}
.exp-block{margin-bottom:10px;page-break-inside:avoid;break-inside:avoid;}
.exp-header{display:flex;justify-content:space-between;align-items:baseline;}
.exp-title{font-size:10.5px;font-weight:700;color:#111;}
.exp-dates{font-size:8px;color:#555;margin-left:8px;white-space:nowrap;}
.exp-company{font-size:9.5px;color:#333;font-style:italic;margin-bottom:3px;}
.exp-loc{color:#888;}
.bullet-row{display:flex;align-items:flex-start;gap:6px;margin-bottom:2px;page-break-inside:avoid;break-inside:avoid;}
.bullet-dot{width:3.5px;height:3.5px;border-radius:50%;background:#111;margin-top:4px;flex-shrink:0;}
.bullet-text{font-size:9px;color:#333;flex:1;line-height:1.45;}
.proj-block{margin-bottom:8px;page-break-inside:avoid;break-inside:avoid;}
.proj-name{font-size:10px;font-weight:700;color:#111;margin-bottom:1px;}
.proj-desc{font-size:9px;color:#555;font-style:italic;}
.edu-degree{font-size:9.5px;font-weight:700;}
.edu-school{font-size:8.5px;color:#444;font-style:italic;}
.edu-meta{font-size:8.5px;color:#888;}
.edu-block{margin-bottom:6px;page-break-inside:avoid;break-inside:avoid;}
.skill-cat{font-size:8px;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;color:#333;margin:5px 0 3px;}
.skill-pills{display:flex;flex-wrap:wrap;gap:3px;margin-bottom:3px;page-break-inside:avoid;break-inside:avoid;}
.pill{background:#F3F4F6;border:1px solid #D1D5DB;border-radius:2px;padding:1px 6px;font-size:8.5px;color:#111;margin:1px 1px;display:inline-block;}
.inline-row{display:flex;flex-wrap:wrap;gap:3px;}
.lang-item{font-size:8.5px;color:#333;margin-bottom:3px;page-break-inside:avoid;break-inside:avoid;}
.cert-item{font-size:8.5px;color:#444;margin-bottom:3px;font-style:italic;page-break-inside:avoid;break-inside:avoid;}
</style></head><body>
<div class="page">
  <div class="name-block">
    <div class="full-name">${escHtml(f.firstName)} ${escHtml(f.lastName)}</div>
    ${f.jobTitle ? `<div class="job-title">${escHtml(f.jobTitle)}</div>` : ''}
  </div>
  <div class="contact-bar">${buildContactItems(f)}</div>
  <div class="body-layout">
    ${f.summary ? `<div class="section-title">Profil Professionnel</div><p class="summary-text">${escHtml(f.summary)}</p>` : ''}
    ${f.experiences.length > 0 ? `<div class="section-title">Expériences</div>${buildExperiencesHtml(f.experiences, '#111')}` : ''}
    ${f.projects.length > 0 ? `<div class="section-title">Projets</div>${buildProjectsHtml(f.projects, '#111')}` : ''}
    ${f.education.length > 0 ? `<div class="section-title">Formation</div>${buildEducationHtml(f.education)}` : ''}
    ${f.skillsHtml ? `<div class="section-title">Compétences</div>${f.skillsHtml}` : ''}
    ${f.languages.length > 0 ? `<div class="section-title">Langues</div><div class="inline-row">${f.languages.map(l => `<span class="pill">${escHtml(l)}</span>`).join('')}</div>` : ''}
    ${f.certifications.length > 0 ? `<div class="section-title">Certifications</div>${f.certifications.map(c => `<div class="cert-item">• ${escHtml(c)}</div>`).join('')}` : ''}
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
