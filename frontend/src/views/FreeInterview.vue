<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useHead } from '@unhead/vue'
import { useI18n } from 'vue-i18n'
import Footer from '../components/Footer.vue'
import LandingNav from '../components/LandingNav.vue'
import {
  MicrophoneIcon,
  StopIcon,
  PlayIcon,
  VideoCameraIcon,
  PhoneXMarkIcon,
  SparklesIcon,
  CpuChipIcon,
  ChartBarIcon,
  PencilSquareIcon,
  QuestionMarkCircleIcon
} from '@heroicons/vue/24/solid'
import { ShieldCheckIcon } from '@heroicons/vue/24/outline'

const { t, locale } = useI18n()
const router = useRouter()

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

// SEO optimization using @unhead/vue
useHead({
  title: computed(() => t('seo.free_interview.title')),
  meta: [
    { name: 'description', content: computed(() => t('seo.free_interview.description')) },
    { property: 'og:title', content: computed(() => t('seo.free_interview.og_title')) },
    { property: 'og:description', content: computed(() => t('seo.free_interview.og_description')) }
  ],
  script: [
    {
      type: 'application/ld+json',
      innerHTML: JSON.stringify({
        "@context": "https://schema.org",
        "@type": "WebApplication",
        "name": "Simulateur Entretien IA GoldArmy",
        "applicationCategory": "EducationalApplication",
        "operatingSystem": "All",
        "description": t('seo.free_interview.description'),
        "offers": {
          "@type": "Offer",
          "price": "0",
          "priceCurrency": "EUR"
        }
      })
    }
  ]
})

// States
const step = ref('intro') // intro -> connecting -> interviewing -> feedback
const jobTitle = ref('')
const isProcessing = ref(false)

// Interview variables
const question = ref('')
const userAnswer = ref('')
const feedback = ref(null)

const interviewType = ref('Général')
const interviewTypes = ['Général', 'Technique', 'Ressources Humaines', 'Culture Fit', 'Management']
const openFaqIndex = ref(null)

const faqItems = computed(() => [
  { q: t('free_interview.faq_q1'), a: t('free_interview.faq_a1') },
  { q: t('free_interview.faq_q2'), a: t('free_interview.faq_a2') },
  { q: t('free_interview.faq_q3'), a: t('free_interview.faq_a3') }
])
const interviewReasons = computed(() => {
  const li1 = t('free_interview.seo_article_li1')
  const li2 = t('free_interview.seo_article_li2')
  const li3 = t('free_interview.seo_article_li3')
  const split = (s) => {
    const i = s.indexOf(': ')
    return i >= 0 ? { title: s.slice(0, i).trim(), desc: s.slice(i + 2).trim() } : { title: s, desc: '' }
  }
  return [split(li1), split(li2), split(li3)]
})

// Web Speech API references
let synthesis = null
let recognition = null
const isListening = ref(false)

// Helper to get locale for Web Speech API
const speechLocale = computed(() => {
    return locale.value === 'fr' ? 'fr-FR' : 'en-US'
})

onMounted(() => {
    synthesis = window.speechSynthesis
    initRecognition()
})

const initRecognition = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
    if (SpeechRecognition) {
        if (recognition) recognition.stop()
        recognition = new SpeechRecognition()
        recognition.lang = speechLocale.value
        recognition.continuous = true
        recognition.interimResults = true
        
        recognition.onresult = (event) => {
            let finalTranscript = ''
            for (let i = event.resultIndex; i < event.results.length; ++i) {
                if (event.results[i].isFinal) {
                    finalTranscript += event.results[i][0].transcript
                }
            }
            if (finalTranscript) userAnswer.value += " " + finalTranscript
        }
        
        recognition.onend = () => {
            isListening.value = false
        }
    }
}

// Re-init recognition if language changes
watch(speechLocale, () => {
    initRecognition()
})

onUnmounted(() => {
    if (synthesis) synthesis.cancel()
    if (recognition) recognition.stop()
})

const getBestVoice = (lang) => {
    if (!synthesis) return null;
    const voices = synthesis.getVoices();
    if (!voices.length) return null;

    // Filter by exact language or primary language tag (e.g. 'fr-FR' or 'fr')
    const langVoices = voices.filter(v => v.lang.startsWith(lang) || v.lang.replace('_', '-').startsWith(lang));
    
    if (langVoices.length === 0) return voices[0];
    
    // Priority: Premium/Natural > Google > Microsoft > Default
    const premiumKeywords = ['premium', 'natural', 'neural', 'wavenet'];
    for (const kw of premiumKeywords) {
        const found = langVoices.find(v => v.name.toLowerCase().includes(kw));
        if (found) return found;
    }
    
    const googleVoice = langVoices.find(v => v.name.toLowerCase().includes('google'));
    if (googleVoice) return googleVoice;
    
    const msVoice = langVoices.find(v => v.name.toLowerCase().includes('microsoft'));
    if (msVoice) return msVoice;
    
    return langVoices[0];
}

