<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { authFetch } from '@/utils/auth'
import {
  UsersIcon, CheckCircleIcon, DocumentTextIcon, BriefcaseIcon,
  ChartBarIcon, TrophyIcon, ArrowUpRightIcon, ArrowTrendingUpIcon,
  CalendarDaysIcon, VideoCameraIcon, UserPlusIcon, ArrowDownTrayIcon
} from '@heroicons/vue/24/outline'

const { t } = useI18n()
const router = useRouter()
const loading = ref(true)
const analytics = ref(null)
const nextEvent = ref(null)
const animate = ref(false)

const counters = ref({ members: 0, active: 0, applications: 0, interviews: 0 })
function tween(key, target) {
  const dur = 1000, start = performance.now()
  function step(now) {
    const p = Math.min((now - start) / dur, 1)
    const eased = 1 - Math.pow(1 - p, 3)
    counters.value[key] = Math.round(target * eased)
    if (p < 1) requestAnimationFrame(step)
  }
  requestAnimationFrame(step)
}

const kpis = computed(() => analytics.value?.kpis || {})
const counts = computed(() => analytics.value?.counts || {})

const cards = computed(() => [
  { key: 'members', icon: UsersIcon, value: counters.value.members, label: t('org.stats.members'), featured: true, delta: t('org.home.this_month') },
  { key: 'active', icon: CheckCircleIcon, value: counters.value.active, label: t('org.stats.active'), sub: t('org.home.of_members', { n: kpis.value.total_members || 0 }) },
  { key: 'applications', icon: BriefcaseIcon, value: counters.value.applications, label: t('org.stats.applications'), sub: t('org.home.avg_each', { n: kpis.value.avg_applications ?? 0 }) },
  { key: 'interviews', icon: ChartBarIcon, value: counters.value.interviews, label: t('org.stats.interviews'), sub: (kpis.value.placement_rate ?? 0) + '% ' + t('org.stats.placement') },
])

// Bar chart — highlight the tallest month with a value bubble; muted bars for empty months
const monthly = computed(() => {
  const arr = analytics.value?.monthly || []
  const max = Math.max(0, ...arr.map(m => m.count))
  return arr.map(m => ({ ...m, active: m.count > 0, peak: m.count === max && max > 0 }))
})

// Semi-circular gauge — cohort placement rate
const gaugePct = computed(() => Math.min(100, kpis.value.placement_rate ?? 0))
const gaugeOffset = computed(() => {
  const len = 251.2
  return animate.value ? len - (len * gaugePct.value / 100) : len
})

const withCvPct = computed(() => {
  const k = kpis.value
  if (!k.total_members) return 0
  return Math.round((k.with_cv / k.total_members) * 100)
})

const funnelSteps = computed(() => {
  const f = analytics.value?.funnel || {}
  const order = [
    { key: 'TO_APPLY', label: t('org.funnel.to_apply'), color: '#98A2B3' },
    { key: 'APPLIED', label: t('org.funnel.applied'), color: '#6366F1' },
    { key: 'FOLLOW_UP', label: t('org.funnel.follow_up'), color: '#0EA5E9' },
    { key: 'INTERVIEW', label: t('org.funnel.interview'), color: '#F59E0B' },
    { key: 'REJECTED', label: t('org.funnel.rejected'), color: '#EF4444' },
  ]
  const max = Math.max(1, ...order.map(o => f[o.key] || 0))
  return order.map(o => ({ ...o, count: f[o.key] || 0, pct: Math.round(((f[o.key] || 0) / max) * 100) }))
})

const topMembers = computed(() => analytics.value?.top_members || [])
const secondary = computed(() => {
  const k = kpis.value, c = counts.value
  return [
    { label: t('org.stats.placement'), value: (k.placement_rate ?? 0) + '%', color: 'gold' },
    { label: t('org.stats.with_cv'), value: withCvPct.value + '%', color: 'emerald' },
    { label: t('org.roles.mentor') + 's', value: c.mentors ?? 0, color: 'indigo' },
    { label: t('org.events.title'), value: c.events ?? 0, color: 'sky' },
    { label: t('org.nav.network'), value: c.network ?? 0, color: 'pink' },
    { label: t('org.nav.community'), value: c.posts ?? 0, color: 'gold' },
  ]
})

