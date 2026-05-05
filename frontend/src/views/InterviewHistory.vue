<template>
  <div class="interview-history-page min-h-screen relative overflow-hidden font-sans text-slate-900 bg-[#fbfbff]">
    <!-- MOVING BACKGROUND BLOBS (Dribbble/Framer style) -->
    <div class="absolute inset-0 pointer-events-none overflow-hidden">
      <div class="absolute -top-[10%] -left-[10%] w-[60%] h-[60%] bg-[#E85D3E]/10 rounded-full blur-[120px] animate-blob"></div>
      <div class="absolute -bottom-[10%] -right-[10%] w-[50%] h-[50%] bg-[#6366f1]/10 rounded-full blur-[120px] animate-blob animation-delay-2000"></div>
    </div>

    <div class="max-w-7xl mx-auto px-6 py-12 md:py-20 relative z-10">
      <!-- ARTISTIC HEADER -->
      <div class="flex flex-col items-center text-center space-y-6 mb-20">
        <button @click="router.push('/interview')" class="group flex items-center gap-3 px-6 py-3 bg-white/50 backdrop-blur-xl border border-white/80 rounded-full text-slate-500 hover:text-[#E85D3E] transition-all hover:px-8 shadow-sm">
          <ArrowLeftIcon class="w-4 h-4 transition-transform group-hover:-translate-x-1" />
          <span class="text-xs font-black uppercase tracking-widest">Retour au simulateur</span>
        </button>
        
        <div class="space-y-4">
          <h1 class="text-5xl md:text-7xl font-black tracking-tighter text-slate-900 leading-[0.9]">
            Votre <span class="text-transparent bg-clip-text bg-gradient-to-br from-[#E85D3E] to-[#FF8C6B]">Progression</span>
          </h1>
          <p class="text-slate-400 font-medium text-lg md:text-xl max-w-2xl mx-auto">
            Retrouvez chaque entretien, analysez vos faiblesses et dominez le marché du travail.
          </p>
        </div>
      </div>

      <!-- FLOATING STATS GRID -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-20 stagger-item">
        <div v-for="stat in stats" :key="stat.label" class="bg-white/40 backdrop-blur-2xl border border-white/60 p-8 rounded-[2.5rem] shadow-[0_20px_50px_rgba(0,0,0,0.03)] hover:shadow-xl transition-all hover:-translate-y-1">
          <div class="w-12 h-12 rounded-2xl bg-white flex items-center justify-center mb-6 shadow-sm text-[#E85D3E]">
            <component :is="stat.icon" class="w-6 h-6" />
          </div>
          <div class="text-3xl font-black text-slate-900 mb-1 tracking-tight">{{ stat.value }}</div>
          <div class="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em]">{{ stat.label }}</div>
        </div>
      </div>

      <!-- CONTENT -->
      <div v-if="loading" class="flex flex-col items-center justify-center py-20 gap-6">
        <div class="w-16 h-16 border-4 border-slate-100 border-t-[#E85D3E] rounded-full animate-spin"></div>
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
        <router-link to="/interview" class="inline-flex px-10 py-5 bg-[#E85D3E] text-white font-black text-xs uppercase tracking-[0.2em] rounded-2xl transition-all shadow-2xl shadow-[#E85D3E]/30 hover:scale-105 active:scale-95">
          Démarrer l'entraînement
        </router-link>
      </div>

      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        <div v-for="session in sessions" :key="session.session_id" 
          @click="openDetail(session)"
          class="session-bento-card group relative">
          
          <div class="absolute inset-0 bg-gradient-to-br from-[#E85D3E]/5 to-[#6366f1]/5 opacity-0 group-hover:opacity-100 transition-opacity rounded-[3rem] -z-10 blur-xl"></div>
          
          <div class="bg-white/60 backdrop-blur-2xl border border-white/80 rounded-[3rem] p-10 h-full shadow-[0_20px_50px_rgba(0,0,0,0.02)] group-hover:shadow-[0_40px_80px_rgba(0,0,0,0.06)] group-hover:-translate-y-2 transition-all duration-500 cursor-pointer flex flex-col">
            
            <div class="flex justify-between items-start mb-8">
              <div class="w-14 h-14 rounded-2xl bg-white shadow-sm flex items-center justify-center text-3xl transition-transform group-hover:scale-110 group-hover:rotate-6">
                {{ getRecruiter(session.recruiter_id).avatar }}
              </div>
              <div :class="decisionClassRaw(session.decision)" class="px-4 py-2 rounded-full text-[9px] font-black uppercase tracking-widest backdrop-blur-xl border border-white/50 shadow-sm">
                {{ session.decision }}
              </div>
            </div>

            <div class="space-y-2 mb-8">
              <h3 class="text-2xl font-black text-slate-900 tracking-tighter leading-tight group-hover:text-[#E85D3E] transition-colors line-clamp-2">
                {{ session.job_title }}
              </h3>
              <p class="text-slate-400 font-bold text-[10px] uppercase tracking-[0.2em] flex items-center gap-2">
                <BuildingOfficeIcon class="w-4 h-4 text-[#E85D3E]/50" /> {{ session.company || 'Confidentiel' }}
              </p>
            </div>

            <div class="mt-auto space-y-6 pt-6 border-t border-slate-100/50">
              <div class="flex justify-between items-center">
                <div class="flex flex-col">
                  <span class="text-[2rem] font-black text-slate-900 leading-none tabular-nums">{{ session.scores?.overall || 0 }}</span>
                  <span class="text-[10px] font-black text-slate-300 uppercase tracking-widest mt-1">Score Global / 10</span>
                </div>
                <div class="flex -space-x-2">
                   <div v-for="i in 3" :key="i" class="w-8 h-8 rounded-full border-2 border-white bg-slate-50 flex items-center justify-center text-[10px]">
                      {{ i === 1 ? '🎨' : i === 2 ? '⚡' : '🧠' }}
                   </div>
                </div>
              </div>

              <div class="flex items-center justify-between text-[10px] font-black text-slate-400 uppercase tracking-widest">
                <div class="flex items-center gap-2">
                  <CalendarIcon class="w-4 h-4" /> {{ formatDateShort(session.created_at) }}
                </div>
                <div class="flex items-center gap-2">
                  <ClockIcon class="w-4 h-4" /> {{ session.duration_minutes || 0 }}m
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- DETAIL MODAL (Inspired by Scorecard) -->
    <transition name="modal">
      <div v-if="selected" class="fixed inset-0 z-[100] flex items-center justify-center p-4 md:p-10">
        <div class="absolute inset-0 bg-slate-900/60 backdrop-blur-sm" @click="selected = null"></div>
          <div class="bg-white border border-slate-100 rounded-[3rem] w-full max-w-4xl max-h-[90vh] overflow-y-auto relative z-10 shadow-2xl animate-fade-in-up custom-scrollbar flex flex-col">
          <!-- Close -->
          <button @click="selected = null" class="absolute top-6 right-6 w-12 h-12 flex items-center justify-center bg-slate-50/50 backdrop-blur-md rounded-2xl text-slate-400 hover:text-slate-900 transition-all z-20">
            <XMarkIcon class="w-6 h-6" />
          </button>

          <!-- Top Banner Decor -->
          <div class="h-32 bg-gradient-to-r from-slate-50 to-white relative overflow-hidden shrink-0">
            <div class="absolute inset-0 opacity-[0.03] pointer-events-none" style="background-image: radial-gradient(#E85D3E 1px, transparent 1px); background-size: 20px 20px;"></div>
            <div class="absolute bottom-0 left-12 transform translate-y-1/2">
                <div class="w-24 h-24 rounded-[2rem] bg-white border-4 border-[#F9FAFB] shadow-xl flex items-center justify-center text-4xl">
                    {{ getRecruiter(selected.recruiter_id).avatar }}
                </div>
            </div>
          </div>

          <!-- Header -->
          <div class="px-12 pt-16 pb-8 border-b border-slate-50 shrink-0">
            <div class="flex flex-col md:flex-row md:items-end justify-between gap-6 mb-10">
              <div>
                <div class="flex items-center gap-3 mb-2">
                    <span class="px-3 py-1 bg-slate-100 text-slate-500 rounded-full text-[9px] font-black uppercase tracking-widest flex items-center gap-1.5">
                        <CalendarIcon class="w-3 h-3" /> {{ formatDate(selected.created_at) }}
                    </span>
                    <span class="px-3 py-1 bg-slate-100 text-slate-500 rounded-full text-[9px] font-black uppercase tracking-widest flex items-center gap-1.5">
                        <ClockIcon class="w-3 h-3" /> {{ selected.duration_minutes || 0 }} min
                    </span>
                    <span class="px-3 py-1 bg-[#E85D3E]/10 text-[#E85D3E] rounded-full text-[9px] font-black uppercase tracking-widest flex items-center gap-1.5">
                        <UserGroupIcon class="w-3 h-3" /> {{ selected.interview_type === 'technical' ? 'Technique' : 'RH' }}
                    </span>
                </div>
                <h2 class="text-4xl font-black text-slate-900 tracking-tight">{{ selected.job_title }}</h2>
                <p class="text-slate-400 font-bold text-xs uppercase tracking-widest mt-1.5 flex items-center gap-2">
                    <BuildingOfficeIcon class="w-4 h-4 text-[#E85D3E]" /> {{ selected.company || 'Entreprise Confidentielle' }}
                </p>
              </div>

              <div class="flex flex-col items-end gap-3">
                <div :class="decisionClass(selected.decision)" class="px-8 py-3 rounded-2xl text-[10px] font-black uppercase tracking-[0.2em] shadow-sm">
                    {{ selected.decision }}
                </div>
                <button class="text-[10px] font-black text-slate-300 uppercase tracking-widest hover:text-[#E85D3E] transition-colors flex items-center gap-2">
                    <ChatBubbleLeftRightIcon class="w-4 h-4" /> Voir la transcription complète
                </button>
              </div>
            </div>

            <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div v-for="(val, cat) in selected.scores" :key="cat" v-show="['technical', 'communication', 'soft_skills', 'overall'].includes(cat)" class="p-6 bg-white border border-slate-100 rounded-[2.5rem] text-center shadow-sm relative overflow-hidden group">
                <div class="absolute inset-0 bg-gradient-to-b from-transparent to-slate-50/50 opacity-0 group-hover:opacity-100 transition-opacity"></div>
                <span class="block text-[8px] font-black text-slate-400 uppercase tracking-[0.2em] mb-4 relative z-10">
                  {{ cat === 'technical' ? 'Technique' : cat === 'communication' ? 'Communication' : cat === 'soft_skills' ? 'Soft Skills' : 'Global' }}
                </span>
                <div class="relative flex items-center justify-center z-10">
                  <svg class="w-20 h-20 transform -rotate-90">
                    <circle cx="40" cy="40" r="34" stroke="currentColor" stroke-width="8" fill="transparent" class="text-slate-50" />
                    <circle cx="40" cy="40" r="34" stroke="currentColor" stroke-width="8" fill="transparent" :stroke-dasharray="2 * Math.PI * 34" :stroke-dashoffset="2 * Math.PI * 34 * (1 - val / 10)" class="text-[#E85D3E] transition-all duration-1000" stroke-linecap="round" />
                  </svg>
                  <span class="absolute text-xl font-black text-slate-900">{{ val }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Content -->
          <div class="p-12 space-y-12 overflow-y-auto">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-10">
              <!-- Points Forts -->
              <div class="p-10 bg-emerald-50/30 rounded-[3rem] border border-emerald-100/50 relative overflow-hidden">
                <div class="absolute -top-10 -right-10 w-40 h-40 bg-emerald-100/20 rounded-full blur-3xl"></div>
                <h3 class="text-sm font-black text-emerald-900 uppercase tracking-widest mb-8 flex items-center gap-4 relative z-10">
                  <div class="w-10 h-10 rounded-2xl bg-emerald-100 flex items-center justify-center shadow-sm">
                    <CheckCircleIcon class="w-5 h-5 text-emerald-600" />
                  </div>
                  Points Forts
                </h3>
                <ul class="space-y-5 relative z-10">
                  <li v-for="point in selected.feedback?.points_forts" :key="point" class="flex gap-4 text-emerald-900/70 text-sm font-bold leading-relaxed">
                    <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 mt-2 shrink-0"></span> {{ point }}
                  </li>
                </ul>
              </div>

              <!-- Points à améliorer -->
              <div class="p-10 bg-amber-50/30 rounded-[3rem] border border-amber-100/50 relative overflow-hidden">
                <div class="absolute -top-10 -right-10 w-40 h-40 bg-amber-100/20 rounded-full blur-3xl"></div>
                <h3 class="text-sm font-black text-amber-900 uppercase tracking-widest mb-8 flex items-center gap-4 relative z-10">
                  <div class="w-10 h-10 rounded-2xl bg-amber-100 flex items-center justify-center shadow-sm">
                    <AcademicCapIcon class="w-5 h-5 text-amber-600" />
                  </div>
                  Axes d'amélioration
                </h3>
                <ul class="space-y-5 relative z-10">
                  <li v-for="point in selected.feedback?.points_amelioration" :key="point" class="flex gap-4 text-amber-900/70 text-sm font-bold leading-relaxed">
                    <span class="w-1.5 h-1.5 rounded-full bg-amber-400 mt-2 shrink-0"></span> {{ point }}
                  </li>
                </ul>
              </div>
            </div>

            <!-- Recruiter Opinion Card -->
            <div class="bg-slate-900 p-12 rounded-[3.5rem] text-white relative overflow-hidden shadow-2xl">
              <div class="absolute top-0 right-0 p-12 opacity-[0.05]">
                <SparklesIcon class="w-48 h-48 text-white" />
              </div>
              
              <div class="flex items-center justify-between relative z-10 mb-10">
                <div class="flex items-center gap-5">
                  <div class="w-14 h-14 rounded-2xl bg-white/10 backdrop-blur-md flex items-center justify-center border border-white/5 shadow-xl">
                    <StarIcon class="w-7 h-7 text-[#E85D3E]" />
                  </div>
                  <div>
                    <h3 class="text-2xl font-black tracking-tight">Verdict de {{ getRecruiter(selected.recruiter_id).name }}</h3>
                    <p class="text-slate-500 font-bold text-[10px] uppercase tracking-widest">{{ getRecruiter(selected.recruiter_id).role }}</p>
                  </div>
                </div>
                <div class="w-16 h-16 rounded-3xl bg-white/5 border border-white/10 flex items-center justify-center text-3xl shadow-inner">
                    {{ getRecruiter(selected.recruiter_id).avatar }}
                </div>
              </div>
              
              <div class="relative z-10 mb-10">
                <div class="absolute -left-6 top-0 text-6xl text-white/10 font-serif">"</div>
                <p class="text-slate-300 text-xl font-medium leading-relaxed italic px-2">
                  {{ selected.feedback?.conseils || 'Aucun conseil spécifique pour cette session.' }}
                </p>
              </div>
              
              <div class="pt-8 border-t border-white/5 flex items-center justify-between relative z-10">
                <div class="flex items-center gap-4">
                    <div class="w-12 h-12 rounded-2xl bg-[#E85D3E] flex items-center justify-center font-black text-sm shadow-lg shadow-[#E85D3E]/20">GA</div>
                    <div>
                    <p class="text-[10px] font-black uppercase tracking-widest text-white">GoldArmy Intelligence</p>
                    <p class="text-[8px] font-bold text-slate-500 uppercase tracking-[0.2em]">Système d'Analyse 3.1 Pro</p>
                    </div>
                </div>
                
                <div class="flex gap-2">
                    <div class="w-1.5 h-1.5 rounded-full bg-[#E85D3E] animate-pulse"></div>
                    <div class="w-1.5 h-1.5 rounded-full bg-[#E85D3E]/50"></div>
                    <div class="w-1.5 h-1.5 rounded-full bg-[#E85D3E]/20"></div>
                </div>
              </div>
            </div>
          </div>
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
  tech: { name: 'Sophie', role: 'CTO / Tech Lead', avatar: '👩‍💻' },
  hr: { name: 'Marc', role: 'Responsable RH', avatar: '👨‍💼' },
  ceo: { name: 'Alice', role: 'Fondatrice / CEO', avatar: '👩‍💼' }
}

const getRecruiter = (id) => RECRUITERS[id] || { name: 'IA Expert', role: 'Recruteur GoldArmy', avatar: '🤖' }

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

.modal-enter-active, .modal-leave-active {
  transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}
.modal-enter-from, .modal-leave-to {
  opacity: 0;
  transform: scale(0.95);
}

.custom-scrollbar::-webkit-scrollbar {
  width: 5px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #E85D3E33;
  border-radius: 20px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: #E85D3E66;
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