const speakText = (text, onEndCallback = null) => {
    if (!synthesis) return
    synthesis.cancel()
    const utterance = new SpeechSynthesisUtterance(text)
    
    const baseLang = speechLocale.value.split('-')[0]; // 'fr' or 'en'
    const bestVoice = getBestVoice(baseLang);
    if (bestVoice) {
        utterance.voice = bestVoice;
    }
    
    utterance.lang = speechLocale.value
    utterance.rate = 1.05
    utterance.pitch = 0.95 // Slightly deeper, more professional voice
    
    if (onEndCallback) {
        utterance.onend = onEndCallback
    }
    synthesis.speak(utterance)
}

const startCall = async () => {
    if (!jobTitle.value.trim()) return
    step.value = 'connecting'
    
    try {
        const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'
        const res = await fetch(`${apiUrl}/api/public/interview`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                job_title: jobTitle.value,
                interview_type: interviewType.value,
                locale: locale.value 
            })
        })
        const data = await res.json()
        if (data.status === 'success') {
            question.value = data.text
            step.value = 'interviewing'
            
            // Wait a sec to "connect", then speak
            setTimeout(() => {
                speakText(question.value)
            }, 1000)
            
        } else {
            throw new Error("API Exception")
        }
    } catch(err) {
        alert(t('common.error') + ": " + err.message)
        step.value = 'intro'
    }
}

const toggleRecording = () => {
    if (!recognition) {
        alert(t('free_interview.recognition_error'))
        return
    }
    
    if (isListening.value) {
        recognition.stop()
    } else {
        synthesis.cancel() // Stop AI if it's still talking
        userAnswer.value = ''
        try {
            recognition.start()
            isListening.value = true
        } catch(e) { console.error(e) }
    }
}

const submitAnswer = async () => {
    if(isListening.value) {
        recognition.stop()
        isListening.value = false
    }
    
    if (!userAnswer.value.trim()) {
        alert(t('free_interview.empty_answer'))
        return
    }
    
    isProcessing.value = true
    
    try {
        const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'
        const res = await fetch(`${apiUrl}/api/public/interview`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                job_title: jobTitle.value,
                interview_type: interviewType.value,
                context: question.value,
                user_response: userAnswer.value,
                locale: locale.value
            })
        })
        const data = await res.json()
        if (data.status === 'success') {
            feedback.value = data.text
            step.value = 'feedback'
            speakText(feedback.value)
        }
    } catch(err) {
        console.error(err)
    } finally {
        isProcessing.value = false
    }
}

const endCall = () => {
    synthesis.cancel()
    router.push('/')
}
</script>

