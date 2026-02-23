<script setup>
import { authFetch } from '../utils/auth'

import { ref, onMounted } from 'vue'
import { 
  BriefcaseIcon,
  DocumentCheckIcon,
  ChatBubbleLeftRightIcon,
  UserPlusIcon,
  EllipsisVerticalIcon,
  CalendarIcon
} from '@heroicons/vue/24/outline'

const userEmail = ref('Yves')

const kpiStats = ref([
  { label: 'Candidatures envoyées', value: '0', shortDesc: 'Candidatures récents', timeframe: 'dans les 30 derniers jours', color: 'text-indigo-400', bg: 'bg-indigo-500/10', icon: BriefcaseIcon },
  { label: 'CV Analysés', value: '0', shortDesc: 'Analyses effectuées', timeframe: 'dans les 30 derniers jours', color: 'text-emerald-400', bg: 'bg-emerald-500/10', icon: DocumentCheckIcon },
  { label: 'Entretiens Décrochés', value: '0', shortDesc: 'En cours', timeframe: 'dans les 30 derniers jours', color: 'text-amber-400', bg: 'bg-amber-500/10', icon: ChatBubbleLeftRightIcon },
  { label: 'Réseau (Contacts)', value: '0', shortDesc: 'Nouveaux contacts', timeframe: 'dans les 30 derniers jours', color: 'text-rose-400', bg: 'bg-rose-500/10', icon: UserPlusIcon }
])

const chartData = ref([])
const recentActivity = ref([])

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
        const res2 = await authFetch('http://localhost:8000/api/crm/applications')
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

          <!-- SVG Area Chart -->
          <div class="h-64 w-full relative z-10">
                <div class="absolute inset-0 flex flex-col justify-between pointer-events-none z-0 pb-6">
                    <div class="border-b border-surface-800/60 w-full h-0 relative"><span class="absolute -top-3 left-0 text-[10px] font-bold text-slate-600">60</span></div>
                    <div class="border-b border-surface-800/60 w-full h-0 relative"><span class="absolute -top-3 left-0 text-[10px] font-bold text-slate-600">40</span></div>
                    <div class="border-b border-surface-800/60 w-full h-0 relative"><span class="absolute -top-3 left-0 text-[10px] font-bold text-slate-600">20</span></div>
                    <div class="border-b border-surface-800/60 w-full h-0 relative"><span class="absolute -top-3 left-0 text-[10px] font-bold text-slate-600">0</span></div>
                </div>

                <svg v-if="chartData && chartData.length > 0" class="w-full h-full overflow-visible pl-6 pb-6" preserveAspectRatio="none" viewBox="0 0 100 100">
                    <defs>
                        <linearGradient id="chartGradient" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="0%" stop-color="#818cf8" stop-opacity="0.3" />
                            <stop offset="100%" stop-color="#818cf8" stop-opacity="0.0" />
                        </linearGradient>
                    </defs>
                    
                    <polygon 
                        :points="`0,100 ${chartData.map((d, i) => `${(i / (chartData.length - 1)) * 100},${100 - d.heightPct}`).join(' ')} 100,100`" 
                        fill="url(#chartGradient)"
                    />
                    
                    <polyline 
                        :points="chartData.map((d, i) => `${(i / (chartData.length - 1)) * 100},${100 - d.heightPct}`).join(' ')" 
                        fill="none" 
                        stroke="#818cf8" 
                        stroke-width="2.5" 
                        stroke-linecap="round"
                        stroke-linejoin="round"
                    />

                    <circle 
                        v-for="(d, i) in chartData" 
                        :key="i"
                        :cx="(i / (chartData.length - 1)) * 100" 
                        :cy="100 - d.heightPct" 
                        r="3" 
                        fill="#1e1e2d" 
                        stroke="#818cf8" 
                        stroke-width="2"
                    >
                        <title>{{ d.count }} offres</title>
                    </circle>
                </svg>

                <div v-if="chartData && chartData.length > 0" class="absolute bottom-0 inset-x-0 pl-6 flex justify-between">
                    <span v-for="(d, i) in chartData" :key="i" class="text-[9px] font-bold text-slate-500 uppercase tracking-widest">{{ d.label }}</span>
                </div>
                
                <div v-if="!chartData || chartData.length === 0" class="absolute inset-0 flex items-center justify-center text-slate-500 font-bold">
                    Aucune donnée
                </div>
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
