<script setup>
import { ref, onMounted, onUnmounted, computed, watch, nextTick } from 'vue'
import { useI18n } from 'vue-i18n'
import { useHead } from '@unhead/vue'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import Footer from '../components/Footer.vue'

gsap.registerPlugin(ScrollTrigger)

const { t } = useI18n()

useHead({
  title: computed(() => t('seo.landing.title')),
  meta: [
    { name: 'description', content: computed(() => t('seo.landing.description')) },
    { property: 'og:title', content: computed(() => t('seo.landing.title')) },
    { property: 'og:type', content: 'website' }
  ]
})

const navOpen = ref(false)
const rootRef = ref(null)

const arrowPath = 'M6.64774 0.127319C6.8175 -0.0424396 7.09266 -0.0424396 7.26242 0.127319L12.9678 5.83267C12.9972 5.8621 13.0199 5.89563 13.0391 5.9303C13.0604 5.96873 13.0777 6.00981 13.0866 6.05426C13.0979 6.11054 13.0978 6.16861 13.0866 6.22491C13.0778 6.26941 13.0604 6.31038 13.0391 6.34886C13.0198 6.38377 12.9974 6.41774 12.9678 6.44735L7.26242 12.1527C7.09267 12.3224 6.81749 12.3224 6.64774 12.1527C6.47799 11.9829 6.478 11.7078 6.64774 11.538L11.611 6.5747H0.434693C0.194629 6.5747 1.76984e-05 6.38007 0 6.14001C0 5.89993 0.194618 5.70531 0.434693 5.70531H11.611L6.64774 0.742002C6.47799 0.572249 6.478 0.297078 6.64774 0.127319Z'

const openFaqIndex = ref(null)

const stickyTitleWords = computed(() => {
  const prefix = t('landing.agents_intro.title_prefix')
  const suffix = t('landing.agents_intro.title_suffix')
  const full = `${prefix} ${suffix}`.trim()
  return full ? full.split(/\s+/) : []
})
const stickyTitlePrefixLength = computed(() => {
  const prefix = t('landing.agents_intro.title_prefix')
  return prefix ? prefix.trim().split(/\s+/).length : 0
})
function stickyWordClass(i) {
  return i >= stickyTitlePrefixLength.value
    ? ['line-split-word', 'tertiary-color-emphasis']
    : ['line-split-word']
}

const faqItems = computed(() => [
  { q: t('landing.faq_items.q1'), a: t('landing.faq_items.a1') },
  { q: t('landing.faq_items.q2'), a: t('landing.faq_items.a2') },
  { q: t('landing.faq_items.q3'), a: t('landing.faq_items.a3') },
  { q: t('landing.faq_items.q4'), a: t('landing.faq_items.a4') },
  { q: t('landing.faq_items.q5'), a: t('landing.faq_items.a5') }
])

watch(navOpen, (open) => {
  document.body.style.overflow = open ? 'hidden' : ''
  document.body.style.touchAction = open ? 'none' : ''
})

let gsapCtx

onMounted(async () => {
  const link = document.createElement('link')
  link.rel = 'stylesheet'
  link.href = '/orvimo-landing.css'
  link.id = 'orvimo-landing-css'
  document.head.appendChild(link)
  document.documentElement.classList.add('w-mod-ix3')
  await nextTick()
  gsapCtx = gsap.context(() => {
    const root = rootRef.value
    if (!root) return
    const section = root.querySelector('#agents')
    const stickyCol = root.querySelector('.home1-left-sticky')
    const cardsScroll = root.querySelector('.home1-cards-scroll')
    const defaultTrigger = { start: 'top 85%', toggleActions: 'play none none none' }
    const revealContent = root.querySelectorAll('[reveal-content="true"]')
    const fadeIn = root.querySelectorAll('[fade-in="true"]')
    const revealCard = root.querySelectorAll('[reveal-card="true"]')
    const lineWords = root.querySelectorAll('#agents .line-split-word')
    gsap.set(revealContent, { opacity: 0, y: 28 })
    gsap.set(fadeIn, { opacity: 0, y: 20 })
    gsap.set(revealCard, { opacity: 0, y: 56 })
    gsap.set(lineWords, { opacity: 0, y: 14 })
    if (revealContent.length) {
      gsap.to(revealContent, {
        opacity: 1,
        y: 0,
        duration: 0.7,
        ease: 'power2.out',
        stagger: 0.08,
        scrollTrigger: { trigger: section || root, ...defaultTrigger }
      })
    }
    if (fadeIn.length) {
      gsap.to(fadeIn, {
        opacity: 1,
        y: 0,
        duration: 0.5,
        ease: 'power2.out',
        stagger: 0.06,
        scrollTrigger: { trigger: section || root, ...defaultTrigger }
      })
    }
    if (revealCard.length) {
      revealCard.forEach((card) => {
        gsap.to(card, {
          opacity: 1,
          y: 0,
          duration: 0.85,
          ease: 'power3.out',
          scrollTrigger: {
            trigger: card,
            start: 'top 88%',
            end: 'top 55%',
            toggleActions: 'play none none none'
          }
        })
      })
    }
    if (lineWords.length) {
      gsap.to(lineWords, {
        opacity: 1,
        y: 0,
        duration: 0.4,
        stagger: 0.03,
        ease: 'power2.out',
        scrollTrigger: { trigger: stickyCol || section || root, ...defaultTrigger }
      })
    }
  }, rootRef)
})

onUnmounted(() => {
  gsapCtx?.revert()
  document.body.style.overflow = ''
  document.body.style.touchAction = ''
  document.getElementById('orvimo-landing-css')?.remove()
  document.documentElement.classList.remove('w-mod-ix3')
})

function closeNav() {
  navOpen.value = false
}
</script>

