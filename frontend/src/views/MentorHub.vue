<script setup>
// Hub Mentors — marketplace de mentorat à la demande (« Uber des mentors »).
// Registre ouvert (tout user peut devenir mentor), mise en relation gratuite,
// demandes de session, événements/ateliers avec RSVP, avis après session.
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { authFetch } from '@/utils/auth'
import { toastState } from '@/store/toastState'
import {
  MagnifyingGlassIcon, MapPinIcon, CalendarDaysIcon, PlusIcon, TrashIcon,
  XMarkIcon, PaperAirplaneIcon, AcademicCapIcon, ClockIcon, VideoCameraIcon,
  UsersIcon, SparklesIcon, ChatBubbleLeftRightIcon, CheckCircleIcon, LinkIcon,
  BriefcaseIcon
} from '@heroicons/vue/24/outline'
import { StarIcon } from '@heroicons/vue/24/solid'

const { t } = useI18n()

const tab = ref('discover')
const tabs = computed(() => [
  { key: 'discover', label: t('mentorhub.tab_discover'), icon: SparklesIcon },
  { key: 'requests', label: t('mentorhub.tab_requests'), icon: ChatBubbleLeftRightIcon },
  { key: 'events', label: t('mentorhub.tab_events'), icon: CalendarDaysIcon },
  { key: 'mentor', label: t('mentorhub.tab_mentor'), icon: AcademicCapIcon },
])

const SERVICE_TYPES = ['cv_review', 'interview_sim', 'career_advice', 'salary_nego', 'reconversion', 'networking', 'other']
function svcLabel(k) { return t('mentorhub.svc_' + (SERVICE_TYPES.includes(k) ? k : 'other')) }

// ── Découvrir ────────────────────────────────────────────────────────────────
const mentors = ref([])
const loadingMentors = ref(true)
const q = ref('')
const specialtyFilter = ref('')
const allSpecialties = computed(() => {
  const set = new Set()
  mentors.value.forEach(m => (m.specialties || []).forEach(s => set.add(s)))
  return [...set].sort()
})
const filteredMentors = computed(() => {
  let list = mentors.value
  if (specialtyFilter.value) list = list.filter(m => (m.specialties || []).includes(specialtyFilter.value))
  const term = q.value.trim().toLowerCase()
  if (term) list = list.filter(m =>
    (m.full_name || '').toLowerCase().includes(term) ||
    (m.headline || '').toLowerCase().includes(term) ||
    (m.specialties || []).some(s => s.toLowerCase().includes(term)))
  return list
})

async function loadMentors() {
  loadingMentors.value = true
  try {
    const r = await authFetch('/api/mentors')
    const j = await r.safeJson()
    if (j?.status === 'success') mentors.value = j.data
  } catch (e) {} finally { loadingMentors.value = false }
}

// ── Fiche mentor détaillée ─────────────────────────────────────────────────
const showDetail = ref(false)
const detailMentor = ref(null)
const loadingDetail = ref(false)
async function openDetail(m) {
  detailMentor.value = m
  showDetail.value = true
  loadingDetail.value = true
  try {
    const r = await authFetch(`/api/mentors/${m.user_id}`)
    const j = await r.safeJson()
    if (j?.status === 'success') detailMentor.value = j.data
  } catch (e) {} finally { loadingDetail.value = false }
}
function requestFromDetail() {
  const m = detailMentor.value
  showDetail.value = false
  openRequest(m)
}

// ── Demande de session ───────────────────────────────────────────────────────
const showRequest = ref(false)
const requestMentor = ref(null)
const requestForm = ref({ service_type: 'cv_review', message: '', preferred_slot: '' })
const sending = ref(false)

function openRequest(m) {
  requestMentor.value = m
  requestForm.value = { service_type: 'cv_review', message: '', preferred_slot: '' }
  showRequest.value = true
}
async function submitRequest() {
  if (sending.value) return
  sending.value = true
  try {
    const r = await authFetch(`/api/mentors/${requestMentor.value.user_id}/request`, {
      method: 'POST', body: JSON.stringify(requestForm.value)
    })
    const j = await r.safeJson()
    if (r.ok && j?.status === 'success') {
      toastState.addToast(t('mentorhub.request_sent'), 'success')
      showRequest.value = false
      sentRequests.value.unshift(j.data)
    } else toastState.addToast(j?.detail || t('common.error'), 'error')
  } catch (e) { toastState.addToast(t('common.error'), 'error') } finally { sending.value = false }
}

// ── Mes demandes (envoyées) ──────────────────────────────────────────────────
const sentRequests = ref([])
const loadingSent = ref(false)
async function loadSent() {
  loadingSent.value = true
  try {
    const r = await authFetch('/api/mentors/requests/sent')
    const j = await r.safeJson()
    if (j?.status === 'success') sentRequests.value = j.data
  } catch (e) {} finally { loadingSent.value = false }
}
async function cancelRequest(req) {
  if (!confirm(t('mentorhub.cancel_confirm'))) return
  try {
    const r = await authFetch(`/api/mentors/requests/${req.id}/cancel`, { method: 'POST' })
    const j = await r.safeJson()
    if (r.ok && j?.status === 'success') Object.assign(req, j.data)
    else toastState.addToast(j?.detail || t('common.error'), 'error')
  } catch (e) { toastState.addToast(t('common.error'), 'error') }
}

// ── Avis ─────────────────────────────────────────────────────────────────────
const showReview = ref(false)
const reviewReq = ref(null)
const reviewForm = ref({ rating: 5, comment: '' })
function openReview(req) { reviewReq.value = req; reviewForm.value = { rating: 5, comment: '' }; showReview.value = true }
async function submitReview() {
  try {
    const r = await authFetch(`/api/mentors/requests/${reviewReq.value.id}/review`, {
      method: 'POST', body: JSON.stringify(reviewForm.value)
    })
    const j = await r.safeJson()
    if (r.ok && j?.status === 'success') {
      toastState.addToast(t('mentorhub.review_thanks'), 'success')
      reviewReq.value.reviewed = true
      showReview.value = false
    } else toastState.addToast(j?.detail || t('common.error'), 'error')
  } catch (e) { toastState.addToast(t('common.error'), 'error') }
}

// ── Espace mentor ────────────────────────────────────────────────────────────
const DAYS = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
function dayLabel(d) { return t('mentorhub.day_' + d) }
const myProfile = ref(null)
function emptyProfileForm() {
  return {
    headline: '', role: '', company: '', experience_years: '', location: '', timezone: '',
    bio: '', specialtiesText: '', languagesText: '',
    availability: 'available', availability_days: [], availability_note: '',
    links: { linkedin: '', website: '', portfolio: '', calendar: '' },
    avatar_url: '', is_active: true,
  }
}
const profileForm = ref(emptyProfileForm())
const savingProfile = ref(false)
const receivedRequests = ref([])
const photoInput = ref(null)
const uploadingPhoto = ref(false)

function toggleDay(d) {
  const a = profileForm.value.availability_days
  const i = a.indexOf(d)
  if (i >= 0) a.splice(i, 1); else a.push(d)
}

