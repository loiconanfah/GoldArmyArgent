<script setup>
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { authFetch } from '@/utils/auth'
import { CalendarDaysIcon, PlusIcon, TrashIcon, MapPinIcon, LinkIcon, AcademicCapIcon, UsersIcon } from '@heroicons/vue/24/outline'

const { t } = useI18n()
const loading = ref(true)
const mentors = ref([])
const advisors = ref([])
const events = ref([])
const showForm = ref(false)
const saving = ref(false)
const form = ref({ title: '', description: '', date: '', location: '', link: '' })

async function load() {
  loading.value = true
  try {
    const [mRes, eRes] = await Promise.all([authFetch('/api/org/mentors'), authFetch('/api/org/events')])
    const mJson = await mRes.safeJson()
    const eJson = await eRes.safeJson()
    if (mJson?.status === 'success') { mentors.value = mJson.data.mentors; advisors.value = mJson.data.advisors }
    if (eJson?.status === 'success') events.value = eJson.data
  } catch (e) {} finally { loading.value = false }
}

async function createEvent() {
  if (!form.value.title.trim() || !form.value.date) return
  saving.value = true
  try {
    const res = await authFetch('/api/org/events', { method: 'POST', body: JSON.stringify(form.value) })
    const json = await res.safeJson()
    if (json?.status === 'success') {
      events.value.push(json.data)
      events.value.sort((a, b) => new Date(a.date) - new Date(b.date))
      form.value = { title: '', description: '', date: '', location: '', link: '' }
      showForm.value = false
    }
  } catch (e) {} finally { saving.value = false }
}

async function removeEvent(ev) {
  if (!confirm(t('org.events.remove_confirm'))) return
  try {
    const res = await authFetch(`/api/org/events/${ev.id}`, { method: 'DELETE' })
    if (res.ok) events.value = events.value.filter(x => x.id !== ev.id)
  } catch (e) {}
}

async function toggleRsvp(ev) {
  try {
    const res = await authFetch(`/api/org/events/${ev.id}/rsvp`, { method: 'POST' })
    const json = await res.safeJson()
    if (json?.status === 'success') {
      ev.is_attending = json.is_attending
      ev.attendees_count = json.attendees_count
    }
  } catch (e) {}
}

function fmtDate(d) { if (!d) return '—'; try { return new Date(d).toLocaleString() } catch { return d } }
function initials(p) { return (p.full_name || p.email || '?')[0].toUpperCase() }

onMounted(load)
</script>

