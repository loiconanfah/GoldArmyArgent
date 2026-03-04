<script setup>
import { ref, onMounted, onUnmounted, computed, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useHead } from '@unhead/vue'
import {
  MapPinIcon, SparklesIcon, MicrophoneIcon, ClipboardDocumentListIcon, UserGroupIcon,
  DocumentTextIcon, BoltIcon, GlobeAltIcon, ChartBarIcon, MagnifyingGlassIcon,
  BriefcaseIcon, CheckCircleIcon, PencilIcon, PencilSquareIcon, StarIcon,
  ChatBubbleLeftRightIcon, CpuChipIcon, ArrowTrendingUpIcon, TrophyIcon,
  Squares2X2Icon, ArrowRightIcon, EnvelopeIcon, CalendarDaysIcon,
  BuildingOfficeIcon, UserIcon, LightBulbIcon, PhoneIcon,
  BeakerIcon, QuestionMarkCircleIcon,
} from '@heroicons/vue/24/outline'

const { t, tm } = useI18n()
const router = useRouter()
const ready = ref(false)
const userName = ref(t('home.welcome', { name: '' }).replace('Bonjour, ', '').trim() || 'là')

useHead({
  title: computed(() => t('seo.home.title')),
  meta: [
    { name: 'description', content: computed(() => t('seo.home.description')) }
  ]
})

onMounted(async () => {
  const stored = localStorage.getItem('user')
  if (stored) { try { userName.value = JSON.parse(stored).email?.split('@')[0] ?? 'là' } catch {} }
  await nextTick()
  setTimeout(() => { ready.value = true }, 100)
  tipInterval = setInterval(() => { activeTip.value = (activeTip.value + 1) % tips.value.length }, 4000)
  window.addEventListener('keydown', (e) => { if (e.key === 'Escape') closeTutorial() })
})
onUnmounted(() => clearInterval(tipInterval))

// ── Floating 3D Badges ───────────────────────────────────────────────────────
const floatingBadges = computed(() => [
  { icon: MapPinIcon,                label: t('nav.sniper'),    color: '#3B82F6', delay: '0s',    x: '7%',  y: '22%', size: 'lg' },
  { icon: SparklesIcon,              label: t('nav.mentor'), color: '#8B5CF6', delay: '0.6s',  x: '84%', y: '18%', size: 'lg' },
  { icon: MicrophoneIcon,            label: t('home.features.interview.tag'), color: '#10B981', delay: '1.2s',  x: '4%',  y: '68%', size: 'md' },
  { icon: ClipboardDocumentListIcon, label: t('nav.crm'),       color: '#F59E0B', delay: '0.3s',  x: '89%', y: '62%', size: 'md' },
  { icon: UserGroupIcon,             label: t('nav.network'),    color: '#F43F5E', delay: '0.9s',  x: '50%', y: '88%', size: 'sm' },
  { icon: DocumentTextIcon,          label: 'CV',        color: '#22D3EE', delay: '1.5s',  x: '22%', y: '84%', size: 'sm' },
  { icon: BoltIcon,                  label: 'IA',        color: '#A78BFA', delay: '1.8s',  x: '75%', y: '82%', size: 'sm' },
])

