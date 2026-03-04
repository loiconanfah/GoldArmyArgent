<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useHead } from '@unhead/vue'
import { useI18n } from 'vue-i18n'
import Footer from '../components/Footer.vue'
import {
  DocumentTextIcon,
  ArrowUpTrayIcon,
  ExclamationTriangleIcon,
  ArrowRightIcon,
  ShieldCheckIcon,
  LockClosedIcon,
  CheckCircleIcon
} from '@heroicons/vue/24/outline'

const { t, locale } = useI18n()
const router = useRouter()

useHead({
  title: computed(() => t('seo.free_cv.title')),
  meta: [
    { name: 'description', content: computed(() => t('seo.free_cv.description')) },
    { property: 'og:title', content: computed(() => t('seo.free_cv.og_title')) },
    { property: 'og:description', content: computed(() => t('seo.free_cv.og_description')) },
  ],
  script: [
    {
      type: 'application/ld+json',
      innerHTML: JSON.stringify({
        "@context": "https://schema.org",
        "@type": "WebApplication",
        "name": "Audit CV IA GoldArmy",
        "applicationCategory": "BusinessApplication",
        "operatingSystem": "All",
        "description": t('seo.free_cv.description'),
        "offers": {
          "@type": "Offer",
          "price": "0",
          "priceCurrency": "EUR"
        }
      })
    }
  ]
})

const file = ref(null)
const isDragging = ref(false)
const isAnalyzing = ref(false)
const result = ref(null) // { score: Number, flaws: Array }
const expandedIdx = ref(0) // Control the interactive accordion

const handleFileDrop = (e) => {
  e.preventDefault()
  isDragging.value = false
  const droppedFile = e.dataTransfer.files[0]
  if (droppedFile && droppedFile.type === 'application/pdf') {
    file.value = droppedFile
    analyzeFile()
  } else {
    alert("Veuillez uploader un fichier PDF.")
  }
}

const handleFileSelect = (e) => {
  const selectedFile = e.target.files[0]
  if (selectedFile && selectedFile.type === 'application/pdf') {
    file.value = selectedFile
    analyzeFile()
  }
}

const analyzeFile = async () => {
    isAnalyzing.value = true
    result.value = null
    
    const formData = new FormData()
    formData.append('file', file.value)
    
    try {
        const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'
        const response = await fetch(`${apiUrl}/api/public/mini-audit`, {
            method: 'POST',
            body: formData
        })
        
        const data = await response.json()
        if (data.status === 'success') {
            result.value = {
                score: data.score,
                flaws: data.flaws || []
            }
        } else {
            throw new Error("Erreur de l'API")
        }
    } catch (e) {
        console.error("Erreur d'analyse:", e)
        result.value = {
            score: 0,
            flaws: ["Impossible d'analyser le fichier.", "Le fichier est peut-être corrompu ou illisible.", "Veuillez vérifier votre connexion et réessayer."]
        }
    } finally {
        isAnalyzing.value = false
    }
}

const goToRegister = () => {
    router.push('/register')
}
</script>

