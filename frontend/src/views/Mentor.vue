<script setup>
import { 
  AcademicCapIcon, 
  BoltIcon, 
  CodeBracketIcon 
} from '@heroicons/vue/24/outline'

const mentorFeatures = [
  {
    title: 'Audit CV Implacable',
    desc: 'Uploade ton CV complet. L\'IA va agir comme du Senior Management et déceler tes failles avant même que tu postules.',
    icon: BoltIcon,
    color: 'from-purple-500 to-fuchsia-500',
    locked: false
  },
  {
    title: 'Simulateur d\'Entretien',
    desc: 'Passe un examen blanc oral/écrit ultra-réaliste. L\'IA prend le rôle du CTO de la boîte que tu vises et te questionne.',
    icon: AcademicCapIcon,
    color: 'from-blue-500 to-cyan-500',
    locked: false
  },
  {
    title: 'Générateur de Projets',
    desc: 'L\'Agent détecte ce qui manque à ton CV (ex: Docker) et génère sur mesure le code de départ d\'un projet GitHub à réaliser ce week-end.',
    icon: CodeBracketIcon,
    color: 'from-emerald-500 to-teal-500',
    locked: true
  }
]
</script>

<template>
  <div class="p-6 md:p-10 max-w-7xl mx-auto animate-fade-in space-y-8">
    
    <!-- Title Section -->
    <div class="border-b border-slate-700 pb-6">
       <h1 class="text-3xl font-bold flex items-center gap-3 text-white">
         <span class="p-2 bg-gradient-to-br from-purple-500 to-indigo-500 rounded-xl shadow-lg shadow-indigo-500/20">
            <AcademicCapIcon class="w-8 h-8 text-white" />
         </span>
         Le Mentor IA
         <span class="bg-gradient-to-r from-purple-500 to-indigo-500 text-white text-xs uppercase font-bold px-3 py-1 rounded-full tracking-wider ml-2">Phase 2</span>
       </h1>
       <p class="text-slate-400 mt-2 text-lg">Prépare-toi comme un Pro. Audits, simulations, comblement de lacunes.</p>
    </div>

    <!-- Feature Cards -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
       <div 
         v-for="feature in mentorFeatures" 
         :key="feature.title"
         class="relative flex flex-col p-6 rounded-2xl border border-slate-700 bg-slate-800/50 backdrop-blur overflow-hidden group hover:border-slate-500 transition-colors"
       >
          <!-- Background Glow -->
          <div :class="`absolute -top-24 -right-24 w-48 h-48 bg-gradient-to-br ${feature.color} opacity-20 rounded-full blur-3xl group-hover:opacity-30 transition-opacity`"></div>
          
          <div class="relative z-10 flex-1">
             <div :class="`w-12 h-12 rounded-xl bg-gradient-to-br ${feature.color} flex items-center justify-center shadow-lg mb-6`">
               <component :is="feature.icon" class="w-6 h-6 text-white" />
             </div>
             <h3 class="text-xl font-bold text-white mb-3">{{ feature.title }}</h3>
             <p class="text-slate-400 text-sm leading-relaxed mb-6">{{ feature.desc }}</p>
          </div>
          
          <div class="relative z-10 mt-auto pt-4 border-t border-slate-700 flex justify-between items-center">
             <button :disabled="feature.locked" :class="[
               'px-4 py-2 font-bold rounded-lg transition-colors text-sm w-full text-center',
               feature.locked ? 'bg-slate-700 text-slate-500 cursor-not-allowed' : 'bg-slate-100/10 text-white hover:bg-slate-100/20'
             ]">
               {{ feature.locked ? 'Bientôt Disponible' : 'Lancer l\'outil' }}
             </button>
          </div>
       </div>
    </div>
    
  </div>
</template>
