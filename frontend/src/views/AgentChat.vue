<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { PaperAirplaneIcon, ArrowPathIcon, DocumentTextIcon, CheckIcon } from '@heroicons/vue/24/solid'

const route = useRoute()
const inputQuery = ref('')
const cvText = ref('')
const isUploading = ref(false)
const isLoading = ref(false)
const messages = ref([
  {
    id: 1,
    role: 'assistant',
    content: "Bonjour Yves ! Je suis GoldArmy, ton Co-Pilote de Carrière. 🪖\n\nJe suis connecté et prêt. Tu peux coller ton CV complet ci-dessous pour que je l'audite ou que je génère ton Web Portfolio personnalisé.",
    timestamp: new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})
  }
])

const chatContainer = ref(null)

const scrollToBottom = async () => {
    await nextTick()
    if (chatContainer.value) {
        chatContainer.value.scrollTop = chatContainer.value.scrollHeight
    }
}

onMounted(() => {
  if (route.query.prompt) {
    inputQuery.value = route.query.prompt
    sendMessage()
  }
})

const sendMessage = async () => {
  if (!inputQuery.value.trim() && !cvText.value.trim()) return
  
  const userMsg = inputQuery.value
  inputQuery.value = ''
  
  if (userMsg) {
      messages.value.push({
        id: Date.now(),
        role: 'user',
        content: userMsg,
        timestamp: new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})
      })
  }

  if (cvText.value) {
       messages.value.push({
          id: Date.now() + 1,
          role: 'user',
          content: "[CV Chargé en Contexte]\n" + cvText.value.substring(0, 100) + "...",
          timestamp: new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})
      })
  }
  
  scrollToBottom()
  isLoading.value = true
  
  try {
    const res = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMsg, cv_text: cvText.value, nb_results: 5 })
    })
    const data = await res.json()
    
    // Clear CV after sending to avoid re-sending it constantly unless needed
    // cvText.value = '' 
    
    messages.value.push({
      id: Date.now() + 2,
      role: 'assistant',
      // If it's HTML, we'll mark it
      is_html: data.data.type === 'portfolio_html',
      content: data.data.content,
      timestamp: new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})
    })
    
  } catch (e) {
    messages.value.push({
      id: Date.now() + 2,
      role: 'assistant',
      content: "⚠️ Erreur de connexion avec le quartier général (Backend indisponible).",
      timestamp: new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}),
      error: true
    })
  } finally {
    isLoading.value = false
    scrollToBottom()
  }
}

