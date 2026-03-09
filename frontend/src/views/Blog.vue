<script setup>
import { computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useHead } from '@unhead/vue'
import { articles } from '@/data/articles'
import LandingNav from '@/components/LandingNav.vue'
import Footer from '@/components/Footer.vue'

const { t } = useI18n()
const router = useRouter()

const featuredArticle = computed(() => articles.find(a => a.featured) ?? articles[0] ?? null)
const otherFeatured = computed(() => articles.filter(a => a.id !== featuredArticle.value?.id).slice(0, 5))
const recentArticles = computed(() => articles)

onMounted(() => {
  const link = document.createElement('link')
  link.rel = 'stylesheet'
  link.href = '/orvimo-landing.css'
  link.id = 'orvimo-landing-css'
  document.head.appendChild(link)
  document.documentElement.classList.add('w-mod-ix3')
})
onUnmounted(() => {
  const link = document.getElementById('orvimo-landing-css')
  if (link) link.remove()
  document.documentElement.classList.remove('w-mod-ix3')
})

useHead({
  title: computed(() => t('seo.blog.title')),
  meta: [
    { name: 'description', content: computed(() => t('seo.blog.description')) }
  ]
})

function goToArticle(id) {
  router.push(`/blog/${id}`)
}
</script>

<template>
  <div class="page-wrapper page-wrapper--blog">
    <LandingNav />
    <main class="main dark-secondary">
      <!-- Featured Posts -->
      <section class="section blog-featured">
        <div class="blog-featured__container">
          <div class="blog-featured__grid">
            <!-- Main featured card -->
            <article
              v-if="featuredArticle"
              class="blog-featured__main"
              @click="goToArticle(featuredArticle.id)"
            >
              <div class="blog-featured__main-img-wrap">
                <img
                  :src="featuredArticle.image"
                  :alt="featuredArticle.title"
                  class="blog-featured__main-img"
                  loading="eager"
                />
                <div class="blog-featured__main-overlay"></div>
                <div class="blog-featured__main-content">
                  <span class="blog-featured__pill">{{ t('blog.category_default') }}</span>
                  <h2 class="blog-featured__main-title">{{ featuredArticle.title }}</h2>
                </div>
              </div>
            </article>

            <!-- Other featured posts -->
            <div class="blog-featured__side">
              <h3 class="blog-featured__side-title">{{ t('blog.other_featured_posts') }}</h3>
              <div class="blog-featured__list">
                <button
                  v-for="art in otherFeatured"
                  :key="art.id"
                  type="button"
                  class="blog-featured__item"
                  @click="goToArticle(art.id)"
                >
                  <div class="blog-featured__item-thumb">
                    <img :src="art.image" :alt="art.title" loading="lazy" />
                  </div>
                  <span class="blog-featured__item-title">{{ art.title }}</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Recent Posts -->
      <section id="recent-posts" class="section blog-recent">
        <div class="blog-recent__container">
          <header class="blog-recent__header">
            <h2 class="blog-recent__heading">{{ t('blog.recent_posts') }}</h2>
            <a href="#recent-posts" class="blog-recent__all-btn">{{ t('blog.all_posts') }}</a>
          </header>
          <div class="blog-recent__grid">
            <article
              v-for="article in recentArticles"
              :key="article.id"
              class="blog-recent__card"
              @click="goToArticle(article.id)"
            >
              <div class="blog-recent__card-img-wrap">
                <img
                  :src="article.image"
                  :alt="article.title"
                  class="blog-recent__card-img"
                  loading="lazy"
                />
              </div>
              <div class="blog-recent__card-body">
                <h3 class="blog-recent__card-title">{{ article.title }}</h3>
                <p class="blog-recent__card-desc">{{ article.description }}</p>
                <div class="blog-recent__card-meta">
                  <span class="blog-recent__card-author">
                    <span class="blog-recent__avatar">{{ (article.author || t('blog.author_default')).charAt(0) }}</span>
                    {{ article.author || t('blog.author_default') }}
                  </span>
                  <span class="blog-recent__card-dot"></span>
                  <span class="blog-recent__card-read">{{ article.readTime }}</span>
                </div>
              </div>
            </article>
          </div>
        </div>
      </section>
    </main>
    <Footer />
  </div>
</template>

<style scoped>
/* Thème identique landing (orvimo dark) */
.page-wrapper--blog {
  min-height: 100vh;
  overflow-x: clip;
  --_theme---bodybackground: #2e2e2e;
  --_theme---textcolor--primarytext: #ffffff;
  --_theme---textcolor--secondarytext: #e8e8e8;
  --_theme---textcolor--tertiarytext: #b8b8b8;
  --_theme---background--primarybackground: #2e2e2e;
  --_theme---background--secondarybackground: #1f1f1f;
  --_theme---background--tertiarybackground: #333;
  --_theme---border--mediumalpha: rgba(255, 255, 255, 0.12);
  --_theme---textcolor--accenttext1: #ff6f00;
  background-color: var(--_theme---bodybackground);
  color: var(--_theme---textcolor--primarytext);
}
.page-wrapper--blog :deep(.main) {
  padding-top: 0;
}

