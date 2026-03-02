<script setup>
import { ref, onMounted, onUnmounted, computed, nextTick } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const ready = ref(false)
const userName = ref('là')

onMounted(async () => {
  const stored = localStorage.getItem('user')
  if (stored) { try { userName.value = JSON.parse(stored).email?.split('@')[0] ?? 'là' } catch {} }
  await nextTick()
  setTimeout(() => { ready.value = true }, 100)

  // Tips auto-cycle
  tipInterval = setInterval(() => { activeTip.value = (activeTip.value + 1) % tips.length }, 4000)
  window.addEventListener('keydown', (e) => { if (e.key === 'Escape') closeTutorial() })
})
onUnmounted(() => { clearInterval(tipInterval) })

// ── Floating badges in hero ───────────────────────────────────────────────────
const floatingBadges = [
  { icon: '🎯', label: 'Job Search',    color: '#3B82F6', delay: '0s',    x: '8%',  y: '20%', size: 'lg' },
  { icon: '🧠', label: 'Mentor IA',    color: '#8B5CF6', delay: '0.6s',  x: '82%', y: '15%', size: 'lg' },
  { icon: '🎙️', label: 'Entretien',   color: '#10B981', delay: '1.2s',  x: '5%',  y: '65%', size: 'md' },
  { icon: '📋', label: 'CRM',          color: '#F59E0B', delay: '0.3s',  x: '88%', y: '60%', size: 'md' },
  { icon: '🤝', label: 'Réseau',       color: '#F43F5E', delay: '0.9s',  x: '50%', y: '88%', size: 'sm' },
  { icon: '📄', label: 'CV',           color: '#22D3EE', delay: '1.5s',  x: '15%', y: '85%', size: 'sm' },
  { icon: '⚡', label: 'IA',           color: '#A78BFA', delay: '1.8s',  x: '75%', y: '82%', size: 'sm' },
]

