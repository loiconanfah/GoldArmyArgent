<script setup>
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { 
  AcademicCapIcon, 
  BoltIcon, 
  CodeBracketIcon,
  DocumentArrowDownIcon
} from '@heroicons/vue/24/outline'

const router = useRouter()
const { t } = useI18n()

const mentorFeatures = [
  {
    titleKey: 'mentor.features.cv_audit_title',
    descKey: 'mentor.features.cv_audit_desc',
    icon: DocumentArrowDownIcon,
    color: 'from-indigo-500 to-purple-500',
    locked: false,
    actionPromptKey: 'mentor.features.cv_audit_prompt'
  },
  {
    titleKey: 'mentor.features.portfolio_title',
    descKey: 'mentor.features.portfolio_desc',
    icon: CodeBracketIcon,
    color: 'from-emerald-500 to-teal-500',
    locked: true,
    actionPromptKey: 'mentor.features.portfolio_prompt'
  },
  {
    titleKey: 'mentor.features.interview_title',
    descKey: 'mentor.features.interview_desc',
    icon: AcademicCapIcon,
    color: 'from-blue-500 to-violet-500',
    locked: false,
    routeTarget: '/interview'
  }
]

const handleFeatureClick = (feature) => {
    if (!feature.locked) {
        if (feature.routeTarget) {
            router.push(feature.routeTarget)
        } else if (feature.actionPromptKey) {
            const query = { prompt: t(feature.actionPromptKey) }
            if (feature.titleKey.includes('cv_audit')) {
                query.action = 'cv_audit'
            }
            router.push({ name: 'AgentChat', query })
        }
    }
}
</script>

<template>
  <div class="p-6 md:p-10 max-w-7xl mx-auto animate-fade-in space-y-8">
    
    <!-- Title Section -->
    <div class="border-b border-slate-700 pb-6">
       <h1 class="text-3xl font-bold flex items-center gap-3 text-white">
         <span class="p-2 bg-gradient-to-br from-purple-500 to-indigo-500 rounded-xl shadow-lg shadow-indigo-500/20">
            <AcademicCapIcon class="w-8 h-8 text-white" />
         </span>
         {{ $t('mentor.title') }}
         <span class="bg-gradient-to-r from-purple-500 to-indigo-500 text-white text-xs uppercase font-bold px-3 py-1 rounded-full tracking-wider ml-2">Phase 2</span>
       </h1>
       <p class="text-slate-400 mt-2 text-lg">{{ $t('mentor.subtitle') }}</p>
    </div>

    <!-- Feature Cards -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
       <div 
         v-for="feature in mentorFeatures" 
         :key="feature.titleKey"
         class="relative flex flex-col p-6 rounded-2xl border border-slate-700 bg-slate-800/50 backdrop-blur overflow-hidden group hover:border-slate-500 transition-colors"
       >
          <!-- Background Glow -->
          <div :class="`absolute -top-24 -right-24 w-48 h-48 bg-gradient-to-br ${feature.color} opacity-20 rounded-full blur-3xl group-hover:opacity-30 transition-opacity`"></div>
          
          <!-- Coming Soon Badge -->
          <div v-if="feature.locked" class="absolute top-4 right-4 z-20">
             <span class="bg-indigo-500 text-white text-[10px] font-black px-2 py-1 rounded-md shadow-lg shadow-indigo-500/20 animate-pulse">
                {{ $t('mentor.coming_soon_badge') }}
             </span>
          </div>
          
          <div class="relative z-10 flex-1">
             <div :class="`w-12 h-12 rounded-xl bg-gradient-to-br ${feature.color} flex items-center justify-center shadow-lg mb-6`">
               <component :is="feature.icon" class="w-6 h-6 text-white" />
             </div>
             <h3 class="text-xl font-bold text-white mb-3">{{ $t(feature.titleKey) }}</h3>
             <p class="text-slate-400 text-sm leading-relaxed mb-6">{{ $t(feature.descKey) }}</p>
          </div>
          
          <div class="relative z-10 mt-auto pt-4 border-t border-slate-700 flex justify-between items-center">
             <button 
                @click="handleFeatureClick(feature)"
                :disabled="feature.locked" :class="[
               'px-4 py-2 font-bold rounded-lg transition-colors text-sm w-full text-center',
               feature.locked ? 'bg-slate-700 text-slate-500 cursor-not-allowed' : 'bg-slate-100/10 text-white hover:bg-slate-100/20'
             ]">
               {{ feature.locked ? $t('mentor.coming_soon_btn') : $t('mentor.launch_tool') }}
             </button>
          </div>
       </div>
    </div>
    
  </div>
</template>
