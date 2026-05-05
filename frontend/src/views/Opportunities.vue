<script setup>
import { authFetch } from '../utils/auth'
import { toastState } from '../store/toastState'
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { toRefs } from 'vue'
import { sniperState } from '../store/sniperState'
import { 
    BriefcaseIcon, 
    FunnelIcon, 
    MapPinIcon, 
    CurrencyDollarIcon, 
    CheckCircleIcon,
    MagnifyingGlassIcon,
    DocumentTextIcon,
    ArrowPathIcon,
    SparklesIcon,
    SignalIcon,
    ArrowUpTrayIcon,
    XMarkIcon
} from '@heroicons/vue/24/outline'
import { CV_TEMPLATES } from '../utils/cvTemplates/index'

const {
    filter, searchQuery, inputLocation, cvText, isUploading, isLoading, isParsingPdf, 
    jobs, selectedFileName, resultLimit, loadingRadarFor
} = toRefs(sniperState)


const CV_THEMES = CV_TEMPLATES.map(t => ({
  id: t.id,
  name: t.label,
  colors: [t.accentColor, t.accentColor],
  build: t.build,
}))

const showAdaptCvModal = ref(false)
const adaptCvCard = ref(null)
const cvTextForAdapt = ref('')
const isAdaptingCv = ref(false)
const adaptedData = ref(null)
const adaptCvFileInput = ref(null)

const showDownloadCvModal = ref(false)
const selectedCvTheme = ref('goldarmy')
const isDownloadingPdf = ref(false)

const { t } = useI18n()

const fileInput = ref(null)

const triggerFileInput = () => {
    fileInput.value?.click()
}

const handleFileUpload = async (event) => {
    const file = event.target.files[0]
    if (!file) return
    
    if (file.type !== 'application/pdf') {
        toastState.addToast(t('opportunities.upload_pdf_only') || "Veuillez sélectionner un fichier PDF.", "error")
        return
    }
    
    selectedFileName.value = file.name
    isParsingPdf.value = true
    cvText.value = "" // Reset old cv text
    
    const formData = new FormData()
    formData.append('file', file)
    
    try {
        const res = await authFetch('/api/parse-pdf', {
            method: 'POST',
            body: formData
        })
        
        const json = await res.json()
        if (json.status === "success") {
            cvText.value = json.text
            isUploading.value = false // Collpase the menu
            // If the user already typed a query, Auto-start the search
            if (searchQuery.value.trim()) {
                performSearch()
            }
        } else {
             toastState.addToast(json.detail || t('opportunities.error_reading_pdf') || "Erreur lors de la lecture du PDF.", "error")
             selectedFileName.value = ""
        }
    } catch(e) {
        toastState.addToast(t('opportunities.network_error_cv') || "Erreur réseau lors de l'envoi du CV.", "error")
        selectedFileName.value = ""
        console.error(e)
    } finally {
        isParsingPdf.value = false
    }
}

const filteredJobs = computed(() => {
    if (filter.value === t('opportunities.filters.all')) return jobs.value;
    return jobs.value.filter(job => {
        if (filter.value === t('opportunities.filters.internships')) return job.type.toLowerCase().includes('stage') || job.title.toLowerCase().includes('stage') || job.title.toLowerCase().includes('intern')
        if (filter.value === t('opportunities.filters.juniors')) return job.type.toLowerCase().includes('junior') || job.title.toLowerCase().includes('junior')
        if (filter.value === t('opportunities.filters.score_80')) return job.matchScore > 80
        return true
    })
})


const parseMarkdownJobs = (mdText) => {
    // Basic parser to turn the LLM Markdown return into structured objects for the UI
    const parsedJobs = []
    
    if (typeof mdText === 'object') {
        // If the backend returned raw JSON job lists directly
        return mdText.jobs || mdText
    }
    
    const lines = mdText.split('\n')
    let currentJob = null
    
    for (let line of lines) {
        if (line.startsWith('### ')) {
            if (currentJob) parsedJobs.push(currentJob)
            currentJob = {
                id: Math.random().toString(36).substr(2, 9),
                title: line.replace('### ', '').trim(),
                company: t('common.not_specified') || 'Non spécifié',
                location: t('common.not_specified') || 'Non spécifié',
                matchScore: 0,
                salary: t('common.not_specified') || 'Non spécifié',
                type: t('opportunities.job_stage') || 'Emploi / Stage',
                posted: t('opportunities.recent') || "Récent",
                desc: "",
                rawUrl: ""
            }
        } else if (currentJob) {
            if (line.includes('**Entreprise:**')) currentJob.company = line.split('**Entreprise:**')[1].trim()
            if (line.includes('**Localisation:**')) currentJob.location = line.split('**Localisation:**')[1].trim()
            if (line.includes('**Score de Match:**')) {
                const scoreMatch = line.match(/\d+/)
                if (scoreMatch) currentJob.matchScore = parseInt(scoreMatch[0])
            }
            if (line.includes('[Lien vers l\'offre](')) {
                const urlMatch = line.match(/\((.*?)\)/)
                if (urlMatch) currentJob.rawUrl = urlMatch[1]
            }
            if (line.trim() && !line.startsWith('**') && !line.startsWith('[')) {
                currentJob.desc += line + " "
            }
        }
    }
    
    if (currentJob) parsedJobs.push(currentJob)
    return parsedJobs
}

