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
</script>

<template>
  <div class="page-wrapper feature-page">
    <LandingNav />
    <main class="feature-main">
      <div class="feature-hero">
        <div class="feature-container">
          <span class="feature-pill">Coaching Autonome</span>
          <h1 class="feature-h1">Votre mentor carrière IA, disponible 24h/24</h1>
          <p class="feature-lead">
            Un CV générique ne passe plus les algorithmes de filtrage. Laissez notre IA analyser vos expériences, extraire votre potentiel caché et générer des candidatures taillées sur mesure pour chaque poste visé.
          </p>
          <div class="feature-hero-cta">
            <router-link to="/register" class="btn-primary">Essayer le Mentor IA</router-link>
          </div>
        </div>
      </div>

      <section class="feature-content-section">
        <div class="feature-container feature-grid">
          <div class="feature-text-content">
            <h2>Pourquoi avez-vous besoin d'un Mentor IA ?</h2>
            <p>
              Rédiger un CV percutant et une lettre de motivation unique pour chaque candidature demande un temps considérable. Pourtant, face aux logiciels ATS (Applicant Tracking Systems) utilisés par plus de 90% des grandes entreprises, la personnalisation sémantique est devenue une nécessité absolue. Le <strong>Mentor IA</strong> de GoldArmy résout cette équation en automatisant l'optimisation de votre profil.
            </p>

            <h2>Les fonctionnalités de votre Coach Carrière</h2>
            <ul>
              <li><strong>Audit CV Instantané :</strong> L'IA passe au crible la structure de votre PDF, identifie les failles de lisibilité et vérifie la densité de vos mots-clés par rapport aux standards de l'industrie.</li>
              <li><strong>Réécriture Orientée Impact :</strong> Notre modèle linguistique transforme de simples descriptions de tâches en réalisations quantifiables orientées résultats (méthode de type Harvard/STAR).</li>
              <li><strong>Génération Contextuelle :</strong> En un clic, le Mentor analyse la description d'une offre d'emploi ciblée et produit une lettre d'accompagnement percutante qui met en avant vos atouts les plus pertinents.</li>
            </ul>

            <h2>Un accompagnement tout au long de votre carrière</h2>
            <p>
              Au-delà de la simple correction de documents, le Mentor IA vous aide à identifier les compétences manquantes sur votre profil pour atteindre les postes de niveau supérieur. Il vous suggère des formations clés et des projets personnels stratégiques pour combler l'écart entre votre poste actuel et vos ambitions.
            </p>
          </div>

          <aside class="feature-sidebar">
            <div class="sidebar-card">
              <h3>Prêt à optimiser votre profil ?</h3>
              <p>Découvrez instantanément les failles invisibles qui bloquent vos candidatures.</p>
              <router-link to="/free-cv-roast" class="btn-sidebar">Faire un Audit CV Gratuit</router-link>
            </div>
            <div class="sidebar-links">
              <h4>Autres outils IA</h4>
              <router-link to="/sniper-search">Découvrir le Sniper Search →</router-link>
              <router-link to="/simulation-entretien">Simulateur d'entretien vocal →</router-link>
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
