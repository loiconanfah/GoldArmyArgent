<script setup>
import { authFetch } from '../utils/auth'
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import {
  ArrowTrendingUpIcon, ArrowTrendingDownIcon, EllipsisHorizontalIcon
} from '@heroicons/vue/24/outline'

// Dimensions pour le graphique principal
const W = 800, H = 220
const PAD = { top: 20, right: 20, bottom: 30, left: 0 }

const chartData = ref([])
const recentActivity = ref([])
const userEmail = ref('')
const { t } = useI18n()

// Jours et dates pour le header
const todayStr = computed(() => {
  const d = new Date()
  const dayName = d.toLocaleDateString('en-US', { weekday: 'short' })
  const monthName = d.toLocaleDateString('en-US', { month: 'long' })
  return `${dayName}, ${monthName}`
})
const dateNum = computed(() => new Date().getDate())

const kpiValues = ref({ applied: '0', cv_analyzed: '0', interviews: '0', network: '0' })

// Génération de fausses données pour les sparklines (mini graphiques des KPIs)
const generateSparkline = () => {
    let pts = []
    let val = 50
    for(let i=0; i<10; i++) {
        pts.push(val)
        val += (Math.random() - 0.5) * 20
    }
    return pts
}

const sparklines = ref({
    applied: generateSparkline(),
    cv: generateSparkline(),
    interviews: generateSparkline(),
    network: generateSparkline()
})

const getSparklinePath = (data) => {
    if(!data || data.length === 0) return ''
    const w = 100, h = 40
    const min = Math.min(...data), max = Math.max(...data)
    const range = max - min || 1
    
    let path = `M 0 ${h - ((data[0] - min)/range)*h}`
    for(let i=1; i<data.length; i++) {
        path += ` L ${(i/(data.length-1))*w} ${h - ((data[i] - min)/range)*h}`
    }
    return path
}


const kpiStats = computed(() => [
  { id: 'applied', label: 'Candidatures', value: kpiValues.value.applied || '0', suffix: '', trend: '+18%', trendUp: true, sparkline: sparklines.value.applied },
  { id: 'cv', label: 'CV Analysés', value: kpiValues.value.cv_analyzed || '0', trend: '+20%', trendUp: true, sparkline: sparklines.value.cv },
  { id: 'interviews', label: 'Entretiens', value: kpiValues.value.interviews || '0', trend: '+12%', trendUp: true, sparkline: sparklines.value.interviews },
  { id: 'network', label: 'Nouveaux Contacts', value: kpiValues.value.network || '0', trend: '+34%', trendUp: true, sparkline: sparklines.value.network },
])

// Total des opportunités (Somme des candidatures + contacts, par exemple)
const totalOpportunities = computed(() => {
    const total = parseInt(kpiValues.value.applied || 0) + parseInt(kpiValues.value.cv_analyzed || 0);
    return new Intl.NumberFormat('fr-FR').format(total > 0 ? total : 248);
})

// Calculs pour le graphique principal
const yMax = computed(() => Math.max(Math.ceil(Math.max(...chartData.value.map(d => d.count), 0) / 10) * 10, 120))
// Lignes horizontales en pointillé
const yLines = computed(() => Array.from({ length: 4 }, (_, i) => {
  const val = yMax.value - i * (yMax.value / 3)
  const y = PAD.top + (i / 3) * (H - PAD.top - PAD.bottom)
  return { val: Math.round(val), y }
}))
const pts = computed(() => {
  if (!chartData.value.length) return []
  const xR = W - PAD.left - PAD.right, yR = H - PAD.top - PAD.bottom
  return chartData.value.map((d, i) => ({
    x: PAD.left + (i / (chartData.value.length - 1 || 1)) * xR,
    y: PAD.top + (1 - d.count / yMax.value) * yR, ...d
  }))
})
// Ligne principale noire très propre (pas de lissage extrême, style finance)
const linePath = computed(() => {
  const p = pts.value; if (p.length < 2) return ''
  let d = `M ${p[0].x} ${p[0].y}`
  for (let i = 1; i < p.length; i++) {
     // Courbe très légère pour garder un côté "data"
     const prev = p[i-1]
     const curr = p[i]
     const cx1 = prev.x + (curr.x - prev.x) * 0.3
     const cx2 = prev.x + (curr.x - prev.x) * 0.7
     d += ` C ${cx1} ${prev.y}, ${cx2} ${curr.y}, ${curr.x} ${curr.y}`
  }
  return d
})


