<script setup>
import { 
  ChartBarIcon, 
  EnvelopeIcon, 
  ArrowPathIcon,
  ExclamationCircleIcon
} from '@heroicons/vue/24/outline'

const columns = [
  { id: 'todo', title: 'À Postuler', count: 2, icon: EnvelopeIcon, color: 'text-amber-400', bg: 'bg-amber-400/10' },
  { id: 'applied', title: 'Candidatures Envoyées', count: 5, icon: ChartBarIcon, color: 'text-blue-400', bg: 'bg-blue-400/10' },
  { id: 'followup', title: 'Relance Requise', count: 1, icon: ExclamationCircleIcon, color: 'text-rose-400', bg: 'bg-rose-400/10' },
  { id: 'interview', title: 'Entretiens', count: 1, icon: ArrowPathIcon, color: 'text-emerald-400', bg: 'bg-emerald-400/10' }
]

const crmCards = {
  'todo': [
     { id: 1, company: 'Stripe', role: 'Integration Engineer Intern', date: 'Ajouté hier' },
     { id: 2, company: 'Shopify', role: 'Backend Developer (Junior)', date: 'Ajouté il y a 3j' }
  ],
  'applied': [
     { id: 3, company: 'TechCorp QC', role: 'Stage Full-Stack', date: 'Envoyé le 12/03' }
  ],
  'followup': [
     { id: 4, company: 'Innovatech', role: 'Développeur Logiciel', date: 'J+8 - Relance IA prête' }
  ],
  'interview': [
     { id: 5, company: 'DataMinds Inc', role: 'Internship ML', date: 'Call RH Ven. 15h' }
  ]
}
</script>

<template>
  <div class="p-6 md:p-10 mx-auto w-full max-w-[1400px] flex flex-col h-full animate-fade-in">
    
    <div class="border-b border-slate-700 pb-6 mb-8 shrink-0">
       <h1 class="text-3xl font-bold flex items-center gap-3 text-white">
         <span class="p-2 bg-gradient-to-br from-rose-500 to-orange-500 rounded-xl shadow-lg shadow-orange-500/20">
            <ChartBarIcon class="w-8 h-8 text-white" />
         </span>
         CRM Candidatures
         <span class="bg-gradient-to-r from-rose-500 to-orange-500 text-white text-xs uppercase font-bold px-3 py-1 rounded-full tracking-wider ml-2">Phase 3</span>
       </h1>
       <p class="text-slate-400 mt-2 text-lg">Centralise tes envois. L'Agent s'occupe de minuter tes relances automatiques.</p>
    </div>

    <!-- Kanban Board -->
    <div class="flex-1 overflow-x-auto pb-4">
      <div class="flex gap-6 min-w-max h-full">
         
         <!-- Column -->
         <div 
           v-for="col in columns" 
           :key="col.id" 
           class="w-80 flex flex-col bg-slate-800/40 rounded-3xl border border-slate-700/50 p-4 shrink-0"
         >
            <!-- Column Header -->
            <div class="flex items-center justify-between mb-4 px-2">
               <h3 class="flex items-center gap-2 font-bold text-slate-200">
                 <component :is="col.icon" :class="['w-5 h-5', col.color]" />
                 {{ col.title }}
               </h3>
               <span :class="['text-xs font-bold px-2 py-1 rounded-lg', col.bg, col.color]">
                 {{ col.count }}
               </span>
            </div>
            
            <!-- Cards Container -->
            <div class="flex-1 space-y-3 overflow-y-auto pr-1 custom-scrollbar">
               <div 
                 v-for="card in crmCards[col.id]" 
                 :key="card.id"
                 class="bg-slate-800 border border-slate-700 p-4 rounded-xl shadow-sm hover:border-slate-500 hover:shadow-md transition-all cursor-grab active:cursor-grabbing group relative"
               >
                  <!-- Card Decoration -->
                  <div :class="['absolute top-0 left-0 w-1 h-full rounded-l-xl opacity-0 group-hover:opacity-100 transition-opacity', col.bg.replace('/10', '')]"></div>
                  
                  <h4 class="font-bold text-slate-100 text-sm mb-1 line-clamp-1">{{ card.role }}</h4>
                  <p class="text-amber-500 text-sm font-medium">{{ card.company }}</p>
                  
                  <div class="mt-4 flex items-center justify-between">
                     <span class="text-[10px] uppercase font-bold text-slate-500 tracking-wider">
                       {{ card.date }}
                     </span>
                     
                     <button v-if="col.id === 'followup'" class="text-[10px] font-bold bg-rose-500/20 text-rose-400 hover:bg-rose-500 hover:text-white transition-colors px-2 py-1 rounded border border-rose-500/30">
                       Rédiger Relance
                     </button>
                     <button v-else-if="col.id === 'todo'" class="text-[10px] font-bold bg-amber-500/10 text-amber-500 hover:bg-amber-500 hover:text-slate-900 transition-colors px-2 py-1 rounded border border-amber-500/30">
                       Générer CV
                     </button>
                  </div>
               </div>
               
               <div v-if="!crmCards[col.id] || crmCards[col.id].length === 0" class="h-24 border-2 border-dashed border-slate-700 rounded-xl flex items-center justify-center text-slate-500 text-sm">
                 Glisser ici
               </div>
            </div>
         </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #334155;
  border-radius: 4px;
}
</style>
