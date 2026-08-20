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
</script>

<template>
  <div class="page-wrapper feature-page">
    <LandingNav />
    <main class="feature-main">
      <div class="feature-hero">
        <div class="feature-container">
          <span class="feature-pill">Communauté</span>
          <h1 class="feature-h1">Chercher un emploi, mais pas tout seul</h1>
          <p class="feature-lead">Un espace d'entraide type Discord pour les membres d'une même organisation : on partage, on s'entraide, on progresse ensemble.</p>
          <div class="feature-hero-cta"><router-link to="/register" class="btn-primary">Rejoindre une communauté</router-link></div>
        </div>
      </div>
      <section class="feature-content-section">
        <div class="feature-container feature-grid">
          <div class="feature-text-content">
            <h2>Des salons pour tout partager</h2>
            <p>La Communauté s'organise en salons thématiques, à la manière d'un Discord : discussion générale, <strong>modèles de CV</strong>, <strong>portfolios</strong>, <strong>offres d'emploi</strong> et <strong>résultats de simulation d'entretien</strong>. Chaque publication peut être likée et commentée.</p>
            <h2>Le partage de CV avec score ATS</h2>
            <p>Un membre peut déposer un modèle de CV : le système en calcule le <strong>score ATS</strong> et l'affiche à côté de l'aperçu, pour que la cohorte s'inspire des meilleurs formats — pas des pires.</p>
            <h2>Réservée à ton organisation</h2>
            <p>La Communauté est privée à ton organisation : seuls les membres rattachés y accèdent. C'est l'endroit où la dynamique de groupe accélère l'insertion de chacun.</p>
          </div>
          <aside class="feature-sidebar">
            <div class="sidebar-card">
              <h3>Tu fais partie d'une organisation ?</h3>
              <p>Rejoins ta communauté et profite de l'entraide de ta cohorte.</p>
              <router-link to="/register" class="btn-sidebar">Créer mon compte</router-link>
            </div>
            <div class="sidebar-links">
              <h4>Autres modules</h4>
              <router-link to="/mentorat-a-la-demande">Le Hub Mentors →</router-link>
              <router-link to="/pour-les-organisations">Espace Organisation →</router-link>
            </div>
          </aside>
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
.feature-grid { display: grid; grid-template-columns: 1fr; gap: 3rem; }
@media(min-width: 900px){ .feature-grid { grid-template-columns: 2fr 1fr; } }
.feature-text-content h2 { font-size: 1.7rem; font-weight: 800; color: #0f172a; margin: 2.5rem 0 1rem; border-bottom: 2px solid #ff6f00; padding-bottom: 0.5rem; }
.feature-text-content h2:first-of-type { margin-top: 0; }
.feature-text-content p { font-size: 1.05rem; line-height: 1.75; margin-bottom: 1.25rem; color: #334155; }
.sidebar-card { background: #fff; border: 1px solid #e2e8f0; padding: 1.5rem; border-radius: 0.9rem; box-shadow: 0 4px 15px rgba(0,0,0,0.05); margin-bottom: 2rem; text-align: center; }
.sidebar-card h3 { margin: 0 0 .5rem; }
.btn-sidebar { background: #ea580c; color: #fff; display: block; padding: 0.75rem; border-radius: 0.5rem; text-decoration: none; font-weight: 700; margin-top: 1rem; }
.sidebar-links h4 { font-size: 1rem; color: #0f172a; margin-bottom: 1rem; }
.sidebar-links a { display: block; color: #ea580c; text-decoration: none; margin-bottom: 0.75rem; font-weight: 600; }
.sidebar-links a:hover { text-decoration: underline; }
</style>
