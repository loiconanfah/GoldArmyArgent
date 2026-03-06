<script setup>
import { authFetch } from '../utils/auth'
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { toastState } from '../store/toastState'
import { 
  ChartBarIcon, 
  EnvelopeIcon, 
  ArrowPathIcon,
  LinkIcon,
  BriefcaseIcon,
  SparklesIcon,
  ArrowTopRightOnSquareIcon,
  CheckBadgeIcon,
  BellAlertIcon,
  PlusIcon,
  XMarkIcon,
  ClipboardDocumentIcon,
  CheckIcon,
  TrashIcon
} from '@heroicons/vue/24/outline'

const { t } = useI18n()
const router = useRouter()

const columns = [
  { id: 'TO_APPLY', title: t('crm_board.columns.to_apply'), icon: EnvelopeIcon, color: 'text-amber-400', bg: 'bg-amber-400/10', border: 'border-amber-400/20', accent: '#f59e0b', tagStyle: 'bg-amber-500/10 text-amber-400 border-amber-500/20' },
  { id: 'APPLIED', title: t('crm_board.columns.applied'), icon: ChartBarIcon, color: 'text-indigo-400', bg: 'bg-indigo-400/10', border: 'border-indigo-400/20', accent: '#6366f1', tagStyle: 'bg-indigo-500/10 text-indigo-400 border-indigo-500/20' },
  { id: 'FOLLOW_UP', title: t('crm_board.columns.follow_up'), icon: BellAlertIcon, color: 'text-rose-400', bg: 'bg-rose-400/10', border: 'border-rose-400/20', accent: '#f43f5e', tagStyle: 'bg-rose-500/10 text-rose-400 border-rose-500/20' },
  { id: 'INTERVIEW', title: t('crm_board.columns.interview'), icon: CheckBadgeIcon, color: 'text-emerald-400', bg: 'bg-emerald-400/10', border: 'border-emerald-400/20', accent: '#10b981', tagStyle: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' }
]

const crmCards = ref({ 'TO_APPLY': [], 'APPLIED': [], 'FOLLOW_UP': [], 'INTERVIEW': [] })
const isLoading = ref(true)
const draggedItem = ref(null)
const dragOverCol = ref(null)

// Follow-up popup state
const showFollowupPopup = ref(false)
const followupEmail = ref('')
const followupCard = ref(null)
const isGeneratingFollowup = ref(false)
const followupCount = ref(0)
const copied = ref(false)

// Delete popup state
const showDeletePopup = ref(false)
const itemToDelete = ref(null)

// Summary stats
const totalCards = computed(() => Object.values(crmCards.value).flat().length)
const interviewCount = computed(() => crmCards.value['INTERVIEW']?.length || 0)
const followUpCount = computed(() => crmCards.value['FOLLOW_UP']?.length || 0)
const appliedCount = computed(() => crmCards.value['APPLIED']?.length || 0)

const fetchCrmData = async () => {
    isLoading.value = true
    try {
        const res = await authFetch('/api/crm')
        const json = await res.json()
        const rawData = json.data || []
        const grouped = { 'TO_APPLY': [], 'APPLIED': [], 'FOLLOW_UP': [], 'INTERVIEW': [] }
        rawData.forEach(item => { if (grouped[item.status]) grouped[item.status].push(item) })
        crmCards.value = grouped
    } catch(e) { console.error("Failed to fetch CRM data", e) }
    finally { isLoading.value = false }
}

const newLinkUrl = ref('')
const isAddingLink = ref(false)

const addFromLink = async () => {
    if(!newLinkUrl.value.trim()) return
    isAddingLink.value = true
    try {
        const res = await authFetch('/api/crm/link', {
            method: 'POST',
            body: JSON.stringify({ url: newLinkUrl.value.trim() })
        })
        const json = await res.json()
        if (res.ok && json.status === 'success') {
            toastState.addToast(t('common.success'), 'success')
            newLinkUrl.value = ''
            await fetchCrmData() // refresh the board
        } else {
            toastState.addToast(`${t('common.error')}: ${json.detail || json.message || t('common.error')}`, 'error')
        }
    } catch(e) {
        toastState.addToast(t('common.network_error'), 'error')
    } finally {
        isAddingLink.value = false
    }
}

const handleDragStart = (e, card, sourceColumn) => {
    draggedItem.value = { card, sourceColumn }
    if (e.dataTransfer) { e.dataTransfer.effectAllowed = 'move'; e.dataTransfer.setData('text/plain', card.id) }
}

const handleDrop = async (e, targetColumnId) => {
    e.preventDefault()
    dragOverCol.value = null
    if (!draggedItem.value) return
    const { card, sourceColumn } = draggedItem.value
    if (sourceColumn === targetColumnId) { draggedItem.value = null; return }
    crmCards.value[sourceColumn] = crmCards.value[sourceColumn].filter(c => c.id !== card.id)
    card.status = targetColumnId
    crmCards.value[targetColumnId].push(card)
    draggedItem.value = null
    try {
        await authFetch(`/api/crm/${card.id}`, {
            method: 'PUT', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ status: targetColumnId })
        })
    } catch(err) { fetchCrmData() }
}

