<script setup>
import { ref, onMounted, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { authFetch } from '@/utils/auth'
import { XMarkIcon, TrashIcon, AcademicCapIcon, DocumentTextIcon, BriefcaseIcon, ChatBubbleLeftRightIcon, SparklesIcon, LockClosedIcon } from '@heroicons/vue/24/outline'
import { useRouter } from 'vue-router'

const { t } = useI18n()
const router = useRouter()
const loading = ref(true)
const members = ref([])
const search = ref('')
const seat = ref({ gold: 300, cap: 5, used: 0 })
const sponsoring = ref('')

const detailOpen = ref(false)
const detailLoading = ref(false)
const detail = ref(null)
const savingRole = ref(false)

const filtered = computed(() => {
  const q = search.value.toLowerCase().trim()
  if (!q) return members.value
  return members.value.filter(m =>
    (m.full_name || '').toLowerCase().includes(q) || (m.email || '').toLowerCase().includes(q))
})
const usedSeats = computed(() => members.value.filter(m => m.sponsored).length)
const capReached = computed(() => seat.value.cap != null && usedSeats.value >= seat.value.cap)

async function load() {
  loading.value = true
  try {
    const [mRes, bRes] = await Promise.all([authFetch('/api/org/members'), authFetch('/api/org/billing')])
    const mJson = await mRes.safeJson()
    const bJson = await bRes.safeJson()
    if (mJson?.status === 'success') members.value = mJson.data
    if (bJson?.status === 'success') {
      seat.value = { gold: bJson.data.member_gold, cap: bJson.data.sponsored_seats_cap, used: bJson.data.sponsored_seats_used }
    }
  } catch (e) {}
  finally { loading.value = false }
}

async function toggleSponsor(m) {
  const next = !m.sponsored
  if (next && capReached.value) { alert(t('org.sponsor.cap_reached', { cap: seat.value.cap })); return }
  sponsoring.value = m.id
  try {
    const res = await authFetch(`/api/org/members/${m.id}/sponsor`, { method: 'PUT', body: JSON.stringify({ sponsored: next }) })
    const json = await res.safeJson()
    if (res.ok && json?.status === 'success') {
      m.sponsored = next
      if (detail.value && detail.value.profile.id === m.id) { detail.value.profile.sponsored = next }
    } else {
      alert(json?.detail || t('common.error'))
    }
  } catch (e) { alert(t('common.error')) }
  finally { sponsoring.value = '' }
}

async function openDetail(m) {
  detailOpen.value = true
  detailLoading.value = true
  detail.value = null
  try {
    const res = await authFetch(`/api/org/members/${m.id}/detail`)
    const json = await res.safeJson()
    if (json?.status === 'success') detail.value = json.data
  } catch (e) {}
  finally { detailLoading.value = false }
}

function closeDetail() { detailOpen.value = false }

async function setRole(role) {
  if (!detail.value) return
  savingRole.value = true
  try {
    await authFetch(`/api/org/members/${detail.value.profile.id}/role`, {
      method: 'PUT', body: JSON.stringify({ member_role: role })
    })
    detail.value.profile.org_member_role = role
  } catch (e) {}
  finally { savingRole.value = false }
}

async function removeMember(m) {
  if (!confirm(t('org.members.remove_confirm', { name: m.full_name || m.email }))) return
  try {
    const res = await authFetch(`/api/org/members/${m.id}`, { method: 'DELETE' })
    if (res.ok) { members.value = members.value.filter(x => x.id !== m.id); closeDetail() }
  } catch (e) {}
}

const funnelList = computed(() => {
  const f = detail.value?.funnel || {}
  return Object.entries(f).map(([k, v]) => ({ k, v }))
})

function fmtDate(d) { if (!d) return '—'; try { return new Date(d).toLocaleDateString() } catch { return '—' } }
function roleBadge(r) {
  return r === 'mentor' ? t('org.roles.mentor') : r === 'advisor' ? t('org.roles.advisor') : t('org.roles.member')
}

onMounted(load)
</script>

<template>
  <div class="om">
    <header class="om__head">
      <div>
        <h1 class="om__title">{{ t('org.tabs.members') }}</h1>
        <p class="om__sub">{{ t('org.members.sub') }}</p>
      </div>
      <div class="om__head-right">
        <button class="om__seats" @click="router.push('/organisation/facturation')" :title="t('org.sponsor.manage')">
          <SparklesIcon class="w-4 h-4" />
          <span><b>{{ usedSeats }}</b> / {{ seat.cap ?? '∞' }} {{ t('org.sponsor.seats') }}</span>
          <span class="om__seats-tier">{{ seat.gold }} Gold/mois</span>
        </button>
        <input v-model="search" class="om__search" :placeholder="t('org.members.search')" />
      </div>
    </header>

    <div v-if="loading" class="om__loading">{{ t('common.loading') }}…</div>
    <div v-else-if="!members.length" class="om__empty">{{ t('org.members.empty') }}</div>

    <div v-else class="om__grid">
      <button v-for="m in filtered" :key="m.id" class="om__card" @click="openDetail(m)">
        <div class="om__avatar">{{ (m.full_name || m.email)[0].toUpperCase() }}</div>
        <div class="om__info">
          <div class="om__name">{{ m.full_name || m.email.split('@')[0] }}</div>
          <div class="om__email">{{ m.email }}</div>
        </div>
        <div class="om__mini">
          <div class="om__mini-item"><strong>{{ m.applications }}</strong><span>{{ t('org.stats.applications') }}</span></div>
          <div class="om__mini-item"><strong>{{ m.interviews }}</strong><span>{{ t('org.stats.interviews') }}</span></div>
        </div>
        <span
          :class="['om__spon', m.sponsored ? 'om__spon--on' : 'om__spon--off']"
          role="button" :aria-disabled="sponsoring === m.id"
          @click.stop="toggleSponsor(m)"
          :title="m.sponsored ? t('org.sponsor.remove') : t('org.sponsor.give')"
        >
          <SparklesIcon v-if="m.sponsored" class="w-3.5 h-3.5" />
          <LockClosedIcon v-else class="w-3.5 h-3.5" />
          {{ m.sponsored ? t('org.sponsor.premium') : t('org.sponsor.free') }}
        </span>
      </button>
    </div>

    <!-- Detail drawer -->
    <transition name="om-drawer">
      <div v-if="detailOpen" class="om__drawer-wrap" @click.self="closeDetail">
        <aside class="om__drawer">
          <button class="om__drawer-close" @click="closeDetail"><XMarkIcon class="w-5 h-5" /></button>

          <div v-if="detailLoading" class="om__loading">{{ t('common.loading') }}…</div>
          <template v-else-if="detail">
            <div class="om__drawer-head">
              <div class="om__avatar om__avatar--lg">{{ (detail.profile.full_name || detail.profile.email)[0].toUpperCase() }}</div>
              <div>
                <div class="om__drawer-name">{{ detail.profile.full_name || detail.profile.email.split('@')[0] }}</div>
                <div class="om__drawer-email">{{ detail.profile.email }}</div>
                <div class="om__drawer-meta">
                  {{ t('org.members.joined') }} {{ fmtDate(detail.profile.joined_at) }} ·
                  <span :class="['om__role-tag', 'om__role-tag--' + detail.profile.org_member_role]">{{ roleBadge(detail.profile.org_member_role) }}</span>
                </div>
              </div>
            </div>

            <!-- Sponsorship (accès premium) -->
            <div class="om__section om__section--spon" :class="{ 'om__section--spon-on': detail.profile.sponsored }">
              <div class="om__spon-row">
                <div>
                  <h3 class="om__section-title om__section-title--tight"><SparklesIcon class="w-4 h-4" /> {{ t('org.sponsor.title') }}</h3>
                  <p class="om__spon-desc">
                    {{ detail.profile.sponsored
                        ? t('org.sponsor.on_desc', { gold: seat.gold })
                        : t('org.sponsor.off_desc') }}
                  </p>
                </div>
                <button
                  :class="['om__spon-toggle', { 'om__spon-toggle--on': detail.profile.sponsored }]"
                  :disabled="sponsoring === detail.profile.id || (!detail.profile.sponsored && capReached)"
                  @click="toggleSponsor(detail.profile)"
                >
                  <span class="om__spon-knob"></span>
                </button>
              </div>
              <p v-if="!detail.profile.sponsored && capReached" class="om__spon-cap">{{ t('org.sponsor.cap_note', { cap: seat.cap }) }}</p>
            </div>

            <!-- Role assign -->
            <div class="om__section">
              <h3 class="om__section-title"><AcademicCapIcon class="w-4 h-4" /> {{ t('org.members.assign_role') }}</h3>
              <div class="om__roles">
                <button v-for="r in ['member','mentor','advisor']" :key="r"
                  :class="['om__role-btn', { 'om__role-btn--active': detail.profile.org_member_role === r }]"
                  :disabled="savingRole" @click="setRole(r)">{{ roleBadge(r) }}</button>
              </div>
            </div>

            <!-- Funnel -->
            <div class="om__section">
              <h3 class="om__section-title"><BriefcaseIcon class="w-4 h-4" /> {{ t('org.home.funnel') }}</h3>
              <div class="om__funnel">
                <span v-for="f in funnelList" :key="f.k" class="om__funnel-chip">{{ f.k }} <strong>{{ f.v }}</strong></span>
                <span v-if="!funnelList.length" class="om__muted">{{ t('org.members.no_apps') }}</span>
              </div>
            </div>

            <!-- Applications -->
            <div class="om__section">
              <h3 class="om__section-title"><DocumentTextIcon class="w-4 h-4" /> {{ t('org.members.applications_list') }} ({{ detail.applications.length }})</h3>
              <div class="om__list">
                <div v-for="a in detail.applications.slice(0, 12)" :key="a.id" class="om__list-row">
                  <div>
                    <div class="om__list-title">{{ a.job_title || '—' }}</div>
                    <div class="om__list-sub">{{ a.company_name || '—' }}</div>
                  </div>
                  <span class="om__status">{{ a.status }}</span>
                </div>
                <div v-if="!detail.applications.length" class="om__muted">{{ t('org.members.no_apps') }}</div>
              </div>
            </div>

            <!-- Simulations -->
            <div class="om__section">
              <h3 class="om__section-title"><ChatBubbleLeftRightIcon class="w-4 h-4" /> {{ t('org.members.simulations') }} ({{ detail.simulations.length }})</h3>
              <div class="om__list">
                <div v-for="s in detail.simulations.slice(0, 8)" :key="s.id" class="om__list-row">
                  <div class="om__list-title">{{ s.job_title || s.company_name || t('org.members.simulation') }}</div>
                  <span class="om__status">{{ s.status }}</span>
                </div>
                <div v-if="!detail.simulations.length" class="om__muted">{{ t('org.members.no_sims') }}</div>
              </div>
            </div>

            <button class="om__remove" @click="removeMember(detail.profile)">
              <TrashIcon class="w-4 h-4" /> {{ t('org.members.remove') }}
            </button>
          </template>
        </aside>
      </div>
    </transition>
  </div>
</template>

<style scoped>
.om { max-width: 1200px; margin: 0 auto; color: #1E293B; }
.om__head { display: flex; align-items: flex-end; justify-content: space-between; gap: 1rem; margin-bottom: 1.5rem; flex-wrap: wrap; }
.om__title { font-size: 1.7rem; font-weight: 800; margin: 0; letter-spacing: -0.02em; }
.om__sub { color: #64748B; font-size: 0.9rem; margin: 0.3rem 0 0; }
.om__search { padding: 0.65rem 0.95rem; border-radius: 0.7rem; background: #fff; border: 1px solid #EEF0F3; color: #1E293B; font-size: 0.85rem; min-width: 240px; outline: none; box-shadow: 0 1px 2px rgba(15,23,42,0.04); }
.om__search:focus { border-color: #F59E0B; box-shadow: 0 0 0 3px rgba(245,158,11,0.15); }
.om__head-right { display: flex; align-items: center; gap: 0.6rem; flex-wrap: wrap; }
.om__seats { display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.55rem 0.9rem; border-radius: 999px; background: #FFFBEB; border: 1px solid #FDE68A; color: #B45309; font-size: 0.82rem; font-weight: 700; cursor: pointer; }
.om__seats b { color: #92400E; }
.om__seats-tier { font-size: 0.6rem; font-weight: 800; text-transform: uppercase; background: #F59E0B; color: #fff; padding: 0.1rem 0.4rem; border-radius: 999px; }

/* Sponsor badge on member cards */
.om__spon { display: inline-flex; align-items: center; gap: 0.3rem; font-size: 0.6rem; font-weight: 800; text-transform: uppercase; padding: 0.28rem 0.6rem; border-radius: 999px; cursor: pointer; user-select: none; transition: all 0.15s; }
.om__spon--on { background: linear-gradient(135deg, #FBBF24, #F59E0B); color: #fff; box-shadow: 0 4px 10px -4px rgba(245,158,11,0.6); }
.om__spon--off { background: #F1F3F6; color: #98A2B3; }
.om__spon--off:hover { background: #FEF3C7; color: #B45309; }

/* Sponsorship section in drawer */
.om__section--spon { border-color: #FDE68A; background: #FFFBEB; }
.om__section--spon-on { border-color: #F59E0B; }
.om__spon-row { display: flex; align-items: center; justify-content: space-between; gap: 0.8rem; }
.om__section-title--tight { margin: 0 0 0.3rem; }
.om__spon-desc { font-size: 0.76rem; color: #92400E; margin: 0; }
.om__spon-toggle { width: 3rem; height: 1.7rem; border-radius: 999px; border: none; background: #E2E8F0; position: relative; cursor: pointer; flex-shrink: 0; transition: background 0.2s; }
.om__spon-toggle--on { background: linear-gradient(135deg, #FBBF24, #F59E0B); }
.om__spon-toggle:disabled { opacity: 0.5; cursor: not-allowed; }
.om__spon-knob { position: absolute; top: 0.2rem; left: 0.2rem; width: 1.3rem; height: 1.3rem; border-radius: 50%; background: #fff; transition: transform 0.2s; box-shadow: 0 1px 3px rgba(0,0,0,0.2); }
.om__spon-toggle--on .om__spon-knob { transform: translateX(1.3rem); }
.om__spon-cap { font-size: 0.72rem; color: #B45309; margin: 0.6rem 0 0; }
.om__loading, .om__empty { padding: 3rem; text-align: center; color: #94A3B8; }

.om__grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(290px, 1fr)); gap: 0.9rem; }
.om__card { display: flex; align-items: center; gap: 0.8rem; padding: 1.2rem; border-radius: 1.4rem; background: #fff; border: 1px solid #EEF0F3; cursor: pointer; text-align: left; color: inherit; box-shadow: 0 1px 2px rgba(15,23,42,0.04); transition: border-color 0.15s, transform 0.15s, box-shadow 0.15s; }
.om__card:hover { border-color: #FCD34D; transform: translateY(-3px); box-shadow: 0 14px 30px -18px rgba(245,158,11,0.4); }
.om__avatar { width: 2.7rem; height: 2.7rem; border-radius: 50%; background: linear-gradient(135deg, #FBBF24, #F59E0B); color: #fff; display: flex; align-items: center; justify-content: center; font-weight: 800; flex-shrink: 0; box-shadow: 0 4px 12px -3px rgba(245,158,11,0.5); }
.om__avatar--lg { width: 3.6rem; height: 3.6rem; font-size: 1.35rem; }
.om__info { flex: 1; min-width: 0; }
.om__name { font-weight: 700; font-size: 0.9rem; color: #1E293B; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.om__email { font-size: 0.72rem; color: #94A3B8; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.om__mini { display: flex; gap: 0.9rem; }
.om__mini-item { text-align: center; }
.om__mini-item strong { display: block; font-size: 1.05rem; color: #0F172A; }
.om__mini-item span { font-size: 0.58rem; color: #94A3B8; text-transform: uppercase; font-weight: 600; }
.om__pill { font-size: 0.6rem; font-weight: 800; padding: 0.22rem 0.55rem; border-radius: 999px; text-transform: uppercase; }
.om__pill--ok { background: #D1FAE5; color: #059669; }
.om__pill--off { background: #F1F5F9; color: #94A3B8; }

.om__drawer-wrap { position: fixed; inset: 0; background: rgba(15,23,42,0.45); backdrop-filter: blur(2px); z-index: 70; display: flex; justify-content: flex-end; }
.om__drawer { width: min(500px, 100%); height: 100%; background: #F8FAFC; border-left: 1px solid #EEF0F3; padding: 1.6rem; overflow-y: auto; position: relative; box-shadow: -20px 0 50px -20px rgba(15,23,42,0.3); }
.om__drawer-close { position: absolute; top: 1rem; right: 1rem; background: #fff; border: 1px solid #EEF0F3; border-radius: 0.5rem; padding: 0.3rem; color: #64748B; cursor: pointer; }
.om__drawer-head { display: flex; gap: 1rem; align-items: center; margin: 0.25rem 0 1.5rem; }
.om__drawer-name { font-size: 1.2rem; font-weight: 800; color: #0F172A; }
.om__drawer-email { font-size: 0.8rem; color: #64748B; }
.om__drawer-meta { font-size: 0.72rem; color: #94A3B8; margin-top: 0.35rem; }
.om__role-tag { padding: 0.1rem 0.45rem; border-radius: 999px; font-weight: 700; }
.om__role-tag--mentor { background: #EEF2FF; color: #4F46E5; }
.om__role-tag--advisor { background: #D1FAE5; color: #059669; }
.om__role-tag--member { background: #F1F5F9; color: #64748B; }

.om__section { margin-bottom: 1.3rem; background: #fff; border: 1px solid #EEF0F3; border-radius: 0.9rem; padding: 1rem 1.1rem; }
.om__section-title { display: flex; align-items: center; gap: 0.4rem; font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 700; color: #94A3B8; margin: 0 0 0.7rem; }
.om__roles { display: flex; gap: 0.4rem; }
.om__role-btn { flex: 1; padding: 0.55rem; border-radius: 0.55rem; border: 1px solid #EEF0F3; background: #F8FAFC; color: #475569; font-size: 0.78rem; font-weight: 600; cursor: pointer; transition: all 0.15s; }
.om__role-btn:hover { border-color: #CBD5E1; }
.om__role-btn--active { background: linear-gradient(135deg, #FBBF24, #F59E0B); color: #fff; border: none; box-shadow: 0 4px 12px -3px rgba(245,158,11,0.5); }
.om__funnel { display: flex; flex-wrap: wrap; gap: 0.4rem; }
.om__funnel-chip { background: #F1F5F9; border-radius: 0.5rem; padding: 0.3rem 0.6rem; font-size: 0.72rem; color: #475569; }
.om__funnel-chip strong { color: #0F172A; }
.om__list { display: flex; flex-direction: column; gap: 0.4rem; }
.om__list-row { display: flex; align-items: center; justify-content: space-between; gap: 0.5rem; padding: 0.55rem 0.75rem; border-radius: 0.6rem; background: #F8FAFC; border: 1px solid #F1F5F9; }
.om__list-title { font-size: 0.82rem; font-weight: 600; color: #334155; }
.om__list-sub { font-size: 0.7rem; color: #94A3B8; }
.om__status { font-size: 0.62rem; font-weight: 700; padding: 0.18rem 0.5rem; border-radius: 999px; background: #EEF2FF; color: #4F46E5; }
.om__muted { color: #94A3B8; font-size: 0.8rem; }
.om__remove { display: flex; align-items: center; gap: 0.4rem; justify-content: center; width: 100%; padding: 0.75rem; border-radius: 0.7rem; border: 1px solid #FECACA; background: #FEF2F2; color: #DC2626; font-weight: 700; font-size: 0.82rem; cursor: pointer; margin-top: 0.5rem; transition: background 0.15s; }
.om__remove:hover { background: #FEE2E2; }

.om-drawer-enter-active, .om-drawer-leave-active { transition: opacity 0.25s; }
.om-drawer-enter-active .om__drawer, .om-drawer-leave-active .om__drawer { transition: transform 0.25s ease; }
.om-drawer-enter-from, .om-drawer-leave-to { opacity: 0; }
.om-drawer-enter-from .om__drawer, .om-drawer-leave-to .om__drawer { transform: translateX(100%); }
</style>
