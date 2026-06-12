/**
 * Template 6 — Néon Tech
 * Dark background (#0D0D1A), cyan (#00E5FF) + magenta (#FF00A0) neon accents.
 * Format classique monocolonne avec en-tête cyber-glowing.
 */
import { CvTemplate, CvData, ParsedAudit } from './types';
import { escHtml, extractCvFields, buildEducationHtml } from './helpers';

export const templateNeonTech: CvTemplate = {
  id: 'neon_tech',
  label: 'Néon Tech',
  description: 'Dark / Cyber (Format classique 1 colonne)',
  accentColor: '#00E5FF',
  build(cvData: CvData, parsedAudit: ParsedAudit | null): string {
    const f = extractCvFields(cvData, parsedAudit);
    const { firstName, lastName, jobTitle, email, phone, location, linkedin, github, summary,
            experiences, projects, education, languages, certifications, skillsHtml } = f;

    const contact = [
      phone    ? `<div class="ci"><span class="ci-icon">☎</span>${escHtml(phone)}</div>` : '',
      email    ? `<div class="ci"><span class="ci-icon">✉</span>${escHtml(email)}</div>` : '',
      location ? `<div class="ci"><span class="ci-icon">⌖</span>${escHtml(location)}</div>` : '',
      linkedin ? `<div class="ci"><span class="ci-icon">in</span><span class="ci-link">${escHtml(linkedin)}</span></div>` : '',
      github   ? `<div class="ci"><span class="ci-icon">⌾</span>${escHtml(github)}</div>` : '',
    ].filter(Boolean).join('');

    const sec = (label: string) =>
      `<div class="sec-head"><span class="sec-bar"></span><span class="sec-label">${label}</span></div>`;

    const expHtml = experiences.map(exp => `
      <div class="exp-block">
        <div class="exp-top">
          <span class="exp-title">${escHtml(exp.title || '')}</span>
          <span class="exp-dates">${[exp.start_date, exp.end_date].filter(Boolean).map(escHtml).join(' – ')}</span>
        </div>
        <div class="exp-co">${escHtml(exp.company || '')}${exp.location ? ` <span class="exp-loc">· ${escHtml(exp.location)}</span>` : ''}</div>
        ${Array.isArray(exp.bullets) && exp.bullets.length ? exp.bullets.map((b: string) => `<div class="bullet"><span class="bdot">▸</span>${escHtml(b)}</div>`).join('') : ''}
      </div>`).join('');

    const projHtml = projects.map(p => `
      <div class="proj-block">
        <div class="proj-name">${escHtml(p.name || '')}</div>
        ${p.description ? `<div class="proj-desc">${escHtml(p.description)}</div>` : ''}
        ${Array.isArray(p.bullets) && p.bullets.length ? p.bullets.map((b: string) => `<div class="bullet"><span class="bdot">▸</span>${escHtml(b)}</div>`).join('') : ''}
      </div>`).join('');

    return `<!DOCTYPE html><html lang="fr"><head><meta charset="utf-8"/>
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Inter:wght@300;400;600;700&display=swap');
@page{size:A4;margin:0;}
*{margin:0;padding:0;box-sizing:border-box;}
html,body{width:210mm;height:297mm;overflow:hidden;}
body{font-family:'Inter',sans-serif;background:#0D0D1A;color:#E0E0FF;font-size:9.5px;line-height:1.45;-webkit-print-color-adjust:exact;print-color-adjust:exact;}
.page{width:210mm;height:297mm;overflow:hidden;background:#0D0D1A;display:flex;flex-direction:column;}
.banner{background:#111128;padding:16px 32px 12px;border-bottom:1px solid #00E5FF22;text-align:center;flex-shrink:0;}
.avatar-ring{width:44px;height:44px;border-radius:50%;border:2px solid #00E5FF;box-shadow:0 0 10px #00E5FF66;display:flex;align-items:center;justify-content:center;margin:0 auto 8px;background:#1A1A35;}
.avatar-initials{font-family:'Share Tech Mono',monospace;font-size:14px;color:#00E5FF;letter-spacing:2px;}
.name-block{text-align:center;margin-bottom:6px;}
.name-first{font-size:9px;color:#00E5FF;letter-spacing:3px;text-transform:uppercase;}
.name-last{font-family:'Inter',sans-serif;font-size:16px;font-weight:700;color:#fff;letter-spacing:1px;}
.name-title{font-size:8.5px;color:#FF00A0;letter-spacing:1.5px;text-transform:uppercase;margin-top:2px;}
.contact-bar{background:#111128;padding:7px 32px;display:flex;flex-wrap:wrap;justify-content:center;gap:12px;border-bottom:1px solid #00E5FF22;flex-shrink:0;}
.ci{display:flex;align-items:baseline;gap:5px;font-size:8.5px;color:#A0A0CC;}
.ci-icon{font-size:9px;color:#00E5FF;flex-shrink:0;font-family:'Share Tech Mono',monospace;}
.ci-link{color:#00E5FF;font-size:8px;}
.body{padding:14px 32px;background:#0D0D1A;flex:1;overflow:hidden;}
.sec-head{display:flex;align-items:center;gap:6px;margin:10px 0 6px;}
.sec-head:first-child{margin-top:0;}
.sec-bar{width:2px;height:12px;background:linear-gradient(#00E5FF,#FF00A0);border-radius:2px;flex-shrink:0;}
.sec-label{font-size:8px;letter-spacing:3px;text-transform:uppercase;color:#00E5FF;font-family:'Share Tech Mono',monospace;}
.summary-text{font-size:9.5px;color:#C0C0E0;line-height:1.5;}
.exp-block{margin-bottom:10px;padding-left:8px;border-left:2px solid #1A1A3A;page-break-inside:avoid;break-inside:avoid;}
.exp-top{display:flex;justify-content:space-between;align-items:baseline;}
.exp-title{font-size:10.5px;font-weight:700;color:#fff;}
.exp-dates{font-size:8px;color:#00E5FF;font-family:'Share Tech Mono',monospace;}
.exp-co{font-size:8.5px;color:#FF00A0;font-weight:600;margin-bottom:3px;}
.exp-loc{color:#7070AA;font-weight:400;}
.bullet{display:flex;align-items:flex-start;gap:5px;margin-bottom:2px;page-break-inside:avoid;break-inside:avoid;}
.bdot{color:#00E5FF;flex-shrink:0;font-size:8px;margin-top:1px;}
.bullet div,.bullet{font-size:9px;color:#C0C0E0;line-height:1.45;}
.proj-block{margin-bottom:8px;padding:7px 9px;border:1px solid #1A1A3A;border-radius:4px;background:#111128;page-break-inside:avoid;break-inside:avoid;}
.proj-name{font-size:10px;font-weight:700;color:#fff;margin-bottom:2px;}
.proj-desc{font-size:8.5px;color:#9090BB;margin-bottom:3px;}
.edu-block{margin-bottom:6px;page-break-inside:avoid;break-inside:avoid;padding-left:8px;border-left:2px solid #1A1A3A;}
.edu-degree{font-size:9px;font-weight:600;color:#E0E0FF;}
.edu-school{font-size:8.5px;color:#8080AA;}
.edu-meta{font-size:8px;color:#6060AA;}
.skill-cat{font-size:8px;letter-spacing:1.5px;text-transform:uppercase;color:#00E5FF;margin:5px 0 3px;}
.skill-pills{display:flex;flex-wrap:wrap;gap:3px;page-break-inside:avoid;break-inside:avoid;}
.pill{background:#1A1A3A;border:1px solid #00E5FF44;border-radius:2px;padding:1px 6px;font-size:8.5px;color:#C0C0FF;margin:1px 1px;display:inline-block;}
.inline-row{display:flex;flex-wrap:wrap;gap:3px;}
.cert-item{font-size:8.5px;color:#A0A0CC;margin-bottom:3px;padding-left:6px;border-left:2px solid #FF00A0;page-break-inside:avoid;break-inside:avoid;}
</style></head><body>
<div class="page">
  <div class="banner">
    <div class="avatar-ring"><div class="avatar-initials">${escHtml(firstName[0] || '')}${escHtml(lastName[0] || '')}</div></div>
    <div class="name-block">
      <div class="name-first">${escHtml(firstName)}</div>
      <div class="name-last">${escHtml(lastName)}</div>
      ${jobTitle ? `<div class="name-title">${escHtml(jobTitle)}</div>` : ''}
    </div>
  </div>
  ${contact ? `<div class="contact-bar">${contact}</div>` : ''}
  <div class="body">
    ${summary ? `${sec('Profil')}<p class="summary-text">${escHtml(summary)}</p>` : ''}
    ${expHtml ? `${sec('Expériences')}${expHtml}` : ''}
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
