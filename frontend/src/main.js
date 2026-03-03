import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router'
import { inject } from '@vercel/analytics'
import { injectSpeedInsights } from '@vercel/speed-insights'
import './utils/firebase' // Initialize Firebase Analytics

// PostHog removed — us.i.posthog.com is blocked in China / Russia / Iran
// and caused the app to fail loading in those regions.

// Vercel Observability — lightweight, non-blocking
inject()
injectSpeedInsights()

const app = createApp(App)
app.use(router)
app.mount('#app')
