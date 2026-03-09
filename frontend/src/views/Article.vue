<script setup>
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useHead } from '@unhead/vue'
import { articles } from '@/data/articles'
import { ArrowLeftIcon, ArrowRightIcon, LinkIcon } from '@heroicons/vue/24/outline'
import LandingNav from '@/components/LandingNav.vue'
import Footer from '@/components/Footer.vue'

const { t, locale } = useI18n()
const route = useRoute()
const router = useRouter()

const article = computed(() => articles.find(a => a.id === route.params.id))

useHead({
  title: computed(() => article.value ? `${article.value.title} | GoldArmy Blog` : 'Blog | GoldArmy'),
  meta: [
    {
      name: 'description',
      content: computed(() => article.value?.description ?? t('seo.blog.description'))
    }
  ]
})

const scrollProgress = ref(0)

function handleScroll() {
  const windowHeight = window.innerHeight
  const documentHeight = document.documentElement.scrollHeight - windowHeight
  if (documentHeight <= 0) return
  scrollProgress.value = (window.scrollY / documentHeight) * 100
}

function copyLink() {
  navigator.clipboard.writeText(window.location.href)
  alert(t('blog.link_copied'))
}

function shareLinkedIn() {
  window.open(`https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(window.location.href)}`, '_blank')
}

function shareTwitter() {
  const url = encodeURIComponent(window.location.href)
  const text = encodeURIComponent(t('blog.share_text', { title: article.value?.title }))
  window.open(`https://twitter.com/intent/tweet?url=${url}&text=${text}`, '_blank')
}

function formatDate(dateStr) {
  return new Date(dateStr).toLocaleDateString(locale.value === 'fr' ? 'fr-FR' : 'en-US', {
    day: 'numeric',
    month: 'long',
    year: 'numeric'
  })
}

onMounted(() => {
  const link = document.createElement('link')
  link.rel = 'stylesheet'
  link.href = '/orvimo-landing.css'
  link.id = 'orvimo-landing-css'
  document.head.appendChild(link)
  document.documentElement.classList.add('w-mod-ix3')
  if (!article.value) {
    router.replace('/blog')
    return
  }
  window.addEventListener('scroll', handleScroll)
})

onUnmounted(() => {
  const link = document.getElementById('orvimo-landing-css')
  if (link) link.remove()
  document.documentElement.classList.remove('w-mod-ix3')
  window.removeEventListener('scroll', handleScroll)
})
</script>

