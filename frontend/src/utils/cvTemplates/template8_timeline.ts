/**
 * Template 8 — Timeline Infographique
 * Vertical timeline center spine, alternating left/right content cards,
 * bold colored decade markers, card shadows. Warm coral #E85D4A + slate.
 * Unique infographic/visual style — great for portfolio, design, marketing.
 */
import { CvTemplate, CvData, ParsedAudit } from './types';
import { escHtml, extractCvFields, buildEducationHtml } from './helpers';

export const templateTimeline: CvTemplate = {
  id: 'timeline',
  label: 'Timeline',
  description: 'Infographique',
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
    ].join('');

    // Timeline entries from experiences + projects merged
    const timelineItems = [
      ...experiences.map(exp => ({
        type: 'exp',
        title: exp.title || '',
        sub: exp.company || '',
        loc: exp.location || '',
        dates: [exp.start_date, exp.end_date].filter(Boolean).map(escHtml).join(' – '),
        bullets: exp.bullets || [],
      })),
      ...projects.map(p => ({
        type: 'proj',
        title: p.name || '',
        sub: '',
        loc: '',
        dates: '',
        desc: p.description || '',
        bullets: p.bullets || [],
      })),
    ];

    const timelineHtml = timelineItems.map((item, i) => {
      const side = i % 2 === 0 ? 'left' : 'right';
      const bulletRows = item.bullets.length
        ? `<ul class="tl-bullets">${item.bullets.map((b: string) => `<li>${escHtml(b)}</li>`).join('')}</ul>` : '';
      const cardContent = `
        <div class="tl-card">
          ${item.dates ? `<div class="tl-dates">${item.dates}</div>` : ''}
          <div class="tl-title">${escHtml(item.title)}</div>
          ${item.sub ? `<div class="tl-sub">${escHtml(item.sub)}${item.loc ? ` <span class="tl-loc">· ${escHtml(item.loc)}</span>` : ''}</div>` : ''}
          ${(item as any).desc ? `<div class="tl-desc">${escHtml((item as any).desc)}</div>` : ''}
          ${bulletRows}
        </div>`;
      const typeLabel = item.type === 'proj' ? '★' : '●';
      return `
        <div class="tl-row ${side}">
          <div class="tl-side tl-${side}">${side === 'left' ? cardContent : ''}</div>
          <div class="tl-center">
            <div class="tl-node">${typeLabel}</div>
          </div>
          <div class="tl-side tl-${side === 'left' ? 'right' : 'left'}">${side === 'right' ? cardContent : ''}</div>
        </div>`;
    }).join('');

    return `<!DOCTYPE html><html lang="fr"><head><meta charset="utf-8"/>
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@300;400;600;700;800&family=Playfair+Display:wght@700&display=swap');
*{margin:0;padding:0;box-sizing:border-box;}
body{font-family:'Nunito',sans-serif;background:#F9F5F0;color:#2D2D2D;font-size:11px;line-height:1.55;-webkit-print-color-adjust:exact;print-color-adjust:exact;}
.page{max-width:900px;margin:0 auto;}
/* Header strip */
.hdr{background:#2D2D2D;padding:32px 48px;display:flex;justify-content:space-between;align-items:center;}
.hdr-left{}
.hdr-name{font-family:'Playfair Display',serif;font-size:36px;color:#fff;letter-spacing:1px;}
.hdr-title{font-size:12px;color:#E85D4A;letter-spacing:3px;text-transform:uppercase;margin-top:4px;font-weight:600;}
.hdr-right{text-align:right;}
/* Contact */
.ct-item{display:flex;align-items:baseline;gap:6px;font-size:10px;color:#BBBBBB;margin-bottom:4px;justify-content:flex-end;}
.ct-ic{color:#E85D4A;font-weight:700;min-width:14px;text-align:center;}
.ct-li{align-items:flex-start;}
.ct-link{color:#E85D4A;font-size:9px;word-break:break-all;}
/* Summary band */
.summary-band{background:#fff;border-left:4px solid #E85D4A;padding:16px 48px;margin:0;font-size:11.5px;color:#555;line-height:1.75;font-style:italic;}
/* Skill + meta row */
.meta-row{display:flex;gap:0;background:#F0EBE3;}
.meta-cell{flex:1;padding:20px 24px;border-right:1px solid #E5DDD5;page-break-inside:avoid;break-inside:avoid;}
.meta-cell:last-child{border-right:none;}
.meta-title{font-size:9px;letter-spacing:2.5px;text-transform:uppercase;color:#E85D4A;font-weight:700;margin-bottom:8px;}
.skill-cat{font-size:9px;text-transform:uppercase;letter-spacing:1px;color:#888;margin:6px 0 3px;font-weight:600;}
.skill-pills{display:flex;flex-wrap:wrap;gap:3px;page-break-inside:avoid;break-inside:avoid;}
.pill{background:#fff;border:1px solid #DDD;border-radius:10px;padding:2px 8px;font-size:9px;color:#555;}
.lang-item{font-size:10px;color:#666;margin-bottom:3px;page-break-inside:avoid;break-inside:avoid;}
.cert-item{font-size:10px;color:#666;margin-bottom:4px;padding-left:8px;border-left:2px solid #E85D4A;page-break-inside:avoid;break-inside:avoid;}
/* Timeline */
.tl-container{padding:32px 0;}
.tl-header{text-align:center;margin-bottom:20px;}
.tl-header-title{font-size:11px;letter-spacing:4px;text-transform:uppercase;color:#E85D4A;font-weight:700;}
.tl-row{display:flex;align-items:flex-start;position:relative;page-break-inside:avoid;break-inside:avoid;}
.tl-side{flex:1;padding:8px 20px;}
.tl-left{text-align:right;}
.tl-center{width:50px;flex-shrink:0;display:flex;flex-direction:column;align-items:center;position:relative;}
.tl-center::before{content:'';position:absolute;top:0;bottom:-24px;left:50%;transform:translateX(-50%);width:2px;background:#E5DDD5;z-index:0;}
.tl-row:last-child .tl-center::before{display:none;}
.tl-node{width:28px;height:28px;border-radius:50%;background:#E85D4A;color:#fff;display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:800;z-index:1;position:relative;box-shadow:0 2px 8px rgba(232,93,74,0.4);}
.tl-card{background:#fff;border-radius:6px;padding:12px 14px;box-shadow:0 2px 10px rgba(0,0,0,0.07);margin-bottom:16px;page-break-inside:avoid;break-inside:avoid;}
.tl-dates{font-size:9px;color:#E85D4A;font-weight:700;letter-spacing:1px;text-transform:uppercase;margin-bottom:3px;}
.tl-title{font-size:12px;font-weight:700;color:#2D2D2D;}
.tl-sub{font-size:10px;color:#888;margin-bottom:5px;}
.tl-loc{color:#BBB;}
.tl-desc{font-size:11px;color:#666;margin-bottom:5px;}
.tl-bullets{list-style:none;padding:0;}
.tl-bullets li{font-size:10px;color:#666;margin-bottom:2px;padding-left:10px;position:relative;}
.tl-bullets li::before{content:'›';position:absolute;left:0;color:#E85D4A;font-weight:700;}
/* Education */
.edu-block{margin-bottom:8px;page-break-inside:avoid;break-inside:avoid;}
.edu-degree{font-size:10px;font-weight:600;color:#2D2D2D;}
.edu-school{font-size:10px;color:#888;}
.edu-meta{font-size:9px;color:#BBB;}
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
  ${(skillsHtml || languages.length || certifications.length || education.length) ? `
  <div class="meta-row">
    ${skillsHtml ? `<div class="meta-cell"><div class="meta-title">Compétences</div>${skillsHtml}</div>` : ''}
    ${(languages.length || certifications.length) ? `<div class="meta-cell">
      ${languages.length ? `<div class="meta-title">Langues</div>${languages.map(l => `<div class="lang-item">— ${escHtml(l)}</div>`).join('')}` : ''}
      ${certifications.length ? `<div class="meta-title" style="margin-top:10px">Certifications</div>${certifications.map(c => `<div class="cert-item">${escHtml(c)}</div>`).join('')}` : ''}
    </div>` : ''}
    ${education.length ? `<div class="meta-cell"><div class="meta-title">Formation</div>${buildEducationHtml(education)}</div>` : ''}
  </div>` : ''}
  ${timelineHtml ? `
  <div class="tl-container">
    <div class="tl-header"><span class="tl-header-title">Parcours Professionnel</span></div>
    ${timelineHtml}
  </div>` : ''}
</div>
</body></html>`;
  }
};
