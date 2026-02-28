<script setup>
import { 
  ArrowLeftIcon, 
  CheckIcon, 
  StarIcon, 
  RocketLaunchIcon, 
  SparklesIcon,
  ShieldCheckIcon,
  UserGroupIcon,
  BriefcaseIcon,
  MicrophoneIcon,
  MapIcon
} from '@heroicons/vue/24/outline'
import { authFetch } from '../utils/auth'
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const goBack = () => router.push('/dashboard')

const tiers = [
  {
    name: 'Gratuit',
    id: 'tier-free',
    price: '0€',
    description: 'Pour débuter votre conquête du marché.',
    features: [
      '2 recherches Sniper / jour',
      '2 audits de CV (Mentor IA)',
      '1 entretien RH vocal',
      '5 relances automatiques',
      '3 adaptations de CV par IA',
      'Accès communautaire',
    ],
    unavailable: [
      'Usage Headhunter',
      'Carnet d\'adresses privé',
      'Portfolio personnalisé'
    ],
    buttonText: 'Plan Actuel',
    highlighted: false,
    gradient: 'from-slate-800 to-slate-900',
    icon: ShieldCheckIcon
  },
  {
    name: 'Essentiel',
    id: 'tier-essential',
    price: '9.99€',
    description: 'Le choix des vainqueurs (Conseillé).',
    features: [
      '25 recherches Sniper / mois',
      '10 audits de CV ATS',
      '10 entretiens RH vocaux',
      '10 usages Headhunter',
      '25 places au carnet d\'adresses',
      'Relances illimitées',
      'Adaptations CV illimitées',
    ],
    buttonText: 'Choisir Essentiel',
    highlighted: true,
    gradient: 'from-amber-500/10 to-gold-500/5',
    icon: StarIcon
  },
  {
    name: 'Pro',
    id: 'tier-pro',
    price: '19.99€',
    description: 'Puissance de feu maximale pour l\'élite.',
    features: [
      'Recherches Sniper illimitées',
      '20 audits de CV approfondis',
      '15 entretiens RH IA',
      'Headhunter illimité (Automation)',
      'Carnet d\'adresses illimité',
      'Portfolio personnalisé IA',
      'Support Prioritaire 24/7',
    ],
    buttonText: 'Devenir Pro',
    highlighted: false,
    gradient: 'from-indigo-600/20 to-violet-600/10',
    icon: RocketLaunchIcon
  }
]

const userTier = ref('FREE')

const fetchProfile = async () => {
  try {
    const res = await authFetch('http://localhost:8000/api/profile')
    const json = await res.json()
    if (json.status === 'success') {
      userTier.value = json.data.subscription_tier || 'FREE'
    }
  } catch (e) {
    console.error("Failed to fetch profile", e)
  }
}

onMounted(fetchProfile)

const isSubscribing = ref(false)

const handleSubscribe = async (tierId) => {
  if (isSubscribing.value) return
  
  // Mapping frontend IDs to backend tier names
  const tierMap = {
    'tier-free': 'FREE',
    'tier-essential': 'ESSENTIAL',
    'tier-pro': 'PRO'
  }
  
  const tier = tierMap[tierId]
  if (tier === 'FREE') {
    // Already handled or just redirect to dashboard
    router.push('/dashboard')
    return
  }
  
  if (tier === userTier.value) {
    toastState.addToast("Vous êtes déjà sur ce forfait.", "info")
    return
  }

  isSubscribing.value = true
  try {
    const res = await authFetch('http://localhost:8000/api/stripe/create-checkout-session', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ tier })
    })
    const json = await res.json()
    if (json.status === 'success' && json.url) {
      window.location.href = json.url
    } else {
      toastState.addToast("Erreur lors de la création de la session Stripe.", "error")
    }
  } catch (e) {
    toastState.addToast("Erreur de connexion au service de paiement.", "error")
  } finally {
    isSubscribing.value = false
  }
}

const displayTiers = computed(() => {
  return tiers.map(t => {
    let isActive = (t.id === 'tier-free' && userTier.value === 'FREE') || 
                   (t.id === 'tier-essential' && userTier.value === 'ESSENTIAL') ||
                   (t.id === 'tier-pro' && userTier.value === 'PRO')
    
    // Branding Admin for Pro tier if user is Admin
    let buttonText = isActive ? 'Plan Actuel' : t.buttonText
    let tierName = t.name
    
    if (t.id === 'tier-pro' && userTier.value === 'ADMIN') {
        isActive = true
        buttonText = 'Plan Admin GoldArmy'
        tierName = 'Admin'
    }

    return {
      ...t,
      name: tierName,
      buttonText: buttonText,
      highlighted: t.id === 'tier-essential' || isActive
    }
  })
})
</script>

