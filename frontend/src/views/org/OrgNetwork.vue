<script setup>
import { ref, onMounted, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { authFetch } from '@/utils/auth'
import {
  PlusIcon, TrashIcon, EnvelopeIcon, BuildingOffice2Icon,
  MagnifyingGlassIcon, UsersIcon, ClipboardDocumentIcon, XMarkIcon, LinkIcon,
  ArrowUpTrayIcon, SparklesIcon
} from '@heroicons/vue/24/outline'

const { t } = useI18n()
const loading = ref(true)
const contacts = ref([])
const showForm = ref(false)
const saving = ref(false)
const search = ref('')
const activeCat = ref('all')
const copiedId = ref('')
const form = ref({ name: '', category: 'partner', company: '', role: '', email: '', linkedin: '', notes: '' })
const suggestions = ref([])
const importing = ref(false)
const importMsg = ref('')
const fileInput = ref(null)

const STATUSES = computed(() => ({
  to_contact: { label: t('org.network.st_to_contact'), color: '#98A2B3', bg: '#F1F3F6' },
  contacted: { label: t('org.network.st_contacted'), color: '#D97706', bg: '#FEF3C7' },
  responded: { label: t('org.network.st_responded'), color: '#059669', bg: '#D1FAE5' },
}))
const STATUS_ORDER = ['to_contact', 'contacted', 'responded']
function statusMeta(s) { return STATUSES.value[s] || STATUSES.value.to_contact }

async function cycleStatus(c) {
  const cur = c.status || 'to_contact'
  const next = STATUS_ORDER[(STATUS_ORDER.indexOf(cur) + 1) % STATUS_ORDER.length]
  c.status = next
  try { await authFetch(`/api/org/network/${c.id}/status`, { method: 'PUT', body: JSON.stringify({ status: next }) }) } catch (e) {}
}

async function loadSuggestions() {
  try {
    const res = await authFetch('/api/org/network/suggestions')
    const json = await res.safeJson()
    if (json?.status === 'success') suggestions.value = json.data
  } catch (e) {}
}
async function addSuggestion(s) {
  try {
    const res = await authFetch('/api/org/network', {
      method: 'POST',
      body: JSON.stringify({ name: s.company, company: s.company, category: 'company', notes: t('org.network.from_cohort', { n: s.applicants }) })
    })
    const json = await res.safeJson()
    if (json?.status === 'success') {
      contacts.value.unshift(json.data)
      suggestions.value = suggestions.value.filter(x => x.company !== s.company)
    }
  } catch (e) {}
}

function parseCSV(text) {
  const lines = text.split(/\r?\n/).filter(l => l.trim())
  if (!lines.length) return []
  const splitRow = (line) => {
    const out = []; let cur = ''; let q = false
    for (let i = 0; i < line.length; i++) {
      const ch = line[i]
      if (ch === '"') { if (q && line[i + 1] === '"') { cur += '"'; i++ } else q = !q }
      else if (ch === ',' && !q) { out.push(cur); cur = '' }
      else cur += ch
    }
    out.push(cur); return out.map(s => s.trim())
  }
  const headers = splitRow(lines[0]).map(h => h.toLowerCase())
  const map = { nom: 'name', name: 'name', entreprise: 'company', company: 'company', fonction: 'role', role: 'role', poste: 'role', email: 'email', courriel: 'email', linkedin: 'linkedin', notes: 'notes', categorie: 'category', category: 'category', 'catégorie': 'category' }
  return lines.slice(1).map(line => {
    const cells = splitRow(line); const obj = {}
    headers.forEach((h, i) => { const k = map[h]; if (k) obj[k] = cells[i] || '' })
    return obj
  }).filter(o => o.name)
}

async function handleFile(e) {
  const file = e.target.files?.[0]
  if (!file) return
  importing.value = true; importMsg.value = ''
  try {
    const text = await file.text()
    const rows = parseCSV(text)
    if (!rows.length) { importMsg.value = t('org.network.import_empty'); return }
    const res = await authFetch('/api/org/network/import', { method: 'POST', body: JSON.stringify({ contacts: rows }) })
    const json = await res.safeJson()
    if (json?.status === 'success') {
      importMsg.value = t('org.network.import_done', { n: json.imported, s: json.skipped })
      await load()
    }
  } catch (err) { importMsg.value = t('common.error') }
  finally { importing.value = false; if (fileInput.value) fileInput.value.value = ''; setTimeout(() => importMsg.value = '', 5000) }
}

const CATS = computed(() => [
  { key: 'partner', label: t('org.network.cat_partner'), color: '#F59E0B', bg: '#FEF3C7', fg: '#B45309' },
  { key: 'recruiter', label: t('org.network.cat_recruiter'), color: '#6366F1', bg: '#EEF2FF', fg: '#4F46E5' },
  { key: 'company', label: t('org.network.cat_company'), color: '#0EA5E9', bg: '#E0F2FE', fg: '#0284C7' },
  { key: 'mentor', label: t('org.network.cat_mentor'), color: '#10B981', bg: '#D1FAE5', fg: '#059669' },
  { key: 'other', label: t('org.network.cat_other'), color: '#98A2B3', bg: '#F1F3F6', fg: '#475467' },
])
function catMeta(k) { return CATS.value.find(c => c.key === k) || CATS.value[4] }

const filtered = computed(() => {
  const q = search.value.toLowerCase().trim()
  return contacts.value.filter(c => {
    const matchCat = activeCat.value === 'all' || (c.category || 'other') === activeCat.value
    const matchQ = !q || [c.name, c.company, c.role, c.email].some(f => (f || '').toLowerCase().includes(q))
    return matchCat && matchQ
  })
})
const stats = computed(() => ({
  total: contacts.value.length,
  companies: new Set(contacts.value.map(c => (c.company || '').trim().toLowerCase()).filter(Boolean)).size,
  withEmail: contacts.value.filter(c => c.email).length,
}))
function catCount(key) { return contacts.value.filter(c => (c.category || 'other') === key).length }

async function load() {
  loading.value = true
  try {
    const res = await authFetch('/api/org/network')
    const json = await res.safeJson()
    if (json?.status === 'success') contacts.value = json.data
    loadSuggestions()
  } catch (e) {} finally { loading.value = false }
}
async function add() {
  if (!form.value.name.trim()) return
  saving.value = true
  try {
    const res = await authFetch('/api/org/network', { method: 'POST', body: JSON.stringify(form.value) })
    const json = await res.safeJson()
    if (json?.status === 'success') {
      contacts.value.unshift(json.data)
      form.value = { name: '', category: 'partner', company: '', role: '', email: '', linkedin: '', notes: '' }
      showForm.value = false
    }
  } catch (e) {} finally { saving.value = false }
}
async function remove(c) {
  if (!confirm(t('org.network.remove_confirm', { name: c.name }))) return
  try { const res = await authFetch(`/api/org/network/${c.id}`, { method: 'DELETE' }); if (res.ok) contacts.value = contacts.value.filter(x => x.id !== c.id) } catch (e) {}
}
function copyEmail(c) { if (c.email) { navigator.clipboard?.writeText(c.email); copiedId.value = c.id; setTimeout(() => copiedId.value = '', 1500) } }
function initials(n) { return (n || '?')[0].toUpperCase() }

onMounted(load)
</script>

<template>
  <div class="on">
    <header class="on__head">
      <div>
        <h1 class="on__title">{{ t('org.nav.network') }}</h1>
        <p class="on__sub">{{ t('org.network.sub') }}</p>
      </div>
      <div class="on__head-actions">
        <input ref="fileInput" type="file" accept=".csv,text/csv" class="on__file" @change="handleFile" />
        <button class="on__ghost" :disabled="importing" @click="fileInput?.click()">
          <ArrowUpTrayIcon class="w-4 h-4" /> {{ importing ? t('common.loading') : t('org.network.import') }}
        </button>
        <button class="on__cta" @click="showForm = !showForm"><PlusIcon class="w-4 h-4" /> {{ t('org.network.add') }}</button>
      </div>
    </header>
    <p v-if="importMsg" class="on__import-msg">{{ importMsg }}</p>

    <!-- Suggestions from cohort applications -->
    <section v-if="suggestions.length" class="on__suggest">
      <div class="on__suggest-head">
        <span class="on__suggest-title"><SparklesIcon class="w-4 h-4" /> {{ t('org.network.suggest_title') }}</span>
        <span class="on__suggest-sub">{{ t('org.network.suggest_sub') }}</span>
      </div>
      <div class="on__suggest-list">
        <button v-for="s in suggestions" :key="s.company" class="on__suggest-chip" @click="addSuggestion(s)">
          <span class="on__suggest-name">{{ s.company }}</span>
          <span class="on__suggest-count">{{ s.applicants }}</span>
          <PlusIcon class="w-3.5 h-3.5" />
        </button>
      </div>
    </section>

    <!-- Stats -->
    <div class="on__stats">
      <div class="on__stat"><UsersIcon class="on__stat-ic on__stat-ic--g" /><div><b>{{ stats.total }}</b><span>{{ t('org.network.contacts') }}</span></div></div>
      <div class="on__stat"><BuildingOffice2Icon class="on__stat-ic on__stat-ic--s" /><div><b>{{ stats.companies }}</b><span>{{ t('org.network.companies') }}</span></div></div>
      <div class="on__stat"><EnvelopeIcon class="on__stat-ic on__stat-ic--i" /><div><b>{{ stats.withEmail }}</b><span>{{ t('org.network.with_email') }}</span></div></div>
    </div>

    <!-- Add form -->
    <transition name="on-form">
      <div v-if="showForm" class="on__form">
        <div class="on__form-head">{{ t('org.network.add') }}<button class="on__form-close" @click="showForm = false"><XMarkIcon class="w-4 h-4" /></button></div>
        <div class="on__form-grid">
          <input v-model="form.name" :placeholder="t('org.network.name')" class="on__input" />
          <select v-model="form.category" class="on__input">
            <option v-for="c in CATS" :key="c.key" :value="c.key">{{ c.label }}</option>
          </select>
          <input v-model="form.company" :placeholder="t('org.network.company')" class="on__input" />
          <input v-model="form.role" :placeholder="t('org.network.role')" class="on__input" />
          <input v-model="form.email" type="email" :placeholder="t('org.network.email')" class="on__input" />
          <input v-model="form.linkedin" :placeholder="t('org.network.linkedin')" class="on__input" />
        </div>
        <input v-model="form.notes" :placeholder="t('org.network.notes')" class="on__input on__input--full" />
        <button class="on__save" @click="add" :disabled="saving">{{ saving ? t('common.saving') : t('org.network.save') }}</button>
      </div>
    </transition>

    <!-- Toolbar: search + category filters -->
    <div class="on__toolbar">
      <div class="on__search">
        <MagnifyingGlassIcon class="on__search-ic" />
        <input v-model="search" :placeholder="t('org.network.search')" />
      </div>
      <div class="on__cats">
        <button :class="['on__cat', { 'on__cat--active': activeCat === 'all' }]" @click="activeCat = 'all'">{{ t('org.community.all') }} <span class="on__cat-n">{{ contacts.length }}</span></button>
        <button v-for="c in CATS" :key="c.key" :class="['on__cat', { 'on__cat--active': activeCat === c.key }]" @click="activeCat = c.key">
          <span class="on__cat-dot" :style="{ background: c.color }"></span>{{ c.label }} <span class="on__cat-n">{{ catCount(c.key) }}</span>
        </button>
      </div>
    </div>

    <div v-if="loading" class="on__loading">{{ t('common.loading') }}…</div>
    <div v-else-if="!contacts.length" class="on__empty-block">
      <UsersIcon class="on__empty-ic" />
      <p>{{ t('org.network.empty') }}</p>
      <button class="on__empty-btn" @click="showForm = true">{{ t('org.network.add') }}</button>
    </div>
    <div v-else-if="!filtered.length" class="on__empty-block"><p>{{ t('org.network.no_match') }}</p></div>

    <div v-else class="on__grid">
      <div v-for="c in filtered" :key="c.id" class="on__card">
        <div class="on__card-top">
          <div class="on__avatar" :style="{ background: catMeta(c.category).color }">{{ initials(c.name) }}</div>
          <div class="on__id">
            <div class="on__name">{{ c.name }}</div>
            <div v-if="c.role || c.company" class="on__role">{{ c.role }}<span v-if="c.role && c.company"> · </span>{{ c.company }}</div>
          </div>
          <button class="on__del" @click="remove(c)"><TrashIcon class="w-4 h-4" /></button>
        </div>
        <div class="on__tags">
          <span class="on__tag" :style="{ background: catMeta(c.category).bg, color: catMeta(c.category).fg }">{{ catMeta(c.category).label }}</span>
          <button class="on__status" :style="{ background: statusMeta(c.status).bg, color: statusMeta(c.status).color }" @click="cycleStatus(c)" :title="t('org.network.cycle_status')">
            <span class="on__status-dot" :style="{ background: statusMeta(c.status).color }"></span>{{ statusMeta(c.status).label }}
          </button>
        </div>
        <p v-if="c.notes" class="on__notes">{{ c.notes }}</p>
        <div class="on__actions">
          <a v-if="c.email" :href="'mailto:' + c.email" class="on__action"><EnvelopeIcon class="w-3.5 h-3.5" /> {{ t('org.network.write') }}</a>
          <button v-if="c.email" class="on__action" @click="copyEmail(c)"><ClipboardDocumentIcon class="w-3.5 h-3.5" /> {{ copiedId === c.id ? t('org.invite.copied') : t('org.network.copy_email') }}</button>
          <a v-if="c.linkedin" :href="c.linkedin.startsWith('http') ? c.linkedin : 'https://' + c.linkedin" target="_blank" class="on__action"><LinkIcon class="w-3.5 h-3.5" /> LinkedIn</a>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.on { max-width: 1200px; margin: 0 auto; color: #101828; }
.on__head { display: flex; align-items: flex-end; justify-content: space-between; gap: 1rem; margin-bottom: 1.3rem; flex-wrap: wrap; }
.on__title { font-size: 1.9rem; font-weight: 800; margin: 0; letter-spacing: -0.03em; }
.on__sub { color: #667085; font-size: 0.92rem; margin: 0.3rem 0 0; }
.on__cta { display: inline-flex; align-items: center; gap: 0.45rem; padding: 0.7rem 1.15rem; border-radius: 999px; background: linear-gradient(135deg, #FBBF24, #F59E0B); color: #fff; border: none; font-weight: 700; font-size: 0.85rem; cursor: pointer; box-shadow: 0 10px 22px -10px rgba(245,158,11,0.7); transition: transform 0.15s; }
.on__cta:hover { transform: translateY(-2px); }
.on__head-actions { display: flex; gap: 0.6rem; }
.on__file { display: none; }
.on__ghost { display: inline-flex; align-items: center; gap: 0.45rem; padding: 0.7rem 1.15rem; border-radius: 999px; background: #fff; color: #344054; border: 1px solid #EEF0F3; font-weight: 700; font-size: 0.85rem; cursor: pointer; transition: border-color 0.15s; }
.on__ghost:hover { border-color: #D0D5DD; }
.on__ghost:disabled { opacity: 0.6; cursor: not-allowed; }
.on__import-msg { font-size: 0.82rem; font-weight: 600; color: #059669; margin: 0 0 1rem; }

.on__suggest { background: linear-gradient(155deg, #FFFBEB, #fff); border: 1px solid #FDE68A; border-radius: 1.5rem; padding: 1.25rem; margin-bottom: 1.1rem; }
.on__suggest-head { display: flex; align-items: baseline; gap: 0.6rem; margin-bottom: 0.9rem; flex-wrap: wrap; }
.on__suggest-title { display: inline-flex; align-items: center; gap: 0.4rem; font-weight: 800; font-size: 0.92rem; color: #B45309; }
.on__suggest-sub { font-size: 0.76rem; color: #98A2B3; }
.on__suggest-list { display: flex; flex-wrap: wrap; gap: 0.5rem; }
.on__suggest-chip { display: inline-flex; align-items: center; gap: 0.45rem; padding: 0.5rem 0.55rem 0.5rem 0.9rem; border-radius: 999px; background: #fff; border: 1px solid #FDE68A; color: #92400E; font-size: 0.8rem; font-weight: 700; cursor: pointer; transition: all 0.15s; }
.on__suggest-chip:hover { background: #FEF3C7; transform: translateY(-2px); }
.on__suggest-count { background: #FEF3C7; color: #B45309; border-radius: 999px; padding: 0.05rem 0.45rem; font-size: 0.68rem; }

.on__tags { display: flex; align-items: center; gap: 0.4rem; flex-wrap: wrap; margin-top: 0.8rem; }
.on__status { display: inline-flex; align-items: center; gap: 0.3rem; font-size: 0.62rem; font-weight: 800; text-transform: uppercase; padding: 0.2rem 0.55rem; border-radius: 999px; border: none; cursor: pointer; }
.on__status-dot { width: 0.45rem; height: 0.45rem; border-radius: 50%; }

.on__stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 0.9rem; margin-bottom: 1.1rem; }
.on__stat { display: flex; align-items: center; gap: 0.8rem; background: #fff; border: 1px solid #EEF0F3; border-radius: 1.25rem; padding: 1.1rem 1.2rem; box-shadow: 0 1px 2px rgba(16,24,40,0.03); }
.on__stat-ic { width: 2.4rem; height: 2.4rem; padding: 0.5rem; border-radius: 0.8rem; flex-shrink: 0; }
.on__stat-ic--g { color: #D97706; background: #FEF3C7; }
.on__stat-ic--s { color: #0284C7; background: #E0F2FE; }
.on__stat-ic--i { color: #4F46E5; background: #EEF2FF; }
.on__stat b { font-size: 1.4rem; font-weight: 800; color: #101828; display: block; line-height: 1; }
.on__stat span { font-size: 0.72rem; color: #98A2B3; text-transform: uppercase; font-weight: 600; }

.on__form { margin-bottom: 1.1rem; padding: 1.25rem; border-radius: 1.5rem; background: #fff; border: 1px solid #EEF0F3; box-shadow: 0 1px 2px rgba(16,24,40,0.03); }
.on__form-head { display: flex; align-items: center; justify-content: space-between; font-weight: 800; font-size: 0.9rem; margin-bottom: 0.8rem; }
.on__form-close { background: none; border: none; color: #98A2B3; cursor: pointer; }
.on__form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 0.6rem; margin-bottom: 0.6rem; }
.on__input { padding: 0.7rem 0.9rem; border-radius: 0.8rem; background: #F9FAFB; border: 1px solid #EEF0F3; color: #101828; font-size: 0.85rem; outline: none; }
.on__input:focus { border-color: #F59E0B; box-shadow: 0 0 0 3px rgba(245,158,11,0.12); background: #fff; }
.on__input--full { width: 100%; margin-bottom: 0.8rem; }
.on__save { padding: 0.7rem 1.4rem; border-radius: 0.9rem; background: linear-gradient(135deg, #FBBF24, #F59E0B); color: #fff; border: none; font-weight: 700; font-size: 0.85rem; cursor: pointer; }

.on__toolbar { display: flex; align-items: center; gap: 1rem; margin-bottom: 1.1rem; flex-wrap: wrap; }
.on__search { position: relative; flex: 1; min-width: 200px; }
.on__search-ic { position: absolute; left: 0.85rem; top: 50%; transform: translateY(-50%); width: 1.05rem; height: 1.05rem; color: #98A2B3; }
.on__search input { width: 100%; padding: 0.7rem 0.9rem 0.7rem 2.5rem; border-radius: 999px; background: #fff; border: 1px solid #EEF0F3; font-size: 0.85rem; color: #101828; outline: none; }
.on__search input:focus { border-color: #F59E0B; box-shadow: 0 0 0 3px rgba(245,158,11,0.12); }
.on__cats { display: flex; flex-wrap: wrap; gap: 0.4rem; }
.on__cat { display: inline-flex; align-items: center; gap: 0.35rem; padding: 0.5rem 0.85rem; border-radius: 999px; border: 1px solid #EEF0F3; background: #fff; color: #475467; font-size: 0.76rem; font-weight: 700; cursor: pointer; transition: all 0.15s; }
.on__cat:hover { border-color: #D0D5DD; }
.on__cat--active { background: #101828; color: #fff; border-color: #101828; }
.on__cat-dot { width: 0.5rem; height: 0.5rem; border-radius: 50%; }
.on__cat-n { font-size: 0.68rem; opacity: 0.7; }

.on__loading { padding: 4rem; text-align: center; color: #98A2B3; }
.on__empty-block { text-align: center; padding: 3rem 1rem; }
.on__empty-ic { width: 3rem; height: 3rem; color: #D0D5DD; margin: 0 auto 0.8rem; }
.on__empty-block p { color: #98A2B3; font-size: 0.9rem; margin: 0 0 1.1rem; }
.on__empty-btn { padding: 0.65rem 1.3rem; border-radius: 999px; background: #F9FAFB; border: 1px solid #EEF0F3; color: #344054; font-weight: 700; font-size: 0.82rem; cursor: pointer; }
.on__empty-btn:hover { border-color: #F59E0B; color: #D97706; }

.on__grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 0.9rem; }
.on__card { background: #fff; border: 1px solid #EEF0F3; border-radius: 1.4rem; padding: 1.25rem; box-shadow: 0 1px 2px rgba(16,24,40,0.03); transition: transform 0.15s, box-shadow 0.15s; }
.on__card:hover { transform: translateY(-3px); box-shadow: 0 14px 30px -18px rgba(16,24,40,0.28); }
.on__card-top { display: flex; align-items: center; gap: 0.7rem; }
.on__avatar { width: 2.7rem; height: 2.7rem; border-radius: 50%; color: #fff; display: flex; align-items: center; justify-content: center; font-weight: 800; flex-shrink: 0; }
.on__id { flex: 1; min-width: 0; }
.on__name { font-weight: 800; font-size: 0.95rem; color: #101828; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.on__role { font-size: 0.76rem; color: #667085; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.on__del { background: none; border: none; color: #FCA5A5; cursor: pointer; flex-shrink: 0; }
.on__del:hover { color: #EF4444; }
.on__tag { display: inline-block; font-size: 0.62rem; font-weight: 800; text-transform: uppercase; padding: 0.2rem 0.55rem; border-radius: 999px; }
.on__notes { font-size: 0.78rem; color: #667085; margin: 0.7rem 0 0; line-height: 1.4; }
.on__actions { display: flex; flex-wrap: wrap; gap: 0.4rem; margin-top: 0.9rem; padding-top: 0.8rem; border-top: 1px solid #F1F3F6; }
.on__action { display: inline-flex; align-items: center; gap: 0.3rem; padding: 0.4rem 0.7rem; border-radius: 999px; background: #F9FAFB; border: 1px solid #EEF0F3; color: #475467; font-size: 0.72rem; font-weight: 600; cursor: pointer; text-decoration: none; transition: all 0.15s; }
.on__action:hover { border-color: #F59E0B; color: #D97706; }

.on-form-enter-active, .on-form-leave-active { transition: opacity 0.2s; }
.on-form-enter-from, .on-form-leave-to { opacity: 0; }
@media (max-width: 600px) { .on__form-grid { grid-template-columns: 1fr; } }
</style>