<template>
  <div v-if="article" class="page-wrapper page-wrapper--article">
    <div class="article-progress" :style="{ width: `${scrollProgress}%` }"></div>

    <LandingNav />

    <main class="main article-main">
      <article class="article-content">
        <header class="article-header">
          <router-link to="/blog" class="article-back">
            <ArrowLeftIcon class="article-back__icon" />
            {{ t('blog.back_to_blog') }}
          </router-link>

          <div class="article-meta">
            <time :datetime="article.date">{{ formatDate(article.date) }}</time>
            <span class="article-meta__dot"></span>
            <span>{{ article.readTime }}</span>
          </div>

          <h1 class="article-title">{{ article.title }}</h1>
          <p class="article-lead">{{ article.description }}</p>
        </header>

        <div class="article-hero-image">
          <img :src="article.image" :alt="article.title" loading="eager" />
        </div>

        <div class="article-body-wrap">
          <div v-html="article.content" class="article-body"></div>

          <footer class="article-cta">
            <p class="article-cta__tagline">{{ t('blog.cta_tagline') }}</p>
            <h2 class="article-cta__title">{{ t('blog.cta_title') }}</h2>
            <p class="article-cta__subtitle">{{ t('blog.cta_subtitle') }}</p>
            <router-link to="/register" class="article-cta__btn">
              {{ t('blog.cta_button') }}
              <ArrowRightIcon class="article-cta__btn-icon" />
            </router-link>
            <p class="article-cta__footnote">{{ t('blog.cta_free_trial') }}</p>
          </footer>
        </div>
      </article>

      <aside class="article-share">
        <button type="button" class="article-share__btn" title="LinkedIn" @click="shareLinkedIn" aria-label="Partager sur LinkedIn">
          <svg class="article-share__icon" fill="currentColor" viewBox="0 0 24 24"><path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z"/></svg>
        </button>
        <a v-if="article.mediumUrl" :href="article.mediumUrl" target="_blank" rel="noopener noreferrer" class="article-share__btn" title="Lire sur Medium" aria-label="Lire l'article sur Medium">
          <svg class="article-share__icon" viewBox="0 0 24 24" fill="currentColor"><path d="M13.54 12a6.8 6.8 0 01-6.77 6.82A6.8 6.8 0 010 12a6.8 6.8 0 016.77-6.82A6.8 6.8 0 0113.54 12zM20.96 12c0 3.54-1.51 6.42-3.38 6.42-1.87 0-3.39-2.88-3.39-6.42s1.52-6.42 3.39-6.42 3.38 2.88 3.38 6.42M24 12c0 3.17-.53 5.75-1.19 5.75-.66 0-1.2-2.58-1.2-5.75s.54-5.75 1.2-5.75C23.47 6.25 24 8.83 24 12z"/></svg>
        </a>
        <a v-if="article.devToUrl" :href="article.devToUrl" target="_blank" rel="noopener noreferrer" class="article-share__btn" title="Lire sur DEV Community" aria-label="Lire l'article sur DEV.to">
          <svg class="article-share__icon" viewBox="0 0 24 24" fill="currentColor"><path d="M7.42 10.05c0-.2-.02-.4-.06-.6.6-.3 1.2-.5 1.9-.7.1 0 .1.2.1.3 0 .3 0 .6-.1.9-.6.2-1.2.4-1.8.6-.1.1-.2 0-.2-.2v-.5zM6.12 12c0 .4 0 .8.1 1.2.5.2 1 .4 1.6.5.1 0 .2.1.2.2v.6c0 .1-.1.2-.2.2-.7.2-1.4.4-2.1.5-.1 0-.2-.1-.2-.2v-2.8zm10.56 0c0 .5 0 1-.1 1.5-.5.2-1 .3-1.5.5-.1 0-.2 0-.2-.2v-.6c0-.1.1-.2.2-.2.6-.2 1.2-.4 1.8-.6.1-.3.1-.6.1-.9 0-.1-.1-.2-.2-.2-.6-.2-1.2-.4-1.8-.6-.1 0-.2.1-.2.2v.3zm-5.36 2.2c-.4 0-.7-.3-.7-.7s.3-.7.7-.7.7.3.7.7-.3.7-.7.7zM24 11.3V13c0 .5 0 1-.1 1.5-.6.2-1.2.4-1.8.6-.1 0-.2 0-.2-.2v-.6c0-.1.1-.2.2-.2.6-.2 1.2-.4 1.8-.6.1-.4.1-.8.1-1.2v-.4c0-.5 0-1 .1-1.5.5-.2 1-.4 1.5-.5.1 0 .2 0 .2.2v.6c0 .1-.1.2-.2.2-.6.2-1.2.4-1.8.6-.1.4-.1.8-.1 1.2v.2zm-2.4-2.4v.4c0 .4 0 .8.1 1.2-.5.2-1 .4-1.6.5-.1 0-.2 0-.2-.2v-.6c0-.1.1-.2.2-.2.6-.2 1.2-.4 1.8-.6-.1-.4-.1-.8-.1-1.2V9.2c0-.5 0-1 .1-1.5.6-.2 1.2-.4 1.8-.6.1 0 .2.1.2.2v.6c0 .1-.1.2-.2.2-.6.2-1.2.4-1.8.6-.1.3-.1.6-.1.9z"/></svg>
        </a>
        <button type="button" class="article-share__btn" title="X (Twitter)" @click="shareTwitter" aria-label="Partager sur X">
          <svg class="article-share__icon" fill="currentColor" viewBox="0 0 24 24"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>
        </button>
        <button type="button" class="article-share__btn" title="Copier le lien" @click="copyLink" aria-label="Copier le lien">
          <LinkIcon class="article-share__icon" />
        </button>
      </aside>
    </main>

    <Footer />
  </div>
</template>

