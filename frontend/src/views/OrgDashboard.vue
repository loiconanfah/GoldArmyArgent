<script setup>
import { ref, onMounted, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useHead } from '@unhead/vue'
import { authFetch } from '@/utils/auth'
import {
  BuildingOffice2Icon, UsersIcon, DocumentTextIcon, BriefcaseIcon,
  ChartBarIcon, ClipboardDocumentIcon, EnvelopeIcon, TrashIcon,
  Cog6ToothIcon, CheckCircleIcon, ArrowPathIcon
} from '@heroicons/vue/24/outline'

const { t } = useI18n()

const loading = ref(true)
const org = ref(null)
const stats = ref(null)
const members = ref([])
const activeTab = ref('overview') // overview | members | settings

// Invitation
const inviteEmail = ref('')
const inviteSending = ref(false)
const inviteMsg = ref('')
const copied = ref(false)

// Settings form
const form = ref({ name: '', type: 'employability', member_tier: 'ESSENTIAL', seats_limit: 50, contact_email: '' })
const savingSettings = ref(false)
const settingsMsg = ref('')

useHead({ title: computed(() => t('org.dashboard.title') + ' | GoldArmy') })

const orgTypes = ['employability', 'school', 'bootcamp', 'agency', 'coach', 'other']

const joinUrl = computed(() =>
  org.value ? `https://goldarmyai.com/register?org=${org.value.invite_code}` : ''
)
const seatsUsed = computed(() => stats.value?.total_members ?? 0)
const seatsLimit = computed(() => org.value?.seats_limit ?? 0)

async function loadAll() {
  loading.value = true
  try {
    const [oRes, sRes, mRes] = await Promise.all([
      authFetch('/api/org/me'),
      authFetch('/api/org/stats'),
      authFetch('/api/org/members'),
    ])
    const oJson = await oRes.safeJson()
    const sJson = await sRes.safeJson()
    const mJson = await mRes.safeJson()
    if (oJson?.status === 'success') {
      org.value = oJson.data
      form.value = {
        name: oJson.data.name || '',
        type: oJson.data.type || 'employability',
        member_tier: oJson.data.member_tier || 'ESSENTIAL',
        seats_limit: oJson.data.seats_limit || 50,
        contact_email: oJson.data.contact_email || '',
      }
    }
    if (sJson?.status === 'success') stats.value = sJson.data
    if (mJson?.status === 'success') members.value = mJson.data
  } catch (e) {
    // silencieux — l'UI affiche l'état vide
  } finally {
    loading.value = false
  }
}

function copyLink() {
  if (!joinUrl.value) return
  navigator.clipboard?.writeText(joinUrl.value)
  copied.value = true
  setTimeout(() => { copied.value = false }, 2000)
}

async function sendInvite() {
  inviteMsg.value = ''
  if (!inviteEmail.value.includes('@')) { inviteMsg.value = t('org.invite.invalid_email'); return }
  inviteSending.value = true
  try {
    const res = await authFetch('/api/org/invite', {
      method: 'POST',
      body: JSON.stringify({ email: inviteEmail.value })
    })
    const json = await res.safeJson()
    if (res.ok && json?.status === 'success') {
      inviteMsg.value = t('org.invite.sent', { email: inviteEmail.value })
      inviteEmail.value = ''
    } else {
      inviteMsg.value = json?.detail || t('org.invite.error')
    }
  } catch (e) {
    inviteMsg.value = t('org.invite.error')
  } finally {
    inviteSending.value = false
  }
}

async function removeMember(m) {
  if (!confirm(t('org.members.remove_confirm', { name: m.full_name || m.email }))) return
  try {
    const res = await authFetch(`/api/org/members/${m.id}`, { method: 'DELETE' })
    if (res.ok) {
      members.value = members.value.filter(x => x.id !== m.id)
      await refreshStats()
    }
  } catch (e) {}
}

