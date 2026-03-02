<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import {
  MapIcon,
  ChatBubbleBottomCenterTextIcon,
  BriefcaseIcon,
  UserGroupIcon,
  MicrophoneIcon,
  HomeIcon,
  SparklesIcon,
  ArrowRightIcon,
  XMarkIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
  QuestionMarkCircleIcon
} from '@heroicons/vue/24/outline'

const router = useRouter()

// ─── User greeting ───────────────────────────────────────────────────────────
const userName = ref('là')
onMounted(() => {
  const stored = localStorage.getItem('user')
  if (stored) {
    try {
      const u = JSON.parse(stored)
      userName.value = u.email?.split('@')[0] ?? 'là'
    } catch {}
  }
  // Start entrance animation
  setTimeout(() => cardsReady.value = true, 100)
})

// ─── Feature cards ───────────────────────────────────────────────────────────
const features = [
  {
    id: 'sniper',
    name: 'Sniper Search',
    route: '/opportunities',
    color: 'from-blue-600 to-cyan-500',
    glow: 'shadow-blue-500/20',
    border: 'border-blue-500/20',
    icon: MapIcon,
    emoji: '🎯',
    tag: 'IA Puissante',
    tagColor: 'bg-blue-500/20 text-blue-300',
    description: 'Recherche ultraprécise d\'offres d\'emploi. L\'IA scanne des centaines de sources pour trouver les meilleures opportunités qui correspondent à ton profil et ta localisation.',
    stats: [
      { label: 'Sources analysées', value: '50+' },
      { label: 'Précision', value: '94%' },
    ],
    gradient: 'radial-gradient(ellipse at 30% 40%, rgba(59, 130, 246, 0.15) 0%, transparent 70%)',
  },
  {
    id: 'mentor',
    name: 'Mentor IA',
    route: '/mentor',
    color: 'from-violet-600 to-purple-500',
    glow: 'shadow-violet-500/20',
    border: 'border-violet-500/20',
    icon: ChatBubbleBottomCenterTextIcon,
    emoji: '🧠',
    tag: 'Pro',
    tagColor: 'bg-violet-500/20 text-violet-300',
    description: 'Ton coach carrière personnel. Analyse ton CV, identifie tes points forts, génère des lettres de motivation sur mesure et prépare-toi à chaque entretien.',
    stats: [
      { label: 'Audit CV', value: '< 30s' },
      { label: 'Taux succès', value: '+40%' },
    ],
    gradient: 'radial-gradient(ellipse at 70% 30%, rgba(139, 92, 246, 0.15) 0%, transparent 70%)',
  },
  {
    id: 'interview',
    name: 'Entretien Vocal',
    route: '/interview',
    color: 'from-emerald-600 to-teal-500',
    glow: 'shadow-emerald-500/20',
    border: 'border-emerald-500/20',
    icon: MicrophoneIcon,
    emoji: '🎙️',
    tag: 'Vocal IA',
    tagColor: 'bg-emerald-500/20 text-emerald-300',
    description: 'Simule de vrais entretiens d\'embauche avec un recruteur IA vocal. Pratique, reçois un feedback instantané et améliore ta confiance avant le grand jour.',
    stats: [
      { label: 'Questions/session', value: '10+' },
      { label: 'Feedback', value: 'Temps réel' },
    ],
    gradient: 'radial-gradient(ellipse at 50% 70%, rgba(16, 185, 129, 0.15) 0%, transparent 70%)',
  },
  {
    id: 'crm',
    name: 'CRM Candidatures',
    route: '/crm',
    color: 'from-amber-500 to-orange-500',
    glow: 'shadow-amber-500/20',
    border: 'border-amber-500/20',
    icon: BriefcaseIcon,
    emoji: '📋',
    tag: 'Kanban',
    tagColor: 'bg-amber-500/20 text-amber-300',
    description: 'Tableau Kanban intelligent pour suivre toutes tes candidatures. Glisse-dépose, génère des emails de relance automatiques et ne rate plus jamais une opportunité.',
    stats: [
      { label: 'Colonnes Kanban', value: '5' },
      { label: 'Relances auto', value: 'IA' },
    ],
    gradient: 'radial-gradient(ellipse at 20% 60%, rgba(245, 158, 11, 0.15) 0%, transparent 70%)',
  },
  {
    id: 'network',
    name: 'Réseau Pro',
    route: '/network',
    color: 'from-rose-600 to-pink-500',
    glow: 'shadow-rose-500/20',
    border: 'border-rose-500/20',
    icon: UserGroupIcon,
    emoji: '🤝',
    tag: 'Networking',
    tagColor: 'bg-rose-500/20 text-rose-300',
    description: 'Trouve les décideurs et RH des entreprises qui t\'intéressent. L\'IA rédige des emails d\'approche personnalisés pour maximiser tes chances de réponse.',
    stats: [
      { label: 'Contacts trouvés', value: 'Auto' },
      { label: 'Templates emails', value: '∞' },
    ],
    gradient: 'radial-gradient(ellipse at 80% 50%, rgba(244, 63, 94, 0.15) 0%, transparent 70%)',
  },
]

