<script setup>
import { authFetch } from '../utils/auth'
import { ref, computed, onMounted } from 'vue'
import { 
  BriefcaseIcon,
  DocumentCheckIcon,
  ChatBubbleLeftRightIcon,
  UserPlusIcon,
  EllipsisVerticalIcon,
  CalendarIcon,
  ArrowTrendingUpIcon
} from '@heroicons/vue/24/outline'

// --- Chart constants ---
const W = 600  // SVG viewBox width
const H = 200  // SVG viewBox height
const PAD = { top: 16, right: 16, bottom: 32, left: 40 }

const chartData = ref([])
const recentActivity = ref([])

// Y-axis max value (always at least 10)
const yMax = computed(() => {
    const m = Math.max(...chartData.value.map(d => d.count), 0)
    return Math.max(Math.ceil(m / 10) * 10, 10)
})

// Y grid lines (from top to bottom)
const yGridLines = computed(() => {
    const steps = 4
    const step = yMax.value / steps
    return Array.from({ length: steps + 1 }, (_, i) => {
        const val = yMax.value - i * step
        const y = PAD.top + (i / steps) * (H - PAD.top - PAD.bottom)
        return { val: Math.round(val), y }
    })
})

// Compute (x, y) for each data point
const points = computed(() => {
    if (!chartData.value.length) return []
    const xRange = W - PAD.left - PAD.right
    const yRange = H - PAD.top - PAD.bottom
    return chartData.value.map((d, i) => ({
        x: PAD.left + (i / (chartData.value.length - 1 || 1)) * xRange,
        y: PAD.top + (1 - d.count / yMax.value) * yRange,
        ...d
    }))
})

// Smooth line path (Catmull-Rom -> Bezier)
const linePath = computed(() => {
    const pts = points.value
    if (pts.length < 2) return ''
    let d = `M ${pts[0].x} ${pts[0].y}`
    for (let i = 0; i < pts.length - 1; i++) {
        const p0 = pts[i - 1] ?? pts[i]
        const p1 = pts[i]
        const p2 = pts[i + 1]
        const p3 = pts[i + 2] ?? p2
        const t = 0.3
        const cp1x = p1.x + t * (p2.x - p0.x) / 2
        const cp1y = p1.y + t * (p2.y - p0.y) / 2
        const cp2x = p2.x - t * (p3.x - p1.x) / 2
        const cp2y = p2.y - t * (p3.y - p1.y) / 2
        d += ` C ${cp1x} ${cp1y}, ${cp2x} ${cp2y}, ${p2.x} ${p2.y}`
    }
    return d
})

// Filled area path (same curve but closed to bottom)
const areaPath = computed(() => {
    if (!linePath.value) return ''
    const pts = points.value
    const bottom = H - PAD.bottom
    return `${linePath.value} L ${pts[pts.length - 1].x} ${bottom} L ${pts[0].x} ${bottom} Z`
})

const userEmail = ref('Yves')

const kpiStats = ref([
  { label: 'Candidatures envoyées', value: '0', shortDesc: 'Candidatures récents', timeframe: 'dans les 30 derniers jours', color: 'text-indigo-400', bg: 'bg-indigo-500/10', icon: BriefcaseIcon },
  { label: 'CV Analysés', value: '0', shortDesc: 'Analyses effectuées', timeframe: 'dans les 30 derniers jours', color: 'text-emerald-400', bg: 'bg-emerald-500/10', icon: DocumentCheckIcon },
  { label: 'Entretiens Décrochés', value: '0', shortDesc: 'En cours', timeframe: 'dans les 30 derniers jours', color: 'text-amber-400', bg: 'bg-amber-500/10', icon: ChatBubbleLeftRightIcon },
  { label: 'Réseau (Contacts)', value: '0', shortDesc: 'Nouveaux contacts', timeframe: 'dans les 30 derniers jours', color: 'text-rose-400', bg: 'bg-rose-500/10', icon: UserPlusIcon }
])

