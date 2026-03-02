import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router'

// ─── PostHog Analytics (non-blocking) ────────────────────────────────────────
// We defer initialisation so a network failure (e.g. posthog.com blocked by a
// firewall in China / Russia / Iran) NEVER prevents the app from loading.
// opt_out_capturing is set to true first; we opt back in only if the SDK
// manages to load. This way the app renders immediately even if the request
// hangs indefinitely (posthog-js caps its own XHR but the import itself
// must not block the main bundle evaluation).
try {
    import('posthog-js').then(({ default: posthog }) => {
        posthog.init('phc_UW265ETldt4KJz27sBt5eLmsY1rfNcWzClWYWADGRHL', {
            api_host: 'https://us.i.posthog.com',
            person_profiles: 'always',
            capture_pageview: true,
            persistence: 'localStorage',
            // If posthog can't be reached in 3 s, give up — don't stall the browser
            request_timeout_ms: 3000,
        })
    }).catch(() => { /* analytics blocked — app continues normally */ })
} catch (_) { /* safety net */ }


const app = createApp(App)
app.use(router)
app.mount('#app')
