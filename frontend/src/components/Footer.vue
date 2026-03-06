<script setup>
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
const router = useRouter()
const currentYear = new Date().getFullYear()

function goToSection(hash) {
  if (router.currentRoute.value.path === '/' && hash) {
    const el = document.getElementById(hash)
    if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' })
  } else if (hash) {
    router.push(`/#${hash}`)
  }
}
</script>

<template>
  <footer class="footer-tech" role="contentinfo">
    <div class="footer-tech__glow"></div>
    <div class="footer-tech__container">
      <div class="footer-tech__grid">
        <div class="footer-tech__brand-col">
          <router-link to="/" class="footer-tech__brand">
            <img src="/logo.png" alt="GoldArmy" class="footer-tech__logo" width="48" height="48" loading="lazy" />
            <span class="footer-tech__name">GoldArmy</span>
          </router-link>
          <p class="footer-tech__tagline">{{ t('landing.footer.description') }}</p>
          <div class="footer-tech__accent-line"></div>
        </div>

        <div class="footer-tech__col">
          <span class="footer-tech__heading">{{ t('footer_global.product_title') }}</span>
          <ul class="footer-tech__list">
            <li><a href="#" @click.prevent="goToSection('agents')" class="footer-tech__link">{{ t('landing.nav.features') }}</a></li>
            <li><a href="#" @click.prevent="goToSection('agents')" class="footer-tech__link">{{ t('landing.nav.agents') }}</a></li>
            <li><a href="#" @click.prevent="goToSection('pricing')" class="footer-tech__link">{{ t('landing.nav.pricing') }}</a></li>
            <li><a href="#" @click.prevent="goToSection('avis')" class="footer-tech__link">{{ t('landing.nav.reviews') }}</a></li>
            <li><router-link to="/blog" class="footer-tech__link">{{ t('landing.nav.blog') }}</router-link></li>
          </ul>
        </div>

        <div class="footer-tech__col">
          <span class="footer-tech__heading">{{ t('footer_global.tools_title') }}</span>
          <ul class="footer-tech__list">
            <li><router-link to="/free-cv-roast" class="footer-tech__link">{{ t('landing.nav.cv_audit') }}</router-link></li>
            <li><router-link to="/free-interview" class="footer-tech__link">{{ t('landing.nav.simulation') }}</router-link></li>
          </ul>
        </div>

        <div class="footer-tech__col">
          <span class="footer-tech__heading">{{ t('footer_global.platform_title') }}</span>
          <ul class="footer-tech__list">
            <li><router-link to="/login" class="footer-tech__link">{{ t('landing.nav.login') }}</router-link></li>
            <li><router-link to="/register" class="footer-tech__link">{{ t('footer_global.create_account') }}</router-link></li>
          </ul>
        </div>
      </div>

      <div class="footer-tech__bottom">
        <p class="footer-tech__copy">{{ t('footer_global.rights', { year: currentYear }) }}</p>
        <div class="footer-tech__legal">
          <a href="#" class="footer-tech__legal-link">{{ t('footer_global.privacy') }}</a>
          <span class="footer-tech__dot" aria-hidden="true"></span>
          <a href="#" class="footer-tech__legal-link">{{ t('footer_global.terms') }}</a>
        </div>
      </div>
    </div>
  </footer>
</template>

<style scoped>
.footer-tech {
  position: relative;
  margin-top: auto;
  padding: 4rem 0 2rem;
  background: linear-gradient(180deg, #0d0d12 0%, #08080c 100%);
  border-top: 1px solid rgba(255, 255, 255, 0.06);
  overflow: hidden;
}
.footer-tech__glow {
  position: absolute;
  top: -120px;
  left: 50%;
  transform: translateX(-50%);
  width: 600px;
  height: 200px;
  background: radial-gradient(ellipse 80% 50% at 50% 100%, rgba(255, 111, 0, 0.12) 0%, transparent 70%);
  pointer-events: none;
}
.footer-tech__container {
  position: relative;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1.5rem;
}
.footer-tech__grid {
  display: grid;
  grid-template-columns: 1.2fr 1fr 1fr 1fr;
  gap: 3rem 2rem;
  padding-bottom: 3rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}
@media (max-width: 991px) {
  .footer-tech__grid {
    grid-template-columns: 1fr 1fr;
  }
}
@media (max-width: 567px) {
  .footer-tech__grid {
    grid-template-columns: 1fr;
    gap: 2rem;
    padding-bottom: 2rem;
  }
}
.footer-tech__brand-col {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.footer-tech__brand {
  display: inline-flex;
  align-items: center;
  gap: 0.75rem;
  text-decoration: none;
  color: #fff;
  font-weight: 700;
  font-size: 1.25rem;
  letter-spacing: -0.02em;
  transition: color 0.2s;
}
.footer-tech__brand:hover {
  color: #ff8c42;
}
.footer-tech__logo {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  object-fit: cover;
  border: 1px solid rgba(255, 255, 255, 0.1);
}
.footer-tech__tagline {
  font-size: 0.9375rem;
  line-height: 1.6;
  color: rgba(255, 255, 255, 0.6);
  max-width: 320px;
  margin: 0;
}
.footer-tech__accent-line {
  width: 48px;
  height: 3px;
  background: linear-gradient(90deg, #ff6f00, transparent);
  border-radius: 2px;
  margin-top: 0.5rem;
}
.footer-tech__col {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.footer-tech__heading {
  font-size: 0.6875rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.15em;
  color: rgba(255, 111, 0, 0.95);
}
.footer-tech__list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.footer-tech__link {
  font-size: 0.9375rem;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.8);
  text-decoration: none;
  transition: color 0.2s, padding-left 0.2s;
}
.footer-tech__link:hover {
  color: #ff8c42;
  padding-left: 4px;
}
.footer-tech__bottom {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding-top: 2rem;
}
.footer-tech__copy {
  font-size: 0.8125rem;
  color: rgba(255, 255, 255, 0.4);
  margin: 0;
}
.footer-tech__legal {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}
.footer-tech__legal-link {
  font-size: 0.8125rem;
  color: rgba(255, 255, 255, 0.45);
  text-decoration: none;
  transition: color 0.2s;
}
.footer-tech__legal-link:hover {
  color: #ff8c42;
}
.footer-tech__dot {
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.25);
}
</style>
