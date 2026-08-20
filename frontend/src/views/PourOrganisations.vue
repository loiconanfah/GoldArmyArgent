<script setup>
import { useHead } from '@unhead/vue'
import LandingNav from '@/components/LandingNav.vue'
import Footer from '@/components/Footer.vue'

const BASE = 'https://www.goldarmyai.com'
useHead({
  title: 'Espace Organisation — GoldArmy pour écoles, bootcamps & organismes d\'employabilité',
  meta: [
    { name: 'description', content: "Un portail B2B2C complet pour piloter vos cohortes : tableau de bord, suivi des membres, mentors, réseau, communauté et facturation par paliers. Parrainez vos membres en Gold et mesurez l'insertion en temps réel." },
    { name: 'robots', content: 'index, follow' },
    { property: 'og:type', content: 'website' },
    { property: 'og:title', content: 'Espace Organisation — GoldArmy' },
    { property: 'og:description', content: 'Pilotez l\'employabilité de vos cohortes : KPIs, mentors, réseau, communauté et facturation par paliers.' },
    { property: 'og:url', content: `${BASE}/pour-les-organisations` },
    { property: 'og:image', content: `${BASE}/og-banner.png` },
    { property: 'og:site_name', content: 'GoldArmy AI' },
    { name: 'twitter:card', content: 'summary_large_image' }
  ],
  link: [{ rel: 'canonical', href: `${BASE}/pour-les-organisations` }]
})

const screens = [
  {
    img: '/images/org-dashboard.png', eyebrow: 'Pilotage',
    title: 'Toute votre cohorte, en un coup d\'œil',
    desc: "Le tableau de bord réunit les indicateurs qui comptent et se met à jour en temps réel, pour piloter l'insertion sans tableur.",
    points: ['KPIs animés : membres, actifs, candidatures, entretiens', 'Courbe des candidatures & jauge du taux d\'entretien', 'Prochain événement et membres les plus actifs'],
    reverse: false
  },
  {
    img: '/images/org-members.png', eyebrow: 'Suivi des membres',
    title: 'Le suivi individuel, membre par membre',
    desc: "Ouvrez la fiche d'un membre et pilotez tout son accompagnement depuis un panneau clair.",
    points: ['Parrainage : activez l\'accès premium pour verser du Gold mensuel', 'Rôle dans l\'organisation : Membre, Mentor, Conseiller', 'Progression des candidatures, entretiens et simulations'],
    reverse: true
  },
  {
    img: '/images/org-community.png', eyebrow: 'Vie de la cohorte',
    title: 'Une communauté façon Discord',
    desc: "Un espace privé où votre cohorte échange, s'entraide et partage ses meilleures ressources.",
    points: ['Salons : général, modèles-cv, portfolios, offres, résultats', 'Publications likables et commentables', 'Membres par rôle dans un panneau latéral'],
    reverse: false
  },
  {
    img: '/images/org-billing.png', eyebrow: 'Gestion',
    title: 'Une facturation claire, par paliers',
    desc: "Un forfait qui grandit avec votre cohorte, en mensuel ou annuel — vous parrainez à la carte.",
    points: ['Starter, Growth, Scale, Enterprise', 'Gold mensuel par membre inclus dans chaque palier', 'Résiliable à tout moment, prix transparents'],
    reverse: true
  }
]

const plans = [
  { name: 'Starter', members: 'Jusqu\'à 25 membres', gold: '300 Gold/membre/mois', highlight: false },
  { name: 'Growth', members: 'Jusqu\'à 75 membres', gold: '300 Gold/membre/mois', highlight: true },
  { name: 'Scale', members: 'Jusqu\'à 200 membres', gold: '600 Gold/membre/mois', highlight: false },
  { name: 'Enterprise', members: 'Membres illimités', gold: 'Gold sur devis', highlight: false }
]
</script>

