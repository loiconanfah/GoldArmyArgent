<script setup>
import { ref, onMounted, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { authFetch } from '@/utils/auth'
import {
  UsersIcon, CheckCircleIcon, DocumentTextIcon, BriefcaseIcon,
  ChartBarIcon, TrophyIcon
} from '@heroicons/vue/24/outline'

const { t } = useI18n()
const loading = ref(true)
const analytics = ref(null)
const animate = ref(false)

// Compteurs animés
const counters = ref({ members: 0, active: 0, applications: 0, interviews: 0 })

function tween(key, target) {
  const dur = 900, start = performance.now()
  function step(now) {
    const p = Math.min((now - start) / dur, 1)
    const eased = 1 - Math.pow(1 - p, 3)
    counters.value[key] = Math.round(target * eased)
    if (p < 1) requestAnimationFrame(step)
  }
  requestAnimationFrame(step)
}

const funnelSteps = computed(() => {
  const f = analytics.value?.funnel || {}
  const order = [
    { key: 'TO_APPLY', label: t('org.funnel.to_apply'), color: '#64748b' },
    { key: 'APPLIED', label: t('org.funnel.applied'), color: '#6366f1' },
    { key: 'FOLLOW_UP', label: t('org.funnel.follow_up'), color: '#0ea5e9' },
    { key: 'INTERVIEW', label: t('org.funnel.interview'), color: '#10b981' },
    { key: 'REJECTED', label: t('org.funnel.rejected'), color: '#ef4444' },
  ]
  const max = Math.max(1, ...order.map(o => f[o.key] || 0))
  return order.map(o => ({ ...o, count: f[o.key] || 0, pct: Math.round(((f[o.key] || 0) / max) * 100) }))
})

const monthly = computed(() => analytics.value?.monthly || [])
const topMembers = computed(() => analytics.value?.top_members || [])
const withCvPct = computed(() => {
  const k = analytics.value?.kpis
  if (!k || !k.total_members) return 0
  return Math.round((k.with_cv / k.total_members) * 100)
})

const secondary = computed(() => {
  const k = analytics.value?.kpis || {}
  const c = analytics.value?.counts || {}
  return [
    { label: t('org.stats.placement'), value: (k.placement_rate ?? 0) + '%', color: 'emerald' },
    { label: t('org.stats.avg'), value: k.avg_applications ?? 0, color: 'indigo' },
    { label: t('org.stats.with_cv'), value: k.with_cv ?? 0, color: 'gold' },
    { label: t('org.roles.mentor') + 's', value: c.mentors ?? 0, color: 'indigo' },
    { label: t('org.events.title'), value: c.events ?? 0, color: 'gold' },
    { label: t('org.nav.network'), value: c.network ?? 0, color: 'sky' },
    { label: t('org.nav.community'), value: c.posts ?? 0, color: 'pink' },
  ]
})

async function load() {
  loading.value = true
  try {
    const res = await authFetch('/api/org/analytics')
    const json = await res.safeJson()
    if (json?.status === 'success') {
      analytics.value = json.data
      const k = json.data.kpis
      setTimeout(() => {
        animate.value = true
        tween('members', k.total_members)
        tween('active', k.active_members)
        tween('applications', k.total_applications)
        tween('interviews', k.total_interviews)
      }, 100)
    }
  } catch (e) {}
  finally { loading.value = false }
}

onMounted(load)
</script>

<template>
  <div class="oh">
    <header class="oh__head">
      <h1 class="oh__title">{{ t('org.tabs.overview') }}</h1>
      <p class="oh__sub">{{ t('org.home.sub') }}</p>
    </header>

    <div v-if="loading" class="oh__loading">{{ t('common.loading') }}…</div>

    <template v-else>
      <!-- KPI cards -->
      <div class="oh__kpis">
        <div class="oh__kpi oh__kpi--a">
          <UsersIcon class="oh__kpi-icon" />
          <div class="oh__kpi-val">{{ counters.members }}</div>
          <div class="oh__kpi-lbl">{{ t('org.stats.members') }}</div>
        </div>
        <div class="oh__kpi oh__kpi--b">
          <CheckCircleIcon class="oh__kpi-icon" />
          <div class="oh__kpi-val">{{ counters.active }}</div>
          <div class="oh__kpi-lbl">{{ t('org.stats.active') }}</div>
        </div>
        <div class="oh__kpi oh__kpi--c">
          <BriefcaseIcon class="oh__kpi-icon" />
          <div class="oh__kpi-val">{{ counters.applications }}</div>
          <div class="oh__kpi-lbl">{{ t('org.stats.applications') }}</div>
        </div>
        <div class="oh__kpi oh__kpi--d">
          <ChartBarIcon class="oh__kpi-icon" />
          <div class="oh__kpi-val">{{ counters.interviews }}</div>
          <div class="oh__kpi-lbl">{{ t('org.stats.interviews') }}</div>
        </div>
      </div>

      <!-- Secondary KPI strip -->
      <div class="oh__strip">
        <div v-for="(s, i) in secondary" :key="i" :class="['oh__chip', 'oh__chip--' + s.color]">
          <div class="oh__chip-val">{{ s.value }}</div>
          <div class="oh__chip-lbl">{{ s.label }}</div>
        </div>
      </div>

      <div class="oh__grid">
        <!-- Monthly bar chart -->
        <section class="oh__card oh__card--wide">
          <h2 class="oh__card-title"><ChartBarIcon class="w-4 h-4" /> {{ t('org.home.monthly') }}</h2>
          <div class="oh__chart">
            <div v-for="(m, i) in monthly" :key="i" class="oh__bar-col">
              <div class="oh__bar-track">
                <div
                  class="oh__bar"
                  :style="{ height: animate ? m.pct + '%' : '0%', transitionDelay: (i * 60) + 'ms' }"
                >
                  <span v-if="m.count" class="oh__bar-count">{{ m.count }}</span>
                </div>
              </div>
              <div class="oh__bar-lbl">{{ m.label }}</div>
            </div>
          </div>
        </section>

        <!-- Donut: CV completion -->
        <section class="oh__card">
          <h2 class="oh__card-title"><DocumentTextIcon class="w-4 h-4" /> {{ t('org.home.cv_rate') }}</h2>
          <div class="oh__donut-wrap">
            <svg viewBox="0 0 120 120" class="oh__donut">
              <defs>
                <linearGradient id="ohGold" x1="0" y1="0" x2="1" y2="1">
                  <stop offset="0%" stop-color="#FBBF24" />
                  <stop offset="100%" stop-color="#F59E0B" />
                </linearGradient>
              </defs>
              <circle cx="60" cy="60" r="50" class="oh__donut-bg" />
              <circle
                cx="60" cy="60" r="50" class="oh__donut-fg"
                :stroke-dasharray="314"
                :stroke-dashoffset="animate ? 314 - (314 * withCvPct / 100) : 314"
              />
            </svg>
            <div class="oh__donut-center">
              <div class="oh__donut-pct">{{ withCvPct }}%</div>
              <div class="oh__donut-lbl">{{ t('org.stats.with_cv') }}</div>
            </div>
          </div>
        </section>

        <!-- Funnel -->
        <section class="oh__card oh__card--wide">
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
.oh { max-width: 1200px; margin: 0 auto; color: #1E293B; }
.oh__head { margin-bottom: 1.5rem; }
.oh__title { font-size: 1.7rem; font-weight: 800; margin: 0; letter-spacing: -0.02em; }
.oh__sub { color: #64748B; font-size: 0.9rem; margin: 0.3rem 0 0; }
.oh__loading { padding: 3rem; text-align: center; color: #94A3B8; }

.oh__kpis { display: grid; grid-template-columns: repeat(auto-fit, minmax(190px, 1fr)); gap: 1rem; margin-bottom: 1.25rem; }
.oh__kpi { position: relative; padding: 1.4rem; border-radius: 1.1rem; background: #fff; border: 1px solid #E2E8F0; overflow: hidden; box-shadow: 0 1px 2px rgba(15,23,42,0.04), 0 8px 24px -16px rgba(15,23,42,0.15); transition: transform 0.2s, box-shadow 0.2s; }
.oh__kpi:hover { transform: translateY(-3px); box-shadow: 0 1px 2px rgba(15,23,42,0.04), 0 16px 32px -18px rgba(15,23,42,0.25); }
.oh__kpi::after { content: ''; position: absolute; right: -24px; top: -24px; width: 96px; height: 96px; border-radius: 50%; opacity: 0.1; }
.oh__kpi--a::after { background: #F59E0B; } .oh__kpi--b::after { background: #6366F1; }
.oh__kpi--c::after { background: #0EA5E9; } .oh__kpi--d::after { background: #10B981; }
.oh__kpi-icon { width: 2.2rem; height: 2.2rem; padding: 0.45rem; border-radius: 0.7rem; margin-bottom: 0.7rem; }
.oh__kpi--a .oh__kpi-icon { color: #D97706; background: #FEF3C7; }
.oh__kpi--b .oh__kpi-icon { color: #4F46E5; background: #EEF2FF; }
.oh__kpi--c .oh__kpi-icon { color: #0284C7; background: #E0F2FE; }
.oh__kpi--d .oh__kpi-icon { color: #059669; background: #D1FAE5; }
.oh__kpi-val { font-size: 2.2rem; font-weight: 800; line-height: 1; color: #0F172A; }
.oh__kpi-lbl { font-size: 0.72rem; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 600; margin-top: 0.35rem; }

.oh__strip { display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 0.75rem; margin-bottom: 1.25rem; }
.oh__chip { background: #fff; border: 1px solid #E2E8F0; border-radius: 0.9rem; padding: 0.9rem 1rem; box-shadow: 0 1px 2px rgba(15,23,42,0.04); position: relative; overflow: hidden; }
.oh__chip::before { content: ''; position: absolute; left: 0; top: 0; bottom: 0; width: 4px; }
.oh__chip--gold::before { background: #F59E0B; } .oh__chip--indigo::before { background: #6366F1; }
.oh__chip--emerald::before { background: #10B981; } .oh__chip--sky::before { background: #0EA5E9; }
.oh__chip--pink::before { background: #EC4899; }
.oh__chip-val { font-size: 1.4rem; font-weight: 800; color: #0F172A; line-height: 1; }
.oh__chip-lbl { font-size: 0.68rem; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.03em; font-weight: 600; margin-top: 0.3rem; }

.oh__grid { display: grid; grid-template-columns: 2fr 1fr; gap: 1rem; }
.oh__card { background: #fff; border: 1px solid #E2E8F0; border-radius: 1.1rem; padding: 1.4rem; box-shadow: 0 1px 2px rgba(15,23,42,0.04), 0 8px 24px -18px rgba(15,23,42,0.18); }
.oh__card--wide { grid-column: 1; }
.oh__card:nth-child(2) { grid-column: 2; grid-row: 1; }
.oh__card-title { display: flex; align-items: center; gap: 0.45rem; font-size: 0.9rem; font-weight: 700; margin: 0 0 1.2rem; color: #334155; }

.oh__chart { display: flex; align-items: flex-end; gap: 0.55rem; height: 190px; padding-top: 0.5rem; }
.oh__bar-col { flex: 1; display: flex; flex-direction: column; align-items: center; height: 100%; }
.oh__bar-track { flex: 1; width: 100%; display: flex; align-items: flex-end; background: linear-gradient(180deg, #F8FAFC, transparent); border-radius: 6px; }
.oh__bar { width: 78%; margin: 0 auto; border-radius: 7px 7px 0 0; background: linear-gradient(180deg, #FBBF24, #F59E0B); transition: height 0.9s cubic-bezier(0.16,1,0.3,1); position: relative; min-height: 3px; box-shadow: 0 -2px 8px -2px rgba(245,158,11,0.4); }
.oh__bar-count { position: absolute; top: -1.25rem; left: 50%; transform: translateX(-50%); font-size: 0.66rem; font-weight: 800; color: #B45309; }
.oh__bar-lbl { font-size: 0.66rem; color: #94A3B8; font-weight: 600; margin-top: 0.45rem; }

.oh__donut-wrap { position: relative; display: flex; align-items: center; justify-content: center; height: 190px; }
.oh__donut { width: 168px; height: 168px; transform: rotate(-90deg); }
.oh__donut-bg { fill: none; stroke: #F1F5F9; stroke-width: 13; }
.oh__donut-fg { fill: none; stroke: url(#ohGold); stroke-width: 13; stroke-linecap: round; transition: stroke-dashoffset 1.1s cubic-bezier(0.16,1,0.3,1); }
.oh__donut-center { position: absolute; text-align: center; }
.oh__donut-pct { font-size: 1.9rem; font-weight: 800; color: #0F172A; }
.oh__donut-lbl { font-size: 0.68rem; color: #94A3B8; text-transform: uppercase; font-weight: 600; }

.oh__funnel { display: flex; flex-direction: column; gap: 0.75rem; }
.oh__funnel-row { display: flex; align-items: center; gap: 0.8rem; }
.oh__funnel-lbl { width: 92px; font-size: 0.78rem; font-weight: 600; color: #475569; flex-shrink: 0; }
.oh__funnel-track { flex: 1; height: 13px; background: #F1F5F9; border-radius: 999px; overflow: hidden; }
.oh__funnel-fill { height: 100%; border-radius: 999px; transition: width 1s cubic-bezier(0.16,1,0.3,1); }
.oh__funnel-val { width: 34px; text-align: right; font-weight: 800; font-size: 0.88rem; color: #0F172A; }

.oh__top { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 0.5rem; }
.oh__top-row { display: flex; align-items: center; gap: 0.7rem; padding: 0.55rem 0.6rem; border-radius: 0.7rem; background: #F8FAFC; border: 1px solid #F1F5F9; }
.oh__top-rank { width: 1.6rem; height: 1.6rem; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 0.75rem; font-weight: 800; background: #E2E8F0; color: #475569; flex-shrink: 0; }
.oh__top-rank--1 { background: linear-gradient(135deg, #FBBF24, #F59E0B); color: #fff; }
.oh__top-rank--2 { background: #CBD5E1; color: #0F172A; }
.oh__top-rank--3 { background: #FED7AA; color: #9A3412; }
.oh__top-name { flex: 1; font-size: 0.85rem; font-weight: 600; color: #334155; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.oh__top-stat { font-size: 0.85rem; font-weight: 800; color: #D97706; }
.oh__top-stat small { color: #94A3B8; font-weight: 500; }
.oh__empty { color: #94A3B8; font-size: 0.85rem; text-align: center; padding: 1rem; }

@media (max-width: 860px) {
  .oh__grid { grid-template-columns: 1fr; }
  .oh__card--wide, .oh__card:nth-child(2) { grid-column: 1 !important; grid-row: auto !important; }
}
</style>
