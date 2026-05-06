<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
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
} from '@heroicons/vue/24/outline'

const router = useRouter()

// --- State ---
const userTier = ref('FREE')
const profileData = ref({ full_name: '', email: '' })
const usage = ref({})
const isSubscribing = ref(false)

// --- Tier Config (matches subscription.py exactly) ---
const tierConfig = {
  FREE: {
    label: 'Gratuit', price: '0€', icon: ShieldCheckIcon, color: 'slate',
    description: 'Pour débuter votre conquête.',
    features: [
      { key: 'sniper_search', label: 'Recherches Sniper', icon: MagnifyingGlassIcon },
      { key: 'cv_audit', label: 'Audits CV (Mentor IA)', icon: DocumentTextIcon },
      { key: 'hr_interview', label: 'Entretiens RH vocaux', icon: MicrophoneIcon },
      { key: 'follow_up', label: 'Relances auto', icon: BoltIcon },
      { key: 'cv_adaptation', label: 'Adaptations de CV', icon: DocumentTextIcon },
    ],
    unavailable: ['Headhunter', 'Carnet d\'adresses', 'Portfolio IA']
  },
  ESSENTIAL: {
    label: 'Essentiel', price: '9.99€', icon: StarIcon, color: 'amber',
    description: 'Le choix des vainqueurs (Conseillé).',
    features: [
      { key: 'sniper_search', label: 'Recherches Sniper', icon: MagnifyingGlassIcon },
      { key: 'cv_audit', label: 'Audits CV ATS', icon: DocumentTextIcon },
      { key: 'hr_interview', label: 'Entretiens RH vocaux', icon: MicrophoneIcon },
      { key: 'headhunter', label: 'Usages Headhunter', icon: UsersIcon },
      { key: 'address_book', label: 'Carnet d\'adresses', icon: BriefcaseIcon },
      { key: 'follow_up', label: 'Relances', icon: BoltIcon },
      { key: 'cv_adaptation', label: 'Adaptations CV', icon: DocumentTextIcon },
    ],
    unavailable: ['Portfolio IA personnalisé']
  },
  PRO: {
    label: 'Pro', price: '19.99€', icon: RocketLaunchIcon, color: 'indigo',
    description: 'Puissance maximale pour l\'élite.',
    features: [
      { key: 'sniper_search', label: 'Recherches Sniper', icon: MagnifyingGlassIcon },
      { key: 'cv_audit', label: 'Audits CV approfondis', icon: DocumentTextIcon },
      { key: 'hr_interview', label: 'Entretiens RH IA', icon: MicrophoneIcon },
      { key: 'headhunter', label: 'Headhunter', icon: UsersIcon },
      { key: 'address_book', label: 'Carnet d\'adresses', icon: BriefcaseIcon },
      { key: 'follow_up', label: 'Relances', icon: BoltIcon },
      { key: 'cv_adaptation', label: 'Adaptations CV', icon: DocumentTextIcon },
    ],
    unavailable: []
  }
}

const tierOrder = ['FREE', 'ESSENTIAL', 'PRO']

// --- Fetch ---
const fetchAll = async () => {
  try {
    const [profileRes, usageRes] = await Promise.all([
      authFetch('/api/profile'),
      authFetch('/api/profile/usage')
    ])
    const profileJson = await profileRes.json()
    const usageJson = await usageRes.json()

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
  indigo: 'text-indigo-600 bg-indigo-50 border-indigo-200',
  slate: 'text-slate-600 bg-slate-100 border-slate-200',
}[color])

const tierBorderClass = (tier, color) => isCurrentTier(tier)
  ? (color === 'amber' ? 'border-amber-400 shadow-amber-100 shadow-lg' : color === 'indigo' ? 'border-indigo-500 shadow-indigo-100 shadow-lg' : 'border-slate-400')
  : 'border-slate-200 hover:border-slate-300'

const tierBtnClass = (tier, color) => {
  if (isCurrentTier(tier)) return 'bg-slate-900 text-white cursor-default'
  if (color === 'amber') return 'bg-amber-500 hover:bg-amber-600 text-white shadow-lg'
  if (color === 'indigo') return 'bg-indigo-600 hover:bg-indigo-700 text-white shadow-lg'
  return 'bg-slate-100 text-slate-700 hover:bg-slate-200'
}

