<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useHead } from '@unhead/vue'
import { useI18n } from 'vue-i18n'
import Footer from '../components/Footer.vue'
import LandingNav from '../components/LandingNav.vue'
import {
  DocumentTextIcon,
  ArrowUpTrayIcon,
  ArrowRightIcon,
  ShieldCheckIcon,
  LockClosedIcon,
  CheckCircleIcon,
  CpuChipIcon,
  ChartBarIcon,
  PencilSquareIcon,
  QuestionMarkCircleIcon
} from '@heroicons/vue/24/outline'

const { t, locale } = useI18n()
const router = useRouter()

const arrowPath = 'M6.64774 0.127319C6.8175 -0.0424396 7.09266 -0.0424396 7.26242 0.127319L12.9678 5.83267C12.9972 5.8621 13.0199 5.89563 13.0391 5.9303C13.0604 5.96873 13.0777 6.00981 13.0866 6.05426C13.0979 6.11054 13.0978 6.16861 13.0866 6.22491C13.0778 6.26941 13.0604 6.31038 13.0391 6.34886C13.0198 6.38377 12.9974 6.41774 12.9678 6.44735L7.26242 12.1527C7.09267 12.3224 6.81749 12.3224 6.64774 12.1527C6.47799 11.9829 6.478 11.7078 6.64774 11.538L11.611 6.5747H0.434693C0.194629 6.5747 1.76984e-05 6.38007 0 6.14001C0 5.89993 0.194618 5.70531 0.434693 5.70531H11.611L6.64774 0.742002C6.47799 0.572249 6.478 0.297078 6.64774 0.127319Z'

onMounted(() => {
  const link = document.createElement('link')
  link.rel = 'stylesheet'
  link.href = '/orvimo-landing.css'
  link.id = 'orvimo-landing-css'
  document.head.appendChild(link)
  document.documentElement.classList.add('w-mod-ix3')
})
onUnmounted(() => {
  const link = document.getElementById('orvimo-landing-css')
  if (link) link.remove()
  document.documentElement.classList.remove('w-mod-ix3')
})

useHead({
  title: computed(() => t('seo.free_cv.title')),
  meta: [
    { name: 'description', content: computed(() => t('seo.free_cv.description')) },
    { property: 'og:title', content: computed(() => t('seo.free_cv.og_title')) },
    { property: 'og:description', content: computed(() => t('seo.free_cv.og_description')) },
  ],
  script: [
    {
      type: 'application/ld+json',
      innerHTML: JSON.stringify({
        "@context": "https://schema.org",
        "@type": "WebApplication",
        "name": "Audit CV IA GoldArmy",
        "applicationCategory": "BusinessApplication",
        "operatingSystem": "All",
        "description": t('seo.free_cv.description'),
        "offers": { "@type": "Offer", "price": "0", "priceCurrency": "EUR" }
      })
    }
  ]
})

const file = ref(null)
const isDragging = ref(false)
const isAnalyzing = ref(false)
const result = ref(null)
const expandedIdx = ref(null)
const openFaqIndex = ref(null)

const faqItems = computed(() => [
  { q: t('free_cv.faq_q1'), a: t('free_cv.faq_a1') },
  { q: t('free_cv.faq_q2'), a: t('free_cv.faq_a2') },
  { q: t('free_cv.faq_q3'), a: t('free_cv.faq_a3') }
])

const atsReasons = computed(() => {
  const li1 = t('free_cv.seo_article_li1')
  const li2 = t('free_cv.seo_article_li2')
  const li3 = t('free_cv.seo_article_li3')
  const split = (s) => {
    const i = s.indexOf(': ')
    return i >= 0 ? { title: s.slice(0, i).trim(), desc: s.slice(i + 2).trim() } : { title: s, desc: '' }
  }
  return [split(li1), split(li2), split(li3)]
})

const handleFileDrop = (e) => {
  e.preventDefault()
  isDragging.value = false
  const droppedFile = e.dataTransfer.files[0]
  if (droppedFile && droppedFile.type === 'application/pdf') {
    file.value = droppedFile
    analyzeFile()
  } else {
    alert("Veuillez uploader un fichier PDF.")
  }
}