// ── Feature cards ─────────────────────────────────────────────────────────────
const features = [
  {
    id: 'sniper', name: 'Sniper Search', route: '/opportunities',
    emoji: '🎯', tag: 'IA Puissante', tagColor: '#3B82F6',
    color: '#3B82F6', border: 'rgba(59,130,246,0.25)',
    panelBg: 'linear-gradient(135deg,#0d2045 0%,#0a1628 50%,#071020 100%)',
    panelAccent: 'rgba(59,130,246,0.15)',
    description: 'Recherche ultra-précise d\'offres d\'emploi. L\'IA analyse simultanément 50+ sources pour trouver les opportunités parfaitement adaptées à ton profil et ta localisation.',
    tip: 'Utilise des mots-clés précis : poste + ville + expérience',
    stats: [{v:'50+',l:'Sources'},{v:'94%',l:'Précision'},{v:'< 5s',l:'Résultats'}],
    features: ['Filtres géographiques intelligents','Matching CV automatique','Alertes temps réel'],
    panelIcons: [
      { icon: '🗺️', label: 'Carte', x: '12%', y: '25%' },
      { icon: '📊', label: 'Stats', x: '50%', y: '15%' },
      { icon: '🔍', label: 'Scan',  x: '78%', y: '30%' },
      { icon: '💼', label: 'Offre', x: '25%', y: '65%' },
      { icon: '✅', label: 'Match', x: '65%', y: '62%' },
    ],
  },
  {
    id: 'mentor', name: 'Mentor IA', route: '/mentor',
    emoji: '🧠', tag: 'Pro', tagColor: '#8B5CF6',
    color: '#8B5CF6', border: 'rgba(139,92,246,0.25)',
    panelBg: 'linear-gradient(135deg,#1e0a4e 0%,#15073a 50%,#0d0425 100%)',
    panelAccent: 'rgba(139,92,246,0.15)',
    description: 'Ton coach carrière personnel propulsé par l\'IA. Analyse ton CV en 30s, identifie les lacunes, adapte chaque candidature et génère des lettres de motivation percutantes.',
    tip: 'Upload ton PDF — le Mentor fait le reste en 30 secondes',
    stats: [{v:'< 30s',l:'Audit'},{v:'+40%',l:'Succès'},{v:'100%',l:'Personnalisé'}],
    features: ['Audit CV détaillé','Adaptation par offre','Lettres de motivation IA'],
    panelIcons: [
      { icon: '📄', label: 'CV',      x: '15%', y: '20%' },
      { icon: '🔬', label: 'Analyse', x: '55%', y: '15%' },
      { icon: '✏️', label: 'Edit',    x: '80%', y: '28%' },
      { icon: '⭐', label: 'Score',   x: '30%', y: '65%' },
      { icon: '📝', label: 'Lettre',  x: '68%', y: '62%' },
    ],
  },
  {
    id: 'interview', name: 'Entretien Vocal', route: '/interview',
    emoji: '🎙️', tag: 'Vocal IA', tagColor: '#10B981',
    color: '#10B981', border: 'rgba(16,185,129,0.25)',
    panelBg: 'linear-gradient(135deg,#022c1a 0%,#011d12 50%,#000e09 100%)',
    panelAccent: 'rgba(16,185,129,0.15)',
    description: 'Simulation d\'entretien en temps réel avec un recruteur IA vocal. Parle à voix haute, affine tes réponses et construis ta confiance avant le grand jour.',
    tip: 'Fais 3 sessions d\'entraînement avant ton vrai entretien',
    stats: [{v:'10+',l:'Questions'},{v:'100%',l:'Vocal'},{v:'Temps réel',l:'Feedback'}],
    features: ['Recruteur IA conversationnel','Évaluation des réponses','Score de confiance'],
    panelIcons: [
      { icon: '🎤', label: 'Voix',    x: '50%', y: '18%' },
      { icon: '💬', label: 'Dialog',  x: '15%', y: '38%' },
      { icon: '🤖', label: 'IA',      x: '78%', y: '35%' },
      { icon: '📈', label: 'Score',   x: '28%', y: '66%' },
      { icon: '🏆', label: 'Succès',  x: '68%', y: '64%' },
    ],
  },
  {
    id: 'crm', name: 'CRM Candidatures', route: '/crm',
    emoji: '📋', tag: 'Kanban', tagColor: '#F59E0B',
    color: '#F59E0B', border: 'rgba(245,158,11,0.25)',
    panelBg: 'linear-gradient(135deg,#2d1700 0%,#1e1000 50%,#0f0800 100%)',
    panelAccent: 'rgba(245,158,11,0.15)',
    description: 'Tableau Kanban intelligent pour gérer toutes tes candidatures. Glisse-dépose entre colonnes, génère des relances automatiques et ne laisse plus passer une opportunité.',
    tip: 'Génère une relance IA en 1 clic si tu n\'as pas de réponse après 7 jours',
    stats: [{v:'5',l:'Colonnes'},{v:'Auto',l:'Relances'},{v:'∞',l:'Candidatures'}],
    features: ['Glisser-déposer Kanban','Emails de relance IA','Historique complet'],
    panelIcons: [
      { icon: '🗂️', label: 'Board',   x: '50%', y: '18%' },
      { icon: '→',  label: 'Move',    x: '18%', y: '40%' },
      { icon: '✅', label: 'Done',    x: '80%', y: '38%' },
      { icon: '📧', label: 'Email',   x: '28%', y: '68%' },
      { icon: '📅', label: 'Date',    x: '68%', y: '66%' },
    ],
  },
  {
    id: 'network', name: 'Réseau Pro', route: '/network',
    emoji: '🤝', tag: 'Networking', tagColor: '#F43F5E',
    color: '#F43F5E', border: 'rgba(244,63,94,0.25)',
    panelBg: 'linear-gradient(135deg,#2d0010 0%,#1e000a 50%,#100005 100%)',
    panelAccent: 'rgba(244,63,94,0.15)',
    description: 'Accède au marché caché de l\'emploi. Trouve les RH et décideurs clés des entreprises cibles, puis laisse l\'IA rédiger des emails d\'approche ultra-personnalisés pour toi.',
    tip: '70% des emplois ne sont pas publiés — le réseau est clé',
    stats: [{v:'Auto',l:'Contacts'},{v:'∞',l:'Emails IA'},{v:'70%',l:'Marché caché'}],
    features: ['Recherche de décideurs','Emails personnalisés IA','Carnet d\'adresses'],
    panelIcons: [
      { icon: '👥', label: 'Réseau',  x: '50%', y: '18%' },
      { icon: '🏢', label: 'Société', x: '15%', y: '38%' },
      { icon: '👤', label: 'RH',      x: '80%', y: '35%' },
      { icon: '✉️', label: 'Email',   x: '28%', y: '68%' },
      { icon: '💼', label: 'Poste',   x: '68%', y: '66%' },
    ],
  },
]

