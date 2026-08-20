<script setup>
import { useHead } from '@unhead/vue'
import LandingNav from '@/components/LandingNav.vue'
import Footer from '@/components/Footer.vue'

const BASE = 'https://www.goldarmyai.com'
useHead({
  title: 'Espace Organisation — GoldArmy pour écoles, bootcamps & organismes d\'employabilité',
  meta: [
    { name: 'description', content: "Un portail B2B2C complet pour piloter vos cohortes : suivi des membres, mentors, réseau, communauté et facturation par paliers. Parrainez vos membres en Gold et mesurez l'insertion en temps réel." },
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

const modules = [
  { t: 'Tableau de bord cohorte', d: 'KPIs animés en temps réel : taux d\'insertion, candidatures, entretiens, membres actifs.' },
  { t: 'Suivi des membres', d: 'Progression individuelle, état d\'avancement, et parrainage en Gold membre par membre.' },
  { t: 'Espace Mentors', d: 'Assignez des mentors et conseillers, planifiez des ateliers et des événements avec RSVP.' },
  { t: 'Réseau', d: 'Carnet de contacts partenaires par catégorie, import CSV et suggestions pour la cohorte.' },
  { t: 'Communauté', d: 'Un espace type Discord : partage de CV, portfolios, offres et résultats d\'entretien.' },
  { t: 'Facturation par paliers', d: 'Payez pour parrainer vos membres — chaque forfait crédite du Gold mensuel à la cohorte.' }
]
const plans = [
  { name: 'Starter', members: 'Jusqu\'à 25 membres', gold: '300 Gold/membre/mois', highlight: false },
  { name: 'Growth', members: 'Jusqu\'à 75 membres', gold: '300 Gold/membre/mois', highlight: true },
  { name: 'Scale', members: 'Jusqu\'à 200 membres', gold: '600 Gold/membre/mois', highlight: false },
  { name: 'Enterprise', members: 'Membres illimités', gold: '1000 Gold/membre/mois', highlight: false }
]
</script>

<template>
  <div class="org-page">
    <LandingNav />
    <main>
      <!-- HERO -->
      <header class="org-hero">
        <div class="org-wrap org-hero-grid">
          <div>
            <span class="org-pill">Pour les organisations</span>
            <h1 class="org-h1">Pilotez l'employabilité de vos cohortes, au même endroit.</h1>
            <p class="org-lead">Écoles, bootcamps, organismes d'employabilité, agences de placement : offrez à vos membres toute la puissance de GoldArmy, et gardez le contrôle avec un portail d'administration complet.</p>
            <div class="org-hero-cta">
              <router-link to="/register" class="org-btn-primary">Créer mon espace organisation</router-link>
              <a href="#modules" class="org-btn-ghost">Voir les modules</a>
            </div>
            <div class="org-hero-stats">
              <div><b>Temps réel</b><span>Insertion & activité</span></div>
              <div><b>Par paliers</b><span>Facturation simple</span></div>
              <div><b>Gold inclus</b><span>Parrainage des membres</span></div>
            </div>
          </div>
          <!-- Mockup dashboard (illustration CSS) -->
          <div class="org-mock" aria-hidden="true">
            <div class="org-mock-head"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><small>Tableau de bord — cohorte</small></div>
            <div class="org-mock-kpis">
              <div class="kpi"><b>78%</b><span>Insertion</span></div>
              <div class="kpi"><b>124</b><span>Membres actifs</span></div>
              <div class="kpi"><b>312</b><span>Entretiens</span></div>
            </div>
            <div class="org-mock-bars"><i style="height:40%"></i><i style="height:65%"></i><i style="height:50%"></i><i style="height:80%"></i><i style="height:70%"></i><i style="height:90%"></i></div>
            <div class="org-mock-rows"><span></span><span></span><span></span></div>
          </div>
        </div>
      </header>

      <!-- PROBLÈME -->
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

      <!-- MODULES -->
      <section id="modules" class="org-section org-alt">
        <div class="org-wrap">
          <div class="org-head">
            <span class="org-eyebrow">Ce qui est inclus</span>
            <h2>Un portail d'administration complet</h2>
            <p>Tout pour accompagner une cohorte, de l'onboarding à l'insertion.</p>
          </div>
          <div class="org-grid">
            <article v-for="m in modules" :key="m.t" class="org-mod">
              <div class="org-mod-ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M4 5h16M4 12h16M4 19h10"/></svg></div>
              <h4>{{ m.t }}</h4>
              <p>{{ m.d }}</p>
            </article>
          </div>
        </div>
      </section>

      <!-- MODÈLE SPONSORING -->
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
.org-page { background: #FBFAF8; color: #1C1917; }
.org-wrap { max-width: 1120px; margin: 0 auto; padding: 0 1.5rem; }
.org-pill, .org-eyebrow { display: inline-block; font-size: .72rem; font-weight: 800; letter-spacing: .14em; text-transform: uppercase; color: #B26B00; background: #FDF4E3; padding: .35rem .8rem; border-radius: 999px; }
/* HERO */
.org-hero { background: linear-gradient(160deg, #17130D 0%, #211a10 100%); color: #fff; padding: 4.5rem 0 4rem; }
.org-hero-grid { display: grid; grid-template-columns: 1fr; gap: 2.5rem; align-items: center; }
@media (min-width: 940px) { .org-hero-grid { grid-template-columns: 1.1fr .9fr; } }
.org-h1 { font-size: clamp(2rem, 4.2vw, 3.1rem); font-weight: 800; line-height: 1.12; margin: 1.2rem 0 1rem; letter-spacing: -.02em; }
.org-lead { color: #D6CFC4; font-size: 1.12rem; line-height: 1.6; max-width: 44ch; }
.org-hero-cta { display: flex; gap: .8rem; flex-wrap: wrap; margin: 1.8rem 0 1.6rem; }
.org-btn-primary { background: linear-gradient(135deg, #FBBF24, #F59E0B); color: #1a1206; font-weight: 800; padding: .9rem 1.6rem; border-radius: .8rem; text-decoration: none; box-shadow: 0 12px 28px -10px rgba(245,158,11,.6); }
.org-btn-ghost { color: #fff; border: 1px solid rgba(255,255,255,.25); padding: .9rem 1.4rem; border-radius: .8rem; text-decoration: none; font-weight: 700; }
.org-hero-stats { display: flex; gap: 2rem; flex-wrap: wrap; margin-top: 1.4rem; }
.org-hero-stats div { display: flex; flex-direction: column; }
.org-hero-stats b { color: #F5B301; font-size: 1.05rem; }
.org-hero-stats span { color: #A69C8E; font-size: .8rem; }
/* Mockup dashboard */
.org-mock { background: #fff; border-radius: 1.3rem; padding: 1rem; box-shadow: 0 30px 60px -30px rgba(0,0,0,.6); }
.org-mock-head { display: flex; align-items: center; gap: .4rem; padding: .3rem .4rem .8rem; border-bottom: 1px solid #EEF0F3; }
.org-mock-head small { color: #98A2B3; margin-left: auto; font-weight: 700; }
.dot { width: .6rem; height: .6rem; border-radius: 50%; } .dot.r { background: #F87171; } .dot.y { background: #FBBF24; } .dot.g { background: #34D399; }
.org-mock-kpis { display: grid; grid-template-columns: repeat(3,1fr); gap: .6rem; margin: .9rem 0; }
.kpi { background: #FBFAF8; border: 1px solid #EEF0F3; border-radius: .8rem; padding: .7rem; text-align: center; }
.kpi b { display: block; font-size: 1.3rem; color: #B26B00; } .kpi span { font-size: .68rem; color: #98A2B3; }
.org-mock-bars { display: flex; align-items: flex-end; gap: .4rem; height: 70px; padding: 0 .3rem; }
.org-mock-bars i { flex: 1; background: linear-gradient(180deg, #FBBF24, #F59E0B); border-radius: .25rem .25rem 0 0; }
.org-mock-rows { margin-top: .8rem; display: flex; flex-direction: column; gap: .4rem; }
.org-mock-rows span { height: .55rem; background: #F1F3F6; border-radius: 999px; } .org-mock-rows span:nth-child(2){ width: 80%; } .org-mock-rows span:nth-child(3){ width: 60%; }
/* Sections */
.org-section { padding: 4rem 0; }
.org-alt { background: #fff; }
.org-head { text-align: center; max-width: 640px; margin: 0 auto 2.5rem; }
.org-head h2 { font-size: clamp(1.6rem, 3.4vw, 2.3rem); font-weight: 800; margin: 1rem 0 .6rem; letter-spacing: -.02em; }
.org-head p { color: #57534E; font-size: 1.02rem; }
.org-two, .org-two-b { display: grid; grid-template-columns: 1fr; gap: 1.2rem; align-items: center; }
@media (min-width: 860px) { .org-two { grid-template-columns: 1fr 1fr; } .org-two-b { grid-template-columns: .9fr 1.1fr; } }
.org-card { border-radius: 1.3rem; padding: 1.8rem; }
.org-card h3 { font-size: 1.1rem; font-weight: 800; margin: 0 0 1rem; }
.org-card ul { margin: 0; padding-left: 1.1rem; line-height: 1.7; }
.org-card.bad { background: #FBEEE8; border: 1px solid #F0D3C6; color: #7c3a24; }
.org-card.good { background: #EAF6EC; border: 1px solid #CDE8D2; color: #1f5130; }
.org-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px,1fr)); gap: 1rem; }
.org-mod { background: #FBFAF8; border: 1px solid #ECE7E0; border-radius: 1.2rem; padding: 1.5rem; }
.org-alt .org-mod { background: #FBFAF8; }
.org-mod-ic { width: 2.6rem; height: 2.6rem; border-radius: .8rem; background: #FDF4E3; color: #B26B00; display: flex; align-items: center; justify-content: center; margin-bottom: 1rem; }
.org-mod-ic svg { width: 1.4rem; height: 1.4rem; }
.org-mod h4 { font-size: 1rem; font-weight: 800; margin: 0 0 .4rem; }
.org-mod p { font-size: .88rem; color: #57534E; line-height: 1.5; margin: 0; }
.org-p { color: #44403C; font-size: 1.05rem; line-height: 1.7; margin: 1rem 0 1.6rem; }
/* Mockup membres */
.org-mock2 { background: #fff; border: 1px solid #ECE7E0; border-radius: 1.3rem; padding: 1rem; box-shadow: 0 20px 40px -28px rgba(0,0,0,.3); display: flex; flex-direction: column; gap: .7rem; }
.mem { display: flex; align-items: center; gap: .7rem; background: #FBFAF8; border: 1px solid #EEF0F3; border-radius: .9rem; padding: .7rem; }
.mem .av { width: 2rem; height: 2rem; border-radius: 50%; background: linear-gradient(135deg,#FBBF24,#F59E0B); color: #fff; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: .8rem; }
.mem b { font-size: .85rem; } .mem small { color: #98A2B3; font-size: .72rem; }
.mem .tag { margin-left: auto; font-size: .62rem; font-weight: 800; text-transform: uppercase; padding: .15rem .5rem; border-radius: 999px; }
.tag.on { background: #D1FAE5; color: #059669; } .tag.off { background: #F1F3F6; color: #98A2B3; }
/* Plans */
.org-plans { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px,1fr)); gap: 1rem; }
.org-plan { position: relative; background: #FBFAF8; border: 1px solid #ECE7E0; border-radius: 1.3rem; padding: 1.7rem 1.4rem; text-align: center; }
.org-plan.hot { border-color: #F59E0B; box-shadow: 0 18px 40px -22px rgba(245,158,11,.5); background: #fff; }
.org-plan-badge { position: absolute; top: -.6rem; left: 50%; transform: translateX(-50%); background: linear-gradient(135deg,#FBBF24,#F59E0B); color: #fff; font-size: .6rem; font-weight: 800; text-transform: uppercase; letter-spacing: .06em; padding: .25rem .7rem; border-radius: 999px; }
.org-plan h4 { font-size: 1.2rem; font-weight: 800; margin: 0 0 .5rem; }
.org-plan-mem { color: #57534E; font-size: .88rem; margin: 0 0 .3rem; }
.org-plan-gold { color: #B26B00; font-weight: 800; font-size: .95rem; margin: 0 0 1.2rem; }
.org-plan-cta { display: block; background: #1C1917; color: #fff; padding: .7rem; border-radius: .7rem; text-decoration: none; font-weight: 700; }
.org-plan.hot .org-plan-cta { background: linear-gradient(135deg,#FBBF24,#F59E0B); color: #1a1206; }
/* CTA final */
.org-cta-final { background: linear-gradient(160deg, #17130D, #241b10); color: #fff; padding: 4.5rem 0; text-align: center; }
.org-cta-final h2 { font-size: clamp(1.8rem,3.6vw,2.5rem); font-weight: 800; margin: 0 0 .6rem; }
.org-cta-final p { color: #D6CFC4; margin: 0 0 1.6rem; }
.org-btn-light { background: #fff; color: #1C1917; font-weight: 800; padding: 1rem 1.8rem; border-radius: .8rem; text-decoration: none; }
</style>
