<script setup>
import { useHead } from '@unhead/vue'
import LandingNav from '@/components/LandingNav.vue'
import Footer from '@/components/Footer.vue'
const BASE = 'https://www.goldarmyai.com'
useHead({
  title: 'Le Gold — payez à l\'usage, sans abonnement obligatoire | GoldArmy AI',
  meta: [
    { name: 'description', content: "Le Gold est la monnaie de GoldArmy : 50 offerts à l'inscription, 100 gratuits chaque mois, rechargeable via la Boutique. Payez à l'usage, le Gold ne périme jamais." },
    { name: 'robots', content: 'index, follow' },
    { property: 'og:title', content: 'Le Gold — payez à l\'usage | GoldArmy' },
    { property: 'og:description', content: 'La monnaie GoldArmy : Gold offert chaque mois, packs à la carte, aucun abonnement obligatoire.' },
    { property: 'og:url', content: `${BASE}/economie-gold` },
    { property: 'og:image', content: `${BASE}/og-banner.png` }
  ],
  link: [{ rel: 'canonical', href: `${BASE}/economie-gold` }]
})

const svg = (inner) => `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">${inner}</svg>`

const stats = [
  { n: '50', l: 'Gold offerts à l\'inscription' },
  { n: '100', l: 'Gold gratuits chaque mois' },
  { n: '0 €', l: 'd\'abonnement obligatoire' },
  { n: '∞', l: 'le Gold ne périme jamais' }
]

const steps = [
  { num: '01', title: 'Du Gold offert', desc: "50 Gold dès l'inscription, puis 100 Gold gratuits chaque mois, renouvelés automatiquement. De quoi tout essayer.", icon: svg('<path d="M20 12v9H4v-9"/><path d="M2 7h20v5H2z"/><path d="M12 22V7"/><path d="M12 7S9 7 8 5.5 9 3 10 3.5 12 7 12 7z"/><path d="M12 7s3 0 4-1.5S15 3 14 3.5 12 7 12 7z"/>') },
  { num: '02', title: 'Payez à l\'usage', desc: "Chaque action — Sniper, audit CV, adaptation à une offre, simulation d'entretien — a un coût affiché avant d'agir. Aucune surprise, aucune facturation cachée.", icon: svg('<circle cx="12" cy="12" r="8"/><path d="M12 7v10"/><path d="M15 9.5C15 8 13.5 7.5 12 7.5S9 8.2 9 9.5s1.3 1.8 3 2 3 .7 3 2-1.5 2-3 2-3-.6-3-2"/>') },
  { num: '03', title: 'Rechargez à volonté', desc: "Rechargez via la Boutique quand vous voulez. Vous n'êtes jamais bloqué, et ce que vous avez reste à vous.", icon: svg('<path d="M20 12a8 8 0 1 1-2.3-5.6"/><path d="M20 4v4h-4"/>') }
]