<template>
  <div class="px-4 md:px-10 py-8 max-w-[1400px] mx-auto w-full animate-fade-in-up">
    
    <!-- Top Header -->
    <div class="flex items-center justify-between border-b border-surface-800 pb-8 mb-12 mt-6">
        <div class="flex items-center gap-6">
            <button @click="goBack" class="group p-3 bg-surface-900 border border-surface-800 hover:border-gold-500/50 rounded-2xl text-slate-400 hover:text-white transition-all shadow-sm">
                <ArrowLeftIcon class="w-6 h-6 group-hover:-translate-x-1 transition-transform" />
            </button>
            <div>
                <h1 class="text-4xl font-display font-black text-white tracking-tight">Paramètres <span class="text-gold-400">&</span> Abonnements</h1>
                <p class="text-slate-400 mt-1 font-medium italic text-lg">Optimisez votre arsenal et gérez vos privilèges GoldArmy.</p>
            </div>
        </div>
        <div class="hidden lg:flex items-center gap-3 bg-indigo-500/10 border border-indigo-500/20 px-4 py-2 rounded-xl">
             <ShieldCheckIcon class="w-5 h-5 text-indigo-400" />
             <span class="text-sm font-bold text-indigo-300">Compte vérifié</span>
        </div>
    </div>

    <!-- Pricing Grid -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-16 relative">
      <!-- Background Glow decor -->
      <div class="absolute -top-24 left-1/2 -translate-x-1/2 w-[600px] h-[400px] bg-gold-500/5 blur-[100px] pointer-events-none"></div>

      <div 
        v-for="tier in displayTiers" 
        :key="tier.id"
        class="relative flex flex-col p-8 rounded-[2.5rem] border transition-all duration-500 group"
        :class="[
            tier.highlighted 
                ? 'bg-surface-900 border-gold-500 shadow-[0_0_40px_rgba(245,158,11,0.15)] ring-1 ring-gold-500/50 scale-105 z-10' 
                : 'bg-surface-900 border-surface-800 hover:border-surface-600'
        ]"
      >
        <!-- Popular Badge -->
        <div v-if="tier.highlighted" class="absolute -top-4 left-1/2 -translate-x-1/2 px-4 py-1.5 bg-gradient-to-r from-gold-500 to-amber-600 rounded-full text-[10px] font-black text-surface-950 uppercase tracking-widest shadow-lg shadow-gold-500/30">
            Le plus populaire
        </div>

        <div class="mb-8">
            <div 
                class="w-14 h-14 rounded-2xl flex items-center justify-center mb-6 bg-gradient-to-br transition-all duration-500 group-hover:scale-110"
                :class="tier.gradient"
            >
                <component :is="tier.icon" class="w-7 h-7" :class="tier.highlighted ? 'text-gold-400' : 'text-slate-400'" />
            </div>
            <h3 class="text-2xl font-display font-bold text-white mb-2">{{ tier.name }}</h3>
            <div class="flex items-baseline gap-1 mb-4">
                <span class="text-5xl font-black text-white tracking-tighter">{{ tier.price }}</span>
                <span class="text-slate-500 font-bold uppercase text-xs tracking-widest">/ mois</span>
            </div>
            <p class="text-slate-400 text-sm leading-relaxed font-medium">{{ tier.description }}</p>
        </div>

        <div class="flex-1 space-y-4 mb-10">
            <div v-for="feature in tier.features" :key="feature" class="flex items-start gap-3">
                <div class="mt-1 w-5 h-5 rounded-full bg-emerald-500/10 flex items-center justify-center shrink-0 border border-emerald-500/20">
                    <CheckIcon class="w-3 h-3 text-emerald-400" />
                </div>
                <span class="text-sm font-semibold text-slate-300">{{ feature }}</span>
            </div>
            <div v-for="unfeat in tier.unavailable" :key="unfeat" class="flex items-start gap-3 opacity-30 grayscale">
                <div class="mt-1 w-5 h-5 rounded-full bg-slate-800 flex items-center justify-center shrink-0 border border-slate-700">
                    <div class="w-1.5 h-px bg-slate-500"></div>
                </div>
                <span class="text-sm font-semibold text-slate-500 line-through">{{ unfeat }}</span>
            </div>
        </div>

        <button 
            @click="handleSubscribe(tier.id)"
            :disabled="isSubscribing"
            class="w-full py-4 rounded-2xl font-black text-sm uppercase tracking-widest transition-all duration-300 active:scale-95 disabled:opacity-50"
            :class="[
                tier.highlighted
                    ? 'bg-gradient-to-r from-gold-500 to-amber-600 text-surface-950 shadow-lg shadow-gold-500/20 hover:shadow-gold-500/40'
                    : 'bg-surface-800 border border-surface-700 text-white hover:bg-surface-700 hover:border-slate-500'
            ]"
        >
            <span v-if="isSubscribing && !((tier.id === 'tier-free' && userTier === 'FREE') || 
                   (tier.id === 'tier-essential' && userTier === 'ESSENTIAL') ||
                   (tier.id === 'tier-pro' && userTier === 'PRO'))" class="flex items-center justify-center gap-2">
                <svg class="animate-spin h-4 w-4 text-current" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
                Chargement...
            </span>
            <span v-else>{{ tier.buttonText }}</span>
        </button>
      </div>
    </div>

    <!-- Extra Settings Section -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-20 animate-fade-in-up" style="animation-delay: 200ms">
        <div class="bg-surface-900 border border-surface-800 rounded-[2rem] p-8 hover:border-surface-700 transition-colors">
            <div class="flex items-center gap-4 mb-6">
                <div class="p-3 bg-indigo-500/10 rounded-xl">
                    <SparklesIcon class="w-6 h-6 text-indigo-400" />
                </div>
                <h4 class="text-xl font-display font-bold text-white">Préférences IA</h4>
            </div>
            <div class="space-y-6">
                <div class="flex items-center justify-between">
                    <div>
                        <p class="text-white font-bold text-sm">Précision de filtrage Sniper</p>
                        <p class="text-xs text-slate-500">Définit le niveau de sévérité de Gemini 3.1</p>
                    </div>
                    <select class="bg-surface-800 border border-surface-700 text-white text-xs font-bold rounded-lg px-3 py-1.5 focus:outline-none focus:ring-1 focus:ring-gold-500">
                        <option>Chirurgicale</option>
                        <option selected>Standard (Auto)</option>
                        <option>Large</option>
                    </select>
                </div>
                <div class="flex items-center justify-between">
                    <div>
                        <p class="text-white font-bold text-sm">Voix de l'entretien</p>
                        <p class="text-xs text-slate-500">Sélectionnez le profil vocal du recruteur IA</p>
                    </div>
                    <select class="bg-surface-800 border border-surface-700 text-white text-xs font-bold rounded-lg px-3 py-1.5 focus:outline-none focus:ring-1 focus:ring-gold-500">
                        <option>Directeur RH (Formel)</option>
                        <option>Tech Lead (Direct)</option>
                        <option selected>Recruteur Standard</option>
                    </select>
                </div>
            </div>
        </div>

        <div class="bg-surface-900 border border-surface-800 rounded-[2rem] p-8 hover:border-surface-700 transition-colors">
            <div class="flex items-center gap-4 mb-6">
                <div class="p-3 bg-emerald-500/10 rounded-xl">
                    <UserGroupIcon class="w-6 h-6 text-emerald-400" />
                </div>
                <h4 class="text-xl font-display font-bold text-white">Profil & Confidentialité</h4>
            </div>
            <div class="space-y-4">
                <div class="p-4 bg-surface-950 border border-surface-800 rounded-2xl flex items-center justify-between">
                    <div class="flex items-center gap-3">
                        <div class="w-10 h-10 rounded-full bg-gold-500/10 flex items-center justify-center text-gold-400 font-bold">Y</div>
                        <div>
                            <p class="text-sm font-bold text-white">Yves D.</p>
                            <p class="text-[10px] text-slate-500 uppercase font-black">Utilisateur GoldArmy</p>
                        </div>
                    </div>
                    <button class="text-xs font-bold text-slate-400 hover:text-white transition-colors">Modifier</button>
                </div>
                <button class="w-full text-center py-3 border border-surface-800 hover:bg-rose-500/5 hover:border-rose-500/20 text-slate-500 hover:text-rose-400 rounded-2xl text-xs font-bold transition-all">
                    Supprimer mon compte et mes données
                </button>
            </div>
        </div>
    </div>
  </div>
</template>

<style scoped>
.animate-fade-in-up {
  animation: fadeInUp 0.6s ease-out forwards;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
