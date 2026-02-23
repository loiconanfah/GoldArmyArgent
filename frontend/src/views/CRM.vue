<script setup>
import { authFetch } from '../utils/auth'

import { ref, onMounted } from 'vue'
import { 
  ChartBarIcon, 
  EnvelopeIcon, 
  ArrowPathIcon,
  ExclamationCircleIcon,
  LinkIcon
} from '@heroicons/vue/24/outline'

const columns = [
  { id: 'TO_APPLY', title: 'À Postuler', icon: EnvelopeIcon, color: 'text-amber-400', bg: 'bg-amber-400/10' },
  { id: 'APPLIED', title: 'Candidatures Envoyées', icon: ChartBarIcon, color: 'text-blue-400', bg: 'bg-blue-400/10' },
  { id: 'FOLLOW_UP', title: 'Relance Requise', icon: ExclamationCircleIcon, color: 'text-rose-400', bg: 'bg-rose-400/10' },
  { id: 'INTERVIEW', title: 'Entretiens', icon: ArrowPathIcon, color: 'text-emerald-400', bg: 'bg-emerald-400/10' }
]

const crmCards = ref({
  'TO_APPLY': [],
  'APPLIED': [],
  'FOLLOW_UP': [],
  'INTERVIEW': []
})

const isLoading = ref(true)
const draggedItem = ref(null)

const fetchCrmData = async () => {
    isLoading.value = true
    try {
        const res = await authFetch('http://localhost:8000/api/crm/applications')
        const json = await res.json()
        const rawData = json.data || []
        
        const grouped = { 'TO_APPLY': [], 'APPLIED': [], 'FOLLOW_UP': [], 'INTERVIEW': [] }
        rawData.forEach(item => {
            if (grouped[item.status]) {
                grouped[item.status].push(item)
            }
        })
        crmCards.value = grouped
    } catch(e) {
        console.error("Failed to fetch CRM data", e)
    } finally {
        isLoading.value = false
    }
}

const handleDragStart = (e, card, sourceColumn) => {
    draggedItem.value = { card, sourceColumn }
    // Pour Firefox (nécessaire)
    if (e.dataTransfer) {
       e.dataTransfer.effectAllowed = 'move'
       e.dataTransfer.setData('text/plain', card.id)
    }
}

const handleDrop = async (e, targetColumnId) => {
    e.preventDefault()
    if (!draggedItem.value) return
    
    const { card, sourceColumn } = draggedItem.value
    
    if (sourceColumn === targetColumnId) {
        draggedItem.value = null
        return // Pas de changement
    }
    
    // Optimistic UI Update
    crmCards.value[sourceColumn] = crmCards.value[sourceColumn].filter(c => c.id !== card.id)
    card.status = targetColumnId
    crmCards.value[targetColumnId].push(card)
    
    draggedItem.value = null
    
    // Server Sync
    try {
        await authFetch(`http://localhost:8000/api/crm/applications/${card.id}/status`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ status: targetColumnId })
        })
    } catch(err) {
        console.error("Erreur serveur lors du Drag & Drop :", err)
        // Rollback (Optionnel ou re-fetch)
        fetchCrmData()
    }
}

const handleDragOver = (e) => {
   e.preventDefault() // Autoriser le drop
}

const formatDate = (isoString) => {
    if(!isoString) return ''
    const d = new Date(isoString)
    return `${d.getDate().toString().padStart(2, '0')}/${(d.getMonth()+1).toString().padStart(2, '0')}/${d.getFullYear()}`
}

onMounted(() => {
    fetchCrmData()
})
</script>