async function refreshStats() {
  const sRes = await authFetch('/api/org/stats')
  const sJson = await sRes.safeJson()
  if (sJson?.status === 'success') stats.value = sJson.data
}

async function saveSettings() {
  savingSettings.value = true
  settingsMsg.value = ''
  try {
    const res = await authFetch('/api/org/settings', {
      method: 'PUT',
      body: JSON.stringify(form.value)
    })
    const json = await res.safeJson()
    if (res.ok && json?.status === 'success') {
      settingsMsg.value = t('org.settings.saved')
      if (json.data) org.value = json.data
    } else {
      settingsMsg.value = json?.detail || t('common.error')
    }
  } catch (e) {
    settingsMsg.value = t('common.error')
  } finally {
    savingSettings.value = false
    setTimeout(() => { settingsMsg.value = '' }, 3000)
  }
}

function fmtDate(d) {
  if (!d) return '—'
  try { return new Date(d).toLocaleDateString() } catch { return '—' }
}

onMounted(loadAll)
</script>

<template>
  <div class="org">
    <!-- Header -->
    <header class="org__header">
      <div class="org__title-row">
        <div class="org__icon"><BuildingOffice2Icon class="w-6 h-6" /></div>
        <div>
          <h1 class="org__title">{{ org?.name || t('org.dashboard.title') }}</h1>
          <p class="org__subtitle">{{ t('org.dashboard.subtitle') }}</p>
        </div>
      </div>
      <button class="org__refresh" @click="loadAll" :disabled="loading">
        <ArrowPathIcon :class="['w-4 h-4', { 'org__spin': loading }]" /> {{ t('common.refresh') }}
      </button>
    </header>

    <!-- Tabs -->
    <nav class="org__tabs">
      <button :class="['org__tab', { 'org__tab--active': activeTab === 'overview' }]" @click="activeTab = 'overview'">
        <ChartBarIcon class="w-4 h-4" /> {{ t('org.tabs.overview') }}
      </button>
      <button :class="['org__tab', { 'org__tab--active': activeTab === 'members' }]" @click="activeTab = 'members'">
        <UsersIcon class="w-4 h-4" /> {{ t('org.tabs.members') }} <span class="org__badge">{{ members.length }}</span>
      </button>
      <button :class="['org__tab', { 'org__tab--active': activeTab === 'settings' }]" @click="activeTab = 'settings'">
        <Cog6ToothIcon class="w-4 h-4" /> {{ t('org.tabs.settings') }}
      </button>
    </nav>

    <div v-if="loading" class="org__loading">{{ t('common.loading') }}…</div>

    <!-- OVERVIEW -->
    <section v-else-if="activeTab === 'overview'" class="org__section">
      <div class="org__stats">
        <div class="org__stat">
          <UsersIcon class="org__stat-icon" />
          <div><div class="org__stat-value">{{ stats?.total_members ?? 0 }}</div><div class="org__stat-label">{{ t('org.stats.members') }}</div></div>
        </div>
        <div class="org__stat">
          <CheckCircleIcon class="org__stat-icon" />
          <div><div class="org__stat-value">{{ stats?.active_members ?? 0 }}</div><div class="org__stat-label">{{ t('org.stats.active') }}</div></div>
        </div>
        <div class="org__stat">
          <DocumentTextIcon class="org__stat-icon" />
          <div><div class="org__stat-value">{{ stats?.with_cv ?? 0 }}</div><div class="org__stat-label">{{ t('org.stats.with_cv') }}</div></div>
        </div>
        <div class="org__stat">
          <BriefcaseIcon class="org__stat-icon" />
          <div><div class="org__stat-value">{{ stats?.total_applications ?? 0 }}</div><div class="org__stat-label">{{ t('org.stats.applications') }}</div></div>
        </div>
        <div class="org__stat">
          <ChartBarIcon class="org__stat-icon" />
          <div><div class="org__stat-value">{{ stats?.total_interviews ?? 0 }}</div><div class="org__stat-label">{{ t('org.stats.interviews') }}</div></div>
        </div>
        <div class="org__stat">
          <ChartBarIcon class="org__stat-icon" />
          <div><div class="org__stat-value">{{ stats?.avg_applications ?? 0 }}</div><div class="org__stat-label">{{ t('org.stats.avg') }}</div></div>
        </div>
      </div>

      <!-- Invite panel -->
      <div class="org__card">
        <h2 class="org__card-title">{{ t('org.invite.title') }}</h2>
        <p class="org__card-desc">{{ t('org.invite.desc') }}</p>

        <div class="org__seats">
          {{ t('org.invite.seats', { used: seatsUsed, total: seatsLimit }) }}
        </div>

        <label class="org__label">{{ t('org.invite.link_label') }}</label>
        <div class="org__invite-link">
          <input :value="joinUrl" readonly class="org__input org__input--mono" />
          <button class="org__btn" @click="copyLink">
            <ClipboardDocumentIcon class="w-4 h-4" /> {{ copied ? t('org.invite.copied') : t('org.invite.copy') }}
          </button>
        </div>
        <div class="org__code">{{ t('org.invite.code_label') }} <strong>{{ org?.invite_code }}</strong></div>

        <label class="org__label mt-4">{{ t('org.invite.email_label') }}</label>
        <div class="org__invite-link">
          <input v-model="inviteEmail" type="email" :placeholder="t('org.invite.email_placeholder')" class="org__input" />
          <button class="org__btn org__btn--primary" @click="sendInvite" :disabled="inviteSending">
            <EnvelopeIcon class="w-4 h-4" /> {{ inviteSending ? t('org.invite.sending') : t('org.invite.send') }}
          </button>
        </div>
        <p v-if="inviteMsg" class="org__msg">{{ inviteMsg }}</p>
      </div>
    </section>

    <!-- MEMBERS -->
    <section v-else-if="activeTab === 'members'" class="org__section">
      <div class="org__card">
        <h2 class="org__card-title">{{ t('org.members.title') }}</h2>
        <div v-if="members.length === 0" class="org__empty">{{ t('org.members.empty') }}</div>
        <div v-else class="org__table-wrap">
          <table class="org__table">
            <thead>
              <tr>
                <th>{{ t('org.members.name') }}</th>
                <th>{{ t('org.members.cv') }}</th>
                <th>{{ t('org.members.applications') }}</th>
                <th>{{ t('org.members.interviews') }}</th>
                <th>{{ t('org.members.last_activity') }}</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="m in members" :key="m.id">
                <td>
                  <div class="org__member-name">{{ m.full_name || m.email.split('@')[0] }}</div>
                  <div class="org__member-email">{{ m.email }}</div>
                </td>
                <td>
                  <span :class="['org__pill', m.has_cv ? 'org__pill--ok' : 'org__pill--off']">
                    {{ m.has_cv ? t('org.members.cv_yes') : t('org.members.cv_no') }}
                  </span>
                </td>
                <td><strong>{{ m.applications }}</strong> <span class="org__muted">({{ m.applied }} {{ t('org.members.sent') }})</span></td>
                <td>{{ m.interviews }}</td>
                <td class="org__muted">{{ fmtDate(m.last_activity) }}</td>
                <td>
                  <button class="org__icon-btn" :title="t('org.members.remove')" @click="removeMember(m)">
                    <TrashIcon class="w-4 h-4" />
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </section>

    <!-- SETTINGS -->
    <section v-else-if="activeTab === 'settings'" class="org__section">
      <div class="org__card org__card--narrow">
        <h2 class="org__card-title">{{ t('org.settings.title') }}</h2>

        <label class="org__label">{{ t('org.settings.name') }}</label>
        <input v-model="form.name" class="org__input org__input--full" />

        <label class="org__label mt-3">{{ t('org.settings.type') }}</label>
        <select v-model="form.type" class="org__input org__input--full">
          <option v-for="ot in orgTypes" :key="ot" :value="ot">{{ t('org.types.' + ot) }}</option>
        </select>

        <label class="org__label mt-3">{{ t('org.settings.member_tier') }}</label>
        <select v-model="form.member_tier" class="org__input org__input--full">
          <option value="ESSENTIAL">ESSENTIAL</option>
          <option value="PRO">PRO</option>
          <option value="FREE">FREE</option>
        </select>
        <p class="org__hint">{{ t('org.settings.member_tier_hint') }}</p>

        <label class="org__label mt-3">{{ t('org.settings.seats') }}</label>
        <input v-model.number="form.seats_limit" type="number" min="1" class="org__input org__input--full" />

        <label class="org__label mt-3">{{ t('org.settings.contact_email') }}</label>
        <input v-model="form.contact_email" type="email" class="org__input org__input--full" />

        <button class="org__btn org__btn--primary org__btn--block mt-4" @click="saveSettings" :disabled="savingSettings">
          {{ savingSettings ? t('common.saving') : t('org.settings.save') }}
        </button>
        <p v-if="settingsMsg" class="org__msg">{{ settingsMsg }}</p>
      </div>
    </section>
  </div>
