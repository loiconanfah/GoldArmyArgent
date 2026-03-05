<script setup>
import { authFetch } from '../utils/auth'
import { toastState } from '../store/toastState'
import { getApiUrl } from '../config'

import { ref, onMounted, nextTick, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'
import { 
  PaperAirplaneIcon, 
  ArrowPathIcon, 
  DocumentTextIcon, 
  CheckIcon, 
  XMarkIcon, 
  ArrowUpTrayIcon, 
  EyeIcon, 
  CodeBracketIcon,
  CommandLineIcon,
  GlobeAltIcon,
  CloudArrowUpIcon,
  ChevronLeftIcon,
  ChevronRightIcon, 
  ArrowDownTrayIcon,
  PhotoIcon,
  ArrowsPointingOutIcon,
  ArrowsPointingInIcon
} from '@heroicons/vue/24/solid'
import {
    SparklesIcon,
    CloudArrowDownIcon,
    CheckCircleIcon
} from '@heroicons/vue/24/outline'

const route = useRoute()
const { t } = useI18n()
const inputQuery = ref('')
const inputLocation = ref('')
const cvText = ref('')
const cvFilename = ref('')
const isSaving = ref(false)
const isGeneratingPortfolio = ref(false)
const isUploadingCv = ref(false)
const isUploading = ref(false)
const isLoading = ref(false)
const loadingStep = ref(0) // 0 to 4 pour les étapes d'analyse CV
const loadingInterval = ref(null)
const isWorkspaceFullScreen = ref(false)
const selectedImage = ref(null) // Base64 of the design image
const currentUser = ref(null)

// Workspace IDE State
const isWorkspaceOpen = ref(false)
const activeWorkspaceTab = ref('app') // 'app', 'code', 'terminal'
const workspaceProject = ref({
    title: t('agent_chat.workspace.new_project') || 'Nouveau Projet',
    content: ''
})
const mockTerminalLogs = ref([
    { type: 'info', text: t('agent_chat.terminal.init') },
    { type: 'success', text: t('agent_chat.terminal.build_success') },
    { type: 'info', text: t('agent_chat.terminal.listening') }
])
const activeFileTab = ref('html') // 'html', 'css', 'js'
// Session unique par onglet pour que le backend maintienne l'historique
const sessionId = ref((typeof crypto !== 'undefined' && crypto.randomUUID) ? crypto.randomUUID() : `session_${Date.now()}`)

const iframeKey = ref(0) // Utilisé pour forcer le rafraîchissement de l'iframe

// Construit le srcdoc complet en injectant CSS et JS dans le HTML
const computedSrcdoc = computed(() => {
    const html = workspaceProject.value.html || ''
    const css = workspaceProject.value.css || ''
    const js = workspaceProject.value.js || ''
    if (!html) return ''
    // Injecter CSS et JS supplémentaires dans le document si pas déjà dans le HTML
    const hasCssTag = html.includes('<style') || html.includes('<link')
    const hasJsTag = html.includes('<script')
    let doc = html
    if (css && !hasCssTag) {
        doc = doc.replace('</head>', `<style>${css}</style></head>`) || `<style>${css}</style>${doc}`
    } else if (css) {
        // inject before </head> anyway as extra styles
        doc = doc.replace('</head>', `<style>${css}</style></head>`)
    }
    if (js && !hasJsTag) {
        doc = doc.replace('</body>', `<script>${js}<\/script></body>`) || `${doc}<script>${js}<\/script>`
    }
    return doc
})

const messages = ref([
  {
    id: 1,
    role: 'assistant',
    content: t('agent_chat.initial_message'),
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

const loadingStepsTexts = [
    t('agent_chat.loading_steps.step_0'),
    t('agent_chat.loading_steps.step_1'),
    t('agent_chat.loading_steps.step_2'),
    t('agent_chat.loading_steps.step_3'),
    t('agent_chat.loading_steps.step_4')
]

const startLoadingAnimation = () => {
    loadingStep.value = 0
    loadingInterval.value = setInterval(() => {
        if (loadingStep.value < 4) {
             loadingStep.value++
             scrollToBottom()
        }
    }, 2500) // Change step every 2.5s
}

const stopLoadingAnimation = () => {
    clearInterval(loadingInterval.value)
}

onMounted(async () => {
  if (route.query.prompt) {
    inputQuery.value = route.query.prompt
    sendMessage()
  }
  
  // Si on vient du profil pour éditer le portfolio
  if (route.query.action === 'edit_last_portfolio') {
      try {
          mockTerminalLogs.value.push({ type: 'info', text: t('agent_chat.terminal.restoring') })
          const res = await authFetch('/api/profile')
          const json = await res.json()
          if (json.status === 'success' && json.data.last_portfolio) {
              workspaceProject.value = {
                  title: t('agent_chat.workspace.restored_project') || 'Projet Portfolio (Restauré)',
                  ...json.data.last_portfolio
              }
              isWorkspaceOpen.value = true
              activeWorkspaceTab.value = 'app'
              mockTerminalLogs.value.push({ type: 'success', text: t('agent_chat.terminal.restore_success') })
          } else {
              mockTerminalLogs.value.push({ type: 'error', text: t('agent_chat.terminal.restore_error') })
          }
      } catch (e) {
          console.error("Erreur restauration portfolio:", e)
      }
    }

  // Fetch current user info for Admin/Premium checks
  try {
      const res = await authFetch('/api/profile')
      if (res.ok) {
          const json = await res.json()
          currentUser.value = json.data
      }
  } catch (e) {
      console.error("Erreur chargement profil:", e)
  }
})

const sendMessage = async () => {
  if (!inputQuery.value.trim() && !cvText.value.trim()) return
  
  const userMsg = inputQuery.value
  // ⚠️ Ne PAS vider inputQuery avant la garde — on le restaure si besoin

  // ─── Guard Portfolio : Bientôt Disponible ──────────────────────────────
  const isPortfolioRequest = userMsg.toLowerCase().includes('portfolio') || userMsg.toLowerCase().includes('site web')

  if (isPortfolioRequest) {
    // Afficher le message de l'utilisateur dans le chat
    if (userMsg) {
      messages.value.push({
        id: Date.now(),
        role: 'user',
        content: userMsg,
        timestamp: new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})
      })
    }
    // Répondre avec un message d'attente (Feature en cours de dev)
    messages.value.push({
      id: Date.now() + 1,
      role: 'assistant',
      content: t('agent_chat.portfolio_soon_title') + '\n\n' + t('agent_chat.portfolio_soon_desc'),
      timestamp: new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})
    })
    scrollToBottom()
    inputQuery.value = ''
    return  // Bloquer l'envoi au backend
  }
  // ────────────────────────────────────────────────────────────────────────

  // Maintenant on peut vider l'input
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
  
  if (cvText.value) {
      startLoadingAnimation()
  }
  // Si on détecte une demande de portfolio, on prépare le workspace
  if (userMsg.toLowerCase().includes('portfolio')) {
      isGeneratingPortfolio.value = true
      isWorkspaceOpen.value = true
      activeWorkspaceTab.value = 'app'
      mockTerminalLogs.value.push({ type: 'info', text: t('agent_chat.terminal.designing') })
  }
  
  try {
    const res = await authFetch('/api/chat', {
        method: 'POST',
        body: JSON.stringify({ 
            message: userMsg, 
            cv_text: cvText.value, 
            cv_filename: cvFilename.value, 
            // Ne pas forcer nb_results si un CV est présent (évite le faux déclenchement du quota job search)
            nb_results: cvText.value ? null : 5, 
            location: inputLocation.value,
            session_id: sessionId.value,
            image_data: selectedImage.value
        })
    })
    const data = await res.json()
    
    // Gère la réponse plate {status, type, content} (ex: limit_reached) ET la réponse imbriquée {status, data: {type, content}}
    const responseData = data.data || data
    
    const assistantMsg = {
      id: Date.now() + 2,
      role: 'assistant',
      type: responseData.type || 'chat',
      is_html: responseData.type === 'portfolio_html',
      activeTab: responseData.type === 'portfolio_html' ? 'preview' : 'code',
      is_cv_rewrite: responseData.type === 'cv_rewrite',
      is_audit_rewrite: responseData.type === 'cv_audit_rewrite',
      audit: responseData.audit || '',
      content: responseData.content || data.detail || data.message || '⚠️ Réponse vide du serveur. Vérifiez les logs backend.',
      timestamp: new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})
    }
    
    
    // Si c'est un portfolio (Projet structuré), on l'ouvre dans le Workspace SANS message dans le chat
    if (responseData.type === 'portfolio_project' && responseData.project) {
        workspaceProject.value = {
            title: 'Projet Portfolio',
            ...responseData.project
        }
        isWorkspaceOpen.value = true
        activeWorkspaceTab.value = 'app'
        
        // Push personality analysis to terminal only
        if (responseData.project.personality_analysis) {
             mockTerminalLogs.value.push({ type: 'info', text: t('agent_chat.terminal.analysis', [responseData.project.personality_analysis]) })
        }
        mockTerminalLogs.value.push({ type: 'success', text: t('agent_chat.terminal.project_success') })
    }
    // Cas fallback pour l'ancien format HTML unique
    else if (assistantMsg.is_html) {
        workspaceProject.value = {
            title: 'Portfolio Généré',
            html: assistantMsg.content,
            css: '',
            js: ''
        }
        isWorkspaceOpen.value = true
        activeWorkspaceTab.value = 'app'
    }
    else {
        // Pour tout le reste, on garde le message dans le chat
        messages.value.push(assistantMsg)
    }
    
    // Clear image after send
    selectedImage.value = null
    
  } catch (e) {
    messages.value.push({
      id: Date.now() + 2,
      role: 'assistant',
      content: t('agent_chat.network_error_backend'),
      timestamp: new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}),
      error: true
    })
  } finally {
    isLoading.value = false
    stopLoadingAnimation()
    isGeneratingPortfolio.value = false
    scrollToBottom()
  }
}