const performSearch = async () => {
    if (!searchQuery.value.trim()) return
    
    isLoading.value = true
    jobs.value = [] // Clear previous results
    
    try {
        const res = await authFetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                message: searchQuery.value, 
                cv_text: cvText.value, 
                cv_filename: selectedFileName.value,
                nb_results: resultLimit.value,
                location: inputLocation.value
            })
        })
        const json = await res.json()
        
        if (json.status === 'error' && json.type === 'limit_reached') {
            toastState.addToast(json.content, "warning")
            isLoading.value = false
            return
        }

        // The orchestrator returns { status: "success", type: "job_search_results", content: { matched_jobs: [] } }
        let rawJobs = []
        if (json.data && json.data.content && json.data.content.matched_jobs) {
             rawJobs = json.data.content.matched_jobs
        } else if (json.data && Array.isArray(json.data.content)) {
             rawJobs = json.data.content
        } else if (json.data && Array.isArray(json.data)) {
             rawJobs = json.data 
        }

        // Map the backend fields to the UI expected fields
        jobs.value = rawJobs.map(job => ({
             id: job.id || Math.random().toString(36).substr(2, 9),
             title: job.title || t('common.not_specified') || 'Non spécifié',
             company: job.company || t('common.not_specified') || 'Non spécifié',
             location: job.location || t('common.not_specified') || 'Non spécifié',
             matchScore: job.match_score || 0,
             salary: job.salary || t('common.not_specified') || 'Non spécifié',
             type: job.type || t('opportunities.job_stage') || 'Emploi / Stage',
             posted: job.posted_date || t('opportunities.recent') || 'Récent',
             desc: job.description || job.snippet || t('opportunities.no_desc') || 'Aucune description fournie.',
             rawUrl: job.url || ''
        }))
        
    } catch(e) {
        toastState.addToast(t('opportunities.search_error') || "Erreur de connexion avec le Serveur de Recherche GoldArmy.", "error")
        console.error(e)
    } finally {
        isLoading.value = false
        isUploading.value = false // Hide CV form after search
    }
}


const openAdaptCvModal = (job) => {
  adaptCvCard.value = job
  cvTextForAdapt.value = ''
  adaptedData.value = null
  showAdaptCvModal.value = true
  showDownloadCvModal.value = false
}

const useProfileCv = async () => {
  if (!adaptCvCard.value) return
  try {
    const res = await authFetch('/api/profile')
    const json = await res.json()
    const cvText = json?.data?.cv_text
    if (!cvText || cvText.length < 50) {
      toastState.addToast('Aucun CV enregistré dans votre profil. Uploadez un CV d\'abord.', 'info')
      return
    }
    cvTextForAdapt.value = cvText
    await runAdapt()
  } catch (e) {
    toastState.addToast(t('common.network_error'), 'error')
  }
}

const onAdaptFileSelected = async (e) => {
  const file = e.target?.files?.[0]
  if (!file || !file.name.toLowerCase().endsWith('.pdf')) {
    toastState.addToast('Veuillez sélectionner un fichier PDF.', 'info')
    return
  }
  const formData = new FormData()
  formData.append('file', file)
  try {
    const res = await authFetch('/api/parse-pdf', { method: 'POST', body: formData })
    const json = await res.json()
    const text = json?.text
    if (!text || text.length < 50) {
      toastState.addToast('Impossible de lire le PDF ou fichier trop court.', 'error')
      return
    }
    cvTextForAdapt.value = text
    await runAdapt()
  } catch (err) {
    toastState.addToast(t('common.network_error'), 'error')
  }
  e.target.value = ''
}

const runAdapt = async () => {
  if (!adaptCvCard.value || !cvTextForAdapt.value || cvTextForAdapt.value.length < 50) {
    toastState.addToast('CV manquant ou trop court.', 'info')
    return
  }
  isAdaptingCv.value = true
  try {
    const res = await authFetch('/api/adapt-cv', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        job_title: adaptCvCard.value.title,
        job_description: adaptCvCard.value.desc,
        cv_text: cvTextForAdapt.value
      })
    })
    const json = await res.json()
    if (json.status === 'success' && json.data) {
      adaptedData.value = json.data
      showAdaptCvModal.value = false
      showDownloadCvModal.value = true
      selectedCvTheme.value = 'goldarmy'
    } else {
      toastState.addToast(json.detail || t('opportunities.adapt_error') || "Erreur lors de l'adaptation.", 'error')
    }
  } catch (e) {
    toastState.addToast(t('common.network_error'), 'error')
  } finally {
    isAdaptingCv.value = false
  }
}

