import re

path = 'c:/Users/Utilisateur/PycharmProjects/GoldArmyArgent/frontend/src/views/Interview.vue'

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update the Header (Call bar)
room_header = """    <!-- IMMERSIVE VIDEO CALL UI — Design Premium SaaS -->
    <div v-else class="fixed inset-0 bg-[#0c0c0e] flex flex-col md:flex-row z-[210] overflow-hidden font-sans interview-room">
      
      <!-- ═══ PANNEAU GAUCHE : Salle d'appel ═══ -->
      <div class="flex-1 flex flex-col min-w-0 relative">
        <!-- Background -->
        <div class="absolute inset-0 z-0 bg-gradient-to-b from-[#111113] to-black">
          <div class="absolute inset-0 interview-room-grain pointer-events-none opacity-20"></div>
        </div>

        <!-- NEW PREMIUM CALL HEADER -->
        <header class="relative z-10 flex items-center justify-between px-6 py-4 border-b border-white/[0.05] bg-black/40 backdrop-blur-2xl">
          <div class="flex items-center gap-6">
            <button @click="goBackToDashboard" class="w-10 h-10 flex items-center justify-center rounded-xl bg-white/5 hover:bg-white/10 text-white/70 transition-all border border-white/5">
              <ArrowLeftIcon class="w-5 h-5" />
            </button>
            <div class="flex items-center gap-4">
              <div class="w-10 h-10 rounded-xl overflow-hidden border border-white/10 shadow-lg">
                <img :src="currentRecruiter?.img" class="w-full h-full object-cover" alt="" />
              </div>
              <div>
                <h1 class="text-sm font-black text-white m-0 tracking-tight flex items-center gap-2">
                  {{ config.company }} <span class="w-1 h-1 rounded-full bg-white/20"></span> {{ config.jobTitle }}
                </h1>
                <div class="flex items-center gap-2 mt-1">
                  <span class="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-md bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-[9px] font-black uppercase tracking-[0.1em]">
                    <span class="relative flex h-1.5 w-1.5">
                      <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                      <span class="relative inline-flex rounded-full h-1.5 w-1.5 bg-emerald-500"></span>
                    </span>
                    Live Interview
                  </span>
                  <span class="text-slate-500 text-[10px] font-black tabular-nums">{{ callElapsed }}</span>
                </div>
              </div>
            </div>
          </div>
          
          <div class="flex items-center gap-3">
             <div class="hidden sm:flex items-center gap-3 px-4 py-2 rounded-xl bg-white/5 border border-white/10">
                <div class="flex flex-col items-end">
                    <span class="text-white text-[10px] font-black tracking-tight">{{ currentRecruiter?.name }}</span>
                    <span class="text-slate-500 text-[8px] font-bold uppercase tracking-widest">{{ currentRecruiter?.role }}</span>
                </div>
                <img :src="currentRecruiter?.img" class="w-8 h-8 rounded-full object-cover border border-white/20" />
             </div>
          </div>
        </header>"""

# Find the old header and replace it
# Block starts around line 780
header_pattern = r'<!-- IMMERSIVE VIDEO CALL UI.*?<header.*?header>'
content = re.sub(header_pattern, room_header, content, flags=re.DOTALL)

# 2. Update the Control Bar
room_controls = """        <!-- NEW PREMIUM CONTROLS -->
        <div class="relative z-20 px-4 pb-8 flex flex-col items-center gap-4">
          <div v-if="isListening" class="text-[#E85D3E] font-black uppercase tracking-[0.3em] text-[10px] animate-pulse drop-shadow-lg mb-2">
              Microphone Actif — Parlez Maintenant
          </div>
          
          <div class="inline-flex items-center gap-2 p-2.5 rounded-[2.5rem] bg-black/60 backdrop-blur-2xl border border-white/10 shadow-2xl">
            <button @click="showChat = !showChat" 
              :class="showChat ? 'bg-[#E85D3E] text-white shadow-xl shadow-[#E85D3E]/20' : 'bg-white/5 text-slate-400 hover:text-white hover:bg-white/10'"
              class="w-12 h-12 flex items-center justify-center rounded-full transition-all duration-300">
              <ChatBubbleLeftRightIcon class="w-5 h-5" />
            </button>
            
            <button @click="testAudio" class="w-12 h-12 flex items-center justify-center rounded-full bg-white/5 text-slate-400 hover:text-[#E85D3E] hover:bg-white/10 transition-all">
              <SpeakerWaveIcon class="w-5 h-5" />
            </button>
            
            <div class="w-px h-8 bg-white/10 mx-1"></div>
            
            <button @click="triggerListen" 
              :class="isListening ? 'bg-rose-500 text-white scale-110 shadow-xl shadow-rose-500/40' : (isAIThinking ? 'bg-[#E85D3E] text-white scale-105 shadow-xl shadow-[#E85D3E]/20' : 'bg-white/10 text-white hover:bg-white/20')"
              class="w-16 h-16 flex items-center justify-center rounded-full transition-all duration-300 mx-1">
              <MicrophoneIcon v-if="!isListening && !isAIThinking" class="w-6 h-6" />
              <StopIcon v-else-if="isListening" class="w-6 h-6" />
              <div v-else class="flex gap-1">
                <span class="w-1.5 h-1.5 bg-white rounded-full animate-bounce" style="animation-delay: 0ms"></span>
                <span class="w-1.5 h-1.5 bg-white rounded-full animate-bounce" style="animation-delay: 150ms"></span>
                <span class="w-1.5 h-1.5 bg-white rounded-full animate-bounce" style="animation-delay: 300ms"></span>
              </div>
            </button>

            <div class="w-px h-8 bg-white/10 mx-1"></div>

            <button @click="finishInterview" class="w-14 h-14 flex items-center justify-center rounded-full bg-rose-600 hover:bg-rose-500 text-white transition-all hover:scale-105 active:scale-95 shadow-xl shadow-rose-900/40">
              <PhoneIcon class="w-6 h-6 rotate-[135deg]" />
            </button>
          </div>
        </div>"""

