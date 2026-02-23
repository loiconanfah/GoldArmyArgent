<script setup>
import { authFetch } from '../utils/auth'

import { ref, onMounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { PaperAirplaneIcon, ArrowPathIcon, DocumentTextIcon, CheckIcon, XMarkIcon, ArrowUpTrayIcon } from '@heroicons/vue/24/solid'

const route = useRoute()
const inputQuery = ref('')
const inputLocation = ref('')
const cvText = ref('')
const cvFilename = ref('')
const isUploadingCv = ref(false)
const isUploading = ref(false)
const isLoading = ref(false)
// Session unique par onglet pour que le backend maintienne l'historique
const sessionId = ref((typeof crypto !== 'undefined' && crypto.randomUUID) ? crypto.randomUUID() : `session_${Date.now()}`)
const messages = ref([
  {
    id: 1,
    role: 'assistant',
    content: "Bonjour ! Je suis GoldArmy, ton Co-Pilote de Carrière. 🪖\n\nJe suis connecté et prêt. Uploade ton CV en PDF pour que je l'audite, génère ton portfolio, ou pose-moi n'importe quelle question.",
    timestamp: new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})
  }
])

const chatContainer = ref(null)

const scrollToBottom = async () => {
    await nextTick()
    if (chatContainer.value) {
        chatContainer.value.scrollTop = chatContainer.value.scrollHeight
    }
}

onMounted(() => {
  if (route.query.prompt) {
    inputQuery.value = route.query.prompt
    sendMessage()
  }
})

const sendMessage = async () => {
  if (!inputQuery.value.trim() && !cvText.value.trim()) return
  
  const userMsg = inputQuery.value
  inputQuery.value = ''
  
  if (userMsg) {
      messages.value.push({
        id: Date.now(),
        role: 'user',
        content: userMsg,
        timestamp: new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})
      })
  }

  if (cvText.value && cvFilename.value) {
       messages.value.push({
          id: Date.now() + 1,
          role: 'user',
          content: `[CV chargé : ${cvFilename.value}]`,
          timestamp: new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})
      })
  }
  
  scrollToBottom()
  isLoading.value = true
  
  try {
    const res = await authFetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
            message: userMsg, 
            cv_text: cvText.value, 
            cv_filename: cvFilename.value, 
            nb_results: 5, 
            location: inputLocation.value,
            session_id: sessionId.value 
        })
    })
    const data = await res.json()
    
    messages.value.push({
      id: Date.now() + 2,
      role: 'assistant',
      type: (data.data && data.data.type) || 'chat',
      is_html: data.data && data.data.type === 'portfolio_html',
      is_cv_rewrite: data.data && data.data.type === 'cv_rewrite',
      is_audit_rewrite: data.data && data.data.type === 'cv_audit_rewrite',
      audit: (data.data && data.data.audit) || '',
      content: (data.data && data.data.content) || 'Réponse vide du serveur.',
      timestamp: new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})
    })
    
  } catch (e) {
    messages.value.push({
      id: Date.now() + 2,
      role: 'assistant',
      content: "⚠️ Erreur de connexion avec le quartier général (Backend indisponible).",
      timestamp: new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}),
      error: true
    })
  } finally {
    isLoading.value = false
    scrollToBottom()
  }
}

const uploadCvPdf = async (event) => {
    const file = event.target.files[0]
    if (!file) return
    if (!file.name.toLowerCase().endsWith('.pdf')) {
        alert('Veuillez sélectionner un fichier PDF.')
        return
    }
    isUploadingCv.value = true
    cvFilename.value = ''
    cvText.value = ''
    try {
        const formData = new FormData()
        formData.append('file', file)
        const token = localStorage.getItem('token')
        const res = await fetch('http://localhost:8000/api/parse-pdf', {
            method: 'POST',
            headers: token ? { Authorization: `Bearer ${token}` } : {},
            body: formData
        })
        const data = await res.json()
        if (data.status === 'success' && data.text) {
            cvText.value = data.text
            cvFilename.value = file.name
        } else {
            alert(data.detail || 'Erreur lors de la lecture du PDF.')
        }
    } catch (e) {
        alert('Impossible de contacter le serveur pour lire le PDF.')
    } finally {
        isUploadingCv.value = false
    }
}

