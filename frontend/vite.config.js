import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'
import { articles } from './src/data/articles.js'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
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
