<script setup>
import { ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
const navOpen = ref(false)

function closeNav() {
  navOpen.value = false
}

watch(navOpen, (open) => {
  document.body.style.overflow = open ? 'hidden' : ''
  document.body.style.touchAction = open ? 'none' : ''
})
</script>

<template>
  <header class="nav-tech" role="banner">
    <div class="nav-tech__bar">
      <div class="nav-tech__container">
        <router-link to="/" class="nav-tech__brand" @click="closeNav" aria-label="GoldArmy">
          <img src="/logo.png" alt="" class="nav-tech__logo" width="36" height="36" />
          <span class="nav-tech__name">GoldArmy</span>
        </router-link>

        <nav class="nav-tech__links" aria-label="Navigation principale">
          <router-link to="/#agents" class="nav-tech__link" @click="closeNav">{{ t('landing.nav.features') }}</router-link>
          <router-link to="/#agents" class="nav-tech__link" @click="closeNav">{{ t('landing.nav.agents') }}</router-link>
          <router-link to="/#pricing" class="nav-tech__link" @click="closeNav">{{ t('landing.nav.pricing') }}</router-link>
          <router-link to="/#avis" class="nav-tech__link" @click="closeNav">{{ t('landing.nav.reviews') }}</router-link>
          <router-link to="/free-cv-roast" class="nav-tech__link" @click="closeNav">{{ t('landing.nav.cv_audit') }}</router-link>
          <router-link to="/free-interview" class="nav-tech__link" @click="closeNav">{{ t('landing.nav.simulation') }}</router-link>
          <router-link to="/blog" class="nav-tech__link" @click="closeNav">{{ t('landing.nav.blog') }}</router-link>
        </nav>

        <div class="nav-tech__actions">
          <router-link to="/login" class="nav-tech__btn nav-tech__btn--ghost" @click="closeNav">{{ t('landing.nav.login') }}</router-link>
          <router-link to="/register" class="nav-tech__btn nav-tech__btn--cta" @click="closeNav">{{ t('landing.nav.get_started') }}</router-link>
        </div>

        <button
          type="button"
          class="nav-tech__burger"
          :class="{ 'nav-tech__burger--open': navOpen }"
          aria-label="Menu"
          :aria-expanded="navOpen"
          @click="navOpen = !navOpen"
        >
          <span class="nav-tech__burger-line"></span>
          <span class="nav-tech__burger-line"></span>
          <span class="nav-tech__burger-line"></span>
        </button>
      </div>
    </div>

    <!-- Overlay mobile -->
    <Transition name="nav-overlay">
      <div v-show="navOpen" class="nav-tech__overlay" @click="closeNav">
        <nav class="nav-tech__drawer" @click.stop>
          <router-link to="/" class="nav-tech__drawer-link" @click="closeNav">{{ t('landing.nav.features') }}</router-link>
          <router-link to="/#agents" class="nav-tech__drawer-link" @click="closeNav">{{ t('landing.nav.agents') }}</router-link>
          <router-link to="/#pricing" class="nav-tech__drawer-link" @click="closeNav">{{ t('landing.nav.pricing') }}</router-link>
          <router-link to="/#avis" class="nav-tech__drawer-link" @click="closeNav">{{ t('landing.nav.reviews') }}</router-link>
          <router-link to="/free-cv-roast" class="nav-tech__drawer-link" @click="closeNav">{{ t('landing.nav.cv_audit') }}</router-link>
          <router-link to="/free-interview" class="nav-tech__drawer-link" @click="closeNav">{{ t('landing.nav.simulation') }}</router-link>
          <router-link to="/blog" class="nav-tech__drawer-link" @click="closeNav">{{ t('landing.nav.blog') }}</router-link>
          <div class="nav-tech__drawer-actions">
            <router-link to="/login" class="nav-tech__btn nav-tech__btn--ghost" @click="closeNav">{{ t('landing.nav.login') }}</router-link>
            <router-link to="/register" class="nav-tech__btn nav-tech__btn--cta" @click="closeNav">{{ t('landing.nav.get_started') }}</router-link>
          </div>
        </nav>
      </div>
    </Transition>
  </header>
</template>

<style scoped>
.nav-tech {
  position: sticky;
  top: 0;
  z-index: 1000;
}
.nav-tech__bar {
  backdrop-filter: saturate(180%) blur(12px);
  background: rgba(15, 15, 24, 0.85);
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  box-shadow: 0 1px 0 0 rgba(255, 111, 0, 0.08);
}
.nav-tech__container {
  max-width: 1280px;
  margin: 0 auto;
  padding: 0.75rem 1.5rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1.5rem;
}
.nav-tech__brand {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  text-decoration: none;
  color: #fff;
  font-weight: 700;
  font-size: 1.125rem;
  letter-spacing: -0.02em;
}
.nav-tech__brand:hover {
  color: #ff8c42;
}
.nav-tech__logo {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  object-fit: cover;
  border: 1px solid rgba(255, 255, 255, 0.1);
}
.nav-tech__name {
  font-family: system-ui, -apple-system, sans-serif;
}
.nav-tech__links {
  display: none;
  align-items: center;
  gap: 0.25rem;
}
@media (min-width: 992px) {
  .nav-tech__links {
    display: flex;
  }
}
.nav-tech__link {
  padding: 0.5rem 0.75rem;
  font-size: 0.8125rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: rgba(255, 255, 255, 0.85);
  text-decoration: none;
  border: none;
  background: none;
  cursor: pointer;
  border-radius: 8px;
  transition: color 0.2s, background 0.2s;
}
.nav-tech__link:hover {
  color: #ff8c42;
  background: rgba(255, 111, 0, 0.08);
}
.nav-tech__actions {
  display: none;
  align-items: center;
  gap: 0.5rem;
}
@media (min-width: 992px) {
  .nav-tech__actions {
    display: flex;
  }
}
.nav-tech__btn {
  padding: 0.5rem 1rem;
  font-size: 0.8125rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  text-decoration: none;
  border-radius: 8px;
  transition: color 0.2s, background 0.2s, box-shadow 0.2s;
}
.nav-tech__btn--ghost {
  color: rgba(255, 255, 255, 0.7);
  background: transparent;
}
.nav-tech__btn--ghost:hover {
  color: #fff;
}
.nav-tech__btn--cta {
  color: #0a0a12;
  background: linear-gradient(135deg, #ff8c42 0%, #ff6f00 100%);
  border: 1px solid rgba(255, 111, 0, 0.5);
  box-shadow: 0 0 20px rgba(255, 111, 0, 0.25);
}
.nav-tech__btn--cta:hover {
  box-shadow: 0 0 28px rgba(255, 111, 0, 0.4);
  background: linear-gradient(135deg, #ff9a5c 0%, #ff7a14 100%);
}
.nav-tech__burger {
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 5px;
  width: 44px;
  height: 44px;
  padding: 10px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 10px;
  cursor: pointer;
  transition: background 0.2s;
}
@media (min-width: 992px) {
  .nav-tech__burger {
    display: none;
  }
}
.nav-tech__burger:hover {
  background: rgba(255, 255, 255, 0.08);
}
.nav-tech__burger-line {
  display: block;
  height: 2px;
  background: #fff;
  border-radius: 1px;
  transition: transform 0.25s, opacity 0.25s;
}
.nav-tech__burger--open .nav-tech__burger-line:nth-child(1) {
  transform: translateY(7px) rotate(45deg);
}
.nav-tech__burger--open .nav-tech__burger-line:nth-child(2) {
  opacity: 0;
}
.nav-tech__burger--open .nav-tech__burger-line:nth-child(3) {
  transform: translateY(-7px) rotate(-45deg);
}

.nav-tech__overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(4px);
  z-index: 999;
  display: flex;
  justify-content: flex-end;
}
.nav-tech__drawer {
  width: min(320px, 100%);
  background: linear-gradient(180deg, #1a1a24 0%, #0f0f18 100%);
  border-left: 1px solid rgba(255, 255, 255, 0.06);
  padding: 5rem 1.5rem 2rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.nav-tech__drawer-link {
  padding: 0.75rem 1rem;
  font-size: 0.9375rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: rgba(255, 255, 255, 0.9);
  text-decoration: none;
  border-radius: 8px;
  transition: background 0.2s, color 0.2s;
}
.nav-tech__drawer-link:hover {
  background: rgba(255, 111, 0, 0.12);
  color: #ff8c42;
}
.nav-tech__drawer-actions {
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.nav-tech__drawer-actions .nav-tech__btn {
  justify-content: center;
  text-align: center;
}

.nav-overlay-enter-active,
.nav-overlay-leave-active {
  transition: opacity 0.2s ease;
}
.nav-overlay-enter-from,
.nav-overlay-leave-to {
  opacity: 0;
}
</style>
