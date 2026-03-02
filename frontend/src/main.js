import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router'
import { inject } from '@vercel/analytics'

// PostHog removed — us.i.posthog.com is blocked in China / Russia / Iran
// and caused the app to fail loading in those regions.

// Vercel Analytics — lightweight, non-blocking
inject()

const app = createApp(App)
app.use(router)
app.mount('#app')