// hover pan effect per card panel
const panelMousePos = ref(features.map(() => ({ x: 50, y: 50 })))
function onPanelMove(e, idx) {
  const el = e.currentTarget
  const r = el.getBoundingClientRect()
  panelMousePos.value[idx] = { x: ((e.clientX - r.left) / r.width) * 100, y: ((e.clientY - r.top) / r.height) * 100 }
}
function onPanelLeave(idx) { panelMousePos.value[idx] = { x: 50, y: 50 } }

// 3D tilt
const tilts = ref(features.map(() => ({ x: 0, y: 0 })))
function onCardMove(e, idx) {
  const r = e.currentTarget.getBoundingClientRect()
  const cx = (e.clientX - r.left) / r.width - 0.5
  const cy = (e.clientY - r.top) / r.height - 0.5
  tilts.value[idx] = { x: cy * -10, y: cx * 10 }
}
function onCardLeave(idx) { tilts.value[idx] = { x: 0, y: 0 } }

// Active feature details panel (show/hide on click in card panel area)
const expandedCard = ref(null)
function toggleCard(id) { expandedCard.value = expandedCard.value === id ? null : id }

// Tips
const tips = [
  { icon: '💡', title: 'Commence par ton CV', text: 'Upload ton CV dans le Mentor IA d\'abord. Tous les autres outils seront plus précis avec ton profil.' },
  { icon: '⚡', title: 'Sniper quotidien', text: 'Lance une recherche chaque matin. Les offres fraîches reçoivent 3× plus de réponses.' },
  { icon: '🎯', title: 'Qualité > Quantité', text: '5 candidatures ciblées valent mieux que 50 génériques. Adapte chaque CV avec le Mentor.' },
  { icon: '📞', title: 'Relance à J+7', text: 'Les candidats qui relancent obtiennent 30% de réponses en plus. Utilise le CRM pour ça.' },
  { icon: '🤝', title: 'Réseau d\'abord', text: '70% des emplois ne sont pas publiés. Utilise l\'outil Réseau pour y accéder.' },
  { icon: '🎙️', title: 'Pratique l\'entretien', text: 'La confiance se construit par la répétition. Fais 3 simulations avant ton vrai entretien.' },
]
const activeTip = ref(0)
let tipInterval = null

// Tutorial
const tutorialActive = ref(false)
const tutorialStep = ref(0)
const tutorialSteps = [
  { targetId: 'home-hero',            title: '👋 Bienvenue sur GoldArmy !', text: 'Cette page te présente tous les outils disponibles. Chaque card est un outil IA — clique dessus pour y accéder.' },
  { targetId: 'feature-card-sniper',  title: '🎯 Sniper Search',            text: 'Lance ici ta recherche d\'emploi ultra-précise. Donne ton profil, ta ville et l\'IA trouve les meilleures offres.' },
  { targetId: 'feature-card-mentor',  title: '🧠 Mentor IA',                text: 'Upload ton CV en PDF — l\'IA l\'analyse en 30 secondes, l\'adapte pour chaque offre et génère tes lettres de motivation.' },
  { targetId: 'feature-card-interview', title: '🎙️ Entretien Vocal',       text: 'Simule un vrai entretien à voix haute. L\'IA joue le recruteur et te donne un feedback instantané sur tes réponses.' },
  { targetId: 'feature-card-crm',     title: '📋 CRM Candidatures',         text: 'Tableau Kanban pour suivre toutes tes candidatures. Glisse les cartes entre colonnes, génère des relances en 1 clic.' },
  { targetId: 'feature-card-network', title: '🤝 Réseau Pro',               text: 'Accède au marché caché. L\'IA trouve les décideurs et rédige des emails d\'approche personnalisés pour toi.' },
  { targetId: 'home-tips',            title: '💡 Conseils Pro',              text: 'Ces conseils s\'actualisent automatiquement. Ils maximisent tes chances de succès dès le premier jour.' },
]
const currentStep = computed(() => tutorialSteps[tutorialStep.value])
const isLast = computed(() => tutorialStep.value === tutorialSteps.length - 1)
function startTutorial() { tutorialStep.value = 0; tutorialActive.value = true; scrollTarget() }
function nextStep() { if (isLast.value) { closeTutorial(); return } tutorialStep.value++; scrollTarget() }
function prevStep() { if (tutorialStep.value > 0) { tutorialStep.value--; scrollTarget() } }
function closeTutorial() { tutorialActive.value = false }
function scrollTarget() {
  nextTick(() => { document.getElementById(currentStep.value.targetId)?.scrollIntoView({ behavior: 'smooth', block: 'center' }) })
}
</script>

