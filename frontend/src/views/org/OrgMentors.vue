<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { authFetch } from '@/utils/auth'
import {
  CalendarDaysIcon, PlusIcon, TrashIcon, MapPinIcon, LinkIcon,
  AcademicCapIcon, UsersIcon, UserPlusIcon, VideoCameraIcon, XMarkIcon
} from '@heroicons/vue/24/outline'

const { t } = useI18n()
const router = useRouter()
// memberMode: vue "consultation" côté app candidat (masque les contrôles admin)
const props = defineProps({ memberMode: { type: Boolean, default: false } })
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
    const mJson = await mRes.safeJson(); const eJson = await eRes.safeJson()
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
      events.value.push({ ...json.data, attendees_count: 0, is_attending: false })
      events.value.sort((a, b) => new Date(a.date) - new Date(b.date))
      form.value = { title: '', description: '', date: '', location: '', link: '' }
      showForm.value = false
    }
  } catch (e) {} finally { saving.value = false }
}
async function removeEvent(ev) {
  if (!confirm(t('org.events.remove_confirm'))) return
  try { const res = await authFetch(`/api/org/events/${ev.id}`, { method: 'DELETE' }); if (res.ok) events.value = events.value.filter(x => x.id !== ev.id) } catch (e) {}
}
async function toggleRsvp(ev) {
  try {
    const res = await authFetch(`/api/org/events/${ev.id}/rsvp`, { method: 'POST' })
    const json = await res.safeJson()
    if (json?.status === 'success') { ev.is_attending = json.is_attending; ev.attendees_count = json.attendees_count }
  } catch (e) {}
}

const totalPeople = computed(() => mentors.value.length + advisors.value.length)
const upcomingCount = computed(() => events.value.filter(e => new Date(e.date) >= new Date()).length)
function initials(p) { return (p.full_name || p.email || '?')[0].toUpperCase() }
const MONTHS = ['JAN','FÉV','MAR','AVR','MAI','JUIN','JUIL','AOÛ','SEP','OCT','NOV','DÉC']
function evDay(d) { try { return new Date(d).getDate() } catch { return '--' } }
function evMonth(d) { try { return MONTHS[new Date(d).getMonth()] } catch { return '' } }
function evTime(d) { try { return new Date(d).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) } catch { return '' } }
function isPast(d) { try { return new Date(d) < new Date() } catch { return false } }

onMounted(load)
</script>

