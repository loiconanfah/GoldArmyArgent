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
  TrashIcon,
  DocumentTextIcon,
  ArrowUpTrayIcon,
  TrophyIcon,
  XCircleIcon,
  ClockIcon,
  FireIcon,
  Bars3Icon,
} from '@heroicons/vue/24/outline'

const { t } = useI18n()
const router = useRouter()

const columns = [
  { id: 'TO_APPLY',  title: 'À Postuler',          icon: EnvelopeIcon,   accent: '#d97706', accentBg: 'rgba(217,119,6,0.1)',   label: 'À postuler' },
  { id: 'APPLIED',   title: 'Candidature Envoyée',  icon: ChartBarIcon,   accent: '#6366f1', accentBg: 'rgba(99,102,241,0.1)',  label: 'Envoyée' },
  { id: 'FOLLOW_UP', title: 'Relance Requise',      icon: BellAlertIcon,  accent: '#ef4444', accentBg: 'rgba(239,68,68,0.1)',   label: 'Relance' },
  { id: 'INTERVIEW', title: 'Entretien',            icon: CheckBadgeIcon, accent: '#16a34a', accentBg: 'rgba(22,163,74,0.1)',   label: 'Entretien' },
  { id: 'OFFER',     title: 'Offre Reçue',          icon: TrophyIcon,     accent: '#7c3aed', accentBg: 'rgba(124,58,237,0.1)',  label: 'Offre' },
]

const crmCards = ref({ 'TO_APPLY': [], 'APPLIED': [], 'FOLLOW_UP': [], 'INTERVIEW': [], 'OFFER': [] })
const isLoading = ref(true)
const draggedItem = ref(null)
const dragOverCol = ref(null)

// Follow-up popup
const showFollowupPopup = ref(false)
const followupEmail = ref('')
const followupCard = ref(null)
const isGeneratingFollowup = ref(false)
const followupCount = ref(0)
const copied = ref(false)

// Delete popup
const showDeletePopup = ref(false)
const itemToDelete = ref(null)

// Adapter CV
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

const CV_THEMES = CV_TEMPLATES.map(t => ({
  id: t.id,
  name: t.label,
  colors: [t.accentColor, t.accentColor],
  build: t.build,
}))

// ── Stats ──
const totalCards   = computed(() => Object.values(crmCards.value).flat().length)
const interviewCount = computed(() => crmCards.value['INTERVIEW']?.length || 0)
const followUpCount  = computed(() => crmCards.value['FOLLOW_UP']?.length || 0)
const appliedCount   = computed(() => crmCards.value['APPLIED']?.length || 0)
const offerCount     = computed(() => crmCards.value['OFFER']?.length || 0)

const conversionRate = computed(() => {
  const sent = appliedCount.value + followUpCount.value + interviewCount.value + offerCount.value
  if (!sent) return 0
  return Math.round(((interviewCount.value + offerCount.value) / sent) * 100)
})

const fetchCrmData = async () => {
  isLoading.value = true
  try {
    const res = await authFetch('/api/crm')
    const json = await res.json()
    const rawData = json.data || []
    const grouped = { 'TO_APPLY': [], 'APPLIED': [], 'FOLLOW_UP': [], 'INTERVIEW': [], 'OFFER': [] }
    rawData.forEach(item => { if (grouped[item.status]) grouped[item.status].push(item) })
    crmCards.value = grouped
  } catch(e) { console.error('Failed to fetch CRM data', e) }
  finally { isLoading.value = false }
}

const newLinkUrl = ref('')
const isAddingLink = ref(false)

const addFromLink = async () => {
  if (!newLinkUrl.value.trim()) return
  isAddingLink.value = true
  try {
    const res = await authFetch('/api/crm/link', {
      method: 'POST',
      body: JSON.stringify({ url: newLinkUrl.value.trim() })
    })
    const json = await res.json()
    if (res.ok && json.status === 'success') {
      toastState.addToast('Candidature ajoutée avec succès !', 'success')
      newLinkUrl.value = ''
      await fetchCrmData()
    } else {
      toastState.addToast(`Erreur : ${json.detail || json.message || t('common.error')}`, 'error')
    }
  } catch(e) {
    toastState.addToast(t('common.network_error'), 'error')
  } finally {
    isAddingLink.value = false
  }
}

// ── Drag & Drop ──
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

const deleteCard = (cardId, colId) => { itemToDelete.value = { cardId, colId }; showDeletePopup.value = true }

