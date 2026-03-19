/**
 * Shared helpers used by all CV PDF templates.
 */

import { CvData, ParsedAudit } from './types';

export function escHtml(s: any): string {
  if (Array.isArray(s)) return s.map(escHtml).join(', ');
  return String(s ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

export function extractCvFields(cvData: CvData, parsedAudit: ParsedAudit | null) {
  const fullName  = cvData.full_name || parsedAudit?.candidate_name || 'Prénom Nom';
  const parts     = fullName.trim().split(' ');
  const firstName = parts[0] ?? '';
  const lastName  = parts.slice(1).join(' ');
  const jobTitle  = cvData.title || parsedAudit?.candidate_title || '';
  const email     = cvData.email || '';
  const phone     = cvData.phone || '';
  const location  = cvData.location || '';
  const linkedin  = cvData.linkedin || '';
  const github    = cvData.github || '';
  const summary   = cvData.summary || '';

  const experiences   = Array.isArray(cvData.experiences) ? cvData.experiences : [];
  const projects      = Array.isArray(cvData.projects) ? cvData.projects : [];
  const education     = Array.isArray(cvData.education) ? cvData.education : [];
  const languages     = Array.isArray(cvData.languages) ? cvData.languages.map(String) : [];
  const certifications = Array.isArray(cvData.certifications) ? cvData.certifications.map(String) : [];

  let skillsHtml = '';
  if (cvData.skills && typeof cvData.skills === 'object' && !Array.isArray(cvData.skills)) {
    skillsHtml = Object.entries(cvData.skills as Record<string, string[]>)
      .filter(([, items]) => Array.isArray(items) && items.length > 0)
      .map(([cat, items]) =>
        `<div class="skill-cat">${escHtml(cat)}</div><div class="skill-pills">${
          items.map(s => `<span class="pill">${escHtml(s)}</span>`).join('')
        }</div>`
      ).join('');
  } else if (Array.isArray(cvData.skills)) {
    skillsHtml = `<div class="skill-pills">${(cvData.skills as string[]).map(s => `<span class="pill">${escHtml(s)}</span>`).join('')}</div>`;
  }

  return {
    firstName, lastName, fullName, jobTitle,
    email, phone, location, linkedin, github,
    summary, experiences, projects, education,
    languages, certifications, skillsHtml,
  };
}

/** Contact bar items, returns HTML <li> elements with icons */
export function buildContactItems(fields: ReturnType<typeof extractCvFields>, iconStyle = ''): string {
  const { email, phone, location, linkedin, github } = fields;
  const items: string[] = [];
  if (phone)    items.push(`<span class="ci" style="${iconStyle}">☎</span>${escHtml(phone)}`);
  if (email)    items.push(`<span class="ci" style="${iconStyle}">✉</span>${escHtml(email)}`);
  if (location) items.push(`<span class="ci" style="${iconStyle}">⌖</span>${escHtml(location)}`);
  if (linkedin) items.push(`<span class="ci" style="${iconStyle}">in</span>${escHtml(linkedin)}`);
  if (github)   items.push(`<span class="ci" style="${iconStyle}">⌾</span>${escHtml(github)}`);
  return items.map(i => `<div class="contact-item">${i}</div>`).join('');
}

export function buildExperiencesHtml(experiences: any[], bulletColor = '#333'): string {
  if (!experiences.length) return '';
  return experiences.map(exp => `
    <div class="exp-block">
      <div class="exp-header">
        <div class="exp-title">${escHtml(exp.title)}</div>
        <div class="exp-dates">${[exp.start_date, exp.end_date].filter(Boolean).map(escHtml).join(' – ')}</div>
      </div>
      <div class="exp-company">${escHtml(exp.company)}${exp.location ? ` <span class="exp-loc">· ${escHtml(exp.location)}</span>` : ''}</div>
      ${Array.isArray(exp.bullets) && exp.bullets.length > 0 ? exp.bullets.map((b: string) => `
        <div class="bullet-row"><div class="bullet-dot" style="background:${bulletColor}"></div><div class="bullet-text">${escHtml(b)}</div></div>
      `).join('') : ''}
    </div>
  `).join('');
}

export function buildProjectsHtml(projects: any[], bulletColor = '#333'): string {
  if (!projects.length) return '';
  return projects.map(p => `
    <div class="proj-block">
      <div class="proj-name">${escHtml(p.name)}</div>
      ${p.description ? `<div class="proj-desc">${escHtml(p.description)}</div>` : ''}
      ${Array.isArray(p.bullets) && p.bullets.length > 0 ? p.bullets.map((b: string) => `
        <div class="bullet-row"><div class="bullet-dot" style="background:${bulletColor}"></div><div class="bullet-text">${escHtml(b)}</div></div>
      `).join('') : ''}
    </div>
  `).join('');
}

export function buildEducationHtml(education: any[]): string {
  return education.map(ed => `
    <div class="edu-block">
      <div class="edu-degree">${escHtml(ed.degree)}</div>
      <div class="edu-school">${escHtml(ed.institution || ed.school)}</div>
      <div class="edu-meta">${[ed.location, ed.year].filter(Boolean).map(escHtml).join(' · ')}</div>
    </div>
  `).join('');
}
