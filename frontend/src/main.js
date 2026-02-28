import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router'
import posthog from 'posthog-js'

// Initialisation de PostHog mission 16.1
posthog.init('phc_UW265ETldt4KJz27sBt5eLmsY1rfNcWzClWYWADGRHL', {
    api_host: 'https://us.i.posthog.com',
    person_profiles: 'always', // Nécessaire pour les nouvelles versions de PostHog
    capture_pageview: true,
    persistence: 'localStorage'
})

const app = createApp(App)
app.use(router)
app.mount('#app')
