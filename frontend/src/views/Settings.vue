<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { authFetch } from '../utils/auth'
import { toastState } from '../store/toastState'
import {
  ArrowLeftIcon,
  CheckIcon,
  StarIcon,
  RocketLaunchIcon,
  ShieldCheckIcon,
  SparklesIcon,
  UserCircleIcon,
  MagnifyingGlassIcon,
  DocumentTextIcon,
  MicrophoneIcon,
  UsersIcon,
  BriefcaseIcon,
  BoltIcon,
  CurrencyDollarIcon,
  ExclamationTriangleIcon,
  BellIcon,
  Cog6ToothIcon,
  CreditCardIcon,
  ArrowDownTrayIcon,
  LockClosedIcon,
  LanguageIcon,
} from '@heroicons/vue/24/outline'

const router = useRouter()
const { t } = useI18n()

// --- State ---
const userTier = ref('FREE')
const goldBalance = ref(null)
const monthlyRefill = { FREE: 100, ESSENTIAL: 200, PRO: 500 }
const profileData = ref({ full_name: '', email: '' })
const usage = ref({})
const isSubscribing = ref(false)

// --- Notifications & Preferences State ---
const notifSniper = ref(true)
const notifFollowup = ref(true)
const notifWeeklyDigest = ref(false)
const notifPushMobile = ref(true)

const ghostbusterAuto = ref(false)
const aiTone = ref('professional')
const aiLanguage = ref('fr')
const isExportingData = ref(false)
const isOpeningPortal = ref(false)

const fetchGhostbusterStatus = async () => {
  try {
    const res = await authFetch('/api/workflows/ghostbuster/status')
    const json = await res.json()
    if (json.status === 'success') {
      ghostbusterAuto.value = json.data?.auto_enabled || false
    }
  } catch(e) {}
}

const toggleGhostbuster = async () => {
  ghostbusterAuto.value = !ghostbusterAuto.value
  try {
    const res = await authFetch('/api/workflows/ghostbuster/toggle', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ enabled: ghostbusterAuto.value })
    })
    const json = await res.json()
    if (res.ok) {
      toastState.addToast(
        ghostbusterAuto.value 
          ? 'Mode Ghostbuster Auto (48h) activé !' 
          : 'Mode Ghostbuster Auto désactivé.', 
        'success'
      )
    }
  } catch(e) {
    toastState.addToast('Modification enregistrée', 'success')
  }
}

const openStripePortal = async () => {
  isOpeningPortal.value = true
  try {
    const res = await authFetch('/api/stripe/create-portal-session', { method: 'POST' })
    const json = await res.json()
    if (json.status === 'success' && json.url) {
      window.location.href = json.url
    } else {
      toastState.addToast(json.detail || 'Portail Stripe non disponible.', 'info')
    }
  } catch(e) {
    toastState.addToast('Gérez vos abonnements via les boutons de forfaits ci-dessus.', 'info')
  } finally {
    isOpeningPortal.value = false
  }
}

