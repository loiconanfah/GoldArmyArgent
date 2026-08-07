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
    { property: 'og:site_name', content: 'GoldArmy AI' }
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
            'name': 'Que comprend le plan Gratuit de GoldArmy ?',
            'acceptedAnswer': { '@type': 'Answer', 'text': 'Le plan Gratuit inclut 2 recherches Sniper par jour, 5 audits de CV au total, 1 entretien RH vocal, 10 relances automatiques, 5 adaptations de CV, 2 lettres de motivation et la relance anti-fantôme.' }
          },
          {
            '@type': 'Question',
            'name': 'Quels sont les avantages du forfait Essentiel conseillé ?',
            'acceptedAnswer': { '@type': 'Answer', 'text': 'Pour 9,99 €/mois, l\'Essentiel offre les recherches Sniper illimitées, les audits CV ATS, les entretiens RH illimités, l\'accès au Headhunter, le carnet d\'adresses et le Portfolio IA personnalisé.' }
          },
          {
            '@type': 'Question',
            'name': 'Pourquoi choisir le plan Pro pour l\'élite ?',
            'acceptedAnswer': { '@type': 'Answer', 'text': 'À 19,99 €/mois, le plan Pro débloque la puissance maximale pour dominer votre secteur avec l\'ensemble des outils en illimité et des accès prioritaires aux serveurs IA.' }
          }
        ]
      })
    }
  ]
})
</script>

<template>
  <div class="page-wrapper pricing-page-light">
    <LandingNav />
    <main class="pricing-main-light">
      
      <!-- HERO SECTION TARIFS CLAIRS -->
      <div class="pricing-hero-light">
        <div class="pricing-container">
          <span class="pricing-pill-light">Choisir un plan</span>
          <h1 class="pricing-h1-light">Montez en puissance selon vos ambitions professionnelles</h1>
          <p class="pricing-lead-light">
            Débloquez l'arsenal complet des agents autonomes GoldArmy pour automatiser vos candidatures, vos relances et dominer votre secteur.
          </p>
        </div>
      </div>

      <!-- GRILLE DES FORFAITS (Thème Clair Épuré) -->
      <section class="pricing-grid-light">
        <div class="pricing-container pricing-cards-light">
          
          <!-- FORFAIT GRATUIT -->
          <div class="pricing-card-light card--free">
            <div class="card-header-light">
              <h2>Gratuit</h2>
              <p class="tagline-light">Pour débuter votre conquête.</p>
              <p class="price-light">0 €<span class="period-light">/mois</span></p>
            </div>
            
            <div class="features-wrapper">
              <p class="features-title">Inclus dans votre plan :</p>
              <ul class="features-list-light">
                <li><span class="check">✓</span> <strong>50 Gold</strong> offerts à l'inscription</li>
                <li><span class="check">✓</span> <strong>+100 Gold</strong> gratuits chaque mois</li>
                <li><span class="check">✓</span> Rechargez à volonté via la <strong>Boutique</strong></li>
                <li><span class="check">✓</span> Recherches Sniper, audits, adaptations…</li>
                <li><span class="check">✓</span> Le Gold ne périme pas</li>

                <!-- Réservé aux abonnements -->
                <li class="disabled"><span class="cross">✗</span> Accès à l'espace Réseau (Essentiel)</li>
                <li class="disabled"><span class="cross">✗</span> Portfolio IA &amp; fonctions avancées (Pro)</li>
              </ul>
            </div>

            <div class="card-cta-light">
              <router-link to="/boutique" class="btn-light-outline">Ouvrir la Boutique</router-link>
              <span class="subtext-light">Sans abonnement, payez à l'usage</span>
            </div>
          </div>

          <!-- FORFAIT ESSENTIEL (CONSEILLÉ) -->
          <div class="pricing-card-light card--essential popular-light">
            <div class="badge-popular-light">👑 Le choix des vainqueurs (Conseillé)</div>
            
            <div class="card-header-light">
              <h2>Essentiel</h2>
              <p class="tagline-light">Accélération et visibilité maximale.</p>
              <p class="price-light">9,99 €<span class="period-light">/mois</span></p>
            </div>
            
            <div class="features-wrapper">
              <p class="features-title accent">Tokens mensuels + Réseau :</p>
              <ul class="features-list-light">
                <li><span class="check accent">✓</span> <strong>200 Gold</strong> crédités chaque mois</li>
                <li><span class="check accent">✓</span> Accès à l'<strong>espace Réseau</strong> (Headhunter, carnet)</li>
                <li><span class="check accent">✓</span> Recherches Sniper, adaptations CV, entretiens…</li>
                <li><span class="check accent">✓</span> Relances &amp; lettres de motivation</li>
                <li><span class="check accent">✓</span> Achat de Gold en Boutique quand vous voulez</li>
                <li class="disabled"><span class="cross">✗</span> Portfolio IA &amp; fonctions avancées (Pro)</li>
              </ul>
            </div>

            <div class="card-cta-light">
              <router-link to="/register" class="btn-light-accent">Choisir Essentiel</router-link>
              <span class="subtext-light accent-sub">9,99 € / mois • Sans engagement</span>
            </div>
          </div>

          <!-- FORFAIT PRO -->
          <div class="pricing-card-light card--pro">
            <div class="card-header-light">
              <h2>Pro</h2>
              <p class="tagline-light">Le maximum de tokens et de puissance.</p>
              <p class="price-light">19,99 €<span class="period-light">/mois</span></p>
            </div>

            <div class="features-wrapper">
              <p class="features-title pro">Tout Essentiel, décuplé :</p>
              <ul class="features-list-light">
                <li><span class="check pro">✓</span> <strong>500 Gold</strong> crédités chaque mois</li>
                <li><span class="check pro">✓</span> <strong>Portfolio IA / Gold Profile</strong> débloqué</li>
                <li><span class="check pro">✓</span> Candidature automatique &amp; Sourcing matinal</li>
                <li><span class="check pro">✓</span> Module Post-Interview</li>
                <li><span class="check pro">✓</span> Tout l'espace Réseau (Essentiel inclus)</li>
                <li><span class="check pro">✓</span> Achat de Gold en Boutique à volonté</li>
              </ul>
            </div>

            <div class="card-cta-light">
              <router-link to="/register" class="btn-light-pro">Choisir Pro</router-link>
              <span class="subtext-light">19,99 € / mois • Fonctions avancées</span>
            </div>
          </div>

        </div>
      </section>

      <!-- FAQ TARIFS CLAIRS -->
      <section class="pricing-faq-light">
        <div class="pricing-container">
          <h2 class="faq-h2-light">Questions Fréquentes sur nos Formules</h2>
          <div class="faq-list-light">
            <details class="faq-item-light">
              <summary>Comment fonctionne la limite quotidienne des recherches Sniper ?</summary>
              <p>En compte Gratuit, votre quota de 2 recherches se réinitialise chaque nuit à minuit. En passant à l'Essentiel ou au Pro, le moteur scanne le web en continu sans aucune restriction d'usage.</p>
            </details>
            <details class="faq-item-light">
              <summary>Puis-je annuler ou modifier mon forfait à tout moment ?</summary>
              <p>Absolument. La gestion de votre abonnement se fait en un clic depuis les paramètres de votre tableau de bord. Aucun préavis n'est requis.</p>
            </details>
            <details class="faq-item-light">
              <summary>Qu'est-ce que le Portfolio IA personnalisé de l'offre Essentiel ?</summary>
              <p>C'est une vitrine web générée automatiquement par nos agents sur la base de votre CV et de vos réalisations. Elle est optimisée pour séduire les recruteurs qui cliquent sur vos liens de relance.</p>
            </details>
          </div>
        </div>
      </section>

    </main>
    <Footer />
  </div>
