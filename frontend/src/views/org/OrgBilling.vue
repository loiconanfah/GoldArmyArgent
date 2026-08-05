<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { authFetch } from '@/utils/auth'
import { CreditCardIcon, CheckBadgeIcon, UsersIcon, BanknotesIcon, ArrowTopRightOnSquareIcon } from '@heroicons/vue/24/outline'

const { t } = useI18n()
const route = useRoute()
const loading = ref(true)
const billing = ref(null)
const working = ref(false)

const isActive = computed(() => billing.value?.billing_status === 'active')
const statusLabel = computed(() => {
  const s = billing.value?.billing_status
  if (s === 'active') return t('org.billing.status_active')
  if (s === 'canceled') return t('org.billing.status_canceled')
  return t('org.billing.status_inactive')
})

async function load() {
  loading.value = true
  try {
    const res = await authFetch('/api/org/billing')
    const json = await res.safeJson()
    if (json?.status === 'success') billing.value = json.data
  } catch (e) {} finally { loading.value = false }
}

async function subscribe() {
  working.value = true
  try {
    const res = await authFetch('/api/org/billing/checkout', { method: 'POST' })
    const json = await res.safeJson()
    if (json?.url) window.location.href = json.url
    else alert(json?.detail || t('common.error'))
  } catch (e) {} finally { working.value = false }
}

async function manage() {
  working.value = true
  try {
    const res = await authFetch('/api/org/billing/portal', { method: 'POST' })
    const json = await res.safeJson()
    if (json?.url) window.location.href = json.url
    else alert(json?.detail || t('common.error'))
  } catch (e) {} finally { working.value = false }
}

onMounted(load)
</script>

