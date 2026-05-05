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
    color: 'bg-indigo-50', textColor: 'text-indigo-600',
    locked: false,
    actionPromptKey: 'mentor.features.cv_audit_prompt'
  },
  {
    titleKey: 'mentor.features.interview_title',
    descKey: 'mentor.features.interview_desc',
    icon: AcademicCapIcon,
    color: 'bg-emerald-50', textColor: 'text-emerald-600',
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
  <div class="db-root animate-fade-in">
    <div class="max-w-7xl mx-auto">
      
      <!-- Dashboard Header Style -->
      <div class="db-header">
        <div class="header-title-box">
          <div class="flex items-center gap-4 mb-2">
            <div class="w-12 h-12 bg-white rounded-2xl shadow-sm border border-slate-100 flex items-center justify-center overflow-hidden">
               <img src="/logo.png" class="w-8 h-8 object-contain animate-pulse" />
            </div>
            <h1>{{ t('mentor.title') }}</h1>
          </div>
          <p>{{ t('mentor.subtitle') }}</p>
        </div>

        <div class="header-date-box hidden md:flex">
          <div class="date-num">🎓</div>
          <div class="date-str">MENTOR IA</div>
          <div class="date-divider"></div>
          <div class="date-str text-slate-400">GOLDARMY PLATFORM</div>
        </div>
      </div>

      <!-- Features Grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        <div 
          v-for="feature in mentorFeatures" 
          :key="feature.titleKey"
          @click="handleFeatureClick(feature)"
          class="kpi-card cursor-pointer group"
        >
          <!-- Locked Badge -->
          <div v-if="feature.locked" class="card-tag bg-slate-100 text-slate-500">
            {{ $t('mentor.coming_soon_badge') }}
          </div>
          <div v-else class="card-tag bg-[#E85D3E]/10 text-[#E85D3E]">
            ACTIVE
          </div>

          <div :class="[feature.color, 'icon-box']">
            <component :is="feature.icon" :class="['w-6 h-6', feature.textColor]" />
          </div>

          <h3 class="text-xl font-bold text-slate-900 mb-2 group-hover:text-[#E85D3E] transition-colors">{{ $t(feature.titleKey) }}</h3>
          <p class="text-slate-500 text-sm leading-relaxed mb-8 flex-1">{{ $t(feature.descKey) }}</p>

          <div class="pt-6 border-t border-slate-50 flex items-center justify-between">
            <span class="text-sm font-bold text-slate-400 group-hover:text-[#E85D3E] transition-colors">
               {{ feature.locked ? $t('mentor.coming_soon_btn') : $t('mentor.launch_tool') }}
            </span>
            <div class="w-8 h-8 rounded-full bg-slate-50 flex items-center justify-center group-hover:bg-[#E85D3E] transition-all">
               <svg class="w-4 h-4 text-slate-400 group-hover:text-white transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                 <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="9 5l7 7-7 7" />
               </svg>
            </div>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>





<style scoped>
.db-root {
  min-height: 100vh;
  background-color: #F9FAFB;
  padding: 40px;
}

.db-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 40px;
}

.header-title-box {
  display: flex;
  flex-direction: column;
}

.header-title-box h1 {
  font-size: 32px;
  font-weight: 800;
  color: #111827;
  letter-spacing: -0.02em;
  margin: 0;
}

.header-title-box p {
  color: #6B7280;
  font-size: 16px;
  margin-top: 4px;
}

.header-date-box {
  display: flex;
  align-items: center;
  background: white;
  padding: 8px 16px;
  border-radius: 12px;
  border: 1px solid #E5E7EB;
  box-shadow: 0 1px 2px rgba(0,0,0,0.05);
}

.date-num {
  font-weight: 800;
  font-size: 20px;
  color: #E85D3E;
  margin-right: 12px;
}

.date-str {
  font-size: 14px;
  font-weight: 600;
  color: #374151;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.date-divider {
  width: 1px;
  height: 20px;
  background: #E5E7EB;
  margin: 0 12px;
}

.kpi-card {
  background: white;
  border-radius: 24px;
  padding: 24px;
  border: 1px solid #E5E7EB;
  box-shadow: 0 1px 3px rgba(0,0,0,0.02);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.kpi-card:hover {
  border-color: #E85D3E;
  box-shadow: 0 10px 20px rgba(232, 93, 62, 0.05);
  transform: translateY(-2px);
}

.icon-box {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 20px;
  transition: transform 0.3s ease;
}

.kpi-card:hover .icon-box {
  transform: scale(1.1) rotate(-5deg);
}

.card-tag {
  position: absolute;
  top: 24px;
  right: 24px;
  font-size: 10px;
  font-weight: 800;
  padding: 4px 8px;
  border-radius: 6px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
</style>



