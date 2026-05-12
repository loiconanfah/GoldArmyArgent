<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useHead } from '@unhead/vue'
import LandingNav from '@/components/LandingNav.vue'
import Footer from '@/components/Footer.vue'

const { t } = useI18n()
const BASE = 'https://www.goldarmyai.com'

useHead({
  title: computed(() => t('seo.crm_emploi.title')),
  meta: [
    { name: 'description', content: computed(() => t('seo.crm_emploi.description')) },
    { name: 'robots', content: 'index, follow' },
    { property: 'og:type', content: 'website' },
    { property: 'og:title', content: computed(() => t('seo.crm_emploi.title')) },
    { property: 'og:description', content: computed(() => t('seo.crm_emploi.description')) },
    { property: 'og:url', content: `${BASE}/crm-emploi` },
    { property: 'og:image', content: `${BASE}/og-banner.png` },
    { property: 'og:site_name', content: 'GoldArmy AI' },
    { property: 'og:locale', content: 'fr_FR' },
    { name: 'twitter:card', content: 'summary_large_image' },
    { name: 'twitter:title', content: computed(() => t('seo.crm_emploi.title')) },
    { name: 'twitter:description', content: computed(() => t('seo.crm_emploi.description')) },
    { name: 'twitter:image', content: `${BASE}/og-banner.png` }
  ],
  link: [
    { rel: 'canonical', href: `${BASE}/crm-emploi` }
  ],
  script: [
    {
      type: 'application/ld+json',
      innerHTML: JSON.stringify({
        '@context': 'https://schema.org',
        '@type': 'SoftwareApplication',
        'name': 'CRM Emploi IA par GoldArmy AI',
        'url': `${BASE}/crm-emploi`,
        'applicationCategory': 'BusinessApplication',
        'operatingSystem': 'Web',
        'description': 'Outil de gestion de candidatures (CRM) sous forme de tableau Kanban intelligent avec rappels de relance et suivi automatisé du pipeline de recherche d\'emploi.',
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
          <span class="feature-pill">Organisation &amp; Suivi</span>
          <h1 class="feature-h1">Organisez votre recherche d'emploi comme un commercial</h1>
          <p class="feature-lead">
            Ne perdez plus le fil de vos candidatures dispersées dans des feuilles de calcul. Suivez chaque opportunité sur un tableau Kanban intelligent, programmez des relances automatiques et maximisez vos taux de conversion.
          </p>
          <div class="feature-hero-cta">
            <router-link to="/register" class="btn-primary">Accéder au CRM gratuitement</router-link>
          </div>
        </div>
      </div>

      <section class="feature-content-section">
        <div class="feature-container feature-grid">
          <div class="feature-text-content">
            <h2>Gérez votre pipeline de recherche d'emploi</h2>
            <p>
              Rechercher un emploi est un processus de vente B2B où vous êtes à la fois le produit et le commercial. Pour réussir, une organisation rigoureuse est indispensable. Le <strong>CRM Emploi</strong> de GoldArmy centralise l'ensemble de votre activité pour vous offrir une visibilité totale sur votre progression.
            </p>

            <h2>Les avantages d'un suivi de candidatures centralisé</h2>
            <ul>
              <li><strong>Tableau Kanban Visuel :</strong> Suivez l'état d'avancement de chaque candidature (À postuler, Envoyée, Entretien, Offre) par simple glisser-déposer.</li>
              <li><strong>Gestionnaire de Relances Intelligentes :</strong> Les statistiques prouvent qu'un suivi actif augmente de 30% les retours positifs. L'IA vous notifie automatiquement lorsqu'une relance est pertinente et en rédige le brouillon.</li>
              <li><strong>Scoring Prédictif :</strong> L'algorithme évalue la probabilité de succès de chaque piste en fonction de l'adéquation de votre profil et de la réactivité des recruteurs.</li>
            </ul>

            <h2>Ne laissez plus aucune opportunité s'échapper</h2>
            <p>
              En éliminant la charge mentale liée au suivi manuel de dizaines de pistes simultanées, vous pouvez concentrer votre énergie sur la préparation de vos entretiens et le ciblage d'offres à forte valeur ajoutée.
            </p>
          </div>

          <aside class="feature-sidebar">
            <div class="sidebar-card">
              <h3>Créez votre espace candidat</h3>
              <p>Centralisez vos outils de recherche et vos documents en un seul endroit.</p>
              <router-link to="/register" class="btn-sidebar">Créer un compte</router-link>
            </div>
            <div class="sidebar-links">
              <h4>Parcourir les fonctionnalités</h4>
              <router-link to="/sniper-search">Détecteur d'offres cachées →</router-link>
              <router-link to="/mentor-ia">Générateur de lettres de motivation →</router-link>
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