const deleteCard = (cardId, colId) => {
    itemToDelete.value = { cardId, colId };
    showDeletePopup.value = true;
}

const confirmDeleteCard = async () => {
    if (!itemToDelete.value) return;
    const { cardId, colId } = itemToDelete.value;
    
    // Simulate optimistic UI update
    const previousState = [...crmCards.value[colId]];
    crmCards.value[colId] = crmCards.value[colId].filter(c => c.id !== cardId);
    
    showDeletePopup.value = false;
    itemToDelete.value = null;
    
    try {
        const res = await authFetch(`/api/crm/${cardId}`, { method: 'DELETE' });
        if (!res.ok) throw new Error("Failed to delete");
        toastState.addToast(t('common.success'), "success");
    } catch(err) {
        // Revert on failure
        crmCards.value[colId] = previousState;
        toastState.addToast(t('common.error'), "error");
    }
}

const handleDragOver = (e, colId) => { e.preventDefault(); dragOverCol.value = colId }
const handleDragLeave = () => { dragOverCol.value = null }
const formatDate = (iso) => { if(!iso) return '?'; const d = new Date(iso); return `${d.getDate().toString().padStart(2,'0')}/${(d.getMonth()+1).toString().padStart(2,'0')}` }
const getInitial = (n) => n ? n.charAt(0).toUpperCase() : '?'

// ── Actions ──
const goToInterview = () => router.push('/interview')

const generateFollowup = async (card) => {
    followupCard.value = card
    followupEmail.value = ''
    isGeneratingFollowup.value = true
    showFollowupPopup.value = true
    copied.value = false
    try {
        const res = await authFetch(`/api/crm/applications/${card.id}/followup`, { method: 'POST' })
        
        if (res.status === 403) {
            const data = await res.json()
            followupEmail.value = `⚠️ Limite atteinte : ${data.detail || 'Veuillez passer au forfait Pro pour plus de relances.'}`
            return
        }

        const data = await res.json()
        if (data.status === 'success') {
            followupEmail.value = data.email
            followupCount.value = data.followUpCount
            // Update the card's count in UI
            const col = crmCards.value['FOLLOW_UP']
            const idx = col.findIndex(c => c.id === card.id)
            if (idx !== -1) col[idx].follow_up_count = data.followUpCount
        } else {
            const errDetail = data.detail || data.message || t('common.error')
            const errStr = typeof errDetail === 'object' ? JSON.stringify(errDetail) : errDetail
            followupEmail.value = `❌ ${t('common.error')}:\n${errStr}`
        }
    } catch(e) {
        followupEmail.value = `❌ ${t('common.error')}:\n${e.message}`
    } finally {
        isAddingLink.value = false
    }
}

const copyEmail = async () => {
    try {
        await navigator.clipboard.writeText(followupEmail.value)
        copied.value = true
        setTimeout(() => copied.value = false, 2500)
    } catch(e) {}
}

const closeFollowup = () => { showFollowupPopup.value = false; followupEmail.value = ''; followupCard.value = null }

onMounted(() => { fetchCrmData() })
</script>

