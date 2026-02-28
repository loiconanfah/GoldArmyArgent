<script setup>
import { authFetch } from '../utils/auth'
import { toastState } from '../store/toastState'

import { ref, computed, onMounted } from 'vue'
import { 
    BriefcaseIcon, 
    FunnelIcon, 
    MapPinIcon, 
    CurrencyDollarIcon, 
    CheckCircleIcon,
    MagnifyingGlassIcon,
    DocumentTextIcon,
    ArrowPathIcon,
    SparklesIcon
} from '@heroicons/vue/24/outline'
import { toRefs } from 'vue'
import { sniperState } from '../store/sniperState'

const {
    filter, searchQuery, inputLocation, cvText, isUploading, isLoading, isParsingPdf, 
    jobs, selectedFileName, resultLimit, showAdaptModal, isAdaptingCV, 
    adaptingJobId, adaptedData, loadingRadarFor
} = toRefs(sniperState)

const fileInput = ref(null)

const triggerFileInput = () => {
    fileInput.value?.click()
}

const handleFileUpload = async (event) => {
    const file = event.target.files[0]
    if (!file) return
    
    if (file.type !== 'application/pdf') {
        toastState.addToast("Veuillez sélectionner un fichier PDF.", "error")
        return
    }
    
    selectedFileName.value = file.name
    isParsingPdf.value = true
    cvText.value = "" // Reset old cv text
    
    const formData = new FormData()
    formData.append('file', file)
    
    try {
        const res = await authFetch('http://localhost:8000/api/parse-pdf', {
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
             toastState.addToast(json.detail || "Erreur lors de la lecture du PDF.", "error")
             selectedFileName.value = ""
        }
    } catch(e) {
        toastState.addToast("Erreur réseau lors de l'envoi du CV.", "error")
        selectedFileName.value = ""
        console.error(e)
    } finally {
        isParsingPdf.value = false
    }
}

const filteredJobs = computed(() => {
    if (filter.value === 'Toutes les pertinentes') return jobs.value;
    return jobs.value.filter(job => {
        if (filter.value === 'Stages Uniquement') return job.type.toLowerCase().includes('stage') || job.title.toLowerCase().includes('stage') || job.title.toLowerCase().includes('intern')
        if (filter.value === 'Juniors (< 2 ans)') return job.type.toLowerCase().includes('junior') || job.title.toLowerCase().includes('junior')
        if (filter.value === 'Score > 80%') return job.matchScore > 80
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
                company: 'Non spécifié',
                location: 'Non spécifié',
                matchScore: 0,
                salary: 'Variable',
                type: 'Emploi / Stage',
                posted: "Récent",
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
        const res = await authFetch('http://localhost:8000/api/chat', {
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
             title: job.title || 'Non spécifié',
             company: job.company || 'Non spécifié',
             location: job.location || 'Non spécifié',
             matchScore: job.match_score || 0,
             salary: job.salary || 'Non spécifié',
             type: job.type || 'Emploi / Stage',
             posted: job.posted_date || 'Récent',
             desc: job.description || job.snippet || 'Aucune description fournie.',
             rawUrl: job.url || ''
        }))
        
    } catch(e) {
        toastState.addToast("Erreur de connexion avec le Serveur de Recherche GoldArmy.", "error")
        console.error(e)
    } finally {
        isLoading.value = false
        isUploading.value = false // Hide CV form after search
    }
}

const adaptCV = async (job) => {
    if (!cvText.value) {
        toastState.addToast("Veuillez d'abord télécharger/coller votre CV dans la section ci-dessus avant d'adapter.", "info");
        return;
    }

    adaptingJobId.value = job.id;
    isAdaptingCV.value = true;
    showAdaptModal.value = true;
    adaptedData.value = null;
    
    try {
        const res = await authFetch('http://localhost:8000/api/adapt-cv', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                job_title: job.title,
                job_description: job.desc,
                cv_text: cvText.value
            })
        });
        
        const json = await res.json();
        
        if (json.status === "success" && json.data) {
            adaptedData.value = json.data;
        } else {
            toastState.addToast("Erreur lors de l'adaptation du CV.", "error");
            showAdaptModal.value = false;
        }
    } catch(e) {
        console.error("Adapt CV Error:", e);
        toastState.addToast("Impossible de contacter le serveur d'intelligence.", "error");
        showAdaptModal.value = false;
    } finally {
        isAdaptingCV.value = false;
    }
}