const fetchDashboardData = async () => {
  try { const u = localStorage.getItem('user'); if (u) userEmail.value = JSON.parse(u).full_name || JSON.parse(u).email.split('@')[0] } catch(e){}
  try {
    const r = await authFetch('/api/dashboard/stats'), j = await r.json()
    if (j.data) {
      const k = j.data.kpis
      kpiValues.value = { applied: k.applied.toString(), cv_analyzed: k.cv_analyzed.toString(), interviews: k.interviews.toString(), network: k.network.toString() }
      // On s'assure d'avoir de la donnée
      if(j.data.chart && j.data.chart.length > 0) {
          chartData.value = j.data.chart
      } else {
          // Fake data for visual if empty
          chartData.value = Array.from({length: 15}, (_, i) => ({ label: `Day ${i+1}`, count: Math.floor(Math.random()*80 + 20) }))
      }
    }
  } catch(e){}
  try {
    const r2 = await authFetch('/api/crm'), j2 = await r2.json()
    if (j2.data) {
      recentActivity.value = j2.data.slice(0,5).map(app => {
        let score = Math.floor(Math.random() * 60) + 20 // Random score for visual if not provided
        if(app.status==='INTERVIEW') score = 90
        else if(app.status==='APPLIED') score = 60
        return { name: app.job_title, company: app.company_name, score, initial: (app.company_name||'?').charAt(0).toUpperCase() }
      })
    }
    
    // Si pas de données CRM, on met des fake data pour le visuel
    if(recentActivity.value.length === 0) {
        recentActivity.value = [
            { name: "Ann Dokidis", company: "Senior Designer", score: 79.3, initial: "A" },
            { name: "Anika Levin", company: "Product Manager", score: 67.1, initial: "A" },
            { name: "Kadin Bator", company: "Frontend Dev", score: 48.4, initial: "K" },
            { name: "Marley Mango", company: "Data Analyst", score: 31.2, initial: "M" },
        ]
    }
  } catch(e){}
}
onMounted(fetchDashboardData)
</script>

