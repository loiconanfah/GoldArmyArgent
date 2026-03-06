<script setup>
import { ref, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
const router = useRouter()
const route = useRoute()
const navOpen = ref(false)

function closeNav() {
  navOpen.value = false
}

watch(navOpen, (open) => {
  document.body.style.overflow = open ? 'hidden' : ''
  document.body.style.touchAction = open ? 'none' : ''
})

function goToSection(hash) {
  closeNav()
  if (route.path === '/') {
    const el = document.getElementById(hash)
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'start' })
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
        <router-link to="/" class="nav-modern__brand" @click="closeNav" aria-label="GoldArmy">
          <img src="/logo.png" alt="" class="nav-modern__logo" width="40" height="40" />
          <span class="nav-modern__name">GoldArmy</span>
        </router-link>

        <nav class="nav-modern__links" aria-label="Navigation principale">
          <a href="#agents" class="nav-modern__link" @click.prevent="goToSection('agents')">{{ t('landing.nav.features') }}</a>
          <a href="#agents" class="nav-modern__link" @click.prevent="goToSection('agents')">{{ t('landing.nav.agents') }}</a>
          <a href="#pricing" class="nav-modern__link" @click.prevent="goToSection('pricing')">{{ t('landing.nav.pricing') }}</a>
          <a href="#avis" class="nav-modern__link" @click.prevent="goToSection('avis')">{{ t('landing.nav.reviews') }}</a>
          <router-link to="/free-cv-roast" class="nav-modern__link" @click="closeNav">{{ t('landing.nav.cv_audit') }}</router-link>
          <router-link to="/free-interview" class="nav-modern__link" @click="closeNav">{{ t('landing.nav.simulation') }}</router-link>
          <router-link to="/blog" class="nav-modern__link" @click="closeNav">{{ t('landing.nav.blog') }}</router-link>
        </nav>

        <div class="nav-modern__actions">
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

    <Transition name="nav-drawer">
      <div v-show="navOpen" class="nav-modern__backdrop" @click="closeNav">
        <nav class="nav-modern__drawer" @click.stop>
          <a href="#agents" class="nav-modern__drawer-link" @click.prevent="goToSection('agents')">{{ t('landing.nav.features') }}</a>
          <a href="#agents" class="nav-modern__drawer-link" @click.prevent="goToSection('agents')">{{ t('landing.nav.agents') }}</a>
          <a href="#pricing" class="nav-modern__drawer-link" @click.prevent="goToSection('pricing')">{{ t('landing.nav.pricing') }}</a>
          <a href="#avis" class="nav-modern__drawer-link" @click.prevent="goToSection('avis')">{{ t('landing.nav.reviews') }}</a>
          <router-link to="/free-cv-roast" class="nav-modern__drawer-link" @click="closeNav">{{ t('landing.nav.cv_audit') }}</router-link>
          <router-link to="/free-interview" class="nav-modern__drawer-link" @click="closeNav">{{ t('landing.nav.simulation') }}</router-link>
          <router-link to="/blog" class="nav-modern__drawer-link" @click="closeNav">{{ t('landing.nav.blog') }}</router-link>
          <div class="nav-modern__drawer-actions">
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
  background: rgba(10, 10, 18, 0.92);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.25);
}
.nav-modern__container {
  max-width: 1280px;
  margin: 0 auto;
  padding: 0.875rem 1.5rem;
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
  border-radius: 12px;
  object-fit: cover;
  border: 1px solid rgba(255, 255, 255, 0.12);
}
.nav-modern__name {
  font-family: system-ui, -apple-system, 'Segoe UI', sans-serif;
}
.nav-modern__links {
  display: none;
  align-items: center;
  gap: 0.125rem;
}
@media (min-width: 992px) {
  .nav-modern__links {
    display: flex;
  }
}
.nav-modern__link {
  padding: 0.5rem 0.875rem;
  font-size: 0.8125rem;
  font-weight: 600;
  letter-spacing: 0.04em;
  color: rgba(255, 255, 255, 0.88);
  text-decoration: none;
  border-radius: 10px;
  transition: color 0.2s, background 0.2s, box-shadow 0.2s;
}
.nav-modern__link:hover {
  color: #fff;
  background: rgba(255, 255, 255, 0.06);
  box-shadow: 0 0 0 1px rgba(255, 255, 255, 0.06);
}
.nav-modern__link.router-link-active {
  color: #ff8c42;
  background: rgba(255, 111, 0, 0.1);
}
.nav-modern__actions {
  display: none;
  align-items: center;
  gap: 0.5rem;
}
@media (min-width: 992px) {
  .nav-modern__actions {
    display: flex;
  }
}
.nav-modern__btn {
  padding: 0.55rem 1.1rem;
  font-size: 0.8125rem;
  font-weight: 600;
  letter-spacing: 0.04em;
  text-decoration: none;
  border-radius: 10px;
  transition: color 0.2s, background 0.2s, box-shadow 0.2s, transform 0.15s;
}
.nav-modern__btn--ghost {
  color: rgba(255, 255, 255, 0.75);
  background: transparent;
}
.nav-modern__btn--ghost:hover {
  color: #fff;
  background: rgba(255, 255, 255, 0.06);
}
.nav-modern__btn--cta {
  color: #0a0a12;
  background: linear-gradient(135deg, #ff9a5c 0%, #ff6f00 100%);
  border: none;
  box-shadow: 0 2px 12px rgba(255, 111, 0, 0.35);
}
.nav-modern__btn--cta:hover {
  color: #0a0a12;
  box-shadow: 0 4px 20px rgba(255, 111, 0, 0.45);
  transform: translateY(-1px);
}
.nav-modern__btn--cta:active {
  transform: translateY(0);
}
.nav-modern__burger {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 5px;
  width: 48px;
  height: 48px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  cursor: pointer;
  transition: background 0.2s, border-color 0.2s;
}
@media (min-width: 992px) {
  .nav-modern__burger {
    display: none;
  }
}
.nav-modern__burger:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.12);
}
.nav-modern__burger-line {
  display: block;
  width: 20px;
  height: 2px;
  background: #fff;
  border-radius: 1px;
  transition: transform 0.25s ease, opacity 0.25s ease;
}
.nav-modern__burger--open .nav-modern__burger-line:nth-child(1) {
  transform: translateY(7px) rotate(45deg);
}
.nav-modern__burger--open .nav-modern__burger-line:nth-child(2) {
  opacity: 0;
}
.nav-modern__burger--open .nav-modern__burger-line:nth-child(3) {
  transform: translateY(-7px) rotate(-45deg);
}