<template>
  <div class="ome">
    <header class="ome__head">
      <div>
        <h1 class="ome__title">{{ t('org.nav.mentors') }}</h1>
        <p class="ome__sub">{{ t('org.mentors.sub') }}</p>
      </div>
    </header>

    <div v-if="loading" class="ome__loading">{{ t('common.loading') }}…</div>

    <template v-else>
      <div class="ome__cols">
        <!-- People -->
        <section class="ome__card">
          <h2 class="ome__card-title"><AcademicCapIcon class="w-4 h-4" /> {{ t('org.roles.mentor') }}s</h2>
          <div v-if="mentors.length" class="ome__people">
            <div v-for="p in mentors" :key="p.id" class="ome__person">
              <div class="ome__avatar ome__avatar--m">{{ initials(p) }}</div>
              <div><div class="ome__person-name">{{ p.full_name || p.email.split('@')[0] }}</div><div class="ome__person-email">{{ p.email }}</div></div>
            </div>
          </div>
          <p v-else class="ome__muted">{{ t('org.mentors.no_mentors') }}</p>

          <h2 class="ome__card-title mt"><AcademicCapIcon class="w-4 h-4" /> {{ t('org.roles.advisor') }}s</h2>
          <div v-if="advisors.length" class="ome__people">
            <div v-for="p in advisors" :key="p.id" class="ome__person">
              <div class="ome__avatar ome__avatar--a">{{ initials(p) }}</div>
              <div><div class="ome__person-name">{{ p.full_name || p.email.split('@')[0] }}</div><div class="ome__person-email">{{ p.email }}</div></div>
            </div>
          </div>
          <p v-else class="ome__muted">{{ t('org.mentors.no_advisors') }}</p>
          <p class="ome__hint">{{ t('org.mentors.assign_hint') }}</p>
        </section>

        <!-- Events -->
        <section class="ome__card">
          <div class="ome__events-head">
            <h2 class="ome__card-title"><CalendarDaysIcon class="w-4 h-4" /> {{ t('org.events.title') }}</h2>
            <button class="ome__add" @click="showForm = !showForm"><PlusIcon class="w-4 h-4" /> {{ t('org.events.add') }}</button>
          </div>

          <transition name="ome-form">
            <div v-if="showForm" class="ome__form">
              <input v-model="form.title" :placeholder="t('org.events.name')" class="ome__input" />
              <textarea v-model="form.description" :placeholder="t('org.events.description')" class="ome__input ome__textarea"></textarea>
              <input v-model="form.date" type="datetime-local" class="ome__input" />
              <input v-model="form.location" :placeholder="t('org.events.location')" class="ome__input" />
              <input v-model="form.link" :placeholder="t('org.events.link')" class="ome__input" />
              <button class="ome__save" @click="createEvent" :disabled="saving">{{ saving ? t('common.saving') : t('org.events.create') }}</button>
            </div>
          </transition>

          <div v-if="!events.length && !showForm" class="ome__muted">{{ t('org.events.empty') }}</div>
          <div class="ome__events">
            <div v-for="ev in events" :key="ev.id" class="ome__event">
              <div class="ome__event-date">{{ fmtDate(ev.date) }}</div>
              <button class="ome__event-del" @click="removeEvent(ev)"><TrashIcon class="w-4 h-4" /></button>
              <div class="ome__event-title">{{ ev.title }}</div>
              <p v-if="ev.description" class="ome__event-desc">{{ ev.description }}</p>
              <div class="ome__event-meta">
                <span v-if="ev.location"><MapPinIcon class="w-3.5 h-3.5" /> {{ ev.location }}</span>
                <a v-if="ev.link" :href="ev.link" target="_blank" class="ome__event-link"><LinkIcon class="w-3.5 h-3.5" /> {{ t('org.events.link_label') }}</a>
                <span class="ome__event-attendees"><UsersIcon class="w-3.5 h-3.5" /> {{ ev.attendees_count || 0 }}</span>
              </div>
              <div class="ome__event-foot">
                <button :class="['ome__rsvp', { 'ome__rsvp--on': ev.is_attending }]" @click="toggleRsvp(ev)">
                  {{ ev.is_attending ? t('org.events.attending') : t('org.events.rsvp') }}
                </button>
                <span class="ome__event-by">{{ t('org.events.by') }} {{ ev.created_by_name }}</span>
              </div>
            </div>
          </div>
        </section>
      </div>
    </template>
  </div>
</template>

