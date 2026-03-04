import { createI18n } from 'vue-i18n'
import fr from './locales/fr.json'
import en from './locales/en.json'

const messages = {
    fr,
    en
}

// Get initial locale from localStorage or browser settings
const getInitialLocale = () => {
    const saved = localStorage.getItem('language')
    if (saved) return saved

    const browserLang = navigator.language.split('-')[0]
    return languages[browserLang] ? browserLang : 'fr'
}

const languages = {
    en: true,
    fr: true
}

const i18n = createI18n({
    legacy: false, // Use Composition API
    locale: getInitialLocale(),
    fallbackLocale: 'fr',
    messages,
})

export default i18n
