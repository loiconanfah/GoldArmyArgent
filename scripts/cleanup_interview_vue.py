import re

path = 'c:/Users/Utilisateur/PycharmProjects/GoldArmyArgent/frontend/src/views/Interview.vue'

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Remove duplicate transcript/thinking blocks
# The loop ends, then we have the new blocks, then the old ones.
# Let's find the end of the conversation loop and keep only the new blocks.
# The new blocks use 0ms, 150ms, 300ms for thinking animation.
# The old ones used 0ms, 100ms, 200ms.

# I'll replace the entire transcript panel again to be sure.
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

# 2. Scorecard Modal
scorecard_modal = """      <!-- SCORECARD MODAL -->
      <div v-if="showScorecard" class="fixed inset-0 z-[100] flex items-center justify-center p-4">
          <div class="absolute inset-0 bg-slate-900/60 backdrop-blur-md" @click="!isAnalyzing ? stopInterview() : null"></div>
          
          <div class="bg-white border border-slate-100 w-full max-w-4xl rounded-[2.5rem] overflow-hidden shadow-2xl relative z-10 animate-scale-in">
              <!-- Header -->
              <div class="p-8 border-b border-slate-100 bg-slate-50 flex items-center justify-between">
                  <div class="flex items-center gap-4">
                      <div class="w-12 h-12 rounded-2xl bg-[#E85D3E] flex items-center justify-center shadow-lg shadow-[#E85D3E]/20">
                          <ChartBarIcon class="w-6 h-6 text-white" />
                      </div>
                      <div>
                          <h2 class="text-2xl font-black text-slate-900 tracking-tight leading-none mb-1">Rapport d'Entretien</h2>
                          <p class="text-[10px] font-black text-slate-400 uppercase tracking-widest">God Mode Analysis System</p>
                      </div>
                  </div>
                  <button v-if="!isAnalyzing" @click="stopInterview" class="p-2 text-slate-400 hover:text-slate-900 transition-colors">
                      <XMarkIcon class="w-6 h-6" />
                  </button>
              </div>

              <!-- Content -->
              <div class="p-8 max-h-[75vh] overflow-y-auto custom-scrollbar bg-white">
                  <!-- Loading State -->
                  <div v-if="isAnalyzing" class="flex flex-col items-center justify-center py-20 gap-8">
                      <div class="relative w-24 h-24">
                          <div class="absolute inset-0 border-4 border-slate-100 rounded-full"></div>
                          <div class="absolute inset-0 border-4 border-[#E85D3E] border-t-transparent rounded-full animate-spin"></div>
                      </div>
                      <div class="text-center">
                        <p class="text-xl font-black text-slate-900 mb-2">Analyse IA en cours...</p>
                        <p class="text-sm text-slate-400 max-w-xs mx-auto">Nous examinons votre communication, votre expertise et votre attitude professionnelle.</p>
                      </div>
                  </div>

                  <!-- Results State -->
                  <div v-else-if="scorecard" class="space-y-10">
                      <!-- Hero Scores (Bento) -->
                      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                          <div v-for="(val, cat) in scorecard.scores" :key="cat" class="bg-slate-50 border border-slate-100 p-6 rounded-[2rem] flex flex-col items-center gap-4 transition-all hover:border-[#E85D3E]/20">
                              <span class="text-[9px] uppercase font-black tracking-widest text-slate-400">{{ cat === 'technical' ? 'Technique' : cat === 'communication' ? 'Élocution' : cat === 'soft_skills' ? 'Attitude' : 'Global' }}</span>
                              <div class="relative flex items-center justify-center">
                                  <svg class="w-20 h-20 -rotate-90">
                                      <circle class="text-white" stroke-width="6" stroke="currentColor" fill="transparent" r="34" cx="40" cy="40"/>
                                      <circle :class="val >= 7 ? 'text-emerald-500' : val >= 5 ? 'text-amber-500' : 'text-rose-500'" stroke-width="6" :stroke-dasharray="213" :stroke-dashoffset="213 - (213 * val / 10)" stroke-linecap="round" stroke="currentColor" fill="transparent" r="34" cx="40" cy="40"/>
                                  </svg>
                                  <span class="absolute text-xl font-black text-slate-900">{{ val }}<span class="text-[10px] text-slate-400 opacity-50">/10</span></span>
                              </div>
                          </div>
                      </div>

                      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                          <!-- Points Forts -->
                          <div class="p-8 bg-emerald-50/50 border border-emerald-100 rounded-[2.5rem] space-y-6">
                              <h3 class="text-xs font-black uppercase tracking-widest text-emerald-600 flex items-center gap-3">
                                  <div class="w-8 h-8 rounded-full bg-white flex items-center justify-center shadow-sm border border-emerald-100">
                                    <CheckCircleIcon class="w-4 h-4" />
                                  </div>
                                  Points Forts
                              </h3>
                              <ul class="space-y-4">
                                  <li v-for="p in scorecard.feedback.points_forts" :key="p" class="flex gap-4 text-sm text-slate-700 font-bold leading-relaxed">
                                      <span class="w-1.5 h-1.5 rounded-full bg-emerald-500 mt-1.5 shrink-0"></span>
                                      {{ p }}
                                  </li>
                              </ul>
                          </div>

                          <!-- Points à améliorer -->
                          <div class="p-8 bg-amber-50/50 border border-amber-100 rounded-[2.5rem] space-y-6">
                              <h3 class="text-xs font-black uppercase tracking-widest text-amber-600 flex items-center gap-3">
                                  <div class="w-8 h-8 rounded-full bg-white flex items-center justify-center shadow-sm border border-amber-100">
                                    <AcademicCapIcon class="w-4 h-4" />
                                  </div>
                                  Axes d'amélioration
                              </h3>
                              <ul class="space-y-4">
                                  <li v-for="p in scorecard.feedback.points_amelioration" :key="p" class="flex gap-4 text-sm text-slate-700 font-bold leading-relaxed">
                                      <span class="w-1.5 h-1.5 rounded-full bg-amber-500 mt-1.5 shrink-0"></span>
                                      {{ p }}
                                  </li>
                              </ul>
                          </div>
                      </div>

                      <!-- Recruiter Opinion Card -->
                      <div class="bg-slate-900 p-10 rounded-[3rem] space-y-6 relative overflow-hidden group shadow-2xl">
                          <div class="absolute top-0 right-0 p-8 opacity-5 group-hover:rotate-12 transition-transform">
                              <SparklesIcon class="w-32 h-32 text-white" />
                          </div>
                          
                          <div class="flex items-center justify-between relative z-10">
                            <div class="flex items-center gap-4">
                                <div class="w-12 h-12 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center">
                                    <StarIcon class="w-6 h-6 text-[#E85D3E]" />
                                </div>
                                <h3 class="text-xl font-black text-white m-0">Verdict du Recruteur</h3>
                            </div>
                            <div :class="scorecard.decision.includes('Favorable') ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400' : 'bg-amber-500/10 border-amber-500/20 text-amber-400'" class="px-6 py-2 rounded-full border font-black text-[10px] uppercase tracking-widest">
                                {{ scorecard.decision }}
                            </div>
                          </div>
                          
                          <p class="text-slate-400 text-base font-medium leading-relaxed relative z-10 italic">
                            " {{ scorecard.feedback.conseils }} "
                          </p>
                          
                          <div class="pt-6 border-t border-white/5 flex items-center gap-4">
                             <img :src="currentRecruiter?.img" class="w-10 h-10 rounded-full object-cover border border-white/10" />
                             <div>
                                <p class="text-xs font-black text-white m-0">{{ currentRecruiter?.name }}</p>
                                <p class="text-[10px] text-slate-500 font-bold uppercase tracking-widest m-0">{{ currentRecruiter?.role }}</p>
                             </div>
                          </div>
                      </div>
                  </div>
              </div>

              <!-- Footer -->
              <div class="p-8 bg-slate-50 border-t border-slate-100 flex flex-col md:flex-row justify-between items-center gap-4">
                  <router-link to="/interview/history" class="text-[10px] font-black text-slate-400 hover:text-slate-900 uppercase tracking-[0.2em] transition-colors">
                      Voir l'historique complet
                  </router-link>
                  <div class="flex gap-4">
                    <button @click="stopInterview" class="px-10 py-4 bg-[#E85D3E] hover:bg-[#C44A2D] text-white font-black rounded-2xl transition-all shadow-xl shadow-[#E85D3E]/20 text-xs uppercase tracking-widest">
                        Quitter l'entretien
                    </button>
                  </div>
              </div>
          </div>
      </div>"""

