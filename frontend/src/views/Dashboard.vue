<script setup>
import { 
  MagnifyingGlassIcon,
  ArrowUpRightIcon,
  ArrowDownRightIcon,
  BriefcaseIcon,
  DocumentCheckIcon,
  ChatBubbleLeftRightIcon,
  UserPlusIcon,
  EllipsisHorizontalIcon
} from '@heroicons/vue/24/outline'

const kpiStats = [
  { 
    label: 'Candidatures envoyées', 
    value: '852', 
    trend: '+18%', 
    trendUp: true,
    icon: BriefcaseIcon,
    color: 'text-indigo-400',
    bg: 'bg-indigo-500/10'
  },
  { 
    label: 'CV Analysés', 
    value: '47', 
    trend: '-9%', 
    trendUp: false,
    icon: DocumentCheckIcon,
    color: 'text-rose-400',
    bg: 'bg-rose-500/10'
  },
  { 
    label: 'Entretiens Décrochés', 
    value: '11', 
    trend: '+6%', 
    trendUp: true,
    icon: ChatBubbleLeftRightIcon,
    color: 'text-emerald-400',
    bg: 'bg-emerald-500/10'
  },
  { 
    label: 'Réseau (Contacts)', 
    value: '162', 
    trend: '+38%', 
    trendUp: true,
    icon: UserPlusIcon,
    color: 'text-amber-400',
    bg: 'bg-amber-500/10'
  }
]

const recentActivity = [
  { name: 'Développeur Fullstack', company: 'Google', status: 'Candidature Envoyée', score: 93, color: 'bg-emerald-500', initial: 'G' },
  { name: 'Data Scientist Junior', company: 'Netflix', status: 'En attente', score: 53, color: 'bg-rose-500', initial: 'N' },
  { name: 'Ingénieur IA', company: 'Microsoft', status: 'Entretien Planifié', score: 88, color: 'bg-indigo-500', initial: 'M' },
  { name: 'Analyste Cyber', company: 'Amazon', status: 'CV Refusé', score: 19, color: 'bg-amber-500', initial: 'A' },
  { name: 'DevOps Cloud', company: 'Stripe', status: 'Candidature Envoyée', score: 91, color: 'bg-violet-500', initial: 'S' },
]
</script>

