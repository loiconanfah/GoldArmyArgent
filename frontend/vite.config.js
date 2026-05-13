import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'
import { writeFileSync } from 'node:fs'
import { articles } from './src/data/articles.js'

const BASE = 'https://www.goldarmyai.com'

// ── Plugin Vite : génère sitemap.xml dans /dist à la fin de chaque build ──
function sitemapPlugin() {
  return {
    name: 'vite-plugin-sitemap',
    closeBundle() {
      const today = new Date().toISOString().split('T')[0]

      const staticPages = [
        { path: '/',                     changefreq: 'weekly',  priority: '1.0' },
        { path: '/blog',                 changefreq: 'daily',   priority: '0.9' },
        { path: '/tarifs',               changefreq: 'monthly', priority: '0.8' },
        { path: '/free-cv-roast',        changefreq: 'monthly', priority: '0.8' },
        { path: '/free-interview',       changefreq: 'monthly', priority: '0.7' },
        { path: '/sniper-search',        changefreq: 'monthly', priority: '0.7' },
        { path: '/mentor-ia',            changefreq: 'monthly', priority: '0.7' },
        { path: '/simulation-entretien', changefreq: 'monthly', priority: '0.7' },
        { path: '/crm-emploi',           changefreq: 'monthly', priority: '0.6' },
        { path: '/support',              changefreq: 'monthly', priority: '0.4' },
        { path: '/privacy',              changefreq: 'yearly',  priority: '0.2' },
      ]

      const articleUrls = articles.map(a => `
  <url>
    <loc>${BASE}/blog/${a.id}</loc>
    <lastmod>${a.date || today}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>`).join('')

      const staticUrls = staticPages.map(p => `
  <url>
    <loc>${BASE}${p.path}</loc>
    <lastmod>${today}</lastmod>
    <changefreq>${p.changefreq}</changefreq>
    <priority>${p.priority}</priority>
  </url>`).join('')

      const sitemap = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9
        http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd">
${staticUrls}
${articleUrls}
</urlset>`

      try {
        writeFileSync('dist/sitemap.xml', sitemap, 'utf-8')
        console.log('✅ sitemap.xml généré dans /dist')
      } catch (e) {
        console.warn('⚠️  sitemap.xml non écrit (build non finalisé ?):', e.message)
      }
    }
  }
}

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue(), sitemapPlugin()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  ssgOptions: {
    script: 'async',
    style: 'async',
    // Routes à pré-rendre statiquement (le reste est SPA)
    includedRoutes() {
      const articleRoutes = articles.map(a => `/blog/${a.id}`)
      return [
        '/',
        '/blog',
        ...articleRoutes,
        '/free-cv-roast',
        '/free-interview',
        '/sniper-search',
        '/mentor-ia',
        '/simulation-entretien',
        '/crm-emploi',
        '/tarifs',
        '/support',
        '/privacy',
      ]
    }
  }
})