const packs = [
  { name: 'Découverte', gold: '100 Gold', price: '4,99 €', badge: '' },
  { name: 'Populaire', gold: '300 + 20 Gold', price: '12,99 €', badge: 'Meilleur' },
  { name: 'Pro', gold: '750 + 100 Gold', price: '24,99 €', badge: '' },
  { name: 'Méga', gold: '2000 + 400 Gold', price: '59,99 €', badge: '' }
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
            <span class="sn-pill">Économie Gold</span>
            <h1 class="sn-h1">Payez seulement ce que vous utilisez</h1>
            <p class="sn-lead">
              Le Gold est la monnaie de GoldArmy. Pas d'abonnement obligatoire : vous recevez du Gold gratuit
              chaque mois, et vous rechargez à volonté selon vos besoins.
            </p>
            <div class="sn-hero-cta">
              <router-link to="/register" class="sn-btn">Commencer avec 50 Gold offerts</router-link>
              <a href="#packs" class="sn-btn-ghost">Voir les packs</a>
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
          <h2 class="sn-h2">Comment fonctionne le Gold</h2>
          <p class="sn-p">
            Le Gold se dépense à l'usage : recherche Sniper, audit CV, adaptation à une offre, simulation
            d'entretien, relance… Vous voyez le coût <strong>avant d'agir</strong>, et votre solde est
            toujours affiché en haut de l'application. Pas de surprise, pas de facturation cachée.
          </p>
        </div>
      </section>

      <!-- FONCTIONNEMENT -->
      <section class="sn-section sn-alt">
        <div class="sn-wrap">
          <div class="sn-head">
            <span class="sn-eyebrow">Le fonctionnement</span>
            <h2 class="sn-h2">Simple, transparent, sans engagement</h2>
            <p class="sn-sub">Du Gold offert chaque mois, un coût clair par action, rechargeable à tout moment.</p>
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

      <!-- PACKS -->
      <section id="packs" class="sn-section">
        <div class="sn-wrap">
          <div class="sn-head">
            <span class="sn-eyebrow">La Boutique</span>
            <h2 class="sn-h2">Rechargez selon vos besoins</h2>
            <p class="sn-sub">Des packs à la carte. Le Gold acheté ne périme jamais.</p>
          </div>
          <div class="sn-packs">
            <div v-for="p in packs" :key="p.name" :class="['sn-pack', { hot: p.badge }]">
              <span v-if="p.badge" class="sn-pack__badge">{{ p.badge }}</span>
              <h4>{{ p.name }}</h4>
              <p class="sn-pack__amt">{{ p.gold }}</p>
              <p class="sn-pack__price">{{ p.price }}</p>
              <router-link to="/register" class="sn-pack__cta">Obtenir</router-link>
            </div>
          </div>
        </div>
      </section>

      <!-- ABONNEMENTS (split) -->
      <section class="sn-section sn-alt">
        <div class="sn-wrap sn-split">
          <div class="sn-split__figure">
            <div class="sn-big-stat"><b>0 €</b><span>d'abonnement obligatoire : le mode « à l'usage » suffit pour la plupart</span></div>
          </div>
          <div class="sn-split__copy">
            <span class="sn-eyebrow">En option</span>
            <h2 class="sn-h2">Les abonnements, seulement si vous le voulez</h2>
            <p class="sn-p">
              Deux forfaits légers débloquent des modules et créditent plus de Gold chaque mois. Mais rien
              n'est obligatoire : le mode à l'usage reste disponible et gratuit.
            </p>
            <ul class="sn-checks">
              <li>Essentiel : 200 Gold/mois + espace Réseau</li>
              <li>Pro : 500 Gold/mois + Portfolio et fonctions avancées</li>
              <li>Le mode « à l'usage » reste gratuit</li>
            </ul>
            <div class="sn-links">
              <router-link to="/sniper-search">Découvrir le Sniper Search →</router-link>
              <router-link to="/mentor-ia">Le Mentor IA →</router-link>
            </div>
          </div>
        </div>
      </section>

      <!-- FAQ -->
      <section class="sn-section">
        <div class="sn-wrap sn-narrow">
          <div class="sn-head">
            <span class="sn-eyebrow">FAQ</span>
            <h2 class="sn-h2">Questions fréquentes</h2>
          </div>
          <div class="sn-faq">
            <details class="sn-faq__item">
              <summary>Le Gold gratuit expire-t-il ?</summary>
              <p>Le Gold ne périme jamais : ce que vous recevez ou achetez reste à vous, sans date limite.</p>
            </details>
            <details class="sn-faq__item">
              <summary>Suis-je obligé de prendre un abonnement ?</summary>
              <p>Non. Le mode « à l'usage » avec le Gold gratuit mensuel suffit pour la plupart des besoins. Les abonnements sont une option pour aller plus loin.</p>
            </details>
          </div>
        </div>
      </section>

      <!-- CTA -->
      <section class="sn-cta">
        <div class="sn-wrap">
          <h2 class="sn-h2">Commencez sans carte bancaire</h2>
          <p class="sn-sub">50 Gold offerts à l'inscription pour tout essayer, tout de suite.</p>
          <router-link to="/register" class="sn-btn">Créer mon compte gratuit</router-link>
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

/* Packs */
.sn-packs { display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 1rem; }
.sn-pack { position: relative; background: #fff; border: 1px solid #eaeaea; border-radius: 1.4rem; padding: 1.8rem 1.4rem; text-align: center; transition: transform .2s, box-shadow .2s; }
.sn-pack:hover { transform: translateY(-4px); box-shadow: 0 20px 40px -24px rgba(0,0,0,.16); }
.sn-pack.hot { border-color: #161616; }
.sn-pack__badge { position: absolute; top: -.6rem; left: 50%; transform: translateX(-50%); background: #161616; color: #fff; font-size: .6rem; font-weight: 700; text-transform: uppercase; letter-spacing: .06em; padding: .25rem .7rem; border-radius: 999px; }
.sn-pack h4 { font-family: var(--fonts--primaryfont, "DM Sans", sans-serif); font-size: 1.15rem; font-weight: 700; color: #161616; margin: 0 0 .5rem; }
.sn-pack__amt { color: #161616; font-weight: 700; margin: 0 0 .2rem; }
.sn-pack__price { color: #6b6b6b; font-size: 1.05rem; font-weight: 600; margin: 0 0 1.1rem; }
.sn-pack__cta { display: block; background: #161616; color: #fff; padding: .7rem; border-radius: .6rem; text-decoration: none; font-weight: 700; transition: background .2s; }
.sn-pack__cta:hover { background: #000; }

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