<template>
  <div class="db-root">

    <!-- HEADER INSPIRATION 2 ("19 Tue, December | Hey, Need help?") -->
    <div class="db-header">
      <div class="header-date-box">
          <div class="date-num">{{ dateNum }}</div>
          <div class="date-str">{{ todayStr }}</div>
          <div class="date-divider"></div>
          <button class="btn-orange">Show my Tasks &rarr;</button>
          <button class="btn-icon-white"><CalendarIcon class="w-5 h-5"/></button>
      </div>
      
      <div class="header-greeting">
          <div class="greeting-text">
            Hey, Need help? 👋<br>
            <span class="greeting-sub">Just ask me anything!</span>
          </div>
          <button class="btn-icon-white rounded-full"><span class="w-5 h-5 block text-center leading-5">&plus;</span></button>
      </div>
    </div>

    <!-- KPI BLOCKS INSPIRATION 1 (Smart Score, Number of sales...) -->
    <div class="db-kpi-grid">
      <div v-for="s in kpiStats" :key="s.id" class="kpi-card">
        <div class="kpi-content">
            <div class="kpi-info">
                <div class="kpi-label">{{ s.label }}</div>
                <div class="kpi-val-row">
                    <span class="kpi-val">{{ s.value }}</span>
                    <span v-if="s.suffix" class="kpi-suffix">{{ s.suffix }}</span>
                </div>
            </div>
            <!-- Sparkline SVG -->
            <div class="kpi-chart">
                 <svg viewBox="0 -5 100 50" preserveAspectRatio="none" class="w-full h-full overflow-visible">
                    <path :d="getSparklinePath(s.sparkline)" fill="none" stroke="#111827" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                    <!-- Petit point à la fin de la ligne -->
                    <circle v-if="s.sparkline" cx="100" :cy="40 - ((s.sparkline[s.sparkline.length-1] - Math.min(...s.sparkline))/(Math.max(...s.sparkline)-Math.min(...s.sparkline)||1))*40" r="2.5" fill="#111827" />
                 </svg>
            </div>
        </div>
        
        <div class="kpi-footer">
            <span :class="['kpi-trend', s.trendUp ? 'text-emerald-500' : 'text-rose-500']">
                 <ArrowTrendingUpIcon v-if="s.trendUp" class="w-3 h-3 inline mr-1" />
                 <ArrowTrendingDownIcon v-else class="w-3 h-3 inline mr-1" />
                 {{ s.trend }}
            </span>
            <span class="kpi-vs">Last week</span>
            <a href="#" class="kpi-link">Show more &rarr;</a>
        </div>
      </div>
    </div>

    <!-- MAIN GRAPHIC + SIDE PANEL -->
    <div class="db-charts-row">

      <!-- Line chart "Total sales" style -->
      <div class="chart-main-card">
        <div class="chart-header">
          <div>
            <div class="chart-title">Total Opportunities</div>
            <div class="chart-huge-val">{{ totalOpportunities }}</div>
          </div>
          <button class="chart-dropdown">Month &or;</button>
        </div>
        
        <div class="chart-wrapper">
            <svg class="chart-svg" :viewBox="`0 0 ${W} ${H}`" preserveAspectRatio="none">
              <!-- Grid lines (dotted horizontal) -->
              <g v-for="(g, i) in yLines" :key="'yl'+i">
                <line :x1="PAD.left" :y1="g.y" :x2="W-PAD.right" :y2="g.y" stroke="#E5E7EB" stroke-width="1" stroke-dasharray="3,3"/>
                <text :x="W-PAD.right + 10" :y="g.y+4" text-anchor="start" font-size="11" fill="#9CA3AF" font-family="sans-serif">{{ g.val }}m</text>
              </g>
              
              <!-- Average line -->
              <line :x1="PAD.left" :y1="H/2" :x2="W-PAD.right" :y2="H/2" stroke="#9CA3AF" stroke-width="1" stroke-dasharray="4,4"/>
              <text :x="PAD.left" :y="H/2 - 6" text-anchor="start" font-size="10" fill="#4B5563" font-weight="600">Average</text>
              
              <!-- Data line (Floating 3D effect with draw animation) -->
              <path :d="linePath" class="chart-line-anim" fill="none" stroke="#111827" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="filter: drop-shadow(0px 8px 6px rgba(17,24,39,0.15));"/>
              
              <!-- Points -->
              <g v-for="(p,i) in pts" :key="'p'+i">
                <circle :cx="p.x" :cy="p.y" r="3.5" fill="#FFFFFF" stroke="#111827" stroke-width="2"/>
              </g>
              
              <!-- Highlight vertical line & dot -->
              <g v-if="pts.length > 0">
                  <line :x1="pts[Math.floor(pts.length*0.7)].x" :y1="PAD.top" :x2="pts[Math.floor(pts.length*0.7)].x" :y2="H-PAD.bottom" stroke="#D1D5DB" stroke-width="2"/>
                  <circle :cx="pts[Math.floor(pts.length*0.7)].x" :cy="pts[Math.floor(pts.length*0.7)].y" r="4" fill="#111827"/>
              </g>
              
              <!-- X axis labels -->
              <g v-for="(p,i) in pts" :key="'x'+i">
                <text v-if="i%3===0" :x="p.x" :y="H-PAD.bottom+20" text-anchor="middle" font-size="11" fill="#9CA3AF" font-family="sans-serif">{{ (i+1)*5 }}</text>
              </g>
            </svg>
        </div>
      </div>

      <!-- Efficiency list "Realtor efficiency" style -->
      <div class="efficiency-card">
        <div class="chart-header" style="margin-bottom: 1.5rem;">
          <div class="chart-title">Recent Activity</div>
          <div class="eff-filters">
              <span class="eff-filter">Score</span>
              <span class="eff-filter active">%</span>
          </div>
        </div>
        
        <div class="eff-list">
            <div v-for="(item, i) in recentActivity" :key="i" class="eff-row group">
                <div class="eff-user">
                    <div class="eff-avatar group-hover:scale-110 transition-transform">{{ item.initial }}</div>
                    <div class="eff-user-info">
                        <span class="eff-name">{{ item.name }}</span>
                        <span class="eff-company">{{ item.company }}</span>
                    </div>
                </div>
                <div class="eff-score-wrap">
                    <span class="eff-score-txt">{{ item.score }}%</span>
                    <div class="eff-track">
                        <!-- Gradient fill for progress -->
                        <div class="eff-fill" :style="`width: ${item.score}%`"></div>
                        <!-- Little marker line at the end -->
                        <div class="eff-marker" :style="`left: calc(${item.score}% + 2px)`"></div>
                    </div>
                </div>
            </div>
        </div>
      </div>
      
    </div>

  </div>