<template>
  <div class="page-wrapper page-wrapper--interview">
    <LandingNav />
    <main class="main dark-secondary">
    <!-- Simulator full-page when intro: show hero + card; when connecting/interviewing/feedback: show that view -->
    <template v-if="step === 'intro'">
      <section class="section hero-1">
        <div class="hero-content">
          <div class="w-layout-grid hero1-grid interview-hero-grid">
            <div class="hero-left-col">
              <div class="hero-text-wrap">
                <span class="interview-badge">{{ t('free_interview.hero_badge') }}</span>
                <h1 class="hero-heading interview-hero-heading">
                  <span class="interview-hero-line1">{{ t('free_interview.hero_title_part1') }}</span>
                  <span class="tertiary-color-emphasis interview-hero-emphasis">{{ t('free_interview.hero_title_italic') }}</span>
                  <span class="interview-hero-line2">{{ t('free_interview.hero_title_highlight') }}</span>
                </h1>
                <p class="hero-paragraph">{{ t('free_interview.hero_subtitle') }}</p>
                <div class="interview-trust">
                  <span class="trust-item"><MicrophoneIcon class="trust-icon" /> {{ t('free_interview.mic_required') }}</span>
                  <span class="trust-item"><ShieldCheckIcon class="trust-icon" /> {{ t('free_interview.no_recording') }}</span>
        </div>
      </div>
            </div>
            <div class="interview-intro-col">
              <div class="interview-intro-card">
                <div class="interview-type-wrap">
                  <button v-for="type in interviewTypes" :key="type" type="button" @click="interviewType = type" :class="['interview-type-btn', { 'interview-type-btn--active': interviewType === type }]">{{ type }}</button>
                </div>
                <input v-model="jobTitle" @keyup.enter="startCall" type="text" :placeholder="t('free_interview.job_placeholder')" class="interview-job-input" />
                <button type="button" @click="startCall" :disabled="!jobTitle.trim()" class="interview-start-btn">
                  <VideoCameraIcon class="btn-icon-svg" /> {{ t('free_interview.start_button') }}
                </button>
            </div>
            </div>
            </div>
        </div>
      </section>
    </template>
    <template v-else-if="step === 'connecting'">
      <section class="section interview-connecting">
        <div class="interview-connecting-card">
          <div class="interview-spinner"></div>
          <h2 class="interview-connecting-title">{{ t('free_interview.connecting') }}</h2>
          <p class="interview-connecting-sub">{{ t('free_interview.secure_channel') }}</p>
    </div>
      </section>
    </template>
    <div v-else-if="step === 'interviewing' || step === 'feedback'" class="interview-simulator-wrap">
      <div class="interview-simulator-container">
      <div class="interview-panels flex-1 flex flex-col z-10 pt-8 pb-32 px-4 sm:px-8 w-full max-w-6xl mx-auto relative">
        
        <!-- Glowing Ambient Lights for HUD -->
        <div class="absolute top-1/4 left-1/4 w-96 h-96 bg-indigo-600/10 blur-[100px] pointer-events-none rounded-full"></div>
        <div class="absolute bottom-1/4 right-1/4 w-96 h-96 bg-fuchsia-600/10 blur-[100px] pointer-events-none rounded-full"></div>

        <!-- Video Grid: Asymmetrical Floating Panels -->
        <div class="flex-1 grid grid-cols-1 lg:grid-cols-12 gap-6 lg:gap-8 w-full relative z-10">
            
            <!-- Recruiter (AI) - Primary Focus -->
            <div class="lg:col-span-8 bg-surface-950/40 backdrop-blur-3xl border border-white/10 rounded-[2.5rem] relative overflow-hidden flex flex-col shadow-[0_20px_80px_-20px_rgba(79,70,229,0.15)]">
                
                <!-- AI Avatar Container -->
                <div class="flex-1 flex flex-col items-center justify-center p-12 relative">
                    <!-- Audio Visualizer Rings effect -->
                    <div class="absolute inset-x-0 bottom-0 h-1/2 bg-gradient-to-t from-indigo-900/30 to-transparent pointer-events-none"></div>
                    
                    <div class="relative w-64 h-64">
                        <!-- Ripple effect when AI talks -->
                        <div class="absolute inset-0 bg-indigo-500 rounded-full animate-ping opacity-10 scale-150" v-if="(step === 'interviewing' && userAnswer === '') || step === 'feedback'"></div>
                        <div class="absolute inset-0 bg-fuchsia-400 rounded-full animate-pulse opacity-5 scale-[1.2]" v-if="(step === 'interviewing' && userAnswer === '') || step === 'feedback'"></div>
                        
                        <img src="/avatars/tech.png" :alt="t('free_interview.recruiter_alt')" class="w-full h-full rounded-full object-cover border-[4px] border-indigo-500/20 relative z-10 shadow-[0_0_50px_rgba(99,102,241,0.2)] bg-[#0d1117] p-2" />
                    </div>
                </div>
                
                <!-- Subtitles / Feedback area HUD style -->
                <div class="absolute bottom-6 inset-x-6 sm:bottom-8 sm:inset-x-10">
                    <div class="bg-surface-900/60 backdrop-blur-2xl rounded-3xl p-6 sm:p-8 border border-white/10 shadow-2xl relative overflow-hidden flex flex-col items-center text-center">
                        <div class="absolute top-0 inset-x-0 h-1 bg-gradient-to-r from-transparent via-indigo-500 to-transparent opacity-50"></div>
                        
                        <p class="text-xs font-black text-indigo-300 uppercase tracking-[0.2em] mb-4 flex items-center justify-center gap-2">
                            <span class="w-2 h-2 rounded-full bg-indigo-500 animate-pulse shadow-[0_0_10px_#6366f1]" v-if="(step === 'interviewing' && userAnswer === '') || step === 'feedback'"></span>
                            <span class="w-2 h-2 rounded-full bg-slate-600" v-else></span>
                            {{ t('free_interview.recruiter_label') }}
                        </p>
                        
                        <p class="text-xl sm:text-3xl xl:text-4xl font-semibold leading-relaxed font-sans text-white" v-if="step === 'interviewing'">
                            "{{ question }}"
                        </p>
                        <p class="text-xl sm:text-3xl xl:text-4xl font-semibold leading-relaxed text-indigo-300 font-sans" v-else-if="step === 'feedback'">
                            "{{ feedback }}"
                        </p>
                    </div>
                </div>
            </div>

            <!-- User (You) - Sidebar Panel -->
            <div class="lg:col-span-4 flex flex-col gap-6">
                
                <!-- User Webcam Placeholder -->
                <div class="bg-surface-950/40 backdrop-blur-xl rounded-[2.5rem] border border-white/10 relative overflow-hidden flex flex-col aspect-square lg:aspect-auto lg:h-[40%] shadow-[0_20px_40px_-10px_rgba(0,0,0,0.5)]">
                    <div class="flex-1 flex items-center justify-center p-8 relative">
                         <!-- User speaking radar -->
                        <div v-if="isListening" class="absolute inset-0 bg-gradient-to-t from-rose-500/10 to-transparent animate-pulse"></div>
                        <div class="w-24 h-24 rounded-full bg-slate-800/80 backdrop-blur-md flex items-center justify-center border border-white/20 shadow-2xl relative z-10">
                            <span class="text-2xl text-slate-400 font-bold uppercase tracking-widest">{{ t('free_interview.you_label') }}</span>
                        </div>
                    </div>
                </div>
                
                <!-- Live Transcription Box -->
                <div class="bg-surface-950/40 backdrop-blur-xl rounded-[2.5rem] border border-white/10 relative flex flex-col flex-1 shadow-[0_20px_40px_-10px_rgba(0,0,0,0.5)] overflow-hidden">
                    <div class="absolute top-0 right-0 w-48 h-48 bg-rose-500/5 blur-[50px] pointer-events-none"></div>

                    <div class="p-8 flex flex-col h-full justify-between relative z-10">
                        <div>
                            <p class="text-[10px] font-black uppercase tracking-[0.2em] mb-4 flex items-center gap-2" :class="isListening ? 'text-rose-400' : 'text-slate-500'">
                                <span v-if="isListening" class="w-2 h-2 rounded-full bg-rose-500 animate-pulse shadow-[0_0_10px_#f43f5e]"></span>
                                {{ isListening ? t('free_interview.live_transcription') : t('free_interview.waiting_label') }}
                            </p>
                            
                            <p class="text-base text-slate-300 font-medium leading-relaxed" v-if="step === 'interviewing'">
                                {{ userAnswer || (isListening ? t('free_interview.speak_now') : t('free_interview.mic_instruction')) }}
                            </p>
                        </div>
                    </div>
                </div>

                <!-- Final CTA Overlay (if feedback is given) -->
                <div v-if="step === 'feedback'" class="absolute inset-0 z-50 bg-surface-950/90 backdrop-blur-3xl flex flex-col items-center justify-center p-8 text-center animate-fade-in border border-indigo-500/30 rounded-[3rem] shadow-[0_0_100px_rgba(99,102,241,0.2)]">
                    <div class="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/cubes.png')] opacity-10"></div>
                    
                    <div class="relative z-10 flex flex-col items-center">
                        <div class="w-20 h-20 bg-gradient-to-br from-indigo-500 to-fuchsia-600 rounded-3xl flex items-center justify-center mb-8 shadow-[0_0_40px_rgba(139,92,246,0.4)]">
                            <SparklesIcon class="w-10 h-10 text-white" />
                        </div>
                        <h3 class="text-4xl md:text-5xl font-black mb-6 text-white tracking-tight">{{ t('free_interview.end_simulation_title') }}</h3>
                        <p class="text-slate-400 text-lg md:text-xl mb-12 max-w-xl leading-relaxed">
                            {{ t('free_interview.end_simulation_desc') }}
                        </p>
                        
                        <button @click="router.push('/register')" class="bg-white text-indigo-950 font-black uppercase tracking-widest text-sm px-12 py-6 rounded-2xl shadow-[0_0_40px_rgba(255,255,255,0.2)] hover:scale-[1.02] active:scale-95 transition-all mb-6">
                            {{ t('free_interview.create_account') }}
                        </button>
                        <button @click="endCall" class="text-xs font-bold text-slate-500 hover:text-white uppercase tracking-widest transition-colors py-2">
                            {{ t('free_interview.exit_call') }}
                        </button>
                    </div>
                </div>

            </div>
        </div>

        <!-- Zoom Controls Bar (Floating Dock) -->
        <div class="absolute bottom-8 inset-x-0 flex justify-center z-[60] pointer-events-none px-4">
            <div class="bg-surface-900/80 backdrop-blur-3xl border border-white/10 p-3 sm:p-4 rounded-[2rem] flex items-center gap-3 sm:gap-6 shadow-[0_30px_60px_rgba(0,0,0,0.6)] pointer-events-auto transition-transform hover:-translate-y-1 duration-300">
                
                <!-- Mic Toggle -->
                <div class="flex flex-col items-center">
                    <button @click="toggleRecording" :disabled="step !== 'interviewing'" class="w-16 h-16 sm:w-20 sm:h-20 rounded-[1.5rem] flex items-center justify-center transition-all duration-300 shadow-xl" :class="isListening ? 'bg-rose-500 text-white hover:bg-rose-600 border border-rose-400 shadow-[0_0_30px_rgba(244,63,94,0.4)] scale-105' : 'bg-surface-800 text-slate-300 hover:bg-surface-700 hover:text-white border border-white/10 disabled:opacity-50 disabled:cursor-not-allowed'">
                        <MicrophoneIcon class="w-7 h-7 sm:w-8 sm:h-8" v-if="!isListening" />
                        <StopIcon class="w-7 h-7 sm:w-8 sm:h-8" v-else />
                    </button>
                    <span class="text-xs font-bold mt-3 uppercase tracking-widest hidden sm:block transition-colors" :class="isListening ? 'text-rose-400' : 'text-slate-500'">{{ isListening ? t('free_interview.dock_stop') : t('free_interview.dock_talk') }}</span>
                </div>

                <div class="w-px h-12 bg-white/10 mx-2"></div>

                <!-- Submit Answer -->
                <div class="flex flex-col items-center">
                    <button @click="submitAnswer" :disabled="step !== 'interviewing' || !userAnswer || isProcessing" class="px-8 h-14 sm:h-16 rounded-2xl flex items-center gap-3 transition-all duration-300 shadow-lg text-sm sm:text-base font-black tracking-wide uppercase" :class="userAnswer && !isProcessing ? 'bg-indigo-600 hover:bg-indigo-500 text-white shadow-[0_0_20px_rgba(79,70,229,0.3)]' : 'bg-surface-800 text-slate-500 border border-white/5 disabled:opacity-50 disabled:cursor-not-allowed'">
                        <span v-if="isProcessing" class="w-5 h-5 rounded-full border-2 border-white/30 border-t-white animate-spin"></span>
                        <PlayIcon v-else class="w-5 h-5" />
                        {{ isProcessing ? t('free_interview.dock_analyzing') : t('free_interview.dock_validate') }}
                    </button>
                    <span class="text-[10px] font-bold text-transparent mt-2 hidden sm:block">.</span>
                </div>

                <div class="w-px h-10 bg-white/10 mx-2"></div>

                <!-- End Call -->
                <div class="flex flex-col items-center">
                    <button @click="endCall" class="w-14 h-14 sm:w-16 sm:h-16 rounded-2xl bg-rose-600 hover:bg-rose-500 text-white flex items-center justify-center transition-all duration-300 shadow-[0_0_20px_rgba(225,29,72,0.3)]">
                        <PhoneXMarkIcon class="w-6 h-6 sm:w-7 sm:h-7" />
                    </button>
                    <span class="text-[10px] font-bold text-slate-500 mt-2 uppercase tracking-widest hidden sm:block">{{ t('free_interview.dock_exit') }}</span>
                </div>
            </div>
        </div>

    </div>
      </div>
    </div>

    <!-- 3 colonnes (bento) -->
    <section class="section home1-3col">
      <div class="w-layout-blockcontainer container w-container">
        <div class="_3cols-heading">
          <h3 class="center-align">{{ t('free_interview.bento_title1') }} <span class="tertiary-color-emphasis">{{ t('free_interview.bento_title2') }}</span></h3>
          <p class="fsize-body-large center-align">{{ t('free_interview.bento_tagline') }}</p>
        </div>
        <div class="w-layout-grid home1-3cols">
          <div class="card-item-home1">
            <div class="card-item-img-wrap card-item-img-wrap--num">1</div>
            <div class="card-text-content-home1">
              <h4 class="fsize-xxs">{{ t('free_interview.bento_feature1_title') }}</h4>
              <p>{{ t('free_interview.bento_feature1_desc') }}</p>
            </div>
          </div>
          <div class="card-item-home1">
            <div class="card-item-img-wrap card-item-img-wrap--num">2</div>
            <div class="card-text-content-home1">
              <h4 class="fsize-xxs">{{ t('free_interview.bento_feature2_title') }}</h4>
              <p>{{ t('free_interview.bento_feature2_desc') }}</p>
            </div>
          </div>
          <div class="card-item-home1">
            <div class="card-item-img-wrap card-item-img-wrap--num">3</div>
            <div class="card-text-content-home1">
              <h4 class="fsize-xxs">{{ t('free_interview.bento_feature3_title') }}</h4>
              <p>{{ t('free_interview.bento_feature3_desc') }}</p>
            </div>
                        </div>
                    </div>
                </div>
    </section>

    <!-- Bloc SEO + FAQ (design type ATS) -->
    <section class="interview-ats-block">
      <div class="ats-block-inner">
        <div class="ats-badge">IA & Voix</div>
        <h2 class="ats-main-title">{{ t('free_interview.seo_article_h2') }}</h2>
        <div class="ats-intro">
          <p class="ats-intro-p">{{ t('free_interview.seo_article_p1') }}</p>
        </div>
        <h3 class="ats-subtitle">{{ t('free_interview.seo_article_h3') }}</h3>
        <div class="ats-reasons-grid">
          <article v-for="(reason, idx) in interviewReasons" :key="idx" class="ats-reason-card">
            <div class="ats-reason-icon" :class="'ats-reason-icon--' + (idx + 1)">
              <CpuChipIcon v-if="idx === 0" class="ats-reason-svg" />
              <ChartBarIcon v-else-if="idx === 1" class="ats-reason-svg" />
              <PencilSquareIcon v-else class="ats-reason-svg" />
            </div>
            <span class="ats-reason-num">0{{ idx + 1 }}</span>
            <h4 class="ats-reason-title">{{ reason.title }}</h4>
            <p class="ats-reason-desc">{{ reason.desc }}</p>
          </article>
                </div>
        <div class="ats-faq-wrap">
          <h3 class="ats-faq-heading">
            <QuestionMarkCircleIcon class="ats-faq-heading-icon" />
            {{ t('free_interview.faq_title') }}
          </h3>
          <div class="ats-faq-list">
            <div v-for="(faq, i) in faqItems" :key="i" class="ats-faq-item" :class="{ 'ats-faq-item--open': openFaqIndex === i }">
              <button type="button" class="ats-faq-q" @click="openFaqIndex = openFaqIndex === i ? null : i">
                <span>{{ faq.q }}</span>
                <span class="ats-faq-chevron" aria-hidden="true"></span>
              </button>
              <div class="ats-faq-a">
                <p>{{ faq.a }}</p>
                </div>
            </div>
          </div>
        </div>
                    </div>
            </section>

    <!-- CTA final -->
    <section class="section cta-v1">
      <div class="cta1-wrapper">
        <div class="w-layout-grid cta1-content">
          <div class="cta-text-wrapper-left">
            <h2 class="heading-cta">{{ t('free_interview.final_cta_title') }}</h2>
          </div>
          <div class="cta-text-wrapper-right">
            <div class="cta-text-right">{{ t('free_interview.final_cta_desc') }}</div>
            <div class="reveal-content-wrap">
              <router-link to="/register" class="button-default w-button">{{ t('free_interview.final_cta_button') }}</router-link>
            </div>
          </div>
        </div>
        <div class="background-cta">
          <img class="cta-img-bg" src="https://cdn.prod.website-files.com/69383496538f3c3da700a557/6939c21874a51449ee9fd368_background.avif" alt="" loading="lazy" />
        </div>
            </div>
        </section>

    </main>

    <!-- Global Footer -->
    <Footer />
  </div>
