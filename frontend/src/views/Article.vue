<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useHead } from '@unhead/vue'
import { articles } from '@/data/articles'
import { ArrowLeftIcon, ArrowRightIcon, LinkIcon } from '@heroicons/vue/24/outline'
import Footer from '@/components/Footer.vue'

const { t, locale } = useI18n()
const route = useRoute()
const router = useRouter()

const article = computed(() => {
  return articles.find(a => a.id === route.params.id)
})

const scrollProgress = ref(0)
const isLoaded = ref(false)

const handleScroll = () => {
  const windowHeight = window.innerHeight
  const documentHeight = document.documentElement.scrollHeight
  const scrollTop = window.scrollY
  scrollProgress.value = (scrollTop / (documentHeight - windowHeight)) * 100
}

const copyLink = () => {
  navigator.clipboard.writeText(window.location.href)
  alert(t('blog.link_copied'))
}

const shareLinkedIn = () => {
  const url = encodeURIComponent(window.location.href)
  window.open(`https://www.linkedin.com/sharing/share-offsite/?url=${url}`, '_blank')
}

const shareTwitter = () => {
  const url = encodeURIComponent(window.location.href)
  const text = encodeURIComponent(t('blog.share_text', { title: article.value?.title }))
  window.open(`https://twitter.com/intent/tweet?url=${url}&text=${text}`, '_blank')
}

onMounted(() => {
  if (article.value) {
    useHead({
      title: `${article.value.title} | GoldArmy AI Blog`,
      meta: [
        { name: 'description', content: article.value.description }
      ]
    })
    window.addEventListener('scroll', handleScroll)
    // Trigger entrance animations
    setTimeout(() => {
      isLoaded.value = true
    }, 100)
  } else {
    router.replace('/blog')
  }
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})
</script>