async function loadProfile() {
  try {
    const r = await authFetch('/api/mentors/me')
    const j = await r.safeJson()
    if (j?.status === 'success' && j.data) {
      myProfile.value = j.data
      profileForm.value = {
        headline: j.data.headline || '', role: j.data.role || '', company: j.data.company || '',
        experience_years: j.data.experience_years || '', location: j.data.location || '', timezone: j.data.timezone || '',
        bio: j.data.bio || '',
        specialtiesText: (j.data.specialties || []).join(', '),
        languagesText: (j.data.languages || []).join(', '),
        availability: j.data.availability || 'available',
        availability_days: [...(j.data.availability_days || [])],
        availability_note: j.data.availability_note || '',
        links: { linkedin: '', website: '', portfolio: '', calendar: '', ...(j.data.links || {}) },
        avatar_url: j.data.avatar_url || '', is_active: j.data.is_active !== false,
      }
    }
  } catch (e) {}
}
async function saveProfile() {
  savingProfile.value = true
  try {
    const f = profileForm.value
    const body = {
      headline: f.headline, role: f.role, company: f.company,
      experience_years: parseInt(f.experience_years) || 0,
      location: f.location, timezone: f.timezone, bio: f.bio,
      specialties: f.specialtiesText.split(',').map(s => s.trim()).filter(Boolean),
      languages: f.languagesText.split(',').map(s => s.trim()).filter(Boolean),
      availability: f.availability,
      availability_days: f.availability_days,
      availability_note: f.availability_note,
      links: f.links,
      avatar_url: f.avatar_url,
      is_active: f.is_active,
    }
    const r = await authFetch('/api/mentors/me', { method: 'PUT', body: JSON.stringify(body) })
    const j = await r.safeJson()
    if (r.ok && j?.status === 'success') { myProfile.value = j.data; toastState.addToast(t('mentorhub.profile_saved'), 'success'); loadMentors() }
    else toastState.addToast(j?.detail || t('common.error'), 'error')
  } catch (e) { toastState.addToast(t('common.error'), 'error') } finally { savingProfile.value = false }
}
async function uploadPhoto(e) {
  const file = e.target.files?.[0]
  if (!file) return
  uploadingPhoto.value = true
  try {
    const fd = new FormData()
    fd.append('file', file)
    const r = await authFetch('/api/mentors/me/photo', { method: 'POST', body: fd })
    const j = await r.safeJson()
    if (r.ok && j?.status === 'success') {
      profileForm.value.avatar_url = j.data.avatar_url
      if (myProfile.value) myProfile.value.avatar_url = j.data.avatar_url
      toastState.addToast(t('mentorhub.photo_updated'), 'success')
    } else toastState.addToast(j?.detail || t('common.error'), 'error')
  } catch (e) { toastState.addToast(t('common.error'), 'error') } finally { uploadingPhoto.value = false; if (photoInput.value) photoInput.value.value = '' }
}
async function loadReceived() {
  try {
    const r = await authFetch('/api/mentors/requests/received')
    const j = await r.safeJson()
    if (j?.status === 'success') receivedRequests.value = j.data
  } catch (e) {}
}
async function respond(req, action) {
  try {
    const r = await authFetch(`/api/mentors/requests/${req.id}/respond`, {
      method: 'POST', body: JSON.stringify({ action })
    })
    const j = await r.safeJson()
    if (r.ok && j?.status === 'success') Object.assign(req, j.data)
    else toastState.addToast(j?.detail || t('common.error'), 'error')
  } catch (e) { toastState.addToast(t('common.error'), 'error') }
}

// ── Événements ───────────────────────────────────────────────────────────────
const events = ref([])
const showEventForm = ref(false)
const savingEvent = ref(false)
const eventForm = ref({ title: '', description: '', date: '', location: '', link: '' })
async function loadEvents() {
  try {
    const r = await authFetch('/api/mentors/events/list')
    const j = await r.safeJson()
    if (j?.status === 'success') events.value = j.data
  } catch (e) {}
}
async function createEvent() {
  if (!eventForm.value.title.trim() || !eventForm.value.date) return
  savingEvent.value = true
  try {
    const r = await authFetch('/api/mentors/events', { method: 'POST', body: JSON.stringify(eventForm.value) })
    const j = await r.safeJson()
    if (r.ok && j?.status === 'success') {
      events.value.push(j.data); events.value.sort((a, b) => new Date(a.date) - new Date(b.date))
      eventForm.value = { title: '', description: '', date: '', location: '', link: '' }
      showEventForm.value = false
    } else toastState.addToast(j?.detail || t('common.error'), 'error')
  } catch (e) { toastState.addToast(t('common.error'), 'error') } finally { savingEvent.value = false }
}
async function rsvp(ev) {
  try {
    const r = await authFetch(`/api/mentors/events/${ev.id}/rsvp`, { method: 'POST' })
    const j = await r.safeJson()
    if (r.ok && j?.status === 'success') { ev.is_attending = j.is_attending; ev.attendees_count = j.attendees_count }
  } catch (e) {}
}
async function deleteEvent(ev) {
  if (!confirm(t('mentorhub.event_remove_confirm'))) return
  try { const r = await authFetch(`/api/mentors/events/${ev.id}`, { method: 'DELETE' }); if (r.ok) events.value = events.value.filter(x => x.id !== ev.id) } catch (e) {}
}

// ── Helpers ──────────────────────────────────────────────────────────────────
function initials(n) { return (n || '?').trim()[0]?.toUpperCase() || '?' }
function availLabel(a) { return t('mentorhub.avail_' + (a || 'available')) }
function hasLinks(m) { return m.links && Object.keys(m.links).length > 0 }
const LINK_PROPER = { linkedin: 'LinkedIn', portfolio: 'Portfolio', twitter: 'X', github: 'GitHub' }
function linkName(key) { return LINK_PROPER[key] || t('mentorhub.link_name_' + key) }
function roleLine(m) { return [m.role, m.company].filter(Boolean).join(' · ') }
function statusLabel(s) { return t('mentorhub.status_' + s) }
function fmtDate(d) { try { return new Date(d).toLocaleString([], { dateStyle: 'medium', timeStyle: 'short' }) } catch { return '' } }
const MONTHS = ['JAN', 'FÉV', 'MAR', 'AVR', 'MAI', 'JUIN', 'JUIL', 'AOÛ', 'SEP', 'OCT', 'NOV', 'DÉC']
function evDay(d) { try { return new Date(d).getDate() } catch { return '--' } }
function evMonth(d) { try { return MONTHS[new Date(d).getMonth()] } catch { return '' } }
function isPast(d) { try { return new Date(d) < new Date() } catch { return false } }

function switchTab(k) {
  tab.value = k
  if (k === 'requests') loadSent()
  else if (k === 'events') loadEvents()
  else if (k === 'mentor') { loadProfile(); loadReceived() }
}

onMounted(() => { loadMentors() })
</script>