const removeCv = () => {
    cvText.value = ''
    cvFilename.value = ''
}

const downloadHtml = (htmlContent) => {
    const blob = new Blob([htmlContent], { type: 'text/html' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'portfolio.html'
    a.click()
    URL.revokeObjectURL(url)
}

const isDownloadingDocx = ref(false)
const downloadCvDocx = async (cvJsonString) => {
    isDownloadingDocx.value = true
    try {
        // Extraire le nom pour le nom de fichier
        let filename = 'CV_ATS_Optimise'
        try {
            const parsed = JSON.parse(cvJsonString)
            if (parsed.full_name) {
                filename = `CV_${parsed.full_name.replace(/\s+/g, '_')}_ATS`
            }
        } catch {}

        const token = localStorage.getItem('token')
        const res = await fetch('http://localhost:8000/api/generate-cv-pdf', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                ...(token ? { Authorization: `Bearer ${token}` } : {})
            },
            body: JSON.stringify({ cv_json: cvJsonString, filename })
        })

        if (!res.ok) {
            const err = await res.json()
            alert(`Erreur: ${err.detail || 'Impossible de générer le DOCX'}`)
            return
        }

        const blob = await res.blob()
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = filename + '.pdf'
        a.click()
        URL.revokeObjectURL(url)
    } catch (e) {
        alert('Erreur lors du téléchargement du CV.')
    } finally {
        isDownloadingDocx.value = false
    }
}
</script>

