import re

path = 'c:/Users/Utilisateur/PycharmProjects/GoldArmyArgent/frontend/src/views/AgentChat.vue'

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Define the new premium Audit UI template
new_audit_ui = """
            <div v-else-if="msg.is_audit_rewrite && msg.audit && typeof msg.audit === 'object'" class="w-full space-y-6">

              <!-- HEADER PREMIUM -->
              <div class="flex flex-col md:flex-row items-center gap-4 p-5 bg-white border border-slate-100 rounded-[2rem] shadow-sm relative overflow-hidden group">
                <div class="absolute inset-0 bg-gradient-to-r from-slate-50/50 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
                <div class="w-16 h-16 rounded-2xl bg-[#F9FAFB] border border-slate-100 flex items-center justify-center text-3xl shadow-inner relative z-10">🎯</div>
                <div class="flex-1 text-center md:text-left relative z-10">
                  <h3 class="text-xl font-black text-slate-900 m-0 leading-tight tracking-tight">{{ msg.audit.candidate_name || t('agent_chat.audit.candidate') }}</h3>
                  <div class="flex items-center justify-center md:justify-start gap-2 mt-1">
                      <span class="px-2 py-0.5 bg-[#E85D3E]/10 text-[#E85D3E] text-[10px] font-black uppercase tracking-wider rounded-md border border-[#E85D3E]/20">
                        {{ msg.audit.candidate_title || t('agent_chat.audit.title') }}
                      </span>
                  </div>
                </div>
                <div class="px-4 py-2 bg-slate-50 rounded-2xl border border-slate-100 text-center shrink-0">
                  <p class="text-[9px] text-slate-400 font-black uppercase tracking-[0.2em] mb-0.5">{{ t('agent_chat.audit.ats_report') }}</p>
                  <p class="text-[11px] text-slate-900 font-bold">#{{ msg.id }}</p>
                </div>
              </div>

              <!-- BENTO GRID: SCORE & CATEGORIES -->
              <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <!-- SCORE CENTRAL -->
                <div class="lg:col-span-1 p-8 bg-white border border-slate-100 rounded-[2.5rem] flex flex-col items-center justify-center relative overflow-hidden shadow-sm group">
                  <div class="absolute -top-4 -right-4 text-8xl font-black text-slate-50 select-none pointer-events-none group-hover:text-slate-100/50 transition-colors">ATS</div>
                  
                  <p class="text-[10px] font-black text-slate-400 uppercase tracking-[0.3em] mb-8 relative z-10">{{ t('agent_chat.audit.global_score') }}</p>
                  
                  <div class="relative w-44 h-44 z-10">
                    <svg class="w-full h-full -rotate-90 drop-shadow-xl" viewBox="0 0 120 120">
                      <circle cx="60" cy="60" r="52" fill="none" stroke="#F1F5F9" stroke-width="10"/>
                      <circle cx="60" cy="60" r="52" fill="none"
                        :stroke="msg.audit.ats_score >= 75 ? '#10b981' : msg.audit.ats_score >= 50 ? '#f59e0b' : '#ef4444'"
                        stroke-width="10"
                        stroke-linecap="round"
                        :stroke-dasharray="`${(msg.audit.ats_score || 0) * 3.267} 326.7`"
                        class="transition-all duration-[2000ms] ease-out"
                      />
                    </svg>
                    <div class="absolute inset-0 flex flex-col items-center justify-center">
                      <div class="flex items-start">
                        <span class="text-6xl font-black tracking-tighter text-slate-900 leading-none">{{ msg.audit.ats_score || 0 }}</span>
                      </div>
                      <div class="flex items-center gap-1.5 mt-2">
                        <span class="text-slate-400 text-xs font-bold">/100</span>
                        <div v-if="msg.audit.original_ats_score && msg.audit.original_ats_score !== msg.audit.ats_score" 
                             class="px-2 py-0.5 bg-slate-100 rounded-full text-[9px] font-bold text-slate-500 border border-slate-200">
                           {{ t('common.draft') || 'Draft' }}
                        </div>
                      </div>
                    </div>
                  </div>

                  <div v-if="msg.audit.original_ats_score" class="mt-6 flex flex-col items-center gap-2">
                      <div class="flex items-center gap-2 px-4 py-1.5 bg-green-50 text-green-600 text-[10px] font-black rounded-full border border-green-100">
                          <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 10l7-7m0 0l7 7m-7-7v18"/></svg>
                          PROGRESSION: +{{ msg.audit.ats_score - msg.audit.original_ats_score }}%
                      </div>
                      <p class="text-[11px] font-bold text-slate-400">AVANT: {{ msg.audit.original_ats_score }}</p>
                  </div>
                </div>

                <!-- CATEGORIES GRID -->
                <div class="lg:col-span-2 p-8 bg-white border border-slate-100 rounded-[2.5rem] shadow-sm relative overflow-hidden">
                  <p class="text-[10px] font-black text-slate-400 uppercase tracking-[0.3em] mb-8">{{ t('common.detail_by_category') }}</p>
                  
                  <div class="grid grid-cols-1 md:grid-cols-2 gap-x-10 gap-y-6">
                    <div v-for="(val, key) in {
                      [t('agent_chat.audit.categories.keywords')]: msg.audit.scores?.mots_cles,
                      [t('agent_chat.audit.categories.impact')]: msg.audit.scores?.impact_resultats,
                      [t('agent_chat.audit.categories.formatting')]: msg.audit.scores?.mise_en_forme,
                      [t('agent_chat.audit.categories.readability')]: msg.audit.scores?.lisibilite,
                      [t('agent_chat.audit.categories.relevance')]: msg.audit.scores?.experience_pertinence
                    }" :key="key" class="space-y-3 group/cat">
                      <div class="flex justify-between items-end">
                        <span class="text-xs font-bold text-slate-500 group-hover/cat:text-[#E85D3E] transition-colors uppercase tracking-wider">{{ key }}</span>
                        <span class="text-sm font-black text-slate-900">{{ val || 0 }}<span class="text-[10px] text-slate-300 ml-0.5">/100</span></span>
                      </div>
                      <div class="h-2.5 bg-slate-50 rounded-full overflow-hidden border border-slate-100 relative shadow-inner">
                        <div class="h-full rounded-full transition-all duration-[1500ms] ease-out shadow-sm"
                          :class="val >= 75 ? 'bg-emerald-500' : val >= 50 ? 'bg-amber-500' : 'bg-rose-500'"
                          :style="`width: ${val}%`"
                        ></div>
                      </div>
                    </div>
                  </div>
                  
                  <!-- Final Verdict -->
                  <div class="mt-10 pt-6 border-t border-slate-50 flex items-center justify-between">
                      <div class="flex items-center gap-2">
                          <div :class="msg.audit.ats_score >= 75 ? 'bg-emerald-500' : 'bg-amber-500'" class="w-2 h-2 rounded-full animate-pulse"></div>
                          <span class="text-xs font-bold text-slate-400">{{ t('agent_chat.audit.status') || 'Status' }}:</span>
                          <span :class="msg.audit.ats_score >= 75 ? 'text-emerald-600' : 'text-amber-600'" class="text-xs font-black uppercase tracking-widest">
                            {{ msg.audit.ats_score >= 75 ? t('agent_chat.audit.good_profile') : t('agent_chat.audit.to_improve') }}
                          </span>
                      </div>
                  </div>
                </div>
              </div>

              <!-- ANALYSIS: FLAWS & ACTIONS -->
              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                 <!-- FLAWS -->
                 <div class="p-6 bg-rose-50/30 border border-rose-100 rounded-[2rem] relative overflow-hidden group">
                    <div class="absolute -right-4 -top-4 w-24 h-24 bg-rose-500/5 rounded-full blur-2xl group-hover:scale-150 transition-transform"></div>
                    <div class="flex items-center gap-3 mb-6">
                        <div class="w-8 h-8 rounded-lg bg-rose-500/10 flex items-center justify-center text-rose-500 border border-rose-500/20">
                            <XMarkIcon class="w-5 h-5" />
                        </div>
                        <h4 class="text-sm font-black text-rose-600 uppercase tracking-[0.2em] m-0">{{ msg.audit.original_failles ? t('agent_chat.audit.initial_flaws') : t('agent_chat.audit.critical_flaws') }}</h4>
                    </div>
                    <ul class="space-y-4">
                      <li v-for="(faille, i) in (msg.audit.original_failles || msg.audit.failles || [])" :key="i"
                        class="flex gap-4 group/li"
                      >
                        <span class="text-rose-300 font-black text-xs mt-0.5 group-hover/li:text-rose-500 transition-colors">{{ (i + 1).toString().padStart(2, '0') }}</span>
                        <p class="text-[13px] text-slate-600 font-medium leading-relaxed m-0">{{ faille }}</p>
                      </li>
                    </ul>
                 </div>

                 <!-- ACTIONS -->
                 <div class="p-6 bg-emerald-50/30 border border-emerald-100 rounded-[2rem] relative overflow-hidden group">
                    <div class="absolute -right-4 -top-4 w-24 h-24 bg-emerald-500/5 rounded-full blur-2xl group-hover:scale-150 transition-transform"></div>
                    <div class="flex items-center gap-3 mb-6">
                        <div class="w-8 h-8 rounded-lg bg-emerald-500/10 flex items-center justify-center text-emerald-600 border border-emerald-500/20">
                            <CheckIcon class="w-5 h-5" />
                        </div>
                        <h4 class="text-sm font-black text-emerald-600 uppercase tracking-[0.2em] m-0">{{ t('agent_chat.audit.priority_actions') }}</h4>
                    </div>
                    <ul class="space-y-4">
                      <li v-for="(action, i) in (msg.audit.actions || [])" :key="i"
                        class="flex gap-4 group/li"
                      >
                        <span class="text-emerald-300 font-black text-xs mt-0.5 group-hover/li:text-emerald-600 transition-colors">{{ (i + 1).toString().padStart(2, '0') }}</span>
                        <p class="text-[13px] text-slate-600 font-medium leading-relaxed m-0">{{ action }}</p>
                      </li>
                    </ul>
                 </div>
              </div>

              <!-- IMPACT TRANSFORMATIONS -->
              <div v-if="msg.audit.correction_mapping && Object.keys(msg.audit.correction_mapping).length" class="space-y-6">
                 <div class="flex items-center justify-between px-2">
                    <div class="flex items-center gap-3">
                        <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-[#E85D3E] to-gold-500 flex items-center justify-center text-white shadow-lg shadow-gold-500/20">
                            <SparklesIcon class="w-5 h-5" />
                        </div>
                        <div>
                            <h4 class="text-base font-black text-slate-900 uppercase tracking-widest m-0">{{ t('agent_chat.audit.transformations_impact') }}</h4>
                            <p class="text-[10px] font-bold text-slate-400 mt-0.5 uppercase tracking-wider">God Mode Intelligence 3.1 Pro</p>
                        </div>
                    </div>
                 </div>

                 <div class="grid grid-cols-1 gap-4">
                    <div v-for="(solution, flaw) in msg.audit.correction_mapping" :key="flaw" 
                         class="group relative bg-white border border-slate-100 rounded-[2rem] p-6 hover:border-[#E85D3E]/30 transition-all duration-500 shadow-sm hover:shadow-xl hover:shadow-[#E85D3E]/5 overflow-hidden">
                        
                        <div class="absolute top-0 bottom-0 left-0 w-1.5 bg-gradient-to-b from-rose-400 via-[#E85D3E] to-emerald-400 opacity-20 group-hover:opacity-100 transition-opacity"></div>
                        
                        <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 items-center">
                            <!-- Flaw -->
                            <div class="lg:col-span-5 space-y-2">
                                <div class="flex items-center gap-2 text-[10px] font-black text-rose-500 uppercase tracking-widest opacity-60">
                                    <XMarkIcon class="w-3 h-3" /> {{ t('agent_chat.audit.flaw') }}
                                </div>
                                <p class="text-[13px] text-slate-400 font-semibold italic leading-relaxed m-0">{{ flaw }}</p>
                            </div>

                            <!-- Arrow -->
                            <div class="lg:col-span-1 flex items-center justify-center opacity-20 group-hover:opacity-100 group-hover:scale-110 transition-all">
                                <svg class="w-6 h-6 text-[#E85D3E] transform rotate-90 lg:rotate-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M13 5l7 7-7 7M5 5l7 7-7 7"/>
                                </svg>
                            </div>

                            <!-- Solution -->
                            <div class="lg:col-span-6 p-4 bg-emerald-50/50 rounded-2xl border border-emerald-100/50 group-hover:bg-emerald-50 group-hover:border-emerald-200 transition-colors">
                                <div class="flex items-center gap-2 text-[10px] font-black text-emerald-600 uppercase tracking-widest mb-2">
                                    <CheckCircleIcon class="w-3 h-3" /> {{ t('agent_chat.audit.impact') }}
                                </div>
                                <p class="text-[13px] text-slate-900 font-bold leading-relaxed m-0">{{ solution }}</p>
                            </div>
                        </div>
                    </div>
                 </div>
              </div>

              <!-- TEMPLATE SELECTOR -->
              <div class="p-8 bg-white border border-slate-100 rounded-[2.5rem] shadow-sm">
                  <p class="text-[10px] font-black text-slate-400 uppercase tracking-[0.3em] mb-8">{{ t('agent_chat.audit.choose_template') }}</p>
                  
                  <div class="flex flex-col md:flex-row gap-8">
                      <!-- PREVIEW -->
                      <div class="w-full md:w-32 h-44 bg-slate-50 rounded-2xl border border-slate-100 overflow-hidden shrink-0 shadow-inner group relative">
                           <div class="absolute inset-0 transition-all duration-500" :style="{ backgroundColor: (CV_THEMES.find(t => t.id === (hoveredTheme || selectedTheme))?.colors[0]) === '#ffffff' ? '#f8fafc' : (CV_THEMES.find(t => t.id === (hoveredTheme || selectedTheme))?.colors[0]) }">
                               <div class="absolute left-0 top-0 bottom-0 w-1/3 opacity-30" :style="{ backgroundColor: CV_THEMES.find(t => t.id === (hoveredTheme || selectedTheme))?.colors[1] }"></div>
                               <div class="absolute top-4 left-1/3 right-4 h-2 rounded-full opacity-40" :style="{ backgroundColor: CV_THEMES.find(t => t.id === (hoveredTheme || selectedTheme))?.colors[1] }"></div>
                               <div class="absolute top-8 left-1/3 right-8 h-1.5 rounded-full opacity-20" :style="{ backgroundColor: CV_THEMES.find(t => t.id === (hoveredTheme || selectedTheme))?.colors[1] }"></div>
                               <div class="absolute top-12 left-1/3 right-4 h-1 rounded-full opacity-10" :style="{ backgroundColor: CV_THEMES.find(t => t.id === (hoveredTheme || selectedTheme))?.colors[1] }"></div>
                           </div>
                           <div class="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity bg-slate-900/10 backdrop-blur-[2px]">
                               <EyeIcon class="w-8 h-8 text-white" />
                           </div>
                      </div>

                      <!-- GRID -->
                      <div class="flex-1 grid grid-cols-2 lg:grid-cols-3 gap-3">
                          <button
                              v-for="theme in CV_THEMES"
                              :key="theme.id"
                              @click="selectedTheme = theme.id"
                              @mouseenter="hoveredTheme = theme.id"
                              @mouseleave="hoveredTheme = null"
                              :class="[
                                  'p-4 rounded-2xl border text-left flex flex-col gap-2 transition-all duration-300 relative overflow-hidden',
                                  selectedTheme === theme.id
                                      ? 'bg-[#E85D3E] border-[#E85D3E] shadow-xl shadow-[#E85D3E]/20 translate-y-[-2px]'
                                      : 'bg-white border-slate-100 hover:border-slate-300 hover:bg-slate-50'
                              ]"
                          >
                              <div class="flex items-center gap-3">
                                  <div class="w-4 h-4 rounded-full border border-white/20 shadow-inner shrink-0" :style="{ background: `linear-gradient(135deg, ${theme.colors[0]} 50%, ${theme.colors[1]} 50%)` }"></div>
                                  <span :class="selectedTheme === theme.id ? 'text-white' : 'text-slate-900'" class="text-xs font-black truncate">{{ theme.name }}</span>
                              </div>
                              <span :class="selectedTheme === theme.id ? 'text-white/70' : 'text-slate-400'" class="text-[9px] font-bold uppercase tracking-widest">{{ theme.id === 'goldarmy' ? 'Official' : 'Modern' }}</span>
                          </button>
                      </div>
                  </div>
              </div>

              <!-- ACTIONS -->
              <div class="flex flex-col gap-3">
                  <button
                    @click="downloadCvDocx(msg.content)"
                    :disabled="isDownloadingDocx"
                    class="w-full group flex items-center justify-center gap-3 px-8 py-5 bg-gradient-to-r from-slate-900 to-slate-800 hover:from-[#E85D3E] hover:to-gold-600 text-white rounded-[2rem] font-black transition-all duration-500 shadow-2xl shadow-slate-900/20 active:scale-[0.98] disabled:opacity-50"
                  >
                    <ArrowDownTrayIcon v-if="!isDownloadingDocx" class="w-6 h-6 transform group-hover:translate-y-1 transition-transform" />
                    <ArrowPathIcon v-else class="w-6 h-6 animate-spin" />
                    <span class="text-base uppercase tracking-widest">
                        {{ isDownloadingDocx ? t('agent_chat.audit.generating_file') : t('agent_chat.audit.download_cv_rewritten') }}
                    </span>
                  </button>
                  <p class="text-[10px] text-slate-400 font-bold text-center uppercase tracking-widest flex items-center justify-center gap-2">
                      <span class="w-1.5 h-1.5 bg-emerald-500 rounded-full"></span>
                      {{ t('agent_chat.audit.ats_friendly') }}
                  </p>
              </div>

            </div>
"""

# Use regex to replace the entire block
# We need to be careful with the start and end of the block
pattern = r'<div v-else-if="msg\.is_audit_rewrite && msg\.audit && typeof msg\.audit === \'object\'".*?<!-- Fallback audit'
# Note: we stop at <!-- Fallback audit to keep the rest
content = re.sub(pattern, new_audit_ui + '\n             <!-- Fallback audit', content, flags=re.DOTALL)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print("done")
