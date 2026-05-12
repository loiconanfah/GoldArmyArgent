import './style.css'
import App from './App.vue'
import { ViteSSG } from 'vite-ssg'
import i18n from './i18n'
import { routes } from './router'

export const createApp = ViteSSG(
  App,
  { routes, base: '/' },
  ({ app, router, isClient }) => {
    app.use(i18n)

    // ── Router guards ──────────────────────────────────────────────────────────
    router.beforeEach((to, from, next) => {
      const isAuthenticated = typeof localStorage !== 'undefined'
        ? !!localStorage.getItem('token')
        : false

      if (to.meta.requiresAuth && !isAuthenticated) {
        next('/login')
      } else if (
        (to.name === 'Login' || to.name === 'Register' || to.name === 'Landing') &&
        isAuthenticated
      ) {
        next('/home')
      } else if (to.meta.requiresAdmin) {
        const user = typeof localStorage !== 'undefined'
          ? JSON.parse(localStorage.getItem('user') || '{}')
          : {}
        if (user.subscription_tier === 'ADMIN') {
          next()
        } else {
          next('/dashboard')
        }
      } else {
        next()
      }
    })

    router.afterEach((to) => {
      if (typeof window !== 'undefined') {
        import('./utils/analytics').then(({ trackEvent }) => {
          trackEvent('page_view', { name: to.name, path: to.path })
        })
      }
    })

    // ── Client-only initializations ────────────────────────────────────────────
    if (isClient) {
      import('@vercel/analytics').then(({ inject }) => inject())
      import('@vercel/speed-insights').then(({ injectSpeedInsights }) => injectSpeedInsights())
      import('@microsoft/clarity').then(({ default: Clarity }) => Clarity.init('vqnc1r3lwk'))
      import('./utils/firebase')
    }
  }
)