</template>

<style scoped>
.page-wrapper--interview {
  min-height: 100vh;
  overflow-x: clip;
  --_theme---bodybackground: #2e2e2e;
  --_theme---textcolor--primarytext: #ffffff;
  --_theme---textcolor--secondarytext: #e8e8e8;
  --_theme---textcolor--tertiarytext: #b8b8b8;
  --_theme---background--primarybackground: #2e2e2e;
  --_theme---background--secondarybackground: #1f1f1f;
  background-color: var(--_theme---bodybackground);
  color: var(--_theme---textcolor--primarytext);
}
.page-wrapper--interview :deep(.main) {
  padding-top: 0;
}
.page-wrapper--interview :deep(.hero-heading),
.page-wrapper--interview :deep(.hero-paragraph),
.page-wrapper--interview :deep(.heading-cta),
.page-wrapper--interview :deep(.cta-text-right),
.page-wrapper--interview :deep(h1), .page-wrapper--interview :deep(h2),
.page-wrapper--interview :deep(h3), .page-wrapper--interview :deep(h4),
.page-wrapper--interview :deep(._3cols-heading h3), .page-wrapper--interview :deep(._3cols-heading p),
.page-wrapper--interview :deep(.card-text-content-home1 h4), .page-wrapper--interview :deep(.card-text-content-home1 p),
.page-wrapper--interview :deep(.ats-main-title), .page-wrapper--interview :deep(.ats-reason-title),
.page-wrapper--interview :deep(.ats-faq-q) {
  color: var(--_theme---textcolor--primarytext);
}
.page-wrapper--interview :deep(.tertiary-color-emphasis) {
  color: var(--_theme---textcolor--tertiarytext);
}