<template>
  <div class="org-page">
    <LandingNav />
    <main>
      <!-- HERO -->
      <header class="org-hero">
        <div class="org-wrap org-hero-grid">
          <div class="org-hero-copy">
            <span class="org-pill">Pour les organisations</span>
            <h1 class="org-h1">Pilotez l'employabilité de vos cohortes, au même endroit.</h1>
            <p class="org-lead">Écoles, bootcamps, organismes d'employabilité, agences de placement : offrez à vos membres toute la puissance de GoldArmy, et gardez le contrôle avec un portail d'administration complet.</p>
            <div class="org-hero-cta">
              <router-link to="/register" class="org-btn-primary">Créer mon espace organisation</router-link>
              <a href="#apercu" class="org-btn-ghost">Voir le portail</a>
            </div>
            <div class="org-hero-stats">
              <div><b>Temps réel</b><span>Insertion & activité</span></div>
              <div><b>Par paliers</b><span>Facturation simple</span></div>
              <div><b>Gold inclus</b><span>Parrainage des membres</span></div>
            </div>
          </div>
          <figure class="org-frame org-frame--hero">
            <div class="org-frame__bar"><span></span><span></span><span></span></div>
            <img :src="screens[0].img" alt="Tableau de bord de l'espace organisation GoldArmy" loading="eager" />
          </figure>
        </div>
      </header>

      <!-- PROBLÈME / SOLUTION -->
      <section class="org-section">
        <div class="org-wrap org-two">
          <div class="org-card bad">
            <h3>Sans outil dédié</h3>
            <ul><li>Suivi des membres dans des tableurs éparpillés</li><li>Aucune visibilité sur l'insertion réelle</li><li>Mentors et ateliers gérés à la main</li><li>Impossible de mesurer l'impact du programme</li></ul>
          </div>
          <div class="org-card good">
            <h3>Avec GoldArmy Organisation</h3>
            <ul><li>Un portail unique, KPIs animés en temps réel</li><li>Progression individuelle de chaque membre</li><li>Mentors, événements et communauté intégrés</li><li>Parrainage en Gold + facturation claire par paliers</li></ul>
          </div>
        </div>
      </section>

      <!-- APERÇU DU PORTAIL (captures réelles) -->
      <section id="apercu" class="org-section org-alt">
        <div class="org-wrap">
          <div class="org-head">
            <span class="org-eyebrow">Aperçu du portail</span>
            <h2>Conçu pour piloter, pas pour bricoler</h2>
            <p>Chaque écran a été pensé pour accompagner une cohorte, de l'onboarding à l'insertion.</p>
          </div>

          <div class="org-features">
            <article v-for="s in screens" :key="s.title" :class="['org-feature', { 'org-feature--reverse': s.reverse }]">
              <figure class="org-frame">
                <div class="org-frame__bar"><span></span><span></span><span></span></div>
                <img :src="s.img" :alt="s.title" loading="lazy" />
              </figure>
              <div class="org-feature__copy">
                <span class="org-eyebrow">{{ s.eyebrow }}</span>
                <h3>{{ s.title }}</h3>
                <p>{{ s.desc }}</p>
                <ul>
                  <li v-for="p in s.points" :key="p">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M5 13l4 4L19 7"/></svg>
                    {{ p }}
                  </li>
                </ul>
              </div>
            </article>
          </div>
        </div>
      </section>

      <!-- MODÈLE DE PARRAINAGE -->
      <section class="org-section">
        <div class="org-wrap org-two-b">
          <div class="org-mock2" aria-hidden="true">
            <div class="mem"><span class="av">A</span><div><b>Membre sponsorisé</b><small>+300 Gold / mois</small></div><span class="tag on">Actif</span></div>
            <div class="mem"><span class="av">M</span><div><b>Membre sponsorisé</b><small>+300 Gold / mois</small></div><span class="tag on">Actif</span></div>
            <div class="mem"><span class="av">Y</span><div><b>Non sponsorisé</b><small>—</small></div><span class="tag off">Libre</span></div>
          </div>
          <div>
            <span class="org-eyebrow">Le modèle</span>
            <h2>Vous avez l'accès complet. Vous parrainez vos membres.</h2>
            <p class="org-p">En tant qu'administrateur, vous disposez de toutes les fonctionnalités. Vous choisissez <strong>quels membres parrainer</strong> : chaque membre sponsorisé reçoit du <strong>Gold chaque mois</strong> pour utiliser le Sniper, les audits CV, les simulations d'entretien, etc. Vous ne payez que pour ce que vous décidez de financer.</p>
            <router-link to="/register" class="org-btn-primary">Démarrer</router-link>
          </div>
        </div>
      </section>

      <!-- TARIFS PALIERS -->
      <section class="org-section org-alt">
        <div class="org-wrap">
          <div class="org-head">
            <span class="org-eyebrow">Facturation par paliers</span>
            <h2>Un forfait qui grandit avec votre cohorte</h2>
            <p>Le Gold mensuel par membre est inclus dans chaque palier. Vous parrainez à la carte.</p>
          </div>
          <div class="org-plans">
            <div v-for="p in plans" :key="p.name" :class="['org-plan', { hot: p.highlight }]">
              <span v-if="p.highlight" class="org-plan-badge">Populaire</span>
              <h4>{{ p.name }}</h4>
              <p class="org-plan-mem">{{ p.members }}</p>
              <p class="org-plan-gold">{{ p.gold }}</p>
              <router-link to="/register" class="org-plan-cta">Choisir</router-link>
            </div>
          </div>
          <p class="org-fineprint">Prix affichés côté portail (CAD), taxes en sus. Résiliable à tout moment.</p>
        </div>
      </section>

      <!-- CTA FINAL -->
      <section class="org-cta-final">
        <div class="org-wrap">
          <h2>Prêt à équiper votre programme ?</h2>
          <p>Créez votre espace organisation en quelques minutes et invitez votre première cohorte.</p>
          <router-link to="/register" class="org-btn-light">Créer mon espace organisation</router-link>
        </div>
      </section>
    </main>
    <Footer />
  </div>