const confirmDeleteCard = async () => {
  if (!itemToDelete.value) return
  const { cardId, colId } = itemToDelete.value
  const previousState = [...crmCards.value[colId]]
  crmCards.value[colId] = crmCards.value[colId].filter(c => c.id !== cardId)
  showDeletePopup.value = false
  itemToDelete.value = null
  try {
    const res = await authFetch(`/api/crm/${cardId}`, { method: 'DELETE' })
    if (!res.ok) throw new Error('Failed to delete')
    toastState.addToast('Candidature supprimée.', 'success')
  } catch(err) {
    crmCards.value[colId] = previousState
    toastState.addToast(t('common.error'), 'error')
  }
}

const handleDragOver = (e, colId) => { e.preventDefault(); dragOverCol.value = colId }
const handleDragLeave = () => { dragOverCol.value = null }

// ── Helpers ──
const daysSince = (iso) => {
  if (!iso) return null
  const diff = Date.now() - new Date(iso).getTime()
  return Math.floor(diff / (1000 * 60 * 60 * 24))
}
const formatDate = (iso) => {
  if (!iso) return '?'
  const d = new Date(iso)
  return `${d.getDate().toString().padStart(2,'0')}/${(d.getMonth()+1).toString().padStart(2,'0')}`
}
const getInitial = (n) => n ? n.charAt(0).toUpperCase() : '?'

const getCompanyLogoUrl = (companyName) => {
  if (!companyName) return null
  const slug = companyName.toLowerCase()
    .replace(/[^a-z0-9\s]/g, '')
    .trim()
    .split(/\s+/)[0]
  if (!slug || slug.length < 2) return null
  return `https://logo.clearbit.com/${slug}.com`
}

const logoErrors = ref({})
const onLogoError = (cardId) => { logoErrors.value[cardId] = true }

// ── Actions ──
const goToInterview = (card) => {
  router.push({
    path: '/interview',
    query: { company: card.company_name, jobTitle: card.job_title, jobDetails: card.notes }
  })
}

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
      followupEmail.value = `Limite atteinte : ${data.detail || 'Veuillez passer au forfait Pro pour plus de relances.'}`
      return
    }
    if (!res.ok) {
      const errData = await res.json().catch(() => ({}))
      followupEmail.value = errData.detail || errData.message || t('common.error')
      return
    }
    const data = await res.json()
    if (data.status === 'success') {
      followupEmail.value = (data.email && String(data.email).trim()) || 'Aucun texte généré. Réessayez.'
      followupCount.value = data.followUpCount
      const col = crmCards.value['FOLLOW_UP']
      const idx = col.findIndex(c => c.id === card.id)
      if (idx !== -1) col[idx].follow_up_count = data.followUpCount
    } else {
      followupEmail.value = data.detail || data.message || t('common.error')
    }
  } catch (e) {
    followupEmail.value = e.message
  } finally {
    isGeneratingFollowup.value = false
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

// ── CV Adapt ──
const openAdaptCvModal = (card) => {
  adaptCvCard.value = card; cvTextForAdapt.value = ''; adaptedData.value = null
  showAdaptCvModal.value = true; showDownloadCvModal.value = false
}
const useProfileCv = async () => {
  if (!adaptCvCard.value) return
  try {
    const res = await authFetch('/api/profile')
    const json = await res.json()
    const cvText = json?.data?.cv_text
    if (!cvText || cvText.length < 50) { toastState.addToast('Aucun CV enregistré dans votre profil.', 'info'); return }
    cvTextForAdapt.value = cvText
    await runAdapt()
  } catch (e) { toastState.addToast(t('common.network_error'), 'error') }
}
const onAdaptFileSelected = async (e) => {
  const file = e.target?.files?.[0]
  if (!file || !file.name.toLowerCase().endsWith('.pdf')) { toastState.addToast('Veuillez sélectionner un fichier PDF.', 'info'); return }
  const formData = new FormData()
  formData.append('file', file)
  try {
    const res = await authFetch('/api/parse-pdf', { method: 'POST', body: formData })
    const json = await res.json()
    const text = json?.text
    if (!text || text.length < 50) { toastState.addToast('Impossible de lire le PDF.', 'error'); return }
    cvTextForAdapt.value = text
    await runAdapt()
  } catch (err) { toastState.addToast(t('common.network_error'), 'error') }
  e.target.value = ''
}
const runAdapt = async () => {
  if (!adaptCvCard.value || !cvTextForAdapt.value || cvTextForAdapt.value.length < 50) { toastState.addToast('CV manquant ou trop court.', 'info'); return }
  isAdaptingCv.value = true
  try {
    const res = await authFetch('/api/adapt-cv', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ job_title: adaptCvCard.value.job_title, job_description: adaptCvCard.value.notes || '', cv_text: cvTextForAdapt.value })
    })
    const json = await res.json()
    if (json.status === 'success' && json.data) {
      adaptedData.value = json.data; showAdaptCvModal.value = false; showDownloadCvModal.value = true; selectedCvTheme.value = 'goldarmy'
    } else { toastState.addToast(json.detail || "Erreur lors de l'adaptation.", 'error') }
  } catch (e) { toastState.addToast(t('common.network_error'), 'error') }
  finally { isAdaptingCv.value = false }
}
const closeAdaptCvModal = () => { showAdaptCvModal.value = false; adaptCvCard.value = null; cvTextForAdapt.value = ''; adaptedData.value = null }