const closeAdaptCvModal = () => {
  showAdaptCvModal.value = false
  adaptCvCard.value = null
  cvTextForAdapt.value = ''
  adaptedData.value = null
}

const buildCvJsonFromMarkdown = (markdown) => {
  const lines = (markdown || '').split(/\n/).filter(Boolean)
  const fullName = lines[0]?.replace(/^#+\s*/, '').trim() || 'Candidat'
  return {
    full_name: fullName,
    summary: '',
    experiences: [{ title: 'Expérience professionnelle', company: '', start_date: '', end_date: '', bullets: lines }],
    skills: {},
    education: []
  }
}

const downloadAdaptedPdf = async () => {
  if (!adaptedData.value?.markdown && !adaptedData.value?.cv_json) return
  isDownloadingPdf.value = true
  try {
    let cvJson = null;
    if (adaptedData.value.cv_json) {
        if (typeof adaptedData.value.cv_json === 'object') {
            cvJson = adaptedData.value.cv_json;
        } else if (typeof adaptedData.value.cv_json === 'string') {
            try {
                cvJson = JSON.parse(adaptedData.value.cv_json);
            } catch (e) {
                console.warn("Failed to parse cv_json string, falling back to markdown", e);
            }
        }
    }
    
    if (!cvJson) {
        cvJson = buildCvJsonFromMarkdown(adaptedData.value.markdown || '');
    }

    const filename = `CV_Adapte_${(adaptCvCard.value?.title || 'offre').replace(/\s+/g, '_').slice(0, 30)}`

    // Use the mobile-identical JS templates for consistent design
    const tpl = CV_THEMES.find(t => t.id === selectedCvTheme.value) || CV_THEMES[0]
    const html = tpl.build(cvJson, null)

    const res = await authFetch('/api/generate-cv-pdf-html', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ html, filename })
    })
    if (!res.ok) {
      const err = await res.json()
      toastState.addToast(err.detail || 'Erreur génération PDF', 'error')
      return
    }
    const blob = await res.blob()
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = filename + '.pdf'
    a.click()
    URL.revokeObjectURL(url)
    toastState.addToast('CV téléchargé.', 'success')
    showDownloadCvModal.value = false
    adaptedData.value = null
  } catch (e) {
    toastState.addToast('Erreur lors du téléchargement.', 'error')
  } finally {
    isDownloadingPdf.value = false
  }
}

const closeDownloadCvModal = () => {
  showDownloadCvModal.value = false
  adaptedData.value = null
}

const runRadar = async (job) => {
    loadingRadarFor.value = job.id
    try {
        const res = await authFetch('/api/radar', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ company_name: job.company, job_title: job.title })
        })
        const json = await res.json()
        const data = json.data
        toastState.addToast(`RADAR INSIGHTS : ${job.company}\n🎯 Réputation: ${data.reputation.substring(0, 50)}...\n💰 Salaire: ${data.salary.substring(0, 50)}...`, "info")
    } catch(e) {
        toastState.addToast("Erreur lors de l'appel au Radar.", "error")
    } finally {
        loadingRadarFor.value = null
    }
}

const addToCrmAndApply = async (job) => {
    try {
        // 1. Enregistrer dans le CRM
        await authFetch('/api/crm', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                job_title: job.title,
                company_name: job.company,
                url: job.rawUrl,
                status: 'TO_APPLY',
                notes: job.desc && job.desc.length > 200 ? job.desc.substring(0, 200) + '...' : job.desc
            })
        });
        toastState.addToast(t('common.success'), "success")
        
        // 2. Ouvrir le lien dans un nouvel onglet
        if (job.rawUrl) {
            window.open(job.rawUrl, '_blank', 'noopener,noreferrer');
        }
    } catch (e) {
        console.error("Erreur ajout CRM :", e);
        // Fallback: ouvrir quand même le lien
        if (job.rawUrl) {
            window.open(job.rawUrl, '_blank', 'noopener,noreferrer');
        }
    }
}
</script>

