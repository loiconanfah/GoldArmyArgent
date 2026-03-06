<script setup>
import { ref, onMounted, onUnmounted, nextTick, computed } from 'vue'
import { useRouter } from 'vue-router'
import { authFetch } from '../utils/auth'
import { getWsUrl, getApiUrl } from '../config'
import { MicrophoneIcon, StopIcon, ArrowLeftIcon, SparklesIcon, DocumentTextIcon, BriefcaseIcon, BuildingOfficeIcon, VideoCameraSlashIcon, ChatBubbleLeftRightIcon, XMarkIcon, UserIcon, PhoneIcon, SpeakerWaveIcon, PlayIcon, ChartBarIcon, AcademicCapIcon, CheckCircleIcon } from '@heroicons/vue/24/outline'
import { CheckIcon, UserCircleIcon, StarIcon, VideoCameraIcon } from '@heroicons/vue/24/solid'

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
const showChat = ref(true) // Transcription visible par défaut pour lire l'entretien
const showScorecard = ref(false)
const isAnalyzing = ref(false)
const scorecard = ref(null)
const ttsStatus = ref('Initialisation...') // Diagnostic status
const lastTtsError = ref(null)
const pendingFinish = ref(false)
const callStartTime = ref(null)
const callElapsed = ref('00:00')
let callTimerInterval = null

// Visual audio pulse simulation
const audioLevel = ref(0)
let audioInterval = null

let recognition = null;
let currentSynthesis = null;
let currentHDAudio = null; // Une seule piste HD à la fois (évite la voix en double)
let cachedVoices = []; // ✅ Voix mémorisées dès le chargement de la page
let pendingUtteranceText = null; // Texte en attente si les voix ne sont pas prêtes
let accumulatedTranscript = ''; // ✅ Evite que la phrase soit coupée entre deux respirations