# I'll rebuild the template part carefully
# 1. Everything between room header and transcript panel
# 2. Everything after transcript panel and before style

# Find the transcript panel end
transcript_end_marker = "<!-- ═══ PANNEAU DROIT : Transcription Premium ═══ -->"
scorecard_marker = "<!-- SCORECARD MODAL -->"

# I'll just do a very broad replace to wipe the duplicates.
# 1. Replace the entire room part.
# Let's find the start of the room phase.
room_start_marker = "<!-- IMMERSIVE VIDEO CALL UI — Design Premium SaaS -->"
style_start_marker = "<style scoped>"

# I'll extract the part before the room, and the part after the scorecard.
parts = content.split(room_start_marker)
before_room = parts[0]
after_room_and_scorecard = content.split(style_start_marker)[1]

# Now I need the part between room start and the end of the room (excluding scorecard)
# Then the scorecard itself.

# Let's use a different approach. I'll just fix the duplicates specifically.
content = re.sub(r'</div>\s*</div>\s*<div v-show="showChat".*?<!-- ═══ PANNEAU DROIT : Transcription Premium ═══ -->', '</div>\n      </div>\n\n      '+transcript_panel, content, flags=re.DOTALL)
# Wait, that's not quite right.

# Let's use the line numbers from previous view_file.
# I'll just rewrite the whole template from room start to scorecard end.