const cardsReady = ref(false)
const hoveredCard = ref(null)

// ─── Tutorial system ──────────────────────────────────────────────────────────
const tutorialActive = ref(false)
const tutorialStep = ref(0)

const tutorialSteps = [
  {
    targetId: 'home-welcome',
    title: '👋 Bienvenue sur GoldArmy !',
    text: 'Cette page Accueil est ton point de départ. Elle résume toutes les fonctionnalités disponibles. Clique sur une card pour y accéder directement.',
    position: 'bottom',
  },
  {
    targetId: 'feature-sniper',
    title: '🎯 Sniper Search',
    text: 'Commence ici ! Lance une recherche d\'emploi ultra-précise. Dis à l\'IA ton profil, ta ville et le type de poste souhaité — elle s\'occupe du reste.',
    position: 'right',
  },
  {
    targetId: 'feature-mentor',
    title: '🧠 Mentor IA',
    text: 'Upload ton CV ici pour un audit complet. Le Mentor IA identifie tes lacunes, adapte ton CV pour chaque offre et génère ta lettre de motivation en quelques secondes.',
    position: 'right',
  },
  {
    targetId: 'feature-interview',
    title: '🎙️ Entretien Vocal',
    text: 'Simule un vrai entretien ! Parle à voix haute, l\'IA te pose des questions de recruteur et t\'évalue en temps réel sur tes réponses.',
    position: 'left',
  },
  {
    targetId: 'feature-crm',
    title: '📋 CRM Candidatures',
    text: 'Suis toutes tes candidatures dans ce tableau Kanban. Glisse une carte pour changer son statut, génère des relances automatiques si tu n\'as pas de réponse.',
    position: 'left',
  },
  {
    targetId: 'feature-network',
    title: '🤝 Réseau Pro',
    text: 'Trouve les RH et décideurs des entreprises qui t\'intéressent. L\'IA rédige des emails d\'approche personnalisés — le networking devient automatique !',
    position: 'right',
  },
  {
    targetId: 'tutorial-end',
    title: '🚀 Tu es prêt !',
    text: 'Tu connais maintenant toutes les fonctionnalités de GoldArmy. Lance-toi avec le Sniper Search ou commence par uploader ton CV dans le Mentor IA. Bonne chance !',
    position: 'bottom',
  },
]

const currentTutorialStep = computed(() => tutorialSteps[tutorialStep.value])
const isLastStep = computed(() => tutorialStep.value === tutorialSteps.length - 1)

function startTutorial() {
  tutorialStep.value = 0
  tutorialActive.value = true
  scrollToTarget(tutorialSteps[0].targetId)
}

function nextStep() {
  if (isLastStep.value) {
    closeTutorial()
    return
  }
  tutorialStep.value++
  scrollToTarget(tutorialSteps[tutorialStep.value].targetId)
}

function prevStep() {
  if (tutorialStep.value > 0) {
    tutorialStep.value--
    scrollToTarget(tutorialSteps[tutorialStep.value].targetId)
  }
}

function closeTutorial() {
  tutorialActive.value = false
}

function scrollToTarget(id) {
  setTimeout(() => {
    const el = document.getElementById(id)
    if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' })
  }, 100)
}