<template>
  <div class="ome">
    <header class="ome__head">
      <div>
        <h1 class="ome__title">{{ t('org.nav.mentors') }}</h1>
        <p class="ome__sub">{{ t('org.mentors.sub') }}</p>
      </div>
      <button v-if="!memberMode" class="ome__cta" @click="showForm = !showForm"><PlusIcon class="w-4 h-4" /> {{ t('org.events.add') }}</button>
    </header>

    <!-- Quick stats -->
    <div class="ome__stats">
      <div class="ome__stat"><AcademicCapIcon class="ome__stat-ic ome__stat-ic--i" /><div><b>{{ mentors.length }}</b><span>{{ t('org.roles.mentor') }}s</span></div></div>
      <div class="ome__stat"><UsersIcon class="ome__stat-ic ome__stat-ic--g" /><div><b>{{ advisors.length }}</b><span>{{ t('org.roles.advisor') }}s</span></div></div>
      <div class="ome__stat"><CalendarDaysIcon class="ome__stat-ic ome__stat-ic--s" /><div><b>{{ upcomingCount }}</b><span>{{ t('org.mentors.upcoming') }}</span></div></div>
    </div>

    <div v-if="loading" class="ome__loading">{{ t('common.loading') }}…</div>

    <template v-else>
      <div class="ome__cols">
        <!-- People -->
        <section class="ome__card">
          <div class="ome__card-head">
            <h2 class="ome__card-title"><AcademicCapIcon class="w-4 h-4" /> {{ t('org.mentors.team') }}</h2>
            <button v-if="!memberMode" class="ome__link-btn" @click="router.push('/organisation/membres')"><UserPlusIcon class="w-3.5 h-3.5" /> {{ t('org.mentors.assign') }}</button>
          </div>

          <div v-if="totalPeople" class="ome__people">
            <div v-for="p in mentors" :key="p.id" class="ome__person">
              <div class="ome__avatar ome__avatar--m">{{ initials(p) }}</div>
              <div class="ome__person-info"><div class="ome__person-name">{{ p.full_name || p.email.split('@')[0] }}</div><div class="ome__person-email">{{ p.email }}</div></div>
              <span class="ome__role-tag ome__role-tag--m">{{ t('org.roles.mentor') }}</span>
            </div>
            <div v-for="p in advisors" :key="p.id" class="ome__person">
              <div class="ome__avatar ome__avatar--a">{{ initials(p) }}</div>
              <div class="ome__person-info"><div class="ome__person-name">{{ p.full_name || p.email.split('@')[0] }}</div><div class="ome__person-email">{{ p.email }}</div></div>
              <span class="ome__role-tag ome__role-tag--a">{{ t('org.roles.advisor') }}</span>
            </div>
          </div>
          <div v-else class="ome__empty-block">
            <AcademicCapIcon class="ome__empty-ic" />
            <p>{{ t('org.mentors.empty_team') }}</p>
            <button v-if="!memberMode" class="ome__empty-btn" @click="router.push('/organisation/membres')">{{ t('org.mentors.assign') }}</button>
          </div>
        </section>

        <!-- Events -->
        <section class="ome__card">
          <div class="ome__card-head">
            <h2 class="ome__card-title"><CalendarDaysIcon class="w-4 h-4" /> {{ t('org.events.title') }}</h2>
          </div>

          <transition name="ome-form">
            <div v-if="showForm && !memberMode" class="ome__form">
              <div class="ome__form-head">{{ t('org.events.new') }}<button class="ome__form-close" @click="showForm = false"><XMarkIcon class="w-4 h-4" /></button></div>
              <input v-model="form.title" :placeholder="t('org.events.name')" class="ome__input" />
              <textarea v-model="form.description" :placeholder="t('org.events.description')" class="ome__input ome__textarea"></textarea>
              <div class="ome__form-row">
                <input v-model="form.date" type="datetime-local" class="ome__input" />
                <input v-model="form.location" :placeholder="t('org.events.location')" class="ome__input" />
              </div>
              <input v-model="form.link" :placeholder="t('org.events.link')" class="ome__input" />
              <button class="ome__save" @click="createEvent" :disabled="saving">{{ saving ? t('common.saving') : t('org.events.create') }}</button>
            </div>
          </transition>

          <div v-if="!events.length && !showForm" class="ome__empty-block">
            <CalendarDaysIcon class="ome__empty-ic" />
            <p>{{ t('org.events.empty') }}</p>
            <button v-if="!memberMode" class="ome__empty-btn" @click="showForm = true">{{ t('org.events.add') }}</button>
          </div>

          <div class="ome__events">
            <div v-for="ev in events" :key="ev.id" :class="['ome__event', { 'ome__event--past': isPast(ev.date) }]">
              <div class="ome__cal">
                <span class="ome__cal-day">{{ evDay(ev.date) }}</span>
                <span class="ome__cal-month">{{ evMonth(ev.date) }}</span>
              </div>
              <div class="ome__event-body">
                <div class="ome__event-title">{{ ev.title }}</div>
                <p v-if="ev.description" class="ome__event-desc">{{ ev.description }}</p>
                <div class="ome__event-meta">
                  <span><CalendarDaysIcon class="w-3.5 h-3.5" /> {{ evTime(ev.date) }}</span>
                  <span v-if="ev.location"><MapPinIcon class="w-3.5 h-3.5" /> {{ ev.location }}</span>
                  <a v-if="ev.link" :href="ev.link" target="_blank" class="ome__event-link"><VideoCameraIcon class="w-3.5 h-3.5" /> {{ t('org.events.link_label') }}</a>
                </div>
                <div class="ome__event-foot">
                  <button :class="['ome__rsvp', { 'ome__rsvp--on': ev.is_attending }]" @click="toggleRsvp(ev)">
                    {{ ev.is_attending ? t('org.events.attending') : t('org.events.rsvp') }}
                  </button>
                  <span class="ome__attendees"><UsersIcon class="w-3.5 h-3.5" /> {{ ev.attendees_count || 0 }}</span>
                  <button v-if="!memberMode" class="ome__event-del" @click="removeEvent(ev)"><TrashIcon class="w-4 h-4" /></button>
                </div>
              </div>
            </div>
          </div>
        </section>
      </div>
    </template>
  </div>