# Find the old controls and replace it
# Block starts around line 927
controls_pattern = r'<!-- Barre de contrôles.*?</div>\s*</div>\s*<p v-if="isListening"'
content = re.sub(controls_pattern, room_controls, content, flags=re.DOTALL)

# 3. Update the Transcript Panel
transcript_panel = """      <!-- ═══ PANNEAU DROIT : Transcription Premium ═══ -->
      <div v-show="showChat" class="interview-room-chat w-full md:w-[400px] lg:w-[440px] shrink-0 flex flex-col bg-[#111113] border-l border-white/[0.05] shadow-2xl relative z-[220]">
        <div class="p-6 border-b border-white/[0.05] flex items-center justify-between bg-black/20">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-xl bg-[#E85D3E]/10 flex items-center justify-center">
              <ChatBubbleLeftRightIcon class="w-5 h-5 text-[#E85D3E]" />
            </div>
            <div>
                <h2 class="text-sm font-black text-white m-0 tracking-tight">Transcription Live</h2>
                <p class="text-[9px] font-bold text-slate-500 uppercase tracking-widest mt-0.5">IA Insight System</p>
            </div>
          </div>
          <button @click="showChat = false" class="p-2 rounded-xl hover:bg-white/5 text-slate-500 transition-colors">
            <XMarkIcon class="w-5 h-5" />
          </button>
        </div>

        <div class="flex-1 overflow-y-auto p-6 space-y-6 scroll-smooth custom-scrollbar" ref="chatContainer">
          <div v-for="msg in conversation" :key="msg.id" :class="msg.role === 'user' ? 'flex flex-col items-end' : 'flex flex-col items-start'">
            <div :class="msg.role === 'user' 
              ? 'max-w-[90%] rounded-2xl rounded-tr-sm p-4 bg-white/5 border border-white/10 text-white shadow-sm' 
              : 'max-w-[90%] rounded-2xl rounded-tl-sm p-4 bg-[#E85D3E]/5 border border-[#E85D3E]/10 text-slate-200'">
              
              <div class="flex items-center gap-2 mb-2">
                <div v-if="msg.role !== 'user'" class="w-5 h-5 rounded-full overflow-hidden border border-[#E85D3E]/30">
                  <img :src="currentRecruiter?.img" class="w-full h-full object-cover" />
                </div>
                <span class="text-[9px] font-black uppercase tracking-widest text-slate-500">
                    {{ msg.role === 'user' ? 'Candidat (Vous)' : currentRecruiter?.name }}
                </span>
              </div>
              
              <p class="text-sm leading-relaxed whitespace-pre-wrap font-medium">{{ msg.content }}</p>
            </div>
          </div>
          
          <div v-if="isAIThinking" class="flex flex-col items-start animate-pulse">
            <div class="rounded-2xl rounded-tl-sm p-4 bg-white/5 border border-white/10 text-slate-400 text-xs flex items-center gap-3">
              <div class="flex gap-1">
                <span class="w-1 h-1 bg-white/40 rounded-full animate-bounce" style="animation-delay: 0ms"></span>
                <span class="w-1 h-1 bg-white/40 rounded-full animate-bounce" style="animation-delay: 150ms"></span>
                <span class="w-1 h-1 bg-white/40 rounded-full animate-bounce" style="animation-delay: 300ms"></span>
              </div>
              Analyse de la réponse...
            </div>
          </div>
          
          <div v-if="transcript && !isAIThinking" class="flex flex-col items-end">
            <div class="max-w-[90%] rounded-2xl p-4 bg-white/5 border border-white/10 border-dashed text-slate-400 text-xs italic">
              {{ transcript }}...
            </div>
          </div>
        </div>
      </div>"""

# Find the old transcript and replace it
# Block starts around line 957
transcript_pattern = r'<!-- ═══ PANNEAU DROIT : Transcription.*?</div>\s*</div>'
content = re.sub(transcript_pattern, transcript_panel, content, flags=re.DOTALL)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print("done")