const fetchDashboardData = async () => {
    try {
        const userStr = localStorage.getItem('user')
        if (userStr) {
            const user = JSON.parse(userStr)
            userEmail.value = user.email.split('@')[0]
        }
    } catch(e) {}

    try {
        const res = await authFetch('http://localhost:8000/api/dashboard/stats')
        const json = await res.json()
        if (json.data) {
            const kpis = json.data.kpis
            kpiStats.value[0].value = kpis.applied.toString()
            kpiStats.value[1].value = kpis.cv_analyzed.toString()
            kpiStats.value[2].value = kpis.interviews.toString()
            kpiStats.value[3].value = kpis.network.toString()
            
            chartData.value = json.data.chart
        }
    } catch(e) { console.error("Stats fetch error:", e) }
    
    try {
        const res2 = await authFetch('http://localhost:8000/api/crm')
        const json2 = await res2.json()
        if (json2.data) {
            recentActivity.value = json2.data.slice(0, 5).map(app => {
                let statusLabel = 'À Postuler'
                let score = 80
                let color = 'bg-slate-500'
                
                if(app.status === 'APPLIED') { statusLabel = 'Candidature Envoyée'; color = 'bg-indigo-500'; score = 91 }
                else if(app.status === 'INTERVIEW') { statusLabel = 'Entretien Planifié'; color = 'bg-emerald-500'; score = 98 }
                else if(app.status === 'FOLLOW_UP') { statusLabel = 'Relance Requise'; color = 'bg-amber-500'; score = 65 }
                
                return {
                    name: app.job_title,
                    company: app.company_name,
                    status: statusLabel,
                    score: score,
                    color: color,
                    initial: app.company_name ? app.company_name.charAt(0).toUpperCase() : '?'
                }
            })
        }
    } catch(e) { console.error("Recent apps fetch error:", e) }
}

onMounted(() => {
    fetchDashboardData()
})
</script>

