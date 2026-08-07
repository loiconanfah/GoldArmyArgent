<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { authFetch } from '@/utils/auth'
import {
  CheckBadgeIcon, UsersIcon, ExclamationTriangleIcon, CheckIcon,
  ArrowTopRightOnSquareIcon, SparklesIcon
} from '@heroicons/vue/24/outline'

const { t } = useI18n()
const route = useRoute()
const loading = ref(true)
const billing = ref(null)
const interval = ref('annual')
const working = ref('')

const isActive = computed(() => billing.value?.billing_status === 'active')
const plans = computed(() => (billing.value?.plans || []).filter(p => p.key !== 'free' && p.key !== 'enterprise'))
const currency = computed(() => billing.value?.currency || 'CAD')

function priceFor(p) { return interval.value === 'annual' ? p.annual : p.monthly }
function monthlyEq(p) { return Math.round(p.annual / 12) }
function isRecommended(p) { return billing.value?.recommended_plan === p.key }
function isCurrent(p) { return billing.value?.current_plan === p.key && isActive.value }

async function load() {
  loading.value = true
  try {
    const res = await authFetch('/api/org/billing')
    const json = await res.safeJson()
    if (json?.status === 'success') billing.value = json.data
  } catch (e) {} finally { loading.value = false }
}
async function subscribe(planKey) {
  working.value = planKey
  try {
    const res = await authFetch('/api/org/billing/checkout', { method: 'POST', body: JSON.stringify({ plan: planKey, interval: interval.value }) })
    const json = await res.safeJson()
    if (json?.url) window.location.href = json.url
    else alert(json?.detail || t('common.error'))
  } catch (e) { alert(t('common.error')) } finally { working.value = '' }
}
async function manage() {
  working.value = 'manage'
  try {
    const res = await authFetch('/api/org/billing/portal', { method: 'POST' })
    const json = await res.safeJson()
    if (json?.url) window.location.href = json.url
    else alert(json?.detail || t('common.error'))
  } catch (e) {} finally { working.value = '' }
}

onMounted(load)
</script>

<template>
  <div class="ob">
    <header class="ob__head">
      <div>
        <h1 class="ob__title">{{ t('org.nav.billing') }}</h1>
        <p class="ob__sub">{{ t('org.billing.sub2') }}</p>
      </div>
      <button v-if="billing?.has_subscription" class="ob__manage" @click="manage" :disabled="working==='manage'">
        <ArrowTopRightOnSquareIcon class="w-4 h-4" /> {{ t('org.billing.manage') }}
      </button>
    </header>

    <div v-if="route.query.status === 'success'" class="ob__banner ob__banner--ok">
      <CheckBadgeIcon class="w-5 h-5" /> {{ t('org.billing.checkout_success') }}
    </div>

    <div v-if="loading" class="ob__loading">{{ t('common.loading') }}…</div>

    <template v-else>
      <!-- Status bar -->
      <div class="ob__status">
        <div class="ob__status-item">
          <UsersIcon class="ob__status-ic" />
          <div><b>{{ billing?.active_members ?? 0 }}</b><span>{{ t('org.billing.active_members') }}</span></div>
        </div>
        <div class="ob__status-item">
          <SparklesIcon class="ob__status-ic ob__status-ic--gold" />
          <div><b>{{ t('org.plans.' + (billing?.current_plan || (billing?.recommended_plan) || 'free')) }}</b><span>{{ billing?.current_plan ? t('org.billing.current') : t('org.billing.recommended') }}</span></div>
        </div>
        <div class="ob__status-badge" :class="isActive ? 'ob__status-badge--ok' : 'ob__status-badge--off'">
          <span class="ob__dot"></span> {{ isActive ? t('org.billing.status_active') : t('org.billing.status_inactive') }}
        </div>
      </div>

      <div v-if="billing?.over_cap" class="ob__banner ob__banner--warn">
        <ExclamationTriangleIcon class="w-5 h-5" /> {{ t('org.billing.over_cap') }}
      </div>

      <!-- Interval toggle -->
      <div class="ob__toggle-row">
        <div class="ob__toggle">
          <button :class="['ob__toggle-btn', { 'ob__toggle-btn--on': interval==='monthly' }]" @click="interval='monthly'">{{ t('org.billing.monthly') }}</button>
          <button :class="['ob__toggle-btn', { 'ob__toggle-btn--on': interval==='annual' }]" @click="interval='annual'">{{ t('org.billing.annual') }} <span class="ob__save">{{ t('org.billing.save_2m') }}</span></button>
        </div>
      </div>

      <!-- Plans grid -->
      <div class="ob__plans">
        <div v-for="p in plans" :key="p.key" :class="['ob__plan', { 'ob__plan--reco': isRecommended(p), 'ob__plan--current': isCurrent(p) }]">
          <div v-if="isRecommended(p)" class="ob__plan-tag ob__plan-tag--reco">{{ t('org.billing.recommended') }}</div>
          <div v-else-if="isCurrent(p)" class="ob__plan-tag ob__plan-tag--current">{{ t('org.billing.current') }}</div>

          <div class="ob__plan-name">{{ p.name }}</div>
          <div v-if="p.member_gold" class="ob__plan-tier">{{ t('org.billing.members_gold', { gold: p.member_gold }) }}</div>
          <div v-if="p.tagline" class="ob__plan-tagline">{{ t('org.billing.' + p.tagline) }}</div>
          <div class="ob__plan-price">
            <span class="ob__plan-amount">${{ priceFor(p) }}</span>
            <span class="ob__plan-period">/ {{ interval === 'annual' ? t('org.billing.year') : t('org.billing.month') }}</span>
          </div>
          <div v-if="interval === 'annual'" class="ob__plan-eq">≈ ${{ monthlyEq(p) }} / {{ t('org.billing.month') }}</div>

          <ul class="ob__plan-feats">
            <li class="ob__plan-cap-feat"><UsersIcon class="w-3.5 h-3.5" /> {{ t('org.billing.up_to', { n: p.max_active }) }}</li>
            <li v-for="f in p.features" :key="f"><CheckIcon class="w-3.5 h-3.5" /> {{ t('org.billing.' + f) }}</li>
          </ul>

          <button v-if="isCurrent(p)" class="ob__plan-btn ob__plan-btn--current" disabled>{{ t('org.billing.your_plan') }}</button>
          <button v-else class="ob__plan-btn" :class="{ 'ob__plan-btn--primary': isRecommended(p) }" @click="subscribe(p.key)" :disabled="working===p.key">
            {{ working===p.key ? '…' : (billing?.current_plan ? t('org.billing.switch') : t('org.billing.subscribe')) }}
          </button>
        </div>

        <!-- Enterprise -->
        <div class="ob__plan ob__plan--ent">
          <div class="ob__plan-name">Enterprise</div>
          <div class="ob__plan-cap">{{ t('org.billing.ent_cap') }}</div>
          <div class="ob__plan-price"><span class="ob__plan-amount ob__plan-amount--sm">{{ t('org.billing.custom') }}</span></div>
          <ul class="ob__plan-feats">
            <li><CheckIcon class="w-3.5 h-3.5" /> {{ t('org.billing.ent_1') }}</li>
            <li><CheckIcon class="w-3.5 h-3.5" /> {{ t('org.billing.ent_2') }}</li>
            <li><CheckIcon class="w-3.5 h-3.5" /> {{ t('org.billing.ent_3') }}</li>
          </ul>
          <a href="mailto:sales@goldarmyai.com" class="ob__plan-btn">{{ t('org.billing.contact') }}</a>
        </div>
      </div>

      <p class="ob__foot">{{ t('org.billing.foot') }}</p>
    </template>
  </div>