<template>
  <div class="min-h-screen bg-[#0a0a12] text-white font-sans overflow-x-hidden selection:bg-violet-500/30" v-if="article">
    
    <!-- Reading Progress Bar -->
    <div class="fixed top-0 left-0 h-1 bg-gradient-to-r from-violet-600 to-indigo-400 z-[200] transition-all duration-150 ease-out"
         :style="{ width: `${scrollProgress}%` }">
    </div>

    <!-- Premium Navbar matching Landing.vue -->
    <nav class="fixed top-6 inset-x-0 z-[100] px-6 transition-all duration-700 delay-300"
         :class="isLoaded ? 'opacity-100 translate-y-0' : 'opacity-0 -translate-y-8'">
      <div class="max-w-7xl mx-auto flex items-center justify-between
                  bg-white/5 backdrop-blur-2xl border border-white/10
                  rounded-2xl px-6 py-4 shadow-2xl shadow-black/40">
        <router-link to="/" class="flex items-center gap-3 group">
          <div class="w-9 h-9 rounded-xl overflow-hidden border border-violet-500/30 shadow-[0_0_20px_rgba(124,58,237,0.4)] group-hover:shadow-[0_0_30px_rgba(124,58,237,0.6)] transition-shadow">
            <img src="/logo.png" alt="Logo" class="w-full h-full object-cover" />
          </div>
          <span class="text-lg font-black tracking-tight uppercase text-white group-hover:text-violet-100 transition-colors">GoldArmy</span>
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

    <!-- Floating Share Sidebar (Desktop only) -->
    <div class="hidden lg:flex fixed left-8 top-1/2 -translate-y-1/2 flex-col gap-4 z-50 transition-all duration-1000 delay-500"
         :class="isLoaded ? 'opacity-100 translate-x-0' : 'opacity-0 -translate-x-12'">
      <div class="w-px h-16 bg-gradient-to-b from-transparent to-white/20 mx-auto mb-2"></div>
      
      <button @click="shareLinkedIn" class="w-10 h-10 rounded-full bg-white/5 border border-white/10 flex items-center justify-center text-white/50 hover:text-blue-400 hover:bg-blue-500/10 hover:border-blue-500/30 transition-all hover:scale-110 group" title="Partager sur LinkedIn">
        <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z"/></svg>
      </button>

      <button @click="shareTwitter" class="w-10 h-10 rounded-full bg-white/5 border border-white/10 flex items-center justify-center text-white/50 hover:text-sky-400 hover:bg-sky-500/10 hover:border-sky-500/30 transition-all hover:scale-110 group" title="Partager sur X (Twitter)">
        <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M24 4.557c-.883.392-1.832.656-2.828.775 1.017-.609 1.798-1.574 2.165-2.724-.951.564-2.005.974-3.127 1.195-.897-.957-2.178-1.555-3.594-1.555-3.179 0-5.515 2.966-4.797 6.045-4.091-.205-7.719-2.165-10.148-5.144-1.29 2.213-.669 5.108 1.523 6.574-.806-.026-1.566-.247-2.229-.616-.054 2.281 1.581 4.415 3.949 4.89-.693.188-1.452.232-2.224.084.626 1.956 2.444 3.379 4.6 3.419-2.07 1.623-4.678 2.348-7.29 2.04 2.179 1.397 4.768 2.212 7.548 2.212 9.142 0 14.307-7.721 13.995-14.646.962-.695 1.797-1.562 2.457-2.549z"/></svg>
      </button>

      <button @click="copyLink" class="w-10 h-10 rounded-full bg-white/5 border border-white/10 flex items-center justify-center text-white/50 hover:text-white hover:bg-white/10 hover:border-white/30 transition-all hover:scale-110 group" title="Copier le lien">
        <LinkIcon class="w-4 h-4" />
      </button>

      <div class="w-px h-16 bg-gradient-to-t from-transparent to-white/20 mx-auto mt-2"></div>
    </div>

    <!-- Article Header -->
    <div class="relative pt-40 pb-12 px-6 max-w-4xl mx-auto z-10 transition-all duration-1000"
         :class="isLoaded ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-12'">
      
      <!-- Glow blobs behind title -->
      <div class="absolute top-[20%] right-[-20%] w-[400px] h-[400px] bg-violet-600/20 rounded-full blur-[120px] pointer-events-none transition-opacity duration-1000 delay-500"
           :class="isLoaded ? 'opacity-100' : 'opacity-0'"></div>
      <div class="absolute top-[40%] left-[-10%] w-[300px] h-[300px] bg-indigo-600/15 rounded-full blur-[100px] pointer-events-none transition-opacity duration-1000 delay-700"
           :class="isLoaded ? 'opacity-100' : 'opacity-0'"></div>

      <button @click="router.push('/blog')" class="flex items-center gap-2 text-white/40 hover:text-white transition-colors mb-12 text-xs font-bold uppercase tracking-widest group">
        <ArrowLeftIcon class="w-4 h-4 group-hover:-translate-x-1 transition-transform" /> {{ t('blog.back_to_blog') }}
      </button>

      <div class="flex items-center gap-4 text-[10px] font-bold uppercase tracking-widest text-violet-400 mb-6">
        <span class="px-3 py-1 rounded-full border border-violet-500/30 bg-violet-500/10">{{ new Date(article.date).toLocaleDateString(locale === 'fr' ? 'fr-FR' : 'en-US', { day: 'numeric', month: 'long', year: 'numeric' }) }}</span>
        <span class="w-1 h-1 rounded-full bg-violet-400/50"></span>
        <span class="flex items-center gap-1.5"><svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" /></svg> {{ t('blog.read_time', { time: article.readTime }) }}</span>
      </div>

      <h1 class="text-4xl md:text-6xl font-black mb-8 leading-[1.1] tracking-tighter">
        {{ article.title }}
      </h1>
      
      <p class="text-xl text-white/50 leading-relaxed max-w-2xl border-l-2 border-violet-500/50 pl-6">
        {{ article.description }}
      </p>
    </div>

    <!-- Hero Image Parallax Wrapper -->
    <div class="relative max-w-5xl mx-auto px-6 mb-24 z-10 transition-all duration-1000 delay-300"
         :class="isLoaded ? 'opacity-100 scale-100' : 'opacity-0 scale-95'">
      <div class="h-[400px] md:h-[600px] w-full rounded-[2.5rem] overflow-hidden border border-white/10 shadow-[0_30px_60px_-15px_rgba(0,0,0,0.8)] relative group">
        <!-- Overlay gradients for depth -->
        <div class="absolute inset-x-0 bottom-0 h-1/2 bg-gradient-to-t from-[#0a0a12] to-transparent z-10 pointer-events-none opacity-60"></div>
        <div class="absolute inset-0 ring-1 ring-inset ring-white/10 rounded-[2.5rem] z-20 pointer-events-none"></div>
        
        <!-- The Image with smooth scale animation -->
        <img :src="article.image" :alt="article.title" 
             class="w-full h-full object-cover transition-transform duration-[20s] ease-out group-hover:scale-110" 
             style="transform-origin: center center" />
      </div>
    </div>

    <!-- Article Content -->
    <div class="relative z-10 px-6 pb-32 max-w-3xl mx-auto prose prose-invert prose-lg 
                prose-p:text-white/70 prose-p:leading-[1.8] prose-p:tracking-[0.01em]
                prose-a:text-violet-400 hover:prose-a:text-violet-300 prose-a:transition-colors prose-a:underline-offset-4 prose-a:decoration-violet-500/30 hover:prose-a:decoration-violet-400
                prose-headings:text-white prose-headings:font-black prose-headings:tracking-tight 
                prose-strong:text-white prose-strong:font-bold
                prose-blockquote:border-l-4 prose-blockquote:border-violet-500 prose-blockquote:bg-white/[0.02] prose-blockquote:pl-6 prose-blockquote:py-2 prose-blockquote:rounded-r-xl prose-blockquote:not-italic
                prose-li:marker:text-violet-500
                transition-all duration-1000 delay-500"
         :class="isLoaded ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-12'">
      
      <div v-html="article.content" class="article-body"></div>
      
      <!-- Premium CTAs Matching Landing Tone -->
      <div class="mt-32 pt-20 border-t border-white/5 text-center relative">
        <!-- Glow behind CTA -->
        <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[400px] h-[400px] bg-violet-600/10 blur-[100px] rounded-full pointer-events-none"></div>
        
        <div class="relative z-10 p-12 rounded-[3rem] bg-gradient-to-b from-white/[0.03] to-transparent border border-white/5 shadow-2xl backdrop-blur-xl">
            <p class="text-[10px] font-black uppercase tracking-[0.5em] text-violet-500 mb-6 flex items-center justify-center gap-3">
              <span class="w-8 h-px bg-violet-500/30"></span> {{ t('blog.cta_tagline') }} <span class="w-8 h-px bg-violet-500/30"></span>
            </p>
            <h3 class="text-4xl lg:text-5xl font-black mb-6 tracking-tighter leading-tight">{{ t('blog.cta_title') }}</h3>
            <p class="text-lg text-white/50 mb-10 max-w-lg mx-auto leading-relaxed">{{ t('blog.cta_subtitle') }}</p>
            
            <router-link to="/register"
              class="inline-flex items-center justify-center gap-3 bg-white text-[#0a0a12] font-black text-sm uppercase tracking-[0.2em]
                     px-12 py-5 rounded-2xl shadow-[0_0_40px_rgba(255,255,255,0.3)] transition-all hover:scale-[1.03] active:scale-95 hover:shadow-[0_0_60px_rgba(255,255,255,0.5)] group w-full sm:w-auto">
              {{ t('blog.cta_button') }} <ArrowRightIcon class="w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </router-link>
            
            <p class="mt-8 text-xs font-bold text-white/30 uppercase tracking-widest">{{ t('blog.cta_free_trial') }}</p>
        </div>
      </div>
    </div>

    <Footer />
  </div>
