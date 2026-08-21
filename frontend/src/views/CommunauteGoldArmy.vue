<script setup>
import { useHead } from '@unhead/vue'
import LandingNav from '@/components/LandingNav.vue'
import Footer from '@/components/Footer.vue'
const BASE = 'https://www.goldarmyai.com'
useHead({
  title: 'Communauté GoldArmy — entraide entre candidats d\'une même organisation | GoldArmy AI',
  meta: [
    { name: 'description', content: "Un espace d'entraide type Discord pour les membres d'une organisation : partagez modèles de CV, portfolios, offres et résultats d'entretien, échangez en salons thématiques." },
    { name: 'robots', content: 'index, follow' },
    { property: 'og:title', content: 'Communauté GoldArmy — entraide entre candidats' },
    { property: 'og:description', content: "Salons, partage de CV et portfolios, offres et résultats d'entretien : la vie de cohorte au même endroit." },
    { property: 'og:url', content: `${BASE}/communaute-goldarmy` },
    { property: 'og:image', content: `${BASE}/og-banner.png` }
  ],
  link: [{ rel: 'canonical', href: `${BASE}/communaute-goldarmy` }]
})

const svg = (inner) => `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">${inner}</svg>`

const stats = [
  { n: 'Salons', l: 'des discussions thématiques' },
  { n: 'Type Discord', l: 'entraide en temps réel' },
  { n: 'Score ATS', l: 'sur les CV partagés' },
  { n: 'Privée', l: 'réservée à ton organisation' }
]

const steps = [
  { num: '01', title: 'Des salons pour tout partager', desc: "Discussion générale, modèles de CV, portfolios, offres d'emploi et résultats de simulation d'entretien. Chaque publication peut être likée et commentée.", icon: svg('<path d="M4 9h16"/><path d="M4 15h16"/><path d="M10 3L8 21"/><path d="M16 3l-2 18"/>') },
  { num: '02', title: 'Le partage de CV avec score ATS', desc: "Dépose un modèle de CV : le système calcule son score ATS et l'affiche à côté de l'aperçu, pour que la cohorte s'inspire des meilleurs formats.", icon: svg('<path d="M14 3v4a1 1 0 0 0 1 1h4"/><path d="M17 21H7a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h7l5 5v11a2 2 0 0 1-2 2z"/><path d="M9 14l2 2 4-4"/>') },
  { num: '03', title: 'Réservée à ton organisation', desc: "Seuls les membres rattachés accèdent à la Communauté. C'est l'endroit où la dynamique de groupe accélère l'insertion de chacun.", icon: svg('<path d="M12 3l7 3v6c0 4.5-3 7.5-7 9-4-1.5-7-4.5-7-9V6z"/><path d="M9.5 12l1.8 1.8L15 10"/>') }
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
            <span class="sn-pill">Communauté</span>
            <h1 class="sn-h1">Chercher un emploi, mais pas tout seul</h1>
            <p class="sn-lead">
              Un espace d'entraide type Discord pour les membres d'une même organisation : on partage,
              on s'entraide, on progresse ensemble.
            </p>
            <div class="sn-hero-cta">
              <router-link to="/register" class="sn-btn">Rejoindre une communauté</router-link>
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

      <!-- PRINCIPE -->
      <section class="sn-section">
        <div class="sn-wrap sn-narrow">
          <span class="sn-eyebrow">Le principe</span>
          <h2 class="sn-h2">La vie de cohorte, au même endroit</h2>
          <p class="sn-p">
            La Communauté s'organise en salons thématiques, à la manière d'un Discord : discussion générale,
            <strong>modèles de CV</strong>, <strong>portfolios</strong>, <strong>offres d'emploi</strong> et
            <strong>résultats de simulation d'entretien</strong>. Chaque publication peut être likée et
            commentée.
          </p>
        </div>
      </section>

      <!-- FONCTIONNEMENT -->
      <section id="fonctionnement" class="sn-section sn-alt">
        <div class="sn-wrap">
          <div class="sn-head">
            <span class="sn-eyebrow">Ce que tu y trouves</span>
            <h2 class="sn-h2">Une communauté pensée pour l'entraide</h2>
            <p class="sn-sub">Des salons, du partage de ressources et une dynamique de groupe privée.</p>
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

      <!-- HIGHLIGHT (split) -->
      <section class="sn-section">
        <div class="sn-wrap sn-split">
          <div class="sn-split__figure">
            <div class="sn-big-stat"><b>Discord</b><span>l'entraide façon Discord, mais privée à ton organisation</span></div>
          </div>
          <div class="sn-split__copy">
            <span class="sn-eyebrow">L'esprit</span>
            <h2 class="sn-h2">La dynamique de groupe qui accélère l'insertion</h2>
            <p class="sn-p">
              Quand une cohorte partage ses meilleurs formats de CV, ses offres et ses retours d'entretien,
              chacun progresse plus vite. La Communauté transforme la recherche d'emploi, souvent solitaire,
              en effort collectif.
            </p>
            <ul class="sn-checks">
              <li>Salons thématiques (CV, portfolios, offres…)</li>
              <li>Publications likables et commentables</li>
              <li>CV partagés avec leur score ATS</li>
            </ul>
            <div class="sn-links">
              <router-link to="/mentorat-a-la-demande">Le Hub Mentors →</router-link>
              <router-link to="/pour-les-organisations">Espace Organisation →</router-link>
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
              <summary>Qui peut accéder à la Communauté ?</summary>
              <p>Elle est privée à ton organisation : seuls les membres rattachés y accèdent, ce qui garantit un espace de confiance.</p>
            </details>
            <details class="sn-faq__item">
              <summary>Que peut-on partager ?</summary>
              <p>Modèles de CV (avec score ATS), portfolios, offres d'emploi et résultats de simulation d'entretien, dans des salons dédiés.</p>
            </details>
          </div>
        </div>
      </section>

      <!-- CTA -->
      <section class="sn-cta">
        <div class="sn-wrap">
          <h2 class="sn-h2">Tu fais partie d'une organisation ?</h2>
          <p class="sn-sub">Rejoins ta communauté et profite de l'entraide de ta cohorte.</p>
          <router-link to="/register" class="sn-btn">Créer mon compte</router-link>
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
.sn-big-stat b { display: block; font-family: var(--fonts--primaryfont, "DM Sans", sans-serif); font-size: clamp(2.4rem, 6vw, 3.6rem); font-weight: 700; line-height: 1; }
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
