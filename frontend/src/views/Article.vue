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

    <main class="main dark-secondary">
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
/* Thème identique landing (orvimo dark) */
.page-wrapper--article {
  min-height: 100vh;
  overflow-x: clip;
  --_theme---bodybackground: #2e2e2e;
  --_theme---textcolor--primarytext: #ffffff;
  --_theme---textcolor--secondarytext: #e8e8e8;
  --_theme---textcolor--tertiarytext: #b8b8b8;
  --_theme---background--primarybackground: #2e2e2e;
  --_theme---background--secondarybackground: #1f1f1f;
  --_theme---textcolor--accenttext1: #ff6f00;
  --_theme---border--mediumalpha: rgba(255, 255, 255, 0.12);
  background-color: var(--_theme---bodybackground);
  color: var(--_theme---textcolor--primarytext);
}
.page-wrapper--article :deep(.main) {
  padding-top: 0;
  padding-bottom: 0;
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
  color: var(--_theme---textcolor--secondarytext);
  text-decoration: none;
  margin-bottom: 1.5rem;
  transition: color 0.2s;
}
.article-back:hover {
  color: var(--_theme---textcolor--accenttext1);
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
  color: var(--_theme---textcolor--accenttext1);
  margin-bottom: 1rem;
}
.article-meta__dot {
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: var(--_theme---textcolor--accenttext1);
  opacity: 0.6;
}
.article-title {
  font-size: clamp(1.875rem, 4vw, 2.75rem);
  font-weight: 800;
  letter-spacing: -0.03em;
  line-height: 1.15;
  margin: 0 0 1rem;
  color: var(--_theme---textcolor--primarytext);
}
.article-lead {
  font-size: 1.125rem;
  line-height: 1.6;
  color: var(--_theme---textcolor--secondarytext);
  margin: 0;
  padding-left: 1.25rem;
  border-left: 3px solid var(--_theme---textcolor--accenttext1);
  opacity: 0.8;
}
.article-hero-image {
  border-radius: var(--radius--s, 1rem);
  overflow: hidden;
  margin-bottom: 2.5rem;
  border: 1px solid var(--_theme---border--mediumalpha, rgba(255, 255, 255, 0.12));
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
  border-top: 1px solid var(--_theme---border--mediumalpha, rgba(255, 255, 255, 0.12));
  text-align: center;
  background: var(--_theme---background--secondarybackground);
  border: 1px solid var(--_theme---border--mediumalpha, rgba(255, 255, 255, 0.12));
  border-radius: var(--radius--s, 1rem);
  padding: 2rem 1.5rem;
}
.article-cta__tagline {
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  color: var(--_theme---textcolor--accenttext1);
  margin: 0 0 0.75rem;
}
.article-cta__title {
  font-size: 1.75rem;
  font-weight: 800;
  letter-spacing: -0.02em;
  margin: 0 0 0.75rem;
  color: var(--_theme---textcolor--primarytext);
}
.article-cta__subtitle {
  font-size: 1rem;
  line-height: 1.6;
  color: var(--_theme---textcolor--secondarytext);
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
  color: #1f1f1f;
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
  color: var(--_theme---textcolor--tertiarytext);
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
  background: var(--_theme---background--secondarybackground);
  border: 1px solid var(--_theme---border--mediumalpha, rgba(255, 255, 255, 0.12));
  border-radius: var(--radius--xs, 0.5rem);
  color: var(--_theme---textcolor--secondarytext);
  cursor: pointer;
  transition: color 0.2s, background 0.2s, border-color 0.2s;
}
.article-share__btn:hover {
  color: var(--_theme---textcolor--accenttext1);
  background: rgba(255, 111, 0, 0.1);
  border-color: rgba(255, 111, 0, 0.25);
}
.article-share__icon {
  width: 1.25rem;
  height: 1.25rem;
}
</style>

<style>
/* Contenu article : couleurs thème landing */
.page-wrapper--article .article-body :deep(h2) {
  font-size: 1.75rem;
  font-weight: 800;
  letter-spacing: -0.02em;
  margin-top: 2.5rem;
  margin-bottom: 1rem;
  color: var(--_theme---textcolor--primarytext);
  padding-bottom: 0.5rem;
  border-bottom: 2px solid rgba(255, 111, 0, 0.35);
}
.page-wrapper--article .article-body :deep(p) {
  font-size: 1.0625rem;
  line-height: 1.75;
  color: var(--_theme---textcolor--secondarytext);
  margin-bottom: 1.25rem;
}
.page-wrapper--article .article-body :deep(p:first-of-type) {
  font-size: 1.125rem;
}
.page-wrapper--article .article-body :deep(a) {
  color: var(--_theme---textcolor--accenttext1);
  text-decoration: underline;
  text-underline-offset: 3px;
}
.page-wrapper--article .article-body :deep(a:hover) {
  color: #ffb380;
}
.page-wrapper--article .article-body :deep(strong) {
  color: var(--_theme---textcolor--primarytext);
  font-weight: 700;
}
.page-wrapper--article .article-body :deep(ul),
.page-wrapper--article .article-body :deep(ol) {
  margin: 1.25rem 0;
  padding-left: 1.5rem;
  color: var(--_theme---textcolor--secondarytext);
  line-height: 1.7;
}
.page-wrapper--article .article-body :deep(li) {
  margin-bottom: 0.5rem;
}
.page-wrapper--article .article-body :deep(li::marker) {
  color: var(--_theme---textcolor--accenttext1);
}
.page-wrapper--article .article-body :deep(img) {
  width: 100%;
  height: auto;
  border-radius: 12px;
  margin: 1.5rem 0;
  border: 1px solid var(--_theme---border--mediumalpha, rgba(255, 255, 255, 0.12));
}
.page-wrapper--article .article-body :deep(blockquote) {
  margin: 1.5rem 0;
  padding: 1rem 1.25rem;
  border-left: 4px solid var(--_theme---textcolor--accenttext1);
  background: rgba(255, 111, 0, 0.06);
  border-radius: 0 8px 8px 0;
  color: var(--_theme---textcolor--primarytext);
  font-style: normal;
}
</style>
