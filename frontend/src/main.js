import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router'

// PostHog removed — us.i.posthog.com is blocked in China / Russia / Iran
// and caused the app to fail loading in those regions.

const app = createApp(App)
app.use(router)
app.mount('#app')
