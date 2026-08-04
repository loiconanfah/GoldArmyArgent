<script setup>
import { authFetch } from '../utils/auth'
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { toastState } from '../store/toastState'
import {
  ChartBarIcon, EnvelopeIcon, ArrowPathIcon, LinkIcon, BriefcaseIcon,
  SparklesIcon, ArrowTopRightOnSquareIcon, CheckBadgeIcon, BellAlertIcon,
  PlusIcon, XMarkIcon, ClipboardDocumentIcon, CheckIcon, TrashIcon,
  DocumentTextIcon, ArrowUpTrayIcon, TrophyIcon, XCircleIcon,
  ClockIcon, FireIcon, Bars3Icon, MagnifyingGlassIcon
} from '@heroicons/vue/24/outline'

const { t } = useI18n()
const router = useRouter()

const columns = [
  { id: 'TO_APPLY',  title: 'À Postuler',         icon: EnvelopeIcon,   accent: '#f59e0b', accentRgb: '245,158,11',  accentBg: 'rgba(245,158,11,0.08)',  label: 'À postuler',  gradient: 'from-amber-500/5 to-orange-400/0' },
  { id: 'APPLIED',   title: 'Candidature Envoyée', icon: ChartBarIcon,   accent: '#6366f1', accentRgb: '99,102,241',  accentBg: 'rgba(99,102,241,0.08)',  label: 'Envoyée',     gradient: 'from-indigo-500/5 to-purple-400/0' },
  { id: 'FOLLOW_UP', title: 'Relance Requise',     icon: BellAlertIcon,  accent: '#ef4444', accentRgb: '239,68,68',   accentBg: 'rgba(239,68,68,0.08)',   label: 'Relance',     gradient: 'from-red-500/5 to-rose-400/0' },
  { id: 'INTERVIEW', title: 'Entretien',           icon: CheckBadgeIcon, accent: '#10b981', accentRgb: '16,185,129',  accentBg: 'rgba(16,185,129,0.08)',  label: 'Entretien',   gradient: 'from-emerald-500/5 to-teal-400/0' },
  { id: 'OFFER',     title: 'Offre Reçue',         icon: TrophyIcon,     accent: '#8b5cf6', accentRgb: '139,92,246',  accentBg: 'rgba(139,92,246,0.08)', label: 'Offre',       gradient: 'from-violet-500/5 to-purple-400/0' },
]

const crmCards = ref({ 'TO_APPLY': [], 'APPLIED': [], 'FOLLOW_UP': [], 'INTERVIEW': [], 'OFFER': [] })
const isLoading = ref(true)
const draggedItem = ref(null)
const dragOverCol = ref(null)
const boardVisible = ref(false)

// Instant Search & Filter Bar
const searchQuery = ref('')
const activeFilterTag = ref('ALL') // ALL, URGENT, LINKEDIN, WITH_NOTES

const filteredCrmCards = computed(() => {
  const result = { 'TO_APPLY': [], 'APPLIED': [], 'FOLLOW_UP': [], 'INTERVIEW': [], 'OFFER': [] }
  const q = searchQuery.value.trim().toLowerCase()

  for (const [colId, cards] of Object.entries(crmCards.value)) {
    result[colId] = (cards || []).filter(card => {
      // 1. Text Search
      const titleMatch = !q || (card.job_title && card.job_title.toLowerCase().includes(q))
      const companyMatch = !q || (card.company_name && card.company_name.toLowerCase().includes(q))
      const notesMatch = !q || (card.notes && card.notes.toLowerCase().includes(q))
      if (!titleMatch && !companyMatch && !notesMatch) return false

      // 2. Filter Pills
      if (activeFilterTag.value === 'URGENT') {
        const days = daysSince(card.created_at)
        if (colId !== 'FOLLOW_UP' || days <= 7) return false
      } else if (activeFilterTag.value === 'LINKEDIN') {
        if (!card.url || !card.url.toLowerCase().includes('linkedin')) return false
      } else if (activeFilterTag.value === 'WITH_NOTES') {
        if (!card.notes || !card.notes.trim()) return false
      }

      return true
    })
  }

  return result
})

const showFollowupPopup = ref(false)
const followupEmail = ref('')
const followupCard = ref(null)
const isGeneratingFollowup = ref(false)
const followupCount = ref(0)
const copied = ref(false)

const showDeletePopup = ref(false)
const itemToDelete = ref(null)

const showAdaptCvModal = ref(false)
const adaptCvCard = ref(null)
const cvTextForAdapt = ref('')
const isAdaptingCv = ref(false)
const adaptedData = ref(null)
const adaptCvFileInput = ref(null)
const showDownloadCvModal = ref(false)
const selectedCvTheme = ref('goldarmy')
const isDownloadingPdf = ref(false)

import { CV_TEMPLATES } from '../utils/cvTemplates/index'
import CvEditorModal from '../components/CvEditorModal.vue'

const CV_THEMES = CV_TEMPLATES.map(t => ({ id: t.id, name: t.label, colors: [t.accentColor, t.accentColor], build: t.build }))

const totalCards    = computed(() => Object.values(crmCards.value).flat().length)
const interviewCount = computed(() => crmCards.value['INTERVIEW']?.length || 0)
const followUpCount  = computed(() => crmCards.value['FOLLOW_UP']?.length || 0)
const appliedCount   = computed(() => crmCards.value['APPLIED']?.length || 0)
const offerCount     = computed(() => crmCards.value['OFFER']?.length || 0)
const conversionRate = computed(() => {
  const sent = appliedCount.value + followUpCount.value + interviewCount.value + offerCount.value
  return sent ? Math.round(((interviewCount.value + offerCount.value) / sent) * 100) : 0
})

const fetchCrmData = async () => {
  isLoading.value = true
  boardVisible.value = false
  try {
    const res = await authFetch('/api/crm')
    const json = await res.json()
    const rawData = json.data || []
    const grouped = { 'TO_APPLY': [], 'APPLIED': [], 'FOLLOW_UP': [], 'INTERVIEW': [], 'OFFER': [] }
    rawData.forEach(item => { if (grouped[item.status]) grouped[item.status].push(item) })
    crmCards.value = grouped
    await nextTick()
    setTimeout(() => { boardVisible.value = true }, 50)
  } catch(e) { console.error(e) }
  finally { isLoading.value = false }
}

const newLinkUrl = ref('')
const isAddingLink = ref(false)

const addFromLink = async () => {
  if (!newLinkUrl.value.trim()) return
  isAddingLink.value = true
  try {
    const res = await authFetch('/api/crm/link', { method: 'POST', body: JSON.stringify({ url: newLinkUrl.value.trim() }) })
    const json = await res.json()
    if (res.ok && json.status === 'success') {
      toastState.addToast('Candidature ajoutée !', 'success')
      newLinkUrl.value = ''
      await fetchCrmData()
    } else { toastState.addToast(`Erreur : ${json.detail || json.message || t('common.error')}`, 'error') }
  } catch(e) { toastState.addToast(t('common.network_error'), 'error') }
  finally { isAddingLink.value = false }
}

