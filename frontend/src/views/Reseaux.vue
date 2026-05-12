<script setup>
import { authFetch } from '../utils/auth'
import { ref, onMounted, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { toastState } from '../store/toastState'
import {
  BuildingOfficeIcon, UserGroupIcon, EnvelopeIcon, SparklesIcon,
  CheckBadgeIcon, LinkIcon, ArrowPathIcon, ClipboardIcon,
  CheckCircleIcon, PencilSquareIcon, UserIcon, DocumentDuplicateIcon, CheckIcon
} from '@heroicons/vue/24/outline'

const { t } = useI18n()

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
    fetchProfile()
    loadNinjaResults()
})


// ── Ninja SVG Node positioning helpers ──
const ninjaNodeX = (i, total, radius) => {
    const angle = (i / total) * Math.PI * 2 - Math.PI / 2
    return 500 + Math.cos(angle) * radius
}
const ninjaNodeY = (i, total, radius) => {
    const angle = (i / total) * Math.PI * 2 - Math.PI / 2
    return 340 + Math.sin(angle) * radius
}
const ninjaProfileX = (ci, pi, cTotal, pTotal) => {
    const cx = ninjaNodeX(ci, cTotal, 210)
    const baseAngle = (ci / cTotal) * Math.PI * 2 - Math.PI / 2
    const spread = Math.PI / 2.2
    const step = pTotal > 1 ? spread / (pTotal - 1) : 0
    const angle = baseAngle - spread / 2 + step * pi
    return cx + Math.cos(angle) * 95
}
const ninjaProfileY = (ci, pi, cTotal, pTotal) => {
    const cy = ninjaNodeY(ci, cTotal, 210)
    const baseAngle = (ci / cTotal) * Math.PI * 2 - Math.PI / 2
    const spread = Math.PI / 2.2
    const step = pTotal > 1 ? spread / (pTotal - 1) : 0
    const angle = baseAngle - spread / 2 + step * pi
    return cy + Math.sin(angle) * 95
}

const ninjaHoverNode = ref(null)
const ninjaTooltipX = ref(0)
const ninjaTooltipY = ref(0)
let ninjaHideTimer = null

const showNinjaTooltip = (e, profile) => {
    if (ninjaHideTimer) { clearTimeout(ninjaHideTimer); ninjaHideTimer = null }
    ninjaHoverNode.value = profile
    let x = e.clientX + 20
    let y = e.clientY - 30
    if (x + 290 > window.innerWidth) x = e.clientX - 310
    if (y + 320 > window.innerHeight) y = e.clientY - 320
    ninjaTooltipX.value = x
    ninjaTooltipY.value = y
}
const scheduleHideTooltip = () => {
    ninjaHideTimer = setTimeout(() => { ninjaHoverNode.value = null }, 200)
}
const cancelHideTooltip = () => {
    if (ninjaHideTimer) { clearTimeout(ninjaHideTimer); ninjaHideTimer = null }
}

// ── Ninja Pan/Zoom Navigation ──
const ninjaSvgEl = ref(null)
const ninjaPanX = ref(0)
const ninjaPanY = ref(0)
const ninjaScale = ref(1)
const ninjaDragging = ref(false)
let ninjaDragStart = { x: 0, y: 0, panX: 0, panY: 0 }

const ninjaResetView = () => {
    ninjaPanX.value = 0
    ninjaPanY.value = 0
    ninjaScale.value = 1
}

const ninjaZoom = (delta) => {
    ninjaScale.value = Math.min(3, Math.max(0.3, ninjaScale.value + delta))
}

const ninjaPanStart = (e) => {
    ninjaDragging.value = true
    ninjaDragStart = { x: e.clientX, y: e.clientY, panX: ninjaPanX.value, panY: ninjaPanY.value }
}

const ninjaPanMove = (e) => {
    if (!ninjaDragging.value) return
    ninjaPanX.value = ninjaDragStart.panX + (e.clientX - ninjaDragStart.x)
    ninjaPanY.value = ninjaDragStart.panY + (e.clientY - ninjaDragStart.y)
}

const ninjaPanEnd = () => { ninjaDragging.value = false }

const ninjaWheel = (e) => {
    const delta = e.deltaY > 0 ? -0.1 : 0.1
    ninjaScale.value = Math.min(3, Math.max(0.3, ninjaScale.value + delta))
}

const ninjaLabelX = (i, total, radius) => {
    const angle = (i / total) * Math.PI * 2 - Math.PI / 2
    const cx = 500 + Math.cos(angle) * radius
    // If node is on the right half, put label to the right; else to the left (with offset)
    return Math.cos(angle) >= 0 ? cx + 14 : cx - 162
}
// ── End Pan/Zoom ──
// ── End Ninja Helpers ──