<template>
  <div class="h-full flex flex-col p-4 md:p-8 max-w-4xl mx-auto w-full relative animate-fade-in-up">
    <!-- Header Minimal -->
    <div class="flex items-center justify-between mb-8">
      <div>
        <h2 class="text-2xl font-display font-black text-white tracking-tight">Agent GoldArmy</h2>
        <p class="text-slate-400 mt-1 text-sm font-medium">Orchestration, Analyse CV &amp; Génération Web</p>
      </div>
      
      <!-- Context Toggle Button -->
      <button 
        @click="isUploading = !isUploading" 
        :class="cvFilename ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30' : 'bg-surface-800 text-slate-300 hover:text-white border-surface-700 hover:border-surface-600'" 
        class="px-4 py-2 rounded-xl border flex items-center gap-2 transition-all shadow-sm text-sm font-bold"
      >
          <DocumentTextIcon class="w-4 h-4" />
          <span class="hidden sm:inline">{{ cvFilename ? cvFilename : 'Ajouter CV (PDF)' }}</span>
          <CheckIcon v-if="cvFilename" class="w-4 h-4 ml-1" />
      </button>
    </div>
    
    <!-- Context Panel (PDF Upload) -->
    <transition
        enter-active-class="transition duration-300 ease-out origin-top"
        enter-from-class="transform scale-y-95 opacity-0"
        enter-to-class="transform scale-y-100 opacity-100"
        leave-active-class="transition duration-200 ease-in origin-top"
        leave-from-class="transform scale-y-100 opacity-100"
        leave-to-class="transform scale-y-95 opacity-0"
    >
        <div v-if="isUploading" class="mb-6 bg-surface-900 border border-surface-800 p-4 rounded-2xl shadow-sm relative z-10">
            <div class="flex justify-between items-center mb-3">
                <h3 class="text-white font-bold text-sm tracking-wide flex items-center gap-2">
                    <span class="w-2 h-2 rounded-full bg-emerald-400"></span> 
                    CV en Contexte
                </h3>
                <button @click="isUploading = false" class="text-slate-500 hover:text-white text-xs font-bold uppercase tracking-wider">Fermer</button>
            </div>

            <!-- Uploaded state -->
            <div v-if="cvFilename" class="flex items-center gap-3 p-3 bg-emerald-500/10 border border-emerald-500/30 rounded-xl">
                <DocumentTextIcon class="w-5 h-5 text-emerald-400 shrink-0" />
                <span class="flex-1 text-emerald-300 text-sm font-semibold truncate">{{ cvFilename }}</span>
                <button @click="removeCv" class="p-1 text-slate-400 hover:text-rose-400 transition-colors rounded-lg hover:bg-rose-500/10">
                    <XMarkIcon class="w-4 h-4" />
                </button>
            </div>

            <!-- Upload drop zone -->
            <label v-else class="flex flex-col items-center justify-center gap-3 h-28 border-2 border-dashed border-surface-600 hover:border-emerald-500/60 rounded-xl cursor-pointer transition-all bg-surface-950/50 hover:bg-emerald-500/5 group">
                <input type="file" accept=".pdf" class="hidden" @change="uploadCvPdf" />
                <ArrowUpTrayIcon v-if="!isUploadingCv" class="w-7 h-7 text-slate-500 group-hover:text-emerald-400 transition-colors" />
                <ArrowPathIcon v-else class="w-7 h-7 text-emerald-400 animate-spin" />
                <span class="text-sm font-semibold" :class="isUploadingCv ? 'text-emerald-400' : 'text-slate-400 group-hover:text-slate-200'">
                    {{ isUploadingCv ? 'Extraction du texte...' : 'Cliquer pour uploader votre CV (PDF)' }}
                </span>
            </label>
        </div>
    </transition>

    <!-- Chat History Area -->
    <div ref="chatContainer" class="flex-1 overflow-y-auto space-y-8 pr-2 pb-32 scroll-smooth">
      <div 
        v-for="msg in messages" 
        :key="msg.id"
        :class="['flex w-full', msg.role === 'user' ? 'justify-end' : 'justify-start']"
      >
        <!-- User Bubble -->
        <div v-if="msg.role === 'user'" class="max-w-[85%] md:max-w-[70%] bg-surface-800 text-white rounded-2xl p-5 shadow-sm border border-surface-700 font-medium">
             <div class="whitespace-pre-wrap leading-relaxed">{{ msg.content }}</div>
             <span class="block text-[10px] mt-2 opacity-40 text-right font-bold">{{ msg.timestamp }}</span>
        </div>
        
        <!-- Assistant Output Rendering -->
        <div v-if="msg.role === 'assistant'" class="flex gap-4 max-w-[95%] md:max-w-[85%]">
          <!-- Avatar -->
          <div class="shrink-0 w-8 h-8 rounded-lg bg-gradient-to-br from-gold-400 to-amber-600 flex items-center justify-center shadow-lg shadow-gold-500/20 text-sm mt-1">
             🪖
          </div>
          
          <div class="flex-1 min-w-0 prose prose-invert prose-p:leading-relaxed prose-a:text-gold-400 hover:prose-a:text-gold-300 prose-strong:text-white prose-headings:text-white prose-pre:bg-surface-900 prose-pre:border prose-pre:border-surface-700 prose-pre:shadow-inner w-full">
            
            <div v-if="msg.error" class="bg-rose-500/10 border border-rose-500/30 text-rose-200 p-4 rounded-2xl w-full">
                {{ msg.content }}
            </div>

            <!-- ══════════ AUDIT + ATS DASHBOARD ══════════ -->
            <div v-else-if="msg.is_audit_rewrite && msg.audit && typeof msg.audit === 'object'" class="w-full space-y-4">

              <!-- Header candidat -->
              <div class="flex items-center gap-3 p-4 bg-surface-800/60 border border-surface-700 rounded-2xl">
                <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-lg">🎯</div>
                <div>
                  <p class="font-bold text-white text-sm m-0">{{ msg.audit.candidate_name || 'Candidat' }}</p>
                  <p class="text-slate-400 text-xs m-0">{{ msg.audit.candidate_title || 'Profil Professionnel' }}</p>
                </div>
                <div class="ml-auto text-right">
                  <p class="text-[10px] text-slate-500 uppercase tracking-wide">Rapport ATS</p>
                </div>
              </div>

              <!-- Score ATS principal + barres de catégories -->
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">

                <!-- Score circulaire -->
                <div class="p-5 bg-surface-800/60 border border-surface-700 rounded-2xl flex flex-col items-center justify-center gap-3">
                  <p class="text-xs font-bold text-slate-400 uppercase tracking-widest">Score ATS Global</p>
                  <div class="relative w-32 h-32">
                    <svg class="w-full h-full -rotate-90" viewBox="0 0 120 120">
                      <circle cx="60" cy="60" r="52" fill="none" stroke="rgb(30,41,59)" stroke-width="12"/>
                      <circle cx="60" cy="60" r="52" fill="none"
                        :stroke="msg.audit.ats_score >= 75 ? '#22c55e' : msg.audit.ats_score >= 50 ? '#f59e0b' : '#ef4444'"
                        stroke-width="12"
                        stroke-linecap="round"
                        :stroke-dasharray="`${(msg.audit.ats_score || 0) * 3.267} 326.7`"
                        style="transition: stroke-dasharray 1.2s ease"
                      />
                    </svg>
                    <div class="absolute inset-0 flex flex-col items-center justify-center">
                      <span class="text-3xl font-black"
                        :class="msg.audit.ats_score >= 75 ? 'text-green-400' : msg.audit.ats_score >= 50 ? 'text-amber-400' : 'text-red-400'"
                      >{{ msg.audit.ats_score || 0 }}</span>
                      <span class="text-slate-500 text-xs font-bold">/100</span>
                    </div>
                  </div>
                  <p class="text-xs text-center font-semibold m-0"
                    :class="msg.audit.ats_score >= 75 ? 'text-green-400' : msg.audit.ats_score >= 50 ? 'text-amber-400' : 'text-red-400'"
                  >
                    {{ msg.audit.ats_score >= 75 ? '✅ Bon profil ATS' : msg.audit.ats_score >= 50 ? '⚠️ Profil à améliorer' : '❌ Risque de rejet ATS' }}
                  </p>
                </div>

                <!-- Barres de scores par catégorie -->
                <div class="p-5 bg-surface-800/60 border border-surface-700 rounded-2xl space-y-3">
                  <p class="text-xs font-bold text-slate-400 uppercase tracking-widest mb-4">Détail par catégorie</p>
                  <template v-if="msg.audit.scores">
                    <div v-for="(val, key) in {
                      'Mots-clés': msg.audit.scores.mots_cles,
                      'Impact & Résultats': msg.audit.scores.impact_resultats,
                      'Mise en forme': msg.audit.scores.mise_en_forme,
                      'Lisibilité': msg.audit.scores.lisibilite,
                      'Pertinence Exp.': msg.audit.scores.experience_pertinence
                    }" :key="key" class="space-y-1">
                      <div class="flex justify-between text-[11px]">
                        <span class="text-slate-300 font-medium">{{ key }}</span>
                        <span :class="val >= 70 ? 'text-green-400' : val >= 45 ? 'text-amber-400' : 'text-red-400'" class="font-bold">{{ val }}/100</span>
                      </div>
                      <div class="h-1.5 bg-surface-700 rounded-full overflow-hidden">
                        <div class="h-full rounded-full transition-all duration-1000"
                          :class="val >= 70 ? 'bg-green-500' : val >= 45 ? 'bg-amber-500' : 'bg-red-500'"
                          :style="`width: ${val}%`"
                        ></div>
                      </div>
                    </div>
                  </template>
                </div>
              </div>

              <!-- Failles + Actions côte à côte -->
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <!-- Failles critiques -->
                <div class="p-4 bg-red-500/5 border border-red-500/20 rounded-2xl">
                  <p class="text-xs font-bold text-red-400 uppercase tracking-widest mb-3">❌ Failles Critiques</p>
                  <ul class="space-y-2">
                    <li v-for="(faille, i) in (msg.audit.failles || [])" :key="i"
                      class="flex gap-2 text-xs text-slate-300 leading-snug"
                    >
                      <span class="text-red-400 shrink-0 font-bold mt-0.5">{{ i + 1 }}.</span>
                      <span>{{ faille }}</span>
                    </li>
                  </ul>
                </div>

                <!-- Actions prioritaires -->
                <div class="p-4 bg-green-500/5 border border-green-500/20 rounded-2xl">
                  <p class="text-xs font-bold text-green-400 uppercase tracking-widest mb-3">🛠️ Actions Prioritaires</p>
                  <ul class="space-y-2">
                    <li v-for="(action, i) in (msg.audit.actions || [])" :key="i"
                      class="flex gap-2 text-xs text-slate-300 leading-snug"
                    >
                      <span class="text-green-400 shrink-0 font-bold mt-0.5">{{ i + 1 }}.</span>
                      <span>{{ action }}</span>
                    </li>
                  </ul>
                </div>
              </div>

              <!-- Technologies manquantes + Points forts -->
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <!-- Tech manquantes -->
                <div v-if="msg.audit.tech_manquantes && msg.audit.tech_manquantes.length" class="p-4 bg-amber-500/5 border border-amber-500/20 rounded-2xl">
                  <p class="text-xs font-bold text-amber-400 uppercase tracking-widest mb-3">💡 Technologies Manquantes</p>
                  <div class="flex flex-wrap gap-2">
                    <span v-for="tech in msg.audit.tech_manquantes" :key="tech"
                      class="px-2.5 py-1 bg-amber-500/10 border border-amber-500/20 text-amber-300 text-[11px] font-bold rounded-lg"
                    >{{ tech }}</span>
                  </div>
                </div>

                <!-- Points forts -->
                <div v-if="msg.audit.points_forts && msg.audit.points_forts.length" class="p-4 bg-indigo-500/5 border border-indigo-500/20 rounded-2xl">
                  <p class="text-xs font-bold text-indigo-400 uppercase tracking-widest mb-3">✅ Points Forts</p>
                  <ul class="space-y-1.5">
                    <li v-for="(pt, i) in msg.audit.points_forts" :key="i" class="flex gap-2 text-xs text-slate-300">
                      <span class="text-indigo-400 shrink-0">•</span>
                      <span>{{ pt }}</span>
                    </li>
                  </ul>
                </div>
              </div>

              <!-- Bouton téléchargement -->
              <button
                @click="downloadCvDocx(msg.content)"
                :disabled="isDownloadingDocx"
                class="w-full flex items-center justify-center gap-2 px-5 py-3.5 bg-gradient-to-r from-indigo-500 to-purple-500 hover:from-indigo-400 hover:to-purple-400 disabled:from-surface-700 disabled:to-surface-700 disabled:text-slate-500 text-white rounded-xl font-bold transition-all shadow-lg shadow-indigo-500/20 text-sm"
              >
                <ArrowUpTrayIcon v-if="!isDownloadingDocx" class="w-4 h-4 rotate-180" />
                <ArrowPathIcon v-else class="w-4 h-4 animate-spin" />
                {{ isDownloadingDocx ? 'Génération du fichier...' : '⬇ Télécharger le CV Corrigé (.pdf)' }}
              </button>
              <p class="text-[10px] text-slate-500 text-center">✅ ATS-friendly · Calibri 10pt · Mono-colonne · Mots-clés optimisés</p>
            </div>

            <!-- Fallback audit si format non-structuré (chaîne texte) -->
            <div v-else-if="msg.is_audit_rewrite && msg.audit && typeof msg.audit === 'string'" class="space-y-4 w-full">
              <div class="whitespace-pre-wrap text-slate-300 pb-4 border-b border-surface-700" v-html="msg.audit.replace(/\n/g, '<br/>')"></div>
              <button @click="downloadCvDocx(msg.content)" :disabled="isDownloadingDocx"
                class="w-full flex items-center justify-center gap-2 px-5 py-3 bg-indigo-500 hover:bg-indigo-400 text-white rounded-xl font-bold transition-all">
                <ArrowUpTrayIcon v-if="!isDownloadingDocx" class="w-4 h-4 rotate-180" />
                <ArrowPathIcon v-else class="w-4 h-4 animate-spin" />
                {{ isDownloadingDocx ? 'Génération...' : '⬇ Télécharger CV Corrigé (.pdf)' }}
              </button>
            </div>

            <!-- Standard text/markdown rendering -->
            <div v-else-if="!msg.is_html && !msg.is_cv_rewrite && !msg.is_audit_rewrite" class="whitespace-pre-wrap text-slate-300" v-html="msg.content.replace(/\n/g, '<br/>')"></div>
            
            <!-- HTML App Rendering (Portfolio generator) -->
            <div v-else class="space-y-4 w-full">
                <div class="p-4 bg-emerald-500/10 border border-emerald-500/20 rounded-2xl flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                    <div>
                        <h4 class="font-bold text-emerald-400 text-lg m-0">✅ Portfolio Généré</h4>
                        <p class="text-sm text-emerald-500/80 m-0 mt-1">Code source complet prêt à être déployé.</p>
                    </div>
                    <button @click="downloadHtml(msg.content)" class="px-5 py-2.5 bg-emerald-500 hover:bg-emerald-400 text-surface-950 rounded-xl font-bold transition-all shadow-lg shadow-emerald-500/20 whitespace-nowrap">
                        Télécharger HTML
                    </button>
                </div>
                
                <h4 class="text-slate-400 text-sm mt-4 font-bold border-b border-surface-700 pb-2">Aperçu du Code Source</h4>
                <div class="relative group/code">
                    <pre class="bg-surface-950/80 overflow-x-auto p-5 rounded-2xl border border-surface-700 mt-2 font-mono text-xs text-slate-300 max-h-96 shadow-inner">{{ msg.content }}</pre>
                </div>
            </div>
            
            <span class="block text-[10px] mt-4 opacity-40 font-bold" :class="msg.error ? 'text-rose-200' : 'text-slate-500'">{{ msg.timestamp }}</span>
          </div>
        </div>
      </div>
      
      <!-- Typing Indicator -->
      <div v-if="isLoading" class="flex w-full justify-start gap-4">
         <div class="shrink-0 w-8 h-8 rounded-lg bg-surface-800 flex items-center justify-center border border-surface-700 text-sm mt-1 animate-pulse">
             🤖
         </div>
         <div class="py-2.5 flex items-center gap-1.5 opacity-50">
            <div class="w-2 h-2 rounded-full bg-gold-500/50 animate-bounce" style="animation-delay: 0ms"></div>
            <div class="w-2 h-2 rounded-full bg-gold-500/50 animate-bounce" style="animation-delay: 150ms"></div>
            <div class="w-2 h-2 rounded-full bg-gold-500/50 animate-bounce" style="animation-delay: 300ms"></div>
         </div>
      </div>
    </div>

    <!-- Floating Input Area -->
    <div class="absolute bottom-4 left-4 right-4 md:left-8 md:right-8 lg:bottom-8 lg:left-8 lg:right-8 bg-surface-950/80 pt-4 backdrop-blur-md">
      <div class="bg-surface-900 border border-surface-700 p-2 rounded-2xl shadow-lg flex flex-col sm:flex-row items-end sm:items-center gap-2 focus-within:ring-1 focus-within:ring-surface-600 focus-within:border-surface-600 transition-all">
         
         <!-- Champ Localisation -->
         <div class="w-full sm:w-1/3 md:w-1/4 flex items-center gap-2 px-3 py-2 bg-surface-800 rounded-xl border border-surface-700">
             <span class="text-slate-400 text-lg">📍</span>
             <input 
                 v-model="inputLocation" 
                 type="text" 
                 placeholder="Lieu (ex: Paris, France...)" 
                 class="w-full bg-transparent border-none focus:ring-0 text-white text-sm placeholder-slate-500 p-0"
                 @keydown.enter="sendMessage"
             />
         </div>

         <!-- Séparateur visuel Desktop -->
         <div class="hidden sm:block w-px h-8 bg-surface-700 mx-1"></div>

         <!-- Champ principal Message -->
         <textarea 
            v-model="inputQuery"
            @keydown.enter.exact.prevent="sendMessage"
            class="w-full bg-transparent border-none focus:ring-0 text-white resize-none h-14 max-h-48 p-3 placeholder-slate-500 scrollbar-hide font-medium text-[15px]"
            placeholder="Rechercher un emploi, demander un audit CV..."
         ></textarea>
         
         <!-- Bouton Envoyer -->
         <button 
            @click="sendMessage"
            :disabled="(!inputQuery.trim() && !cvText.trim()) || isLoading"
            class="p-4 bg-gold-500 hover:bg-gold-400 disabled:bg-surface-800 text-surface-950 disabled:text-slate-600 rounded-xl transition-all font-bold shrink-0 shadow-lg shadow-gold-500/20"
         >
            <PaperAirplaneIcon v-if="!isLoading" class="w-6 h-6" />
            <ArrowPathIcon v-else class="w-6 h-6 animate-spin" />
         </button>
      </div>
      <div class="text-center mt-3">
          <p class="text-[11px] font-bold text-slate-500 tracking-wide">
             GoldArmy peut faire des erreurs. Vérifiez les informations importantes.
          </p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.scrollbar-hide::-webkit-scrollbar {
  display: none;
}
.scrollbar-hide {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
</style>