const handleFileSelect = (e) => {
  const selectedFile = e.target.files[0]
  if (selectedFile && selectedFile.type === 'application/pdf') {
    file.value = selectedFile
    analyzeFile()
  }
}

const analyzeFile = async () => {
    isAnalyzing.value = true
    result.value = null
    const formData = new FormData()
    formData.append('file', file.value)
    try {
        const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'
    const response = await fetch(`${apiUrl}/api/public/mini-audit`, { method: 'POST', body: formData })
        const data = await response.json()
        if (data.status === 'success') {
      result.value = { score: data.score, flaws: data.flaws || [] }
        } else {
            throw new Error("Erreur de l'API")
        }
    } catch (e) {
        console.error("Erreur d'analyse:", e)
        result.value = {
            score: 0,
      flaws: [
        "Impossible d'analyser le fichier.",
        "Le fichier est peut-être corrompu ou illisible.",
        "Veuillez vérifier votre connexion et réessayer."
      ]
        }
    } finally {
        isAnalyzing.value = false
    }
}

const goToRegister = () => router.push('/register')
const resetScan = () => { result.value = null; file.value = null; expandedIdx.value = null }
</script>

<template>
  <div class="page-wrapper page-wrapper--cv-roast">
    <LandingNav />
    <main class="main dark-secondary">

      <!-- HERO + UPLOAD (structure identique landing hero-1) -->
      <section class="section hero-1">
        <div class="hero-content">
          <div class="w-layout-grid hero1-grid cv-roast-hero-grid">
            <div class="hero-left-col">
              <div class="hero-text-wrap">
                <h1 class="hero-heading">
                    {{ t('free_cv.hero_title') }}
                  <span class="tertiary-color-emphasis">{{ t('free_cv.hero_highlight') }}</span>
                </h1>
                <p class="hero-paragraph">
                  {{ t('free_cv.hero_subtitle1') }}
                  <strong class="primary-color-emphasis">{{ t('free_cv.hero_error_bold') }}</strong>
                  {{ t('free_cv.hero_subtitle2') }}
                </p>
                <div class="cv-roast-trust">
                  <span class="trust-item">
                    <ShieldCheckIcon class="trust-icon" />
                    {{ t('free_cv.confidential') }}
                  </span>
                  <span class="trust-item">
                    <DocumentTextIcon class="trust-icon" />
                    {{ t('free_cv.pdf_format') }}
                  </span>
                </div>
                </div>
            </div>
            <div class="cv-roast-upload-col">
              <!-- Upload zone (visible when no result and not analyzing) -->
              <div v-if="!result && !isAnalyzing" class="cv-roast-upload-card"
                            @dragover.prevent="isDragging = true"
                            @dragleave.prevent="isDragging = false"
                            @drop="handleFileDrop"
                @click="$refs.fileInput?.click()"
                :class="{ 'is-dragging': isDragging }">
                <div class="upload-card-inner">
                  <div class="upload-icon-wrap">
                    <DocumentTextIcon class="upload-icon" />
                        </div>
                  <p class="upload-title">{{ t('free_cv.upload_title') }}</p>
                  <p class="upload-subtitle">{{ t('free_cv.upload_subtitle') }}</p>
                  <input type="file" ref="fileInput" @change="handleFileSelect" accept="application/pdf" class="hidden-input" />
                  <span class="upload-btn">
                    <ArrowUpTrayIcon class="btn-icon-inline" /> {{ t('free_cv.upload_button') }}
                  </span>
                        </div>
                    </div>
              <!-- Analyzing state -->
              <div v-if="isAnalyzing" class="cv-roast-analyzing">
                <div class="analyzing-doc">
                  <DocumentTextIcon class="analyzing-icon" />
                </div>
                <h3 class="fsize-s">{{ t('free_cv.analyzing_title') }}</h3>
                <ul class="analyzing-steps">
                  <li><span class="step-dot"></span> {{ t('free_cv.analyzing_step1') }}</li>
                  <li><span class="step-dot"></span> {{ t('free_cv.analyzing_step2') }}</li>
                  <li><span class="step-dot step-pending"></span> {{ t('free_cv.analyzing_step3') }}</li>
                </ul>
                </div>
            </div>
          </div>
        </div>
      </section>

      <!-- RÉSULTATS (après analyse) -->
        <template v-if="result && !isAnalyzing">
        <section class="section cv-roast-results">
          <div class="w-layout-blockcontainer container w-container">
            <div class="results-score-block">
              <div class="score-circle-wrap">
                <svg class="score-svg" viewBox="0 0 120 120">
                  <circle class="score-bg" cx="60" cy="60" r="52" />
                  <circle class="score-fill" cx="60" cy="60" r="52"
                    :class="result.score > 70 ? 'score-good' : result.score > 40 ? 'score-mid' : 'score-low'"
                    :stroke-dasharray="327"
                    :stroke-dashoffset="327 - (327 * result.score) / 100" />
                            </svg>
                <div class="score-value">{{ result.score }}</div>
                <span class="score-label">{{ t('free_cv.score_label') }}</span>
                            </div>
              <h2 class="fsize-m">{{ result.score > 70 ? t('free_cv.score_good') : t('free_cv.score_bad') }}</h2>
              <p class="fsize-body-large">{{ t('free_cv.flaws_found', { count: result.flaws.length }) }}</p>
                        </div>
                        
            <div class="faq-list flaws-list">
              <div v-for="(item, idx) in result.flaws.slice(0, 8)" :key="'f-'+idx"
                class="accordion-item"
                :class="{ 'w--open': expandedIdx === idx }">
                <div class="accordion-title-toggle" @click="expandedIdx = expandedIdx === idx ? null : idx">
                  <div class="flaw-title">
                    <span class="flaw-num">0{{ idx + 1 }}</span>
                    <span class="flaw-text">{{ item.flaw || item }}</span>
                    </div>
                  <div class="accordion-toggle">
                    <div class="cross-h"></div>
                    <div class="cross-v"></div>
                                    </div>
                                </div>
                <div class="accordion-content">
                  <div v-if="item.correction" class="correction-block">
                    <CheckCircleIcon class="correction-icon" />
                                        <div>
                      <span class="correction-label">{{ t('free_cv.correction_title') }}</span>
                      <p class="accordion-content-text">{{ item.correction }}</p>
                                        </div>
                                    </div>
                                </div>
                        </div>
                    </div>

            <!-- Flaws locked (fomo) -->
            <div v-if="result.flaws.length > 8" class="locked-flaws">
              <div class="locked-overlay">
                <LockClosedIcon class="locked-icon" />
                <span class="locked-text">{{ t('free_cv.locked_count_cta', { count: result.flaws.length - 8 }) }}</span>
                                </div>
              <div class="locked-list">
                <div v-for="(flaw, idx) in result.flaws.slice(8)" :key="'locked-'+idx" class="locked-item">
                  <LockClosedIcon class="locked-item-icon" />
                  <span>{{ t('free_cv.locked_fails') }}</span>
                                </div>
                            </div>
                        </div>
                        
            <div class="reveal-content-wrap cta-results-wrap">
              <button type="button" @click="goToRegister" class="button-default w-button button-default--accent">
                {{ t('free_cv.cta_unlock_button') }} <ArrowRightIcon class="btn-icon-inline" />
                        </button>
                    </div>
            <button type="button" @click="resetScan" class="cv-roast-rescan">{{ t('free_cv.scan_another') }}</button>
          </div>
        </section>
      </template>

      <!-- SECTION BENTO / 3 PILLIERS -->
      <section class="section home1-3col">
        <div class="w-layout-blockcontainer container w-container">
          <div class="_3cols-heading">
            <h3 class="center-align">{{ t('free_cv.bento_title1') }} <span class="tertiary-color-emphasis">{{ t('free_cv.bento_title2') }}</span></h3>
            <p class="fsize-body-large center-align">{{ t('free_cv.bento_tagline') }}</p>
          </div>
          <div class="w-layout-grid home1-3cols">
            <div class="card-item-home1">
              <div class="card-item-img-wrap card-item-img-wrap--num">1</div>
              <div class="card-text-content-home1">
                <h4 class="fsize-xxs">{{ t('free_cv.bento_feature1_title') }}</h4>
                <p>{{ t('free_cv.bento_feature1_desc') }}</p>
                </div>
            </div>
            <div class="card-item-home1">
              <div class="card-item-img-wrap card-item-img-wrap--num">2</div>
              <div class="card-text-content-home1">
                <h4 class="fsize-xxs">{{ t('free_cv.bento_feature2_title') }}</h4>
                <p>{{ t('free_cv.bento_feature2_desc') }}</p>
              </div>
            </div>
            <div class="card-item-home1">
              <div class="card-item-img-wrap card-item-img-wrap--num">3</div>
              <div class="card-text-content-home1">
                <h4 class="fsize-xxs">{{ t('free_cv.bento_feature3_title') }}</h4>
                <p>{{ t('free_cv.bento_feature3_desc') }}</p>
              </div>
                        </div>
                    </div>
        </div>
      </section>

      <!-- Bloc ATS + FAQ (design unique) -->
      <section class="cv-roast-ats-block">
        <div class="ats-block-inner">
          <div class="ats-badge">ATS & IA</div>
          <h2 class="ats-main-title">{{ t('free_cv.seo_article_title') }}</h2>
          <div class="ats-intro">
            <p class="ats-intro-p">{{ t('free_cv.seo_article_p1') }}</p>
            <p class="ats-intro-p">{{ t('free_cv.seo_article_p2') }}</p>
                </div>

          <h3 class="ats-subtitle">{{ t('free_cv.seo_article_h3') }}</h3>
          <div class="ats-reasons-grid">
            <article v-for="(reason, idx) in atsReasons" :key="idx" class="ats-reason-card">
              <div class="ats-reason-icon" :class="'ats-reason-icon--' + (idx + 1)">
                <CpuChipIcon v-if="idx === 0" class="ats-reason-svg" />
                <ChartBarIcon v-else-if="idx === 1" class="ats-reason-svg" />
                <PencilSquareIcon v-else class="ats-reason-svg" />
              </div>
              <span class="ats-reason-num">0{{ idx + 1 }}</span>
              <h4 class="ats-reason-title">{{ reason.title }}</h4>
              <p class="ats-reason-desc">{{ reason.desc }}</p>
            </article>
                </div>

          <div class="ats-faq-wrap">
            <h3 class="ats-faq-heading">
              <QuestionMarkCircleIcon class="ats-faq-heading-icon" />
              {{ t('free_cv.faq_title') }}
            </h3>
            <div class="ats-faq-list">
              <div v-for="(faq, i) in faqItems" :key="i" class="ats-faq-item" :class="{ 'ats-faq-item--open': openFaqIndex === i }">
                <button type="button" class="ats-faq-q" @click="openFaqIndex = openFaqIndex === i ? null : i">
                  <span>{{ faq.q }}</span>
                  <span class="ats-faq-chevron" aria-hidden="true"></span>
                </button>
                <div class="ats-faq-a">
                  <p>{{ faq.a }}</p>
                </div>
              </div>
            </div>
          </div>
                    </div>
            </section>

      <!-- CTA FINAL (identique landing cta-v1) -->
      <section class="section cta-v1">
        <div class="cta1-wrapper">
          <div class="w-layout-grid cta1-content">
            <div class="cta-text-wrapper-left">
              <h2 class="heading-cta">{{ t('free_cv.final_cta_title') }}</h2>
            </div>
            <div class="cta-text-wrapper-right">
              <div class="cta-text-right">{{ t('free_cv.final_cta_desc') }}</div>
              <div class="reveal-content-wrap">
                <router-link to="/register" class="button-default w-button">{{ t('free_cv.final_cta_button') }}</router-link>
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
/* Theme sombre - texte clair sur fond sombre */
.page-wrapper--cv-roast {
  min-height: 100vh;
  overflow-x: clip;
  --_theme---bodybackground: #2e2e2e;
  --_theme---textcolor--primarytext: #ffffff;
  --_theme---textcolor--secondarytext: #e8e8e8;
  --_theme---textcolor--tertiarytext: #b8b8b8;
  --_theme---background--primarybackground: #2e2e2e;
  --_theme---background--secondarybackground: #1f1f1f;
  background-color: var(--_theme---bodybackground);
  color: var(--_theme---textcolor--primarytext);
}
.page-wrapper--cv-roast :deep(.main) {
  padding-top: 0;
}
/* Titres et textes lisibles */
.page-wrapper--cv-roast :deep(.hero-heading),
.page-wrapper--cv-roast :deep(.hero-paragraph),
.page-wrapper--cv-roast :deep(.heading-cta),
.page-wrapper--cv-roast :deep(.cta-text-right),
.page-wrapper--cv-roast :deep(h1), .page-wrapper--cv-roast :deep(h2),
.page-wrapper--cv-roast :deep(h3), .page-wrapper--cv-roast :deep(h4),
.page-wrapper--cv-roast :deep(.fsize-m), .page-wrapper--cv-roast :deep(.fsize-s),
.page-wrapper--cv-roast :deep(.accordion-title-toggle div),
.page-wrapper--cv-roast :deep(.flaw-text), .page-wrapper--cv-roast :deep(.accordion-content-text),
.page-wrapper--cv-roast :deep(.card-text-content-home1 h4),
.page-wrapper--cv-roast :deep(.card-text-content-home1 p),
.page-wrapper--cv-roast :deep(._3cols-heading h3), .page-wrapper--cv-roast :deep(._3cols-heading p),
.page-wrapper--cv-roast :deep(.score-value), .page-wrapper--cv-roast :deep(.score-label),
.page-wrapper--cv-roast :deep(.locked-text), .page-wrapper--cv-roast :deep(.cv-roast-seo-p),
.page-wrapper--cv-roast :deep(.cv-roast-ul) {
  color: var(--_theme---textcolor--primarytext);
}
.page-wrapper--cv-roast :deep(.tertiary-color-emphasis) {
  color: var(--_theme---textcolor--tertiarytext);
}
.page-wrapper--cv-roast :deep(.accordion-content-text) {
  color: var(--_theme---textcolor--secondarytext);
}
.page-wrapper--cv-roast :deep(.flaw-num) {
  color: var(--_theme---textcolor--tertiarytext);
}