// ── Feature cards ─────────────────────────────────────────────────────────────
// Each panelIcon is now a Heroicons component reference
// ── Feature cards ─────────────────────────────────────────────────────────────
// Each panelIcon is now a Heroicons component reference
const features = computed(() => [
  {
    id: 'sniper', name: t('home.features.sniper.name'), route: '/opportunities',
    icon: MapPinIcon, tag: t('home.features.sniper.tag'),
    color: '#3B82F6', border: 'rgba(59,130,246,0.25)',
    panelBg: 'linear-gradient(135deg,#0d2045 0%,#0a1628 55%,#071020 100%)',
    description: t('home.features.sniper.desc'),
    tip: t('home.features.sniper.tip'),
    stats: [{v:'50+',l:'Sources'},{v:'94%',l:t('landing.hero.stat_precision')},{v:'< 5s',l:'Résultats'}],
    features: [(tm('landing.agents.sniper.features') || []).find(f => f.includes('Filtres')) || 'Filtres Smart', (tm('landing.agents.sniper.features') || []).find(f => f.includes('CV')) || 'Matching CV', (tm('landing.agents.sniper.features') || []).find(f => f.includes('temps réel')) || 'Alertes'],
    panelIcons: [
      { icon: GlobeAltIcon,      label: 'Carte',  x: '12%', y: '28%' },
      { icon: ChartBarIcon,      label: 'Stats',  x: '50%', y: '18%' },
      { icon: MagnifyingGlassIcon, label: 'Scan', x: '80%', y: '30%' },
      { icon: BriefcaseIcon,     label: 'Offre',  x: '27%', y: '68%' },
      { icon: CheckCircleIcon,   label: 'Match',  x: '67%', y: '65%' },
    ],
  },
  {
    id: 'mentor', name: t('home.features.mentor.name'), route: '/mentor',
    icon: SparklesIcon, tag: t('home.features.mentor.tag'),
    color: '#8B5CF6', border: 'rgba(139,92,246,0.25)',
    panelBg: 'linear-gradient(135deg,#1e0a4e 0%,#15073a 55%,#0d0425 100%)',
    description: t('home.features.mentor.desc'),
    tip: t('home.features.mentor.tip'),
    stats: [{v:'< 30s',l:'Audit'},{v:'+40%',l:'Succès'},{v:'100%',l:'Personnalisé'}],
    features: [(tm('landing.agents.mentor.features') || []).find(f => f.includes('Audit')) || 'Audit CV', (tm('landing.agents.mentor.features') || []).find(f => f.includes('Adaptation')) || 'Adaptation', (tm('landing.agents.mentor.features') || []).find(f => f.includes('Lettre')) || 'Générateur Lettre'],
    panelIcons: [
      { icon: DocumentTextIcon,  label: 'CV',     x: '15%', y: '25%' },
      { icon: BeakerIcon,        label: 'Analyse',x: '55%', y: '18%' },
      { icon: PencilIcon,        label: 'Edit',   x: '82%', y: '30%' },
      { icon: StarIcon,          label: 'Score',  x: '30%', y: '68%' },
      { icon: PencilSquareIcon,  label: 'Lettre', x: '68%', y: '65%' },
    ],
  },
  {
    id: 'interview', name: t('home.features.interview.name'), route: '/interview',
    icon: MicrophoneIcon, tag: t('home.features.interview.tag'),
    color: '#10B981', border: 'rgba(16,185,129,0.25)',
    panelBg: 'linear-gradient(135deg,#022c1a 0%,#011d12 55%,#000e09 100%)',
    description: t('home.features.interview.desc'),
    tip: t('home.features.interview.tip'),
    stats: [{v:'10+',l:'Questions'},{v:'100%',l:'Vocal'},{v:'Live',l:'Feedback'}],
    features: [(tm('landing.agents.mentor.features') || []).find(f => f.includes('techniques')) || 'Simulations', (tm('landing.agents.mentor.features') || []).find(f => f.includes('Débriefing')) || 'Feedback IA', 'Score de confiance'],
    panelIcons: [
      { icon: MicrophoneIcon,            label: 'Voix',   x: '50%', y: '20%' },
      { icon: ChatBubbleLeftRightIcon,   label: 'Dialog', x: '15%', y: '42%' },
      { icon: CpuChipIcon,               label: 'IA',     x: '80%', y: '38%' },
      { icon: ArrowTrendingUpIcon,       label: 'Score',  x: '28%', y: '70%' },
      { icon: TrophyIcon,                label: 'Succès', x: '68%', y: '68%' },
    ],
  },
  {
    id: 'crm', name: t('home.features.crm.name'), route: '/crm',
    icon: ClipboardDocumentListIcon, tag: t('home.features.crm.tag'),
    color: '#F59E0B', border: 'rgba(245,158,11,0.25)',
    panelBg: 'linear-gradient(135deg,#2d1700 0%,#1e1000 55%,#0f0800 100%)',
    description: t('home.features.crm.desc'),
    tip: t('home.features.crm.tip'),
    stats: [{v:'5',l:'Colonnes'},{v:'Auto',l:'Relances'},{v:'∞',l:'Candidatures'}],
    features: [(tm('landing.agents.crm.features') || []).find(f => f.includes('Kanban')) || 'Kanban', (tm('landing.agents.crm.features') || []).find(f => f.includes('relance')) || 'Relances IA', (tm('landing.agents.crm.features') || []).find(f => f.includes('Historique')) || 'Historique'],
    panelIcons: [
      { icon: Squares2X2Icon,    label: 'Board',  x: '50%', y: '20%' },
      { icon: ArrowRightIcon,    label: 'Avance',  x: '18%', y: '42%' },
      { icon: CheckCircleIcon,   label: 'Done',   x: '82%', y: '40%' },
      { icon: EnvelopeIcon,      label: 'Email',  x: '28%', y: '70%' },
      { icon: CalendarDaysIcon,  label: 'Relance', x: '68%', y: '68%' },
    ],
  },
  {
    id: 'network', name: t('home.features.network.name'), route: '/network',
    icon: UserGroupIcon, tag: t('home.features.network.tag'),
    color: '#F43F5E', border: 'rgba(244,63,94,0.25)',
    panelBg: 'linear-gradient(135deg,#2d0010 0%,#1e000a 55%,#100005 100%)',
    description: t('home.features.network.desc'),
    tip: t('home.features.network.tip'),
    stats: [{v:'Auto',l:'Contacts'},{v:'∞',l:'Emails IA'},{v:'70%',l:'Marché caché'}],
    features: [(tm('landing.agents.network.features') || []).find(f => f.includes('RH')) || 'RH Search', (tm('landing.agents.network.features') || []).find(f => f.includes('messages')) || 'Outreach IA', (tm('landing.agents.network.features') || []).find(f => f.includes('Carnet')) || 'Contacts'],
    panelIcons: [
      { icon: UserGroupIcon,     label: 'Réseau',  x: '50%', y: '20%' },
      { icon: BuildingOfficeIcon,label: 'Société', x: '15%', y: '42%' },
      { icon: UserIcon,          label: 'RH',      x: '82%', y: '38%' },
      { icon: EnvelopeIcon,      label: 'Email',   x: '28%', y: '70%' },
      { icon: BriefcaseIcon,     label: 'Poste',   x: '68%', y: '68%' },
    ],
  },
])