</template>

<style scoped>
.ome { max-width: 1200px; margin: 0 auto; color: #101828; }
.ome__head { display: flex; align-items: flex-end; justify-content: space-between; gap: 1rem; margin-bottom: 1.3rem; flex-wrap: wrap; }
.ome__title { font-size: 1.9rem; font-weight: 800; margin: 0; letter-spacing: -0.03em; }
.ome__sub { color: #667085; font-size: 0.92rem; margin: 0.3rem 0 0; }
.ome__cta { display: inline-flex; align-items: center; gap: 0.45rem; padding: 0.7rem 1.15rem; border-radius: 999px; background: linear-gradient(135deg, #FBBF24, #F59E0B); color: #fff; border: none; font-weight: 700; font-size: 0.85rem; cursor: pointer; box-shadow: 0 10px 22px -10px rgba(245,158,11,0.7); transition: transform 0.15s; }
.ome__cta:hover { transform: translateY(-2px); }

.ome__stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 0.9rem; margin-bottom: 1.1rem; }
.ome__stat { display: flex; align-items: center; gap: 0.8rem; background: #fff; border: 1px solid #EEF0F3; border-radius: 1.25rem; padding: 1.1rem 1.2rem; box-shadow: 0 1px 2px rgba(16,24,40,0.03); }
.ome__stat-ic { width: 2.4rem; height: 2.4rem; padding: 0.5rem; border-radius: 0.8rem; flex-shrink: 0; }
.ome__stat-ic--i { color: #4F46E5; background: #EEF2FF; }
.ome__stat-ic--g { color: #D97706; background: #FEF3C7; }
.ome__stat-ic--s { color: #0284C7; background: #E0F2FE; }
.ome__stat b { font-size: 1.4rem; font-weight: 800; color: #101828; display: block; line-height: 1; }
.ome__stat span { font-size: 0.72rem; color: #98A2B3; text-transform: uppercase; font-weight: 600; }

.ome__loading { padding: 4rem; text-align: center; color: #98A2B3; }
.ome__cols { display: grid; grid-template-columns: 1fr 1.25fr; gap: 1rem; align-items: start; }
.ome__card { background: #fff; border: 1px solid #EEF0F3; border-radius: 1.6rem; padding: 1.5rem; box-shadow: 0 1px 2px rgba(16,24,40,0.03); }
.ome__card-head { display: flex; align-items: center; justify-content: space-between; margin-bottom: 1.1rem; }
.ome__card-title { display: flex; align-items: center; gap: 0.4rem; font-size: 1rem; font-weight: 800; margin: 0; color: #101828; }
.ome__link-btn { display: inline-flex; align-items: center; gap: 0.3rem; background: none; border: none; color: #D97706; font-size: 0.76rem; font-weight: 700; cursor: pointer; }

.ome__people { display: flex; flex-direction: column; gap: 0.55rem; }
.ome__person { display: flex; align-items: center; gap: 0.75rem; padding: 0.65rem; border-radius: 1rem; background: #F9FAFB; border: 1px solid #EEF0F3; transition: transform 0.15s; }
.ome__person:hover { transform: translateX(3px); }
.ome__avatar { width: 2.5rem; height: 2.5rem; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 0.9rem; color: #fff; flex-shrink: 0; }
.ome__avatar--m { background: linear-gradient(135deg, #6366F1, #8B5CF6); }
.ome__avatar--a { background: linear-gradient(135deg, #FBBF24, #F59E0B); }
.ome__person-info { flex: 1; min-width: 0; }
.ome__person-name { font-weight: 700; font-size: 0.88rem; color: #101828; }
.ome__person-email { font-size: 0.72rem; color: #98A2B3; }
.ome__role-tag { font-size: 0.6rem; font-weight: 800; text-transform: uppercase; padding: 0.2rem 0.5rem; border-radius: 999px; }
.ome__role-tag--m { background: #EEF2FF; color: #4F46E5; }
.ome__role-tag--a { background: #FEF3C7; color: #D97706; }

.ome__empty-block { text-align: center; padding: 2rem 1rem; }
.ome__empty-ic { width: 2.8rem; height: 2.8rem; color: #D0D5DD; margin: 0 auto 0.7rem; }
.ome__empty-block p { color: #98A2B3; font-size: 0.85rem; margin: 0 0 1rem; }
.ome__empty-btn { padding: 0.6rem 1.2rem; border-radius: 999px; background: #F9FAFB; border: 1px solid #EEF0F3; color: #344054; font-weight: 700; font-size: 0.8rem; cursor: pointer; }
.ome__empty-btn:hover { border-color: #F59E0B; color: #D97706; }

.ome__form { display: flex; flex-direction: column; gap: 0.55rem; margin-bottom: 1.1rem; padding: 1.1rem; border-radius: 1.2rem; background: #F9FAFB; border: 1px solid #EEF0F3; }
.ome__form-head { display: flex; align-items: center; justify-content: space-between; font-weight: 800; font-size: 0.85rem; color: #101828; margin-bottom: 0.2rem; }
.ome__form-close { background: none; border: none; color: #98A2B3; cursor: pointer; }
.ome__form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 0.55rem; }
.ome__input { padding: 0.65rem 0.85rem; border-radius: 0.7rem; background: #fff; border: 1px solid #EEF0F3; color: #101828; font-size: 0.82rem; outline: none; }
.ome__input:focus { border-color: #F59E0B; box-shadow: 0 0 0 3px rgba(245,158,11,0.12); }
.ome__textarea { resize: vertical; min-height: 56px; }
.ome__save { padding: 0.7rem; border-radius: 0.8rem; background: linear-gradient(135deg, #FBBF24, #F59E0B); color: #fff; border: none; font-weight: 700; font-size: 0.82rem; cursor: pointer; }

.ome__events { display: flex; flex-direction: column; gap: 0.75rem; }
.ome__event { display: flex; gap: 0.9rem; padding: 1rem; border-radius: 1.2rem; background: #fff; border: 1px solid #EEF0F3; transition: box-shadow 0.15s, transform 0.15s; }
.ome__event:hover { box-shadow: 0 12px 26px -18px rgba(16,24,40,0.3); transform: translateY(-2px); }
.ome__event--past { opacity: 0.6; }
.ome__cal { width: 3.3rem; flex-shrink: 0; border-radius: 0.9rem; background: linear-gradient(160deg, #FEF3C7, #FDE68A); display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 0.5rem 0; }
.ome__cal-day { font-size: 1.4rem; font-weight: 800; color: #B45309; line-height: 1; }
.ome__cal-month { font-size: 0.6rem; font-weight: 800; color: #D97706; letter-spacing: 0.05em; margin-top: 0.15rem; }
.ome__event-body { flex: 1; min-width: 0; }
.ome__event-title { font-weight: 700; font-size: 0.95rem; color: #101828; }
.ome__event-desc { font-size: 0.78rem; color: #667085; margin: 0.35rem 0 0.5rem; }
.ome__event-meta { display: flex; flex-wrap: wrap; gap: 0.9rem; font-size: 0.72rem; color: #667085; }
.ome__event-meta span, .ome__event-link { display: inline-flex; align-items: center; gap: 0.25rem; }
.ome__event-link { color: #D97706; text-decoration: none; font-weight: 600; }
.ome__event-foot { display: flex; align-items: center; gap: 0.6rem; margin-top: 0.7rem; padding-top: 0.6rem; border-top: 1px solid #F1F3F6; }
.ome__rsvp { padding: 0.35rem 0.95rem; border-radius: 999px; border: 1px solid #EEF0F3; background: #fff; color: #475467; font-size: 0.72rem; font-weight: 700; cursor: pointer; transition: all 0.15s; }
.ome__rsvp:hover { border-color: #F59E0B; color: #D97706; }
.ome__rsvp--on { background: linear-gradient(135deg, #FBBF24, #F59E0B); color: #fff; border: none; }
.ome__attendees { display: inline-flex; align-items: center; gap: 0.25rem; font-size: 0.75rem; color: #667085; font-weight: 600; }
.ome__event-del { margin-left: auto; background: none; border: none; color: #FCA5A5; cursor: pointer; }
.ome__event-del:hover { color: #EF4444; }

.ome-form-enter-active, .ome-form-leave-active { transition: opacity 0.2s; }
.ome-form-enter-from, .ome-form-leave-to { opacity: 0; }
@media (max-width: 860px) { .ome__cols { grid-template-columns: 1fr; } .ome__form-row { grid-template-columns: 1fr; } }
</style>