const prefillDraft = (companyNameStr) => {
    companyName.value = companyNameStr
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

// ── Gold Profile Logic ──
const goldProfileStep = ref('audit')
const goldProfileLoading = ref(false)
const goldProfileAuditData = ref(null)
const goldProfilePlanData = ref([])
const goldProfilePostData = ref('')
const goldProfileSelectedTopic = ref(null)

const fetchGoldProfileAudit = async () => {
    goldProfileLoading.value = true
    try {
        const res = await authFetch('/api/network/gold-profile/audit', { method: 'POST' })
        const json = await res.json()
        if (json.status === 'success') {
            goldProfileAuditData.value = json.data
            goldProfileStep.value = 'audit'
            toastState.addToast("Audit LinkedIn terminé !", "success")
        } else {
            toastState.addToast(json.detail || json.content || "Erreur d'audit", "error")
        }
    } catch(e) {
        toastState.addToast("Erreur d'audit LinkedIn", "error")
    } finally {
        goldProfileLoading.value = false
    }
}

const fetchGoldProfilePlan = async () => {
    goldProfileLoading.value = true
    try {
        const res = await authFetch('/api/network/gold-profile/plan', { method: 'POST' })
        const json = await res.json()
        if (json.status === 'success') {
            goldProfilePlanData.value = json.data.plan || json.data
            goldProfileStep.value = 'plan'
        } else {
            toastState.addToast(json.detail || json.content || "Erreur de planification", "error")
        }
    } catch(e) {
        toastState.addToast("Erreur lors de la création du plan", "error")
    } finally {
        goldProfileLoading.value = false
    }
}

const generateGoldProfilePost = async (topic) => {
    goldProfileLoading.value = true
    goldProfileSelectedTopic.value = topic
    try {
        const res = await authFetch('/api/network/gold-profile/post', { 
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ topic: topic.topic })
        })
        const json = await res.json()
        if (json.status === 'success') {
            goldProfilePostData.value = json.data.post_content || json.data
            goldProfileStep.value = 'post'
        } else {
            toastState.addToast(json.detail || json.content || "Erreur de génération", "error")
        }
    } catch(e) {
        toastState.addToast("Erreur de génération de post", "error")
    } finally {
        goldProfileLoading.value = false
    }
}
// ────────────────────────

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
    try { await navigator.clipboard.writeText(text); draftCopied.value = true; setTimeout(() => draftCopied.value = false, 2500) } catch(e) {}
}

const copyToClipboard = async (text) => {
    try { await navigator.clipboard.writeText(text); toastState.addToast('Copié !') } catch(e) {}
}


</script>

