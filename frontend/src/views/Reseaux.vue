<script setup>
import { authFetch } from '../utils/auth'

import { ref, onMounted } from 'vue'
import { 
  BuildingOfficeIcon, 
  UserGroupIcon, 
  EnvelopeIcon, 
  SparklesIcon,
  CheckBadgeIcon,
  LinkIcon,
  DocumentTextIcon,
  ArrowPathIcon,
  BookOpenIcon,
  GlobeAltIcon
} from '@heroicons/vue/24/outline'

const activeTab = ref('osint')

// États pour l'enrichissement
const companyName = ref('')
const isEnriching = ref(false)
const hrProfiles = ref([])
const hasEnriched = ref(false)

// États pour le Headhunter
const hhCompanyName = ref('')
const isHunting = ref(false)
const decisionMakers = ref([])
const hasHunted = ref(false)

// États pour la rédaction d'email
const requestType = ref('emploi')
const draftCompanyName = ref('') // Company name specific to draft panel (standalone)
const targetDomain = ref('')
const selectedHrName = ref('')
const isDrafting = ref(false)
const draftResult = ref(null)
const draftError = ref('')
const draftCopied = ref(false)

// Carnet d'adresses
const savedContacts = ref([])
const isLoadingContacts = ref(false)

const loadContacts = async () => {
    isLoadingContacts.value = true
    try {
        const res = await authFetch('http://localhost:8000/api/network/contacts')
        const json = await res.json()
        if (json.status === 'success') {
            savedContacts.value = json.data || []
        }
    } catch(e) {
        console.error("Erreur Chargement Carnet:", e)
    } finally {
        isLoadingContacts.value = false
    }
}

onMounted(() => {
    loadContacts()
})

const prefillDraft = (companyNameStr) => {
    activeTab.value = 'osint'
    companyName.value = companyNameStr
    draftCompanyName.value = companyNameStr  // Also fill the draft form
}

// Simulation de récupération du CV déposé (Stocké globalement en VRAI VUE, ici simplifié)
// L'API a besoin du cv_text. Si non présent, l'API renvoie une erreur gracieuse.
const cvTextStatus = ref('Prêt à l\'emploi') 

const enrichCompany = async () => {
    if (!companyName.value.trim()) return
    isEnriching.value = true
    hasEnriched.value = false
    hrProfiles.value = []
    draftResult.value = null
    
    try {
        const res = await authFetch('http://localhost:8000/api/network/enrich', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ company_name: companyName.value })
        })
        const json = await res.json()
        if (json.status === 'success') {
            hrProfiles.value = json.data || []
            hasEnriched.value = true
        }
    } catch(e) {
        console.error("Erreur Enrichissement:", e)
        alert("Impossible de contacter le serveur OSINT.")
    } finally {
        isEnriching.value = false
    }
}

const findDecisionMakers = async () => {
    if (!hhCompanyName.value.trim()) return
    isHunting.value = true
    hasHunted.value = false
    decisionMakers.value = []
    
    try {
        const res = await authFetch('http://localhost:8000/api/network/headhunter', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ company_name: hhCompanyName.value })
        })
        const json = await res.json()
        if (json.status === 'success') {
            decisionMakers.value = json.data || []
            hasHunted.value = true
        }
    } catch(e) {
        console.error("Erreur Headhunter:", e)
        alert("Impossible de contacter le HeadhunterAgent.")
    } finally {
        isHunting.value = false
    }
}

const selectHr = (name) => {
    selectedHrName.value = name
}

