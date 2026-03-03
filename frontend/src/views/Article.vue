<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { articles } from '@/data/articles'
import { useMeta } from '@/composables/useMeta'
import { ArrowLeftIcon, ArrowRightIcon, LinkIcon } from '@heroicons/vue/24/outline'

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
  alert('Lien copié dans le presse-papiers !')
}

const shareLinkedIn = () => {
  const url = encodeURIComponent(window.location.href)
  window.open(`https://www.linkedin.com/sharing/share-offsite/?url=${url}`, '_blank')
}

const shareTwitter = () => {
  const url = encodeURIComponent(window.location.href)
  const text = encodeURIComponent(`Découvrez cet article de GoldArmy AI : ${article.value?.title}`)
  window.open(`https://twitter.com/intent/tweet?url=${url}&text=${text}`, '_blank')
}

onMounted(() => {
  if (article.value) {
    useMeta({
      title: `${article.value.title} | GoldArmy AI Blog`,
      description: article.value.description
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
          <router-link to="/" class="text-xs font-bold uppercase tracking-[0.2em] text-white/50 hover:text-white transition-colors">Accueil</router-link>
          <router-link to="/blog" class="text-xs font-bold uppercase tracking-[0.2em] text-violet-400 hover:text-violet-300 transition-colors">Blog</router-link>
        </div>
        <div class="flex items-center gap-3">
          <router-link to="/login" class="hidden sm:block text-xs font-bold uppercase tracking-widest text-white/50 hover:text-white transition-colors">
            Connexion
          </router-link>
          <router-link to="/register"
            class="bg-violet-600 hover:bg-violet-500 text-white text-[10px] font-black uppercase tracking-[0.25em]
                   px-5 py-2.5 rounded-xl shadow-lg shadow-violet-600/30
                   transition-all hover:shadow-violet-500/40 hover:scale-[1.02] active:scale-95">
            Démarrer →
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
        <ArrowLeftIcon class="w-4 h-4 group-hover:-translate-x-1 transition-transform" /> Retour au blog
      </button>

      <div class="flex items-center gap-4 text-[10px] font-bold uppercase tracking-widest text-violet-400 mb-6">
        <span class="px-3 py-1 rounded-full border border-violet-500/30 bg-violet-500/10">{{ new Date(article.date).toLocaleDateString('fr-FR', { day: 'numeric', month: 'long', year: 'numeric' }) }}</span>
        <span class="w-1 h-1 rounded-full bg-violet-400/50"></span>
        <span class="flex items-center gap-1.5"><svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" /></svg> Lecture {{ article.readTime }}</span>
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
              <span class="w-8 h-px bg-violet-500/30"></span> Passez à la vitesse supérieure <span class="w-8 h-px bg-violet-500/30"></span>
            </p>
            <h3 class="text-4xl lg:text-5xl font-black mb-6 tracking-tighter leading-tight">Ne postulez plus dans le vide.</h3>
            <p class="text-lg text-white/50 mb-10 max-w-lg mx-auto leading-relaxed">Arrêtez d'envoyer des CV qui finissent à la poubelle. Laissez nos Agents IA auditer votre profil et vous trouver les meilleures opportunités en quelques secondes.</p>
            
            <router-link to="/register"
              class="inline-flex items-center justify-center gap-3 bg-white text-[#0a0a12] font-black text-sm uppercase tracking-[0.2em]
                     px-12 py-5 rounded-2xl shadow-[0_0_40px_rgba(255,255,255,0.3)] transition-all hover:scale-[1.03] active:scale-95 hover:shadow-[0_0_60px_rgba(255,255,255,0.5)] group w-full sm:w-auto">
              Créer mon compte VIP <ArrowRightIcon class="w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </router-link>
            
            <p class="mt-8 text-xs font-bold text-white/30 uppercase tracking-widest">Essai 100% gratuit. Sans carte de crédit.</p>
        </div>
      </div>
    </div>

    <!-- Full Footer matching Landing.vue -->
    <footer class="border-t border-white/5 pt-20 pb-10 mt-20 relative bg-[#0a0a12] z-10">
      <div class="max-w-7xl mx-auto px-6 grid grid-cols-1 md:grid-cols-4 gap-12 mb-16">
        <div class="md:col-span-2">
          <div class="flex items-center gap-3 mb-6">
            <div class="w-9 h-9 rounded-xl overflow-hidden border border-violet-500/30">
              <img src="/logo.png" alt="Logo" class="w-full h-full object-cover" />
            </div>
            <span class="text-lg font-black uppercase tracking-widest text-white">GoldArmy</span>
          </div>
          <p class="text-white/40 text-sm leading-relaxed max-w-sm mb-8">
            L'intelligence artificielle au service de votre carrière. Ne cherchez plus d'emploi, laissez les opportunités venir à vous grâce à nos agents autonomes.
          </p>
        </div>

        <div>
          <h4 class="text-white font-black uppercase tracking-[0.2em] text-xs mb-6">Navigation</h4>
          <ul class="space-y-4">
            <li><a href="/#agents" class="text-sm text-white/40 hover:text-white transition-colors">Nos Agents IA</a></li>
            <li><a href="/#tarifs" class="text-sm text-white/40 hover:text-white transition-colors">Tarification</a></li>
            <li><router-link to="/blog" class="text-sm text-white/40 hover:text-white transition-colors">Le Blog IA</router-link></li>
            <li><router-link to="/login" class="text-sm text-white/40 hover:text-white transition-colors">Espace Candidat</router-link></li>
          </ul>
        </div>

        <div>
          <h4 class="text-white font-black uppercase tracking-[0.2em] text-xs mb-6">Contact</h4>
          <ul class="space-y-4 mb-8">
            <li><a href="mailto:support@goldarmyai.com" class="text-sm text-white/40 hover:text-violet-400 transition-colors flex items-center gap-2"><span class="w-1.5 h-1.5 rounded-full bg-violet-500"></span> Support Client</a></li>
            <li><a href="mailto:yvanloic@goldarmyai.com" class="text-sm text-white/40 hover:text-violet-400 transition-colors flex items-center gap-2"><span class="w-1.5 h-1.5 rounded-full bg-violet-500"></span> Contacter le CEO</a></li>
          </ul>
        </div>
      </div>

      <div class="max-w-7xl mx-auto px-6 border-t border-white/5 pt-8 flex flex-col md:flex-row items-center justify-between gap-4">
        <p class="text-xs text-white/20 font-bold">© 2026 GoldArmy Agent IA. Tous droits réservés.</p>
        <div class="flex gap-6">
          <a href="#" class="text-xs text-white/20 hover:text-white transition-colors font-bold tracking-widest uppercase">Confidentialité</a>
          <a href="#" class="text-xs text-white/20 hover:text-white transition-colors font-bold tracking-widest uppercase">CGU</a>
        </div>
      </div>
    </footer>
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