<template>
  <div class="relative min-h-full bg-surface-950 overflow-x-hidden">

    <!-- ══ Tutorial overlay ══════════════════════════════════════════════════ -->
    <Transition name="fade">
      <div v-if="tutorialActive" class="fixed inset-0 bg-black/60 backdrop-blur-sm z-40 pointer-events-none" />
    </Transition>
    <Transition name="pop">
      <div v-if="tutorialActive" class="fixed bottom-6 right-6 z-50 w-80 bg-[#1e2030] border border-indigo-500/30 rounded-2xl shadow-2xl p-5 pointer-events-auto">
        <div class="absolute inset-0 rounded-2xl bg-gradient-to-br from-indigo-500/5 to-violet-500/5 pointer-events-none" />
        <div class="relative">
          <div class="flex items-center justify-between mb-3">
            <span class="text-[10px] font-black uppercase tracking-widest text-indigo-400 bg-indigo-500/10 px-2 py-0.5 rounded-full">Étape {{ tutorialStep + 1 }} / {{ tutorialSteps.length }}</span>
            <button @click="closeTutorial" class="text-slate-500 hover:text-white transition-colors p-1 hover:bg-white/5 rounded-lg text-sm">✕</button>
          </div>
          <h3 class="font-bold text-white text-sm mb-2">{{ currentStep.title }}</h3>
          <p class="text-slate-300 text-xs leading-relaxed mb-4">{{ currentStep.text }}</p>
          <div class="flex items-center gap-1 mb-4">
            <div v-for="(_, i) in tutorialSteps" :key="i"
              class="flex-1 h-1 rounded-full transition-all duration-500 cursor-pointer"
              :class="i <= tutorialStep ? 'bg-indigo-400' : 'bg-surface-700'"
              @click="tutorialStep = i; scrollTarget()"
            />
          </div>
          <div class="flex gap-2">
            <button @click="prevStep" :disabled="tutorialStep === 0" class="flex-1 text-xs font-bold py-2 rounded-xl border border-surface-600 text-slate-400 hover:text-white hover:border-surface-500 disabled:opacity-30 transition-all">← Préc.</button>
            <button @click="nextStep" class="flex-1 text-xs font-bold py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl transition-all">{{ isLast ? '🎉 Terminer' : 'Suivant →' }}</button>
          </div>
          <p class="text-[10px] text-slate-600 text-center mt-3">L'élément est surligné · Échap pour quitter</p>
        </div>
      </div>
    </Transition>

    <!-- ══ HERO — full width ══════════════════════════════════════════════ -->
    <section id="home-hero"
      class="relative min-h-[520px] flex flex-col items-center justify-center text-center px-6 py-20 overflow-hidden border-b border-surface-800"
      :class="{ 'ring-2 ring-indigo-400 ring-offset-2 ring-offset-surface-950 z-[41] relative': tutorialActive && currentStep.targetId === 'home-hero' }"
      :style="{ opacity: ready ? 1:0, transform: ready ? 'none':'translateY(16px)', transition:'all 0.8s cubic-bezier(.22,1,.36,1)' }"
    >
      <!-- Animated background mesh -->
      <div class="absolute inset-0 pointer-events-none">
        <div class="absolute inset-0" style="background: radial-gradient(ellipse 80% 60% at 50% 0%, rgba(99,102,241,0.14) 0%, transparent 70%)" />
        <div class="absolute inset-0" style="background: radial-gradient(ellipse 60% 50% at 80% 80%, rgba(139,92,246,0.09) 0%, transparent 70%)" />
        <!-- Grid -->
        <div class="absolute inset-0 opacity-[0.035]" style="background-image:linear-gradient(rgba(99,102,241,1) 1px,transparent 1px),linear-gradient(90deg,rgba(99,102,241,1) 1px,transparent 1px);background-size:50px 50px" />
      </div>

      <!-- 3D Floating badges -->
      <div
        v-for="(b, i) in floatingBadges" :key="i"
        class="absolute pointer-events-none select-none"
        :style="{
          left: b.x, top: b.y,
          animation: `floatBadge 4s ease-in-out infinite`,
          animationDelay: b.delay,
          transform: 'translate(-50%,-50%)',
          zIndex: 2
        }"
      >
        <!-- Badge card with 3D shadow effect -->
        <div
          class="flex flex-col items-center gap-1 rounded-2xl backdrop-blur-md border border-white/10"
          :style="{
            background: `linear-gradient(135deg, ${b.color}22, ${b.color}0a)`,
            boxShadow: `0 8px 32px ${b.color}30, 0 2px 8px ${b.color}20, inset 0 1px 0 rgba(255,255,255,0.1)`,
            padding: b.size === 'lg' ? '12px 14px' : b.size === 'md' ? '9px 11px' : '7px 9px',
          }"
        >
          <span :style="{ fontSize: b.size === 'lg' ? '28px' : b.size === 'md' ? '22px' : '16px' }">{{ b.icon }}</span>
          <span
            class="font-black uppercase tracking-widest leading-none"
            :style="{ color: b.color, fontSize: b.size === 'lg' ? '9px' : '8px' }"
          >{{ b.label }}</span>
        </div>
        <!-- Glow dot underneath -->
        <div class="absolute bottom-0 left-1/2 -translate-x-1/2 translate-y-2 w-6 h-1 rounded-full blur-md"
          :style="{ background: b.color, opacity: 0.5 }" />
      </div>

      <!-- Main content (above badges) -->
      <div class="relative z-10 max-w-3xl mx-auto">
        <!-- Badge -->
        <div class="flex justify-center mb-6">
          <span class="inline-flex items-center gap-2 px-4 py-1.5 bg-indigo-500/10 border border-indigo-500/25 rounded-full text-indigo-300 text-xs font-bold uppercase tracking-wider">
            <span class="w-1.5 h-1.5 bg-indigo-400 rounded-full animate-ping" />
            Co-Pilote de Carrière IA
          </span>
        </div>

        <h1 class="text-5xl lg:text-7xl font-black text-white mb-5 leading-[1.05] tracking-tight">
          Bonjour,
          <span class="relative">
            <span class="bg-gradient-to-r from-indigo-400 via-violet-300 to-blue-400 bg-clip-text text-transparent">{{ userName }}</span>
            <!-- Underline accent -->
            <svg class="absolute -bottom-2 left-0 w-full" height="6" viewBox="0 0 200 6" preserveAspectRatio="none">
              <path d="M0 5 Q50 0 100 4 Q150 8 200 3" stroke="url(#ug)" stroke-width="2.5" fill="none" stroke-linecap="round"/>
              <defs><linearGradient id="ug" x1="0" x2="1"><stop offset="0%" stop-color="#818CF8"/><stop offset="100%" stop-color="#60A5FA"/></linearGradient></defs>
            </svg>
          </span>  👋
        </h1>

        <p class="text-slate-400 text-lg lg:text-xl max-w-xl mx-auto leading-relaxed mb-10">
          Ton arsenal complet pour décrocher le job de tes rêves.<br class="hidden md:block" />
          5 outils IA, un seul objectif.
        </p>

        <div class="flex flex-col sm:flex-row items-center justify-center gap-3 mb-12">
          <button @click="startTutorial"
            class="group relative overflow-hidden flex items-center gap-2.5 px-8 py-4 bg-indigo-600 hover:bg-indigo-500 text-white font-bold rounded-2xl shadow-xl shadow-indigo-500/30 transition-all hover:scale-105 hover:shadow-indigo-500/50 active:scale-95 text-sm"
          >
            <span class="absolute inset-0 bg-gradient-to-r from-white/0 via-white/12 to-white/0 -translate-x-full group-hover:translate-x-full transition-transform duration-700" />
            ❓ Lancer le tutoriel interactif
          </button>
          <button @click="router.push('/opportunities')"
            class="flex items-center gap-2.5 px-8 py-4 bg-surface-800/70 hover:bg-surface-700/80 backdrop-blur border border-surface-700 text-white font-bold rounded-2xl transition-all hover:scale-105 active:scale-95 text-sm"
          >
            🎯 Trouver un emploi maintenant
          </button>
        </div>

        <!-- Stats bar -->
        <div class="flex items-center justify-center gap-8 flex-wrap">
          <div v-for="s in [{v:'5',l:'Outils IA'},{v:'50+',l:'Sources'},{v:'< 30s',l:'Analyse CV'},{v:'∞',l:'Potentiel'}]" :key="s.l" class="text-center">
            <p class="text-2xl font-black text-white">{{ s.v }}</p>
            <p class="text-[11px] text-slate-500 uppercase tracking-wider font-bold">{{ s.l }}</p>
          </div>
        </div>
      </div>
    </section>

    <div class="max-w-7xl mx-auto px-4 sm:px-6 py-12 space-y-16">

      <!-- ══ FEATURE CARDS (wide 2-col) ════════════════════════════════════ -->
      <section>
        <div class="mb-8">
          <h2 class="text-2xl font-black text-white mb-1">Tes 5 outils IA</h2>
          <p class="text-slate-500 text-sm">Clique sur une card pour accéder à l'outil · Survole pour l'effet 3D</p>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div
            v-for="(feat, idx) in features" :key="feat.id"
            :id="`feature-card-${feat.id}`"
            @mousemove="(e) => onCardMove(e, idx)"
            @mouseleave="onCardLeave(idx)"
            :style="{
              opacity: ready ? 1 : 0,
              transform: `perspective(1000px) rotateX(${tilts[idx].x}deg) rotateY(${tilts[idx].y}deg) ${ready ? 'translateY(0)' : 'translateY(28px)'}`,
              transition: tilts[idx].x || tilts[idx].y ? 'transform 0.12s ease, opacity 0.6s, box-shadow 0.3s' : 'transform 0.5s cubic-bezier(.22,1,.36,1), opacity 0.6s, box-shadow 0.3s',
              transitionDelay: ready ? idx * 80 + 'ms' : '0ms',
              boxShadow: tilts[idx].x || tilts[idx].y ? `0 30px 70px ${feat.color}20, 0 8px 24px rgba(0,0,0,0.4)` : '0 4px 24px rgba(0,0,0,0.3)',
              border: tutorialActive && currentStep.targetId === `feature-card-${feat.id}` ? '2px solid #818CF8' : `1px solid ${feat.border}`,
            }"
            class="rounded-3xl overflow-hidden bg-surface-900 cursor-pointer group"
            :class="tutorialActive && currentStep.targetId === `feature-card-${feat.id}` ? 'ring-2 ring-indigo-400 ring-offset-2 ring-offset-surface-950 z-[41]' : ''"
            @click="router.push(feat.route)"
          >
            <!-- ── TOP PANEL: Visual illustration zone ── -->
            <div
              class="relative h-56 overflow-hidden"
              :style="{ background: feat.panelBg }"
              @mousemove.stop="(e) => onPanelMove(e, idx)"
              @mouseleave.stop="onPanelLeave(idx)"
            >
              <!-- Animated radial spotlight following mouse -->
              <div class="absolute inset-0 transition-opacity duration-300 pointer-events-none"
                :style="{ background: `radial-gradient(circle 140px at ${panelMousePos[idx].x}% ${panelMousePos[idx].y}%, ${feat.color}18, transparent 70%)` }" />

              <!-- Background grid lines -->
              <div class="absolute inset-0 opacity-[0.06] pointer-events-none"
                :style="{ backgroundImage:`linear-gradient(${feat.color}88 1px, transparent 1px),linear-gradient(90deg,${feat.color}88 1px,transparent 1px)`, backgroundSize:'32px 32px' }" />

              <!-- Corner accent glow -->
              <div class="absolute -top-8 -right-8 w-32 h-32 rounded-full blur-2xl pointer-events-none"
                :style="{ background: `${feat.color}25` }" />
              <div class="absolute -bottom-4 -left-4 w-24 h-24 rounded-full blur-2xl pointer-events-none"
                :style="{ background: `${feat.color}15` }" />

              <!-- Floating icon nodes in panel -->
              <div v-for="(pi, pii) in feat.panelIcons" :key="pii"
                class="absolute flex flex-col items-center gap-1"
                :style="{
                  left: pi.x, top: pi.y, transform:'translate(-50%,-50%)',
                  animation: 'floatBadge 3.5s ease-in-out infinite',
                  animationDelay: pii * 0.4 + 's'
                }"
              >
                <div class="rounded-xl flex items-center justify-center text-xl backdrop-blur-sm border border-white/10"
                  :style="{
                    width:'44px', height:'44px',
                    background:`linear-gradient(135deg,${feat.color}30,${feat.color}10)`,
                    boxShadow:`0 6px 20px ${feat.color}25, inset 0 1px 0 rgba(255,255,255,0.1)`
                  }"
                >{{ pi.icon }}</div>
                <span class="text-[8px] font-black uppercase tracking-wider" :style="{ color: feat.color }">{{ pi.label }}</span>
              </div>

              <!-- Center big emoji -->
              <div class="absolute inset-0 flex items-center justify-center pointer-events-none">
                <div class="text-6xl opacity-10 group-hover:opacity-20 transition-opacity duration-500 select-none"
                  :style="{ filter: `drop-shadow(0 0 24px ${feat.color})`}"
                >{{ feat.emoji }}</div>
              </div>

              <!-- Tag badge top-left -->
              <div class="absolute top-4 left-4">
                <span class="text-[10px] font-black uppercase tracking-widest px-2.5 py-1 rounded-full border"
                  :style="{ background:`${feat.color}15`, color:feat.color, borderColor:`${feat.color}30` }"
                >{{ feat.tag }}</span>
              </div>

              <!-- Stats bar bottom of panel -->
              <div class="absolute bottom-0 left-0 right-0 h-px" :style="{ background:`linear-gradient(90deg,transparent,${feat.color}60,transparent)` }" />
            </div>

            <!-- ── BOTTOM: Info section ── -->
            <div class="p-6">
              <!-- Name row -->
              <div class="flex items-center gap-3 mb-3">
                <div class="w-10 h-10 rounded-xl flex items-center justify-center text-xl shrink-0 transition-transform duration-300 group-hover:scale-110 group-hover:-rotate-3"
                  :style="{ background:`linear-gradient(135deg,${feat.color}40,${feat.color}15)`, border:`1px solid ${feat.color}25` }"
                >{{ feat.emoji }}</div>
                <h3 class="text-lg font-bold text-white">{{ feat.name }}</h3>
              </div>

              <!-- Description with transition -->
              <p class="text-slate-400 text-sm leading-relaxed mb-4 group-hover:text-slate-300 transition-colors duration-300">{{ feat.description }}</p>

              <!-- Feature list -->
              <ul class="space-y-1.5 mb-5">
                <li v-for="f in feat.features" :key="f" class="flex items-center gap-2 text-xs text-slate-400 group-hover:text-slate-300 transition-colors">
                  <div class="w-4 h-4 rounded flex items-center justify-center shrink-0" :style="{ background:`${feat.color}20` }">
                    <div class="w-1.5 h-1.5 rounded-full" :style="{ background: feat.color }" />
                  </div>
                  {{ f }}
                </li>
              </ul>

              <!-- Stats -->
              <div class="flex gap-3 mb-5">
                <div v-for="s in feat.stats" :key="s.l" class="flex-1 bg-surface-800 rounded-xl p-2.5 text-center border border-surface-700">
                  <p class="text-sm font-black text-white">{{ s.v }}</p>
                  <p class="text-[9px] text-slate-500 uppercase tracking-wide font-bold">{{ s.l }}</p>
                </div>
              </div>

              <!-- Tip -->
              <div class="flex items-start gap-2.5 p-3 rounded-xl mb-5" :style="{ background:`${feat.color}08`, border:`1px solid ${feat.color}15` }">
                <span class="text-sm shrink-0">💡</span>
                <p class="text-[11px] text-slate-400 leading-relaxed">{{ feat.tip }}</p>
              </div>

              <!-- CTA -->
              <div class="flex items-center justify-between">
                <span class="flex items-center gap-2 font-bold text-sm transition-all duration-300 group-hover:gap-3" :style="{ color: feat.color }">
                  Accéder → {{ feat.name }}
                </span>
                <div class="w-8 h-8 rounded-xl flex items-center justify-center transition-all duration-300 group-hover:scale-110"
                  :style="{ background:`${feat.color}15`, color:feat.color }">→</div>
              </div>
            </div>

            <!-- Bottom accent line animated on hover -->
            <div class="h-0.5 w-0 group-hover:w-full transition-all duration-700 rounded-full"
              :style="{ background:`linear-gradient(90deg,transparent,${feat.color},transparent)` }" />
          </div>
        </div>
      </section>

      <!-- ══ PRO TIPS ════════════════════════════════════════════════════════ -->
      <section id="home-tips"
        :style="{ opacity:ready?1:0, transform:ready?'none':'translateY(24px)', transition:'all 0.7s cubic-bezier(.22,1,.36,1) 0.5s' }"
        :class="tutorialActive && currentStep.targetId === 'home-tips' ? 'ring-2 ring-indigo-400 ring-offset-2 ring-offset-surface-950 z-[41] relative rounded-3xl' : ''"
      >
        <div class="mb-6">
          <h2 class="text-2xl font-black text-white mb-1">💡 Conseils Pro</h2>
          <p class="text-slate-500 text-sm">Stratégies éprouvées pour maximiser tes chances</p>
        </div>

        <div class="relative overflow-hidden rounded-2xl border border-indigo-500/20 p-6 mb-4"
          style="background:radial-gradient(ellipse at top left, rgba(99,102,241,0.1), transparent 60%)">
          <Transition name="tip" mode="out-in">
            <div :key="activeTip" class="relative">
              <span class="text-3xl mb-3 block">{{ tips[activeTip].icon }}</span>
              <h3 class="text-lg font-bold text-white mb-2">{{ tips[activeTip].title }}</h3>
              <p class="text-slate-300 text-sm leading-relaxed">{{ tips[activeTip].text }}</p>
            </div>
          </Transition>
          <div class="flex gap-1.5 mt-5">
            <button v-for="(_, i) in tips" :key="i" @click="activeTip = i"
              class="h-1 rounded-full transition-all duration-300"
              :class="i === activeTip ? 'w-6 bg-indigo-400' : 'w-2 bg-surface-700 hover:bg-surface-600'"
            />
          </div>
        </div>

        <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2">
          <button v-for="(tip, i) in tips" :key="i" @click="activeTip = i"
            class="text-left p-3 rounded-xl border transition-all duration-200 group"
            :class="i === activeTip ? 'bg-indigo-500/10 border-indigo-500/30' : 'bg-surface-900 border-surface-800 hover:border-surface-700 hover:bg-surface-800'"
          >
            <span class="text-lg mb-1 block">{{ tip.icon }}</span>
            <p class="text-[10px] font-bold" :class="i === activeTip ? 'text-indigo-200' : 'text-slate-400 group-hover:text-white'">{{ tip.title }}</p>
          </button>
        </div>
      </section>

      <!-- ══ CTA ════════════════════════════════════════════════════════════ -->
      <section class="relative rounded-3xl overflow-hidden border border-surface-800 p-10 lg:p-16 text-center"
        :style="{ opacity:ready?1:0, transform:ready?'none':'translateY(24px)', transition:'all 0.7s cubic-bezier(.22,1,.36,1) 0.65s' }">
        <div class="absolute inset-0 pointer-events-none" style="background:radial-gradient(ellipse at center,rgba(99,102,241,0.08),transparent 60%)" />
        <p class="relative z-10 text-indigo-400 text-xs font-black uppercase tracking-widest mb-3">Lance-toi maintenant</p>
        <h2 class="relative z-10 text-3xl lg:text-4xl font-black text-white mb-8">Prêt à décrocher ton prochain job ?</h2>
        <div class="relative z-10 flex flex-col sm:flex-row items-center justify-center gap-3">
          <button @click="router.push('/mentor')" class="flex items-center gap-2.5 px-8 py-4 bg-violet-600 hover:bg-violet-500 text-white font-bold rounded-2xl shadow-xl shadow-violet-500/20 transition-all hover:scale-105 text-sm">
            🧠 Analyser mon CV
          </button>
          <button @click="router.push('/opportunities')" class="flex items-center gap-2.5 px-8 py-4 bg-blue-600/20 hover:bg-blue-600/30 border border-blue-500/30 text-blue-300 font-bold rounded-2xl transition-all hover:scale-105 text-sm">
            🎯 Rechercher un emploi
          </button>
        </div>
      </section>

    </div>
  </div>
</template>

<style scoped>
@keyframes floatBadge {
  0%, 100% { transform: translate(-50%, -50%) translateY(0px) rotate(0deg); }
  33%       { transform: translate(-50%, -50%) translateY(-10px) rotate(1deg); }
  66%       { transform: translate(-50%, -50%) translateY(-5px) rotate(-0.5deg); }
}

.fade-enter-active, .fade-leave-active { transition: opacity 0.3s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

.pop-enter-active { transition: all 0.35s cubic-bezier(0.34,1.56,0.64,1); }
.pop-leave-active { transition: all 0.2s ease; }
.pop-enter-from { opacity: 0; transform: scale(0.8) translateY(12px); }
.pop-leave-to { opacity: 0; transform: scale(0.9) translateY(4px); }

.tip-enter-active { transition: all 0.4s cubic-bezier(0.22,1,0.36,1); }
.tip-leave-active { transition: all 0.2s ease; }
.tip-enter-from { opacity: 0; transform: translateY(10px); }
.tip-leave-to { opacity: 0; transform: translateY(-6px); }
</style>
