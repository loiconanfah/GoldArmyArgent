<script setup>
import { ref } from 'vue'
import { BriefcaseIcon, FunnelIcon, MapPinIcon, CurrencyDollarIcon, CheckCircleIcon } from '@heroicons/vue/24/outline'

const filter = ref('Toutes')

const mockJobs = [
  {
    id: 1,
    title: 'Stage Développeur Full-Stack (Vue/Python)',
    company: 'TechCorp QC',
    location: 'Québec City, QC',
    matchScore: 92,
    salary: '22$ - 28$/h',
    type: 'Stage',
    posted: 'Il y a 2h',
    desc: "Rejoignez notre escouade d'élite pour bâtir la prochaine génération d'outils internes. Forte courbe d'apprentissage."
  },
  {
    id: 2,
    title: 'Développeur Logiciel Junior',
    company: 'Innovatech',
    location: 'Montréal, QC (Hybride)',
    matchScore: 85,
    salary: '65k - 75k',
    type: 'Emploi Junior',
    posted: 'Il y a 1j',
    desc: "Nous cherchons un talent junior maîtrisant Python et intéressé par le Cloud Computing (AWS/Azure)."
  },
  {
    id: 3,
    title: 'Internship Machine Learning',
    company: 'DataMinds Inc',
    location: 'Remote',
    matchScore: 78,
    salary: 'Non spécifié',
    type: 'Stage',
    posted: 'Il y a 3j',
    desc: "Aide notre équipe R&D à nettoyer et structurer les données d'entraînement pour nos LLM."
  }
]
</script>

<template>
  <div class="p-6 md:p-10 max-w-7xl mx-auto space-y-8 animate-fade-in">
    
    <!-- Title & Filters -->
    <div class="flex flex-col md:flex-row md:items-end justify-between gap-4 border-b border-slate-700 pb-6">
       <div>
         <h1 class="text-3xl font-bold flex items-center gap-3 text-white">
           <span class="p-2 bg-gradient-to-br from-emerald-400 to-teal-500 rounded-xl shadow-lg shadow-teal-500/20">
              <BriefcaseIcon class="w-8 h-8 text-slate-900" />
           </span>
           Opportunités (Sniper)
         </h1>
         <p class="text-slate-400 mt-2 text-lg">Les pépites trouvées par l'Agent GoldArmy.</p>
       </div>
       
       <div class="flex items-center gap-2 bg-slate-800 p-1.5 rounded-xl border border-slate-700">
          <FunnelIcon class="w-5 h-5 text-slate-400 ml-2" />
          <select v-model="filter" class="bg-transparent text-slate-200 focus:outline-none focus:ring-0 cursor-pointer pr-4 font-medium appearance-none">
            <option>Toutes les pertinentes</option>
            <option>Stages Uniquement</option>
            <option>Juniors (< 2 ans)</option>
            <option>Score > 80%</option>
          </select>
       </div>
    </div>

    <!-- Job Cards List -->
    <div class="grid grid-cols-1 gap-4">
       <div 
         v-for="job in mockJobs" 
         :key="job.id"
         class="flex flex-col md:flex-row gap-6 p-6 rounded-2xl bg-slate-800/80 border border-slate-700 hover:border-emerald-500/50 transition-all hover:bg-slate-800 hover:shadow-xl hover:shadow-emerald-900/10 group"
       >
          <!-- Score Bubble -->
          <div class="hidden md:flex flex-col items-center justify-center shrink-0 w-24 h-24 rounded-full border-4 shadow-inner"
               :class="job.matchScore >= 90 ? 'border-emerald-500 bg-emerald-500/10' : (job.matchScore >= 80 ? 'border-amber-400 bg-amber-400/10' : 'border-slate-500 bg-slate-500/10')">
            <span class="text-2xl font-black" :class="job.matchScore >= 90 ? 'text-emerald-400' : (job.matchScore >= 80 ? 'text-amber-400' : 'text-slate-300')">{{ job.matchScore }}</span>
            <span class="text-[10px] font-bold uppercase tracking-wider text-slate-400">Match</span>
          </div>

          <!-- Content -->
          <div class="flex-1 flex flex-col justify-center">
             <!-- Mobile Score -->
             <div class="md:hidden inline-flex items-center gap-1 mb-2">
                <span class="text-xs font-bold px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">Match {{job.matchScore}}%</span>
             </div>
             
             <div class="flex flex-wrap items-baseline gap-2 mb-1">
               <h3 class="text-xl font-bold text-slate-100 group-hover:text-white">{{ job.title }}</h3>
               <span class="text-sm font-medium text-emerald-400 bg-emerald-400/10 px-2 py-0.5 rounded-md border border-emerald-400/20">{{ job.company }}</span>
             </div>
             
             <div class="flex flex-wrap items-center gap-4 text-sm text-slate-400 mb-4 mt-2">
                <span class="flex items-center gap-1"><MapPinIcon class="w-4 h-4" /> {{ job.location }}</span>
                <span class="flex items-center gap-1"><CurrencyDollarIcon class="w-4 h-4" /> {{ job.salary }}</span>
                <span class="flex items-center gap-1 bg-slate-700 px-2 rounded-md">{{ job.type }}</span>
                <span>🕒 {{ job.posted }}</span>
             </div>
             
             <p class="text-sm text-slate-300 line-clamp-2 md:line-clamp-3 leading-relaxed">
               {{ job.desc }}
             </p>
          </div>
          
          <!-- Actions -->
          <div class="flex flex-col gap-2 justify-center shrink-0 w-full md:w-auto mt-4 md:mt-0 border-t md:border-t-0 md:border-l border-slate-700 pt-4 md:pt-0 md:pl-6">
             <button class="w-full flex items-center justify-center gap-2 px-5 py-3 bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 text-slate-900 font-bold rounded-xl transition-all shadow-lg shadow-teal-500/20">
                <CheckCircleIcon class="w-5 h-5 text-slate-800" />
                Détails & Postuler
             </button>
             <button class="w-full px-5 py-3 bg-slate-700 hover:bg-slate-600 text-slate-200 font-semibold rounded-xl transition-all text-sm border border-slate-600">
                Générer Email Froid
             </button>
          </div>
       </div>
    </div>
    
  </div>
</template>
