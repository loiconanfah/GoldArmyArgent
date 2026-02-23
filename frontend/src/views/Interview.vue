<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { MicrophoneIcon, StopIcon, ArrowLeftIcon, SparklesIcon, DocumentTextIcon, BriefcaseIcon, BuildingOfficeIcon } from '@heroicons/vue/24/outline'
import { CheckIcon } from '@heroicons/vue/24/solid'

const router = useRouter()

// Phase states
const isInterviewStarted = ref(false)

// Config Form Data
const config = ref({
    cv: '',
    jobTitle: '',
    company: '',
    jobDetails: '',
    interviewType: 'general'
})

const fileInput = ref(null)
const isUploadingCV = ref(false)

// Interview states
const isListening = ref(false)
const isSpeaking = ref(false)
const transcript = ref('')
const conversation = ref([])
const socket = ref(null)
const chatContainer = ref(null)
const errorMsg = ref('')
const isAIThinking = ref(false)

// Visual audio pulse simulation
const audioLevel = ref(0)
let audioInterval = null

let recognition = null;
let currentSynthesis = null;
let cachedVoices = []; // ✅ Voix mémorisées dès le chargement de la page
let pendingUtteranceText = null; // Texte en attente si les voix ne sont pas prêtes

const startInterview = () => {
    if (!config.value.jobTitle || !config.value.company) {
        errorMsg.value = "Poste et Entreprise sont requis."
        return
    }
    errorMsg.value = ""
    isInterviewStarted.value = true
    
    // Initialize Web Speech API
    const hasSpeech = initSpeechRecognition()
    if (hasSpeech) {
        connectWebSocket()
    }
}

const handleFileUpload = async (event) => {
    const file = event.target.files[0]
    if (!file) return
    
    if (file.type !== 'application/pdf') {
        errorMsg.value = "Veuillez sélectionner un fichier PDF."
        return
    }
    
    errorMsg.value = ""
    isUploadingCV.value = true
    
    const formData = new FormData()
    formData.append("file", file)
    
    try {
        const response = await fetch('http://localhost:8000/api/parse-pdf', {
            method: 'POST',
            body: formData,
            headers: {
                 // Do not set Content-Type for FormData, the browser will set it with the boundary
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        })
        const result = await response.json()
        if (result.status === 'success') {
            config.value.cv = result.text
        } else {
            errorMsg.value = result.detail || "Erreur lors de l'extraction du PDF."
        }
    } catch (e) {
        errorMsg.value = "Erreur de connexion au serveur pour l'upload."
    } finally {
        isUploadingCV.value = false
        if (fileInput.value) fileInput.value.value = '' // Reset input
    }
}

const initSpeechRecognition = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
        errorMsg.value = "Votre navigateur ne supporte pas la reconnaissance vocale. Utilisez Chrome ou Safari."
        return false;
    }
    
    recognition = new SpeechRecognition()
    recognition.lang = 'fr-FR'
    recognition.continuous = true  // ✅ Empêche le navigateur de couper après une pause
    recognition.interimResults = true
    
    recognition.onstart = () => {
        isListening.value = true
        startAudioPulse()
    }
    
    let silenceTimer = null
    const SILENCE_TIMEOUT = 10000 // 10 secondes de silence demandées par l'utilisateur
    
    recognition.onresult = (event) => {
        let interimTranscript = ''
        let finalTranscript = ''

        for (let i = event.resultIndex; i < event.results.length; ++i) {
            if (event.results[i].isFinal) {
                finalTranscript += event.results[i][0].transcript
            } else {
                interimTranscript += event.results[i][0].transcript
            }
        }
        
        transcript.value = finalTranscript || interimTranscript
        
        // Timer de silence : on reset à chaque mot capté
        if (silenceTimer) clearTimeout(silenceTimer)
        silenceTimer = setTimeout(() => {
            if (transcript.value.trim() !== '') {
                console.log("Silence prolongé (10s) détecté, envoi automatique.")
                recognition.stop() // Déclenchera onend() qui enverra le message
            }
        }, SILENCE_TIMEOUT)
    }
    
    recognition.onend = () => {
        isListening.value = false
        stopAudioPulse()
        if (silenceTimer) clearTimeout(silenceTimer)
        
        // On n'envoie que si on a un transcrit et qu'on n'est pas déjà en train de parler
        if (transcript.value.trim() !== '' && !isSpeaking.value) {
            sendMessageToAI(transcript.value)
            transcript.value = ''
        } else if (!isSpeaking.value && isInterviewStarted.value) {
            // Si le micro s'arrête tout seul sans texte (timeout navigateur), on le relance
            console.log("Micro arrêté sans texte, relance...")
            // try { recognition.start() } catch(e) {}
        }
    }
    
    recognition.onerror = (event) => {
        console.error("Speech recognition error", event.error)
        isListening.value = false
        stopAudioPulse()
        if(event.error !== 'no-speech' && event.error !== 'aborted') {
            errorMsg.value = "Erreur micro: " + event.error
        }
    }
    return true
}