<template>
  <div class="min-h-screen bg-[#0a0a12] text-white flex flex-col font-sans relative overflow-x-hidden selection:bg-violet-500/30">
    
    <!-- Background Elements with CSS Animations -->
    <div class="fixed inset-0 bg-[#0a0a12] pointer-events-none z-0"></div>
    <div class="fixed top-[-20%] left-[-10%] w-[50%] h-[50%] rounded-full bg-violet-600/10 blur-[150px] mix-blend-screen animate-blob pointer-events-none z-0"></div>
    <div class="fixed bottom-[-20%] right-[-10%] w-[50%] h-[50%] rounded-full bg-fuchsia-600/10 blur-[150px] mix-blend-screen animate-blob pointer-events-none z-0" style="animation-delay: 2s"></div>
    <div class="fixed top-[40%] left-[60%] w-[40%] h-[40%] rounded-full bg-indigo-600/10 blur-[150px] mix-blend-screen animate-blob pointer-events-none z-0" style="animation-delay: 4s"></div>
    <div class="fixed inset-0 opacity-20 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-indigo-900/40 via-transparent to-transparent pointer-events-none z-0"></div>

    <!-- ─── NAVBAR ─── -->
    <nav class="fixed top-6 inset-x-0 z-[100] px-6">
      <div class="max-w-7xl mx-auto flex items-center justify-between
                  bg-white/5 backdrop-blur-2xl border border-white/10
                  rounded-2xl px-6 py-4 shadow-2xl shadow-black/40">
        <!-- Logo -->
        <router-link to="/" class="flex items-center gap-3">
          <div class="w-9 h-9 rounded-xl overflow-hidden border border-violet-500/30 shadow-[0_0_20px_rgba(124,58,237,0.4)]">
            <img src="/logo.png" alt="Logo" class="w-full h-full object-cover" />
          </div>
          <span class="text-lg font-black tracking-tight uppercase text-white hover:text-violet-400 transition-colors">GoldArmy</span>
        </router-link>
        <!-- Links -->
        <div class="hidden md:flex items-center gap-6">
          <router-link to="/free-cv-roast" class="text-xs font-bold uppercase tracking-[0.2em] text-violet-400 hover:text-violet-300 transition-colors flex items-center gap-1.5">
             Audit CV
          </router-link>
          <router-link to="/free-interview" class="text-xs font-bold uppercase tracking-[0.2em] text-indigo-400 hover:text-indigo-300 transition-colors flex items-center gap-1.5">
             Simulation
          </router-link>
          <div class="h-4 w-px bg-white/10 mx-2"></div>
          <router-link to="/blog" class="text-xs font-bold uppercase tracking-[0.2em] text-fuchsia-400 hover:text-fuchsia-300 transition-colors">
            Blog
          </router-link>
        </div>
        <!-- CTA -->
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

    <!-- Main Container -->
    <main class="relative z-10 w-full flex-1 flex flex-col pt-32 pb-20 px-4 md:px-8">
        
        <!-- Hero & Tool Section (Split Layout on Desktop) -->
        <div class="max-w-[1400px] mx-auto w-full grid grid-cols-1 lg:grid-cols-2 gap-12 lg:gap-24 items-center mb-32">
            
            <!-- LEFT: Hero Copy -->
            <div class="text-left relative z-20">
                <div class="inline-flex items-center gap-3 px-4 py-2 rounded-full bg-surface-900/80 border border-white/5 backdrop-blur-md mb-8 shadow-2xl">
                    <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                    <span class="text-xs font-bold text-slate-300 tracking-widest uppercase">{{ t('free_cv.hero_badge') }}</span>
                </div>
                
                <h1 class="text-5xl sm:text-6xl md:text-7xl font-black tracking-tighter leading-[1.1] mb-6">
                    {{ t('free_cv.hero_title') }}
                    <span class="block text-transparent bg-clip-text bg-gradient-to-r from-violet-400 via-fuchsia-400 to-indigo-400 pb-2">{{ t('free_cv.hero_highlight') }}</span>
                </h1>
                
                <p class="text-lg md:text-xl text-slate-400 mb-10 max-w-lg font-medium leading-relaxed">
                    {{ t('free_cv.hero_subtitle1') }} <strong class="text-white">{{ t('free_cv.hero_error_bold') }}</strong> {{ t('free_cv.hero_subtitle2') }}
                </p>
                
                <div class="flex items-center gap-6 text-sm font-bold text-slate-500">
                    <div class="flex items-center gap-2">
                        <ShieldCheckIcon class="w-5 h-5 text-emerald-500" />
                        <span>{{ t('free_cv.confidential') }}</span>
                    </div>
                    <div class="flex items-center gap-2">
                        <DocumentTextIcon class="w-5 h-5 text-violet-400" />
                        <span>{{ t('free_cv.pdf_format') }}</span>
                    </div>
                </div>
            </div>

            <!-- RIGHT: Interactive Tool (Glassmorphism Modal) -->
            <div v-if="!result" class="relative w-full max-w-xl mx-auto lg:mx-0">
                <!-- Massive Background Glow for the tool -->
                <div class="absolute inset-0 bg-violet-600/20 blur-[120px] rounded-full pointer-events-none"></div>
                
                <div class="relative bg-surface-950/60 backdrop-blur-3xl border border-white/10 rounded-[2.5rem] p-8 sm:p-12 shadow-[0_0_80px_rgba(139,92,246,0.15)] overflow-hidden">
                    
                    <!-- Decorative corner glow inside modal -->
                    <div class="absolute -top-24 -right-24 w-48 h-48 bg-fuchsia-500/30 blur-[60px] rounded-full pointer-events-none"></div>

                    <!-- Intro State (Upload) -->
                    <template v-if="!isAnalyzing">
                        <div 
                            @dragover.prevent="isDragging = true"
                            @dragleave.prevent="isDragging = false"
                            @drop="handleFileDrop"
                            class="relative w-full border-2 border-dashed rounded-3xl p-10 text-center transition-all duration-300 cursor-pointer group bg-surface-900/30"
                            :class="isDragging ? 'border-violet-400 bg-violet-500/10 scale-[1.02]' : 'border-surface-700/50 hover:border-violet-500/50 hover:bg-surface-800/50'"
                            @click="$refs.fileInput.click()"
                        >
                        <div class="w-16 h-16 rounded-2xl bg-gradient-to-br from-surface-800 to-surface-900 border border-white/5 mx-auto flex items-center justify-center mb-6 shadow-xl group-hover:-translate-y-2 transition-transform duration-300">
                            <DocumentTextIcon class="w-8 h-8 text-violet-400 group-hover:text-fuchsia-400 transition-colors" />
                        </div>
                        <h3 class="text-2xl font-black text-white mb-2">{{ t('free_cv.upload_title') }}</h3>
                        <p class="text-sm text-slate-400 mb-8 font-medium">{{ t('free_cv.upload_subtitle') }}</p>
                        
                        <input type="file" ref="fileInput" @change="handleFileSelect" accept="application/pdf" class="hidden" />
                        
                        <button class="w-full bg-white text-black font-black uppercase tracking-widest text-sm py-4 rounded-xl shadow-lg transition-transform hover:scale-[1.02] active:scale-95 flex items-center justify-center gap-2">
                            <ArrowUpTrayIcon class="w-5 h-5" /> {{ t('free_cv.upload_button') }}
                        </button>
                    </div>
                </template>

                <!-- Analyzing State -->
                <template v-if="isAnalyzing">
                    <div class="w-full relative rounded-3xl p-10 text-center min-h-[400px] flex flex-col items-center justify-center">
                        <div class="relative w-32 h-32 mx-auto mb-10">
                            <!-- Scanning Laser -->
                            <div class="absolute inset-x-0 h-0.5 bg-fuchsia-500 shadow-[0_0_20px_#d946ef] animate-[scan_1.5s_ease-in-out_infinite] z-20"></div>
                            
                            <!-- Glowing Document -->
                            <div class="absolute inset-0 bg-violet-500/20 blur-xl rounded-full animate-pulse"></div>
                            <DocumentTextIcon class="w-full h-full text-violet-300 relative z-10 drop-shadow-[0_0_15px_rgba(167,139,250,0.5)]" />
                        </div>
                        
                        <h2 class="text-2xl font-black text-white mb-6">{{ t('free_cv.analyzing_title') }}</h2>
                        
                        <div class="flex flex-col gap-3 w-full max-w-[240px] mx-auto text-sm font-bold text-slate-400 text-left">
                            <div class="flex items-center gap-3 bg-surface-900/50 py-2 px-4 rounded-lg border border-white/5"><span class="w-2 h-2 rounded-full bg-emerald-500 shadow-[0_0_10px_#10b981] animate-ping"></span> {{ t('free_cv.analyzing_step1') }}</div>
                            <div class="flex items-center gap-3 bg-surface-900/50 py-2 px-4 rounded-lg border border-white/5"><span class="w-2 h-2 rounded-full bg-violet-500 shadow-[0_0_10px_#8b5cf6]"></span> {{ t('free_cv.analyzing_step2') }}</div>
                            <div class="flex items-center gap-3 bg-surface-900/50 py-2 px-4 rounded-lg border border-white/5 opacity-50"><span class="w-2 h-2 rounded-full bg-rose-500"></span> {{ t('free_cv.analyzing_step3') }}</div>
                        </div>
                    </div>
                </template>

                </div>
            </div>
            
        </div>

        <!-- Result State (FULL WIDTH) -->
        <template v-if="result && !isAnalyzing">
            <div class="max-w-[1000px] mx-auto w-full relative animate-fade-in-up z-20 mb-32">
                <!-- Glassmorphism Container for Full Width Results -->
                <div class="relative bg-surface-950/60 backdrop-blur-3xl border border-white/10 rounded-[2.5rem] p-8 md:p-12 shadow-[0_0_80px_rgba(139,92,246,0.15)] overflow-hidden">
                    <!-- Background Glow based on score -->
                    <div class="absolute -top-40 -right-40 w-96 h-96 blur-[100px] pointer-events-none opacity-30" :class="result.score > 70 ? 'bg-emerald-500' : (result.score > 40 ? 'bg-amber-500' : 'bg-rose-500')"></div>

                    <div class="flex flex-col items-center text-center relative z-10 mb-12">
                        <!-- Massive Score Circle -->
                        <div class="relative mb-8">
                            <svg class="w-56 h-56 transform -rotate-90">
                                <circle cx="112" cy="112" r="96" class="stroke-surface-800" stroke-width="10" fill="none" />
                                <circle cx="112" cy="112" r="96" :class="result.score > 70 ? 'stroke-emerald-400' : (result.score > 40 ? 'stroke-amber-400' : 'stroke-rose-400')" stroke-width="10" stroke-linecap="round" fill="none" :stroke-dasharray="603" :stroke-dashoffset="603 - (603 * result.score) / 100" class="transition-all duration-1000 ease-out drop-shadow-[0_0_20px_currentColor]" />
                            </svg>
                            <div class="absolute inset-0 flex flex-col items-center justify-center">
                                <span class="text-7xl font-black font-display text-white tracking-tighter">{{ result.score }}</span>
                                <span class="text-xs uppercase tracking-widest text-slate-400 font-bold mt-2">{{ t('free_cv.score_label') }}</span>
                            </div>
                        </div>
                        
                        <h3 class="text-3xl md:text-4xl font-black text-white mb-4">
                            {{ result.score > 70 ? t('free_cv.score_good') : t('free_cv.score_bad') }}
                        </h3>
                        <p class="text-slate-400 text-lg font-medium px-4 max-w-2xl mx-auto">
                            {{ t('free_cv.flaws_found', { count: result.flaws.length }) }}
                        </p>
                    </div>
                    
                    <!-- Flaws Grid (8 Unlocked, Accordion Style) -->
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8 text-left relative z-10">
                        <div v-for="(item, idx) in result.flaws.slice(0, 8)" :key="'unlocked-'+idx" 
                            @click="expandedIdx = expandedIdx === idx ? null : idx"
                            class="group relative bg-surface-900/60 backdrop-blur-sm border rounded-2xl p-5 cursor-pointer shadow-lg transition-all duration-300 overflow-hidden"
                            :class="expandedIdx === idx ? 'border-rose-500/50 shadow-[0_0_30px_rgba(244,63,94,0.15)] bg-surface-900' : 'border-white/5 hover:border-white/20 hover:bg-surface-800/80'"
                        >
                            <div class="flex items-start justify-between gap-4 relative z-10">
                                <div class="flex items-start gap-4 text-left">
                                    <div class="mt-0.5 w-8 h-8 rounded-full flex items-center justify-center shrink-0 border transition-colors duration-300"
                                         :class="expandedIdx === idx ? 'bg-rose-500/20 border-rose-500/30' : 'bg-surface-800 border-white/5'">
                                        <span class="text-xs font-black" :class="expandedIdx === idx ? 'text-rose-400' : 'text-slate-500'">0{{ idx + 1 }}</span>
                                    </div>
                                    <div>
                                        <span class="text-[10px] font-black tracking-widest uppercase mb-1 block transition-colors duration-300"
                                              :class="expandedIdx === idx ? 'text-rose-400' : 'text-slate-500'">{{ t('free_cv.faille_critique') }}</span>
                                        <span class="font-medium text-sm leading-relaxed transition-colors duration-300"
                                              :class="expandedIdx === idx ? 'text-white' : 'text-slate-300 group-hover:text-white'">
                                            {{ item.flaw || item }}
                                        </span>
                                    </div>
                                </div>
                                <div class="w-6 h-6 rounded-full border border-white/10 flex items-center justify-center shrink-0 transition-transform duration-300"
                                     :class="expandedIdx === idx ? 'bg-white/10 -rotate-180' : 'bg-transparent'">
                                    <svg v-if="expandedIdx !== idx" class="w-3 h-3 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M19 9l-7 7-7-7" /></svg>
                                    <svg v-else class="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 15l7-7 7 7" /></svg>
                                </div>
                            </div>
                            <div class="grid transition-all duration-300 ease-in-out text-left"
                                 :class="expandedIdx === idx ? 'grid-rows-[1fr] mt-0 opacity-100' : 'grid-rows-[0fr] opacity-0'">
                                <div class="overflow-hidden">
                                    <div v-if="item.correction" class="pt-4 mt-4 border-t border-white/5 flex items-start gap-3 relative before:absolute before:left-[11px] before:-top-4 before:w-[2px] before:h-4 before:bg-surface-800">
                                        <div class="mt-0.5 bg-emerald-500/10 p-1 rounded-md border border-emerald-500/20 relative z-10 shrink-0">
                                            <CheckCircleIcon class="w-4 h-4 text-emerald-400" />
                                        </div>
                                        <div>
                                            <span class="text-[10px] font-black tracking-widest text-emerald-400 uppercase mb-1 block">{{ t('free_cv.correction_title') }}</span>
                                            <span class="text-slate-300 font-medium text-sm leading-relaxed">{{ item.correction }}</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div class="absolute inset-0 bg-gradient-to-br from-rose-500/5 to-transparent pointer-events-none transition-opacity duration-300"
                                 :class="expandedIdx === idx ? 'opacity-100' : 'opacity-0'"></div>
                        </div>
                    </div>

                    <!-- Locked Flaws Container (FOMO) -->
                    <div v-if="result.flaws.length > 8" class="relative mt-2 z-10">
                        <div class="absolute inset-0 bg-gradient-to-b from-transparent via-surface-950/90 to-surface-950 z-10 pointer-events-none rounded-2xl"></div>
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div v-for="(flaw, idx) in result.flaws.slice(8)" :key="'locked-'+idx" 
                                class="bg-surface-900/40 border border-white/5 rounded-2xl p-5 flex items-center gap-4 opacity-40 blur-[2px] select-none text-left">
                                <div class="w-8 h-8 rounded-full flex items-center justify-center shrink-0 border bg-surface-800 border-white/5">
                                    <LockClosedIcon class="w-4 h-4 text-slate-500" />
                                </div>
                                <div>
                                    <span class="text-[10px] font-black tracking-widest uppercase mb-1 block text-slate-600">{{ t('free_cv.locked_fails') }}</span>
                                    <span class="font-medium text-sm text-slate-500">{{ t('free_cv.locked_subtitle') }}</span>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Floating Lock CTA over the blurred area -->
                        <div class="absolute inset-0 z-20 flex flex-col items-center justify-center p-6 text-center">
                            <div class="w-14 h-14 bg-rose-500/20 rounded-full flex items-center justify-center mb-4 border border-rose-500/30 shadow-[0_0_40px_rgba(244,63,94,0.4)]">
                                <LockClosedIcon class="w-7 h-7 text-rose-400" />
                            </div>
                            <span class="text-white font-black text-2xl drop-shadow-md">{{ t('free_cv.locked_count_cta', { count: result.flaws.length - 8 }) }}</span>
                        </div>
                    </div>

                    <!-- CTA Callout -->
                    <div class="mt-12 bg-gradient-to-br from-violet-600 to-indigo-600 rounded-3xl p-8 md:p-10 text-center text-white shadow-2xl relative overflow-hidden group mx-auto max-w-3xl">
                        <div class="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/stardust.png')] mix-blend-overlay opacity-20"></div>
                        <h4 class="font-black text-2xl md:text-3xl mb-3 relative z-10">{{ t('free_cv.cta_unlock_title') }}</h4>
                        <p class="text-violet-200 mb-8 font-medium relative z-10 text-base md:text-lg">{{ t('free_cv.cta_unlock_subtitle', { count: result.flaws.length }) }}</p>
                        
                        <button @click="goToRegister" class="w-full bg-white text-indigo-950 font-black uppercase tracking-widest py-5 rounded-2xl shadow-[0_0_30px_rgba(255,255,255,0.3)] transition-transform group-hover:scale-[1.02] active:scale-95 flex items-center justify-center gap-2 relative z-10 text-lg">
                            {{ t('free_cv.cta_unlock_button') }} <ArrowRightIcon class="w-6 h-6" />
                        </button>
                    </div>
                    
                    <button @click="result = null; file = null" class="w-full mt-8 text-sm font-bold text-slate-500 hover:text-white transition-colors uppercase tracking-widest py-4">
                        {{ t('free_cv.scan_another') }}
                    </button>
                </div>
            </div>
        </template>

        <!-- Bento Box Explanatory Section -->
        <section class="max-w-[1400px] mx-auto w-full pt-20 border-t border-white/5 relative z-10">
            <div class="text-center mb-20">
                <span class="text-fuchsia-400 text-xs font-black uppercase tracking-[0.2em] mb-4 block">{{ t('free_cv.bento_tagline') }}</span>
                <h2 class="text-4xl md:text-6xl font-black mb-6 tracking-tight">{{ t('free_cv.bento_title1') }} <span class="italic font-display text-slate-500">{{ t('free_cv.bento_title2') }}</span></h2>
            </div>

            <!-- Asymmetrical Bento Grid -->
            <div class="grid grid-cols-1 md:grid-cols-4 md:grid-rows-2 gap-6 h-auto md:h-[600px] mb-32">
                
                <!-- BENTO 1: Large Feature -->
                <div class="md:col-span-2 md:row-span-2 bg-gradient-to-br from-surface-900 to-[#0a0a12] border border-white/5 rounded-[2.5rem] p-10 relative overflow-hidden group">
                    <div class="absolute top-0 right-0 w-full h-full bg-[radial-gradient(circle_at_top_right,_var(--tw-gradient-stops))] from-violet-500/10 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-700"></div>
                    <div class="w-16 h-16 bg-violet-500/10 rounded-2xl flex items-center justify-center text-violet-400 font-black text-2xl mb-8 border border-violet-500/20 shadow-[0_0_30px_rgba(139,92,246,0.2)]">1</div>
                    <h3 class="text-3xl font-black mb-4">{{ t('free_cv.bento_feature1_title') }}</h3>
                    <p class="text-slate-400 text-lg leading-relaxed max-w-md">
                        {{ t('free_cv.bento_feature1_desc') }}
                    </p>
                    <div class="mt-10 h-32 bg-surface-950 rounded-2xl border border-surface-800 flex items-end justify-center p-4 overflow-hidden relative">
                        <div class="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/cubes.png')] opacity-20"></div>
                        <div class="flex gap-2 items-end w-full max-w-[200px] h-full">
                            <div class="w-1/3 bg-rose-500 rounded-t-sm h-[20%] animate-pulse"></div>
                            <div class="w-1/3 bg-amber-500 rounded-t-sm h-[40%] animate-pulse" style="animation-delay: 0.2s"></div>
                            <div class="w-1/3 bg-emerald-500 rounded-t-sm h-[90%] shadow-[0_0_20px_#10b981] animate-pulse" style="animation-delay: 0.4s"></div>
                        </div>
                    </div>
                </div>

                <!-- BENTO 2: Top Right Small -->
                <div class="md:col-span-2 md:row-span-1 bg-surface-900 border border-white/5 rounded-[2.5rem] p-10 relative overflow-hidden">
                    <div class="w-12 h-12 bg-rose-500/10 rounded-xl flex items-center justify-center text-rose-400 font-black text-xl mb-4 border border-rose-500/20">2</div>
                    <h3 class="text-2xl font-black mb-3 text-white">{{ t('free_cv.bento_feature2_title') }}</h3>
                    <p class="text-slate-400 text-sm leading-relaxed max-w-sm">
                        {{ t('free_cv.bento_feature2_desc') }}
                    </p>
                </div>

                <!-- BENTO 3: Bottom Right Small -->
                <div class="md:col-span-2 md:row-span-1 bg-surface-900 border border-white/5 rounded-[2.5rem] p-10 relative overflow-hidden group">
                    <div class="absolute inset-0 bg-gradient-to-r from-emerald-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
                    <div class="w-12 h-12 bg-emerald-500/10 rounded-xl flex items-center justify-center text-emerald-400 font-black text-xl mb-4 border border-emerald-500/20">3</div>
                    <h3 class="text-2xl font-black mb-3 text-white">{{ t('free_cv.bento_feature3_title') }}</h3>
                    <p class="text-slate-400 text-sm leading-relaxed max-w-sm">
                        {{ t('free_cv.bento_feature3_desc') }}
                    </p>
                </div>

            </div>

            <!-- Massive SEO Content: How It Works & FAQ -->
            <section class="max-w-4xl mx-auto w-full pt-12 pb-24 text-left px-4">
                <article class="prose prose-invert prose-lg max-w-none">
                    <h2 class="text-3xl font-black text-white mb-6">{{ t('free_cv.seo_article_title') }}</h2>
                    <p class="text-slate-400 mb-6 leading-relaxed">
                        {{ t('free_cv.seo_article_p1') }}
                        {{ t('free_cv.seo_article_p2') }}
                    </p>
                    
                    <h3 class="text-2xl font-bold text-white mt-12 mb-4">{{ t('free_cv.seo_article_h3') }}</h3>
                    <ul class="text-slate-400 mb-10 space-y-3 list-disc pl-6 marker:text-violet-500">
                        <li>{{ t('free_cv.seo_article_li1') }}</li>
                        <li>{{ t('free_cv.seo_article_li2') }}</li>
                        <li>{{ t('free_cv.seo_article_li3') }}</li>
                    </ul>

                    <h2 class="text-3xl font-black text-white mt-16 mb-8">{{ t('free_cv.faq_title') }}</h2>
                    
                    <div class="space-y-6">
                        <details class="bg-surface-900/50 border border-white/5 rounded-2xl p-6 group cursor-pointer hover:bg-surface-800/50 transition-colors">
                            <summary class="text-xl font-bold text-white list-none flex justify-between items-center">
                                {{ t('free_cv.faq_q1') }}
                                <span class="text-violet-400 group-open:rotate-180 transition-transform">▼</span>
                            </summary>
                            <p class="text-slate-400 mt-4 leading-relaxed">
                                {{ t('free_cv.faq_a1') }}
                            </p>
                        </details>
                        
                        <details class="bg-surface-900/50 border border-white/5 rounded-2xl p-6 group cursor-pointer hover:bg-surface-800/50 transition-colors">
                            <summary class="text-xl font-bold text-white list-none flex justify-between items-center">
                                {{ t('free_cv.faq_q2') }}
                                <span class="text-violet-400 group-open:rotate-180 transition-transform">▼</span>
                            </summary>
                            <p class="text-slate-400 mt-4 leading-relaxed">
                                {{ t('free_cv.faq_a2') }}
                            </p>
                        </details>

                        <details class="bg-surface-900/50 border border-white/5 rounded-2xl p-6 group cursor-pointer hover:bg-surface-800/50 transition-colors">
                            <summary class="text-xl font-bold text-white list-none flex justify-between items-center">
                                {{ t('free_cv.faq_q3') }}
                                <span class="text-violet-400 group-open:rotate-180 transition-transform">▼</span>
                            </summary>
                            <p class="text-slate-400 mt-4 leading-relaxed">
                                {{ t('free_cv.faq_a3') }}
                            </p>
                        </details>
                    </div>
                </article>
            </section>

            <!-- Massive Footer CTA -->
            <div class="relative w-full rounded-[3rem] p-16 md:p-24 text-center overflow-hidden border border-white/10 bg-surface-950">
                <!-- Glowing orb behind -->
                <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-gradient-to-tr from-violet-600/20 to-fuchsia-600/20 blur-[120px] rounded-full pointer-events-none"></div>
                
                <h3 class="text-4xl md:text-6xl font-black mb-6 tracking-tight relative z-10 text-white">{{ t('free_cv.final_cta_title') }}</h3>
                <p class="text-slate-400 text-lg md:text-xl mb-12 max-w-2xl mx-auto relative z-10">
                    {{ t('free_cv.final_cta_desc') }}
                </p>
                
                <router-link to="/register" class="relative z-10 inline-flex items-center justify-center bg-white text-black font-black uppercase tracking-widest text-sm px-12 py-6 rounded-2xl shadow-[0_0_40px_rgba(255,255,255,0.2)] hover:scale-105 hover:shadow-[0_0_60px_rgba(255,255,255,0.4)] active:scale-95 transition-all">
                    {{ t('free_cv.final_cta_button') }}
                </router-link>
            </div>
        </section>
    </main>

    <!-- Global Footer -->
    <Footer />
  </div>
</template>

<style scoped>
@keyframes scan {
  0% { top: 0; opacity: 0; }
  10% { opacity: 1; }
  90% { opacity: 1; }
  100% { top: 100%; opacity: 0; }
}
</style>
