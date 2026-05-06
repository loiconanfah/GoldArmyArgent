<script setup>
import { authFetch } from '../utils/auth'
import { ref, onMounted, computed, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'
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

const { t } = useI18n()
const route = useRoute()
const activeTab = ref('osint')

// Watch ?tab= query param for deep-link from Dashboard
watch(() => route.query.tab, (tab) => {
    if (tab === 'ninja') activeTab.value = 'ninja'
}, { immediate: true })

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

// ── Network Ninja State ──
const ninjaCompanies   = ref([])       // [{company_name, job_title, profiles:[...]}]
const ninjaRunning     = ref(false)
const ninjaLoading     = ref(false)    // chargement initial des résultats persistés
const ninjaGeneratedAt = ref(null)
const ninjaError       = ref('')
const ninjaSelectedNode = ref(null)    // profil sélectionné dans le réseau
const ninjaCopied       = ref({})      // { profileKey: true }

const ninjaTotalProfiles = computed(() =>
    ninjaCompanies.value.reduce((s, c) => s + (c.profiles?.length || 0), 0)
)

const loadNinjaResults = async () => {
    ninjaLoading.value = true
    ninjaError.value = ''
    try {
        const r = await authFetch('/api/workflows/network-ninja/results')
        const j = await r.json()
        if (j.status === 'success' && j.data) {
            ninjaCompanies.value   = j.data.companies || []
            ninjaGeneratedAt.value = j.data.generated_at
        }
    } catch(e) {
        console.warn('[NetworkNinja] Load error', e)
    } finally {
        ninjaLoading.value = false
    }
}

const runNinja = async () => {
    ninjaRunning.value = true
    ninjaError.value = ''
    try {
        const r = await authFetch('/api/workflows/network-ninja/run', { method: 'POST' })
        const j = await r.json()
        if (j.status === 'success' && j.data) {
            ninjaCompanies.value   = j.data.companies || []
            ninjaGeneratedAt.value = j.data.generated_at
        } else {
            ninjaError.value = 'Erreur lors du scan. Réessayez.'
        }
    } catch(e) {
        ninjaError.value = 'Erreur réseau.'
    } finally {
        ninjaRunning.value = false
    }
}

const copyNinjaMessage = async (msg, key) => {
    try {
        await navigator.clipboard.writeText(msg)
        ninjaCopied.value = { ...ninjaCopied.value, [key]: true }
        setTimeout(() => { ninjaCopied.value = { ...ninjaCopied.value, [key]: false } }, 2500)
    } catch(e) {}
}

const formatNinjaDate = (iso) => {
    if (!iso) return ''
    return new Date(iso).toLocaleDateString('fr-FR', { day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' })
}

onMounted(() => {
    loadContacts()
    fetchProfile()
    loadNinjaResults()
})

// ── Graph Positioning Helpers ──
const getCompanyX = (i, total) => {
    const angle = (i / total) * Math.PI * 2 - Math.PI / 2
    const radius = 180 // Distance from center
    return Math.cos(angle) * radius
}
const getCompanyY = (i, total) => {
    const angle = (i / total) * Math.PI * 2 - Math.PI / 2
    const radius = 180
    return Math.sin(angle) * radius
}
const getProfileX = (ci, pi, cTotal, pTotal) => {
    const cX = getCompanyX(ci, cTotal)
    // Angle of company relative to center
    const baseAngle = (ci / cTotal) * Math.PI * 2 - Math.PI / 2
    // Spread profiles around company in an arc outwards
    const spread = Math.PI / 2
    const startAngle = baseAngle - spread / 2
    const step = pTotal > 1 ? spread / (pTotal - 1) : 0
    const angle = startAngle + step * pi
    const radius = 80 // Distance from company
    return cX + Math.cos(angle) * radius
}
const getProfileY = (ci, pi, cTotal, pTotal) => {
    const cY = getCompanyY(ci, cTotal)
    const baseAngle = (ci / cTotal) * Math.PI * 2 - Math.PI / 2
    const spread = Math.PI / 2
    const startAngle = baseAngle - spread / 2
    const step = pTotal > 1 ? spread / (pTotal - 1) : 0
    const angle = startAngle + step * pi
    const radius = 80
    return cY + Math.sin(angle) * radius
}

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
        toastState.addToast(t('common.error'), "error")
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
        toastState.addToast(t('common.error'), "error")
    } finally {
        isHunting.value = false
    }
}

const selectHr = (name) => {
    selectedHrName.value = name
}

const draftEmail = async () => {
    if (!companyName.value) {
        draftError.value = t('network_osint.company_required')
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
                company_name: companyName.value,
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
            toastState.addToast(t('common.success'))
        } else {
            draftError.value = json.detail || t('common.error')
            toastState.addToast(draftError.value, "error")
        }
    } catch(e) {
        draftError.value = t('common.network_error')
        toastState.addToast(t('common.network_error'), "error")
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
    <div class="relative mb-12 rounded-[2.5rem] overflow-hidden bg-white border border-slate-100 p-8 md:p-12 shadow-sm">
        <div class="absolute top-0 right-0 w-1/2 h-full bg-gradient-to-l from-[#E85D3E]/5 via-[#E85D3E]/2 to-transparent pointer-events-none"></div>
        <div class="absolute -bottom-24 -left-24 w-96 h-96 bg-indigo-500/5 rounded-full blur-[100px] pointer-events-none"></div>
        
        <div class="relative z-10 max-w-2xl">
            <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#E85D3E]/10 border border-[#E85D3E]/20 text-[#E85D3E] text-[10px] font-black tracking-[0.2em] uppercase mb-6">
                 <span class="flex h-2 w-2 relative">
                    <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#E85D3E] opacity-75"></span>
                    <span class="relative inline-flex rounded-full h-2 w-2 bg-[#E85D3E]"></span>
                 </span>
                 {{ t('network_osint.tagline') }}
            </div>
            <h1 class="text-4xl md:text-6xl font-black text-slate-900 tracking-tight leading-[1.1] mb-6">
                {{ t('network_osint.title_part1') }} <span class="text-transparent bg-clip-text bg-gradient-to-r from-[#E85D3E] to-rose-400">{{ t('network_osint.title_part2') }}</span>
            </h1>
            <p class="text-slate-500 text-lg font-medium leading-relaxed">
                {{ t('network_osint.description') }}
            </p>
        </div>
    </div>
    <!-- Enhanced Tabs -->
    <div class="flex items-center gap-2 mb-10 bg-slate-100 p-1.5 rounded-2xl border border-slate-200 w-fit mx-auto md:mx-0 flex-wrap">
        <button 
            @click="activeTab = 'osint'"
            :class="activeTab === 'osint' ? 'bg-white text-[#E85D3E] shadow-sm' : 'text-slate-500 hover:text-slate-700'"
            class="px-6 py-2.5 rounded-xl text-sm font-black transition-all flex items-center gap-2"
        >
            <SparklesIcon class="w-4 h-4" />
            {{ t('network_osint.tabs.osint') }}
        </button>
        <button 
            @click="activeTab = 'headhunter'"
            :class="activeTab === 'headhunter' ? 'bg-white text-indigo-500 shadow-sm' : 'text-slate-500 hover:text-slate-700'"
            class="px-6 py-2.5 rounded-xl text-sm font-black transition-all flex items-center gap-2"
        >
            <MagnifyingGlassIcon class="w-4 h-4" />
            {{ t('network_osint.tabs.headhunter') }}
        </button>
        <button 
            @click="activeTab = 'carnet'"
            :class="activeTab === 'carnet' ? 'bg-white text-emerald-500 shadow-sm' : 'text-slate-500 hover:text-slate-700'"
            class="px-6 py-2.5 rounded-xl text-sm font-black transition-all flex items-center gap-2"
        >
            <BookOpenIcon class="w-4 h-4" />
            {{ t('network_osint.tabs.contacts') }}
        </button>
        <!-- Network Ninja tab -->
        <button 
            @click="activeTab = 'ninja'"
            :class="activeTab === 'ninja' ? 'bg-white text-purple-600 shadow-sm' : 'text-slate-500 hover:text-slate-700'"
            class="px-6 py-2.5 rounded-xl text-sm font-black transition-all flex items-center gap-2 relative"
        >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M13 10V3L4 14h7v7l9-11h-7z"/>
            </svg>
            Network Ninja
            <span v-if="ninjaTotalProfiles > 0"
              class="absolute -top-1.5 -right-1.5 min-w-[18px] h-[18px] px-1 bg-purple-600 text-white text-[9px] font-black rounded-full flex items-center justify-center">
              {{ ninjaTotalProfiles }}
            </span>
        </button>
    </div>
    <!-- Tab Content -->
    <div v-if="activeTab === 'osint'" class="space-y-12 animate-fade-in">
        <!-- OSINT Search Panel -->
        <div class="bg-white border border-slate-100 rounded-[2.5rem] p-8 md:p-10 shadow-sm relative overflow-hidden group">
            <div class="flex items-center gap-3 mb-8">
                <div class="p-2 bg-[#E85D3E]/10 rounded-xl">
                    <SparklesIcon class="w-5 h-5 text-[#E85D3E]" />
                </div>
                <h3 class="text-xl font-bold text-slate-900 tracking-tight">{{ t('network_osint.osint_form.title') }}</h3>
            </div>
            
            <form @submit.prevent="enrichCompany" class="flex flex-col md:flex-row gap-4">
                <div class="flex-1 relative group/input">
                    <BuildingOfficeIcon class="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400 group-focus-within/input:text-[#E85D3E] transition-colors" />
                    <input 
                        v-model="companyName"
                        type="text" 
                        :placeholder="t('network_osint.osint_form.placeholder')" 
                        class="w-full bg-slate-50 border border-slate-200 text-slate-900 rounded-2xl pl-12 pr-4 py-4 focus:ring-2 focus:ring-[#E85D3E]/20 focus:border-[#E85D3E] outline-none transition-all placeholder:text-slate-400 font-bold"
                        required
                    />
                </div>
                <button 
                    type="submit" 
                    :disabled="isEnriching"
                    class="bg-[#E85D3E] hover:bg-[#D44D2D] text-white font-black px-8 py-4 rounded-2xl transition-all shadow-lg shadow-[#E85D3E]/20 disabled:opacity-50 flex items-center justify-center gap-2 group/btn"
                >
                    <ArrowPathIcon v-if="isEnriching" class="w-5 h-5 animate-spin" />
                    <SparklesIcon v-else class="w-5 h-5 transition-transform group-hover/btn:rotate-12" />
                    {{ t('network_osint.osint_form.button') }}
                </button>
            </form>

            <div v-if="hasEnriched && hrProfiles.length > 0" class="mt-8 pt-8 border-t border-slate-100">
                <h4 class="text-[11px] font-black text-slate-400 uppercase tracking-[0.2em] mb-6">{{ t('network_osint.osint_identified') }}</h4>
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    <div 
                        v-for="hr in hrProfiles" 
                        :key="hr.url"
                        @click="selectHr(hr.name)"
                        :class="selectedHrName === hr.name ? 'border-[#E85D3E] bg-[#E85D3E]/5 ring-1 ring-[#E85D3E]/20' : 'border-slate-200 bg-white hover:border-[#E85D3E]/30'"
                        class="p-4 rounded-2xl border transition-all cursor-pointer group/card flex flex-col relative"
                    >
                        <div class="flex items-start justify-between mb-3">
                            <div class="p-2 bg-slate-50 rounded-lg border border-slate-100 group-hover/card:bg-[#E85D3E]/10 transition-colors">
                                <UserGroupIcon class="w-4 h-4 text-[#E85D3E]" />
                            </div>
                            <a 
                                v-if="hr.url" 
                                :href="hr.url" 
                                target="_blank" 
                                @click.stop
                                class="p-1.5 text-slate-400 hover:text-blue-500 bg-slate-50 rounded-lg border border-slate-100 hover:border-blue-500/30 transition-all"
                                title="Voir sur LinkedIn"
                            >
                                <LinkIcon class="w-3.5 h-3.5" />
                            </a>
                        </div>
                        <h5 class="text-sm font-bold text-slate-900 mb-1 group-hover/card:text-[#E85D3E] transition-colors">{{ hr.name }}</h5>
                        <p class="text-[11px] text-slate-500 line-clamp-2 leading-relaxed h-8">{{ hr.snippet || t('network_osint.osint_snippet_fallback') }}</p>
                        
                        <div v-if="selectedHrName === hr.name" class="absolute top-2 right-2 flex h-2 w-2">
                            <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#E85D3E] opacity-75"></span>
                            <span class="relative inline-flex rounded-full h-2 w-2 bg-[#E85D3E]"></span>
                        </div>
                    </div>
                </div>
            </div>
            <div v-else-if="hasEnriched && hrProfiles.length === 0" class="mt-8 pt-8 border-t border-slate-100 text-center">
                <p class="text-sm text-slate-400 italic">{{ t('network_osint.osint_empty') }}</p>
            </div>
        </div>

        <!-- Drafting Section -->
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-8 pb-20">
            <!-- Parameters -->
            <div class="lg:col-span-5 space-y-6">
                <div class="bg-white border border-slate-100 rounded-[2.5rem] p-8 shadow-sm">
                    <h3 class="text-lg font-bold text-slate-900 mb-6 flex items-center gap-2">
                        <PencilSquareIcon class="w-5 h-5 text-indigo-500" />
                        Paramètres de l'IA
                    </h3>
                    
                    <div class="space-y-5">
                        <div class="space-y-2">
                            <label class="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1">{{ t('network_osint.draft_panel.type_label') }}</label>
                            <div class="grid grid-cols-2 gap-2 p-1 bg-slate-50 rounded-xl border border-slate-100">
                                <button @click="requestType='emploi'" :class="requestType==='emploi' ? 'bg-white text-indigo-600 shadow-sm border border-slate-200' : 'text-slate-500'" class="py-2.5 rounded-lg text-xs font-black transition-all">{{ t('network_osint.draft_panel.job_request') }}</button>
                                <button @click="requestType='stage'" :class="requestType==='stage' ? 'bg-white text-indigo-600 shadow-sm border border-slate-200' : 'text-slate-500'" class="py-2.5 rounded-lg text-xs font-black transition-all">{{ t('network_osint.draft_panel.partnership') }}</button>
                            </div>
                        </div>

                        <div class="space-y-2">
                            <label class="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1">{{ t('nav_admin.status') }}</label>
                            <div class="relative group/input">
                                <UserIcon class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400 group-focus-within/input:text-indigo-500 transition-colors" />
                                <input v-model="selectedHrName" type="text" :placeholder="t('network_osint.draft_panel.name_placeholder').includes('placeholder') ? 'ex: Jean Dupont (RH)' : t('network_osint.draft_panel.name_placeholder')" class="w-full bg-slate-50 border border-slate-200 text-slate-900 rounded-xl pl-10 pr-4 py-3 text-sm focus:border-indigo-500 transition-all font-bold outline-none" />
                            </div>
                        </div>

                        <div class="space-y-2">
                            <label class="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1">{{ t('network_osint.draft_panel.target_label') }}</label>
                            <input v-model="targetDomain" type="text" :placeholder="t('network_osint.draft_panel.target_placeholder')" class="w-full bg-slate-50 border border-slate-200 text-slate-900 rounded-xl px-4 py-3 text-sm focus:border-indigo-500 transition-all font-bold outline-none" />
                        </div>

                        <button 
                            @click="draftEmail"
                            :disabled="isDrafting"
                            class="w-full bg-indigo-600 hover:bg-indigo-500 text-white font-black py-4 rounded-2xl transition-all shadow-lg shadow-indigo-600/20 disabled:opacity-50 flex items-center justify-center gap-2 mt-4"
                        >
                            <SparklesIcon v-if="!isDrafting" class="w-5 h-5" />
                            <ArrowPathIcon v-else class="w-5 h-5 animate-spin" />
                            {{ t('network_osint.draft_panel.button').toUpperCase() }}
                        </button>
                    </div>
                </div>
            </div>

            <!-- Result -->
            <div class="lg:col-span-7">
                <div class="bg-white border border-slate-100 rounded-[2.5rem] p-8 md:p-10 shadow-sm h-full flex flex-col min-h-[500px] relative overflow-hidden group/result">
                    <div class="absolute inset-0 bg-gradient-to-br from-indigo-500/[0.02] to-transparent pointer-events-none"></div>
                    
                    <div v-if="!draftResult && !isDrafting" class="flex-1 flex flex-col items-center justify-center text-center opacity-60 group-hover/result:opacity-80 transition-opacity">
                        <div class="w-20 h-20 rounded-full bg-slate-50 flex items-center justify-center mb-6">
                            <EnvelopeIcon class="w-10 h-10 text-slate-400" />
                        </div>
                        <h3 class="text-xl font-bold text-slate-500">{{ t('network_osint.draft_panel.waiting') }}</h3>
                        <p class="text-sm text-slate-400 max-w-xs mt-2">{{ t('network_osint.draft_panel.waiting_desc') }}</p>
                    </div>

                    <div v-else-if="isDrafting" class="flex-1 flex flex-col items-center justify-center text-center">
                        <div class="relative w-16 h-16 mb-6">
                            <div class="absolute inset-0 border-4 border-indigo-500/20 rounded-full"></div>
                            <div class="absolute inset-0 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin"></div>
                        </div>
                        <h3 class="text-xl font-bold text-slate-900 animate-pulse">{{ t('network_osint.draft_panel.drafting') }}</h3>
                        <p class="text-sm text-slate-500 mt-2">{{ t('network_osint.draft_panel.customizing') }}</p>
                    </div>

                    <div v-else-if="draftResult" class="flex flex-col h-full animate-fade-in">
                        <div class="flex items-center justify-between mb-8">
                            <div class="flex items-center gap-3">
                                <div class="w-10 h-10 rounded-xl bg-indigo-50 flex items-center justify-center border border-indigo-100">
                                    <CheckBadgeIcon class="w-6 h-6 text-indigo-500" />
                                </div>
                                <div>
                                    <h3 class="font-bold text-slate-900 tracking-tight leading-none mb-1">{{ t('network_osint.draft_panel.success_title') }}</h3>
                                    <p class="text-[10px] font-black text-slate-400 uppercase tracking-widest">GEMINI 2.0 FLASH // ULTRA-PERSONALIZED</p>
                                </div>
                            </div>
                            <button @click="copyDraftEmail" :class="draftCopied ? 'bg-indigo-500 text-white' : 'bg-slate-50 text-slate-600 hover:text-slate-900'" class="flex items-center gap-2 px-4 py-2 rounded-xl font-bold text-xs transition-all active:scale-95 shadow-sm border border-slate-200">
                                <CheckCircleIcon v-if="draftCopied" class="w-4 h-4" />
                                <ClipboardIcon v-else class="w-4 h-4" />
                                {{ draftCopied ? t('common.copied') : t('common.copy') }}
                            </button>
                        </div>

                        <div class="flex-1 space-y-4">
                            <div class="p-4 bg-slate-50 rounded-2xl border border-slate-100">
                                <p class="text-[10px] font-black text-indigo-500 uppercase tracking-widest mb-1.5 opacity-70">Objet :</p>
                                <p class="text-sm font-bold text-slate-900">{{ draftResult.subject }}</p>
                            </div>
                            <div class="p-6 bg-slate-50 rounded-3xl border border-slate-100 flex-1 font-medium italic text-slate-700 relative">
                                <p class="whitespace-pre-wrap leading-relaxed text-[15px]">{{ draftResult.body }}</p>
                                <!-- HUD element -->
                                <div class="absolute bottom-4 right-6 text-[10px] font-mono text-slate-400 opacity-50 select-none">GOLDARMY_AI_DRAFT_SYSTEM_V2</div>
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
        <div class="bg-white border border-slate-100 rounded-[2.5rem] p-8 md:p-10 shadow-sm relative overflow-hidden group">
            <div class="flex items-center gap-3 mb-8">
                <div class="p-2 bg-indigo-500/10 rounded-xl">
                    <MagnifyingGlassIcon class="w-5 h-5 text-indigo-500" />
                </div>
                <h3 class="text-xl font-bold text-slate-900 tracking-tight">{{ t('network_osint.hh_form.title') }}</h3>
            </div>
            
            <form @submit.prevent="findDecisionMakers" class="flex flex-col md:flex-row gap-4">
                <div class="flex-1 relative group/input">
                    <BuildingOfficeIcon class="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400 group-focus-within/input:text-indigo-500 transition-colors" />
                    <input 
                        v-model="hhCompanyName"
                        type="text" 
                        :placeholder="t('network_osint.hh_form.placeholder')" 
                        class="w-full bg-slate-50 border border-slate-200 text-slate-900 rounded-2xl pl-12 pr-4 py-4 focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 outline-none transition-all placeholder:text-slate-400 font-bold"
                        required
                    />
                </div>
                <button 
                    type="submit" 
                    :disabled="isHunting"
                    class="bg-indigo-600 hover:bg-indigo-500 text-white font-black px-8 py-4 rounded-2xl transition-all shadow-lg shadow-indigo-600/20 disabled:opacity-50 flex items-center justify-center gap-2 group/btn"
                >
                    <ArrowPathIcon v-if="isHunting" class="w-5 h-5 animate-spin" />
                    <MagnifyingGlassIcon v-else class="w-5 h-5 transition-transform group-hover/btn:scale-110" />
                    {{ t('network_osint.hh_form.button').toUpperCase() }}
                </button>
            </form>
        </div>

        <!-- Headhunter Results Grid -->
        <div v-if="hasHunted" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 pb-20">
            <div v-if="decisionMakers.length === 0" class="col-span-full text-center text-slate-400 py-12 bg-slate-50 rounded-2xl border border-slate-200 border-dashed">
                {{ t('network_osint.hh_form.empty') }}
            </div>
            
            <div 
                v-for="(maker, idx) in decisionMakers" 
                :key="idx"
                class="bg-white border border-slate-200 rounded-3xl p-6 hover:border-indigo-500/50 transition-all flex flex-col group shadow-sm hover:translate-y-[-4px]"
            >
                <div class="flex items-start justify-between mb-4">
                    <div class="w-12 h-12 rounded-[1.2rem] bg-gradient-to-br from-indigo-50 to-purple-50 border border-indigo-100 flex items-center justify-center shrink-0">
                        <span class="text-lg font-black text-indigo-500">{{ maker.name.charAt(0) }}</span>
                    </div>
                    <a 
                        v-if="maker.linkedin_url" 
                        :href="maker.linkedin_url" 
                        target="_blank" 
                        class="text-slate-400 hover:text-blue-500 bg-slate-50 p-2.5 rounded-xl border border-slate-100 transition-colors shadow-inner"
                        title="Voir sur LinkedIn"
                    >
                        <LinkIcon class="w-4 h-4" />
                    </a>
                </div>
                
                <h3 class="text-lg font-bold text-slate-900 mb-1 group-hover:text-indigo-600 transition-colors tracking-tight">{{ maker.name }}</h3>
                <p class="text-xs font-bold text-indigo-500/70 mb-2 uppercase tracking-tight">{{ maker.role }}</p>
                <p class="text-[11px] text-slate-500 line-clamp-2 leading-relaxed h-8 mb-6 italic">{{ maker.snippet || t('network_osint.osint_snippet_fallback') }}</p>
                
                <button 
                    @click="activeTab='osint'; companyName=hhCompanyName; selectedHrName=maker.name; requestType='emploi';"
                    class="w-full bg-slate-50 hover:bg-indigo-50 text-slate-500 hover:text-indigo-600 border border-slate-200 hover:border-indigo-200 font-black py-3 rounded-xl transition-all flex items-center justify-center gap-2 text-xs uppercase tracking-widest"
                >
                    <EnvelopeIcon class="w-4 h-4" />
                    {{ t('network_osint.hh_form.prepare_cta') }}
                </button>
            </div>
        </div>
    </div>

    <!-- Contenu Carnet d'Adresses -->
    <div v-else-if="activeTab === 'carnet'" class="animate-fade-in pb-20">
        <!-- Header -->
        <div class="flex items-center justify-between mb-8">
            <div>
                <h2 class="text-2xl font-bold text-slate-900 tracking-tight">{{ t('network_osint.contacts_title_prefix') }} <span class="text-transparent bg-clip-text bg-gradient-to-r from-emerald-500 to-cyan-500">{{ t('network_osint.tabs.contacts') }}</span></h2>
                <p class="text-slate-500 text-sm mt-0.5 font-medium">{{ savedContacts.length }} {{ t('network_osint.companies_collected') }}</p>
            </div>
            <button @click="loadContacts" class="flex items-center gap-2 px-6 py-3 text-sm font-black text-slate-500 hover:text-slate-900 bg-white rounded-2xl border border-slate-200 hover:bg-slate-50 transition-all active:scale-95 shadow-sm">
                <ArrowPathIcon :class="isLoadingContacts ? 'animate-spin' : ''" class="w-4 h-4" />
                {{ t('common.refresh').toUpperCase() }}
            </button>
        </div>
        
        <!-- Empty State -->
        <div v-if="savedContacts.length === 0" class="bg-white border border-slate-100 rounded-[3rem] p-20 text-center relative overflow-hidden shadow-sm">
            <div class="absolute inset-0 bg-gradient-to-b from-emerald-500/[0.02] to-transparent pointer-events-none"></div>
            <div class="w-20 h-20 rounded-3xl bg-slate-50 flex items-center justify-center mx-auto mb-6 shadow-inner border border-slate-100">
                <BookOpenIcon class="w-10 h-10 text-slate-400" />
            </div>
            <h3 class="text-xl font-bold text-slate-900 mb-2">{{ t('network_osint.empty_contacts') }}</h3>
            <p class="text-slate-500 max-w-sm mx-auto text-sm leading-relaxed font-medium">
                {{ t('network_osint.empty_contacts_desc') }}
            </p>
        </div>
        
        <!-- Contact Cards Grid -->
        <div v-else class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
            <div 
                v-for="contact in savedContacts" 
                :key="contact.id"
                class="bg-white border border-slate-200 rounded-[2rem] p-6 hover:border-emerald-500/30 transition-all flex flex-col group shadow-sm hover:translate-y-[-4px]"
            >
                <!-- Card Header -->
                <div class="flex items-start gap-4 mb-5">
                    <div class="w-12 h-12 rounded-2xl bg-slate-50 border border-slate-100 flex items-center justify-center shrink-0 group-hover:bg-emerald-50 group-hover:border-emerald-200 transition-colors shadow-inner">
                        <BuildingOfficeIcon class="w-6 h-6 text-slate-400 group-hover:text-emerald-500 transition-colors" />
                    </div>
                    <div class="flex-1 min-w-0">
                        <h3 class="font-bold text-slate-900 text-lg truncate leading-tight group-hover:text-emerald-600 transition-colors">{{ contact.company_name }}</h3>
                        <p class="text-[11px] font-black text-slate-400 mt-1 uppercase tracking-widest">
                            Sync: {{ new Date(contact.last_updated).toLocaleDateString(t('locale') === 'locale' ? 'en-US' : (t('common.save') === 'Enregistrer' ? 'fr-FR' : 'en-US')) }}
                        </p>
                    </div>
                </div>

                <!-- Badge Row -->
                <div class="flex items-center gap-2 flex-wrap mb-5">
                    <span v-if="contact.category && contact.category !== 'Non catégorisée'" class="inline-flex items-center px-2.5 py-1 rounded-lg text-[10px] font-black uppercase tracking-widest bg-indigo-50 text-indigo-600 border border-indigo-100">
                        {{ contact.category }}
                    </span>
                    <span v-if="contact.emails && contact.emails.length > 0" class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-[10px] font-black uppercase tracking-widest bg-emerald-50 text-emerald-600 border border-emerald-100">
                        <EnvelopeIcon class="w-3.5 h-3.5" />
                        {{ contact.emails.length }} email{{ contact.emails.length > 1 ? 's' : '' }}
                    </span>
                    <span v-if="contact.phone" class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-[10px] font-black uppercase tracking-widest bg-amber-50 text-amber-600 border border-amber-100">
                        📞 Tel
                    </span>
                </div>

                <!-- Contact Details -->
                <div class="space-y-2.5 flex-1 mb-6">
                    <a v-if="contact.site_url" :href="contact.site_url" target="_blank"
                        class="flex items-center gap-3 p-3 rounded-2xl bg-slate-50 border border-slate-100 hover:border-blue-500/30 transition-all group/link shadow-inner">
                        <GlobeAltIcon class="w-4 h-4 text-blue-500 shrink-0" />
                        <span class="text-[13px] font-bold text-blue-500 group-hover/link:text-blue-600 truncate">
                            {{ contact.site_url.replace(/https?:\/\//, '').replace(/\/$/, '') }}
                        </span>
                    </a>

                    <div v-if="contact.phone" class="flex items-center gap-3 p-3 rounded-2xl bg-slate-50 border border-slate-100 shadow-inner">
                        <span class="text-sm">📞</span>
                        <span class="text-[13px] font-bold text-emerald-600 select-all">{{ contact.phone }}</span>
                    </div>

                    <div v-for="email in (contact.emails || [])" :key="email"
                        @click="navigator.clipboard?.writeText(email)"
                        class="flex items-center gap-3 p-3 rounded-2xl bg-slate-50 border border-slate-100 hover:border-emerald-500/30 cursor-pointer transition-all group/email shadow-inner">
                        <EnvelopeIcon class="w-4 h-4 text-slate-400 group-hover/email:text-emerald-500 transition-colors shrink-0" />
                        <span class="text-[13px] font-bold text-slate-600 group-hover/email:text-slate-900 truncate select-all">{{ email }}</span>
                    </div>
                </div>
                
                <button 
                    @click="prefillDraft(contact.company_name)"
                    class="w-full bg-slate-50 hover:bg-emerald-50 text-slate-600 hover:text-emerald-700 border border-slate-200 hover:border-emerald-300 font-black py-3 rounded-xl transition-all flex items-center justify-center gap-2 text-[11px] uppercase tracking-[0.2em]"
                >
                    <SparklesIcon class="w-4 h-4" />
                    {{ t('network_osint.draft_panel.button') }}
                </button>
            </div>
        </div>
    </div>

    <!-- ================================================================
         NETWORK NINJA TAB — Dark Mindmap Design
         ================================================================ -->
    <div v-else-if="activeTab === 'ninja'" class="relative w-full h-[700px] rounded-[2.5rem] bg-[#050505] overflow-hidden flex flex-col font-sans animate-fade-in shadow-xl mt-8">
        


        <!-- Background Grid / Stars -->
        <div class="absolute inset-0 ninja-dark-bg pointer-events-none opacity-40"></div>
        
        <!-- Header (Internal to canvas) -->
        <div class="absolute top-6 left-6 z-10 flex items-center gap-4">
            <div class="flex items-center gap-2 px-4 py-2 bg-neutral-900/80 border border-neutral-800 rounded-2xl backdrop-blur-md text-sm text-neutral-300 font-medium">
                <span class="text-[#E85D3E] font-black">🥷</span>
                <span class="text-white font-bold tracking-wide">Network Ninja</span>
                <span class="text-neutral-500 ml-2">Scanner Actif</span>
            </div>
            
            <div v-if="ninjaTotalProfiles > 0" class="px-3 py-1.5 bg-[#E85D3E]/10 border border-[#E85D3E]/30 rounded-full flex items-center gap-2">
                <span class="w-2 h-2 rounded-full bg-[#E85D3E] animate-pulse"></span>
                <span class="text-xs font-bold text-[#E85D3E]">{{ ninjaTotalProfiles }} décideur(s) identifié(s)</span>
            </div>
        </div>

        <!-- Run button inside canvas (Optional, to reload) -->
        <button @click="runNinja" :disabled="ninjaRunning" class="absolute top-6 right-6 z-10 px-4 py-2 bg-neutral-900 border border-neutral-800 hover:border-[#E85D3E] text-white rounded-xl text-sm font-bold transition-all flex items-center gap-2 group shadow-lg">
            <svg v-if="ninjaRunning" class="w-4 h-4 animate-spin text-[#E85D3E]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>
            <svg v-else class="w-4 h-4 text-neutral-400 group-hover:text-[#E85D3E] transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>
            Relancer
        </button>

        <!-- SVG Mindmap -->
        <div class="absolute inset-0 flex items-center justify-center overflow-visible">
            <svg class="w-full h-full overflow-visible" viewBox="-400 -300 800 600">
                <defs>
                    <filter id="glow-orange">
                        <feGaussianBlur stdDeviation="4" result="coloredBlur"/>
                        <feMerge><feMergeNode in="coloredBlur"/><feMergeNode in="SourceGraphic"/></feMerge>
                    </filter>
                    <filter id="glow-white">
                        <feGaussianBlur stdDeviation="5" result="coloredBlur"/>
                        <feMerge><feMergeNode in="coloredBlur"/><feMergeNode in="SourceGraphic"/></feMerge>
                    </filter>
                </defs>

                <!-- Edges -->
                <g class="ninja-edges">
                    <template v-for="(company, ci) in ninjaCompanies" :key="'edge-c-'+ci">
                        <!-- Moi -> Company -->
                        <line x1="0" y1="0" 
                              :x2="getCompanyX(ci, ninjaCompanies.length)" 
                              :y2="getCompanyY(ci, ninjaCompanies.length)"
                              stroke="#E85D3E" stroke-width="1.5" opacity="0.4" class="ninja-anim-edge" />
                              
                        <!-- Company -> Profiles -->
                        <template v-for="(profile, pi) in company.profiles" :key="'edge-p-'+ci+'-'+pi">
                            <line :x1="getCompanyX(ci, ninjaCompanies.length)" 
                                  :y1="getCompanyY(ci, ninjaCompanies.length)"
                                  :x2="getProfileX(ci, pi, ninjaCompanies.length, company.profiles.length)" 
                                  :y2="getProfileY(ci, pi, ninjaCompanies.length, company.profiles.length)"
                                  stroke="#a3a3a3" stroke-width="0.5" opacity="0.3" class="ninja-anim-edge" />
                        </template>
                    </template>
                </g>

                <!-- Nodes -->
                <g class="ninja-nodes">
                    <!-- Central Node (Moi) -->
                    <circle cx="0" cy="0" r="10" fill="#ffffff" filter="url(#glow-white)" />
                    <circle cx="0" cy="0" r="4" fill="#ffffff" />
                    
                    <!-- Companies & Profiles -->
                    <template v-for="(company, ci) in ninjaCompanies" :key="'node-c-'+ci">
                        <!-- Company Group (Floating) -->
                        <g class="ninja-float" :style="{ animationDelay: ci * 0.2 + 's' }">
                            <!-- Company Node -->
                            <circle :cx="getCompanyX(ci, ninjaCompanies.length)" 
                                    :cy="getCompanyY(ci, ninjaCompanies.length)" 
                                    r="8" fill="#E85D3E" class="cursor-pointer transition-transform hover:scale-150 ninja-anim-node" />
                            <!-- Company Label -->
                            <g :transform="`translate(${getCompanyX(ci, ninjaCompanies.length) + 14}, ${getCompanyY(ci, ninjaCompanies.length) - 10})`">
                                <rect width="130" height="24" rx="12" fill="#171717" stroke="#333333" stroke-width="1" />
                                <text x="12" y="16" fill="#f5f5f5" font-size="10" font-family="sans-serif" font-weight="600">{{ company.company_name.substring(0,18) }}</text>
                            </g>

                            <!-- Profile Nodes -->
                            <template v-for="(profile, pi) in company.profiles" :key="'node-p-'+ci+'-'+pi">
                                <circle :cx="getProfileX(ci, pi, ninjaCompanies.length, company.profiles.length)" 
                                        :cy="getProfileY(ci, pi, ninjaCompanies.length, company.profiles.length)" 
                                        r="5" fill="#a3a3a3" 
                                        class="cursor-pointer transition-all hover:fill-white hover:r-[7px]"
                                        @click.stop="ninjaSelectedNode = { ...profile, company_name: company.company_name, x: getProfileX(ci, pi, ninjaCompanies.length, company.profiles.length), y: getProfileY(ci, pi, ninjaCompanies.length, company.profiles.length), key: company.company_name + '_' + pi }" />
                                <!-- Profile Label -->
                                <g :transform="`translate(${getProfileX(ci, pi, ninjaCompanies.length, company.profiles.length) + 8}, ${getProfileY(ci, pi, ninjaCompanies.length, company.profiles.length) - 10})`">
                                    <rect width="100" height="20" rx="10" fill="#171717" stroke="#262626" stroke-width="1" />
                                    <text x="10" y="14" fill="#a3a3a3" font-size="9" font-family="sans-serif">{{ (profile.name || 'Profil').split(' ')[0] }}</text>
                                </g>
                            </template>
                        </g>
                    </template>
                </g>
            </svg>
        </div>

        <!-- Popover (Connected Topics style) -->
        <Transition name="fade">
            <div v-if="ninjaSelectedNode" 
                 class="absolute z-20 w-80 bg-[#121212] border border-[#262626] rounded-2xl shadow-2xl p-5 backdrop-blur-xl"
                 :style="{ left: `calc(50% + ${ninjaSelectedNode.x}px + 20px)`, top: `calc(50% + ${ninjaSelectedNode.y}px - 20px)` }">
                 
                 <!-- Close button -->
                 <button @click="ninjaSelectedNode = null" class="absolute top-4 right-4 text-neutral-500 hover:text-white">
                     <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
                 </button>

                 <!-- Date / Role -->
                 <p class="text-[#E85D3E] text-xs font-bold mb-3 tracking-wide uppercase">{{ ninjaSelectedNode.role }} @ {{ ninjaSelectedNode.company_name }}</p>
                 
                 <!-- Message Quote -->
                 <p class="text-neutral-200 text-sm leading-relaxed mb-6 font-serif italic border-l-2 border-[#E85D3E] pl-3">
                     "{{ ninjaSelectedNode.message }}"
                 </p>
                 
                 <p class="text-neutral-500 text-xs mb-2 uppercase tracking-widest font-bold">Actions</p>
                 
                 <!-- Action Links -->
                 <div class="space-y-1">
                     <a v-if="ninjaSelectedNode.linkedin_url" :href="ninjaSelectedNode.linkedin_url" target="_blank"
                        class="flex items-center justify-between p-3 rounded-xl hover:bg-[#1a1a1a] transition-colors group">
                         <div class="flex items-center gap-3">
                             <svg class="w-4 h-4 text-[#0A66C2]" fill="currentColor" viewBox="0 0 24 24"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>
                             <span class="text-sm font-medium text-neutral-300 group-hover:text-white">Ouvrir le profil</span>
                         </div>
                         <svg class="w-4 h-4 text-neutral-600 group-hover:text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/></svg>
                     </a>
                     
                     <button @click="copyNinjaMessage(ninjaSelectedNode.message, ninjaSelectedNode.key)"
                        class="w-full flex items-center justify-between p-3 rounded-xl hover:bg-[#1a1a1a] transition-colors group border border-transparent hover:border-[#E85D3E]/30">
                         <div class="flex items-center gap-3">
                             <svg class="w-4 h-4 text-neutral-400 group-hover:text-[#E85D3E]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"/></svg>
                             <span class="text-sm font-medium text-neutral-300 group-hover:text-white">Copier ({{ (ninjaSelectedNode.message || '').length }} car.)</span>
                         </div>
                         <svg v-if="ninjaCopied[ninjaSelectedNode.key]" class="w-4 h-4 text-[#E85D3E]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
                         <svg v-else class="w-4 h-4 text-neutral-600 group-hover:text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/></svg>
                     </button>
                 </div>
            </div>
        </Transition>

        <!-- Bottom Toolbar -->
        <div class="absolute bottom-8 left-1/2 -translate-x-1/2 flex items-center gap-2 p-2 bg-neutral-900/80 border border-neutral-800 rounded-full backdrop-blur-xl shadow-2xl">
            <button class="w-10 h-10 rounded-full flex items-center justify-center text-[#E85D3E] bg-[#E85D3E]/10 border border-[#E85D3E]/30 transition-colors">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4"/></svg>
            </button>
            <div class="w-px h-6 bg-neutral-800"></div>
            <button class="w-10 h-10 rounded-full flex items-center justify-center text-neutral-400 hover:text-white hover:bg-neutral-800 transition-colors">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v3m0 0v3m0-3h3m-3 0H7"/></svg>
            </button>
            <button class="w-10 h-10 rounded-full flex items-center justify-center text-neutral-400 hover:text-white hover:bg-neutral-800 transition-colors">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM13 10H7"/></svg>
            </button>
            <div class="w-px h-6 bg-neutral-800"></div>
            <button class="w-10 h-10 rounded-full flex items-center justify-center text-neutral-400 hover:text-white hover:bg-neutral-800 transition-colors">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg>
            </button>
        </div>
        
        <!-- Empty State Overlay -->
        <div v-if="!ninjaLoading && ninjaCompanies.length === 0 && !ninjaRunning" class="absolute inset-0 bg-[#050505]/90 backdrop-blur-sm z-40 flex flex-col items-center justify-center text-center">
            <div class="w-16 h-16 rounded-full bg-neutral-900 border border-neutral-800 flex items-center justify-center mb-4">
                <svg class="w-8 h-8 text-neutral-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
            </div>
            <p class="text-neutral-300 text-lg font-medium mb-2">Aucun réseau identifié</p>
            <p class="text-neutral-500 text-sm max-w-sm">Lancez le workflow Network Ninja depuis votre Dashboard pour commencer l'extraction.</p>
        </div>

        <!-- Loading / Scanning State Overlay -->
        <div v-if="ninjaRunning" class="absolute inset-0 bg-[#050505]/90 backdrop-blur-sm z-50 flex flex-col items-center justify-center text-center">
            <div class="relative w-24 h-24 mb-6">
                <div class="absolute inset-0 border-4 border-[#E85D3E]/20 rounded-full"></div>
                <div class="absolute inset-0 border-4 border-[#E85D3E] border-t-transparent rounded-full animate-spin"></div>
                <div class="absolute inset-0 flex items-center justify-center text-3xl">🥷</div>
            </div>
            <p class="text-[#E85D3E] text-lg font-black tracking-widest uppercase animate-pulse">Extraction en cours</p>
            <p class="text-neutral-400 text-sm mt-2 max-w-xs">Analyse des candidatures et ciblage des décideurs LinkedIn...</p>
        </div>
    </div>

    <!-- Loading Modal for Drafting -->

    <div v-if="isDrafting" class="fixed inset-0 z-[100] flex items-center justify-center p-4">
        <div class="absolute inset-0 bg-white/80 backdrop-blur-md animate-fade-in"></div>
        <div class="relative bg-white border border-slate-100 rounded-[2.5rem] p-10 shadow-2xl max-w-sm w-full text-center animate-fade-in-up">
            <div class="relative w-24 h-24 mx-auto mb-8">
                <div class="absolute inset-0 border-4 border-indigo-100 rounded-full"></div>
                <div class="absolute inset-0 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin"></div>
                <div class="absolute inset-0 flex items-center justify-center">
                    <SparklesIcon class="w-10 h-10 text-indigo-500 animate-pulse" />
                </div>
            </div>
            <h3 class="text-2xl font-black text-slate-900 mb-3">{{ t('network_osint.loading_title') }}</h3>
            <p class="text-slate-500 font-medium leading-relaxed">
                {{ t('network_osint.loading_desc') }}
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

/* ── Network Ninja animations ── */
.ninja-dot {
  animation: ninja-bounce 0.8s ease-in-out infinite alternate;
}
@keyframes ninja-bounce {
  from { transform: translateY(0); opacity: 0.5; }
  to   { transform: translateY(-8px); opacity: 1; }
}

.ninja-pulse-ring {
  animation: ninja-ring 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
  border: 3px solid #a855f7;
}
@keyframes ninja-ring {
  0%  { transform: scale(1);   opacity: 0.8; }
  50% { transform: scale(1.3); opacity: 0.2; }
  100%{ transform: scale(1);   opacity: 0.8; }
}

.ninja-grid {
  background-image:
    linear-gradient(rgba(168, 85, 247, 0.08) 1px, transparent 1px),
    linear-gradient(90deg, rgba(168, 85, 247, 0.08) 1px, transparent 1px);
  background-size: 32px 32px;
}

.ninja-edge {
  animation: ninja-dash 3s linear infinite;
}
@keyframes ninja-dash {
  from { stroke-dashoffset: 0; }
  to   { stroke-dashoffset: -40; }
}

.ninja-profile-node {
  animation: ninja-node-pulse 2.5s ease-in-out infinite;
  transform-origin: center;
  transform-box: fill-box;
}
@keyframes ninja-node-pulse {
  0%, 100% { r: 16; }
  50%       { r: 18; }
}

/* Ninja Animation Styles */
@keyframes dash-ninja {
  to { stroke-dashoffset: -20; }
}
@keyframes pulse-glow-ninja {
  0%, 100% { filter: drop-shadow(0 0 4px rgba(232, 93, 62, 0.4)); transform: scale(1); }
  50% { filter: drop-shadow(0 0 10px rgba(232, 93, 62, 0.8)); transform: scale(1.1); }
}
@keyframes float-node-ninja {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-3px); }
}
.ninja-anim-edge {
  stroke-dasharray: 4,4;
  animation: dash-ninja 2s linear infinite;
}
.ninja-anim-node {
  transform-origin: center;
  animation: pulse-glow-ninja 3s infinite ease-in-out;
  transform-box: fill-box;
}
.ninja-float {
  animation: float-node-ninja 4s infinite ease-in-out;
}

</style>
