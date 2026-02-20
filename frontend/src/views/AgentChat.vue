<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { PaperAirplaneIcon, ArrowPathIcon } from '@heroicons/vue/24/solid'

const route = useRoute()
const inputQuery = ref('')
const isLoading = ref(false)
const messages = ref([
  {
    id: 1,
    role: 'assistant',
    content: "Bonjour Yves ! Je suis GoldArmy, ton Co-Pilote de Carrière. 🪖\n\nJe suis connecté et prêt. Que veux-tu faire aujourd'hui ? Je peux auditer ton CV, chercher des offres de stage, ou te préparer à un entretien technique.",
    timestamp: new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})
  }
])

onMounted(() => {
  if (route.query.prompt) {
    inputQuery.value = route.query.prompt
    sendMessage()
  }
})

const sendMessage = async () => {
  if (!inputQuery.value.trim()) return
  
  const userMsg = inputQuery.value
  inputQuery.value = ''
  
  messages.value.push({
    id: Date.now(),
    role: 'user',
    content: userMsg,
    timestamp: new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})
  })
  
  isLoading.value = true
  
  try {
    const res = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMsg, nb_results: 5 })
    })
    const data = await res.json()
    
    // Simulate real typing feel or just append
    messages.value.push({
      id: Date.now() + 1,
      role: 'assistant',
      content: JSON.stringify(data.data, null, 2), // Temporary raw dump until we format it securely
      timestamp: new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})
    })
    
  } catch (e) {
    messages.value.push({
      id: Date.now() + 1,
      role: 'assistant',
      content: "⚠️ Erreur de connexion avec le quartier général (Backend indisponible).",
      timestamp: new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}),
      error: true
    })
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div class="h-full flex flex-col p-4 md:p-6 lg:p-8 max-w-5xl mx-auto w-full animate-fade-in">
    <!-- Header -->
    <div class="flex items-center justify-between mb-6 pb-4 border-b border-slate-700/50">
      <div>
        <h2 class="text-2xl font-bold flex items-center gap-3">
          <span class="p-2 bg-amber-500/10 text-amber-500 rounded-xl border border-amber-500/20">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"></path></svg>
          </span>
          Agent Principal
        </h2>
        <p class="text-slate-400 mt-1 text-sm">Orchestration, Recherche et Analyse CV</p>
      </div>
    </div>

    <!-- Chat Area -->
    <div class="flex-1 overflow-y-auto space-y-6 pr-4 pb-4 scroll-smooth">
      <div 
        v-for="msg in messages" 
        :key="msg.id"
        :class="['flex w-full', msg.role === 'user' ? 'justify-end' : 'justify-start']"
      >
        <div 
          :class="[
            'max-w-[85%] md:max-w-[75%] rounded-2xl p-4 flex flex-col',
            msg.role === 'user' 
              ? 'bg-amber-600 text-white rounded-br-none shadow-amber-900/20' 
              : msg.error 
                ? 'bg-rose-500/10 border border-rose-500/30 text-rose-200 rounded-bl-none'
                : 'bg-slate-800 border border-slate-700 text-slate-200 rounded-bl-none shadow-black/20'
          ]"
          class="shadow-lg relative group"
        >
          <!-- User Profile Icon -->
          <div v-if="msg.role === 'assistant'" class="absolute -left-12 top-0 w-8 h-8 rounded-full bg-slate-800 border border-slate-600 flex items-center justify-center text-lg shadow-sm">
            🪖
          </div>
          
          <div class="whitespace-pre-wrap font-sans text-[15px] leading-relaxed" v-if="msg.role === 'user' || msg.error">{{ msg.content }}</div>
          
          <!-- Mocking formatted agent response for now -->
          <div v-if="msg.role === 'assistant' && !msg.error" class="prose prose-invert prose-amber max-w-none text-sm">
            <pre class="bg-slate-900 overflow-x-auto p-4 rounded-xl border border-slate-700 mt-2 font-mono text-xs text-emerald-400">{{ msg.content }}</pre>
          </div>
          
          <span class="text-[10px] mt-2 opacity-50 self-end">{{ msg.timestamp }}</span>
        </div>
      </div>
      
      <!-- Typing Indicator -->
      <div v-if="isLoading" class="flex w-full justify-start">
         <div class="max-w-[85%] rounded-2xl p-4 bg-slate-800 border border-slate-700 text-slate-200 rounded-bl-none shadow-lg shadow-black/20 relative">
            <div class="absolute -left-12 top-0 w-8 h-8 rounded-full bg-slate-800 border border-slate-600 flex items-center justify-center text-lg shadow-sm">🪖</div>
            <div class="flex gap-1.5 items-center py-2 h-6">
              <div class="w-2 h-2 rounded-full bg-amber-500 animate-bounce" style="animation-delay: 0ms"></div>
              <div class="w-2 h-2 rounded-full bg-amber-500 animate-bounce" style="animation-delay: 150ms"></div>
              <div class="w-2 h-2 rounded-full bg-amber-500 animate-bounce" style="animation-delay: 300ms"></div>
            </div>
         </div>
      </div>
    </div>

    <!-- Input Area -->
    <div class="mt-4 pt-4 border-t border-slate-700/50 relative">
      <div class="absolute -top-10 left-0 right-0 h-10 bg-gradient-to-t from-slate-900 to-transparent pointer-events-none"></div>
      <div class="relative flex items-end gap-2 bg-slate-800 rounded-2xl border border-slate-600 focus-within:border-amber-500 p-2 shadow-inner transition-colors">
         <textarea 
            v-model="inputQuery"
            @keydown.enter.exact.prevent="sendMessage"
            class="w-full bg-transparent border-none focus:ring-0 text-slate-200 resize-none h-14 max-h-32 p-2 placeholder-slate-500 scrollbar-hide"
            placeholder="Écris ton message à l'Agent..."
         ></textarea>
         <button 
            @click="sendMessage"
            :disabled="!inputQuery.trim() || isLoading"
            class="p-3 bg-amber-500 hover:bg-amber-400 disabled:bg-slate-700 disabled:text-slate-500 text-slate-900 rounded-xl transition-colors shrink-0 mb-1"
         >
            <PaperAirplaneIcon v-if="!isLoading" class="w-5 h-5" />
            <ArrowPathIcon v-else class="w-5 h-5 animate-spin" />
         </button>
      </div>
      <p class="text-center text-xs text-slate-500 mt-2">L'IA peut faire des erreurs. Vérifiez les informations importantes.</p>
    </div>
  </div>
</template>

<style scoped>
.scrollbar-hide::-webkit-scrollbar {
  display: none;
}
.scrollbar-hide {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
</style>