/* Featured section */
.blog-featured {
  padding: 2.5rem 1.5rem 3rem;
}
.blog-featured__container {
  max-width: 1200px;
  margin: 0 auto;
}
.blog-featured__grid {
  display: grid;
  gap: 2rem;
  grid-template-columns: 1fr;
}
@media (min-width: 900px) {
  .blog-featured__grid {
    grid-template-columns: 1.4fr 1fr;
    gap: 2.5rem;
  }
}

.blog-featured__main {
  border-radius: 1rem;
  overflow: hidden;
  cursor: pointer;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.35);
  transition: transform 0.2s, box-shadow 0.2s;
}
.blog-featured__main:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.4);
}
.blog-featured__main-img-wrap {
  position: relative;
  aspect-ratio: 16 / 10;
  min-height: 280px;
}
.blog-featured__main-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}
.blog-featured__main-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(to top, rgba(30, 30, 30, 0.95) 0%, transparent 50%);
  pointer-events: none;
}
.blog-featured__main-content {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  padding: 1.5rem 1.5rem 1.75rem;
}
.blog-featured__pill {
  display: inline-block;
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #fff;
  background: var(--_theme---background--secondarybackground);
  padding: 0.35rem 0.75rem;
  border-radius: 999px;
  margin-bottom: 0.75rem;
}
.blog-featured__main-title {
  font-size: clamp(1.25rem, 2.5vw, 1.75rem);
  font-weight: 800;
  letter-spacing: -0.02em;
  line-height: 1.25;
  margin: 0;
  color: var(--_theme---textcolor--primarytext);
}

.blog-featured__side-title {
  font-size: 1.125rem;
  font-weight: 700;
  color: var(--_theme---textcolor--primarytext);
  margin: 0 0 1.25rem;
}
.blog-featured__list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}
.blog-featured__item {
  display: flex;
  align-items: center;
  gap: 1rem;
  width: 100%;
  text-align: left;
  padding: 0;
  border: none;
  background: transparent;
  cursor: pointer;
  border-radius: 0.75rem;
  padding: 0.5rem;
  transition: background 0.2s;
}
.blog-featured__item:hover {
  background: var(--_theme---background--secondarybackground);
}
.blog-featured__item-thumb {
  flex-shrink: 0;
  width: 72px;
  height: 72px;
  border-radius: 0.5rem;
  overflow: hidden;
  background: var(--_theme---background--tertiarybackground);
}
.blog-featured__item-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.blog-featured__item-title {
  font-size: 0.9375rem;
  font-weight: 600;
  color: var(--_theme---textcolor--primarytext);
  line-height: 1.35;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* Recent section */
.blog-recent {
  padding: 0 1.5rem 4rem;
}
.blog-recent__container {
  max-width: 1200px;
  margin: 0 auto;
}
.blog-recent__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 1.75rem;
}
.blog-recent__heading {
  font-size: 1.5rem;
  font-weight: 800;
  color: var(--_theme---textcolor--primarytext);
  margin: 0;
}
.blog-recent__all-btn {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--_theme---textcolor--primarytext);
  padding: 0.5rem 1.25rem;
  border: 1px solid var(--_theme---border--mediumalpha);
  border-radius: 0.5rem;
  text-decoration: none;
  transition: border-color 0.2s, background 0.2s;
}
.blog-recent__all-btn:hover {
  border-color: var(--_theme---textcolor--accenttext1);
  background: rgba(255, 111, 0, 0.08);
}

.blog-recent__grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.75rem;
}
@media (min-width: 768px) {
  .blog-recent__grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
@media (min-width: 1024px) {
  .blog-recent__grid {
    grid-template-columns: repeat(3, 1fr);
    gap: 2rem;
  }
}

.blog-recent__card {
  background: var(--_theme---background--secondarybackground);
  border: 1px solid var(--_theme---border--mediumalpha);
  border-radius: 1rem;
  overflow: hidden;
  cursor: pointer;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
  transition: border-color 0.25s, transform 0.2s, box-shadow 0.2s;
  display: flex;
  flex-direction: column;
}
.blog-recent__card:hover {
  border-color: rgba(255, 111, 0, 0.35);
  transform: translateY(-4px);
  box-shadow: 0 8px 28px rgba(0, 0, 0, 0.3);
}
.blog-recent__card-img-wrap {
  aspect-ratio: 16 / 10;
  overflow: hidden;
}
.blog-recent__card-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.4s ease;
}
.blog-recent__card:hover .blog-recent__card-img {
  transform: scale(1.05);
}
.blog-recent__card-body {
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  flex: 1;
}
.blog-recent__card-title {
  font-size: 1.125rem;
  font-weight: 700;
  letter-spacing: -0.02em;
  line-height: 1.35;
  margin: 0 0 0.5rem;
  color: var(--_theme---textcolor--primarytext);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.blog-recent__card-desc {
  font-size: 0.9375rem;
  line-height: 1.5;
  color: var(--_theme---textcolor--secondarytext);
  margin: 0 0 1rem;
  flex: 1;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.blog-recent__card-meta {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.8125rem;
  color: var(--_theme---textcolor--tertiarytext);
}
.blog-recent__card-author {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
}
.blog-recent__avatar {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: var(--_theme---textcolor--accenttext1);
  color: #1f1f1f;
  font-weight: 700;
  font-size: 0.7rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.blog-recent__card-dot {
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: var(--_theme---textcolor--tertiarytext);
}
</style>