const startInterview = async () => {
    if (!config.value.jobTitle || !config.value.company || !config.value.cv) {
        errorMsg.value = "Poste, Entreprise et CV sont obligatoires."
        return
    }

    errorMsg.value = ""
    isInterviewStarted.value = true
    callStartTime.value = Date.now()
    callTimerInterval = setInterval(() => {
        if (!callStartTime.value) return
        const s = Math.floor((Date.now() - callStartTime.value) / 1000)
        const m = Math.floor(s / 60)
        callElapsed.value = `${String(m).padStart(2, '0')}:${String(s % 60).padStart(2, '0')}`
    }, 1000)
    
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
        const response = await authFetch('/api/parse-pdf', {
            method: 'POST',
            body: formData
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

        for (let i = event.resultIndex; i < event.results.length; ++i) {
            if (event.results[i].isFinal) {
                accumulatedTranscript += event.results[i][0].transcript + ' '
            } else {
                interimTranscript += event.results[i][0].transcript
            }
        }
        
        transcript.value = accumulatedTranscript + interimTranscript
        
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
        if (recognition._noSpeechRestartTimer) {
            clearTimeout(recognition._noSpeechRestartTimer)
            recognition._noSpeechRestartTimer = null
        }
        // On n'envoie que si on a un transcrit et qu'on n'est pas déjà en train de parler
        if (accumulatedTranscript.trim() !== '' && !isSpeaking.value) {
            sendMessageToAI(accumulatedTranscript.trim())
            accumulatedTranscript = ''
            transcript.value = ''
        } else if (!isSpeaking.value && isInterviewStarted.value) {
            // Si le micro s'arrête sans texte (timeout navigateur), relancer après un court délai pour éviter la boucle no-speech
            recognition._noSpeechRestartTimer = setTimeout(() => {
                recognition._noSpeechRestartTimer = null
                try { recognition.start() } catch(e) {}
            }, 800)
        }
    }
    
    recognition.onerror = (event) => {
        if (recognition._noSpeechRestartTimer) {
            clearTimeout(recognition._noSpeechRestartTimer)
            recognition._noSpeechRestartTimer = null
        }
        isListening.value = false
        stopAudioPulse()
        if (event.error === 'no-speech' || event.error === 'aborted') {
            // Ne pas afficher d'erreur à l'utilisateur ; relancer le micro après un délai pour éviter le spam
            if (isInterviewStarted.value && !isSpeaking.value) {
                setTimeout(() => {
                    try { recognition.start() } catch(e) {}
                }, 1000)
            }
            return
        }
        console.error("Speech recognition error", event.error)
        errorMsg.value = "Erreur micro: " + event.error
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
        socket.value = new WebSocket(getWsUrl(`/api/interview/ws?token=${token}`))
        
        socket.value.onopen = () => {
            console.log("Connecté au Mentor IA")
            socket.value.send(JSON.stringify({
                type: 'setup',
                payload: config.value
            }))
        }
        
        socket.value.onmessage = (event) => {
            const msg = JSON.parse(event.data)
            
            // Texte du recruteur (backend envoie "recruiter_response" avec .text)
            if (msg.type === 'recruiter_response' && msg.text) {
                isAIThinking.value = false
                const content = msg.text
                if (conversation.value.length && conversation.value[conversation.value.length - 1].role === 'assistant') {
                    conversation.value[conversation.value.length - 1].content = content
                } else {
                    conversation.value.push({ id: Date.now(), role: 'assistant', content })
                }
                const endKeywords = ['au revoir', 'bonne journée', 'bonne chance', 'merci pour votre temps', 'bientôt', 'clôturer', 'fini cet entretien']
                if (endKeywords.some(k => content.toLowerCase().includes(k))) pendingFinish.value = true
                scrollToBottom()
            } else if (msg.type === 'message' || msg.type === 'chunk') {
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
                const endKeywords = ['au revoir', 'bonne journée', 'bonne chance', 'merci pour votre temps', 'bientôt', 'clôturer', 'fini cet entretien']
                if (endKeywords.some(k => content.toLowerCase().includes(k))) pendingFinish.value = true
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
                // Si l'erreur arrive au début, on reset pour afficher l'erreur sur le wizard
                if (conversation.value.length === 0) {
                    isInterviewStarted.value = false
                    stopWebcam()
                }
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
        const response = await authFetch('/api/interview/test-voice', {
            method: 'POST',
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
 * Joue l'audio Haute Définition (edge-tts) reçu du backend.
 * Une seule piste à la fois : on arrête toute lecture HD précédente pour éviter la voix en double.
 */
const playHDAudio = (base64Data) => {
    if (!base64Data) return

    if (currentHDAudio) {
        try {
            currentHDAudio.pause()
            currentHDAudio.currentTime = 0
            currentHDAudio.src = ''
        } catch (e) {}
        currentHDAudio = null
    }
    window.speechSynthesis.cancel() // TTS local coupé pour n'avoir qu'une seule voix

    ttsStatus.value = "Lecture audio HD..."
    try {
        const audio = new Audio(`data:audio/mp3;base64,${base64Data}`)
        currentHDAudio = audio

        audio.onplay = () => {
            isSpeaking.value = true
            startAudioPulse()
            if (recognition) { try { recognition.stop() } catch(e) {} }
        }

        audio.onended = () => {
            currentHDAudio = null
            isSpeaking.value = false
            stopAudioPulse()
            ttsStatus.value = "Prêt (HD)"
            setTimeout(() => {
                if (pendingFinish.value) {
                    finishInterview()
                    pendingFinish.value = false
                    return
                }
                if (!isListening.value && recognition && isInterviewStarted.value) {
                    try { recognition.start() } catch(e) {}
                }
            }, 800)
        }

        audio.onerror = (e) => {
            currentHDAudio = null
            console.error("HD Audio error:", e)
            ttsStatus.value = "Erreur Audio HD"
            isSpeaking.value = false
        }

        audio.play()
    } catch (err) {
        currentHDAudio = null
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
    callStartTime.value = null
    if (callTimerInterval) clearInterval(callTimerInterval)
    callTimerInterval = null
    showScorecard.value = false
    scorecard.value = null
    if (socket.value) socket.value.close()
    if (recognition) recognition.stop()
    if (window.speechSynthesis) window.speechSynthesis.cancel()
    if (currentHDAudio) {
        try { currentHDAudio.pause(); currentHDAudio.src = '' } catch (e) {}
        currentHDAudio = null
    }
    stopWebcam()
    stopAudioPulse()
    conversation.value = []
}

/**
 * Termine l'entretien proprement et lance l'analyse
 */
const finishInterview = async () => {
    if (isAnalyzing.value) return
    
    // Si l'entretien n'est pas commencé ou si on est déjà au score, on quitte juste
    if (!isInterviewStarted.value) {
        goBackToDashboard()
        return
    }

    isAnalyzing.value = true
    showScorecard.value = true // On affiche le modal de chargement
    
    // Arrêt des flux
    if (recognition) try { recognition.stop() } catch(e){}
    if (window.speechSynthesis) window.speechSynthesis.cancel()
    stopAudioPulse()
    
    try {
        const response = await authFetch('/api/interview/analyze', {
            method: 'POST',
            body: JSON.stringify({
                history: conversation.value,
                jobTitle: config.value.jobTitle
            })
        })
        const result = await response.json()
        if (result.status === 'success') {
            scorecard.value = result.analysis
        } else {
            errorMsg.value = "L'analyse a échoué."
        }
    } catch (e) {
        console.error("Analysis error:", e)
        errorMsg.value = "Erreur de connexion pour l'analyse."
    } finally {
        isAnalyzing.value = false
    }
}

onUnmounted(() => {
    stopInterview()
})
</script>

<template>
  <div class="fixed inset-0 z-[60] bg-surface-950 overflow-y-auto custom-scrollbar flex flex-col">
    <!-- CONFIGURATION WIZARD -->
    <div v-if="!isInterviewStarted" class="p-6 md:p-10 max-w-4xl mx-auto animate-fade-in-up space-y-8 flex flex-col w-full">
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

    <!-- IMMERSIVE VIDEO CALL UI — Design réaliste type visio pro -->
    <div v-else class="fixed inset-0 bg-[#0c0c0e] flex flex-col md:flex-row z-[210] overflow-hidden font-sans interview-room">
      
      <!-- ═══ PANNEAU GAUCHE : Salle d'appel ═══ -->
      <div class="flex-1 flex flex-col min-w-0 relative">
        <!-- Fond ambiant (salle sombre) -->
        <div class="absolute inset-0 z-0 bg-gradient-to-b from-slate-950/95 via-slate-950 to-black">
          <div class="absolute inset-0 interview-room-grain pointer-events-none"></div>
        </div>

        <!-- Header réaliste (barre d'appel) -->
        <header class="relative z-10 flex items-center justify-between px-4 md:px-6 py-3 border-b border-white/[0.08] bg-black/50 backdrop-blur-xl">
          <div class="flex items-center gap-4">
            <button @click="goBackToDashboard" class="p-2.5 rounded-xl bg-white/5 hover:bg-white/10 text-white/90 transition-all hover:scale-105 active:scale-95">
              <ArrowLeftIcon class="w-5 h-5" />
            </button>
            <div class="flex items-center gap-3">
              <div class="w-9 h-9 rounded-xl overflow-hidden border border-white/10 bg-surface-900 flex-shrink-0">
                <img :src="currentRecruiter?.img" class="w-full h-full object-cover" alt="" />
              </div>
              <div>
                <h1 class="text-sm md:text-base font-bold text-white truncate max-w-[180px] md:max-w-sm">
                  {{ config.company }} · {{ config.jobTitle }}
                </h1>
                <div class="flex items-center gap-2 mt-0.5">
                  <span class="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-md bg-emerald-500/15 border border-emerald-500/25 text-emerald-400 text-[10px] font-bold uppercase tracking-wider">
                    <span class="relative flex h-1.5 w-1.5">
                      <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                      <span class="relative inline-flex rounded-full h-1.5 w-1.5 bg-emerald-500"></span>
                    </span>
                    En direct
                  </span>
                  <span class="text-slate-500 text-[10px] font-medium tabular-nums">{{ callElapsed }}</span>
                </div>
              </div>
            </div>
          </div>
          <div class="flex items-center gap-2">
            <span class="hidden sm:flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-white/5 border border-white/10 text-[10px] text-slate-400">
              <span class="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
              Connexion stable
            </span>
            <div class="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-white/5 border border-white/10">
              <img :src="currentRecruiter?.img" class="w-6 h-6 rounded-full object-cover border border-white/20" alt="" />
              <span class="text-xs font-semibold text-white hidden sm:inline">{{ currentRecruiter?.name }}</span>
            </div>
          </div>
        </header>

        <!-- Zone vidéo principale : cadre type écran / webcam -->
        <div class="relative z-10 flex-1 flex min-h-0 p-4 md:p-6">
          <div class="interview-video-frame flex-1 flex rounded-2xl overflow-hidden relative bg-black shadow-2xl shadow-black/60 border border-white/[0.06]">
            <!-- Vignette écran (bords assombris) -->
            <div class="absolute inset-0 interview-vignette pointer-events-none z-[1]"></div>
            <!-- Légère texture écran -->
            <div class="absolute inset-0 interview-scan pointer-events-none z-[2] opacity-[0.03]"></div>
            
            <!-- Flux principal : recruteur (vue "caméra") -->
            <div class="absolute inset-0 flex items-center justify-center p-2 md:p-6">
              <div class="relative w-full h-full flex items-center justify-center">
                <img 
                  :src="currentRecruiter?.img" 
                  class="max-h-full w-auto object-contain rounded-lg transition-all duration-700 interview-speaker-img"
                  :class="isAIThinking ? 'interview-thinking' : (isSpeaking ? 'interview-speaking' : '')"
                />
                <!-- Halo quand le recruteur parle -->
                <div v-if="isSpeaking" class="absolute inset-0 flex items-center justify-center pointer-events-none">
                  <div class="w-[70%] h-[70%] rounded-full bg-emerald-500/10 blur-3xl animate-pulse"></div>
                </div>
              </div>
            </div>

            <!-- Badge participant principal (recruteur) -->
            <div class="absolute bottom-4 left-4 z-10 flex items-center gap-3 px-4 py-2.5 rounded-xl bg-black/60 backdrop-blur-md border border-white/10 shadow-xl">
              <div class="relative">
                <img :src="currentRecruiter?.img" class="w-10 h-10 rounded-full object-cover border-2 border-white/20" alt="" />
                <span v-if="isSpeaking" class="absolute -bottom-0.5 -right-0.5 w-3 h-3 rounded-full bg-emerald-500 border-2 border-black"></span>
              </div>
              <div>
                <span class="text-sm font-bold text-white block">{{ currentRecruiter?.name }}</span>
                <span class="text-[10px] text-slate-400">{{ currentRecruiter?.role }}</span>
              </div>
            </div>

            <!-- Grille participants (vignettes type visio) -->
            <div class="absolute top-4 right-4 z-10 flex flex-col gap-3">
              <div class="interview-tile w-20 h-20 md:w-24 md:h-24 rounded-xl overflow-hidden border-2 border-white/15 bg-black/40 shadow-xl relative"
                   :class="isSpeaking ? 'interview-tile-speaking' : ''">
                <img :src="currentRecruiter?.img" class="w-full h-full object-cover" alt="" />
                <div class="absolute bottom-0 left-0 right-0 py-1 bg-gradient-to-t from-black/80 to-transparent text-center">
                  <span class="text-[9px] font-bold text-white drop-shadow-lg">Recruteur</span>
                </div>
              </div>
              <div class="interview-tile w-20 h-20 md:w-24 md:h-24 rounded-xl overflow-hidden border-2 shadow-xl relative transition-all duration-300"
                   :class="isListening ? 'border-rose-500 interview-tile-you-speaking shadow-rose-500/20' : 'border-white/15 bg-black/40'">
                <video ref="userVideo" autoplay playsinline muted class="w-full h-full object-cover bg-surface-900"></video>
                <div v-if="!stream" class="absolute inset-0 flex items-center justify-center bg-slate-900/95">
                  <div class="text-center">
                    <VideoCameraSlashIcon class="w-8 h-8 text-slate-600 mx-auto mb-1" />
                    <span class="text-[9px] text-slate-500 font-medium">Caméra off</span>
                  </div>
                </div>
                <div class="absolute bottom-0 left-0 right-0 py-1.5 bg-gradient-to-t from-black/80 to-transparent text-center">
                  <span class="text-[9px] font-bold text-white drop-shadow-lg">Vous</span>
                </div>
                <div v-if="isListening" class="absolute top-1.5 right-1.5 flex gap-0.5">
                  <span class="w-1 h-3 bg-rose-400 rounded-full animate-waveform" style="animation-delay: 0ms"></span>
                  <span class="w-1 h-2 bg-rose-400 rounded-full animate-waveform" style="animation-delay: 150ms"></span>
                  <span class="w-1 h-4 bg-rose-400 rounded-full animate-waveform" style="animation-delay: 300ms"></span>
                  <span class="w-1 h-2 bg-rose-400 rounded-full animate-waveform" style="animation-delay: 450ms"></span>
                  <span class="w-1 h-3 bg-rose-400 rounded-full animate-waveform" style="animation-delay: 600ms"></span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Bandeau parole live (réaliste) -->
        <div class="relative z-10 mx-4 mb-3 p-3.5 rounded-xl bg-black/50 backdrop-blur-xl border border-white/[0.06] flex items-center gap-4 shadow-lg">
          <div class="flex-shrink-0 flex items-center gap-1 h-8">
            <template v-if="isSpeaking">
              <span class="w-1 h-4 bg-emerald-400 rounded-full animate-waveform" style="animation-delay: 0ms"></span>
              <span class="w-1 h-6 bg-emerald-400 rounded-full animate-waveform" style="animation-delay: 100ms"></span>
              <span class="w-1 h-3 bg-emerald-400 rounded-full animate-waveform" style="animation-delay: 200ms"></span>
              <span class="w-1 h-5 bg-emerald-400 rounded-full animate-waveform" style="animation-delay: 300ms"></span>
              <span class="w-1 h-4 bg-emerald-400 rounded-full animate-waveform" style="animation-delay: 400ms"></span>
            </template>
            <template v-else-if="isListening">
              <span class="w-1 h-4 bg-rose-400 rounded-full animate-waveform" style="animation-delay: 0ms"></span>
              <span class="w-1 h-6 bg-rose-400 rounded-full animate-waveform" style="animation-delay: 120ms"></span>
              <span class="w-1 h-3 bg-rose-400 rounded-full animate-waveform" style="animation-delay: 240ms"></span>
              <span class="w-1 h-5 bg-rose-400 rounded-full animate-waveform" style="animation-delay: 360ms"></span>
              <span class="w-1 h-4 bg-rose-400 rounded-full animate-waveform" style="animation-delay: 480ms"></span>
            </template>
            <template v-else>
              <SpeakerWaveIcon class="w-5 h-5 text-slate-500" />
            </template>
          </div>
          <p class="text-sm text-slate-300 flex-1 min-w-0 truncate">
            <template v-if="isAIThinking"><span class="text-indigo-400">Le recruteur prépare sa question...</span></template>
            <template v-else-if="isSpeaking && conversation.length">{{ conversation[conversation.length - 1]?.content || 'Parole en cours...' }}</template>
            <template v-else-if="transcript"><span class="text-rose-200/90">{{ transcript }}...</span></template>
            <template v-else><span class="text-slate-500">En attente — activez le micro pour répondre.</span></template>
          </p>
        </div>

        <!-- Barre de contrôles (style pro) -->
        <div class="relative z-20 px-4 pb-6 flex items-center justify-center">
          <div class="inline-flex items-center gap-1 p-2 rounded-[2rem] bg-black/70 backdrop-blur-xl border border-white/10 shadow-[0_20px_60px_rgba(0,0,0,0.5)]">
            <button @click="showChat = !showChat" 
              :class="showChat ? 'bg-indigo-500 text-white shadow-lg shadow-indigo-500/30' : 'bg-white/5 text-slate-400 hover:text-white hover:bg-white/10'"
              class="p-3.5 rounded-full transition-all duration-200" title="Transcription">
              <ChatBubbleLeftRightIcon class="w-5 h-5" />
            </button>
            <button @click="testAudio" class="p-3.5 rounded-full bg-white/5 text-slate-400 hover:text-indigo-400 hover:bg-white/10 transition-all" title="Tester le son">
              <SpeakerWaveIcon class="w-5 h-5" />
            </button>
            <button @click="triggerListen" 
              :class="isListening ? 'bg-rose-500 text-white scale-110 shadow-lg shadow-rose-500/40' : (isAIThinking ? 'bg-indigo-500 text-white scale-105' : 'bg-white/10 text-white hover:bg-white/20')"
              class="p-5 rounded-full transition-all duration-200 mx-1 interview-mic-btn" title="Micro">
              <MicrophoneIcon v-if="!isListening && !isAIThinking" class="w-6 h-6" />
              <StopIcon v-else-if="isListening" class="w-6 h-6" />
              <span v-else class="flex gap-1">
                <span class="w-2 h-2 bg-white rounded-full animate-bounce" style="animation-delay: 0ms"></span>
                <span class="w-2 h-2 bg-white rounded-full animate-bounce" style="animation-delay: 100ms"></span>
                <span class="w-2 h-2 bg-white rounded-full animate-bounce" style="animation-delay: 200ms"></span>
              </span>
            </button>
            <button @click="finishInterview" class="p-3.5 rounded-full bg-rose-500 hover:bg-rose-400 text-white transition-all hover:scale-105 active:scale-95 shadow-lg shadow-rose-900/30" title="Terminer l'entretien">
              <PhoneIcon class="w-5 h-5 rotate-[135deg]" />
            </button>
          </div>
        </div>
        <p v-if="isListening" class="text-center text-rose-400 text-[10px] font-bold uppercase tracking-[0.2em] pb-3 animate-pulse">Micro actif — parlez maintenant</p>
      </div>

      <!-- ═══ PANNEAU DROIT : Transcription (style chat pro) ═══ -->
      <div v-show="showChat" class="w-full md:w-[380px] lg:w-[420px] shrink-0 flex flex-col bg-[#111113] border-l border-white/[0.06] shadow-2xl">
        <div class="p-4 border-b border-white/[0.06] flex items-center justify-between bg-black/30">
          <div class="flex items-center gap-2">
            <div class="w-8 h-8 rounded-lg bg-indigo-500/20 flex items-center justify-center">
              <DocumentTextIcon class="w-4 h-4 text-indigo-400" />
            </div>
            <h2 class="text-sm font-bold text-white">Transcription en direct</h2>
          </div>
          <button @click="showChat = false" class="md:hidden p-2 rounded-lg hover:bg-white/10 text-slate-400 transition-colors">
            <XMarkIcon class="w-5 h-5" />
          </button>
        </div>
        <div class="flex-1 overflow-y-auto p-4 space-y-4 scroll-smooth custom-scrollbar" ref="chatContainer">
          <div v-for="msg in conversation" :key="msg.id" :class="msg.role === 'user' ? 'flex justify-end' : 'flex justify-start'">
            <div :class="msg.role === 'user' 
              ? 'max-w-[85%] rounded-2xl rounded-br-md px-4 py-3 bg-indigo-500/95 text-white shadow-lg border border-indigo-400/20' 
              : 'max-w-[85%] rounded-2xl rounded-bl-md px-4 py-3 bg-white/[0.07] text-slate-200 border border-white/[0.08]'">
              <p class="text-[10px] font-bold opacity-90 mb-1.5 flex items-center gap-1.5">
                <span v-if="msg.role !== 'user'" class="w-4 h-4 rounded-full overflow-hidden border border-white/20">
                  <img :src="currentRecruiter?.img" class="w-full h-full object-cover" alt="" />
                </span>
                {{ msg.role === 'user' ? 'Vous' : currentRecruiter?.name }}
              </p>
              <p class="text-sm leading-relaxed whitespace-pre-wrap">{{ msg.content }}</p>
            </div>
          </div>
          <div v-if="isAIThinking" class="flex justify-start">
            <div class="rounded-2xl rounded-bl-md px-4 py-3 bg-indigo-500/15 border border-indigo-500/25 text-slate-300 text-sm flex items-center gap-3">
              <span class="flex gap-1">
                <span class="w-2 h-2 bg-indigo-400 rounded-full animate-bounce" style="animation-delay: 0ms"></span>
                <span class="w-2 h-2 bg-indigo-400 rounded-full animate-bounce" style="animation-delay: 150ms"></span>
                <span class="w-2 h-2 bg-indigo-400 rounded-full animate-bounce" style="animation-delay: 300ms"></span>
              </span>
              Le recruteur rédige sa réponse...
            </div>
          </div>
          <div v-if="transcript && !isAIThinking" class="flex justify-end">
            <div class="max-w-[85%] rounded-2xl rounded-br-md px-4 py-2.5 bg-rose-500/20 border border-rose-500/30 text-rose-200 text-sm italic">
              {{ transcript }}...
            </div>
          </div>
        </div>
      </div>

      <!-- Note analyste (overlay discret) -->
      <transition enter-active-class="transition duration-300 ease-out" leave-active-class="transition duration-200 ease-in" enter-from-class="opacity-0 translate-y-2" leave-to-class="opacity-0 translate-y-2">
        <div v-if="analystNote" class="absolute left-4 bottom-28 z-30 max-w-xs md:left-6">
          <div class="bg-black/80 backdrop-blur-xl border border-amber-500/20 p-4 rounded-2xl shadow-2xl">
            <div class="flex items-center gap-2 mb-2">
              <SparklesIcon class="w-4 h-4 text-amber-400" />
              <span class="text-[10px] font-bold text-amber-400/80 uppercase">Conseil live</span>
            </div>
            <p class="text-sm text-white leading-relaxed">{{ analystNote.tip }}</p>
            <span class="text-[10px] text-indigo-400 font-medium">{{ analystNote.sentiment }}</span>
          </div>
        </div>
      </transition>

      <!-- SCORECARD MODAL -->
      <div v-if="showScorecard" class="fixed inset-0 z-[100] flex items-center justify-center p-4">
          <div class="absolute inset-0 bg-black/80 backdrop-blur-md" @click="!isAnalyzing ? stopInterview() : null"></div>
          
          <div class="bg-surface-900 border border-white/10 w-full max-w-4xl rounded-[2.5rem] overflow-hidden shadow-2xl relative z-10 animate-scale-in">
              <!-- Header -->
              <div class="p-8 border-b border-white/5 bg-gradient-to-r from-indigo-500/10 to-purple-500/10 flex items-center justify-between">
                  <div class="flex items-center gap-4">
                      <div class="w-12 h-12 rounded-2xl bg-indigo-500 flex items-center justify-center shadow-lg shadow-indigo-500/20">
                          <ChartBarIcon class="w-6 h-6 text-white" />
                      </div>
                      <div>
                          <h2 class="text-2xl font-display font-bold text-white tracking-tight">Récapitulatif de votre entretien</h2>
                          <p class="text-sm text-slate-400">Analyse générée par l'IA GoldArmy</p>
                      </div>
                  </div>
                  <button v-if="!isAnalyzing" @click="stopInterview" class="p-2 text-slate-500 hover:text-white transition-colors">
                      <XMarkIcon class="w-6 h-6" />
                  </button>
              </div>

              <!-- Content -->
              <div class="p-8 max-h-[70vh] overflow-y-auto custom-scrollbar">
                  <!-- Loading State -->
                  <div v-if="isAnalyzing" class="flex flex-col items-center justify-center py-20 gap-6">
                      <div class="relative w-20 h-20">
                          <div class="absolute inset-0 border-4 border-indigo-500/20 rounded-full"></div>
                          <div class="absolute inset-0 border-4 border-white border-t-transparent rounded-full animate-spin"></div>
                      </div>
                      <p class="text-lg font-bold text-white animate-pulse">Analyse de vos réponses en cours...</p>
                      <p class="text-sm text-slate-400 max-w-xs text-center">Le Mentor IA examine votre communication et votre expertise technique.</p>
                  </div>

                  <!-- Results State -->
                  <div v-else-if="scorecard" class="space-y-10">
                      <!-- Hero Score -->
                      <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
                          <div v-for="(val, cat) in scorecard.scores" :key="cat" class="bg-white/5 border border-white/10 p-6 rounded-3xl flex flex-col items-center gap-3">
                              <span class="text-[10px] uppercase font-black tracking-widest text-slate-500">{{ cat === 'technical' ? 'Technique' : cat === 'communication' ? 'Élocution' : cat === 'soft_skills' ? 'Attitude' : 'Global' }}</span>
                              <div class="relative flex items-center justify-center">
                                  <svg class="w-20 h-20">
                                      <circle class="text-white/5" stroke-width="6" stroke="currentColor" fill="transparent" r="34" cx="40" cy="40"/>
                                      <circle :class="val >= 7 ? 'text-emerald-500' : val >= 5 ? 'text-amber-500' : 'text-rose-500'" stroke-width="6" :stroke-dasharray="213" :stroke-dashoffset="213 - (213 * val / 10)" stroke-linecap="round" stroke="currentColor" fill="transparent" r="34" cx="40" cy="40"/>
                                  </svg>
                                  <span class="absolute text-xl font-black text-white">{{ val }}/10</span>
                              </div>
                          </div>
                      </div>

                      <div class="grid grid-cols-1 md:grid-cols-2 gap-10">
                          <!-- Points Forts -->
                          <div class="space-y-4">
                              <h3 class="text-sm font-black uppercase tracking-widest text-emerald-400 flex items-center gap-2">
                                  <CheckCircleIcon class="w-5 h-5" />
                                  Points Forts
                              </h3>
                              <ul class="space-y-3">
                                  <li v-for="p in scorecard.feedback.points_forts" :key="p" class="flex gap-3 text-sm text-slate-300">
                                      <span class="text-emerald-500 shrink-0">●</span>
                                      {{ p }}
                                  </li>
                              </ul>
                          </div>

                          <!-- Points à améliorer -->
                          <div class="space-y-4">
                              <h3 class="text-sm font-black uppercase tracking-widest text-amber-400 flex items-center gap-2">
                                  <AcademicCapIcon class="w-5 h-5" />
                                  Axe d'amélioration
                              </h3>
                              <ul class="space-y-3">
                                  <li v-for="p in scorecard.feedback.points_amelioration" :key="p" class="flex gap-3 text-sm text-slate-300">
                                      <span class="text-amber-500 shrink-0">●</span>
                                      {{ p }}
                                  </li>
                              </ul>
                          </div>
                      </div>

                      <!-- Final Advice Card -->
                      <div class="bg-indigo-600/10 border border-indigo-500/30 p-8 rounded-[2rem] space-y-4 relative overflow-hidden group">
                          <div class="absolute top-0 right-0 p-4 opacity-10 group-hover:rotate-12 transition-transform">
                              <SparklesIcon class="w-24 h-24 text-indigo-400" />
                          </div>
                          <div class="flex items-center gap-3">
                              <StarIcon class="w-6 h-6 text-indigo-400" />
                              <h3 class="text-lg font-bold text-white">L'avis du Recruteur</h3>
                          </div>
                          <p class="text-slate-300 text-sm leading-relaxed relative z-10">{{ scorecard.feedback.conseils }}</p>
                          <div class="pt-4 flex items-center justify-between border-t border-white/5">
                              <span class="text-xs font-bold text-slate-500 uppercase tracking-widest">Décision finale :</span>
                              <span :class="scorecard.decision.includes('Favorable') ? 'text-emerald-400' : 'text-amber-400'" class="px-4 py-1.5 rounded-full bg-white/5 border border-white/10 font-black text-xs">
                                  {{ scorecard.decision }}
                              </span>
                          </div>
                      </div>
                  </div>
              </div>

              <!-- Footer -->
              <div class="p-8 bg-black/20 flex justify-end gap-4">
                  <button @click="stopInterview" class="px-8 py-4 bg-gradient-to-r from-indigo-500 to-purple-600 hover:scale-105 active:scale-95 text-white font-black rounded-2xl transition-all shadow-xl shadow-indigo-500/20">
                      Retour au Dashboard
                  </button>
              </div>
          </div>
      </div>

      <!-- Live status text -->
      <div v-if="isListening" class="absolute bottom-32 left-1/2 -translate-x-1/2 text-pink-400 font-black uppercase tracking-[0.3em] text-xs animate-pulse z-10 drop-shadow-lg">
          Microphone Actif — Parlez Maintenant
      </div>
   </div>
  </div>
</template>

<style scoped>
.noise-overlay {
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='1'/%3E%3C/svg%3E");
  background-size: 200px 200px;
}

/* Salle d'appel : grain léger */
.interview-room-grain {
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='g'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23g)' opacity='0.04'/%3E%3C/svg%3E");
  background-size: 128px 128px;
}

/* Cadre vidéo : vignette (bords sombres) */
.interview-vignette {
  background: radial-gradient(ellipse 80% 80% at 50% 50%, transparent 40%, rgba(0,0,0,0.4) 100%);
}

/* Très légère ligne de scan (effet écran) */
.interview-scan {
  background: repeating-linear-gradient(
    0deg,
    transparent,
    transparent 2px,
    rgba(0,0,0,0.03) 2px,
    rgba(0,0,0,0.03) 4px
  );
}

/* Flux principal : léger zoom quand le recruteur parle */
.interview-speaker-img.interview-speaking {
  transform: scale(1.02);
  filter: brightness(1.05);
}
.interview-speaker-img.interview-thinking {
  filter: blur(2px) brightness(0.9);
}

/* Tuiles participants : bordure "live" quand on parle */
.interview-tile-speaking {
  box-shadow: 0 0 0 2px rgba(34, 197, 94, 0.5);
}
.interview-tile-you-speaking {
  box-shadow: 0 0 0 2px rgba(244, 63, 94, 0.6), 0 0 20px rgba(244, 63, 94, 0.15);
}

/* Barres son animées */
@keyframes waveform {
  0%, 100% { transform: scaleY(0.5); }
  50% { transform: scaleY(1); }
}
.animate-waveform {
  animation: waveform 0.6s ease-in-out infinite;
}
</style>