<style scoped>
.ome { max-width: 1150px; margin: 0 auto; color: #1E293B; }
.ome__head { margin-bottom: 1.5rem; }
.ome__title { font-size: 1.7rem; font-weight: 800; margin: 0; letter-spacing: -0.02em; }
.ome__sub { color: #64748B; font-size: 0.9rem; margin: 0.3rem 0 0; }
.ome__loading { padding: 3rem; text-align: center; color: #94A3B8; }
.ome__cols { display: grid; grid-template-columns: 1fr 1.3fr; gap: 1rem; align-items: start; }
.ome__card { background: #fff; border: 1px solid #E2E8F0; border-radius: 1.1rem; padding: 1.4rem; box-shadow: 0 1px 2px rgba(15,23,42,0.04); }
.ome__card-title { display: flex; align-items: center; gap: 0.4rem; font-size: 0.9rem; font-weight: 700; margin: 0 0 0.9rem; color: #334155; }
.ome__card-title.mt { margin-top: 1.4rem; }
.ome__people { display: flex; flex-direction: column; gap: 0.5rem; }
.ome__person { display: flex; align-items: center; gap: 0.7rem; padding: 0.55rem; border-radius: 0.7rem; background: #F8FAFC; border: 1px solid #F1F5F9; }
.ome__avatar { width: 2.3rem; height: 2.3rem; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 0.85rem; color: #fff; flex-shrink: 0; }
.ome__avatar--m { background: linear-gradient(135deg, #6366F1, #8B5CF6); }
.ome__avatar--a { background: linear-gradient(135deg, #FBBF24, #F59E0B); }
.ome__person-name { font-weight: 700; font-size: 0.85rem; color: #1E293B; }
.ome__person-email { font-size: 0.7rem; color: #94A3B8; }
.ome__muted { color: #94A3B8; font-size: 0.82rem; }
.ome__hint { font-size: 0.72rem; color: #94A3B8; margin-top: 1rem; border-top: 1px solid #F1F5F9; padding-top: 0.85rem; }

.ome__events-head { display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.5rem; }
.ome__add { display: inline-flex; align-items: center; gap: 0.3rem; padding: 0.5rem 0.9rem; border-radius: 0.6rem; background: linear-gradient(135deg, #FBBF24, #F59E0B); color: #fff; border: none; font-weight: 700; font-size: 0.75rem; cursor: pointer; box-shadow: 0 5px 14px -6px rgba(245,158,11,0.6); }
.ome__form { display: flex; flex-direction: column; gap: 0.5rem; margin: 0.5rem 0 1rem; padding: 1rem; border-radius: 0.8rem; background: #F8FAFC; border: 1px solid #F1F5F9; }
.ome__input { padding: 0.6rem 0.8rem; border-radius: 0.55rem; background: #fff; border: 1px solid #E2E8F0; color: #1E293B; font-size: 0.82rem; outline: none; }
.ome__input:focus { border-color: #F59E0B; box-shadow: 0 0 0 3px rgba(245,158,11,0.12); }
.ome__textarea { resize: vertical; min-height: 56px; }
.ome__save { padding: 0.6rem; border-radius: 0.55rem; background: #F59E0B; color: #fff; border: none; font-weight: 700; font-size: 0.8rem; cursor: pointer; }
.ome__events { display: flex; flex-direction: column; gap: 0.7rem; margin-top: 0.5rem; }
.ome__event { position: relative; padding: 1rem; border-radius: 0.8rem; background: #F8FAFC; border: 1px solid #F1F5F9; border-left: 3px solid #F59E0B; }
.ome__event-date { font-size: 0.72rem; font-weight: 700; color: #D97706; }
.ome__event-del { position: absolute; top: 0.8rem; right: 0.8rem; background: none; border: none; color: #FCA5A5; cursor: pointer; }
.ome__event-del:hover { color: #EF4444; }
.ome__event-title { font-weight: 700; font-size: 0.94rem; color: #0F172A; margin-top: 0.2rem; }
.ome__event-desc { font-size: 0.78rem; color: #64748B; margin: 0.4rem 0 0.5rem; }
.ome__event-meta { display: flex; gap: 1rem; font-size: 0.72rem; color: #64748B; }
.ome__event-meta span, .ome__event-link { display: inline-flex; align-items: center; gap: 0.25rem; }
.ome__event-link { color: #D97706; text-decoration: none; font-weight: 600; }
.ome__event-attendees { display: inline-flex; align-items: center; gap: 0.25rem; color: #64748B; }
.ome__event-foot { display: flex; align-items: center; justify-content: space-between; gap: 0.5rem; margin-top: 0.7rem; padding-top: 0.6rem; border-top: 1px solid #F1F5F9; }
.ome__rsvp { padding: 0.35rem 0.9rem; border-radius: 999px; border: 1px solid #E2E8F0; background: #fff; color: #475569; font-size: 0.72rem; font-weight: 700; cursor: pointer; transition: all 0.15s; }
.ome__rsvp:hover { border-color: #F59E0B; color: #D97706; }
.ome__rsvp--on { background: linear-gradient(135deg, #FBBF24, #F59E0B); color: #fff; border: none; }
.ome__event-by { font-size: 0.65rem; color: #94A3B8; }
.ome-form-enter-active, .ome-form-leave-active { transition: opacity 0.2s; }
.ome-form-enter-from, .ome-form-leave-to { opacity: 0; }
@media (max-width: 860px) { .ome__cols { grid-template-columns: 1fr; } }
</style>