<style scoped>
/* Blog article : fond clair, texte sombre (priorité maximale pour lisibilité) */
.page-wrapper--article {
  min-height: 100vh;
  overflow-x: clip;
  background-color: #f8fafc !important;
  color: #0f172a !important;
}
.page-wrapper--article :deep(.main) {
  padding-top: 0;
  padding-bottom: 0;
  background-color: #f8fafc !important;
}
.article-progress {
  position: fixed;
  top: 0;
  left: 0;
  height: 3px;
  background: linear-gradient(90deg, #ff6f00, #ff9a5c);
  z-index: 1001;
  transition: width 0.1s ease-out;
}
.article-content {
  max-width: 720px;
  margin: 0 auto;
  padding: 2rem 1.5rem 4rem;
}
.article-header {
  margin-bottom: 2.5rem;
}
.article-back {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.8125rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #475569 !important;
  text-decoration: none;
  margin-bottom: 1.5rem;
  transition: color 0.2s;
}
.article-back:hover {
  color: #ea580c !important;
}
.article-back__icon {
  width: 1rem;
  height: 1rem;
}
.article-meta {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: #ea580c !important;
  margin-bottom: 1rem;
}
.article-meta__dot {
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: #ff6f00 !important;
  opacity: 0.8;
}
.article-title {
  font-size: clamp(1.875rem, 4vw, 2.75rem);
  font-weight: 800;
  letter-spacing: -0.03em;
  line-height: 1.15;
  margin: 0 0 1rem;
  color: #0f172a !important;
}
.article-lead {
  font-size: 1.125rem;
  line-height: 1.6;
  color: #0f172a !important;
  margin: 0;
  padding-left: 1.25rem;
  border-left: 3px solid #ff6f00;
}
.article-hero-image {
  border-radius: var(--radius--s, 1rem);
  overflow: hidden;
  margin-bottom: 2.5rem;
  border: 1px solid #e2e8f0;
}
.article-hero-image img {
  width: 100%;
  height: auto;
  max-height: 420px;
  object-fit: cover;
  display: block;
}
.article-body-wrap {
  margin-bottom: 3rem;
}
.article-cta {
  margin-top: 3.5rem;
  padding-top: 2.5rem;
  border-top: 1px solid #e2e8f0;
  text-align: center;
  background: #f1f5f9 !important;
  border: 1px solid #e2e8f0;
  border-radius: var(--radius--s, 1rem);
  padding: 2rem 1.5rem;
}
.article-cta__tagline {
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  color: #ea580c !important;
  margin: 0 0 0.75rem;
}
.article-cta__title {
  font-size: 1.75rem;
  font-weight: 800;
  letter-spacing: -0.02em;
  margin: 0 0 0.75rem;
  color: #0f172a !important;
}
.article-cta__subtitle {
  font-size: 1rem;
  line-height: 1.6;
  color: #334155 !important;
  margin: 0 auto 1.5rem;
  max-width: 480px;
}
.article-cta__btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  font-size: 0.875rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #1f1f1f !important;
  background: linear-gradient(135deg, #ff9a5c, #ff6f00);
  border: none;
  border-radius: var(--radius--xs, 0.5rem);
  text-decoration: none;
  box-shadow: 0 4px 20px rgba(255, 111, 0, 0.35);
  transition: transform 0.2s, box-shadow 0.2s;
}
.article-cta__btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 28px rgba(255, 111, 0, 0.45);
}
.article-cta__btn-icon {
  width: 1.125rem;
  height: 1.125rem;
}
.article-cta__footnote {
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: #64748b !important;
  margin: 1rem 0 0;
}
.article-share {
  position: fixed;
  left: 1.25rem;
  top: 50%;
  transform: translateY(-50%);
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  z-index: 100;
}
@media (max-width: 1024px) {
  .article-share {
    display: none;
  }
}
.article-share__btn {
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f1f5f9 !important;
  border: 1px solid #e2e8f0;
  border-radius: var(--radius--xs, 0.5rem);
  color: #475569 !important;
  cursor: pointer;
  transition: color 0.2s, background 0.2s, border-color 0.2s;
  text-decoration: none;
}
.article-share__btn:hover {
  color: #ea580c !important;
  background: rgba(255, 111, 0, 0.1) !important;
  border-color: rgba(255, 111, 0, 0.3);
}
.article-share__icon {
  width: 1.25rem;
  height: 1.25rem;
}
</style>

<style>
/* Forcer thème clair sur la zone article */
.page-wrapper--article .article-main {
  background-color: #f8fafc !important;
  color: #0f172a !important;
}

/* Règle globale : tout le contenu de l'article en texte lisible (noir/slate foncé) */
.page-wrapper--article .article-body,
.page-wrapper--article .article-body :deep(*),
.page-wrapper--article .article-body :deep(div),
.page-wrapper--article .article-body :deep(p),
.page-wrapper--article .article-body :deep(span),
.page-wrapper--article .article-body :deep(li),
.page-wrapper--article .article-body :deep(em),
.page-wrapper--article .article-body :deep(h1),
.page-wrapper--article .article-body :deep(h2),
.page-wrapper--article .article-body :deep(h3),
.page-wrapper--article .article-body :deep(h4),
.page-wrapper--article .article-body :deep(h5),
.page-wrapper--article .article-body :deep(h6),
.page-wrapper--article .article-body :deep(strong),
.page-wrapper--article .article-body :deep(section),
.page-wrapper--article .article-body :deep(blockquote) {
  color: #0f172a !important;
}