/* Hero grid: 2 cols desktop, 1 col mobile (like landing) */
.cv-roast-hero-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  align-items: center;
  gap: var(--_size---paddingsize--large, 2rem);
}
@media (max-width: 991px) {
  .cv-roast-hero-grid {
    grid-template-columns: 1fr;
    grid-template-rows: auto auto;
  }
}
.cv-roast-trust {
  display: flex;
  flex-wrap: wrap;
  gap: var(--_size---paddingsize--medium, 1.5rem);
  margin-top: var(--_size---paddingsize--medium, 1rem);
}
.trust-item {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  font-size: var(--_size---fonts--xs, 0.875rem);
  color: var(--_theme---textcolor--secondarytext);
}
.trust-icon {
  width: 1.25rem;
  height: 1.25rem;
  color: var(--_theme---textcolor--accenttext1);
}

.cv-roast-upload-col {
  min-height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--_size---paddingsize--small, 1rem);
}
.cv-roast-upload-card {
  width: 100%;
  max-width: 400px;
  padding: 0;
  border: 2px dashed var(--_theme---border--mediumalpha);
  border-radius: var(--radius--m, 1rem);
  background-color: var(--_theme---background--secondarybackground);
  text-align: center;
  cursor: pointer;
  transition: border-color 0.25s ease, background-color 0.25s ease, box-shadow 0.25s ease;
}
.cv-roast-upload-card:hover,
.cv-roast-upload-card.is-dragging {
  border-color: var(--_theme---textcolor--accenttext1);
  background-color: rgba(255, 111, 0, 0.08);
  box-shadow: 0 0 0 1px rgba(255, 111, 0, 0.25);
}
.upload-card-inner {
  padding: 2.25rem 1.75rem;
  min-height: 240px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0;
}
@media (max-width: 479px) {
  .upload-card-inner {
    padding: 1.75rem 1.25rem;
    min-height: 220px;
  }
  .upload-title { font-size: 1.125rem; }
  .upload-subtitle { font-size: 0.75rem; }
}
.upload-icon-wrap {
  position: relative;
  width: 5rem;
  height: 5rem;
  margin-bottom: 1.25rem;
  border-radius: var(--radius--s, 0.75rem);
  background: linear-gradient(145deg, var(--_theme---background--tertiarybackground), var(--_theme---background--secondarybackground));
  border: 1px solid var(--_theme---border--lightalpha);
  display: flex;
  align-items: center;
  justify-content: center;
}
.upload-icon {
  width: 2.5rem;
  height: 2.5rem;
  color: var(--_theme---textcolor--accenttext1);
}
.upload-title {
  font-size: 1.25rem;
  font-weight: 700;
  line-height: 1.3;
  color: var(--_theme---textcolor--primarytext);
  margin: 0 0 0.5rem;
  letter-spacing: -0.02em;
}
.upload-subtitle {
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--_theme---textcolor--tertiarytext);
  margin: 0 0 1.5rem;
  letter-spacing: 0.03em;
  opacity: 0.95;
}
.hidden-input {
  position: absolute;
  width: 0;
  height: 0;
  opacity: 0;
  pointer-events: none;
}
.upload-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  font-size: 0.875rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--_theme---textcolor--primarytext);
  background-color: var(--_theme---textcolor--accenttext1);
  border: 1px solid var(--_theme---textcolor--accenttext1);
  border-radius: var(--radius--xs, 0.5rem);
  cursor: pointer;
  transition: opacity 0.2s, transform 0.15s;
}
.upload-btn:hover {
  opacity: 0.95;
  transform: translateY(-1px);
}
.upload-btn:active {
  transform: translateY(0);
}
.btn-icon-inline {
  width: 1.125rem;
  height: 1.125rem;
}