<template>
  <div ref="rootRef" class="page-wrapper">
    <!-- NAVIGATION - identique home.html -->
    <div class="navigation">
      <header class="navbar w-nav" role="banner" data-collapse="medium" data-animation="default">
        <div class="nav-wrapper">
          <div class="nav-container">
            <div class="nav-left">
              <router-link to="/" class="brand-logo w-nav-brand" aria-current="page">
                <img src="/logo.png" alt="GoldArmy" class="logo-nav" loading="eager" />
              </router-link>
            </div>
            <nav class="nav-menu w-nav-menu" :class="{ 'w--open': navOpen }">
              <a href="#agents" class="nav-link w-nav-link" @click="closeNav">{{ t('landing.nav.features') }}</a>
              <a href="#agents" class="nav-link w-nav-link" @click="closeNav">{{ t('landing.nav.agents') }}</a>
              <a href="#pricing" class="nav-link w-nav-link" @click="closeNav">{{ t('landing.nav.pricing') }}</a>
              <a href="#avis" class="nav-link w-nav-link" @click="closeNav">{{ t('landing.nav.reviews') }}</a>
              <router-link to="/free-cv-roast" class="nav-link w-nav-link" @click="closeNav">{{ t('landing.nav.cv_audit') }}</router-link>
              <router-link to="/free-interview" class="nav-link w-nav-link" @click="closeNav">{{ t('landing.nav.simulation') }}</router-link>
              <a href="#blog" class="nav-link w-nav-link" @click="closeNav">{{ t('landing.nav.blog') }}</a>
              <div class="nav-right-sign-cta-wrap">
                <router-link to="/login" class="menu-sign-btn w-nav-link" @click="closeNav">{{ t('landing.nav.login') }}</router-link>
                <router-link to="/register" class="btn-menu" @click="closeNav">{{ t('landing.nav.get_started') }}</router-link>
              </div>
            </nav>
            <div class="nav-right">
              <router-link to="/login" class="menu-sign-btn w-nav-link desktop-only">{{ t('landing.nav.login') }}</router-link>
              <router-link to="/register" class="btn-menu desktop-only">{{ t('landing.nav.get_started') }}</router-link>
              <button type="button" class="burger w-nav-button" aria-label="Menu" :class="{ 'w--open': navOpen }" :aria-expanded="navOpen" @click="navOpen = !navOpen">
                <div class="icon-wrapper">
                  <div class="burger-icon">
                    <div class="line1"></div>
                    <div class="line2"></div>
                  </div>
                </div>
              </button>
            </div>
          </div>
        </div>
      </header>
    </div>

    <main class="main">
      <!-- HERO 1 -->
      <section class="section hero-1">
        <div class="hero-content">
          <div class="w-layout-grid hero1-grid">
            <div class="hero-left-col">
              <div class="hero-text-wrap">
                <h1 class="hero-heading">{{ t('landing.hero.title_1') }} <span class="tertiary-color-emphasis">{{ t('landing.hero.title_2') }}</span> {{ t('landing.hero.title_3') }}</h1>
                <p class="hero-paragraph">{{ t('landing.hero.description') }}</p>
              </div>
              <router-link to="/register" class="button-arrow w-inline-block" aria-label="CTA">
                <div class="btn-bg-arrow">
                  <svg viewBox="0 0 14 13" fill="none" width="14" height="6" class="btn-icon"><path :d="arrowPath" fill="currentColor"/></svg>
                  <svg viewBox="0 0 14 13" fill="none" width="14" height="6" class="btn-icon" btn-arrow-left=""><path :d="arrowPath" fill="currentColor"/></svg>
                </div>
                <div class="btn-text-mask">
                  <div class="button-arrow-text">{{ t('landing.hero.cta_main') }}</div>
                  <div class="button-arrow-text">{{ t('landing.hero.cta_main') }}</div>
                </div>
              </router-link>
            </div>
            <div class="hero1-background">
              <div class="gradient-wrapper">
                <div class="yellow-gradient" gradient="true"></div>
                <div class="blue-gradient" gradient="true"></div>
                <div class="orange-gradient" gradient="true"></div>
                <div class="light" gradient="true"></div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- SLIDESHOW - App capture GoldArmy -->
      <section class="section slideshow">
        <div class="offset-separator">
          <div class="offset-top"></div>
          <div class="offset-bottom"></div>
        </div>
        <div class="w-layout-blockcontainer container slideshow w-container">
          <h2 class="fsize-m">{{ t('landing.slideshow.title') }}<br /><span class="tertiary-color-emphasis">{{ t('landing.slideshow.title_emphasis') }}</span></h2>
          <div class="slideshow-wrapper">
            <div class="slider w-slider">
              <div class="mask w-slider-mask">
                <div class="slide w-slide">
                  <img src="/images/capture%20app.png" loading="lazy" :alt="t('landing.slideshow.title')" class="slide-img" />
                </div>
              </div>
              <div class="slide-nav w-slider-nav"></div>
            </div>
          </div>
        </div>
      </section>

      <!-- LOGO CLIENTS -->
      <section class="section logo-clients-home1">
        <div class="w-layout-blockcontainer container w-container">
          <div class="client-logos-wrapper">
            <h2 class="fsize-m">{{ t('landing.logos.prefix') }} <span class="tertiary-color-emphasis">{{ t('landing.logos.suffix') }}</span></h2>
            <div class="w-layout-grid clients-logo-grid">
              <img src="https://cdn.prod.website-files.com/69383496538f3c3da700a557/6943c7e0203b31d31009c8a1_Logo-2.svg" loading="lazy" alt="Logo client" class="client-logo-img" />
              <img src="https://cdn.prod.website-files.com/69383496538f3c3da700a557/6943c7e004207716c18cce39_Logo-1.svg" loading="lazy" alt="Logo client" class="client-logo-img" />
              <img src="https://cdn.prod.website-files.com/69383496538f3c3da700a557/6943c7e0f5925df955da51ff_Logo-3.svg" loading="lazy" alt="Logo client" class="client-logo-img" />
              <img src="https://cdn.prod.website-files.com/69383496538f3c3da700a557/6943c7e0a3a82b904e745e92_Logo6.svg" loading="lazy" alt="Logo client" class="client-logo-img" />
              <img src="https://cdn.prod.website-files.com/69383496538f3c3da700a557/6943c7e0e8531b2688fccf34_Logo-4.svg" loading="lazy" alt="Logo client" class="client-logo-img" />
              <img src="https://cdn.prod.website-files.com/69383496538f3c3da700a557/6943c7e00cf1bd4750d08448_Logo-5.svg" loading="lazy" alt="Logo client" class="client-logo-img" />
            </div>
          </div>
        </div>
      </section>

      <!-- HOME1 STICKY - 3 cards GoldArmy (animations: reveal-content, line-split, fade-in, reveal-card) -->
      <section id="agents" class="section home1-sticky">
        <div class="w-layout-blockcontainer container w-container">
          <div class="w-layout-grid home1-2cols">
            <div reveal-content="true" class="home1-left-sticky">
              <h2 class="line-split-heading">
                <template v-for="(word, i) in stickyTitleWords" :key="i">
                  <span :class="stickyWordClass(i)">{{ word }}</span>{{ i !== stickyTitleWords.length - 1 ? ' ' : '' }}
                </template>
              </h2>
              <p line-split="true" class="fsize-body-large">{{ t('landing.agents_intro.paragraph') }}</p>
              <div fade-in="true" class="reveal-content-wrap">
                <router-link
                  to="/register"
                  button-arrow=""
                  aria-label="view more"
                  data-wf--arrow-button--variant="light"
                  class="button-arrow w-inline-block">
                  <div class="btn-bg-arrow">
                    <svg viewBox="0 0 14 13" fill="none" width="14" height="6" btn-arrow="" class="btn-icon"><path :d="arrowPath" fill="currentColor"/></svg>
                    <svg viewBox="0 0 14 13" fill="none" width="14" height="6" btn-arrow-left="" class="btn-icon"><path :d="arrowPath" fill="currentColor"/></svg>
                  </div>
                  <div class="btn-text-mask">
                    <div button-text="" class="button-arrow-text">{{ t('landing.sticky.cta_trial') }}</div>
                    <div button-text="" class="button-arrow-text">{{ t('landing.sticky.cta_trial') }}</div>
                  </div>
                </router-link>
              </div>
            </div>
            <div class="home1-cards-scroll">
              <div card="true" reveal-card="true" class="big-card-home1 first">
                <div card="true" class="updates-banner">updates available</div>
                <div class="big-card-img-wrapper">
                  <img src="/images/sniper.png" loading="lazy" card="true" :alt="t('landing.sticky.card1_title')" class="big-card--home1-img" />
                </div>
                <div class="big-card-text">
                  <p line-split="true">{{ t('landing.sticky.card1_category') }}</p>
                  <h3 line-split="true" class="fsize-s">{{ t('landing.sticky.card1_title') }}</h3>
                  <p line-split="true">{{ t('landing.sticky.card1_desc') }}</p>
                  <router-link
                    to="/opportunities"
                    button-arrow=""
                    aria-label="view more"
                    data-wf--arrow-button--variant="light"
                    class="button-arrow w-inline-block">
                    <div class="btn-bg-arrow">
                      <svg viewBox="0 0 14 13" fill="none" width="14" height="6" btn-arrow="" class="btn-icon"><path :d="arrowPath" fill="currentColor"/></svg>
                      <svg viewBox="0 0 14 13" fill="none" width="14" height="6" btn-arrow-left="" class="btn-icon"><path :d="arrowPath" fill="currentColor"/></svg>
                    </div>
                    <div class="btn-text-mask">
                      <div button-text="" class="button-arrow-text">{{ t('landing.sticky.cta_explore') }}</div>
                      <div button-text="" class="button-arrow-text">{{ t('landing.sticky.cta_explore') }}</div>
                    </div>
                  </router-link>
                </div>
              </div>
              <div reveal-card="true" class="big-card-home1 dark">
                <div class="big-card-img-wrapper">
                  <img src="/images/simulateur.png" loading="lazy" card="true" :alt="t('landing.sticky.card2_title')" class="big-card--home1-img" />
                </div>
                <div class="big-card-text">
                  <p line-split="true">{{ t('landing.sticky.card2_category') }}</p>
                  <h3 line-split="true" class="fsize-s">{{ t('landing.sticky.card2_title') }}</h3>
                  <p line-split="true">{{ t('landing.sticky.card2_desc') }}</p>
                  <router-link
                    to="/mentor"
                    button-arrow=""
                    aria-label="view more"
                    data-wf--arrow-button--variant="dark"
                    class="button-arrow w-variant-3b90a6fd-627b-3ead-4bd6-a49c02101310 w-inline-block">
                    <div class="btn-bg-arrow w-variant-3b90a6fd-627b-3ead-4bd6-a49c02101310">
                      <svg viewBox="0 0 14 13" fill="none" width="14" height="6" btn-arrow="" class="btn-icon"><path :d="arrowPath" fill="currentColor"/></svg>
                      <svg viewBox="0 0 14 13" fill="none" width="14" height="6" btn-arrow-left="" class="btn-icon"><path :d="arrowPath" fill="currentColor"/></svg>
                    </div>
                    <div class="btn-text-mask">
                      <div button-text="" class="button-arrow-text w-variant-3b90a6fd-627b-3ead-4bd6-a49c02101310">{{ t('landing.sticky.cta_explore') }}</div>
                      <div button-text="" class="button-arrow-text w-variant-3b90a6fd-627b-3ead-4bd6-a49c02101310">{{ t('landing.sticky.cta_explore') }}</div>
                    </div>
                  </router-link>
                </div>
              </div>
              <div reveal-card="true" class="big-card-home1 last">
                <div class="big-card-img-wrapper">
                  <img src="/images/crmcandidat.png" loading="lazy" card="true" :alt="t('landing.sticky.card3_title')" class="big-card--home1-img" />
                </div>
                <div class="big-card-text">
                  <p line-split="true">{{ t('landing.sticky.card3_category') }}</p>
                  <h3 line-split="true" class="fsize-s">{{ t('landing.sticky.card3_title') }}</h3>
                  <p line-split="true">{{ t('landing.sticky.card3_desc') }}</p>
                  <router-link
                    to="/crm"
                    button-arrow=""
                    aria-label="view more"
                    data-wf--arrow-button--variant="light"
                    class="button-arrow w-inline-block">
                    <div class="btn-bg-arrow">
                      <svg viewBox="0 0 14 13" fill="none" width="14" height="6" btn-arrow="" class="btn-icon"><path :d="arrowPath" fill="currentColor"/></svg>
                      <svg viewBox="0 0 14 13" fill="none" width="14" height="6" btn-arrow-left="" class="btn-icon"><path :d="arrowPath" fill="currentColor"/></svg>
                    </div>
                    <div class="btn-text-mask">
                      <div button-text="" class="button-arrow-text">{{ t('landing.sticky.cta_explore') }}</div>
                      <div button-text="" class="button-arrow-text">{{ t('landing.sticky.cta_explore') }}</div>
                    </div>
                  </router-link>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- HOME1 3COL - GoldArmy -->
      <section class="section home1-3col">
        <div class="w-layout-blockcontainer container w-container">
          <div class="_3cols-heading">
            <h3 class="center-align">{{ t('landing.threecol.title') }} <br /><span class="tertiary-color-emphasis">{{ t('landing.threecol.title_emphasis') }}</span></h3>
            <p class="fsize-body-large center-align">{{ t('landing.threecol.paragraph') }}</p>
          </div>
          <div class="w-layout-grid home1-3cols">
            <div class="card-item-home1">
              <div class="card-item-img-wrap">
                <img src="/images/sniper.png" loading="lazy" :alt="t('landing.threecol.card1_title')" class="img-card-home1" />
              </div>
              <div class="card-text-content-home1">
                <div>{{ t('landing.threecol.card1_category') }}</div>
                <h4 class="fsize-xxs">{{ t('landing.threecol.card1_title') }}</h4>
                <p>{{ t('landing.threecol.card1_desc') }}</p>
              </div>
            </div>
            <div class="card-item-home1">
              <div class="card-item-img-wrap">
                <img src="/images/crmcandidat.png" loading="lazy" :alt="t('landing.threecol.card2_title')" class="img-card-home1" />
              </div>
              <div class="card-text-content-home1">
                <div>{{ t('landing.threecol.card2_category') }}</div>
                <h4 class="fsize-xxs">{{ t('landing.threecol.card2_title') }}</h4>
                <p>{{ t('landing.threecol.card2_desc') }}</p>
              </div>
            </div>
            <div class="card-item-home1">
              <div class="card-item-img-wrap">
                <img src="/images/simulateur.png" loading="lazy" :alt="t('landing.threecol.card3_title')" class="img-card-home1" />
              </div>
              <div class="card-text-content-home1">
                <div>{{ t('landing.threecol.card3_category') }}</div>
                <h4 class="fsize-xxs">{{ t('landing.threecol.card3_title') }}</h4>
                <p>{{ t('landing.threecol.card3_desc') }}</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- HOME1 DEV - GoldArmy -->
      <section class="section home1-dev">
        <div class="w-layout-blockcontainer container w-container">
          <div class="w-layout-grid dev-home1-grid">
            <h4>{{ t('landing.dev.title') }} <span class="tertiary-color-emphasis">{{ t('landing.dev.title_emphasis') }}</span></h4>
          </div>
          <div class="w-layout-grid dev-home1-grid">
            <div class="features-item-wrapper">
              <div class="code-feature-item">
                <img src="https://cdn.prod.website-files.com/69383496538f3c3da700a557/694eac84caa6687a94014774_dev-research-icon.svg" loading="lazy" :alt="t('landing.dev.feature1_label')" class="code-feature-icon" />
                <div class="fsize-body-large primary-color-emphasis">{{ t('landing.dev.feature1_label') }}</div>
                <p class="primary-color-emphasis">{{ t('landing.dev.feature1_desc') }}</p>
              </div>
              <div class="code-feature-item">
                <img src="https://cdn.prod.website-files.com/69383496538f3c3da700a557/694eac8427aa97ef7752b2e8_orvimo-lab-icon.svg" loading="lazy" :alt="t('landing.dev.feature2_label')" class="code-feature-icon" />
                <div class="fsize-body-large primary-color-emphasis">{{ t('landing.dev.feature2_label') }}</div>
                <p class="primary-color-emphasis">{{ t('landing.dev.feature2_desc') }}</p>
              </div>
              <div class="code-feature-item">
                <img src="https://cdn.prod.website-files.com/69383496538f3c3da700a557/694eac84ff9f10f7f83e0d77_smart-monitoring-orvimo.svg" loading="lazy" :alt="t('landing.dev.feature3_label')" class="code-feature-icon" />
                <div class="fsize-body-large primary-color-emphasis">{{ t('landing.dev.feature3_label') }}</div>
                <p class="primary-color-emphasis">{{ t('landing.dev.feature3_desc') }}</p>
              </div>
              <div class="code-feature-item">
                <img src="https://cdn.prod.website-files.com/69383496538f3c3da700a557/694eac84cec739569d673056_ai-intelligence.svg" loading="lazy" :alt="t('landing.dev.feature4_label')" class="code-feature-icon" />
                <div class="fsize-body-large primary-color-emphasis">{{ t('landing.dev.feature4_label') }}</div>
                <p class="primary-color-emphasis">{{ t('landing.dev.feature4_desc') }}</p>
              </div>
            </div>
            <div class="full-card-right">
              <div class="text-content">
                <h5 class="fsize-xxs">{{ t('landing.dev.card_title') }}</h5>
                <p>{{ t('landing.dev.card_paragraph') }}</p>
                <router-link to="/register" class="button-arrow w-inline-block">
                  <div class="btn-bg-arrow">
                    <svg viewBox="0 0 14 13" fill="none" width="14" height="6" class="btn-icon"><path :d="arrowPath" fill="currentColor"/></svg>
                  </div>
                  <div class="btn-text-mask">
                    <div class="button-arrow-text">{{ t('landing.dev.cta') }}</div>
                    <div class="button-arrow-text">{{ t('landing.dev.cta') }}</div>
                  </div>
                </router-link>
              </div>
              <div class="full-card-img-wrapper">
                <img src="https://cdn.prod.website-files.com/69383496538f3c3da700a557/694eafd3c8ef7fd81aea809b_c809f11685ad994e94791ec0fb55b410_code-ui.png" loading="lazy" :alt="t('landing.dev.card_title')" class="code-ui-img" />
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- IMG GRID MOTION -->
      <section class="section img-grid-motion">
        <div class="motion-grid-wrapper">
          <div class="motion-grid-parallax-wrapper">
            <img src="https://cdn.prod.website-files.com/69383496538f3c3da700a557/695241a041a35e17f8ca2711_victor-UoIiVYka3VY-unsplash.avif" loading="lazy" alt="" class="top-bottom-grid-img" />
          </div>
          <div class="motion-grid-parallax-wrapper">
            <img src="https://cdn.prod.website-files.com/69383496538f3c3da700a557/69523e91c5230423b4d853c3_anna-dziubinska-mVhd5QVlDWw-unsplash.avif" loading="lazy" alt="" class="top-bottom-grid-img" />
          </div>
          <div class="motion-grid-parallax-wrapper">
            <img src="https://cdn.prod.website-files.com/69383496538f3c3da700a557/69523e9761a700887790947f_daniil-komov-WhcfAUy8uKg-unsplash.avif" loading="lazy" alt="" class="top-bottom-grid-img" />
          </div>
          <div class="motion-grid-parallax-wrapper">
            <img src="https://cdn.prod.website-files.com/69383496538f3c3da700a557/69523dc6ae98181d0a14825d_simone-hutsch-l8fyK9RS-OU-unsplash.avif" loading="lazy" alt="" class="central-grid-img" />
          </div>
          <div class="motion-grid-parallax-wrapper">
            <img src="https://cdn.prod.website-files.com/69383496538f3c3da700a557/6948f54b270afe855a420a15_forest-river.avif" loading="lazy" alt="" class="central-grid-img" />
            <div class="title-wrap">
              <h3 class="home-3-grid-motion-tile">Flowing Forward With<br /><span class="accent1-color-emphasis">Intelligent Automation.</span></h3>
            </div>
          </div>
          <div class="motion-grid-parallax-wrapper">
            <img src="https://cdn.prod.website-files.com/69383496538f3c3da700a557/69524198f1ef108473a36c1a_homa-appliances-pWUyHVJgLhg-unsplash.avif" loading="lazy" alt="" class="central-grid-img" />
          </div>
          <div class="motion-grid-parallax-wrapper">
            <img src="https://cdn.prod.website-files.com/69383496538f3c3da700a557/69524198f1ef108473a36c1a_homa-appliances-pWUyHVJgLhg-unsplash.avif" loading="lazy" alt="" class="top-bottom-grid-img" />
          </div>
          <div class="motion-grid-parallax-wrapper">
            <img src="https://cdn.prod.website-files.com/69383496538f3c3da700a557/69523dcbc18b5ae99fc07c04_vitaly-gariev-Tn0fjekZemA-unsplash.avif" loading="lazy" alt="" class="top-bottom-grid-img" />
          </div>
          <div class="motion-grid-parallax-wrapper">
            <img src="https://cdn.prod.website-files.com/69383496538f3c3da700a557/694eb8bfa7dbbd15f4a2fe95_maarten-van-den-heuvel-KSQgzzn3dW0-unsplash.avif" loading="lazy" alt="" class="top-bottom-grid-img" />
          </div>
        </div>
      </section>

      <!-- KEY FIGURES - GoldArmy -->
      <section class="section home1-key-figures">
        <div class="w-layout-blockcontainer container w-container">
          <div class="key-figures-home1-wrapper">
            <div class="w-layout-grid key-figures-grid">
              <div class="heading-wrapper">
                <h4>{{ t('landing.key_figures.title') }} <span class="tertiary-color-emphasis">{{ t('landing.key_figures.title_emphasis') }}</span></h4>
                <p>{{ t('landing.key_figures.paragraph') }}</p>
              </div>
            </div>
            <div class="w-layout-grid key-figures-grid">
              <div class="key-figures-card dark">
                <div class="figures-card-wrapper">
                  <div class="key-number">{{ t('landing.key_figures.card1_number') }}<sup>+</sup></div>
                  <div><strong>{{ t('landing.key_figures.card1_label_1') }}<br />{{ t('landing.key_figures.card1_label_2') }}</strong></div>
                </div>
                <div class="key-card-content-p">
                  <div class="fsize-body-large primary-color-emphasis">{{ t('landing.key_figures.card1_title') }}</div>
                  <p>{{ t('landing.key_figures.card1_desc') }}</p>
                </div>
              </div>
              <div class="key-figures-card dark">
                <div class="figures-card-wrapper">
                  <div class="key-number">{{ t('landing.key_figures.card2_number') }}<sup>%</sup></div>
                  <div><strong>{{ t('landing.key_figures.card2_label_1') }} <br />{{ t('landing.key_figures.card2_label_2') }}</strong></div>
                </div>
                <div class="key-card-content-p">
                  <div class="fsize-body-large primary-color-emphasis">{{ t('landing.key_figures.card2_title') }}</div>
                  <p>{{ t('landing.key_figures.card2_desc') }}</p>
                </div>
              </div>
              <div class="key-figures-card dark">
                <div class="figures-card-wrapper">
                  <div class="key-number">{{ t('landing.key_figures.card3_number') }}<sup>+</sup></div>
                  <div><strong>{{ t('landing.key_figures.card3_label_1') }} <br />{{ t('landing.key_figures.card3_label_2') }}</strong></div>
                </div>
                <div class="key-card-content-p">
                  <div class="fsize-body-large primary-color-emphasis">{{ t('landing.key_figures.card3_title') }}</div>
                  <p>{{ t('landing.key_figures.card3_desc') }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- TESTIMONIALS - GoldArmy -->
      <section id="avis" class="section home1-testimonials">
        <div class="w-layout-blockcontainer container w-container">
          <div class="w-layout-grid home1-grid-testimonials">
            <div class="testimonial-card-wrapper">
              <div class="testimonial-card">
                <div class="testimonial-logo">
                  <img src="https://cdn.prod.website-files.com/69383496538f3c3da700a557/6943c7e00cf1bd4750d08448_Logo-5.svg" loading="lazy" alt="Logo client" />
                </div>
                <div class="testimonial-content">
                  <div class="testimonial-quote">"{{ t('landing.testimonials.quote1') }}"</div>
                  <div><strong class="testimonial-author">{{ t('landing.testimonials.author1') }}</strong></div>
                </div>
              </div>
              <div class="testimonial-card">
                <div class="testimonial-logo">
                  <img src="https://cdn.prod.website-files.com/69383496538f3c3da700a557/6943c7e0e8531b2688fccf34_Logo-4.svg" loading="lazy" alt="Logo client" />
                </div>
                <div class="testimonial-content">
                  <div class="testimonial-quote">"{{ t('landing.testimonials.quote2') }}"</div>
                  <div><strong class="testimonial-author">{{ t('landing.testimonials.author2') }}</strong></div>
                </div>
              </div>
            </div>
            <div class="testimonial-card-bg-img dark">
              <div class="testimonial-logo">
                <img src="https://cdn.prod.website-files.com/69383496538f3c3da700a557/694eba67e2e43f7ad899aa03_Logo-3-white.svg" loading="lazy" alt="" />
              </div>
              <div class="testimonial-content">
                <div class="testimonial-quote">"{{ t('landing.testimonials.quote3') }}"</div>
                <div><strong class="testimonial-author">{{ t('landing.testimonials.author3') }}</strong></div>
              </div>
              <div class="testimonial-bg-wrapper">
                <div class="gradient-testimonall"></div>
                <img class="testimonial-bg-img" src="https://cdn.prod.website-files.com/69383496538f3c3da700a557/694eb8bfa7dbbd15f4a2fe95_maarten-van-den-heuvel-KSQgzzn3dW0-unsplash.avif" alt="" loading="lazy" />
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- BLOG HOME1 - GoldArmy -->
      <section id="blog" class="section blog-home1">
        <div class="w-layout-blockcontainer container w-container">
          <div class="heading-wrapper">
            <h2 class="header-title">{{ t('landing.blog.header_title') }}</h2>
            <h2 class="header-subtitle">{{ t('landing.blog.header_subtitle') }}</h2>
          </div>
          <div class="blog-list-featured">
            <div class="blog-item-featured featured">
              <a href="#" class="blog-list-img-wrapper blog-v1 featured w-inline-block">
                <img src="https://cdn.prod.website-files.com/69383496538f3c3da700a56e/693934e70995d1778cf1edbd_jimmy-chang-ACt8ycSzpdE-unsplash.avif" loading="lazy" alt="" class="blog-img" />
              </a>
              <div class="blog-list-content">
                <div class="blog-category-wrapper">
                  <div class="blog-category-title featured">{{ t('landing.blog.featured_category') }}</div>
                </div>
                <a href="#" class="blog-title-wrapper w-inline-block">
                  <div class="blog-title-text featured">{{ t('landing.blog.featured_title') }}</div>
                </a>
                <div class="summary-wrapper">
                  <p class="summary-text featured">{{ t('landing.blog.featured_summary') }}</p>
                </div>
                <div class="date-wrapper">
                  <div class="date">—</div>
                  <div class="date">{{ t('landing.blog.featured_date') }}</div>
                </div>
              </div>
            </div>
          </div>
          <div class="blog-list-home1">
            <div class="blog-item">
              <a href="#" class="blog-list-img-wrapper blog-v1 w-inline-block">
                <img src="https://cdn.prod.website-files.com/69383496538f3c3da700a56e/693939b6497441ceb33405f3_daniil-komov-WhcfAUy8uKg-unsplash.avif" loading="lazy" alt="" class="blog-img" />
              </a>
              <div class="blog-list-content">
                <div class="blog-category-wrapper"><div class="blog-category-title">{{ t('landing.blog.item1_category') }}</div></div>
                <a href="#" class="blog-title-wrapper w-inline-block"><div class="blog-title-text">{{ t('landing.blog.item1_title') }}</div></a>
                <div class="summary-wrapper"><p class="summary-text">{{ t('landing.blog.item1_summary') }}</p></div>
                <div class="date-wrapper"><div class="date">—</div><div class="date">{{ t('landing.blog.item_date') }}</div></div>
              </div>
            </div>
            <div class="blog-item">
              <a href="#" class="blog-list-img-wrapper blog-v1 w-inline-block">
                <img src="https://cdn.prod.website-files.com/69383496538f3c3da700a56e/69393a447db46aaa909fe6d4_homa-appliances-pWUyHVJgLhg-unsplash.avif" loading="lazy" alt="" class="blog-img" />
              </a>
              <div class="blog-list-content">
                <div class="blog-category-wrapper"><div class="blog-category-title">{{ t('landing.blog.item2_category') }}</div></div>
                <a href="#" class="blog-title-wrapper w-inline-block"><div class="blog-title-text">{{ t('landing.blog.item2_title') }}</div></a>
                <div class="summary-wrapper"><p class="summary-text">{{ t('landing.blog.item2_summary') }}</p></div>
                <div class="date-wrapper"><div class="date">—</div><div class="date">{{ t('landing.blog.item_date') }}</div></div>
              </div>
            </div>
            <div class="blog-item">
              <a href="#" class="blog-list-img-wrapper blog-v1 w-inline-block">
                <img src="https://cdn.prod.website-files.com/69383496538f3c3da700a56e/693939f6f6dda0fc21949f22_olena-bohovyk-3BlVILvh9hM-unsplash.avif" loading="lazy" alt="" class="blog-img" />
              </a>
              <div class="blog-list-content">
                <div class="blog-category-wrapper"><div class="blog-category-title">{{ t('landing.blog.item3_category') }}</div></div>
                <a href="#" class="blog-title-wrapper w-inline-block"><div class="blog-title-text">{{ t('landing.blog.item3_title') }}</div></a>
                <div class="summary-wrapper"><p class="summary-text">{{ t('landing.blog.item3_summary') }}</p></div>
                <div class="date-wrapper"><div class="date">—</div><div class="date">{{ t('landing.blog.item_date') }}</div></div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- PRICING - GoldArmy: Free, 9.99, 19.99 -->
      <section id="pricing" class="section home1-pricing">
        <div class="w-layout-blockcontainer container w-container">
          <div class="pricing-v3-wrapper">
            <div class="home1-pricing-left-col">
              <div class="heading-wrapper">
                <h2>{{ t('landing.pricing.title') }}</h2>
                <p>{{ t('landing.pricing.paragraph') }}</p>
              </div>
              <div class="pricing-v3-picture-wrap">
                <div class="img-curtain"></div>
                <div class="pricing-v3-picture-content">
                  <div class="pricing-v3-picture-heading">{{ t('landing.pricing.picture_heading') }}</div>
                  <p>{{ t('landing.pricing.picture_paragraph') }}</p>
                </div>
                <div class="pricingv3-background">
                  <img src="https://cdn.prod.website-files.com/69383496538f3c3da700a557/6942c7713ce8ee94735cd376_brooke-cagle-LCcFI_26diA-unsplash.avif" loading="lazy" alt="" class="img-pricing-v3" />
                </div>
              </div>
            </div>
            <div class="w-layout-grid grid-pricing-v3-home1">
              <div class="pricing-v3-col home1 first">
                <div class="pricing-row1">
                  <div class="pricing-title-wrap">
                    <div class="price-title">{{ t('landing.pricing.plan1_title') }}</div>
                    <div>{{ t('landing.pricing.plan1_desc') }}</div>
                  </div>
                  <div class="price-wrapper">
                    <div class="billed-annualy">
                      <div class="price">{{ t('landing.pricing.plan1_price') }}</div>
                      <div class="period">{{ t('landing.pricing.plan1_period_monthly') }}</div>
                    </div>
                  </div>
                  <div class="pricing-infos">
                    <div class="info-figure">{{ t('landing.pricing.plan1_info_figure') }}</div>
                    <div class="infos-sub-text">{{ t('landing.pricing.plan1_info_1') }} <br />{{ t('landing.pricing.plan1_info_2') }}</div>
                  </div>
                  <router-link to="/register" class="pricing-button w-inline-block">
                    <div class="price-btn-cta">{{ t('landing.pricing.plan1_cta') }}</div>
                    <div class="price-btn-subtext">{{ t('landing.pricing.plan1_subtext') }}</div>
                  </router-link>
                  <div class="infos-2-wrapper">
                    <img src="https://cdn.prod.website-files.com/69383496538f3c3da700a557/69416fc4e9533b6332c923d0_hosting-icon-black.svg" loading="lazy" alt="" />
                    <div>{{ t('landing.pricing.plan1_hosted') }}</div>
                  </div>
                </div>
              </div>
              <div class="pricing-v3-col home1">
                <div class="pricing-row1">
                  <div class="pricing-title-wrap">
                    <div class="price-title">{{ t('landing.pricing.plan2_title') }}</div>
                    <div>{{ t('landing.pricing.plan2_desc') }}</div>
                  </div>
                  <div class="price-wrapper">
                    <div class="billed-annualy">
                      <div class="price">{{ t('landing.pricing.plan2_price') }}</div>
                      <div class="period">{{ t('landing.pricing.plan2_period_annual') }}</div>
                    </div>
                    <div class="billed-monthly">
                      <div class="price">{{ t('landing.pricing.plan2_price') }}</div>
                      <div class="period">{{ t('landing.pricing.plan2_period_monthly') }}</div>
                    </div>
                  </div>
                  <div class="pricing-infos">
                    <div class="info-figure">{{ t('landing.pricing.plan2_info_figure') }}</div>
                    <div class="infos-sub-text">{{ t('landing.pricing.plan2_info_1') }} <br />{{ t('landing.pricing.plan2_info_2') }}</div>
                  </div>
                  <router-link to="/register" class="pricing-button w-inline-block">
                    <div class="price-btn-cta">{{ t('landing.pricing.plan2_cta') }}</div>
                    <div class="price-btn-subtext">{{ t('landing.pricing.plan2_subtext') }}</div>
                  </router-link>
                  <div class="infos-2-wrapper">
                    <img src="https://cdn.prod.website-files.com/69383496538f3c3da700a557/69416fc4e9533b6332c923d0_hosting-icon-black.svg" loading="lazy" alt="" />
                    <div>{{ t('landing.pricing.plan2_hosted') }}</div>
                  </div>
                </div>
              </div>
              <div class="pricing-v3-col home1">
                <div class="pricing-row1">
                  <div class="pricing-title-wrap">
                    <div class="price-title">{{ t('landing.pricing.plan3_title') }}</div>
                    <div>{{ t('landing.pricing.plan3_desc') }}</div>
                  </div>
                  <div class="price-wrapper">
                    <div class="billed-annualy">
                      <div class="price">{{ t('landing.pricing.plan3_price') }}</div>
                      <div class="period">{{ t('landing.pricing.plan3_period_annual') }}</div>
                    </div>
                    <div class="billed-monthly">
                      <div class="price">{{ t('landing.pricing.plan3_price') }}</div>
                      <div class="period">{{ t('landing.pricing.plan3_period_monthly') }}</div>
                    </div>
                  </div>
                  <div class="pricing-infos">
                    <div class="info-figure">{{ t('landing.pricing.plan3_info_figure') }}</div>
                    <div class="infos-sub-text">{{ t('landing.pricing.plan3_info_1') }} <br />{{ t('landing.pricing.plan3_info_2') }}</div>
                  </div>
                  <router-link to="/register" class="pricing-button w-inline-block">
                    <div class="price-btn-cta">{{ t('landing.pricing.plan3_cta') }}</div>
                    <div class="price-btn-subtext">{{ t('landing.pricing.plan3_subtext') }}</div>
                  </router-link>
                  <div class="infos-2-wrapper">
                    <img src="https://cdn.prod.website-files.com/69383496538f3c3da700a557/6941757c14730bd9f517661a_self-hosting-dark.svg" loading="lazy" alt="" />
                    <div>{{ t('landing.pricing.plan3_hosted') }}</div>
                  </div>
                </div>
              </div>
              <div class="pricing-v3-col home1 dark last">
                <div class="pricing-row1">
                  <div class="pricing-title-wrap">
                    <div class="price-title">{{ t('landing.pricing.plan4_title') }}</div>
                    <div>{{ t('landing.pricing.plan4_desc') }}</div>
                  </div>
                  <div class="price-wrapper">
                    <div class="price">{{ t('landing.pricing.plan4_price') }}</div>
                  </div>
                  <div class="pricing-infos">
                    <img src="https://cdn.prod.website-files.com/69383496538f3c3da700a557/694176ce78bb904b99d64825_Custom.svg" loading="lazy" alt="" />
                    <div class="infos-sub-text">{{ t('landing.pricing.plan4_info_1') }} <br />{{ t('landing.pricing.plan4_info_2') }}</div>
                  </div>
                  <router-link to="/register" class="pricing-button accent1 w-inline-block">
                    <div class="price-btn-cta">{{ t('landing.pricing.plan4_cta') }}</div>
                  </router-link>
                  <div class="infos-2-wrapper">
                    <img src="https://cdn.prod.website-files.com/69383496538f3c3da700a557/69416fc4883379fdc3e30642_hosting-icon-white.svg" loading="lazy" alt="" />
                    <img src="https://cdn.prod.website-files.com/69383496538f3c3da700a557/6941757c333623480a910900_self-hosting-white.svg" loading="lazy" alt="" />
                    <div>{{ t('landing.pricing.plan4_hosted') }}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- FAQ - GoldArmy -->
      <section class="section faq-home1">
        <div class="w-layout-blockcontainer container w-container">
          <h2 class="center-align">{{ t('landing.faq_title') }}</h2>
          <div class="faq-list">
            <div v-for="(faq, i) in faqItems" :key="i" class="accordion-item" :class="{ 'w--open': openFaqIndex === i }">
              <div class="accordion-title-toggle" @click="openFaqIndex = openFaqIndex === i ? null : i">
                <div>{{ faq.q }}</div>
                <div class="accordion-toggle">
                  <div class="cross-h"></div>
                  <div class="cross-v"></div>
                </div>
              </div>
              <div class="accordion-content">
                <p class="accordion-content-text">{{ faq.a }}</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- CTA V1 - GoldArmy -->
      <section class="section cta-v1">
        <div class="cta1-wrapper">
          <div class="w-layout-grid cta1-content">
            <div class="cta-text-wrapper-left">
              <h2 class="heading-cta">{{ t('landing.cta.line1') }}<br />{{ t('landing.cta.line2') }}<br />{{ t('landing.cta.line3') }}</h2>
            </div>
            <div class="cta-text-wrapper-right">
              <div class="cta-text-right">{{ t('landing.cta.subtitle') }}</div>
              <div class="reveal-content-wrap">
                <router-link to="/register" class="button-default w-button">{{ t('landing.cta.button') }}</router-link>
              </div>
            </div>
          </div>
          <div class="background-cta">
            <img class="cta-img-bg" src="https://cdn.prod.website-files.com/69383496538f3c3da700a557/6939c21874a51449ee9fd368_background.avif" alt="" loading="lazy" />
          </div>
        </div>
      </section>
    </main>

    <Footer />
  </div>
</template>

<style scoped>
/* overflow-x: clip so position:sticky works in #agents (overflow-x: hidden breaks it) */
.page-wrapper {
  min-height: 100vh;
  overflow-x: clip;
}
.main {
  overflow-x: clip;
}
.desktop-only { display: none; }
@media (min-width: 992px) {
  .desktop-only { display: inline-block; }
  .nav-menu .nav-right-sign-cta-wrap { display: none; }
}

/* Mobile: show nav menu when burger open (override orvimo display:none) */
@media screen and (max-width: 991px) {
  .page-wrapper .nav-menu.w--open {
    display: flex !important;
    flex-direction: column;
    padding-top: 5rem;
    padding-left: 1.5rem;
    padding-right: 1.5rem;
    top: 0;
    left: 0;
    right: 0;
    position: fixed;
    z-index: 100;
  }
  .page-wrapper .nav-container {
    display: grid;
    grid-template-columns: 1fr auto;
  }
}

.accordion-item.w--open .accordion-content {
  height: auto;
  overflow: visible;
  padding-bottom: 1rem;
}
.accordion-item.w--open .cross-v {
  transform: rotate(90deg);
}

/* Line-split animation: words start hidden, GSAP reveals */
.line-split-heading .line-split-word {
  display: inline-block;
  margin-right: 0.2em;
  opacity: 0;
}

/* Responsive: containers and sections */
.page-wrapper :deep(.w-container),
.page-wrapper :deep(.container) {
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
}
@media screen and (max-width: 991px) {
  .page-wrapper :deep(.w-container),
  .page-wrapper :deep(.container) {
    padding-left: 1.5rem;
    padding-right: 1.5rem;
  }
}
@media screen and (max-width: 767px) {
  .page-wrapper :deep(.container),
  .page-wrapper :deep(.w-container) {
    padding-left: 1rem;
    padding-right: 1rem;
  }
  .page-wrapper :deep(.hero-content) {
    height: auto;
    min-height: 70vh;
    padding-top: 6rem;
  }
  .page-wrapper :deep(.hero-heading) {
    font-size: clamp(1.75rem, 5vw, 2.5rem);
  }
  .page-wrapper :deep(.slide-img),
  .page-wrapper :deep(.img-card-home1),
  .page-wrapper :deep(.big-card--home1-img) {
    max-width: 100%;
    height: auto;
  }
}
@media screen and (max-width: 479px) {
  .page-wrapper :deep(.container),
  .page-wrapper :deep(.w-container) {
    padding-left: 0.75rem;
    padding-right: 0.75rem;
  }
  .page-wrapper :deep(.hero-heading) {
    font-size: clamp(1.5rem, 4vw, 2rem);
  }
  .page-wrapper :deep(.grid-pricing-v3-home1) {
    grid-template-columns: 1fr;
  }
}

/* Global: prevent horizontal overflow on landing */
.page-wrapper :deep(main img),
.page-wrapper :deep(.slide-img),
.page-wrapper :deep(.img-card-home1),
.page-wrapper :deep(.big-card--home1-img),
.page-wrapper :deep(.code-ui-img),
.page-wrapper :deep(.client-logo-img) {
  max-width: 100%;
  height: auto;
  object-fit: contain;
}
.page-wrapper :deep(.w-layout-grid),
.page-wrapper :deep(.w-layout-blockcontainer) {
  box-sizing: border-box;
}
</style>