</template>

<style>
/* Scoped overrides for the v-html injected content for maximum legibility and style */
.article-body h2 {
  font-size: 2.5rem;
  margin-top: 4.5rem;
  margin-bottom: 2rem;
  font-weight: 900;
  letter-spacing: -0.03em;
  line-height: 1.1;
  position: relative;
}
.article-body h2::after {
  content: '';
  position: absolute;
  bottom: -1rem;
  left: 0;
  width: 40px;
  height: 4px;
  background: #8b5cf6;
  border-radius: 2px;
}
.article-body p {
  margin-bottom: 2rem;
  font-size: 1.125rem;
}
.article-body p:first-of-type::first-letter {
  font-size: 4rem;
  font-weight: 900;
  color: #8b5cf6;
  float: left;
  line-height: 1;
  margin-right: 0.75rem;
  margin-top: 0.25rem;
}
.article-body ul, .article-body ol {
  margin-top: 2rem;
  margin-bottom: 3rem;
  padding-left: 1.5rem;
  background: rgba(255,255,255,0.02);
  border: 1px solid rgba(255,255,255,0.05);
  border-radius: 1rem;
  padding: 2rem 2rem 2rem 3rem;
}
.article-body li {
  margin-bottom: 1.25rem;
  line-height: 1.8;
}
.article-body li:last-child {
  margin-bottom: 0;
}
</style>