const isSavingToProfile = ref(false)
const saveAdaptedToProfile = async () => {
    if (!adaptedData.value || !adaptedData.value.markdown) return
    isSavingToProfile.value = true
    try {
        const res = await authFetch('http://localhost:8000/api/profile', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                cv_text: adaptedData.value.markdown 
            })
        })
        const json = await res.json()
        if (json.status === 'success') {
            toastState.addToast("Ce CV a été enregistré comme votre CV principal dans votre profil !")
        } else {
            toastState.addToast("Erreur lors de l'enregistrement : " + (json.detail || "Inconnu"), "error")
        }
    } catch(e) {
        console.error("Save Profile Error:", e)
        toastState.addToast("Erreur de connexion.", "error")
    } finally {
        isSavingToProfile.value = false
    }
}

const closeAdaptModal = () => {
    showAdaptModal.value = false;
    adaptedData.value = null;
    adaptingJobId.value = null;
    isAdaptingCV.value = false;
}

const runRadar = async (job) => {
    loadingRadarFor.value = job.id
    try {
        const res = await authFetch('http://localhost:8000/api/radar', {
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
        await authFetch('http://localhost:8000/api/crm', {
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
  <div class="px-4 md:px-10 py-8 max-w-[1400px] mx-auto w-full animate-fade-in-up">
    
    <!-- Title & Filters Header -->
    <div class="flex flex-col lg:flex-row lg:items-end justify-between gap-6 mb-8 pt-4">
       <div class="relative z-10">
         <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-gold-400/10 border border-gold-400/20 text-gold-400 text-xs font-bold tracking-wider uppercase mb-3">
             <span class="relative flex h-2 w-2">
                <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-gold-400 opacity-75"></span>
                <span class="relative inline-flex rounded-full h-2 w-2 bg-gold-500"></span>
             </span>
             Radar Actif
         </div>
         <h1 class="text-4xl md:text-5xl font-display font-black text-white tracking-tight flex items-center gap-4">
           Sniper 
           <span class="text-transparent bg-clip-text bg-gradient-to-r from-gold-400 to-amber-600">Opportunités</span>
         </h1>
         <p class="text-slate-400 mt-2 text-lg font-medium max-w-xl">
           Scraping intelligent du marché en temps réel et matching contextuel avec votre profil.
         </p>
       </div>
       
       <div class="flex flex-col sm:flex-row gap-3 relative z-10">
           <!-- Filters Container (Solid) -->
           <div class="flex items-center gap-2 bg-surface-900 border border-surface-800 p-1.5 rounded-xl shadow-sm">
              <div class="p-2 bg-surface-800 rounded-lg">
                  <FunnelIcon class="w-4 h-4 text-gold-400" />
              </div>
              <select v-model="filter" class="bg-transparent text-white focus:outline-none focus:ring-0 cursor-pointer pr-4 font-semibold appearance-none text-sm group">
                <option class="text-slate-900">Toutes les pertinentes</option>
                <option class="text-slate-900">Stages Uniquement</option>
                <option class="text-slate-900">Juniors (< 2 ans)</option>
                <option class="text-slate-900">Score > 80%</option>
              </select>
           </div>
           
           <!-- Limit Container (Solid) -->
           <div class="flex items-center gap-2 bg-surface-900 border border-surface-800 p-1.5 rounded-xl shadow-sm">
              <span class="text-slate-400 ml-3 text-sm font-medium">Résultats max:</span>
              <select v-model="resultLimit" @change="performSearch" class="bg-transparent text-white focus:outline-none focus:ring-0 cursor-pointer pr-4 font-bold appearance-none text-sm border-l border-surface-700/50 pl-2">
                <option class="text-slate-900" :value="5">5</option>
                <option class="text-slate-900" :value="10">10</option>
                <option class="text-slate-900" :value="15">15</option>
                <option class="text-slate-900" :value="20">20</option>
                <option class="text-slate-900" :value="30">30</option>
                <option class="text-slate-900" :value="40">40</option>
              </select>
           </div>
       </div>
    </div>

    <!-- MAIN SEARCH ENGINE (Hero Bento Solid) -->
    <div class="bg-surface-900 border border-surface-800 p-2 md:p-3 rounded-3xl shadow-sm mb-12 relative overflow-hidden">
        
        <div class="bg-surface-950 rounded-2xl p-4 md:p-6 border border-surface-800 relative z-10">
            <div class="flex flex-col lg:flex-row gap-4">
                <!-- Search Inputs: Keyword + Location -->
                <div class="flex-1 flex flex-col md:flex-row gap-0 group bg-surface-900 border border-surface-700 rounded-2xl focus-within:border-gold-500/50 transition-colors relative">
                    <div class="absolute inset-0 bg-gradient-to-r from-gold-500 to-amber-500 rounded-2xl blur opacity-0 group-focus-within:opacity-20 transition-opacity duration-500 pointer-events-none"></div>
                    
                    <!-- Keyword -->
                    <div class="relative flex-1 flex items-center h-16 w-full border-b md:border-b-0 md:border-r border-surface-700">
                        <MagnifyingGlassIcon class="absolute left-5 w-6 h-6 text-slate-500 group-focus-within:text-gold-400 transition-colors" />
                        <input 
                            v-model="searchQuery"
                            @keyup.enter="performSearch"
                            type="text" 
                            placeholder="Ex: Stage Ingénieur Logiciel..."
                            class="w-full pl-14 pr-4 py-4 bg-transparent text-white focus:outline-none text-lg placeholder-slate-600 font-medium rounded-l-2xl z-10"
                        />
                    </div>

                    <!-- Location -->
                    <div class="relative flex-[0.7] flex items-center h-16 w-full">
                        <MapPinIcon class="absolute left-5 w-6 h-6 text-slate-500 group-focus-within:text-gold-400 transition-colors" />
                        <input 
                            v-model="inputLocation"
                            @keyup.enter="performSearch"
                            type="text" 
                            placeholder="Localisation (ex: Montréal, QC)"
                            class="w-full pl-14 pr-4 py-4 bg-transparent text-white focus:outline-none text-lg placeholder-slate-600 font-medium rounded-r-2xl z-10"
                        />
                    </div>
                </div>
                
                <!-- Actions -->
                <div class="flex gap-3 shrink-0">
                    <button 
                        @click="isUploading = !isUploading"
                        :class="cvText ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30' : 'bg-surface-800 text-slate-300 border-surface-700 hover:border-slate-500 hover:bg-surface-700'"
                        class="px-6 h-16 rounded-2xl flex items-center justify-center gap-2 border font-bold transition-all w-full lg:w-auto overflow-hidden relative group/btn"
                    >
                        <!-- Sparkle effect for CV ready -->
                        <div v-if="cvText" class="absolute inset-0 bg-gradient-to-r from-emerald-400/0 via-emerald-400/20 to-emerald-400/0 translate-x-[-100%] group-hover/btn:translate-x-[100%] transition-transform duration-1000"></div>
                        
                        <DocumentTextIcon class="w-6 h-6" :class="cvText ? 'text-emerald-400' : 'text-slate-400'" />
                        <span class="hidden md:inline">{{ cvText ? 'CV Profilé' : 'Joindre CV' }}</span>
                    </button>
                    
                    <button 
                        @click="performSearch"
                        :disabled="!searchQuery || isLoading"
                        class="px-8 h-16 bg-gradient-to-r from-gold-500 to-amber-600 hover:from-gold-400 hover:to-amber-500 disabled:opacity-50 disabled:grayscale text-surface-950 font-black tracking-tight rounded-2xl transition-all shadow-[0_0_20px_rgba(245,158,11,0.3)] hover:shadow-[0_0_30px_rgba(245,158,11,0.5)] flex items-center justify-center min-w-[160px] group/launch"
                    >
                        <span v-if="!isLoading" class="flex items-center gap-2">
                            Lancer Sniper
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
                <div v-if="isUploading" class="pt-6 mt-6 border-t border-surface-800">
                    <div 
                        @click="triggerFileInput"
                        class="w-full border-2 border-dashed border-surface-700 hover:border-gold-500/50 bg-gradient-to-b from-surface-900 to-surface-800/50 rounded-2xl p-10 flex flex-col items-center justify-center cursor-pointer transition-all group"
                    >
                        <input type="file" ref="fileInput" accept=".pdf" class="hidden" @change="handleFileUpload" />
                        
                        <div v-if="isParsingPdf" class="flex flex-col items-center">
                            <ArrowPathIcon class="w-10 h-10 text-gold-500 animate-spin mb-4" />
                            <p class="text-gold-400 font-bold tracking-tight">Analyse du Profil en cours...</p>
                        </div>
                        <div v-else-if="selectedFileName" class="flex flex-col items-center gap-3">
                            <div class="w-16 h-16 rounded-full bg-emerald-500/10 flex items-center justify-center">
                                <CheckCircleIcon class="w-8 h-8 text-emerald-500" />
                            </div>
                            <div class="text-center">
                                <p class="text-white font-bold text-lg">{{ selectedFileName }}</p>
                                <p class="text-slate-400 text-sm mt-1">CV prêt à être matché. Clique pour modifier.</p>
                            </div>
                        </div>
                        <div v-else class="flex flex-col items-center">
                            <div class="p-5 bg-surface-800 rounded-full group-hover:bg-gold-500/10 mb-4 transition-colors ring-1 ring-surface-700 group-hover:ring-gold-500/30">
                                <DocumentTextIcon class="w-10 h-10 text-slate-400 group-hover:text-gold-400 transition-colors" />
                            </div>
                            <h3 class="text-white font-bold text-lg">Uploader votre CV (.pdf)</h3>
                            <p class="text-slate-500 text-sm mt-2 text-center max-w-sm">
                                L'IA GoldArmy analysera vos compétences pour calculer un Matching Score précis pour chaque offre.
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
        <h3 class="text-2xl font-display font-bold text-white mb-3 tracking-tight">Analyse du Marché...</h3>
        <p class="text-slate-400 text-center max-w-md text-sm leading-relaxed">
            Recherche via de multiples fournisseurs, filtrage du bruit, et calcul du matching neuronal avec votre profil CV.
        </p>
    </div>
    
    <div v-else-if="jobs.length === 0 && !isLoading" class="flex flex-col items-center justify-center py-24 bg-surface-900/50 rounded-[2rem] border-dashed border-2 border-surface-800">
        <div class="p-6 bg-surface-800 rounded-full mb-6 ring-1 ring-surface-700">
            <BriefcaseIcon class="w-12 h-12 text-slate-500" />
        </div>
        <h3 class="text-2xl font-display font-bold text-white mb-2 tracking-tight">Aucune opportunité détectée</h3>
        <p class="text-slate-500 text-center">Renseignez vos critères de recherche ci-dessus pour lancer le Sniper.</p>
    </div>

    <!-- Job Cards List (Bento Box style Solid) -->
    <div v-else class="grid grid-cols-1 xl:grid-cols-2 gap-6 pb-20">
       <div 
         v-for="(job, index) in filteredJobs" 
         :key="job.id"
         class="bg-surface-900 border border-surface-800 p-6 rounded-3xl transition-all hover:bg-surface-800 hover:border-surface-700 shadow-sm group flex flex-col justify-between"
         :style="`animation-delay: ${index * 50}ms`"
         style="animation: fadeInUp 0.5s ease-out forwards; opacity: 0;"
       >
          <div>
              <!-- Header Card -->
              <div class="flex items-start justify-between gap-4 mb-5">
                  <div class="flex-1 min-w-0">
                      <!-- Tags -->
                      <div class="flex flex-wrap gap-2 mb-3">
                        <span class="text-[10px] font-black uppercase tracking-wider text-gold-400 bg-gold-400/10 border border-gold-400/20 px-2.5 py-1 rounded-lg">
                            {{ job.type }}
                        </span>
                        <span class="text-xs font-semibold text-slate-300 bg-surface-800 border border-surface-700 px-2.5 py-1 rounded-lg flex items-center gap-1">
                            <MapPinIcon class="w-3.5 h-3.5 text-slate-500" />
                            {{ job.location }}
                        </span>
                      </div>
                      
                      <h3 class="text-2xl font-display font-bold text-white leading-tight mb-2 truncate group-hover:text-gold-400 transition-colors" :title="job.title">
                          {{ job.title }}
                      </h3>
                      <div class="flex items-center gap-2 text-slate-400 font-medium">
                          <span class="w-6 h-6 rounded bg-gradient-to-br from-surface-700 to-surface-800 flex items-center justify-center text-xs text-white border border-surface-600">
                              {{ job.company.charAt(0).toUpperCase() }}
                          </span>
                          <span class="truncate">{{ job.company }}</span>
                      </div>
                  </div>
                  
                  <!-- Circular Progress Score -->
                  <div class="shrink-0 relative w-16 h-16 md:w-20 md:h-20 flex items-center justify-center bg-surface-900 rounded-full shadow-inner ring-1 ring-surface-700/50">
                      <!-- SVG Circle Background -->
                      <svg class="absolute inset-0 w-full h-full transform -rotate-90">
                          <circle cx="50%" cy="50%" r="42%" stroke="currentColor" stroke-width="6%" fill="transparent" class="text-surface-800" />
                          <circle cx="50%" cy="50%" r="42%" stroke="currentColor" stroke-width="6%" fill="transparent" 
                                  :stroke-dasharray="2 * Math.PI * 42" 
                                  :stroke-dashoffset="2 * Math.PI * 42 * (1 - job.matchScore / 100)"
                                  stroke-linecap="round"
                                  :class="job.matchScore >= 80 ? 'text-emerald-500' : (job.matchScore >= 50 ? 'text-gold-500' : 'text-slate-500')"
                                  class="transition-all duration-1000 ease-out" />
                      </svg>
                      <div class="text-center z-10">
                          <span class="block text-xl md:text-2xl font-black leading-none" :class="job.matchScore >= 80 ? 'text-white' : 'text-slate-300'">
                              {{ job.matchScore }}<span class="text-[10px] text-slate-500 font-bold ml-0.5">%</span>
                          </span>
                      </div>
                  </div>
              </div>
              
              <!-- Description Snippet -->
              <p class="text-sm text-slate-400 line-clamp-3 leading-relaxed mb-6 font-medium">
                {{ job.desc }}
              </p>
          </div>
          
          <!-- Card Footer Actions -->
          <div class="flex items-center gap-3 pt-4 border-t border-surface-800/50 mt-auto">
             <button 
                v-if="job.rawUrl" 
                @click="addToCrmAndApply(job)"
                class="flex-[0.4] text-center bg-white hover:bg-slate-200 text-surface-950 px-4 py-3 rounded-xl font-bold text-sm transition-colors shadow-sm focus:ring-2 focus:ring-white/50 outline-none">
                Postuler
             </button>
             <button disabled class="flex-[0.4] text-center bg-surface-800 text-slate-500 px-4 py-3 rounded-xl font-bold text-sm cursor-not-allowed" v-else>
                 Lien Mort
             </button>
             
             <!-- AI Adapt CV Button -->
             <button 
                @click="adaptCV(job)"
                :disabled="isAdaptingCV && adaptingJobId === job.id"
                class="flex-1 flex items-center justify-center gap-2 bg-gradient-to-r from-gold-500/10 to-amber-500/10 hover:from-gold-500/20 hover:to-amber-500/20 disabled:opacity-50 text-gold-400 px-4 py-3 rounded-xl font-bold text-sm transition-all border border-gold-500/20 hover:border-gold-500/40 focus:ring-2 focus:ring-gold-500/50 outline-none group/adapt">
                <ArrowPathIcon v-if="isAdaptingCV && adaptingJobId === job.id" class="w-5 h-5 animate-spin text-gold-400" />
                <SparklesIcon v-else class="w-5 h-5 text-gold-500 group-hover/adapt:scale-110 transition-transform" />
                <span class="hidden sm:inline">Adapter CV</span>
             </button>
             
             <button 
                @click="runRadar(job)"
                :disabled="loadingRadarFor === job.id"
                class="flex-[0.4] flex items-center justify-center gap-2 bg-surface-800 hover:bg-surface-700 disabled:opacity-50 text-white px-4 py-3 rounded-xl font-semibold text-sm transition-colors border border-surface-700 focus:ring-2 focus:ring-gold-500/50 outline-none group/radar">
                <ArrowPathIcon v-if="loadingRadarFor === job.id" class="w-5 h-5 animate-spin text-gold-400" />
                <svg v-else class="w-5 h-5 text-slate-400 group-hover/radar:text-gold-400 transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
                <span class="hidden sm:inline">Radar</span>
             </button>
          </div>
       </div>
    </div>
    
    <!-- AI CV Adaptation Modal -->
    <div v-if="showAdaptModal" class="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6">
        <div class="absolute inset-0 bg-surface-950/80 backdrop-blur-sm" @click="closeAdaptModal"></div>
        
        <div class="relative w-full max-w-4xl max-h-[90vh] flex flex-col bg-surface-900 border border-surface-700 rounded-3xl shadow-2xl overflow-hidden animate-fade-in-up">
            <!-- Modal Header -->
            <div class="px-6 py-5 border-b border-surface-800 flex items-center justify-between bg-surface-900/50">
                <div class="flex items-center gap-3 text-gold-400">
                    <SparklesIcon class="w-6 h-6 animate-pulse" />
                    <h3 class="text-xl font-display font-bold text-white tracking-tight">Gemini 3 CV Intelligence</h3>
                </div>
                <button @click="closeAdaptModal" class="text-slate-400 hover:text-white transition-colors bg-surface-800 hover:bg-surface-700 p-2 rounded-xl">
                    <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
                </button>
            </div>
            
            <!-- Modal Body -->
            <div class="p-6 overflow-y-auto flex-1 custom-scrollbar">
                
                <div v-if="isAdaptingCV" class="flex flex-col items-center justify-center py-20 text-center">
                    <ArrowPathIcon class="w-12 h-12 text-gold-500 animate-spin mb-6" />
                    <p class="text-lg font-bold text-white mb-2">Analyse du poste et refonte du CV en cours...</p>
                    <p class="text-slate-400 font-medium">L'agent Gemini 3.1 Pro croise vos compétences avec la description.</p>
                </div>
                
                <div v-else-if="adaptedData" class="space-y-8">
                    
                    <!-- Markdown CV Recommendation -->
                    <div class="bg-surface-950 border border-surface-800 rounded-2xl p-6">
                        <div class="flex items-center gap-2 mb-4">
                            <DocumentTextIcon class="w-5 h-5 text-emerald-400" />
                            <h4 class="text-lg font-bold text-white">Résumé & Points Forts Suggérés</h4>
                        </div>
                        <div class="prose prose-invert max-w-none text-slate-300 prose-headings:text-white prose-a:text-gold-400 prose-strong:text-emerald-400">
                            <!-- We use pre-wrap to respect newlines currently -->
                            <div class="whitespace-pre-wrap">{{ adaptedData.markdown }}</div>
                        </div>
                    </div>
                    
                    <!-- Missing Experience Projects -->
                    <div v-if="adaptedData.projects && adaptedData.projects.length" class="space-y-4">
                        <h4 class="text-lg font-bold text-white flex items-center gap-2">
                            <BriefcaseIcon class="w-5 h-5 text-amber-500" />
                            Projets Recommandés (pour combler les lacunes)
                        </h4>
                        
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div v-for="(proj, idx) in adaptedData.projects" :key="idx" 
                                 class="bg-gradient-to-br from-surface-800 to-surface-900 border border-amber-500/20 rounded-xl p-5 hover:border-amber-500/50 transition-colors">
                                <h5 class="font-bold text-emerald-400 mb-2">{{ proj.title }}</h5>
                                <p class="text-sm text-slate-400 leading-relaxed">{{ proj.desc }}</p>
                            </div>
                        </div>
                    </div>
                    
                </div>
            </div>
            
            <!-- Modal Footer -->
            <div class="px-6 py-5 border-t border-surface-800 flex items-center justify-between bg-surface-900/50">
                <button @click="closeAdaptModal" class="px-6 py-3 border border-surface-700 text-slate-400 hover:text-white hover:bg-surface-800 rounded-xl font-bold transition-all">
                    Fermer
                </button>
                
                <div class="flex items-center gap-3">
                    <button 
                        v-if="adaptedData"
                        @click="saveAdaptedToProfile"
                        :disabled="isSavingToProfile"
                        class="px-6 py-3 bg-indigo-500/10 border border-indigo-500/30 text-indigo-400 hover:bg-indigo-500/20 rounded-xl font-bold transition-all flex items-center gap-2"
                    >
                        <CheckCircleIcon v-if="!isSavingToProfile" class="w-5 h-5" />
                        <ArrowPathIcon v-else class="w-5 h-5 animate-spin" />
                        {{ isSavingToProfile ? 'Enregistrement...' : 'Enregistrer dans Profil' }}
                    </button>
                    
                    <button 
                        @click="copyAdaptedCV"
                        class="px-8 py-3 bg-gradient-to-r from-gold-500 to-amber-600 text-surface-950 font-bold rounded-xl shadow-lg shadow-gold-500/20 hover:scale-105 active:scale-95 transition-all">
                        Copier le Contenu
                    </button>
                </div>
            </div>
        </div>
    </div>
    
  </div>
</template>