</template>

<style scoped>
.org { max-width: 1100px; margin: 0 auto; padding: 1.5rem; }
.org__header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 1.5rem; gap: 1rem; flex-wrap: wrap; }
.org__title-row { display: flex; align-items: center; gap: 0.9rem; }
.org__icon { width: 3rem; height: 3rem; border-radius: 0.9rem; background: linear-gradient(135deg, #ff9a5c, #ff6f00); color: #1a1a22; display: flex; align-items: center; justify-content: center; }
.org__title { font-size: 1.5rem; font-weight: 800; margin: 0; }
.org__subtitle { font-size: 0.85rem; opacity: 0.6; margin: 0.15rem 0 0; }
.org__refresh { display: inline-flex; align-items: center; gap: 0.4rem; padding: 0.5rem 0.9rem; border-radius: 0.6rem; border: 1px solid rgba(128,128,128,0.25); background: transparent; font-size: 0.8rem; font-weight: 600; cursor: pointer; color: inherit; }
.org__spin { animation: org-spin 0.8s linear infinite; }
@keyframes org-spin { to { transform: rotate(360deg); } }

.org__tabs { display: flex; gap: 0.4rem; border-bottom: 1px solid rgba(128,128,128,0.2); margin-bottom: 1.5rem; flex-wrap: wrap; }
.org__tab { display: inline-flex; align-items: center; gap: 0.4rem; padding: 0.7rem 1rem; border: none; background: none; font-size: 0.85rem; font-weight: 600; color: inherit; opacity: 0.55; cursor: pointer; border-bottom: 2px solid transparent; margin-bottom: -1px; }
.org__tab--active { opacity: 1; border-bottom-color: #ff6f00; color: #ff6f00; }
.org__badge { background: rgba(255,111,0,0.15); color: #ff6f00; border-radius: 999px; padding: 0.05rem 0.5rem; font-size: 0.7rem; font-weight: 800; }

.org__loading { padding: 3rem; text-align: center; opacity: 0.6; }
.org__section { display: flex; flex-direction: column; gap: 1.25rem; }

.org__stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 0.9rem; }
.org__stat { display: flex; align-items: center; gap: 0.75rem; padding: 1.1rem; border-radius: 0.9rem; border: 1px solid rgba(128,128,128,0.18); background: rgba(128,128,128,0.05); }
.org__stat-icon { width: 1.75rem; height: 1.75rem; color: #ff6f00; flex-shrink: 0; }
.org__stat-value { font-size: 1.5rem; font-weight: 800; line-height: 1; }
.org__stat-label { font-size: 0.72rem; opacity: 0.6; margin-top: 0.2rem; text-transform: uppercase; letter-spacing: 0.03em; }

.org__card { padding: 1.5rem; border-radius: 1rem; border: 1px solid rgba(128,128,128,0.18); background: rgba(128,128,128,0.04); }
.org__card--narrow { max-width: 520px; }
.org__card-title { font-size: 1.05rem; font-weight: 800; margin: 0 0 0.35rem; }
.org__card-desc { font-size: 0.85rem; opacity: 0.6; margin: 0 0 1rem; }
.org__seats { font-size: 0.8rem; font-weight: 700; color: #ff6f00; margin-bottom: 1rem; }

.org__label { display: block; font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; opacity: 0.6; margin-bottom: 0.4rem; }
.org__invite-link { display: flex; gap: 0.5rem; flex-wrap: wrap; }
.org__input { flex: 1; min-width: 180px; padding: 0.7rem 0.9rem; border-radius: 0.6rem; border: 1px solid rgba(128,128,128,0.25); background: rgba(128,128,128,0.08); color: inherit; font-size: 0.9rem; outline: none; }
.org__input--mono { font-family: monospace; font-size: 0.8rem; }
.org__input--full { width: 100%; flex: none; }
.org__input:focus { border-color: #ff6f00; }
.org__code { font-size: 0.8rem; opacity: 0.7; margin-top: 0.6rem; }
.org__code strong { font-family: monospace; letter-spacing: 0.1em; color: #ff6f00; }

.org__btn { display: inline-flex; align-items: center; gap: 0.4rem; padding: 0.7rem 1rem; border-radius: 0.6rem; border: 1px solid rgba(128,128,128,0.25); background: transparent; color: inherit; font-size: 0.8rem; font-weight: 700; cursor: pointer; white-space: nowrap; }
.org__btn--primary { background: linear-gradient(135deg, #ff9a5c, #ff6f00); color: #1a1a22; border: none; }
.org__btn--primary:disabled { opacity: 0.6; cursor: not-allowed; }
.org__btn--block { width: 100%; justify-content: center; padding: 0.85rem; }
.org__msg { font-size: 0.8rem; font-weight: 600; color: #16a34a; margin-top: 0.7rem; }
.org__hint { font-size: 0.72rem; opacity: 0.55; margin: 0.35rem 0 0; }

.org__table-wrap { overflow-x: auto; }
.org__table { width: 100%; border-collapse: collapse; font-size: 0.85rem; }
.org__table th { text-align: left; padding: 0.6rem 0.75rem; font-size: 0.68rem; text-transform: uppercase; letter-spacing: 0.05em; opacity: 0.55; border-bottom: 1px solid rgba(128,128,128,0.2); }
.org__table td { padding: 0.75rem; border-bottom: 1px solid rgba(128,128,128,0.12); vertical-align: middle; }
.org__member-name { font-weight: 700; }
.org__member-email { font-size: 0.75rem; opacity: 0.55; }
.org__muted { opacity: 0.55; font-size: 0.8rem; }
.org__pill { font-size: 0.68rem; font-weight: 800; padding: 0.2rem 0.55rem; border-radius: 999px; text-transform: uppercase; }
.org__pill--ok { background: rgba(22,163,74,0.15); color: #16a34a; }
.org__pill--off { background: rgba(128,128,128,0.15); opacity: 0.7; }
.org__icon-btn { padding: 0.4rem; border-radius: 0.5rem; border: none; background: transparent; color: #ef4444; cursor: pointer; opacity: 0.7; }
.org__icon-btn:hover { opacity: 1; background: rgba(239,68,68,0.1); }
.org__empty { padding: 2rem; text-align: center; opacity: 0.55; font-size: 0.9rem; }
.mt-3 { margin-top: 0.75rem; } .mt-4 { margin-top: 1rem; }
</style>
