<script setup>
import { ref, onMounted, onUnmounted, computed, nextTick } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// ── User greeting ─────────────────────────────────────────────────────────────
const userName = ref('là')
onMounted(async () => {
  const stored = localStorage.getItem('user')
  if (stored) {
    try { userName.value = JSON.parse(stored).email?.split('@')[0] ?? 'là' } catch {}
  }
  await nextTick()
  setTimeout(() => { ready.value = true }, 80)
})

const ready = ref(false)

// ── Feature cards ─────────────────────────────────────────────────────────────
const features = [
  {
    id: 'sniper',
    name: 'Sniper Search',
    route: '/opportunities',
    emoji: '🎯',
    tag: 'IA Puissante',
    color: '#3B82F6',
    colorBg: 'rgba(59,130,246,0.08)',
    colorBorder: 'rgba(59,130,246,0.2)',
    colorGlow: 'rgba(59,130,246,0.15)',
    gradient: 'linear-gradient(135deg,#1e3a5f 0%,#0f1e35 100%)',
    description: 'Recherche ultra-précise d\'offres. L\'IA analyse 50+ sources pour trouver les meilleures opportunités adaptées à ton profil.',
    tips: ['Donne ta ville et ton niveau d\'expérience pour de meilleurs résultats', 'Utilise des mots-clés précis comme "React senior Paris"'],
    screenshots: ['🗺️', '📊', '🔍'],
    stats: [{ v: '50+', l: 'Sources' }, { v: '94%', l: 'Précision' }],
  },
  {
    id: 'mentor',
    name: 'Mentor IA',
    route: '/mentor',
    emoji: '🧠',
    tag: 'Pro',
    color: '#8B5CF6',
    colorBg: 'rgba(139,92,246,0.08)',
    colorBorder: 'rgba(139,92,246,0.2)',
    colorGlow: 'rgba(139,92,246,0.15)',
    gradient: 'linear-gradient(135deg,#2d1b69 0%,#1a0f3d 100%)',
    description: 'Ton coach carrière IA. Analyse ton CV, génère des lettres de motivation et optimise chaque candidature en quelques secondes.',
    tips: ['Upload ton CV en PDF pour un audit complet', 'Colle l\'offre d\'emploi pour adapter ton CV automatiquement'],
    screenshots: ['📄', '✏️', '⭐'],
    stats: [{ v: '< 30s', l: 'Audit CV' }, { v: '+40%', l: 'Taux succès' }],
  },
  {
    id: 'interview',
    name: 'Entretien Vocal',
    route: '/interview',
    emoji: '🎙️',
    tag: 'Vocal IA',
    color: '#10B981',
    colorBg: 'rgba(16,185,129,0.08)',
    colorBorder: 'rgba(16,185,129,0.2)',
    colorGlow: 'rgba(16,185,129,0.15)',
    gradient: 'linear-gradient(135deg,#064e3b 0%,#022c22 100%)',
    description: 'Simule de vrais entretiens avec un recruteur IA vocal. Parle à voix haute et reçois un feedback instantané sur tes réponses.',
    tips: ['Utilise des écouteurs pour une meilleure reconnaissance vocale', 'Fais 2-3 sessions avant ton vrai entretien'],
    screenshots: ['🎤', '💬', '📈'],
    stats: [{ v: '10+', l: 'Questions' }, { v: 'Temps réel', l: 'Feedback' }],
  },
  {
    id: 'crm',
    name: 'CRM Candidatures',
    route: '/crm',
    emoji: '📋',
    tag: 'Kanban',
    color: '#F59E0B',
    colorBg: 'rgba(245,158,11,0.08)',
    colorBorder: 'rgba(245,158,11,0.2)',
    colorGlow: 'rgba(245,158,11,0.15)',
    gradient: 'linear-gradient(135deg,#451a03 0%,#27100a 100%)',
    description: 'Tableau Kanban pour suivre toutes tes candidatures. Glisse-dépose, génère des relances automatiques, ne rate plus rien.',
    tips: ['Glisse les cartes entre colonnes pour changer leur statut', 'Le bouton relance génère un email personnalisé en 1 clic'],
    screenshots: ['🗂️', '→', '✅'],
    stats: [{ v: '5', l: 'Colonnes' }, { v: 'Auto', l: 'Relances' }],
  },
  {
    id: 'network',
    name: 'Réseau Pro',
    route: '/network',
    emoji: '🤝',
    tag: 'Networking',
    color: '#F43F5E',
    colorBg: 'rgba(244,63,94,0.08)',
    colorBorder: 'rgba(244,63,94,0.2)',
    colorGlow: 'rgba(244,63,94,0.15)',
    gradient: 'linear-gradient(135deg,#4c0519 0%,#2d020e 100%)',
    description: 'Trouve les RH et décideurs des entreprises cibles. L\'IA rédige des emails d\'approche ultra-personnalisés pour maximiser tes réponses.',
    tips: ['Commence par les entreprises dans ta zone géographique', 'L\'IA adapte le ton de l\'email selon le poste visé'],
    screenshots: ['👥', '✉️', '💼'],
    stats: [{ v: 'Auto', l: 'Contacts' }, { v: '∞', l: 'Emails IA' }],
  },
]