.cv-roast-analyzing {
  width: 100%;
  max-width: 380px;
  padding: var(--_size---paddingsize--large, 2rem);
  border-radius: var(--radius--s, 0.75rem);
  background-color: var(--_theme---background--secondarybackground);
  text-align: center;
}
.analyzing-doc {
  margin-bottom: 1rem;
}
.analyzing-icon {
  width: 4rem;
  height: 4rem;
  color: var(--_theme---textcolor--accenttext1);
  animation: pulse 1.5s ease-in-out infinite;
}
@keyframes pulse {
  50% { opacity: 0.6; }
}
.analyzing-steps {
  list-style: none;
  padding: 0;
  margin: 0;
  text-align: left;
  color: var(--_theme---textcolor--secondarytext);
  font-size: var(--_size---fonts--xs, 0.875rem);
}
.analyzing-steps li {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.35rem 0;
}
.step-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--_theme---textcolor--accenttext1);
  flex-shrink: 0;
}
.step-pending {
  opacity: 0.5;
}

/* Results section */
.cv-roast-results {
  padding-top: var(--_size---paddingsize--large, 3rem);
  padding-bottom: var(--_size---paddingsize--large, 3rem);
}
.results-score-block {
  text-align: center;
  margin-bottom: var(--_size---paddingsize--large, 2rem);
}
.score-circle-wrap {
  position: relative;
  width: 140px;
  height: 140px;
  margin: 0 auto 1rem;
}
.score-svg {
  width: 100%;
  height: 100%;
  transform: rotate(-90deg);
}
.score-bg {
  fill: none;
  stroke: var(--_theme---background--tertiarybackground);
  stroke-width: 8;
}
.score-fill {
  fill: none;
  stroke-width: 8;
  stroke-linecap: round;
  transition: stroke-dashoffset 0.8s ease-out;
}
.score-good { stroke: #22c55e; }
.score-mid { stroke: #eab308; }
.score-low { stroke: #ef4444; }
.score-value {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--_theme---textcolor--primarytext);
}
.score-label {
  font-size: var(--_size---fonts--xxs, 0.75rem);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--_theme---textcolor--tertiarytext);
}

.flaws-list {
  margin-bottom: var(--_size---paddingsize--medium, 1.5rem);
}
.flaw-title {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
}
.flaw-num {
  font-size: var(--_size---fonts--xxs, 0.75rem);
  font-weight: 700;
  color: var(--_theme---textcolor--tertiarytext);
  flex-shrink: 0;
}
.flaw-text {
  flex: 1;
}
.correction-block {
  display: flex;
  gap: 0.75rem;
  padding-top: 0.75rem;
  margin-top: 0.75rem;
  border-top: 1px solid var(--_theme---border--lightalpha);
}
.correction-icon {
  width: 1.25rem;
  height: 1.25rem;
  color: #22c55e;
  flex-shrink: 0;
}
.correction-label {
  font-size: var(--_size---fonts--xxs, 0.75rem);
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #22c55e;
  display: block;
  margin-bottom: 0.25rem;
}

.locked-flaws {
  position: relative;
  margin-bottom: var(--_size---paddingsize--large, 2rem);
  min-height: 120px;
}
.locked-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 0.5rem;
  opacity: 0.4;
  filter: blur(2px);
  pointer-events: none;
}
.locked-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem;
  border-radius: var(--radius--xs, 0.5rem);
  background-color: var(--_theme---background--secondarybackground);
  font-size: var(--_size---fonts--xs, 0.875rem);
  color: var(--_theme---textcolor--tertiarytext);
}
.locked-item-icon {
  width: 1rem;
  height: 1rem;
}
.locked-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  z-index: 2;
}
.locked-icon {
  width: 2.5rem;
  height: 2.5rem;
  color: var(--_theme---textcolor--accenttext1);
}
.locked-text {
  font-weight: 700;
  font-size: var(--_size---fonts--m, 1.125rem);
  color: var(--_theme---textcolor--primarytext);
}
.cta-results-wrap {
  text-align: center;
  margin-bottom: 1rem;
}
.button-default--accent {
  background-color: var(--_theme---textcolor--accenttext1);
  color: #fff;
  border-color: var(--_theme---textcolor--accenttext1);
}
.cv-roast-rescan {
  display: block;
  width: 100%;
  padding: 0.75rem;
  background: none;
  border: none;
  font-size: var(--_size---fonts--xs, 0.875rem);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--_theme---textcolor--tertiarytext);
  cursor: pointer;
  transition: color 0.2s;
}
.cv-roast-rescan:hover {
  color: var(--_theme---textcolor--primarytext);
}

