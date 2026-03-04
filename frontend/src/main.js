import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router'
import { inject } from '@vercel/analytics'
import { injectSpeedInsights } from '@vercel/speed-insights'
import './utils/firebase' // Initialize Firebase Analytics

// PostHog removed — us.i.posthog.com is blocked in China / Russia / Iran
// and caused the app to fail loading in those regions.

import { createHead } from '@unhead/vue/client'
import i18n from './i18n'
import Clarity from '@microsoft/clarity'

// Vercel Observability — lightweight, non-blocking
inject()
injectSpeedInsights()

// Microsoft Clarity — behavior analytics
Clarity.init('vqnc1r3lwk')

const app = createApp(App)
const head = createHead()

app.use(router)
app.use(head)
app.use(i18n)
app.mount('#app')
