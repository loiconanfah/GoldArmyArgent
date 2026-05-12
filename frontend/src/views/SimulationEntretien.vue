<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useHead } from '@unhead/vue'
import LandingNav from '@/components/LandingNav.vue'
import Footer from '@/components/Footer.vue'

const { t } = useI18n()
const BASE = 'https://www.goldarmyai.com'

useHead({
  title: computed(() => t('seo.simulation_entretien.title')),
  meta: [
    { name: 'description', content: computed(() => t('seo.simulation_entretien.description')) },
    { name: 'robots', content: 'index, follow' },
    { property: 'og:type', content: 'website' },
    { property: 'og:title', content: computed(() => t('seo.simulation_entretien.title')) },
    { property: 'og:description', content: computed(() => t('seo.simulation_entretien.description')) },
    { property: 'og:url', content: `${BASE}/simulation-entretien` },
    { property: 'og:image', content: `${BASE}/og-banner.png` },
    { property: 'og:site_name', content: 'GoldArmy AI' },
    { property: 'og:locale', content: 'fr_FR' },
    { name: 'twitter:card', content: 'summary_large_image' },
    { name: 'twitter:title', content: computed(() => t('seo.simulation_entretien.title')) },
    { name: 'twitter:description', content: computed(() => t('seo.simulation_entretien.description')) },
    { name: 'twitter:image', content: `${BASE}/og-banner.png` }
  ],
  link: [
    { rel: 'canonical', href: `${BASE}/simulation-entretien` }
  ],
  script: [
    {
      type: 'application/ld+json',
      innerHTML: JSON.stringify({
        '@context': 'https://schema.org',
        '@type': 'SoftwareApplication',
        'name': 'Simulateur d\'Entretien Vocal IA par GoldArmy AI',
        'url': `${BASE}/simulation-entretien`,
        'applicationCategory': 'TrainingApplication',
        'operatingSystem': 'Web',
        'description': 'Simulateur d\'entretien d\'embauche vocal qui permet aux candidats de s\'entraîner en conditions réelles face à un recruteur IA avec débriefing instantané.',
        'offers': { '@type': 'Offer', 'price': '0', 'priceCurrency': 'EUR' }
      })
    }
  ]
})
</script>

