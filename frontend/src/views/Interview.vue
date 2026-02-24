<script setup>
import { ref, onMounted, onUnmounted, nextTick, computed } from 'vue'
import { useRouter } from 'vue-router'
import { MicrophoneIcon, StopIcon, ArrowLeftIcon, SparklesIcon, DocumentTextIcon, BriefcaseIcon, BuildingOfficeIcon, VideoCameraIcon, VideoCameraSlashIcon, ChatBubbleLeftRightIcon, XMarkIcon, UserIcon, PhoneIcon, SpeakerWaveIcon, PlayIcon } from '@heroicons/vue/24/outline'
import { CheckIcon, UserCircleIcon } from '@heroicons/vue/24/solid'

const router = useRouter()

// Phase states
const isInterviewStarted = ref(false)

// Config Form Data
const config = ref({
    cv: '',
    jobTitle: '',
    company: '',
    jobDetails: '',
    interviewType: 'general',
    recruiterId: 'tech' // 'tech', 'hr', 'ceo'
})

const recruiters = [
    { id: 'tech', name: 'Sophie - Tech Lead', role: 'Expertise Technique', img: '/avatars/tech.png' },
    { id: 'hr', name: 'Marc - HR Manager', role: 'Culture & Soft Skills', img: '/avatars/hr.png' },
    { id: 'ceo', name: 'Alice - CEO', role: 'Vision & Strategie', img: '/avatars/ceo.png' }
]

const currentRecruiter = computed(() => recruiters.find(r => r.id === config.value.recruiterId))

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
const analystNote = ref(null)
const userVideo = ref(null)
const stream = ref(null)
const showChat = ref(false)
const ttsStatus = ref('Initialisation...') // Diagnostic status
const lastTtsError = ref(null)

// Visual audio pulse simulation
const audioLevel = ref(0)
let audioInterval = null

let recognition = null;
let currentSynthesis = null;
let cachedVoices = []; // ✅ Voix mémorisées dès le chargement de la page
let pendingUtteranceText = null; // Texte en attente si les voix ne sont pas prêtes

const startInterview = async () => {
    if (!config.value.jobTitle || !config.value.company) {
        errorMsg.value = "Poste et Entreprise sont requis."
        return
    }
    errorMsg.value = ""
    isInterviewStarted.value = true
    
    // Hack: Débloquer l'audio immédiatement sur le geste utilisateur
    if (window.speechSynthesis) {
        const unlock = new SpeechSynthesisUtterance("")
        unlock.volume = 0
        window.speechSynthesis.speak(unlock)
        window.speechSynthesis.resume()
    }
    
    // Start Camera
    await startWebcam()
    
    // Initialize Web Speech API
    const hasSpeech = initSpeechRecognition()
    if (hasSpeech) {
        connectWebSocket()
    }
}

const startWebcam = async () => {
    try {
        const mediaStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false })
        stream.value = mediaStream
        if (userVideo.value) {
            userVideo.value.srcObject = mediaStream
        }
    } catch (err) {
        console.warn("Camera access denied or unavailable:", err)
    }
}