const exportDataJSON = async () => {
  isExportingData.value = true
  try {
    const res = await authFetch('/api/profile/export')
    const json = await res.json()
    const blob = new Blob([JSON.stringify(json.data || json, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `GoldArmy_Mes_Donnees_${new Date().toISOString().slice(0, 10)}.json`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
    toastState.addToast('Export RGPD téléchargé avec succès !', 'success')
  } catch(e) {
    toastState.addToast('Erreur lors de l\'exportation des données.', 'error')
  } finally {
    isExportingData.value = false
  }
}

// --- Tier Config (matches subscription.py exactly) ---
const tierConfig = {
  FREE: {
    labelKey: 'settings.tier_free', price: '0€', icon: ShieldCheckIcon, color: 'slate', gold: 100,
    descKey: 'settings.desc_free',
    features: [
      { key: 'sniper_search', lk: 'settings.feat_sniper', icon: MagnifyingGlassIcon },
      { key: 'cv_audit', lk: 'settings.feat_cv_audit', icon: DocumentTextIcon },
      { key: 'hr_interview', lk: 'settings.feat_hr', icon: MicrophoneIcon },
      { key: 'follow_up', lk: 'settings.feat_followup', icon: BoltIcon },
      { key: 'cv_adaptation', lk: 'settings.feat_cv_adapt', icon: DocumentTextIcon },
    ],
    unavailable: ['settings.feat_headhunter', 'settings.feat_address', 'settings.feat_portfolio']
  },
  ESSENTIAL: {
    labelKey: 'settings.tier_essential', price: '9.99€', icon: StarIcon, color: 'amber', gold: 200,
    descKey: 'settings.desc_essential',
    features: [
      { key: 'sniper_search', lk: 'settings.feat_sniper', icon: MagnifyingGlassIcon },
      { key: 'cv_audit', lk: 'settings.feat_cv_audit', icon: DocumentTextIcon },
      { key: 'hr_interview', lk: 'settings.feat_hr', icon: MicrophoneIcon },
      { key: 'headhunter', lk: 'settings.feat_headhunter', icon: UsersIcon },
      { key: 'address_book', lk: 'settings.feat_address', icon: BriefcaseIcon },
      { key: 'follow_up', lk: 'settings.feat_followup', icon: BoltIcon },
      { key: 'cv_adaptation', lk: 'settings.feat_cv_adapt', icon: DocumentTextIcon },
    ],
    unavailable: ['settings.feat_portfolio']
  },
  PRO: {
    labelKey: 'settings.tier_pro', price: '19.99€', icon: RocketLaunchIcon, color: 'indigo', gold: 500,
    descKey: 'settings.desc_pro',
    features: [
      { key: 'sniper_search', lk: 'settings.feat_sniper', icon: MagnifyingGlassIcon },
      { key: 'cv_audit', lk: 'settings.feat_cv_audit', icon: DocumentTextIcon },
      { key: 'hr_interview', lk: 'settings.feat_hr', icon: MicrophoneIcon },
      { key: 'headhunter', lk: 'settings.feat_headhunter', icon: UsersIcon },
      { key: 'address_book', lk: 'settings.feat_address', icon: BriefcaseIcon },
      { key: 'follow_up', lk: 'settings.feat_followup', icon: BoltIcon },
      { key: 'cv_adaptation', lk: 'settings.feat_cv_adapt', icon: DocumentTextIcon },
    ],
    unavailable: []
  }
}

const tierOrder = ['FREE', 'ESSENTIAL', 'PRO']

// --- Fetch ---
const fetchAll = async () => {
  try {
    const [profileRes, usageRes, goldRes] = await Promise.all([
      authFetch('/api/profile'),
      authFetch('/api/profile/usage'),
      authFetch('/api/gold/balance')
    ])
    const profileJson = await profileRes.json()
    const usageJson = await usageRes.json()
    try { const gj = await goldRes.json(); if (gj?.status === 'success') goldBalance.value = gj.data.balance } catch (e) {}

    if (profileJson.status === 'success') {
      const d = profileJson.data
      userTier.value = d.subscription_tier || 'FREE'
      profileData.value = {
        full_name: d.full_name || d.email?.split('@')[0] || 'Utilisateur',
        email: d.email || ''
      }
    }
    if (usageJson.status === 'success') {
      usage.value = usageJson.data.usage || {}
    }
    fetchGhostbusterStatus()
  } catch (e) {
    console.error('Failed to fetch settings data', e)
  }
}

onMounted(fetchAll)

// --- Subscribe ---
const handleSubscribe = async (targetTier) => {
  if (isSubscribing.value) return
  if (targetTier === 'FREE') { router.push('/dashboard'); return }
  if (targetTier === userTier.value || (userTier.value === 'ADMIN' && targetTier === 'PRO')) {
    toastState.addToast('Vous êtes déjà sur ce forfait.', 'info')
    return
  }
  isSubscribing.value = true
  try {
    const res = await authFetch('/api/stripe/create-checkout-session', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ tier: targetTier })
    })
    const json = await res.json()
    if (json.status === 'success' && json.url) {
      window.location.href = json.url
    } else {
      toastState.addToast('Erreur lors de la création de la session Stripe.', 'error')
    }
  } catch (e) {
    toastState.addToast('Erreur de connexion au service de paiement.', 'error')
  } finally {
    isSubscribing.value = false
  }
}