/* Hero title: lisibilité et mise en valeur de "faiblesses" */
.interview-hero-heading {
  font-size: clamp(1.75rem, 4.5vw, 2.75rem);
  line-height: 1.25;
  font-weight: 800;
  letter-spacing: -0.02em;
  margin: 0 0 1rem;
  max-width: 22ch;
}
.interview-hero-heading .interview-hero-line1,
.interview-hero-heading .interview-hero-line2 {
  display: inline;
}
.interview-hero-heading .interview-hero-emphasis {
  font-style: italic;
  color: var(--_theme---textcolor--tertiarytext);
}
@media (min-width: 768px) {
  .interview-hero-heading {
    max-width: none;
    font-size: clamp(2rem, 3.2vw, 2.85rem);
    line-height: 1.2;
  }
}

.interview-hero-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  align-items: center;
  gap: var(--_size---paddingsize--large, 2rem);
}
@media (max-width: 991px) {
  .interview-hero-grid {
    grid-template-columns: 1fr;
    grid-template-rows: auto auto;
  }
}
.interview-badge {
  display: inline-block;
  font-size: var(--_size---fonts--xxs, 0.75rem);
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--_theme---textcolor--accenttext1);
  margin-bottom: 0.75rem;
}
.interview-trust {
  display: flex;
  flex-wrap: wrap;
  gap: var(--_size---paddingsize--medium, 1rem);
  margin-top: var(--_size---paddingsize--medium, 1rem);
}
.interview-trust .trust-item {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  font-size: var(--_size---fonts--xs, 0.875rem);
  color: var(--_theme---textcolor--secondarytext);
}
.interview-trust .trust-icon {
  width: 1.25rem;
  height: 1.25rem;
  color: var(--_theme---textcolor--accenttext1);
}

