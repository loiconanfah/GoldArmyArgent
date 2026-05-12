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
            'acceptedAnswer': { '@type': 'Answer', 'text': 'Oui, notre formule Freemium à 0 € vous permet de tester nos outils essentiels, d\'effectuer un audit de CV IA gratuit et de lancer un agent actif en simultané sans carte bancaire.' }
          },
          {
            '@type': 'Question',
            'name': 'Qu\'apporte la formule Essential recommandée ?',
            'acceptedAnswer': { '@type': 'Answer', 'text': 'Le forfait Essential à 9,99 €/mois débloque 3 Agents actifs en simultané, les recherches et audits étendus, ainsi que le suivi CRM intelligent.' }
          },
          {
            '@type': 'Question',
            'name': 'À qui s\'adresse la formule Pro IA ?',
            'acceptedAnswer': { '@type': 'Answer', 'text': 'La formule Pro IA à 19,99 €/mois s\'adresse aux candidats voulant une puissance illimitée, incluant des agents illimités, un autopilotage complet du sourcing et l\'option d\'auto-hébergement.' }
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
    <main class="pricing-main dark-secondary">
      
      <!-- HERO SECTION TARIFS -->
      <div class="pricing-hero">
        <div class="pricing-container">
          <span class="pricing-pill">Investissement Transparent</span>
          <h1 class="pricing-h1">Déployez votre armée d'Agents IA</h1>
          <p class="pricing-lead">
            Choisissez la puissance de frappe adaptée à vos ambitions. Démarrez gratuitement et passez à la vitesse supérieure pour automatiser entièrement votre recherche d'emploi et dominer votre marché.
          </p>
        </div>
      </div>

      <!-- GRILLE DES FORFAITS -->
      <section class="pricing-grid-section">
        <div class="pricing-container pricing-cards">
          
          <!-- FORFAIT FREEMIUM -->
          <div class="pricing-card card--freemium">
            <div class="card-header">
              <span class="plan-type-badge">Découverte</span>
              <h2>Freemium</h2>
              <p class="price">0 €<span class="period">/mois</span></p>
              <p class="desc">Idéal pour auditer votre profil et découvrir l'écosystème.</p>
            </div>
            
            <ul class="features-list">
              <li><span class="bullet">✓</span> <strong>1 Agent actif</strong> en simultané</li>
              <li><span class="bullet">✓</span> Audit de CV IA gratuit</li>
              <li><span class="bullet">✓</span> Accès aux outils de base</li>
              <li><span class="bullet">✓</span> Hébergement sécurisé</li>
            </ul>
            
            <div class="card-cta">
              <router-link to="/register" class="btn-cta btn--freemium">Commencer gratuitement</router-link>
              <span class="subtext">Sans carte bancaire</span>
            </div>
          </div>

          <!-- FORFAIT ESSENTIAL (RECOMMANDÉ) -->
          <div class="pricing-card card--essential popular">
            <div class="badge-popular">👑 Recommandé</div>
            <div class="card-header">
              <span class="plan-type-badge accent">Accélération</span>
              <h2>Essential</h2>
              <p class="price">9,99 €<span class="period">/mois</span></p>
              <p class="desc">Pour les candidats actifs ciblant une transition rapide.</p>
            </div>
            
            <ul class="features-list">
              <li><span class="bullet accent">✓</span> <strong>3 Agents actifs</strong> en simultané</li>
              <li><span class="bullet accent">✓</span> Recherches et audits étendus</li>
              <li><span class="bullet accent">✓</span> Suivi CRM intelligent</li>
              <li><span class="bullet accent">✓</span> Support prioritaire</li>
            </ul>
            
            <div class="card-cta">
              <router-link to="/register" class="btn-cta btn--essential">Débloquer Essential</router-link>
              <span class="subtext accent-sub">Essai gratuit disponible</span>
            </div>
          </div>

          <!-- FORFAIT PRO IA -->
          <div class="pricing-card card--pro">
            <div class="card-header">
              <span class="plan-type-badge premium">Domination</span>
              <h2>Pro IA</h2>
              <p class="price">19,99 €<span class="period">/mois</span></p>
              <p class="desc">Puissance illimitée pour dominer le marché et le réseau.</p>
            </div>
            
            <ul class="features-list">
              <li><span class="bullet premium-bullet">✓</span> <strong>Agents illimités</strong></li>
              <li><span class="bullet premium-bullet">✓</span> Autopilotage complet du sourcing</li>
              <li><span class="bullet premium-bullet">✓</span> Système de prospection réseau</li>
              <li><span class="bullet premium-bullet">✓</span> Option d'auto-hébergement (Self-hosted)</li>
            </ul>
            
            <div class="card-cta">
              <router-link to="/register" class="btn-cta btn--pro">Passer au niveau Pro</router-link>
              <span class="subtext">Garantie de satisfaction</span>
            </div>
          </div>

        </div>
      </section>

      <!-- FAQ TARIFS -->
      <section class="pricing-faq-section">
        <div class="pricing-container">
          <h2 class="faq-h2">Questions Fréquentes sur nos Formules</h2>
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
              <summary>Qu'est-ce que l'option d'auto-hébergement (Self-hosted) ?</summary>
              <p>Disponible dans la formule Pro IA, cette option vous permet de connecter vos propres clés d'API (OpenAI, Anthropic, Gemini) ou vos modèles en local pour un contrôle total des coûts et de la confidentialité de vos données de sourcing.</p>
            </details>
          </div>
        </div>
      </section>

    </main>
    <Footer />
  </div>
</template>

<style scoped>
/* COHÉRENCE GLOBALE GOLDARMY : Thème sombre et finitions dorées */
.pricing-page { background-color: #0b0b0e; color: #cbd5e1; font-family: sans-serif; }
.pricing-container { max-width: 1200px; margin: 0 auto; padding: 0 1.5rem; }

/* HERO */
.pricing-hero { padding: 6rem 0 3rem; text-align: center; background: radial-gradient(circle at 50% 100%, rgba(255, 111, 0, 0.08) 0%, transparent 60%); }
.pricing-pill { background: rgba(255, 111, 0, 0.12); color: #ff8c42; padding: 0.4rem 1.25rem; border-radius: 999px; font-size: 0.75rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.15em; border: 1px solid rgba(255, 111, 0, 0.2); }
.pricing-h1 { font-size: clamp(2.25rem, 5vw, 4rem); font-weight: 900; color: #ffffff; margin: 1.5rem 0 1.25rem; letter-spacing: -0.03em; line-height: 1.1; }
.pricing-lead { font-size: 1.15rem; color: #94a3b8; max-width: 750px; margin: 0 auto; line-height: 1.6; }

/* GRILLE */
.pricing-grid-section { padding-bottom: 6rem; }
.pricing-cards { display: grid; grid-template-columns: 1fr; gap: 2rem; align-items: stretch; margin-top: 2rem; }
@media (min-width: 850px) { .pricing-cards { grid-template-columns: repeat(3, 1fr); } }

/* CARTES DE FORFAITS (Glassmorphism Premium) */
.pricing-card {
  background: rgba(20, 20, 28, 0.6);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 1.25rem;
  padding: 2.5rem 2rem;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  box-shadow: 0 10px 30px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,255,255,0.05);
  position: relative;
  transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1), border-color 0.3s, box-shadow 0.3s;
}
.pricing-card:hover { transform: translateY(-8px); border-color: rgba(255, 255, 255, 0.2); }

/* FORFAIT ESSENTIAL SUR-MIS EN VALEUR */
.card--essential.popular {
  background: linear-gradient(165deg, rgba(25, 25, 36, 0.8), rgba(15, 15, 22, 0.95));
  border: 2px solid #ff6f00;
  box-shadow: 0 20px 50px rgba(255, 111, 0, 0.2), inset 0 1px 0 rgba(255,255,255,0.1);
  z-index: 10;
}
.card--essential.popular:hover { border-color: #ff8c42; box-shadow: 0 25px 60px rgba(255, 111, 0, 0.3); }

/* FORFAIT PRO */
.card--pro { background: rgba(12, 12, 18, 0.8); }

/* BADGES ET EN-TÊTES */
.badge-popular {
  position: absolute;
  top: -14px;
  left: 50%;
  transform: translateX(-50%);
  background: linear-gradient(135deg, #ff9a5c, #ff6f00);
  color: #000;
  font-size: 0.75rem;
  font-weight: 900;
  text-transform: uppercase;
  padding: 0.35rem 1.25rem;
  border-radius: 999px;
  letter-spacing: 0.1em;
  box-shadow: 0 4px 15px rgba(255, 111, 0, 0.4);
}
.plan-type-badge { font-size: 0.7rem; font-weight: 700; text-transform: uppercase; color: #94a3b8; letter-spacing: 0.1em; display: block; margin-bottom: 0.5rem; }
.plan-type-badge.accent { color: #ff8c42; font-weight: 800; }
.plan-type-badge.premium { color: #38bdf8; }

.card-header h2 { font-size: 1.75rem; font-weight: 800; color: #ffffff; margin: 0 0 0.75rem; letter-spacing: -0.02em; }
.price { font-size: 3rem; font-weight: 900; color: #ffffff; margin: 0 0 0.5rem; line-height: 1; }
.period { font-size: 1rem; font-weight: 500; color: #64748b; }
.desc { font-size: 0.9rem; color: #94a3b8; margin: 0 0 2rem; line-height: 1.5; height: 2.7rem; }

/* LISTE DE FONCTIONNALITÉS */
.features-list { list-style: none; padding: 0; margin: 0 0 2.5rem; flex-grow: 1; border-top: 1px solid rgba(255,255,255,0.06); padding-top: 1.5rem; }
.features-list li { padding: 0.75rem 0; font-size: 0.95rem; color: #e2e8f0; display: flex; align-items: flex-start; gap: 0.5rem; }
.bullet { color: #64748b; font-weight: bold; flex-shrink: 0; }
.bullet.accent { color: #ff6f00; }
.premium-bullet { color: #38bdf8; }
.features-list strong { color: #ffffff; }

/* CALL TO ACTIONS */
.card-cta { text-align: center; }
.btn-cta {
  display: block;
  width: 100%;
  padding: 1rem;
  border-radius: 0.5rem;
  font-size: 1rem;
  font-weight: 800;
  text-decoration: none;
  text-align: center;
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
  box-sizing: border-box;
}

/* Bouton Gratuit */
.btn--freemium { background: rgba(255, 255, 255, 0.05); color: #ffffff; border: 1px solid rgba(255, 255, 255, 0.1); }
.btn--freemium:hover { background: rgba(255, 255, 255, 0.1); border-color: rgba(255, 255, 255, 0.2); }

/* Bouton Essential */
.btn--essential { background: linear-gradient(135deg, #ff9a5c, #ff6f00); color: #000000; box-shadow: 0 8px 20px rgba(255, 111, 0, 0.3); }
.btn--essential:hover { transform: translateY(-2px); box-shadow: 0 12px 25px rgba(255, 111, 0, 0.45); }

/* Bouton Pro */
.btn--pro { background: #ffffff; color: #0f172a; box-shadow: 0 8px 20px rgba(255, 255, 255, 0.15); }
.btn--pro:hover { background: #f8fafc; box-shadow: 0 12px 25px rgba(255, 255, 255, 0.25); }

.subtext { display: block; font-size: 0.75rem; color: #64748b; margin-top: 0.6rem; font-weight: 600; }
.subtext.accent-sub { color: #ff8c42; }

/* SECTION FAQ */
.pricing-faq-section { background: linear-gradient(180deg, #0b0b0e 0%, #121218 100%); padding: 5rem 0; border-top: 1px solid rgba(255,255,255,0.05); }
.faq-h2 { font-size: 2rem; font-weight: 800; color: #ffffff; text-align: center; margin-bottom: 3rem; letter-spacing: -0.02em; }
.faq-list { max-width: 850px; margin: 0 auto; display: flex; flex-direction: column; gap: 1rem; }
.faq-item { background: rgba(255, 255, 255, 0.02); border: 1px solid rgba(255, 255, 255, 0.06); border-radius: 0.75rem; padding: 1.25rem 1.5rem; transition: border-color 0.2s; }
.faq-item:hover { border-color: rgba(255, 111, 0, 0.2); }
.faq-item summary { font-weight: 700; font-size: 1.05rem; cursor: pointer; color: #ffffff; outline: none; display: flex; justify-content: space-between; align-items: center; }
.faq-item p { margin: 1rem 0 0; color: #94a3b8; line-height: 1.6; font-size: 0.95rem; }
</style>