const draftEmail = async () => {
    const company = draftCompanyName.value.trim() || companyName.value.trim()
    if (!company) {
        draftError.value = "Veuillez saisir le nom de l'entreprise."
        return
    }
    
    isDrafting.value = true
    draftResult.value = null
    draftError.value = ''
    draftCopied.value = false
    
    try {
        const res = await authFetch('http://localhost:8000/api/network/draft-email', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                company_name: company,
                company_description: '',
                hr_name: selectedHrName.value,
                request_type: requestType.value,
                target_domain: targetDomain.value,
                // Generic fallback CV so the AI still has context
                cv_text: 'Professionnel motivé avec expérience solide. Compétences : communication, organisation, résolution de problèmes, travail en équipe. Disponible rapidement.'
            })
        })
        const json = await res.json()
        if (json.status === 'success') {
            draftResult.value = json.data
        } else {
            draftError.value = json.detail || 'Erreur lors de la génération du courriel.'
        }
    } catch(e) {
        draftError.value = `Erreur de connexion: ${e.message}`
        console.error('Erreur Drafting:', e)
    } finally {
        isDrafting.value = false
    }
}

const copyDraftEmail = async () => {
    if (!draftResult.value) return
    const text = `Objet: ${draftResult.value.subject}\n\n${draftResult.value.body}`
    try {
        await navigator.clipboard.writeText(text)
        draftCopied.value = true
        setTimeout(() => draftCopied.value = false, 2500)
    } catch(e) {}
}
</script>