// --- Helpers ---
const isCurrentTier = (tier) => {
  if (tier === 'PRO' && userTier.value === 'ADMIN') return true
  return tier === userTier.value
}

const formatLimit = (val, period) => {
  if (val >= 9999) return '∞'
  return `${val}/${period === 'day' ? 'j' : period === 'month' ? 'mois' : 'total'}`
}

const getUsagePercent = (feat) => {
  const u = usage.value[feat]
  if (!u || u.limit >= 9999) return 0
  return Math.min(100, Math.round((u.current / u.limit) * 100))
}

const tierColorClass = (color) => ({
  amber: 'text-amber-600 bg-amber-50 border-amber-200',
  indigo: 'text-amber-600 bg-amber-50 border-amber-200',
  slate: 'text-slate-700 bg-slate-100 border-slate-200',
}[color])

const tierBorderClass = (tier, color) => isCurrentTier(tier)
  ? (color === 'amber' ? 'border-amber-400 shadow-amber-100 shadow-lg' : color === 'indigo' ? 'border-amber-500 shadow-amber-100 shadow-lg' : 'border-slate-400')
  : 'border-slate-200 hover:border-slate-300'

const tierBtnClass = (tier, color) => {
  if (isCurrentTier(tier)) return 'bg-amber-500 text-white cursor-default shadow-sm'
  if (color === 'amber') return 'bg-amber-500 hover:bg-amber-600 text-white shadow-lg'
  if (color === 'indigo') return 'bg-amber-500 hover:bg-amber-600 text-white shadow-lg'
  return 'bg-slate-100 text-slate-700 hover:bg-slate-200'
}

const tierBtnLabel = (tier) => {
  if (isCurrentTier(tier)) return tier === 'FREE' ? t('settings.btn_current_free') : t('settings.btn_current')
  if (tier === 'FREE') return t('settings.btn_downgrade')
  return tier === 'ESSENTIAL' ? t('settings.btn_essential') : t('settings.btn_pro')
}

const currentConfig = computed(() => tierConfig[userTier.value === 'ADMIN' ? 'PRO' : userTier.value] || tierConfig.FREE)
</script>

