<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { 
  MagnifyingGlassIcon,
  SparklesIcon,
  DocumentCheckIcon,
  ChartPieIcon,
  ArrowRightIcon
} from '@heroicons/vue/24/solid'

const router = useRouter()
const searchInput = ref('')

const quickActions = [
  { 
    title: 'Audit Express CV', 
    desc: 'Analyse tes compétences', 
    icon: DocumentCheckIcon, 
    color: 'text-indigo-400 bg-indigo-500/10 border-indigo-500/20' 
  },
  { 
    title: 'Offres Juniors', 
    desc: 'Débutant (< 2 ans)', 
    icon: SparklesIcon, 
    color: 'text-amber-400 bg-amber-500/10 border-amber-500/20' 
  },
  { 
    title: 'Analyse Marché', 
    desc: 'Salaires & Tendances', 
    icon: ChartPieIcon, 
    color: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20' 
  }
]

const recentStats = [
  { label: 'Candidatures envoyées', value: '12', trend: '+3 cette semaine' },
  { label: 'CV Adaptés', value: '4', trend: 'Taux de match: 85%' },
  { label: 'Retours positifs', value: '1', trend: 'Entretien prévu' }
]

const handleSearch = () => {
  if (searchInput.value) {
     router.push({ name: 'AgentChat', query: { prompt: searchInput.value }})
  }
}
</script>

<template>
  <div class="p-6 md:p-10 max-w-7xl mx-auto space-y-8 animate-fade-in">
    
    <!-- Hero Section -->
    <section class="relative overflow-hidden rounded-3xl bg-gradient-to-br from-slate-800 to-slate-900 border border-slate-700/60 p-8 md:p-12 shadow-2xl">
       <div class="absolute top-0 right-0 -mt-20 -mr-20 w-80 h-80 bg-amber-500/10 rounded-full blur-3xl pointer-events-none"></div>
       <div class="absolute bottom-0 left-0 -mb-20 -ml-20 w-72 h-72 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none"></div>
       
       <div class="relative z-10 flex flex-col md:flex-row gap-8 items-center justify-between">
          <div class="space-y-4 max-w-2xl">
            <h1 class="text-3xl md:text-5xl font-extrabold text-white tracking-tight">
              Bienvenue dans ta <span class="bg-gradient-to-r from-amber-400 to-orange-500 bg-clip-text text-transparent">Tour de Contrôle</span> de Carrière.
            </h1>
            <p class="text-slate-400 text-lg md:text-xl">
              Prêt à décrocher ton prochain poste ? L'Agent IA analyse le marché en temps réel et postule de manière chirurgicale à ta place.
            </p>
          </div>
       </div>

       <!-- Search input overlayed -->
       <div class="mt-10 relative max-w-2xl z-20">
          <div class="relative flex items-center">
            <MagnifyingGlassIcon class="absolute left-4 w-6 h-6 text-slate-400" />
            <input 
              v-model="searchInput"
              @keyup.enter="handleSearch"
              type="text" 
              placeholder="Que cherches-tu aujourd'hui ? (ex: Stage Python Québec)"
              class="w-full pl-12 pr-32 py-4 bg-slate-900/80 backdrop-blur border border-slate-600 rounded-2xl text-slate-200 focus:outline-none focus:ring-2 focus:ring-amber-500/50 focus:border-amber-500 shadow-inner transition-all text-lg placeholder-slate-500"
            />
            <button 
              @click="handleSearch"
              class="absolute right-2 px-6 py-2 bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-400 hover:to-orange-400 text-slate-900 font-bold rounded-xl transition-all h-[calc(100%-16px)] flex items-center">
              Rechercher
            </button>
          </div>
       </div>
    </section>

    <!-- Content Grid -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
      
      <!-- Actions Rapides -->
      <div class="lg:col-span-2 space-y-4">
        <h2 class="text-xl font-bold text-slate-200 flex items-center gap-2">
          ⚡ Actions Rapides
        </h2>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div 
            v-for="action in quickActions" 
            :key="action.title"
            class="group cursor-pointer p-5 rounded-2xl border border-slate-700 bg-slate-800 hover:bg-slate-750 transition-all hover:scale-[1.02] hover:shadow-xl flex flex-col items-start gap-4"
          >
            <div :class="['p-3 rounded-xl border', action.color]">
               <component :is="action.icon" class="w-6 h-6" />
            </div>
            <div>
              <h3 class="font-bold text-slate-200 group-hover:text-white">{{ action.title }}</h3>
              <p class="text-sm text-slate-400 mt-1">{{ action.desc }}</p>
            </div>
            <ArrowRightIcon class="w-5 h-5 text-slate-500 group-hover:text-amber-400 mt-auto self-end transition-colors" />
          </div>
        </div>
      </div>

      <!-- Stats CRM Mini -->
      <div class="space-y-4">
        <h2 class="text-xl font-bold text-slate-200 flex items-center gap-2">
          📊 Mon Entonnoir
        </h2>
        <div class="bg-slate-800 border border-slate-700 rounded-2xl p-5 space-y-4">
           <div v-for="(stat, idx) in recentStats" :key="idx" class="flex justify-between items-center p-3 rounded-xl bg-slate-900/50 border border-slate-700/50">
              <div>
                <p class="text-xs text-slate-400 uppercase tracking-wider font-semibold mb-1">{{ stat.label }}</p>
                <p class="text-2xl font-bold text-white">{{ stat.value }}</p>
              </div>
              <div class="text-right">
                <span class="text-xs font-medium text-emerald-400 bg-emerald-400/10 px-2 py-1 rounded-lg border border-emerald-400/20">
                  {{ stat.trend }}
                </span>
              </div>
           </div>
           
           <button @click="router.push('/crm')" class="w-full mt-2 py-3 text-sm font-semibold text-slate-300 hover:text-white bg-slate-700 hover:bg-slate-600 rounded-xl transition-colors">
             Voir le CRM complet
           </button>
        </div>
      </div>

    </div>
  </div>
</template>

<style scoped>
.animate-fade-in {
  animation: fadeIn 0.5s ease-out forwards;
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