<template>
  <div class="p-4 md:p-6 lg:p-8 max-w-[1600px] mx-auto space-y-6">
    
    <!-- Header -->
    <div class="mb-6">
      <h1 class="text-2xl md:text-3xl font-display font-bold text-white tracking-tight flex items-center gap-2">
        Organise tes recherches, Bonjour {{ userEmail }} 🔥
      </h1>
      <p class="text-slate-400 text-sm font-medium mt-1">Gère facilement tes candidatures, suis tes entretiens et atteins tes objectifs au même endroit.</p>
    </div>

    <!-- Cards Row -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <div v-for="stat in kpiStats" :key="stat.label" class="bg-surface-900 border border-surface-800 rounded-xl p-5 shadow-sm hover:border-surface-700 transition-colors group">
         <div class="flex items-center justify-between mb-4">
             <div class="flex items-center gap-3">
                 <div :class="['w-8 h-8 rounded flex items-center justify-center', stat.bg]">
                    <component :is="stat.icon" :class="['w-4 h-4', stat.color]" />
                 </div>
                 <span class="text-xs font-bold text-slate-200">{{ stat.label }}</span>
             </div>
             <button class="text-slate-500 hover:text-white">
                 <EllipsisVerticalIcon class="w-5 h-5" />
             </button>
         </div>
         
         <div class="mb-3">
             <div class="flex items-baseline gap-2">
                 <span class="text-3xl font-bold text-white leading-none">{{ stat.value }}</span>
                 <span class="text-xs font-bold" :class="stat.color">{{ stat.shortDesc }}</span>
             </div>
         </div>
         
         <div>
             <p class="text-[10px] font-medium text-slate-500 uppercase tracking-wide">{{ stat.timeframe }}</p>
         </div>
      </div>
    </div>

    <!-- Charts Row -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Area Chart -->
      <div class="lg:col-span-2 bg-surface-900 border border-surface-800 rounded-xl p-5 shadow-sm">
          <div class="flex items-center justify-between mb-6">
                <h3 class="text-sm font-bold text-white">Croissance des Opportunités</h3>
                <button class="flex items-center gap-2 border border-surface-700 bg-surface-800 hover:bg-surface-700 text-xs font-semibold text-slate-300 rounded-lg py-1.5 px-3 transition-colors">
                    <CalendarIcon class="w-4 h-4 text-slate-400" />
                    Filtrer
                </button>
          </div>
          
          <div class="flex items-center gap-4 mb-6">
              <div class="flex items-center gap-1.5"><div class="w-2.5 h-2.5 rounded shadow-sm bg-indigo-500"></div><span class="text-[11px] font-bold text-slate-400">Total Opportunités</span></div>
          </div>

          <!-- Premium SVG Line Chart -->
          <div class="mt-2 w-full" style="height:220px;">
            <svg
              :viewBox="`0 0 ${W} ${H}`"
              preserveAspectRatio="xMidYMid meet"
              class="w-full h-full"
              style="overflow:visible"
            >
              <defs>
                <linearGradient id="areaGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stop-color="#6366f1" stop-opacity="0.35"/>
                  <stop offset="100%" stop-color="#6366f1" stop-opacity="0"/>
                </linearGradient>
                <filter id="lineGlow">
                  <feGaussianBlur stdDeviation="3" result="blur"/>
                  <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
                </filter>
              </defs>

              <!-- Y grid lines -->
              <g v-for="g in yGridLines" :key="g.val">
                <line :x1="PAD.left" :y1="g.y" :x2="W - PAD.right" :y2="g.y" stroke="#1e293b" stroke-width="1" stroke-dasharray="4,4"/>
                <text :x="PAD.left - 8" :y="g.y + 4" text-anchor="end" font-size="11" fill="#475569" font-family="sans-serif">{{ g.val }}</text>
              </g>

              <!-- X axis ticks / labels -->
              <g v-for="(pt, i) in points" :key="'x'+i">
                <line :x1="pt.x" :y1="H - PAD.bottom" :x2="pt.x" :y2="H - PAD.bottom + 4" stroke="#334155" stroke-width="1"/>
                <text :x="pt.x" :y="H - PAD.bottom + 16" text-anchor="middle" font-size="10" fill="#64748b" font-family="sans-serif" font-weight="bold">{{ pt.label }}</text>
              </g>

              <!-- Area fill -->
              <path :d="areaPath" fill="url(#areaGrad)"/>

              <!-- Smooth line (with glow) -->
              <path :d="linePath" fill="none" stroke="#6366f1" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" filter="url(#lineGlow)"/>
              <!-- Clean line on top -->
              <path :d="linePath" fill="none" stroke="#818cf8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>

              <!-- Data points -->
              <g v-for="(pt, i) in points" :key="'pt'+i">
                <circle :cx="pt.x" :cy="pt.y" r="5" fill="#1e293b" stroke="#6366f1" stroke-width="2.5"/>
                <circle :cx="pt.x" :cy="pt.y" r="2.5" fill="#818cf8"/>
                <title>{{ pt.label }}: {{ pt.count }} offres</title>
              </g>

              <!-- Empty state -->
              <text v-if="!chartData.length" :x="W/2" :y="H/2" text-anchor="middle" fill="#475569" font-size="14" font-family="sans-serif">Aucune donnée disponible</text>
            </svg>
          </div>
      </div>
      
      <!-- Bar Chart (Mocked Status) -->
      <div class="lg:col-span-1 bg-surface-900 border border-surface-800 rounded-xl p-5 shadow-sm flex flex-col">
          <div class="flex items-center justify-between mb-6">
                <h3 class="text-sm font-bold text-white">Opportunités par Statut</h3>
                <button class="flex items-center gap-2 border border-surface-700 bg-surface-800 hover:bg-surface-700 text-xs font-semibold text-slate-300 rounded-lg py-1.5 px-3 transition-colors">
                    <CalendarIcon class="w-4 h-4 text-slate-400" />
                    Filtrer
                </button>
          </div>
          
          <div class="flex items-center flex-wrap gap-3 mb-8">
              <div class="flex items-center gap-1.5"><div class="w-2.5 h-2.5 rounded-sm bg-rose-500"></div><span class="text-[10px] font-bold text-slate-400">Backlog</span></div>
              <div class="flex items-center gap-1.5"><div class="w-2.5 h-2.5 rounded-sm bg-indigo-500"></div><span class="text-[10px] font-bold text-slate-400">À Faire</span></div>
              <div class="flex items-center gap-1.5"><div class="w-2.5 h-2.5 rounded-sm bg-amber-500"></div><span class="text-[10px] font-bold text-slate-400">En cours</span></div>
          </div>
          
          <div class="flex-1 flex items-end justify-around gap-2 px-2 pb-4 border-b border-surface-800 relative z-10 w-full">
              <div class="absolute inset-x-0 bottom-4 top-0 flex flex-col justify-between pointer-events-none z-0">
                  <div class="border-b border-surface-800/60 w-full h-0"><span class="absolute -top-3 -left-2 text-[9px] font-medium text-slate-600">60</span></div>
                  <div class="border-b border-surface-800/60 w-full h-0"><span class="absolute -top-3 -left-2 text-[9px] font-medium text-slate-600">40</span></div>
                  <div class="border-b border-surface-800/60 w-full h-0"><span class="absolute -top-3 -left-2 text-[9px] font-medium text-slate-600">20</span></div>
                  <div class="border-b border-surface-800/60 w-full h-0"><span class="absolute -top-3 -left-2 text-[9px] font-medium text-slate-600">0</span></div>
              </div>
              
              <div class="w-6 sm:w-8 bg-rose-500 rounded-t relative z-10 h-[30%]"></div>
              <div class="w-6 sm:w-8 bg-indigo-500 rounded-t relative z-10 h-[60%]"></div>
              <div class="w-6 sm:w-8 bg-amber-500 rounded-t relative z-10 h-[80%]"></div>
              <div class="w-6 sm:w-8 bg-emerald-500 rounded-t relative z-10 h-[40%]"></div>
          </div>
          <div class="flex justify-around pt-3">
              <span class="text-[9px] font-bold text-slate-500">Backlog</span>
              <span class="text-[9px] font-bold text-slate-500">À Faire</span>
              <span class="text-[9px] font-bold text-slate-500">En cours</span>
              <span class="text-[9px] font-bold text-slate-500">Fait</span>
          </div>
      </div>
    </div>
    
    <!-- Timeline Section -->
    <div class="bg-surface-900 border border-surface-800 rounded-xl p-5 shadow-sm mt-6">
        <div class="flex items-center justify-between mb-6">
            <h3 class="text-sm font-bold text-white">Task Completion Over Time & Activité Récente</h3>
        </div>
        
        <!-- Headers -->
        <div class="grid grid-cols-4 gap-4 px-4 border-b border-surface-800 pb-3 mb-4 text-[10px] font-bold text-slate-500 uppercase tracking-widest">
            <div class="col-span-2">Rôle & Opportunité</div>
            <div>Statut</div>
            <div class="text-right">Progression</div>
        </div>
        
        <div class="space-y-2">
            <div v-if="!recentActivity || recentActivity.length === 0" class="text-center py-6 text-slate-500 text-sm">
                Aucune activité récente.
            </div>
            
            <div 
                v-for="(item, idx) in recentActivity" 
                :key="idx"
                class="grid grid-cols-4 gap-4 px-4 py-3 rounded-lg hover:bg-surface-800 items-center transition-colors group cursor-pointer"
            >
                <div class="col-span-2 flex items-center gap-3">
                    <div :class="['w-8 h-8 rounded shrink-0 flex items-center justify-center font-bold text-white text-xs', item.color]">
                        {{ item.initial }}
                    </div>
                    <div>
                        <p class="text-sm font-bold text-white">{{ item.name }}</p>
                        <p class="text-[11px] font-medium text-slate-400 mt-0.5">{{ item.company }}</p>
                    </div>
                </div>
                <div>
                   <span class="px-2 py-1 flex items-center max-w-max gap-1.5 text-[10px] font-bold bg-surface-800 text-slate-300 rounded border border-surface-700 whitespace-nowrap">
                       <span class="w-1.5 h-1.5 rounded-full" :class="item.score > 80 ? 'bg-emerald-500' : 'bg-amber-500'"></span>
                       {{ item.status }}
                   </span>
                </div>
                <div class="text-right flex items-center justify-end">
                    <div class="w-16 h-1.5 bg-surface-800 rounded-full overflow-hidden mr-3">
                        <div class="h-full rounded-full" :class="item.score > 80 ? 'bg-emerald-500' : 'bg-amber-500'" :style="`width: ${item.score}%`"></div>
                    </div>
                    <span class="text-xs font-bold text-slate-300 w-8">{{ item.score }}%</span>
                </div>
            </div>
        </div>
    </div>

  </div>
</template>

<style scoped>
.animate-fade-in-up {
  animation: fadeInUp 0.5s ease-out forwards;
}
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