const stopWebcam = () => {
    if (stream.value) {
        stream.value.getTracks().forEach(track => track.stop())
        stream.value = null
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
    
    try {
        socket.value = new WebSocket(`ws://localhost:8000/api/interview/ws?token=${token}`)
        
        socket.value.onopen = () => {
            console.log("Connecté au Mentor IA")
            socket.value.send(JSON.stringify({
                type: 'setup',
                payload: config.value
            }))
        }
        
        socket.value.onmessage = (event) => {
            const msg = JSON.parse(event.data)
            
            if (msg.type === 'message' || msg.type === 'chunk') {
                isAIThinking.value = false
                const content = msg.content
                if (msg.type === 'message') {
                    conversation.value.push({ id: Date.now(), role: 'assistant', content: content })
                } else {
                    if (conversation.value.length === 0 || conversation.value[conversation.value.length - 1].role !== 'assistant') {
                        conversation.value.push({ id: Date.now(), role: 'assistant', content: content })
                    } else {
                        conversation.value[conversation.value.length - 1].content += content
                    }
                }
                scrollToBottom()
            } else if (msg.type === 'analysis') {
                analystNote.value = msg.payload
                setTimeout(() => { analystNote.value = null }, 8000)
            } else if (msg.type === 'voice') {
                // HD Voice from Backend (edge-tts)
                playHDAudio(msg.audio)
            } else if (msg.type === 'done') {
                // Legacy speakText is now handled by the 'voice' message event for better quality
                // and avoid dual audio. We keep a console log for debugging.
                console.log("Flux texte terminé, en attente du flux audio HD...")
            } else if (msg.type === 'error') {
                isAIThinking.value = false
                errorMsg.value = msg.message
            }
        }
        
        socket.value.onclose = () => {
            console.log("WebSocket Interview fermé")
        }
    } catch (e) {
        errorMsg.value = "Erreur de connexion au serveur d'entretien."
    }
}

const sendMessageToAI = (text) => {
    if (!socket.value || socket.value.readyState !== WebSocket.OPEN) return
    
    conversation.value.push({ id: Date.now(), role: 'user', content: text })
    isAIThinking.value = true
    analystNote.value = null // Reset last note
    nextTick(scrollToBottom)
    
    if (window.speechSynthesis) window.speechSynthesis.cancel()
    socket.value.send(JSON.stringify({ text: text }))
}

// Prend les voix en cache ou les voix disponibles maintenant
const getVoice = () => {
    const voices = cachedVoices.length > 0 ? cachedVoices : window.speechSynthesis.getVoices()
    if (voices.length === 0) {
        ttsStatus.value = "Aucune voix système"
        return null
    }
    
    const frVoices = voices.filter(v => v.lang.startsWith('fr'))
    
    // NOUVELLE PRIORITÉ : On évite les voix "Online" qui font souvent du "synthesis-failed"
    // On cherche d'abord les voix Microsoft ou Google locales, puis les voix simples
    const selected = frVoices.find(v => !v.name.includes('Online') && (v.name.includes('Thomas') || v.name.includes('Henri') || v.name.includes('Hortense') || v.name.includes('Julie')))
        || frVoices.find(v => !v.name.includes('Online'))
        || frVoices[0] 
        || voices[0]
        
    if (selected) {
        ttsStatus.value = `Voix: ${selected.name}`
        console.log("Voix sélectionnée:", selected.name, "Online:", selected.name.includes('Online'))
    }
    return selected
}

const testAudio = async () => {
    ttsStatus.value = "Génération du test HD..."
    try {
        const response = await fetch('http://localhost:8000/api/interview/test-voice', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                text: `Bonjour, je suis ${currentRecruiter.value.name}. Je suis prête à commencer votre entretien en Haute Définition. M'entendez-vous bien ?`,
                recruiterId: config.value.recruiterId
            })
        })
        const result = await response.json()
        if (result.status === 'success') {
            playHDAudio(result.audio)
        } else {
            ttsStatus.value = "Erreur Test HD"
            // Fallback sur TTS local pour diagnostic
            speakText("Le test Haute Définition a échoué. Voici la voix locale de secours.")
        }
    } catch (e) {
        console.error("Test Voice Error:", e)
        ttsStatus.value = "Erreur connexion"
        speakText("Erreur de connexion au serveur audio.")
    }
}

/**
 * Joue l'audio Haute Définition (edge-tts) reçu du backend
 */