<template>
  <div class="ob">
    <header class="ob__head">
      <h1 class="ob__title">{{ t('org.nav.billing') }}</h1>
      <p class="ob__sub">{{ t('org.billing.sub') }}</p>
    </header>

    <div v-if="route.query.status === 'success'" class="ob__banner ob__banner--ok">
      <CheckBadgeIcon class="w-5 h-5" /> {{ t('org.billing.checkout_success') }}
    </div>

    <div v-if="loading" class="ob__loading">{{ t('common.loading') }}…</div>

    <div v-else class="ob__grid">
      <!-- Cost card -->
      <section class="ob__card ob__card--hero">
        <div class="ob__hero-badge" :class="isActive ? 'ob__hero-badge--ok' : 'ob__hero-badge--off'">
          <span class="ob__dot"></span> {{ statusLabel }}
        </div>
        <div class="ob__price">
          <span class="ob__price-amount">${{ billing?.monthly_total ?? 0 }}</span>
          <span class="ob__price-period">/ {{ t('org.billing.month') }}</span>
        </div>
        <div class="ob__breakdown">
          <span class="ob__seats-num">{{ billing?.billable_seats ?? 0 }}</span>
          {{ t('org.billing.members') }} × ${{ billing?.price_per_seat ?? 1 }}
        </div>
        <p class="ob__note">{{ t('org.billing.admin_excluded') }}</p>

        <button v-if="!isActive" class="ob__btn ob__btn--primary" @click="subscribe" :disabled="working">
          <CreditCardIcon class="w-4 h-4" /> {{ working ? t('common.loading') : t('org.billing.subscribe') }}
        </button>
        <button v-else class="ob__btn ob__btn--manage" @click="manage" :disabled="working">
          <ArrowTopRightOnSquareIcon class="w-4 h-4" /> {{ t('org.billing.manage') }}
        </button>
      </section>

      <!-- Info cards -->
      <div class="ob__side">
        <div class="ob__mini">
          <div class="ob__mini-icon ob__mini-icon--gold"><UsersIcon class="w-5 h-5" /></div>
          <div>
            <div class="ob__mini-val">{{ billing?.billable_seats ?? 0 }}</div>
            <div class="ob__mini-lbl">{{ t('org.billing.billable_seats') }}</div>
          </div>
        </div>
        <div class="ob__mini">
          <div class="ob__mini-icon ob__mini-icon--indigo"><BanknotesIcon class="w-5 h-5" /></div>
          <div>
            <div class="ob__mini-val">${{ billing?.price_per_seat ?? 1 }}</div>
            <div class="ob__mini-lbl">{{ t('org.billing.per_member') }}</div>
          </div>
        </div>
        <div class="ob__how">
          <h3 class="ob__how-title">{{ t('org.billing.how_title') }}</h3>
          <ul class="ob__how-list">
            <li>{{ t('org.billing.how_1') }}</li>
            <li>{{ t('org.billing.how_2') }}</li>
            <li>{{ t('org.billing.how_3') }}</li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.ob { max-width: 1000px; margin: 0 auto; color: #1E293B; }
.ob__head { margin-bottom: 1.5rem; }
.ob__title { font-size: 1.7rem; font-weight: 800; margin: 0; letter-spacing: -0.02em; }
.ob__sub { color: #64748B; font-size: 0.9rem; margin: 0.3rem 0 0; }
.ob__loading { padding: 3rem; text-align: center; color: #94A3B8; }
.ob__banner { display: flex; align-items: center; gap: 0.5rem; padding: 0.8rem 1rem; border-radius: 0.8rem; font-weight: 600; font-size: 0.85rem; margin-bottom: 1.25rem; }
.ob__banner--ok { background: #D1FAE5; color: #059669; border: 1px solid #A7F3D0; }

.ob__grid { display: grid; grid-template-columns: 1.3fr 1fr; gap: 1rem; align-items: start; }
.ob__card { background: #fff; border: 1px solid #EEF0F3; border-radius: 1.2rem; padding: 1.6rem; box-shadow: 0 1px 2px rgba(15,23,42,0.04), 0 12px 32px -22px rgba(15,23,42,0.3); }
.ob__card--hero { position: relative; overflow: hidden; background: linear-gradient(150deg, #FFFBEB 0%, #fff 55%); }
.ob__card--hero::after { content: ''; position: absolute; right: -40px; top: -40px; width: 160px; height: 160px; border-radius: 50%; background: radial-gradient(circle, rgba(245,158,11,0.18), transparent 70%); }
.ob__hero-badge { display: inline-flex; align-items: center; gap: 0.4rem; font-size: 0.72rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.05em; padding: 0.3rem 0.7rem; border-radius: 999px; margin-bottom: 1.2rem; }
.ob__hero-badge--ok { background: #D1FAE5; color: #059669; }
.ob__hero-badge--off { background: #F1F5F9; color: #64748B; }
.ob__dot { width: 0.5rem; height: 0.5rem; border-radius: 50%; background: currentColor; }
.ob__price { display: flex; align-items: baseline; gap: 0.4rem; }
.ob__price-amount { font-size: 3rem; font-weight: 800; line-height: 1; color: #0F172A; letter-spacing: -0.03em; }
.ob__price-period { font-size: 1rem; color: #64748B; font-weight: 600; }
.ob__breakdown { margin-top: 0.6rem; font-size: 0.9rem; color: #475569; }
.ob__seats-num { font-weight: 800; color: #D97706; }
.ob__note { font-size: 0.76rem; color: #94A3B8; margin: 0.4rem 0 1.4rem; }
.ob__btn { display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.85rem 1.4rem; border-radius: 0.7rem; border: none; font-weight: 700; font-size: 0.9rem; cursor: pointer; }
.ob__btn--primary { background: linear-gradient(135deg, #FBBF24, #F59E0B); color: #fff; box-shadow: 0 10px 24px -10px rgba(245,158,11,0.7); }
.ob__btn--manage { background: #0F172A; color: #fff; }
.ob__btn:disabled { opacity: 0.6; cursor: not-allowed; }

.ob__side { display: flex; flex-direction: column; gap: 1rem; }
.ob__mini { display: flex; align-items: center; gap: 0.8rem; background: #fff; border: 1px solid #EEF0F3; border-radius: 1rem; padding: 1rem 1.1rem; box-shadow: 0 1px 2px rgba(15,23,42,0.04); }
.ob__mini-icon { width: 2.4rem; height: 2.4rem; border-radius: 0.7rem; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.ob__mini-icon--gold { background: #FEF3C7; color: #D97706; }
.ob__mini-icon--indigo { background: #EEF2FF; color: #4F46E5; }
.ob__mini-val { font-size: 1.4rem; font-weight: 800; color: #0F172A; line-height: 1; }
.ob__mini-lbl { font-size: 0.72rem; color: #94A3B8; text-transform: uppercase; font-weight: 600; margin-top: 0.2rem; }
.ob__how { background: #F8FAFC; border: 1px solid #F1F5F9; border-radius: 1rem; padding: 1.1rem; }
.ob__how-title { font-size: 0.85rem; font-weight: 700; margin: 0 0 0.6rem; color: #334155; }
.ob__how-list { margin: 0; padding-left: 1.1rem; display: flex; flex-direction: column; gap: 0.4rem; }
.ob__how-list li { font-size: 0.78rem; color: #64748B; line-height: 1.4; }
@media (max-width: 860px) { .ob__grid { grid-template-columns: 1fr; } }
</style>
