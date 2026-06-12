/**
 * Template 8 — Timeline (Format classique monocolonne)
 * En-tête sombre avec accent corail #E85D4A + slate.
 * Format classique 1 colonne.
 */
import { CvTemplate, CvData, ParsedAudit } from './types';
import { escHtml, extractCvFields, buildEducationHtml } from './helpers';

export const templateTimeline: CvTemplate = {
  id: 'timeline',
  label: 'Timeline',
  description: 'Timeline (Format classique 1 colonne)',
  accentColor: '#E85D4A',
  build(cvData: CvData, parsedAudit: ParsedAudit | null): string {
    const f = extractCvFields(cvData, parsedAudit);
    const { firstName, lastName, jobTitle, email, phone, location, linkedin, github, summary,
            experiences, projects, education, languages, certifications, skillsHtml } = f;

    const contact = [
      email    ? `<div class="ct-item"><span class="ct-ic">✉</span>${escHtml(email)}</div>` : '',
      phone    ? `<div class="ct-item"><span class="ct-ic">☎</span>${escHtml(phone)}</div>` : '',
      location ? `<div class="ct-item"><span class="ct-ic">⌖</span>${escHtml(location)}</div>` : '',
      linkedin ? `<div class="ct-item ct-li"><span class="ct-ic">in</span><span class="ct-link">${escHtml(linkedin)}</span></div>` : '',
      github   ? `<div class="ct-item"><span class="ct-ic">⌾</span>${escHtml(github)}</div>` : '',
    ].filter(Boolean).join('');

    const sec = (label: string) =>
      `<div class="sec-head"><span class="sec-label">${label}</span></div>`;

    const expHtml = experiences.map(exp => `
      <div class="exp-block">
        <div class="exp-header">
          <div class="exp-title">${escHtml(exp.title)}</div>
          <div class="exp-dates">${[exp.start_date, exp.end_date].filter(Boolean).map(escHtml).join(' – ')}</div>
        </div>
        <div class="exp-company">${escHtml(exp.company)}${exp.location ? ` <span class="exp-loc">· ${escHtml(exp.location)}</span>` : ''}</div>
        ${Array.isArray(exp.bullets) && exp.bullets.length > 0 ? exp.bullets.map((b: string) => `
          <div class="bullet-row"><div class="bullet-dot"></div><div class="bullet-text">${escHtml(b)}</div></div>
        `).join('') : ''}
      </div>`).join('');

    const projHtml = projects.map(p => `
      <div class="proj-block">
        <div class="proj-name">${escHtml(p.name)}</div>
        ${p.description ? `<div class="proj-desc">${escHtml(p.description)}</div>` : ''}
        ${Array.isArray(p.bullets) && p.bullets.length > 0 ? p.bullets.map((b: string) => `
          <div class="bullet-row"><div class="bullet-dot"></div><div class="bullet-text">${escHtml(b)}</div></div>
        `).join('') : ''}
      </div>`).join('');

    return `<!DOCTYPE html><html lang="fr"><head><meta charset="utf-8"/>
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@300;400;600;700;800&family=Playfair+Display:wght@700&display=swap');
*{margin:0;padding:0;box-sizing:border-box;}
body{font-family:'Nunito',sans-serif;background:#F9F5F0;color:#2D2D2D;font-size:11px;line-height:1.55;-webkit-print-color-adjust:exact;print-color-adjust:exact;}
.page{max-width:900px;margin:0 auto;background:#fff;}
.hdr{background:#2D2D2D;padding:32px 48px;display:flex;justify-content:space-between;align-items:center;}
.hdr-left{}
.hdr-name{font-family:'Playfair Display',serif;font-size:36px;color:#fff;letter-spacing:1px;}
.hdr-title{font-size:12px;color:#E85D4A;letter-spacing:3px;text-transform:uppercase;margin-top:4px;font-weight:600;}
.hdr-right{text-align:right;}
.ct-item{display:flex;align-items:baseline;gap:6px;font-size:10px;color:#BBBBBB;margin-bottom:4px;justify-content:flex-end;}
.ct-ic{color:#E85D4A;font-weight:700;min-width:14px;text-align:center;}
.ct-li{align-items:flex-start;}
.ct-link{color:#E85D4A;font-size:9px;word-break:break-all;}
.summary-band{background:#fff;border-left:4px solid #E85D4A;padding:16px 48px;margin:0;font-size:11.5px;color:#555;line-height:1.75;font-style:italic;}
.body{padding:28px 48px;background:#fff;}
.sec-head{margin:22px 0 10px;border-bottom:2px solid #E85D4A;padding-bottom:4px;}
.sec-label{font-size:11px;letter-spacing:3px;text-transform:uppercase;color:#E85D4A;font-weight:700;}
.exp-block{margin-bottom:18px;page-break-inside:avoid;break-inside:avoid;}
.exp-header{display:flex;justify-content:space-between;align-items:baseline;}
.exp-title{font-size:12px;font-weight:700;color:#2D2D2D;}
.exp-dates{font-size:9.5px;color:#E85D4A;font-weight:700;}
.exp-company{font-size:11px;color:#888;font-weight:600;margin-bottom:5px;}
.exp-loc{color:#BBB;}
.bullet-row{display:flex;align-items:flex-start;gap:7px;margin-bottom:3px;page-break-inside:avoid;break-inside:avoid;}
.bullet-dot{width:4px;height:4px;border-radius:50%;background:#E85D4A;margin-top:5px;flex-shrink:0;}
.bullet-text{font-size:11px;color:#555;flex:1;line-height:1.55;}
.proj-block{margin-bottom:14px;page-break-inside:avoid;break-inside:avoid;}
.proj-name{font-size:12px;font-weight:700;color:#2D2D2D;margin-bottom:2px;}
.proj-desc{font-size:11px;color:#666;}
.edu-block{margin-bottom:10px;page-break-inside:avoid;break-inside:avoid;}
.edu-degree{font-size:11px;font-weight:700;color:#2D2D2D;}
.edu-school{font-size:10px;color:#888;}
.edu-meta{font-size:10px;color:#BBB;}
.skill-cat{font-size:9px;text-transform:uppercase;letter-spacing:1px;color:#888;margin:6px 0 3px;font-weight:600;}
.skill-pills{display:flex;flex-wrap:wrap;gap:3px;page-break-inside:avoid;break-inside:avoid;}
.pill{background:#fff;border:1px solid #DDD;border-radius:10px;padding:2px 8px;font-size:9px;color:#555;margin:2px 2px;display:inline-block;}
.inline-row{display:flex;flex-wrap:wrap;gap:4px;}
.lang-item{font-size:10px;color:#666;margin-bottom:3px;page-break-inside:avoid;break-inside:avoid;}
.cert-item{font-size:10px;color:#666;margin-bottom:4px;padding-left:8px;border-left:2px solid #E85D4A;page-break-inside:avoid;break-inside:avoid;}
</style></head><body>
<div class="page">
  <div class="hdr">
    <div class="hdr-left">
      <div class="hdr-name">${escHtml(firstName)} ${escHtml(lastName)}</div>
      ${jobTitle ? `<div class="hdr-title">${escHtml(jobTitle)}</div>` : ''}
    </div>
    <div class="hdr-right">${contact}</div>
  </div>
  ${summary ? `<div class="summary-band">${escHtml(summary)}</div>` : ''}
  <div class="body">
    ${expHtml ? `${sec('Parcours Professionnel')}${expHtml}` : ''}
    ${projHtml ? `${sec('Projets')}${projHtml}` : ''}
    ${education.length ? `${sec('Formation')}${buildEducationHtml(education)}` : ''}
    ${skillsHtml ? `${sec('Compétences')}${skillsHtml}` : ''}
    ${languages.length ? `${sec('Langues')}<div class="inline-row">${languages.map(l => `<span class="pill">${escHtml(l)}</span>`).join('')}</div>` : ''}
    ${certifications.length ? `${sec('Certifications')}${certifications.map(c => `<div class="cert-item">${escHtml(c)}</div>`).join('')}` : ''}
  </div>
</div>
</body></html>`;
  }
};