const playHDAudio = (base64Data) => {
    if (!base64Data) return
    
    ttsStatus.value = "Lecture audio HD..."
    window.speechSynthesis.cancel() // On coupe le TTS local au cas où
    
    try {
        const audio = new Audio(`data:audio/mp3;base64,${base64Data}`)
        
        audio.onplay = () => {
            isSpeaking.value = true
            startAudioPulse()
            if (recognition) { try { recognition.stop() } catch(e) {} }
        }
        
        audio.onended = () => {
            isSpeaking.value = false
            stopAudioPulse()
            ttsStatus.value = "Prêt (HD)"
            
            // Relancer le micro
            setTimeout(() => {
                if (!isListening.value && recognition && isInterviewStarted.value) {
                    try { recognition.start() } catch(e) {}
                }
            }, 800)
        }
        
        audio.onerror = (e) => {
            console.error("HD Audio error:", e)
            ttsStatus.value = "Erreur Audio HD"
            isSpeaking.value = false
        }
        
        audio.play()
    } catch (err) {
        console.error("Failed to play HD Audio:", err)
        ttsStatus.value = "Erreur lecture HD"
    }
}

let retryCount = 0;
const speakText = (text) => {
    if (!window.speechSynthesis || !text?.trim()) return
    
    ttsStatus.value = "Préparation..."
    
    // HACK CRITIQUE : On cancel d'abord
    window.speechSynthesis.cancel()
    
    // On attend un tout petit peu que le moteur audio soit "propre" (Fix Chrome)
    setTimeout(() => {
        const utterance = new SpeechSynthesisUtterance(text)
        utterance.lang = 'fr-FR'
        utterance.rate = 1.0
        utterance.pitch = 1.0
        utterance.volume = 1.0
        
        const voice = getVoice()
        if (voice) utterance.voice = voice
        
        utterance.onstart = () => {
            ttsStatus.value = "IA parle..."
            isSpeaking.value = true
            startAudioPulse()
            retryCount = 0
            if (recognition) { try { recognition.stop() } catch(e) {} }
        }
        
        utterance.onend = () => {
            ttsStatus.value = "Prêt"
            isSpeaking.value = false
            stopAudioPulse()
            setTimeout(() => {
                if (!isListening.value && recognition && isInterviewStarted.value) {
                    try { recognition.start() } catch(e) {}
                }
            }, 800)
        }
        
        utterance.onerror = (e) => {
            console.error("SpeechSynthesis error:", e.error)
            ttsStatus.value = `Erreur: ${e.error}`
            isSpeaking.value = false
            stopAudioPulse()
            
            // Tentative de secours : on change de voix et on réessaie une fois
            if (retryCount < 2) {
                console.warn("Échec synthèse, tentative de secours...")
                retryCount++
                speakText(text)
            }
        }
        
        window.speechSynthesis.resume()
        window.speechSynthesis.speak(utterance)
    }, 100)
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

const goBackToDashboard = () => router.push('/dashboard')

const stopInterview = () => {
    isInterviewStarted.value = false
    if (socket.value) socket.value.close()
    if (recognition) recognition.stop()
    if (window.speechSynthesis) window.speechSynthesis.cancel()
    stopWebcam()
    stopAudioPulse()
    conversation.value = []
}

onUnmounted(() => {
    stopInterview()
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
                  <label class="block text-sm font-bold text-slate-300 mb-3">Choix du Recruteur</label>
                  <div class="grid grid-cols-3 gap-3">
                      <button v-for="r in recruiters" :key="r.id" 
                         @click="config.recruiterId = r.id" 
                         :class="config.recruiterId === r.id ? 'bg-indigo-500/20 border-indigo-500 ring-2 ring-indigo-500/10' : 'bg-surface-900 border-surface-700 hover:border-surface-600'"
                         class="p-3 border rounded-xl flex flex-col items-center gap-2 transition-all relative overflow-hidden group"
                      >
                         <img :src="r.img" class="w-14 h-14 rounded-full object-cover border-2 border-surface-800 group-hover:scale-105 transition-transform" />
                         <span class="text-[11px] font-bold text-white text-center leading-tight">{{ r.name }}</span>
                         <span class="text-[9px] text-slate-500 uppercase tracking-tighter">{{ r.role }}</span>
                         <CheckIcon v-if="config.recruiterId === r.id" class="absolute top-1 right-1 w-3 h-3 text-indigo-400" />
                      </button>
                  </div>
              </div>

              <div>
                  <label class="block text-sm font-bold text-slate-300 mb-3">Format de l'Entretien</label>
                  <div class="grid grid-cols-2 gap-3">
                      <button @click="config.interviewType = 'general'" :class="config.interviewType === 'general' ? 'bg-indigo-500/20 border-indigo-500 text-indigo-400' : 'bg-surface-900 border-surface-700 text-slate-400 hover:border-surface-600'" class="p-4 border rounded-xl flex flex-col items-center justify-center gap-2 transition-all">
                         <span v-if="config.interviewType === 'general'" class="absolute top-2 right-2"><CheckIcon class="w-4 h-4 text-indigo-400" /></span>
                         <span class="font-bold relative text-sm">Général & HR</span>
                      </button>
                      <button @click="config.interviewType = 'technical'" :class="config.interviewType === 'technical' ? 'bg-rose-500/20 border-rose-500 text-rose-400' : 'bg-surface-900 border-surface-700 text-slate-400 hover:border-surface-600'" class="p-4 border rounded-xl flex flex-col items-center justify-center gap-2 transition-all">
                         <span v-if="config.interviewType === 'technical'" class="absolute top-2 right-2"><CheckIcon class="w-4 h-4 text-rose-400" /></span>
                         <span class="font-bold relative text-sm">Technique</span>
                      </button>
                  </div>
              </div>
          </div>
      </div>
      
      <div v-if="errorMsg" class="mt-4 p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 font-semibold text-sm text-center animate-shake">
          {{ errorMsg }}
      </div>

      <div class="mt-8 pt-8 border-t border-surface-800 flex items-center justify-between">
          <div class="flex items-center gap-4">
              <button @click="testAudio" class="px-4 py-2 bg-surface-800 hover:bg-surface-700 text-indigo-400 text-xs font-bold rounded-lg border border-indigo-500/20 flex items-center gap-2 transition-all">
                  <SpeakerWaveIcon class="w-4 h-4" />
                  Tester le son
              </button>
              <span v-if="ttsStatus" class="text-[10px] text-slate-500 uppercase font-medium">{{ ttsStatus }}</span>
          </div>
          <button @click="startInterview" class="px-8 py-4 bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-400 hover:to-purple-500 text-white font-bold rounded-xl shadow-xl shadow-indigo-500/20 flex items-center gap-3 transition-all hover:scale-[1.05] active:scale-95">
              Lancer la Visioconférence
              <VideoCameraIcon class="w-5 h-5" />
          </button>
      </div>
   </div>

   <!-- IMMERSIVE VIDEO CALL UI -->
   <div v-else class="fixed inset-0 bg-black flex flex-col pointer-events-auto z-[60] overflow-hidden font-sans">
      
      <!-- BACKGROUND / RECRUITER VIDEO AREA -->
      <div class="absolute inset-0 z-0">
          <img 
            :src="currentRecruiter?.img" 
            class="w-full h-full object-cover transition-all duration-1000"
            :class="isAIThinking ? 'blur-sm scale-110' : 'blur-none scale-100'"
          />
          <!-- Screen Overlay for dark/meeting vibe -->
          <div class="absolute inset-0 bg-gradient-to-t from-black via-transparent to-black/40"></div>
          
          <!-- Pulse / Aura effect around the AI face -->
          <div class="absolute inset-0 flex items-center justify-center pointer-events-none">
              <div 
                class="w-[500px] h-[500px] rounded-full blur-[120px] transition-all duration-300 pointer-events-none opacity-40 mix-blend-screen"
                :style="isSpeaking ? `background-color: #6366f1; transform: scale(${1 + audioLevel/50});` : 'background-color: transparent'"
              ></div>
          </div>
      </div>

      <!-- TOP BAR -->
      <header class="absolute top-0 w-full p-6 flex items-center justify-between z-20">
          <div class="flex items-center gap-4">
              <div class="bg-black/40 backdrop-blur-xl border border-white/10 px-4 py-2 rounded-2xl flex items-center gap-3">
                  <BuildingOfficeIcon class="w-4 h-4 text-indigo-400" />
                  <span class="text-xs font-bold text-white tracking-widest uppercase">{{ config.company }} — {{ currentRecruiter?.role }}</span>
              </div>
          </div>

          <div class="flex items-center gap-3">
              <div v-if="ttsStatus" class="bg-black/40 backdrop-blur-xl border border-white/5 px-3 py-1.5 rounded-xl hidden md:flex items-center gap-2">
                  <SpeakerWaveIcon class="w-3 h-3 text-indigo-400" />
                  <span class="text-[9px] font-bold text-indigo-200 uppercase tracking-widest">{{ ttsStatus.includes('HD') ? 'Son Haute-Fidélité' : ttsStatus }}</span>
              </div>
              <div class="bg-indigo-500/20 backdrop-blur-xl border border-indigo-500/30 px-4 py-2 rounded-2xl flex items-center gap-3">
                  <div class="w-2 h-2 rounded-full bg-indigo-400 animate-pulse"></div>
                  <span class="text-xs font-bold text-indigo-100 uppercase tracking-tighter">{{ currentRecruiter?.name }}</span>
              </div>
          </div>
      </header>

      <!-- ANALYST TIPS (Nano Banana) -->
      <div v-if="analystNote" class="absolute left-6 top-24 z-30 max-w-xs animate-fade-in-right">
          <div class="bg-white/10 backdrop-blur-2xl border border-white/20 p-4 rounded-2xl shadow-2xl">
              <div class="flex items-center gap-2 mb-2">
                  <SparklesIcon class="w-4 h-4 text-yellow-400" />
                  <span class="text-[10px] uppercase font-black tracking-widest text-slate-400">Notes de l'Analyste</span>
              </div>
              <p class="text-sm font-medium text-white leading-relaxed">{{ analystNote.tip }}</p>
              <div class="mt-2 flex items-center gap-2">
                  <div class="text-[8px] bg-white/5 border border-white/10 px-2 py-0.5 rounded text-slate-400 uppercase">{{ analystNote.sentiment }}</div>
              </div>
          </div>
      </div>

      <!-- USER WEBCAM (VIGNETTE) -->
      <div class="absolute right-6 bottom-32 w-48 md:w-64 aspect-video bg-surface-900 rounded-2xl border-2 border-white/20 shadow-2xl overflow-hidden z-20 group transition-all"
           :class="isListening ? 'border-pink-500 scale-105 shadow-pink-500/20' : ''">
          <video ref="userVideo" autoplay playsinline muted class="w-full h-full object-cover grayscale-[0.3]"></video>
          <div v-if="!stream" class="absolute inset-0 flex items-center justify-center bg-surface-950 flex-col gap-2">
              <VideoCameraSlashIcon class="w-8 h-8 text-slate-700" />
              <span class="text-[10px] text-slate-500 uppercase font-bold">Caméra désactivée</span>
          </div>
          <div class="absolute bottom-2 left-2 flex items-center gap-1.5 bg-black/60 backdrop-blur px-2 py-1 rounded-lg">
              <UserIcon class="w-3 h-3 text-slate-300" />
              <span class="text-[9px] font-bold text-white uppercase">Moi</span>
          </div>
      </div>

      <!-- TRANSCRIPTION DRAWER (Toggleable) -->
      <div v-if="showChat" class="absolute left-6 bottom-32 w-80 max-h-[40%] bg-black/60 backdrop-blur-3xl border border-white/10 rounded-3xl z-40 flex flex-col overflow-hidden animate-fade-in-up">
          <div class="p-4 border-b border-white/5 flex items-center justify-between">
              <span class="text-xs font-black uppercase text-slate-400">Transcription</span>
              <button @click="showChat = false" class="p-1 hover:bg-white/10 rounded-lg text-slate-400"><XMarkIcon class="w-4 h-4" /></button>
          </div>
          <div class="flex-1 overflow-y-auto p-4 space-y-4 text-sm scroll-smooth" ref="chatContainer">
              <div v-for="msg in conversation" :key="msg.id" :class="msg.role === 'user' ? 'text-indigo-200' : 'text-slate-300'">
                  <span class="font-bold text-[10px] block opacity-50">{{ msg.role === 'user' ? 'VOUS' : 'RECRUTEUR' }}</span>
                  {{ msg.content }}
              </div>
              <div v-if="transcript" class="text-pink-300 italic opacity-60">{{ transcript }}...</div>
          </div>
      </div>

      <!-- MEETING TOOLBAR -->
      <div class="absolute bottom-10 w-full flex items-center justify-center gap-6 z-50">
          <div class="bg-white/5 backdrop-blur-3xl border border-white/10 p-2 rounded-full flex items-center gap-3 shadow-[0_0_50px_rgba(0,0,0,0.5)]">
              
              <!-- Toggle Transcription -->
              <button @click="showChat = !showChat" 
                :class="showChat ? 'bg-white/20 text-white' : 'text-slate-400 hover:text-white'"
                class="p-4 rounded-full transition-all" title="Transcription">
                  <ChatBubbleLeftRightIcon class="w-6 h-6" />
              </button>

              <!-- Manual Audio Recovery -->
              <button @click="testAudio" 
                class="p-4 rounded-full text-slate-400 hover:text-indigo-400 transition-all border border-dashed border-white/5" title="Relancer le son">
                  <SpeakerWaveIcon class="w-6 h-6" />
              </button>

              <!-- Main Interaction Button (The Orb) -->
              <button @click="triggerListen" class="relative group">
                  <div class="absolute inset-0 rounded-full blur-2xl transition-all duration-500 group-hover:scale-125"
                    :class="isListening ? 'bg-pink-500/50' : (isAIThinking ? 'bg-indigo-500/50' : 'bg-white/5')"></div>
                  
                  <div class="w-20 h-20 rounded-full flex items-center justify-center border-4 relative z-10 transition-all duration-300"
                    :class="isListening 
                       ? 'bg-pink-500 border-pink-400 shadow-[0_0_30px_#ec4899] scale-110' 
                       : (isAIThinking ? 'bg-indigo-600 border-indigo-400 animate-pulse' : 'bg-surface-800 border-white/20 group-hover:border-white/40')">
                      
                      <div v-if="isAIThinking" class="flex gap-1">
                          <span class="w-2 h-2 bg-white rounded-full animate-bounce [animation-delay:-0.3s]"></span>
                          <span class="w-2 h-2 bg-white rounded-full animate-bounce [animation-delay:-0.15s]"></span>
                          <span class="w-2 h-2 bg-white rounded-full animate-bounce"></span>
                      </div>
                      <StopIcon v-else-if="isListening" class="w-10 h-10 text-white" />
                      <MicrophoneIcon v-else class="w-10 h-10 text-white" />
                  </div>
              </button>

              <!-- End Call Button -->
              <button @click="stopInterview" class="p-4 rounded-full text-rose-500 hover:bg-rose-500/20 transition-all">
                  <div class="bg-rose-600 p-2.5 rounded-full rotate-[135deg] shadow-lg shadow-rose-900/50">
                      <PhoneIcon class="w-6 h-6 text-white" />
                  </div>
              </button>
          </div>
      </div>

      <!-- Live status text -->
      <div v-if="isListening" class="absolute bottom-32 left-1/2 -translate-x-1/2 text-pink-400 font-black uppercase tracking-[0.3em] text-xs animate-pulse z-10 drop-shadow-lg">
          Microphone Actif — Parlez Maintenant
      </div>
   </div>
</template>
