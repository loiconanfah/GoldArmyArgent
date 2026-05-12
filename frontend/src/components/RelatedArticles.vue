<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { articles } from '@/data/articles'

const props = defineProps({
  currentId: { type: String, required: true }
})

const router = useRouter()

const related = computed(() =>
  articles.filter(a => a.id !== props.currentId).slice(0, 3)
)

function go(id) {
  router.push(`/blog/${id}`)
}
</script>

<template>
  <section class="related-articles" aria-label="Articles liés">
    <div class="related-articles__container">
      <h2 class="related-articles__title">Articles liés</h2>
      <div class="related-articles__grid">
        <article
          v-for="art in related"
          :key="art.id"
          class="related-articles__card"
          @click="go(art.id)"
        >
          <div class="related-articles__img-wrap">
            <img
              :src="art.image"
              :alt="art.title"
              loading="lazy"
              width="400"
              height="225"
              class="related-articles__img"
            />
          </div>
          <div class="related-articles__body">
            <p class="related-articles__date">{{ art.date }}</p>
            <h3 class="related-articles__card-title">{{ art.title }}</h3>
            <p class="related-articles__desc">{{ art.description }}</p>
            <router-link :to="`/blog/${art.id}`" class="related-articles__link">
              Lire l'article →
            </router-link>
          </div>
        </article>
      </div>

      <!-- Maillage interne vers les features -->
      <div class="related-articles__features">
        <p class="related-articles__features-title">Outils GoldArmy AI</p>
        <nav class="related-articles__features-nav" aria-label="Features GoldArmy">
          <router-link to="/sniper-search">🎯 Sniper Search</router-link>
          <router-link to="/mentor-ia">🧠 Mentor IA</router-link>
          <router-link to="/simulation-entretien">🎤 Simulation d'entretien</router-link>
          <router-link to="/crm-emploi">📋 CRM Emploi</router-link>
        </nav>
      </div>
    </div>
  </section>
</template>

<style scoped>
.related-articles {
  background: #f8fafc;
  padding: 3rem 1.5rem;
  border-top: 1px solid #e2e8f0;
}
.related-articles__container {
  max-width: 900px;
  margin: 0 auto;
}
.related-articles__title {
  font-size: 1.5rem;
  font-weight: 800;
  color: #0f172a;
  margin: 0 0 1.75rem;
  letter-spacing: -0.02em;
}
.related-articles__grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.25rem;
}
@media (min-width: 768px) {
  .related-articles__grid { grid-template-columns: repeat(3, 1fr); }
}
.related-articles__card {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 0.75rem;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}
.related-articles__card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 24px rgba(0,0,0,0.08);
}
.related-articles__img-wrap {
  aspect-ratio: 16/9;
  overflow: hidden;
}
.related-articles__img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s;
}
.related-articles__card:hover .related-articles__img {
  transform: scale(1.04);
}
.related-articles__body {
  padding: 1rem;
}
.related-articles__date {
  font-size: 0.75rem;
  color: #94a3b8;
  margin: 0 0 0.4rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
.related-articles__card-title {
  font-size: 0.9375rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0 0 0.4rem;
  line-height: 1.35;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.related-articles__desc {
  font-size: 0.8125rem;
  color: #64748b;
  margin: 0 0 0.75rem;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.related-articles__link {
  font-size: 0.8125rem;
  font-weight: 600;
  color: #ea580c;
  text-decoration: none;
}
.related-articles__link:hover { text-decoration: underline; }

/* Features nav */
.related-articles__features {
  margin-top: 2rem;
  padding-top: 1.5rem;
  border-top: 1px solid #e2e8f0;
}
.related-articles__features-title {
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: #94a3b8;
  margin: 0 0 0.75rem;
}
.related-articles__features-nav {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}
.related-articles__features-nav a {
  font-size: 0.875rem;
  font-weight: 600;
  color: #0f172a;
  text-decoration: none;
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 999px;
  padding: 0.35rem 0.9rem;
  transition: border-color 0.2s, color 0.2s;
}
.related-articles__features-nav a:hover {
  border-color: #ff6f00;
  color: #ea580c;
}
/* Screen-reader only H1 helper */
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border-width: 0;
}
</style>