const uploadCvPdf = async (event) => {
    const file = event.target.files[0]
    if (!file) return
    if (!file.name.toLowerCase().endsWith('.pdf')) {
        toastState.addToast(t('agent_chat.upload_pdf_only'), 'error')
        return
    }
    isUploadingCv.value = true
    cvFilename.value = ''
    cvText.value = ''
    try {
        const formData = new FormData()
        formData.append('file', file)
        const res = await authFetch('/api/parse-pdf', {
            method: 'POST',
            body: formData
        })
        const data = await res.json()
        if (data.status === 'success' && data.text) {
            cvText.value = data.text
            cvFilename.value = file.name
        } else {
            toastState.addToast(data.detail || t('agent_chat.error_reading_pdf'), 'error')
        }
    } catch (e) {
        toastState.addToast(t('agent_chat.network_error_pdf'), 'error')
    } finally {
        isUploadingCv.value = false
    }
}

const removeCv = () => {
    cvText.value = ''
    cvFilename.value = ''
}

const saveWorkspaceProject = async () => {
    try {
        isSaving.value = true
        const res = await authFetch('/api/profile', {
            method: 'POST',
            body: JSON.stringify({
                last_portfolio: {
                    html: workspaceProject.value.html,
                    css: workspaceProject.value.css,
                    js: workspaceProject.value.js,
                    personality_analysis: workspaceProject.value.personality_analysis
                }
            })
        })
        const json = await res.json()
        if (json.status === 'success') {
            toastState.addToast(t('agent_chat.workspace.save_success'))
            mockTerminalLogs.value.push({ type: 'success', text: t('agent_chat.terminal.save_db') })
            iframeKey.value++ // Rafraîchir l'iframe pour voir les changements
        }
    } catch (e) {
        toastState.addToast(t('agent_chat.workspace.save_error'), "error")
    } finally {
        isSaving.value = false
    }
}