.interview-intro-col {
  min-height: 280px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--_size---paddingsize--small, 1rem);
}
.interview-intro-card {
  width: 100%;
  max-width: 420px;
  padding: 1.75rem;
  border-radius: var(--radius--m, 1rem);
  background-color: var(--_theme---background--secondarybackground);
  border: 1px solid var(--_theme---border--mediumalpha);
}
.interview-type-wrap {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 1.25rem;
}
.interview-type-btn {
  padding: 0.5rem 1rem;
  font-size: 0.8125rem;
  font-weight: 600;
  border-radius: var(--radius--xs, 0.5rem);
  border: 1px solid var(--_theme---border--mediumalpha);
  background: var(--_theme---background--tertiarybackground);
  color: var(--_theme---textcolor--secondarytext);
  cursor: pointer;
  transition: border-color 0.2s, background 0.2s, color 0.2s;
}
.interview-type-btn--active {
  border-color: var(--_theme---textcolor--accenttext1);
  background: rgba(255, 111, 0, 0.12);
  color: var(--_theme---textcolor--primarytext);
}
.interview-job-input {
  width: 100%;
  padding: 0.875rem 1rem;
  margin-bottom: 1rem;
  font-size: 1rem;
  border-radius: var(--radius--xs, 0.5rem);
  border: 1px solid var(--_theme---border--mediumalpha);
  background: var(--_theme---background--primarybackground);
  color: var(--_theme---textcolor--primarytext);
  outline: none;
}
.interview-job-input::placeholder {
  color: var(--_theme---textcolor--tertiarytext);
}
.interview-start-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  width: 100%;
  padding: 0.875rem 1.25rem;
  font-size: 0.9375rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #fff;
  background: var(--_theme---textcolor--accenttext1);
  border: 1px solid var(--_theme---textcolor--accenttext1);
  border-radius: var(--radius--xs, 0.5rem);
  cursor: pointer;
  transition: opacity 0.2s, transform 0.15s;
}
.interview-start-btn:hover:not(:disabled) {
  opacity: 0.95;
  transform: translateY(-1px);
}
.interview-start-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
.btn-icon-svg {
  width: 1.25rem;
  height: 1.25rem;
}

