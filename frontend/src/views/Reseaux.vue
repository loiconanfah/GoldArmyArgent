<script setup>
import { authFetch } from '../utils/auth'
import { ref, onMounted } from 'vue'
import { toastState } from '../store/toastState'
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
  GlobeAltIcon,
  MagnifyingGlassIcon,
  ClipboardIcon,
  CheckCircleIcon,
  PencilSquareIcon,
  UserIcon
} from '@heroicons/vue/24/outline'

const activeTab = ref('osint')

// Profile Data (for real CV)
const profile = ref({ cv_text: '' })
const fetchProfile = async () => {
    try {
        const res = await authFetch('/api/profile')
        const json = await res.json()
        if (json.status === 'success') {
            profile.value = json.data
        }
    } catch (e) {
        console.error("Erreur chargement profil:", e)
    }
}

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
        const res = await authFetch('/api/network/contacts')
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
    fetchProfile()
})

const prefillDraft = (companyNameStr) => {
    activeTab.value = 'osint'
    companyName.value = companyNameStr
    draftCompanyName.value = companyNameStr  // Also fill the draft form
}

const enrichCompany = async () => {
    if (!companyName.value.trim()) return
    isEnriching.value = true
    hasEnriched.value = false
    hrProfiles.value = []
    draftResult.value = null
    
    try {
        const res = await authFetch('/api/network/enrich', {
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
        toastState.addToast("Erreur lors de l'enrichissement OSINT.", "error")
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
        const res = await authFetch('/api/network/headhunter', {
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
        toastState.addToast("Erreur de l'agent Headhunter.", "error")
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
        const res = await authFetch('/api/network/draft-email', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                company_name: company,
                company_description: '',
                hr_name: selectedHrName.value,
                request_type: requestType.value,
                target_domain: targetDomain.value,
                cv_text: profile.value.cv_text || 'CV non fourni. John Doe, développeur motivé.'
            })
        })
        const json = await res.json()
        if (json.status === 'success') {
            draftResult.value = json.data
            toastState.addToast("Email généré avec succès !")
        } else {
            draftError.value = json.detail || 'Erreur lors de la génération du courriel.'
            toastState.addToast(draftError.value, "error")
        }
    } catch(e) {
        draftError.value = `Erreur de connexion.`
        toastState.addToast("Erreur de connexion au serveur.", "error")
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
    
    <!-- Hero Header -->
    <div class="relative mb-12 rounded-[2.5rem] overflow-hidden bg-surface-900 border border-surface-800 p-8 md:p-12 shadow-2xl">
        <div class="absolute top-0 right-0 w-1/2 h-full bg-gradient-to-l from-emerald-500/10 via-emerald-500/5 to-transparent pointer-events-none"></div>
        <div class="absolute -bottom-24 -left-24 w-96 h-96 bg-indigo-500/10 rounded-full blur-[100px] pointer-events-none"></div>
        
        <div class="relative z-10 max-w-2xl">
            <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-400/10 border border-emerald-400/20 text-emerald-400 text-[10px] font-black tracking-[0.2em] uppercase mb-6">
                 <span class="flex h-2 w-2 relative">
                    <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                    <span class="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                 </span>
                 Intelligence Réseaux Active
            </div>
            <h1 class="text-4xl md:text-6xl font-display font-black text-white tracking-tight leading-[1.1] mb-6">
                Levez les barrières du <span class="text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-cyan-500">Recrutement.</span>
            </h1>
            <p class="text-slate-400 text-lg font-medium leading-relaxed">
                Utilisez l'OSINT pour identifier les décideurs et générez des approches froides si percutantes qu'elles ne peuvent pas être ignorées.
            </p>
        </div>
    </div>
    <!-- Enhanced Tabs -->
    <div class="flex items-center gap-2 mb-10 bg-surface-900/50 p-1.5 rounded-2xl border border-surface-800 w-fit mx-auto md:mx-0">
        <button 
            @click="activeTab = 'osint'"
            :class="activeTab === 'osint' ? 'bg-surface-800 text-emerald-400 shadow-lg' : 'text-slate-500 hover:text-slate-300'"
            class="px-6 py-2.5 rounded-xl text-sm font-black transition-all flex items-center gap-2"
        >
            <SparklesIcon class="w-4 h-4" />
            Scanner & Rédiger
        </button>
        <button 
            @click="activeTab = 'headhunter'"
            :class="activeTab === 'headhunter' ? 'bg-surface-800 text-indigo-400 shadow-lg' : 'text-slate-500 hover:text-slate-300'"
            class="px-6 py-2.5 rounded-xl text-sm font-black transition-all flex items-center gap-2"
        >
            <MagnifyingGlassIcon class="w-4 h-4" />
            Headhunter
        </button>
        <button 
            @click="activeTab = 'carnet'"
            :class="activeTab === 'carnet' ? 'bg-surface-800 text-emerald-400 shadow-lg' : 'text-slate-500 hover:text-slate-300'"
            class="px-6 py-2.5 rounded-xl text-sm font-black transition-all flex items-center gap-2"
        >
            <BookOpenIcon class="w-4 h-4" />
            Carnet
        </button>
    </div>
    <!-- Tab Content -->
    <div v-if="activeTab === 'osint'" class="space-y-12 animate-fade-in">
        <!-- OSINT Search Panel -->
        <div class="bg-surface-900 border border-surface-800 rounded-[2.5rem] p-8 md:p-10 shadow-sm relative overflow-hidden group">
            <div class="flex items-center gap-3 mb-8">
                <div class="p-2 bg-emerald-500/10 rounded-xl">
                    <SparklesIcon class="w-5 h-5 text-emerald-400" />
                </div>
                <h3 class="text-xl font-bold text-white tracking-tight">Osculter une Entreprise</h3>
            </div>
            
            <form @submit.prevent="enrichCompany" class="flex flex-col md:flex-row gap-4">
                <div class="flex-1 relative group/input">
                    <BuildingOfficeIcon class="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500 group-focus-within/input:text-emerald-400 transition-colors" />
                    <input 
                        v-model="companyName"
                        type="text" 
                        placeholder="Nom de l'entreprise (ex: Google, Orange...)" 
                        class="w-full bg-surface-950 border border-surface-800 text-white rounded-2xl pl-12 pr-4 py-4 focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500 outline-none transition-all placeholder:text-slate-700 font-medium"
                        required
                    />
                </div>
                <button 
                    type="submit" 
                    :disabled="isEnriching"
                    class="bg-emerald-500 hover:bg-emerald-400 text-white font-black px-8 py-4 rounded-2xl transition-all shadow-lg shadow-emerald-500/20 disabled:opacity-50 flex items-center justify-center gap-2 group/btn"
                >
                    <ArrowPathIcon v-if="isEnriching" class="w-5 h-5 animate-spin" />
                    <SparklesIcon v-else class="w-5 h-5 transition-transform group-hover/btn:rotate-12" />
                    OSCULTER
                </button>
            </form>

            <div v-if="hasEnriched && hrProfiles.length > 0" class="mt-8 pt-8 border-t border-surface-800">
                <h4 class="text-[11px] font-black text-slate-500 uppercase tracking-[0.2em] mb-6">Décideurs identifiés via OSINT</h4>
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    <div 
                        v-for="hr in hrProfiles" 
                        :key="hr.url"
                        @click="selectHr(hr.name)"
                        :class="selectedHrName === hr.name ? 'border-emerald-500 bg-emerald-500/5 ring-1 ring-emerald-500/20' : 'border-surface-800 bg-surface-950 hover:border-emerald-500/30'"
                        class="p-4 rounded-2xl border transition-all cursor-pointer group/card flex flex-col relative"
                    >
                        <div class="flex items-start justify-between mb-3">
                            <div class="p-2 bg-surface-900 rounded-lg border border-surface-800 group-hover/card:bg-emerald-500/10 transition-colors">
                                <UserGroupIcon class="w-4 h-4 text-emerald-400" />
                            </div>
                            <a 
                                v-if="hr.url" 
                                :href="hr.url" 
                                target="_blank" 
                                @click.stop
                                class="p-1.5 text-slate-500 hover:text-blue-400 bg-surface-900 rounded-lg border border-surface-800 hover:border-blue-400/30 transition-all"
                                title="Voir sur LinkedIn"
                            >
                                <LinkIcon class="w-3.5 h-3.5" />
                            </a>
                        </div>
                        <h5 class="text-sm font-bold text-white mb-1 group-hover/card:text-emerald-400 transition-colors">{{ hr.name }}</h5>
                        <p class="text-[11px] text-slate-500 line-clamp-2 leading-relaxed h-8">{{ hr.snippet || "Profil identifié par l'analyseur OSINT." }}</p>
                        
                        <div v-if="selectedHrName === hr.name" class="absolute top-2 right-2 flex h-2 w-2">
                            <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                            <span class="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                        </div>
                    </div>
                </div>
            </div>
            <div v-else-if="hasEnriched && hrProfiles.length === 0" class="mt-8 pt-8 border-t border-surface-800 text-center">
                <p class="text-sm text-slate-500 italic">Aucun profil spécifique trouvé via OSINT. Essayez l'Agent Headhunter pour une recherche plus profonde.</p>
            </div>
        </div>

        <!-- Drafting Section -->
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-8 pb-20">
            <!-- Parameters -->
            <div class="lg:col-span-5 space-y-6">
                <div class="bg-surface-900 border border-surface-800 rounded-[2.5rem] p-8 shadow-sm">
                    <h3 class="text-lg font-bold text-white mb-6 flex items-center gap-2">
                        <PencilSquareIcon class="w-5 h-5 text-indigo-400" />
                        Paramètres de l'IA
                    </h3>
                    
                    <div class="space-y-5">
                        <div class="space-y-2">
                            <label class="text-[10px] font-black text-slate-500 uppercase tracking-widest ml-1">Type de demande</label>
                            <div class="grid grid-cols-2 gap-2 p-1 bg-surface-950 rounded-xl border border-surface-800">
                                <button @click="requestType='emploi'" :class="requestType==='emploi' ? 'bg-surface-800 text-white shadow-lg' : 'text-slate-500'" class="py-2.5 rounded-lg text-xs font-black transition-all">EMPLOI</button>
                                <button @click="requestType='stage'" :class="requestType==='stage' ? 'bg-surface-800 text-white shadow-lg' : 'text-slate-500'" class="py-2.5 rounded-lg text-xs font-black transition-all">STAGE</button>
                            </div>
                        </div>

                        <div class="space-y-2">
                            <label class="text-[10px] font-black text-slate-500 uppercase tracking-widest ml-1">Nom du destinataire</label>
                            <div class="relative group/input">
                                <UserIcon class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500 group-focus-within/input:text-indigo-400 transition-colors" />
                                <input v-model="selectedHrName" type="text" placeholder="ex: Jean Dupont (RH)" class="w-full bg-surface-950 border border-surface-800 text-white rounded-xl pl-10 pr-4 py-3 text-sm focus:border-indigo-500 transition-all font-medium outline-none" />
                            </div>
                        </div>

                        <div class="space-y-2">
                            <label class="text-[10px] font-black text-slate-500 uppercase tracking-widest ml-1">Domaine visé</label>
                            <input v-model="targetDomain" type="text" placeholder="ex: Analyste SOC, Dév Frontend..." class="w-full bg-surface-950 border border-surface-800 text-white rounded-xl px-4 py-3 text-sm focus:border-indigo-500 transition-all font-medium outline-none" />
                        </div>

                        <button 
                            @click="draftEmail"
                            :disabled="isDrafting"
                            class="w-full bg-indigo-500 hover:bg-indigo-400 text-white font-black py-4 rounded-2xl transition-all shadow-lg shadow-indigo-500/20 disabled:opacity-50 flex items-center justify-center gap-2 mt-4"
                        >
                            <SparklesIcon v-if="!isDrafting" class="w-5 h-5" />
                            <ArrowPathIcon v-else class="w-5 h-5 animate-spin" />
                            GÉNÉRER L'APPROCHE
                        </button>
                    </div>
                </div>
            </div>

            <!-- Result -->
            <div class="lg:col-span-7">
                <div class="bg-surface-900 border border-surface-800 rounded-[2.5rem] p-8 md:p-10 shadow-sm h-full flex flex-col min-h-[500px] relative overflow-hidden group/result">
                    <div class="absolute inset-0 bg-gradient-to-br from-indigo-500/[0.02] to-transparent pointer-events-none"></div>
                    
                    <div v-if="!draftResult && !isDrafting" class="flex-1 flex flex-col items-center justify-center text-center opacity-40 group-hover/result:opacity-60 transition-opacity">
                        <div class="w-20 h-20 rounded-full bg-surface-800 flex items-center justify-center mb-6">
                            <EnvelopeIcon class="w-10 h-10 text-slate-600" />
                        </div>
                        <h3 class="text-xl font-bold text-slate-300">En attente de génération</h3>
                        <p class="text-sm text-slate-500 max-w-xs mt-2">Remplissez le nom de l'entreprise et lancez la rédaction par l'IA.</p>
                    </div>

                    <div v-else-if="isDrafting" class="flex-1 flex flex-col items-center justify-center text-center">
                        <div class="relative w-16 h-16 mb-6">
                            <div class="absolute inset-0 border-4 border-indigo-500/20 rounded-full"></div>
                            <div class="absolute inset-0 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
                        </div>
                        <h3 class="text-xl font-bold text-white animate-pulse">L'IA rédige...</h3>
                        <p class="text-sm text-slate-400 mt-2">Personnalisation en cours avec votre CV...</p>
                    </div>

                    <div v-else-if="draftResult" class="flex flex-col h-full animate-fade-in">
                        <div class="flex items-center justify-between mb-8">
                            <div class="flex items-center gap-3">
                                <div class="w-10 h-10 rounded-xl bg-emerald-500/10 flex items-center justify-center border border-emerald-500/20">
                                    <CheckBadgeIcon class="w-6 h-6 text-emerald-400" />
                                </div>
                                <div>
                                    <h3 class="font-bold text-white tracking-tight leading-none mb-1">Approche Terminée</h3>
                                    <p class="text-[10px] font-black text-slate-500 uppercase tracking-widest">GEMINI 2.0 FLASH // ULTRA-PERSONALIZED</p>
                                </div>
                            </div>
                            <button @click="copyDraftEmail" :class="draftCopied ? 'bg-emerald-500 text-white' : 'bg-surface-800 text-slate-300 hover:text-white'" class="flex items-center gap-2 px-4 py-2 rounded-xl font-bold text-xs transition-all active:scale-95 shadow-lg border border-surface-700">
                                <CheckCircleIcon v-if="draftCopied" class="w-4 h-4" />
                                <ClipboardIcon v-else class="w-4 h-4" />
                                {{ draftCopied ? 'Copié !' : 'Copier Tout' }}
                            </button>
                        </div>

                        <div class="flex-1 space-y-4">
                            <div class="p-4 bg-surface-950 rounded-2xl border border-surface-800">
                                <p class="text-[10px] font-black text-indigo-400 uppercase tracking-widest mb-1.5 opacity-50">Objet :</p>
                                <p class="text-sm font-bold text-white">{{ draftResult.subject }}</p>
                            </div>
                            <div class="p-6 bg-surface-950 rounded-3xl border border-surface-800 flex-1 font-medium italic text-slate-300 relative">
                                <p class="whitespace-pre-wrap leading-relaxed text-[15px]">{{ draftResult.body }}</p>
                                <!-- HUD element -->
                                <div class="absolute bottom-4 right-6 text-[10px] font-mono text-slate-700 opacity-50 select-none">GOLDARMY_AI_DRAFT_SYSTEM_V2</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Contenu Headhunter -->
    <div v-else-if="activeTab === 'headhunter'" class="space-y-10 animate-fade-in">
        <!-- Headhunter Search Panel -->
        <div class="bg-surface-900 border border-surface-800 rounded-[2.5rem] p-8 md:p-10 shadow-sm relative overflow-hidden group">
            <div class="flex items-center gap-3 mb-8">
                <div class="p-2 bg-indigo-500/10 rounded-xl">
                    <MagnifyingGlassIcon class="w-5 h-5 text-indigo-400" />
                </div>
                <h3 class="text-xl font-bold text-white tracking-tight">Agent d'Infiltration (Headhunter)</h3>
            </div>
            
            <form @submit.prevent="findDecisionMakers" class="flex flex-col md:flex-row gap-4">
                <div class="flex-1 relative group/input">
                    <BuildingOfficeIcon class="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500 group-focus-within/input:text-indigo-400 transition-colors" />
                    <input 
                        v-model="hhCompanyName"
                        type="text" 
                        placeholder="Nom de l'entreprise cible..." 
                        class="w-full bg-surface-950 border border-surface-800 text-white rounded-2xl pl-12 pr-4 py-4 focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 outline-none transition-all placeholder:text-slate-700 font-medium"
                        required
                    />
                </div>
                <button 
                    type="submit" 
                    :disabled="isHunting"
                    class="bg-indigo-500 hover:bg-indigo-400 text-white font-black px-8 py-4 rounded-2xl transition-all shadow-lg shadow-indigo-500/20 disabled:opacity-50 flex items-center justify-center gap-2 group/btn"
                >
                    <ArrowPathIcon v-if="isHunting" class="w-5 h-5 animate-spin" />
                    <MagnifyingGlassIcon v-else class="w-5 h-5 transition-transform group-hover/btn:scale-110" />
                    TRAQUER
                </button>
            </form>
        </div>

        <!-- Headhunter Results Grid -->
        <div v-if="hasHunted" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 pb-20">
            <div v-if="decisionMakers.length === 0" class="col-span-full text-center text-slate-400 py-12 bg-surface-900/50 rounded-2xl border border-surface-800 border-dashed">
                Aucun profil de décideur n'a été clairement identifié par l'Agent IA.
            </div>
            
            <div 
                v-for="(maker, idx) in decisionMakers" 
                :key="idx"
                class="bg-surface-900 border border-surface-800 rounded-3xl p-6 hover:border-indigo-500/50 transition-all flex flex-col group shadow-sm hover:translate-y-[-4px]"
            >
                <div class="flex items-start justify-between mb-4">
                    <div class="w-12 h-12 rounded-[1.2rem] bg-gradient-to-br from-indigo-500/20 to-purple-500/20 border border-indigo-500/30 flex items-center justify-center shrink-0">
                        <span class="text-lg font-black text-indigo-300">{{ maker.name.charAt(0) }}</span>
                    </div>
                    <a 
                        v-if="maker.linkedin_url" 
                        :href="maker.linkedin_url" 
                        target="_blank" 
                        class="text-slate-500 hover:text-blue-400 bg-surface-950 p-2.5 rounded-xl border border-surface-800 transition-colors shadow-inner"
                        title="Voir sur LinkedIn"
                    >
                        <LinkIcon class="w-4 h-4" />
                    </a>
                </div>
                
                <h3 class="text-lg font-bold text-white mb-1 group-hover:text-indigo-400 transition-colors tracking-tight">{{ maker.name }}</h3>
                <p class="text-xs font-bold text-indigo-400/70 mb-2 uppercase tracking-tight">{{ maker.role }}</p>
                <p class="text-[11px] text-slate-500 line-clamp-2 leading-relaxed h-8 mb-6 italic">{{ maker.snippet || "Stratégie d'infiltration identifiée par l'IA." }}</p>
                
                <button 
                    @click="activeTab='osint'; companyName=hhCompanyName; selectedHrName=maker.name; requestType='emploi';"
                    class="w-full bg-surface-950 hover:bg-indigo-500/10 text-slate-400 hover:text-indigo-400 border border-surface-800 hover:border-indigo-500/50 font-black py-3 rounded-xl transition-all flex items-center justify-center gap-2 text-xs uppercase tracking-widest"
                >
                    <EnvelopeIcon class="w-4 h-4" />
                    Préparer l'approche
                </button>
            </div>
        </div>
    </div>

    <!-- Contenu Carnet d'Adresses -->
    <div v-else-if="activeTab === 'carnet'" class="animate-fade-in pb-20">
        <!-- Header -->
        <div class="flex items-center justify-between mb-8">
            <div>
                <h2 class="text-2xl font-bold text-white tracking-tight">Mon <span class="text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-cyan-500">Réseau</span></h2>
                <p class="text-slate-500 text-sm mt-0.5 font-medium">{{ savedContacts.length }} entreprises collectées</p>
            </div>
            <button @click="loadContacts" class="flex items-center gap-2 px-6 py-3 text-sm font-black text-slate-400 hover:text-white bg-surface-900 rounded-2xl border border-surface-800 hover:bg-surface-800 transition-all active:scale-95">
                <ArrowPathIcon :class="isLoadingContacts ? 'animate-spin' : ''" class="w-4 h-4" />
                ACTUALISER LE CARNET
            </button>
        </div>
        
        <!-- Empty State -->
        <div v-if="savedContacts.length === 0" class="bg-surface-900 border border-surface-800 rounded-[3rem] p-20 text-center relative overflow-hidden">
            <div class="absolute inset-0 bg-gradient-to-b from-emerald-500/[0.02] to-transparent pointer-events-none"></div>
            <div class="w-20 h-20 rounded-3xl bg-surface-950 flex items-center justify-center mx-auto mb-6 shadow-inner border border-surface-800">
                <BookOpenIcon class="w-10 h-10 text-slate-600" />
            </div>
            <h3 class="text-xl font-bold text-white mb-2">Votre carnet est vide</h3>
            <p class="text-slate-500 max-w-sm mx-auto text-sm leading-relaxed font-medium">
                Utilisez le <strong class="text-emerald-400">Sniper</strong> pour découvrir des opportunités. L'Agent extraira automatiquement les contacts et les stockera ici pour vos approches.
            </p>
        </div>
        
        <!-- Contact Cards Grid -->
        <div v-else class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
            <div 
                v-for="contact in savedContacts" 
                :key="contact.id"
                class="bg-surface-900 border border-surface-800 rounded-[2rem] p-6 hover:border-emerald-500/30 transition-all flex flex-col group shadow-sm hover:translate-y-[-4px]"
            >
                <!-- Card Header -->
                <div class="flex items-start gap-4 mb-5">
                    <div class="w-12 h-12 rounded-2xl bg-surface-950 border border-surface-800 flex items-center justify-center shrink-0 group-hover:bg-emerald-500/10 group-hover:border-emerald-500/20 transition-colors shadow-inner">
                        <BuildingOfficeIcon class="w-6 h-6 text-slate-500 group-hover:text-emerald-400 transition-colors" />
                    </div>
                    <div class="flex-1 min-w-0">
                        <h3 class="font-bold text-white text-lg truncate leading-tight group-hover:text-emerald-400 transition-colors">{{ contact.company_name }}</h3>
                        <p class="text-[11px] font-black text-slate-600 mt-1 uppercase tracking-widest">
                            Sync: {{ new Date(contact.last_updated).toLocaleDateString('fr-CA') }}
                        </p>
                    </div>
                </div>

                <!-- Badge Row -->
                <div class="flex items-center gap-2 flex-wrap mb-5">
                    <span v-if="contact.category && contact.category !== 'Non catégorisée'" class="inline-flex items-center px-2.5 py-1 rounded-lg text-[10px] font-black uppercase tracking-widest bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                        {{ contact.category }}
                    </span>
                    <span v-if="contact.emails && contact.emails.length > 0" class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-[10px] font-black uppercase tracking-widest bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                        <EnvelopeIcon class="w-3.5 h-3.5" />
                        {{ contact.emails.length }} email{{ contact.emails.length > 1 ? 's' : '' }}
                    </span>
                    <span v-if="contact.phone" class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-[10px] font-black uppercase tracking-widest bg-amber-500/10 text-amber-400 border border-amber-500/20">
                        📞 Tel
                    </span>
                </div>

                <!-- Contact Details -->
                <div class="space-y-2.5 flex-1 mb-6">
                    <a v-if="contact.site_url" :href="contact.site_url" target="_blank"
                        class="flex items-center gap-3 p-3 rounded-2xl bg-surface-950 border border-surface-800 hover:border-blue-500/30 transition-all group/link shadow-inner">
                        <GlobeAltIcon class="w-4 h-4 text-blue-400 shrink-0" />
                        <span class="text-[13px] font-medium text-blue-400 group-hover/link:text-blue-300 truncate">
                            {{ contact.site_url.replace(/https?:\/\//, '').replace(/\/$/, '') }}
                        </span>
                    </a>

                    <div v-if="contact.phone" class="flex items-center gap-3 p-3 rounded-2xl bg-surface-950 border border-surface-800 shadow-inner">
                        <span class="text-sm">📞</span>
                        <span class="text-[13px] font-bold text-emerald-400 select-all">{{ contact.phone }}</span>
                    </div>

                    <div v-for="email in (contact.emails || [])" :key="email"
                        @click="navigator.clipboard?.writeText(email)"
                        class="flex items-center gap-3 p-3 rounded-2xl bg-surface-950 border border-surface-800 hover:border-emerald-500/30 cursor-pointer transition-all group/email shadow-inner">
                        <EnvelopeIcon class="w-4 h-4 text-slate-500 group-hover/email:text-emerald-400 transition-colors shrink-0" />
                        <span class="text-[13px] font-medium text-slate-300 group-hover/email:text-white truncate select-all">{{ email }}</span>
                    </div>
                </div>
                
                <button 
                    @click="prefillDraft(contact.company_name)"
                    class="w-full bg-surface-950 hover:bg-emerald-500 text-slate-300 hover:text-white border border-surface-800 hover:border-emerald-500 font-black py-3 rounded-xl transition-all flex items-center justify-center gap-2 text-[11px] uppercase tracking-[0.2em]"
                >
                    <SparklesIcon class="w-4 h-4" />
                    Rédiger courriel
                </button>
            </div>
        </div>
    </div>

    <!-- Loading Modal for Drafting -->
    <div v-if="isDrafting" class="fixed inset-0 z-[100] flex items-center justify-center p-4">
        <div class="absolute inset-0 bg-surface-950/80 backdrop-blur-md animate-fade-in"></div>
        <div class="relative bg-surface-900 border border-surface-800 rounded-[2.5rem] p-10 shadow-2xl max-w-sm w-full text-center animate-fade-in-up">
            <div class="relative w-24 h-24 mx-auto mb-8">
                <div class="absolute inset-0 border-4 border-indigo-500/20 rounded-full"></div>
                <div class="absolute inset-0 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
                <div class="absolute inset-0 flex items-center justify-center">
                    <SparklesIcon class="w-10 h-10 text-indigo-400 animate-pulse" />
                </div>
            </div>
            <h3 class="text-2xl font-black text-white mb-3">Intelligence en Action</h3>
            <p class="text-slate-400 font-medium leading-relaxed">
                Gemini 2.0 Pro analyse votre CV et l'entreprise pour rédiger une approche ultra-personnalisée...
            </p>
            <div class="mt-8 flex items-center justify-center gap-1.5">
                <span class="w-1.5 h-1.5 rounded-full bg-indigo-500 animate-bounce" style="animation-delay: 0ms"></span>
                <span class="w-1.5 h-1.5 rounded-full bg-indigo-500 animate-bounce" style="animation-delay: 150ms"></span>
                <span class="w-1.5 h-1.5 rounded-full bg-indigo-500 animate-bounce" style="animation-delay: 300ms"></span>
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