// carousel per card
const carouselIndex = ref(features.map(() => 0))
function nextSlide(i) { carouselIndex.value[i] = (carouselIndex.value[i] + 1) % features[i].screenshots.length }
function prevSlide(i) { carouselIndex.value[i] = (carouselIndex.value[i] - 1 + features[i].screenshots.length) % features[i].screenshots.length }

// 3D tilt
const tilts = ref(features.map(() => ({ x: 0, y: 0 })))
function onMouseMove(e, idx) {
  const card = e.currentTarget
  const rect = card.getBoundingClientRect()
  const cx = (e.clientX - rect.left) / rect.width - 0.5
  const cy = (e.clientY - rect.top) / rect.height - 0.5
  tilts.value[idx] = { x: cy * -12, y: cx * 12 }
}
function onMouseLeave(idx) { tilts.value[idx] = { x: 0, y: 0 } }

// Global tips
const tips = [
  { icon: '💡', title: 'Commence par ton CV', text: 'Upload ton CV dans le Mentor IA d\'abord. Tous les autres outils seront plus précis.' },
  { icon: '⚡', title: 'Utilise Sniper quotidiennement', text: 'Lance une recherche chaque matin. Les offres les plus récentes reçoivent 3x plus de réponses.' },
  { icon: '🎯', title: 'Candidature ciblée > masse', text: 'Adapte ton CV pour chaque offre avec le Mentor. 5 candidatures ciblées valent mieux que 50 génériques.' },
  { icon: '📞', title: 'Relance après 7 jours', text: 'Utilise le CRM pour programmer tes relances. Les candidats qui relancent obtiennent 30% de réponses en plus.' },
  { icon: '🤝', title: 'Réseau d\'abord', text: '70% des emplois ne sont pas publiés. Utilise l\'outil Réseau pour accéder au marché caché.' },
  { icon: '🎙️', title: 'Pratique l\'entretien', text: 'Fais au moins 3 simulations vocales avant un vrai entretien. La confiance se construit par la répétition.' },
]
const activeTip = ref(0)
let tipInterval = null
onMounted(() => { tipInterval = setInterval(() => { activeTip.value = (activeTip.value + 1) % tips.length }, 4000) })
onUnmounted(() => clearInterval(tipInterval))

// ── Tutorial ─────────────────────────────────────────────────────────────────
const tutorialActive = ref(false)
const tutorialStep = ref(0)
const tooltipStyle = ref({})

const tutorialSteps = [
  { targetId: 'home-hero', title: '👋 Bienvenue sur GoldArmy !', text: 'Cette page résume tout ce que tu peux faire avec GoldArmy. Chaque card correspond à un outil IA. Clique sur une card pour y accéder.', pos: 'bottom' },
  { targetId: 'feature-card-sniper', title: '🎯 Sniper Search', text: 'Lance ici ta recherche d\'emploi ultra-précise. L\'IA scanne 50+ sources et filtre les meilleures offres selon ton profil.', pos: 'right' },
  { targetId: 'feature-card-mentor', title: '🧠 Mentor IA', text: 'Upload ton CV et l\'IA l\'analyse en 30 secondes. Elle adapte aussi ton CV pour chaque offre et génère tes lettres de motivation.', pos: 'right' },
  { targetId: 'feature-card-interview', title: '🎙️ Entretien Vocal', text: 'Simule un vrai entretien à voix haute ! L\'IA joue le rôle d\'un recruteur et te donne un feedback instantané sur tes réponses.', pos: 'left' },
  { targetId: 'feature-card-crm', title: '📋 CRM Candidatures', text: 'Suis toutes tes candidatures dans un tableau Kanban. Glisse les cartes pour changer leur statut, génère des relances en 1 clic.', pos: 'left' },
  { targetId: 'feature-card-network', title: '🤝 Réseau Pro', text: 'Accède au marché caché de l\'emploi. L\'IA trouve les décideurs des entreprises cibles et rédige des emails d\'approche personnalisés.', pos: 'right' },
  { targetId: 'home-tips', title: '💡 Conseils Pro', text: 'Ces conseils s\'actualisent automatiquement. Suis-les pour maximiser tes chances de décrocher un entretien rapidement.', pos: 'top' },
]