<template>
  <div class="min-h-screen bg-[#F8FAFC] font-sans pb-20">

    <!-- Header -->
    <div class="bg-white border-b border-slate-200 sticky top-0 z-10">
      <div class="max-w-6xl mx-auto px-6 lg:px-10 h-16 flex items-center gap-4">
        <button @click="router.push('/dashboard')" class="p-2 hover:bg-slate-100 rounded-xl transition-colors text-slate-500">
          <ArrowLeftIcon class="w-5 h-5" />
        </button>
        <div>
          <h1 class="text-base font-bold text-slate-900">{{ t('settings.title') }}</h1>
          <p class="text-[10px] text-slate-400 font-bold uppercase tracking-widest">{{ t('settings.subtitle') }}</p>
        </div>
        <div class="ml-auto flex items-center gap-2">
          <div class="hidden sm:flex items-center gap-2 px-3 py-1.5 bg-amber-50 rounded-lg border border-amber-200">
            <div class="w-2 h-2 rounded-full bg-amber-500"></div>
            <span class="text-[10px] font-bold text-amber-800 uppercase tracking-widest">
              {{ userTier === 'ADMIN' ? 'Admin GoldArmy' : userTier === 'PRO' ? 'Membre Pro' : userTier === 'ESSENTIAL' ? 'Membre Essentiel' : 'Compte Gratuit' }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <div class="max-w-6xl mx-auto px-6 lg:px-10 py-10 space-y-12">

      <!-- === SOLDE GOLD === -->
      <section>
        <div class="flex items-center gap-3 mb-6">
          <h2 class="text-sm font-bold text-slate-900 uppercase tracking-tight">{{ t('settings.my_gold') }}</h2>
        </div>
        <div class="bg-gradient-to-br from-slate-800 to-slate-900 rounded-2xl shadow-sm p-6 flex flex-col sm:flex-row items-center gap-6">
          <div class="flex items-center gap-4 flex-1">
            <div class="w-14 h-14 rounded-2xl bg-amber-500/20 flex items-center justify-center">
              <BoltIcon class="w-7 h-7 text-amber-400" />
            </div>
            <div>
              <div class="text-3xl font-black text-white leading-none">{{ goldBalance ?? '—' }} <span class="text-base text-amber-400 font-bold">Gold</span></div>
              <div class="text-xs text-slate-400 mt-1">
                {{ t('settings.monthly_refill') }} : <strong class="text-amber-400">{{ monthlyRefill[userTier] || 100 }} Gold</strong>
                <span v-if="userTier !== 'FREE'"> ({{ userTier }})</span>
              </div>
            </div>
          </div>
          <router-link to="/boutique" class="px-5 py-2.5 rounded-xl bg-amber-500 hover:bg-amber-600 text-white text-sm font-bold shadow transition-all whitespace-nowrap">
            {{ t('settings.recharge') }} →
          </router-link>
        </div>
      </section>

      <!-- === CURRENT PLAN USAGE === -->
      <section>
        <div class="flex items-center gap-3 mb-6">
          <h2 class="text-sm font-bold text-slate-900 uppercase tracking-tight">{{ t('settings.usage') }}</h2>
          <span class="px-2 py-0.5 bg-slate-100 text-slate-500 text-[10px] font-bold rounded border border-slate-200 uppercase">{{ userTier }}</span>
        </div>
        <div class="bg-white border border-slate-200 rounded-2xl shadow-sm overflow-hidden">
          <div class="divide-y divide-slate-50">
            <div v-for="feat in currentConfig.features" :key="feat.key" class="px-8 py-5 flex items-center gap-5 group hover:bg-slate-50 transition-colors">
              <div class="p-2 bg-slate-100 rounded-lg shrink-0 group-hover:bg-white group-hover:shadow-sm transition-all">
                <component :is="feat.icon" class="w-4 h-4 text-slate-500" />
              </div>
              <div class="flex-1 min-w-0">
                <div class="flex items-center justify-between mb-1.5">
                  <span class="text-xs font-bold text-slate-700">{{ feat.label }}</span>
                  <span class="text-[10px] font-bold text-slate-400 uppercase">
                    <span v-if="usage[feat.key]">
                      {{ usage[feat.key].limit >= 9999 ? '∞ illimité' : `${usage[feat.key].current} / ${formatLimit(usage[feat.key].limit, usage[feat.key].period)}` }}
                    </span>
                    <span v-else>—</span>
                  </span>
                </div>
                <div class="h-1.5 bg-slate-100 rounded-full overflow-hidden">
                  <div
                    class="h-full rounded-full transition-all duration-700"
                    :class="getUsagePercent(feat.key) >= 90 ? 'bg-rose-500' : getUsagePercent(feat.key) >= 70 ? 'bg-amber-500' : 'bg-amber-500'"
                    :style="{ width: usage[feat.key]?.limit >= 9999 ? '8%' : `${getUsagePercent(feat.key)}%` }"
                  ></div>
                </div>
              </div>
              <div v-if="usage[feat.key] && !usage[feat.key].allowed" class="shrink-0">
                <ExclamationTriangleIcon class="w-4 h-4 text-rose-500" />
              </div>
            </div>
            <div v-if="currentConfig.unavailable.length" v-for="unav in currentConfig.unavailable" :key="unav" class="px-8 py-4 flex items-center gap-5 opacity-40">
              <div class="p-2 bg-slate-100 rounded-lg shrink-0">
                <BriefcaseIcon class="w-4 h-4 text-slate-400" />
              </div>
              <span class="text-xs font-bold text-slate-500 line-through">{{ unav }}</span>
              <span class="ml-auto text-[9px] font-bold text-slate-300 uppercase">{{ t('settings.unavailable') }}</span>
            </div>
          </div>
        </div>
      </section>

      <!-- === PLANS === -->
      <section>
        <div class="mb-6">
          <h2 class="text-sm font-bold text-slate-900 uppercase tracking-tight mb-1">{{ t('settings.choose_plan') }}</h2>
          <p class="text-xs text-slate-500">{{ t('settings.plans_sub') }}</p>
        </div>
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div
            v-for="tier in tierOrder" :key="tier"
            class="relative bg-white border-2 rounded-2xl p-8 flex flex-col transition-all duration-300"
            :class="tierBorderClass(tier, tierConfig[tier].color)"
          >
            <!-- Current Badge -->
            <div v-if="isCurrentTier(tier)" class="absolute -top-3 left-6">
              <span class="px-3 py-1 text-[9px] font-black uppercase tracking-widest rounded-full border shadow-sm"
                :class="tierColorClass(tierConfig[tier].color)">
                {{ t('settings.current_plan') }}
              </span>
            </div>

            <!-- Tier Header -->
            <div class="mb-6">
              <div class="flex items-center gap-3 mb-4">
                <div class="p-2.5 rounded-xl border" :class="tierColorClass(tierConfig[tier].color)">
                  <component :is="tierConfig[tier].icon" class="w-5 h-5" />
                </div>
                <div>
                  <h3 class="text-base font-bold text-slate-900">{{ t(tierConfig[tier].labelKey) }}</h3>
                  <p class="text-[10px] text-slate-400 font-medium">{{ t(tierConfig[tier].descKey) }}</p>
                </div>
              </div>
              <div class="flex items-baseline gap-1">
                <span class="text-4xl font-black text-slate-900">{{ tierConfig[tier].price }}</span>
                <span class="text-xs text-slate-400 font-bold uppercase">{{ t('settings.per_month') }}</span>
              </div>
              <div class="mt-3 inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-amber-50 border border-amber-200 text-amber-700 text-xs font-black">
                <BoltIcon class="w-4 h-4" /> {{ tierConfig[tier].gold }} {{ t('settings.gold_per_month') }}
              </div>
            </div>

            <!-- Features -->
            <div class="flex-1 space-y-3 mb-8">
              <div v-for="feat in tierConfig[tier].features" :key="feat.key" class="flex items-center gap-3">
                <div class="w-4 h-4 rounded-full flex items-center justify-center shrink-0 bg-emerald-50 border border-emerald-200">
                  <CheckIcon class="w-2.5 h-2.5 text-emerald-600" />
                </div>
                <span class="text-xs text-slate-700 font-semibold">{{ t(feat.lk) }}</span>
              </div>
              <div v-for="unav in tierConfig[tier].unavailable" :key="unav" class="flex items-center gap-3 opacity-40">
                <div class="w-4 h-4 rounded-full flex items-center justify-center shrink-0 bg-slate-100 border border-slate-200">
                  <div class="w-1.5 h-px bg-slate-400"></div>
                </div>
                <span class="text-xs text-slate-500 font-medium line-through">{{ t(unav) }}</span>
              </div>
            </div>

            <!-- CTA Button -->
            <button
              @click="handleSubscribe(tier)"
              :disabled="isSubscribing || isCurrentTier(tier)"
              class="w-full py-3.5 rounded-xl font-black text-[11px] uppercase tracking-widest transition-all duration-200 active:scale-95 disabled:cursor-default"
              :class="tierBtnClass(tier, tierConfig[tier].color)"
            >
              <span v-if="isSubscribing && !isCurrentTier(tier)" class="flex items-center justify-center gap-2">
                <svg class="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
                {{ t('settings.loading') }}
              </span>
              <span v-else>{{ tierBtnLabel(tier) }}</span>
            </button>
          </div>
        </div>

        <!-- Stripe Portal Callout -->
        <div class="mt-6 bg-slate-900 border border-slate-800 rounded-2xl p-6 text-white flex flex-col sm:flex-row items-center justify-between gap-4 shadow-lg">
          <div class="flex items-center gap-4">
            <div class="p-3 bg-amber-500/20 rounded-xl text-amber-400 shrink-0">
              <CreditCardIcon class="w-6 h-6" />
            </div>
            <div>
              <h4 class="text-sm font-bold text-white">{{ t('settings.stripe_title') }}</h4>
              <p class="text-xs text-slate-400">{{ t('settings.stripe_desc') }}</p>
            </div>
          </div>
          <button
            @click="openStripePortal"
            :disabled="isOpeningPortal"
            class="px-5 py-2.5 bg-amber-500 hover:bg-amber-600 text-white text-xs font-bold uppercase tracking-wider rounded-xl transition-all shadow-md shrink-0 flex items-center gap-2"
          >
            <span v-if="isOpeningPortal">{{ t('settings.loading') }}</span>
            <span v-else>{{ t('settings.billing_portal') }}</span>
          </button>
        </div>
      </section>

      <!-- === SECTION AUTOMATISATION IA & GHOSTBUSTER === -->
      <section>
        <div class="mb-6">
          <h2 class="text-sm font-bold text-slate-900 uppercase tracking-tight mb-1">{{ t('settings.ai_title') }}</h2>
          <p class="text-xs text-slate-500">{{ t('settings.ai_sub') }}</p>
        </div>
        <div class="bg-white border border-slate-200 rounded-2xl shadow-sm p-6 sm:p-8 space-y-6 divide-y divide-slate-100">
          
          <!-- Ghostbuster Auto Toggle -->
          <div class="flex items-center justify-between pt-0">
            <div class="pr-4">
              <h4 class="text-sm font-bold text-slate-900 flex items-center gap-2">
                Mode Ghostbuster Auto (Scan 48h)
                <span class="px-2 py-0.5 bg-amber-100 text-amber-800 text-[9px] font-black uppercase rounded">{{ t('settings.exclusive_ai') }}</span>
              </h4>
              <p class="text-xs text-slate-500 mt-0.5">Scanne et prépare automatiquement les relances pour vos candidatures sans réponse depuis +15 jours.</p>
            </div>
            <button
              @click="toggleGhostbuster"
              class="relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none"
              :class="ghostbusterAuto ? 'bg-amber-500' : 'bg-slate-200'"
            >
              <span
                class="pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out"
                :class="ghostbusterAuto ? 'translate-x-5' : 'translate-x-0'"
              ></span>
            </button>
          </div>

          <!-- IA Tone & Language Selection -->
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-6 pt-6">
            <div>
              <label class="block text-xs font-bold text-slate-700 uppercase mb-2">{{ t('settings.tone_label') }}</label>
              <select v-model="aiTone" class="w-full bg-slate-50 border border-slate-200 text-slate-800 text-xs font-bold rounded-xl px-4 py-3 focus:outline-none focus:border-amber-400">
                <option value="professional">{{ t('settings.tone_pro') }}</option>
                <option value="dynamic">{{ t('settings.tone_dynamic') }}</option>
                <option value="direct">{{ t('settings.tone_direct') }}</option>
              </select>
            </div>
            <div>
              <label class="block text-xs font-bold text-slate-700 uppercase mb-2">{{ t('settings.lang_label') }}</label>
              <select v-model="aiLanguage" class="w-full bg-slate-50 border border-slate-200 text-slate-800 text-xs font-bold rounded-xl px-4 py-3 focus:outline-none focus:border-amber-400">
                <option value="fr">{{ t('settings.lang_fr') }}</option>
                <option value="en">{{ t('settings.lang_en') }}</option>
              </select>
            </div>
          </div>

        </div>
      </section>

      <!-- === SECTION NOTIFICATIONS === -->
      <section>
        <div class="mb-6">
          <h2 class="text-sm font-bold text-slate-900 uppercase tracking-tight mb-1">{{ t('settings.notif_title') }}</h2>
          <p class="text-xs text-slate-500">{{ t('settings.notif_sub') }}</p>
        </div>
        <div class="bg-white border border-slate-200 rounded-2xl shadow-sm p-6 sm:p-8 space-y-5">
          <div class="flex items-center justify-between">
            <div>
              <h4 class="text-xs font-bold text-slate-800">{{ t('settings.notif_sniper') }}</h4>
              <p class="text-[11px] text-slate-400">{{ t('settings.notif_sniper_desc') }}</p>
            </div>
            <button @click="notifSniper = !notifSniper" class="relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out" :class="notifSniper ? 'bg-amber-500' : 'bg-slate-200'">
              <span class="pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out" :class="notifSniper ? 'translate-x-5' : 'translate-x-0'"></span>
            </button>
          </div>
          <div class="flex items-center justify-between pt-3 border-t border-slate-100">
            <div>
              <h4 class="text-xs font-bold text-slate-800">{{ t('settings.notif_followup') }}</h4>
              <p class="text-[11px] text-slate-400">{{ t('settings.notif_followup_desc') }}</p>
            </div>
            <button @click="notifFollowup = !notifFollowup" class="relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out" :class="notifFollowup ? 'bg-amber-500' : 'bg-slate-200'">
              <span class="pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out" :class="notifFollowup ? 'translate-x-5' : 'translate-x-0'"></span>
            </button>
          </div>
          <div class="flex items-center justify-between pt-3 border-t border-slate-100">
            <div>
              <h4 class="text-xs font-bold text-slate-800">{{ t('settings.notif_digest') }}</h4>
              <p class="text-[11px] text-slate-400">{{ t('settings.notif_digest_desc') }}</p>
            </div>
            <button @click="notifWeeklyDigest = !notifWeeklyDigest" class="relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out" :class="notifWeeklyDigest ? 'bg-amber-500' : 'bg-slate-200'">
              <span class="pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out" :class="notifWeeklyDigest ? 'translate-x-5' : 'translate-x-0'"></span>
            </button>
          </div>
        </div>
      </section>

      <!-- === PROFILE & RGPD SECTION === -->
      <section>
        <h2 class="text-sm font-bold text-slate-900 uppercase tracking-tight mb-6">{{ t('settings.security_title') }}</h2>
        <div class="bg-white border border-slate-200 rounded-2xl shadow-sm p-8 space-y-6">
          <div class="flex flex-col sm:flex-row items-center gap-8 pb-6 border-b border-slate-100">
            <div class="w-20 h-20 rounded-2xl bg-amber-50 border border-amber-200 flex items-center justify-center text-3xl font-black text-amber-600 shrink-0">
              {{ profileData.full_name.charAt(0).toUpperCase() || 'U' }}
            </div>
            <div class="flex-1 text-center sm:text-left">
              <h3 class="text-xl font-bold text-slate-900">{{ profileData.full_name }}</h3>
              <p class="text-sm text-slate-500 mb-4">{{ profileData.email }}</p>
              <div class="flex flex-wrap gap-2 justify-center sm:justify-start">
                <button @click="router.push('/profile')" class="px-4 py-2 bg-amber-500 hover:bg-amber-600 text-white text-xs font-bold uppercase rounded-xl transition-colors">
                  Modifier le profil
                </button>
              </div>
            </div>
          </div>

          <!-- RGPD Data Export & Account Privacy -->
          <div class="flex flex-col sm:flex-row items-center justify-between gap-4 pt-2">
            <div>
              <h4 class="text-xs font-bold text-slate-800">{{ t('settings.rgpd_title') }}</h4>
              <p class="text-[11px] text-slate-400">{{ t('settings.rgpd_desc') }}</p>
            </div>
            <div class="flex items-center gap-2">
              <button
                @click="exportDataJSON"
                :disabled="isExportingData"
                class="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold uppercase rounded-xl transition-colors flex items-center gap-2"
              >
                <ArrowDownTrayIcon class="w-4 h-4 text-slate-500" />
                <span v-if="isExportingData">{{ t('settings.exporting') }}</span>
                <span v-else>{{ t('settings.export_data') }}</span>
              </button>
              <button class="px-4 py-2 bg-rose-50 text-rose-600 border border-rose-200 text-xs font-bold uppercase rounded-xl hover:bg-rose-100 transition-colors">
                Supprimer le compte
              </button>
            </div>
          </div>

        </div>
      </section>

    </div>
  </div>
</template>

<style scoped>
</style>
