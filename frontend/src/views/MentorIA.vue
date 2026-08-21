<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useHead } from '@unhead/vue'
import LandingNav from '@/components/LandingNav.vue'
import Footer from '@/components/Footer.vue'

const { t } = useI18n()
const BASE = 'https://www.goldarmyai.com'

useHead({
  title: computed(() => t('seo.mentor_ia.title')),
  meta: [
    { name: 'description', content: computed(() => t('seo.mentor_ia.description')) },
    { name: 'robots', content: 'index, follow' },
    { property: 'og:type', content: 'website' },
    { property: 'og:title', content: computed(() => t('seo.mentor_ia.title')) },
    { property: 'og:description', content: computed(() => t('seo.mentor_ia.description')) },
    { property: 'og:url', content: `${BASE}/mentor-ia` },
    { property: 'og:image', content: `${BASE}/og-banner.png` },
    { property: 'og:site_name', content: 'GoldArmy AI' },
    { property: 'og:locale', content: 'fr_FR' },
    { name: 'twitter:card', content: 'summary_large_image' },
    { name: 'twitter:title', content: computed(() => t('seo.mentor_ia.title')) },
    { name: 'twitter:description', content: computed(() => t('seo.mentor_ia.description')) },
    { name: 'twitter:image', content: `${BASE}/og-banner.png` }
  ],
  link: [
    { rel: 'canonical', href: `${BASE}/mentor-ia` }
  ],
  script: [
    {
      type: 'application/ld+json',
      innerHTML: JSON.stringify({
        '@context': 'https://schema.org',
        '@type': 'SoftwareApplication',
        'name': 'Mentor IA Carrière par GoldArmy AI',
        'url': `${BASE}/mentor-ia`,
        'applicationCategory': 'EducationalApplication',
        'operatingSystem': 'Web',
        'description': 'Coach de carrière IA personnel qui audite votre CV, adapte vos candidatures aux exigences des recruteurs et génère des lettres de motivation sur mesure.',
        'offers': { '@type': 'Offer', 'price': '0', 'priceCurrency': 'EUR' }
      })
    }
  ]
})

const svg = (inner) => `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">${inner}</svg>`

const stats = [
  { n: 'ATS', l: 'optimisation sémantique du CV' },
  { n: '24/7', l: 'un coach carrière toujours disponible' },
  { n: '1 clic', l: 'pour générer une lettre ciblée' },
  { n: 'STAR', l: 'réécriture orientée résultats' }
]

const steps = [
  { num: '01', title: 'Audit CV instantané', desc: "L'IA passe au crible la structure de votre PDF, identifie les failles de lisibilité et vérifie la densité de vos mots-clés par rapport aux standards de l'industrie.", icon: svg('<path d="M14 3v4a1 1 0 0 0 1 1h4"/><path d="M17 21H7a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h7l5 5v11a2 2 0 0 1-2 2z"/><path d="M9 14l2 2 4-4"/>') },
  { num: '02', title: 'Réécriture orientée impact', desc: "Notre modèle transforme de simples descriptions de tâches en réalisations quantifiables orientées résultats (méthode de type Harvard/STAR).", icon: svg('<path d="M12 3l1.9 4.6L18.5 9.5 13.9 11.4 12 16l-1.9-4.6L5.5 9.5l4.6-1.9z"/>') },
  { num: '03', title: 'Génération contextuelle', desc: "En un clic, le Mentor analyse la description d'une offre ciblée et produit une lettre d'accompagnement percutante qui met en avant vos atouts les plus pertinents.", icon: svg('<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 7l9 6 9-6"/>') }
]
</script>