.interview-connecting {
  min-height: 50vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}
.interview-connecting-card {
  text-align: center;
  padding: 2.5rem;
  border-radius: var(--radius--m, 1rem);
  background: var(--_theme---background--secondarybackground);
  border: 1px solid var(--_theme---border--mediumalpha);
}
.interview-spinner {
  width: 56px;
  height: 56px;
  margin: 0 auto 1.5rem;
  border: 3px solid var(--_theme---background--tertiarybackground);
  border-top-color: var(--_theme---textcolor--accenttext1);
  border-radius: 50%;
  animation: interview-spin 0.8s linear infinite;
}
@keyframes interview-spin {
  to { transform: rotate(360deg); }
}
.interview-connecting-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--_theme---textcolor--primarytext);
  margin: 0 0 0.5rem;
}
.interview-connecting-sub {
  font-size: 0.875rem;
  color: var(--_theme---textcolor--tertiarytext);
  margin: 0;
}

.interview-simulator-wrap {
  padding-top: 1rem;
  padding-bottom: 2rem;
}
.interview-simulator-container {
  max-width: 1200px;
  margin: 0 auto;
}
.interview-panels :deep(.fsize-body-large),
.interview-panels :deep(p) {
  color: var(--_theme---textcolor--secondarytext);
}

/* Bloc ATS/FAQ (réutilise structure Free CV Roast) */
.interview-ats-block {
  background: linear-gradient(180deg, #252530 0%, #1c1c24 100%);
  border-top: 1px solid rgba(255, 255, 255, 0.06);
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  padding: 3.5rem 1.5rem 4rem;
}
.interview-ats-block .ats-block-inner { max-width: 900px; margin: 0 auto; }
.interview-ats-block .ats-badge {
  display: inline-block;
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: var(--_theme---textcolor--accenttext1, #ff6f00);
  margin-bottom: 0.75rem;
}
.interview-ats-block .ats-main-title {
  font-size: clamp(1.5rem, 4vw, 2.25rem);
  font-weight: 700;
  line-height: 1.25;
  color: #ffffff;
  margin: 0 0 1.5rem;
}
.interview-ats-block .ats-intro { margin-bottom: 2.5rem; }
.interview-ats-block .ats-intro-p {
  font-size: 1rem;
  line-height: 1.7;
  color: #e0e0e0;
  margin: 0 0 1rem;
}
.interview-ats-block .ats-subtitle {
  font-size: 1.2rem;
  font-weight: 700;
  color: #ffffff;
  margin: 0 0 1.25rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid rgba(255, 111, 0, 0.4);
  display: inline-block;
}
.interview-ats-block .ats-reasons-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.25rem;
  margin-bottom: 3rem;
}
@media (min-width: 768px) {
  .interview-ats-block .ats-reasons-grid {
    grid-template-columns: repeat(3, 1fr);
    gap: 1.5rem;
  }
}
.interview-ats-block .ats-reason-card {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  padding: 1.5rem;
  position: relative;
}
.interview-ats-block .ats-reason-icon {
  width: 44px;
  height: 44px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 0.75rem;
}
.interview-ats-block .ats-reason-icon--1 { background: rgba(255, 111, 0, 0.15); color: #ff8c42; }
.interview-ats-block .ats-reason-icon--2 { background: rgba(0, 94, 255, 0.15); color: #4d9aff; }
.interview-ats-block .ats-reason-icon--3 { background: rgba(34, 197, 94, 0.15); color: #4ade80; }
.interview-ats-block .ats-reason-svg { width: 1.5rem; height: 1.5rem; }
.interview-ats-block .ats-reason-num {
  position: absolute;
  top: 1rem;
  right: 1rem;
  font-size: 0.7rem;
  font-weight: 700;
  color: rgba(255, 255, 255, 0.35);
}
.interview-ats-block .ats-reason-title {
  font-size: 1rem;
  font-weight: 700;
  color: #ffffff;
  margin: 0 0 0.5rem;
}
.interview-ats-block .ats-reason-desc {
  font-size: 0.875rem;
  line-height: 1.55;
  color: #b8b8b8;
  margin: 0;
}
.interview-ats-block .ats-faq-wrap {
  padding-top: 2rem;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
}
.interview-ats-block .ats-faq-heading {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1.25rem;
  font-weight: 700;
  color: #ffffff;
  margin: 0 0 1.25rem;
}
.interview-ats-block .ats-faq-heading-icon {
  width: 1.5rem;
  height: 1.5rem;
  color: var(--_theme---textcolor--accenttext1);
}
.interview-ats-block .ats-faq-list { display: flex; flex-direction: column; gap: 0.5rem; }
.interview-ats-block .ats-faq-item {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 10px;
  overflow: hidden;
}
.interview-ats-block .ats-faq-item--open {
  border-color: rgba(255, 111, 0, 0.3);
}
.interview-ats-block .ats-faq-q {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 1rem 1.25rem;
  background: none;
  border: none;
  font-size: 0.9375rem;
  font-weight: 600;
  color: #ffffff;
  text-align: left;
  cursor: pointer;
}
.interview-ats-block .ats-faq-chevron {
  flex-shrink: 0;
  width: 20px;
  height: 20px;
  border-right: 2px solid currentColor;
  border-bottom: 2px solid currentColor;
  transform: rotate(45deg);
  margin-top: -4px;
  transition: transform 0.2s;
  opacity: 0.7;
}
.interview-ats-block .ats-faq-item--open .ats-faq-chevron {
  transform: rotate(-135deg);
  margin-top: 4px;
}
.interview-ats-block .ats-faq-a {
  max-height: 0;
  overflow: hidden;
  transition: max-height 0.25s ease-out;
}
.interview-ats-block .ats-faq-item--open .ats-faq-a {
  max-height: 500px;
}
.interview-ats-block .ats-faq-a p {
  margin: 0;
  padding: 0 1.25rem 1rem 1.25rem;
  font-size: 0.9375rem;
  line-height: 1.6;
  color: #c8c8c8;
}

.page-wrapper--interview :deep(.card-item-img-wrap--num) {
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  font-weight: 700;
  color: var(--_theme---textcolor--accenttext1);
  background-color: var(--_theme---background--tertiarybackground);
}
</style>