const downloadZip = async () => {
    try {
        const res = await authFetch('/api/portfolio/download-zip')
        if (!res.ok) throw new Error("Erreur de téléchargement")
        const blob = await res.blob()
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = 'goldarmy_portfolio.zip'
        a.click()
    } catch (e) {
        toastState.addToast(t('agent_chat.workspace.zip_error'), 'error')
    }
}

const CV_THEMES = [
    { id: 'midnight', name: 'Midnight Pro (Sidebar Gauche)', colors: ['#1e293b', '#38bdf8'] },
    { id: 'emerald', name: 'Emerald Leader (Sidebar Gauche)', colors: ['#064e3b', '#10b981'] },
    { id: 'modern', name: 'Modern Startup (Sidebar Droite)', colors: ['#4c1d95', '#8b5cf6'] },
    { id: 'minimal', name: 'Executive Minimal (Une Colonne)', colors: ['#ffffff', '#0f172a'] },
    { id: 'bold', name: 'Creative Bold (Grille Bento)', colors: ['#000000', '#f43f5e'] },
    { id: 'banker', name: 'Trustworthy Banker (Bandeau Top)', colors: ['#1e3a8a', '#1e40af'] },
    { id: 'tech', name: 'Tech Terminal (Style Code)', colors: ['#000000', '#22c55e'] },
    { id: 'classic', name: 'Classic Academic (Minimal Centré)', colors: ['#ffffff', '#451a03'] },
    { id: 'vibrant', name: 'Vibrant Energy (Deux Colonnes)', colors: ['#991b1b', '#ea580c'] },
    { id: 'luxury', name: 'Elegant Luxury (Compact Pro)', colors: ['#000000', '#ca8a04'] }
]
const selectedTheme = ref('midnight')

