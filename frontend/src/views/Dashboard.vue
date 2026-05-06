<script setup>
import { authFetch } from '../utils/auth'
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import {
  ArrowTrendingUpIcon, ArrowTrendingDownIcon, EllipsisHorizontalIcon,
  RocketLaunchIcon, EnvelopeIcon, UsersIcon, LightBulbIcon,
  MagnifyingGlassIcon, MegaphoneIcon, HandThumbUpIcon, PhoneIcon,
  ArrowPathIcon, DocumentTextIcon, InformationCircleIcon, XMarkIcon
} from '@heroicons/vue/24/outline'

// Dimensions pour le graphique principal
const W = 800, H = 250
const PAD = { top: 30, bottom: 40, left: 60, right: 40 }

const chartData = ref([])
const chartData2 = ref([])

// Dropdowns State
const monthDropdownOpen = ref(false)
const yearDropdownOpen = ref(false)
const selectedMonth = ref('Month')
const selectedYear = ref('Year')

// Data for Bar Chart (computed from real data)
const barData = computed(() => {
    if (!chartData.value || chartData.value.length === 0) return Array.from({length: 12}, () => Math.floor(Math.random()*30 + 15))
    let res = []
    for(let i=0; i<12; i++) {
        res.push(chartData.value[i] ? chartData.value[i].count : 0)
    }
    return res
})
const barData2 = computed(() => {
    if (!chartData2.value || chartData2.value.length === 0) return Array.from({length: 12}, () => Math.floor(Math.random()*25 + 5))
    let res = []
    for(let i=0; i<12; i++) {
        res.push(chartData2.value[i] ? chartData2.value[i].count : 0)
    }
    return res
})
const barYMax = computed(() => {
    const max = Math.max(...barData.value, ...barData2.value)
    return Math.max(Math.ceil(max / 10) * 10, 40)
})

const recentActivity = ref([])
const userEmail = ref('')
const { t, locale } = useI18n()

// Jours et dates pour le header
const todayStr = computed(() => {
  const d = new Date()
  const loc = (locale.value && locale.value.includes('fr')) ? 'fr-FR' : 'en-US'
  const dayName = d.toLocaleDateString(loc, { weekday: 'short' })
  const monthName = d.toLocaleDateString(loc, { month: 'long' })
  return `${dayName}, ${monthName}`
})
const dateNum = computed(() => new Date().getDate())

const kpiValues = ref({ applied: '0', cv_analyzed: '0', interviews: '0', network: '0' })

const playbooks = ref([
  { id: 1, name: 'Sniper-to-Apply', desc: 'Candidature Express 1-Clic', fullDesc: "Ce workflow analyse l'offre d'emploi, adapte votre CV spécifiquement pour celle-ci, et remplit automatiquement le formulaire ATS de l'entreprise via l'agent MultiOn.", icon: RocketLaunchIcon, active: true },
  { id: 2, name: 'Ghostbuster', desc: 'Relance Anti-Fantôme', fullDesc: "Détecte automatiquement les candidatures sans réponse depuis plus de 7 jours et génère un email de relance poli et percutant pour le recruteur.", icon: EnvelopeIcon, active: true },
  { id: 3, name: 'Network Ninja', desc: 'Chasseur de Décideurs', fullDesc: "Cherche et identifie les décideurs clés (RH, CEO, Lead Dev) de l'entreprise sur LinkedIn et prépare un message d'accroche personnalisé.", icon: UsersIcon, active: false },
  { id: 4, name: 'Pre-Interview', desc: 'Entraînement Immersif', fullDesc: "Récupère les détails du poste et de l'entreprise pour préparer un simulateur d'entretien avec des questions probables et des conseils de posture.", icon: LightBulbIcon, active: true },
  { id: 5, name: 'Daily Hunt', desc: 'Chasse Matinale (Cron)', fullDesc: "S'exécute tous les matins à 7h00. Scanne le web pour trouver 5 nouvelles offres d'emploi correspondant exactement à votre profil et les ajoute au CRM.", icon: MagnifyingGlassIcon, active: true },
  { id: 6, name: 'Elevator Pitch', desc: 'Présentation Instantanée', fullDesc: "Génère un pitch de présentation de 30 secondes (texte + audio) adapté à l'entreprise que vous ciblez.", icon: MegaphoneIcon, active: false },
  { id: 7, name: 'Post-Interview', desc: 'Debrief & Remerciement', fullDesc: "S'active après un entretien. Génère un email de remerciement stratégique et met à jour le statut de la candidature dans le CRM.", icon: HandThumbUpIcon, active: false },
  { id: 8, name: 'Cold Call', desc: 'Script Téléphonique', fullDesc: "Prépare un script d'appel téléphonique sur mesure pour contacter directement un recruteur ou un manager, avec gestion des objections.", icon: PhoneIcon, active: false },
  { id: 9, name: 'Rejection Pivot', desc: 'Rebond & Alternatives', fullDesc: "Suite à un refus, envoie un email demandant du feedback constructif, et trouve instantanément 3 offres similaires pour rebondir.", icon: ArrowPathIcon, active: true },
  { id: 10, name: 'Smart Cover', desc: 'Lettre d\'Actualité', fullDesc: "Rédige une lettre de motivation dynamique en intégrant la dernière actualité pertinente de l'entreprise ciblée.", icon: DocumentTextIcon, active: false }
])