/* Bento: num placeholders */
.card-item-img-wrap--num {
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  font-weight: 700;
  color: var(--_theme---textcolor--accenttext1);
  background-color: var(--_theme---background--tertiarybackground);
}

/* Bloc ATS + FAQ (design unique) */
.cv-roast-ats-block {
  background: linear-gradient(180deg, #252530 0%, #1c1c24 100%);
  border-top: 1px solid rgba(255, 255, 255, 0.06);
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  padding: 3.5rem 1.5rem 4rem;
}
.ats-block-inner {
  max-width: 900px;
  margin: 0 auto;
}
.ats-badge {
  display: inline-block;
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: var(--_theme---textcolor--accenttext1, #ff6f00);
  margin-bottom: 0.75rem;
}
.ats-main-title {
  font-size: clamp(1.5rem, 4vw, 2.25rem);
  font-weight: 700;
  line-height: 1.25;
  color: #ffffff;
  margin: 0 0 1.5rem;
  letter-spacing: -0.02em;
}
.ats-intro {
  margin-bottom: 2.5rem;
}
.ats-intro-p {
  font-size: 1rem;
  line-height: 1.7;
  color: #e0e0e0;
  margin: 0 0 1rem;
}
.ats-intro-p:last-child {
  margin-bottom: 0;
}
.ats-subtitle {
  font-size: 1.2rem;
  font-weight: 700;
  color: #ffffff;
  margin: 0 0 1.25rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid rgba(255, 111, 0, 0.4);
  display: inline-block;
}
.ats-reasons-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.25rem;
  margin-bottom: 3rem;
}
@media (min-width: 768px) {
  .ats-reasons-grid {
    grid-template-columns: repeat(3, 1fr);
    gap: 1.5rem;
  }
}
.ats-reason-card {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  padding: 1.5rem;
  position: relative;
  transition: border-color 0.2s, background 0.2s;
}
.ats-reason-card:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(255, 111, 0, 0.25);
}
.ats-reason-icon {
  width: 44px;
  height: 44px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 0.75rem;
}
.ats-reason-icon--1 { background: rgba(255, 111, 0, 0.15); color: #ff8c42; }
.ats-reason-icon--2 { background: rgba(0, 94, 255, 0.15); color: #4d9aff; }
.ats-reason-icon--3 { background: rgba(34, 197, 94, 0.15); color: #4ade80; }
.ats-reason-svg {
  width: 1.5rem;
  height: 1.5rem;
}
.ats-reason-num {
  position: absolute;
  top: 1rem;
  right: 1rem;
  font-size: 0.7rem;
  font-weight: 700;
  color: rgba(255, 255, 255, 0.35);
}
.ats-reason-title {
  font-size: 1rem;
  font-weight: 700;
  color: #ffffff;
  margin: 0 0 0.5rem;
  line-height: 1.3;
}
.ats-reason-desc {
  font-size: 0.875rem;
  line-height: 1.55;
  color: #b8b8b8;
  margin: 0;
}
.ats-faq-wrap {
  padding-top: 2rem;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
}
.ats-faq-heading {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1.25rem;
  font-weight: 700;
  color: #ffffff;
  margin: 0 0 1.25rem;
}
.ats-faq-heading-icon {
  width: 1.5rem;
  height: 1.5rem;
  color: var(--_theme---textcolor--accenttext1, #ff6f00);
}
.ats-faq-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.ats-faq-item {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 10px;
  overflow: hidden;
  transition: border-color 0.2s;
}
.ats-faq-item--open {
  border-color: rgba(255, 111, 0, 0.3);
}
.ats-faq-q {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 1rem 1.25rem;
  background: none;
  border: none;
  font-size: 0.9375rem;
  font-weight: 600;
  color: #ffffff;
  text-align: left;
  cursor: pointer;
  transition: background 0.2s;
}
.ats-faq-q:hover {
  background: rgba(255, 255, 255, 0.04);
}
.ats-faq-chevron {
  flex-shrink: 0;
  width: 20px;
  height: 20px;
  border-right: 2px solid currentColor;
  border-bottom: 2px solid currentColor;
  transform: rotate(45deg);
  margin-top: -4px;
  transition: transform 0.2s;
  opacity: 0.7;
}
.ats-faq-item--open .ats-faq-chevron {
  transform: rotate(-135deg);
  margin-top: 4px;
}
.ats-faq-a {
  max-height: 0;
  overflow: hidden;
  transition: max-height 0.25s ease-out;
}
.ats-faq-item--open .ats-faq-a {
  max-height: 500px;
}
.ats-faq-a p {
  margin: 0;
  padding: 0 1.25rem 1rem 1.25rem;
  font-size: 0.9375rem;
  line-height: 1.6;
  color: #c8c8c8;
}

/* Accordion (same as Landing) */
.page-wrapper--cv-roast :deep(.accordion-item.w--open .accordion-content) {
  height: auto;
  overflow: visible;
  padding-bottom: 1rem;
}
.page-wrapper--cv-roast :deep(.accordion-item.w--open .cross-v) {
  transform: rotate(90deg);
}
</style>
