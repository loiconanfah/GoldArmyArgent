import { articles } from './src/data/articles.js'

const BASE = 'https://www.goldarmyai.com'

// Pages statiques publiques avec leur priorité et fréquence de mise à jour
const staticPages = [
  { path: '/',                    changefreq: 'weekly',  priority: '1.0' },
  { path: '/blog',                changefreq: 'daily',   priority: '0.9' },
  { path: '/tarifs',              changefreq: 'monthly', priority: '0.8' },
  { path: '/free-cv-roast',       changefreq: 'monthly', priority: '0.8' },
  { path: '/free-interview',      changefreq: 'monthly', priority: '0.7' },
  { path: '/sniper-search',       changefreq: 'monthly', priority: '0.7' },
  { path: '/mentor-ia',           changefreq: 'monthly', priority: '0.7' },
  { path: '/simulation-entretien',changefreq: 'monthly', priority: '0.7' },
  { path: '/crm-emploi',          changefreq: 'monthly', priority: '0.6' },
  { path: '/support',             changefreq: 'monthly', priority: '0.4' },
  { path: '/privacy',             changefreq: 'yearly',  priority: '0.2' },
]

// Date du jour en format ISO 8601 pour lastmod
const today = new Date().toISOString().split('T')[0]

// Génération des entrées d'articles de blog
const articleEntries = articles.map(article => ({
  path: `/blog/${article.id}`,
  lastmod: article.date || today,
  changefreq: 'monthly',
  priority: '0.8'
}))

// Génération XML complète du sitemap
const urls = [
  ...staticPages.map(p => `
  <url>
    <loc>${BASE}${p.path}</loc>
    <lastmod>${today}</lastmod>
    <changefreq>${p.changefreq}</changefreq>
    <priority>${p.priority}</priority>
  </url>`),
  ...articleEntries.map(a => `
  <url>
    <loc>${BASE}${a.path}</loc>
    <lastmod>${a.lastmod}</lastmod>
    <changefreq>${a.changefreq}</changefreq>
    <priority>${a.priority}</priority>
  </url>`)
].join('')

const sitemap = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9
        http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd">
${urls}
</urlset>`

export default sitemap
