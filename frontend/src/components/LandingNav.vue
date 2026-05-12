<script setup>
import { ref, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { 
  MapIcon, 
  SparklesIcon, 
  MicrophoneIcon, 
  BriefcaseIcon, 
  DocumentCheckIcon, 
  CreditCardIcon, 
  DocumentTextIcon, 
  StarIcon, 
  LifebuoyIcon 
} from '@heroicons/vue/24/outline'

const { t, locale } = useI18n()
const router = useRouter()
const route = useRoute()
const navOpen = ref(false)

function closeNav() {
  navOpen.value = false
}

function setLocale(lang) {
  locale.value = lang
  if (typeof localStorage !== 'undefined') localStorage.setItem('language', lang)
  closeNav()
}

watch(navOpen, (open) => {
  if (typeof document !== 'undefined') {
    document.body.style.overflow = open ? 'hidden' : ''
    document.body.style.touchAction = open ? 'none' : ''
  }
})

function goToSection(hash) {
  closeNav()
  if (route.path === '/') {
    if (typeof document !== 'undefined') {
      const el = document.getElementById(hash)
      if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' })
    }
  } else {
    router.push({ path: '/', hash: `#${hash}` })
  }
}
</script>

<template>
  <header class="nav-modern" role="banner">
    <div class="nav-modern__bar">
      <div class="nav-modern__container">
        <router-link to="/" class="nav-modern__brand" @click="closeNav" aria-label="GoldArmy AI Accueil">
          <img src="/logo.png" alt="Logo de GoldArmy AI" class="nav-modern__logo" width="40" height="40" />
          <span class="nav-modern__name">GoldArmy</span>
        </router-link>

        <nav class="nav-modern__links" aria-label="Navigation principale">
          <!-- Dropdown Outils IA -->
          <div class="nav-dropdown">
            <button type="button" class="nav-modern__link nav-dropdown__trigger" aria-haspopup="true" aria-expanded="false">
              Outils IA <span class="nav-dropdown__arrow">▾</span>
            </button>
            <div class="nav-dropdown__content" role="menu">
              <router-link to="/sniper-search" class="nav-dropdown__item" role="menuitem" @click="closeNav">
                <span class="nav-dropdown__icon"><MapIcon class="nav-icon" /></span>
                <div>
                  <strong>Sniper Search</strong>
                  <p>Détecteur d'offres cachées</p>
                </div>
              </router-link>
              <router-link to="/mentor-ia" class="nav-dropdown__item" role="menuitem" @click="closeNav">
                <span class="nav-dropdown__icon"><SparklesIcon class="nav-icon" /></span>
                <div>
                  <strong>Mentor IA</strong>
                  <p>Coaching &amp; Lettres sur mesure</p>
                </div>
              </router-link>
              <router-link to="/simulation-entretien" class="nav-dropdown__item" role="menuitem" @click="closeNav">
                <span class="nav-dropdown__icon"><MicrophoneIcon class="nav-icon" /></span>
                <div>
                  <strong>Simulation Entretien</strong>
                  <p>Entraînement visio vocal IA</p>
                </div>
              </router-link>
              <router-link to="/crm-emploi" class="nav-dropdown__item" role="menuitem" @click="closeNav">
                <span class="nav-dropdown__icon"><BriefcaseIcon class="nav-icon" /></span>
                <div>
                  <strong>CRM Emploi</strong>
                  <p>Kanban &amp; Relances automatiques</p>
                </div>
              </router-link>
            </div>
          </div>

          <!-- Liens directs -->
          <router-link to="/free-cv-roast" class="nav-modern__link" @click="closeNav">Audit CV Gratuit</router-link>
          <router-link to="/tarifs" class="nav-modern__link" @click="closeNav">Tarifs</router-link>
          <router-link to="/blog" class="nav-modern__link" @click="closeNav">Blog</router-link>
          <a href="#avis" class="nav-modern__link" @click.prevent="goToSection('avis')">Avis</a>
        </nav>

        <div class="nav-modern__actions">
          <div class="nav-modern__lang" role="group" aria-label="Changer la langue">
            <button type="button" :class="['nav-modern__lang-btn', { 'nav-modern__lang-btn--active': locale === 'fr' }]" @click="setLocale('fr')" :aria-pressed="locale === 'fr'">FR</button>
            <span class="nav-modern__lang-sep" aria-hidden="true">|</span>
            <button type="button" :class="['nav-modern__lang-btn', { 'nav-modern__lang-btn--active': locale === 'en' }]" @click="setLocale('en')" :aria-pressed="locale === 'en'">EN</button>
          </div>
          <router-link to="/login" class="nav-modern__btn nav-modern__btn--ghost" @click="closeNav">{{ t('landing.nav.login') }}</router-link>
          <router-link to="/register" class="nav-modern__btn nav-modern__btn--cta" @click="closeNav">{{ t('landing.nav.get_started') }}</router-link>
        </div>

        <button
          type="button"
          class="nav-modern__burger"
          :class="{ 'nav-modern__burger--open': navOpen }"
          aria-label="Ouvrir le menu"
          :aria-expanded="navOpen"
          @click="navOpen = !navOpen"
        >
          <span class="nav-modern__burger-line"></span>
          <span class="nav-modern__burger-line"></span>
          <span class="nav-modern__burger-line"></span>
        </button>
      </div>
    </div>

    <!-- Tiroir Mobile (Drawer) -->
    <Transition name="nav-drawer">
      <div v-show="navOpen" class="nav-modern__backdrop" @click="closeNav">
        <nav class="nav-modern__drawer" @click.stop aria-label="Menu mobile">
          <p class="nav-modern__drawer-title">Outils GoldArmy AI</p>
          <router-link to="/sniper-search" class="nav-modern__drawer-link" @click="closeNav">
            <MapIcon class="nav-icon-inline" /> Sniper Search
          </router-link>
          <router-link to="/mentor-ia" class="nav-modern__drawer-link" @click="closeNav">
            <SparklesIcon class="nav-icon-inline" /> Mentor IA Carrière
          </router-link>
          <router-link to="/simulation-entretien" class="nav-modern__drawer-link" @click="closeNav">
            <MicrophoneIcon class="nav-icon-inline" /> Simulation Entretien IA
          </router-link>
          <router-link to="/crm-emploi" class="nav-modern__drawer-link" @click="closeNav">
            <BriefcaseIcon class="nav-icon-inline" /> CRM Emploi IA
          </router-link>
          <router-link to="/free-cv-roast" class="nav-modern__drawer-link" @click="closeNav">
            <DocumentCheckIcon class="nav-icon-inline" /> Audit CV Gratuit
          </router-link>

          <p class="nav-modern__drawer-title mt-4">Navigation</p>
          <router-link to="/tarifs" class="nav-modern__drawer-link" @click="closeNav">
            <CreditCardIcon class="nav-icon-inline" /> Tarifs &amp; Forfaits
          </router-link>
          <router-link to="/blog" class="nav-modern__drawer-link" @click="closeNav">
            <DocumentTextIcon class="nav-icon-inline" /> Blog &amp; Astuces
          </router-link>
          <a href="#avis" class="nav-modern__drawer-link" @click.prevent="goToSection('avis')">
            <StarIcon class="nav-icon-inline" /> Avis Candidats
          </a>
          <router-link to="/support" class="nav-modern__drawer-link" @click="closeNav">
            <LifebuoyIcon class="nav-icon-inline" /> Support Client
          </router-link>

          <div class="nav-modern__drawer-actions">
            <div class="nav-modern__lang nav-modern__lang--drawer" role="group" aria-label="Changer la langue">
              <button type="button" :class="['nav-modern__lang-btn', { 'nav-modern__lang-btn--active': locale === 'fr' }]" @click="setLocale('fr')">FR</button>
              <span class="nav-modern__lang-sep">|</span>
              <button type="button" :class="['nav-modern__lang-btn', { 'nav-modern__lang-btn--active': locale === 'en' }]" @click="setLocale('en')">EN</button>
            </div>
            <router-link to="/login" class="nav-modern__btn nav-modern__btn--ghost" @click="closeNav">{{ t('landing.nav.login') }}</router-link>
            <router-link to="/register" class="nav-modern__btn nav-modern__btn--cta" @click="closeNav">{{ t('landing.nav.get_started') }}</router-link>
          </div>
        </nav>
      </div>
    </Transition>
  </header>
</template>

<style scoped>
.nav-modern {
  position: sticky;
  top: 0;
  z-index: 1000;
}
.nav-modern__bar {
  background: rgba(10, 10, 18, 0.85);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  box-shadow: 0 4px 30px rgba(0, 0, 0, 0.3);
}
.nav-modern__container {
  max-width: 1280px;
  margin: 0 auto;
  padding: 0.75rem 1.5rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}
.nav-modern__brand {
  display: inline-flex;
  align-items: center;
  gap: 0.65rem;
  text-decoration: none;
  color: #fff;
  font-weight: 800;
  font-size: 1.2rem;
  letter-spacing: -0.03em;
  transition: transform 0.2s, color 0.2s;
}
.nav-modern__brand:hover {
  color: #ff8c42;
  transform: translateY(-1px);
}
.nav-modern__logo {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  object-fit: cover;
  border: 1px solid rgba(255, 255, 255, 0.15);
}
.nav-modern__name {
  font-family: system-ui, -apple-system, 'Segoe UI', sans-serif;
  background: linear-gradient(90deg, #fff, #cbd5e1);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}
.nav-modern__links {
  display: none;
  align-items: center;
  gap: 0.25rem;
}
@media (min-width: 1024px) {
  .nav-modern__links { display: flex; }
}
.nav-modern__link {
  padding: 0.5rem 0.85rem;
  font-size: 0.85rem;
  font-weight: 600;
  letter-spacing: 0.03em;
  color: rgba(255, 255, 255, 0.85);
  text-decoration: none;
  border-radius: 8px;
  background: transparent;
  border: none;
  cursor: pointer;
  transition: color 0.2s, background 0.2s;
}
.nav-modern__link:hover {
  color: #fff;
  background: rgba(255, 255, 255, 0.06);
}
.nav-modern__link.router-link-active {
  color: #ff8c42;
  background: rgba(255, 111, 0, 0.12);
}

/* Dropdown Outils IA */
.nav-dropdown {
  position: relative;
  display: inline-block;
}
.nav-dropdown__arrow {
  font-size: 0.75rem;
  margin-left: 0.2rem;
  transition: transform 0.2s;
}
.nav-dropdown:hover .nav-dropdown__arrow {
  transform: rotate(180deg);
}
.nav-dropdown__content {
  position: absolute;
  top: 100%;
  left: 0;
  background: rgba(15, 15, 26, 0.95);
  backdrop-filter: blur(25px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 0.75rem;
  min-width: 310px;
  box-shadow: 0 10px 40px rgba(0,0,0,0.5);
  opacity: 0;
  visibility: hidden;
  transform: translateY(10px);
  transition: opacity 0.2s, transform 0.2s, visibility 0.2s;
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  z-index: 1001;
}
.nav-dropdown:hover .nav-dropdown__content {
  opacity: 1;
  visibility: visible;
  transform: translateY(0);
}
.nav-dropdown__item {
  display: flex;
  align-items: center;
  gap: 0.85rem;
  padding: 0.65rem 0.85rem;
  text-decoration: none;
  border-radius: 8px;
  transition: background 0.2s;
}
.nav-dropdown__item:hover {
  background: rgba(255, 111, 0, 0.12);
}
.nav-dropdown__icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  color: #ff8c42;
  flex-shrink: 0;
}
.nav-icon {
  width: 20px;
  height: 20px;
  stroke-width: 2;
}
.nav-icon-inline {
  width: 18px;
  height: 18px;
  display: inline-block;
  vertical-align: -3px;
  margin-right: 0.4rem;
  color: #ff8c42;
  stroke-width: 2;
}
.nav-dropdown__item strong {
  display: block;
  font-size: 0.875rem;
  color: #fff;
  font-weight: 700;
  margin-bottom: 0.1rem;
}
.nav-dropdown__item p {
  margin: 0;
  font-size: 0.75rem;
  color: #94a3b8;
}

/* Actions de droite */
.nav-modern__actions {
  display: none;
  align-items: center;
  gap: 0.65rem;
}
@media (min-width: 1024px) {
  .nav-modern__actions { display: flex; }
}
.nav-modern__btn {
  padding: 0.55rem 1.1rem;
  font-size: 0.8125rem;
  font-weight: 600;
  letter-spacing: 0.03em;
  text-decoration: none;
  border-radius: 8px;
  transition: all 0.2s;
}
.nav-modern__btn--ghost {
  color: rgba(255, 255, 255, 0.75);
}
.nav-modern__btn--ghost:hover {
  color: #fff;
  background: rgba(255, 255, 255, 0.08);
}
.nav-modern__btn--cta {
  color: #000;
  background: linear-gradient(135deg, #ff9a5c, #ff6f00);
  font-weight: 700;
  box-shadow: 0 4px 15px rgba(255, 111, 0, 0.35);
}
.nav-modern__btn--cta:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(255, 111, 0, 0.5);
}

/* Sélecteur de langue */
.nav-modern__lang {
  display: flex;
  align-items: center;
  gap: 0.2rem;
}
.nav-modern__lang-btn {
  padding: 0.25rem 0.45rem;
  font-size: 0.75rem;
  font-weight: 700;
  color: rgba(255, 255, 255, 0.4);
  background: transparent;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: color 0.2s;
}
.nav-modern__lang-btn:hover { color: #fff; }
.nav-modern__lang-btn--active {
  color: #ff8c42;
  background: rgba(255, 111, 0, 0.15);
}
.nav-modern__lang-sep {
  color: rgba(255, 255, 255, 0.15);
  font-size: 0.75rem;
}

/* Burger Mobile */
.nav-modern__burger {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 5px;
  width: 44px;
  height: 44px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  cursor: pointer;
}
@media (min-width: 1024px) {
  .nav-modern__burger { display: none; }
}
.nav-modern__burger-line {
  display: block;
  width: 18px;
  height: 2px;
  background: #fff;
  border-radius: 1px;
  transition: transform 0.25s, opacity 0.25s;
}
.nav-modern__burger--open .nav-modern__burger-line:nth-child(1) { transform: translateY(7px) rotate(45deg); }
.nav-modern__burger--open .nav-modern__burger-line:nth-child(2) { opacity: 0; }
.nav-modern__burger--open .nav-modern__burger-line:nth-child(3) { transform: translateY(-7px) rotate(-45deg); }

/* Tiroir Mobile (Drawer) */
.nav-modern__backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.75);
  backdrop-filter: blur(10px);
  z-index: 999;
  display: flex;
  justify-content: flex-end;
}
.nav-modern__drawer {
  width: min(320px, 85vw);
  background: #0b0b12;
  border-left: 1px solid rgba(255, 255, 255, 0.1);
  padding: 5.5rem 1.5rem 2rem;
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  overflow-y: auto;
}
.nav-modern__drawer-title {
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: #64748b;
  margin: 0.75rem 0 0.25rem;
}
.mt-4 { margin-top: 1rem; }
.nav-modern__drawer-link {
  display: flex;
  align-items: center;
  padding: 0.75rem 1rem;
  font-size: 0.9rem;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.85);
  text-decoration: none;
  border-radius: 8px;
  transition: background 0.2s, color 0.2s;
}
.nav-modern__drawer-link:hover {
  background: rgba(255, 111, 0, 0.12);
  color: #ff8c42;
}
.nav-modern__drawer-actions {
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
}
.nav-modern__drawer-actions .nav-modern__btn { text-align: center; padding: 0.85rem; }
.nav-modern__lang--drawer { justify-content: center; margin-bottom: 0.5rem; }

.nav-drawer-enter-active, .nav-drawer-leave-active { transition: opacity 0.2s; }
.nav-drawer-enter-from, .nav-drawer-leave-to { opacity: 0; }
.nav-drawer-enter-active .nav-modern__drawer, .nav-drawer-leave-active .nav-modern__drawer { transition: transform 0.25s; }
.nav-drawer-enter-from .nav-modern__drawer, .nav-drawer-leave-to .nav-modern__drawer { transform: translateX(100%); }
</style>