const panelMousePos = ref(features.value.map(() => ({ x: 50, y: 50 })))
function onPanelMove(e, idx) {
  const r = e.currentTarget.getBoundingClientRect()
  panelMousePos.value[idx] = { x: ((e.clientX - r.left) / r.width) * 100, y: ((e.clientY - r.top) / r.height) * 100 }
}
function onPanelLeave(idx) { panelMousePos.value[idx] = { x: 50, y: 50 } }

const tilts = ref(features.value.map(() => ({ x: 0, y: 0 })))
function onCardMove(e, idx) {
  const r = e.currentTarget.getBoundingClientRect()
  tilts.value[idx] = { x: ((e.clientY - r.top) / r.height - 0.5) * -10, y: ((e.clientX - r.left) / r.width - 0.5) * 10 }
}
function onCardLeave(idx) { tilts.value[idx] = { x: 0, y: 0 } }

// ── Tips ─────────────────────────────────────────────────────────────────────
const tips = computed(() => [
  { icon: LightBulbIcon, title: t('home.tips.tip1_title'),      text: t('home.tips.tip1_text') },
  { icon: BoltIcon,       title: t('home.tips.tip2_title'),      text: t('home.tips.tip2_text') },
  { icon: MapPinIcon,     title: t('home.tips.tip3_title'),      text: t('home.tips.tip3_text') },
  { icon: PhoneIcon,      title: t('home.tips.tip4_title'),      text: t('home.tips.tip4_text') },
  { icon: UserGroupIcon,  title: t('home.tips.tip5_title'),      text: t('home.tips.tip5_text') },
  { icon: MicrophoneIcon, title: t('home.tips.tip6_title'),      text: t('home.tips.tip6_text') },
])
const activeTip = ref(0)
let tipInterval = null