.nav-modern__backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(8px);
  z-index: 999;
  display: flex;
  justify-content: flex-end;
}
.nav-modern__drawer {
  width: min(300px, 85vw);
  background: linear-gradient(180deg, #14141c 0%, #0c0c12 100%);
  border-left: 1px solid rgba(255, 255, 255, 0.08);
  padding: 5.5rem 1.25rem 2rem;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  box-shadow: -8px 0 32px rgba(0, 0, 0, 0.4);
}
.nav-modern__drawer-link {
  padding: 0.85rem 1rem;
  font-size: 0.9375rem;
  font-weight: 600;
  letter-spacing: 0.03em;
  color: rgba(255, 255, 255, 0.9);
  text-decoration: none;
  border-radius: 10px;
  transition: background 0.2s, color 0.2s;
}
.nav-modern__drawer-link:hover {
  background: rgba(255, 111, 0, 0.12);
  color: #ff8c42;
}
.nav-modern__drawer-actions {
  margin-top: 1.25rem;
  padding-top: 1.25rem;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.nav-modern__drawer-actions .nav-modern__btn {
  justify-content: center;
  text-align: center;
  padding: 0.75rem 1rem;
}

.nav-drawer-enter-active,
.nav-drawer-leave-active {
  transition: opacity 0.2s ease;
}
.nav-drawer-enter-from,
.nav-drawer-leave-to {
  opacity: 0;
}
.nav-drawer-enter-active .nav-modern__drawer,
.nav-drawer-leave-active .nav-modern__drawer {
  transition: transform 0.25s ease;
}
.nav-drawer-enter-from .nav-modern__drawer,
.nav-drawer-leave-to .nav-modern__drawer {
  transform: translateX(100%);
}
</style>