const buildCvJsonFromMarkdown = (markdown) => {
  const lines = (markdown || '').split(/\n/).filter(Boolean)
  const fullName = lines[0]?.replace(/^#+\s*/, '').trim() || 'Candidat'
  return { full_name: fullName, summary: '', experiences: [{ title: 'Expérience professionnelle', company: '', start_date: '', end_date: '', bullets: lines }], skills: {}, education: [] }
}

const showCrmEditor = ref(false)
const crmEditorData = ref(null)
const openCrmEditor = () => {
  if (!adaptedData.value?.cv_json && !adaptedData.value?.markdown) return
  let cvJson = null
  if (adaptedData.value.cv_json) {
    if (typeof adaptedData.value.cv_json === 'object') { cvJson = adaptedData.value.cv_json }
    else { try { cvJson = JSON.parse(adaptedData.value.cv_json) } catch (e) {} }
  }
  if (!cvJson) cvJson = buildCvJsonFromMarkdown(adaptedData.value.markdown || '')
  crmEditorData.value = cvJson; showCrmEditor.value = true
}
const saveCrmEditor = (newData) => {
  adaptedData.value.cv_json = newData
  if (adaptCvCard.value) adaptCvCard.value.adapted_cv = newData
  showCrmEditor.value = false; crmEditorData.value = null
  toastState.addToast('Modifications sauvegardées.', 'success')
}
const downloadAdaptedPdf = async () => {
  if (!adaptedData.value?.markdown && !adaptedData.value?.cv_json) return
  isDownloadingPdf.value = true
  try {
    let cvJson = null
    if (adaptedData.value.cv_json) {
      if (typeof adaptedData.value.cv_json === 'object') { cvJson = adaptedData.value.cv_json }
      else { try { cvJson = JSON.parse(adaptedData.value.cv_json) } catch (e) {} }
    }
    if (!cvJson) cvJson = buildCvJsonFromMarkdown(adaptedData.value.markdown || '')
    const filename = `CV_Adapte_${(adaptCvCard.value?.job_title || 'offre').replace(/\s+/g,'_').slice(0,30)}`
    const tpl = CV_THEMES.find(t => t.id === selectedCvTheme.value) || CV_THEMES[0]
    const html = tpl.build(cvJson, null)
    const res = await authFetch('/api/generate-cv-pdf-html', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ html, filename }) })
    if (!res.ok) { const err = await res.json(); toastState.addToast(err.detail || 'Erreur génération PDF', 'error'); return }
    const blob = await res.blob()
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a'); a.href = url; a.download = filename + '.pdf'; a.click(); URL.revokeObjectURL(url)
    toastState.addToast('CV téléchargé.', 'success')
    showDownloadCvModal.value = false; adaptedData.value = null
  } catch (e) { toastState.addToast('Erreur lors du téléchargement.', 'error') }
  finally { isDownloadingPdf.value = false }
}
const closeDownloadCvModal = () => { showDownloadCvModal.value = false; adaptedData.value = null }

onMounted(() => { fetchCrmData() })
</script>