const connectWebSocket = () => {
    const token = localStorage.getItem('token')
    if(!token) {
        router.push('/login')
        return
    }
    
    socket.value = new WebSocket(`ws://localhost:8000/api/interview/ws?token=${token}`)
    
    socket.value.onopen = () => {
        console.log("Connecté au Mentor IA")
        // Send the setup config payload
        socket.value.send(JSON.stringify({
            type: 'setup',
            payload: config.value
        }))
    }
    
    socket.value.onmessage = (event) => {
        const data = JSON.parse(event.data)
        
        if (data.type === 'message') {
            // ❌ NE PAS appeler speakText ici — le message arrive avant les chunks.
            // On ajoute juste le message vide qui sera complété par les chunks.
            if (!conversation.value.find(m => m.role === 'assistant' && m.content === data.content)) {
                conversation.value.push({
                    role: 'assistant',
                    content: data.content,
                    id: Date.now()
                })
                scrollToBottom()
            }
            
        } else if (data.type === 'chunk') {
            const lastMsg = conversation.value[conversation.value.length - 1]
            if (lastMsg && lastMsg.role === 'assistant') {
                lastMsg.content += data.content
                scrollToBottom()
            } else {
                conversation.value.push({ role: 'assistant', content: data.content, id: Date.now() })
            }
        } else if (data.type === 'done') {
            // ✅ C'est ICI l'unique endroit où on parle. Le contenu est maintenant complet.
            isAIThinking.value = false
            const lastMsg = conversation.value[conversation.value.length - 1]
            if (lastMsg && lastMsg.role === 'assistant') {
                speakText(lastMsg.content)
            }
        } else if (data.type === 'error') {
            isAIThinking.value = false
            errorMsg.value = data.message
        }
    }
    
    socket.value.onclose = () => {
        console.log("WebSocket déconnecté")
        if (isSpeaking.value && window.speechSynthesis) window.speechSynthesis.cancel()
    }
}

const sendMessageToAI = (text) => {
    if (!socket.value || socket.value.readyState !== WebSocket.OPEN) return
    
    isAIThinking.value = true
    conversation.value.push({ role: 'user', content: text, id: Date.now() })
    scrollToBottom()
    
    if (window.speechSynthesis) window.speechSynthesis.cancel()
    socket.value.send(JSON.stringify({ text: text }))
}

// Prend les voix en cache ou les voix disponibles maintenant
const getVoice = () => {
    const voices = cachedVoices.length > 0 ? cachedVoices : window.speechSynthesis.getVoices()
    const frVoices = voices.filter(v => v.lang.startsWith('fr'))
    
    // Ordre de priorité : Online/Natural > Google/Thomas/Henri/Microsoft > n'importe quelle voix fr
    return frVoices.find(v => v.name.includes('Online') || v.name.includes('Natural') || v.name.includes('Premium'))
        || frVoices.find(v => ['Google', 'Thomas', 'Henri', 'Microsoft'].some(n => v.name.includes(n)))
        || frVoices[0]
        || null
}