function fmtDate(d) { if (!d) return ''; try { return new Date(d).toLocaleString([], { dateStyle: 'medium', timeStyle: 'short' }) } catch { return d } }

async function load() {
  loading.value = true
  try {
    const [aRes, eRes] = await Promise.all([authFetch('/api/org/analytics'), authFetch('/api/org/events')])
    const aJson = await aRes.safeJson()
    const eJson = await eRes.safeJson()
    if (aJson?.status === 'success') {
      analytics.value = aJson.data
      const k = aJson.data.kpis
      setTimeout(() => {
        animate.value = true
        tween('members', k.total_members); tween('active', k.active_members)
        tween('applications', k.total_applications); tween('interviews', k.total_interviews)
      }, 120)
    }
    if (eJson?.status === 'success') {
      const upcoming = (eJson.data || []).filter(e => new Date(e.date) >= new Date())
      nextEvent.value = upcoming[0] || (eJson.data || [])[0] || null
    }
  } catch (e) {}
  finally { loading.value = false }
}
onMounted(load)
</script>

<template>
  <div class="oh">
    <!-- Header -->
    <header class="oh__head">
      <div>
        <h1 class="oh__title">{{ t('org.home.hello') }}</h1>
        <p class="oh__sub">{{ t('org.home.sub') }}</p>
      </div>
      <div class="oh__actions">
        <button class="oh__btn oh__btn--primary" @click="router.push('/organisation/parametres')">
          <UserPlusIcon class="w-4 h-4" /> {{ t('org.home.invite_cta') }}
        </button>
        <button class="oh__btn oh__btn--ghost" @click="router.push('/organisation/membres')">
          <ArrowDownTrayIcon class="w-4 h-4" /> {{ t('org.home.view_members') }}
        </button>
      </div>
    </header>

    <div v-if="loading" class="oh__loading">{{ t('common.loading') }}…</div>

    <template v-else>
      <!-- KPI cards -->
      <div class="oh__kpis">
        <div v-for="c in cards" :key="c.key" :class="['oh__kpi', { 'oh__kpi--feat': c.featured }]">
          <div class="oh__kpi-top">
            <component :is="c.icon" class="oh__kpi-icon" />
            <span class="oh__kpi-arrow"><ArrowUpRightIcon class="w-4 h-4" /></span>
          </div>
          <div class="oh__kpi-val">{{ c.value }}</div>
          <div class="oh__kpi-lbl">{{ c.label }}</div>
          <div v-if="c.featured" class="oh__kpi-delta"><ArrowTrendingUpIcon class="w-3.5 h-3.5" /> {{ c.delta }}</div>
          <div v-else class="oh__kpi-subline">{{ c.sub }}</div>
        </div>
      </div>

      <!-- Secondary chips -->
      <div class="oh__strip">
        <div v-for="(s, i) in secondary" :key="i" :class="['oh__chip', 'oh__chip--' + s.color]">
          <div class="oh__chip-val">{{ s.value }}</div>
          <div class="oh__chip-lbl">{{ s.label }}</div>
        </div>
      </div>

      <!-- Row: analytics + gauge -->
      <div class="oh__grid2">
        <section class="oh__card">
          <div class="oh__card-head">
            <h2 class="oh__card-title">{{ t('org.home.monthly') }}</h2>
            <span class="oh__legend"><span class="oh__legend-dot"></span> {{ t('org.stats.applications') }}</span>
          </div>
          <div class="oh__chart">
            <div v-for="(m, i) in monthly" :key="i" class="oh__bar-col">
              <div class="oh__bar-track">
                <div v-if="m.peak" class="oh__bubble" :style="{ opacity: animate ? 1 : 0 }">{{ m.count }}</div>
                <div
                  :class="['oh__bar', m.active ? 'oh__bar--on' : 'oh__bar--off']"
                  :style="{ height: animate ? Math.max(m.pct, m.active ? 12 : 22) + '%' : '0%', transitionDelay: (i * 70) + 'ms' }"
                ></div>
              </div>
              <div class="oh__bar-lbl">{{ m.label }}</div>
            </div>
          </div>
        </section>

        <section class="oh__card oh__gauge-card">
          <h2 class="oh__card-title">{{ t('org.home.gauge_title') }}</h2>
          <div class="oh__gauge">
            <svg viewBox="0 0 200 120" class="oh__gauge-svg">
              <defs>
                <linearGradient id="ohGauge" x1="0" y1="0" x2="1" y2="0">
                  <stop offset="0%" stop-color="#FBBF24" /><stop offset="100%" stop-color="#F59E0B" />
                </linearGradient>
              </defs>
              <path d="M 20 100 A 80 80 0 0 1 180 100" fill="none" stroke="#F1F3F6" stroke-width="18" stroke-linecap="round" />
              <path d="M 20 100 A 80 80 0 0 1 180 100" fill="none" stroke="url(#ohGauge)" stroke-width="18" stroke-linecap="round"
                    stroke-dasharray="251.2" :stroke-dashoffset="gaugeOffset" style="transition: stroke-dashoffset 1.2s cubic-bezier(0.16,1,0.3,1)" />
            </svg>
            <div class="oh__gauge-center">
              <div class="oh__gauge-pct">{{ gaugePct }}%</div>
              <div class="oh__gauge-lbl">{{ t('org.stats.placement') }}</div>
            </div>
          </div>
          <div class="oh__gauge-foot">
            <span><span class="oh__dot oh__dot--gold"></span> {{ kpis.total_interviews ?? 0 }} {{ t('org.stats.interviews') }}</span>
            <span><span class="oh__dot oh__dot--muted"></span> {{ kpis.total_members ?? 0 }} {{ t('org.stats.members') }}</span>
          </div>
        </section>
      </div>

      <!-- Row: next event + funnel + top members -->
      <div class="oh__grid3">
        <!-- Reminder / next event -->
        <section class="oh__card oh__reminder">
          <h2 class="oh__card-title">{{ t('org.home.reminder') }}</h2>
          <template v-if="nextEvent">
            <div class="oh__rem-title">{{ nextEvent.title }}</div>
            <div class="oh__rem-time"><CalendarDaysIcon class="w-4 h-4" /> {{ fmtDate(nextEvent.date) }}</div>
            <a v-if="nextEvent.link" :href="nextEvent.link" target="_blank" class="oh__rem-btn"><VideoCameraIcon class="w-4 h-4" /> {{ t('org.home.join_event') }}</a>
            <button v-else class="oh__rem-btn" @click="router.push('/organisation/mentors')"><CalendarDaysIcon class="w-4 h-4" /> {{ t('org.events.title') }}</button>
          </template>
          <div v-else class="oh__rem-empty">
            <p>{{ t('org.home.no_event') }}</p>
            <button class="oh__rem-btn" @click="router.push('/organisation/mentors')">{{ t('org.events.add') }}</button>
          </div>
        </section>

        <!-- Funnel -->
        <section class="oh__card">
          <h2 class="oh__card-title">{{ t('org.home.funnel') }}</h2>
          <div class="oh__funnel">
            <div v-for="s in funnelSteps" :key="s.key" class="oh__funnel-row">
              <span class="oh__funnel-lbl">{{ s.label }}</span>
              <div class="oh__funnel-track">
                <div class="oh__funnel-fill" :style="{ width: animate ? s.pct + '%' : '0%', background: s.color }"></div>
              </div>
              <span class="oh__funnel-val">{{ s.count }}</span>
            </div>
          </div>
        </section>

        <!-- Top members -->
        <section class="oh__card">
          <h2 class="oh__card-title"><TrophyIcon class="w-4 h-4" /> {{ t('org.home.top_members') }}</h2>
          <ol class="oh__top">
            <li v-for="(m, i) in topMembers" :key="m.id" class="oh__top-row">
              <span class="oh__top-rank" :class="'oh__top-rank--' + (i+1)">{{ i + 1 }}</span>
              <span class="oh__top-name">{{ m.name }}</span>
              <span class="oh__top-stat">{{ m.apps }} <small>{{ t('org.home.apps') }}</small></span>
            </li>
            <li v-if="!topMembers.length" class="oh__empty">{{ t('org.members.empty') }}</li>
          </ol>
        </section>
      </div>
    </template>
  </div>
