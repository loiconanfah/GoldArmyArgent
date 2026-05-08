<template>
  <div class="interview-history-page min-h-screen relative overflow-hidden font-sans text-slate-900 bg-[#fbfbff]">
    <!-- MOVING BACKGROUND BLOBS (Dribbble/Framer style) -->
    <div class="absolute inset-0 pointer-events-none overflow-hidden">
      <div class="absolute -top-[10%] -left-[10%] w-[60%] h-[60%] bg-[#F59E0B]/10 rounded-full blur-[120px] animate-blob"></div>
      <div class="absolute -bottom-[10%] -right-[10%] w-[50%] h-[50%] bg-[#6366f1]/10 rounded-full blur-[120px] animate-blob animation-delay-2000"></div>
    </div>

    <div class="max-w-7xl mx-auto px-6 py-12 md:py-20 relative z-10">
      <!-- ARTISTIC HEADER -->
      <div class="flex flex-col items-center text-center space-y-6 mb-20">
        <button @click="router.push('/interview')" class="group flex items-center gap-3 px-6 py-3 bg-white/50 backdrop-blur-xl border border-white/80 rounded-full text-slate-500 hover:text-[#F59E0B] transition-all hover:px-8 shadow-sm">
          <ArrowLeftIcon class="w-4 h-4 transition-transform group-hover:-translate-x-1" />
          <span class="text-xs font-black uppercase tracking-widest">Retour au simulateur</span>
        </button>
        
        <div class="space-y-4">
          <h1 class="text-5xl md:text-7xl font-black tracking-tighter text-slate-900 leading-[0.9]">
            Votre <span class="text-transparent bg-clip-text bg-gradient-to-br from-[#F59E0B] to-[#FF8C6B]">Progression</span>
          </h1>
          <p class="text-slate-400 font-medium text-lg md:text-xl max-w-2xl mx-auto">
            Retrouvez chaque entretien, analysez vos faiblesses et dominez le marché du travail.
          </p>
        </div>
      </div>

      <!-- FLOATING STATS GRID -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-20 stagger-item">
        <div v-for="stat in stats" :key="stat.label" class="bg-white/40 backdrop-blur-2xl border border-white/60 p-8 rounded-[2.5rem] shadow-[0_20px_50px_rgba(0,0,0,0.03)] hover:shadow-xl transition-all hover:-translate-y-1">
          <div class="w-12 h-12 rounded-2xl bg-white flex items-center justify-center mb-6 shadow-sm text-[#F59E0B]">
            <component :is="stat.icon" class="w-6 h-6" />
          </div>
          <div class="text-3xl font-black text-slate-900 mb-1 tracking-tight">{{ stat.value }}</div>
          <div class="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em]">{{ stat.label }}</div>
        </div>
      </div>

      <!-- CONTENT -->
      <div v-if="loading" class="flex flex-col items-center justify-center py-20 gap-6">
        <div class="w-16 h-16 border-4 border-slate-100 border-t-[#F59E0B] rounded-full animate-spin"></div>
        <p class="text-slate-400 font-black text-xs uppercase tracking-[0.3em] animate-pulse">Synchronisation God Mode...</p>
      </div>

      <div v-else-if="sessions.length === 0" class="max-w-xl mx-auto text-center space-y-8 py-20 stagger-item">
        <div class="w-32 h-32 bg-white/50 backdrop-blur-xl border border-white rounded-[3rem] flex items-center justify-center mx-auto shadow-2xl rotate-3">
          <VideoCameraSlashIcon class="w-16 h-16 text-slate-200" />
        </div>
        <div class="space-y-4">
          <h2 class="text-3xl font-black text-slate-900">Le terrain est vide.</h2>
          <p class="text-slate-400 font-medium">Vos futures victoires n'attendent que votre premier passage devant l'IA.</p>
        </div>
        <router-link to="/interview" class="inline-flex px-10 py-5 bg-[#F59E0B] text-white font-black text-xs uppercase tracking-[0.2em] rounded-2xl transition-all shadow-2xl shadow-[#F59E0B]/30 hover:scale-105 active:scale-95">
          Démarrer l'entraînement
        </router-link>
      </div>

      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        <div v-for="session in sessions" :key="session.session_id" 
          @click="openDetail(session)"
          class="session-bento-card group relative">
          
          <div class="absolute inset-0 bg-gradient-to-br from-[#F59E0B]/5 to-[#6366f1]/5 opacity-0 group-hover:opacity-100 transition-opacity rounded-[3rem] -z-10 blur-xl"></div>
          
          <div class="bg-white/40 backdrop-blur-3xl border border-white/60 rounded-[2.5rem] p-8 h-full shadow-[0_20px_50px_rgba(0,0,0,0.02)] group-hover:shadow-[0_40px_100px_rgba(232,93,62,0.1)] group-hover:-translate-y-2 transition-all duration-700 cursor-pointer flex flex-col relative overflow-hidden">
            <!-- Hover Gradient -->
            <div class="absolute inset-0 bg-gradient-to-br from-transparent via-white/5 to-[#F59E0B]/5 opacity-0 group-hover:opacity-100 transition-opacity duration-700"></div>
            
            <div class="flex justify-between items-start mb-8 relative z-10">
              <div class="w-12 h-12 rounded-2xl bg-white shadow-xl flex items-center justify-center transition-transform group-hover:scale-110 group-hover:rotate-3 border border-slate-50">
                <component :is="getRecruiter(session.recruiter_id).icon" :class="getRecruiter(session.recruiter_id).color" class="w-6 h-6" />
              </div>
              <div :class="decisionClassRaw(session.decision)" class="px-4 py-1.5 rounded-full text-[8px] font-black uppercase tracking-widest backdrop-blur-xl border border-white/50 shadow-sm transition-transform group-hover:scale-105">
                {{ session.decision }}
              </div>
            </div>

            <div class="space-y-2 mb-8 relative z-10">
              <h3 class="text-xl font-black text-slate-900 tracking-tighter leading-tight group-hover:text-[#F59E0B] transition-colors line-clamp-2">
                {{ session.job_title }}
              </h3>
              <div class="flex items-center gap-2">
                <div class="w-1.5 h-1.5 rounded-full bg-slate-200 group-hover:bg-[#F59E0B]/30 transition-colors"></div>
                <p class="text-slate-400 font-bold text-[9px] uppercase tracking-[0.2em]">
                  {{ session.company || 'Confidentiel' }}
                </p>
              </div>
            </div>

            <div class="mt-auto pt-6 border-t border-slate-100/50 flex items-center justify-between relative z-10">
              <div class="flex flex-col">
                <div class="flex items-baseline gap-0.5">
                  <span class="text-2xl font-black text-slate-900 tabular-nums">{{ session.scores?.overall || 0 }}</span>
                  <span class="text-[9px] font-black text-slate-300">/10</span>
                </div>
                <span class="text-[8px] font-black text-slate-300 uppercase tracking-widest mt-0.5">Performance</span>
              </div>

              <div class="flex items-center gap-4 text-[9px] font-black text-slate-400 uppercase tracking-widest">
                <div class="flex items-center gap-1.5 group/time">
                  <ClockIcon class="w-3.5 h-3.5 text-slate-200 group-hover/time:text-[#F59E0B] transition-colors" />
                  {{ session.duration_minutes || 0 }}m
                </div>
                <ChevronRightIcon class="w-4 h-4 text-slate-200 group-hover:translate-x-1 transition-transform" />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <transition name="modal">
      <div v-if="selected" class="fixed inset-0 z-[100] flex items-center justify-center p-4 md:p-6">
        <div class="absolute inset-0 bg-slate-900/60 backdrop-blur-sm" @click="selected = null"></div>
        
        <div class="bg-white rounded-[2rem] w-full max-w-4xl max-h-[90vh] overflow-y-auto md:overflow-hidden relative z-10 shadow-2xl animate-modal-in flex flex-col md:flex-row custom-scrollbar">
          
          <!-- SIDEBAR (META & SCORES) -->
          <div class="w-full md:w-[300px] bg-slate-50/50 border-b md:border-b-0 md:border-r border-slate-100 flex flex-col p-8 md:overflow-y-auto custom-scrollbar shrink-0">
            <div class="flex items-center gap-5 md:flex-col md:text-center mb-8">
              <div class="w-16 h-16 md:w-20 md:h-20 rounded-2xl bg-white border border-slate-100 shadow-sm flex items-center justify-center md:mb-4 shrink-0">
                <component :is="getRecruiter(selected.recruiter_id).icon" :class="getRecruiter(selected.recruiter_id).color" class="w-8 h-8 md:w-10 md:h-10" />
              </div>
              <div class="flex-1">
                <h3 class="text-base font-black text-slate-900 tracking-tight">{{ getRecruiter(selected.recruiter_id).name }}</h3>
                <p class="text-[9px] font-black text-slate-400 uppercase tracking-widest mt-0.5">{{ getRecruiter(selected.recruiter_id).role }}</p>
              </div>
            </div>

            <div class="space-y-6">
              <div class="p-5 bg-white rounded-2xl border border-slate-100 shadow-sm">
                <div class="text-[8px] font-black text-slate-300 uppercase tracking-widest mb-3">Verdict</div>
                <div :class="decisionClassRaw(selected.decision)" class="w-full py-2 rounded-xl text-[9px] font-black uppercase tracking-widest text-center border">
                  {{ selected.decision }}
                </div>
              </div>

              <div class="space-y-3">
                <div class="text-[8px] font-black text-slate-300 uppercase tracking-widest px-1">Scores détaillés</div>
                <div v-for="(val, cat) in selected.scores" :key="cat" v-show="['technical', 'communication', 'soft_skills', 'overall'].includes(cat)" 
                  class="p-4 bg-white rounded-xl border border-slate-100 shadow-sm flex items-center justify-between">
                  <div class="flex flex-col">
                    <span class="text-[8px] font-black text-slate-400 uppercase tracking-widest mb-1">{{ cat === 'overall' ? 'Global' : cat }}</span>
                    <div class="w-20 h-1 bg-slate-50 rounded-full overflow-hidden">
                      <div class="h-full bg-[#F59E0B] transition-all duration-1000" :style="{ width: val * 10 + '%' }"></div>
                    </div>
                  </div>
                  <div class="text-lg font-black text-slate-900">{{ val }}<span class="text-[9px] text-slate-300">/10</span></div>
                </div>
              </div>

              <button class="w-full py-3.5 bg-gold-600 text-white rounded-xl font-black text-[9px] uppercase tracking-widest hover:bg-[#F59E0B] transition-all shadow-lg flex items-center justify-center gap-2">
                <ChatBubbleLeftRightIcon class="w-4 h-4" /> Transcription complète
              </button>
            </div>
          </div>

          <!-- MAIN CONTENT (ANALYSIS) -->
          <div class="flex-1 md:overflow-y-auto custom-scrollbar flex flex-col bg-white">
            <div class="p-8 md:p-10 space-y-10">
              <!-- Header -->
              <div class="space-y-4">
                <div class="flex flex-wrap gap-2">
                  <span class="px-2.5 py-1 bg-slate-50 text-slate-400 rounded-lg text-[8px] font-black uppercase tracking-widest flex items-center gap-1.5">
                    <CalendarIcon class="w-3 h-3" /> {{ formatDateShort(selected.created_at) }}
                  </span>
                  <span class="px-2.5 py-1 bg-slate-50 text-slate-400 rounded-lg text-[8px] font-black uppercase tracking-widest flex items-center gap-1.5">
                    <ClockIcon class="w-3 h-3" /> {{ selected.duration_minutes || 0 }} minutes
                  </span>
                </div>
                <h2 class="text-2xl md:text-3xl font-black text-slate-900 tracking-tight leading-tight">
                  {{ selected.job_title }}
                </h2>
                <div class="flex items-center gap-2 text-slate-400 font-bold text-xs">
                  <BuildingOfficeIcon class="w-4 h-4 text-[#F59E0B]/50" /> {{ selected.company || 'Confidentiel' }}
                </div>
              </div>

              <!-- Feedback Bento -->
              <div class="grid grid-cols-1 gap-6">
                <div class="p-8 bg-emerald-50/20 rounded-3xl border border-emerald-100/30">
                  <div class="flex items-center gap-3 text-emerald-600 mb-6">
                    <CheckCircleIcon class="w-5 h-5" />
                    <h4 class="text-[10px] font-black uppercase tracking-widest">Points Forts</h4>
                  </div>
                  <ul class="space-y-4">
                    <li v-for="p in selected.feedback?.points_forts" :key="p" class="flex gap-3 text-emerald-900/70 text-sm font-bold leading-snug">
                      <div class="w-1.5 h-1.5 rounded-full bg-emerald-400 mt-1.5 shrink-0"></div> {{ p }}
                    </li>
                  </ul>
                </div>

                <div class="p-8 bg-amber-50/20 rounded-3xl border border-amber-100/30">
                  <div class="flex items-center gap-3 text-amber-600 mb-6">
                    <AcademicCapIcon class="w-5 h-5" />
                    <h4 class="text-[10px] font-black uppercase tracking-widest">Axes d'amélioration</h4>
                  </div>
                  <ul class="space-y-4">
                    <li v-for="p in selected.feedback?.points_amelioration" :key="p" class="flex gap-3 text-amber-900/70 text-sm font-bold leading-snug">
                      <div class="w-1.5 h-1.5 rounded-full bg-amber-400 mt-1.5 shrink-0"></div> {{ p }}
                    </li>
                  </ul>
                </div>
              </div>

              <!-- Verdict -->
              <div class="bg-slate-50 p-8 rounded-3xl border border-slate-100 relative overflow-hidden">
                <div class="relative z-10 space-y-6">
                  <div class="flex items-center gap-3 text-[#F59E0B]">
                    <StarIcon class="w-5 h-5" />
                    <span class="text-[10px] font-black uppercase tracking-widest text-slate-400">Verdict GoldArmy AI</span>
                  </div>
                  <p class="text-xl md:text-2xl font-bold text-slate-900 leading-tight tracking-tight italic">
                    "{{ selected.feedback?.conseils || 'Performance solide.' }}"
                  </p>
                  <div class="pt-6 border-t border-slate-200/50 flex flex-col sm:flex-row sm:items-center justify-between gap-6">
                    <div class="flex items-center gap-3">
                      <div class="w-8 h-8 rounded-lg bg-gold-600 text-white flex items-center justify-center text-[8px] font-black shadow-lg shadow-slate-900/20">GA</div>
                      <span class="text-[9px] font-black text-slate-400 uppercase tracking-widest">Analyse v4.0 Pro</span>
                    </div>
                    <button class="px-6 py-3 bg-[#F59E0B] text-white rounded-xl font-black text-[9px] uppercase tracking-widest hover:bg-slate-900 transition-all shadow-xl shadow-[#F59E0B]/20">
                      Améliorer mon score
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Close -->
          <button @click="selected = null" class="absolute top-4 right-4 w-10 h-10 flex items-center justify-center bg-white border border-slate-100 rounded-xl text-slate-400 hover:text-slate-900 transition-all z-20 shadow-sm hover:rotate-90">
            <XMarkIcon class="w-5 h-5" />
          </button>
        </div>
      </div>
    </transition>

  </div>