const speakText = (text) => {
    if (!window.speechSynthesis || !text?.trim()) return
    
    // Si les voix ne sont pas encore chargées, on mémorise le texte et on attend  
    if (cachedVoices.length === 0 && window.speechSynthesis.getVoices().length === 0) {
        console.log("Voix pas encore prêtes, texte en attente...")
        pendingUtteranceText = text
        return
    }
    
    // Stopper tout ce qui joue
    window.speechSynthesis.cancel()
    
    const utterance = new SpeechSynthesisUtterance(text)
    utterance.lang = 'fr-FR'
    utterance.rate = 1.0
    utterance.pitch = 0.95
    utterance.volume = 1.0
    
    const voice = getVoice()
    if (voice) {
        console.log("Voix utilisée:", voice.name)
        utterance.voice = voice
    } else {
        console.warn("Aucune voix fr-FR trouvée, on utilise la voix par défaut du navigateur.")
    }
    
    utterance.onstart = () => {
        isSpeaking.value = true
        startAudioPulse()
        // Couper le micro pendant que le recruteur parle
        if (isListening.value && recognition) {
            try { recognition.stop() } catch(e) {}
        }
    }
    
    utterance.onend = () => {
        isSpeaking.value = false
        stopAudioPulse()
        
        // Relancer le micro automatiquement 1s après la fin du recruteur
        setTimeout(() => {
            if (!isListening.value && recognition && isInterviewStarted.value) {
                try {
                    errorMsg.value = ''
                    recognition.start()
                    console.log("Micro relancé après l'IA")
                } catch(e) {
                    console.log("Micro: ", e.message)
                }
            }
        }, 1000)
    }
    
    utterance.onerror = (e) => {
        console.error("SpeechSynthesis error:", e.error || e)
        isSpeaking.value = false
        stopAudioPulse()
    }
    
    currentSynthesis = utterance
    window.speechSynthesis.speak(utterance)
    console.log("speechSynthesis.speak() appelé avec:", text.substring(0, 50))
}

const triggerListen = () => {
    if (isSpeaking.value) window.speechSynthesis.cancel()
    if (isListening.value) {
        recognition.stop()
    } else {
        errorMsg.value = ''
        try { recognition.start() } catch(e) {}
    }
}

const stopInterview = () => {
    if (isListening.value && recognition) recognition.stop()
    if (isSpeaking.value && window.speechSynthesis) window.speechSynthesis.cancel()
    if (socket.value) socket.value.close()
    
    isInterviewStarted.value = false
    conversation.value = []
}

const goBackToDashboard = () => router.push('/dashboard')

const scrollToBottom = () => {
    nextTick(() => {
        if (chatContainer.value) {
            chatContainer.value.scrollTop = chatContainer.value.scrollHeight
        }
    })
}

const startAudioPulse = () => {
    if (audioInterval) clearInterval(audioInterval)
    audioInterval = setInterval(() => { audioLevel.value = Math.random() * 40 + 10 }, 150)
}

const stopAudioPulse = () => {
    if (audioInterval) clearInterval(audioInterval)
    audioLevel.value = 0
}

onMounted(() => {
    // ✅ Cache les voix dès qu'elles sont prêtes (asynchrone sur Chrome)
    if (window.speechSynthesis) {
        const loadVoices = () => {
            const voices = window.speechSynthesis.getVoices()
            if (voices.length > 0) {
                cachedVoices = voices
                console.log(`✅ ${voices.length} voix chargées. Voix fr:`, voices.filter(v => v.lang.startsWith('fr')).map(v => v.name))
                // Si un texte était en attente, on le joue maintenant
                if (pendingUtteranceText) {
                    speakText(pendingUtteranceText)
                    pendingUtteranceText = null
                }
            }
        }
        window.speechSynthesis.onvoiceschanged = loadVoices
        loadVoices() // Tentative synchrone (marche sur Firefox/Safari)
    }
})

onUnmounted(() => {
    if (socket.value) socket.value.close()
    if (recognition) recognition.stop()
    if (window.speechSynthesis) window.speechSynthesis.cancel()
    stopAudioPulse()
})
</script>