</template>

<style scoped>
.oh { max-width: 1240px; margin: 0 auto; color: #101828; }
.oh__head { display: flex; align-items: flex-end; justify-content: space-between; gap: 1rem; margin-bottom: 1.5rem; flex-wrap: wrap; }
.oh__title { font-size: 1.9rem; font-weight: 800; margin: 0; letter-spacing: -0.03em; }
.oh__sub { color: #667085; font-size: 0.92rem; margin: 0.3rem 0 0; }
.oh__actions { display: flex; gap: 0.6rem; }
.oh__btn { display: inline-flex; align-items: center; gap: 0.45rem; padding: 0.7rem 1.15rem; border-radius: 999px; font-weight: 700; font-size: 0.85rem; cursor: pointer; border: 1px solid transparent; transition: transform 0.15s, box-shadow 0.15s; }
.oh__btn--primary { background: linear-gradient(135deg, #FBBF24, #F59E0B); color: #fff; box-shadow: 0 10px 22px -10px rgba(245,158,11,0.7); }
.oh__btn--primary:hover { transform: translateY(-2px); }
.oh__btn--ghost { background: #fff; color: #344054; border-color: #EEF0F3; }
.oh__btn--ghost:hover { border-color: #D0D5DD; }
.oh__loading { padding: 4rem; text-align: center; color: #98A2B3; }

.oh__kpis { display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 1rem; margin-bottom: 1.1rem; }
.oh__kpi { position: relative; padding: 1.5rem; border-radius: 1.6rem; background: #fff; border: 1px solid #EEF0F3; box-shadow: 0 1px 2px rgba(16,24,40,0.03); transition: transform 0.2s, box-shadow 0.2s; }
.oh__kpi:hover { transform: translateY(-3px); box-shadow: 0 14px 30px -18px rgba(16,24,40,0.28); }
.oh__kpi-top { display: flex; align-items: center; justify-content: space-between; margin-bottom: 1.4rem; }
.oh__kpi-icon { width: 2.4rem; height: 2.4rem; padding: 0.5rem; border-radius: 0.85rem; color: #475467; background: #F4F5F7; }
.oh__kpi-arrow { width: 2rem; height: 2rem; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: #98A2B3; border: 1px solid #EEF0F3; }
.oh__kpi-val { font-size: 2.4rem; font-weight: 800; line-height: 1; color: #101828; }
.oh__kpi-lbl { font-size: 0.85rem; color: #667085; font-weight: 600; margin-top: 0.4rem; }
.oh__kpi-subline { font-size: 0.72rem; color: #98A2B3; margin-top: 0.7rem; }
.oh__kpi-delta { display: inline-flex; align-items: center; gap: 0.3rem; font-size: 0.72rem; font-weight: 700; margin-top: 0.8rem; padding: 0.2rem 0.6rem; border-radius: 999px; }
/* Featured card (filled gold) */
.oh__kpi--feat { background: linear-gradient(155deg, #F9A93A 0%, #F59E0B 55%, #E08807 100%); border-color: transparent; box-shadow: 0 16px 34px -14px rgba(245,158,11,0.65); }
.oh__kpi--feat .oh__kpi-icon { color: #fff; background: rgba(255,255,255,0.22); }
.oh__kpi--feat .oh__kpi-arrow { color: #fff; border-color: rgba(255,255,255,0.35); background: rgba(255,255,255,0.12); }
.oh__kpi--feat .oh__kpi-val, .oh__kpi--feat .oh__kpi-lbl { color: #fff; }
.oh__kpi--feat .oh__kpi-delta { background: rgba(255,255,255,0.2); color: #fff; }

.oh__strip { display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 0.75rem; margin-bottom: 1.1rem; }
.oh__chip { background: #fff; border: 1px solid #EEF0F3; border-radius: 1.25rem; padding: 1rem 1.1rem; box-shadow: 0 1px 2px rgba(16,24,40,0.03); position: relative; overflow: hidden; }
.oh__chip::before { content: ''; position: absolute; left: 0; top: 0.9rem; bottom: 0.9rem; width: 4px; border-radius: 0 4px 4px 0; }
.oh__chip--gold::before { background: #F59E0B; } .oh__chip--indigo::before { background: #6366F1; }
.oh__chip--emerald::before { background: #10B981; } .oh__chip--sky::before { background: #0EA5E9; }
.oh__chip--pink::before { background: #EC4899; }
.oh__chip-val { font-size: 1.45rem; font-weight: 800; color: #101828; line-height: 1; }
.oh__chip-lbl { font-size: 0.68rem; color: #98A2B3; text-transform: uppercase; letter-spacing: 0.03em; font-weight: 600; margin-top: 0.3rem; }

.oh__grid2 { display: grid; grid-template-columns: 1.7fr 1fr; gap: 1rem; margin-bottom: 1rem; }
.oh__grid3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1rem; }
.oh__card { background: #fff; border: 1px solid #EEF0F3; border-radius: 1.6rem; padding: 1.5rem; box-shadow: 0 1px 2px rgba(16,24,40,0.03); }
.oh__card-head { display: flex; align-items: center; justify-content: space-between; margin-bottom: 1.2rem; }
.oh__card-title { display: flex; align-items: center; gap: 0.4rem; font-size: 1rem; font-weight: 800; margin: 0 0 1.2rem; color: #101828; letter-spacing: -0.01em; }
.oh__card-head .oh__card-title { margin: 0; }
.oh__legend { display: inline-flex; align-items: center; gap: 0.4rem; font-size: 0.72rem; color: #98A2B3; font-weight: 600; }
.oh__legend-dot { width: 0.6rem; height: 0.6rem; border-radius: 3px; background: #F59E0B; }

.oh__chart { display: flex; align-items: flex-end; gap: 0.6rem; height: 210px; }
.oh__bar-col { flex: 1; display: flex; flex-direction: column; align-items: center; height: 100%; }
.oh__bar-track { flex: 1; width: 100%; display: flex; align-items: flex-end; justify-content: center; position: relative; }
.oh__bar { width: 60%; max-width: 42px; border-radius: 999px; transition: height 0.9s cubic-bezier(0.16,1,0.3,1); min-height: 8px; }
.oh__bar--on { background: linear-gradient(180deg, #FBBF24, #F59E0B); box-shadow: 0 6px 14px -6px rgba(245,158,11,0.6); }
.oh__bar--off { background: repeating-linear-gradient(135deg, #EEF0F3, #EEF0F3 5px, #F6F7F9 5px, #F6F7F9 10px); }
.oh__bubble { position: absolute; top: -0.2rem; left: 50%; transform: translateX(-50%); background: #101828; color: #fff; font-size: 0.7rem; font-weight: 800; padding: 0.2rem 0.5rem; border-radius: 0.6rem; transition: opacity 0.5s 0.6s; }
.oh__bubble::after { content: ''; position: absolute; bottom: -4px; left: 50%; transform: translateX(-50%); border: 4px solid transparent; border-top-color: #101828; }
.oh__bar-lbl { font-size: 0.72rem; color: #98A2B3; font-weight: 600; margin-top: 0.55rem; }

.oh__gauge-card { display: flex; flex-direction: column; }
.oh__gauge { position: relative; display: flex; align-items: flex-end; justify-content: center; padding-top: 0.5rem; }
.oh__gauge-svg { width: 100%; max-width: 240px; }
.oh__gauge-center { position: absolute; bottom: 0.2rem; text-align: center; width: 100%; }
.oh__gauge-pct { font-size: 2.1rem; font-weight: 800; color: #101828; }
.oh__gauge-lbl { font-size: 0.7rem; color: #98A2B3; text-transform: uppercase; font-weight: 600; }
.oh__gauge-foot { display: flex; justify-content: center; gap: 1.2rem; margin-top: 1rem; font-size: 0.75rem; color: #667085; }
.oh__gauge-foot span { display: inline-flex; align-items: center; gap: 0.35rem; }
.oh__dot { width: 0.55rem; height: 0.55rem; border-radius: 50%; }
.oh__dot--gold { background: #F59E0B; } .oh__dot--muted { background: #D0D5DD; }

/* Reminder card — dark accent like Donezo time tracker/reminder */
.oh__reminder { background: linear-gradient(160deg, #1D2939 0%, #101828 100%); border-color: transparent; color: #fff; }
.oh__reminder .oh__card-title { color: #fff; }
.oh__rem-title { font-size: 1.15rem; font-weight: 800; line-height: 1.3; }
.oh__rem-time { display: inline-flex; align-items: center; gap: 0.4rem; font-size: 0.8rem; color: #98A2B3; margin: 0.6rem 0 1.2rem; }
.oh__rem-btn { display: inline-flex; align-items: center; gap: 0.45rem; padding: 0.7rem 1.1rem; border-radius: 999px; background: linear-gradient(135deg, #FBBF24, #F59E0B); color: #fff; border: none; font-weight: 700; font-size: 0.82rem; cursor: pointer; text-decoration: none; }
.oh__rem-empty { color: #98A2B3; font-size: 0.85rem; }
.oh__rem-empty p { margin: 0.5rem 0 1rem; }

.oh__funnel { display: flex; flex-direction: column; gap: 0.8rem; }
.oh__funnel-row { display: flex; align-items: center; gap: 0.8rem; }
.oh__funnel-lbl { width: 92px; font-size: 0.78rem; font-weight: 600; color: #475467; flex-shrink: 0; }
.oh__funnel-track { flex: 1; height: 13px; background: #F1F3F6; border-radius: 999px; overflow: hidden; }
.oh__funnel-fill { height: 100%; border-radius: 999px; transition: width 1s cubic-bezier(0.16,1,0.3,1); }
.oh__funnel-val { width: 30px; text-align: right; font-weight: 800; font-size: 0.88rem; color: #101828; }

.oh__top { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 0.5rem; }
.oh__top-row { display: flex; align-items: center; gap: 0.7rem; padding: 0.55rem 0.6rem; border-radius: 0.9rem; background: #F9FAFB; }
.oh__top-rank { width: 1.6rem; height: 1.6rem; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 0.75rem; font-weight: 800; background: #EAECF0; color: #475467; flex-shrink: 0; }
.oh__top-rank--1 { background: linear-gradient(135deg, #FBBF24, #F59E0B); color: #fff; }
.oh__top-rank--2 { background: #D0D5DD; color: #101828; }
.oh__top-rank--3 { background: #FED7AA; color: #9A3412; }
.oh__top-name { flex: 1; font-size: 0.85rem; font-weight: 600; color: #344054; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.oh__top-stat { font-size: 0.85rem; font-weight: 800; color: #D97706; }
.oh__top-stat small { color: #98A2B3; font-weight: 500; }
.oh__empty { color: #98A2B3; font-size: 0.85rem; text-align: center; padding: 1rem; }

@media (max-width: 980px) {
  .oh__grid2, .oh__grid3 { grid-template-columns: 1fr; }
}
</style>