<template>
  <div class="px-4 md:px-10 py-8 max-w-[1600px] mx-auto w-full h-[calc(100vh-theme(spacing.20))] flex flex-col animate-fade-in-up">
    
    <!-- Header -->
    <div class="flex flex-col md:flex-row md:items-end justify-between gap-4 border-b border-surface-800 pb-6 mb-6 shrink-0">
       <div>
         <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-gold-400/10 border border-gold-400/20 text-gold-400 text-xs font-bold tracking-wider uppercase mb-3">
             Pipelines Actifs
         </div>
         <h1 class="text-3xl md:text-4xl font-display font-black text-white tracking-tight flex items-center gap-3">
           Central 
           <span class="text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-cyan-500">Candidatures</span>
         </h1>
         <p class="text-slate-400 mt-2 font-medium">Glissez-déposez vos opportunités pour suivre leur avancement en temps réel.</p>
       </div>
       <button @click="fetchCrmData" class="flex items-center gap-2 text-sm font-bold bg-surface-800 hover:bg-surface-700 text-slate-300 px-4 py-2 rounded-xl border border-surface-700 transition-colors">
           <ArrowPathIcon class="w-4 h-4" :class="{'animate-spin': isLoading}" />
           Actualiser
       </button>
    </div>

    <!-- Kanban Board -->
    <div class="flex-1 overflow-x-auto custom-scrollbar-horizontal pb-4">
      <div class="flex gap-6 min-w-max h-full">
         
         <!-- Column -->
         <div 
           v-for="col in columns" 
           :key="col.id" 
           class="w-[340px] flex flex-col bg-surface-900 border border-surface-800 rounded-3xl p-5 shrink-0"
           @dragover="handleDragOver"
           @drop="handleDrop($event, col.id)"
         >
            <!-- Column Header -->
            <div class="flex items-center justify-between mb-5 px-1 border-b border-surface-800 pb-3">
               <h3 class="flex items-center gap-2 font-bold text-white text-lg tracking-tight">
                 <div :class="['p-1.5 rounded-lg border border-white/5', col.bg]">
                    <component :is="col.icon" :class="['w-5 h-5', col.color]" />
                 </div>
                 {{ col.title }}
               </h3>
               <span class="text-xs font-black bg-surface-800 text-slate-400 px-2.5 py-1 rounded-full border border-surface-700">
                 {{ crmCards[col.id]?.length || 0 }}
               </span>
            </div>
            
            <!-- Cards Container -->
            <div class="flex-1 space-y-4 overflow-y-auto pr-1 custom-scrollbar">
               <div 
                 v-for="card in crmCards[col.id]" 
                 :key="card.id"
                 draggable="true"
                 @dragstart="handleDragStart($event, card, col.id)"
                 class="bg-surface-950 border border-surface-800 p-5 rounded-2xl shadow-sm hover:border-surface-600 focus:ring-2 focus:ring-gold-500 hover:shadow-lg transition-all cursor-grab active:cursor-grabbing group relative"
               >
                  <!-- Drag border indicator -->
                  <div :class="['absolute top-0 left-0 w-1.5 h-full rounded-l-2xl opacity-0 group-hover:opacity-100 transition-opacity', col.bg.replace('/10', '')]"></div>
                  
                  <!-- Match Score (Placeholder/Mock) or URL Link -->
                  <div class="flex justify-between items-start mb-2">
                     <span class="text-[10px] font-black uppercase tracking-wider text-slate-500 bg-surface-800 px-2 py-0.5 rounded border border-surface-700">
                         {{ formatDate(card.created_at) }}
                     </span>
                     <a v-if="card.url" :href="card.url" target="_blank" title="Voir l'offre" class="text-slate-500 hover:text-gold-400 transition-colors p-1 bg-surface-800 hover:bg-surface-700 rounded-lg">
                        <LinkIcon class="w-4 h-4" />
                     </a>
                  </div>
                  
                  <h4 class="font-bold text-white text-base mb-1 group-hover:text-gold-400 transition-colors" :title="card.job_title">{{ card.job_title }}</h4>
                  <p class="text-slate-400 text-sm font-medium flex items-center gap-1.5 mb-3">
                     <span class="w-4 h-4 rounded bg-gradient-to-br from-surface-700 to-surface-800 flex items-center justify-center text-[9px] text-white border border-surface-600">{{ card.company_name.charAt(0) }}</span>
                     {{ card.company_name }}
                  </p>
                  
                  <div v-if="card.notes" class="text-xs text-slate-500 line-clamp-2 bg-surface-900 border border-surface-800 p-2 rounded-lg mb-3">
                      {{ card.notes }}
                  </div>
                  
                  <!-- Bottom Actions / Tags based on Column -->
                  <div class="pt-3 border-t border-surface-800 flex items-center justify-between">
                     <button v-if="col.id === 'TO_APPLY'" class="text-[10px] font-bold bg-gold-400/10 text-gold-400 hover:bg-gold-500 hover:text-surface-950 transition-colors px-3 py-1.5 rounded-lg border border-gold-400/20 w-full text-center">
                       Adapter CV IA
                     </button>
                     <button v-else-if="col.id === 'FOLLOW_UP'" class="text-[10px] font-bold bg-rose-500/10 text-rose-400 hover:bg-rose-500 hover:text-white transition-colors px-3 py-1.5 rounded-lg border border-rose-500/20 w-full text-center flex items-center justify-center gap-1">
                       <ExclamationCircleIcon class="w-3 h-3" /> Relancer
                     </button>
                     <div v-else class="text-[10px] font-bold text-slate-500 w-full text-center py-1.5">
                         {{ col.id === 'APPLIED' ? 'En attente de retour' : 'Processus Actif' }}
                     </div>
                  </div>
               </div>
               
               <div v-if="!crmCards[col.id] || crmCards[col.id].length === 0" class="h-32 border-2 border-dashed border-surface-800 bg-surface-900/50 rounded-2xl flex flex-col items-center justify-center text-slate-600 text-sm gap-2">
                 <ArrowPathIcon class="w-5 h-5 opacity-50" />
                 Glisser une carte ici
               </div>
            </div>
         </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.custom-scrollbar::-webkit-scrollbar { width: 6px; }
.custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: #334155; border-radius: 6px; }
.custom-scrollbar::-webkit-scrollbar-thumb:hover { background: #475569; }

.custom-scrollbar-horizontal::-webkit-scrollbar { height: 8px; }
.custom-scrollbar-horizontal::-webkit-scrollbar-track { background: transparent; }
.custom-scrollbar-horizontal::-webkit-scrollbar-thumb { background: #334155; border-radius: 8px; }
.custom-scrollbar-horizontal::-webkit-scrollbar-thumb:hover { background: #475569; }
</style>