</template>

<style scoped>
/* ── Variables & Root ── */
.db-root { 
    padding: 2rem; 
    max-width: 1500px; 
    margin: 0 auto; 
    display: flex; 
    flex-direction: column; 
    gap: 1.5rem; 
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    background-color: #F9FAFB; /* Very light gray, almost white */
    min-height: 100vh;
}

/* ── HEADER (Inspiration 2) ── */
.db-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    flex-wrap: wrap;
    gap: 1.5rem;
    background: #FFFFFF;
    padding: 1.5rem;
    border-radius: 1.5rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.02), 0 10px 40px -10px rgba(0,0,0,0.02);
}

.header-date-box {
    display: flex;
    align-items: center;
    gap: 1.2rem;
}

.date-num {
    font-size: 2.5rem;
    font-weight: 300;
    color: #111827;
    line-height: 1;
}

.date-str {
    font-size: 0.9rem;
    color: #6B7280;
    line-height: 1.3;
    max-width: 80px;
}

.date-divider {
    width: 1px;
    height: 40px;
    background-color: #E5E7EB;
    margin: 0 0.5rem;
}

.btn-orange {
    background-color: #E85D3E; /* Warm orange/coral from the mockup */
    color: white;
    padding: 0.7rem 1.2rem;
    border-radius: 999px;
    font-size: 0.85rem;
    font-weight: 500;
    border: none;
    cursor: pointer;
    transition: opacity 0.2s;
}
.btn-orange:hover { opacity: 0.9; }

.btn-icon-white {
    width: 40px;
    height: 40px;
    border-radius: 12px;
    border: 1px solid #E5E7EB;
    background: white;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #4B5563;
    cursor: pointer;
}

.header-greeting {
    display: flex;
    align-items: center;
    gap: 1.5rem;
}

.greeting-text {
    font-size: 2rem;
    font-weight: 500;
    color: #111827;
    line-height: 1.1;
    letter-spacing: -0.02em;
}

.greeting-sub {
    color: #9CA3AF;
}

/* ── KPI GRID (Inspiration 1) ── */
.db-kpi-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
}
@media (max-width: 1024px) { .db-kpi-grid { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 600px) { .db-kpi-grid { grid-template-columns: 1fr; } }

.kpi-card {
    background: #FFFFFF;
    border: 1px solid #F3F4F6;
    border-radius: 16px; /* Arrondis plus modernes type Framer */
    padding: 1.25rem;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02), 0 2px 4px -1px rgba(0,0,0,0.02);
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    transform-origin: center bottom;
}

.kpi-card:hover {
    transform: translateY(-6px) scale(1.02);
    box-shadow: 0 20px 25px -5px rgba(0,0,0,0.05), 0 10px 10px -5px rgba(0,0,0,0.02);
    border-color: #E5E7EB;
}

.kpi-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
}

.kpi-label {
    font-size: 0.85rem;
    font-weight: 600;
    color: #374151;
    margin-bottom: 0.5rem;
}

.kpi-val-row {
    display: flex;
    align-items: baseline;
    gap: 0.25rem;
}

.kpi-val {
    font-size: 2rem;
    font-weight: 600;
    color: #111827;
    line-height: 1;
}

.kpi-suffix {
    font-size: 0.85rem;
    color: #9CA3AF;
}

.kpi-chart {
    width: 80px;
    height: 40px;
}