const currentStep = computed(() => tutorialSteps[tutorialStep.value])
const isLast = computed(() => tutorialStep.value === tutorialSteps.length - 1)

function startTutorial() {
  tutorialStep.value = 0
  tutorialActive.value = true
  updateTooltipPos()
}
function nextStep() { if (isLast.value) { closeTutorial(); return } tutorialStep.value++; updateTooltipPos() }
function prevStep() { if (tutorialStep.value > 0) { tutorialStep.value--; updateTooltipPos() } }
function closeTutorial() { tutorialActive.value = false }

function updateTooltipPos() {
  nextTick(() => {
    const el = document.getElementById(currentStep.value.targetId)
    if (!el) return
    el.scrollIntoView({ behavior: 'smooth', block: 'center' })
    setTimeout(() => {
      const r = el.getBoundingClientRect()
      const pos = currentStep.value.pos
      const TW = 320, TH = 220
      let style = {}
      if (pos === 'bottom') style = { top: r.bottom + 16 + 'px', left: Math.min(window.innerWidth - TW - 8, Math.max(8, r.left + r.width / 2 - TW / 2)) + 'px' }
      else if (pos === 'top') style = { top: r.top - TH - 16 + 'px', left: Math.min(window.innerWidth - TW - 8, Math.max(8, r.left + r.width / 2 - TW / 2)) + 'px' }
      else if (pos === 'right') style = { top: Math.min(window.innerHeight - TH - 8, Math.max(8, r.top + r.height / 2 - TH / 2)) + 'px', left: r.right + 16 + 'px' }
      else if (pos === 'left') style = { top: Math.min(window.innerHeight - TH - 8, Math.max(8, r.top + r.height / 2 - TH / 2)) + 'px', left: r.left - TW - 16 + 'px' }
      tooltipStyle.value = style
    }, 400)
  })
}

// scroll listener keeps tooltip pinned
function onScroll() { if (tutorialActive.value) updateTooltipPos() }
onMounted(() => {
  document.querySelector('main')?.addEventListener('scroll', onScroll)
  window.addEventListener('keydown', (e) => { if (e.key === 'Escape') closeTutorial() })
})
onUnmounted(() => { document.querySelector('main')?.removeEventListener('scroll', onScroll) })
</script>

