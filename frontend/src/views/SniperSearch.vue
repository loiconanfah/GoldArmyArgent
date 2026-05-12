<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useHead } from '@unhead/vue'
import LandingNav from '@/components/LandingNav.vue'
import Footer from '@/components/Footer.vue'

const { t } = useI18n()
const BASE = 'https://www.goldarmyai.com'

useHead({
  title: computed(() => t('seo.sniper_search.title')),
  meta: [
    { name: 'description', content: computed(() => t('seo.sniper_search.description')) },
    { name: 'robots', content: 'index, follow' },
    { property: 'og:type', content: 'website' },
    { property: 'og:title', content: computed(() => t('seo.sniper_search.title')) },
    { property: 'og:description', content: computed(() => t('seo.sniper_search.description')) },
    { property: 'og:url', content: `${BASE}/sniper-search` },
    { property: 'og:image', content: `${BASE}/og-banner.png` },
    { property: 'og:site_name', content: 'GoldArmy AI' },
    { property: 'og:locale', content: 'fr_FR' },
    { name: 'twitter:card', content: 'summary_large_image' },
    { name: 'twitter:title', content: computed(() => t('seo.sniper_search.title')) },
    { name: 'twitter:description', content: computed(() => t('seo.sniper_search.description')) },
    { name: 'twitter:image', content: `${BASE}/og-banner.png` }
  ],
  link: [
    { rel: 'canonical', href: `${BASE}/sniper-search` }
  ],
  script: [
    {
      type: 'application/ld+json',
      innerHTML: JSON.stringify({
        '@context': 'https://schema.org',
        '@type': 'SoftwareApplication',
        'name': 'Sniper Search par GoldArmy AI',
        'url': `${BASE}/sniper-search`,
        'applicationCategory': 'BusinessApplication',
        'operatingSystem': 'Web',
        'description': 'Moteur de recherche d\'emploi propulsé par l\'IA qui détecte les offres cachées et non publiées sur 50+ sources.',
        'offers': { '@type': 'Offer', 'price': '0', 'priceCurrency': 'EUR' }
      })
    },
    {
      type: 'application/ld+json',
      innerHTML: JSON.stringify({
        '@context': 'https://schema.org',
        '@type': 'FAQPage',
        'mainEntity': [
          {
            '@type': 'Question',
            'name': 'Qu\'est-ce que le Sniper Search ?',
            'acceptedAnswer': { '@type': 'Answer', 'text': 'Le Sniper Search est un outil exclusif de GoldArmy AI qui explore le web en profondeur pour détecter les offres d\'emploi avant leur publication sur les job boards traditionnels.' }
          },
          {
            '@type': 'Question',
            'name': 'Combien de sources le Sniper Search analyse-t-il ?',
            'acceptedAnswer': { '@type': 'Answer', 'text': 'Le Sniper Search analyse simultanément plus de 50 sources, incluant les sites carrières d\'entreprises, les réseaux sociaux professionnels et les agrégateurs spécialisés.' }
          }
        ]
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
          <span class="feature-pill">Sourcing de précision</span>
          <h1 class="feature-h1">Sniper Search : trouvez les offres cachées grâce à l'IA</h1>
          <p class="feature-lead">
            Ne perdez plus votre temps sur des agrégateurs saturés où des centaines de candidats postulent aux mêmes annonces.
            Notre algorithme explore le web profond pour vous positionner en premier.
          </p>
          <div class="feature-hero-cta">
            <router-link to="/register" class="btn-primary">Lancer le Sniper Search gratuitement</router-link>
          </div>
        </div>
      </div>

      <section class="feature-content-section">
        <div class="feature-container feature-grid">
          <div class="feature-text-content">
            <h2>Qu'est-ce que le Sniper Search ?</h2>
            <p>
              Le marché de l'emploi actuel souffre d'une asymétrie d'information majeure. La plupart des opportunités de grande valeur sont pourvues avant même d'atteindre les plateformes publiques de recrutement. Le <strong>Sniper Search</strong> a été conçu par les ingénieurs de GoldArmy AI pour briser cette barrière.
            </p>
            <p>
              En combinant des techniques avancées de scraping en temps réel et un filtrage sémantique par intelligence artificielle, notre agent autonome cartographie en continu les pages carrières de milliers d'entreprises, les publications sur les réseaux sociaux et les forums spécialisés.
            </p>

            <h2>Comment fonctionne notre technologie de Sourcing IA ?</h2>
            <p>Le processus se déroule en trois étapes hautement automatisées :</p>
            <ul>
              <li><strong>Exploration Multi-Sources :</strong> L'agent interroge plus de 50 écosystèmes distincts pour capturer le signal brut des besoins en recrutement.</li>
              <li><strong>Scoring d'Affinité (Matching CV) :</strong> Chaque description de poste est instantanément comparée à votre profil et vos compétences techniques. Le système calcule un score de pertinence sur 100.</li>
              <li><strong>Alerte Instantanée :</strong> Dès qu'une opportunité franchit votre seuil de pertinence, elle est injectée dans votre tableau de bord avec des suggestions d'adaptation de CV.</li>
            </ul>

            <h2>Pourquoi cibler le marché caché de l'emploi ?</h2>
            <p>
              Les études statistiques montrent que près de 70% des postes ouverts ne font jamais l'objet d'une annonce publique d'envergure. En vous positionnant sur ce segment via le Sniper Search, vous réduisez drastiquement la concurrence directe. Vous n'êtes plus l'un des 500 CVs reçus par un logiciel ATS, mais le candidat qualifié qui arrive au moment précis où le besoin émerge.
            </p>
          </div>

          <aside class="feature-sidebar">
            <div class="sidebar-card">
              <h3>Pourquoi choisir GoldArmy AI ?</h3>
              <p>Rejoignez des milliers de candidats qui ont divisé par 10 leur temps de recherche d'emploi.</p>
              <ul class="sidebar-benefits">
                <li>✓ Accès aux offres non publiées</li>
                <li>✓ Recommandations de mots-clés ATS</li>
                <li>✓ Génération de lettres sur mesure</li>
              </ul>
              <router-link to="/register" class="btn-sidebar">Créer un compte</router-link>
            </div>
            <div class="sidebar-links">
              <h4>Continuer votre lecture</h4>
              <router-link to="/blog/ia-recherche-emploi-guide">Guide de la recherche d'emploi IA →</router-link>
              <router-link to="/mentor-ia">Découvrir le Mentor IA →</router-link>
            </div>
          </aside>
        </div>
      </section>

      <section class="feature-faq-section">
        <div class="feature-container">
          <h2 class="faq-h2">Questions fréquentes sur le Sniper Search</h2>
          <div class="faq-list">
            <details class="faq-item">
              <summary>Le Sniper Search fonctionne-t-il pour tous les secteurs ?</summary>
              <p>Oui, notre algorithme est agnostique. Il excelle particulièrement dans la Tech, la Finance, le Marketing et l'Ingénierie, où les entreprises publient fréquemment leurs besoins sur des canaux décentralisés.</p>
            </details>
            <details class="faq-item">
              <summary>Puis-je lier le Sniper Search à mon compte LinkedIn ?</summary>
              <p>Le système fonctionne de manière autonome en arrière-plan sans nécessiter de connexion risquée à vos profils sociaux personnels, garantissant la sécurité de vos comptes.</p>
            </details>
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
.sidebar-card { background: #fff; border: 1px solid #e2e8f0; padding: 1.5rem; border-radius: 0.75rem; box-shadow: 0 4px 15px rgba(0,0,0,0.05); margin-bottom: 2rem; }
.sidebar-benefits { list-style: none; padding: 0; margin: 1rem 0 1.5rem; font-size: 0.95rem; line-height: 1.8; color: #475569; }
.btn-sidebar { background: #0f172a; color: #fff; text-align: center; display: block; padding: 0.75rem; border-radius: 0.5rem; text-decoration: none; font-weight: 600; }
.sidebar-links h4 { font-size: 1rem; color: #0f172a; margin-bottom: 1rem; }
.sidebar-links a { display: block; color: #ea580c; text-decoration: none; margin-bottom: 0.75rem; font-weight: 500; }
.sidebar-links a:hover { text-decoration: underline; }
.feature-faq-section { background: #f1f5f9; padding: 4rem 0; border-top: 1px solid #e2e8f0; }
.faq-h2 { font-size: 2rem; font-weight: 800; text-align: center; margin-bottom: 2rem; }
.faq-list { max-width: 800px; margin: 0 auto; }
.faq-item { background: #fff; border: 1px solid #e2e8f0; margin-bottom: 1rem; border-radius: 0.5rem; padding: 1rem; }
.faq-item summary { font-weight: 700; font-size: 1.1rem; cursor: pointer; color: #0f172a; }
.faq-item p { margin: 0.75rem 0 0; color: #475569; line-height: 1.6; }
</style>