/* Liens : accent orange */
.page-wrapper--article .article-body :deep(a) {
  color: #ea580c !important;
  text-decoration: underline;
  text-underline-offset: 3px;
}
.page-wrapper--article .article-body :deep(a:hover) {
  color: #c2410c !important;
}

/* Accents (indigo/gold/red dans le HTML → couleurs lisibles) */
.page-wrapper--article .article-body :deep(.text-indigo-400),
.page-wrapper--article .article-body :deep(.text-indigo-300),
.page-wrapper--article .article-body :deep(.text-indigo-200) {
  color: #ea580c !important;
}
.page-wrapper--article .article-body :deep(.text-gold-400),
.page-wrapper--article .article-body :deep(.text-gold-500) {
  color: #b45309 !important;
}
.page-wrapper--article .article-body :deep(.text-red-400) {
  color: #b91c1c !important;
}

/* Annuler TOUTES les classes texte clair (thème sombre) */
.page-wrapper--article .article-body :deep([class*="text-white"]),
.page-wrapper--article .article-body :deep([class*="text-gray"]),
.page-wrapper--article .article-body :deep([class*="text-slate-1"]),
.page-wrapper--article .article-body :deep([class*="text-slate-2"]),
.page-wrapper--article .article-body :deep([class*="text-slate-3"]),
.page-wrapper--article .article-body :deep([class*="text-slate-4"]),
.page-wrapper--article .article-body :deep(.prose-invert),
.page-wrapper--article .article-body :deep(.prose-invert *) {
  color: #0f172a !important;
}

/* Garder les liens en orange même avec classe text-indigo */
.page-wrapper--article .article-body :deep(a[class*="text-indigo"]),
.page-wrapper--article .article-body :deep(a[class*="hover:text-indigo"]) {
  color: #ea580c !important;
}

/* Typo : tailles et espacements */
.page-wrapper--article .article-body :deep(h2) {
  font-size: 1.75rem;
  font-weight: 800;
  letter-spacing: -0.02em;
  margin-top: 2.5rem;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid rgba(255, 111, 0, 0.4);
}
.page-wrapper--article .article-body :deep(h3) {
  font-size: 1.35rem;
  font-weight: 700;
  margin-top: 2rem;
  margin-bottom: 0.75rem;
}
.page-wrapper--article .article-body :deep(p) {
  font-size: 1.0625rem;
  line-height: 1.75;
  margin-bottom: 1.25rem;
}
.page-wrapper--article .article-body :deep(p:first-of-type) {
  font-size: 1.125rem;
}
.page-wrapper--article .article-body :deep(ul),
.page-wrapper--article .article-body :deep(ol) {
  margin: 1.25rem 0;
  padding-left: 1.5rem;
  line-height: 1.7;
}
.page-wrapper--article .article-body :deep(li) {
  margin-bottom: 0.5rem;
}
.page-wrapper--article .article-body :deep(li::marker) {
  color: #ff6f00 !important;
}
.page-wrapper--article .article-body :deep(img) {
  width: 100%;
  height: auto;
  border-radius: 12px;
  margin: 1.5rem 0;
  border: 1px solid #e2e8f0;
}
.page-wrapper--article .article-body :deep(blockquote) {
  margin: 1.5rem 0;
  padding: 1rem 1.25rem;
  border-left: 4px solid #ff6f00;
  background: rgba(255, 111, 0, 0.08);
  border-radius: 0 8px 8px 0;
  font-style: normal;
}

/* Fonds : toujours clairs */
.page-wrapper--article .article-body :deep([class*="bg-surface"]),
.page-wrapper--article .article-body :deep([class*="bg-indigo-9"]),
.page-wrapper--article .article-body :deep([class*="bg-slate-9"]) {
  background-color: #f1f5f9 !important;
}
.page-wrapper--article .article-body :deep(.bg-surface-800\/60),
.page-wrapper--article .article-body :deep(.bg-surface-800\/40) {
  background-color: #e2e8f0 !important;
}

/* Bordures : visibles sur fond clair */
.page-wrapper--article .article-body :deep([class*="border-surface"]),
.page-wrapper--article .article-body :deep([class*="border-indigo"]),
.page-wrapper--article .article-body :deep([class*="border-gold"]),
.page-wrapper--article .article-body :deep([class*="border-red"]),
.page-wrapper--article .article-body :deep(.border-white\/10) {
  border-color: #e2e8f0 !important;
}
.page-wrapper--article .article-body :deep(blockquote) {
  border-left-color: #f97316 !important;
}
</style>