</template>

<script setup>
import { ref, onMounted, computed, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { authFetch } from '../utils/auth'
import { 
  ArrowLeftIcon, SparklesIcon, PlusIcon, BriefcaseIcon, ChartBarIcon, 
  CheckCircleIcon, ClockIcon, BuildingOfficeIcon, CpuChipIcon, 
  VideoCameraSlashIcon, XMarkIcon, StarIcon, AcademicCapIcon,
  CalendarIcon, UserGroupIcon, ChatBubbleLeftRightIcon, ChevronRightIcon
} from '@heroicons/vue/24/outline'
import gsap from 'gsap'

const router  = useRouter()
const sessions = ref([])
const total    = ref(0)
const loading  = ref(true)
const selected = ref(null)

const RECRUITERS = {
  tech: { name: 'Sophie', role: 'CTO / Tech Lead', icon: CpuChipIcon, color: 'text-indigo-500' },
  hr: { name: 'Marc', role: 'Responsable RH', icon: UserGroupIcon, color: 'text-emerald-500' },
  ceo: { name: 'Alice', role: 'Fondatrice / CEO', icon: StarIcon, color: 'text-amber-500' }
}

const getRecruiter = (id) => RECRUITERS[id] || { name: 'IA Expert', role: 'Recruteur GoldArmy', icon: SparklesIcon, color: 'text-[#F59E0B]' }

// Calculated Stats
const avgScore = computed(() => {
  if (!sessions.value.length) return 0
  const sum = sessions.value.reduce((acc, s) => acc + (s.scores?.overall || 0), 0)
  return (sum / sessions.value.length).toFixed(1)
})

const favorableRate = computed(() => {
  if (!sessions.value.length) return 0
  const favorable = sessions.value.filter(s => s.decision === 'Favorable').length
  return Math.round((favorable / sessions.value.length) * 100)
})

const totalDuration = computed(() => {
  return sessions.value.reduce((acc, s) => acc + (s.duration_minutes || 0), 0)
})

const stats = computed(() => [
  { label: 'Entretiens', value: total.value, icon: BriefcaseIcon },
  { label: 'Score Moyen', value: avgScore.value + '/10', icon: ChartBarIcon },
  { label: 'Taux Succès', value: favorableRate.value + '%', icon: CheckCircleIcon },
  { label: 'Min. Entraînés', value: totalDuration.value, icon: ClockIcon }
])

async function fetchHistory() {
  try {
    const res = await authFetch('/api/interview/history?limit=50')
    if (!res.ok) throw new Error('Erreur réseau')
    const data = await res.json()
    sessions.value = data.sessions || []
    total.value    = data.total || 0
    
    await nextTick()
    animateCards()
  } catch (e) {
    console.error('History fetch error:', e)
  } finally {
    loading.value = false
  }
}

function animateCards() {
  gsap.from('.stagger-item', {
    y: 40,
    opacity: 0,
    duration: 1,
    stagger: 0.1,
    ease: 'power4.out',
    clearProps: 'all'
  })
  
  gsap.from('.session-bento-card', {
    y: 60,
    opacity: 0,
    duration: 1.2,
    stagger: 0.05,
    ease: 'expo.out',
    delay: 0.3,
    clearProps: 'all'
  })
}

function openDetail(session) {
  selected.value = session
}

function formatDateShort(iso) {
  if (!iso) return ''
  return new Date(iso).toLocaleDateString('fr-FR', { day: '2-digit', month: 'short' })
}

function formatDate(iso) {
  if (!iso) return ''
  return new Date(iso).toLocaleDateString('fr-FR', {
    year: 'numeric', month: 'short', day: 'numeric',
    hour: '2-digit', minute: '2-digit'
  })
}

function decisionClassRaw(d) {
  if (d === 'Favorable') return 'bg-emerald-400/10 text-emerald-500 border-emerald-500/20 shadow-[0_0_20px_rgba(16,185,129,0.1)]'
  if (d === 'Défavorable') return 'bg-rose-400/10 text-rose-500 border-rose-500/20 shadow-[0_0_20px_rgba(244,63,94,0.1)]'
  return 'bg-amber-400/10 text-amber-500 border-amber-500/20 shadow-[0_0_20px_rgba(245,158,11,0.1)]'
}

function decisionClass(d) {
  if (!d) return ''
  return d === 'Favorable' 
    ? 'bg-emerald-500 text-white shadow-lg shadow-emerald-500/20' 
    : d === 'Défavorable' 
      ? 'bg-rose-500 text-white shadow-lg shadow-rose-500/20' 
      : 'bg-amber-500 text-white shadow-lg shadow-amber-500/20'
}

function scoreColor(v) {
  if (v >= 8) return '#10b981'
  if (v >= 6) return '#f59e0b'
  return '#ef4444'
}

function scoreDisplay(scores) {
  if (!scores) return []
  const labels = { technical: 'Technique', communication: 'Communication', soft_skills: 'Soft Skills', overall: 'Global' }
  return Object.entries(scores)
    .filter(([k]) => labels[k])
    .map(([k, v]) => ({ label: labels[k], value: v }))
}

onMounted(fetchHistory)
</script>

<style scoped>
.interview-history-page {
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

@keyframes blob {
  0% { transform: translate(0px, 0px) scale(1); }
  33% { transform: translate(30px, -50px) scale(1.1); }
  66% { transform: translate(-20px, 20px) scale(0.9); }
  100% { transform: translate(0px, 0px) scale(1); }
}

.animate-blob {
  animation: blob 7s infinite;
}

.animation-delay-2000 {
  animation-delay: 2s;
}

@keyframes modalIn {
  from { opacity: 0; transform: scale(0.9) translateY(40px) rotate(-1deg); }
  to { opacity: 1; transform: scale(1) translateY(0) rotate(0deg); }
}

.animate-modal-in {
  animation: modalIn 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

.custom-scrollbar::-webkit-scrollbar {
  width: 5px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #F59E0B33;
  border-radius: 20px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: #F59E0B66;
}

.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.session-bento-card:hover {
  z-index: 20;
}

@media (max-width: 768px) {
  .interview-history-page {
    padding-bottom: 5rem;
  }
}
</style>
