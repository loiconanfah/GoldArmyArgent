import re

path = 'c:/Users/Utilisateur/PycharmProjects/GoldArmyArgent/frontend/src/views/Interview.vue'

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update the top level class for the wizard phase
content = content.replace('<div class="interview-page fixed inset-0 z-[60] bg-surface-950', '<div class="interview-page fixed inset-0 z-[60] bg-[#F9FAFB]')

# 2. Redesign the Wizard Header
wizard_header = """    <!-- CONFIGURATION WIZARD -->
    <div v-if="!isInterviewStarted" class="p-4 md:p-10 max-w-6xl mx-auto animate-fade-in-up space-y-10 flex flex-col w-full min-h-screen">
      <!-- NEW PREMIUM HEADER -->
      <div class="flex flex-col md:flex-row items-center justify-between gap-6 pt-10">
        <div class="flex items-center gap-6">
            <button @click="goBackToDashboard" class="w-12 h-12 flex items-center justify-center bg-white border border-slate-200 rounded-2xl text-slate-400 hover:text-[#E85D3E] hover:border-[#E85D3E]/30 transition-all shadow-sm">
                <ArrowLeftIcon class="w-6 h-6" />
            </button>
            <div>
                <h1 class="text-4xl font-black text-slate-900 tracking-tight leading-none mb-2">Simulateur d'Entretien</h1>
                <p class="text-slate-400 font-bold text-xs uppercase tracking-widest flex items-center gap-2">
                    <SparklesIcon class="w-4 h-4 text-[#E85D3E]" /> God Mode Intelligence 3.1
                </p>
            </div>
        </div>
        
        <router-link to="/interview/history" class="px-6 py-3 bg-white border border-slate-200 text-slate-900 font-black text-xs uppercase tracking-widest rounded-2xl transition-all flex items-center gap-3 hover:border-[#E85D3E]/30 shadow-sm">
            <DocumentTextIcon class="w-4 h-4 text-[#E85D3E]" /> Mon Historique
        </router-link>
      </div>"""

# Find the old header block and replace it
# The old block starts at line 636/637
header_pattern = r'<!-- CONFIGURATION WIZARD -->\s*<div v-if="!isInterviewStarted".*?</h1>.*?</div>.*?Mon Historique\s*</router-link>\s*</div>'
content = re.sub(header_pattern, wizard_header, content, flags=re.DOTALL)

