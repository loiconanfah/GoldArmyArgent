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
const packs = [
  { name: 'Découverte', gold: '100 Gold', price: '4,99 €', badge: '' },
  { name: 'Populaire', gold: '300 + 20 Gold', price: '12,99 €', badge: 'Meilleur' },
  { name: 'Pro', gold: '750 + 100 Gold', price: '24,99 €', badge: '' },
  { name: 'Méga', gold: '2000 + 400 Gold', price: '59,99 €', badge: '' }
]
</script>

<template>
  <div class="page-wrapper feature-page">
    <LandingNav />
    <main class="feature-main">
      <div class="feature-hero">
        <div class="feature-container">
          <span class="feature-pill">Économie Gold</span>
          <h1 class="feature-h1">Payez seulement ce que vous utilisez</h1>
          <p class="feature-lead">Le Gold est la monnaie de GoldArmy. Pas d'abonnement obligatoire : vous recevez du Gold gratuit chaque mois, et vous rechargez à volonté selon vos besoins.</p>
          <div class="feature-hero-cta"><router-link to="/register" class="btn-primary">Commencer avec 50 Gold offerts</router-link></div>
        </div>
      </div>
      <section class="feature-content-section">
        <div class="feature-container">
          <div class="feature-text-content" style="max-width:820px;margin:0 auto;">
            <h2>Comment fonctionne le Gold</h2>
            <ul>
              <li><strong>50 Gold offerts</strong> dès l'inscription, pour tout essayer.</li>
              <li><strong>100 Gold gratuits chaque mois</strong>, renouvelés automatiquement.</li>
              <li><strong>Rechargeable</strong> à tout moment via la Boutique — vous n'êtes jamais bloqué.</li>
              <li><strong>Le Gold ne périme jamais.</strong> Ce que vous avez reste à vous.</li>
            </ul>
            <h2>Chaque fonctionnalité a son coût, clairement</h2>
            <p>Le Gold se dépense à l'usage : recherche Sniper, audit CV, adaptation à une offre, simulation d'entretien, relance… Vous voyez le coût avant d'agir, et votre solde est toujours affiché en haut de l'application. Pas de surprise, pas de facturation cachée.</p>
            <h2>Les abonnements, en option</h2>
            <p>Deux forfaits légers débloquent des modules et créditent plus de Gold chaque mois : <strong>Essentiel</strong> (200 Gold/mois + espace Réseau) et <strong>Pro</strong> (500 Gold/mois + Portfolio et fonctions avancées). Mais rien n'est obligatoire : le mode « à l'usage » suffit pour la plupart.</p>
          </div>

          <div class="gold-packs">
            <div v-for="p in packs" :key="p.name" :class="['gold-pack', { hot: p.badge }]">
              <span v-if="p.badge" class="gold-badge">{{ p.badge }}</span>
              <h4>{{ p.name }}</h4>
              <p class="gold-amount">{{ p.gold }}</p>
              <p class="gold-price">{{ p.price }}</p>
              <router-link to="/register" class="gold-cta">Obtenir</router-link>
            </div>
          </div>
        </div>
      </section>
    </main>
    <Footer />
  </div>
</template>

<style scoped>
.feature-page { background: #f8fafc; color: #0f172a; }
.feature-container { max-width: 1100px; margin: 0 auto; padding: 0 1.5rem; }
.feature-hero { background: #0f172a; color: #fff; padding: 5rem 0 4rem; text-align: center; }
.feature-pill { background: rgba(255,111,0,0.18); color: #ff9a5c; padding: 0.4rem 1rem; border-radius: 999px; font-size: 0.8rem; font-weight: 800; text-transform: uppercase; letter-spacing: .1em; }
.feature-h1 { font-size: clamp(2rem, 4vw, 3.3rem); font-weight: 800; margin: 1.5rem 0 1rem; line-height: 1.15; }
.feature-lead { font-size: 1.15rem; color: #cbd5e1; max-width: 720px; margin: 0 auto 2rem; line-height: 1.6; }
.btn-primary { background: linear-gradient(135deg, #ff9a5c, #ff6f00); color: #000000; font-weight: 800; padding: 1rem 2rem; border-radius: 0.7rem; text-decoration: none; display: inline-block; box-shadow: 0 12px 28px -10px rgba(255,111,0,0.6); }
.feature-content-section { padding: 4rem 0; }
.feature-text-content h2 { font-size: 1.7rem; font-weight: 800; color: #0f172a; margin: 2.5rem 0 1rem; border-bottom: 2px solid #ff6f00; padding-bottom: 0.5rem; }
.feature-text-content h2:first-of-type { margin-top: 0; }
.feature-text-content p { font-size: 1.05rem; line-height: 1.75; margin-bottom: 1.25rem; color: #334155; }
.feature-text-content ul { margin: 1.25rem 0; padding-left: 1.5rem; line-height: 1.8; color: #334155; }
.gold-packs { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px,1fr)); gap: 1rem; max-width: 900px; margin: 3rem auto 0; }
.gold-pack { position: relative; background: #fff; border: 1px solid #e2e8f0; border-radius: 1.2rem; padding: 1.6rem 1.2rem; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.04); }
.gold-pack.hot { border-color: #ff6f00; box-shadow: 0 18px 40px -22px rgba(255,111,0,.5); }
.gold-badge { position: absolute; top: -.6rem; left: 50%; transform: translateX(-50%); background: linear-gradient(135deg,#ff9a5c,#ff6f00); color: #fff; font-size: .6rem; font-weight: 800; text-transform: uppercase; letter-spacing: .06em; padding: .25rem .7rem; border-radius: 999px; }
.gold-pack h4 { font-size: 1.15rem; font-weight: 800; margin: 0 0 .4rem; }
.gold-amount { color: #ea580c; font-weight: 800; margin: 0 0 .2rem; }
.gold-price { color: #64748b; font-size: 1.1rem; font-weight: 700; margin: 0 0 1.1rem; }
.gold-cta { display: block; background: #0f172a; color: #fff; padding: .7rem; border-radius: .6rem; text-decoration: none; font-weight: 700; }
.gold-pack.hot .gold-cta { background: linear-gradient(135deg,#ff9a5c,#ff6f00); color: #000000; }
</style>