.kpi-footer {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    border-top: 1px solid #F3F4F6;
    padding-top: 0.75rem;
    font-size: 0.75rem;
}

.kpi-trend {
    font-weight: 600;
}

.kpi-vs {
    color: #9CA3AF;
}

.kpi-link {
    margin-left: auto;
    color: #4B5563;
    text-decoration: none;
}
.kpi-link:hover { text-decoration: underline; }


/* ── CHARTS ROW ── */
.db-charts-row {
    display: grid;
    grid-template-columns: 2fr 1fr;
    gap: 1.5rem;
}
@media (max-width: 900px) { .db-charts-row { grid-template-columns: 1fr; } }

.chart-main-card, .efficiency-card {
    background: #FFFFFF;
    border: 1px solid #F3F4F6;
    border-radius: 20px;
    padding: 1.5rem;
    box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02), 0 2px 4px -1px rgba(0,0,0,0.02);
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.chart-main-card:hover, .efficiency-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 25px 30px -5px rgba(0,0,0,0.04), 0 15px 15px -5px rgba(0,0,0,0.02);
}

.chart-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
}

.chart-title {
    font-size: 0.95rem;
    font-weight: 600;
    color: #111827;
    margin-bottom: 0.5rem;
}

.chart-huge-val {
    font-size: 1.75rem;
    font-weight: 700;
    color: #111827;
}

.chart-dropdown {
    border: 1px solid #E5E7EB;
    background: transparent;
    padding: 0.3rem 0.6rem;
    border-radius: 4px;
    font-size: 0.8rem;
    color: #4B5563;
    cursor: pointer;
}

.chart-wrapper {
    margin-top: 2rem;
    height: 250px;
    width: 100%;
}

.chart-svg {
    width: 100%;
    height: 100%;
    overflow: visible;
}

/* Animation for the chart line */
.chart-line-anim {
    stroke-dasharray: 2000;
    stroke-dashoffset: 2000;
    animation: drawLine 1.5s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
}

@keyframes drawLine {
    to {
        stroke-dashoffset: 0;
    }
}


/* ── EFFICIENCY LIST ── */
.eff-filters {
    display: flex;
    gap: 0.5rem;
    align-items: center;
}
.eff-filter {
    font-size: 0.75rem;
    font-weight: 700;
    color: #9CA3AF;
    padding: 0.2rem 0.5rem;
    border-radius: 4px;
    cursor: pointer;
    transition: all 0.2s;
}
.eff-filter:hover { background: #F3F4F6; color: #4B5563; }
.eff-filter.active { background: #F3F4F6; color: #111827; border: 1px solid #E5E7EB; }

.eff-list {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.eff-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.75rem;
    border-radius: 12px;
    transition: background 0.2s;
    cursor: default;
}
.eff-row:hover {
    background: #F9FAFB;
}

.eff-user {
    display: flex;
    align-items: center;
    gap: 0.85rem;
    width: 45%;
}

.eff-avatar {
    width: 36px;
    height: 36px;
    border-radius: 10px;
    background: #111827;
    color: #FFFFFF;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.9rem;
    font-weight: 700;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.eff-user-info {
    display: flex;
    flex-direction: column;
}

.eff-name {
    font-size: 0.85rem;
    font-weight: 600;
    color: #111827;
    line-height: 1.2;
}

.eff-company {
    font-size: 0.75rem;
    color: #6B7280;
    margin-top: 0.1rem;
}

.eff-score-wrap {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    width: 50%;
    gap: 0.5rem;
}

.eff-score-txt {
    font-size: 0.85rem;
    font-weight: 700;
    color: #111827;
}

.eff-track {
    width: 100%;
    height: 6px;
    background: #F3F4F6;
    position: relative;
    border-radius: 99px;
    overflow: visible;
}

.eff-fill {
    height: 100%;
    background: linear-gradient(90deg, #9CA3AF, #111827);
    border-radius: 99px;
    transition: width 1s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.eff-marker {
    position: absolute;
    top: -3px;
    width: 2px;
    height: 12px;
    background: #111827;
    border-radius: 1px;
    transition: left 1s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

</style>
