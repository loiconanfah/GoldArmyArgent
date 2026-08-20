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
</script>

<template>
  <div class="page-wrapper feature-page">
    <LandingNav />
    <main class="feature-main">
      <div class="feature-hero">
        <div class="feature-container">
          <span class="feature-pill">Mentorat à la demande</span>
          <h1 class="feature-h1">Un mentor carrière, quand tu en as besoin</h1>
          <p class="feature-lead">Fini de chercher « quelqu'un qui pourrait t'aider ». Le Hub Mentors est un véritable marketplace : trouve un mentor, choisis un service, réserve — et progresse.</p>
          <div class="feature-hero-cta"><router-link to="/register" class="btn-primary">Découvrir les mentors</router-link></div>
        </div>
      </div>
      <section class="feature-content-section">
        <div class="feature-container feature-grid">
          <div class="feature-text-content">
            <h2>Comment ça marche</h2>
            <p>Le Hub Mentors met en relation les candidats et des mentors inscrits. Chaque mentor affiche ses <strong>spécialités</strong>, ses <strong>disponibilités</strong>, sa note et son tarif. Tu envoies une demande de session ciblée, le mentor accepte, et tu obtiens un accompagnement concret.</p>
            <h2>Les services proposés</h2>
            <ul>
              <li><strong>Revue de CV :</strong> un regard expert sur ton dossier et son adéquation au poste.</li>
              <li><strong>Simulation d'entretien :</strong> t'entraîner en conditions réelles avec un pro.</li>
              <li><strong>Conseil carrière & reconversion :</strong> clarifier ton cap et tes prochaines étapes.</li>
              <li><strong>Négociation salariale :</strong> aborder l'offre avec les bons arguments.</li>
            </ul>
            <h2>Deviens mentor à ton tour</h2>
            <p>Registre ouvert : n'importe quel membre peut publier un profil de mentor (photo, expertises, disponibilités, liens), recevoir des demandes et gérer sa boîte de réservations. Les avis après session construisent ta réputation.</p>
          </div>
          <aside class="feature-sidebar">
            <div class="sidebar-card">
              <h3>Prêt à te faire accompagner ?</h3>
              <p>Trouve un mentor aligné sur ton objectif dès aujourd'hui.</p>
              <router-link to="/register" class="btn-sidebar">Ouvrir le Hub Mentors</router-link>
            </div>
            <div class="sidebar-links">
              <h4>Autres modules</h4>
              <router-link to="/communaute-goldarmy">La Communauté →</router-link>
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
.feature-hero { background: #17130D; color: #fff; padding: 5rem 0 4rem; text-align: center; }
.feature-pill { background: rgba(245,158,11,0.18); color: #F5B301; padding: 0.4rem 1rem; border-radius: 999px; font-size: 0.8rem; font-weight: 800; text-transform: uppercase; letter-spacing: .1em; }
.feature-h1 { font-size: clamp(2rem, 4vw, 3.3rem); font-weight: 800; margin: 1.5rem 0 1rem; line-height: 1.15; }
.feature-lead { font-size: 1.15rem; color: #D6CFC4; max-width: 720px; margin: 0 auto 2rem; line-height: 1.6; }
.btn-primary { background: linear-gradient(135deg, #FBBF24, #F59E0B); color: #1a1206; font-weight: 800; padding: 1rem 2rem; border-radius: 0.7rem; text-decoration: none; display: inline-block; box-shadow: 0 12px 28px -10px rgba(245,158,11,0.6); }
.feature-content-section { padding: 4rem 0; }
.feature-grid { display: grid; grid-template-columns: 1fr; gap: 3rem; }
@media(min-width: 900px){ .feature-grid { grid-template-columns: 2fr 1fr; } }
.feature-text-content h2 { font-size: 1.7rem; font-weight: 800; color: #0f172a; margin: 2.5rem 0 1rem; border-bottom: 2px solid #F59E0B; padding-bottom: 0.5rem; }
.feature-text-content h2:first-of-type { margin-top: 0; }
.feature-text-content p { font-size: 1.05rem; line-height: 1.75; margin-bottom: 1.25rem; color: #334155; }
.feature-text-content ul { margin: 1.25rem 0; padding-left: 1.5rem; line-height: 1.7; color: #334155; }
.feature-text-content li { margin-bottom: 0.75rem; }
.sidebar-card { background: #fff; border: 1px solid #e2e8f0; padding: 1.5rem; border-radius: 0.9rem; box-shadow: 0 4px 15px rgba(0,0,0,0.05); margin-bottom: 2rem; text-align: center; }
.sidebar-card h3 { margin: 0 0 .5rem; }
.btn-sidebar { background: #B45309; color: #fff; display: block; padding: 0.75rem; border-radius: 0.5rem; text-decoration: none; font-weight: 700; margin-top: 1rem; }
.sidebar-links h4 { font-size: 1rem; color: #0f172a; margin-bottom: 1rem; }
.sidebar-links a { display: block; color: #B45309; text-decoration: none; margin-bottom: 0.75rem; font-weight: 600; }
.sidebar-links a:hover { text-decoration: underline; }
</style>
