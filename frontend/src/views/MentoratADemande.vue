<script setup>
import { useHead } from '@unhead/vue'
import LandingNav from '@/components/LandingNav.vue'
import Footer from '@/components/Footer.vue'
const BASE = 'https://www.goldarmyai.com'
useHead({
  title: 'Hub Mentors — le mentorat carrière à la demande | GoldArmy AI',
  meta: [
    { name: 'description', content: "Trouvez un mentor et réservez une session en quelques clics. Un marketplace de mentorat carrière : revue de CV, simulation d'entretien, conseil et négociation salariale." },
    { name: 'robots', content: 'index, follow' },
    { property: 'og:title', content: 'Hub Mentors — mentorat à la demande | GoldArmy' },
    { property: 'og:description', content: 'Le mentorat carrière à la demande : trouve un mentor, réserve une session, participe aux ateliers.' },
    { property: 'og:url', content: `${BASE}/mentorat-a-la-demande` },
    { property: 'og:image', content: `${BASE}/og-banner.png` }
  ],
  link: [{ rel: 'canonical', href: `${BASE}/mentorat-a-la-demande` }]
})

const svg = (inner) => `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">${inner}</svg>`

const stats = [
  { n: 'Marketplace', l: 'des mentors par spécialité' },
  { n: 'À la demande', l: 'réserve une session ciblée' },
  { n: 'Ateliers', l: 'sessions de groupe' },
  { n: 'Avis', l: 'une réputation par note' }
]

const steps = [
  { num: '01', title: 'Trouve ton mentor', desc: "Chaque mentor affiche ses spécialités, ses disponibilités, sa note et son tarif. Filtre selon ton objectif du moment.", icon: svg('<circle cx="9" cy="8" r="3"/><path d="M3 20c0-3 3-5 6-5s6 2 6 5"/><circle cx="17.5" cy="9" r="2.2"/><path d="M15.5 15c2.6.3 4.5 2 4.5 5"/>') },
  { num: '02', title: 'Réserve une session', desc: "Tu envoies une demande de session ciblée, le mentor accepte, et tu obtiens un accompagnement concret au créneau convenu.", icon: svg('<rect x="3" y="4" width="18" height="17" rx="2"/><path d="M3 9h18"/><path d="M8 2v4"/><path d="M16 2v4"/>') },
  { num: '03', title: 'Progresse et évalue', desc: "Après la session, tes avis construisent la réputation des mentors et guident les prochains membres vers les meilleurs.", icon: svg('<path d="M12 3l2.9 6 6.1.9-4.5 4.3 1.1 6.1L12 18.8 6.4 20.3l1.1-6.1L3 9.9 9.1 9z"/>') }
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
            <span class="sn-pill">Mentorat à la demande</span>
            <h1 class="sn-h1">Un mentor carrière, quand tu en as besoin</h1>
            <p class="sn-lead">
              Fini de chercher « quelqu'un qui pourrait t'aider ». Le Hub Mentors est un véritable
              marketplace : trouve un mentor, choisis un service, réserve — et progresse.
            </p>
            <div class="sn-hero-cta">
              <router-link to="/register" class="sn-btn">Découvrir les mentors</router-link>
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
          <h2 class="sn-h2">Comment ça marche</h2>
          <p class="sn-p">
            Le Hub Mentors met en relation les candidats et des mentors inscrits. Chaque mentor affiche ses
            <strong>spécialités</strong>, ses <strong>disponibilités</strong>, sa note et son tarif. Tu
            envoies une demande de session ciblée, le mentor accepte, et tu obtiens un accompagnement concret.
          </p>
        </div>
      </section>

      <!-- FONCTIONNEMENT -->
      <section id="fonctionnement" class="sn-section sn-alt">
        <div class="sn-wrap">
          <div class="sn-head">
            <span class="sn-eyebrow">Le parcours</span>
            <h2 class="sn-h2">Trois étapes pour te faire accompagner</h2>
            <p class="sn-sub">Du choix du mentor à la session, tout se passe au même endroit.</p>
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

      <!-- SERVICES (split) -->
      <section class="sn-section">
        <div class="sn-wrap sn-split">
          <div class="sn-split__figure">
            <div class="sn-big-stat"><b>4</b><span>services clés pour chaque étape de ta recherche</span></div>
          </div>
          <div class="sn-split__copy">
            <span class="sn-eyebrow">Les services</span>
            <h2 class="sn-h2">Un accompagnement concret, à la carte</h2>
            <p class="sn-p">Choisis exactement le coup de pouce dont tu as besoin, au moment où tu en as besoin.</p>
            <ul class="sn-checks">
              <li>Revue de CV : un regard expert sur ton dossier</li>
              <li>Simulation d'entretien avec un professionnel</li>
              <li>Conseil carrière &amp; reconversion</li>
              <li>Négociation salariale</li>
            </ul>
            <div class="sn-links">
              <router-link to="/communaute-goldarmy">La Communauté →</router-link>
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
              <summary>Puis-je devenir mentor à mon tour ?</summary>
              <p>Oui, le registre est ouvert : publie un profil (photo, expertises, disponibilités, liens), reçois des demandes et gère ta boîte de réservations. Les avis après session construisent ta réputation.</p>
            </details>
            <details class="sn-faq__item">
              <summary>Comment se déroule une session ?</summary>
              <p>Tu choisis un mentor et un service, puis tu envoies une demande. Une fois acceptée, la session se tient au créneau convenu, et tu peux laisser un avis ensuite.</p>
            </details>
          </div>
        </div>
      </section>

      <!-- CTA -->
      <section class="sn-cta">
        <div class="sn-wrap">
          <h2 class="sn-h2">Prêt à te faire accompagner ?</h2>
          <p class="sn-sub">Trouve un mentor aligné sur ton objectif dès aujourd'hui.</p>
          <router-link to="/register" class="sn-btn">Ouvrir le Hub Mentors</router-link>
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