<template>
  <div class="db-root animate-fade-in-up">
    
    <!-- HEADER (Uniform with Dashboard) -->
    <div class="db-header">
       <div class="header-date-box">
           <div class="date-num flex items-center justify-center bg-[#E85D3E]/10 rounded-lg w-10 h-10"><SignalIcon class="w-6 h-6 text-[#E85D3E]" /></div>
           <div class="date-str">{{ t('opportunities.tagline') }}</div>
           <div class="date-divider"></div>
           <div class="flex items-center gap-2">
               <span class="text-xs font-bold text-slate-400 uppercase tracking-widest">{{ t('opportunities.max_results') }}</span>
               <select v-model="resultLimit" @change="performSearch" class="bg-slate-100 text-slate-900 focus:outline-none focus:ring-0 cursor-pointer px-2 py-1 rounded-lg font-bold appearance-none text-xs border border-slate-200">
                 <option :value="10">10</option>
                 <option :value="20">20</option>
                 <option :value="50">50</option>
                 <option :value="100">100</option>
                 <option :value="150">150</option>
                 <option :value="200">200</option>
               </select>
           </div>
       </div>
       
       <div class="header-greeting flex-1">
           <div class="greeting-text">
             <div class="flex items-center gap-3">
                 {{ t('opportunities.title_sniper') }} 
                 <span class="text-[#E85D3E]">{{ t('opportunities.title_recruitment') }}</span>
                 <img src="/logo.png" alt="Logo" class="w-10 h-10 animate-float ml-auto md:ml-4" />
             </div>
             <span class="greeting-sub text-sm md:text-lg block mt-1">{{ t('opportunities.description') }}</span>
           </div>
       </div>
    </div>

    <!-- MAIN SEARCH ENGINE (Uniform Clean Style) -->
    <div class="bg-white border border-slate-200 p-4 md:p-6 rounded-[2rem] shadow-sm mb-8 relative overflow-hidden">
        <div class="relative z-10">
            <div class="flex flex-col lg:flex-row gap-4">
                <!-- Search Inputs: Keyword + Location -->
                <div class="flex-1 flex flex-col md:flex-row gap-0 group bg-slate-50 border border-slate-200 rounded-2xl focus-within:border-[#E85D3E]/50 transition-colors relative">
                    <div class="absolute inset-0 bg-gradient-to-r from-gold-500 to-amber-500 rounded-2xl blur opacity-0 group-focus-within:opacity-20 transition-opacity duration-500 pointer-events-none"></div>
                    
                    <!-- Keyword -->
                    <div class="relative flex-1 flex items-center h-16 w-full border-b md:border-b-0 md:border-r border-slate-200">
                        <MagnifyingGlassIcon class="absolute left-5 w-6 h-6 text-slate-400 group-focus-within:text-[#E85D3E] transition-colors" />
                        <input 
                            v-model="searchQuery"
                            @keyup.enter="performSearch"
                            type="text" 
                            :placeholder="t('opportunities.search_placeholder')"
                            class="w-full pl-14 pr-4 py-4 bg-transparent text-slate-900 focus:outline-none text-lg placeholder-slate-400 font-medium rounded-l-2xl z-10"
                        />
                    </div>

                    <!-- Location -->
                    <div class="relative flex-[0.7] flex items-center h-16 w-full">
                        <MapPinIcon class="absolute left-5 w-6 h-6 text-slate-400 group-focus-within:text-[#E85D3E] transition-colors" />
                        <input 
                            v-model="inputLocation"
                            @keyup.enter="performSearch"
                            type="text" 
                            :placeholder="t('opportunities.location_placeholder')"
                            class="w-full pl-14 pr-4 py-4 bg-transparent text-slate-900 focus:outline-none text-lg placeholder-slate-400 font-medium rounded-r-2xl z-10"
                        />
                    </div>
                </div>
                
                <!-- Actions -->
                <div class="flex gap-3 shrink-0">
                    <button 
                        @click="isUploading = !isUploading"
                        :class="cvText ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30' : 'bg-surface-800 text-slate-300 border-slate-200 hover:border-slate-500 hover:bg-surface-700'"
                        class="px-6 h-16 rounded-2xl flex items-center justify-center gap-2 border font-bold transition-all w-full lg:w-auto overflow-hidden relative group/btn"
                    >
                        <!-- Sparkle effect for CV ready -->
                        <div v-if="cvText" class="absolute inset-0 bg-gradient-to-r from-emerald-400/0 via-emerald-400/20 to-emerald-400/0 translate-x-[-100%] group-hover/btn:translate-x-[100%] transition-transform duration-1000"></div>
                        
                        <DocumentTextIcon class="w-6 h-6" :class="cvText ? 'text-emerald-400' : 'text-slate-400'" />
                        <span class="hidden md:inline">{{ cvText ? t('opportunities.cv_profiled') : t('opportunities.attach_cv') }}</span>
                    </button>
                    
                    <button 
                        @click="performSearch"
                        :disabled="!searchQuery || isLoading"
                        class="px-8 h-16 bg-[#E85D3E] hover:opacity-90 disabled:opacity-50 disabled:grayscale text-white font-bold tracking-tight rounded-2xl transition-all shadow-lg shadow-[#E85D3E]/20 flex items-center justify-center min-w-[160px] group/launch"
                    >
                        <span v-if="!isLoading" class="flex items-center gap-2">
                            {{ t('opportunities.launch_button') }}
                            <svg class="w-5 h-5 -mr-1 group-hover/launch:translate-x-1 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3"/></svg>
                        </span>
                        <div v-else class="flex gap-2">
                             <span class="w-2 h-2 rounded-full bg-surface-950 animate-bounce" style="animation-delay: 0ms"></span>
                             <span class="w-2 h-2 rounded-full bg-surface-950 animate-bounce" style="animation-delay: 150ms"></span>
                             <span class="w-2 h-2 rounded-full bg-surface-950 animate-bounce" style="animation-delay: 300ms"></span>
                        </div>
                    </button>
                </div>
            </div>
            
            <!-- CV Upload Expansion (Smooth transition) -->
            <transition
                enter-active-class="transition duration-300 ease-out origin-top"
                enter-from-class="transform scale-y-95 opacity-0 max-h-0"
                enter-to-class="transform scale-y-100 opacity-100 max-h-[400px]"
                leave-active-class="transition duration-200 ease-in origin-top"
                leave-from-class="transform scale-y-100 opacity-100 max-h-[400px]"
                leave-to-class="transform scale-y-95 opacity-0 max-h-0"
            >
                <div v-if="isUploading" class="pt-6 mt-6 border-t border-slate-100">
                    <div 
                        @click="triggerFileInput"
                        class="w-full border-2 border-dashed border-slate-200 hover:border-gold-500/50 bg-gradient-to-b from-surface-900 to-surface-800/50 rounded-2xl p-10 flex flex-col items-center justify-center cursor-pointer transition-all group"
                    >
                        <input type="file" ref="fileInput" accept=".pdf" class="hidden" @change="handleFileUpload" />
                        
                        <div v-if="isParsingPdf" class="flex flex-col items-center">
                            <ArrowPathIcon class="w-10 h-10 text-gold-500 animate-spin mb-4" />
                            <p class="text-gold-400 font-bold tracking-tight">{{ t('opportunities.parsing_profile') }}</p>
                        </div>
                        <div v-else-if="selectedFileName" class="flex flex-col items-center gap-3">
                            <div class="w-16 h-16 rounded-full bg-emerald-500/10 flex items-center justify-center">
                                <CheckCircleIcon class="w-8 h-8 text-emerald-500" />
                            </div>
                            <div class="text-center">
                                <p class="text-slate-900 font-bold text-lg">{{ selectedFileName }}</p>
                                <p class="text-slate-400 text-sm mt-1">{{ t('opportunities.cv_ready_desc') }}</p>
                            </div>
                        </div>
                        <div v-else class="flex flex-col items-center">
                            <div class="p-5 bg-surface-800 rounded-full group-hover:bg-gold-500/10 mb-4 transition-colors ring-1 ring-surface-700 group-hover:ring-gold-500/30">
                                <DocumentTextIcon class="w-10 h-10 text-slate-400 group-hover:text-gold-400 transition-colors" />
                            </div>
                            <h3 class="text-slate-900 font-bold text-lg">{{ t('opportunities.upload_cv_title') }}</h3>
                            <p class="text-slate-500 text-sm mt-2 text-center max-w-sm">
                                {{ t('opportunities.upload_cv_desc') }}
                            </p>
                        </div>
                    </div>
                </div>
            </transition>
        </div>
    </div>

    <!-- Empty / Loading States -->
    <div v-if="isLoading" class="flex flex-col items-center justify-center py-32">
        <div class="relative w-24 h-24 mb-8">
            <div class="absolute inset-0 rounded-full border-t-2 border-gold-500 animate-spin"></div>
            <div class="absolute inset-2 rounded-full border-r-2 border-amber-400 animate-spin" style="animation-direction: reverse; animation-duration: 1.5s;"></div>
            <div class="absolute inset-0 flex items-center justify-center">
                <span class="text-2xl">🪖</span>
            </div>
        </div>
        <h3 class="text-2xl font-display font-bold text-slate-900 mb-3 tracking-tight">{{ t('opportunities.analyzing_market') }}</h3>
        <p class="text-slate-400 text-center max-w-md text-sm leading-relaxed">
            {{ t('opportunities.analyzing_market_desc') }}
        </p>
    </div>
    
    <div v-else-if="jobs.length === 0 && !isLoading" class="flex flex-col items-center justify-center py-24 bg-white rounded-[2rem] border-dashed border-2 border-slate-200">
        <div class="p-6 bg-slate-50 rounded-full mb-6 ring-1 ring-slate-100">
            <BriefcaseIcon class="w-12 h-12 text-slate-500" />
        </div>
        <h3 class="text-2xl font-display font-bold text-slate-900 mb-2 tracking-tight">{{ t('opportunities.no_opportunities') }}</h3>
        <p class="text-slate-500 text-center">{{ t('opportunities.no_opportunities_desc') }}</p>
    </div>

    <!-- Job Cards List (Premium SaaS Style) -->
    <div v-else class="grid grid-cols-1 lg:grid-cols-2 gap-6 pb-20">
       <div 
         v-for="(job, index) in filteredJobs" 
         :key="job.id"
         class="relative bg-white border border-slate-200 p-6 rounded-3xl transition-all hover:border-[#E85D3E] hover:shadow-md group flex flex-col justify-between overflow-hidden"
         :style="`animation-delay: ${index * 50}ms`"
         style="animation: fadeInUp 0.5s ease-out forwards; opacity: 0;"
       >
          <!-- Subtle glow effect on hover -->
          <div class="absolute inset-0 bg-gradient-to-br from-gold-500/0 to-amber-500/0 group-hover:from-gold-500/5 group-hover:to-amber-500/5 transition-colors pointer-events-none"></div>

          <div class="relative z-10">
              <!-- Header Card -->
              <div class="flex items-start justify-between gap-4 mb-5">
                  <div class="flex-1 min-w-0">
                      <!-- Tags -->
                      <div class="flex flex-wrap gap-2 mb-4">
                        <span class="text-[10px] font-black uppercase tracking-wider text-[#E85D3E] bg-[#E85D3E]/10 border border-[#E85D3E]/20 px-3 py-1.5 rounded-xl">
                            {{ job.type }}
                        </span>
                        <span class="text-xs font-semibold text-slate-300 bg-surface-800 border border-slate-200 px-3 py-1.5 rounded-xl flex items-center gap-1.5">
                            <MapPinIcon class="w-3.5 h-3.5 text-slate-500" />
                            {{ job.location }}
                        </span>
                      </div>
                      
                      <h3 class="text-2xl font-display font-black text-slate-900 leading-tight mb-2 truncate group-hover:text-[#E85D3E] transition-colors" :title="job.title">
                          {{ job.title }}
                      </h3>
                      <div class="flex items-center gap-2.5 text-slate-400 font-medium">
                          <span class="w-7 h-7 rounded-lg bg-surface-800 flex items-center justify-center text-xs font-bold text-white border border-slate-200 shadow-inner">
                              {{ job.company.charAt(0).toUpperCase() }}
                          </span>
                          <span class="truncate">{{ job.company }}</span>
                      </div>
                  </div>
                  
                  <!-- Circular Progress Score -->
                  <div class="shrink-0 relative w-16 h-16 flex items-center justify-center bg-slate-50 rounded-2xl shadow-inner ring-1 ring-slate-100">
                      <!-- SVG Circle Background -->
                      <svg class="absolute inset-0 w-full h-full transform -rotate-90">
                          <circle cx="50%" cy="50%" r="40%" stroke="currentColor" stroke-width="8%" fill="transparent" class="text-surface-800" />
                          <circle cx="50%" cy="50%" r="40%" stroke="currentColor" stroke-width="8%" fill="transparent" 
                                  :stroke-dasharray="2 * Math.PI * 40" 
                                  :stroke-dashoffset="2 * Math.PI * 40 * (1 - job.matchScore / 100)"
                                  stroke-linecap="round"
                                  :class="job.matchScore >= 80 ? 'text-emerald-500' : (job.matchScore >= 50 ? 'text-gold-500' : 'text-slate-500')"
                                  class="transition-all duration-1000 ease-out" />
                      </svg>
                      <div class="text-center z-10 flex flex-col items-center">
                          <span class="block text-lg font-black leading-none" :class="job.matchScore >= 80 ? 'text-slate-900' : 'text-slate-500'">
                              {{ job.matchScore }}<span class="text-[10px] text-slate-500 font-bold">%</span>
                          </span>
                      </div>
                  </div>
              </div>
              
              <!-- Description Snippet -->
              <p class="text-[13px] text-slate-400 line-clamp-3 leading-relaxed mb-6 font-medium">
                {{ job.desc }}
              </p>
          </div>
          
          <!-- Card Footer Actions -->
          <div class="relative z-10 flex items-center gap-3 pt-5 border-t border-slate-100/80 mt-auto">
             <button 
                v-if="job.rawUrl" 
                @click="addToCrmAndApply(job)"
                class="flex-1 flex items-center justify-center gap-2 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white px-4 py-3.5 rounded-xl font-bold text-sm transition-all shadow-lg shadow-emerald-600/20 active:scale-95 outline-none">
                {{ t('opportunities.apply') }}
             </button>
             <button disabled class="flex-1 bg-surface-800 text-slate-500 px-4 py-3.5 rounded-xl font-bold text-sm cursor-not-allowed" v-else>
                 {{ t('opportunities.dead_link') }}
             </button>
             
             <!-- AI Adapt CV Button -->
             <button 
                @click="openAdaptCvModal(job)"
                class="flex-1 flex items-center justify-center gap-2 bg-gradient-to-r from-[#E85D3E]/10 to-[#E85D3E]/5 hover:from-[#E85D3E]/20 hover:to-[#E85D3E]/10 text-[#E85D3E] px-4 py-3.5 rounded-xl font-bold text-sm transition-all border border-[#E85D3E]/20 hover:border-[#E85D3E]/40 active:scale-95 outline-none group/adapt">
                <SparklesIcon class="w-5 h-5 text-[#E85D3E] group-hover/adapt:scale-110 transition-transform" />
                <span class="hidden sm:inline">{{ t('opportunities.adapt_cv') }}</span>
             </button>
             
             <button 
                @click="runRadar(job)"
                :disabled="loadingRadarFor === job.id"
                class="flex items-center justify-center bg-slate-100 hover:bg-slate-200 disabled:opacity-50 text-slate-600 w-12 h-12 rounded-xl transition-colors border border-slate-200 active:scale-95 outline-none group/radar shrink-0">
                <ArrowPathIcon v-if="loadingRadarFor === job.id" class="w-5 h-5 animate-spin text-gold-400" />
                <svg v-else class="w-5 h-5 text-slate-400 group-hover/radar:text-[#E85D3E] transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
             </button>
          </div>
       </div>
    </div>
    
    
    <!-- ═══ POPUP 1 : Adapter le CV – Choix du CV (upload ou profil) ═══ -->
    <div v-if="showAdaptCvModal" class="fixed inset-0 z-[200] flex items-center justify-center p-4">
      <div class="absolute inset-0 bg-black/70 backdrop-blur-sm" @click="closeAdaptCvModal"></div>
      <div class="relative z-10 bg-surface-900 border border-slate-200 rounded-3xl shadow-2xl w-full max-w-md overflow-hidden" style="animation: scale-in 0.2s ease-out forwards;">
        <div class="px-6 pt-6 pb-4 border-b border-slate-100 flex items-center justify-between">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-xl bg-amber-500/10 flex items-center justify-center">
              <SparklesIcon class="w-5 h-5 text-amber-400" />
            </div>
            <div>
              <h3 class="font-bold text-white">Adapter le CV pour cette offre</h3>
              <p class="text-xs text-slate-500 mt-0.5">{{ adaptCvCard?.title }} — {{ adaptCvCard?.company }}</p>
            </div>
          </div>
          <button @click="closeAdaptCvModal" class="p-1.5 text-slate-500 hover:text-white rounded-lg hover:bg-surface-800"><XMarkIcon class="w-5 h-5" /></button>
        </div>
        <div class="p-6">
          <div v-if="isAdaptingCv" class="flex flex-col items-center py-10 gap-4">
            <ArrowPathIcon class="w-12 h-12 text-amber-500 animate-spin" />
            <p class="text-sm font-bold text-white">Adaptation en cours (conformité ~95% à l'offre)...</p>
          </div>
          <div v-else class="space-y-4">
            <p class="text-sm text-slate-400">Choisissez le CV à adapter :</p>
            <input ref="adaptCvFileInput" type="file" accept=".pdf" class="hidden" @change="onAdaptFileSelected" />
            <button type="button" @click="adaptCvFileInput?.click()" class="w-full flex items-center justify-center gap-3 px-5 py-4 rounded-xl border-2 border-dashed border-surface-600 hover:border-amber-500/50 bg-surface-800/50 text-slate-300 hover:text-amber-400 transition-all">
              <ArrowUpTrayIcon class="w-6 h-6" />
              <span class="font-bold">Uploader un CV (PDF)</span>
            </button>
            <button type="button" @click="useProfileCv" class="w-full flex items-center justify-center gap-3 px-5 py-4 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-400 hover:bg-amber-500/20 transition-all font-bold">
              <DocumentTextIcon class="w-6 h-6" />
              Utiliser le CV du profil
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- ═══ POPUP 2 : Choisir le modèle et télécharger le CV adapté ═══ -->
    <div v-if="showDownloadCvModal" class="fixed inset-0 z-[200] flex items-center justify-center p-4">
      <div class="absolute inset-0 bg-black/70 backdrop-blur-sm" @click="closeDownloadCvModal"></div>
      <div class="relative z-10 bg-surface-900 border border-slate-200 rounded-3xl shadow-2xl w-full max-w-lg overflow-hidden" style="animation: scale-in 0.2s ease-out forwards;">
        <div class="px-6 pt-6 pb-4 border-b border-slate-100 flex items-center justify-between">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-xl bg-emerald-500/10 flex items-center justify-center">
              <DocumentTextIcon class="w-5 h-5 text-emerald-400" />
            </div>
            <div>
              <h3 class="font-bold text-white">Télécharger le CV adapté</h3>
              <p class="text-xs text-slate-500 mt-0.5">Choisissez un modèle puis téléchargez le PDF</p>
            </div>
          </div>
          <button @click="closeDownloadCvModal" class="p-1.5 text-slate-500 hover:text-white rounded-lg hover:bg-surface-800"><XMarkIcon class="w-5 h-5" /></button>
        </div>
        <div class="p-6 space-y-6">
          <div v-if="adaptedData?.markdown" class="max-h-32 overflow-y-auto custom-scrollbar rounded-xl bg-surface-950 border border-slate-100 p-4 text-sm text-slate-400 whitespace-pre-wrap">{{ adaptedData.markdown.slice(0, 400) }}{{ adaptedData.markdown.length > 400 ? '…' : '' }}</div>
          <div>
            <p class="text-xs font-bold text-slate-500 uppercase tracking-wider mb-3">Modèle du CV</p>
            <div class="flex flex-wrap gap-2">
              <button v-for="theme in CV_THEMES" :key="theme.id" type="button" @click="selectedCvTheme = theme.id"
                class="h-10 w-10 rounded-lg border-2 transition-all overflow-hidden shrink-0"
                :class="selectedCvTheme === theme.id ? 'border-amber-500 ring-2 ring-amber-500/30' : 'border-slate-200 hover:border-surface-600'">
                <div class="flex w-full h-full">
                  <div class="w-1/2 h-full" :style="{ backgroundColor: theme.colors[0] }"></div>
                  <div class="w-1/2 h-full" :style="{ backgroundColor: theme.colors[1] }"></div>
                </div>
              </button>
            </div>
            <p class="text-[11px] text-slate-500 mt-2">{{ CV_THEMES.find(th => th.id === selectedCvTheme)?.name }}</p>
          </div>
          <button @click="downloadAdaptedPdf" :disabled="isDownloadingPdf"
            class="w-full flex items-center justify-center gap-2 px-5 py-3.5 bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 disabled:opacity-60 text-surface-950 font-bold rounded-xl shadow-lg transition-all">
            <ArrowUpTrayIcon v-if="!isDownloadingPdf" class="w-5 h-5 rotate-180" />
            <ArrowPathIcon v-else class="w-5 h-5 animate-spin" />
            {{ isDownloadingPdf ? 'Génération…' : 'Télécharger le PDF' }}
          </button>
        </div>
      </div>
    </div>
    
  </div>
</template>

<style scoped>

.db-root { 
    padding: 2rem; 
    max-width: 1500px; 
    margin: 0 auto; 
    display: flex; 
    flex-direction: column; 
    gap: 1.5rem; 
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    background-color: #F9FAFB; 
    min-height: 100vh;
}

.db-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    flex-wrap: wrap;
    gap: 1.5rem;
    background: #FFFFFF;
    padding: 1.5rem;
    border-radius: 1.5rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.02), 0 10px 40px -10px rgba(0,0,0,0.02);
}

