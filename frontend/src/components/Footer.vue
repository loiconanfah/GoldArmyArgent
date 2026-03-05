<script setup>
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
const currentYear = new Date().getFullYear()
</script>

<template>
  <footer class="footer landing-footer" role="contentinfo">
    <div class="footer-content-wrapper">
      <div class="w-layout-grid footer-links-grid">
        <!-- Product -->
        <div class="footer-links-list-wrapper">
          <div class="footer-links-heading">{{ t('footer_global.product_title') }}</div>
          <div class="footer-list-wrapper">
            <ul role="list" class="footer-links-list">
              <li class="footer-list-item">
                <a href="#agents" class="footer-link-item">{{ t('landing.nav.features') }}</a>
              </li>
              <li class="footer-list-item">
                <a href="#agents" class="footer-link-item">{{ t('landing.nav.agents') }}</a>
              </li>
              <li class="footer-list-item">
                <a href="#pricing" class="footer-link-item">{{ t('landing.nav.pricing') }}</a>
              </li>
              <li class="footer-list-item">
                <a href="#avis" class="footer-link-item">{{ t('landing.nav.reviews') }}</a>
              </li>
              <li class="footer-list-item">
                <a href="#blog" class="footer-link-item">{{ t('landing.nav.blog') }}</a>
              </li>
            </ul>
          </div>
        </div>
        <!-- Free Tools -->
        <div class="footer-links-list-wrapper">
          <div class="footer-links-heading">{{ t('footer_global.tools_title') }}</div>
          <div class="footer-list-wrapper">
            <ul role="list" class="footer-links-list">
              <li class="footer-list-item">
                <router-link to="/free-cv-roast" class="footer-link-item">{{ t('landing.nav.cv_audit') }}</router-link>
              </li>
              <li class="footer-list-item">
                <router-link to="/free-interview" class="footer-link-item">{{ t('landing.nav.simulation') }}</router-link>
              </li>
            </ul>
          </div>
        </div>
        <!-- Account -->
        <div class="footer-links-list-wrapper">
          <div class="footer-links-heading">{{ t('footer_global.platform_title') }}</div>
          <div class="footer-list-wrapper">
            <ul role="list" class="footer-links-list">
              <li class="footer-list-item">
                <router-link to="/login" class="footer-link-item">{{ t('landing.nav.login') }}</router-link>
              </li>
              <li class="footer-list-item">
                <router-link to="/register" class="footer-link-item">{{ t('footer_global.create_account') }}</router-link>
              </li>
              <li class="footer-list-item">
                <router-link to="/blog" class="footer-link-item">{{ t('footer_global.blog_link') }}</router-link>
              </li>
            </ul>
          </div>
        </div>
      </div>

      <div class="w-layout-grid footer-bottom">
        <div class="footer-logo-wrapper">
          <router-link to="/" class="footer-logo-link" aria-label="GoldArmy Home">
            <img src="/logo.png" alt="GoldArmy" loading="lazy" class="logo-footer" />
          </router-link>
          <p class="footer-tagline">{{ t('landing.footer.description') }}</p>
        </div>
        <div class="footer-legal">
          <p class="footer-copyright">{{ t('footer_global.rights', { year: currentYear }) }}</p>
          <div class="footer-legal-links">
            <a href="#" class="footer-link-item">{{ t('footer_global.privacy') }}</a>
            <a href="#" class="footer-link-item">{{ t('footer_global.terms') }}</a>
          </div>
        </div>
      </div>
    </div>
  </footer>
</template>

<style scoped>
/* Fallback when orvimo-landing.css is not loaded (e.g. other pages) */
.landing-footer {
  padding-top: var(--_size---paddingsize--large, 3rem);
  background-color: var(--_theme---background--secondarybackground, #0f0f18);
  color: var(--_theme---textcolor--primarytext, #f1f1f4);
  font-size: var(--_textstyle---fontsize, 1rem);
  line-height: 1.5;
  position: relative;
  bottom: 0;
}

.footer-content-wrapper {
  max-width: var(--_size---site--maxwidth, 75rem);
  width: 100%;
  margin-left: auto;
  margin-right: auto;
  padding-left: var(--_size---site--sitepadding, 1.5rem);
  padding-right: var(--_size---site--sitepadding, 1.5rem);
  box-sizing: border-box;
}

.footer-links-grid {
  display: grid;
  grid-template-columns: 0.25fr 0.25fr 1fr;
  gap: 2rem;
  padding-bottom: var(--_size---paddingsize--small, 1.5rem);
}

.footer-links-heading {
  font-size: var(--_size---fonts--xxs, 0.75rem);
  text-transform: uppercase;
  color: var(--_theme---textcolor--tertiarytext, #6b6b7b);
  margin-bottom: 0.75rem;
  font-weight: 500;
}

.footer-links-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.footer-list-item {
  margin-bottom: 0.5rem;
}

.footer-link-item {
  color: var(--_theme---textcolor--primarytext, #f1f1f4);
  text-decoration: none;
  font-size: 0.9375rem;
  transition: opacity 0.2s ease;
}

.footer-link-item:hover {
  opacity: 0.8;
}

.footer-bottom {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
  padding-top: 2rem;
  padding-bottom: 2rem;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  align-items: end;
}

.footer-logo-wrapper {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.footer-logo-link {
  display: inline-block;
}

.logo-footer {
  width: 70%;
  max-width: 140px;
  height: auto;
  display: block;
}

.footer-tagline {
  font-size: 0.875rem;
  color: var(--_theme---textcolor--secondarytext, #a1a1aa);
  max-width: 28rem;
  margin: 0;
  line-height: 1.5;
}

.footer-legal {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: flex-end;
  gap: 1rem 1.5rem;
}

.footer-copyright {
  font-size: 0.75rem;
  color: var(--_theme---textcolor--tertiarytext, #6b6b7b);
  margin: 0;
}

.footer-legal-links {
  display: flex;
  gap: 1rem;
}

.footer-legal-links .footer-link-item {
  font-size: 0.75rem;
  color: var(--_theme---textcolor--tertiarytext, #6b6b7b);
}

.footer-legal-links .footer-link-item:hover {
  color: var(--_theme---textcolor--primarytext, #f1f1f4);
}

@media screen and (max-width: 991px) {
  .footer-links-grid {
    grid-template-columns: 1fr 1fr;
  }
  .footer-bottom {
    grid-template-columns: 1fr;
    grid-auto-flow: dense;
    gap: 2.5rem;
  }
  .logo-footer {
    width: 60%;
  }
}

@media screen and (max-width: 767px) {
  .footer-links-grid {
    grid-template-columns: 1fr 1fr;
  }
  .footer-legal {
    justify-content: flex-start;
  }
}

/* 479px: align with home (2-col links, full-width logo) */
@media screen and (max-width: 479px) {
  .landing-footer {
    padding-top: var(--_size---paddingsize--small, 1.5rem);
  }
  .footer-links-grid {
    grid-template-columns: 1fr 1fr;
    gap: 1.5rem;
  }
  .footer-list-wrapper.three-cols {
    grid-template-columns: 1fr 1fr;
  }
  .logo-footer {
    width: 100%;
    max-width: 120px;
  }
  .footer-bottom {
    gap: 1.5rem;
    grid-template-columns: 1fr;
    padding-bottom: var(--_size---paddingsize--small, 1.5rem);
  }
  .footer-legal {
    flex-direction: column;
    align-items: flex-start;
  }
}

/* Prevent footer from causing horizontal scroll */
.landing-footer {
  overflow-x: hidden;
  width: 100%;
  box-sizing: border-box;
}
</style>