const tierBtnLabel = (tier) => {
  if (isCurrentTier(tier)) return tier === 'FREE' ? 'Plan actuel' : '✓ Votre plan'
  if (tier === 'FREE') return 'Rétrograder'
  return tier === 'ESSENTIAL' ? 'Choisir Essentiel' : 'Devenir Pro'
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
          <h1 class="text-base font-bold text-slate-900">Paramètres & Abonnements</h1>
          <p class="text-[10px] text-slate-400 font-bold uppercase tracking-widest">Gérez vos accès et votre plan</p>
        </div>
        <div class="ml-auto flex items-center gap-2">
          <div class="hidden sm:flex items-center gap-2 px-3 py-1.5 bg-indigo-50 rounded-lg border border-indigo-100">
            <div class="w-2 h-2 rounded-full bg-indigo-500"></div>
            <span class="text-[10px] font-bold text-indigo-600 uppercase tracking-widest">
              {{ userTier === 'ADMIN' ? 'Admin GoldArmy' : userTier === 'PRO' ? 'Membre Pro' : userTier === 'ESSENTIAL' ? 'Membre Essentiel' : 'Compte Gratuit' }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <div class="max-w-6xl mx-auto px-6 lg:px-10 py-10 space-y-12">

      <!-- === CURRENT PLAN USAGE === -->
      <section>
        <div class="flex items-center gap-3 mb-6">
          <h2 class="text-sm font-bold text-slate-900 uppercase tracking-tight">Mon Utilisation</h2>
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
                    :class="getUsagePercent(feat.key) >= 90 ? 'bg-rose-500' : getUsagePercent(feat.key) >= 70 ? 'bg-amber-500' : 'bg-indigo-500'"
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
              <span class="ml-auto text-[9px] font-bold text-slate-300 uppercase">Non disponible</span>
            </div>
          </div>
        </div>
      </section>

      <!-- === PLANS === -->
      <section>
        <div class="mb-6">
          <h2 class="text-sm font-bold text-slate-900 uppercase tracking-tight mb-1">Choisir un plan</h2>
          <p class="text-xs text-slate-500">Montez en puissance selon vos ambitions professionnelles.</p>
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
                Plan actuel
              </span>
            </div>

            <!-- Tier Header -->
            <div class="mb-6">
              <div class="flex items-center gap-3 mb-4">
                <div class="p-2.5 rounded-xl border" :class="tierColorClass(tierConfig[tier].color)">
                  <component :is="tierConfig[tier].icon" class="w-5 h-5" />
                </div>
                <div>
                  <h3 class="text-base font-bold text-slate-900">{{ tierConfig[tier].label }}</h3>
                  <p class="text-[10px] text-slate-400 font-medium">{{ tierConfig[tier].description }}</p>
                </div>
              </div>
              <div class="flex items-baseline gap-1">
                <span class="text-4xl font-black text-slate-900">{{ tierConfig[tier].price }}</span>
                <span class="text-xs text-slate-400 font-bold uppercase">/mois</span>
              </div>
            </div>

            <!-- Features -->
            <div class="flex-1 space-y-3 mb-8">
              <div v-for="feat in tierConfig[tier].features" :key="feat.key" class="flex items-center gap-3">
                <div class="w-4 h-4 rounded-full flex items-center justify-center shrink-0 bg-emerald-50 border border-emerald-200">
                  <CheckIcon class="w-2.5 h-2.5 text-emerald-600" />
                </div>
                <span class="text-xs text-slate-700 font-semibold">{{ feat.label }}</span>
              </div>
              <div v-for="unav in tierConfig[tier].unavailable" :key="unav" class="flex items-center gap-3 opacity-40">
                <div class="w-4 h-4 rounded-full flex items-center justify-center shrink-0 bg-slate-100 border border-slate-200">
                  <div class="w-1.5 h-px bg-slate-400"></div>
                </div>
                <span class="text-xs text-slate-500 font-medium line-through">{{ unav }}</span>
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
                Chargement...
              </span>
              <span v-else>{{ tierBtnLabel(tier) }}</span>
            </button>
          </div>
        </div>
      </section>

      <!-- === PROFILE SECTION === -->
      <section>
        <h2 class="text-sm font-bold text-slate-900 uppercase tracking-tight mb-6">Profil & Sécurité</h2>
        <div class="bg-white border border-slate-200 rounded-2xl shadow-sm p-8 flex flex-col sm:flex-row items-center gap-8">
          <div class="w-20 h-20 rounded-2xl bg-indigo-50 border border-indigo-100 flex items-center justify-center text-3xl font-black text-indigo-600 shrink-0">
            {{ profileData.full_name.charAt(0).toUpperCase() || 'U' }}
          </div>
          <div class="flex-1 text-center sm:text-left">
            <h3 class="text-xl font-bold text-slate-900">{{ profileData.full_name }}</h3>
            <p class="text-sm text-slate-500 mb-4">{{ profileData.email }}</p>
            <div class="flex flex-wrap gap-2 justify-center sm:justify-start">
              <button @click="router.push('/profile')" class="px-4 py-2 bg-slate-900 text-white text-xs font-bold uppercase rounded-xl hover:bg-indigo-600 transition-colors">
                Modifier le profil
              </button>
              <button class="px-4 py-2 bg-rose-50 text-rose-600 border border-rose-200 text-xs font-bold uppercase rounded-xl hover:bg-rose-100 transition-colors">
                Supprimer mon compte
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