.header-date-box {
    display: flex;
    align-items: center;
    background: #F3F4F6;
    padding: 0.5rem 1rem;
    border-radius: 1rem;
    height: 56px;
}

.date-num {
    font-size: 1.5rem;
    font-weight: 800;
    color: #111827;
}

.date-str {
    font-size: 0.85rem;
    font-weight: 600;
    color: #4B5563;
    margin-left: 0.5rem;
}

.date-divider {
    width: 1px;
    height: 30px;
    background-color: #E5E7EB;
    margin: 0 1rem;
}

.header-greeting {
    display: flex;
    align-items: center;
    gap: 1.5rem;
}

.greeting-text {
    font-size: 2rem;
    font-weight: 500;
    color: #111827;
    line-height: 1.1;
    letter-spacing: -0.02em;
}

.greeting-sub {
    color: #9CA3AF;
}

@keyframes floatLogo {
    0%, 100% { transform: translateY(0) scale(1); }
    50% { transform: translateY(-5px) scale(1.05) rotate(3deg); }
}
.animate-float {
    animation: floatLogo 3s ease-in-out infinite;
}

.custom-scrollbar::-webkit-scrollbar { width: 4px; }
.custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: #1e293b; border-radius: 10px; }
.custom-scrollbar::-webkit-scrollbar-thumb:hover { background: #475569; }

@keyframes scale-in {
  from { transform: scale(0.94); opacity: 0; }
  to { transform: scale(1); opacity: 1; }
}
</style>

