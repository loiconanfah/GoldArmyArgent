<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useHead } from '@unhead/vue'
import LandingNav from '@/components/LandingNav.vue'
import Footer from '@/components/Footer.vue'

const { t } = useI18n()
const BASE = 'https://www.goldarmyai.com'

useHead({
  title: computed(() => t('seo.tarifs.title')),
  meta: [
    { name: 'description', content: computed(() => t('seo.tarifs.description')) },
    { name: 'robots', content: 'index, follow' },
    { property: 'og:type', content: 'website' },
    { property: 'og:title', content: computed(() => t('seo.tarifs.title')) },
    { property: 'og:description', content: computed(() => t('seo.tarifs.description')) },
    { property: 'og:url', content: `${BASE}/tarifs` },
    { property: 'og:image', content: `${BASE}/og-banner.png` },
    { property: 'og:site_name', content: 'GoldArmy AI' },
    { property: 'og:locale', content: 'fr_FR' },
    { name: 'twitter:card', content: 'summary_large_image' },
    { name: 'twitter:title', content: computed(() => t('seo.tarifs.title')) },
    { name: 'twitter:description', content: computed(() => t('seo.tarifs.description')) },
    { name: 'twitter:image', content: `${BASE}/og-banner.png` }
  ],
  link: [
    { rel: 'canonical', href: `${BASE}/tarifs` }
  ],
  script: [
    {
      type: 'application/ld+json',
      innerHTML: JSON.stringify({
        '@context': 'https://schema.org',
        '@type': 'FAQPage',
        'mainEntity': [
          {
            '@type': 'Question',
            'name': 'Puis-je utiliser GoldArmy AI gratuitement ?',
            'acceptedAnswer': { '@type': 'Answer', 'text': 'Oui, notre formule Freemium vous permet de tester nos outils essentiels, d\'effectuer un audit de CV et de lancer vos premières recherches sans engagement ni carte bancaire.' }
          },
          {
            '@type': 'Question',
            'name': 'Qu\'apporte la formule payante par rapport à la version gratuite ?',
            'acceptedAnswer': { '@type': 'Answer', 'text': 'Les forfaits payants débloquent l\'accès illimité au Sniper Search (recherche automatisée en continu), la gestion complète du CRM de candidatures et le système de prospection réseau avancé.' }
          },
          {
            '@type': 'Question',
            'name': 'L\'abonnement est-il sans engagement ?',
            'acceptedAnswer': { '@type': 'Answer', 'text': 'Absolument. Vous pouvez modifier ou résilier votre abonnement à tout moment en un clic depuis les paramètres de votre compte.' }
          }
        ]
      })
    }
  ]
})
</script>

<template>
  <div class="page-wrapper pricing-page">
    <LandingNav />
    <main class="pricing-main">
      <div class="pricing-hero">
        <div class="pricing-container">
          <span class="pricing-pill">Investissement Transparent</span>
          <h1 class="pricing-h1">Tarifs GoldArmy AI — Gratuit et Premium</h1>
          <p class="pricing-lead">
            Choisissez la puissance de frappe adaptée à vos ambitions. Démarrez gratuitement et passez à la vitesse supérieure pour automatiser entièrement votre recherche d'emploi.
          </p>
        </div>
      </div>

      <section class="pricing-grid-section">
        <div class="pricing-container pricing-cards">
          <!-- Carte Gratuit -->
          <div class="pricing-card">
            <div class="card-header">
              <h2>Freemium</h2>
              <p class="price">0 €<span>/mois</span></p>
              <p class="desc">Idéal pour auditer votre profil et découvrir l'écosystème.</p>
            </div>
            <ul class="features-list">
              <li>✓ <strong>1 Agent actif</strong> en simultané</li>
              <li>✓ Audit de CV IA gratuit</li>
              <li>✓ Accès aux outils de base</li>
              <li>✓ Hébergement sécurisé</li>
            </ul>
            <div class="card-cta">
              <router-link to="/register" class="btn-secondary">Commencer gratuitement</router-link>
              <span class="subtext">Sans carte bancaire</span>
            </div>
          </div>

          <!-- Carte Essential -->
          <div class="pricing-card popular">
            <div class="badge-popular">Recommandé</div>
            <div class="card-header">
              <h2>Essential</h2>
              <p class="price">9,99 €<span>/mois</span></p>
              <p class="desc">Pour les candidats actifs ciblant une transition rapide.</p>
            </div>
            <ul class="features-list">
              <li>✓ <strong>3 Agents actifs</strong> en simultané</li>
              <li>✓ Recherches et audits étendus</li>
              <li>✓ Suivi CRM intelligent</li>
              <li>✓ Support prioritaire</li>
            </ul>
            <div class="card-cta">
              <router-link to="/register" class="btn-primary">Débloquer Essential</router-link>
              <span class="subtext">Essai gratuit disponible</span>
            </div>
          </div>

          <!-- Carte Pro -->
          <div class="pricing-card premium">
            <div class="card-header">
              <h2>Pro IA</h2>
              <p class="price">19,99 €<span>/mois</span></p>
              <p class="desc">Puissance illimitée pour dominer le marché et le réseau.</p>
            </div>
            <ul class="features-list">
              <li>✓ <strong>Agents illimités</strong></li>
              <li>✓ Autopilotage complet du sourcing</li>
              <li>✓ Système de prospection réseau</li>
              <li>✓ Option d'auto-hébergement (Self-hosted)</li>
            </ul>
            <div class="card-cta">
              <router-link to="/register" class="btn-premium">Passer au niveau Pro</router-link>
              <span class="subtext">Garantie de satisfaction</span>
            </div>
          </div>
        </div>
      </section>

      <section class="pricing-faq-section">
        <div class="pricing-container">
          <h2 class="faq-h2">Questions Fréquentes sur nos Abonnements</h2>
          <div class="faq-list">
            <details class="faq-item">
              <summary>Puis-je changer de forfait en cours de route ?</summary>
              <p>Oui, vous pouvez faire évoluer votre abonnement vers une formule supérieure ou inférieure à tout moment. L'ajustement tarifaire est calculé au prorata.</p>
            </details>
            <details class="faq-item">
              <summary>Quelles sont les méthodes de paiement acceptées ?</summary>
              <p>Nous acceptons l'ensemble des cartes de crédit et de débit majeures (Visa, Mastercard, American Express) via notre partenaire de paiement sécurisé Stripe.</p>
            </details>
            <details class="faq-item">
              <summary>Proposez-vous des licences pour les écoles ou les entreprises ?</summary>
              <p>Absolument. Notre offre Enterprise permet de déployer l'arsenal GoldArmy AI à grande échelle pour les centres de carrière et les équipes de reclassement. Contactez notre support pour un devis personnalisé.</p>
            </details>
          </div>
        </div>
      </section>
    </main>
    <Footer />
  </div>