const togglePlaybook = (pb) => {
    pb.active = !pb.active
}

const selectedPlaybookInfo = ref(null)
const showInfo = (pb) => {
    selectedPlaybookInfo.value = pb
}
const closeInfo = () => {
    selectedPlaybookInfo.value = null
}

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
  { id: 'applied', label: t('dashboard.smart_score'), value: kpiValues.value.cv_analyzed || '0', suffix: ' / 100', trend: '+18', trendUp: true, chartType: 'gauge' },
  { id: 'cv', label: t('dashboard.applications'), value: kpiValues.value.applied || '0', trend: '+20%', trendUp: true, chartType: 'line', sparkline: sparklines.value.cv },
  { id: 'interviews', label: t('dashboard.interviews'), value: kpiValues.value.interviews || '0', trend: '+12%', trendUp: true, chartType: 'line', sparkline: sparklines.value.interviews },
  { id: 'network', label: t('dashboard.network'), value: kpiValues.value.network || '0', trend: '+34%', trendUp: true, chartType: 'line', sparkline: sparklines.value.network },
])

// État pour le tooltip du graphique
const activePoint = ref(null)
const activePoint2 = ref(null)

// Total des opportunités
const totalOpportunities = computed(() => {
    const total = parseInt(kpiValues.value.applied || 0) + parseInt(kpiValues.value.cv_analyzed || 0);
    return new Intl.NumberFormat('fr-FR').format(total > 0 ? total : 248);
})

const formatYLabel = (val) => {
    if (val >= 1000000) return (val/1000000).toFixed(1).replace('.0','') + 'm'
    if (val >= 1000) return (val/1000).toFixed(1).replace('.0','') + 'k'
    return val
}

const yMax = computed(() => {
    const max1 = Math.max(...chartData.value.map(d => d.count), 0)
    const max2 = Math.max(...chartData2.value.map(d => d.count), 0)
    return Math.max(Math.ceil(Math.max(max1, max2) / 10) * 10, 120)
})

const pts = computed(() => {
  return chartData.value.map((d, i) => {
    const x = PAD.left + (i / (chartData.value.length - 1 || 1)) * (W - PAD.left - PAD.right)
    const y = H - PAD.bottom - (d.count / yMax.value) * (H - PAD.top - PAD.bottom)
    return { x, y, count: d.count, label: d.label }
  })
})

const pts2 = computed(() => {
  return chartData2.value.map((d, i) => {
    const x = PAD.left + (i / (chartData2.value.length - 1 || 1)) * (W - PAD.left - PAD.right)
    const y = H - PAD.bottom - (d.count / yMax.value) * (H - PAD.top - PAD.bottom)
    return { x, y, count: d.count, label: d.label }
  })
})

const linePath = computed(() => {
  if (pts.value.length === 0) return ''
  return 'M ' + pts.value.map(p => `${p.x},${p.y}`).join(' L ')
})

const areaPath = computed(() => {
  if (pts.value.length === 0) return ''
  const p = pts.value
  return 'M ' + p.map(p => `${p.x},${p.y}`).join(' L ') + ` L ${p[p.length-1].x},${H - PAD.bottom} L ${p[0].x},${H - PAD.bottom} Z`
})