const handleDragStart = (e, card, sourceColumn) => {
  draggedItem.value = { card, sourceColumn }
  if (e.dataTransfer) { e.dataTransfer.effectAllowed = 'move'; e.dataTransfer.setData('text/plain', card.id) }
}
const handleDrop = async (e, targetColumnId) => {
  e.preventDefault(); dragOverCol.value = null
  if (!draggedItem.value) return
  const { card, sourceColumn } = draggedItem.value
  if (sourceColumn === targetColumnId) { draggedItem.value = null; return }
  crmCards.value[sourceColumn] = crmCards.value[sourceColumn].filter(c => c.id !== card.id)
  card.status = targetColumnId
  crmCards.value[targetColumnId].push(card)
  draggedItem.value = null
  try { await authFetch(`/api/crm/${card.id}`, { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ status: targetColumnId }) }) }
  catch(err) { fetchCrmData() }
}
const deleteCard = (cardId, colId) => { itemToDelete.value = { cardId, colId }; showDeletePopup.value = true }
const confirmDeleteCard = async () => {
  if (!itemToDelete.value) return
  const { cardId, colId } = itemToDelete.value
  const prev = [...crmCards.value[colId]]
  crmCards.value[colId] = crmCards.value[colId].filter(c => c.id !== cardId)
  showDeletePopup.value = false; itemToDelete.value = null
  try {
    const res = await authFetch(`/api/crm/${cardId}`, { method: 'DELETE' })
    if (!res.ok) throw new Error()
    toastState.addToast('Supprimé.', 'success')
  } catch { crmCards.value[colId] = prev; toastState.addToast(t('common.error'), 'error') }
}
const handleDragOver = (e, colId) => { e.preventDefault(); dragOverCol.value = colId }
const handleDragLeave = () => { dragOverCol.value = null }

const daysSince = (iso) => { if (!iso) return 0; return Math.floor((Date.now() - new Date(iso).getTime()) / 86400000) }

const getInitial = (n) => n ? n.charAt(0).toUpperCase() : '?'
const getCompanyLogoUrl = (companyName) => {
  if (!companyName) return null
  const slug = companyName.toLowerCase().replace(/[^a-z0-9\s]/g, '').trim().split(/\s+/)[0]
  return (!slug || slug.length < 2) ? null : `https://logo.clearbit.com/${slug}.com`
}
const logoErrors = ref({})
const onLogoError = (cardId) => { logoErrors.value[cardId] = true }
const goToInterview = (card) => { router.push({ path: '/interview', query: { company: card.company_name, jobTitle: card.job_title, jobDetails: card.notes } }) }

const generateFollowup = async (card) => {
  followupCard.value = card; followupEmail.value = ''; isGeneratingFollowup.value = true; showFollowupPopup.value = true; copied.value = false
  try {
    const res = await authFetch(`/api/crm/applications/${card.id}/followup`, { method: 'POST' })
    if (res.status === 403) { const data = await res.json(); followupEmail.value = `Limite atteinte : ${data.detail || 'Passez au Pro.'}`; return }
    if (!res.ok) { const e = await res.json().catch(() => ({})); followupEmail.value = e.detail || e.message || t('common.error'); return }
    const data = await res.json()
    if (data.status === 'success') {
      followupEmail.value = (data.email && String(data.email).trim()) || 'Aucun texte. Réessayez.'
      followupCount.value = data.followUpCount
      const col = crmCards.value['FOLLOW_UP']; const idx = col.findIndex(c => c.id === card.id)
      if (idx !== -1) col[idx].follow_up_count = data.followUpCount
    } else { followupEmail.value = data.detail || data.message || t('common.error') }
  } catch(e) { followupEmail.value = e.message }
  finally { isGeneratingFollowup.value = false }
}
const copyEmail = async () => { try { await navigator.clipboard.writeText(followupEmail.value); copied.value = true; setTimeout(() => copied.value = false, 2500) } catch {} }
const closeFollowup = () => { showFollowupPopup.value = false; followupEmail.value = ''; followupCard.value = null }

const openAdaptCvModal = (card) => { adaptCvCard.value = card; cvTextForAdapt.value = ''; adaptedData.value = null; showAdaptCvModal.value = true; showDownloadCvModal.value = false }
const useProfileCv = async () => {
  if (!adaptCvCard.value) return
  try { const res = await authFetch('/api/profile'); const json = await res.json(); const cvText = json?.data?.cv_text; if (!cvText || cvText.length < 50) { toastState.addToast('Aucun CV enregistré.', 'info'); return }; cvTextForAdapt.value = cvText; await runAdapt() }
  catch { toastState.addToast(t('common.network_error'), 'error') }
}
const onAdaptFileSelected = async (e) => {
  const file = e.target?.files?.[0]; if (!file || !file.name.toLowerCase().endsWith('.pdf')) { toastState.addToast('PDF requis.', 'info'); return }
  const formData = new FormData(); formData.append('file', file)
  try { const res = await authFetch('/api/parse-pdf', { method: 'POST', body: formData }); const json = await res.json(); const text = json?.text; if (!text || text.length < 50) { toastState.addToast('Impossible de lire le PDF.', 'error'); return }; cvTextForAdapt.value = text; await runAdapt() }
  catch { toastState.addToast(t('common.network_error'), 'error') }
  e.target.value = ''
}
const runAdapt = async () => {
  if (!adaptCvCard.value || !cvTextForAdapt.value || cvTextForAdapt.value.length < 50) { toastState.addToast('CV manquant.', 'info'); return }
  isAdaptingCv.value = true
  try {
    const res = await authFetch('/api/adapt-cv', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ job_title: adaptCvCard.value.job_title, job_description: adaptCvCard.value.notes || '', cv_text: cvTextForAdapt.value }) })
    const json = await res.json()
    if (json.status === 'success' && json.data) { adaptedData.value = json.data; showAdaptCvModal.value = false; showDownloadCvModal.value = true; selectedCvTheme.value = 'goldarmy' }
    else { toastState.addToast(json.detail || "Erreur.", 'error') }
  } catch { toastState.addToast(t('common.network_error'), 'error') }
  finally { isAdaptingCv.value = false }
}
const closeAdaptCvModal = () => { showAdaptCvModal.value = false; adaptCvCard.value = null; cvTextForAdapt.value = ''; adaptedData.value = null }
const buildCvJsonFromMarkdown = (markdown) => { const lines = (markdown || '').split(/\n/).filter(Boolean); const fullName = lines[0]?.replace(/^#+\s*/, '').trim() || 'Candidat'; return { full_name: fullName, summary: '', experiences: [{ title: 'Expérience', company: '', start_date: '', end_date: '', bullets: lines }], skills: {}, education: [] } }
const showCrmEditor = ref(false)
const crmEditorData = ref(null)
const openCrmEditor = () => {
  if (!adaptedData.value?.cv_json && !adaptedData.value?.markdown) return
  let cvJson = null
  if (adaptedData.value.cv_json) { if (typeof adaptedData.value.cv_json === 'object') { cvJson = adaptedData.value.cv_json } else { try { cvJson = JSON.parse(adaptedData.value.cv_json) } catch {} } }
  if (!cvJson) cvJson = buildCvJsonFromMarkdown(adaptedData.value.markdown || '')
  crmEditorData.value = cvJson; showCrmEditor.value = true
}
const saveCrmEditor = (newData) => { adaptedData.value.cv_json = newData; if (adaptCvCard.value) adaptCvCard.value.adapted_cv = newData; showCrmEditor.value = false; crmEditorData.value = null; toastState.addToast('Sauvegardé.', 'success') }
const downloadAdaptedPdf = async () => {
  if (!adaptedData.value?.markdown && !adaptedData.value?.cv_json) return
  isDownloadingPdf.value = true
  try {
    let cvJson = null
    if (adaptedData.value.cv_json) { if (typeof adaptedData.value.cv_json === 'object') { cvJson = adaptedData.value.cv_json } else { try { cvJson = JSON.parse(adaptedData.value.cv_json) } catch {} } }
    if (!cvJson) cvJson = buildCvJsonFromMarkdown(adaptedData.value.markdown || '')
    const filename = `CV_Adapte_${(adaptCvCard.value?.job_title || 'offre').replace(/\s+/g,'_').slice(0,30)}`
    const tpl = CV_THEMES.find(t => t.id === selectedCvTheme.value) || CV_THEMES[0]
    const html = tpl.build(cvJson, null)
    const res = await authFetch('/api/generate-cv-pdf-html', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ html, filename }) })
    if (!res.ok) { const err = await res.json(); toastState.addToast(err.detail || 'Erreur PDF', 'error'); return }
    const blob = await res.blob(); const url = URL.createObjectURL(blob)
    const a = document.createElement('a'); a.href = url; a.download = filename + '.pdf'; a.click(); URL.revokeObjectURL(url)
    toastState.addToast('CV téléchargé.', 'success'); showDownloadCvModal.value = false; adaptedData.value = null
  } catch { toastState.addToast('Erreur téléchargement.', 'error') }
  finally { isDownloadingPdf.value = false }
}
const closeDownloadCvModal = () => { showDownloadCvModal.value = false; adaptedData.value = null }