</template>

<style scoped>
.pricing-page { background: #f8fafc; color: #0f172a; }
.pricing-container { max-width: 1150px; margin: 0 auto; padding: 0 1.5rem; }
.pricing-hero { background: #0f172a; color: #fff; padding: 5rem 0 3rem; text-align: center; }
.pricing-pill { background: rgba(255,111,0,0.2); color: #ff9a5c; padding: 0.4rem 1rem; border-radius: 999px; font-size: 0.8rem; font-weight: 700; text-transform: uppercase; }
.pricing-h1 { font-size: clamp(2rem, 4vw, 3.5rem); font-weight: 800; margin: 1.5rem 0 1rem; line-height: 1.15; }
.pricing-lead { font-size: 1.2rem; color: #cbd5e1; max-width: 750px; margin: 0 auto; line-height: 1.6; }
.pricing-grid-section { padding: 4rem 0; margin-top: -2rem; }
.pricing-cards { display: grid; grid-template-columns: 1fr; gap: 2rem; align-items: stretch; }
@media(min-width: 850px){ .pricing-cards { grid-template-columns: repeat(3, 1fr); } }
.pricing-card { background: #fff; border: 1px solid #e2e8f0; border-radius: 1rem; padding: 2.5rem 2rem; display: flex; flex-direction: column; justify-content: space-between; box-shadow: 0 4px 20px rgba(0,0,0,0.05); position: relative; transition: transform 0.2s; }
.pricing-card:hover { transform: translateY(-5px); }
.popular { border-color: #ff6f00; box-shadow: 0 10px 30px rgba(255,111,0,0.15); z-index: 1; }
.premium { background: #0f172a; color: #fff; border-color: #0f172a; }
.premium .card-header h2, .premium .price, .premium .desc, .premium .features-list { color: #fff; }
.premium .features-list li { border-bottom-color: rgba(255,255,255,0.1); }
.badge-popular { position: absolute; top: -12px; left: 50%; transform: translateX(-50%); background: #ff6f00; color: #fff; font-size: 0.75rem; font-weight: 800; text-transform: uppercase; padding: 0.25rem 1rem; border-radius: 999px; letter-spacing: 0.05em; }
.card-header h2 { font-size: 1.4rem; font-weight: 800; margin: 0 0 0.5rem; color: #0f172a; }
.price { font-size: 2.5rem; font-weight: 900; margin: 0 0 0.5rem; color: #0f172a; }
.price span { font-size: 1rem; font-weight: 500; color: #64748b; }
.desc { font-size: 0.9rem; color: #64748b; margin: 0 0 2rem; line-height: 1.5; }
.features-list { list-style: none; padding: 0; margin: 0 0 2.5rem; flex-grow: 1; }
.features-list li { padding: 0.8rem 0; border-bottom: 1px solid #f1f5f9; font-size: 0.95rem; color: #334155; }
.features-list li:last-child { border-bottom: none; }
.card-cta { text-align: center; }
.btn-primary, .btn-secondary, .btn-premium { display: block; width: 100%; padding: 0.85rem; border-radius: 0.5rem; font-weight: 700; text-decoration: none; text-align: center; transition: opacity 0.2s; box-sizing: border-box; }
.btn-primary { background: #ff6f00; color: #fff; box-shadow: 0 4px 15px rgba(255,111,0,0.3); }
.btn-secondary { background: #f1f5f9; color: #0f172a; }
.btn-secondary:hover { background: #e2e8f0; }
.btn-premium { background: #fff; color: #0f172a; }
.btn-premium:hover { background: #f8fafc; }
.subtext { display: block; font-size: 0.75rem; color: #94a3b8; margin-top: 0.5rem; }
.pricing-faq-section { background: #f1f5f9; padding: 4rem 0; border-top: 1px solid #e2e8f0; }
.faq-h2 { font-size: 2rem; font-weight: 800; text-align: center; margin-bottom: 2rem; }
.faq-list { max-width: 800px; margin: 0 auto; }
.faq-item { background: #fff; border: 1px solid #e2e8f0; margin-bottom: 1rem; border-radius: 0.5rem; padding: 1rem; }
.faq-item summary { font-weight: 700; font-size: 1.1rem; cursor: pointer; color: #0f172a; }
.faq-item p { margin: 0.75rem 0 0; color: #475569; line-height: 1.6; }
</style>
