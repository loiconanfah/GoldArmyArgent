<script setup>
import { onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useHead } from '@unhead/vue'
import { articles } from '@/data/articles'
import { ChevronRightIcon } from '@heroicons/vue/24/outline'
import Footer from '@/components/Footer.vue'

const { t } = useI18n()
const router = useRouter()

useHead({
  title: computed(() => t('seo.blog.title')),
  meta: [
    { name: 'description', content: computed(() => t('seo.blog.description')) }
  ]
})
</script>

<template>
  <div class="min-h-screen bg-[#0a0a12] text-white font-sans overflow-x-hidden selection:bg-violet-500/30">
    
    <!-- Premium Navbar matching Landing.vue -->
    <nav class="fixed top-6 inset-x-0 z-[100] px-6">
      <div class="max-w-7xl mx-auto flex items-center justify-between
                  bg-white/5 backdrop-blur-2xl border border-white/10
                  rounded-2xl px-6 py-4 shadow-2xl shadow-black/40">
        <router-link to="/" class="flex items-center gap-3">
          <div class="w-9 h-9 rounded-xl overflow-hidden border border-violet-500/30 shadow-[0_0_20px_rgba(124,58,237,0.4)]">
            <img src="/logo.png" alt="Logo" class="w-full h-full object-cover" />
          </div>
          <span class="text-lg font-black tracking-tight uppercase text-white">GoldArmy</span>
        </router-link>
        <div class="hidden md:flex items-center gap-8">
          <router-link to="/" class="text-xs font-bold uppercase tracking-[0.2em] text-white/50 hover:text-white transition-colors">{{ t('landing.nav.home') }}</router-link>
          <router-link to="/blog" class="text-xs font-bold uppercase tracking-[0.2em] text-violet-400 hover:text-violet-300 transition-colors">{{ t('landing.nav.blog') }}</router-link>
        </div>
        <div class="flex items-center gap-3">
          <router-link to="/login" class="hidden sm:block text-xs font-bold uppercase tracking-widest text-white/50 hover:text-white transition-colors">
            {{ t('landing.nav.login') }}
          </router-link>
          <router-link to="/register"
            class="bg-violet-600 hover:bg-violet-500 text-white text-[10px] font-black uppercase tracking-[0.25em]
                   px-5 py-2.5 rounded-xl shadow-lg shadow-violet-600/30
                   transition-all hover:shadow-violet-500/40 hover:scale-[1.02] active:scale-95">
            {{ t('landing.nav.get_started') }} →
          </router-link>
        </div>
      </div>
    </nav>

    <!-- Header Section with Glows -->
    <section class="relative pt-40 pb-20 overflow-hidden">
      <!-- Glow blobs -->
      <div class="absolute top-[-10%] right-[10%] w-[500px] h-[500px] bg-violet-600/20 rounded-full blur-[120px] pointer-events-none"></div>
      <div class="absolute top-[20%] left-[-10%] w-[300px] h-[300px] bg-indigo-600/15 rounded-full blur-[100px] pointer-events-none"></div>

      <div class="relative px-6 max-w-7xl mx-auto text-center z-10">
        <div class="inline-flex items-center gap-2.5 mb-8 px-4 py-2 rounded-full
                    bg-violet-500/10 border border-violet-500/20 text-violet-300 text-[10px] font-black uppercase tracking-[0.3em]">
          {{ t('blog.tagline') }}
        </div>
        <h1 class="text-5xl md:text-7xl font-black tracking-tighter mb-6 leading-tight">
          {{ t('blog.title_main') }} <span class="text-transparent bg-clip-text bg-gradient-to-r from-violet-400 to-indigo-400">{{ t('blog.title_highlight') }}</span><br/>
          <span class="text-white/30">{{ t('blog.title_sub') }}</span>
        </h1>
        <p class="text-xl text-white/50 max-w-2xl mx-auto leading-relaxed">
          {{ t('blog.subtitle') }}
        </p>
      </div>
    </section>

    <!-- Article Grid -->
    <section class="px-6 pb-32 max-w-7xl mx-auto relative z-10">
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        <article 
          v-for="article in articles" 
          :key="article.id"
          @click="router.push(`/blog/${article.id}`)"
          class="bg-white/3 border border-white/8 rounded-3xl overflow-hidden hover:border-violet-500/30 hover:bg-white/5 transition-all cursor-pointer group flex flex-col shadow-2xl shadow-black/50"
        >
          <div class="h-56 overflow-hidden relative border-b border-white/5">
            <!-- Image Overlay Glow -->
            <div class="absolute inset-0 bg-gradient-to-b from-transparent to-[#0a0a12]/80 z-10"></div>
            <img :src="article.image" :alt="article.title" class="w-full h-full object-cover group-hover:scale-110 transition-transform duration-700 ease-out" />
          </div>
          <div class="p-8 flex-1 flex flex-col relative z-20 -mt-10">
            <div class="flex items-center gap-3 text-[10px] font-bold uppercase tracking-widest text-violet-400 mb-4">
              <span>{{ new Date(article.date).toLocaleDateString('fr-FR', { day: 'numeric', month: 'long', year: 'numeric' }) }}</span>
              <span class="w-1 h-1 rounded-full bg-violet-400/50"></span>
              <span>Lecture {{ article.readTime }}</span>
            </div>
            <h2 class="text-2xl font-black tracking-tight mb-4 group-hover:text-violet-300 transition-colors line-clamp-3 leading-snug">
              {{ article.title }}
            </h2>
            <p class="text-white/50 text-sm mb-8 line-clamp-3 flex-1 leading-relaxed">
              {{ article.description }}
            </p>
            <div class="flex items-center gap-2 text-violet-400 font-bold text-xs uppercase tracking-widest mt-auto group-hover:translate-x-2 transition-transform">
              {{ t('blog.read_more') }} <ChevronRightIcon class="w-4 h-4" />
            </div>
          </div>
        </article>
      </div>
    </section>

    <Footer />
  </div>
</template>
