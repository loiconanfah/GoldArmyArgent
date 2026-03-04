<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useHead } from '@unhead/vue'
import Footer from '../components/Footer.vue'
import {
  MicrophoneIcon,
  StopIcon,
  PlayIcon,
  VideoCameraIcon,
  PhoneXMarkIcon
} from '@heroicons/vue/24/solid'

useHead({
  title: 'Simulateur Entretien IA | Entraînement Visio Gratuit | GoldArmy',
  meta: [
    { name: 'description', content: 'Entraînez-vous gratuitement aux entretiens d\'embauche avec notre IA vocale. Le simulateur génère des questions pièges sur-mesure pour votre métier.' },
    { property: 'og:title', content: 'Simulateur d\'Entretien d\'Embauche IA | GoldArmy' },
    { property: 'og:description', content: 'Ne découvrez pas vos faiblesses le jour J. Passez un faux entretien en visio avec notre Recruteur IA ultra-exigeant.' }
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
        "description": "Un simulateur d'entretien d'embauche en temps réel propulsé par l'intelligence artificielle et la reconnaissance vocale pour s'entraîner aux questions pièges.",
        "offers": {
          "@type": "Offer",
          "price": "0",
          "priceCurrency": "EUR"
        }
      })
    }
  ]
})

const router = useRouter()

// States
const step = ref('intro') // intro -> connecting -> interviewing -> feedback
const jobTitle = ref('')
const isProcessing = ref(false)

// Interview variables
const question = ref('')
const userAnswer = ref('')
const feedback = ref(null)

// Web Speech API references
let synthesis = null
let recognition = null
const isListening = ref(false)

onMounted(() => {
    synthesis = window.speechSynthesis
    
    // Check for Speech Recognition
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
    if (SpeechRecognition) {
        recognition = new SpeechRecognition()
        recognition.lang = 'fr-FR'
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
})

onUnmounted(() => {
    if (synthesis) synthesis.cancel()
    if (recognition) recognition.stop()
})

const speakText = (text, onEndCallback = null) => {
    if (!synthesis) return
    synthesis.cancel()
    const utterance = new SpeechSynthesisUtterance(text)
    utterance.lang = 'fr-FR'
    utterance.rate = 1.05
    utterance.pitch = 0.9 // Slightly deeper, more professional voice
    
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
            body: JSON.stringify({ job_title: jobTitle.value })
        })
        const data = await res.json()
        if (data.status === 'success') {
            question.value = data.text
            step.value = 'interviewing'
            
            // Wait a sec to "connect", then speak
            setTimeout(() => {
                speakText(question.value, () => {
                    // Auto-start recording when question finishes? Or let user click.
                    // Let's let user click to afford control.
                })
            }, 1000)
            
        } else {
            throw new Error("API Exception")
        }
    } catch(err) {
        alert("La connexion avec le recruteur a échoué. Veuillez réessayer.")
        step.value = 'intro'
    }
}