// ── Tutorial ─────────────────────────────────────────────────────────────────
const tutorialActive = ref(false)
const tutorialStep = ref(0)
const tutorialSteps = computed(() => [
  { targetId: 'home-hero',             title: t('home.tutorial.step1_title'), text: t('home.tutorial.step1_text') },
  { targetId: 'feature-card-sniper',   title: t('home.tutorial.step2_title'), text: t('home.tutorial.step2_text') },
  { targetId: 'feature-card-mentor',   title: t('home.tutorial.step3_title'), text: t('home.tutorial.step3_text') },
  { targetId: 'feature-card-interview',title: t('home.tutorial.step4_title'), text: t('home.tutorial.step4_text') },
  { targetId: 'feature-card-crm',      title: t('home.tutorial.step5_title'), text: t('home.tutorial.step5_text') },
  { targetId: 'feature-card-network',  title: t('home.tutorial.step6_title'), text: t('home.tutorial.step6_text') },
  { targetId: 'home-tips',             title: t('home.tutorial.step7_title'), text: t('home.tutorial.step7_text') },
])
const currentStep = computed(() => tutorialSteps.value[tutorialStep.value])
const isLast = computed(() => tutorialStep.value === tutorialSteps.value.length - 1)
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

    <!-- Tutorial overlay -->
    <Transition name="fade">
      <div v-if="tutorialActive" class="fixed inset-0 bg-black/60 backdrop-blur-sm z-40 pointer-events-none" />
    </Transition>
    <Transition name="pop">
      <div v-if="tutorialActive" class="fixed bottom-6 right-6 z-50 w-80 bg-[#1e2030] border border-indigo-500/30 rounded-2xl shadow-2xl p-5 pointer-events-auto">
        <div class="absolute inset-0 rounded-2xl bg-gradient-to-br from-indigo-500/5 to-violet-500/5 pointer-events-none" />
        <div class="relative">
          <div class="flex items-center justify-between mb-3">
            <span class="text-[10px] font-black uppercase tracking-widest text-indigo-400 bg-indigo-500/10 px-2 py-0.5 rounded-full">
              {{ t('home.tutorial.step_label', { current: tutorialStep + 1, total: tutorialSteps.length }) }}
            </span>
            <button @click="closeTutorial" class="text-slate-500 hover:text-white transition-colors p-1 hover:bg-white/5 rounded-lg">
              <component :is="() => null" /><span class="text-sm">✕</span>
            </button>
          </div>
          <h3 class="font-bold text-white text-sm mb-2">{{ currentStep.title }}</h3>
          <p class="text-slate-300 text-xs leading-relaxed mb-4">{{ currentStep.text }}</p>
          <div class="flex items-center gap-1 mb-4">
            <div v-for="(_, i) in tutorialSteps" :key="i"
              class="flex-1 h-1 rounded-full transition-all duration-500 cursor-pointer"
              :class="i <= tutorialStep ? 'bg-indigo-400' : 'bg-surface-700'"
              @click="tutorialStep = i; scrollTarget()" />
          </div>
          <div class="flex gap-2">
            <button @click="prevStep" :disabled="tutorialStep === 0"
              class="flex-1 text-xs font-bold py-2 rounded-xl border border-surface-600 text-slate-400 hover:text-white hover:border-surface-500 disabled:opacity-30 transition-all">
              ← {{ t('common.prev') }}
            </button>
            <button @click="nextStep"
              class="flex-1 text-xs font-bold py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl transition-all">
              {{ isLast ? t('common.finish') : t('common.next') + ' →' }}
            </button>
          </div>
          <p class="text-[10px] text-slate-600 text-center mt-3">{{ t('home.tutorial.footer') }}</p>
        </div>
      </div>
    </Transition>

    <!-- ══ HERO ══════════════════════════════════════════════════════════════ -->
    <section id="home-hero"
      class="relative min-h-[520px] flex flex-col items-center justify-center text-center px-6 py-20 overflow-hidden border-b border-surface-800"
      :class="{ 'ring-2 ring-indigo-400 ring-offset-2 ring-offset-surface-950 z-[41] relative': tutorialActive && currentStep.targetId === 'home-hero' }"
      :style="{ opacity: ready?1:0, transform: ready?'none':'translateY(16px)', transition:'all 0.8s cubic-bezier(.22,1,.36,1)' }"
    >
      <!-- Background -->
      <div class="absolute inset-0 pointer-events-none">
        <div class="absolute inset-0" style="background:radial-gradient(ellipse 80% 60% at 50% 0%,rgba(99,102,241,0.14) 0%,transparent 70%)" />
        <div class="absolute inset-0" style="background:radial-gradient(ellipse 60% 50% at 80% 80%,rgba(139,92,246,0.09) 0%,transparent 70%)" />
        <div class="absolute inset-0 opacity-[0.035]" style="background-image:linear-gradient(rgba(99,102,241,1) 1px,transparent 1px),linear-gradient(90deg,rgba(99,102,241,1) 1px,transparent 1px);background-size:50px 50px" />
      </div>

      <!-- Floating 3D badges with Heroicons -->
      <div v-for="(b, i) in floatingBadges" :key="i"
        class="absolute pointer-events-none select-none"
        :style="{ left:b.x, top:b.y, transform:'translate(-50%,-50%)', animation:'floatBadge 4s ease-in-out infinite', animationDelay:b.delay, zIndex:2 }"
      >
        <div class="flex flex-col items-center gap-1.5 rounded-2xl backdrop-blur-md border border-white/10"
          :style="{
            background:`linear-gradient(135deg,${b.color}25,${b.color}0c)`,
            boxShadow:`0 8px 32px ${b.color}35,0 2px 8px ${b.color}25,inset 0 1px 0 rgba(255,255,255,0.1)`,
            padding: b.size==='lg'?'13px 15px': b.size==='md'?'10px 12px':'8px 10px',
          }"
        >
          <component :is="b.icon"
            :style="{
              width: b.size==='lg'?'26px': b.size==='md'?'20px':'15px',
              height: b.size==='lg'?'26px': b.size==='md'?'20px':'15px',
              color: b.color,
              filter:`drop-shadow(0 0 6px ${b.color}80)`
            }"
            stroke-width="1.5"
          />
          <span class="font-black uppercase tracking-widest leading-none"
            :style="{ color:b.color, fontSize: b.size==='lg'?'8px':'7px' }">{{ b.label }}</span>
        </div>
        <!-- Shadow dot -->
        <div class="absolute bottom-0 left-1/2 -translate-x-1/2 translate-y-2 w-5 h-1 rounded-full blur-md"
          :style="{ background:b.color, opacity:0.45 }" />
      </div>

      <!-- Hero content -->
      <div class="relative z-10 max-w-3xl mx-auto">
        <div class="flex justify-center mb-6">
          <span class="inline-flex items-center gap-2 px-4 py-1.5 bg-indigo-500/10 border border-indigo-500/25 rounded-full text-indigo-300 text-xs font-bold uppercase tracking-wider">
            <span class="w-1.5 h-1.5 bg-indigo-400 rounded-full animate-ping" />
            {{ t('landing.hero.badge').replace('{', '').replace('}', '').trim() }}
          </span>
        </div>

        <h1 class="text-5xl lg:text-7xl font-black text-white mb-5 leading-[1.05] tracking-tight">
          {{ t('home.welcome_prefix') }}
          <span class="relative">
            <span class="bg-gradient-to-r from-indigo-400 via-violet-300 to-blue-400 bg-clip-text text-transparent">{{ userName }}</span>
            <svg class="absolute -bottom-2 left-0 w-full" height="6" viewBox="0 0 200 6" preserveAspectRatio="none">
              <path d="M0 5 Q50 0 100 4 Q150 8 200 3" stroke="url(#ug)" stroke-width="2.5" fill="none" stroke-linecap="round"/>
              <defs><linearGradient id="ug" x1="0" x2="1"><stop offset="0%" stop-color="#818CF8"/><stop offset="100%" stop-color="#60A5FA"/></linearGradient></defs>
            </svg>
          </span>
        </h1>

        <p class="text-slate-400 text-lg lg:text-xl max-w-xl mx-auto leading-relaxed mb-10">
          {{ t('home.subtitle').split('. ')[0] }}.<br class="hidden md:block" />
          {{ t('home.subtitle').split('. ')[1] }}
        </p>

        <div class="flex flex-col sm:flex-row items-center justify-center gap-3 mb-12">
          <button @click="startTutorial"
            class="group relative overflow-hidden flex items-center gap-2.5 px-8 py-4 bg-indigo-600 hover:bg-indigo-500 text-white font-bold rounded-2xl shadow-xl shadow-indigo-500/30 transition-all hover:scale-105 hover:shadow-indigo-500/50 active:scale-95 text-sm"
          >
            <span class="absolute inset-0 bg-gradient-to-r from-white/0 via-white/12 to-white/0 -translate-x-full group-hover:translate-x-full transition-transform duration-700" />
            <QuestionMarkCircleIcon class="w-5 h-5" />
            {{ t('home.tutorial_btn') }}
          </button>
          <button @click="router.push('/opportunities')"
            class="flex items-center gap-2.5 px-8 py-4 bg-surface-800/70 hover:bg-surface-700/80 backdrop-blur border border-surface-700 text-white font-bold rounded-2xl transition-all hover:scale-105 active:scale-95 text-sm"
          >
            <MapPinIcon class="w-5 h-5 text-blue-400" />
            {{ t('home.find_job_btn') }}
          </button>
        </div>

        <!-- Stats -->
        <div class="flex items-center justify-center gap-8 flex-wrap">
          <div v-for="s in [{v:'5',l:t('home.stats.tools')},{v:'50+',l:'Sources'},{v:'< 30s',l:t('home.stats.cv_audit')},{v:'∞',l:t('home.stats.potential')}]" :key="s.l" class="text-center">
            <p class="text-2xl font-black text-white">{{ s.v }}</p>
            <p class="text-[11px] text-slate-500 uppercase tracking-wider font-bold">{{ s.l }}</p>
          </div>
        </div>
      </div>
    </section>

    <div class="max-w-7xl mx-auto px-4 sm:px-6 py-12 space-y-16">

      <!-- ══ FEATURE CARDS ══════════════════════════════════════════════════ -->
      <section>
        <div class="mb-8">
          <h2 class="text-2xl font-black text-white mb-1">{{ t('home.tools_title') }}</h2>
          <p class="text-slate-500 text-sm">{{ t('home.tools_subtitle') }}</p>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div v-for="(feat, idx) in features" :key="feat.id"
            :id="`feature-card-${feat.id}`"
            @mousemove="(e) => onCardMove(e, idx)"
            @mouseleave="onCardLeave(idx)"
            @click="router.push(feat.route)"
            :style="{
              opacity: ready ? 1 : 0,
              transform:`perspective(1000px) rotateX(${tilts[idx].x}deg) rotateY(${tilts[idx].y}deg) ${ready?'translateY(0)':'translateY(28px)'}`,
              transition: tilts[idx].x || tilts[idx].y ? 'transform 0.12s ease,opacity 0.6s,box-shadow 0.3s' : 'transform 0.5s cubic-bezier(.22,1,.36,1),opacity 0.6s,box-shadow 0.3s',
              transitionDelay: ready ? idx * 80 + 'ms' : '0ms',
              boxShadow: tilts[idx].x || tilts[idx].y ? `0 30px 70px ${feat.color}20,0 8px 24px rgba(0,0,0,0.4)` : '0 4px 24px rgba(0,0,0,0.3)',
              border: tutorialActive && currentStep.targetId === `feature-card-${feat.id}` ? '2px solid #818CF8' : `1px solid ${feat.border}`,
            }"
            class="rounded-3xl overflow-hidden bg-surface-900 cursor-pointer group"
            :class="tutorialActive && currentStep.targetId === `feature-card-${feat.id}` ? 'ring-2 ring-indigo-400 ring-offset-2 ring-offset-surface-950 z-[41]' : ''"
          >
            <!-- Visual panel (top) -->
            <div class="relative h-52 overflow-hidden"
              :style="{ background: feat.panelBg }"
              @mousemove.stop="(e) => onPanelMove(e, idx)"
              @mouseleave.stop="onPanelLeave(idx)"
            >
              <!-- Mouse spotlight -->
              <div class="absolute inset-0 pointer-events-none transition-opacity duration-300"
                :style="{ background:`radial-gradient(circle 150px at ${panelMousePos[idx].x}% ${panelMousePos[idx].y}%,${feat.color}18,transparent 70%)` }" />
              <!-- Grid background -->
              <div class="absolute inset-0 opacity-[0.06] pointer-events-none"
                :style="{ backgroundImage:`linear-gradient(${feat.color}88 1px,transparent 1px),linear-gradient(90deg,${feat.color}88 1px,transparent 1px)`, backgroundSize:'32px 32px' }" />
              <!-- Corner glows -->
              <div class="absolute -top-8 -right-8 w-32 h-32 rounded-full blur-2xl pointer-events-none" :style="{ background:`${feat.color}22` }" />
              <div class="absolute -bottom-4 -left-4 w-24 h-24 rounded-full blur-2xl pointer-events-none" :style="{ background:`${feat.color}15` }" />

              <!-- Floating icon nodes -->
              <div v-for="(pi, pii) in feat.panelIcons" :key="pii"
                class="absolute flex flex-col items-center gap-1.5"
                :style="{ left:pi.x, top:pi.y, transform:'translate(-50%,-50%)', animation:'floatBadge 3.5s ease-in-out infinite', animationDelay: pii*0.4+'s' }"
              >
                <div class="rounded-xl flex items-center justify-center backdrop-blur-sm border border-white/10"
                  :style="{ width:'40px', height:'40px', background:`linear-gradient(135deg,${feat.color}30,${feat.color}10)`, boxShadow:`0 6px 20px ${feat.color}25,inset 0 1px 0 rgba(255,255,255,0.1)` }"
                >
                  <component :is="pi.icon" class="w-5 h-5" :style="{ color:feat.color, filter:`drop-shadow(0 0 4px ${feat.color}80)` }" stroke-width="1.5" />
                </div>
                <span class="text-[7px] font-black uppercase tracking-wider" :style="{ color:feat.color }">{{ pi.label }}</span>
              </div>

              <!-- Center watermark icon -->
              <div class="absolute inset-0 flex items-center justify-center pointer-events-none">
                <component :is="feat.icon" class="w-24 h-24 transition-opacity duration-500 opacity-[0.06] group-hover:opacity-[0.12]"
                  :style="{ color:feat.color, filter:`drop-shadow(0 0 24px ${feat.color})` }" stroke-width="1" />
              </div>

              <!-- Tag -->
              <div class="absolute top-4 left-4">
                <span class="text-[10px] font-black uppercase tracking-widest px-2.5 py-1 rounded-full border"
                  :style="{ background:`${feat.color}15`, color:feat.color, borderColor:`${feat.color}30` }">{{ feat.tag }}</span>
              </div>
              <!-- Bottom separator line -->
              <div class="absolute bottom-0 left-0 right-0 h-px" :style="{ background:`linear-gradient(90deg,transparent,${feat.color}50,transparent)` }" />
            </div>

            <!-- Info section (bottom) -->
            <div class="p-6">
              <!-- Name row -->
              <div class="flex items-center gap-3 mb-3">
                <div class="w-10 h-10 rounded-xl flex items-center justify-center shrink-0 transition-transform duration-300 group-hover:scale-110 group-hover:-rotate-3"
                  :style="{ background:`linear-gradient(135deg,${feat.color}40,${feat.color}15)`, border:`1px solid ${feat.color}25` }"
                >
                  <component :is="feat.icon" class="w-5 h-5" :style="{ color:feat.color }" stroke-width="1.5" />
                </div>
                <h3 class="text-lg font-bold text-white">{{ feat.name }}</h3>
              </div>

              <p class="text-slate-400 text-sm leading-relaxed mb-4 group-hover:text-slate-300 transition-colors duration-300">{{ feat.description }}</p>

              <!-- Features list -->
              <ul class="space-y-2 mb-5">
                <li v-for="f in feat.features" :key="f" class="flex items-center gap-2.5 text-xs text-slate-400 group-hover:text-slate-300 transition-colors">
                  <CheckCircleIcon class="w-3.5 h-3.5 shrink-0" :style="{ color:feat.color }" stroke-width="2" />
                  {{ f }}
                </li>
              </ul>

              <!-- Stats -->
              <div class="flex gap-3 mb-4">
                <div v-for="s in feat.stats" :key="s.l" class="flex-1 bg-surface-800 rounded-xl p-2.5 text-center border border-surface-700">
                  <p class="text-sm font-black text-white">{{ s.v }}</p>
                  <p class="text-[9px] text-slate-500 uppercase tracking-wide font-bold">{{ s.l }}</p>
                </div>
              </div>

              <!-- Tip -->
              <div class="flex items-start gap-2.5 p-3 rounded-xl mb-5" :style="{ background:`${feat.color}08`, border:`1px solid ${feat.color}15` }">
                <LightBulbIcon class="w-4 h-4 shrink-0 mt-0.5" :style="{ color:feat.color }" stroke-width="1.5" />
                <p class="text-[11px] text-slate-400 leading-relaxed">{{ feat.tip }}</p>
              </div>

              <!-- CTA row -->
              <div class="flex items-center justify-between pt-1">
                <span class="flex items-center gap-2 font-bold text-sm group-hover:gap-3 transition-all duration-300" :style="{ color:feat.color }">
                  {{ t('home.features.access_prefix') }} {{ feat.name }}
                </span>
                <div class="w-8 h-8 rounded-xl flex items-center justify-center transition-all duration-300 group-hover:scale-110 group-hover:rotate-6"
                  :style="{ background:`${feat.color}15` }">
                  <ArrowRightIcon class="w-4 h-4" :style="{ color:feat.color }" stroke-width="2" />
                </div>
              </div>
            </div>

            <!-- Hover bottom bar -->
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
          <h2 class="text-2xl font-black text-white mb-1">{{ t('home.pro_tips_title') }}</h2>
          <p class="text-slate-500 text-sm">{{ t('home.pro_tips_subtitle') }}</p>
        </div>

        <div class="relative overflow-hidden rounded-2xl border border-indigo-500/20 p-6 mb-4"
          style="background:radial-gradient(ellipse at top left,rgba(99,102,241,0.1),transparent 60%)">
          <Transition name="tip" mode="out-in">
            <div :key="activeTip" class="relative">
              <component :is="tips[activeTip].icon" class="w-8 h-8 text-indigo-400 mb-3" stroke-width="1.5" />
              <h3 class="text-lg font-bold text-white mb-2">{{ tips[activeTip].title }}</h3>
              <p class="text-slate-300 text-sm leading-relaxed">{{ tips[activeTip].text }}</p>
            </div>
          </Transition>
          <div class="flex gap-1.5 mt-5">
            <button v-for="(_, i) in tips" :key="i" @click="activeTip = i"
              class="h-1 rounded-full transition-all duration-300"
              :class="i === activeTip ? 'w-6 bg-indigo-400' : 'w-2 bg-surface-700 hover:bg-surface-600'" />
          </div>
        </div>

        <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2">
          <button v-for="(tip, i) in tips" :key="i" @click="activeTip = i"
            class="text-left p-3 rounded-xl border transition-all duration-200 group"
            :class="i === activeTip ? 'bg-indigo-500/10 border-indigo-500/30' : 'bg-surface-900 border-surface-800 hover:border-surface-700 hover:bg-surface-800'"
          >
            <component :is="tip.icon" class="w-5 h-5 mb-2 transition-colors"
              :class="i === activeTip ? 'text-indigo-400' : 'text-slate-500 group-hover:text-slate-300'" stroke-width="1.5" />
            <p class="text-[10px] font-bold" :class="i === activeTip ? 'text-indigo-200' : 'text-slate-400 group-hover:text-white'">{{ tip.title }}</p>
          </button>
        </div>
      </section>

      <!-- ══ CTA ════════════════════════════════════════════════════════════ -->
      <section class="relative rounded-3xl overflow-hidden border border-surface-800 p-10 lg:p-16 text-center"
        :style="{ opacity:ready?1:0, transform:ready?'none':'translateY(24px)', transition:'all 0.7s cubic-bezier(.22,1,.36,1) 0.65s' }">
        <div class="absolute inset-0 pointer-events-none" style="background:radial-gradient(ellipse at center,rgba(99,102,241,0.08),transparent 60%)" />
        <p class="relative z-10 text-indigo-400 text-xs font-black uppercase tracking-widest mb-3">{{ t('home.cta_final_tagline') }}</p>
        <h2 class="relative z-10 text-3xl lg:text-4xl font-black text-white mb-8">{{ t('home.cta_title') }}</h2>
        <div class="relative z-10 flex flex-col sm:flex-row items-center justify-center gap-3">
          <button @click="router.push('/mentor')"
            class="flex items-center gap-2.5 px-8 py-4 bg-violet-600 hover:bg-violet-500 text-white font-bold rounded-2xl shadow-xl shadow-violet-500/20 transition-all hover:scale-105 text-sm">
            <SparklesIcon class="w-5 h-5" />
            {{ t('home.cta_mentor') }}
          </button>
          <button @click="router.push('/opportunities')"
            class="flex items-center gap-2.5 px-8 py-4 bg-blue-600/20 hover:bg-blue-600/30 border border-blue-500/30 text-blue-300 font-bold rounded-2xl transition-all hover:scale-105 text-sm">
            <MapPinIcon class="w-5 h-5" />
            {{ t('home.cta_opportunities') }}
          </button>
        </div>
      </section>

    </div>
  </div>
</template>

<style scoped>
@keyframes floatBadge {
  0%, 100% { transform: translate(-50%,-50%) translateY(0px) rotate(0deg); }
  33%       { transform: translate(-50%,-50%) translateY(-10px) rotate(1deg); }
  66%       { transform: translate(-50%,-50%) translateY(-5px) rotate(-0.5deg); }
}
.fade-enter-active,.fade-leave-active { transition: opacity 0.3s ease; }
.fade-enter-from,.fade-leave-to { opacity: 0; }
.pop-enter-active { transition: all 0.35s cubic-bezier(0.34,1.56,0.64,1); }
.pop-leave-active { transition: all 0.2s ease; }
.pop-enter-from { opacity:0; transform:scale(0.8) translateY(12px); }
.pop-leave-to { opacity:0; transform:scale(0.9) translateY(4px); }
.tip-enter-active { transition: all 0.4s cubic-bezier(0.22,1,0.36,1); }
.tip-leave-active { transition: all 0.2s ease; }
.tip-enter-from { opacity:0; transform:translateY(10px); }
.tip-leave-to { opacity:0; transform:translateY(-6px); }
</style>