<template>
  <div class="flex flex-col h-full min-h-0 bg-slate-50">

    <!-- ═══ PAGE HEADER ═══ -->
    <div class="shrink-0 px-6 pt-6 pb-5 border-b border-slate-200 bg-white shadow-sm">
      <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 max-w-[2000px] mx-auto">
        <div>
          <span class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-600 text-[10px] font-black tracking-widest uppercase mb-2">
            <span class="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
            Pipeline Actif
          </span>
          <h1 class="text-2xl font-display font-black text-slate-900 tracking-tight">
            Central <span class="text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 to-purple-600">CRM Candidatures</span>
          </h1>
          <p class="text-slate-500 text-sm mt-0.5">Glissez-déposez vos opportunités pour piloter votre pipeline.</p>
        </div>
        <button @click="fetchCrmData" class="flex items-center gap-2 text-sm font-bold bg-white hover:bg-slate-50 text-slate-700 px-4 py-2.5 rounded-xl border border-slate-200 shadow-sm transition-colors shrink-0">
          <ArrowPathIcon class="w-4 h-4" :class="{'animate-spin': isLoading}" />
          Actualiser
        </button>
      </div>

      <!-- ADD URL -->
      <div class="mt-4 max-w-[2000px] mx-auto">
        <form @submit.prevent="addFromLink" class="relative flex items-center">
          <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
            <LinkIcon class="w-5 h-5 text-slate-400" />
          </div>
          <input
            v-model="newLinkUrl"
            type="url"
            placeholder="Collez l'URL d'une offre (LinkedIn, Indeed, Welcome to the Jungle...) pour l'ajouter au CRM"
            class="w-full bg-slate-50 border border-slate-200 text-slate-900 text-sm rounded-xl focus:ring-2 focus:ring-indigo-500/40 focus:border-indigo-500 block pl-11 pr-36 py-3.5 shadow-sm transition-all"
            :disabled="isAddingLink"
            required
          >
          <button
            type="submit"
            :disabled="isAddingLink || !newLinkUrl.trim()"
            class="absolute right-2 top-2 bottom-2 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 disabled:opacity-40 disabled:cursor-not-allowed text-white font-bold text-xs px-4 rounded-lg flex items-center gap-2 transition-all shadow-md"
          >
            <ArrowPathIcon v-if="isAddingLink" class="w-4 h-4 animate-spin" />
            <SparklesIcon v-else class="w-4 h-4" />
            {{ isAddingLink ? 'Analyse IA...' : 'Ajouter au CRM' }}
          </button>
        </form>
      </div>

      <!-- STATS ROW -->
      <div class="mt-4 max-w-[2000px] mx-auto grid grid-cols-5 gap-2">
        <div v-for="col in columns" :key="col.id" class="stat-pill">
          <component :is="col.icon" class="w-4 h-4 shrink-0" :style="`color: ${col.accent}`" />
          <div class="min-w-0">
            <p class="text-xl font-black text-slate-900 leading-none">{{ crmCards[col.id]?.length || 0 }}</p>
            <p class="text-[10px] text-slate-500 font-semibold truncate mt-0.5">{{ col.title }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- ═══ KANBAN BOARD ═══ -->
    <div class="flex-1 min-h-0 kanban-scroll-wrapper px-4 py-5 custom-scrollbar-h">
      <div class="kanban-board">

        <!-- ── COLUMN ── -->
        <div
          v-for="col in columns"
          :key="col.id"
          class="kanban-col flex flex-col rounded-2xl shrink-0 transition-all duration-200"
          :class="dragOverCol === col.id ? 'drag-over' : ''"
          @dragover="handleDragOver($event, col.id)"
          @dragleave="handleDragLeave"
          @drop="handleDrop($event, col.id)"
        >
          <!-- Column Header -->
          <div class="shrink-0 px-4 pt-4 pb-3">
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-2">
                <div class="w-7 h-7 rounded-lg flex items-center justify-center" :style="`background: ${col.accentBg}`">
                  <component :is="col.icon" class="w-4 h-4" :style="`color: ${col.accent}`" />
                </div>
                <span class="font-bold text-sm text-slate-800">{{ col.title }}</span>
              </div>
              <span class="text-xs font-black px-2 py-0.5 rounded-full" :style="`background: ${col.accentBg}; color: ${col.accent}`">
                {{ crmCards[col.id]?.length || 0 }}
              </span>
            </div>
            <!-- Progress bar -->
            <div class="mt-3 h-0.5 rounded-full w-full overflow-hidden bg-slate-100">
              <div class="h-full rounded-full transition-all duration-700" :style="`background: ${col.accent}; width: ${totalCards ? Math.round((crmCards[col.id]?.length||0)/totalCards*100) : 0}%`"></div>
            </div>
          </div>

          <!-- Cards Area -->
          <div class="flex-1 min-h-0 overflow-y-auto px-3 pb-3 space-y-2.5 custom-scrollbar">

            <!-- ── CARD ── -->
            <div
              v-for="card in crmCards[col.id]"
              :key="card.id"
              draggable="true"
              @dragstart="handleDragStart($event, card, col.id)"
              class="crm-card group"
            >
              <div class="crm-card-inner" :style="`--accent: ${col.accent}`">

                <!-- TOP: Logo + Company + Date + Actions -->
                <div class="flex items-start justify-between gap-2 mb-3">
                  <div class="flex items-center gap-2.5 min-w-0 flex-1">
                    <!-- Company logo -->
                    <div class="w-10 h-10 rounded-xl overflow-hidden shrink-0 bg-slate-50 border border-slate-100 flex items-center justify-center shadow-sm">
                      <img
                        v-if="getCompanyLogoUrl(card.company_name) && !logoErrors[card.id]"
                        :src="getCompanyLogoUrl(card.company_name)"
                        :alt="card.company_name"
                        class="w-8 h-8 object-contain"
                        @error="onLogoError(card.id)"
                      />
                      <span v-else class="text-base font-black" :style="`color: ${col.accent}`">{{ getInitial(card.company_name) }}</span>
                    </div>
                    <div class="min-w-0">
                      <p class="text-xs font-bold text-slate-700 truncate">{{ card.company_name || 'Entreprise' }}</p>
                      <p class="text-[10px] text-slate-400 mt-0.5 flex items-center gap-1">
                        <ClockIcon class="w-3 h-3 inline shrink-0" />
                        {{ daysSince(card.created_at) === 0 ? "Aujourd'hui" : daysSince(card.created_at) === 1 ? 'Hier' : `Il y a ${daysSince(card.created_at)}j` }}
                        <span v-if="col.id === 'FOLLOW_UP' && daysSince(card.created_at) > 7" class="text-red-500 font-black ml-0.5">· Urgent</span>
                      </p>
                    </div>
                  </div>
                  <!-- Actions (visible on hover) -->
                  <div class="flex items-center gap-1 shrink-0 opacity-0 group-hover:opacity-100 transition-opacity duration-150">
                    <a v-if="card.url" :href="card.url" target="_blank" title="Voir l'offre"
                      class="p-1.5 text-slate-400 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg transition-all" @click.stop>
                      <ArrowTopRightOnSquareIcon class="w-3.5 h-3.5" />
                    </a>
                    <button @click.stop="deleteCard(card.id, col.id)" title="Supprimer"
                      class="p-1.5 text-slate-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-all">
                      <TrashIcon class="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>

                <!-- Job title -->
                <h4 class="font-black text-slate-900 text-[14px] leading-snug line-clamp-2 mb-2">{{ card.job_title }}</h4>

                <!-- Notes -->
                <p v-if="card.notes" class="text-[11px] text-slate-500 line-clamp-2 leading-relaxed mb-3 bg-slate-50 rounded-lg px-2.5 py-1.5">{{ card.notes }}</p>

                <!-- Divider -->
                <div class="h-px bg-slate-100 mb-3"></div>

                <!-- Footer: status badge + CTA -->
                <div class="flex items-center justify-between gap-2">
                  <span class="inline-flex items-center gap-1 text-[10px] font-bold px-2 py-1 rounded-full" :style="`background: ${col.accentBg}; color: ${col.accent}`">
                    <component :is="col.icon" class="w-3 h-3" />
                    {{ col.label }}
                  </span>

                  <button v-if="col.id === 'TO_APPLY'" @click.stop="openAdaptCvModal(card)"
                    class="crm-cta" :style="`background: ${col.accentBg}; color: ${col.accent}`">
                    <SparklesIcon class="w-3 h-3" />Adapter CV
                  </button>
                  <button v-else-if="col.id === 'FOLLOW_UP'" @click.stop="generateFollowup(card)"
                    class="crm-cta" :style="`background: ${col.accentBg}; color: ${col.accent}`">
                    <BellAlertIcon class="w-3 h-3" />Relancer
                    <span v-if="card.follow_up_count" class="ml-0.5 opacity-60">×{{ card.follow_up_count }}</span>
                  </button>
                  <button v-else-if="col.id === 'INTERVIEW'" @click.stop="goToInterview(card)"
                    class="crm-cta" :style="`background: ${col.accentBg}; color: ${col.accent}`">
                    <CheckBadgeIcon class="w-3 h-3" />Préparer
                  </button>
                  <div v-else-if="col.id === 'APPLIED'"
                    class="crm-cta" :style="`background: ${col.accentBg}; color: ${col.accent}`">
                    <ClockIcon class="w-3 h-3" />En attente
                  </div>
                  <div v-else-if="col.id === 'OFFER'"
                    class="crm-cta" :style="`background: ${col.accentBg}; color: ${col.accent}`">
                    <TrophyIcon class="w-3 h-3" />Résultat
                  </div>
                </div>
              </div>
            </div>

            <!-- Empty Drop Zone -->
            <div v-if="!crmCards[col.id]?.length"
              class="h-28 rounded-2xl border-2 border-dashed flex flex-col items-center justify-center gap-2 text-xs font-bold transition-all"
              :class="dragOverCol === col.id ? 'border-indigo-300 bg-indigo-50 text-indigo-500' : 'border-slate-200 text-slate-400 bg-white/50'"
            >
              <PlusIcon class="w-5 h-5 opacity-50" />
              <span>{{ dragOverCol === col.id ? 'Déposer ici' : 'Glissez une carte' }}</span>
            </div>
          </div>
        </div>

      </div>
    </div>

    <!-- ═══ FOLLOW-UP EMAIL POPUP ═══ -->
    <div v-if="showFollowupPopup" class="fixed inset-0 z-[200] flex items-center justify-center p-4">
      <div class="absolute inset-0 bg-slate-900/40 backdrop-blur-sm" @click="closeFollowup"></div>
      <div class="relative z-10 bg-white border border-slate-200 rounded-3xl shadow-2xl w-full max-w-2xl overflow-hidden animate-scale-in">
        <div class="px-6 pt-6 pb-4 border-b border-slate-100 bg-gradient-to-r from-rose-50 to-pink-50 flex items-start justify-between gap-4">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-xl bg-white border border-rose-100 flex items-center justify-center shadow-sm">
              <BellAlertIcon class="w-5 h-5 text-rose-500" />
            </div>
            <div>
              <h3 class="font-bold text-slate-900">Email de relance généré</h3>
              <p class="text-xs text-slate-500 mt-0.5">
                {{ followupCard?.job_title }} — {{ followupCard?.company_name }}
                <span v-if="followupCount" class="ml-2 text-rose-500 font-bold">Relance #{{ followupCount }}</span>
              </p>
            </div>
          </div>
          <button @click="closeFollowup" class="p-1.5 text-slate-400 hover:text-slate-700 rounded-lg hover:bg-slate-100 transition-colors shrink-0">
            <XMarkIcon class="w-5 h-5" />
          </button>
        </div>
        <div class="p-6">
          <div v-if="isGeneratingFollowup" class="flex flex-col items-center gap-3 py-8">
            <ArrowPathIcon class="w-8 h-8 text-rose-400 animate-spin" />
            <p class="text-sm text-slate-500 font-medium">L'IA rédige votre relance…</p>
          </div>
          <div v-else>
            <div class="bg-slate-50 border border-slate-200 rounded-2xl p-4 text-sm text-slate-700 whitespace-pre-line leading-relaxed font-mono max-h-64 overflow-y-auto custom-scrollbar">{{ followupEmail }}</div>
            <div class="mt-4 flex gap-3">
              <button @click="copyEmail" class="flex-1 flex items-center justify-center gap-2 py-3 rounded-xl font-bold text-sm border transition-all"
                :class="copied ? 'bg-emerald-50 border-emerald-200 text-emerald-700' : 'bg-white border-slate-200 text-slate-700 hover:bg-slate-50'">
                <CheckIcon v-if="copied" class="w-4 h-4" />
                <ClipboardDocumentIcon v-else class="w-4 h-4" />
                {{ copied ? 'Copié !' : 'Copier le texte' }}
              </button>
              <button @click="closeFollowup" class="px-5 py-3 rounded-xl font-bold text-sm bg-white border border-slate-200 text-slate-600 hover:bg-slate-50 transition-colors">
                Fermer
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ═══ ADAPT CV MODAL ═══ -->
    <div v-if="showAdaptCvModal" class="fixed inset-0 z-[200] flex items-center justify-center p-4">
      <div class="absolute inset-0 bg-slate-900/40 backdrop-blur-sm" @click="closeAdaptCvModal"></div>
      <div class="relative z-10 bg-white border border-slate-200 rounded-3xl shadow-2xl w-full max-w-lg overflow-hidden animate-scale-in">
        <div class="px-6 pt-6 pb-4 border-b border-slate-100 bg-gradient-to-r from-indigo-50 to-purple-50 flex items-start justify-between gap-4">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-xl bg-white border border-indigo-100 flex items-center justify-center shadow-sm">
              <SparklesIcon class="w-5 h-5 text-indigo-500" />
            </div>
            <div>
              <h3 class="font-bold text-slate-900">Adapter votre CV avec l'IA</h3>
              <p class="text-xs text-slate-500 mt-0.5">{{ adaptCvCard?.job_title }} — {{ adaptCvCard?.company_name }}</p>
            </div>
          </div>
          <button @click="closeAdaptCvModal" class="p-1.5 text-slate-400 hover:text-slate-700 rounded-lg hover:bg-slate-100 transition-colors shrink-0">
            <XMarkIcon class="w-5 h-5" />
          </button>
        </div>
        <div class="p-6">
          <div v-if="isAdaptingCv" class="flex flex-col items-center gap-3 py-8">
            <ArrowPathIcon class="w-8 h-8 text-indigo-400 animate-spin" />
            <p class="text-sm text-slate-500 font-medium">L'IA adapte votre CV à l'offre…</p>
          </div>
          <div v-else class="space-y-3">
            <p class="text-sm text-slate-600 font-medium">Choisissez votre source de CV :</p>
            <button @click="useProfileCv" class="w-full flex items-center gap-3 p-4 rounded-2xl border-2 border-indigo-100 bg-indigo-50 hover:border-indigo-300 hover:bg-indigo-100 transition-all text-left">
              <div class="w-10 h-10 rounded-xl bg-indigo-600 flex items-center justify-center shrink-0">
                <BriefcaseIcon class="w-5 h-5 text-white" />
              </div>
              <div>
                <p class="font-bold text-slate-900 text-sm">Utiliser mon profil GoldArmy</p>
                <p class="text-xs text-slate-500 mt-0.5">CV enregistré dans votre compte</p>
              </div>
            </button>
            <label class="w-full flex items-center gap-3 p-4 rounded-2xl border-2 border-slate-200 bg-white hover:border-slate-300 hover:bg-slate-50 transition-all text-left cursor-pointer">
              <div class="w-10 h-10 rounded-xl bg-slate-200 flex items-center justify-center shrink-0">
                <ArrowUpTrayIcon class="w-5 h-5 text-slate-600" />
              </div>
              <div>
                <p class="font-bold text-slate-900 text-sm">Uploader un PDF</p>
                <p class="text-xs text-slate-500 mt-0.5">Choisissez un fichier depuis votre ordinateur</p>
              </div>
              <input ref="adaptCvFileInput" type="file" accept=".pdf" class="hidden" @change="onAdaptFileSelected" />
            </label>
          </div>
        </div>
      </div>
    </div>

    <!-- ═══ DOWNLOAD CV MODAL ═══ -->
    <div v-if="showDownloadCvModal && adaptedData" class="fixed inset-0 z-[200] flex items-center justify-center p-4">
      <div class="absolute inset-0 bg-slate-900/40 backdrop-blur-sm" @click="closeDownloadCvModal"></div>
      <div class="relative z-10 bg-white border border-slate-200 rounded-3xl shadow-2xl w-full max-w-xl overflow-hidden animate-scale-in">
        <div class="px-6 pt-6 pb-4 border-b border-slate-100 bg-gradient-to-r from-emerald-50 to-teal-50 flex items-start justify-between gap-4">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-xl bg-white border border-emerald-100 flex items-center justify-center shadow-sm">
              <DocumentTextIcon class="w-5 h-5 text-emerald-500" />
            </div>
            <div>
              <h3 class="font-bold text-slate-900">CV adapté prêt !</h3>
              <p class="text-xs text-slate-500 mt-0.5">Choisissez un thème et téléchargez</p>
            </div>
          </div>
          <button @click="closeDownloadCvModal" class="p-1.5 text-slate-400 hover:text-slate-700 rounded-lg hover:bg-slate-100 transition-colors shrink-0">
            <XMarkIcon class="w-5 h-5" />
          </button>
        </div>
        <div class="p-6">
          <p class="text-sm font-bold text-slate-700 mb-3">Thème du CV :</p>
          <div class="grid grid-cols-2 gap-2 mb-5">
            <button v-for="theme in CV_THEMES" :key="theme.id" @click="selectedCvTheme = theme.id"
              class="flex items-center gap-2 p-3 rounded-xl border-2 transition-all text-left"
              :class="selectedCvTheme === theme.id ? 'border-indigo-500 bg-indigo-50' : 'border-slate-200 bg-white hover:border-slate-300'">
              <div class="w-5 h-5 rounded-full shrink-0 border-2 border-white shadow" :style="`background: ${theme.colors[0]}`"></div>
              <span class="text-sm font-bold text-slate-800">{{ theme.name }}</span>
              <CheckIcon v-if="selectedCvTheme === theme.id" class="w-4 h-4 text-indigo-600 ml-auto" />
            </button>
          </div>
          <div class="flex gap-3">
            <button @click="openCrmEditor" class="flex items-center gap-2 py-3 px-4 rounded-xl font-bold text-sm bg-white border border-slate-200 text-slate-700 hover:bg-slate-50 transition-colors">
              <DocumentTextIcon class="w-4 h-4" />Modifier le CV
            </button>
            <button @click="downloadAdaptedPdf" :disabled="isDownloadingPdf"
              class="flex-1 flex items-center justify-center gap-2 py-3 rounded-xl font-bold text-sm bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 disabled:opacity-50 text-white shadow-lg shadow-emerald-500/20 transition-all">
              <ArrowPathIcon v-if="isDownloadingPdf" class="w-4 h-4 animate-spin" />
              <ArrowUpTrayIcon v-else class="w-4 h-4" />
              {{ isDownloadingPdf ? 'Génération...' : 'Télécharger le PDF' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- ═══ DELETE CONFIRMATION ═══ -->
    <div v-if="showDeletePopup" class="fixed inset-0 z-[200] flex items-center justify-center p-4">
      <div class="absolute inset-0 bg-slate-900/40 backdrop-blur-sm" @click="showDeletePopup = false; itemToDelete = null"></div>
      <div class="relative z-10 bg-white border border-slate-200 rounded-3xl shadow-2xl w-full max-w-sm overflow-hidden animate-scale-in text-center p-6">
        <div class="w-14 h-14 rounded-2xl bg-red-50 flex items-center justify-center mx-auto mb-4 border border-red-100">
          <TrashIcon class="w-7 h-7 text-red-500" />
        </div>
        <h3 class="text-lg font-display font-black text-slate-900 mb-2">Supprimer cette candidature ?</h3>
        <p class="text-sm text-slate-500 mb-6">Cette opportunité sera effacée définitivement. Cette action est irréversible.</p>
        <div class="flex gap-3">
          <button @click="showDeletePopup = false; itemToDelete = null" class="flex-1 py-3 px-4 rounded-xl font-bold text-sm bg-white hover:bg-slate-50 text-slate-700 border border-slate-200 transition-colors">
            Annuler
          </button>
          <button @click="confirmDeleteCard" class="flex-1 py-3 px-4 rounded-xl font-bold text-sm bg-red-600 hover:bg-red-500 text-white shadow-lg shadow-red-500/20 transition-all flex items-center justify-center gap-2">
            <TrashIcon class="w-4 h-4" />Supprimer
          </button>
        </div>
      </div>
    </div>

    <CvEditorModal
      :show="showCrmEditor"
      :cv-data="crmEditorData"
      @close="showCrmEditor = false"
      @save="saveCrmEditor"
    />
  </div>
</template>

<style scoped>
/* ── Scrollbars ── */
.custom-scrollbar::-webkit-scrollbar { width: 4px; }
.custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: #e2e8f0; border-radius: 10px; }
.custom-scrollbar::-webkit-scrollbar-thumb:hover { background: #cbd5e1; }

.custom-scrollbar-h::-webkit-scrollbar { height: 5px; }
.custom-scrollbar-h::-webkit-scrollbar-track { background: transparent; }
.custom-scrollbar-h::-webkit-scrollbar-thumb { background: #e2e8f0; border-radius: 10px; }
.custom-scrollbar-h::-webkit-scrollbar-thumb:hover { background: #cbd5e1; }

/* ── Animations ── */
@keyframes scale-in {
  from { transform: scale(0.94); opacity: 0; }
  to   { transform: scale(1);    opacity: 1; }
}
.animate-scale-in { animation: scale-in 0.2s ease-out forwards; }

/* ── Board layout ── */
.kanban-scroll-wrapper { overflow-x: auto; overflow-y: hidden; -webkit-overflow-scrolling: touch; }
.kanban-board { display: flex; gap: 14px; height: 100%; min-width: max-content; }

/* ── Column ── */
.kanban-col {
  width: 290px;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  box-shadow: 0 1px 4px rgba(0,0,0,0.05);
}
.kanban-col.drag-over {
  border-color: #6366f1;
  box-shadow: 0 0 0 2px rgba(99,102,241,0.2);
  transform: scale(1.01);
}

/* ── Stat pill ── */
.stat-pill {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  background: #fff;
  border: 1px solid #e8edf3;
  border-radius: 14px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}

/* ── Card wrapper ── */
.crm-card { cursor: grab; transition: transform 0.15s ease; }
.crm-card:active { cursor: grabbing; transform: scale(0.97); opacity: 0.75; }
.crm-card:hover  { transform: translateY(-2px); }

/* ── Card inner ── */
.crm-card-inner {
  background: #ffffff;
  border: 1px solid #e8edf3;
  border-radius: 14px;
  padding: 14px;
  position: relative;
  overflow: hidden;
  box-shadow: 0 2px 6px rgba(0,0,0,0.05);
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}
.crm-card:hover .crm-card-inner {
  border-color: #c7d2fe;
  box-shadow: 0 4px 20px rgba(99,102,241,0.1);
}
/* Top accent stripe on hover */
.crm-card-inner::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 3px;
  background: var(--accent, #6366f1);
  opacity: 0;
  transition: opacity 0.2s;
  border-radius: 14px 14px 0 0;
}
.crm-card:hover .crm-card-inner::before { opacity: 1; }

/* ── CTA pill ── */
.crm-cta {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 10px;
  font-weight: 800;
  letter-spacing: 0.01em;
  border: none;
  cursor: pointer;
  transition: filter 0.15s ease, transform 0.1s ease;
  flex-shrink: 0;
}
.crm-cta:hover  { filter: brightness(0.9); transform: scale(1.04); }
.crm-cta:active { transform: scale(0.97); }

/* ── Mobile ── */
@media (max-width: 768px) {
  .kanban-col { width: 265px !important; }
  .stat-pill p { display: none; }
}
</style>
