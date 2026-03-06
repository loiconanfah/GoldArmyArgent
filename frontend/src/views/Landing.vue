<script setup>
import { ref, onMounted, onUnmounted, computed, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useHead } from '@unhead/vue'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import Footer from '../components/Footer.vue'
import LandingNav from '../components/LandingNav.vue'

gsap.registerPlugin(ScrollTrigger)

const route = useRoute()
const { t, locale } = useI18n()

// Apply ?lang= from URL (for SEO / shared links)
if (route.query.lang === 'fr' || route.query.lang === 'en') {
  locale.value = route.query.lang
  if (typeof localStorage !== 'undefined') localStorage.setItem('language', route.query.lang)
}

const logoUrl = computed(() => `${typeof window !== 'undefined' ? window.location.origin : 'https://www.goldarmyai.com'}/images/logosansfond.png`)
const canonicalUrl = computed(() => {
  const base = typeof window !== 'undefined' ? window.location.origin : 'https://www.goldarmyai.com'
  const path = typeof window !== 'undefined' ? window.location.pathname || '/' : '/'
  return path === '/' ? base + '/' : base + path
})

useHead({
  title: computed(() => t('seo.landing.title')),
  htmlAttrs: {
    lang: computed(() => locale.value)
  },
  link: [
    { rel: 'canonical', href: canonicalUrl },
    { rel: 'alternate', hreflang: 'fr', href: computed(() => `${typeof window !== 'undefined' ? window.location.origin : 'https://www.goldarmyai.com'}/?lang=fr`) },
    { rel: 'alternate', hreflang: 'en', href: computed(() => `${typeof window !== 'undefined' ? window.location.origin : 'https://www.goldarmyai.com'}/?lang=en`) },
    { rel: 'alternate', hreflang: 'x-default', href: computed(() => `${typeof window !== 'undefined' ? window.location.origin : 'https://www.goldarmyai.com'}/`) }
  ],
  meta: [
    { name: 'description', content: computed(() => t('seo.landing.description')) },
    { name: 'robots', content: 'index, follow' },
    { property: 'og:type', content: 'website' },
    { property: 'og:title', content: computed(() => t('seo.landing.title')) },
    { property: 'og:description', content: computed(() => t('seo.landing.description')) },
    { property: 'og:image', content: logoUrl },
    { property: 'og:image:alt', content: 'GoldArmy — Co-pilote de carrière propulsé par l\'IA' },
    { property: 'og:url', content: canonicalUrl },
    { property: 'og:site_name', content: 'GoldArmy' },
    { property: 'og:locale', content: computed(() => locale.value === 'fr' ? 'fr_FR' : 'en_GB') },
    { name: 'twitter:card', content: 'summary_large_image' },
    { name: 'twitter:title', content: computed(() => t('seo.landing.title')) },
    { name: 'twitter:description', content: computed(() => t('seo.landing.description')) },
    { name: 'twitter:image', content: logoUrl }
  ]
})

const rootRef = ref(null)
const heroLogoRef = ref(null)

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
function stickyWordSpace(i) {
  return i !== stickyTitleWords.value.length - 1 ? ' ' : ''
}

const faqItems = computed(() => [
  { q: t('landing.faq_items.q1'), a: t('landing.faq_items.a1') },
  { q: t('landing.faq_items.q2'), a: t('landing.faq_items.a2') },
  { q: t('landing.faq_items.q3'), a: t('landing.faq_items.a3') },
  { q: t('landing.faq_items.q4'), a: t('landing.faq_items.a4') },
  { q: t('landing.faq_items.q5'), a: t('landing.faq_items.a5') }
])

let gsapCtx