onMounted(() => { fetchCrmData() })
</script>

<template>
  <div class="crm-root flex flex-col h-full min-h-0">

    <!-- ═══ HEADER ═══ -->
    <div class="crm-header shrink-0 px-6 pt-5 pb-4">
      <div class="max-w-[2000px] mx-auto">

        <!-- Title row -->
        <div class="flex items-start justify-between gap-4 mb-5">
          <div class="header-title-block">
            <div class="live-badge">
              <span class="live-dot"></span>
              Pipeline Actif
            </div>
            <h1 class="crm-title">
              Central <span class="crm-title-accent">CRM</span>
              <span class="crm-title-sub"> Candidatures</span>
            </h1>
            <p class="crm-subtitle">Glissez-déposez vos opportunités · {{ totalCards }} candidature{{ totalCards !== 1 ? 's' : '' }} en cours</p>
          </div>
          <button @click="fetchCrmData" class="refresh-btn" :class="{ spinning: isLoading }">
            <ArrowPathIcon class="w-4 h-4" :class="{ 'animate-spin': isLoading }" />
            <span>Sync</span>
          </button>
        </div>

        <!-- URL input -->
        <div class="url-input-wrapper mb-5">
          <form @submit.prevent="addFromLink" class="relative">
            <div class="url-input-icon">
              <LinkIcon class="w-5 h-5" />
            </div>
            <input
              v-model="newLinkUrl" type="url"
              placeholder="Collez une URL d'offre LinkedIn, Indeed, WTTJ…"
              class="url-input"
              :disabled="isAddingLink" required
            />
            <button type="submit" :disabled="isAddingLink || !newLinkUrl.trim()" class="url-submit-btn">
              <ArrowPathIcon v-if="isAddingLink" class="w-4 h-4 animate-spin" />
              <SparklesIcon v-else class="w-4 h-4" />
              {{ isAddingLink ? 'Analyse…' : 'Ajouter au CRM' }}
            </button>
          </form>
        </div>

        <!-- Stats pills -->
        <div class="stats-row">
          <div v-for="(col, i) in columns" :key="col.id"
            class="stat-card"
            :style="`--accent: ${col.accent}; --accent-bg: ${col.accentBg}; animation-delay: ${i * 60}ms`"
          >
            <div class="stat-icon-wrap">
              <component :is="col.icon" class="w-4 h-4" :style="`color: ${col.accent}`" />
            </div>
            <div>
              <div class="stat-number">{{ crmCards[col.id]?.length || 0 }}</div>
              <div class="stat-label">{{ col.title }}</div>
            </div>
            <div class="stat-bar-track">
              <div class="stat-bar-fill" :style="`width: ${totalCards ? Math.round((crmCards[col.id]?.length||0)/totalCards*100) : 0}%; background: ${col.accent}`"></div>
            </div>
          </div>
          <!-- Conversion rate -->
          <div class="stat-card stat-card-conversion" style="--accent: #6366f1; animation-delay: 300ms">
            <div class="stat-icon-wrap">
              <TrophyIcon class="w-4 h-4 text-indigo-500" />
            </div>
            <div>
              <div class="stat-number">{{ conversionRate }}<span class="text-lg text-slate-400 font-bold">%</span></div>
              <div class="stat-label">Taux de conversion</div>
            </div>
          </div>
        </div>

        <!-- ═══ INSTANT SEARCH & FILTER BAR (LIGHT THEME) ═══ -->
        <div class="mt-4 bg-white border border-slate-200 rounded-2xl p-3.5 shadow-sm flex flex-col md:flex-row items-center justify-between gap-3">
          <!-- Search Input -->
          <div class="relative w-full md:w-80">
            <MagnifyingGlassIcon class="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Rechercher entreprise, poste..."
              class="w-full bg-slate-50 border border-slate-200 rounded-xl pl-9 pr-8 py-2 text-xs font-semibold text-slate-900 placeholder-slate-400 focus:outline-none focus:border-amber-500 focus:bg-white transition-all"
            />
            <button v-if="searchQuery" @click="searchQuery = ''" class="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600">
              <XMarkIcon class="w-3.5 h-3.5" />
            </button>
          </div>

          <!-- Quick Filter Pills -->
          <div class="flex items-center gap-2 overflow-x-auto w-full md:w-auto custom-scrollbar pb-1 md:pb-0">
            <button
              @click="activeFilterTag = 'ALL'"
              class="px-3 py-1.5 rounded-xl text-xs font-bold transition-all whitespace-nowrap cursor-pointer"
              :class="activeFilterTag === 'ALL' ? 'bg-amber-500 text-white shadow-sm' : 'bg-slate-100 hover:bg-slate-200 text-slate-700'"
            >
              Tous ({{ totalCards }})
            </button>

            <button
              @click="activeFilterTag = 'URGENT'"
              class="px-3 py-1.5 rounded-xl text-xs font-bold transition-all whitespace-nowrap cursor-pointer flex items-center gap-1.5"
              :class="activeFilterTag === 'URGENT' ? 'bg-rose-500 text-white shadow-sm' : 'bg-rose-50 hover:bg-rose-100 text-rose-800 border border-rose-200'"
            >
              <span>🚨</span> À relancer urgent
            </button>

            <button
              @click="activeFilterTag = 'LINKEDIN'"
              class="px-3 py-1.5 rounded-xl text-xs font-bold transition-all whitespace-nowrap cursor-pointer flex items-center gap-1.5"
              :class="activeFilterTag === 'LINKEDIN' ? 'bg-amber-500 text-white shadow-sm' : 'bg-amber-50 hover:bg-amber-100 text-amber-900 border border-amber-200'"
            >
              <span>💼</span> LinkedIn
            </button>

            <button
              @click="activeFilterTag = 'WITH_NOTES'"
              class="px-3 py-1.5 rounded-xl text-xs font-bold transition-all whitespace-nowrap cursor-pointer flex items-center gap-1.5"
              :class="activeFilterTag === 'WITH_NOTES' ? 'bg-amber-500 text-white shadow-sm' : 'bg-slate-100 hover:bg-slate-200 text-slate-700'"
            >
              <span>📝</span> Avec notes
            </button>
          </div>
        </div>

      </div>
    </div>

    <!-- ═══ KANBAN BOARD ═══ -->
    <div class="flex-1 min-h-0 kanban-wrapper custom-scrollbar-h">
      <div class="kanban-board px-4 py-4">

        <div
          v-for="(col, colIndex) in columns"
          :key="col.id"
          class="kanban-col"
          :class="{ 'col-drag-over': dragOverCol === col.id }"
          :style="`--accent: ${col.accent}; --accent-rgb: ${col.accentRgb}; --accent-bg: ${col.accentBg}; animation-delay: ${colIndex * 80}ms`"
          @dragover="handleDragOver($event, col.id)"
          @dragleave="handleDragLeave"
          @drop="handleDrop($event, col.id)"
        >
          <!-- Column header -->
          <div class="col-header">
            <div class="col-header-left">
              <div class="col-icon">
                <component :is="col.icon" class="w-4 h-4" />
              </div>
              <span class="col-title">{{ col.title }}</span>
            </div>
            <div class="col-count">{{ filteredCrmCards[col.id]?.length || 0 }}</div>
          </div>

          <!-- Progress bar -->
          <div class="col-progress-track">
            <div class="col-progress-fill"
              :style="`width: ${totalCards ? Math.round((filteredCrmCards[col.id]?.length||0)/totalCards*100) : 0}%; background: ${col.accent}`">
            </div>
          </div>

          <!-- Cards list with TransitionGroup -->
          <div class="col-cards-area custom-scrollbar">
            <TransitionGroup name="card" tag="div" class="space-y-3">

              <div
                v-for="(card, cardIdx) in filteredCrmCards[col.id]"
                :key="card.id"
                draggable="true"
                @dragstart="handleDragStart($event, card, col.id)"
                class="crm-card"
                :style="`--accent: ${col.accent}; --accent-rgb: ${col.accentRgb}; --accent-bg: ${col.accentBg}; --delay: ${cardIdx * 50}ms`"
              >
                <!-- Accent top bar -->
                <div class="card-accent-bar"></div>

                <!-- Card body -->
                <div class="card-body">

                  <!-- Row 1: logo + company + age + actions -->
                  <div class="card-top-row">
                    <div class="card-company-block">
                      <!-- Logo -->
                      <div class="card-logo">
                        <img
                          v-if="getCompanyLogoUrl(card.company_name) && !logoErrors[card.id]"
                          :src="getCompanyLogoUrl(card.company_name)" :alt="card.company_name"
                          class="w-8 h-8 object-contain"
                          @error="onLogoError(card.id)"
                        />
                        <span v-else class="card-logo-fallback" :style="`color: ${col.accent}`">{{ getInitial(card.company_name) }}</span>
                      </div>
                      <div class="card-company-info">
                        <p class="card-company-name">{{ card.company_name || 'Entreprise' }}</p>
                        <p class="card-age">
                          <ClockIcon class="w-3 h-3 inline" />
                          {{ daysSince(card.created_at) === 0 ? "Aujourd'hui" : daysSince(card.created_at) === 1 ? 'Hier' : `Il y a ${daysSince(card.created_at)}j` }}
                          <span v-if="col.id === 'FOLLOW_UP' && daysSince(card.created_at) > 7" class="urgent-tag">
                            <FireIcon class="w-2.5 h-2.5" /> Urgent
                          </span>
                        </p>
                      </div>
                    </div>
                    <div class="card-actions">
                      <a v-if="card.url" :href="card.url" target="_blank" class="card-action-btn" @click.stop>
                        <ArrowTopRightOnSquareIcon class="w-3.5 h-3.5" />
                      </a>
                      <button @click.stop="deleteCard(card.id, col.id)" class="card-action-btn card-action-delete">
                        <TrashIcon class="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </div>

                  <!-- Job title -->
                  <h4 class="card-job-title">{{ card.job_title }}</h4>

                  <!-- Notes -->
                  <p v-if="card.notes" class="card-notes">{{ card.notes }}</p>

                  <!-- Footer: status + CTA -->
                  <div class="card-footer">
                    <span class="card-status-pill">
                      <component :is="col.icon" class="w-3 h-3" />
                      {{ col.label }}
                    </span>

                    <button v-if="col.id === 'TO_APPLY'" @click.stop="openAdaptCvModal(card)" class="card-cta">
                      <SparklesIcon class="w-3 h-3" />Adapter CV
                    </button>
                    <button v-else-if="col.id === 'FOLLOW_UP'" @click.stop="generateFollowup(card)" class="card-cta">
                      <BellAlertIcon class="w-3 h-3" />Relancer
                      <span v-if="card.follow_up_count" class="opacity-60 ml-0.5">×{{ card.follow_up_count }}</span>
                    </button>
                    <button v-else-if="col.id === 'INTERVIEW'" @click.stop="goToInterview(card)" class="card-cta">
                      <CheckBadgeIcon class="w-3 h-3" />Préparer
                    </button>
                    <div v-else-if="col.id === 'APPLIED'" class="card-cta card-cta-passive">
                      <ClockIcon class="w-3 h-3" />En attente
                    </div>
                    <div v-else-if="col.id === 'OFFER'" class="card-cta card-cta-passive">
                      <TrophyIcon class="w-3 h-3" />Résultat
                    </div>
                  </div>
                </div>

                <!-- Drag handle hint -->
                <div class="card-drag-hint">
                  <Bars3Icon class="w-4 h-4" />
                </div>
              </div>

            </TransitionGroup>

            <!-- Empty drop zone -->
            <Transition name="fade">
              <div v-if="!crmCards[col.id]?.length" class="col-empty-zone"
                :class="{ 'col-empty-active': dragOverCol === col.id }">
                <div class="col-empty-icon">
                  <PlusIcon class="w-6 h-6" />
                </div>
                <p>{{ dragOverCol === col.id ? 'Déposer ici' : 'Glissez une carte ici' }}</p>
              </div>
            </Transition>
          </div>
        </div>

      </div>
    </div>

    <!-- ═══ FOLLOW-UP MODAL ═══ -->
    <Transition name="modal">
      <div v-if="showFollowupPopup" class="modal-backdrop" @click.self="closeFollowup">
        <div class="modal-panel">
          <div class="modal-header modal-header-rose">
            <div class="modal-header-icon" style="background: rgba(239,68,68,0.1)">
              <BellAlertIcon class="w-5 h-5 text-red-500" />
            </div>
            <div>
              <h3 class="modal-title">Email de relance généré</h3>
              <p class="modal-subtitle">{{ followupCard?.job_title }} · {{ followupCard?.company_name }}
                <span v-if="followupCount" class="text-red-500 font-bold"> · Relance #{{ followupCount }}</span>
              </p>
            </div>
            <button @click="closeFollowup" class="modal-close"><XMarkIcon class="w-5 h-5" /></button>
          </div>
          <div class="modal-body">
            <div v-if="isGeneratingFollowup" class="modal-loading">
              <div class="modal-spinner"></div>
              <p>L'IA rédige votre relance…</p>
            </div>
            <div v-else>
              <div class="modal-email-preview">{{ followupEmail }}</div>
              <div class="modal-footer-row">
                <button @click="copyEmail" class="modal-btn" :class="copied ? 'modal-btn-success' : 'modal-btn-secondary'">
                  <CheckIcon v-if="copied" class="w-4 h-4" />
                  <ClipboardDocumentIcon v-else class="w-4 h-4" />
                  {{ copied ? 'Copié !' : 'Copier' }}
                </button>
                <button @click="closeFollowup" class="modal-btn modal-btn-ghost">Fermer</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Transition>

    <!-- ═══ ADAPT CV MODAL ═══ -->
    <Transition name="modal">
      <div v-if="showAdaptCvModal" class="modal-backdrop" @click.self="closeAdaptCvModal">
        <div class="modal-panel">
          <div class="modal-header modal-header-indigo">
            <div class="modal-header-icon" style="background: rgba(99,102,241,0.1)">
              <SparklesIcon class="w-5 h-5 text-indigo-500" />
            </div>
            <div>
              <h3 class="modal-title">Adapter votre CV avec l'IA</h3>
              <p class="modal-subtitle">{{ adaptCvCard?.job_title }} · {{ adaptCvCard?.company_name }}</p>
            </div>
            <button @click="closeAdaptCvModal" class="modal-close"><XMarkIcon class="w-5 h-5" /></button>
          </div>
          <div class="modal-body">
            <div v-if="isAdaptingCv" class="modal-loading">
              <div class="modal-spinner modal-spinner-indigo"></div>
              <p>L'IA adapte votre CV à l'offre…</p>
            </div>
            <div v-else class="space-y-3">
              <p class="text-sm font-semibold text-slate-600 mb-3">Choisissez votre source :</p>
              <button @click="useProfileCv" class="adapt-option-btn">
                <div class="adapt-option-icon bg-indigo-600"><BriefcaseIcon class="w-5 h-5 text-white" /></div>
                <div><p class="font-bold text-slate-900 text-sm">Mon profil GoldArmy</p><p class="text-xs text-slate-500">CV enregistré dans votre compte</p></div>
              </button>
              <label class="adapt-option-btn cursor-pointer">
                <div class="adapt-option-icon bg-slate-200"><ArrowUpTrayIcon class="w-5 h-5 text-slate-600" /></div>
                <div><p class="font-bold text-slate-900 text-sm">Uploader un PDF</p><p class="text-xs text-slate-500">Choisissez depuis votre ordinateur</p></div>
                <input ref="adaptCvFileInput" type="file" accept=".pdf" class="hidden" @change="onAdaptFileSelected" />
              </label>
            </div>
          </div>
        </div>
      </div>
    </Transition>

    <!-- ═══ DOWNLOAD CV MODAL ═══ -->
    <Transition name="modal">
      <div v-if="showDownloadCvModal && adaptedData" class="modal-backdrop" @click.self="closeDownloadCvModal">
        <div class="modal-panel modal-panel-wide">
          <div class="modal-header modal-header-emerald">
            <div class="modal-header-icon" style="background: rgba(16,185,129,0.1)">
              <DocumentTextIcon class="w-5 h-5 text-emerald-500" />
            </div>
            <div><h3 class="modal-title">CV adapté prêt !</h3><p class="modal-subtitle">Choisissez un thème et téléchargez</p></div>
            <button @click="closeDownloadCvModal" class="modal-close"><XMarkIcon class="w-5 h-5" /></button>
          </div>
          <div class="modal-body">
            <p class="text-sm font-bold text-slate-700 mb-3">Thème :</p>
            <div class="grid grid-cols-2 gap-2 mb-5">
              <button v-for="theme in CV_THEMES" :key="theme.id" @click="selectedCvTheme = theme.id"
                class="theme-btn" :class="{ 'theme-btn-active': selectedCvTheme === theme.id }">
                <div class="w-4 h-4 rounded-full shrink-0" :style="`background: ${theme.colors[0]}`"></div>
                <span class="text-sm font-bold text-slate-800">{{ theme.name }}</span>
                <CheckIcon v-if="selectedCvTheme === theme.id" class="w-4 h-4 text-indigo-600 ml-auto" />
              </button>
            </div>
            <div class="modal-footer-row">
              <button @click="openCrmEditor" class="modal-btn modal-btn-secondary"><DocumentTextIcon class="w-4 h-4" />Modifier</button>
              <button @click="downloadAdaptedPdf" :disabled="isDownloadingPdf" class="modal-btn modal-btn-primary">
                <ArrowPathIcon v-if="isDownloadingPdf" class="w-4 h-4 animate-spin" />
                <ArrowUpTrayIcon v-else class="w-4 h-4" />
                {{ isDownloadingPdf ? 'Génération…' : 'Télécharger PDF' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </Transition>

    <!-- ═══ DELETE CONFIRM ═══ -->
    <Transition name="modal">
      <div v-if="showDeletePopup" class="modal-backdrop" @click.self="showDeletePopup = false; itemToDelete = null">
        <div class="modal-panel modal-panel-sm text-center">
          <div class="w-14 h-14 rounded-2xl bg-red-50 border border-red-100 flex items-center justify-center mx-auto mb-4">
            <TrashIcon class="w-7 h-7 text-red-500" />
          </div>
          <h3 class="text-lg font-black text-slate-900 mb-2">Supprimer cette candidature ?</h3>
          <p class="text-sm text-slate-500 mb-6">Cette action est irréversible.</p>
          <div class="flex gap-3">
            <button @click="showDeletePopup = false; itemToDelete = null" class="modal-btn modal-btn-ghost flex-1">Annuler</button>
            <button @click="confirmDeleteCard" class="modal-btn modal-btn-danger flex-1"><TrashIcon class="w-4 h-4" />Supprimer</button>
          </div>
        </div>
      </div>
    </Transition>

    <CvEditorModal :show="showCrmEditor" :cv-data="crmEditorData" @close="showCrmEditor = false" @save="saveCrmEditor" />
  </div>
</template>

<style scoped>
/* ════════════════════════════════════════
   ROOT & BACKGROUND
════════════════════════════════════════ */
.crm-root {
  background: linear-gradient(135deg, #f8faff 0%, #f0f4ff 40%, #faf5ff 100%);
  font-family: 'Inter', system-ui, sans-serif;
}

/* ════════════════════════════════════════
   HEADER
════════════════════════════════════════ */
.crm-header {
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(99, 102, 241, 0.08);
  box-shadow: 0 1px 20px rgba(99, 102, 241, 0.06);
}

.header-title-block { animation: slideDown 0.5s cubic-bezier(0.34, 1.56, 0.64, 1) both; }

.live-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 3px 10px;
  border-radius: 20px;
  background: rgba(16, 185, 129, 0.1);
  border: 1px solid rgba(16, 185, 129, 0.2);
  color: #059669;
  font-size: 10px;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  margin-bottom: 8px;
}
.live-dot {
  width: 7px; height: 7px;
  border-radius: 50%;
  background: #10b981;
  animation: pulse-dot 2s ease-in-out infinite;
}

.crm-title {
  font-size: 26px;
  font-weight: 900;
  color: #0f172a;
  letter-spacing: -0.02em;
  line-height: 1.2;
}
.crm-title-accent {
  background: linear-gradient(135deg, #f59e0b, #d97706);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
.crm-title-sub { color: #475569; font-weight: 700; }
.crm-subtitle { color: #94a3b8; font-size: 13px; margin-top: 2px; font-weight: 500; }

.refresh-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  border-radius: 12px;
  background: white;
  border: 1px solid #e2e8f0;
  color: #475569;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s ease;
  animation: fadeIn 0.5s ease both 0.2s;
  box-shadow: 0 1px 4px rgba(0,0,0,0.05);
}
.refresh-btn:hover { background: #f8fafc; border-color: #f59e0b; color: #d97706; transform: translateY(-1px); box-shadow: 0 4px 12px rgba(245,158,11,0.15); }

/* ── URL Input ── */
.url-input-wrapper { animation: slideUp 0.5s cubic-bezier(0.34, 1.56, 0.64, 1) both 0.15s; }
.url-input-icon { position: absolute; left: 14px; top: 50%; transform: translateY(-50%); color: #94a3b8; pointer-events: none; }
.url-input {
  width: 100%;
  background: rgba(248, 250, 255, 0.9);
  border: 1.5px solid rgba(245, 158, 11, 0.2);
  border-radius: 14px;
  color: #0f172a;
  font-size: 14px;
  padding: 13px 160px 13px 44px;
  transition: all 0.25s ease;
  box-shadow: 0 2px 8px rgba(245, 158, 11, 0.05);
  outline: none;
}
.url-input:focus { border-color: #f59e0b; box-shadow: 0 0 0 3px rgba(245, 158, 11, 0.15), 0 2px 8px rgba(245,158,11,0.1); background: white; }
.url-submit-btn {
  position: absolute;
  right: 6px; top: 6px; bottom: 6px;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 0 16px;
  border-radius: 10px;
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: white;
  font-size: 12px;
  font-weight: 800;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 2px 8px rgba(245,158,11,0.35);
}
.url-submit-btn:hover { transform: scale(1.02); box-shadow: 0 4px 16px rgba(245,158,11,0.45); }
.url-submit-btn:active { transform: scale(0.98); }
.url-submit-btn:disabled { opacity: 0.5; cursor: not-allowed; transform: none; }

/* ── Stats ── */
.stats-row {
  display: flex;
  gap: 10px;
  animation: slideUp 0.5s cubic-bezier(0.34, 1.56, 0.64, 1) both 0.25s;
}
.stat-card {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 11px 14px;
  background: white;
  border: 1.5px solid rgba(0,0,0,0.06);
  border-radius: 14px;
  position: relative;
  overflow: hidden;
  box-shadow: 0 1px 4px rgba(0,0,0,0.04);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  animation: popIn 0.4s cubic-bezier(0.34, 1.56, 0.64, 1) both;
}
.stat-card:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(0,0,0,0.08); }
.stat-card::after {
  content: '';
  position: absolute;
  bottom: 0; left: 0; right: 0;
  height: 2px;
  background: var(--accent, #6366f1);
  opacity: 0;
  transition: opacity 0.2s;
}
.stat-card:hover::after { opacity: 1; }
.stat-icon-wrap {
  width: 34px; height: 34px;
  border-radius: 10px;
  background: var(--accent-bg, rgba(99,102,241,0.08));
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.stat-number { font-size: 22px; font-weight: 900; color: #0f172a; line-height: 1; }
.stat-label { font-size: 10px; font-weight: 600; color: #94a3b8; margin-top: 2px; }
.stat-bar-track { position: absolute; bottom: 0; left: 0; right: 0; height: 2px; background: rgba(0,0,0,0.04); }
.stat-bar-fill { height: 100%; transition: width 1s cubic-bezier(0.34, 1.56, 0.64, 1); border-radius: 0 2px 2px 0; }

/* ════════════════════════════════════════
   KANBAN BOARD
════════════════════════════════════════ */
.kanban-wrapper { overflow-x: auto; overflow-y: hidden; -webkit-overflow-scrolling: touch; }
.kanban-board { display: flex; gap: 14px; height: 100%; min-width: max-content; }

/* ── Column ── */
.kanban-col {
  width: 292px;
  display: flex;
  flex-direction: column;
  background: rgba(255, 255, 255, 0.75);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1.5px solid rgba(255, 255, 255, 0.9);
  border-radius: 20px;
  flex-shrink: 0;
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
  box-shadow: 0 4px 16px rgba(0,0,0,0.05), inset 0 1px 0 rgba(255,255,255,0.8);
  animation: slideUp 0.5s cubic-bezier(0.34, 1.56, 0.64, 1) both;
  overflow: hidden;
}
.kanban-col:hover { box-shadow: 0 8px 28px rgba(0,0,0,0.09), inset 0 1px 0 rgba(255,255,255,0.9); }
.col-drag-over {
  border-color: var(--accent, #6366f1) !important;
  box-shadow: 0 0 0 3px rgba(var(--accent-rgb, 99,102,241), 0.2), 0 8px 28px rgba(var(--accent-rgb, 99,102,241), 0.15) !important;
  transform: scale(1.02) !important;
  background: rgba(255, 255, 255, 0.92) !important;
}

.col-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 14px 10px;
  flex-shrink: 0;
}
.col-header-left { display: flex; align-items: center; gap: 8px; }
.col-icon {
  width: 28px; height: 28px;
  border-radius: 8px;
  background: var(--accent-bg);
  display: flex; align-items: center; justify-content: center;
  color: var(--accent);
}
.col-title { font-size: 13px; font-weight: 800; color: #1e293b; letter-spacing: -0.01em; }
.col-count {
  font-size: 11px; font-weight: 900;
  min-width: 22px; height: 22px;
  display: flex; align-items: center; justify-content: center;
  border-radius: 20px;
  background: var(--accent-bg);
  color: var(--accent);
  padding: 0 6px;
}
.col-progress-track { height: 2px; background: rgba(0,0,0,0.05); margin: 0 14px 10px; border-radius: 2px; flex-shrink: 0; }
.col-progress-fill { height: 100%; border-radius: 2px; transition: width 1.2s cubic-bezier(0.34, 1.56, 0.64, 1); }
.col-cards-area { flex: 1; min-height: 0; overflow-y: auto; padding: 0 10px 10px; }

/* ── Card ── */
.crm-card {
  position: relative;
  cursor: grab;
  animation: cardEntry 0.45s cubic-bezier(0.34, 1.56, 0.64, 1) both;
  animation-delay: var(--delay, 0ms);
}
.crm-card:active { cursor: grabbing; }

.card-accent-bar {
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 3px;
  background: linear-gradient(90deg, var(--accent), transparent);
  border-radius: 14px 14px 0 0;
  opacity: 0;
  transition: opacity 0.25s ease;
  z-index: 1;
}
.crm-card:hover .card-accent-bar { opacity: 1; }

.card-body {
  background: white;
  border: 1.5px solid rgba(0, 0, 0, 0.06);
  border-radius: 14px;
  padding: 13px;
  transition: all 0.25s cubic-bezier(0.34, 1.56, 0.64, 1);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  overflow: hidden;
  position: relative;
}
.crm-card:hover .card-body {
  border-color: rgba(var(--accent-rgb), 0.25);
  box-shadow: 0 8px 28px rgba(var(--accent-rgb), 0.1), 0 2px 8px rgba(0,0,0,0.05);
  transform: translateY(-3px);
}
.crm-card:active .card-body { transform: scale(0.97) !important; opacity: 0.8; }

/* Subtle glow bg on hover */
.card-body::after {
  content: '';
  position: absolute;
  bottom: -20px; right: -20px;
  width: 80px; height: 80px;
  border-radius: 50%;
  background: radial-gradient(circle, var(--accent), transparent 70%);
  opacity: 0;
  transition: opacity 0.3s ease;
  pointer-events: none;
}
.crm-card:hover .card-body::after { opacity: 0.06; }

.card-top-row { display: flex; align-items: flex-start; justify-content: space-between; gap: 8px; margin-bottom: 10px; }
.card-company-block { display: flex; align-items: center; gap: 9px; min-width: 0; flex: 1; }
.card-logo {
  width: 38px; height: 38px;
  border-radius: 10px;
  border: 1px solid rgba(0,0,0,0.07);
  background: #f8fafc;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
  overflow: hidden;
  box-shadow: 0 1px 4px rgba(0,0,0,0.07);
}
.card-logo-fallback { font-size: 17px; font-weight: 900; }
.card-company-info { min-width: 0; }
.card-company-name { font-size: 11px; font-weight: 700; color: #475569; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.card-age { font-size: 10px; color: #94a3b8; display: flex; align-items: center; gap: 4px; margin-top: 2px; }
.urgent-tag {
  display: inline-flex; align-items: center; gap: 2px;
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
  padding: 1px 6px;
  border-radius: 20px;
  font-size: 9px; font-weight: 800;
  animation: urgentPulse 2s ease-in-out infinite;
}

.card-actions { display: flex; gap: 4px; flex-shrink: 0; opacity: 0; transition: opacity 0.2s ease; }
.crm-card:hover .card-actions { opacity: 1; }
.card-action-btn {
  width: 28px; height: 28px;
  border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  border: none; cursor: pointer;
  color: #94a3b8;
  background: #f1f5f9;
  transition: all 0.2s ease;
  text-decoration: none;
}
.card-action-btn:hover { background: #e0e7ff; color: #6366f1; transform: scale(1.1); }
.card-action-delete:hover { background: #fee2e2; color: #ef4444; }

.card-job-title {
  font-size: 14px;
  font-weight: 800;
  color: #0f172a;
  line-height: 1.35;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  margin-bottom: 8px;
  letter-spacing: -0.01em;
  transition: color 0.2s ease;
}
.crm-card:hover .card-job-title { color: var(--accent); }

.card-notes {
  font-size: 11px;
  color: #64748b;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  line-height: 1.5;
  background: rgba(248, 250, 252, 0.8);
  border-radius: 8px;
  padding: 7px 9px;
  margin-bottom: 10px;
  border: 1px solid rgba(0,0,0,0.04);
}

.card-footer { display: flex; align-items: center; justify-content: space-between; gap: 8px; margin-top: 10px; padding-top: 10px; border-top: 1px solid rgba(0,0,0,0.05); }
.card-status-pill {
  display: inline-flex; align-items: center; gap: 4px;
  font-size: 10px; font-weight: 700;
  padding: 3px 9px; border-radius: 20px;
  background: var(--accent-bg);
  color: var(--accent);
}
.card-cta {
  display: inline-flex; align-items: center; gap: 4px;
  font-size: 10px; font-weight: 800;
  padding: 5px 11px; border-radius: 20px;
  border: none; cursor: pointer;
  background: var(--accent-bg);
  color: var(--accent);
  transition: all 0.2s cubic-bezier(0.34, 1.56, 0.64, 1);
  flex-shrink: 0;
}
.card-cta:hover { background: var(--accent); color: white; transform: scale(1.06); box-shadow: 0 4px 12px rgba(var(--accent-rgb), 0.35); }
.card-cta:active { transform: scale(0.95); }
.card-cta-passive { cursor: default; }
.card-cta-passive:hover { background: var(--accent-bg); color: var(--accent); transform: none; box-shadow: none; }

.card-drag-hint {
  position: absolute; top: 10px; right: 10px;
  color: #cbd5e1;
  opacity: 0;
  transition: opacity 0.2s ease;
}
.crm-card:hover .card-drag-hint { opacity: 1; }

/* ── Empty zone ── */
.col-empty-zone {
  min-height: 110px;
  border: 2px dashed rgba(0,0,0,0.1);
  border-radius: 14px;
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  gap: 8px;
  color: #94a3b8;
  font-size: 12px; font-weight: 600;
  transition: all 0.3s ease;
  background: rgba(248, 250, 255, 0.5);
}
.col-empty-active {
  border-color: var(--accent);
  background: var(--accent-bg);
  color: var(--accent);
  transform: scale(1.02);
}
.col-empty-icon {
  width: 36px; height: 36px;
  border-radius: 10px;
  background: rgba(0,0,0,0.05);
  display: flex; align-items: center; justify-content: center;
  transition: background 0.3s ease;
}
.col-empty-active .col-empty-icon { background: var(--accent-bg); color: var(--accent); }

/* ════════════════════════════════════════
   MODALS
════════════════════════════════════════ */
.modal-backdrop {
  position: fixed; inset: 0; z-index: 200;
  display: flex; align-items: center; justify-content: center; padding: 16px;
  background: rgba(15, 23, 42, 0.4);
  backdrop-filter: blur(8px);
}
.modal-panel {
  position: relative; z-index: 10;
  background: white;
  border: 1px solid rgba(0,0,0,0.08);
  border-radius: 24px;
  width: 100%; max-width: 560px;
  box-shadow: 0 24px 64px rgba(0,0,0,0.2);
  overflow: hidden;
}
.modal-panel-wide { max-width: 600px; }
.modal-panel-sm { max-width: 380px; padding: 28px; }
.modal-header {
  display: flex; align-items: flex-start; gap: 14px;
  padding: 20px 20px 16px;
  border-bottom: 1px solid rgba(0,0,0,0.06);
}
.modal-header-rose { background: linear-gradient(135deg, #fff5f5, #fff); }
.modal-header-indigo { background: linear-gradient(135deg, #f5f5ff, #fff); }
.modal-header-emerald { background: linear-gradient(135deg, #f0fdf8, #fff); }
.modal-header-icon { width: 40px; height: 40px; border-radius: 12px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.modal-title { font-weight: 800; font-size: 16px; color: #0f172a; }
.modal-subtitle { font-size: 12px; color: #94a3b8; margin-top: 2px; }
.modal-close { margin-left: auto; padding: 6px; color: #94a3b8; border: none; background: transparent; cursor: pointer; border-radius: 8px; transition: all 0.15s ease; flex-shrink: 0; }
.modal-close:hover { background: #f1f5f9; color: #475569; }
.modal-body { padding: 20px; }
.modal-loading { display: flex; flex-direction: column; align-items: center; gap: 12px; padding: 32px 0; }
.modal-loading p { font-size: 13px; color: #94a3b8; font-weight: 500; }
.modal-spinner { width: 36px; height: 36px; border: 3px solid #fee2e2; border-top-color: #ef4444; border-radius: 50%; animation: spin 0.7s linear infinite; }
.modal-spinner-indigo { border-color: #e0e7ff; border-top-color: #6366f1; }
.modal-email-preview { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 14px; padding: 14px; font-size: 13px; color: #334155; white-space: pre-line; line-height: 1.6; font-family: 'Inter', monospace; max-height: 240px; overflow-y: auto; }
.modal-footer-row { display: flex; gap: 10px; margin-top: 16px; }
.modal-btn {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 10px 16px; border-radius: 12px;
  font-size: 13px; font-weight: 700;
  cursor: pointer; border: none;
  transition: all 0.2s ease;
}
.modal-btn-primary { flex: 1; justify-content: center; background: linear-gradient(135deg, #10b981, #059669); color: white; box-shadow: 0 4px 12px rgba(16,185,129,0.3); }
.modal-btn-primary:hover { transform: translateY(-1px); box-shadow: 0 6px 20px rgba(16,185,129,0.4); }
.modal-btn-primary:disabled { opacity: 0.6; transform: none; }
.modal-btn-secondary { background: #f1f5f9; color: #475569; }
.modal-btn-secondary:hover { background: #e2e8f0; }
.modal-btn-success { background: rgba(16,185,129,0.1); color: #059669; }
.modal-btn-ghost { background: transparent; color: #475569; border: 1.5px solid #e2e8f0; }
.modal-btn-ghost:hover { background: #f8fafc; }
.modal-btn-danger { background: #ef4444; color: white; box-shadow: 0 4px 12px rgba(239,68,68,0.3); }
.modal-btn-danger:hover { background: #dc2626; transform: translateY(-1px); }

.adapt-option-btn {
  width: 100%; display: flex; align-items: center; gap: 12px;
  padding: 14px; border-radius: 14px;
  border: 1.5px solid #e2e8f0;
  background: white; cursor: pointer; text-align: left;
  transition: all 0.2s ease;
}
.adapt-option-btn:hover { border-color: #6366f1; background: #f5f5ff; transform: translateY(-1px); box-shadow: 0 4px 12px rgba(99,102,241,0.1); }
.adapt-option-icon { width: 40px; height: 40px; border-radius: 12px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }

.theme-btn {
  display: flex; align-items: center; gap: 8px;
  padding: 11px 14px; border-radius: 12px;
  border: 1.5px solid #e2e8f0; background: white;
  cursor: pointer; transition: all 0.2s ease;
}
.theme-btn:hover { border-color: #c7d2fe; background: #f5f5ff; }
.theme-btn-active { border-color: #6366f1; background: rgba(99,102,241,0.05); }

/* ════════════════════════════════════════
   VUE TRANSITIONS
════════════════════════════════════════ */
/* Card list */
.card-enter-active { animation: cardEntry 0.4s cubic-bezier(0.34, 1.56, 0.64, 1) both; }
.card-leave-active { animation: cardExit 0.3s cubic-bezier(0.4, 0, 0.6, 1) both; }
.card-move { transition: transform 0.4s cubic-bezier(0.34, 1.56, 0.64, 1); }

/* Modal */
.modal-enter-active { animation: modalIn 0.35s cubic-bezier(0.34, 1.56, 0.64, 1) both; }
.modal-leave-active { animation: modalOut 0.2s ease both; }
.modal-enter-active .modal-panel, .modal-leave-active .modal-panel { animation: none !important; }

/* Fade */
.fade-enter-active { animation: fadeIn 0.3s ease both; }
.fade-leave-active { animation: fadeOut 0.2s ease both; }

/* ════════════════════════════════════════
   KEYFRAMES
════════════════════════════════════════ */
@keyframes slideDown {
  from { transform: translateY(-20px); opacity: 0; }
  to   { transform: translateY(0);     opacity: 1; }
}
@keyframes slideUp {
  from { transform: translateY(20px); opacity: 0; }
  to   { transform: translateY(0);    opacity: 1; }
}
@keyframes popIn {
  from { transform: scale(0.88); opacity: 0; }
  to   { transform: scale(1);    opacity: 1; }
}
@keyframes cardEntry {
  from { transform: translateY(16px) scale(0.95); opacity: 0; }
  to   { transform: translateY(0) scale(1); opacity: 1; }
}
@keyframes cardExit {
  from { transform: scale(1); opacity: 1; max-height: 200px; }
  to   { transform: scale(0.9) translateX(20px); opacity: 0; max-height: 0; }
}
@keyframes modalIn {
  from { transform: scale(0.88) translateY(20px); opacity: 0; }
  to   { transform: scale(1) translateY(0); opacity: 1; }
}
@keyframes modalOut {
  from { transform: scale(1);    opacity: 1; }
  to   { transform: scale(0.92); opacity: 0; }
}
@keyframes fadeIn  { from { opacity: 0; } to { opacity: 1; } }
@keyframes fadeOut { from { opacity: 1; } to { opacity: 0; } }
@keyframes spin { to { transform: rotate(360deg); } }
@keyframes pulse-dot {
  0%, 100% { opacity: 1; transform: scale(1); }
  50%       { opacity: 0.6; transform: scale(0.85); }
}
@keyframes urgentPulse {
  0%, 100% { opacity: 1; }
  50%       { opacity: 0.6; }
}

/* ════════════════════════════════════════
   SCROLLBARS
════════════════════════════════════════ */
.custom-scrollbar::-webkit-scrollbar { width: 4px; }
.custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: rgba(99,102,241,0.15); border-radius: 10px; }
.custom-scrollbar::-webkit-scrollbar-thumb:hover { background: rgba(99,102,241,0.3); }

.custom-scrollbar-h::-webkit-scrollbar { height: 5px; }
.custom-scrollbar-h::-webkit-scrollbar-track { background: transparent; }
.custom-scrollbar-h::-webkit-scrollbar-thumb { background: rgba(99,102,241,0.12); border-radius: 10px; }
.custom-scrollbar-h::-webkit-scrollbar-thumb:hover { background: rgba(99,102,241,0.25); }

/* ── Mobile ── */
@media (max-width: 768px) {
  .kanban-col { width: 270px !important; }
  .stats-row { display: grid; grid-template-columns: repeat(3, 1fr); }
  .crm-title { font-size: 20px; }
}
</style>