</template>

<style scoped>
.org-page { background: #fff; color: #0f172a; }
.org-wrap { max-width: 1160px; margin: 0 auto; padding: 0 1.5rem; }
.org-pill, .org-eyebrow { display: inline-block; font-size: .72rem; font-weight: 800; letter-spacing: .16em; text-transform: uppercase; color: #ea580c; background: #FFF1E8; padding: .35rem .8rem; border-radius: 999px; }

/* HERO — léger & épuré, comme la page d'accueil */
.org-hero { background: linear-gradient(180deg, #fff 0%, #f8fafc 100%); color: #0f172a; padding: 4.5rem 0 4rem; overflow: hidden; }
.org-hero-grid { display: grid; grid-template-columns: 1fr; gap: 2.8rem; align-items: center; }
@media (min-width: 980px) { .org-hero-grid { grid-template-columns: 1fr 1.05fr; } }
.org-h1 { font-size: clamp(2rem, 4.2vw, 3.1rem); font-weight: 800; line-height: 1.1; margin: 1.2rem 0 1rem; letter-spacing: -.025em; color: #0f172a; }
.org-lead { color: #475569; font-size: 1.12rem; line-height: 1.6; max-width: 46ch; }
.org-hero-cta { display: flex; gap: .8rem; flex-wrap: wrap; margin: 1.8rem 0 1.6rem; }
.org-btn-primary { background: linear-gradient(135deg, #ff9a5c, #ff6f00); color: #000; font-weight: 800; padding: .9rem 1.6rem; border-radius: .8rem; text-decoration: none; box-shadow: 0 10px 25px rgba(255,111,0,.35); transition: transform .2s, box-shadow .2s; }
.org-btn-primary:hover { transform: translateY(-2px); box-shadow: 0 12px 30px rgba(255,111,0,.45); }
.org-btn-ghost { color: #0f172a; border: 1px solid #e2e8f0; background: #fff; padding: .9rem 1.4rem; border-radius: .8rem; text-decoration: none; font-weight: 700; transition: border-color .2s; }
.org-btn-ghost:hover { border-color: #ff9a5c; }
.org-hero-stats { display: flex; gap: 2rem; flex-wrap: wrap; margin-top: 1.4rem; }
.org-hero-stats div { display: flex; flex-direction: column; }
.org-hero-stats b { color: #ea580c; font-size: 1.05rem; }
.org-hero-stats span { color: #94a3b8; font-size: .8rem; }

/* Cadre navigateur pour les captures — plat, ombre douce */
.org-frame { margin: 0; background: #fff; border: 1px solid #e2e8f0; border-radius: 1.1rem; overflow: hidden; box-shadow: 0 24px 50px -30px rgba(2,6,23,.28); }
.org-frame--hero { box-shadow: 0 30px 60px -30px rgba(2,6,23,.32); }
.org-frame__bar { display: flex; align-items: center; gap: .4rem; padding: .6rem .85rem; background: #f8fafc; border-bottom: 1px solid #e2e8f0; }
.org-frame__bar span { width: .6rem; height: .6rem; border-radius: 50%; background: #cbd5e1; }
.org-frame__bar span:nth-child(1) { background: #f87171; } .org-frame__bar span:nth-child(2) { background: #fbbf24; } .org-frame__bar span:nth-child(3) { background: #34d399; }
.org-frame img { display: block; width: 100%; height: auto; background: #f8fafc; }

/* Sections */
.org-section { padding: 4.5rem 0; }
.org-alt { background: #f8fafc; }
.org-head { text-align: center; max-width: 660px; margin: 0 auto 3rem; }
.org-head h2 { font-size: clamp(1.7rem, 3.6vw, 2.4rem); font-weight: 800; margin: 1rem 0 .6rem; letter-spacing: -.02em; }
.org-head p { color: #475569; font-size: 1.05rem; }

/* Problème / solution */
.org-two, .org-two-b { display: grid; grid-template-columns: 1fr; gap: 1.2rem; align-items: center; }
@media (min-width: 860px) { .org-two { grid-template-columns: 1fr 1fr; } .org-two-b { grid-template-columns: .85fr 1.15fr; } }
.org-card { border-radius: 1.3rem; padding: 1.8rem; }
.org-card h3 { font-size: 1.1rem; font-weight: 800; margin: 0 0 1rem; }
.org-card ul { margin: 0; padding-left: 1.1rem; line-height: 1.75; }
.org-card.bad { background: #FBEEE8; border: 1px solid #F0D3C6; color: #7c3a24; }
.org-card.good { background: #EAF6EC; border: 1px solid #CDE8D2; color: #1f5130; }

/* Aperçu : lignes alternées capture + texte */
.org-features { display: flex; flex-direction: column; gap: 4rem; }
.org-feature { display: grid; grid-template-columns: 1fr; gap: 2rem; align-items: center; }
@media (min-width: 900px) { .org-feature { grid-template-columns: 1.15fr .85fr; } .org-feature--reverse .org-frame { order: 2; } }
.org-feature__copy h3 { font-size: clamp(1.4rem, 2.6vw, 1.9rem); font-weight: 800; margin: .8rem 0 .7rem; letter-spacing: -.02em; }
.org-feature__copy p { color: #475569; font-size: 1.02rem; line-height: 1.65; margin: 0 0 1.2rem; }
.org-feature__copy ul { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: .7rem; }
.org-feature__copy li { display: flex; align-items: flex-start; gap: .65rem; font-size: .95rem; font-weight: 600; color: #1e293b; line-height: 1.45; }
.org-feature__copy li svg { width: 1.15rem; height: 1.15rem; color: #16a34a; flex-shrink: 0; margin-top: .1rem; }

.org-p { color: #334155; font-size: 1.05rem; line-height: 1.7; margin: 1rem 0 1.6rem; }

/* Mockup membres (parrainage) */
.org-mock2 { background: #fff; border: 1px solid #e2e8f0; border-radius: 1.3rem; padding: 1rem; box-shadow: 0 24px 50px -30px rgba(2,6,23,.35); display: flex; flex-direction: column; gap: .7rem; }
.mem { display: flex; align-items: center; gap: .7rem; background: #f8fafc; border: 1px solid #eef2f7; border-radius: .9rem; padding: .7rem; }
.mem .av { width: 2rem; height: 2rem; border-radius: 50%; background: linear-gradient(135deg,#ff9a5c,#ff6f00); color: #fff; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: .8rem; }
.mem b { font-size: .85rem; } .mem small { color: #94a3b8; font-size: .72rem; }
.mem .tag { margin-left: auto; font-size: .62rem; font-weight: 800; text-transform: uppercase; padding: .15rem .5rem; border-radius: 999px; }
.tag.on { background: #D1FAE5; color: #059669; } .tag.off { background: #eef2f7; color: #94a3b8; }

/* Plans */
.org-plans { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px,1fr)); gap: 1rem; }
.org-plan { position: relative; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 1.3rem; padding: 1.8rem 1.4rem; text-align: center; transition: transform .2s, box-shadow .2s; }
.org-plan:hover { transform: translateY(-3px); box-shadow: 0 20px 40px -26px rgba(2,6,23,.35); }
.org-plan.hot { border-color: #ff6f00; box-shadow: 0 18px 40px -22px rgba(255,111,0,.5); background: #fff; }
.org-plan-badge { position: absolute; top: -.6rem; left: 50%; transform: translateX(-50%); background: linear-gradient(135deg,#ff9a5c,#ff6f00); color: #fff; font-size: .6rem; font-weight: 800; text-transform: uppercase; letter-spacing: .06em; padding: .25rem .7rem; border-radius: 999px; }
.org-plan h4 { font-size: 1.2rem; font-weight: 800; margin: 0 0 .5rem; }
.org-plan-mem { color: #475569; font-size: .88rem; margin: 0 0 .3rem; }
.org-plan-gold { color: #ea580c; font-weight: 800; font-size: .95rem; margin: 0 0 1.2rem; }
.org-plan-cta { display: block; background: #0f172a; color: #fff; padding: .7rem; border-radius: .7rem; text-decoration: none; font-weight: 700; }
.org-plan.hot .org-plan-cta { background: linear-gradient(135deg,#ff9a5c,#ff6f00); color: #0b1220; }
.org-fineprint { text-align: center; color: #94a3b8; font-size: .82rem; margin-top: 1.6rem; }

/* CTA final — panneau clair, chaleureux et doux */
.org-cta-final { background: #fff; padding: 4.5rem 0; }
.org-cta-final .org-wrap { background: linear-gradient(135deg, #FFF7F1, #FFF1E8); border: 1px solid #FADBC6; border-radius: 1.6rem; padding: 3.5rem 2rem; text-align: center; max-width: 900px; }
.org-cta-final h2 { font-size: clamp(1.8rem,3.6vw,2.4rem); font-weight: 800; margin: 0 0 .6rem; color: #0f172a; letter-spacing: -.02em; }
.org-cta-final p { color: #475569; margin: 0 0 1.6rem; }
.org-btn-light { background: linear-gradient(135deg, #ff9a5c, #ff6f00); color: #000; font-weight: 800; padding: 1rem 1.9rem; border-radius: .8rem; text-decoration: none; display: inline-block; box-shadow: 0 10px 25px rgba(255,111,0,.35); transition: transform .2s, box-shadow .2s; }
.org-btn-light:hover { transform: translateY(-2px); box-shadow: 0 12px 30px rgba(255,111,0,.45); }
</style>
