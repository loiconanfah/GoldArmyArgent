<script setup>
import { ref, onMounted, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { authFetch } from '@/utils/auth'
import { ClipboardDocumentIcon, EnvelopeIcon } from '@heroicons/vue/24/outline'

const { t } = useI18n()
const org = ref(null)
const loading = ref(true)
const form = ref({ name: '', type: 'employability', member_tier: 'ESSENTIAL', seats_limit: 50, contact_email: '' })
const saving = ref(false)
const savedMsg = ref('')

const inviteEmail = ref('')
const inviteSending = ref(false)
const inviteMsg = ref('')
const copied = ref(false)

const orgTypes = ['employability', 'school', 'bootcamp', 'agency', 'coach', 'other']
const joinUrl = computed(() => org.value ? `https://goldarmyai.com/register?org=${org.value.invite_code}` : '')

async function load() {
  loading.value = true
  try {
    const res = await authFetch('/api/org/me')
    const json = await res.safeJson()
    if (json?.status === 'success') {
      org.value = json.data
      form.value = {
        name: json.data.name || '', type: json.data.type || 'employability',
        member_tier: json.data.member_tier || 'ESSENTIAL',
        seats_limit: json.data.seats_limit || 50, contact_email: json.data.contact_email || '',
      }
    }
  } catch (e) {} finally { loading.value = false }
}

async function save() {
  saving.value = true; savedMsg.value = ''
  try {
    const res = await authFetch('/api/org/settings', { method: 'PUT', body: JSON.stringify(form.value) })
    const json = await res.safeJson()
    if (res.ok && json?.status === 'success') { savedMsg.value = t('org.settings.saved'); if (json.data) org.value = json.data }
    else savedMsg.value = json?.detail || t('common.error')
  } catch (e) { savedMsg.value = t('common.error') }
  finally { saving.value = false; setTimeout(() => savedMsg.value = '', 3000) }
}

function copyLink() { if (joinUrl.value) { navigator.clipboard?.writeText(joinUrl.value); copied.value = true; setTimeout(() => copied.value = false, 2000) } }

async function sendInvite() {
  inviteMsg.value = ''
  if (!inviteEmail.value.includes('@')) { inviteMsg.value = t('org.invite.invalid_email'); return }
  inviteSending.value = true
  try {
    const res = await authFetch('/api/org/invite', { method: 'POST', body: JSON.stringify({ email: inviteEmail.value }) })
    const json = await res.safeJson()
    if (res.ok && json?.status === 'success') { inviteMsg.value = t('org.invite.sent', { email: inviteEmail.value }); inviteEmail.value = '' }
    else inviteMsg.value = json?.detail || t('org.invite.error')
  } catch (e) { inviteMsg.value = t('org.invite.error') }
  finally { inviteSending.value = false }
}

onMounted(load)
</script>

<template>
  <div class="os">
    <header class="os__head">
      <h1 class="os__title">{{ t('org.tabs.settings') }}</h1>
    </header>

    <div v-if="loading" class="os__loading">{{ t('common.loading') }}…</div>

    <div v-else class="os__cols">
      <!-- Invite -->
      <section class="os__card">
        <h2 class="os__card-title">{{ t('org.invite.title') }}</h2>
        <p class="os__desc">{{ t('org.invite.desc') }}</p>
        <div class="os__seats">{{ t('org.invite.seats', { used: org?.seats_used ?? '—', total: org?.seats_limit ?? 0 }) }}</div>

        <label class="os__label">{{ t('org.invite.link_label') }}</label>
        <div class="os__row">
          <input :value="joinUrl" readonly class="os__input os__input--mono" />
          <button class="os__btn" @click="copyLink"><ClipboardDocumentIcon class="w-4 h-4" /> {{ copied ? t('org.invite.copied') : t('org.invite.copy') }}</button>
        </div>
        <div class="os__code">{{ t('org.invite.code_label') }} <strong>{{ org?.invite_code }}</strong></div>

        <label class="os__label mt">{{ t('org.invite.email_label') }}</label>
        <div class="os__row">
          <input v-model="inviteEmail" type="email" :placeholder="t('org.invite.email_placeholder')" class="os__input" />
          <button class="os__btn os__btn--primary" @click="sendInvite" :disabled="inviteSending"><EnvelopeIcon class="w-4 h-4" /> {{ inviteSending ? t('org.invite.sending') : t('org.invite.send') }}</button>
        </div>
        <p v-if="inviteMsg" class="os__msg">{{ inviteMsg }}</p>
      </section>

      <!-- Settings -->
      <section class="os__card">
        <h2 class="os__card-title">{{ t('org.settings.title') }}</h2>
        <label class="os__label">{{ t('org.settings.name') }}</label>
        <input v-model="form.name" class="os__input os__input--full" />
        <label class="os__label mt">{{ t('org.settings.type') }}</label>
        <select v-model="form.type" class="os__input os__input--full">
          <option v-for="ot in orgTypes" :key="ot" :value="ot">{{ t('org.types.' + ot) }}</option>
        </select>
        <label class="os__label mt">{{ t('org.settings.member_tier') }}</label>
        <select v-model="form.member_tier" class="os__input os__input--full">
          <option value="ESSENTIAL">ESSENTIAL</option><option value="PRO">PRO</option><option value="FREE">FREE</option>
        </select>
        <p class="os__hint">{{ t('org.settings.member_tier_hint') }}</p>
        <label class="os__label mt">{{ t('org.settings.seats') }}</label>
        <input v-model.number="form.seats_limit" type="number" min="1" class="os__input os__input--full" />
        <label class="os__label mt">{{ t('org.settings.contact_email') }}</label>
        <input v-model="form.contact_email" type="email" class="os__input os__input--full" />
        <button class="os__btn os__btn--primary os__btn--block mt" @click="save" :disabled="saving">{{ saving ? t('common.saving') : t('org.settings.save') }}</button>
        <p v-if="savedMsg" class="os__msg">{{ savedMsg }}</p>
      </section>
    </div>
  </div>
</template>

<style scoped>
.os { max-width: 1000px; margin: 0 auto; color: #1E293B; }
.os__head { margin-bottom: 1.5rem; }
.os__title { font-size: 1.7rem; font-weight: 800; margin: 0; letter-spacing: -0.02em; }
.os__loading { padding: 3rem; text-align: center; color: #94A3B8; }
.os__cols { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; align-items: start; }
.os__card { background: #fff; border: 1px solid #E2E8F0; border-radius: 1.1rem; padding: 1.5rem; box-shadow: 0 1px 2px rgba(15,23,42,0.04); }
.os__card-title { font-size: 1.02rem; font-weight: 800; color: #0F172A; margin: 0 0 0.35rem; }
.os__desc { font-size: 0.82rem; color: #64748B; margin: 0 0 1rem; }
.os__seats { font-size: 0.78rem; font-weight: 700; color: #D97706; background: #FEF3C7; display: inline-block; padding: 0.3rem 0.7rem; border-radius: 999px; margin-bottom: 1rem; }
.os__label { display: block; font-size: 0.68rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; color: #94A3B8; margin-bottom: 0.35rem; }
.os__label.mt { margin-top: 0.9rem; }
.os__row { display: flex; gap: 0.5rem; flex-wrap: wrap; }
.os__input { flex: 1; min-width: 160px; padding: 0.7rem 0.85rem; border-radius: 0.6rem; background: #F8FAFC; border: 1px solid #E2E8F0; color: #1E293B; font-size: 0.85rem; outline: none; }
.os__input:focus { border-color: #F59E0B; box-shadow: 0 0 0 3px rgba(245,158,11,0.12); background: #fff; }
.os__input--mono { font-family: monospace; font-size: 0.76rem; }
.os__input--full { width: 100%; flex: none; }
.os__code { font-size: 0.78rem; color: #64748B; margin-top: 0.6rem; }
.os__code strong { font-family: monospace; letter-spacing: 0.1em; color: #D97706; }
.os__btn { display: inline-flex; align-items: center; gap: 0.4rem; padding: 0.7rem 1rem; border-radius: 0.6rem; border: 1px solid #E2E8F0; background: #fff; color: #334155; font-size: 0.8rem; font-weight: 700; cursor: pointer; white-space: nowrap; transition: all 0.15s; }
.os__btn:hover { border-color: #CBD5E1; }
.os__btn--primary { background: linear-gradient(135deg, #FBBF24, #F59E0B); color: #fff; border: none; box-shadow: 0 6px 16px -6px rgba(245,158,11,0.6); }
.os__btn--primary:hover { border: none; }
.os__btn--primary:disabled { opacity: 0.6; cursor: not-allowed; }
.os__btn--block { width: 100%; justify-content: center; }
.os__msg { font-size: 0.8rem; font-weight: 600; color: #059669; margin-top: 0.7rem; }
.os__hint { font-size: 0.7rem; color: #94A3B8; margin: 0.4rem 0 0; }
@media (max-width: 860px) { .os__cols { grid-template-columns: 1fr; } }
</style>
