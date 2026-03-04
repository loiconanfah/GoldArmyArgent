<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useHead } from '@unhead/vue'
import {
  RocketLaunchIcon,
  ChartBarIcon,
  BriefcaseIcon,
  CpuChipIcon,
  CheckCircleIcon,
  XMarkIcon,
  ArrowRightIcon,
  SparklesIcon,
  ShieldCheckIcon,
  BoltIcon,
  UserGroupIcon,
  DocumentTextIcon,
  MagnifyingGlassIcon,
  ChatBubbleLeftEllipsisIcon,
  ChevronRightIcon,
  VideoCameraIcon
} from '@heroicons/vue/24/outline'

const { t } = useI18n()
const router = useRouter()

useHead({
  title: computed(() => t('seo.landing.title')),
  meta: [
    { name: 'description', content: computed(() => t('seo.landing.description')) },
    { property: 'og:title', content: computed(() => t('seo.landing.title')) },
    { property: 'og:description', content: computed(() => t('seo.landing.description')) },
    { property: 'og:image', content: '/og-banner.png' },
    { name: 'twitter:card', content: 'summary_large_image' }
  ]
})

// Parallax mouse effect
const mouseX = ref(0)
const mouseY = ref(0)
const handleMouseMove = (e) => {
  mouseX.value = (e.clientX / window.innerWidth - 0.5) * 30
  mouseY.value = (e.clientY / window.innerHeight - 0.5) * 30
}

const testimonials = computed(() => [
  {
    quote: t('landing.testimonials.quote1'),
    name: 'Marc R.',
    role: 'Développeur Fullstack',
    color: 'from-violet-500 to-purple-500',
    initials: 'MR'
  },
  {
    quote: t('landing.testimonials.quote2'),
    name: 'Sophie L.',
    role: 'Data Scientist',
    color: 'from-emerald-500 to-teal-500',
    initials: 'SL'
  },
  {
    quote: t('landing.testimonials.quote3'),
    name: 'Julien D.',
    role: 'Product Manager',
    color: 'from-orange-500 to-amber-500',
    initials: 'JD'
  }
])
onMounted(() => window.addEventListener('mousemove', handleMouseMove))
onUnmounted(() => window.removeEventListener('mousemove', handleMouseMove))
</script>