function runScrollReveals(root) {
  const section = root.querySelector('#agents')
  const stickyCol = root.querySelector('.home1-left-sticky')
  const cardsScroll = root.querySelector('.home1-cards-scroll')
  const threecolSection = root.querySelector('.home1-3col')
  const defaultTrigger = { start: 'top 85%', toggleActions: 'play none none none' }
  const revealContentAgents = section ? section.querySelectorAll('[reveal-content="true"]') : []
  const fadeInAgents = section ? section.querySelectorAll('[fade-in="true"]') : []
  const revealContentThreecol = threecolSection ? threecolSection.querySelectorAll('[reveal-content="true"]') : []
  const fadeInThreecol = threecolSection ? threecolSection.querySelectorAll('[fade-in="true"]') : []
  const revealCard = root.querySelectorAll('[reveal-card="true"]')
  const lineWords = root.querySelectorAll('#agents .line-split-word')

  gsap.set([...revealContentAgents, ...revealContentThreecol], { opacity: 0, y: 28 })
  gsap.set([...fadeInAgents, ...fadeInThreecol], { opacity: 0, y: 20 })
  gsap.set(revealCard, { opacity: 0, y: 56 })
  gsap.set(lineWords, { opacity: 0, y: 14 })

  if (revealContentAgents.length) {
    gsap.to(revealContentAgents, {
      opacity: 1,
      y: 0,
      duration: 0.7,
      ease: 'power2.out',
      stagger: 0.08,
      scrollTrigger: { trigger: section || root, ...defaultTrigger }
    })
  }
  if (fadeInAgents.length) {
    gsap.to(fadeInAgents, {
      opacity: 1,
      y: 0,
      duration: 0.5,
      ease: 'power2.out',
      stagger: 0.06,
      scrollTrigger: { trigger: section || root, ...defaultTrigger }
    })
  }
  if (revealContentThreecol.length) {
    gsap.to(revealContentThreecol, {
      opacity: 1,
      y: 0,
      duration: 0.7,
      ease: 'power2.out',
      stagger: 0.08,
      scrollTrigger: { trigger: threecolSection || root, ...defaultTrigger }
    })
  }
  if (fadeInThreecol.length) {
    gsap.to(fadeInThreecol, {
      opacity: 1,
      y: 0,
      duration: 0.5,
      ease: 'power2.out',
      stagger: 0.06,
      scrollTrigger: { trigger: threecolSection || root, ...defaultTrigger }
    })
  }
  if (revealCard.length) {
    gsap.to(revealCard, {
      opacity: 1,
      y: 0,
      duration: 0.85,
      stagger: 0.12,
      ease: 'power3.out',
      scrollTrigger: {
        trigger: section || cardsScroll || root,
        start: 'top 88%',
        toggleActions: 'play none none none'
      }
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

  ScrollTrigger.refresh()
}

function forceRevealFallback(rootEl) {
  if (!rootEl) return
  const hidden = rootEl.querySelectorAll('[reveal-content="true"], [fade-in="true"], [reveal-card="true"], #agents .line-split-word')
  if (hidden.length) gsap.set(hidden, { opacity: 1, y: 0 })
}

onMounted(async () => {
  const link = document.createElement('link')
  link.rel = 'stylesheet'
  link.href = '/orvimo-landing.css'
  link.id = 'orvimo-landing-css'
  document.head.appendChild(link)
  document.documentElement.classList.add('w-mod-ix3')

  const waitForStyles = new Promise((resolve) => {
    if (link.sheet && link.sheet.cssRules?.length) return resolve()
    link.onload = () => resolve()
    link.onerror = () => resolve()
    setTimeout(resolve, 150)
  })

  await Promise.all([nextTick(), waitForStyles])

  const root = rootRef.value
  if (!root) return

  const heroLogoEl = heroLogoRef.value
  if (heroLogoEl) {
    gsap.set(heroLogoEl, { opacity: 0, scale: 0.88, y: 20 })
    gsap.to(heroLogoEl, {
      opacity: 1,
      scale: 1,
      y: 0,
      duration: 1.1,
      ease: 'power3.out',
      delay: 0.25
    })
    gsap.to(heroLogoEl, {
      y: -8,
      duration: 2.2,
      ease: 'sine.inOut',
      repeat: -1,
      yoyo: true,
      delay: 1.4
    })
  }

  gsapCtx = gsap.context(() => {
    runScrollReveals(root)

    requestAnimationFrame(() => {
      ScrollTrigger.refresh()
      requestAnimationFrame(() => ScrollTrigger.refresh())
    })

    if (typeof window !== 'undefined') {
      const onLoad = () => {
        ScrollTrigger.refresh()
      }
      if (document.readyState === 'complete') onLoad()
      else window.addEventListener('load', onLoad)
    }

    setTimeout(() => {
      const stillHidden = root.querySelectorAll('[reveal-content="true"], [fade-in="true"], [reveal-card="true"], #agents .line-split-word')
      const anyHidden = [...stillHidden].some((el) => parseFloat(getComputedStyle(el).opacity) < 0.1)
      if (anyHidden) forceRevealFallback(root)
    }, 2500)
  }, root)
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
    <LandingNav />
    <main class="main">
      <!-- HERO 1 -->
      <section class="section hero-1">
        <!-- Mobile-first hero (visible only < 992px) -->
        <div class="hero-mobile">
          <div class="hero-mobile__logo-wrap">
            <img src="/images/logosansfond.png" alt="GoldArmy" class="hero-mobile__logo" />
          </div>
          <span class="hero-mobile__badge">{{ t('landing.hero.badge') }}</span>
          <h1 class="hero-mobile__title">{{ t('landing.hero.title_1') }} <span class="hero-mobile__title-accent">{{ t('landing.hero.title_2') }}</span> {{ t('landing.hero.title_3') }}</h1>
          <p class="hero-mobile__desc">{{ t('landing.hero.description') }}</p>
          <router-link to="/register" class="hero-mobile__cta" aria-label="CTA">
            <span>{{ t('landing.hero.cta_main') }}</span>
            <svg class="hero-mobile__cta-arrow" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true"><path fill-rule="evenodd" d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-4.293-4.293a1 1 0 010-1.414z" clip-rule="evenodd"/></svg>
          </router-link>
        </div>
        <!-- Desktop hero (visible >= 992px) -->
        <div class="hero-content hero-content--desktop">
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
              <div ref="heroLogoRef" class="hero-logo-wrap hero-logo-wrap--desktop">
                <img src="/images/logosansfond.png" alt="GoldArmy" class="hero-logo" />
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
                <template v-if="stickyTitleWords.length">
                  <template v-for="(word, i) in stickyTitleWords" :key="i">
                    <span :class="stickyWordClass(i)">{{ word }}</span>{{ stickyWordSpace(i) }}
                  </template>
                </template>
                <template v-else>
                  {{ t('landing.agents_intro.title_prefix') }} <span class="tertiary-color-emphasis">{{ t('landing.agents_intro.title_suffix') }}</span>
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

      <!-- HOME1 3COL - GoldArmy (structure identique home: reveal-content, line-split, fade-in) -->
      <section class="section home1-3col">
        <div class="w-layout-blockcontainer container w-container">
          <div reveal-content="true" class="_3cols-heading">
            <h3 line-split="true" class="center-align">{{ t('landing.threecol.title') }} <br /><span class="tertiary-color-emphasis">{{ t('landing.threecol.title_emphasis') }}</span></h3>
            <p line-split="true" class="fsize-body-large center-align">{{ t('landing.threecol.paragraph') }}</p>
                        </div>
          <div reveal-content="true" class="w-layout-grid home1-3cols">
            <div fade-in="true" class="card-item-home1">
              <div class="card-item-img-wrap">
                <img src="/images/sniper.png" loading="lazy" :alt="t('landing.threecol.card1_title')" class="img-card-home1" />
                    </div>
              <div class="card-text-content-home1">
                <div>{{ t('landing.threecol.card1_category') }}</div>
                <h4 class="fsize-xxs">{{ t('landing.threecol.card1_title') }}</h4>
                <p>{{ t('landing.threecol.card1_desc') }}</p>
                        </div>
                    </div>
            <div fade-in="true" class="card-item-home1">
              <div class="card-item-img-wrap">
                <img src="/images/crmcandidat.png" loading="lazy" :alt="t('landing.threecol.card2_title')" class="img-card-home1" />
                </div>
              <div class="card-text-content-home1">
                <div>{{ t('landing.threecol.card2_category') }}</div>
                <h4 class="fsize-xxs">{{ t('landing.threecol.card2_title') }}</h4>
                <p>{{ t('landing.threecol.card2_desc') }}</p>
            </div>
            </div>
            <div fade-in="true" class="card-item-home1">
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
/* Hero desktop: logo à droite, animé par GSAP */
.page-wrapper :deep(.hero-content--desktop) {
  display: flex;
}
.page-wrapper :deep(.hero-logo-wrap) {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  pointer-events: none;
  z-index: 2;
}
.page-wrapper :deep(.hero-logo) {
  max-width: min(42vw, 380px);
  max-height: min(55vh, 320px);
  width: auto;
  height: auto;
  object-fit: contain;
  filter: drop-shadow(0 20px 40px rgba(0, 0, 0, 0.35));
}

/* ─── Mobile hero (design dédié, fun & UX) ─── */
.hero-mobile {
  display: none;
}
@media screen and (max-width: 991px) {
  .page-wrapper :deep(.section.hero-1) {
    min-height: 0;
    padding-top: 1rem;
    padding-bottom: 2rem;
  }
  .page-wrapper :deep(.hero-content--desktop) {
    display: none !important;
  }
  .hero-mobile {
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    padding: 1.5rem 1.25rem 2.5rem;
    max-width: 480px;
    margin: 0 auto;
  }
  .hero-mobile__logo-wrap {
    width: 88px;
    height: 88px;
    flex-shrink: 0;
    margin-bottom: 1rem;
    animation: hero-mobile-logo-float 4s ease-in-out infinite;
  }
  .hero-mobile__logo {
    width: 100%;
    height: 100%;
    object-fit: contain;
    filter: drop-shadow(0 8px 24px rgba(99, 102, 241, 0.25));
  }
  .hero-mobile__badge {
    display: inline-block;
    font-size: 0.6875rem;
    font-weight: 800;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: rgba(255, 255, 255, 0.7);
    background: linear-gradient(135deg, rgba(99, 102, 241, 0.2), rgba(139, 92, 246, 0.2));
    border: 1px solid rgba(99, 102, 241, 0.35);
    padding: 0.4rem 0.85rem;
    border-radius: 9999px;
    margin-bottom: 1.25rem;
  }
  .hero-mobile__title {
    font-size: clamp(1.5rem, 5.5vw, 2rem);
    font-weight: 800;
    line-height: 1.2;
    color: #fff;
    margin: 0 0 0.75rem;
    letter-spacing: -0.02em;
  }
  .hero-mobile__title-accent {
    background: linear-gradient(135deg, #a5b4fc, #c4b5fd);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
  }
  .hero-mobile__desc {
    font-size: 0.9375rem;
    line-height: 1.5;
    color: rgba(255, 255, 255, 0.75);
    margin: 0 0 1.5rem;
    max-width: 36ch;
  }
  .hero-mobile__cta {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    width: 100%;
    max-width: 320px;
    padding: 1rem 1.5rem;
    font-size: 1rem;
    font-weight: 700;
    color: #fff;
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    border-radius: 16px;
    text-decoration: none;
    box-shadow: 0 10px 40px rgba(99, 102, 241, 0.35);
    transition: transform 0.2s, box-shadow 0.2s;
  }
  .hero-mobile__cta:hover {
    transform: translateY(-2px);
    box-shadow: 0 14px 48px rgba(99, 102, 241, 0.45);
  }
  .hero-mobile__cta:active {
  transform: translateY(0);
  }
  .hero-mobile__cta-arrow {
    width: 1.25rem;
    height: 1.25rem;
  }
}
@media screen and (max-width: 479px) {
  .hero-mobile {
    padding: 1.25rem 1rem 2rem;
  }
  .hero-mobile__logo-wrap {
    width: 72px;
    height: 72px;
    margin-bottom: 0.875rem;
  }
  .hero-mobile__title {
    font-size: clamp(1.375rem, 5vw, 1.75rem);
  }
  .hero-mobile__desc {
    font-size: 0.875rem;
  }
  .hero-mobile__cta {
    padding: 0.9375rem 1.25rem;
    font-size: 0.9375rem;
  }
}
@keyframes hero-mobile-logo-float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-6px); }
}

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

/* Mobile nav: align with home (orvimo .nav-menu + .w--open overlay) */
@media screen and (max-width: 991px) {
  .page-wrapper .nav-menu.w--open {
    display: flex !important;
    flex-direction: column;
    padding-top: 5rem;
    padding-left: var(--_size---paddingsize--tiny, 1.5rem);
    padding-right: var(--_size---paddingsize--tiny, 1.5rem);
    padding-bottom: var(--_size---paddingsize--extrasmall, 1.5rem);
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    height: 110vh;
    position: fixed;
    z-index: 500;
    overflow: auto;
    background-color: var(--_theme---background--primarybackground);
  }
  .page-wrapper .nav-container {
    display: grid;
    grid-template-columns: 1fr 1fr;
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

/* Responsive: containers (use design variables like home) */
.page-wrapper :deep(.w-container),
.page-wrapper :deep(.container) {
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
}

/* 767px: hero + sections like home */
@media screen and (max-width: 767px) {
  .page-wrapper :deep(.hero-content) {
    height: auto;
    min-height: 60vh;
    padding-top: var(--_size---paddingsize--large, 3rem);
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

/* 479px: like home (smaller fonts, tighter spacing) */
@media screen and (max-width: 479px) {
  .page-wrapper {
    overflow: hidden;
  }
  .page-wrapper :deep(.hero-content) {
    padding-top: var(--_size---paddingsize--large, 2rem);
    min-height: 50vh;
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

/* Section "Recherche d'emploi intelligente" – responsive comme maquette mobile */
.page-wrapper :deep(.home1-3col ._3cols-heading) {
  text-align: center;
}
.page-wrapper :deep(.home1-3col ._3cols-heading .center-align) {
  text-align: center;
}
@media screen and (max-width: 767px) {
  .page-wrapper :deep(.home1-3col ._3cols-heading) {
    padding-bottom: var(--_size---paddingsize--small, 1.5rem);
    margin-left: auto;
    margin-right: auto;
    max-width: 100%;
  }
  .page-wrapper :deep(.home1-3col .home1-3cols) {
    grid-template-columns: 1fr;
    grid-row-gap: var(--_size---paddingsize--medium, 2rem);
  }
  .page-wrapper :deep(.home1-3col .card-item-home1) {
    display: grid;
    grid-template-columns: 1fr;
    grid-template-rows: auto auto;
    grid-row-gap: var(--_size---paddingsize--small, 1rem);
    text-align: left;
  }
  .page-wrapper :deep(.home1-3col .card-item-img-wrap) {
    width: 100%;
    order: 1;
    border-radius: var(--radius--xs, 0.5rem);
    overflow: hidden;
    background-color: var(--_theme---background--secondarybackground, #f5f5f5);
  }
  .page-wrapper :deep(.home1-3col .card-text-content-home1) {
    order: 2;
    text-align: left;
    padding-top: var(--_size---paddingsize--tiny, 0.75rem);
  }
  .page-wrapper :deep(.home1-3col .card-text-content-home1 > div:first-child) {
    font-size: var(--_size---fonts--xxs, 0.75rem);
    text-transform: uppercase;
    letter-spacing: 0.02em;
    color: var(--_theme---textcolor--tertiarytext, #6b6b7b);
    margin-bottom: 0.25rem;
  }
  .page-wrapper :deep(.home1-3col .card-text-content-home1 h4) {
    text-align: left;
    margin-top: 0;
    margin-bottom: 0.5rem;
  }
  .page-wrapper :deep(.home1-3col .card-text-content-home1 p) {
    text-align: left;
    color: var(--_theme---textcolor--secondarytext, #666);
    margin-bottom: 0;
    line-height: 1.5;
  }
}
@media screen and (max-width: 479px) {
  .page-wrapper :deep(.home1-3col ._3cols-heading) {
    padding-bottom: var(--_size---paddingsize--tiny, 1rem);
  }
  .page-wrapper :deep(.home1-3col .home1-3cols) {
    grid-row-gap: var(--_size---paddingsize--small, 1.25rem);
  }
  .page-wrapper :deep(.home1-3col .card-text-content-home1) {
    padding-top: var(--_size---paddingsize--tiny, 0.5rem);
  }
}

/* Ensure all 3 cards in home1-sticky are visible (no collapse, scrollable on mobile) */
.page-wrapper :deep(.home1-cards-scroll) {
  display: flex;
}
.page-wrapper :deep(.home1-cards-scroll .big-card-home1) {
  flex: 0 0 auto;
  min-width: 0;
}
@media screen and (max-width: 991px) {
  .page-wrapper :deep(.home1-cards-scroll .big-card-home1) {
    min-width: min(320px, 85vw);
  }
}
</style>