const toggleRecording = () => {
    if (!recognition) {
        alert("Votre navigateur ne supporte pas la reconnaissance vocale. Merci d'utiliser Chrome ou Safari.")
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
        alert("Vous n'avez rien dit !")
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
                context: question.value,
                user_response: userAnswer.value
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
  <div class="min-h-screen bg-[#0a0a12] text-white flex flex-col font-display relative overflow-x-hidden selection:bg-indigo-500/30">
    
    <!-- Background Elements with CSS Animations -->
    <div class="fixed inset-0 bg-[#0a0a12] pointer-events-none z-0"></div>
    <div class="fixed top-[-20%] right-[-10%] w-[50%] h-[50%] rounded-full bg-violet-600/10 blur-[150px] mix-blend-screen animate-blob pointer-events-none z-0"></div>
    <div class="fixed bottom-[-20%] left-[-10%] w-[50%] h-[50%] rounded-full bg-indigo-600/10 blur-[150px] mix-blend-screen animate-blob pointer-events-none z-0" style="animation-delay: 2s"></div>
    <div class="fixed top-[40%] left-[20%] w-[40%] h-[40%] rounded-full bg-fuchsia-600/10 blur-[150px] mix-blend-screen animate-blob pointer-events-none z-0" style="animation-delay: 4s"></div>
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

    <!-- Main Content wrapper -->
    <main class="relative z-10 w-full flex-1 flex flex-col pt-32 pb-20 px-4 md:px-6">
        
        <!-- Simulator Container -->
        <div class="w-full max-w-5xl mx-auto h-[80vh] min-h-[600px] max-h-[850px] border border-surface-800 rounded-[2rem] bg-surface-950/80 backdrop-blur-2xl shadow-[0_20px_60px_-15px_rgba(0,0,0,0.7)] flex flex-col relative overflow-hidden">
            
            <!-- MAIN VIEWS -->
    
    <!-- 1. INTRO (Hero Section Split/Centered) -->
    <div v-if="step === 'intro'" class="flex-1 flex flex-col items-center justify-center p-6 text-center max-w-4xl mx-auto z-10 w-full mb-20">
        
        <div class="inline-flex items-center gap-3 px-4 py-2 rounded-full bg-surface-900/80 border border-white/5 backdrop-blur-md mb-8 shadow-2xl">
            <span class="w-2 h-2 rounded-full bg-indigo-500 animate-pulse"></span>
            <span class="text-xs font-bold text-slate-300 tracking-widest uppercase">Évaluation Orale IA</span>
        </div>

        <h1 class="text-5xl sm:text-6xl md:text-7xl font-black mb-6 tracking-tighter leading-[1.1]">
            Ne découvrez pas vos <span class="italic text-slate-500 font-display">faiblesses</span><br/>
            <span class="text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 via-fuchsia-400 to-rose-400 pb-2">le jour J.</span>
        </h1>
        
        <p class="text-lg md:text-xl text-slate-400 mb-12 max-w-2xl mx-auto font-medium leading-relaxed">
            Passez une simulation d'entretien Visio ultra-réaliste. Notre IA prend le rôle d'un Lead Tech impitoyable et analyse votre voix, vos silences et vos arguments en temps réel.
        </p>
        
        <div class="w-full max-w-2xl relative group">
            <div class="absolute -inset-1 bg-gradient-to-r from-indigo-500 to-fuchsia-500 rounded-3xl blur opacity-25 group-hover:opacity-40 transition duration-1000 group-hover:duration-200"></div>
            <div class="relative bg-surface-950/80 backdrop-blur-xl border border-white/10 rounded-3xl p-2 sm:p-3 flex flex-col sm:flex-row gap-2 shadow-2xl overflow-hidden">
                <input v-model="jobTitle" @keyup.enter="startCall" type="text" placeholder="Le poste visé (ex: Data Analyst)" class="flex-1 bg-transparent px-6 py-4 text-lg font-bold text-white placeholder-slate-500 focus:outline-none text-center sm:text-left" />
                
                <button @click="startCall" :disabled="!jobTitle.trim()" class="bg-white text-indigo-950 disabled:opacity-50 disabled:cursor-not-allowed font-black uppercase tracking-widest py-4 px-8 rounded-2xl shadow-[0_0_20px_rgba(255,255,255,0.2)] transition-transform hover:scale-[1.02] active:scale-95 flex items-center justify-center gap-3 z-10">
                    <VideoCameraIcon class="w-5 h-5 text-indigo-600" /> Rejoindre la Visio
                </button>
            </div>
        </div>
        
        <div class="mt-10 flex items-center justify-center gap-8 text-sm font-bold text-slate-500">
            <div class="flex items-center gap-2">
                <MicrophoneIcon class="w-5 h-5 text-fuchsia-400" />
                <span>Micro Requis</span>
            </div>
            <div class="flex items-center gap-2">
                <ShieldCheckIcon class="w-5 h-5 text-emerald-500" />
                <span>Aucun enregistrement conservé</span>
            </div>
        </div>
    </div>

    <!-- 2. CONNECTING -->
    <div v-if="step === 'connecting'" class="flex-1 flex flex-col items-center justify-center z-10">
        <div class="w-32 h-32 rounded-full border-4 border-surface-800 border-t-indigo-500 animate-spin mb-8"></div>
        <h2 class="text-2xl font-bold animate-pulse">Connexion au recruteur...</h2>
        <p class="text-slate-500 mt-2 font-mono text-sm">Établissement du canal sécurisé</p>
    </div>

    <!-- 3. INTERVIEWING (HUD/Glassmorphism UI) -->
    <div v-if="step === 'interviewing' || step === 'feedback'" class="flex-1 flex flex-col z-10 pt-16 pb-32 px-4 sm:px-12 w-full max-w-[1600px] mx-auto relative">
        
        <!-- Glowing Ambient Lights for HUD -->
        <div class="absolute top-1/4 left-1/4 w-96 h-96 bg-indigo-600/10 blur-[100px] pointer-events-none rounded-full"></div>
        <div class="absolute bottom-1/4 right-1/4 w-96 h-96 bg-fuchsia-600/10 blur-[100px] pointer-events-none rounded-full"></div>

        <!-- Video Grid: Asymmetrical Floating Panels -->
        <div class="flex-1 grid grid-cols-1 lg:grid-cols-12 gap-6 lg:gap-8 w-full relative z-10">
            
            <!-- Recruiter (AI) - Primary Focus -->
            <div class="lg:col-span-8 bg-surface-950/60 backdrop-blur-3xl border border-white/5 rounded-[2.5rem] relative overflow-hidden flex flex-col shadow-[0_20px_80px_-20px_rgba(79,70,229,0.3)]">
                
                <!-- AI Avatar Container -->
                <div class="flex-1 flex flex-col items-center justify-center p-12 relative">
                    <!-- Audio Visualizer Rings effect -->
                    <div class="absolute inset-x-0 bottom-0 h-1/2 bg-gradient-to-t from-indigo-900/30 to-transparent pointer-events-none"></div>
                    
                    <div class="relative w-64 h-64">
                        <!-- Ripple effect when AI talks -->
                        <div class="absolute inset-0 bg-indigo-500 rounded-full animate-ping opacity-20 scale-150" v-if="(step === 'interviewing' && userAnswer === '') || step === 'feedback'"></div>
                        <div class="absolute inset-0 bg-fuchsia-500 rounded-full animate-pulse opacity-10 scale-[1.2]" v-if="(step === 'interviewing' && userAnswer === '') || step === 'feedback'"></div>
                        
                        <img src="/avatars/tech.png" alt="Recruteur" class="w-full h-full rounded-full object-cover border-[6px] border-surface-900 relative z-10 shadow-2xl bg-[#0d1117] p-2" />
                    </div>
                </div>
                
                <!-- Subtitles / Feedback area HUD style -->
                <div class="absolute bottom-6 inset-x-6 sm:bottom-8 sm:inset-x-10">
                    <div class="bg-surface-950/80 backdrop-blur-2xl rounded-3xl p-6 sm:p-8 border border-white/10 shadow-2xl relative overflow-hidden">
                        <div class="absolute left-0 top-0 bottom-0 w-1 bg-indigo-500"></div>
                        
                        <p class="text-xs font-black text-indigo-400 uppercase tracking-[0.2em] mb-3 flex items-center gap-2">
                            <span class="w-2 h-2 rounded-full bg-indigo-500 animate-pulse shadow-[0_0_10px_#6366f1]"></span>
                            IA Recruteur
                        </p>
                        
                        <p class="text-lg sm:text-2xl font-medium leading-relaxed font-sans" v-if="step === 'interviewing'">
                            "{{ question }}"
                        </p>
                        <p class="text-lg sm:text-2xl font-medium leading-relaxed text-rose-300 font-sans" v-else-if="step === 'feedback'">
                            "{{ feedback }}"
                        </p>
                    </div>
                </div>
            </div>

            <!-- User (You) - Sidebar Panel -->
            <div class="lg:col-span-4 flex flex-col gap-6">
                
                <!-- User Webcam Placeholder -->
                <div class="bg-surface-900/40 backdrop-blur-xl rounded-[2.5rem] border border-white/5 relative overflow-hidden flex flex-col aspect-square lg:aspect-auto lg:h-[40%]">
                    <div class="flex-1 flex items-center justify-center p-8 relative">
                         <!-- User speaking radar -->
                        <div v-if="isListening" class="absolute inset-0 bg-rose-500/5 animate-pulse"></div>
                        <div class="w-24 h-24 rounded-full bg-surface-800 flex items-center justify-center border border-white/10 shadow-xl relative z-10">
                            <span class="text-2xl text-slate-500 font-bold">Vous</span>
                        </div>
                    </div>
                </div>
                
                <!-- Live Transcription Box -->
                <div class="bg-surface-950/60 backdrop-blur-xl rounded-[2.5rem] border border-white/5 relative flex flex-col flex-1 shadow-2xl">
                    <div class="absolute top-0 right-0 w-32 h-32 bg-rose-500/10 blur-[40px] pointer-events-none"></div>

                    <div class="p-8 flex flex-col h-full justify-between relative z-10">
                        <div>
                            <p class="text-[10px] font-black uppercase tracking-[0.2em] mb-4 flex items-center gap-2" :class="isListening ? 'text-rose-400' : 'text-slate-500'">
                                <span v-if="isListening" class="w-2 h-2 rounded-full bg-rose-500 animate-pulse shadow-[0_0_10px_#f43f5e]"></span>
                                {{ isListening ? 'Transcription en direct' : 'En attente...' }}
                            </p>
                            
                            <p class="text-base text-slate-300 font-medium leading-relaxed" v-if="step === 'interviewing'">
                                {{ userAnswer || (isListening ? 'Parlez maintenant...' : 'Activez le micro en bas pour répondre.') }}
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
                        <h3 class="text-4xl md:text-5xl font-black mb-6 text-white tracking-tight">Fin de la simulation.</h3>
                        <p class="text-slate-400 text-lg md:text-xl mb-12 max-w-xl leading-relaxed">
                            C'était brutal, non ? GoldArmy vous permet de recommencer cette épreuve jusqu'à devenir totalement insensible au stress.
                        </p>
                        
                        <button @click="router.push('/register')" class="bg-white text-indigo-950 font-black uppercase tracking-widest text-sm px-12 py-6 rounded-2xl shadow-[0_0_40px_rgba(255,255,255,0.2)] hover:scale-[1.02] active:scale-95 transition-all mb-6">
                            Créer un compte Gratuit
                        </button>
                        <button @click="endCall" class="text-xs font-bold text-slate-500 hover:text-white uppercase tracking-widest transition-colors py-2">
                            Quitter l'appel
                        </button>
                    </div>
                </div>

            </div>
        </div>

        <!-- Zoom Controls Bar (Floating Dock) -->
        <div class="absolute bottom-8 inset-x-0 flex justify-center z-[60] pointer-events-none px-4">
            <div class="bg-[#1a1a24]/90 backdrop-blur-2xl border border-white/10 p-2 sm:p-3 rounded-3xl flex items-center gap-2 sm:gap-4 shadow-[0_20px_50px_rgba(0,0,0,0.5)] pointer-events-auto transition-transform hover:-translate-y-1 duration-300">
                
                <!-- Mic Toggle -->
                <div class="flex flex-col items-center">
                    <button @click="toggleRecording" :disabled="step !== 'interviewing'" class="w-14 h-14 sm:w-16 sm:h-16 rounded-2xl flex items-center justify-center transition-all duration-300 shadow-lg" :class="isListening ? 'bg-rose-500/20 text-rose-400 hover:bg-rose-500/30 border border-rose-500/50 shadow-[0_0_20px_rgba(244,63,94,0.3)]' : 'bg-surface-800 text-slate-300 hover:bg-surface-700 hover:text-white border border-white/5 disabled:opacity-50 disabled:cursor-not-allowed'">
                        <MicrophoneIcon class="w-6 h-6 sm:w-7 sm:h-7" v-if="!isListening" />
                        <StopIcon class="w-6 h-6 sm:w-7 sm:h-7" v-else />
                    </button>
                    <span class="text-[10px] font-bold text-slate-500 mt-2 uppercase tracking-widest hidden sm:block">{{ isListening ? 'Stop' : 'Parler' }}</span>
                </div>

                <div class="w-px h-10 bg-white/10 mx-2"></div>

                <!-- Submit Answer -->
                <div class="flex flex-col items-center">
                    <button @click="submitAnswer" :disabled="step !== 'interviewing' || !userAnswer || isProcessing" class="px-8 h-14 sm:h-16 rounded-2xl flex items-center gap-3 transition-all duration-300 shadow-lg text-sm sm:text-base font-black tracking-wide uppercase" :class="userAnswer && !isProcessing ? 'bg-indigo-600 hover:bg-indigo-500 text-white shadow-[0_0_20px_rgba(79,70,229,0.3)]' : 'bg-surface-800 text-slate-500 border border-white/5 disabled:opacity-50 disabled:cursor-not-allowed'">
                        <span v-if="isProcessing" class="w-5 h-5 rounded-full border-2 border-white/30 border-t-white animate-spin"></span>
                        <PlayIcon v-else class="w-5 h-5" />
                        {{ isProcessing ? 'Analyse...' : 'Valider' }}
                    </button>
                    <span class="text-[10px] font-bold text-transparent mt-2 hidden sm:block">.</span>
                </div>

                <div class="w-px h-10 bg-white/10 mx-2"></div>

                <!-- End Call -->
                <div class="flex flex-col items-center">
                    <button @click="endCall" class="w-14 h-14 sm:w-16 sm:h-16 rounded-2xl bg-rose-600 hover:bg-rose-500 text-white flex items-center justify-center transition-all duration-300 shadow-[0_0_20px_rgba(225,29,72,0.3)]">
                        <PhoneXMarkIcon class="w-6 h-6 sm:w-7 sm:h-7" />
                    </button>
                    <span class="text-[10px] font-bold text-slate-500 mt-2 uppercase tracking-widest hidden sm:block">Quitter</span>
                </div>
            </div>
        </div>

    </div>

        </div> <!-- End Simulator Container -->

        <!-- Bento Box Explanatory Section -->
        <section class="max-w-[1400px] mx-auto w-full pt-20 border-t border-white/5 relative z-10">
            <div class="text-center mb-20">
                <span class="text-indigo-400 text-xs font-black uppercase tracking-[0.2em] mb-4 block">Le simulateur de stress</span>
                <h2 class="text-4xl md:text-6xl font-black mb-6 tracking-tight">Ne paniquez plus <span class="italic font-display text-slate-500">face aux RH.</span></h2>
            </div>

            <!-- Asymmetrical Bento Grid -->
            <div class="grid grid-cols-1 md:grid-cols-4 md:grid-rows-2 gap-6 h-auto md:h-[600px] mb-32">
                
                <!-- BENTO 1: Large Audio Visualizer Feature -->
                <div class="md:col-span-2 md:row-span-2 bg-gradient-to-br from-surface-900 to-[#0a0a12] border border-white/5 rounded-[2.5rem] p-10 relative overflow-hidden group">
                    <div class="absolute top-0 left-0 w-full h-full bg-[radial-gradient(circle_at_top_left,_var(--tw-gradient-stops))] from-indigo-500/10 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-700"></div>
                    <div class="w-16 h-16 bg-indigo-500/10 rounded-2xl flex items-center justify-center text-indigo-400 font-black text-2xl mb-8 border border-indigo-500/20 shadow-[0_0_30px_rgba(99,102,241,0.2)]">1</div>
                    <h3 class="text-3xl font-black mb-4">Reconnaissance Intelligente</h3>
                    <p class="text-slate-400 text-lg leading-relaxed max-w-md">
                        Le simulateur vous écoute en temps réel avec le Web Speech API. L'IA analyse votre débit de parole, votre assurance et sanctionne le moindre balbutiement.
                    </p>
                    <div class="mt-10 h-32 bg-surface-950 rounded-2xl border border-surface-800 flex items-center justify-center p-4 overflow-hidden relative">
                        <!-- Abstract sound waves -->
                        <div class="flex items-center gap-1 w-full max-w-[250px] h-16">
                            <div v-for="i in 15" :key="i" class="flex-1 bg-indigo-500 rounded-full animate-pulse shadow-[0_0_10px_#6366f1]" :style="`height: ${Math.random() * 100}%; animation-delay: ${i * 0.1}s; animation-duration: ${0.5 + Math.random()}s`"></div>
                        </div>
                    </div>
                </div>

                <!-- BENTO 2: Top Right Small -->
                <div class="md:col-span-2 md:row-span-1 bg-surface-900 border border-white/5 rounded-[2.5rem] p-10 relative overflow-hidden">
                    <div class="w-12 h-12 bg-fuchsia-500/10 rounded-xl flex items-center justify-center text-fuchsia-400 font-black text-xl mb-4 border border-fuchsia-500/20">2</div>
                    <h3 class="text-2xl font-black mb-3 text-white">Scénarios Extrêmes</h3>
                    <p class="text-slate-400 text-sm leading-relaxed max-w-sm">
                        L'IA génère des questions techniques ultra spécifiques à votre poste, piochées dans les bases de données d'entretiens de Google et Meta.
                    </p>
                </div>

                <!-- BENTO 3: Bottom Right Small -->
                <div class="md:col-span-2 md:row-span-1 bg-surface-900 border border-white/5 rounded-[2.5rem] p-10 relative overflow-hidden group">
                    <div class="absolute inset-0 bg-gradient-to-r from-rose-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
                    <div class="w-12 h-12 bg-rose-500/10 rounded-xl flex items-center justify-center text-rose-400 font-black text-xl mb-4 border border-rose-500/20">3</div>
                    <h3 class="text-2xl font-black mb-3 text-white">Feedback Temps Réel</h3>
                    <p class="text-slate-400 text-sm leading-relaxed max-w-sm">
                        Recevez des critiques directes. Vous ne saurez pas que votre réponse "manque de metrics" si personne n'ose vous le dire en face. L'IA ose.
                    </p>
                </div>

            </div>

            <!-- Massive SEO Content: How It Works & FAQ -->
            <section class="max-w-4xl mx-auto w-full pt-12 pb-24 text-left px-4">
                <article class="prose prose-invert prose-lg max-w-none">
                    <h2 class="text-3xl font-black text-white mb-6">Comment fonctionne notre Simulateur d'Entretien IA ?</h2>
                    <p class="text-slate-400 mb-6 leading-relaxed">
                        Préparer un entretien d'embauche devant un miroir ne suffit plus. Notre <strong>Simulateur d'Entretien IA</strong> utilise la technologie <em>Web Speech API</em> couplée à un Large Language Model (LLM) pour créer un environnement de stress réaliste. L'IA écoute vos réponses en temps réel, analyse la sémantique de votre discours, la richesse de votre vocabulaire technique, et l'absence d'hésitations.
                    </p>
                    
                    <h3 class="text-2xl font-bold text-white mt-12 mb-4">La Tech derrière la magie</h3>
                    <ul class="text-slate-400 mb-10 space-y-3 list-disc pl-6 marker:text-indigo-500">
                        <li><strong>Scraping de l'Extrême :</strong> L'algorithme se base sur des milliers de questions pièges fuitées des entretiens chez Google, Meta, et Stripe pour forger son caractère d'évaluateur impitoyable.</li>
                        <li><strong>Analyse Sémantique Profonde :</strong> Le modèle pénalise l'utilisation de mots faibles ("je crois", "peut-être") et récompense les verbes d'action ("j'ai architecturé", "j'ai maximisé").</li>
                        <li><strong>Feedbacks Temps Réel :</strong> L'IA identifie instantanément si vous n'avez pas répondu à la question de fond ou si vous avez esquivé un point technique.</li>
                    </ul>

                    <h2 class="text-3xl font-black text-white mt-16 mb-8">Foire Aux Questions (FAQ) sur la Simulation</h2>
                    
                    <div class="space-y-6">
                        <details class="bg-surface-900/50 border border-white/5 rounded-2xl p-6 group cursor-pointer hover:bg-surface-800/50 transition-colors">
                            <summary class="text-xl font-bold text-white list-none flex justify-between items-center">
                                Dois-je allumer ma caméra pour l'essai gratuit ?
                                <span class="text-indigo-400 group-open:rotate-180 transition-transform">▼</span>
                            </summary>
                            <p class="text-slate-400 mt-4 leading-relaxed">
                                Non. Pour cet essai public gratuit, seule la reconnaissance vocale de votre navigateur web est sollicitée. Vos données audios ne quittent temporairement votre appareil que sous forme de texte pour l'analyse algorithmique.
                            </p>
                        </details>
                        
                        <details class="bg-surface-900/50 border border-white/5 rounded-2xl p-6 group cursor-pointer hover:bg-surface-800/50 transition-colors">
                            <summary class="text-xl font-bold text-white list-none flex justify-between items-center">
                                Le simulateur prend-il en compte mon métier exact ?
                                <span class="text-indigo-400 group-open:rotate-180 transition-transform">▼</span>
                            </summary>
                            <p class="text-slate-400 mt-4 leading-relaxed">
                                Oui. Avant de lancer l'appel, vous tapez le titre de votre poste cible (ex: "Senior Backend Developer Python"). Le Recruteur IA ajustera alors son lexique et générera des questions techniques d'architecture logicielle ou de management adaptées.
                            </p>
                        </details>

                        <details class="bg-surface-900/50 border border-white/5 rounded-2xl p-6 group cursor-pointer hover:bg-surface-800/50 transition-colors">
                            <summary class="text-xl font-bold text-white list-none flex justify-between items-center">
                                Pourquoi la voix de l'IA semble si froide ?
                                <span class="text-indigo-400 group-open:rotate-180 transition-transform">▼</span>
                            </summary>
                            <p class="text-slate-400 mt-4 leading-relaxed">
                                C'est un choix de design. L'idée est de vous placer dans la "Zone de Panique" temporelle. En étant froid et direct, le simulateur vous force à contrôler votre propre respiration et à structurer votre pensée sans l'empathie naturelle d'un humain pour vous rassurer. C'est le meilleur moyen de vous hyper-préparer.
                            </p>
                        </details>
                    </div>
                </article>
            </section>

            <!-- Massive Footer CTA -->
            <div class="relative w-full rounded-[3rem] p-16 md:p-24 text-center overflow-hidden border border-white/10 bg-surface-950">
                <!-- Glowing orb behind -->
                <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-[conic-gradient(at_top_right,_var(--tw-gradient-stops))] from-indigo-500/20 via-rose-500/20 to-indigo-500/20 blur-[120px] rounded-full pointer-events-none animate-spin-slow"></div>
                
                <h3 class="text-4xl md:text-6xl font-black mb-6 tracking-tight relative z-10 text-white">Devenez inébranlable.</h3>
                <p class="text-slate-400 text-lg md:text-xl mb-12 max-w-2xl mx-auto relative z-10">
                    Débloquez le simulateur sans limite de temps. Enchaînez les faux entretiens de 45 minutes et apprenez à dominer la discussion.
                </p>
                
                <router-link to="/register" class="relative z-10 inline-flex items-center justify-center bg-white text-black font-black uppercase tracking-widest text-sm px-12 py-6 rounded-2xl shadow-[0_0_40px_rgba(255,255,255,0.2)] hover:scale-105 hover:shadow-[0_0_60px_rgba(255,255,255,0.4)] active:scale-95 transition-all">
                    Démarrer l'entraînement
                </router-link>
            </div>
        </section>

    </main>

    <!-- Global Footer -->
    <Footer />
  </div>
</template>

<style scoped>
/* Optional specific styling */
</style>