<template>
  <div class="min-h-screen bg-[#0a0a12] text-white font-sans overflow-x-hidden selection:bg-violet-500/30">

    <!-- ─── NAVBAR ─── -->
    <nav class="fixed top-6 inset-x-0 z-[100] px-6">
      <div class="max-w-7xl mx-auto flex items-center justify-between
                  bg-white/5 backdrop-blur-2xl border border-white/10
                  rounded-2xl px-6 py-4 shadow-2xl shadow-black/40">
        <!-- Logo -->
        <div class="flex items-center gap-3">
          <div class="w-9 h-9 rounded-xl overflow-hidden border border-violet-500/30 shadow-[0_0_20px_rgba(124,58,237,0.4)]">
            <img src="/logo.png" alt="Logo" class="w-full h-full object-cover" />
          </div>
          <span class="text-lg font-black tracking-tight uppercase text-white">GoldArmy</span>
        </div>
        <!-- Links -->
        <div class="hidden md:flex items-center gap-6">
          <a v-for="link in [
               { name: t('landing.nav.agents'), id: 'agents' },
               { name: t('landing.nav.features'), id: 'fonctions' },
               { name: t('landing.nav.pricing'), id: 'tarifs' },
               { name: t('landing.nav.reviews'), id: 'avis' }
             ]" :key="link.id"
             :href="`/#${link.id}`"
             class="text-xs font-bold uppercase tracking-[0.2em] text-white/50 hover:text-white transition-colors">
            {{ link.name }}
          </a>
          <!-- Added Freemium & Blog links -->
          <div class="h-4 w-px bg-white/10 mx-2"></div>
          <router-link to="/free-cv-roast" class="text-xs font-bold uppercase tracking-[0.2em] text-violet-400 hover:text-violet-300 transition-colors flex items-center gap-1.5">
            <DocumentTextIcon class="w-3.5 h-3.5" /> {{ t('landing.nav.cv_audit') }}
          </router-link>
          <router-link to="/free-interview" class="text-xs font-bold uppercase tracking-[0.2em] text-indigo-400 hover:text-indigo-300 transition-colors flex items-center gap-1.5">
            <VideoCameraIcon class="w-3.5 h-3.5" /> {{ t('landing.nav.simulation') }}
          </router-link>
          <router-link to="/blog" class="text-xs font-bold uppercase tracking-[0.2em] text-fuchsia-400 hover:text-fuchsia-300 transition-colors">
            {{ t('landing.nav.blog') }}
          </router-link>
        </div>
        <!-- CTA -->
        <div class="flex items-center gap-3">
          <router-link to="/login" class="hidden sm:block text-xs font-bold uppercase tracking-widest text-white/50 hover:text-white transition-colors">
            {{ t('landing.nav.login') }}
          </router-link>
          <router-link to="/register"
            class="bg-violet-600 hover:bg-violet-500 text-white text-[10px] font-black uppercase tracking-[0.25em]
                   px-5 py-2.5 rounded-xl shadow-lg shadow-violet-600/30
                   transition-all hover:shadow-violet-500/40 hover:scale-[1.02] active:scale-95">
            {{ t('landing.nav.get_started') }} →
          </router-link>
        </div>
      </div>
    </nav>

    <!-- ─── HERO ─── -->
    <section class="relative min-h-screen flex items-center overflow-hidden">
      <!-- Grid overlay -->
      <div class="absolute inset-0 opacity-10"
           style="background-image: linear-gradient(rgba(124,58,237,0.3) 1px, transparent 1px), linear-gradient(90deg, rgba(124,58,237,0.3) 1px, transparent 1px); background-size: 60px 60px;">
      </div>

      <!-- Glow blobs -->
      <div class="absolute top-0 right-[20%] w-[600px] h-[600px] bg-violet-600/20 rounded-full blur-[120px] pointer-events-none"></div>
      <div class="absolute bottom-0 left-[10%] w-[400px] h-[400px] bg-indigo-600/15 rounded-full blur-[100px] pointer-events-none"></div>

      <div class="relative max-w-7xl mx-auto px-6 pt-40 pb-20 grid lg:grid-cols-2 gap-16 items-center">
        <!-- Left text -->
        <div class="relative z-10">
          <!-- Badge -->
          <div class="inline-flex items-center gap-2.5 mb-8 px-4 py-2 rounded-full
                      bg-violet-500/10 border border-violet-500/20 text-violet-300 text-[10px] font-black uppercase tracking-[0.3em]">
            <span class="relative flex h-2 w-2">
              <span class="animate-ping absolute h-full w-full rounded-full bg-violet-400 opacity-75"></span>
              <span class="relative block h-2 w-2 rounded-full bg-violet-400"></span>
            </span>
            { {{ t('landing.hero.badge') }} }
          </div>

          <h1 class="text-6xl md:text-7xl lg:text-8xl font-black leading-[0.9] tracking-tighter mb-8">
            <span class="text-white">{{ t('landing.hero.title_1') }}<br/></span>
            <span class="text-transparent bg-clip-text bg-gradient-to-r from-violet-400 via-purple-400 to-indigo-400">
              {{ t('landing.hero.title_2') }}
            </span>
            <br/>
            <span class="text-white/30">{{ t('landing.hero.title_3') }}</span>
          </h1>

          <p class="text-lg text-white/50 leading-relaxed max-w-md mb-10">
            {{ t('landing.hero.description') }}
          </p>

          <div class="flex flex-col sm:flex-row flex-wrap items-center gap-4">
            <router-link to="/register"
              class="w-full sm:w-auto flex justify-center items-center gap-3 bg-violet-600 hover:bg-violet-500 text-white font-black text-sm uppercase tracking-[0.2em]
                     px-8 py-4 rounded-2xl shadow-xl shadow-violet-600/30 transition-all hover:scale-[1.02] active:scale-95">
              {{ t('landing.hero.cta_main') }} <ArrowRightIcon class="w-4 h-4" />
            </router-link>
            <a href="#fonctions"
               class="flex justify-center items-center gap-2 text-sm font-bold text-white/40 hover:text-white/70 transition-colors uppercase tracking-widest mt-2 sm:mt-0 w-full sm:w-auto">
              {{ t('landing.hero.cta_secondary') }} ↓
            </a>
          </div>

          <!-- Trust bar -->
          <div class="mt-12 flex flex-wrap gap-6">
            <div v-for="t_item in [
              { n: '98.5%', l: t('landing.hero.stat_precision') },
              { n: '40h', l: t('landing.hero.stat_hours') }
            ]" :key="t_item.l" class="flex flex-col">
              <span class="text-2xl font-black text-white">{{ t_item.n }}</span>
              <span class="text-[10px] font-bold uppercase tracking-widest text-white/30">{{ t_item.l }}</span>
            </div>
          </div>
        </div>

        <!-- Right 3D visual -->
        <div class="relative hidden lg:flex items-center justify-center">
          <!-- Floating cube clusters (CSS only) -->
          <div class="relative w-[460px] h-[460px]"
               :style="`transform: perspective(1000px) rotateX(${mouseY * -0.3}deg) rotateY(${mouseX * 0.3}deg)`">

            <!-- Main glowing orb -->
            <div class="absolute inset-0 flex items-center justify-center">
              <div class="w-64 h-64 rounded-full bg-violet-600/20 blur-3xl animate-pulse"></div>
            </div>

            <!-- Floating cube 1 -->
            <div class="absolute top-[5%] right-[15%] w-20 h-20 rounded-2xl border border-violet-400/30
                        bg-violet-600/10 backdrop-blur-xl shadow-[0_0_40px_rgba(124,58,237,0.3)]
                        animate-float-slow flex items-center justify-center">
              <RocketLaunchIcon class="w-8 h-8 text-violet-400" />
            </div>
            <!-- Floating cube 2 -->
            <div class="absolute top-[30%] right-[5%] w-14 h-14 rounded-xl border border-indigo-400/30
                        bg-indigo-600/10 backdrop-blur-xl shadow-[0_0_30px_rgba(99,102,241,0.3)]
                        animate-float-medium flex items-center justify-center">
              <BoltIcon class="w-6 h-6 text-indigo-400" />
            </div>
            <!-- Floating cube 3 -->
            <div class="absolute bottom-[20%] right-[10%] w-16 h-16 rounded-2xl border border-purple-400/30
                        bg-purple-600/10 backdrop-blur-xl shadow-[0_0_30px_rgba(168,85,247,0.3)]
                        animate-float-fast flex items-center justify-center">
              <SparklesIcon class="w-7 h-7 text-purple-400" />
            </div>
            <!-- Floating cube 4 -->
            <div class="absolute top-[10%] left-[10%] w-12 h-12 rounded-xl border border-violet-400/20
                        bg-white/5 backdrop-blur-xl animate-float-medium"></div>
            <!-- Floating cube 5 -->
            <div class="absolute bottom-[10%] left-[15%] w-10 h-10 rounded-lg border border-indigo-400/20
                        bg-white/5 backdrop-blur-xl animate-float-slow"></div>
            <!-- Floating cube 6 - Large central -->
            <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2
                        w-48 h-48 rounded-3xl border border-violet-400/20
                        bg-gradient-to-br from-violet-600/20 to-indigo-600/10
                        backdrop-blur-xl shadow-[0_0_80px_rgba(124,58,237,0.2)]
                        flex items-center justify-center">
              <div class="text-center">
                <div class="text-4xl font-black text-white tracking-tighter">IA</div>
                <div class="text-[10px] font-black text-violet-400 uppercase tracking-[0.4em] mt-1">SNIPER</div>
              </div>
            </div>

            <!-- Scatter mini cubes -->
            <div class="absolute top-[60%] left-[5%] w-8 h-8 rounded-lg border border-violet-500/20 bg-violet-600/10 animate-float-fast"></div>
            <div class="absolute top-[20%] left-[30%] w-6 h-6 rounded-md border border-indigo-500/20 bg-indigo-600/10 animate-float-slow"></div>
            <div class="absolute bottom-[5%] right-[30%] w-10 h-10 rounded-xl border border-purple-500/20 bg-purple-600/10 animate-float-medium"></div>
          </div>
        </div>
      </div>

      <!-- Bottom mini features bar -->
      <div class="absolute bottom-0 inset-x-0 border-t border-white/5">
        <div class="max-w-7xl mx-auto px-6 py-6 grid grid-cols-1 md:grid-cols-3 gap-6">
          <div v-for="f_item in [
            { icon: MagnifyingGlassIcon, title: t('landing.features.title'), desc: t('landing.features.desc') },
            { icon: DocumentTextIcon, title: t('landing.features.cv_title'), desc: t('landing.features.cv_desc') },
            { icon: ChatBubbleLeftEllipsisIcon, title: t('landing.features.coach_title'), desc: t('landing.features.coach_desc') },
          ]" :key="f_item.title" class="flex items-center gap-4 p-4 rounded-xl bg-white/3 hover:bg-white/5 transition-colors border border-white/5">
            <div class="w-10 h-10 rounded-xl bg-violet-600/20 border border-violet-500/20 flex items-center justify-center shrink-0">
              <component :is="f_item.icon" class="w-5 h-5 text-violet-400" />
            </div>
            <div>
              <div class="text-sm font-black text-white">{{ f_item.title }}</div>
              <div class="text-[11px] text-white/40 font-medium mt-0.5">{{ f_item.desc }}</div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ─── AGENTS SECTION ─── -->
    <section id="agents" class="relative py-40 overflow-hidden">
      <div class="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_rgba(124,58,237,0.05)_0%,transparent_70%)]"></div>

      <div class="relative max-w-7xl mx-auto px-6">
        <div class="text-center mb-20">
          <p class="text-[10px] font-black uppercase tracking-[0.5em] text-violet-500 mb-4">{{ t('landing.agents.tagline') }}</p>
          <h2 class="text-5xl md:text-6xl font-black tracking-tighter leading-none" v-html="t('landing.agents.title').replace('. ', '.<br/>').replace(': ', ':<br/>')"></h2>
        </div>

        <!-- Agent 1 – Sniper IA -->
        <div class="grid lg:grid-cols-2 gap-8 items-center mb-16">
          <div class="bg-white/3 border border-white/8 rounded-3xl p-10 hover:border-violet-500/30 transition-all group">
            <div class="flex items-center gap-4 mb-8">
              <div class="w-14 h-14 rounded-2xl bg-gradient-to-br from-violet-600 to-indigo-600 flex items-center justify-center shadow-lg shadow-violet-600/30">
                <RocketLaunchIcon class="w-7 h-7 text-white" />
              </div>
              <div>
                <div class="text-[10px] font-black uppercase tracking-widest text-violet-400 mb-0.5">{{ t('landing.agents.sniper.tag') }}</div>
                <div class="text-2xl font-black text-white">{{ t('landing.agents.sniper.name') }}</div>
              </div>
            </div>
            <p class="text-white/50 leading-relaxed mb-8" v-html="t('landing.agents.sniper.desc').replace('avant même leur publication officielle', '<span class=\'text-violet-400 font-bold\'>avant même leur publication officielle</span>')"></p>
            <ul class="space-y-3">
              <li v-for="agent_feat in t('landing.agents.sniper.features', {returnObjects: true})" :key="agent_feat"
                  class="flex items-center gap-3 text-sm text-white/60">
                <CheckCircleIcon class="w-4 h-4 text-violet-500 shrink-0" />
                {{ agent_feat }}
              </li>
            </ul>
          </div>
          <!-- Visual card -->
          <div class="bg-white/2 border border-white/5 rounded-3xl p-8 space-y-4">
            <div class="h-8 w-1/2 bg-white/5 rounded-lg"></div>
            <div v-for="m in [{ p: '98%', c: 'violet', t: 'Senior Dev React @ Criteo' }, { p: '76%', c: 'indigo', t: 'Fullstack Engineer @ Qonto' }, { p: '61%', c: 'purple', t: 'Lead Frontend @ BlaBlaCar' }]" :key="m.t"
                 class="flex items-center gap-4 p-4 bg-white/3 border border-white/5 rounded-2xl hover:bg-white/5 transition-all">
              <div :class="`text-${m.c}-400 font-black text-lg w-14 shrink-0`">{{ m.p }}</div>
              <div class="text-sm font-bold text-white/70">{{ m.t }}</div>
              <div :class="`ml-auto text-[10px] font-black uppercase tracking-widest text-${m.c}-400 bg-${m.c}-500/10 px-2 py-1 rounded-full`">Match</div>
            </div>
          </div>
        </div>

        <!-- Agent 2 – CRM -->
        <div class="grid lg:grid-cols-2 gap-8 items-center mb-16">
          <!-- Visual card first on desktop -->
            <div class="grid grid-cols-3 gap-3">
              <div v-for="col in [
                { label: t('landing.pricing.essential.features').find(f => f.includes('CRM')) ? 'En cours' : 'Sent', count: 12, color: 'indigo' },
                { label: 'En cours', count: 5, color: 'amber' },
                { label: 'Entretiens', count: 3, color: 'emerald' }
              ]" :key="col.label" class="bg-white/5 border border-white/5 rounded-2xl p-4 text-center">
                <div :class="`text-3xl font-black text-${col.color}-400 mb-1`">{{ col.count }}</div>
                <div class="text-[10px] text-white/40 font-bold uppercase tracking-widest">{{ col.label }}</div>
              </div>
            </div>
            <div class="space-y-2">
              <div v-for="i in 4" :key="i" class="h-12 bg-white/3 border border-white/5 rounded-xl"></div>
            </div>
          </div>
          <div class="lg:order-2 bg-white/3 border border-white/8 rounded-3xl p-10 hover:border-purple-500/30 transition-all">
            <div class="flex items-center gap-4 mb-8">
              <div class="w-14 h-14 rounded-2xl bg-gradient-to-br from-purple-600 to-pink-600 flex items-center justify-center shadow-lg shadow-purple-600/30">
                <ChartBarIcon class="w-7 h-7 text-white" />
              </div>
              <div>
                <div class="text-[10px] font-black uppercase tracking-widest text-purple-400 mb-0.5">{{ t('landing.agents.crm.tag') }}</div>
                <div class="text-2xl font-black text-white">{{ t('landing.agents.crm.name') }}</div>
              </div>
            </div>
            <p class="text-white/50 leading-relaxed mb-8" v-html="t('landing.agents.crm.desc').replace('machine de guerre organisée', '<span class=\"text-purple-400 font-bold\">machine de guerre organisée</span>')"></p>
            <ul class="space-y-3">
              <li v-for="agent_feat in t('landing.agents.crm.features', {returnObjects: true})" :key="agent_feat"
                  class="flex items-center gap-3 text-sm text-white/60">
                <CheckCircleIcon class="w-4 h-4 text-purple-500 shrink-0" />
                {{ agent_feat }}
              </li>
            </ul>
          </div>
        </div>

        <!-- Agent 3 & 4 grid -->
        <div class="grid md:grid-cols-2 gap-8">
          <div class="bg-white/3 border border-white/8 rounded-3xl p-10 hover:border-emerald-500/30 transition-all">
            <div class="flex items-center gap-4 mb-8">
              <div class="w-14 h-14 rounded-2xl bg-gradient-to-br from-emerald-600 to-teal-600 flex items-center justify-center shadow-lg shadow-emerald-600/30">
                <UserGroupIcon class="w-7 h-7 text-white" />
              </div>
              <div>
                <div class="text-[10px] font-black uppercase tracking-widest text-emerald-400 mb-0.5">{{ t('landing.agents.network.tag') }}</div>
                <div class="text-2xl font-black text-white">{{ t('landing.agents.network.name') }}</div>
              </div>
            </div>
            <p class="text-white/50 leading-relaxed mb-8" v-html="t('landing.agents.network.desc').replace('messages d\'accroche ultra-personnalisés', '<span class=\"text-emerald-400 font-bold\">messages d\'accroche ultra-personnalisés</span>')"></p>
            <ul class="space-y-3">
              <li v-for="agent_feat in t('landing.agents.network.features', {returnObjects: true})" :key="agent_feat"
                  class="flex items-center gap-3 text-sm text-white/60">
                <CheckCircleIcon class="w-4 h-4 text-emerald-500 shrink-0" />
                {{ agent_feat }}
              </li>
            </ul>
          </div>

          <div class="bg-white/3 border border-white/8 rounded-3xl p-10 hover:border-orange-500/30 transition-all">
            <div class="flex items-center gap-4 mb-8">
              <div class="w-14 h-14 rounded-2xl bg-gradient-to-br from-orange-600 to-amber-600 flex items-center justify-center shadow-lg shadow-orange-600/30">
                <CpuChipIcon class="w-7 h-7 text-white" />
              </div>
              <div>
                <div class="text-[10px] font-black uppercase tracking-widest text-orange-400 mb-0.5">{{ t('landing.agents.mentor.tag') }}</div>
                <div class="text-2xl font-black text-white">{{ t('landing.agents.mentor.name') }}</div>
              </div>
            </div>
            <p class="text-white/50 leading-relaxed mb-8" v-html="t('landing.agents.mentor.desc').replace('précis et actionnable', '<span class=\"text-orange-400 font-bold\">précis et actionnable</span>')"></p>
            <ul class="space-y-3">
              <li v-for="agent_feat in t('landing.agents.mentor.features', {returnObjects: true})" :key="agent_feat"
                  class="flex items-center gap-3 text-sm text-white/60">
                <CheckCircleIcon class="w-4 h-4 text-orange-500 shrink-0" />
                {{ agent_feat }}
              </li>
            </ul>
          </div>
        </div>
      </div>
    </section>

    <!-- ─── HOW IT WORKS ─── -->
    <section id="fonctions" class="py-32 border-y border-white/5 bg-white/[0.01]">
      <div class="max-w-7xl mx-auto px-6">
        <div class="text-center mb-20">
          <p class="text-[10px] font-black uppercase tracking-[0.5em] text-violet-500 mb-4">{{ t('landing.how_it_works.tagline') }}</p>
          <h2 class="text-5xl font-black tracking-tighter">{{ t('landing.how_it_works.title') }}</h2>
        </div>
        <div class="grid md:grid-cols-3 gap-6">
          <div v-for="(step, idx) in [
            { n: '01', title: t('landing.how_it_works.step1_title'), desc: t('landing.how_it_works.step1_desc'), icon: DocumentTextIcon },
            { n: '02', title: t('landing.how_it_works.step2_title'), desc: t('landing.how_it_works.step2_desc'), icon: BoltIcon },
            { n: '03', title: t('landing.how_it_works.step3_title'), desc: t('landing.how_it_works.step3_desc'), icon: RocketLaunchIcon },
          ]" :key="step.n"
          class="relative p-8 rounded-3xl bg-white/3 border border-white/8 hover:border-violet-500/20 transition-all group overflow-hidden">
            <div class="absolute top-6 right-6 text-7xl font-black text-white/3 group-hover:text-white/5 transition-colors leading-none">{{ step.n }}</div>
            <div class="w-12 h-12 rounded-2xl bg-violet-600/20 border border-violet-500/20 flex items-center justify-center mb-8">
              <component :is="step.icon" class="w-6 h-6 text-violet-400" />
            </div>
            <h3 class="text-xl font-black text-white mb-4">{{ step.title }}</h3>
            <p class="text-sm text-white/50 leading-relaxed">{{ step.desc }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- ─── STATS ─── -->
    <section class="py-32">
      <div class="max-w-7xl mx-auto px-6 grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div v-for="s in [
          { val: '40h', label: t('landing.stats.hours'), color: 'violet' },
          { val: '+300%', label: t('landing.stats.rate'), color: 'indigo' },
          { val: '5/sem', label: t('landing.stats.interviews'), color: 'purple' },
          { val: '98.5%', label: t('landing.stats.precision'), color: 'pink' }
        ]" :key="s.label"
        class="p-8 rounded-3xl bg-white/3 border border-white/8 text-center hover:bg-white/5 transition-all">
          <div :class="`text-4xl font-black text-${s.color}-400 mb-2`">{{ s.val }}</div>
          <div class="text-[10px] font-black uppercase tracking-widest text-white/30">{{ s.label }}</div>
        </div>
      </div>
    </section>

    <!-- ─── TESTIMONIALS ─── -->
    <section id="avis" class="py-32 border-y border-white/5 bg-white/[0.01]">
      <div class="max-w-7xl mx-auto px-6">
        <div class="text-center mb-20">
          <p class="text-[10px] font-black uppercase tracking-[0.5em] text-violet-500 mb-4">{{ t('landing.testimonials.tagline') }}</p>
          <h2 class="text-5xl font-black tracking-tighter">{{ t('landing.testimonials.title') }}</h2>
        </div>
        <div class="grid md:grid-cols-3 gap-6">
          <div v-for="t in testimonials" :key="t.name"
               class="p-8 rounded-3xl bg-white/3 border border-white/8 hover:border-violet-500/20 transition-all flex flex-col gap-6 group">
            <div class="flex gap-1">
              <span v-for="i in 5" :key="i" class="text-violet-400 text-sm group-hover:scale-110 transition-transform inline-block">★</span>
            </div>
            <p class="text-sm text-white/60 italic leading-relaxed flex-1">"{{ t.quote }}"</p>
            <div class="flex items-center gap-3 border-t border-white/5 pt-6">
              <div :class="`w-10 h-10 rounded-full bg-gradient-to-br ${t.color} flex items-center justify-center text-white font-black text-xs shadow-lg`">{{ t.initials }}</div>
              <div>
                <div class="text-sm font-black text-white">{{ t.name }}</div>
                <div class="text-[10px] text-white/30 font-bold uppercase tracking-widest">{{ t.role }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ─── PRICING ─── -->
    <section id="tarifs" class="py-32">
      <div class="max-w-7xl mx-auto px-6">
        <div class="text-center mb-20">
          <p class="text-[10px] font-black uppercase tracking-[0.5em] text-violet-500 mb-4">{{ t('landing.pricing.tagline') }}</p>
          <h2 class="text-5xl font-black tracking-tighter">{{ t('landing.pricing.title') }}</h2>
        </div>
        <div class="grid lg:grid-cols-3 gap-6 items-stretch">
          <!-- FREE -->
          <div class="p-10 rounded-3xl bg-white/3 border border-white/8 flex flex-col">
            <div class="text-sm font-black uppercase tracking-[0.3em] text-white/40 mb-8">{{ t('landing.pricing.free.name') }}</div>
            <div class="mb-8">
              <span class="text-6xl font-black text-white">0€</span>
              <span class="text-sm text-white/30 font-bold"> {{ t('landing.pricing.month') }}</span>
            </div>
            <ul class="space-y-4 mb-10 flex-1">
              <li v-for="item in t('landing.pricing.free.features', {returnObjects: true})" :key="item" class="flex items-center gap-3 text-sm text-white/50">
                <CheckCircleIcon class="w-4 h-4 text-violet-500 shrink-0" /> {{ item }}
              </li>
              <li v-for="item in ['Mentor IA Pro', 'Générateur de Réseau']" :key="item" class="flex items-center gap-3 text-sm text-white/20 line-through">
                <XMarkIcon class="w-4 h-4 shrink-0" /> {{ item }}
              </li>
            </ul>
            <router-link to="/register" class="block w-full py-4 text-center rounded-2xl border border-white/10 font-black text-sm uppercase tracking-widest text-white/50 hover:bg-white/5 hover:text-white transition-all">{{ t('landing.nav.get_started') }}</router-link>
          </div>
          <!-- ESSENTIAL — popular -->
          <div class="relative p-10 rounded-3xl border-2 border-violet-500 bg-gradient-to-b from-violet-600/10 to-transparent shadow-2xl shadow-violet-600/20 flex flex-col">
            <div class="absolute -top-4 left-1/2 -translate-x-1/2 bg-violet-600 text-white text-[10px] font-black uppercase tracking-widest px-5 py-1.5 rounded-full shadow-lg shadow-violet-600/30">{{ t('landing.pricing.essential.popular') }}</div>
            <div class="text-sm font-black uppercase tracking-[0.3em] text-violet-400 mb-8">{{ t('landing.pricing.essential.name') }}</div>
            <div class="mb-8">
              <span class="text-6xl font-black text-white">9.99€</span>
              <span class="text-sm text-white/30 font-bold"> {{ t('landing.pricing.month') }}</span>
            </div>
            <ul class="space-y-4 mb-10 flex-1">
              <li v-for="item in t('landing.pricing.essential.features', {returnObjects: true})" :key="item" class="flex items-center gap-3 text-sm text-white/70">
                <CheckCircleIcon class="w-4 h-4 text-violet-400 shrink-0" /> {{ item }}
              </li>
            </ul>
            <router-link to="/register" class="block w-full py-4 text-center rounded-2xl bg-violet-600 hover:bg-violet-500 font-black text-sm uppercase tracking-widest text-white shadow-xl shadow-violet-600/30 hover:scale-[1.01] active:scale-95 transition-all">{{ t('landing.pricing.essential.cta') }}</router-link>
          </div>
          <!-- PRO -->
          <div class="p-10 rounded-3xl bg-white/3 border border-white/8 flex flex-col">
            <div class="text-sm font-black uppercase tracking-[0.3em] text-white/40 mb-8">{{ t('landing.pricing.pro.name') }}</div>
            <div class="mb-8">
              <span class="text-6xl font-black text-white">19.99€</span>
              <span class="text-sm text-white/30 font-bold"> {{ t('landing.pricing.month') }}</span>
            </div>
            <ul class="space-y-4 mb-10 flex-1">
              <li v-for="item in t('landing.pricing.pro.features', {returnObjects: true})" :key="item" class="flex items-center gap-3 text-sm text-white/70">
                <CheckCircleIcon class="w-4 h-4 text-violet-500 shrink-0" /> {{ item }}
              </li>
            </ul>
            <router-link to="/register" class="block w-full py-4 text-center rounded-2xl border border-white/10 font-black text-sm uppercase tracking-widest text-white/50 hover:bg-white/5 hover:text-white transition-all">{{ t('landing.pricing.pro.cta') }}</router-link>
          </div>
        </div>
      </div>
    </section>

    <!-- ─── CTA FINAL ─── -->
    <section class="py-32">
      <div class="max-w-4xl mx-auto px-6 text-center">
        <div class="relative rounded-[3rem] border border-violet-500/20 bg-gradient-to-b from-violet-600/10 to-transparent p-20 overflow-hidden">
          <div class="absolute -top-20 left-1/2 -translate-x-1/2 w-80 h-80 bg-violet-600/20 blur-[100px] rounded-full pointer-events-none"></div>
          <div class="relative z-10">
            <p class="text-[10px] font-black uppercase tracking-[0.5em] text-violet-500 mb-6">{{ t('landing.cta_final.tagline') }}</p>
            <h2 class="text-5xl md:text-6xl font-black tracking-tighter leading-none mb-8" v-html="t('landing.cta_final.title').replace('?', '?<br/>').replace('décrocher', 'décrocher<br/>')"></h2>
            <p class="text-lg text-white/40 mb-12 max-w-lg mx-auto">{{ t('landing.cta_final.description') }}</p>
            <router-link to="/register"
              class="inline-flex items-center gap-3 bg-violet-600 hover:bg-violet-500 text-white font-black text-sm uppercase tracking-[0.2em]
                     px-12 py-5 rounded-2xl shadow-2xl shadow-violet-600/30 transition-all hover:scale-[1.02] active:scale-95">
              {{ t('landing.cta_final.button') }} <ArrowRightIcon class="w-5 h-5" />
            </router-link>
            <div class="mt-8 flex items-center justify-center gap-2 text-xs text-white/20 font-bold">
              <ShieldCheckIcon class="w-4 h-4" /> {{ t('landing.cta_final.footer') }}
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ─── FULL FOOTER ─── -->
    <footer class="border-t border-white/5 pt-20 pb-10 mt-32 relative bg-[#0a0a12] z-10">
      <div class="max-w-7xl mx-auto px-6 grid grid-cols-1 md:grid-cols-4 gap-12 mb-16">
        <!-- Brand -->
        <div class="md:col-span-2">
          <div class="flex items-center gap-3 mb-6">
            <div class="w-9 h-9 rounded-xl overflow-hidden border border-violet-500/30">
              <img src="/logo.png" alt="Logo" class="w-full h-full object-cover" />
            </div>
            <span class="text-lg font-black uppercase tracking-widest text-white">GoldArmy</span>
          </div>
          <p class="text-white/40 text-sm leading-relaxed max-w-sm mb-8">
            {{ t('landing.footer.description') }}
          </p>
          <div class="flex items-center gap-2 text-xs text-white/20 font-bold">
            <ShieldCheckIcon class="w-4 h-4 text-violet-500" /> {{ t('landing.footer.secure') }}
          </div>
        </div>

        <!-- Liens Rapides -->
        <div>
          <h4 class="text-white font-black uppercase tracking-[0.2em] text-xs mb-6">{{ t('landing.footer.navigation') }}</h4>
          <ul class="space-y-4">
            <li><a href="/#agents" class="text-sm text-white/40 hover:text-white transition-colors">{{ t('landing.nav.agents') }}</a></li>
            <li><a href="/#tarifs" class="text-sm text-white/40 hover:text-white transition-colors">{{ t('landing.nav.pricing') }}</a></li>
            <li><router-link to="/blog" class="text-sm text-white/40 hover:text-white transition-colors">{{ t('landing.nav.blog') }}</router-link></li>
            <li><router-link to="/login" class="text-sm text-white/40 hover:text-white transition-colors">{{ t('landing.nav.login') }}</router-link></li>
          </ul>
        </div>

        <!-- Contact & Legal -->
        <div>
          <h4 class="text-white font-black uppercase tracking-[0.2em] text-xs mb-6">{{ t('landing.footer.contact') }}</h4>
          <ul class="space-y-4 mb-8">
            <li>
              <a href="mailto:support@goldarmyai.com" class="text-sm text-white/40 hover:text-violet-400 transition-colors flex items-center gap-2">
                <span class="w-1.5 h-1.5 rounded-full bg-violet-500"></span> {{ t('landing.footer.support') }}
              </a>
            </li>
            <li>
              <a href="mailto:yvanloic@goldarmyai.com" class="text-sm text-white/40 hover:text-violet-400 transition-colors flex items-center gap-2">
                <span class="w-1.5 h-1.5 rounded-full bg-violet-500"></span> {{ t('landing.footer.ceo') }}
              </a>
            </li>
          </ul>
        </div>
      </div>

      <!-- Bottom Bar -->
      <div class="max-w-7xl mx-auto px-6 border-t border-white/5 pt-8 flex flex-col md:flex-row items-center justify-between gap-4">
        <p class="text-xs text-white/20 font-bold">{{ t('landing.footer.rights') }}</p>
        <div class="flex gap-6">
          <a href="#" class="text-xs text-white/20 hover:text-white transition-colors font-bold tracking-widest uppercase">{{ t('landing.footer.privacy') }}</a>
          <a href="#" class="text-xs text-white/20 hover:text-white transition-colors font-bold tracking-widest uppercase">{{ t('landing.footer.terms') }}</a>
        </div>
      </div>
    </footer>

  </div>
</template>

<style scoped>
@keyframes float-slow {
  0%, 100% { transform: translateY(0px) rotate(0deg); }
  50% { transform: translateY(-16px) rotate(3deg); }
}
@keyframes float-medium {
  0%, 100% { transform: translateY(0px) rotate(0deg); }
  50% { transform: translateY(-10px) rotate(-3deg); }
}
@keyframes float-fast {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-6px); }
}

.animate-float-slow  { animation: float-slow  6s ease-in-out infinite; }
.animate-float-medium{ animation: float-medium 4s ease-in-out infinite; }
.animate-float-fast  { animation: float-fast  3s ease-in-out infinite; }
</style>