const linePath2 = computed(() => {
  if (pts2.value.length === 0) return ''
  return 'M ' + pts2.value.map(p => `${p.x},${p.y}`).join(' L ')
})

const fetchDashboardData = async () => {
  try { const u = localStorage.getItem('user'); if (u) userEmail.value = JSON.parse(u).full_name || JSON.parse(u).email.split('@')[0] } catch(e){}
  try {
    const r = await authFetch('/api/dashboard/stats'), j = await r.json()
    if (j.data) {
      const k = j.data.kpis
      kpiValues.value = { applied: k.applied.toString(), cv_analyzed: k.cv_analyzed.toString(), interviews: k.interviews.toString(), network: k.network.toString() }
      if(j.data.chart && j.data.chart.length > 0) {
          chartData.value = j.data.chart
      } else {
          chartData.value = Array.from({length: 31}, (_, i) => ({ label: `Day ${i+1}`, count: Math.floor(Math.random()*60 + 40) }))
      }
      chartData2.value = chartData.value.map(d => ({ label: d.label, count: Math.max(10, d.count - Math.floor(Math.random()*30 + 10)) }))
    }
  } catch(e){}
  try {
    const r2 = await authFetch('/api/crm'), j2 = await r2.json()
    if (j2.data) {
      recentActivity.value = j2.data.slice(0,5).map(app => {
        let score = 20;
        if(app.status==='APPLIED') score = 40;
        else if(app.status==='FOLLOW_UP') score = 60;
        else if(app.status==='INTERVIEW') score = 85;
        else if(app.status==='OFFER') score = 100;
        
        return { name: app.job_title, company: app.company_name, score, initial: (app.company_name||app.job_title||'?').charAt(0).toUpperCase(), status: app.status }
      })
    }
  } catch(e){}
}
onMounted(fetchDashboardData)
</script>