<template>
  <div class="px-4 md:px-10 py-8 max-w-[1400px] mx-auto w-full animate-fade-in-up">
    
    <!-- Hero Header -->
    <div class="relative mb-12 rounded-[2.5rem] overflow-hidden bg-white border border-slate-100 p-8 md:p-12 shadow-sm">
        <div class="absolute top-0 right-0 w-1/2 h-full bg-gradient-to-l from-[#F59E0B]/5 via-[#F59E0B]/2 to-transparent pointer-events-none"></div>
        <div class="absolute -bottom-24 -left-24 w-96 h-96 bg-indigo-500/5 rounded-full blur-[100px] pointer-events-none"></div>
        
        <div class="relative z-10 max-w-2xl">
            <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#F59E0B]/10 border border-[#F59E0B]/20 text-[#F59E0B] text-[10px] font-black tracking-[0.2em] uppercase mb-6">
                 <span class="flex h-2 w-2 relative">
                    <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#F59E0B] opacity-75"></span>
                    <span class="relative inline-flex rounded-full h-2 w-2 bg-[#F59E0B]"></span>
                 </span>
                 {{ t('network_osint.tagline') }}
            </div>
            <h1 class="text-4xl md:text-6xl font-black text-slate-900 tracking-tight leading-[1.1] mb-6">
                {{ t('network_osint.title_part1') }} <span class="text-transparent bg-clip-text bg-gradient-to-r from-[#F59E0B] to-rose-400">{{ t('network_osint.title_part2') }}</span>
            </h1>
            <p class="text-slate-500 text-lg font-medium leading-relaxed">
                {{ t('network_osint.description') }}
            </p>
        </div>
    </div>
    <!-- ── Bento Grid: Headhunter + Gold Profile ── -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">

      <!-- ── Card 1: Agent Headhunter ── -->
      <div class="bg-white border border-slate-200 rounded-3xl shadow-sm overflow-hidden flex flex-col">
        <!-- Header -->
        <div class="px-6 py-5 border-b border-slate-100 flex items-center justify-between bg-gradient-to-r from-indigo-50 to-slate-50">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-xl bg-indigo-600 flex items-center justify-center shadow-sm shadow-indigo-200">
              <MagnifyingGlassIcon class="w-5 h-5 text-white" />
            </div>
            <div>
              <h3 class="font-black text-slate-800">{{ t('network_osint.hh_form.title') }}</h3>
              <p class="text-[10px] text-slate-400 uppercase tracking-wider">Décideurs LinkedIn · Ciblage IA</p>
            </div>
          </div>
        </div>

        <!-- Body -->
        <div class="p-6 flex flex-col flex-1">
          <!-- Search form -->
          <form @submit.prevent="findDecisionMakers" class="flex gap-3 mb-6">
            <div class="flex-1 relative">
              <BuildingOfficeIcon class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
              <input
                v-model="hhCompanyName"
                type="text"
                :placeholder="t('network_osint.hh_form.placeholder')"
                class="w-full bg-slate-50 border border-slate-200 text-slate-900 rounded-xl pl-10 pr-4 py-3 text-sm focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 outline-none transition-all font-bold"
                required
              />
            </div>
            <button
              type="submit"
              :disabled="isHunting"
              class="bg-indigo-600 hover:bg-indigo-500 text-white font-black px-5 py-3 rounded-xl transition-all shadow-md shadow-indigo-200 disabled:opacity-50 flex items-center gap-2 text-sm"
            >
              <ArrowPathIcon v-if="isHunting" class="w-4 h-4 animate-spin" />
              <MagnifyingGlassIcon v-else class="w-4 h-4" />
              {{ t('network_osint.hh_form.button') }}
            </button>
          </form>

          <!-- Results -->
          <div class="flex-1 overflow-y-auto" style="max-height: 420px;">
            <!-- Scanning -->
            <div v-if="isHunting" class="flex flex-col items-center justify-center py-12 gap-3">
              <div class="w-10 h-10 border-4 border-indigo-100 border-t-indigo-500 rounded-full animate-spin"></div>
              <p class="text-xs font-semibold text-slate-500">Chasse aux décideurs en cours...</p>
            </div>
            <!-- Empty state -->
            <div v-else-if="!hasHunted" class="flex flex-col items-center justify-center py-12 gap-3 text-center">
              <div class="w-14 h-14 bg-indigo-50 rounded-full flex items-center justify-center">
                <UsersIcon class="w-7 h-7 text-indigo-300" />
              </div>
              <p class="text-sm font-bold text-slate-600">Entrez un nom d'entreprise</p>
              <p class="text-xs text-slate-400">L'IA identifiera les décideurs clés (RH, CEO, Lead Dev…)</p>
            </div>
            <!-- No results -->
            <div v-else-if="decisionMakers.length === 0" class="flex flex-col items-center py-10 gap-2 text-center">
              <p class="text-sm text-slate-400 italic">{{ t('network_osint.hh_form.empty') }}</p>
            </div>
            <!-- Decision makers list -->
            <div v-else class="grid grid-cols-1 gap-3">
              <div
                v-for="(maker, idx) in decisionMakers"
                :key="idx"
                class="flex items-start gap-4 p-4 bg-slate-50 border border-slate-200 rounded-2xl hover:border-indigo-300 hover:bg-indigo-50/30 transition-all group"
              >
                <!-- Avatar -->
                <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-100 to-purple-100 border border-indigo-200 flex items-center justify-center shrink-0">
                  <span class="text-base font-black text-indigo-600">{{ maker.name.charAt(0) }}</span>
                </div>
                <!-- Info -->
                <div class="flex-1 min-w-0">
                  <p class="font-bold text-slate-800 text-sm truncate">{{ maker.name }}</p>
                  <p class="text-[10px] font-bold text-indigo-500 uppercase tracking-tight truncate">{{ maker.role }}</p>
                  <p class="text-[11px] text-slate-400 line-clamp-1 mt-0.5 italic">{{ maker.snippet || t('network_osint.osint_snippet_fallback') }}</p>
                </div>
                <!-- Actions -->
                <div class="flex flex-col gap-1 shrink-0">
                  <a v-if="maker.linkedin_url" :href="maker.linkedin_url" target="_blank"
                     class="p-1.5 bg-white border border-slate-200 rounded-lg text-slate-400 hover:text-blue-500 hover:border-blue-300 transition-colors">
                    <LinkIcon class="w-3.5 h-3.5" />
                  </a>
                  <button @click="companyName=hhCompanyName; selectedHrName=maker.name; requestType='emploi';"
                          class="p-1.5 bg-white border border-slate-200 rounded-lg text-slate-400 hover:text-indigo-500 hover:border-indigo-300 transition-colors"
                          :title="t('network_osint.hh_form.prepare_cta')">
                    <EnvelopeIcon class="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- ── Card 2: Gold Profile ── -->
      <div class="bg-white border border-slate-200 rounded-3xl shadow-sm overflow-hidden flex flex-col">
        <!-- Header -->
        <div class="px-6 py-5 border-b border-slate-100 flex items-center justify-between bg-gradient-to-r from-amber-50 to-orange-50">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-xl bg-amber-400 flex items-center justify-center shadow-sm shadow-amber-200">
              <SparklesIcon class="w-5 h-5 text-white" />
            </div>
            <div>
              <h3 class="font-black text-slate-800">✨ Gold Profile</h3>
              <p class="text-[10px] text-slate-500 uppercase tracking-wider">Audit IA · Plan 30 jours · Posts viraux</p>
            </div>
          </div>
          <button @click="fetchGoldProfileAudit" :disabled="goldProfileLoading"
                  class="px-4 py-2 text-xs font-black bg-amber-400 text-white rounded-xl hover:bg-amber-500 disabled:opacity-50 shadow-sm shadow-amber-200 transition-all">
            {{ goldProfileLoading ? 'Analyse...' : 'Auditer mon profil' }}
          </button>
        </div>

        <!-- Body -->
        <div class="p-6 flex-1 flex flex-col" style="min-height: 420px;">
          <!-- Loading -->
          <div v-if="goldProfileLoading" class="flex-1 flex flex-col items-center justify-center gap-3">
            <div class="w-10 h-10 border-4 border-amber-100 border-t-amber-400 rounded-full animate-spin"></div>
            <p class="text-xs font-semibold text-slate-500">L'IA analyse votre profil LinkedIn...</p>
          </div>

          <!-- Empty / CTA -->
          <div v-else-if="!goldProfileAuditData && goldProfileStep==='audit'" class="flex-1 flex flex-col items-center justify-center gap-4 text-center py-6">
            <div class="w-16 h-16 rounded-2xl bg-amber-50 flex items-center justify-center border border-amber-100">
              <SparklesIcon class="w-8 h-8 text-amber-400" />
            </div>
            <div>
              <p class="text-sm font-bold text-slate-700 mb-1">Audit LinkedIn IA</p>
              <p class="text-xs text-slate-400 max-w-[260px]">Obtenez votre score, un headline optimisé et un plan de contenu 30 jours personnalisé.</p>
            </div>
            <button @click="fetchGoldProfileAudit" class="px-5 py-2.5 bg-amber-400 text-white text-xs font-black rounded-xl hover:bg-amber-500 transition-all shadow-md shadow-amber-100">
              Lancer l'audit →
            </button>
          </div>

          <!-- Audit results -->
          <div v-else-if="goldProfileStep==='audit' && goldProfileAuditData" class="flex-1 flex flex-col gap-5">
            <!-- Score + headline -->
            <div class="flex items-center gap-4 p-4 bg-amber-50/50 rounded-2xl border border-amber-100">
              <div class="w-16 h-16 relative shrink-0">
                <svg class="w-16 h-16 -rotate-90" viewBox="0 0 64 64">
                  <circle cx="32" cy="32" r="28" stroke="#fef3c7" stroke-width="6" fill="none"/>
                  <circle cx="32" cy="32" r="28" stroke="#F59E0B" stroke-width="6" fill="none" stroke-linecap="round"
                    :stroke-dasharray="175.9" :stroke-dashoffset="175.9*(1-(goldProfileAuditData.profile_score||0)/100)" class="transition-all duration-1000"/>
                </svg>
                <div class="absolute inset-0 flex items-center justify-center">
                  <span class="text-base font-black text-slate-800">{{ goldProfileAuditData.profile_score }}</span>
                </div>
              </div>
              <div class="flex-1 min-w-0">
                <p class="text-[10px] font-black text-slate-400 uppercase tracking-wider mb-1">Score LinkedIn</p>
                <p class="font-bold text-slate-800 text-sm leading-snug">{{ goldProfileAuditData.headline }}</p>
                <button @click="copyToClipboard(goldProfileAuditData.headline)" class="mt-1 text-[10px] text-amber-600 font-bold hover:underline">
                  Copier le headline →
                </button>
              </div>
            </div>
            <!-- Optimizations -->
            <div class="space-y-2 flex-1 overflow-y-auto">
              <p class="text-[10px] font-black text-slate-400 uppercase tracking-wider mb-2">Optimisations recommandées</p>
              <div v-for="opt in (goldProfileAuditData.field_optimizations||[]).slice(0,4)" :key="opt.field"
                   class="flex items-start gap-2 p-3 bg-slate-50 rounded-xl border border-slate-100">
                <CheckBadgeIcon class="w-4 h-4 text-emerald-500 shrink-0 mt-0.5" />
                <div>
                  <p class="text-xs font-black text-slate-700">{{ opt.field }}</p>
                  <p class="text-[11px] text-slate-400 mt-0.5">{{ opt.recommendation || opt.suggestion }}</p>
                </div>
              </div>
            </div>
            <button @click="fetchGoldProfilePlan" class="w-full py-3 bg-slate-900 text-white text-xs font-black rounded-2xl hover:bg-slate-800 transition-colors">
              Voir la stratégie 30 jours →
            </button>
          </div>

          <!-- Plan 30 jours -->
          <div v-else-if="goldProfileStep==='plan'" class="flex-1 flex flex-col">
            <div class="flex items-center gap-2 mb-4">
              <button @click="goldProfileStep='audit'" class="text-xs text-indigo-600 font-bold">← Audit</button>
              <p class="text-xs font-black text-slate-700 uppercase tracking-wider">Plan 30 Jours</p>
            </div>
            <div class="grid grid-cols-3 gap-2 flex-1 overflow-y-auto content-start" style="max-height:380px;">
              <div v-for="item in goldProfilePlanData" :key="item.day"
                   @click="generateGoldProfilePost(item)"
                   class="p-3 bg-slate-50 border border-slate-200 rounded-xl hover:border-amber-400 cursor-pointer group transition-all">
                <span class="text-[10px] font-black text-amber-500 uppercase">Jour {{ item.day }}</span>
                <p class="text-[11px] font-bold text-slate-700 mt-1 group-hover:text-amber-600 transition-colors line-clamp-2">{{ item.topic }}</p>
              </div>
            </div>
          </div>

          <!-- Post généré -->
          <div v-else-if="goldProfileStep==='post'" class="flex-1 flex flex-col">
            <div class="flex items-center gap-2 mb-4">
              <button @click="goldProfileStep='plan'" class="text-xs text-indigo-600 font-bold">← Plan</button>
              <p class="text-xs font-black text-slate-700 uppercase tracking-wider truncate">{{ goldProfileSelectedTopic?.topic }}</p>
            </div>
            <div class="flex-1 bg-indigo-50 rounded-2xl p-4 text-sm text-slate-700 whitespace-pre-wrap font-medium leading-relaxed overflow-y-auto mb-4" style="max-height:300px;">
              {{ goldProfilePostData }}
            </div>
            <button @click="copyToClipboard(goldProfilePostData)"
                    class="w-full py-3 bg-amber-400 text-white text-xs font-black rounded-2xl hover:bg-amber-500 transition-colors flex items-center justify-center gap-2">
              <DocumentDuplicateIcon class="w-4 h-4" /> Copier le post
            </button>
          </div>
        </div>
      </div>

    </div>


    <!-- ── Section: Network Ninja ── -->
    <div class="relative w-full rounded-[2.5rem] overflow-hidden flex flex-col mb-12 shadow-2xl"
         style="height: 720px; background: #f8fafc; border: 1px solid #e2e8f0;">


        <!-- Header -->
        <div class="absolute top-5 left-6 z-20 flex items-center gap-3">
            <div class="flex items-center gap-2 px-4 py-2 rounded-2xl text-sm font-medium" style="background:white; border:1px solid #e2e8f0; box-shadow: 0 1px 2px rgba(0,0,0,0.05);">
                <span style="color:#F59E0B;" class="font-black">🥷</span>
                <span class="text-slate-800 font-bold tracking-wide">Network Ninja</span>
            </div>
            <div v-if="ninjaTotalProfiles > 0" class="px-3 py-1.5 rounded-full flex items-center gap-2" style="background:rgba(232,93,62,0.1); border:1px solid rgba(232,93,62,0.3);">
                <span class="w-2 h-2 rounded-full animate-pulse" style="background:#F59E0B;"></span>
                <span class="text-xs font-bold" style="color:#F59E0B;">{{ ninjaTotalProfiles }} décideur(s)</span>
            </div>
        </div>

        <!-- Relancer + Recenter -->
        <div class="absolute top-5 right-6 z-20 flex items-center gap-2">
            <button @click="ninjaResetView()"
                title="Recentrer"
                class="w-9 h-9 rounded-xl flex items-center justify-center transition-all"
                style="background:white; border:1px solid #e2e8f0; color:#64748b; box-shadow: 0 1px 2px rgba(0,0,0,0.05);">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4"/></svg>
            </button>
            <button @click="runNinja" :disabled="ninjaRunning"
                class="px-4 py-2 text-slate-800 rounded-xl text-sm font-bold transition-all flex items-center gap-2"
                style="background:white; border:1px solid #e2e8f0; box-shadow: 0 1px 2px rgba(0,0,0,0.05);">
                <svg v-if="ninjaRunning" class="w-4 h-4 animate-spin" style="color:#F59E0B;" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>
                <svg v-else class="w-4 h-4" style="color:#64748b;" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>
                {{ ninjaRunning ? 'Scan...' : 'Relancer' }}
            </button>
        </div>

        <!-- Pan/Zoom hint -->
        <div class="absolute bottom-5 left-6 z-20 flex items-center gap-2" style="color:#64748b; font-size:11px;">
            <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 15l-2 5L9 9l11 4-5 2zm0 0l5 5"/></svg>
            Glisser pour naviguer · Scroll pour zoomer
        </div>

        <!-- Zoom controls -->
        <div class="absolute bottom-4 right-6 z-20 flex flex-col gap-1.5">
            <button @click="ninjaZoom(0.15)" class="w-8 h-8 rounded-xl flex items-center justify-center transition-all" style="background:white; border:1px solid #e2e8f0; color:#64748b; box-shadow: 0 1px 2px rgba(0,0,0,0.05);">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg>
            </button>
            <button @click="ninjaZoom(-0.15)" class="w-8 h-8 rounded-xl flex items-center justify-center transition-all" style="background:white; border:1px solid #e2e8f0; color:#64748b; box-shadow: 0 1px 2px rgba(0,0,0,0.05);">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 12H4"/></svg>
            </button>
        </div>

        <!-- Pan/Zoom SVG -->
        <svg class="absolute inset-0 w-full h-full select-none"
             :class="ninjaDragging ? 'cursor-grabbing' : 'cursor-grab'"
             @mousedown.prevent="ninjaPanStart"
             @mousemove.prevent="ninjaPanMove"
             @mouseup="ninjaPanEnd"
             @mouseleave="ninjaPanEnd"
             @wheel.prevent="ninjaWheel"
             ref="ninjaSvgEl">

            <!-- Transformed group (pan + zoom) -->
            <g :transform="`translate(${ninjaPanX}, ${ninjaPanY}) scale(${ninjaScale})`">

                <!-- Background particle dots -->
                <circle v-for="i in 50" :key="'bg-'+i"
                    :cx="((i * 139.5) % 960) - 80"
                    :cy="((i * 89.1) % 660) - 30"
                    :r="i % 4 === 0 ? 1.8 : 0.9"
                    fill="#94a3b8"
                    :opacity="0.15 + (i%4)*0.05" />

                <template v-if="ninjaCompanies.length > 0">

                    <!-- Center → Company edges -->
                    <template v-for="(company, ci) in ninjaCompanies" :key="'ec-'+ci">
                        <line x1="500" y1="340"
                            :x2="ninjaNodeX(ci, ninjaCompanies.length, 210)"
                            :y2="ninjaNodeY(ci, ninjaCompanies.length, 210)"
                            stroke="#F59E0B" stroke-width="1.2" opacity="0.3"
                            stroke-dasharray="6,5" class="ninja-edge-anim" />
                    </template>

                    <!-- Company → Profile edges -->
                    <template v-for="(company, ci) in ninjaCompanies" :key="'ep-'+ci">
                        <template v-for="(prof, pi) in company.profiles" :key="'ep-'+ci+'-'+pi">
                            <line
                                :x1="ninjaNodeX(ci, ninjaCompanies.length, 210)"
                                :y1="ninjaNodeY(ci, ninjaCompanies.length, 210)"
                                :x2="ninjaProfileX(ci, pi, ninjaCompanies.length, company.profiles.length)"
                                :y2="ninjaProfileY(ci, pi, ninjaCompanies.length, company.profiles.length)"
                                stroke="rgba(0,0,0,0.12)" stroke-width="1"
                                stroke-dasharray="3,4" class="ninja-edge-anim-slow" />
                        </template>
                    </template>

                    <!-- Company nodes -->
                    <template v-for="(company, ci) in ninjaCompanies" :key="'nc-'+ci">
                        <!-- Pulse ring -->
                        <circle :cx="ninjaNodeX(ci, ninjaCompanies.length, 210)"
                                :cy="ninjaNodeY(ci, ninjaCompanies.length, 210)"
                                r="20" fill="none"
                                stroke="#F59E0B" stroke-width="1.5" opacity="0.15"
                                class="ninja-pulse-ring"
                                :style="{ animationDelay: ci * 0.4 + 's' }" />
                        <!-- Dot -->
                        <circle :cx="ninjaNodeX(ci, ninjaCompanies.length, 210)"
                                :cy="ninjaNodeY(ci, ninjaCompanies.length, 210)"
                                r="9" fill="#F59E0B">
                            <animate attributeName="r" values="8;10;8" dur="3s" repeatCount="indefinite"
                                :begin="ci * 0.4 + 's'" />
                        </circle>
                        <!-- Glow -->
                        <circle :cx="ninjaNodeX(ci, ninjaCompanies.length, 210)"
                                :cy="ninjaNodeY(ci, ninjaCompanies.length, 210)"
                                r="5" fill="rgba(255,255,255,0.8)" class="pointer-events-none" />

                        <!-- Company label pill (foreignObject) -->
                        <foreignObject
                            :x="ninjaLabelX(ci, ninjaCompanies.length, 210)"
                            :y="ninjaNodeY(ci, ninjaCompanies.length, 210) - 14"
                            width="148" height="28" class="pointer-events-none">
                            <div xmlns="http://www.w3.org/1999/xhtml"
                                 style="background:rgba(255,255,255,0.95); border:1px solid rgba(232,93,62,0.3); border-radius:14px; padding:4px 11px; font-size:11px; font-weight:700; color:#334155; box-shadow: 0 2px 4px rgba(0,0,0,0.05); font-family:sans-serif; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; max-width:140px; letter-spacing:0.01em;">
                                {{ company.company_name }}
                            </div>
                        </foreignObject>

                        <!-- Profile nodes -->
                        <template v-for="(prof, pi) in company.profiles" :key="'np-'+ci+'-'+pi">
                            <!-- Large hover target -->
                            <circle
                                :cx="ninjaProfileX(ci, pi, ninjaCompanies.length, company.profiles.length)"
                                :cy="ninjaProfileY(ci, pi, ninjaCompanies.length, company.profiles.length)"
                                r="18" fill="transparent" class="cursor-pointer"
                                @mouseenter.stop="showNinjaTooltip($event, { ...prof, company_name: company.company_name, key: company.company_name+'_'+pi })"
                                @mouseleave.stop="scheduleHideTooltip()" />
                            <!-- Visible dot -->
                            <circle
                                :cx="ninjaProfileX(ci, pi, ninjaCompanies.length, company.profiles.length)"
                                :cy="ninjaProfileY(ci, pi, ninjaCompanies.length, company.profiles.length)"
                                :r="ninjaHoverNode && ninjaHoverNode.key === company.company_name+'_'+pi ? 7 : 5"
                                :fill="ninjaHoverNode && ninjaHoverNode.key === company.company_name+'_'+pi ? '#0f172a' : '#cbd5e1'"
                                class="pointer-events-none transition-all" />
                            <!-- Profile name -->
                            <text
                                :x="ninjaProfileX(ci, pi, ninjaCompanies.length, company.profiles.length) + 9"
                                :y="ninjaProfileY(ci, pi, ninjaCompanies.length, company.profiles.length) + 4"
                                font-size="9" fill="#64748b"
                                font-family="sans-serif" class="pointer-events-none font-medium">
                                {{ (prof.name || '').split(' ')[0] }}
                            </text>
                        </template>
                    </template>

                    <!-- Central node (always rendered on top) -->
                    <circle cx="500" cy="340" r="30" fill="rgba(0,0,0,0.03)" />
                    <circle cx="500" cy="340" r="20" fill="rgba(0,0,0,0.05)">
                        <animate attributeName="r" values="18;22;18" dur="4s" repeatCount="indefinite" />
                    </circle>
                    <circle cx="500" cy="340" r="10" fill="#0f172a" opacity="0.95">
                        <animate attributeName="opacity" values="0.8;1;0.8" dur="2s" repeatCount="indefinite" />
                    </circle>
                    <circle cx="500" cy="340" r="4" fill="white" />

                </template>
            </g>
        </svg>

        <!-- Hover Tooltip Card -->
        <Transition name="fade-scale">
            <div v-if="ninjaHoverNode"
                 @mouseenter="cancelHideTooltip()"
                 @mouseleave="scheduleHideTooltip()"
                 class="fixed z-[200] w-72 rounded-2xl shadow-xl p-5"
                 style="background:rgba(255,255,255,0.98); border:1px solid #e2e8f0; backdrop-filter:blur(20px);"
                 :style="{ left: ninjaTooltipX + 'px', top: ninjaTooltipY + 'px' }">

                <p class="text-xs font-black tracking-widest uppercase mb-1" style="color:#F59E0B;">{{ ninjaHoverNode.role }}</p>
                <h4 class="text-slate-900 text-base font-black mb-0.5">{{ ninjaHoverNode.name }}</h4>
                <p class="text-xs mb-4 font-medium" style="color:#64748b;">@ {{ ninjaHoverNode.company_name }}</p>

                <p class="text-sm leading-relaxed mb-5 italic pl-3" style="color:#475569; border-left:2px solid #F59E0B;">
                    "{{ ninjaHoverNode.message }}"
                </p>

                <p class="text-[10px] uppercase tracking-widest font-black mb-2" style="color:#94a3b8;">Actions</p>

                <a v-if="ninjaHoverNode.linkedin_url" :href="ninjaHoverNode.linkedin_url" target="_blank"
                   class="flex items-center justify-between p-3 rounded-xl mb-1 transition-all"
                   style="border:1px solid transparent;"
                   onmouseover="this.style.background='rgba(0,0,0,0.03)'; this.style.borderColor='#e2e8f0'"
                   onmouseout="this.style.background='transparent'; this.style.borderColor='transparent'">
                    <div class="flex items-center gap-3">
                        <svg class="w-4 h-4" fill="#0A66C2" viewBox="0 0 24 24"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>
                        <span class="text-sm font-bold text-slate-700">Voir le profil</span>
                    </div>
                    <svg class="w-4 h-4" style="color:#94a3b8;" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/></svg>
                </a>

                <button @click="copyNinjaMessage(ninjaHoverNode.message, ninjaHoverNode.key)"
                    class="w-full flex items-center justify-between p-3 rounded-xl transition-all"
                    style="border:1px solid transparent;"
                    onmouseover="this.style.background='rgba(232,93,62,0.06)'; this.style.borderColor='rgba(232,93,62,0.25)'"
                    onmouseout="this.style.background='transparent'; this.style.borderColor='transparent'">
                    <div class="flex items-center gap-3">
                        <svg class="w-4 h-4" style="color:#64748b;" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"/></svg>
                        <span class="text-sm font-bold text-slate-700">Copier ({{ (ninjaHoverNode.message||'').length }} car.)</span>
                    </div>
                    <svg v-if="ninjaCopied[ninjaHoverNode.key]" class="w-4 h-4" style="color:#F59E0B;" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
                    <svg v-else class="w-4 h-4" style="color:#94a3b8;" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/></svg>
                </button>
            </div>
        </Transition>

        <!-- Empty state -->
        <div v-if="!ninjaLoading && !ninjaRunning && ninjaCompanies.length === 0"
             class="absolute inset-0 flex flex-col items-center justify-center text-center z-20">
            <div class="w-16 h-16 rounded-full flex items-center justify-center mb-4"
                 style="background:white; border:1px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);">
                <svg class="w-8 h-8" style="color:#F59E0B;" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
            </div>
            <p class="text-slate-900 text-xl font-bold mb-2">Aucun réseau identifié</p>
            <p class="text-sm max-w-sm mb-6" style="color:#64748b;">Lancez le workflow depuis votre Dashboard pour cartographier vos contacts.</p>
            <button @click="runNinja" class="px-6 py-3 text-white font-bold rounded-2xl shadow-lg" style="background:#F59E0B;">Lancer le scan</button>
        </div>

        <!-- Scanning overlay -->
        <div v-if="ninjaRunning" class="absolute inset-0 flex flex-col items-center justify-center text-center z-50"
             style="background:rgba(255,255,255,0.94); backdrop-filter:blur(8px);">
            <div class="relative w-28 h-28 mb-8">
                <div class="absolute inset-0 rounded-full" style="border:4px solid rgba(232,93,62,0.15);"></div>
                <div class="absolute inset-0 rounded-full animate-spin" style="border:4px solid #F59E0B; border-top-color:transparent;"></div>
                <div class="absolute inset-0 flex items-center justify-center text-4xl">🥷</div>
            </div>
            <p class="text-xl font-black tracking-widest uppercase animate-pulse" style="color:#F59E0B;">Scan en cours</p>
            <p class="text-sm mt-3 max-w-sm" style="color:#64748b;">Identification des décideurs LinkedIn...</p>
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
            <p class="text-slate-500 font-medium leading-relaxed">{{ t('network_osint.loading_desc') }}</p>
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