# 3. Redesign the Bento Grid for inputs
bento_form = """      <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
         <!-- MAIN CONFIG (Left Col) -->
         <div class="lg:col-span-7 space-y-6">
             <div class="bg-white border border-slate-100 rounded-[2.5rem] p-8 shadow-sm">
                <h3 class="text-xs font-black text-slate-400 uppercase tracking-widest mb-6 flex items-center gap-2">
                    <BuildingOfficeIcon class="w-4 h-4 text-[#E85D3E]" /> Contexte du Poste
                </h3>
                
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                    <div>
                        <label class="block text-[10px] font-black text-slate-400 uppercase tracking-widest mb-2">Entreprise cible</label>
                        <input v-model="config.company" type="text" placeholder="Ex: Google, Alan, Startup X..." class="w-full bg-slate-50 border border-slate-100 rounded-xl px-4 py-3 text-slate-900 font-bold text-sm focus:outline-none focus:border-[#E85D3E]/50 focus:ring-4 focus:ring-[#E85D3E]/5 transition-all">
                    </div>
                    <div>
                        <label class="block text-[10px] font-black text-slate-400 uppercase tracking-widest mb-2">Poste visé</label>
                        <input v-model="config.jobTitle" type="text" placeholder="Ex: Développeur Fullstack..." class="w-full bg-slate-50 border border-slate-100 rounded-xl px-4 py-3 text-slate-900 font-bold text-sm focus:outline-none focus:border-[#E85D3E]/50 focus:ring-4 focus:ring-[#E85D3E]/5 transition-all">
                    </div>
                </div>
                
                <div>
                    <label class="block text-[10px] font-black text-slate-400 uppercase tracking-widest mb-2">Détails de l'offre (Optionnel)</label>
                    <textarea v-model="config.jobDetails" rows="4" placeholder="Collez ici les missions, la tech stack, ou les prérequis..." class="w-full bg-slate-50 border border-slate-100 rounded-xl px-4 py-3 text-slate-900 font-bold text-sm focus:outline-none focus:border-[#E85D3E]/50 focus:ring-4 focus:ring-[#E85D3E]/5 transition-all resize-none"></textarea>
                </div>
             </div>

             <div class="bg-white border border-slate-100 rounded-[2.5rem] p-8 shadow-sm">
                <div class="flex items-center justify-between mb-6">
                    <h3 class="text-xs font-black text-slate-400 uppercase tracking-widest flex items-center gap-2 m-0">
                        <UserIcon class="w-4 h-4 text-[#E85D3E]" /> Votre Profil / CV
                    </h3>
                    <button @click="$refs.fileInput.click()" class="px-4 py-2 bg-[#E85D3E]/5 text-[#E85D3E] hover:bg-[#E85D3E]/10 rounded-xl border border-[#E85D3E]/20 text-[10px] font-black uppercase tracking-widest transition-all flex items-center gap-2">
                        <span v-if="isUploadingCV" class="w-3 h-3 border-2 border-[#E85D3E] border-t-transparent rounded-full animate-spin"></span>
                        <ArrowUpTrayIcon v-else class="w-4 h-4" />
                        {{ isUploadingCV ? 'Extraction...' : 'Importer PDF' }}
                    </button>
                    <input type="file" accept=".pdf" class="hidden" ref="fileInput" @change="handleFileUpload">
                </div>
                <textarea v-model="config.cv" rows="6" placeholder="Collez le texte de votre CV ou importez un PDF..." class="w-full bg-slate-50 border border-slate-100 rounded-xl px-4 py-3 text-slate-900 font-bold text-sm focus:outline-none focus:border-[#E85D3E]/50 focus:ring-4 focus:ring-[#E85D3E]/5 transition-all resize-none"></textarea>
             </div>
         </div>
         
         <!-- RECRUITER & FORMAT (Right Col) -->
         <div class="lg:col-span-5 space-y-6">
              <div class="bg-white border border-slate-100 rounded-[2.5rem] p-8 shadow-sm">
                  <h3 class="text-xs font-black text-slate-400 uppercase tracking-widest mb-6 flex items-center gap-2">
                    <ChatBubbleLeftRightIcon class="w-4 h-4 text-[#E85D3E]" /> Votre Recruteur
                  </h3>
                  <div class="space-y-3">
                      <button v-for="r in recruiters" :key="r.id" 
                         @click="config.recruiterId = r.id" 
                         :class="config.recruiterId === r.id ? 'bg-[#E85D3E] border-[#E85D3E] shadow-xl shadow-[#E85D3E]/20 translate-y-[-2px]' : 'bg-slate-50 border-slate-100 hover:border-slate-300'"
                         class="w-full p-4 border rounded-2xl flex items-center gap-4 transition-all group relative overflow-hidden"
                      >
                         <img :src="r.img" class="w-12 h-12 rounded-xl object-cover border-2 border-white group-hover:scale-105 transition-transform" />
                         <div class="text-left flex-1">
                             <p :class="config.recruiterId === r.id ? 'text-white' : 'text-slate-900'" class="text-sm font-black m-0 leading-tight">{{ r.name }}</p>
                             <p :class="config.recruiterId === r.id ? 'text-white/70' : 'text-slate-400'" class="text-[10px] font-bold uppercase tracking-widest m-0 mt-1">{{ r.role }}</p>
                         </div>
                         <div v-if="config.recruiterId === r.id" class="w-6 h-6 rounded-full bg-white flex items-center justify-center text-[#E85D3E] shadow-sm">
                             <CheckIcon class="w-4 h-4" />
                         </div>
                      </button>
                  </div>
              </div>

              <div class="bg-white border border-slate-100 rounded-[2.5rem] p-8 shadow-sm">
                  <h3 class="text-xs font-black text-slate-400 uppercase tracking-widest mb-6 flex items-center gap-2">
                    <VideoCameraIcon class="w-4 h-4 text-[#E85D3E]" /> Format & Intensité
                  </h3>
                  <div class="grid grid-cols-2 gap-3">
                      <button @click="config.interviewType = 'general'" :class="config.interviewType === 'general' ? 'bg-[#E85D3E] border-[#E85D3E] text-white shadow-xl shadow-[#E85D3E]/20' : 'bg-slate-50 border-slate-100 text-slate-400 hover:border-slate-300'" class="p-6 border rounded-2xl flex flex-col items-center justify-center gap-3 transition-all">
                         <span class="font-black text-xs uppercase tracking-widest">Général & HR</span>
                         <UserCircleIcon class="w-6 h-6" />
                      </button>
                      <button @click="config.interviewType = 'technical'" :class="config.interviewType === 'technical' ? 'bg-[#E85D3E] border-[#E85D3E] text-white shadow-xl shadow-[#E85D3E]/20' : 'bg-slate-50 border-slate-100 text-slate-400 hover:border-slate-300'" class="p-6 border rounded-2xl flex flex-col items-center justify-center gap-3 transition-all">
                         <span class="font-black text-xs uppercase tracking-widest">Technique</span>
                         <CpuChipIcon class="w-6 h-6" />
                      </button>
                  </div>
              </div>
         </div>
      </div>"""