</template>

<style scoped>
.ob { max-width: 1180px; margin: 0 auto; color: #101828; }
.ob__head { display: flex; align-items: flex-end; justify-content: space-between; gap: 1rem; margin-bottom: 1.4rem; flex-wrap: wrap; }
.ob__title { font-size: 1.9rem; font-weight: 800; margin: 0; letter-spacing: -0.03em; }
.ob__sub { color: #667085; font-size: 0.92rem; margin: 0.3rem 0 0; }
.ob__manage { display: inline-flex; align-items: center; gap: 0.4rem; padding: 0.65rem 1.1rem; border-radius: 999px; background: #101828; color: #fff; border: none; font-weight: 700; font-size: 0.82rem; cursor: pointer; }
.ob__loading { padding: 4rem; text-align: center; color: #98A2B3; }
.ob__banner { display: flex; align-items: center; gap: 0.5rem; padding: 0.85rem 1.1rem; border-radius: 1rem; font-weight: 600; font-size: 0.85rem; margin-bottom: 1.1rem; }
.ob__banner--ok { background: #D1FAE5; color: #059669; border: 1px solid #A7F3D0; }
.ob__banner--warn { background: #FEF3C7; color: #B45309; border: 1px solid #FDE68A; }

.ob__status { display: flex; align-items: center; gap: 1rem; background: #fff; border: 1px solid #EEF0F3; border-radius: 1.4rem; padding: 1.1rem 1.4rem; margin-bottom: 1.3rem; box-shadow: 0 1px 2px rgba(16,24,40,0.03); flex-wrap: wrap; }
.ob__status-item { display: flex; align-items: center; gap: 0.7rem; }
.ob__status-ic { width: 2.3rem; height: 2.3rem; padding: 0.5rem; border-radius: 0.7rem; color: #4F46E5; background: #EEF2FF; }
.ob__status-ic--gold { color: #D97706; background: #FEF3C7; }
.ob__status-item b { font-size: 1.3rem; font-weight: 800; display: block; line-height: 1; }
.ob__status-item span { font-size: 0.72rem; color: #98A2B3; text-transform: uppercase; font-weight: 600; }
.ob__status-badge { margin-left: auto; display: inline-flex; align-items: center; gap: 0.4rem; font-size: 0.72rem; font-weight: 800; text-transform: uppercase; padding: 0.3rem 0.7rem; border-radius: 999px; }
.ob__status-badge--ok { background: #D1FAE5; color: #059669; }
.ob__status-badge--off { background: #F1F3F6; color: #667085; }
.ob__dot { width: 0.5rem; height: 0.5rem; border-radius: 50%; background: currentColor; }

.ob__toggle-row { display: flex; justify-content: center; margin-bottom: 1.3rem; }
.ob__toggle { display: inline-flex; background: #F1F3F6; border-radius: 999px; padding: 0.25rem; }
.ob__toggle-btn { display: inline-flex; align-items: center; gap: 0.4rem; padding: 0.5rem 1.1rem; border-radius: 999px; border: none; background: none; color: #667085; font-size: 0.82rem; font-weight: 700; cursor: pointer; }
.ob__toggle-btn--on { background: #fff; color: #101828; box-shadow: 0 1px 3px rgba(16,24,40,0.1); }
.ob__save { font-size: 0.62rem; font-weight: 800; color: #059669; background: #D1FAE5; padding: 0.1rem 0.4rem; border-radius: 999px; }

.ob__plans { display: grid; grid-template-columns: repeat(auto-fit, minmax(230px, 1fr)); gap: 1rem; }
.ob__plan { position: relative; background: #fff; border: 1px solid #EEF0F3; border-radius: 1.5rem; padding: 1.5rem; box-shadow: 0 1px 2px rgba(16,24,40,0.03); display: flex; flex-direction: column; }
.ob__plan--reco { border-color: #F59E0B; box-shadow: 0 16px 34px -18px rgba(245,158,11,0.5); }
.ob__plan--current { border-color: #10B981; }
.ob__plan--ent { background: linear-gradient(160deg, #F9FAFB, #fff); }
.ob__plan-tag { position: absolute; top: -0.7rem; left: 1.5rem; font-size: 0.62rem; font-weight: 800; text-transform: uppercase; padding: 0.25rem 0.7rem; border-radius: 999px; }
.ob__plan-tag--reco { background: linear-gradient(135deg, #FBBF24, #F59E0B); color: #fff; }
.ob__plan-tag--current { background: #10B981; color: #fff; }
.ob__plan-name { font-size: 1.2rem; font-weight: 800; }
.ob__plan-cap { font-size: 0.76rem; color: #98A2B3; margin-top: 0.2rem; }
.ob__plan-tier { display: inline-block; font-size: 0.62rem; font-weight: 800; text-transform: uppercase; color: #B45309; background: #FEF3C7; padding: 0.15rem 0.5rem; border-radius: 999px; margin-top: 0.5rem; }
.ob__plan-tagline { font-size: 0.78rem; color: #667085; margin-top: 0.4rem; min-height: 2.1rem; }
.ob__plan-cap-feat { font-weight: 700; color: #101828 !important; }
.ob__plan-cap-feat svg { color: #D97706 !important; }
.ob__plan-price { display: flex; align-items: baseline; gap: 0.3rem; margin-top: 1rem; }
.ob__plan-amount { font-size: 2rem; font-weight: 800; color: #101828; letter-spacing: -0.02em; }
.ob__plan-amount--sm { font-size: 1.4rem; }
.ob__plan-period { font-size: 0.82rem; color: #667085; font-weight: 600; }
.ob__plan-eq { font-size: 0.72rem; color: #98A2B3; margin-top: 0.2rem; }
.ob__plan-feats { list-style: none; margin: 1.1rem 0; padding: 0; display: flex; flex-direction: column; gap: 0.55rem; flex: 1; }
.ob__plan-feats li { display: flex; align-items: center; gap: 0.45rem; font-size: 0.8rem; color: #475467; }
.ob__plan-feats svg { color: #10B981; flex-shrink: 0; }
.ob__plan-btn { display: inline-flex; align-items: center; justify-content: center; padding: 0.75rem; border-radius: 0.9rem; border: 1px solid #EEF0F3; background: #F9FAFB; color: #344054; font-weight: 700; font-size: 0.85rem; cursor: pointer; text-decoration: none; text-align: center; }
.ob__plan-btn:hover { border-color: #D0D5DD; }
.ob__plan-btn--primary { background: linear-gradient(135deg, #FBBF24, #F59E0B); color: #fff; border: none; box-shadow: 0 10px 22px -10px rgba(245,158,11,0.7); }
.ob__plan-btn--current { background: #D1FAE5; color: #059669; border: none; cursor: default; }
.ob__foot { text-align: center; font-size: 0.76rem; color: #98A2B3; margin-top: 1.4rem; }
@media (max-width: 560px) { .ob__status-badge { margin-left: 0; } }
</style>