.fade-scale-enter-active, .fade-scale-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}
.fade-scale-enter-from, .fade-scale-leave-to {
  opacity: 0;
  transform: scale(0.95);
}


/* ── Ninja SVG Animations ── */
@keyframes ninja-edge-flow {
  from { stroke-dashoffset: 0; }
  to   { stroke-dashoffset: -18; }
}
.ninja-edge-anim {
  animation: ninja-edge-flow 2.5s linear infinite;
}
.ninja-company-node {
  animation: ninja-company-pulse 3s ease-in-out infinite alternate;
  transform-origin: center;
  transform-box: fill-box;
}
@keyframes ninja-company-pulse {
  from { r: 8; opacity: 0.85; }
  to   { r: 10; opacity: 1; }
}
.ninja-pulse-ring {
  animation: ninja-ring-expand 3s ease-in-out infinite;
  transform-origin: center;
  transform-box: fill-box;
}
@keyframes ninja-ring-expand {
  0%   { r: 12; opacity: 0.4; }
  50%  { r: 22; opacity: 0.1; }
  100% { r: 12; opacity: 0.4; }
}


/* ── Ninja SVG Animations ── */
@keyframes ninja-edge-flow {
  from { stroke-dashoffset: 0; }
  to   { stroke-dashoffset: -22; }
}
.ninja-edge-anim {
  animation: ninja-edge-flow 2s linear infinite;
}
.ninja-edge-anim-slow {
  stroke-dasharray: 3,5;
  animation: ninja-edge-flow 4s linear infinite;
}
.ninja-pulse-ring {
  animation: ninja-ring-pulse 3s ease-in-out infinite;
  transform-box: fill-box;
  transform-origin: center;
}
@keyframes ninja-ring-pulse {
  0%   { opacity: 0.3; transform: scale(0.9); }
  50%  { opacity: 0.08; transform: scale(1.4); }
  100% { opacity: 0.3; transform: scale(0.9); }
}
.fade-scale-enter-active, .fade-scale-leave-active {
  transition: opacity 0.18s ease, transform 0.18s ease;
}
.fade-scale-enter-from, .fade-scale-leave-to {
  opacity: 0;
  transform: scale(0.95) translateY(-4px);
}

</style>