<template>
  <div class="p-4 md:p-6 lg:p-8 max-w-[1600px] mx-auto space-y-6 animate-fade-in-up">
    
    <!-- Greeting Section -->
    <div class="flex flex-col md:flex-row md:items-end justify-between gap-4">
      <div>
        <h1 class="text-3xl md:text-3xl font-display font-bold text-white tracking-tight">
          Bonjour Yves, 
          <span class="block sm:inline text-slate-400 font-medium text-2xl">Prêt pour tes recherches ?</span>
        </h1>
      </div>
      
      <!-- Date Filter -->
      <div class="flex items-center gap-2 bg-surface-900 border border-surface-800 rounded-lg p-1 shadow-sm">
        <button class="px-3 py-1.5 text-xs font-semibold text-slate-200 bg-surface-800 rounded-md shadow-sm">Overview</button>
        <button class="px-3 py-1.5 text-xs font-semibold text-slate-400 hover:text-slate-200 transition-colors">Performance</button>
        <button class="px-3 py-1.5 text-xs font-semibold text-slate-400 hover:text-slate-200 transition-colors">Objectifs</button>
      </div>
    </div>

    <!-- Main Grid Layout -->
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 mt-6">
      
      <!-- Left Column (KPIs & Main Chart) -->
      <div class="lg:col-span-8 space-y-6">
        
        <!-- KPI Row -->
        <div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
          <div 
            v-for="stat in kpiStats" 
            :key="stat.label"
            class="bg-surface-900 border border-surface-800 rounded-2xl p-5 shadow-sm hover:border-surface-700 transition-all group"
          >
            <div class="flex justify-between items-start mb-4">
                <div :class="['w-10 h-10 rounded-xl flex items-center justify-center', stat.bg]">
                    <component :is="stat.icon" :class="['w-5 h-5', stat.color]" />
                </div>
                <div 
                    :class="[
                      'px-2 py-0.5 rounded-full text-[11px] font-bold flex items-center gap-1',
                      stat.trendUp ? 'bg-emerald-500/10 text-emerald-400' : 'bg-rose-500/10 text-rose-400'
                    ]"
                >
                    <ArrowUpRightIcon v-if="stat.trendUp" class="w-3 h-3" />
                    <ArrowDownRightIcon v-else class="w-3 h-3" />
                    {{ stat.trend }}
                </div>
            </div>
            <div>
              <p class="text-[28px] font-bold text-white leading-none tracking-tight">{{ stat.value }}</p>
              <p class="text-xs text-slate-400 font-medium mt-1">{{ stat.label }}</p>
            </div>
            
            <!-- Mock Sparkline -->
            <div class="mt-4 h-8 flex items-end gap-1 opacity-50 group-hover:opacity-100 transition-opacity">
                <div class="w-full bg-surface-800 rounded-t-sm" :style="`height: ${Math.random() * 60 + 20}%`"></div>
                <div class="w-full bg-surface-800 rounded-t-sm" :style="`height: ${Math.random() * 60 + 20}%`"></div>
                <div class="w-full bg-surface-800 rounded-t-sm" :style="`height: ${Math.random() * 60 + 20}%`"></div>
                <div class="w-full bg-surface-800 rounded-t-sm" :style="`height: ${Math.random() * 60 + 20}%`"></div>
                <div class="w-full bg-surface-800 rounded-t-sm" :style="`height: ${Math.random() * 60 + 20}%`"></div>
                <div class="w-full" :class="stat.trendUp ? 'bg-emerald-500' : 'bg-rose-500'" :style="`height: ${Math.random() * 40 + 60}%`" style="border-radius: 2px 2px 0 0;"></div>
            </div>
          </div>
        </div>

        <!-- Main Chart Area -->
        <div class="bg-surface-900 border border-surface-800 rounded-2xl p-6 shadow-sm relative overflow-hidden">
            <div class="flex items-center justify-between mb-8 relative z-10">
                <div>
                    <h3 class="text-lg font-bold text-white flex items-center gap-2">
                        <span class="w-2 h-2 rounded-full bg-indigo-500"></span>
                        Croissance des Opportunités
                    </h3>
                    <p class="text-sm text-slate-400 mt-1">Analyse du volume de postes sourcés par l'IA.</p>
                </div>
                <select class="bg-surface-800 border-none text-xs text-slate-300 rounded-lg py-1.5 px-3 focus:ring-0 cursor-pointer text-center font-semibold">
                    <option>Mensuel</option>
                    <option>Hebdomadaire</option>
                </select>
            </div>
            
            <!-- Chart Bar Mockup -->
            <div class="h-64 flex items-end justify-between gap-2 sm:gap-4 lg:gap-8 px-2 relative z-10">
                <!-- Grid Lines -->
                <div class="absolute inset-x-0 bottom-0 top-0 flex flex-col justify-between pointer-events-none">
                    <div class="border-b border-surface-800/50 w-full flex items-center justify-start"><span class="text-[10px] text-slate-500 -mt-2">100</span></div>
                    <div class="border-b border-surface-800/50 w-full flex items-center justify-start"><span class="text-[10px] text-slate-500 -mt-2">50</span></div>
                    <div class="border-b border-surface-800/50 w-full flex items-center justify-start"><span class="text-[10px] text-slate-500 -mt-2">0</span></div>
                </div>

                <div class="w-full bg-indigo-500/20 rounded-t-md relative group"><div class="absolute bottom-0 w-full bg-indigo-500 rounded-t-md transition-all group-hover:bg-indigo-400 shadow-[0_0_15px_rgba(99,102,241,0.3)]" style="height: 45%;"></div><span class="absolute -bottom-6 w-full text-center text-[10px] text-slate-500 font-bold uppercase">Avr</span></div>
                <div class="w-full bg-indigo-500/20 rounded-t-md relative group"><div class="absolute bottom-0 w-full bg-indigo-500 rounded-t-md transition-all group-hover:bg-indigo-400 shadow-[0_0_15px_rgba(99,102,241,0.3)]" style="height: 80%;"></div><span class="absolute -bottom-6 w-full text-center text-[10px] text-slate-500 font-bold uppercase">Mai</span></div>
                <div class="w-full bg-indigo-500/20 rounded-t-md relative group"><div class="absolute bottom-0 w-full bg-indigo-500 rounded-t-md transition-all group-hover:bg-indigo-400 shadow-[0_0_15px_rgba(99,102,241,0.3)]" style="height: 35%;"></div><span class="absolute -bottom-6 w-full text-center text-[10px] text-slate-500 font-bold uppercase">Juin</span></div>
                <div class="w-full bg-indigo-500/20 rounded-t-md relative group"><div class="absolute bottom-0 w-full bg-indigo-500 rounded-t-md transition-all group-hover:bg-indigo-400 shadow-[0_0_15px_rgba(99,102,241,0.3)]" style="height: 60%;"></div><span class="absolute -bottom-6 w-full text-center text-[10px] text-slate-500 font-bold uppercase">Juil</span></div>
                <div class="w-full bg-indigo-500/20 rounded-t-md relative group"><div class="absolute bottom-0 w-full bg-indigo-500 rounded-t-md transition-all group-hover:bg-indigo-400 shadow-[0_0_15px_rgba(99,102,241,0.3)]" style="height: 95%;"></div><span class="absolute -bottom-6 w-full text-center text-[10px] text-slate-500 font-bold uppercase">Aou</span></div>
                <div class="w-full bg-indigo-500/20 rounded-t-md relative group"><div class="absolute bottom-0 w-full bg-indigo-500 rounded-t-md transition-all group-hover:bg-indigo-400 shadow-[0_0_15px_rgba(99,102,241,0.3)]" style="height: 50%;"></div><span class="absolute -bottom-6 w-full text-center text-[10px] text-slate-500 font-bold uppercase">Sep</span></div>
                <div class="w-full bg-indigo-500/20 rounded-t-md relative group"><div class="absolute bottom-0 w-full bg-indigo-500 rounded-t-md transition-all group-hover:bg-indigo-400 shadow-[0_0_15px_rgba(99,102,241,0.3)]" style="height: 75%;"></div><span class="absolute -bottom-6 w-full text-center text-[10px] text-slate-500 font-bold uppercase">Oct</span></div>
                <div class="w-full bg-indigo-500/20 rounded-t-md relative group"><div class="absolute bottom-0 w-full bg-indigo-500 rounded-t-md transition-all group-hover:bg-indigo-400 shadow-[0_0_15px_rgba(99,102,241,0.3)]" style="height: 40%;"></div><span class="absolute -bottom-6 w-full text-center text-[10px] text-slate-500 font-bold uppercase">Nov</span></div>
            </div>
            <div class="mt-8 pt-4 border-t border-surface-800 flex justify-center gap-6">
                <div class="flex items-center gap-2"><div class="w-3 h-3 rounded-full bg-indigo-500 shadow-[0_0_10px_rgba(99,102,241,0.8)]"></div><span class="text-xs text-slate-400 font-medium tracking-wide">Boost Radar IA</span></div>
                <div class="flex items-center gap-2"><div class="w-3 h-3 rounded-full bg-surface-700"></div><span class="text-xs text-slate-400 font-medium tracking-wide">Candidatures Manuelles</span></div>
            </div>
        </div>

      </div>

      <!-- Right Column (Leaderboard / Activity) -->
      <div class="lg:col-span-4 bg-surface-900 border border-surface-800 rounded-2xl p-6 shadow-sm flex flex-col">
        <div class="flex items-center justify-between mb-6">
            <h3 class="text-lg font-bold text-white flex items-center gap-2">
                <div class="p-1.5 bg-indigo-500/10 rounded-lg">
                    <DocumentCheckIcon class="w-5 h-5 text-indigo-400" />
                </div>
                Activité Récente
            </h3>
            <button class="text-[11px] font-bold text-indigo-400 hover:text-indigo-300 uppercase tracking-widest transition-colors">Voir tout</button>
        </div>

        <div class="flex justify-between text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-3 px-2 border-b border-surface-800 pb-2">
            <span>Entreprise / Rôle</span>
            <span>Match</span>
        </div>

        <div class="flex-1 overflow-y-auto space-y-1">
            <div 
                v-for="(item, idx) in recentActivity" 
                :key="idx"
                class="flex items-center justify-between p-2 rounded-xl hover:bg-surface-800 transition-colors group cursor-pointer"
            >
                <div class="flex items-center gap-3 min-w-0">
                    <div :class="['w-8 h-8 rounded-full flex items-center justify-center text-white font-bold text-xs shrink-0', item.color]">
                        {{ item.initial }}
                    </div>
                    <div class="min-w-0 truncate">
                        <p class="text-sm font-bold text-slate-200 group-hover:text-white truncate">{{ item.company }}</p>
                        <p class="text-[11px] text-slate-400 truncate">{{ item.name }}</p>
                    </div>
                </div>
                <div class="flex items-center gap-3 shrink-0">
                    <div class="text-right hidden sm:block">
                        <p class="text-[10px] text-slate-500 font-medium">{{ item.status }}</p>
                    </div>
                    <div class="w-8 flex justify-end">
                        <span class="text-xs font-bold font-mono" :class="item.score > 80 ? 'text-emerald-400' : (item.score > 40 ? 'text-amber-400' : 'text-rose-400')">
                            {{ item.score }}
                        </span>
                    </div>
                </div>
            </div>
        </div>

        <button class="w-full mt-4 py-3 bg-surface-800 hover:bg-surface-700 border border-surface-700 text-slate-300 text-sm font-bold rounded-xl transition-all shadow-sm">
            Exporter le Rapport (.csv)
        </button>
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