<template>
  <div class="sn-page">
    <LandingNav />
    <main>
      <!-- HERO (centré) -->
      <header class="sn-hero">
        <div class="sn-wrap sn-hero-grid sn-hero-grid--center">
          <div class="sn-hero-copy">
            <span class="sn-pill">Coaching autonome</span>
            <h1 class="sn-h1">Votre mentor carrière IA, disponible 24h/24</h1>
            <p class="sn-lead">
              Un CV générique ne passe plus les algorithmes de filtrage. Laissez notre IA analyser vos
              expériences, extraire votre potentiel caché et générer des candidatures taillées sur mesure
              pour chaque poste visé.
            </p>
            <div class="sn-hero-cta">
              <router-link to="/register" class="sn-btn">Essayer le Mentor IA</router-link>
              <a href="#fonctionnement" class="sn-btn-ghost">Comment ça marche</a>
            </div>
          </div>
        </div>
      </header>

      <!-- STATS -->
      <section class="sn-stats-band">
        <div class="sn-wrap sn-stats">
          <div v-for="s in stats" :key="s.l" class="sn-stat"><b>{{ s.n }}</b><span>{{ s.l }}</span></div>
        </div>
      </section>

      <!-- POURQUOI -->
      <section class="sn-section">
        <div class="sn-wrap sn-narrow">
          <span class="sn-eyebrow">Le principe</span>
          <h2 class="sn-h2">Pourquoi avez-vous besoin d'un Mentor IA ?</h2>
          <p class="sn-p">
            Rédiger un CV percutant et une lettre de motivation unique pour chaque candidature demande un
            temps considérable. Pourtant, face aux logiciels ATS (Applicant Tracking Systems) utilisés par
            plus de 90 % des grandes entreprises, la personnalisation sémantique est devenue une nécessité
            absolue. Le <strong>Mentor IA</strong> de GoldArmy résout cette équation en automatisant
            l'optimisation de votre profil.
          </p>
        </div>
      </section>

      <!-- FONCTIONNEMENT -->
      <section id="fonctionnement" class="sn-section sn-alt">
        <div class="sn-wrap">
          <div class="sn-head">
            <span class="sn-eyebrow">Le fonctionnement</span>
            <h2 class="sn-h2">Les fonctionnalités de votre coach carrière</h2>
            <p class="sn-sub">De l'audit de votre CV à la lettre sur mesure, chaque étape est automatisée.</p>
          </div>
          <div class="sn-steps">
            <article v-for="st in steps" :key="st.num" class="sn-step">
              <div class="sn-step__top">
                <span class="sn-step__ic" v-html="st.icon"></span>
                <span class="sn-step__num">{{ st.num }}</span>
              </div>
              <h3 class="sn-step__title">{{ st.title }}</h3>
              <p class="sn-step__desc">{{ st.desc }}</p>
            </article>
          </div>
        </div>
      </section>

      <!-- HIGHLIGHT ATS -->
      <section class="sn-section">
        <div class="sn-wrap sn-split">
          <div class="sn-split__figure">
            <div class="sn-big-stat"><b>90%</b><span>des CV sont filtrés par un logiciel avant d'atteindre un recruteur humain</span></div>
          </div>
          <div class="sn-split__copy">
            <span class="sn-eyebrow">L'accompagnement</span>
            <h2 class="sn-h2">Un accompagnement tout au long de votre carrière</h2>
            <p class="sn-p">
              Au-delà de la simple correction de documents, le Mentor IA vous aide à identifier les
              compétences manquantes pour atteindre les postes de niveau supérieur. Il vous suggère des
              formations clés et des projets stratégiques pour combler l'écart entre votre poste actuel et
              vos ambitions.
            </p>
            <ul class="sn-checks">
              <li>Audit de lisibilité et de mots-clés</li>
              <li>Réécriture orientée résultats</li>
              <li>Lettres de motivation sur mesure</li>
            </ul>
            <div class="sn-links">
              <router-link to="/free-cv-roast">Faire un audit CV gratuit →</router-link>
              <router-link to="/sniper-search">Découvrir le Sniper Search →</router-link>
            </div>
          </div>
        </div>
      </section>

      <!-- FAQ -->
      <section class="sn-section sn-alt">
        <div class="sn-wrap sn-narrow">
          <div class="sn-head">
            <span class="sn-eyebrow">FAQ</span>
            <h2 class="sn-h2">Questions fréquentes</h2>
          </div>
          <div class="sn-faq">
            <details class="sn-faq__item">
              <summary>Le Mentor IA remplace-t-il un vrai coach ?</summary>
              <p>Il automatise l'optimisation de vos documents et vous guide en continu ; il complète parfaitement un accompagnement humain, sans en avoir le coût ni les délais.</p>
            </details>
            <details class="sn-faq__item">
              <summary>Mes documents de candidature sont-ils en sécurité ?</summary>
              <p>Vos CV et lettres sont traités de façon confidentielle et ne sont jamais partagés avec des tiers.</p>
            </details>
          </div>
        </div>
      </section>

      <!-- CTA -->
      <section class="sn-cta">
        <div class="sn-wrap">
          <h2 class="sn-h2">Prêt à optimiser votre profil ?</h2>
          <p class="sn-sub">Découvrez instantanément les failles invisibles qui bloquent vos candidatures.</p>
          <router-link to="/free-cv-roast" class="sn-btn">Faire un audit CV gratuit</router-link>
        </div>
      </section>
    </main>
    <Footer />
  </div>