const isDownloadingDocx = ref(false)
const downloadCvDocx = async (cvJsonString) => {
    isDownloadingDocx.value = true
    try {
        let filename = 'CV_ATS_Optimise'
        try {
            const parsed = JSON.parse(cvJsonString)
            if (parsed.full_name) {
                filename = `CV_${parsed.full_name.replace(/\s+/g, '_')}_ATS`
            }
        } catch {}

        const res = await authFetch('/api/generate-cv-pdf', {
            method: 'POST',
            body: JSON.stringify({ 
                cv_json: cvJsonString, 
                filename,
                theme_id: selectedTheme.value
            })
        })

        if (!res.ok) {
            const err = await res.json()
            toastState.addToast(`Erreur: ${err.detail || 'Impossible de générer le CV'}`, 'error')
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
        toastState.addToast('Erreur lors du téléchargement du CV.', 'error')
    } finally {
        isDownloadingDocx.value = false
    }
}
const openInWorkspace = (msg) => {
    if (msg.type === 'portfolio_project' && msg.project) {
        workspaceProject.value = {
            title: 'Projet Portfolio',
            ...msg.project
        }
    } else {
        workspaceProject.value = {
            title: 'Portfolio',
            html: msg.content,
            css: '',
            js: ''
        }
    }
    isWorkspaceOpen.value = true
    activeWorkspaceTab.value = 'app'
}
</script>

<template>
  <div class="h-screen w-full flex bg-surface-950 overflow-hidden relative">

    <!-- LEFT PANEL: CHAT (Flexible width) -->
    <div v-show="!isWorkspaceFullScreen" :class="['flex flex-col h-full border-r border-surface-800 transition-all duration-300', isWorkspaceOpen ? 'w-full md:w-1/3' : 'w-full']">
        <div class="h-full flex flex-col p-4 md:p-6 relative">

    <!-- Header Minimal -->
    <div class="flex items-center justify-between mb-8">
      <div>
        <h2 class="text-2xl font-display font-black text-white tracking-tight">{{ t('agent_chat.title') }}</h2>
        <p class="text-slate-400 mt-1 text-sm font-medium">{{ t('agent_chat.tagline') }}</p>
      </div>
      
      <!-- Context Toggle Button -->
      <button 
        @click="isUploading = !isUploading" 
        :class="cvFilename ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30' : 'bg-surface-800 text-slate-300 hover:text-white border-surface-700 hover:border-surface-600'" 
        class="px-4 py-2 rounded-xl border flex items-center gap-2 transition-all shadow-sm text-sm font-bold"
      >
          <DocumentTextIcon class="w-4 h-4" />
          <span class="hidden sm:inline">{{ cvFilename ? cvFilename : t('agent_chat.add_cv') }}</span>
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
                    {{ t('agent_chat.cv_context') }}
                </h3>
                <button @click="isUploading = false" class="text-slate-500 hover:text-white text-xs font-bold uppercase tracking-wider">{{ t('common.close') || 'Fermer' }}</button>
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
                    {{ isUploadingCv ? t('agent_chat.extracting_text') : t('agent_chat.click_to_upload') }}
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
                  <p class="font-bold text-white text-sm m-0">{{ msg.audit.candidate_name || t('agent_chat.audit.candidate') }}</p>
                  <p class="text-slate-400 text-xs m-0">{{ msg.audit.candidate_title || t('agent_chat.audit.title') }}</p>
                </div>
                <div class="ml-auto text-right">
                  <p class="text-[10px] text-slate-500 uppercase tracking-wide">{{ t('agent_chat.audit.ats_report') }}</p>
                </div>
              </div>

              <!-- Score ATS principal + barres de catégories -->
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">

                <!-- Score circulaire -->
                <div class="p-5 bg-surface-800/60 border border-surface-700 rounded-2xl flex flex-col items-center justify-center gap-3">
                  <p class="text-xs font-bold text-slate-400 uppercase tracking-widest">{{ t('agent_chat.audit.global_score') }}</p>
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
                    {{ msg.audit.ats_score >= 75 ? t('agent_chat.audit.good_profile') : msg.audit.ats_score >= 50 ? t('agent_chat.audit.to_improve') : t('agent_chat.audit.risk_rejection') }}
                  </p>
                </div>

                <!-- Barres de scores par catégorie -->
                <div class="p-5 bg-surface-800/60 border border-surface-700 rounded-2xl space-y-3">
                  <p class="text-xs font-bold text-slate-400 uppercase tracking-widest mb-4">{{ t('common.detail_by_category') || 'Détail par catégorie' }}</p>
                  <template v-if="msg.audit.scores">
                    <div v-for="(val, key) in {
                      [t('agent_chat.audit.categories.keywords')]: msg.audit.scores.mots_cles,
                      [t('agent_chat.audit.categories.impact')]: msg.audit.scores.impact_resultats,
                      [t('agent_chat.audit.categories.formatting')]: msg.audit.scores.mise_en_forme,
                      [t('agent_chat.audit.categories.readability')]: msg.audit.scores.lisibilite,
                      [t('agent_chat.audit.categories.relevance')]: msg.audit.scores.experience_pertinence
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
                   <p class="text-xs font-bold text-red-400 uppercase tracking-widest mb-3">{{ t('agent_chat.audit.critical_flaws') }}</p>
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
                   <p class="text-xs font-bold text-green-400 uppercase tracking-widest mb-3">{{ t('agent_chat.audit.priority_actions') }}</p>
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
                   <p class="text-xs font-bold text-amber-400 uppercase tracking-widest mb-3">{{ t('agent_chat.audit.missing_tech') }}</p>
                   <div class="flex flex-wrap gap-2">
                     <span v-for="tech in msg.audit.tech_manquantes" :key="tech"
                       class="px-2.5 py-1 bg-amber-500/10 border border-amber-500/20 text-amber-300 text-[11px] font-bold rounded-lg"
                     >{{ tech }}</span>
                   </div>
                 </div>
 
                 <!-- Points forts -->
                 <div v-if="msg.audit.points_forts && msg.audit.points_forts.length" class="p-4 bg-indigo-500/5 border border-indigo-500/20 rounded-2xl">
                   <p class="text-xs font-bold text-indigo-400 uppercase tracking-widest mb-3">{{ t('agent_chat.audit.strengths') }}</p>
                   <ul class="space-y-1.5">
                     <li v-for="(pt, i) in msg.audit.points_forts" :key="i" class="flex gap-2 text-xs text-slate-300">
                       <span class="text-indigo-400 shrink-0">•</span>
                       <span>{{ pt }}</span>
                     </li>
                   </ul>
                 </div>
               </div>
 
               <!-- Sélecteur de Thème -->
               <div class="p-4 bg-surface-900/50 border border-surface-700/50 rounded-2xl">
                 <p class="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-3">SÉLECTIONNE TON DESIGN PREMIUM</p>
                 <div class="grid grid-cols-5 gap-2">
                   <button 
                     v-for="theme in CV_THEMES" 
                     :key="theme.id"
                     @click="selectedTheme = theme.id"
                     :title="theme.name"
                     class="group relative h-10 rounded-lg border transition-all overflow-hidden"
                     :class="selectedTheme === theme.id ? 'border-gold-500 ring-2 ring-gold-500/20' : 'border-surface-700 hover:border-surface-600'"
                   >
                     <div class="absolute inset-0 flex">
                       <div class="w-1/2 h-full" :style="{ backgroundColor: theme.colors[0] }"></div>
                       <div class="w-1/2 h-full" :style="{ backgroundColor: theme.colors[1] }"></div>
                     </div>
                     <div v-if="selectedTheme === theme.id" class="absolute inset-0 bg-gold-500/10 flex items-center justify-center">
                       <CheckIcon class="w-4 h-4 text-white drop-shadow-md" />
                     </div>
                   </button>
                 </div>
                 <p class="text-[11px] text-center text-slate-400 mt-2 font-bold">{{ CV_THEMES.find(t => t.id === selectedTheme)?.name }}</p>
               </div>

               <!-- Bouton téléchargement -->
               <button
                 @click="downloadCvDocx(msg.content)"
                 :disabled="isDownloadingDocx"
                 class="w-full flex items-center justify-center gap-2 px-5 py-3.5 bg-gradient-to-r from-indigo-500 to-purple-500 hover:from-indigo-400 hover:to-purple-400 disabled:from-surface-700 disabled:to-surface-700 disabled:text-slate-500 text-white rounded-xl font-bold transition-all shadow-lg shadow-indigo-500/20 text-sm"
               >
                 <ArrowUpTrayIcon v-if="!isDownloadingDocx" class="w-4 h-4 rotate-180" />
                 <ArrowPathIcon v-else class="w-4 h-4 animate-spin" />
                 {{ isDownloadingDocx ? t('agent_chat.audit.generating_file') : t('agent_chat.audit.download_cv') }}
               </button>
               <p class="text-[10px] text-slate-500 text-center">{{ t('agent_chat.audit.ats_friendly') }}</p>
             </div>
 
             <!-- Fallback audit si format non-structuré (chaîne texte) -->
             <div v-else-if="msg.is_audit_rewrite && msg.audit && typeof msg.audit === 'string'" class="space-y-4 w-full">
               <div class="whitespace-pre-wrap text-slate-300 pb-4 border-b border-surface-700" v-html="msg.audit.replace(/\n/g, '<br/>')"></div>
               <button @click="downloadCvDocx(msg.content)" :disabled="isDownloadingDocx"
                 class="w-full flex items-center justify-center gap-2 px-5 py-3 bg-indigo-500 hover:bg-indigo-400 text-white rounded-xl font-bold transition-all">
                 <ArrowUpTrayIcon v-if="!isDownloadingDocx" class="w-4 h-4 rotate-180" />
                 <ArrowPathIcon v-else class="w-4 h-4 animate-spin" />
                 {{ isDownloadingDocx ? (t('common.generating') || 'Génération...') : t('agent_chat.audit.download_cv') }}
               </button>
             </div>
 
             <!-- ══════════ CV REWRITE (sans audit dashboard) ══════════ -->
             <div v-else-if="msg.is_cv_rewrite" class="space-y-4 w-full">
               <div class="flex items-center gap-3 p-4 bg-indigo-500/10 border border-indigo-500/30 rounded-2xl">
                 <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-lg">✍️</div>
                 <div>
                   <p class="font-bold text-white text-sm m-0">{{ t('agent_chat.audit.rewrite_title') }}</p>
                   <p class="text-slate-400 text-xs m-0">{{ t('agent_chat.audit.rewrite_desc') }}</p>
                 </div>
               </div>
               <button
                 @click="downloadCvDocx(msg.content)"
                 :disabled="isDownloadingDocx"
                 class="w-full flex items-center justify-center gap-2 px-5 py-3.5 bg-gradient-to-r from-indigo-500 to-purple-500 hover:from-indigo-400 hover:to-purple-400 disabled:from-surface-700 disabled:to-surface-700 disabled:text-slate-500 text-white rounded-xl font-bold transition-all shadow-lg shadow-indigo-500/20 text-sm"
               >
                 <ArrowUpTrayIcon v-if="!isDownloadingDocx" class="w-4 h-4 rotate-180" />
                 <ArrowPathIcon v-else class="w-4 h-4 animate-spin" />
                 {{ isDownloadingDocx ? t('agent_chat.audit.generating_file') : t('agent_chat.audit.download_cv_rewritten') }}
               </button>
               <p class="text-[10px] text-slate-500 text-center">{{ t('agent_chat.audit.ats_friendly') }}</p>
             </div>

            <!-- Standard text/markdown rendering -->
            <div v-else-if="!msg.is_html && !msg.is_cv_rewrite && !msg.is_audit_rewrite" class="whitespace-pre-wrap text-slate-300" v-html="msg.content.replace(/\n/g, '<br/>')"></div>
            
            <!-- Workspace Notification (REMOVED as requested) -->
            <div v-else-if="msg.type === 'portfolio_project' || msg.is_html" class="hidden">
            </div>
            
            <span class="block text-[10px] mt-4 opacity-40 font-bold" :class="msg.error ? 'text-rose-200' : 'text-slate-500'">{{ msg.timestamp }}</span>
          </div>
        </div>
      </div>
      
      <!-- Typing Indicator & Analysis Steps -->
      <div v-if="isLoading" class="flex w-full justify-start gap-4 transition-all duration-500">
         <div class="shrink-0 w-8 h-8 rounded-lg bg-surface-800 flex items-center justify-center border border-surface-700 text-sm mt-1 animate-pulse shadow-glow shadow-gold-500/10">
             🤖
         </div>
         
         <!-- Loading CV Analysis Steps -->
         <div v-if="cvText" class="w-full max-w-sm bg-surface-800/50 border border-surface-700/50 rounded-2xl p-4 shadow-sm backdrop-blur-sm">
             <div class="flex items-center gap-2 mb-3">
                 <SparklesIcon class="w-4 h-4 text-gold-400 animate-pulse" />
                 <span class="text-xs font-bold text-gold-400 uppercase tracking-widest">{{ t('common.processing') || 'Traitement en cours' }}</span>
             </div>
             <div class="space-y-3">
                 <div v-for="(stepText, index) in loadingStepsTexts" :key="index" 
                      class="flex items-center gap-3 transition-all duration-500"
                      :class="{'opacity-100': loadingStep >= index, 'opacity-20 hidden': loadingStep < index}">
                     
                     <div v-if="loadingStep > index" class="w-5 h-5 rounded-full bg-emerald-500/20 flex items-center justify-center shrink-0">
                         <CheckCircleIcon class="w-3.5 h-3.5 text-emerald-400" />
                     </div>
                     <div v-else-if="loadingStep === index" class="w-5 h-5 rounded-full border-2 border-gold-500 border-t-transparent animate-spin shrink-0"></div>
                     
                     <span class="text-xs font-medium" :class="loadingStep > index ? 'text-slate-400 line-through' : 'text-slate-200'">
                         {{ stepText }}
                     </span>
                 </div>
             </div>
         </div>
         
         <!-- Standard Typing dots (if not CV) -->
         <div v-else class="py-2.5 flex items-center gap-1.5 opacity-50">
            <div class="w-2 h-2 rounded-full bg-gold-500/50 animate-bounce" style="animation-delay: 0ms"></div>
            <div class="w-2 h-2 rounded-full bg-gold-500/50 animate-bounce" style="animation-delay: 150ms"></div>
            <div class="w-2 h-2 rounded-full bg-gold-500/50 animate-bounce" style="animation-delay: 300ms"></div>
         </div>
      </div>
    </div>

      <div class="absolute bottom-4 left-4 right-4 bg-surface-950/90 pt-4 backdrop-blur-md">
        <div class="bg-surface-900 border border-surface-700 p-2 rounded-2xl shadow-lg flex flex-col sm:flex-row items-end sm:items-center gap-2">
           <!-- Location Field -->
           <div class="w-full sm:w-1/3 flex items-center gap-2 px-3 py-2 bg-surface-800 rounded-xl border border-surface-700">
               <span class="text-slate-400">📍</span>
               <input v-model="inputLocation" type="text" :placeholder="t('agent_chat.placeholders.location')" class="w-full bg-transparent border-none focus:ring-0 text-white text-xs"/>
           </div>
            <!-- Image Upload -->
            <div class="flex items-center px-2">
                <label class="cursor-pointer p-2 hover:bg-surface-800 rounded-xl transition-colors text-slate-400 hover:text-gold-400 relative">
                    <PhotoIcon class="w-5 h-5" />
                    <input type="file" accept="image/*" class="hidden" @change="e => {
                        const file = e.target.files[0];
                        if (file) {
                            const reader = new FileReader();
                            reader.onload = (ev) => { selectedImage.value = ev.target.result; };
                            reader.readAsDataURL(file);
                        }
                    }" />
                    <!-- Preview dot -->
                    <div v-if="selectedImage" class="absolute top-1.5 right-1.5 w-2 h-2 bg-emerald-500 rounded-full border border-surface-900 shadow-sm"></div>
                </label>
            </div>
            <!-- Main Message -->
            <textarea v-model="inputQuery" @keydown.enter.exact.prevent="sendMessage" class="w-full bg-transparent border-none focus:ring-0 text-white resize-none h-12 p-2 text-sm" :placeholder="t('agent_chat.placeholders.message')"></textarea>
           <!-- Send Button -->
           <button @click="sendMessage" :disabled="isLoading" class="p-3 bg-gold-500 hover:bg-gold-400 text-surface-950 rounded-xl font-bold shrink-0">
              <PaperAirplaneIcon v-if="!isLoading" class="w-5 h-5" />
              <ArrowPathIcon v-else class="w-5 h-5 animate-spin" />
           </button>
        </div>
      </div>
    </div>
  </div>

    <!-- RIGHT PANEL: WORKSPACE (IDE Style) -->
    <div v-if="isWorkspaceOpen" class="flex-1 h-full bg-[#020617] flex flex-col shadow-2xl animate-fade-in">
        <!-- Explorer / Workspace Header (IDE Style) -->
        <div class="flex items-center justify-between px-4 py-2 border-b border-surface-800 bg-surface-950">
            <div class="flex items-center gap-4">
                <div class="flex items-center gap-1.5 p-1 bg-surface-900 rounded-lg border border-surface-800">
                    <button @click="activeWorkspaceTab = 'app'" :class="activeWorkspaceTab === 'app' ? 'bg-surface-700 text-white' : 'text-slate-500'" class="px-3 py-1 text-xs font-bold rounded flex items-center gap-1.5 transition-all">
                        <GlobeAltIcon class="w-3.5 h-3.5" /> {{ t('agent_chat.workspace.app') }}
                    </button>
                    <button @click="activeWorkspaceTab = 'code'" :class="activeWorkspaceTab === 'code' ? 'bg-surface-700 text-white' : 'text-slate-500'" class="px-3 py-1 text-xs font-bold rounded flex items-center gap-1.5 transition-all">
                        <CodeBracketIcon class="w-3.5 h-3.5" /> {{ t('agent_chat.workspace.code') }}
                    </button>
                    <button @click="activeWorkspaceTab = 'terminal'" :class="activeWorkspaceTab === 'terminal' ? 'bg-surface-700 text-white' : 'text-slate-500'" class="px-3 py-1 text-xs font-bold rounded flex items-center gap-1.5 transition-all">
                        <CommandLineIcon class="w-3.5 h-3.5" /> {{ t('agent_chat.workspace.terminal') }}
                    </button>
                </div>
                <div class="hidden lg:flex items-center gap-2 text-slate-500 text-[11px] font-mono">
                    <span class="opacity-50">/</span>
                    <span>{{ workspaceProject.title }}</span>
                </div>
            </div>

            <div class="flex items-center gap-2">
                <button @click="saveWorkspaceProject" :disabled="isSaving" class="flex items-center gap-2 px-3 py-1.5 bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold rounded-lg transition-all shadow-lg shadow-blue-500/20 disabled:opacity-50">
                    <CloudArrowDownIcon class="w-3.5 h-3.5" /> {{ isSaving ? t('agent_chat.workspace.saving') : t('agent_chat.workspace.save') }}
                </button>
                <div class="h-4 w-[1px] bg-surface-800 mx-1"></div>
                <button @click="isWorkspaceFullScreen = !isWorkspaceFullScreen" class="p-2 text-slate-400 hover:text-white transition-colors">
                    <ArrowsPointingOutIcon v-if="!isWorkspaceFullScreen" class="w-4 h-4" />
                    <ArrowsPointingInIcon v-else class="w-4 h-4" />
                </button>
                <button @click="downloadZip" class="flex items-center gap-2 px-3 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold rounded-lg transition-all shadow-lg shadow-emerald-500/20">
                    <ArrowDownTrayIcon class="w-3.5 h-3.5" /> {{ t('agent_chat.workspace.zip') }}
                </button>
                <button class="flex items-center gap-2 px-3 py-1.5 bg-surface-800 text-slate-500 text-xs font-bold rounded-lg transition-all border border-surface-700 cursor-not-allowed relative overflow-hidden group">
                    <CloudArrowUpIcon class="w-3.5 h-3.5" /> {{ t('agent_chat.workspace.deploy') }}
                    <span class="absolute -top-1 -right-1 bg-amber-500 text-[8px] text-white px-1.5 py-0.5 rounded shadow-sm rotate-12 scale-90 group-hover:scale-100 transition-transform">{{ t('agent_chat.workspace.soon') }}</span>
                </button>
                <button @click="isWorkspaceOpen = false" class="p-2 text-slate-500 hover:text-rose-400 transition-colors ml-2">
                    <XMarkIcon class="w-5 h-5" />
                </button>
            </div>
        </div>

        <!-- Address Bar (Browser-like) -->
        <div v-if="activeWorkspaceTab === 'app'" class="flex items-center gap-4 px-4 py-2 bg-[#0a0f1d] border-b border-surface-800">
            <div class="flex items-center gap-1 text-slate-500">
                <ChevronLeftIcon class="w-4 h-4" />
                <ChevronRightIcon class="w-4 h-4" />
                <ArrowPathIcon class="w-3.5 h-3.5 ml-1" />
            </div>
            <div class="flex-1 bg-surface-950 border border-surface-800 rounded-lg px-3 py-1.5 flex items-center gap-2 text-[11px] text-slate-400 font-mono">
                <span class="opacity-50">http://localhost:3000/</span>
            </div>
            <div class="text-slate-600 text-[10px] font-black uppercase tracking-widest">3000</div>
        </div>

        <!-- Workspace Content Area -->
        <div class="flex-1 w-full overflow-hidden relative bg-white">
            <!-- LOADING STATE -->
            <div v-if="isGeneratingPortfolio" class="absolute inset-0 z-50 bg-surface-950 flex flex-col items-center justify-center p-8 text-center animate-fade-in">
                <div class="relative mb-8">
                    <div class="w-24 h-24 border-4 border-indigo-500/20 border-t-indigo-500 rounded-full animate-spin"></div>
                    <SparklesIcon class="w-8 h-8 text-indigo-400 absolute inset-0 m-auto animate-pulse" />
                </div>
                <h3 class="text-2xl font-display font-black text-white mb-3 tracking-tight">{{ t('agent_chat.workspace.generating_portfolio', ['Portfolio']) }}</h3>
                <p class="text-slate-400 text-sm max-w-sm leading-relaxed">
                    {{ t('agent_chat.workspace.generating_portfolio_desc') }}
                </p>
                <div class="mt-10 flex gap-2">
                    <div class="w-1.5 h-1.5 rounded-full bg-indigo-500 animate-bounce" style="animation-delay: 0s"></div>
                    <div class="w-1.5 h-1.5 rounded-full bg-indigo-500 animate-bounce" style="animation-delay: 0.2s"></div>
                    <div class="w-1.5 h-1.5 rounded-full bg-indigo-500 animate-bounce" style="animation-delay: 0.4s"></div>
                </div>
            </div>

            <!-- APP PREVIEW (rendered via srcdoc - no backend endpoint needed) -->
            <div v-if="activeWorkspaceTab === 'app' && !computedSrcdoc && !isGeneratingPortfolio" class="flex flex-col items-center justify-center h-full bg-surface-950 text-slate-500 gap-3">
                <GlobeAltIcon class="w-10 h-10 opacity-30" />
                <p class="text-sm font-medium">{{ t('agent_chat.workspace.no_preview') }}</p>
            </div>
            <iframe 
                v-else-if="activeWorkspaceTab === 'app' && computedSrcdoc"
                :srcdoc="computedSrcdoc" 
                :key="iframeKey"
                class="w-full h-full border-none bg-white" 
                sandbox="allow-scripts allow-same-origin"
            ></iframe>
            
            <!-- CODE EDITOR (Pre) -->
            <div v-else-if="activeWorkspaceTab === 'code'" class="h-full bg-[#0d1117] flex flex-col">
                <!-- File Selector Tabs -->
                <div class="flex items-center gap-1 p-2 bg-surface-950 border-b border-surface-800">
                    <button @click="activeFileTab = 'html'" :class="activeFileTab === 'html' ? 'bg-surface-800 text-orange-400' : 'text-slate-500'" class="px-3 py-1 text-[10px] font-bold rounded flex items-center gap-2">
                        <span class="w-1.5 h-1.5 rounded-full bg-orange-500"></span> index.html
                    </button>
                    <button @click="activeFileTab = 'css'" :class="activeFileTab === 'css' ? 'bg-surface-800 text-blue-400' : 'text-slate-500'" class="px-3 py-1 text-[10px] font-bold rounded flex items-center gap-2">
                        <span class="w-1.5 h-1.5 rounded-full bg-blue-500"></span> style.css
                    </button>
                    <button @click="activeFileTab = 'js'" :class="activeFileTab === 'js' ? 'bg-surface-800 text-yellow-400' : 'text-slate-500'" class="px-3 py-1 text-[10px] font-bold rounded flex items-center gap-2">
                        <span class="w-1.5 h-1.5 rounded-full bg-yellow-500"></span> script.js
                    </button>
                </div>

                <!-- Editor -->
                <div class="flex-1 overflow-hidden p-0 font-mono text-xs text-slate-300 bg-[#0d1117]">
                    <textarea 
                        v-if="activeFileTab === 'html'" 
                        v-model="workspaceProject.html"
                        class="w-full h-full bg-transparent p-4 resize-none focus:outline-none custom-scrollbar leading-relaxed text-slate-300"
                    ></textarea>
                    <textarea 
                        v-else-if="activeFileTab === 'css'" 
                        v-model="workspaceProject.css"
                        class="w-full h-full bg-transparent p-4 resize-none focus:outline-none custom-scrollbar leading-relaxed text-slate-300"
                    ></textarea>
                    <textarea 
                        v-else-if="activeFileTab === 'js'" 
                        v-model="workspaceProject.js"
                        class="w-full h-full bg-transparent p-4 resize-none focus:outline-none custom-scrollbar leading-relaxed text-slate-300"
                    ></textarea>
                </div>
            </div>

            <!-- TERMINAL -->
            <div v-else-if="activeWorkspaceTab === 'terminal'" class="h-full bg-black p-4 font-mono text-xs overflow-auto">
                <div v-for="(log, i) in mockTerminalLogs" :key="i" :class="['mb-1', log.type === 'error' ? 'text-red-400' : log.type === 'success' ? 'text-emerald-400' : 'text-slate-400']">
                    {{ log.text }}
                </div>
                <div class="flex items-center gap-2 text-slate-300 mt-2">
                    <span class="text-emerald-400">➜</span>
                    <span class="text-indigo-400">~/goldarmy-workspace</span>
                    <span class="animate-pulse">_</span>
                </div>
            </div>
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