const downloadHtml = (htmlContent) => {
    const blob = new Blob([htmlContent], { type: 'text/html' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'portfolio.html'
    a.click()
    URL.revokeObjectURL(url)
}
</script>

<template>
  <div class="h-full flex flex-col p-4 md:p-8 max-w-4xl mx-auto w-full relative animate-fade-in-up">
    <!-- Header Minimal -->
    <div class="flex items-center justify-between mb-8">
      <div>
        <h2 class="text-2xl font-display font-black text-white tracking-tight">Agent GoldArmy</h2>
        <p class="text-slate-400 mt-1 text-sm font-medium">Orchestration, Analyse CV & Génération Web</p>
      </div>
      
      <!-- Context Toggle Button -->
      <button 
        @click="isUploading = !isUploading" 
        :class="cvText ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30' : 'bg-surface-800 text-slate-300 hover:text-white border-surface-700 hover:border-surface-600'" 
        class="px-4 py-2 rounded-xl border flex items-center gap-2 transition-all shadow-sm text-sm font-bold"
      >
          <DocumentTextIcon class="w-4 h-4" />
          <span class="hidden sm:inline">{{ cvText ? 'Contexte Injecté' : 'Ajouter Contexte (CV)' }}</span>
          <CheckIcon v-if="cvText" class="w-4 h-4 ml-1" />
      </button>
    </div>
    
    <!-- Context Panel (Animated) -->
    <transition
        enter-active-class="transition duration-300 ease-out origin-top"
        enter-from-class="transform scale-y-95 opacity-0 max-h-0"
        enter-to-class="transform scale-y-100 opacity-100 max-h-[400px]"
        leave-active-class="transition duration-200 ease-in origin-top"
        leave-from-class="transform scale-y-100 opacity-100 max-h-[400px]"
        leave-to-class="transform scale-y-95 opacity-0 max-h-0"
    >
        <div v-if="isUploading" class="mb-6 bg-surface-900 border border-surface-800 p-4 rounded-2xl shadow-sm relative z-10">
            <div class="flex justify-between items-center mb-3">
                <h3 class="text-white font-bold text-sm tracking-wide flex items-center gap-2">
                    <span class="w-2 h-2 rounded-full bg-emerald-400"></span> 
                    Source d'Information
                </h3>
                <button @click="isUploading = false" class="text-slate-500 hover:text-white text-xs font-bold uppercase tracking-wider">Fermer</button>
            </div>
            <textarea 
                v-model="cvText" 
                class="w-full h-32 bg-surface-950/50 border border-surface-700 rounded-xl p-4 text-slate-200 focus:ring-1 focus:ring-gold-500/50 focus:border-gold-500/50 text-sm placeholder-slate-600 font-mono transition-colors" 
                placeholder="Collez ici le texte brut de votre CV..."
            ></textarea>
        </div>
    </transition>

    <!-- Chat History Area -->
    <div ref="chatContainer" class="flex-1 overflow-y-auto space-y-8 pr-2 pb-32 scroll-smooth">
      <div 
        v-for="msg in messages" 
        :key="msg.id"
        :class="['flex w-full', msg.role === 'user' ? 'justify-end' : 'justify-start']"
      >
        <!-- User Bubble -->
        <div v-if="msg.role === 'user'" class="max-w-[85%] md:max-w-[70%] bg-surface-800 text-white rounded-2xl p-5 shadow-sm border border-surface-700 font-medium">
             <div class="whitespace-pre-wrap leading-relaxed">{{ msg.content }}</div>
             <span class="block text-[10px] mt-2 opacity-40 text-right font-bold">{{ msg.timestamp }}</span>
        </div>
        
        <!-- Assistant Output Rendering -->
        <div v-if="msg.role === 'assistant'" class="flex gap-4 max-w-[95%] md:max-w-[85%]">
          <!-- Avatar -->
          <div class="shrink-0 w-8 h-8 rounded-lg bg-gradient-to-br from-gold-400 to-amber-600 flex items-center justify-center shadow-lg shadow-gold-500/20 text-sm mt-1">
             🪖
          </div>
          
          <div class="flex-1 min-w-0 prose prose-invert prose-p:leading-relaxed prose-a:text-gold-400 hover:prose-a:text-gold-300 prose-strong:text-white prose-headings:text-white prose-pre:bg-surface-900 prose-pre:border prose-pre:border-surface-700 prose-pre:shadow-inner w-full">
            
            <div v-if="msg.error" class="bg-rose-500/10 border border-rose-500/30 text-rose-200 p-4 rounded-2xl w-full">
                {{ msg.content }}
            </div>
            
            <!-- Standard text/markdown rendering -->
            <div v-else-if="!msg.is_html" class="whitespace-pre-wrap text-slate-300" v-html="msg.content.replace(/\n/g, '<br/>')"></div>
            
            <!-- HTML App Rendering (Portfolio generator) -->
            <div v-else class="space-y-4 w-full">
                <div class="p-4 bg-emerald-500/10 border border-emerald-500/20 rounded-2xl flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                    <div>
                        <h4 class="font-bold text-emerald-400 text-lg m-0 flex items-center gap-2">
                           <CheckCircleIcon class="w-5 h-5" /> Portfolio Généré
                        </h4>
                        <p class="text-sm text-emerald-500/80 m-0 mt-1">Code source complet prêt à être déployé.</p>
                    </div>
                    <button @click="downloadHtml(msg.content)" class="px-5 py-2.5 bg-emerald-500 hover:bg-emerald-400 text-surface-950 rounded-xl font-bold transition-all shadow-lg shadow-emerald-500/20 whitespace-nowrap">
                        Télécharger HTML
                    </button>
                </div>
                
                <h4 class="text-slate-400 text-sm mt-4 font-bold border-b border-surface-700 pb-2">Aperçu du Code Source</h4>
                <div class="relative group/code">
                    <pre class="bg-surface-950/80 overflow-x-auto p-5 rounded-2xl border border-surface-700 mt-2 font-mono text-xs text-slate-300 max-h-96 shadow-inner">{{ msg.content }}</pre>
                </div>
            </div>
            
            <span class="block text-[10px] mt-4 opacity-40 font-bold" :class="msg.error ? 'text-rose-200' : 'text-slate-500'">{{ msg.timestamp }}</span>
          </div>
        </div>
      </div>
      
      <!-- Typing Indicator -->
      <div v-if="isLoading" class="flex w-full justify-start gap-4">
         <div class="shrink-0 w-8 h-8 rounded-lg bg-surface-800 flex items-center justify-center border border-surface-700 text-sm mt-1 animate-pulse">
             🤖
         </div>
         <div class="py-2.5 flex items-center gap-1.5 opacity-50">
            <div class="w-2 h-2 rounded-full bg-gold-500/50 animate-bounce" style="animation-delay: 0ms"></div>
            <div class="w-2 h-2 rounded-full bg-gold-500/50 animate-bounce" style="animation-delay: 150ms"></div>
            <div class="w-2 h-2 rounded-full bg-gold-500/50 animate-bounce" style="animation-delay: 300ms"></div>
         </div>
      </div>
    </div>

    <!-- Floating Input Area -->
    <div class="absolute bottom-4 left-4 right-4 md:left-8 md:right-8 lg:bottom-8 lg:left-8 lg:right-8 bg-surface-950/80 pt-4 backdrop-blur-md">
      <div class="bg-surface-900 border border-surface-700 p-2 rounded-2xl shadow-lg flex items-end gap-2 focus-within:ring-1 focus-within:ring-surface-600 focus-within:border-surface-600 transition-all">
         <textarea 
            v-model="inputQuery"
            @keydown.enter.exact.prevent="sendMessage"
            class="w-full bg-transparent border-none focus:ring-0 text-white resize-none h-14 max-h-48 p-3 placeholder-slate-500 scrollbar-hide font-medium text-[15px]"
            placeholder="Posez une question, demandez un audit de CV, ou générez un portfolio..."
         ></textarea>
         <button 
            @click="sendMessage"
            :disabled="(!inputQuery.trim() && !cvText.trim()) || isLoading"
            class="p-4 bg-white hover:bg-slate-200 disabled:bg-surface-800 disabled:text-slate-600 text-surface-950 rounded-xl font-bold transition-all shrink-0 shadow-sm"
         >
            <PaperAirplaneIcon v-if="!isLoading" class="w-5 h-5" />
            <ArrowPathIcon v-else class="w-5 h-5 animate-spin" />
         </button>
      </div>
      <div class="text-center mt-3">
          <p class="text-[11px] font-bold text-slate-500 tracking-wide">
             GoldArmy peut faire des erreurs. Vérifiez les informations importantes.
          </p>
      </div>
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