<template>
  <div class="db-root">

    <!-- HEADER INSPIRATION 2 -->
    <div class="db-header animate-slide-up" style="animation-delay: 0s;">
      <div class="header-date-box">
          <div class="date-num">{{ dateNum }}</div>
          <div class="date-str">{{ todayStr }}</div>
          <div class="date-divider"></div>
          <button @click="$router.push('/crm')" class="btn-orange">{{ t('dashboard.show_tasks') }} &rarr;</button>
      </div>
      
      <div class="header-greeting">
          <div class="greeting-text">
            <div class="flex items-center gap-3">
                {{ t('dashboard.need_help') }}
                <img src="/logo.png" alt="Logo" class="w-10 h-10 animate-float" />
            </div>
            <span class="greeting-sub">{{ t('dashboard.ask_anything') }}</span>
          </div>
          <button class="btn-icon-white rounded-full"><span class="w-5 h-5 block text-center leading-5">&plus;</span></button>
      </div>
    </div>

    <div class="mb-4 flex items-center justify-between">
      <h2 class="text-lg font-semibold text-slate-800">Playbooks Actifs</h2>
      <span class="text-xs text-slate-500 bg-slate-100 px-2 py-1 rounded-full font-medium border border-slate-200">10 Workflows Disponibles</span>
    </div>

    <div class="grid grid-cols-2 md:grid-cols-5 gap-3 mb-8">
      <button v-for="(pb, index) in playbooks" :key="pb.id" 
          @click="togglePlaybook(pb)"
          class="relative flex flex-col items-start p-3 rounded-xl border text-left transition-all duration-300 group overflow-hidden bg-white animate-slide-up hover:-translate-y-1 active:scale-95 cursor-pointer"
          :class="pb.active ? 'border-indigo-500 shadow-md shadow-indigo-200/50 ring-1 ring-indigo-500/20' : 'border-slate-200 hover:border-indigo-300 hover:shadow-md hover:shadow-indigo-100 opacity-80 hover:opacity-100'"
          :style="`animation-delay: ${0.05 * index}s;`">
        
        <!-- Active indicator -->
        <div class="absolute top-0 right-0 w-8 h-8 flex items-center justify-center">
            <div v-if="pb.active" class="w-2 h-2 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]"></div>
            <div v-else class="w-1.5 h-1.5 rounded-full bg-slate-300 transition-colors duration-300 group-hover:bg-indigo-300"></div>
        </div>

        <div class="mb-2 p-1.5 rounded-lg transition-transform duration-300 group-hover:scale-110" :class="pb.active ? 'bg-indigo-50 text-indigo-600' : 'bg-slate-50 text-slate-500'">
           <component :is="pb.icon" class="w-5 h-5" />
        </div>
        
        <div class="font-semibold text-sm mb-0.5 flex items-center gap-1" :class="pb.active ? 'text-slate-800' : 'text-slate-600'">
            {{ pb.name }}
            <button @click.stop="showInfo(pb)" class="text-slate-400 hover:text-indigo-500 transition-colors bg-white/80 rounded-full hover:bg-indigo-50" title="Plus d'infos">
                <InformationCircleIcon class="w-3.5 h-3.5" />
            </button>
        </div>
        <div class="text-[10px] leading-tight text-slate-500 font-medium">{{ pb.desc }}</div>
        
        <!-- Background subtle glow if active -->
        <div v-if="pb.active" class="absolute -bottom-6 -right-6 w-16 h-16 bg-indigo-50 rounded-full blur-xl -z-10"></div>
      </button>
    </div>

    <!-- ANCIENNES CARTES KPI A LA PLACE DES GRAPHIQUES -->
    <div class="db-kpi-grid mt-2 mb-8">
      <div v-for="(s, index) in kpiStats" :key="s.id" class="kpi-card animate-slide-up" :style="`animation-delay: ${0.2 + index * 0.1}s;`">
        <div class="kpi-content">
            <div class="kpi-info">
                <div class="kpi-label">{{ s.label }}</div>
                <div class="kpi-val-row">
                    <span class="kpi-val">{{ s.value }}</span>
                    <span v-if="s.suffix" class="kpi-suffix">{{ s.suffix }}</span>
                </div>
            </div>
            <div class="kpi-chart" :class="s.chartType === 'gauge' ? 'w-[100px] h-[50px]' : 'w-[80px] h-[40px]'">
                 <svg v-if="s.chartType === 'gauge'" viewBox="0 0 100 50" class="w-full h-full overflow-visible">
                    <path d="M 10 50 A 40 40 0 0 1 90 50" fill="none" stroke="#E5E7EB" stroke-width="5" stroke-linecap="butt"/>
                    <path d="M 10 50 A 40 40 0 0 1 90 50" fill="none" stroke="#10B981" stroke-width="5" stroke-linecap="butt"
                          :stroke-dasharray="`${(Math.min(parseInt(s.value), 100) / 100) * 125.66} 125.66`"
                          style="transition: stroke-dasharray 1s cubic-bezier(0.175, 0.885, 0.32, 1.275);"/>
                    <path d="M 22 50 A 28 28 0 0 1 78 50" fill="none" stroke="#D1D5DB" stroke-width="2" stroke-dasharray="0.5, 2.5"/>
                    <g :style="`transform: rotate(${((Math.min(parseInt(s.value), 100) / 100) * 180) - 90}deg); transform-origin: 50px 50px; transition: transform 1.2s cubic-bezier(0.175, 0.885, 0.32, 1.275);`">
                        <circle cx="50" cy="50" r="3" fill="#111827" />
                        <line x1="50" y1="48" x2="50" y2="28" stroke="#111827" stroke-width="1.5" stroke-linecap="round"/>
                    </g>
                 </svg>
                 <svg v-else viewBox="0 -5 100 50" preserveAspectRatio="none" class="w-full h-full overflow-visible">
                    <path :d="getSparklinePath(s.sparkline)" fill="none" stroke="#111827" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
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

    <!-- Efficiency row below -->
    <div class="mt-6 animate-slide-up" style="animation-delay: 0.5s;">
      <div class="efficiency-card">
        <div class="chart-header" style="margin-bottom: 1.5rem;">
          <div class="chart-title">Recent Activity</div>
          <div class="eff-filters">
              <div class="segment-control">
                  <span class="segment-btn">Score</span>
                  <span class="segment-btn active">%</span>
              </div>
          </div>
        </div>
        
        <div class="eff-list">
            <div v-if="!recentActivity || recentActivity.length === 0" class="text-center py-8 text-sm text-gray-400 font-medium bg-gray-50 rounded-xl border border-dashed border-gray-200">
                Aucune activité récente.
            </div>
            <div v-for="(item, i) in recentActivity" :key="i" class="eff-row group animate-slide-up" :style="`animation-delay: ${0.6 + i * 0.05}s;`">
                <div class="eff-user">
                    <div class="eff-avatar-wrapper">
                        <div class="eff-avatar">
                            <img src="/logo.png" alt="GoldArmy" class="w-full h-full object-cover rounded-full" />
                        </div>
                    </div>
                    <div class="eff-user-info">
                        <span class="eff-name">{{ item.name }}</span>
                        <div class="flex items-center gap-1.5 mt-0.5">
                            <span class="eff-company">{{ item.company }}</span>
                            <span class="w-1 h-1 rounded-full bg-gray-300"></span>
                            <span class="eff-status">{{ item.status }}</span>
                        </div>
                    </div>
                </div>
                <div class="eff-score-wrap">
                    <span class="eff-score-txt group-hover:text-[#E85D3E] transition-colors">{{ item.score }}%</span>
                    <div class="eff-track">
                        <!-- Gradient fill for progress -->
                        <div class="eff-fill group-hover:bg-[#E85D3E] transition-colors" :style="`width: ${item.score}%`"></div>
                    </div>
                </div>
            </div>
        </div>
      </div>
    </div>
      
    <!-- Info Modal -->
    <Transition name="fade">
      <div v-if="selectedPlaybookInfo" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm" @click="closeInfo">
        <div class="bg-white rounded-2xl shadow-xl w-full max-w-md overflow-hidden animate-slide-up" style="animation-delay: 0s;" @click.stop>
          <div class="p-6">
            <div class="flex items-start justify-between mb-4">
              <div class="flex items-center gap-3">
                <div class="p-2.5 rounded-xl bg-indigo-50 text-indigo-600">
                  <component :is="selectedPlaybookInfo.icon" class="w-6 h-6" />
                </div>
                <div>
                  <h3 class="text-lg font-bold text-slate-800 leading-tight">{{ selectedPlaybookInfo.name }}</h3>
                  <p class="text-xs font-medium text-slate-500 mt-0.5">{{ selectedPlaybookInfo.desc }}</p>
                </div>
              </div>
              <button @click="closeInfo" class="p-1.5 text-slate-400 hover:text-slate-700 hover:bg-slate-100 rounded-full transition-colors">
                <XMarkIcon class="w-5 h-5" />
              </button>
            </div>
            
            <div class="bg-slate-50/80 p-4 rounded-xl border border-slate-100 mb-6 relative overflow-hidden">
              <div class="absolute top-0 right-0 w-24 h-24 bg-indigo-100 rounded-full blur-2xl opacity-50 -mr-10 -mt-10"></div>
              <h4 class="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-2 relative z-10 flex items-center gap-1.5">
                  <InformationCircleIcon class="w-3.5 h-3.5" />
                  Comment ça marche ?
              </h4>
              <p class="text-sm text-slate-700 leading-relaxed relative z-10">
                {{ selectedPlaybookInfo.fullDesc }}
              </p>
            </div>
            
            <div class="flex justify-end gap-3">
              <button @click="closeInfo" class="px-4 py-2 text-sm font-medium text-slate-600 bg-white border border-slate-200 hover:bg-slate-50 hover:text-slate-800 rounded-lg transition-colors">
                Fermer
              </button>
              <button @click="togglePlaybook(selectedPlaybookInfo); closeInfo()" class="px-4 py-2 text-sm font-medium text-white rounded-lg transition-colors shadow-sm" :class="selectedPlaybookInfo.active ? 'bg-rose-500 hover:bg-rose-600 shadow-rose-200' : 'bg-indigo-600 hover:bg-indigo-700 shadow-indigo-200'">
                {{ selectedPlaybookInfo.active ? 'Désactiver' : 'Activer' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </Transition>

  </div>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
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

/* ── ANIMATIONS GLOBALES ── */
@keyframes floatLogo {
    0%, 100% { transform: translateY(0) scale(1); }
    50% { transform: translateY(-5px) scale(1.05) rotate(3deg); }
}
.animate-float {
    animation: floatLogo 3s ease-in-out infinite;
}

.animate-slide-up {
    opacity: 0;
    animation: slideUpFade 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

@keyframes slideUpFade {
    0% {
        opacity: 0;
        transform: translateY(30px);
    }
    100% {
        opacity: 1;
        transform: translateY(0);
    }
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
    border-radius: 16px;
    padding: 1.25rem;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02), 0 2px 4px -1px rgba(0,0,0,0.02);
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    /* Note: on retire transform-origin pour ne pas conflit avec animate-slide-up */
}

.kpi-card:hover {
    transform: translateY(-8px) scale(1.02);
    box-shadow: 0 20px 25px -5px rgba(0,0,0,0.08), 0 10px 10px -5px rgba(0,0,0,0.04);
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
    grid-template-columns: 1fr;
    gap: 1.5rem;
    margin-top: 1.5rem;
}

@media (min-width: 1024px) {
    .db-charts-row {
        grid-template-columns: repeat(2, 1fr);
    }
}

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

.chart-area-anim {
    opacity: 0;
    animation: fadeArea 1s ease-out 0.5s forwards;
}

@keyframes drawLine {
    to {
        stroke-dashoffset: 0;
    }
}

@keyframes fadeArea {
    to {
        opacity: 1;
    }
}

.bar-anim {
    transform: scaleY(0);
    transform-origin: bottom;
    animation: growBar 1s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
}
.bar-anim-dark {
    transform: scaleY(0);
    transform-origin: bottom;
    animation: growBar 1s cubic-bezier(0.175, 0.885, 0.32, 1.275) 0.2s forwards;
}
@keyframes growBar {
    to { transform: scaleY(1); }
}

/* ── EFFICIENCY LIST ── */
.eff-filters {
    display: flex;
    align-items: center;
}

.segment-control {
    display: flex;
    background: #F3F4F6;
    padding: 3px;
    border-radius: 8px;
    gap: 2px;
}

.segment-btn {
    font-size: 0.72rem;
    font-weight: 700;
    color: #6B7280;
    padding: 0.35rem 0.8rem;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.2s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.segment-btn:hover:not(.active) {
    color: #374151;
}

.segment-btn.active {
    background: #FFFFFF;
    color: #111827;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.03);
}

.eff-list {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.eff-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.85rem 1rem;
    border-radius: 16px;
    background: #FFFFFF;
    border: 1px solid transparent;
    transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    cursor: default;
    position: relative;
    overflow: hidden;
}
.eff-row:hover {
    background: #FFFFFF;
    border-color: #E5E7EB;
    box-shadow: 0 10px 15px -3px rgba(0,0,0,0.04), 0 4px 6px -2px rgba(0,0,0,0.02);
    transform: translateY(-2px);
}

.eff-user {
    display: flex;
    align-items: center;
    gap: 1rem;
    width: 60%;
}

.eff-avatar-wrapper {
    position: relative;
    padding: 2px;
    border-radius: 12px;
    background: #FFFFFF;
    transition: transform 0.3s;
}
.eff-row:hover .eff-avatar-wrapper {
    transform: scale(1.08) rotate(2deg);
}

.eff-avatar {
    width: 42px;
    height: 42px;
    border-radius: 50%;
    background: #F3F4F6;
    color: #111827;
    border: 1px solid #E5E7EB;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.1rem;
    font-weight: 700;
}

.eff-user-info {
    display: flex;
    flex-direction: column;
}

.eff-name {
    font-size: 0.9rem;
    font-weight: 700;
    color: #111827;
    line-height: 1.2;
}

.eff-company {
    font-size: 0.75rem;
    font-weight: 500;
    color: #6B7280;
}

.eff-status {
    font-size: 0.65rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: #9CA3AF;
}

.eff-score-wrap {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    width: 35%;
    gap: 0.5rem;
}

.eff-score-txt {
    font-size: 1rem;
    font-weight: 800;
    color: #111827;
}

.eff-track {
    width: 100%;
    height: 6px;
    background: #F3F4F6;
    position: relative;
    border-radius: 99px;
    overflow: hidden;
    box-shadow: inset 0 1px 2px rgba(0,0,0,0.02);
}

.eff-fill {
    height: 100%;
    background: #111827;
    border-radius: 99px;
    transition: width 1.2s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

</style>