</template>

<style scoped>
/* Charte native : DM Sans (titres) + Inter (corps), texte #2e2e2e/#6b6b6b, accent neutre noir */
.sn-page { background: #fff; color: #2e2e2e; font-family: var(--fonts--secondaryfont, Inter, sans-serif); }
.sn-wrap { max-width: 1120px; margin: 0 auto; padding: 0 1.5rem; }
.sn-narrow { max-width: 760px; }
.sn-eyebrow { display: inline-block; font-size: .72rem; font-weight: 700; letter-spacing: .16em; text-transform: uppercase; color: #6b6b6b; background: #f1f1f2; padding: .35rem .8rem; border-radius: 999px; }
.sn-h1, .sn-h2, .sn-step__title { font-family: var(--fonts--primaryfont, "DM Sans", sans-serif); color: #161616; letter-spacing: -.02em; }
.sn-h2 { font-size: clamp(1.6rem, 3.2vw, 2.3rem); font-weight: 700; margin: 1rem 0 .8rem; line-height: 1.15; }
.sn-p { font-size: 1.05rem; line-height: 1.75; color: #6b6b6b; margin: 0 0 1.2rem; }
.sn-p strong { color: #2e2e2e; }

/* Boutons */
.sn-btn { display: inline-block; background: #161616; color: #fff; font-weight: 700; padding: .95rem 1.8rem; border-radius: .7rem; text-decoration: none; transition: transform .2s, background .2s; }
.sn-btn:hover { transform: translateY(-2px); background: #000; }
.sn-btn-ghost { display: inline-block; color: #161616; border: 1px solid #e2e2e5; background: #fff; padding: .95rem 1.5rem; border-radius: .7rem; text-decoration: none; font-weight: 700; transition: border-color .2s; }
.sn-btn-ghost:hover { border-color: #161616; }

/* HERO */
.sn-hero { background: linear-gradient(180deg, #fff, #fafafa); padding: 4.5rem 0 4rem; }
.sn-hero-grid { display: grid; grid-template-columns: 1fr; gap: 2.8rem; align-items: center; }
@media (min-width: 980px) { .sn-hero-grid { grid-template-columns: 1.05fr 1fr; } }
.sn-hero-grid--center { grid-template-columns: 1fr !important; text-align: center; justify-items: center; }
.sn-hero-grid--center .sn-lead { margin-left: auto; margin-right: auto; }
.sn-hero-grid--center .sn-hero-cta { justify-content: center; }
.sn-pill { display: inline-block; font-size: .72rem; font-weight: 700; letter-spacing: .16em; text-transform: uppercase; color: #6b6b6b; background: #f1f1f2; padding: .35rem .8rem; border-radius: 999px; }
.sn-h1 { font-size: clamp(2rem, 4.2vw, 3.1rem); font-weight: 700; margin: 1.2rem 0 1rem; line-height: 1.1; }
.sn-lead { font-size: 1.14rem; line-height: 1.65; color: #6b6b6b; max-width: 48ch; }
.sn-hero-cta { display: flex; gap: .8rem; flex-wrap: wrap; margin-top: 1.8rem; }

/* Cadre navigateur */
.sn-frame { margin: 0; background: #fff; border: 1px solid #eaeaea; border-radius: 1.1rem; overflow: hidden; box-shadow: 0 24px 50px -30px rgba(0,0,0,.28); }
.sn-frame__bar { display: flex; align-items: center; gap: .4rem; padding: .6rem .85rem; background: #f7f7f8; border-bottom: 1px solid #eaeaea; }
.sn-frame__bar span { width: .6rem; height: .6rem; border-radius: 50%; background: #d4d4d8; }
.sn-frame img { display: block; width: 100%; height: auto; }

/* STATS band */
.sn-stats-band { background: #161616; color: #fff; padding: 2.4rem 0; }
.sn-stats { display: grid; grid-template-columns: repeat(2, 1fr); gap: 1.5rem; }
@media (min-width: 760px) { .sn-stats { grid-template-columns: repeat(4, 1fr); } }
.sn-stat { text-align: center; }
.sn-stat b { display: block; font-family: var(--fonts--primaryfont, "DM Sans", sans-serif); font-size: clamp(1.8rem, 3.5vw, 2.4rem); font-weight: 700; line-height: 1; }
.sn-stat span { display: block; margin-top: .5rem; font-size: .85rem; color: #a1a1aa; line-height: 1.35; }

/* Sections */
.sn-section { padding: 4.5rem 0; }
.sn-alt { background: #fafafa; }
.sn-head { text-align: center; max-width: 640px; margin: 0 auto 3rem; }
.sn-head .sn-h2 { margin-top: .8rem; }
.sn-sub { color: #6b6b6b; font-size: 1.05rem; line-height: 1.55; }

/* Étapes */
.sn-steps { display: grid; grid-template-columns: 1fr; gap: 1.2rem; }
@media (min-width: 820px) { .sn-steps { grid-template-columns: repeat(3, 1fr); } }
.sn-step { background: #fff; border: 1px solid #eaeaea; border-radius: 1.4rem; padding: 1.8rem; transition: transform .2s, box-shadow .2s; }
.sn-step:hover { transform: translateY(-4px); box-shadow: 0 20px 40px -24px rgba(0,0,0,.16); }
.sn-step__top { display: flex; align-items: center; justify-content: space-between; margin-bottom: 1.1rem; }
.sn-step__ic { width: 2.8rem; height: 2.8rem; border-radius: .9rem; background: #f4f4f5; color: #161616; display: flex; align-items: center; justify-content: center; }
.sn-step__ic :deep(svg) { width: 1.5rem; height: 1.5rem; }
.sn-step__num { font-family: var(--fonts--primaryfont, "DM Sans", sans-serif); font-size: 1.6rem; font-weight: 700; color: #e4e4e7; }
.sn-step__title { font-size: 1.12rem; font-weight: 700; margin: 0 0 .5rem; }
.sn-step__desc { font-size: .96rem; line-height: 1.6; color: #6b6b6b; margin: 0; }

/* Split highlight */
.sn-split { display: grid; grid-template-columns: 1fr; gap: 2.5rem; align-items: center; }
@media (min-width: 900px) { .sn-split { grid-template-columns: .8fr 1.2fr; } }
.sn-big-stat { background: #161616; color: #fff; border-radius: 1.6rem; padding: 3rem 2rem; text-align: center; }
.sn-big-stat b { display: block; font-family: var(--fonts--primaryfont, "DM Sans", sans-serif); font-size: clamp(3.5rem, 9vw, 5.5rem); font-weight: 700; line-height: 1; }
.sn-big-stat span { display: block; margin-top: 1rem; color: #a1a1aa; font-size: 1rem; line-height: 1.4; }
.sn-checks { list-style: none; margin: 1.4rem 0; padding: 0; display: flex; flex-direction: column; gap: .7rem; }
.sn-checks li { position: relative; padding-left: 1.9rem; font-weight: 600; color: #2e2e2e; }
.sn-checks li::before { content: ""; position: absolute; left: 0; top: .05rem; width: 1.3rem; height: 1.3rem; border-radius: 50%; background: #161616;
  -webkit-mask: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='white' stroke-width='3' stroke-linecap='round' stroke-linejoin='round'><path d='M5 13l4 4L19 7'/></svg>") center / .8rem no-repeat;
  mask: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='white' stroke-width='3' stroke-linecap='round' stroke-linejoin='round'><path d='M5 13l4 4L19 7'/></svg>") center / .8rem no-repeat; }
.sn-links { display: flex; flex-wrap: wrap; gap: 1.2rem; margin-top: 1.4rem; }
.sn-links a { color: #161616; font-weight: 700; text-decoration: none; border-bottom: 2px solid #e4e4e7; padding-bottom: 2px; }
.sn-links a:hover { border-color: #161616; }

/* FAQ */
.sn-faq { display: flex; flex-direction: column; gap: .9rem; }
.sn-faq__item { background: #fff; border: 1px solid #eaeaea; border-radius: 1rem; padding: 1.1rem 1.3rem; }
.sn-faq__item summary { font-weight: 700; font-size: 1.05rem; cursor: pointer; color: #161616; list-style: none; display: flex; justify-content: space-between; align-items: center; gap: 1rem; }
.sn-faq__item summary::after { content: "+"; font-size: 1.4rem; color: #9ca3af; font-weight: 400; }
.sn-faq__item[open] summary::after { content: "−"; }
.sn-faq__item p { margin: .9rem 0 0; color: #6b6b6b; line-height: 1.65; }

/* CTA final */
.sn-cta { background: #fafafa; border-top: 1px solid #eee; padding: 5rem 0; text-align: center; }
.sn-cta .sn-h2 { margin-bottom: .6rem; }
.sn-cta .sn-sub { margin-bottom: 1.8rem; }
</style>