<template>
  <div class="mh">
    <!-- Header -->
    <header class="mh__head">
      <div>
        <h1 class="mh__title">{{ t('mentorhub.title') }}</h1>
        <p class="mh__sub">{{ t('mentorhub.subtitle') }}</p>
      </div>
    </header>

    <!-- Tabs -->
    <div class="mh__tabs">
      <button v-for="tb in tabs" :key="tb.key" :class="['mh__tab', { 'mh__tab--active': tab === tb.key }]" @click="switchTab(tb.key)">
        <component :is="tb.icon" class="w-4 h-4" /> {{ tb.label }}
      </button>
    </div>

    <!-- ═══ DÉCOUVRIR ═══ -->
    <section v-show="tab === 'discover'">
      <div class="mh__toolbar">
        <div class="mh__search">
          <MagnifyingGlassIcon class="w-4 h-4 mh__search-ic" />
          <input v-model="q" :placeholder="t('mentorhub.search_ph')" class="mh__search-input" />
        </div>
        <div class="mh__chips">
          <button :class="['mh__chip', { 'mh__chip--on': !specialtyFilter }]" @click="specialtyFilter = ''">{{ t('mentorhub.filter_all') }}</button>
          <button v-for="s in allSpecialties" :key="s" :class="['mh__chip', { 'mh__chip--on': specialtyFilter === s }]" @click="specialtyFilter = s">{{ s }}</button>
        </div>
      </div>

      <div v-if="loadingMentors" class="mh__loading">{{ t('common.loading') }}…</div>
      <div v-else-if="!filteredMentors.length" class="mh__empty">
        <AcademicCapIcon class="mh__empty-ic" />
        <p>{{ t('mentorhub.no_mentors') }}</p>
        <button class="mh__empty-cta" @click="switchTab('mentor')">{{ t('mentorhub.become_cta') }}</button>
      </div>

      <div v-else class="mh__grid">
        <article v-for="m in filteredMentors" :key="m.user_id" class="mh__card mh__card--clickable" @click="openDetail(m)">
          <div class="mh__card-top">
            <div class="mh__avatar">
              <img v-if="m.avatar_url" :src="m.avatar_url" alt="" />
              <span v-else>{{ initials(m.full_name) }}</span>
              <span :class="['mh__dot', 'mh__dot--' + (m.availability || 'available')]"></span>
            </div>
            <div class="mh__card-id">
              <h3 class="mh__card-name">{{ m.full_name }}</h3>
              <p class="mh__card-headline">{{ m.headline || t('mentorhub.no_headline') }}</p>
            </div>
          </div>

          <div v-if="roleLine(m) || m.location || m.experience_years" class="mh__card-sub">
            <span v-if="roleLine(m)" class="mh__card-role"><BriefcaseIcon class="w-3 h-3" /> {{ roleLine(m) }}</span>
            <span v-if="m.location" class="mh__card-loc"><MapPinIcon class="w-3 h-3" /> {{ m.location }}</span>
            <span v-if="m.experience_years" class="mh__card-exp">{{ m.experience_years }} {{ t('mentorhub.years_exp') }}</span>
          </div>

          <div class="mh__tags">
            <span v-for="s in (m.specialties || []).slice(0, 4)" :key="s" class="mh__tag">{{ s }}</span>
          </div>

          <div class="mh__card-meta">
            <span class="mh__rating"><StarIcon class="w-3.5 h-3.5" /> {{ m.rating_avg || '—' }}<i v-if="m.rating_count">({{ m.rating_count }})</i></span>
            <span class="mh__sessions">{{ m.sessions_count || 0 }} {{ t('mentorhub.sessions') }}</span>
            <span :class="['mh__avail', 'mh__avail--' + (m.availability || 'available')]">{{ availLabel(m.availability) }}</span>
          </div>

          <div v-if="(m.availability_days || []).length || m.availability_note" class="mh__card-when">
            <ClockIcon class="w-3.5 h-3.5" />
            <span v-if="(m.availability_days || []).length" class="mh__when-days">{{ (m.availability_days || []).map(dayLabel).join(' · ') }}</span>
            <span v-if="m.availability_note" class="mh__when-note">{{ m.availability_note }}</span>
          </div>

          <div v-if="hasLinks(m)" class="mh__card-links">
            <a v-for="(url, key) in m.links" :key="key" :href="url" target="_blank" class="mh__link-chip"><LinkIcon class="w-3 h-3" /> {{ linkName(key) }}</a>
          </div>

          <button class="mh__request-btn" @click.stop="openRequest(m)" :disabled="m.availability === 'offline'">
            <PaperAirplaneIcon class="w-4 h-4" /> {{ t('mentorhub.request_btn') }}
          </button>
        </article>
      </div>
    </section>

    <!-- ═══ MES DEMANDES ═══ -->
    <section v-show="tab === 'requests'">
      <div v-if="loadingSent" class="mh__loading">{{ t('common.loading') }}…</div>
      <div v-else-if="!sentRequests.length" class="mh__empty">
        <ChatBubbleLeftRightIcon class="mh__empty-ic" />
        <p>{{ t('mentorhub.empty_sent') }}</p>
        <button class="mh__empty-cta" @click="switchTab('discover')">{{ t('mentorhub.find_mentor') }}</button>
      </div>
      <div v-else class="mh__reqs">
        <div v-for="req in sentRequests" :key="req.id" class="mh__req">
          <div class="mh__req-avatar">{{ initials(req.mentor_name) }}</div>
          <div class="mh__req-body">
            <div class="mh__req-head">
              <span class="mh__req-name">{{ req.mentor_name }}</span>
              <span :class="['mh__status', 'mh__status--' + req.status]">{{ statusLabel(req.status) }}</span>
            </div>
            <div class="mh__req-svc">{{ svcLabel(req.service_type) }}</div>
            <p v-if="req.message" class="mh__req-msg">{{ req.message }}</p>
            <p v-if="req.preferred_slot" class="mh__req-slot"><ClockIcon class="w-3.5 h-3.5" /> {{ req.preferred_slot }}</p>
            <p v-if="req.response_message" class="mh__req-resp">💬 {{ req.response_message }}</p>
            <div class="mh__req-foot">
              <span class="mh__req-date">{{ fmtDate(req.created_at) }}</span>
              <button v-if="['pending', 'accepted'].includes(req.status)" class="mh__mini mh__mini--ghost" @click="cancelRequest(req)">{{ t('mentorhub.cancel_btn') }}</button>
              <button v-if="req.status === 'completed' && !req.reviewed" class="mh__mini mh__mini--gold" @click="openReview(req)"><StarIcon class="w-3.5 h-3.5" /> {{ t('mentorhub.review_btn') }}</button>
              <span v-else-if="req.status === 'completed' && req.reviewed" class="mh__reviewed"><CheckCircleIcon class="w-3.5 h-3.5" /> {{ t('mentorhub.reviewed') }}</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ═══ ÉVÉNEMENTS ═══ -->
    <section v-show="tab === 'events'">
      <div class="mh__section-head">
        <h2 class="mh__section-title"><CalendarDaysIcon class="w-5 h-5" /> {{ t('mentorhub.events_title') }}</h2>
        <button v-if="myProfile" class="mh__cta" @click="showEventForm = !showEventForm"><PlusIcon class="w-4 h-4" /> {{ t('mentorhub.add_event') }}</button>
      </div>

      <transition name="mh-fade">
        <div v-if="showEventForm" class="mh__form">
          <div class="mh__form-head">{{ t('mentorhub.ev_new') }}<button class="mh__form-close" @click="showEventForm = false"><XMarkIcon class="w-4 h-4" /></button></div>
          <input v-model="eventForm.title" :placeholder="t('mentorhub.ev_name')" class="mh__input" />
          <textarea v-model="eventForm.description" :placeholder="t('mentorhub.ev_desc')" class="mh__input mh__textarea"></textarea>
          <div class="mh__form-row">
            <input v-model="eventForm.date" type="datetime-local" class="mh__input" />
            <input v-model="eventForm.location" :placeholder="t('mentorhub.ev_location')" class="mh__input" />
          </div>
          <input v-model="eventForm.link" :placeholder="t('mentorhub.ev_link')" class="mh__input" />
          <button class="mh__save" @click="createEvent" :disabled="savingEvent">{{ savingEvent ? t('common.saving') : t('mentorhub.ev_create') }}</button>
        </div>
      </transition>

      <div v-if="!events.length && !showEventForm" class="mh__empty">
        <CalendarDaysIcon class="mh__empty-ic" />
        <p>{{ t('mentorhub.empty_events') }}</p>
      </div>

      <div class="mh__events">
        <div v-for="ev in events" :key="ev.id" :class="['mh__event', { 'mh__event--past': isPast(ev.date) }]">
          <div class="mh__cal"><span class="mh__cal-day">{{ evDay(ev.date) }}</span><span class="mh__cal-month">{{ evMonth(ev.date) }}</span></div>
          <div class="mh__event-body">
            <div class="mh__event-title">{{ ev.title }}</div>
            <p v-if="ev.description" class="mh__event-desc">{{ ev.description }}</p>
            <div class="mh__event-meta">
              <span><ClockIcon class="w-3.5 h-3.5" /> {{ fmtDate(ev.date) }}</span>
              <span v-if="ev.location"><MapPinIcon class="w-3.5 h-3.5" /> {{ ev.location }}</span>
              <span><AcademicCapIcon class="w-3.5 h-3.5" /> {{ ev.host_name }}</span>
              <a v-if="ev.link" :href="ev.link" target="_blank" class="mh__event-link"><VideoCameraIcon class="w-3.5 h-3.5" /> {{ t('mentorhub.ev_link_label') }}</a>
            </div>
            <div class="mh__event-foot">
              <button :class="['mh__rsvp', { 'mh__rsvp--on': ev.is_attending }]" @click="rsvp(ev)">{{ ev.is_attending ? t('mentorhub.attending') : t('mentorhub.rsvp') }}</button>
              <span class="mh__attendees"><UsersIcon class="w-3.5 h-3.5" /> {{ ev.attendees_count || 0 }}</span>
              <button v-if="ev.is_host" class="mh__event-del" @click="deleteEvent(ev)"><TrashIcon class="w-4 h-4" /></button>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ═══ ESPACE MENTOR ═══ -->
    <section v-show="tab === 'mentor'" class="mh__mentor">
      <!-- Profil mentor -->
      <div class="mh__card-block">
        <h2 class="mh__section-title"><AcademicCapIcon class="w-5 h-5" /> {{ myProfile ? t('mentorhub.your_profile') : t('mentorhub.become_title') }}</h2>
        <p class="mh__block-sub">{{ t('mentorhub.become_sub') }}</p>

        <!-- Photo -->
        <div class="mh__photo-row">
          <div class="mh__photo">
            <img v-if="profileForm.avatar_url" :src="profileForm.avatar_url" alt="" />
            <AcademicCapIcon v-else class="w-7 h-7" />
          </div>
          <div class="mh__photo-actions">
            <input ref="photoInput" type="file" accept="image/png,image/jpeg,image/webp" class="mh__file-hidden" @change="uploadPhoto" />
            <button class="mh__btn-ghost" :disabled="uploadingPhoto" @click="photoInput?.click()">
              {{ uploadingPhoto ? t('mentorhub.photo_uploading') : t('mentorhub.photo_upload') }}
            </button>
            <p class="mh__hint">{{ t('mentorhub.photo_hint') }}</p>
          </div>
        </div>

        <label class="mh__label mt">{{ t('mentorhub.headline_label') }}</label>
        <input v-model="profileForm.headline" :placeholder="t('mentorhub.headline_ph')" class="mh__input mh__input--full" />

        <div class="mh__form-row">
          <div>
            <label class="mh__label mt">{{ t('mentorhub.role_label') }}</label>
            <input v-model="profileForm.role" :placeholder="t('mentorhub.role_ph')" class="mh__input mh__input--full" />
          </div>
          <div>
            <label class="mh__label mt">{{ t('mentorhub.company_label') }}</label>
            <input v-model="profileForm.company" :placeholder="t('mentorhub.company_ph')" class="mh__input mh__input--full" />
          </div>
        </div>

        <div class="mh__form-row">
          <div>
            <label class="mh__label mt">{{ t('mentorhub.experience_label') }}</label>
            <input v-model="profileForm.experience_years" type="number" min="0" :placeholder="t('mentorhub.experience_ph')" class="mh__input mh__input--full" />
          </div>
          <div>
            <label class="mh__label mt">{{ t('mentorhub.location_label') }}</label>
            <input v-model="profileForm.location" :placeholder="t('mentorhub.location_ph')" class="mh__input mh__input--full" />
          </div>
        </div>

        <label class="mh__label mt">{{ t('mentorhub.bio_label') }}</label>
        <textarea v-model="profileForm.bio" :placeholder="t('mentorhub.bio_ph')" class="mh__input mh__input--full mh__textarea"></textarea>

        <div class="mh__form-row">
          <div>
            <label class="mh__label">{{ t('mentorhub.specialties_label') }}</label>
            <input v-model="profileForm.specialtiesText" :placeholder="t('mentorhub.specialties_ph')" class="mh__input mh__input--full" />
          </div>
          <div>
            <label class="mh__label">{{ t('mentorhub.languages_label') }}</label>
            <input v-model="profileForm.languagesText" :placeholder="t('mentorhub.languages_ph')" class="mh__input mh__input--full" />
          </div>
        </div>

        <label class="mh__label mt">{{ t('mentorhub.availability_label') }}</label>
        <div class="mh__avail-pick">
          <button v-for="a in ['available', 'busy', 'offline']" :key="a" :class="['mh__avail-opt', 'mh__avail-opt--' + a, { 'mh__avail-opt--on': profileForm.availability === a }]" @click="profileForm.availability = a">
            <span :class="['mh__dot', 'mh__dot--' + a]"></span> {{ availLabel(a) }}
          </button>
        </div>

        <label class="mh__label mt">{{ t('mentorhub.availability_days_label') }}</label>
        <div class="mh__days">
          <button v-for="d in DAYS" :key="d" type="button" :class="['mh__day', { 'mh__day--on': profileForm.availability_days.includes(d) }]" @click="toggleDay(d)">{{ dayLabel(d) }}</button>
        </div>

        <div class="mh__form-row">
          <div>
            <label class="mh__label mt">{{ t('mentorhub.availability_note_label') }}</label>
            <input v-model="profileForm.availability_note" :placeholder="t('mentorhub.availability_note_ph')" class="mh__input mh__input--full" />
          </div>
          <div>
            <label class="mh__label mt">{{ t('mentorhub.timezone_label') }}</label>
            <input v-model="profileForm.timezone" :placeholder="t('mentorhub.timezone_ph')" class="mh__input mh__input--full" />
          </div>
        </div>

        <label class="mh__label mt">{{ t('mentorhub.links_label') }}</label>
        <div class="mh__links-form">
          <input v-model="profileForm.links.linkedin" :placeholder="t('mentorhub.link_linkedin')" class="mh__input mh__input--full" />
          <input v-model="profileForm.links.website" :placeholder="t('mentorhub.link_website')" class="mh__input mh__input--full" />
          <input v-model="profileForm.links.portfolio" :placeholder="t('mentorhub.link_portfolio')" class="mh__input mh__input--full" />
          <input v-model="profileForm.links.calendar" :placeholder="t('mentorhub.link_calendar')" class="mh__input mh__input--full" />
        </div>

        <label class="mh__switch">
          <input type="checkbox" v-model="profileForm.is_active" />
          <span>{{ t('mentorhub.active_label') }}</span>
        </label>
        <p class="mh__hint">{{ t('mentorhub.active_hint') }}</p>

        <button class="mh__save mh__save--block" @click="saveProfile" :disabled="savingProfile">
          {{ savingProfile ? t('common.saving') : (myProfile ? t('mentorhub.save_profile') : t('mentorhub.publish_profile')) }}
        </button>
      </div>

      <!-- Demandes reçues -->
      <div class="mh__card-block">
        <h2 class="mh__section-title"><ChatBubbleLeftRightIcon class="w-5 h-5" /> {{ t('mentorhub.received_title') }}</h2>
        <div v-if="!receivedRequests.length" class="mh__empty mh__empty--sm">
          <p>{{ t('mentorhub.empty_received') }}</p>
        </div>
        <div v-else class="mh__reqs">
          <div v-for="req in receivedRequests" :key="req.id" class="mh__req">
            <div class="mh__req-avatar">
              <img v-if="req.requester_avatar" :src="req.requester_avatar" alt="" />
              <template v-else>{{ initials(req.requester_name) }}</template>
            </div>
            <div class="mh__req-body">
              <div class="mh__req-head">
                <span class="mh__req-name">{{ req.requester_name }}</span>
                <span :class="['mh__status', 'mh__status--' + req.status]">{{ statusLabel(req.status) }}</span>
              </div>
              <div class="mh__req-svc">{{ svcLabel(req.service_type) }}</div>
              <p v-if="req.message" class="mh__req-msg">{{ req.message }}</p>
              <p v-if="req.preferred_slot" class="mh__req-slot"><ClockIcon class="w-3.5 h-3.5" /> {{ req.preferred_slot }}</p>
              <div class="mh__req-foot">
                <span class="mh__req-date">{{ fmtDate(req.created_at) }}</span>
                <template v-if="req.status === 'pending'">
                  <button class="mh__mini mh__mini--gold" @click="respond(req, 'accept')">{{ t('mentorhub.accept') }}</button>
                  <button class="mh__mini mh__mini--ghost" @click="respond(req, 'decline')">{{ t('mentorhub.decline') }}</button>
                </template>
                <button v-else-if="req.status === 'accepted'" class="mh__mini mh__mini--gold" @click="respond(req, 'complete')">{{ t('mentorhub.mark_complete') }}</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ═══ MODALE : fiche mentor ═══ -->
    <div v-if="showDetail" class="mh__modal" @click.self="showDetail = false">
      <div class="mh__dialog mh__dialog--wide">
        <button class="mh__form-close mh__dialog-x" @click="showDetail = false"><XMarkIcon class="w-5 h-5" /></button>
        <div class="mh__detail-head">
          <div class="mh__detail-avatar">
            <img v-if="detailMentor?.avatar_url" :src="detailMentor.avatar_url" alt="" />
            <span v-else>{{ initials(detailMentor?.full_name) }}</span>
            <span :class="['mh__dot', 'mh__dot--' + (detailMentor?.availability || 'available')]"></span>
          </div>
          <div class="mh__detail-id">
            <h2 class="mh__detail-name">{{ detailMentor?.full_name }}</h2>
            <p class="mh__detail-headline">{{ detailMentor?.headline || t('mentorhub.no_headline') }}</p>
            <div class="mh__detail-facts">
              <span v-if="roleLine(detailMentor || {})"><BriefcaseIcon class="w-3.5 h-3.5" /> {{ roleLine(detailMentor) }}</span>
              <span v-if="detailMentor?.location"><MapPinIcon class="w-3.5 h-3.5" /> {{ detailMentor.location }}</span>
              <span v-if="detailMentor?.experience_years">{{ detailMentor.experience_years }} {{ t('mentorhub.years_exp') }}</span>
              <span class="mh__rating"><StarIcon class="w-3.5 h-3.5" /> {{ detailMentor?.rating_avg || '—' }}<i v-if="detailMentor?.rating_count">({{ detailMentor.rating_count }})</i></span>
            </div>
          </div>
        </div>

        <div class="mh__detail-meta">
          <span :class="['mh__avail', 'mh__avail--' + (detailMentor?.availability || 'available')]">{{ availLabel(detailMentor?.availability) }}</span>
          <span class="mh__sessions">{{ detailMentor?.sessions_count || 0 }} {{ t('mentorhub.sessions') }}</span>
        </div>

        <div v-if="(detailMentor?.availability_days || []).length || detailMentor?.availability_note" class="mh__detail-when">
          <ClockIcon class="w-4 h-4" />
          <span v-if="(detailMentor?.availability_days || []).length" class="mh__when-days">{{ (detailMentor.availability_days || []).map(dayLabel).join(' · ') }}</span>
          <span v-if="detailMentor?.availability_note" class="mh__when-note">{{ detailMentor.availability_note }}</span>
          <span v-if="detailMentor?.timezone" class="mh__when-note">· {{ detailMentor.timezone }}</span>
        </div>

        <div v-if="(detailMentor?.specialties || []).length" class="mh__tags mh__tags--detail">
          <span v-for="s in detailMentor.specialties" :key="s" class="mh__tag">{{ s }}</span>
        </div>

        <p v-if="(detailMentor?.languages || []).length" class="mh__detail-langs">🗣 {{ detailMentor.languages.join(', ') }}</p>

        <p v-if="detailMentor?.bio" class="mh__detail-bio">{{ detailMentor.bio }}</p>

        <div v-if="hasLinks(detailMentor || {})" class="mh__card-links mh__card-links--detail">
          <a v-for="(url, key) in detailMentor.links" :key="key" :href="url" target="_blank" class="mh__link-chip"><LinkIcon class="w-3 h-3" /> {{ linkName(key) }}</a>
        </div>

        <!-- Avis -->
        <div class="mh__reviews">
          <div class="mh__reviews-head"><StarIcon class="w-4 h-4" /> {{ t('mentorhub.reviews_title') }} <span v-if="detailMentor?.rating_count">({{ detailMentor.rating_count }})</span></div>
          <div v-if="loadingDetail" class="mh__loading">{{ t('common.loading') }}…</div>
          <div v-else-if="!(detailMentor?.reviews || []).length" class="mh__reviews-empty">{{ t('mentorhub.no_reviews') }}</div>
          <div v-else class="mh__review-list">
            <div v-for="rv in detailMentor.reviews" :key="rv.id" class="mh__review">
              <div class="mh__review-top">
                <span class="mh__review-author">{{ rv.reviewer_name }}</span>
                <span class="mh__review-stars"><StarIcon v-for="n in rv.rating" :key="n" class="w-3 h-3" /></span>
              </div>
              <p v-if="rv.comment" class="mh__review-comment">{{ rv.comment }}</p>
            </div>
          </div>
        </div>

        <button class="mh__save mh__save--block mt" @click="requestFromDetail" :disabled="detailMentor?.availability === 'offline'">
          <PaperAirplaneIcon class="w-4 h-4" /> {{ t('mentorhub.request_btn') }}
        </button>
      </div>
    </div>

    <!-- ═══ MODALE : demande de session ═══ -->
    <div v-if="showRequest" class="mh__modal" @click.self="showRequest = false">
      <div class="mh__dialog">
        <div class="mh__dialog-head">
          <div class="mh__dialog-title">{{ t('mentorhub.request_title', { name: requestMentor?.full_name }) }}</div>
          <button class="mh__form-close" @click="showRequest = false"><XMarkIcon class="w-5 h-5" /></button>
        </div>
        <label class="mh__label">{{ t('mentorhub.service_label') }}</label>
        <select v-model="requestForm.service_type" class="mh__input mh__input--full">
          <option v-for="s in SERVICE_TYPES" :key="s" :value="s">{{ svcLabel(s) }}</option>
        </select>
        <label class="mh__label mt">{{ t('mentorhub.message_label') }}</label>
        <textarea v-model="requestForm.message" :placeholder="t('mentorhub.message_ph')" class="mh__input mh__input--full mh__textarea"></textarea>
        <label class="mh__label mt">{{ t('mentorhub.slot_label') }}</label>
        <input v-model="requestForm.preferred_slot" :placeholder="t('mentorhub.slot_ph')" class="mh__input mh__input--full" />
        <button class="mh__save mh__save--block mt" @click="submitRequest" :disabled="sending">
          <PaperAirplaneIcon class="w-4 h-4" /> {{ sending ? t('mentorhub.sending') : t('mentorhub.send_request') }}
        </button>
      </div>
    </div>

    <!-- ═══ MODALE : avis ═══ -->
    <div v-if="showReview" class="mh__modal" @click.self="showReview = false">
      <div class="mh__dialog">
        <div class="mh__dialog-head">
          <div class="mh__dialog-title">{{ t('mentorhub.review_title', { name: reviewReq?.mentor_name }) }}</div>
          <button class="mh__form-close" @click="showReview = false"><XMarkIcon class="w-5 h-5" /></button>
        </div>
        <label class="mh__label">{{ t('mentorhub.rating_label') }}</label>
        <div class="mh__stars">
          <button v-for="n in 5" :key="n" @click="reviewForm.rating = n" class="mh__star">
            <StarIcon :class="['w-7 h-7', n <= reviewForm.rating ? 'mh__star--on' : 'mh__star--off']" />
          </button>
        </div>
        <label class="mh__label mt">{{ t('mentorhub.comment_label') }}</label>
        <textarea v-model="reviewForm.comment" :placeholder="t('mentorhub.comment_ph')" class="mh__input mh__input--full mh__textarea"></textarea>
        <button class="mh__save mh__save--block mt" @click="submitReview">{{ t('mentorhub.submit_review') }}</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.mh { max-width: 1240px; margin: 0 auto; color: #101828; }
.mh__head { margin-bottom: 1.1rem; }
.mh__title { font-size: 1.9rem; font-weight: 800; margin: 0; letter-spacing: -0.03em; }
.mh__sub { color: #667085; font-size: 0.92rem; margin: 0.3rem 0 0; }

.mh__tabs { display: flex; gap: 0.4rem; margin-bottom: 1.3rem; border-bottom: 1px solid #EEF0F3; overflow-x: auto; }
.mh__tab { display: inline-flex; align-items: center; gap: 0.4rem; padding: 0.7rem 1rem; border: none; background: none; color: #667085; font-size: 0.86rem; font-weight: 700; cursor: pointer; border-bottom: 2px solid transparent; white-space: nowrap; }
.mh__tab:hover { color: #101828; }
.mh__tab--active { color: #B45309; border-bottom-color: #F59E0B; }

.mh__toolbar { display: flex; flex-direction: column; gap: 0.8rem; margin-bottom: 1.2rem; }
.mh__search { position: relative; max-width: 420px; }
.mh__search-ic { position: absolute; left: 0.9rem; top: 50%; transform: translateY(-50%); color: #98A2B3; }
.mh__search-input { width: 100%; padding: 0.7rem 0.9rem 0.7rem 2.4rem; border-radius: 0.8rem; background: #fff; border: 1px solid #EEF0F3; font-size: 0.88rem; outline: none; }
.mh__search-input:focus { border-color: #F59E0B; box-shadow: 0 0 0 3px rgba(245,158,11,0.12); }
.mh__chips { display: flex; flex-wrap: wrap; gap: 0.4rem; }
.mh__chip { padding: 0.35rem 0.8rem; border-radius: 999px; border: 1px solid #EEF0F3; background: #fff; color: #475467; font-size: 0.78rem; font-weight: 600; cursor: pointer; }
.mh__chip--on { background: #FEF6E7; color: #B45309; border-color: #FDE68A; }

.mh__loading { padding: 3rem; text-align: center; color: #98A2B3; }
.mh__empty { text-align: center; padding: 3rem 1rem; color: #98A2B3; }
.mh__empty--sm { padding: 1.5rem; }
.mh__empty-ic { width: 2.8rem; height: 2.8rem; color: #D0D5DD; margin: 0 auto 0.7rem; }
.mh__empty-cta, .mh__cta { display: inline-flex; align-items: center; gap: 0.4rem; margin-top: 0.9rem; padding: 0.6rem 1.15rem; border-radius: 999px; background: linear-gradient(135deg, #FBBF24, #F59E0B); color: #fff; border: none; font-weight: 700; font-size: 0.82rem; cursor: pointer; box-shadow: 0 10px 22px -10px rgba(245,158,11,0.7); }

/* Grid mentors */
.mh__grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 1rem; }
.mh__card { background: #fff; border: 1px solid #EEF0F3; border-radius: 1.4rem; padding: 1.3rem; box-shadow: 0 1px 2px rgba(16,24,40,0.03); transition: box-shadow 0.15s, transform 0.15s; display: flex; flex-direction: column; }
.mh__card:hover { box-shadow: 0 16px 34px -22px rgba(16,24,40,0.4); transform: translateY(-3px); }
.mh__card-top { display: flex; align-items: center; gap: 0.8rem; }
.mh__avatar { position: relative; width: 3rem; height: 3rem; border-radius: 50%; background: linear-gradient(135deg, #FBBF24, #F59E0B); color: #fff; display: flex; align-items: center; justify-content: center; font-weight: 800; flex-shrink: 0; overflow: hidden; }
.mh__avatar img { width: 100%; height: 100%; object-fit: cover; }
.mh__dot { position: absolute; right: -1px; bottom: -1px; width: 0.7rem; height: 0.7rem; border-radius: 50%; border: 2px solid #fff; }
.mh__dot--available { background: #12B76A; }
.mh__dot--busy { background: #F59E0B; }
.mh__dot--offline { background: #98A2B3; }
.mh__card-id { min-width: 0; }
.mh__card-name { font-size: 0.98rem; font-weight: 800; margin: 0; color: #101828; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.mh__card-headline { font-size: 0.78rem; color: #667085; margin: 0.15rem 0 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.mh__tags { display: flex; flex-wrap: wrap; gap: 0.35rem; margin: 0.9rem 0; min-height: 1.6rem; }
.mh__tag { font-size: 0.68rem; font-weight: 700; padding: 0.2rem 0.55rem; border-radius: 999px; background: #EEF2FF; color: #4F46E5; }
.mh__card-meta { display: flex; align-items: center; gap: 0.7rem; font-size: 0.75rem; color: #667085; margin-bottom: 1rem; flex-wrap: wrap; }
.mh__rating { display: inline-flex; align-items: center; gap: 0.25rem; color: #D97706; font-weight: 800; }
.mh__rating i { font-style: normal; color: #98A2B3; font-weight: 600; }
.mh__sessions { font-weight: 600; }
.mh__avail { margin-left: auto; font-size: 0.66rem; font-weight: 800; text-transform: uppercase; padding: 0.15rem 0.5rem; border-radius: 999px; }
.mh__avail--available { background: #D1FAE5; color: #059669; }
.mh__avail--busy { background: #FEF3C7; color: #B45309; }
.mh__avail--offline { background: #F1F3F6; color: #98A2B3; }
.mh__request-btn { margin-top: auto; display: inline-flex; align-items: center; justify-content: center; gap: 0.45rem; padding: 0.7rem; border-radius: 0.9rem; background: linear-gradient(135deg, #FBBF24, #F59E0B); color: #fff; border: none; font-weight: 800; font-size: 0.82rem; cursor: pointer; box-shadow: 0 8px 18px -8px rgba(245,158,11,0.6); }
.mh__request-btn:disabled { opacity: 0.45; cursor: not-allowed; box-shadow: none; }

/* Requests */
.mh__reqs { display: flex; flex-direction: column; gap: 0.7rem; }
.mh__req { display: flex; gap: 0.8rem; background: #fff; border: 1px solid #EEF0F3; border-radius: 1.2rem; padding: 1rem 1.1rem; }
.mh__req-avatar { width: 2.6rem; height: 2.6rem; border-radius: 50%; background: linear-gradient(135deg, #6366F1, #8B5CF6); color: #fff; display: flex; align-items: center; justify-content: center; font-weight: 800; flex-shrink: 0; overflow: hidden; }
.mh__req-avatar img { width: 100%; height: 100%; object-fit: cover; }
.mh__req-body { flex: 1; min-width: 0; }
.mh__req-head { display: flex; align-items: center; gap: 0.6rem; }
.mh__req-name { font-weight: 800; font-size: 0.9rem; }
.mh__status { font-size: 0.62rem; font-weight: 800; text-transform: uppercase; padding: 0.15rem 0.5rem; border-radius: 999px; }
.mh__status--pending { background: #FEF3C7; color: #B45309; }
.mh__status--accepted { background: #DBEAFE; color: #2563EB; }
.mh__status--completed { background: #D1FAE5; color: #059669; }
.mh__status--declined, .mh__status--cancelled { background: #FEE2E2; color: #DC2626; }
.mh__req-svc { font-size: 0.78rem; font-weight: 700; color: #D97706; margin-top: 0.25rem; }
.mh__req-msg { font-size: 0.83rem; color: #475467; margin: 0.4rem 0 0; white-space: pre-wrap; }
.mh__req-slot { display: inline-flex; align-items: center; gap: 0.3rem; font-size: 0.75rem; color: #667085; margin: 0.35rem 0 0; }
.mh__req-resp { font-size: 0.8rem; color: #344054; background: #F9FAFB; border-radius: 0.6rem; padding: 0.5rem 0.7rem; margin: 0.5rem 0 0; }
.mh__req-foot { display: flex; align-items: center; gap: 0.6rem; margin-top: 0.6rem; flex-wrap: wrap; }
.mh__req-date { font-size: 0.7rem; color: #98A2B3; }
.mh__mini { padding: 0.35rem 0.85rem; border-radius: 999px; font-size: 0.72rem; font-weight: 700; cursor: pointer; border: 1px solid #EEF0F3; }
.mh__mini--gold { background: linear-gradient(135deg, #FBBF24, #F59E0B); color: #fff; border: none; display: inline-flex; align-items: center; gap: 0.3rem; }
.mh__mini--ghost { background: #fff; color: #667085; }
.mh__mini--ghost:hover { border-color: #FCA5A5; color: #DC2626; }
.mh__reviewed { display: inline-flex; align-items: center; gap: 0.3rem; font-size: 0.72rem; color: #059669; font-weight: 700; }

/* Section head / forms */
.mh__section-head { display: flex; align-items: center; justify-content: space-between; margin-bottom: 1rem; gap: 1rem; flex-wrap: wrap; }
.mh__section-title { display: flex; align-items: center; gap: 0.5rem; font-size: 1.05rem; font-weight: 800; margin: 0; color: #101828; }
.mh__form { display: flex; flex-direction: column; gap: 0.6rem; margin-bottom: 1.2rem; padding: 1.2rem; border-radius: 1.2rem; background: #fff; border: 1px solid #EEF0F3; }
.mh__form-head { display: flex; align-items: center; justify-content: space-between; font-weight: 800; font-size: 0.9rem; }
.mh__form-close { background: none; border: none; color: #98A2B3; cursor: pointer; }
.mh__form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 0.6rem; }
.mh__input { padding: 0.7rem 0.9rem; border-radius: 0.7rem; background: #F9FAFB; border: 1px solid #EEF0F3; color: #101828; font-size: 0.85rem; outline: none; font-family: inherit; }
.mh__input:focus { border-color: #F59E0B; box-shadow: 0 0 0 3px rgba(245,158,11,0.12); background: #fff; }
.mh__input--full { width: 100%; }
.mh__textarea { resize: vertical; min-height: 72px; }
.mh__label { display: block; font-size: 0.68rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.05em; color: #98A2B3; margin: 0 0 0.35rem; }
.mh__label.mt { margin-top: 0.9rem; }
.mh__save { padding: 0.75rem 1.3rem; border-radius: 0.9rem; background: linear-gradient(135deg, #FBBF24, #F59E0B); color: #fff; border: none; font-weight: 800; font-size: 0.85rem; cursor: pointer; display: inline-flex; align-items: center; justify-content: center; gap: 0.4rem; box-shadow: 0 10px 22px -12px rgba(245,158,11,0.7); }
.mh__save:disabled { opacity: 0.6; cursor: not-allowed; }
.mh__save--block { width: 100%; margin-top: 0.4rem; }

/* Events */
.mh__events { display: flex; flex-direction: column; gap: 0.75rem; }
.mh__event { display: flex; gap: 0.9rem; padding: 1rem; border-radius: 1.2rem; background: #fff; border: 1px solid #EEF0F3; transition: box-shadow 0.15s, transform 0.15s; }
.mh__event:hover { box-shadow: 0 12px 26px -18px rgba(16,24,40,0.3); transform: translateY(-2px); }
.mh__event--past { opacity: 0.6; }
.mh__cal { width: 3.3rem; flex-shrink: 0; border-radius: 0.9rem; background: linear-gradient(160deg, #FEF3C7, #FDE68A); display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 0.5rem 0; }
.mh__cal-day { font-size: 1.4rem; font-weight: 800; color: #B45309; line-height: 1; }
.mh__cal-month { font-size: 0.6rem; font-weight: 800; color: #D97706; letter-spacing: 0.05em; margin-top: 0.15rem; }
.mh__event-body { flex: 1; min-width: 0; }
.mh__event-title { font-weight: 700; font-size: 0.95rem; color: #101828; }
.mh__event-desc { font-size: 0.78rem; color: #667085; margin: 0.35rem 0 0.5rem; }
.mh__event-meta { display: flex; flex-wrap: wrap; gap: 0.9rem; font-size: 0.72rem; color: #667085; }
.mh__event-meta span, .mh__event-link { display: inline-flex; align-items: center; gap: 0.25rem; }
.mh__event-link { color: #D97706; text-decoration: none; font-weight: 600; }
.mh__event-foot { display: flex; align-items: center; gap: 0.6rem; margin-top: 0.7rem; padding-top: 0.6rem; border-top: 1px solid #F1F3F6; }
.mh__rsvp { padding: 0.35rem 0.95rem; border-radius: 999px; border: 1px solid #EEF0F3; background: #fff; color: #475467; font-size: 0.72rem; font-weight: 700; cursor: pointer; }
.mh__rsvp:hover { border-color: #F59E0B; color: #D97706; }
.mh__rsvp--on { background: linear-gradient(135deg, #FBBF24, #F59E0B); color: #fff; border: none; }
.mh__attendees { display: inline-flex; align-items: center; gap: 0.25rem; font-size: 0.75rem; color: #667085; font-weight: 600; }
.mh__event-del { margin-left: auto; background: none; border: none; color: #FCA5A5; cursor: pointer; }
.mh__event-del:hover { color: #EF4444; }

/* Espace mentor */
.mh__mentor { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; align-items: start; }
.mh__card-block { background: #fff; border: 1px solid #EEF0F3; border-radius: 1.6rem; padding: 1.5rem; box-shadow: 0 1px 2px rgba(16,24,40,0.03); }
.mh__block-sub { font-size: 0.82rem; color: #667085; margin: 0.3rem 0 1rem; }
.mh__avail-pick { display: flex; gap: 0.5rem; flex-wrap: wrap; }
.mh__avail-opt { display: inline-flex; align-items: center; gap: 0.4rem; padding: 0.5rem 0.9rem; border-radius: 999px; border: 1px solid #EEF0F3; background: #fff; color: #475467; font-size: 0.78rem; font-weight: 700; cursor: pointer; }
.mh__avail-opt--on { border-color: #F59E0B; background: #FEF6E7; color: #B45309; }
.mh__switch { display: flex; align-items: center; gap: 0.5rem; margin-top: 1rem; font-size: 0.85rem; font-weight: 700; color: #344054; cursor: pointer; }
.mh__switch input { width: 1.1rem; height: 1.1rem; accent-color: #F59E0B; }
.mh__hint { font-size: 0.72rem; color: #98A2B3; margin: 0.3rem 0 0; }

/* Photo */
.mh__photo-row { display: flex; align-items: center; gap: 1rem; margin: 0.4rem 0 0.2rem; }
.mh__photo { width: 4.5rem; height: 4.5rem; border-radius: 1rem; background: linear-gradient(135deg, #FBBF24, #F59E0B); color: #fff; display: flex; align-items: center; justify-content: center; overflow: hidden; flex-shrink: 0; }
.mh__photo img { width: 100%; height: 100%; object-fit: cover; }
.mh__photo-actions { flex: 1; }
.mh__file-hidden { display: none; }
.mh__btn-ghost { padding: 0.55rem 1rem; border-radius: 0.7rem; background: #fff; border: 1px solid #EEF0F3; color: #344054; font-weight: 700; font-size: 0.8rem; cursor: pointer; }
.mh__btn-ghost:hover { border-color: #F59E0B; color: #B45309; }
.mh__btn-ghost:disabled { opacity: 0.6; cursor: not-allowed; }

/* Jours de disponibilité */
.mh__days { display: flex; flex-wrap: wrap; gap: 0.35rem; }
.mh__day { padding: 0.4rem 0.7rem; border-radius: 0.6rem; border: 1px solid #EEF0F3; background: #fff; color: #475467; font-size: 0.75rem; font-weight: 700; cursor: pointer; text-transform: uppercase; }
.mh__day--on { background: #FEF6E7; border-color: #FDE68A; color: #B45309; }
.mh__links-form { display: flex; flex-direction: column; gap: 0.5rem; }

/* Carte : sous-lignes */
.mh__card-sub { display: flex; flex-wrap: wrap; gap: 0.6rem; margin-top: 0.6rem; font-size: 0.74rem; color: #667085; }
.mh__card-role, .mh__card-loc, .mh__card-exp { display: inline-flex; align-items: center; gap: 0.25rem; }
.mh__card-when { display: flex; align-items: center; gap: 0.4rem; margin-bottom: 0.9rem; font-size: 0.72rem; color: #667085; flex-wrap: wrap; }
.mh__when-days { font-weight: 700; color: #475467; }
.mh__when-note { color: #98A2B3; }
.mh__card-links { display: flex; flex-wrap: wrap; gap: 0.35rem; margin-bottom: 0.9rem; }
.mh__link-chip { display: inline-flex; align-items: center; gap: 0.25rem; font-size: 0.7rem; font-weight: 700; padding: 0.2rem 0.55rem; border-radius: 999px; background: #F1F3F6; color: #475467; text-decoration: none; }
.mh__link-chip:hover { background: #E4E7EC; color: #101828; }

/* Modales */
.mh__modal { position: fixed; inset: 0; z-index: 200; background: rgba(15,23,42,0.5); backdrop-filter: blur(4px); display: flex; align-items: center; justify-content: center; padding: 1rem; }
.mh__dialog { width: 100%; max-width: 480px; background: #fff; border-radius: 1.5rem; padding: 1.6rem; box-shadow: 0 30px 60px -20px rgba(16,24,40,0.5); max-height: 90vh; overflow-y: auto; }
.mh__dialog-head { display: flex; align-items: center; justify-content: space-between; margin-bottom: 1rem; }
.mh__dialog-title { font-size: 1.05rem; font-weight: 800; }
.mh__stars { display: flex; gap: 0.3rem; }
.mh__star { background: none; border: none; cursor: pointer; padding: 0; }
.mh__star--on { color: #F59E0B; }
.mh__star--off { color: #E4E7EC; }

.mh__card--clickable { cursor: pointer; }

/* Fiche mentor (modale) */
.mh__dialog--wide { max-width: 560px; position: relative; }
.mh__dialog-x { position: absolute; top: 1.1rem; right: 1.1rem; }
.mh__detail-head { display: flex; gap: 1rem; align-items: center; padding-right: 2rem; }
.mh__detail-avatar { position: relative; width: 4.5rem; height: 4.5rem; border-radius: 1.1rem; background: linear-gradient(135deg, #FBBF24, #F59E0B); color: #fff; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 1.4rem; overflow: hidden; flex-shrink: 0; }
.mh__detail-avatar img { width: 100%; height: 100%; object-fit: cover; }
.mh__detail-id { min-width: 0; }
.mh__detail-name { font-size: 1.3rem; font-weight: 800; margin: 0; }
.mh__detail-headline { font-size: 0.85rem; color: #667085; margin: 0.15rem 0 0.4rem; }
.mh__detail-facts { display: flex; flex-wrap: wrap; gap: 0.7rem; font-size: 0.75rem; color: #667085; }
.mh__detail-facts span { display: inline-flex; align-items: center; gap: 0.25rem; }
.mh__detail-meta { display: flex; align-items: center; gap: 0.7rem; margin: 1rem 0 0.6rem; }
.mh__detail-when { display: flex; align-items: center; gap: 0.4rem; font-size: 0.78rem; color: #667085; margin-bottom: 0.7rem; flex-wrap: wrap; }
.mh__tags--detail { margin: 0.4rem 0; }
.mh__detail-langs { font-size: 0.82rem; color: #475467; margin: 0.5rem 0; }
.mh__detail-bio { font-size: 0.88rem; line-height: 1.55; color: #344054; white-space: pre-wrap; margin: 0.7rem 0; }
.mh__card-links--detail { margin: 0.6rem 0 0.2rem; }
.mh__reviews { margin-top: 1rem; border-top: 1px solid #EEF0F3; padding-top: 1rem; }
.mh__reviews-head { display: flex; align-items: center; gap: 0.4rem; font-size: 0.9rem; font-weight: 800; color: #101828; margin-bottom: 0.7rem; }
.mh__reviews-empty { font-size: 0.82rem; color: #98A2B3; }
.mh__review-list { display: flex; flex-direction: column; gap: 0.7rem; max-height: 240px; overflow-y: auto; }
.mh__review { background: #F9FAFB; border: 1px solid #EEF0F3; border-radius: 0.9rem; padding: 0.7rem 0.9rem; }
.mh__review-top { display: flex; align-items: center; justify-content: space-between; }
.mh__review-author { font-weight: 700; font-size: 0.82rem; color: #101828; }
.mh__review-stars { display: inline-flex; color: #F59E0B; }
.mh__review-comment { font-size: 0.82rem; color: #475467; margin: 0.35rem 0 0; white-space: pre-wrap; }

.mh-fade-enter-active, .mh-fade-leave-active { transition: opacity 0.2s; }
.mh-fade-enter-from, .mh-fade-leave-to { opacity: 0; }

@media (max-width: 860px) {
  .mh__mentor { grid-template-columns: 1fr; }
  .mh__form-row { grid-template-columns: 1fr; }
}
</style>