# Replace the old form block
# The old block starts with <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
form_pattern = r'<div class="grid grid-cols-1 lg:grid-cols-2 gap-8">.*?</div>\s*</div>\s*</div>'
# Wait, I need to be careful with nested divs.
# I'll look for a more specific end point.
# The block ends before <div v-if="errorMsg"
form_pattern = r'<div class="grid grid-cols-1 lg:grid-cols-2 gap-8">.*?<div v-if="errorMsg"'
content = re.sub(form_pattern, bento_form + '\n\n      <div v-if="errorMsg"', content, flags=re.DOTALL)

# 4. Redesign Footer & Actions
wizard_footer = """      <!-- FOOTER ACTIONS -->
      <div class="mt-4 pt-10 border-t border-slate-200 flex flex-col md:flex-row items-center justify-between gap-6">
          <div class="flex items-center gap-6">
              <button @click="testAudio" class="px-6 py-3 bg-white border border-slate-200 text-slate-900 text-xs font-black rounded-2xl hover:border-[#E85D3E]/30 transition-all flex items-center gap-3 shadow-sm">
                  <SpeakerWaveIcon class="w-4 h-4 text-[#E85D3E]" />
                  Tester le son
              </button>
              <div class="flex flex-col">
                <span class="text-[9px] text-slate-400 uppercase font-black tracking-widest mb-1">Système Audio</span>
                <span v-if="ttsStatus" class="text-[10px] text-slate-900 font-bold uppercase">{{ ttsStatus }}</span>
              </div>
          </div>
          <button @click="startInterview" class="w-full md:w-auto px-10 py-5 bg-gradient-to-r from-[#E85D3E] to-[#C44A2D] hover:from-[#C44A2D] hover:to-[#E85D3E] text-white font-black rounded-[2rem] shadow-2xl shadow-[#E85D3E]/30 flex items-center justify-center gap-4 transition-all hover:scale-[1.02] active:scale-95 text-base uppercase tracking-widest">
              Lancer la Visioconférence
              <VideoCameraIcon class="w-6 h-6" />
          </button>
      </div>
    </div>"""

# Find the old footer and replace it
# The old footer starts with <div class="mt-8 pt-8 border-t border-surface-800
footer_pattern = r'<div class="mt-8 pt-8 border-t border-surface-800 flex items-center justify-between">.*?</div>\s*</div>'
content = re.sub(footer_pattern, wizard_footer, content, flags=re.DOTALL)

# 5. Fix any remaining surface-900/800 colors in wizard (like error message and paywall)
content = content.replace('bg-rose-500/10 border border-rose-500/20 text-rose-400', 'bg-rose-50 border border-rose-100 text-rose-500')
content = content.replace('bg-gradient-to-br from-indigo-900/40 to-purple-900/40 border border-indigo-500/40', 'bg-indigo-50 border border-indigo-100')
content = content.replace('text-white text-lg', 'text-slate-900 text-lg')
content = content.replace('text-slate-400 text-sm mt-1', 'text-slate-500 text-sm mt-1')

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print("done")