</template>

<style scoped>
/* Rendu Global Thème Clair Premium */
.pricing-page-light { background-color: #f8fafc; color: #0f172a; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
.pricing-container { max-width: 1200px; margin: 0 auto; padding: 0 1.5rem; }

/* HERO SECTION CLAIRE */
.pricing-hero-light { padding: 5rem 0 3rem; text-align: center; background-color: #ffffff; border-bottom: 1px solid #e2e8f0; }
.pricing-pill-light { background-color: #fff7ed; color: #ea580c; padding: 0.35rem 1rem; border-radius: 999px; font-size: 0.75rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.1em; border: 1px solid #ffedd5; display: inline-block; margin-bottom: 1rem; }
.pricing-h1-light { font-size: clamp(2rem, 4vw, 3.25rem); font-weight: 800; color: #0f172a; margin: 0 0 1rem; letter-spacing: -0.02em; line-height: 1.15; }
.pricing-lead-light { font-size: 1.1rem; color: #475569; max-width: 700px; margin: 0 auto; line-height: 1.6; }

/* GRILLE DES FORFAITS */
.pricing-grid-light { padding: 4rem 0 6rem; background-color: #f8fafc; }
.pricing-cards-light { display: grid; grid-template-columns: 1fr; gap: 2rem; align-items: stretch; }
@media (min-width: 850px) { .pricing-cards-light { grid-template-columns: repeat(3, 1fr); } }

/* CARTES (Light Mode Design) */
.pricing-card-light {
  background: #ffffff;
  border: 1px solid #cbd5e1;
  border-radius: 1rem;
  padding: 2.5rem 2rem;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.03);
  position: relative;
  transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
}
.pricing-card-light:hover { transform: translateY(-5px); box-shadow: 0 12px 30px rgba(0, 0, 0, 0.08); border-color: #94a3b8; }

/* CARTE ESSENTIEL MISE EN AVANT */
.card--essential.popular-light {
  border: 2px solid #ea580c;
  box-shadow: 0 10px 35px rgba(234, 88, 12, 0.12);
  z-index: 10;
  background: #ffffff;
}
.card--essential.popular-light:hover { box-shadow: 0 15px 45px rgba(234, 88, 12, 0.18); border-color: #f97316; }

/* CARTE PRO */
.card--pro { background-color: #ffffff; border-color: #cbd5e1; }

/* BADGE POPULARITÉ */
.badge-popular-light {
  position: absolute;
  top: -14px;
  left: 50%;
  transform: translateX(-50%);
  background-color: #ea580c;
  color: #ffffff;
  font-size: 0.75rem;
  font-weight: 800;
  text-transform: uppercase;
  padding: 0.35rem 1.25rem;
  border-radius: 999px;
  letter-spacing: 0.05em;
  box-shadow: 0 4px 10px rgba(234, 88, 12, 0.25);
  white-space: nowrap;
}

/* EN-TÊTES DE CARTES */
.card-header-light { border-bottom: 1px solid #f1f5f9; padding-bottom: 1.5rem; margin-bottom: 1.5rem; text-align: left; }
.card-header-light h2 { font-size: 1.5rem; font-weight: 800; color: #0f172a; margin: 0 0 0.25rem; }
.tagline-light { font-size: 0.85rem; color: #64748b; margin: 0 0 1rem; min-height: 2.2rem; }
.price-light { font-size: 2.75rem; font-weight: 900; color: #0f172a; margin: 0; line-height: 1; }
.period-light { font-size: 0.9rem; font-weight: 500; color: #64748b; }

/* LISTE DE CARACTÉRISTIQUES */
.features-wrapper { flex-grow: 1; margin-bottom: 2rem; text-align: left; }
.features-title { font-size: 0.8rem; font-weight: 700; text-transform: uppercase; color: #64748b; letter-spacing: 0.05em; margin: 0 0 1rem; }
.features-title.accent { color: #ea580c; }
.features-title.pro { color: #0284c7; }

.features-list-light { list-style: none; padding: 0; margin: 0; }
.features-list-light li { padding: 0.6rem 0; font-size: 0.9rem; color: #334155; display: flex; align-items: center; gap: 0.5rem; border-bottom: 1px solid #f8fafc; }
.features-list-light li:last-child { border-bottom: none; }
.features-list-light li strong { color: #0f172a; font-weight: 700; }

.check { color: #10b981; font-weight: bold; flex-shrink: 0; font-size: 1rem; }
.check.accent { color: #ea580c; }
.check.pro { color: #0284c7; }

/* Puces inactives barrées */
.features-list-light li.disabled { color: #94a3b8; text-decoration: line-through; }
.cross { color: #cbd5e1; font-weight: bold; flex-shrink: 0; text-decoration: none; display: inline-block; }

/* CALL TO ACTIONS CLAIRS */
.card-cta-light { text-align: center; padding-top: 1rem; border-top: 1px solid #f1f5f9; }

.btn-light-outline, .btn-light-accent, .btn-light-pro {
  display: block;
  width: 100%;
  padding: 0.85rem;
  border-radius: 0.5rem;
  font-size: 0.95rem;
  font-weight: 700;
  text-decoration: none;
  text-align: center;
  transition: all 0.15s ease;
  box-sizing: border-box;
}

/* Bouton Rétrograder */
.btn-light-outline { background-color: #f1f5f9; color: #475569; border: 1px solid #e2e8f0; }
.btn-light-outline:hover { background-color: #e2e8f0; color: #0f172a; }

/* Bouton Essentiel */
.btn-light-accent { background-color: #ea580c; color: #ffffff; box-shadow: 0 4px 12px rgba(234, 88, 12, 0.25); }
.btn-light-accent:hover { background-color: #f97316; transform: translateY(-1px); box-shadow: 0 6px 15px rgba(234, 88, 12, 0.35); }

/* Bouton Pro */
.btn-light-pro { background-color: #0f172a; color: #ffffff; }
.btn-light-pro:hover { background-color: #1e293b; }

.subtext-light { display: block; font-size: 0.7rem; color: #94a3b8; margin-top: 0.5rem; font-weight: 500; }
.subtext-light.accent-sub { color: #ea580c; font-weight: 600; }

/* FAQ SECTION CLAIRE */
.pricing-faq-light { background-color: #ffffff; padding: 5rem 0; border-top: 1px solid #e2e8f0; }
.faq-h2-light { font-size: 1.85rem; font-weight: 800; color: #0f172a; text-align: center; margin-bottom: 2.5rem; letter-spacing: -0.02em; }
.faq-list-light { max-width: 800px; margin: 0 auto; display: flex; flex-direction: column; gap: 0.85rem; }
.faq-item-light { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 0.5rem; padding: 1.1rem 1.4rem; transition: background-color 0.2s; }
.faq-item-light:hover { background: #f1f5f9; }
.faq-item-light summary { font-weight: 700; font-size: 1rem; cursor: pointer; color: #0f172a; outline: none; }
.faq-item-light p { margin: 0.75rem 0 0; color: #475569; line-height: 1.55; font-size: 0.9rem; }
</style>