<template>
  <!-- CONFIGURATION WIZARD -->
  <div v-if="!isInterviewStarted" class="p-6 md:p-10 max-w-4xl mx-auto animate-fade-in-up space-y-8">
     <div class="flex items-center gap-4 border-b border-surface-800 pb-6 mb-8 mt-6">
        <button @click="goBackToDashboard" class="p-2 bg-surface-800 hover:bg-surface-700 rounded-full text-slate-400 hover:text-white transition-colors">
            <ArrowLeftIcon class="w-5 h-5" />
        </button>
        <div>
            <h1 class="text-3xl font-display font-bold text-white tracking-tight">Paramètres de l'Entretien</h1>
            <p class="text-slate-400 mt-1">Configurez le contexte pour que l'IA simule l'entretien parfaitement.</p>
        </div>
     </div>

     <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
         <div class="space-y-5">
             <div>
                <label class="block text-sm font-bold text-slate-300 mb-2 flex items-center gap-2"><BuildingOfficeIcon class="w-4 h-4" /> Entreprise cible <span class="text-rose-500">*</span></label>
                <input v-model="config.company" type="text" placeholder="Ex: Google, Alan, Startup X..." class="w-full bg-surface-900 border border-surface-700 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-colors">
             </div>
             <div>
                <label class="block text-sm font-bold text-slate-300 mb-2 flex items-center gap-2"><BriefcaseIcon class="w-4 h-4" /> Poste visé <span class="text-rose-500">*</span></label>
                <input v-model="config.jobTitle" type="text" placeholder="Ex: Développeur Fullstack, Product Manager..." class="w-full bg-surface-900 border border-surface-700 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-colors">
             </div>
             <div>
                <label class="block text-sm font-bold text-slate-300 mb-2 flex items-center gap-2"><DocumentTextIcon class="w-4 h-4" /> Description de l'offre (Détails)</label>
                <textarea v-model="config.jobDetails" rows="4" placeholder="Collez ici les missions principales de l'offre, la tech stack, ou les prérequis..." class="w-full bg-surface-900 border border-surface-700 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-colors resize-none"></textarea>
             </div>
         </div>
         
         <div class="space-y-5">
             <div>
                <div class="flex items-center justify-between mb-2">
                    <label class="block text-sm font-bold text-slate-300">Votre Profil / CV Actuel</label>
                    <button @click="$refs.fileInput.click()" class="text-xs font-bold bg-indigo-500/10 text-indigo-400 hover:bg-indigo-500/20 px-3 py-1.5 rounded-lg border border-indigo-500/20 transition-colors flex items-center gap-2">
                        <span v-if="isUploadingCV" class="w-3 h-3 border-2 border-indigo-400 border-t-transparent rounded-full animate-spin"></span>
                        <DocumentTextIcon v-else class="w-3.5 h-3.5" />
                        {{ isUploadingCV ? 'Extraction...' : 'Importer un PDF' }}
                    </button>
                    <input type="file" accept=".pdf" class="hidden" ref="fileInput" @change="handleFileUpload">
                </div>
                <textarea v-model="config.cv" rows="5" placeholder="Collez le texte brut de votre CV ou importez un PDF pour que le recruteur puisse réagir dessus..." class="w-full bg-surface-900 border border-surface-700 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-colors resize-none"></textarea>
             </div>
             
             <div>
                 <label class="block text-sm font-bold text-slate-300 mb-3">Format de l'Entretien</label>
                 <div class="grid grid-cols-2 gap-3">
                     <button @click="config.interviewType = 'general'" :class="config.interviewType === 'general' ? 'bg-indigo-500/20 border-indigo-500 text-indigo-400' : 'bg-surface-900 border-surface-700 text-slate-400 hover:border-surface-600'" class="p-4 border rounded-xl flex flex-col items-center justify-center gap-2 transition-all">
                        <span v-if="config.interviewType === 'general'" class="absolute top-2 right-2"><CheckIcon class="w-4 h-4 text-indigo-400" /></span>
                        <span class="font-bold relative">Général & HR</span>
                        <span class="text-[10px] text-center opacity-80">Motivation, soft skills, parcours</span>
                     </button>
                     <button @click="config.interviewType = 'technical'" :class="config.interviewType === 'technical' ? 'bg-rose-500/20 border-rose-500 text-rose-400' : 'bg-surface-900 border-surface-700 text-slate-400 hover:border-surface-600'" class="p-4 border rounded-xl flex flex-col items-center justify-center gap-2 transition-all">
                        <span v-if="config.interviewType === 'technical'" class="absolute top-2 right-2"><CheckIcon class="w-4 h-4 text-rose-400" /></span>
                        <span class="font-bold relative">Technique (QCM)</span>
                        <span class="text-[10px] text-center opacity-80">Connaissances dures, questions pièges</span>
                     </button>
                 </div>
             </div>
         </div>
     </div>
     
     <div v-if="errorMsg" class="mt-4 p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 font-semibold text-sm text-center">
         {{ errorMsg }}
     </div>

     <div class="mt-8 pt-8 border-t border-surface-800 flex justify-end">
         <button @click="startInterview" class="px-8 py-4 bg-gradient-to-r from-indigo-500 to-purple-500 hover:from-indigo-400 hover:to-purple-400 text-white font-bold rounded-xl shadow-lg shadow-indigo-500/30 flex items-center gap-3 transition-all hover:scale-[1.02]">
             Démarrer le Simulateur
             <SparklesIcon class="w-5 h-5" />
         </button>
     </div>
  </div>

  <!-- ACTIVE INTERVIEW UI (SIRI-LIKE) -->
  <div v-else class="fixed inset-0 bg-surface-950 flex flex-col items-center justify-between pointer-events-auto z-[60] overflow-hidden">
    
    <div class="absolute inset-0 flex items-center justify-center pointer-events-none opacity-40">
       <div 
          class="w-96 h-96 bg-indigo-500 rounded-full blur-[140px] transition-all duration-300 ease-out"
          :style="isSpeaking ? `transform: scale(${1 + audioLevel/50}); opacity: 0.6;` : (isListening ? `transform: scale(${1 + audioLevel/40}); background-color: #ec4899; opacity: 0.6;` : 'transform: scale(1)')"
       ></div>
       <div 
          class="absolute w-[600px] h-[600px] bg-violet-600/20 rounded-full blur-[160px] transition-all duration-700"
          :class="isSpeaking || isListening ? 'scale-110 opacity-60' : 'scale-90 opacity-30'"
       ></div>
    </div>

    <!-- Header -->
    <header class="w-full p-6 flex items-center justify-between relative z-10">
        <button @click="stopInterview" class="flex items-center gap-2 text-slate-400 hover:text-white transition-colors bg-surface-900/50 hover:bg-surface-800 px-4 py-2 rounded-full backdrop-blur border border-surface-800">
            <ArrowLeftIcon class="w-4 h-4" />
            <span class="text-sm font-bold uppercase tracking-wider">Interrompre l'entretien</span>
        </button>
        
        <div class="flex items-center gap-2 bg-surface-900/50 backdrop-blur border border-surface-800 px-4 py-2 rounded-full shadow-lg">
            <span class="relative flex h-2.5 w-2.5">
              <span v-if="isSpeaking || isListening" class="animate-ping absolute inline-flex h-full w-full rounded-full opacity-75" :class="isListening ? 'bg-pink-400' : 'bg-indigo-400'"></span>
              <span class="relative inline-flex rounded-full h-2.5 w-2.5" :class="isListening ? 'bg-pink-500' : (isSpeaking ? 'bg-indigo-500' : 'bg-slate-500')"></span>
            </span>
            <span class="text-xs font-bold text-white uppercase tracking-widest">
                {{ isAIThinking ? 'Le Recruteur réfléchit...' : (isListening ? 'Vous Parlez...' : (isSpeaking ? 'Le Recruteur Parle...' : 'En Attente')) }}
            </span>
        </div>
    </header>

    <!-- Chat / Transcription History Area -->
    <main class="flex-1 w-full max-w-3xl px-6 py-8 overflow-y-auto relative z-10 flex flex-col gap-8 scroll-smooth" ref="chatContainer">
        
        <div v-for="msg in conversation" :key="msg.id" class="flex w-full animate-fade-in-up" :class="msg.role === 'user' ? 'justify-end' : 'justify-start'">
            <div class="flex flex-col gap-2 max-w-[85%]">
                <!-- Message Label -->
                <div class="flex items-center gap-2 px-3" :class="msg.role === 'user' ? 'justify-end' : 'justify-start'">
                    <span class="text-[10px] uppercase tracking-widest font-bold font-display" :class="msg.role === 'user' ? 'text-slate-500' : 'text-indigo-400'">
                        {{ msg.role === 'user' ? 'Vous' : 'Recruteur' }}
                    </span>
                    <SparklesIcon v-if="msg.role === 'assistant'" class="w-3 h-3 text-indigo-400 animate-pulse" />
                </div>

                <div 
                   class="rounded-3xl px-6 py-5 backdrop-blur-md shadow-2xl transition-all duration-500"
                   :class="msg.role === 'user' 
                     ? 'bg-white/5 border border-white/10 text-slate-200 rounded-br-sm shadow-indigo-500/5' 
                     : 'bg-indigo-600/10 border border-indigo-500/30 text-indigo-50 rounded-bl-sm shadow-indigo-500/10'"
                >
                    <p class="text-[16px] leading-relaxed font-medium whitespace-pre-wrap select-text selection:bg-indigo-500/30">{{ msg.content }}</p>
                </div>
            </div>
        </div>
        
        <!-- Live Transcript -->
        <div v-if="transcript" class="flex w-full justify-end opacity-60 animate-pulse">
            <div class="max-w-[80%] rounded-2xl px-5 py-3 bg-surface-800/50 text-slate-300 border border-surface-700/50 border-dashed rounded-br-sm">
                <p class="text-sm leading-relaxed font-medium italic">{{ transcript }}...</p>
            </div>
        </div>
    </main>

    <!-- Main Siri/Orb Interaction Area -->
    <div class="w-full pb-16 pt-8 flex flex-col items-center justify-center relative z-10 bg-gradient-to-t from-surface-950 via-surface-950/80 to-transparent">
        
        <!-- The Orb Button -->
        <button 
            @click="triggerListen"
            class="relative group rounded-full p-1"
        >
            <div 
              class="absolute inset-0 rounded-full blur-xl transition-all duration-300"
              :class="isListening ? 'bg-pink-500/50 scale-150 shadow-[0_0_30px_#ec4899]' : 'bg-indigo-500/30 scale-100 group-hover:bg-indigo-400/50 group-hover:scale-125'"
            ></div>
            
            <div 
              class="w-24 h-24 rounded-full flex items-center justify-center relative z-10 shadow-2xl transition-all duration-300 border"
              :class="isListening ? 'bg-gradient-to-br from-pink-500 to-rose-600 border-pink-400/50 scale-110' : 'bg-surface-800 border-surface-700 hover:border-indigo-500/50 bg-gradient-to-b hover:from-surface-700 hover:to-surface-800'"
            >
                <StopIcon v-if="isListening" class="w-10 h-10 text-white" />
                <MicrophoneIcon v-else class="w-10 h-10 text-indigo-100 group-hover:text-white transition-colors" />
            </div>
        </button>

        <p class="mt-8 text-sm font-bold tracking-wide max-w-sm text-center px-4 h-16 flex items-center justify-center">
            <span v-if="isAIThinking" class="text-indigo-400 flex items-center gap-3 animate-pulse bg-indigo-500/5 px-6 py-3 rounded-full border border-indigo-500/20">
                <span class="flex gap-1">
                    <span class="w-1.5 h-1.5 bg-indigo-400 rounded-full animate-bounce [animation-delay:-0.3s]"></span>
                    <span class="w-1.5 h-1.5 bg-indigo-400 rounded-full animate-bounce [animation-delay:-0.15s]"></span>
                    <span class="w-1.5 h-1.5 bg-indigo-400 rounded-full animate-bounce"></span>
                </span>
                Analyse de votre réponse...
            </span>
            <span v-else-if="isSpeaking" class="text-indigo-300 flex items-center gap-2 bg-indigo-500/10 px-6 py-3 rounded-full border border-indigo-500/10">
                <SparklesIcon class="w-4 h-4" /> Écoute du recruteur
            </span>
            <span v-else-if="isListening" class="text-pink-400 flex flex-col items-center gap-1 animate-fadeIn">
                <span class="bg-pink-500/10 px-6 py-3 rounded-full border border-pink-500/20 shadow-lg shadow-pink-500/5">
                    À vous de parler !
                </span>
                <span class="text-[10px] mt-2 opacity-60 uppercase tracking-widest">(Cliquez pour envoyer maintenant)</span>
            </span>
            <span v-else class="text-slate-400 flex flex-col items-center gap-2 group-hover:text-slate-300 transition-colors">
                <span class="bg-surface-900 border border-surface-800 px-8 py-3 rounded-full shadow-inner hover:border-indigo-500/30 transition-all cursor-pointer" @click="triggerListen">
                    Cliquez sur le microphone pour répondre.
                </span>
                <span class="text-[10px] opacity-40 uppercase tracking-tighter">Votre assistant vous écoute puis analyse votre réponse</span>
            </span>
        </p>

    </div>

  </div>
</template>