function getTooltipPosition(step) {
  if (!tutorialActive.value) return {}
  const el = document.getElementById(step.targetId)
  if (!el) return { top: '50%', left: '50%' }
  const rect = el.getBoundingClientRect()
  const pos = step.position

  if (pos === 'bottom') return { top: rect.bottom + window.scrollY + 16 + 'px', left: rect.left + rect.width / 2 + 'px', transform: 'translateX(-50%)' }
  if (pos === 'top') return { bottom: window.innerHeight - rect.top - window.scrollY + 16 + 'px', left: rect.left + rect.width / 2 + 'px', transform: 'translateX(-50%)' }
  if (pos === 'right') return { top: rect.top + window.scrollY + rect.height / 2 + 'px', left: rect.right + 16 + 'px', transform: 'translateY(-50%)' }
  if (pos === 'left') return { top: rect.top + window.scrollY + rect.height / 2 + 'px', right: window.innerWidth - rect.left + 16 + 'px', transform: 'translateY(-50%)' }
  return {}
}

// ESC closes tutorial
function handleKey(e) {
  if (e.key === 'Escape') closeTutorial()
}
onMounted(() => window.addEventListener('keydown', handleKey))
onUnmounted(() => window.removeEventListener('keydown', handleKey))
</script>

<template>
  <div class="relative min-h-full bg-surface-950 text-slate-200 overflow-x-hidden">

    <!-- ── Tutorial overlay backdrop ─────────────────────────────────────── -->
    <Transition name="fade">
      <div
        v-if="tutorialActive"
        class="fixed inset-0 bg-black/60 backdrop-blur-sm z-40 pointer-events-none"
      />
    </Transition>

    <!-- ── Tutorial tooltip ───────────────────────────────────────────────── -->
    <Transition name="tooltip">
      <div
        v-if="tutorialActive"
        :style="getTooltipPosition(currentTutorialStep)"
        class="fixed z-50 w-80 bg-surface-800 border border-surface-600 rounded-2xl shadow-2xl shadow-black/50 p-5 pointer-events-auto"
      >
        <!-- Header -->
        <div class="flex items-start justify-between mb-3">
          <h3 class="font-bold text-white text-base leading-tight">{{ currentTutorialStep.title }}</h3>
          <button @click="closeTutorial" class="text-slate-500 hover:text-white transition-colors ml-2 shrink-0">
            <XMarkIcon class="w-4 h-4" />
          </button>
        </div>
        <p class="text-slate-300 text-sm leading-relaxed mb-4">{{ currentTutorialStep.text }}</p>

        <!-- Progress dots -->
        <div class="flex items-center gap-1.5 mb-4">
          <div
            v-for="(_, i) in tutorialSteps" :key="i"
            class="h-1.5 rounded-full transition-all duration-300"
            :class="i === tutorialStep ? 'w-5 bg-indigo-400' : 'w-1.5 bg-surface-600'"
          />
        </div>

        <!-- Navigation -->
        <div class="flex items-center justify-between">
          <button
            @click="prevStep"
            :disabled="tutorialStep === 0"
            class="flex items-center gap-1.5 text-xs font-bold text-slate-400 hover:text-white disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
          >
            <ChevronLeftIcon class="w-3.5 h-3.5" /> Précédent
          </button>
          <span class="text-[10px] text-slate-500 font-semibold">{{ tutorialStep + 1 }} / {{ tutorialSteps.length }}</span>
          <button
            @click="nextStep"
            class="flex items-center gap-1.5 text-xs font-bold px-3 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg transition-colors"
          >
            {{ isLastStep ? 'Terminer 🎉' : 'Suivant' }} <ChevronRightIcon v-if="!isLastStep" class="w-3.5 h-3.5" />
          </button>
        </div>

        <!-- Arrow pointer decoration (simple triangle) -->
        <div
          v-if="currentTutorialStep.position === 'right'"
          class="absolute -left-2 top-1/2 -translate-y-1/2 w-0 h-0 border-t-8 border-b-8 border-r-8 border-t-transparent border-b-transparent border-r-surface-600"
        />
        <div
          v-if="currentTutorialStep.position === 'bottom'"
          class="absolute -top-2 left-1/2 -translate-x-1/2 w-0 h-0 border-l-8 border-r-8 border-b-8 border-l-transparent border-r-transparent border-b-surface-600"
        />
        <div
          v-if="currentTutorialStep.position === 'left'"
          class="absolute -right-2 top-1/2 -translate-y-1/2 w-0 h-0 border-t-8 border-b-8 border-l-8 border-t-transparent border-b-transparent border-l-surface-600"
        />
      </div>
    </Transition>

    <!-- ── Highlight ring on targeted element ────────────────────────────── -->
    <!-- (handled by the z-index stacking: tutorial elements get z-[41]) -->

    <!-- ── Page content ────────────────────────────────────────────────────── -->
    <div class="max-w-6xl mx-auto px-6 py-10">

      <!-- Hero header -->
      <div
        id="home-welcome"
        class="relative mb-14 text-center overflow-hidden rounded-3xl bg-surface-900 border border-surface-800 p-10 lg:p-16"
        :class="{ 'ring-2 ring-indigo-400 ring-offset-2 ring-offset-surface-950 z-[41] relative': tutorialActive && currentTutorialStep.targetId === 'home-welcome' }"
      >
        <!-- Background glow -->
        <div class="absolute inset-0 -z-0 pointer-events-none">
          <div class="absolute top-0 left-1/2 -translate-x-1/2 w-[600px] h-[300px] bg-indigo-500/10 rounded-full blur-[80px]" />
          <div class="absolute bottom-0 right-0 w-[400px] h-[200px] bg-violet-500/10 rounded-full blur-[80px]" />
        </div>

        <!-- Animated badge -->
        <div class="relative z-10 flex justify-center mb-6">
          <span class="inline-flex items-center gap-2 px-4 py-1.5 bg-indigo-500/10 border border-indigo-500/20 rounded-full text-indigo-300 text-xs font-bold uppercase tracking-wider">
            <SparklesIcon class="w-3.5 h-3.5 animate-pulse" />
            Co-Pilote de Carrière IA
          </span>
        </div>

        <h1 class="relative z-10 text-4xl lg:text-5xl font-bold text-white mb-4 leading-tight">
          Bonjour, <span class="bg-gradient-to-r from-indigo-400 to-violet-400 bg-clip-text text-transparent">{{ userName }}</span> 👋
        </h1>
        <p class="relative z-10 text-slate-400 text-lg max-w-2xl mx-auto leading-relaxed mb-8">
          GoldArmy est ton arsenal complet pour décrocher le job de tes rêves.
          Explore chaque outil ci-dessous ou lance le tutoriel pour commencer.
        </p>

        <div class="relative z-10 flex flex-col sm:flex-row items-center justify-center gap-4" id="tutorial-end">
          <!-- Start tutorial -->
          <button
            @click="startTutorial"
            class="group flex items-center gap-2.5 px-6 py-3 bg-indigo-600 hover:bg-indigo-500 text-white font-bold rounded-xl shadow-lg shadow-indigo-500/20 transition-all hover:scale-105 active:scale-95"
          >
            <QuestionMarkCircleIcon class="w-5 h-5" />
            Lancer le tutoriel
            <ArrowRightIcon class="w-4 h-4 group-hover:translate-x-0.5 transition-transform" />
          </button>

          <!-- Go to sniper -->
          <button
            @click="router.push('/opportunities')"
            class="flex items-center gap-2 px-6 py-3 bg-surface-800 hover:bg-surface-700 border border-surface-700 text-white font-bold rounded-xl transition-all hover:scale-105 active:scale-95"
          >
            <MapIcon class="w-5 h-5 text-blue-400" />
            Trouver un emploi →
          </button>
        </div>
      </div>

      <!-- Features grid -->
      <div class="mb-6">
        <h2 class="text-xl font-bold text-white mb-1">Tes outils</h2>
        <p class="text-slate-500 text-sm">Clique sur une card pour accéder directement à la fonctionnalité.</p>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5">
        <div
          v-for="(feat, idx) in features"
          :key="feat.id"
          :id="`feature-${feat.id}`"
          @click="router.push(feat.route)"
          @mouseenter="hoveredCard = feat.id"
          @mouseleave="hoveredCard = null"
          :style="{
            transitionDelay: cardsReady ? `${idx * 70}ms` : '0ms',
            background: feat.gradient,
            opacity: cardsReady ? 1 : 0,
            transform: cardsReady ? 'translateY(0)' : 'translateY(24px)',
          }"
          class="relative group cursor-pointer rounded-2xl bg-surface-900 border transition-all duration-500 overflow-hidden select-none"
          :class="[
            feat.border,
            tutorialActive && currentTutorialStep.targetId === `feature-${feat.id}`
              ? 'ring-2 ring-indigo-400 ring-offset-2 ring-offset-surface-950 z-[41] shadow-2xl scale-[1.02]'
              : 'hover:scale-[1.02] hover:shadow-xl ' + feat.glow,
          ]"
        >
          <!-- Inner bg glow on hover -->
          <div
            class="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none"
            :class="`bg-gradient-to-br ${feat.color} opacity-5`"
          />

          <div class="relative p-6">
            <!-- Top row: icon + tag -->
            <div class="flex items-start justify-between mb-5">
              <div
                class="w-12 h-12 rounded-xl flex items-center justify-center text-2xl shadow-lg transition-transform duration-300 group-hover:scale-110 group-hover:rotate-3"
                :class="`bg-gradient-to-br ${feat.color}`"
              >
                {{ feat.emoji }}
              </div>
              <span
                class="text-[10px] font-black uppercase tracking-widest px-2.5 py-1 rounded-full"
                :class="feat.tagColor"
              >
                {{ feat.tag }}
              </span>
            </div>

            <!-- Name -->
            <h3 class="text-lg font-bold text-white mb-2 group-hover:text-white transition-colors">{{ feat.name }}</h3>

            <!-- Description -->
            <p class="text-slate-400 text-sm leading-relaxed mb-5 group-hover:text-slate-300 transition-colors">
              {{ feat.description }}
            </p>

            <!-- Stats row -->
            <div class="flex gap-4 mb-5">
              <div v-for="stat in feat.stats" :key="stat.label" class="flex-1">
                <p class="text-lg font-black text-white">{{ stat.value }}</p>
                <p class="text-[10px] text-slate-500 uppercase tracking-wide font-semibold">{{ stat.label }}</p>
              </div>
            </div>

            <!-- CTA -->
            <div
              class="flex items-center gap-2 text-sm font-bold transition-all duration-300 group-hover:gap-3"
              :class="`bg-gradient-to-r ${feat.color} bg-clip-text text-transparent`"
            >
              Accéder
              <ArrowRightIcon class="w-4 h-4 transition-transform duration-300 group-hover:translate-x-1" :class="`text-current`" style="color: inherit" />
            </div>
          </div>

          <!-- Bottom progress bar decorative -->
          <div class="absolute bottom-0 left-0 right-0 h-0.5 overflow-hidden">
            <div
              class="h-full transition-all duration-700 rounded-full"
              :class="`bg-gradient-to-r ${feat.color} ${hoveredCard === feat.id ? 'w-full' : 'w-0'}`"
            />
          </div>
        </div>
      </div>

      <!-- Quick stats footer -->
      <div class="mt-12 grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div
          v-for="(s, i) in [
            { v: '5', l: 'Outils IA', icon: '⚡' },
            { v: '24/7', l: 'Disponible', icon: '🌍' },
            { v: '100%', l: 'Gratuit pour commencer', icon: '🎁' },
            { v: '∞', l: 'Potentiel', icon: '🚀' },
          ]"
          :key="i"
          :style="{ transitionDelay: cardsReady ? `${(features.length + i) * 70}ms` : '0ms', opacity: cardsReady ? 1 : 0, transform: cardsReady ? 'translateY(0)' : 'translateY(24px)' }"
          class="flex flex-col items-center justify-center p-5 bg-surface-900 border border-surface-800 rounded-2xl text-center transition-all duration-500"
        >
          <span class="text-2xl mb-1">{{ s.icon }}</span>
          <p class="text-2xl font-black text-white mb-0.5">{{ s.v }}</p>
          <p class="text-[11px] text-slate-500 uppercase tracking-wide font-semibold">{{ s.l }}</p>
        </div>
      </div>

    </div>
  </div>
</template>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.3s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

.tooltip-enter-active { transition: all 0.25s cubic-bezier(0.34, 1.56, 0.64, 1); }
.tooltip-leave-active { transition: all 0.2s ease; }
.tooltip-enter-from { opacity: 0; transform: scale(0.85) translateY(8px); }
.tooltip-leave-to { opacity: 0; transform: scale(0.9); }
</style>