<template>
  <div class="flex flex-col h-full min-h-0 bg-surface-950">

    <!-- ═══ PAGE HEADER ═══ -->
    <div class="shrink-0 px-6 pt-8 pb-5 border-b border-surface-800/60">
      <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 max-w-[1800px] mx-auto">
        <div>
          <span class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-[10px] font-black tracking-widest uppercase mb-2">
            <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
            Kanban Board
          </span>
          <h1 class="text-3xl font-display font-black text-white tracking-tight">
            Central <span class="text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-purple-500">{{ t('nav.crm') }}</span>
          </h1>
          <p class="text-slate-500 text-sm mt-1 font-medium">{{ t('crm_board.description') || 'Glissez-déposez vos opportunités pour suivre leur pipeline.' }}</p>
        </div>
        <button @click="fetchCrmData" class="flex items-center gap-2 text-sm font-bold bg-surface-800 hover:bg-surface-700 text-slate-300 px-4 py-2.5 rounded-xl border border-surface-700 transition-colors shrink-0">
          <ArrowPathIcon class="w-4 h-4" :class="{'animate-spin': isLoading}" />
          {{ t('common.refresh') }}
        </button>
      </div>

      <!-- ADD URL SECTION -->
      <div class="mt-5 max-w-[1800px] mx-auto">
        <form @submit.prevent="addFromLink" class="relative flex items-center">
          <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
            <LinkIcon class="w-5 h-5 text-slate-500" />
          </div>
          <input 
            v-model="newLinkUrl"
            type="url" 
            placeholder="Collez l'URL d'une offre d'emploi (LinkedIn, Indeed, site vitrine...) pour l'ajouter au CRM..." 
            class="w-full bg-surface-900 border border-surface-800 text-white text-sm rounded-xl focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500 block pl-11 pr-32 py-3.5 shadow-sm transition-all"
            :disabled="isAddingLink"
            required
          >
          <button 
            type="submit" 
            :disabled="isAddingLink || !newLinkUrl.trim()"
            class="absolute right-2 top-2 bottom-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed text-white font-bold text-xs px-4 rounded-lg flex items-center gap-2 transition-all shadow-lg shadow-indigo-500/20"
          >
            <ArrowPathIcon v-if="isAddingLink" class="w-4 h-4 animate-spin" />
            <SparklesIcon v-else class="w-4 h-4" />
            {{ isAddingLink ? t('common.loading') : t('crm_board.add_application') }}
          </button>
        </form>
      </div>

      <!-- OVERVIEW STATS -->
      <div class="mt-5 grid grid-cols-2 md:grid-cols-4 gap-3 max-w-[1800px] mx-auto">
        <div class="bg-surface-900 border border-surface-800 rounded-2xl p-4 flex items-center gap-3">
          <div class="w-9 h-9 rounded-xl bg-indigo-500/10 flex items-center justify-center shrink-0">
            <BriefcaseIcon class="w-5 h-5 text-indigo-400" />
          </div>
          <div><p class="text-2xl font-black text-white leading-none">{{ totalCards }}</p><p class="text-[10px] text-slate-500 font-bold uppercase tracking-widest mt-0.5">{{ t('common.total') }}</p></div>
        </div>
        <div class="bg-surface-900 border border-surface-800 rounded-2xl p-4 flex items-center gap-3">
          <div class="w-9 h-9 rounded-xl bg-indigo-500/10 flex items-center justify-center shrink-0">
            <ChartBarIcon class="w-5 h-5 text-indigo-400" />
          </div>
          <div><p class="text-2xl font-black text-white leading-none">{{ appliedCount }}</p><p class="text-[10px] text-slate-500 font-bold uppercase tracking-widest mt-0.5">{{ t('crm_board.columns.applied') }}</p></div>
        </div>
        <div class="bg-surface-900 border border-rose-500/10 rounded-2xl p-4 flex items-center gap-3">
          <div class="w-9 h-9 rounded-xl bg-rose-500/10 flex items-center justify-center shrink-0">
            <BellAlertIcon class="w-5 h-5 text-rose-400" />
          </div>
          <div><p class="text-2xl font-black text-white leading-none">{{ followUpCount }}</p><p class="text-[10px] text-slate-500 font-bold uppercase tracking-widest mt-0.5">{{ t('crm_board.columns.follow_up') }}</p></div>
        </div>
        <div class="bg-surface-900 border border-emerald-500/10 rounded-2xl p-4 flex items-center gap-3">
          <div class="w-9 h-9 rounded-xl bg-emerald-500/10 flex items-center justify-center shrink-0">
            <CheckBadgeIcon class="w-5 h-5 text-emerald-400" />
          </div>
          <div><p class="text-2xl font-black text-white leading-none">{{ interviewCount }}</p><p class="text-[10px] text-slate-500 font-bold uppercase tracking-widest mt-0.5">{{ t('crm_board.columns.interview') }}</p></div>
        </div>
      </div>
    </div>

    <!-- ═══ KANBAN BOARD ═══ -->
    <div class="flex-1 min-h-0 overflow-x-auto overflow-y-hidden px-6 py-5 custom-scrollbar-h">
      <div class="flex gap-5 h-full min-w-max">

        <div 
          v-for="col in columns" 
          :key="col.id" 
          class="w-[300px] xl:w-[320px] flex flex-col rounded-2xl shrink-0 transition-all duration-200 bg-surface-900 border"
          :class="dragOverCol === col.id ? col.border + ' ring-1 ring-inset ' + col.border : 'border-surface-800'"
          @dragover="handleDragOver($event, col.id)"
          @dragleave="handleDragLeave"
          @drop="handleDrop($event, col.id)"
        >
          <!-- Column Header -->
          <div class="shrink-0 px-4 pt-4 pb-3 border-b border-surface-800">
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-2.5">
                <div class="w-7 h-7 rounded-lg flex items-center justify-center" :class="col.bg">
                  <component :is="col.icon" class="w-4 h-4" :class="col.color" />
                </div>
                <span class="font-bold text-sm text-white tracking-tight">{{ col.title }}</span>
              </div>
              <span class="text-xs font-black px-2 py-0.5 rounded-full border" :class="col.tagStyle">
                {{ crmCards[col.id]?.length || 0 }}
              </span>
            </div>
            <div class="mt-3 h-0.5 rounded-full w-full opacity-40" :style="`background: ${col.accent}`"></div>
          </div>

          <!-- Cards Area -->
          <div class="flex-1 min-h-0 overflow-y-auto px-3 py-3 space-y-3 custom-scrollbar">

            <div 
              v-for="card in crmCards[col.id]" 
              :key="card.id"
              draggable="true"
              @dragstart="handleDragStart($event, card, col.id)"
              class="relative bg-surface-950 border border-surface-800 rounded-xl p-4 cursor-grab active:cursor-grabbing active:scale-[0.98] active:opacity-60 hover:border-surface-600 hover:shadow-xl transition-all duration-200 group overflow-hidden"
            >
              <div class="absolute left-0 top-0 bottom-0 w-[3px] rounded-l-xl opacity-0 group-hover:opacity-100 transition-opacity" :style="`background: ${col.accent}`"></div>

              <!-- Card Top -->
              <div class="flex items-start justify-between mb-3 gap-2">
                <div class="flex items-center gap-2.5 min-w-0">
                  <div class="w-8 h-8 shrink-0 rounded-lg flex items-center justify-center font-black text-sm text-white" :style="`background: ${col.accent}25; border: 1px solid ${col.accent}40`">
                    {{ getInitial(card.company_name) }}
                  </div>
                  <p class="text-xs font-bold text-slate-400 truncate w-32" :title="card.company_name">{{ card.company_name }}</p>
                </div>
                <!-- Card actions (Date, Link, Delete) -->
                <div class="flex items-center gap-1.5 shrink-0 opacity-100 xl:opacity-0 xl:group-hover:opacity-100 transition-opacity">
                  <span class="text-[10px] font-bold text-slate-600 bg-surface-800 px-2 py-0.5 rounded-lg border border-surface-700 hidden sm:inline-block">{{ formatDate(card.created_at) }}</span>
                  <a v-if="card.url" :href="card.url" target="_blank" :title="t('common.details')" class="text-slate-500 hover:text-indigo-400 transition-colors bg-surface-800 p-1 rounded-lg border border-surface-700" @click.stop>
                    <ArrowTopRightOnSquareIcon class="w-3.5 h-3.5" />
                  </a>
                  <button @click.stop="deleteCard(card.id, col.id)" :title="t('common.delete')" class="text-slate-500 hover:text-rose-400 transition-colors bg-surface-800 p-1 rounded-lg border border-surface-700">
                    <TrashIcon class="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>

              <h4 class="font-bold text-white text-sm leading-snug mb-1 group-hover:text-indigo-300 transition-colors line-clamp-2">{{ card.job_title }}</h4>
              <p v-if="card.notes" class="text-[11px] text-slate-500 line-clamp-2 leading-relaxed mb-3 bg-black/20 rounded-lg px-2.5 py-1.5 border border-surface-800">{{ card.notes }}</p>

              <!-- CTA Footer -->
              <div class="mt-3 pt-3 border-t border-surface-800">
                <!-- TO_APPLY: AI CV Adaption -->
                <button v-if="col.id === 'TO_APPLY'" class="text-[10px] font-black uppercase tracking-widest px-3 py-1.5 rounded-lg w-full text-center transition-all flex items-center justify-center gap-1 border hover:opacity-80" :class="col.tagStyle">
                  <SparklesIcon class="w-3 h-3" />Adapter CV IA
                </button>

                <!-- FOLLOW_UP: Generate email -->
                <button v-else-if="col.id === 'FOLLOW_UP'" @click.stop="generateFollowup(card)" class="text-[10px] font-black uppercase tracking-widest px-3 py-1.5 rounded-lg w-full text-center transition-all flex items-center justify-center gap-1.5 border hover:opacity-80 group/btn" :class="col.tagStyle">
                  <BellAlertIcon class="w-3 h-3" />
                  Générer la Relance
                  <span v-if="card.follow_up_count" class="ml-1 px-1.5 py-0 rounded-full text-[9px] font-black bg-rose-500/30">
                    {{ card.follow_up_count }}×
                  </span>
                </button>

                <!-- INTERVIEW: Go to Interview -->
                <button v-else-if="col.id === 'INTERVIEW'" @click.stop="goToInterview" class="text-[10px] font-black uppercase tracking-widest px-3 py-1.5 rounded-lg w-full text-center transition-all flex items-center justify-center gap-1 border hover:opacity-80" :class="col.tagStyle">
                  <CheckBadgeIcon class="w-3 h-3" />Préparer l'Entretien
                </button>

                <!-- APPLIED: Status label -->
                <div v-else class="text-[10px] font-bold text-slate-600 text-center py-0.5">⏳ En attente de retour</div>
              </div>
            </div>

            <!-- Empty Drop Zone -->
            <div v-if="!crmCards[col.id]?.length" class="h-28 rounded-xl border-2 border-dashed flex flex-col items-center justify-center gap-2 text-xs font-bold transition-colors"
              :class="dragOverCol === col.id ? [col.border, col.bg, col.color] : 'border-surface-800 text-slate-700'">
              <PlusIcon class="w-5 h-5" />
              <span>{{ dragOverCol === col.id ? t('common.confirm') : t('common.error') }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ═══ FOLLOW-UP EMAIL POPUP ═══ -->
    <div v-if="showFollowupPopup" class="fixed inset-0 z-[200] flex items-center justify-center p-4">
      <div class="absolute inset-0 bg-black/70 backdrop-blur-sm" @click="closeFollowup"></div>
      <div class="relative z-10 bg-surface-900 border border-surface-700 rounded-3xl shadow-2xl w-full max-w-2xl overflow-hidden animate-scale-in">
        
        <!-- Modal Header -->
        <div class="px-6 pt-6 pb-4 border-b border-surface-800 bg-gradient-to-r from-rose-500/5 to-pink-500/5 flex items-start justify-between gap-4">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-xl bg-rose-500/10 flex items-center justify-center">
              <BellAlertIcon class="w-5 h-5 text-rose-400" />
            </div>
            <div>
              <h3 class="font-bold text-white">Email de relance généré</h3>
              <p class="text-xs text-slate-500 mt-0.5">
                {{ followupCard?.job_title }} — {{ followupCard?.company_name }}
                <span v-if="followupCount" class="ml-2 text-rose-400 font-bold">Relance #{{ followupCount }}</span>
              </p>
            </div>
          </div>
          <button @click="closeFollowup" class="p-1.5 text-slate-500 hover:text-white rounded-lg hover:bg-surface-800 transition-colors shrink-0">
            <XMarkIcon class="w-5 h-5" />
          </button>
        </div>

        <!-- Email Content -->
        <div class="p-6">
          <!-- Loading -->
          <div v-if="isGeneratingFollowup" class="flex flex-col items-center py-10 gap-4">
            <div class="relative w-12 h-12">
              <div class="absolute inset-0 border-4 border-rose-500/20 rounded-full"></div>
              <div class="absolute inset-0 border-4 border-white border-t-transparent rounded-full animate-spin"></div>
            </div>
            <p class="text-sm font-bold text-white animate-pulse">Gemini rédige votre relance...</p>
          </div>

          <!-- Email Text -->
          <div v-else class="space-y-4">
            <div class="bg-surface-950 border border-surface-800 rounded-2xl p-5 font-mono text-sm text-slate-300 leading-relaxed whitespace-pre-wrap min-h-[160px] max-h-[320px] overflow-y-auto custom-scrollbar">{{ followupEmail }}</div>
            
            <!-- Actions -->
            <div class="flex items-center gap-3 pt-2">
              <button 
                @click="copyEmail"
                class="flex items-center gap-2 px-5 py-2.5 rounded-xl font-bold text-sm transition-all"
                :class="copied ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-indigo-500 hover:bg-indigo-400 text-white'"
              >
                <component :is="copied ? CheckIcon : ClipboardDocumentIcon" class="w-4 h-4" />
                {{ copied ? 'Copié !' : 'Copier l\'email' }}
              </button>
                <button @click="generateFollowup(followupCard)" class="flex items-center gap-2 px-4 py-2.5 rounded-xl font-bold text-sm bg-surface-800 hover:bg-surface-700 text-slate-300 border border-surface-700 transition-all">
                <ArrowPathIcon class="w-4 h-4" />{{ t('common.regenerate') }}
              </button>
              <button @click="closeFollowup" class="ml-auto text-sm font-bold text-slate-500 hover:text-white transition-colors px-3 py-2">
                {{ t('common.close') }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ═══ DELETE CONFIRMATION POPUP ═══ -->
    <div v-if="showDeletePopup" class="fixed inset-0 z-[200] flex items-center justify-center p-4">
      <div class="absolute inset-0 bg-black/70 backdrop-blur-sm" @click="showDeletePopup = false; itemToDelete = null"></div>
      <div class="relative z-10 bg-surface-900 border border-surface-700 rounded-3xl shadow-2xl w-full max-w-sm overflow-hidden animate-scale-in text-center p-6">
        <div class="w-16 h-16 rounded-2xl bg-gradient-to-br from-rose-500/20 to-rose-600/5 flex items-center justify-center mx-auto mb-4 border border-rose-500/20">
          <TrashIcon class="w-7 h-7 text-rose-500" />
        </div>
        <h3 class="text-xl font-display font-black text-white mb-2">{{ t('crm_board.card.delete') }} ?</h3>
        <p class="text-[13px] leading-relaxed text-slate-400 mb-6 font-medium">{{ t('crm_board.delete_confirm_desc') || 'Cette opportunité sera effacée définitivement de votre pipeline.' }}</p>
        <div class="flex gap-3">
          <button @click="showDeletePopup = false; itemToDelete = null" class="flex-1 py-3 px-4 rounded-xl font-bold text-sm bg-surface-800 hover:bg-surface-700 text-slate-300 border border-surface-700 transition-colors">
            {{ t('common.cancel') }}
          </button>
          <button @click="confirmDeleteCard" class="flex-1 py-3 px-4 rounded-xl font-bold text-sm bg-rose-600 hover:bg-rose-500 text-white shadow-lg shadow-rose-500/20 transition-all flex items-center justify-center gap-2">
            <TrashIcon class="w-4 h-4" />
            {{ t('common.delete') }}
          </button>
        </div>
      </div>
    </div>

  </div>
</template>

<style scoped>
.custom-scrollbar::-webkit-scrollbar { width: 4px; }
.custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: #1e293b; border-radius: 10px; }
.custom-scrollbar::-webkit-scrollbar-thumb:hover { background: #475569; }

.custom-scrollbar-h::-webkit-scrollbar { height: 6px; }
.custom-scrollbar-h::-webkit-scrollbar-track { background: transparent; }
.custom-scrollbar-h::-webkit-scrollbar-thumb { background: #1e293b; border-radius: 10px; }
.custom-scrollbar-h::-webkit-scrollbar-thumb:hover { background: #475569; }

@keyframes scale-in {
  from { transform: scale(0.94); opacity: 0; }
  to { transform: scale(1); opacity: 1; }
}
.animate-scale-in { animation: scale-in 0.2s ease-out forwards; }
</style>