<template>
  <div class="relative min-h-full bg-surface-950 overflow-x-hidden">

    <!-- ══ Tutorial overlay ══════════════════════════════════════════════════ -->
    <Transition name="fade">
      <div v-if="tutorialActive" class="fixed inset-0 bg-black/65 backdrop-blur-sm z-40 pointer-events-none" />
    </Transition>

    <!-- Tutorial tooltip — FIXED so it stays visible while scrolling -->
    <Transition name="pop">
      <div v-if="tutorialActive" :style="tooltipStyle"
        class="fixed z-50 w-80 bg-[#1e2030] border border-indigo-500/30 rounded-2xl shadow-2xl shadow-indigo-500/10 p-5 pointer-events-auto"
      >
        <!-- Glow -->
        <div class="absolute inset-0 rounded-2xl bg-gradient-to-br from-indigo-500/5 to-violet-500/5 pointer-events-none" />

        <div class="relative">
          <div class="flex items-start justify-between mb-3">
            <h3 class="font-bold text-white text-sm leading-tight">{{ currentStep.title }}</h3>
            <button @click="closeTutorial" class="text-slate-500 hover:text-white transition-colors ml-3 shrink-0 p-1 hover:bg-white/5 rounded-lg">
              ✕
            </button>
          </div>
          <p class="text-slate-300 text-xs leading-relaxed mb-4">{{ currentStep.text }}</p>

          <!-- Progress dots -->
          <div class="flex items-center gap-1.5 mb-4">
            <div v-for="(_, i) in tutorialSteps" :key="i"
              class="h-1 rounded-full transition-all duration-300 cursor-pointer"
              :class="i === tutorialStep ? 'w-5 bg-indigo-400' : i < tutorialStep ? 'w-2 bg-indigo-600/50' : 'w-2 bg-surface-700'"
              @click="tutorialStep = i; updateTooltipPos()"
            />
          </div>

          <div class="flex items-center justify-between">
            <button @click="prevStep" :disabled="tutorialStep === 0"
              class="text-xs font-bold text-slate-400 hover:text-white disabled:opacity-30 disabled:cursor-not-allowed transition-colors px-2 py-1 rounded-lg hover:bg-white/5"
            >← Préc.</button>
            <span class="text-[10px] text-slate-600 font-semibold">{{ tutorialStep + 1 }}/{{ tutorialSteps.length }}</span>
            <button @click="nextStep"
              class="text-xs font-bold px-4 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg transition-all hover:shadow-lg hover:shadow-indigo-500/20"
            >{{ isLast ? '🎉 Terminer' : 'Suivant →' }}</button>
          </div>
        </div>
      </div>
    </Transition>

    <div class="max-w-6xl mx-auto px-4 sm:px-6 py-8 space-y-16">

      <!-- ══ HERO ══════════════════════════════════════════════════════════════ -->
      <section id="home-hero"
        class="relative rounded-3xl overflow-hidden border border-surface-800 min-h-[340px] flex flex-col items-center justify-center text-center p-10 lg:p-16"
        :class="{ 'ring-2 ring-indigo-400 ring-offset-2 ring-offset-surface-950 z-[41] relative': tutorialActive && currentStep.targetId === 'home-hero' }"
        :style="{ opacity: ready ? 1 : 0, transform: ready ? 'none' : 'translateY(20px)', transition: 'all 0.7s cubic-bezier(.22,1,.36,1)' }"
      >
        <!-- animated mesh bg -->
        <div class="absolute inset-0 -z-0">
          <div class="absolute inset-0 bg-[radial-gradient(ellipse_at_top,rgba(99,102,241,0.12)_0%,transparent_60%)]" />
          <div class="absolute inset-0 bg-[radial-gradient(ellipse_at_bottom_right,rgba(139,92,246,0.1)_0%,transparent_60%)]" />
          <!-- Animated grid -->
          <div class="absolute inset-0 opacity-[0.04]" style="background-image: linear-gradient(rgba(99,102,241,.5) 1px, transparent 1px), linear-gradient(90deg, rgba(99,102,241,.5) 1px, transparent 1px); background-size: 40px 40px;" />
          <!-- Floating orbs -->
          <div class="absolute top-8 left-16 w-40 h-40 bg-indigo-500/10 rounded-full blur-3xl animate-pulse" />
          <div class="absolute bottom-8 right-16 w-56 h-56 bg-violet-500/10 rounded-full blur-3xl animate-pulse" style="animation-delay:1s" />
          <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-80 h-80 bg-indigo-600/5 rounded-full blur-3xl animate-pulse" style="animation-delay:2s" />
        </div>

        <!-- Orbiting badge -->
        <div class="relative z-10 mb-5 flex justify-center">
          <span class="inline-flex items-center gap-2 px-4 py-1.5 bg-indigo-500/10 border border-indigo-500/20 rounded-full text-indigo-300 text-xs font-bold uppercase tracking-wider">
            <span class="w-1.5 h-1.5 bg-indigo-400 rounded-full animate-ping" />
            Co-Pilote de Carrière IA
          </span>
        </div>

        <h1 class="relative z-10 text-4xl lg:text-6xl font-black text-white mb-4 leading-tight tracking-tight">
          Bonjour,
          <span class="relative inline-block">
            <span class="bg-gradient-to-r from-indigo-400 via-violet-400 to-blue-400 bg-clip-text text-transparent">{{ userName }}</span>
            <span class="absolute -bottom-1 left-0 right-0 h-px bg-gradient-to-r from-indigo-400/50 via-violet-400/50 to-transparent" />
          </span>
          👋
        </h1>
        <p class="relative z-10 text-slate-400 text-base lg:text-lg max-w-2xl leading-relaxed mb-8">
          Ton arsenal complet pour décrocher le job de tes rêves.<br class="hidden md:block" />
          Explore chaque outil ou lance le tutoriel interactif.
        </p>

        <div class="relative z-10 flex flex-col sm:flex-row items-center justify-center gap-3">
          <button @click="startTutorial"
            class="group relative overflow-hidden flex items-center gap-2.5 px-7 py-3.5 bg-indigo-600 hover:bg-indigo-500 text-white font-bold rounded-2xl shadow-xl shadow-indigo-500/25 transition-all hover:scale-105 active:scale-95 hover:shadow-indigo-500/40"
          >
            <span class="absolute inset-0 bg-gradient-to-r from-white/0 via-white/10 to-white/0 translate-x-[-200%] group-hover:translate-x-[200%] transition-transform duration-700" />
            ❓ Lancer le tutoriel
            <span class="text-indigo-200 text-sm">→</span>
          </button>
          <button @click="router.push('/opportunities')"
            class="flex items-center gap-2.5 px-7 py-3.5 bg-surface-800/80 hover:bg-surface-700 backdrop-blur border border-surface-700 text-white font-bold rounded-2xl transition-all hover:scale-105 active:scale-95"
          >
            🎯 Trouver un emploi
          </button>
        </div>

        <!-- Stats row -->
        <div class="relative z-10 mt-10 flex items-center gap-8 text-center flex-wrap justify-center">
          <div v-for="s in [{v:'5', l:'Outils IA'}, {v:'50+', l:'Sources scannées'}, {v:'< 30s', l:'Analyse CV'}, {v:'∞', l:'Potentiel'}]" :key="s.l">
            <p class="text-2xl font-black text-white">{{ s.v }}</p>
            <p class="text-[11px] text-slate-500 uppercase tracking-wider font-semibold">{{ s.l }}</p>
          </div>
        </div>
      </section>

      <!-- ══ FEATURE CARDS (3-D tilt) ════════════════════════════════════════ -->
      <section>
        <div class="mb-8 flex items-end justify-between">
          <div>
            <h2 class="text-2xl font-black text-white mb-1">Tes outils IA</h2>
            <p class="text-slate-500 text-sm">Clique sur une card pour y accéder · Survole pour l'effet 3D</p>
          </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5">
          <div
            v-for="(feat, idx) in features" :key="feat.id"
            :id="`feature-card-${feat.id}`"
            @click="router.push(feat.route)"
            @mousemove="(e) => onMouseMove(e, idx)"
            @mouseleave="onMouseLeave(idx)"
            :style="{
              transition: 'transform 0.15s ease, box-shadow 0.3s ease, opacity 0.6s cubic-bezier(.22,1,.36,1)',
              transitionDelay: ready ? idx * 70 + 'ms' : '0ms',
              opacity: ready ? 1 : 0,
              transform: `perspective(900px) rotateX(${tilts[idx].x}deg) rotateY(${tilts[idx].y}deg) ${ready ? 'translateY(0px)' : 'translateY(24px)'}`,
              boxShadow: tilts[idx].x || tilts[idx].y ? `0 25px 60px ${feat.colorGlow}` : '0 4px 20px rgba(0,0,0,0.3)',
              background: feat.gradient,
              border: tutorialActive && currentStep.targetId === `feature-card-${feat.id}` ? `2px solid #818CF8` : `1px solid ${feat.colorBorder}`,
            }"
            class="relative rounded-2xl cursor-pointer overflow-hidden group select-none"
            :class="tutorialActive && currentStep.targetId === `feature-card-${feat.id}` ? 'ring-2 ring-indigo-400 ring-offset-1 ring-offset-surface-950 z-[41]' : ''"
          >
            <!-- Card glow overlay on hover -->
            <div class="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none"
              :style="{ background: `radial-gradient(ellipse at 30% 30%, ${feat.colorBg} 0%, transparent 70%)` }" />

            <!-- Inner shine -->
            <div class="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-700 pointer-events-none"
              style="background: linear-gradient(135deg, rgba(255,255,255,0.04) 0%, transparent 50%)" />

            <div class="relative p-6">
              <!-- Top row -->
              <div class="flex items-start justify-between mb-5">
                <div class="relative">
                  <div class="w-14 h-14 rounded-2xl flex items-center justify-center text-3xl shadow-xl transition-transform duration-300 group-hover:scale-110 group-hover:-rotate-3"
                    :style="{ background: `linear-gradient(135deg, ${feat.color}33, ${feat.color}11)`, border: `1px solid ${feat.color}30` }"
                  >{{ feat.emoji }}</div>
                  <!-- Pulse ring -->
                  <div class="absolute inset-0 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-300 animate-ping"
                    :style="{ border: `1px solid ${feat.color}50` }" />
                </div>
                <span class="text-[10px] font-black uppercase tracking-widest px-2.5 py-1 rounded-full"
                  :style="{ background: feat.colorBg, color: feat.color, border: `1px solid ${feat.colorBorder}` }">{{ feat.tag }}</span>
              </div>

              <!-- Name + desc -->
              <h3 class="text-lg font-bold text-white mb-2">{{ feat.name }}</h3>
              <p class="text-slate-400 text-xs leading-relaxed mb-4 group-hover:text-slate-300 transition-colors">{{ feat.description }}</p>

              <!-- Mini carousel  -->
              <div class="relative mb-4 bg-black/20 rounded-xl overflow-hidden h-16 flex items-center justify-center border border-white/5">
                <Transition name="slide" mode="out-in">
                  <div :key="carouselIndex[idx]" class="flex items-center justify-around w-full px-4">
                    <div v-for="(s, si) in feat.screenshots" :key="si"
                      class="w-8 h-8 rounded-lg flex items-center justify-center text-lg transition-all duration-200"
                      :class="si === carouselIndex[idx] ? 'bg-white/10 scale-125' : 'opacity-40 scale-90'"
                    >{{ s }}</div>
                  </div>
                </Transition>
                <!-- Carousel controls -->
                <button @click.stop="prevSlide(idx)" class="absolute left-1 top-1/2 -translate-y-1/2 w-5 h-5 rounded-full bg-black/30 hover:bg-black/60 flex items-center justify-center text-white text-xs transition-all opacity-0 group-hover:opacity-100">‹</button>
                <button @click.stop="nextSlide(idx)" class="absolute right-1 top-1/2 -translate-y-1/2 w-5 h-5 rounded-full bg-black/30 hover:bg-black/60 flex items-center justify-center text-white text-xs transition-all opacity-0 group-hover:opacity-100">›</button>
              </div>

              <!-- Stats -->
              <div class="flex gap-4 mb-4">
                <div v-for="s in feat.stats" :key="s.l" class="flex-1 bg-black/20 rounded-xl p-2.5 text-center border border-white/5">
                  <p class="text-base font-black text-white">{{ s.v }}</p>
                  <p class="text-[9px] text-slate-500 uppercase tracking-wide font-semibold">{{ s.l }}</p>
                </div>
              </div>

              <!-- Tips mini -->
              <div class="space-y-1.5 mb-5">
                <p class="text-[9px] text-slate-600 uppercase font-black tracking-widest">💡 Conseil</p>
                <p class="text-[11px] text-slate-400 leading-relaxed">{{ feat.tips[0] }}</p>
              </div>

              <!-- CTA -->
              <div class="flex items-center gap-2 font-bold text-sm transition-all duration-300 group-hover:gap-3" :style="{ color: feat.color }">
                Accéder à {{ feat.name }}
                <span class="transition-transform duration-300 group-hover:translate-x-1">→</span>
              </div>
            </div>

            <!-- Bottom accent bar -->
            <div class="absolute bottom-0 left-0 right-0 h-0.5"
              :style="{ background: `linear-gradient(90deg, transparent, ${feat.color}, transparent)`, opacity: tilts[idx].x || tilts[idx].y ? 1 : 0, transition: 'opacity 0.3s' }" />
          </div>
        </div>
      </section>

      <!-- ══ PRO TIPS SECTION ════════════════════════════════════════════════ -->
      <section id="home-tips"
        :style="{ opacity: ready ? 1 : 0, transform: ready ? 'none' : 'translateY(24px)', transition: 'all 0.7s cubic-bezier(.22,1,.36,1) 0.5s' }"
        :class="tutorialActive && currentStep.targetId === 'home-tips' ? 'ring-2 ring-indigo-400 ring-offset-2 ring-offset-surface-950 z-[41] relative rounded-3xl' : ''"
      >
        <div class="mb-6">
          <h2 class="text-2xl font-black text-white mb-1">💡 Conseils Pro</h2>
          <p class="text-slate-500 text-sm">Stratégies pour maximiser tes chances de succès</p>
        </div>

        <!-- Active tip highlight -->
        <div class="mb-6 relative overflow-hidden rounded-2xl border border-indigo-500/20 bg-[radial-gradient(ellipse_at_top_left,rgba(99,102,241,0.1),transparent_60%)] p-6">
          <div class="absolute top-0 right-0 w-40 h-40 bg-indigo-500/5 rounded-full blur-2xl" />
          <Transition name="tip" mode="out-in">
            <div :key="activeTip" class="relative">
              <span class="text-3xl mb-3 block">{{ tips[activeTip].icon }}</span>
              <h3 class="text-lg font-bold text-white mb-2">{{ tips[activeTip].title }}</h3>
              <p class="text-slate-300 text-sm leading-relaxed">{{ tips[activeTip].text }}</p>
            </div>
          </Transition>
          <!-- Dots -->
          <div class="flex gap-1.5 mt-5">
            <button v-for="(_, i) in tips" :key="i" @click="activeTip = i"
              class="h-1 rounded-full transition-all duration-300"
              :class="i === activeTip ? 'w-6 bg-indigo-400' : 'w-2 bg-surface-700 hover:bg-surface-600'"
            />
          </div>
        </div>

        <!-- Tips grid -->
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
          <button v-for="(tip, i) in tips" :key="i" @click="activeTip = i"
            class="text-left p-4 rounded-2xl border transition-all duration-200 group"
            :class="i === activeTip
              ? 'bg-indigo-500/10 border-indigo-500/30 text-white'
              : 'bg-surface-900 border-surface-800 hover:border-surface-700 hover:bg-surface-800'"
          >
            <span class="text-xl mb-2 block">{{ tip.icon }}</span>
            <p class="text-xs font-bold" :class="i === activeTip ? 'text-indigo-200' : 'text-slate-300 group-hover:text-white'">{{ tip.title }}</p>
          </button>
        </div>
      </section>

      <!-- ══ QUICK-START CTA ════════════════════════════════════════════════ -->
      <section
        class="relative rounded-3xl overflow-hidden border border-surface-800 p-10 text-center"
        :style="{ opacity: ready ? 1 : 0, transform: ready ? 'none' : 'translateY(24px)', transition: 'all 0.7s cubic-bezier(.22,1,.36,1) 0.65s' }"
      >
        <div class="absolute inset-0 bg-[radial-gradient(ellipse_at_center,rgba(99,102,241,0.08),transparent_60%)] pointer-events-none" />
        <p class="relative z-10 text-slate-400 text-sm uppercase font-black tracking-widest mb-3">Lance-toi maintenant</p>
        <h2 class="relative z-10 text-3xl font-black text-white mb-6">Prêt à décrocher ton prochain job ?</h2>
        <div class="relative z-10 flex flex-col sm:flex-row items-center justify-center gap-3">
          <button @click="router.push('/mentor')" class="group flex items-center gap-2.5 px-7 py-3.5 bg-violet-600 hover:bg-violet-500 text-white font-bold rounded-2xl shadow-xl shadow-violet-500/20 transition-all hover:scale-105">
            🧠 Analyser mon CV
          </button>
          <button @click="router.push('/opportunities')" class="flex items-center gap-2.5 px-7 py-3.5 bg-blue-600/20 hover:bg-blue-600/30 border border-blue-500/30 text-blue-300 font-bold rounded-2xl transition-all hover:scale-105">
            🎯 Rechercher un emploi
          </button>
        </div>
      </section>

    </div>
  </div>
</template>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.3s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

.pop-enter-active { transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1); }
.pop-leave-active { transition: all 0.2s ease; }
.pop-enter-from { opacity: 0; transform: scale(0.8) translateY(8px); }
.pop-leave-to { opacity: 0; transform: scale(0.9); }

.slide-enter-active, .slide-leave-active { transition: all 0.25s ease; }
.slide-enter-from { opacity: 0; transform: translateX(20px); }
.slide-leave-to { opacity: 0; transform: translateX(-20px); }

.tip-enter-active { transition: all 0.4s cubic-bezier(0.22,1,0.36,1); }
.tip-leave-active { transition: all 0.25s ease; }
.tip-enter-from { opacity: 0; transform: translateY(12px); }
.tip-leave-to { opacity: 0; transform: translateY(-8px); }
</style>