<template>
  <div class="page-wrapper feature-page">
    <LandingNav />
    <main class="feature-main">
      <div class="feature-hero">
        <div class="feature-container">
          <span class="feature-pill">Entraînement Intensif</span>
          <h1 class="feature-h1">Simulez votre entretien d'embauche avec l'IA</h1>
          <p class="feature-lead">
            Ne découvrez pas vos points faibles face à un vrai recruteur. Entraînez-vous à l'oral en conditions réelles avec notre IA vocale exigeante et apprenez à maîtriser votre stress.
          </p>
          <div class="feature-hero-cta">
            <router-link to="/free-interview" class="btn-primary">Lancer un faux entretien visio</router-link>
          </div>
        </div>
      </div>

      <section class="feature-content-section">
        <div class="feature-container feature-grid">
          <div class="feature-text-content">
            <h2>L'entraînement est la clé du succès</h2>
            <p>
              Un excellent CV vous permet d'obtenir un entretien, mais c'est votre performance orale qui détermine si vous recevez une offre. Répondre de manière fluide, structurée et convaincante sous la pression d'un évaluateur nécessite de la pratique. La <strong>Simulation d'Entretien IA</strong> de GoldArmy vous offre un environnement sécurisé pour répéter jusqu'à l'excellence.
            </p>

            <h2>Comment fonctionne le Recruteur IA ?</h2>
            <p>
              Notre système exploite les technologies vocales avancées (Web Speech API) couplées à des modèles de langage de pointe pour créer des interactions dynamiques et réalistes :
            </p>
            <ul>
              <li><strong>Personnalisation Métier :</strong> Indiquez le titre du poste ciblé. L'IA génère des questions techniques, situationnelles et comportementales spécifiques à votre domaine.</li>
              <li><strong>Analyse Sémantique en Temps Réel :</strong> L'algorithme évalue la clarté de vos arguments, la précision de votre vocabulaire technique et la pertinence de vos exemples.</li>
              <li><strong>Débriefing Sans Concession :</strong> À l'issue de l'échange, vous recevez un rapport d'analyse critique identifiant vos tics de langage, vos hésitations et les points théoriques à approfondir.</li>
            </ul>

            <h2>Transformez l'anxiété en assurance</h2>
            <p>
              La répétition désensibilise au stress. En effectuant plusieurs sessions d'entraînement face à notre Lead Tech ou RH IA, vous développez des automatismes de réponse qui vous permettront d'aborder vos vrais entretiens avec une confiance inébranlable.
            </p>
          </div>

          <aside class="feature-sidebar">
            <div class="sidebar-card">
              <h3>Testez gratuitement</h3>
              <p>Évaluez vos compétences à l'oral dès maintenant sans inscription.</p>
              <router-link to="/free-interview" class="btn-sidebar">Démarrer la simulation</router-link>
            </div>
            <div class="sidebar-links">
              <h4>Découvrir l'écosystème</h4>
              <router-link to="/crm-emploi">Gestionnaire de candidatures →</router-link>
              <router-link to="/mentor-ia">Optimisation de CV IA →</router-link>
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
.feature-pill { background: rgba(255,111,0,0.2); color: #ff9a5c; padding: 0.4rem 1rem; border-radius: 999px; font-size: 0.8rem; font-weight: 700; text-transform: uppercase; }
.feature-h1 { font-size: clamp(2rem, 4vw, 3.5rem); font-weight: 800; margin: 1.5rem 0 1rem; line-height: 1.15; }
.feature-lead { font-size: 1.2rem; color: #cbd5e1; max-width: 750px; margin: 0 auto 2rem; line-height: 1.6; }
.btn-primary { background: linear-gradient(135deg, #ff9a5c, #ff6f00); color: #000; font-weight: 700; padding: 1rem 2rem; border-radius: 0.5rem; text-decoration: none; display: inline-block; box-shadow: 0 4px 20px rgba(255,111,0,0.4); }
.feature-content-section { padding: 4rem 0; }
.feature-grid { display: grid; grid-template-columns: 1fr; gap: 3rem; }
@media(min-width: 900px){ .feature-grid { grid-template-columns: 2fr 1fr; } }
.feature-text-content h2 { font-size: 1.8rem; font-weight: 800; color: #0f172a; margin: 2.5rem 0 1rem; border-bottom: 2px solid #ff6f00; padding-bottom: 0.5rem; }
.feature-text-content h2:first-of-type { margin-top: 0; }
.feature-text-content p { font-size: 1.05rem; line-height: 1.75; margin-bottom: 1.25rem; color: #334155; }
.feature-text-content ul { margin: 1.25rem 0; padding-left: 1.5rem; line-height: 1.7; color: #334155; }
.feature-text-content li { margin-bottom: 0.75rem; }
.sidebar-card { background: #fff; border: 1px solid #e2e8f0; padding: 1.5rem; border-radius: 0.75rem; box-shadow: 0 4px 15px rgba(0,0,0,0.05); margin-bottom: 2rem; text-align: center; }
.btn-sidebar { background: #ea580c; color: #fff; display: block; padding: 0.75rem; border-radius: 0.5rem; text-decoration: none; font-weight: 600; margin-top: 1rem; }
.sidebar-links h4 { font-size: 1rem; color: #0f172a; margin-bottom: 1rem; }
.sidebar-links a { display: block; color: #ea580c; text-decoration: none; margin-bottom: 0.75rem; font-weight: 500; }
.sidebar-links a:hover { text-decoration: underline; }
</style>