<template>
  <div class="px-4 md:px-10 py-8 max-w-[1400px] mx-auto w-full animate-fade-in-up">
    
    <!-- En-tête -->
    <div class="flex flex-col lg:flex-row lg:items-end justify-between gap-6 mb-10 pt-4">
       <div class="relative z-10">
         <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-400/10 border border-emerald-400/20 text-emerald-400 text-xs font-bold tracking-wider uppercase mb-3">
             <span class="relative flex h-2 w-2">
                <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span class="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
             </span>
             OSINT Actif
         </div>
         <h1 class="text-4xl md:text-5xl font-display font-black text-white tracking-tight flex items-center gap-4">
           Générateur 
           <span class="text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-cyan-500">Réseaux</span>
         </h1>
         <p class="text-slate-400 mt-2 text-lg font-medium max-w-xl">
           Découvre les recruteurs cachés sur LinkedIn et génère des courriels d'approche ultra-personnalisés avec l'IA.
         </p>
       </div>
    </div>

    <!-- Tabs -->
    <div class="flex items-center gap-4 mb-8 border-b border-surface-800 pb-px">
        <button 
            @click="activeTab = 'osint'"
            :class="activeTab === 'osint' ? 'text-emerald-400 border-emerald-400' : 'text-slate-400 border-transparent hover:text-slate-200'"
            class="pb-4 px-2 border-b-2 font-bold transition-all flex items-center gap-2"
        >
            <SparklesIcon class="w-5 h-5" />
            OSINT & Rédaction
        </button>
        <button 
            @click="activeTab = 'carnet'; loadContacts()"
            :class="activeTab === 'carnet' ? 'text-emerald-400 border-emerald-400' : 'text-slate-400 border-transparent hover:text-slate-200'"
            class="pb-4 px-2 border-b-2 font-bold transition-all flex items-center gap-2"
        >
            <BookOpenIcon class="w-5 h-5" />
            Carnet d'Adresses
            <span class="bg-surface-800 text-slate-300 text-xs px-2 py-0.5 rounded-full ml-1">{{ savedContacts.length }}</span>
        </button>
        <button 
            @click="activeTab = 'headhunter'"
            :class="activeTab === 'headhunter' ? 'text-indigo-400 border-indigo-400' : 'text-slate-400 border-transparent hover:text-slate-200'"
            class="pb-4 px-2 border-b-2 font-bold transition-all flex items-center gap-2"
        >
            <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                <path stroke-linecap="round" stroke-linejoin="round" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
            </svg>
            Décideurs LinkedIn
        </button>
    </div>

    <!-- Contenu OSINT -->
    <div v-if="activeTab === 'osint'" class="grid grid-cols-1 lg:grid-cols-12 gap-8 animate-fade-in">
      
      <!-- Colonne Gauche: Outils OSINT -->
      <div class="lg:col-span-5 space-y-8">
          
          <!-- Carte 1: Recherche Entreprise -->
          <div class="bg-surface-900 border border-surface-800 rounded-3xl p-6 shadow-xl relative overflow-hidden group">
              <div class="absolute -top-24 -right-24 w-48 h-48 bg-emerald-500/10 rounded-full blur-3xl group-hover:bg-emerald-500/20 transition-all duration-500"></div>
              
              <div class="flex items-center gap-4 mb-6 relative z-10">
                  <div class="p-3 bg-surface-800 rounded-xl border border-surface-700">
                      <BuildingOfficeIcon class="w-6 h-6 text-emerald-400" />
                  </div>
                  <div>
                      <h2 class="text-xl font-bold text-white">Cibler une Entreprise</h2>
                      <p class="text-sm text-slate-400">Scanner le web pour trouver les décisionnaires RH.</p>
                  </div>
              </div>
              
              <div class="relative z-10">
                  <form @submit.prevent="enrichCompany" class="flex gap-3">
                      <input 
                          v-model="companyName"
                          type="text" 
                          placeholder="Nom de l'entreprise (ex: CGI, Ubisoft)..." 
                          class="flex-1 bg-surface-950 border border-surface-700 text-white rounded-xl px-4 py-3 focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500 outline-none transition-all placeholder:text-slate-600 font-medium"
                          required
                      />
                      <button 
                          type="submit" 
                          :disabled="isEnriching"
                          class="bg-emerald-500 hover:bg-emerald-400 text-surface-950 font-bold px-6 py-3 rounded-xl transition-all shadow-lg shadow-emerald-500/20 disabled:opacity-50 flex items-center gap-2"
                      >
                          <ArrowPathIcon v-if="isEnriching" class="w-5 h-5 animate-spin" />
                          <SparklesIcon v-else class="w-5 h-5" />
                          Scanner
                      </button>
                  </form>
              </div>
          </div>
          
          <!-- Carte 2: Résultats RH LinkedIn -->
          <div v-show="hasEnriched" class="bg-surface-900 border border-surface-800 rounded-3xl p-6 shadow-xl animate-fade-in">
              <div class="flex items-center justify-between mb-6">
                  <h3 class="text-lg font-bold text-white flex items-center gap-2">
                      <UserGroupIcon class="w-5 h-5 text-blue-400" />
                      Aiguilles LinkedIn (Pistes RH)
                  </h3>
                  <span class="bg-blue-500/10 text-blue-400 text-xs font-bold px-2.5 py-1 rounded-lg border border-blue-500/20">
                      {{ hrProfiles.length }} trouvés
                  </span>
              </div>
              
              <div v-if="hrProfiles.length === 0" class="text-slate-400 text-sm italic p-4 bg-surface-950 rounded-xl border border-surface-800">
                  Aucun profil public précis trouvé. Vous devrez peut-être faire une recherche LinkedIn manuelle.
              </div>
              
              <div v-else class="space-y-3">
                  <div 
                      v-for="(profile, idx) in hrProfiles" 
                      :key="idx"
                      class="bg-surface-950 border border-surface-800 p-4 rounded-xl flex items-start gap-4 hover:border-emerald-500/50 transition-colors cursor-pointer group"
                      @click="selectHr(profile.name)"
                  >
                      <div class="w-10 h-10 rounded-full bg-surface-800 flex items-center justify-center shrink-0 border border-surface-700 text-slate-300 font-bold">
                          {{ profile.name.charAt(0) }}
                      </div>
                      <div class="flex-1 min-w-0">
                          <h4 class="text-slate-200 font-bold text-sm line-clamp-1 group-hover:text-emerald-400 transition-colors">
                              {{ profile.name }}
                              <CheckBadgeIcon v-if="selectedHrName === profile.name" class="w-4 h-4 text-emerald-400 inline ml-1" />
                          </h4>
                          <p class="text-slate-500 text-xs line-clamp-2 mt-1">{{ profile.snippet }}</p>
                      </div>
                      <a :href="profile.url" target="_blank" @click.stop class="p-2 text-slate-500 hover:text-blue-400 hover:bg-blue-500/10 rounded-lg transition-colors">
                          <LinkIcon class="w-5 h-5" />
                      </a>
                  </div>
              </div>
          </div>
          
      </div>
      
      <!-- Colonne Droite: Générateur Courriel IA -->
      <div class="lg:col-span-7">
          <div class="bg-slate-800/40 backdrop-blur-xl border border-slate-700/50 rounded-3xl overflow-hidden shadow-2xl h-full flex flex-col">
              
              <!-- Header -->
              <div class="p-6 border-b border-slate-700/50 flex flex-wrap items-center justify-between gap-4 bg-slate-800/50">
                  <div class="flex items-center gap-3">
                      <div class="p-2 bg-indigo-500/20 rounded-lg border border-indigo-500/30">
                          <EnvelopeIcon class="w-6 h-6 text-indigo-400" />
                      </div>
                      <div>
                          <h2 class="text-xl font-bold text-white">Rédaction Auto (Gemini)</h2>
                          <p class="text-xs text-slate-400">Courriel personnalisé généré par IA en quelques secondes.</p>
                      </div>
                  </div>
                  
                  <div class="flex items-center bg-surface-950 p-1 rounded-xl border border-surface-700">
                      <button @click="requestType='emploi'" :class="requestType==='emploi' ? 'bg-indigo-500 text-white shadow-md' : 'text-slate-400 hover:text-white'" class="px-4 py-1.5 rounded-lg text-sm font-bold transition-all">Emploi</button>
                      <button @click="requestType='stage'" :class="requestType==='stage' ? 'bg-indigo-500 text-white shadow-md' : 'text-slate-400 hover:text-white'" class="px-4 py-1.5 rounded-lg text-sm font-bold transition-all">Stage</button>
                  </div>
              </div>
              
              <!-- Zone Configuration & Résultat -->
              <div class="p-6 flex-1 flex flex-col gap-5">
                  
                  <!-- Form Configuration -->
                  <div class="bg-surface-900 border border-surface-800 p-5 rounded-2xl space-y-4">
                      <!-- Company Name (required, standalone) -->
                      <div>
                          <label class="block text-xs font-bold text-slate-400 mb-2 uppercase tracking-wider">
                              Entreprise Cible <span class="text-indigo-400">*</span>
                          </label>
                          <input 
                              v-model="draftCompanyName" 
                              placeholder="Ex: CGI, Ubisoft, Banque Nationale..." 
                              class="w-full bg-surface-950 border border-surface-800 text-white rounded-xl px-4 py-2.5 outline-none focus:border-indigo-500 text-sm transition-colors"
                          />
                          <p v-if="companyName && !draftCompanyName" class="text-xs text-emerald-500 mt-1">
                              ✓ Pré-rempli depuis la recherche OSINT: <strong>{{ companyName }}</strong>
                          </p>
                      </div>
                      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div>
                              <label class="block text-xs font-bold text-slate-400 mb-2 uppercase tracking-wider">Cible RH (Optionnel)</label>
                              <input v-model="selectedHrName" placeholder="Mme. Tremblay..." class="w-full bg-surface-950 border border-surface-800 text-white rounded-xl px-4 py-2.5 outline-none focus:border-indigo-500 text-sm" />
                          </div>
                          <div>
                              <label class="block text-xs font-bold text-slate-400 mb-2 uppercase tracking-wider">Domaine Précis (Optionnel)</label>
                              <input v-model="targetDomain" placeholder="Ex: Backend Python, Vente UX..." class="w-full bg-surface-950 border border-surface-800 text-white rounded-xl px-4 py-2.5 outline-none focus:border-indigo-500 text-sm" />
                          </div>
                      </div>
                  </div>

                  <!-- Error Message -->
                  <div v-if="draftError" class="flex items-center gap-2 bg-rose-500/10 border border-rose-500/20 text-rose-400 rounded-xl px-4 py-3 text-sm font-medium">
                      <span>❌</span> {{ draftError }}
                  </div>
                  
                  <!-- Generate Button -->
                  <div class="flex justify-end">
                      <button 
                          @click="draftEmail"
                          :disabled="isDrafting || (!draftCompanyName.trim() && !companyName.trim())"
                          class="bg-indigo-500 hover:bg-indigo-400 text-white font-bold px-8 py-3 rounded-xl transition-all shadow-lg shadow-indigo-500/20 disabled:opacity-40 disabled:cursor-not-allowed flex items-center gap-2"
                      >
                          <ArrowPathIcon v-if="isDrafting" class="w-5 h-5 animate-spin" />
                          <SparklesIcon v-else class="w-5 h-5" />
                          {{ isDrafting ? 'Génération en cours...' : 'Rédiger le Courriel Moteur' }}
                      </button>
                  </div>
                  
                  <!-- Zone Résultat Email -->
                  <div v-if="draftResult" class="flex-1 bg-surface-950 border border-emerald-500/20 rounded-2xl flex flex-col animate-fade-in overflow-hidden relative group">
                      <div class="absolute inset-0 bg-gradient-to-br from-indigo-500/5 via-transparent to-transparent pointer-events-none"></div>
                      
                      <!-- Subject -->
                      <div class="px-6 pt-5 pb-4 border-b border-surface-800">
                          <label class="text-[10px] uppercase font-bold text-slate-500 tracking-widest block mb-1">Objet du Courriel</label>
                          <h3 class="text-white font-bold text-base select-all cursor-text">{{ draftResult.subject }}</h3>
                      </div>
                      
                      <!-- Body -->
                      <div class="flex-1 px-6 py-5 overflow-y-auto whitespace-pre-wrap text-slate-300 text-sm leading-relaxed custom-scrollbar select-all cursor-text">
                          {{ draftResult.body }}
                      </div>
                      
                      <!-- Footer Actions -->
                      <div class="px-6 py-4 border-t border-surface-800 flex items-center justify-between bg-black/20">
                          <span class="text-xs text-slate-500 flex items-center gap-1.5">
                              <CheckBadgeIcon class="w-4 h-4 text-emerald-500" />
                              Généré par Gemini
                          </span>
                          <div class="flex items-center gap-2">
                              <button @click="draftEmail" class="text-xs font-bold text-slate-400 hover:text-white gap-1.5 flex items-center px-3 py-1.5 rounded-lg hover:bg-surface-800 transition-colors">
                                  <ArrowPathIcon class="w-3.5 h-3.5" />Régénérer
                              </button>
                              <button 
                                  @click="copyDraftEmail"
                                  class="flex items-center gap-2 px-4 py-1.5 rounded-xl font-bold text-xs transition-all"
                                  :class="draftCopied ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-indigo-500 hover:bg-indigo-400 text-white'"
                              >
                                  <span>{{ draftCopied ? '✓ Copié !' : '⎘ Copier l\'email' }}</span>
                              </button>
                          </div>
                      </div>
                  </div>
                  
                  <!-- Loading State -->
                  <div v-else-if="isDrafting" class="flex-1 flex flex-col items-center justify-center py-12 gap-4">
                      <div class="relative w-12 h-12">
                          <div class="absolute inset-0 border-4 border-indigo-500/20 rounded-full"></div>
                          <div class="absolute inset-0 border-4 border-white border-t-transparent rounded-full animate-spin"></div>
                      </div>
                      <p class="text-sm font-bold text-white animate-pulse">Gemini rédige votre chef-d'œuvre...</p>
                  </div>
                  
                  <!-- Placeholder -->
                  <div v-else class="flex-1 border-2 border-dashed border-surface-800 rounded-2xl flex flex-col items-center justify-center text-center p-8">
                      <DocumentTextIcon class="w-12 h-12 text-surface-700 mb-4" />
                      <h3 class="text-slate-400 font-bold mb-1">La Toile Blanche</h3>
                      <p class="text-slate-500 text-sm max-w-sm">Entrez l'entreprise cible ci-dessus et laissez Gemini rédiger un courriel percutant et personnalisé.</p>
                  </div>
                  
              </div>
          </div>
      </div>
      
    </div>

    <!-- Contenu Chasseur de Têtes (Headhunter) -->
    <div v-else-if="activeTab === 'headhunter'" class="animate-fade-in space-y-8">
        <div class="bg-surface-900 border border-surface-800 rounded-3xl p-8 shadow-xl relative overflow-hidden group">
            <div class="absolute -top-24 -right-24 w-48 h-48 bg-indigo-500/10 rounded-full blur-3xl transition-all duration-500"></div>
            
            <div class="flex items-center gap-4 mb-6 relative z-10">
                <div class="p-3 bg-surface-800 rounded-xl border border-surface-700">
                    <svg class="w-6 h-6 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                    </svg>
                </div>
                <div>
                    <h2 class="text-xl font-bold text-white">Chasse aux Décideurs (LinkedIn)</h2>
                    <p class="text-sm text-slate-400">Google Dorking automatisé pour débusquer les CTO, CEO et recruteurs cachés.</p>
                </div>
            </div>
            
            <form @submit.prevent="findDecisionMakers" class="flex gap-3 relative z-10 max-w-2xl">
                <input 
                    v-model="hhCompanyName"
                    type="text" 
                    placeholder="Nom de l'entreprise cible..." 
                    class="flex-1 bg-surface-950 border border-surface-700 text-white rounded-xl px-4 py-3 focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500 outline-none transition-all placeholder:text-slate-600 font-medium"
                    required
                />
                <button 
                    type="submit" 
                    :disabled="isHunting"
                    class="bg-indigo-500 hover:bg-indigo-400 text-white font-bold px-6 py-3 rounded-xl transition-all shadow-lg shadow-indigo-500/20 disabled:opacity-50 flex items-center gap-2"
                >
                    <ArrowPathIcon v-if="isHunting" class="w-5 h-5 animate-spin" />
                    <SparklesIcon v-else class="w-5 h-5" />
                    Traquer
                </button>
            </form>
        </div>

        <!-- Resultats Headhunter -->
        <div v-if="hasHunted" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div v-if="decisionMakers.length === 0" class="col-span-full text-center text-slate-400 py-12 bg-surface-900/50 rounded-2xl border border-surface-800 border-dashed">
                Aucun profil de décideur n'a été clairement identifié par l'Agent IA.
            </div>
            
            <div 
                v-for="(maker, idx) in decisionMakers" 
                :key="idx"
                class="bg-surface-900 border border-surface-800 rounded-2xl p-6 hover:border-indigo-500/50 transition-all flex flex-col group"
            >
                <div class="flex items-start justify-between mb-4">
                    <div class="w-12 h-12 rounded-full bg-gradient-to-br from-indigo-500/20 to-purple-500/20 border border-indigo-500/30 flex items-center justify-center shrink-0">
                        <span class="text-lg font-bold text-indigo-300">{{ maker.name.charAt(0) }}</span>
                    </div>
                    <a :href="maker.linkedin_url" target="_blank" class="text-slate-500 hover:text-blue-400 bg-surface-950 p-2 rounded-lg border border-surface-800 transition-colors">
                        <LinkIcon class="w-5 h-5" />
                    </a>
                </div>
                
                <h3 class="text-lg font-bold text-white mb-1 group-hover:text-indigo-400 transition-colors">{{ maker.name }}</h3>
                <p class="text-sm font-medium text-slate-400 mb-6 flex-1">{{ maker.role }}</p>
                
                <button 
                    @click="activeTab='osint'; companyName=hhCompanyName; selectedHrName=maker.name; requestType='emploi';"
                    class="w-full bg-surface-950 hover:bg-indigo-500 text-slate-300 hover:text-white border border-surface-700 hover:border-indigo-500 font-bold py-2.5 rounded-xl transition-all flex items-center justify-center gap-2"
                >
                    <EnvelopeIcon class="w-4 h-4" />
                    Rédiger courriel
                </button>
            </div>
        </div>
    </div>

    <!-- Contenu Carnet d'Adresses -->
    <div v-else-if="activeTab === 'carnet'" class="animate-fade-in">
        <!-- Header -->
        <div class="flex items-center justify-between mb-6">
            <div>
                <h2 class="text-xl font-bold text-white">Carnet d'Adresses</h2>
                <p class="text-slate-500 text-sm mt-0.5">{{ savedContacts.length }} entreprise{{ savedContacts.length !== 1 ? 's' : '' }} scrapée{{ savedContacts.length !== 1 ? 's' : '' }} automatiquement</p>
            </div>
            <button @click="loadContacts" class="flex items-center gap-2 px-4 py-2 text-sm font-bold text-slate-400 hover:text-white bg-surface-900 rounded-xl border border-surface-800 hover:bg-surface-800 transition-colors">
                <ArrowPathIcon :class="isLoadingContacts ? 'animate-spin' : ''" class="w-4 h-4" />
                Actualiser
            </button>
        </div>
        
        <!-- Empty State -->
        <div v-if="savedContacts.length === 0" class="bg-surface-900 border border-surface-800 rounded-3xl p-16 text-center">
            <div class="w-16 h-16 rounded-2xl bg-surface-800 flex items-center justify-center mx-auto mb-4">
                <BookOpenIcon class="w-8 h-8 text-surface-600" />
            </div>
            <h3 class="text-lg font-bold text-slate-300 mb-2">Carnet Vide</h3>
            <p class="text-slate-500 max-w-sm mx-auto text-sm leading-relaxed">
                Lancez des recherches dans le <strong class="text-slate-300">Sniper d'Opportunités</strong>. L'Agent extraira automatiquement les sites web et e-mails des entreprises et les stockera ici.
            </p>
        </div>
        
        <!-- Contact Cards Grid -->
        <div v-else class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5">
            <div 
                v-for="contact in savedContacts" 
                :key="contact.id"
                class="bg-surface-900 border border-surface-800 rounded-2xl p-5 hover:border-emerald-500/30 transition-all flex flex-col group"
            >
                <!-- Card Header: Company + Badges -->
                <div class="flex items-start gap-3 mb-4">
                    <div class="w-11 h-11 rounded-xl bg-surface-800 border border-surface-700 flex items-center justify-center shrink-0 group-hover:bg-emerald-500/10 group-hover:border-emerald-500/20 transition-colors">
                        <BuildingOfficeIcon class="w-5 h-5 text-slate-500 group-hover:text-emerald-400 transition-colors" />
                    </div>
                    <div class="flex-1 min-w-0">
                        <h3 class="font-bold text-white text-base truncate leading-snug">{{ contact.company_name }}</h3>
                        <p class="text-[11px] text-slate-500 mt-0.5">
                            Mis à jour {{ new Date(contact.last_updated).toLocaleDateString('fr-CA') }}
                        </p>
                    </div>
                </div>

                <!-- Badge Row -->
                <div class="flex items-center gap-2 flex-wrap mb-4">
                    <span v-if="contact.category && contact.category !== 'Non catégorisée'" class="inline-flex items-center px-2 py-0.5 rounded-md text-[10px] font-black uppercase tracking-widest bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                        {{ contact.category }}
                    </span>
                    <span v-if="contact.emails && contact.emails.length > 0" class="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[10px] font-black uppercase tracking-widest bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                        <EnvelopeIcon class="w-3 h-3" />
                        {{ contact.emails.length }} email{{ contact.emails.length > 1 ? 's' : '' }}
                    </span>
                    <span v-if="contact.phone" class="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[10px] font-black uppercase tracking-widest bg-amber-500/10 text-amber-400 border border-amber-500/20">
                        📞 Téléphone
                    </span>
                    <span v-if="!contact.emails?.length && !contact.phone && !contact.site_url" class="inline-flex items-center px-2 py-0.5 rounded-md text-[10px] font-black uppercase tracking-widest bg-surface-800 text-slate-500 border border-surface-700">
                        Infos limitées
                    </span>
                </div>

                <!-- Contact Details -->
                <div class="space-y-2 flex-1 mb-4">
                    <!-- Website -->
                    <a v-if="contact.site_url" :href="contact.site_url" target="_blank"
                        class="flex items-center gap-2.5 p-2.5 rounded-xl bg-surface-950 border border-surface-800 hover:border-blue-500/30 transition-colors group/link">
                        <GlobeAltIcon class="w-4 h-4 text-blue-400 shrink-0" />
                        <span class="text-xs font-medium text-blue-400 group-hover/link:text-blue-300 truncate">
                            {{ contact.site_url.replace(/https?:\/\//, '').replace(/\/$/, '') }}
                        </span>
                    </a>

                    <!-- Phone -->
                    <div v-if="contact.phone" class="flex items-center gap-2.5 p-2.5 rounded-xl bg-surface-950 border border-surface-800">
                        <span class="text-base">📞</span>
                        <span class="text-xs font-bold text-emerald-400 select-all">{{ contact.phone }}</span>
                    </div>

                    <!-- Emails -->
                    <div v-for="email in (contact.emails || [])" :key="email"
                        @click="navigator.clipboard?.writeText(email)"
                        class="flex items-center gap-2.5 p-2.5 rounded-xl bg-surface-950 border border-surface-800 hover:border-emerald-500/30 cursor-pointer transition-colors group/email"
                        :title="`Copier: ${email}`">
                        <EnvelopeIcon class="w-4 h-4 text-slate-500 group-hover/email:text-emerald-400 transition-colors shrink-0" />
                        <span class="text-xs font-medium text-slate-300 group-hover/email:text-white truncate select-all">{{ email }}</span>
                        <span class="ml-auto text-[10px] text-slate-600 group-hover/email:text-emerald-400 transition-colors shrink-0">Copier</span>
                    </div>

                    <!-- Source Job -->
                    <div v-if="contact.source_job" class="flex items-start gap-2 text-[11px] text-slate-600 pt-1">
                        <DocumentTextIcon class="w-3.5 h-3.5 shrink-0 mt-0.5" />
                        <span class="leading-snug line-clamp-1">{{ contact.source_job }}</span>
                    </div>

                    <!-- No data -->
                    <div v-if="!contact.site_url && !contact.phone && (!contact.emails || !contact.emails.length)" class="text-xs text-slate-600 italic py-2">
                        Aucune coordonnée directe disponible pour l'instant.
                    </div>
                </div>
                
                <!-- CTA -->
                <button 
                    @click="prefillDraft(contact.company_name)"
                    class="w-full bg-surface-800 hover:bg-emerald-500/20 text-emerald-400 border border-surface-700 hover:border-emerald-500/40 font-bold py-2.5 rounded-xl transition-all flex items-center justify-center gap-2 text-sm"
                >
                    <SparklesIcon class="w-4 h-4" />
                    Rédiger une approche IA
                </button>
            </div>
        </div>
    </div>
  </div>
</template>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #334155;
  border-radius: 4px;
}
</style>