# I'll read the file again to be absolutely sure of current state.
with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find markers
room_start_idx = -1
transcript_start_idx = -1
scorecard_start_idx = -1
style_start_idx = -1

for i, line in enumerate(lines):
    if "<!-- IMMERSIVE VIDEO CALL UI" in line: room_start_idx = i
    if "<!-- ═══ PANNEAU DROIT : Transcription Premium" in line: 
        if transcript_start_idx == -1: transcript_start_idx = i
    if "<!-- SCORECARD MODAL" in line:
        if scorecard_start_idx == -1: scorecard_start_idx = i
    if "<style scoped>" in line: style_start_idx = i

print(f"Room: {room_start_idx}, Transcript: {transcript_start_idx}, Scorecard: {scorecard_start_idx}, Style: {style_start_idx}")

# The transcript is duplicated. The scorecard is duplicated.
# I'll keep the first occurrence of each.

# I'll reconstruct the room content.
room_content = "".join(lines[room_start_idx:transcript_start_idx])
# The transcript panel I defined above
# The scorecard modal I defined above
# The live status text and concluding tags

# Wait, I need the analystNote overlay too.
analyst_note_block = """      <!-- Note analyste (overlay discret) -->
      <transition enter-active-class="transition duration-300 ease-out" leave-active-class="transition duration-200 ease-in" enter-from-class="opacity-0 translate-y-2" leave-to-class="opacity-0 translate-y-2">
        <div v-if="analystNote" class="absolute left-4 bottom-28 z-30 max-w-xs md:left-6">
          <div class="interview-analyst-note bg-black/80 backdrop-blur-xl border border-amber-500/20 p-4 rounded-2xl shadow-2xl">
            <div class="flex items-center gap-2 mb-2">
              <SparklesIcon class="w-4 h-4 text-amber-400" />
              <span class="text-[10px] font-bold text-amber-400/80 uppercase">Conseil live</span>
            </div>
            <p class="text-sm text-white leading-relaxed">{{ analystNote.tip }}</p>
            <span class="text-[10px] text-indigo-400 font-medium">{{ analystNote.sentiment }}</span>
          </div>
        </div>
      </transition>"""

final_template_part = room_content + transcript_panel + "\n\n" + analyst_note_block + "\n\n" + scorecard_modal + "\n\n" + """      <!-- Live status text -->
      <div v-if="isListening" class="absolute bottom-32 left-1/2 -translate-x-1/2 text-[#E85D3E] font-black uppercase tracking-[0.3em] text-xs animate-pulse z-10 drop-shadow-lg">
          Microphone Actif — Parlez Maintenant
      </div>
   </div>
  </div>
</template>
"""

new_content = "".join(lines[:room_start_idx]) + room_content + transcript_panel + "\n\n" + analyst_note_block + "\n\n" + scorecard_modal + "\n\n" + """      <!-- Live status text -->
      <div v-if="isListening" class="absolute bottom-32 left-1/2 -translate-x-1/2 text-[#E85D3E] font-black uppercase tracking-[0.3em] text-xs animate-pulse z-10 drop-shadow-lg">
          Microphone Actif — Parlez Maintenant
      </div>
    </div>
  </div>
</template>
""" + "".join(lines[style_start_idx:])

with open(path, 'w', encoding='utf-8') as f:
    f.write(new_content)
print("done")
