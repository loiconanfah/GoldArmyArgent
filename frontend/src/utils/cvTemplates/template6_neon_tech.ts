/**
 * Template 6 — Néon Tech
 * Dark background (#0D0D1A), cyan (#00E5FF) + magenta (#FF00A0) neon accents,
 * left sidebar with glowing borders. Futuristic / developer / startup look.
 */
import { CvTemplate, CvData, ParsedAudit } from './types';
import { escHtml, extractCvFields, buildEducationHtml } from './helpers';

export const templateNeonTech: CvTemplate = {
  id: 'neon_tech',
  label: 'Néon Tech',
  description: 'Dark / Cyber',
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
    ].join('');

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
*{margin:0;padding:0;box-sizing:border-box;}
body{font-family:'Inter',sans-serif;background:#0D0D1A;color:#E0E0FF;font-size:11px;line-height:1.5;-webkit-print-color-adjust:exact;print-color-adjust:exact;}
.page{max-width:860px;margin:0 auto;display:flex;min-height:100vh;}
/* Sidebar */
.sidebar{width:230px;flex-shrink:0;background:#111128;border-right:1px solid #00E5FF22;padding:30px 20px;}
.avatar-ring{width:72px;height:72px;border-radius:50%;border:2px solid #00E5FF;box-shadow:0 0 16px #00E5FF66;display:flex;align-items:center;justify-content:center;margin:0 auto 14px;background:#1A1A35;}
.avatar-initials{font-family:'Share Tech Mono',monospace;font-size:22px;color:#00E5FF;letter-spacing:2px;}
.name-block{text-align:center;margin-bottom:20px;}
.name-first{font-size:11px;color:#00E5FF;letter-spacing:3px;text-transform:uppercase;}
.name-last{font-family:'Inter',sans-serif;font-size:20px;font-weight:700;color:#fff;letter-spacing:1px;}
.name-title{font-size:10px;color:#FF00A0;letter-spacing:1.5px;text-transform:uppercase;margin-top:4px;}
/* Contact */
.ci{display:flex;align-items:baseline;gap:6px;font-size:10px;color:#A0A0CC;margin-bottom:5px;word-break:break-all;}
.ci-icon{font-size:11px;color:#00E5FF;flex-shrink:0;font-family:'Share Tech Mono',monospace;}
.ci-link{color:#00E5FF;font-size:9px;}
/* Sidebar sections */
.sb-sec{margin-top:18px;}
.sb-sec-title{font-size:9px;letter-spacing:3px;text-transform:uppercase;color:#FF00A0;margin-bottom:8px;border-bottom:1px solid #FF00A033;padding-bottom:4px;}
.edu-block{margin-bottom:10px;}
.edu-degree{font-size:10px;font-weight:600;color:#E0E0FF;}
.edu-school{font-size:10px;color:#8080AA;}
.edu-meta{font-size:9px;color:#6060AA;}
.skill-cat{font-size:9px;letter-spacing:1.5px;text-transform:uppercase;color:#00E5FF;margin:8px 0 4px;}
.skill-pills{display:flex;flex-wrap:wrap;gap:3px;}
.pill{background:#1A1A3A;border:1px solid #00E5FF44;border-radius:2px;padding:2px 7px;font-size:9px;color:#C0C0FF;}
.lang-row{display:flex;align-items:center;gap:6px;margin-bottom:4px;font-size:10px;color:#A0A0CC;}
.lang-dot{width:6px;height:6px;border-radius:50%;background:#FF00A0;flex-shrink:0;box-shadow:0 0 6px #FF00A0;}
.cert-item{font-size:10px;color:#A0A0CC;margin-bottom:4px;padding-left:8px;border-left:2px solid #FF00A0;}
/* Main */
.main{flex:1;padding:30px 28px;background:#0D0D1A;}
.sec-head{display:flex;align-items:center;gap:8px;margin:18px 0 10px;}
.sec-head:first-child{margin-top:0;}
.sec-bar{width:3px;height:14px;background:linear-gradient(#00E5FF,#FF00A0);border-radius:2px;flex-shrink:0;}
.sec-label{font-size:9px;letter-spacing:3px;text-transform:uppercase;color:#00E5FF;font-family:'Share Tech Mono',monospace;}
.summary-text{font-size:11px;color:#C0C0E0;line-height:1.7;}
.exp-block{margin-bottom:18px;padding-left:10px;border-left:2px solid #1A1A3A;}
.exp-top{display:flex;justify-content:space-between;align-items:baseline;}
.exp-title{font-size:12px;font-weight:700;color:#fff;}
.exp-dates{font-size:9px;color:#00E5FF;font-family:'Share Tech Mono',monospace;}
.exp-co{font-size:10px;color:#FF00A0;font-weight:600;margin-bottom:5px;}
.exp-loc{color:#7070AA;font-weight:400;}
.bullet{display:flex;align-items:flex-start;gap:6px;margin-bottom:3px;}
.bdot{color:#00E5FF;flex-shrink:0;font-size:9px;margin-top:1px;}
.bullet div,.bullet{font-size:11px;color:#C0C0E0;line-height:1.55;}
.proj-block{margin-bottom:14px;padding:10px 12px;border:1px solid #1A1A3A;border-radius:4px;background:#111128;}
.proj-name{font-size:12px;font-weight:700;color:#fff;margin-bottom:4px;}
.proj-desc{font-size:11px;color:#9090BB;margin-bottom:5px;}
</style></head><body>
<div class="page">
  <div class="sidebar">
    <div class="avatar-ring"><div class="avatar-initials">${escHtml(firstName[0] || '')}${escHtml(lastName[0] || '')}</div></div>
    <div class="name-block">
      <div class="name-first">${escHtml(firstName)}</div>
      <div class="name-last">${escHtml(lastName)}</div>
      ${jobTitle ? `<div class="name-title">${escHtml(jobTitle)}</div>` : ''}
    </div>
    ${contact ? contact : ''}
    ${education.length ? `<div class="sb-sec"><div class="sb-sec-title">Formation</div>${buildEducationHtml(education)}</div>` : ''}
    ${skillsHtml ? `<div class="sb-sec"><div class="sb-sec-title">Compétences</div>${skillsHtml}</div>` : ''}
    ${languages.length ? `<div class="sb-sec"><div class="sb-sec-title">Langues</div>${languages.map(l => `<div class="lang-row"><div class="lang-dot"></div>${escHtml(l)}</div>`).join('')}</div>` : ''}
    ${certifications.length ? `<div class="sb-sec"><div class="sb-sec-title">Certifications</div>${certifications.map(c => `<div class="cert-item">${escHtml(c)}</div>`).join('')}</div>` : ''}
  </div>
  <div class="main">
    ${summary ? `${sec('Profil')}<p class="summary-text">${escHtml(summary)}</p>` : ''}
    ${expHtml ? `${sec('Expériences')}${expHtml}` : ''}
    ${projHtml ? `${sec('Projets')}${projHtml}` : ''}
  </div>
</div>
</body></html>`;
  }
};
