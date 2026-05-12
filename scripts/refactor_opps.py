import re

path = 'c:/Users/Utilisateur/PycharmProjects/GoldArmyArgent/frontend/src/views/Opportunities.vue'

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update Imports
imports_replacement = """import { 
    BriefcaseIcon, 
    FunnelIcon, 
    MapPinIcon, 
    CurrencyDollarIcon, 
    CheckCircleIcon,
    MagnifyingGlassIcon,
    DocumentTextIcon,
    ArrowPathIcon,
    SparklesIcon,
    ArrowUpTrayIcon,
    XMarkIcon
} from '@heroicons/vue/24/outline'
import { CV_TEMPLATES } from '../utils/cvTemplates/index'"""
content = re.sub(r"import \{.*?\} from '@heroicons/vue/24/outline'", imports_replacement, content, flags=re.DOTALL)

# 2. Add CV_THEMES and local modal refs
refs_addition = """
const CV_THEMES = CV_TEMPLATES.map(t => ({
  id: t.id,
  name: t.label,
  colors: [t.accentColor, t.accentColor],
  build: t.build,
}))

const showAdaptCvModal = ref(false)
const adaptCvCard = ref(null)
const cvTextForAdapt = ref('')
const isAdaptingCv = ref(false)
const adaptedData = ref(null)
const adaptCvFileInput = ref(null)

const showDownloadCvModal = ref(false)
const selectedCvTheme = ref('goldarmy')
const isDownloadingPdf = ref(false)
"""

# Insert refs_addition before `const { t } = useI18n()`
content = content.replace("const { t } = useI18n()", refs_addition + "\nconst { t } = useI18n()")

# 3. Replace the old `adaptCV` and `saveAdaptedToProfile` and `closeAdaptModal` logic
old_logic_pattern = r"const adaptCV = async \(job\) => \{.*?const closeAdaptModal = \(\) => \{.*?\}\n"
new_logic = """
const openAdaptCvModal = (job) => {
  adaptCvCard.value = job
  cvTextForAdapt.value = ''
  adaptedData.value = null
  showAdaptCvModal.value = true
  showDownloadCvModal.value = false
}

const useProfileCv = async () => {
  if (!adaptCvCard.value) return
  try {
    const res = await authFetch('/api/profile')
    const json = await res.json()
    const cvText = json?.data?.cv_text
    if (!cvText || cvText.length < 50) {
      toastState.addToast('Aucun CV enregistré dans votre profil. Uploadez un CV d\\'abord.', 'info')
      return
    }
    cvTextForAdapt.value = cvText
    await runAdapt()
  } catch (e) {
    toastState.addToast(t('common.network_error'), 'error')
  }
}

const onAdaptFileSelected = async (e) => {
  const file = e.target?.files?.[0]
  if (!file || !file.name.toLowerCase().endsWith('.pdf')) {
    toastState.addToast('Veuillez sélectionner un fichier PDF.', 'info')
    return
  }
  const formData = new FormData()
  formData.append('file', file)
  try {
    const res = await authFetch('/api/parse-pdf', { method: 'POST', body: formData })
    const json = await res.json()
    const text = json?.text
    if (!text || text.length < 50) {
      toastState.addToast('Impossible de lire le PDF ou fichier trop court.', 'error')
      return
    }
    cvTextForAdapt.value = text
    await runAdapt()
  } catch (err) {
    toastState.addToast(t('common.network_error'), 'error')
  }
  e.target.value = ''
}

const runAdapt = async () => {
  if (!adaptCvCard.value || !cvTextForAdapt.value || cvTextForAdapt.value.length < 50) {
    toastState.addToast('CV manquant ou trop court.', 'info')
    return
  }
  isAdaptingCv.value = true
  try {
    const res = await authFetch('/api/adapt-cv', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        job_title: adaptCvCard.value.title,
        job_description: adaptCvCard.value.desc,
        cv_text: cvTextForAdapt.value
      })
    })
    const json = await res.json()
    if (json.status === 'success' && json.data) {
      adaptedData.value = json.data
      showAdaptCvModal.value = false
      showDownloadCvModal.value = true
      selectedCvTheme.value = 'goldarmy'
    } else {
      toastState.addToast(json.detail || t('opportunities.adapt_error') || "Erreur lors de l'adaptation.", 'error')
    }
  } catch (e) {
    toastState.addToast(t('common.network_error'), 'error')
  } finally {
    isAdaptingCv.value = false
  }
}

const closeAdaptCvModal = () => {
  showAdaptCvModal.value = false
  adaptCvCard.value = null
  cvTextForAdapt.value = ''
  adaptedData.value = null
}

const buildCvJsonFromMarkdown = (markdown) => {
  const lines = (markdown || '').split(/\\n/).filter(Boolean)
  const fullName = lines[0]?.replace(/^#+\\s*/, '').trim() || 'Candidat'
  return {
    full_name: fullName,
    summary: '',
    experiences: [{ title: 'Expérience professionnelle', company: '', start_date: '', end_date: '', bullets: lines }],
    skills: {},
    education: []
  }
}

const downloadAdaptedPdf = async () => {
  if (!adaptedData.value?.markdown && !adaptedData.value?.cv_json) return
  isDownloadingPdf.value = true
  try {
    let cvJson = null;
    if (adaptedData.value.cv_json) {
        if (typeof adaptedData.value.cv_json === 'object') {
            cvJson = adaptedData.value.cv_json;
        } else if (typeof adaptedData.value.cv_json === 'string') {
            try {
                cvJson = JSON.parse(adaptedData.value.cv_json);
            } catch (e) {
                console.warn("Failed to parse cv_json string, falling back to markdown", e);
            }
        }
    }
    
    if (!cvJson) {
        cvJson = buildCvJsonFromMarkdown(adaptedData.value.markdown || '');
    }

    const filename = `CV_Adapte_${(adaptCvCard.value?.title || 'offre').replace(/\\s+/g, '_').slice(0, 30)}`

    // Use the mobile-identical JS templates for consistent design
    const tpl = CV_THEMES.find(t => t.id === selectedCvTheme.value) || CV_THEMES[0]
    const html = tpl.build(cvJson, null)

    const res = await authFetch('/api/generate-cv-pdf-html', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ html, filename })
    })
    if (!res.ok) {
      const err = await res.json()
      toastState.addToast(err.detail || 'Erreur génération PDF', 'error')
      return
    }
    const blob = await res.blob()
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = filename + '.pdf'
    a.click()
    URL.revokeObjectURL(url)
    toastState.addToast('CV téléchargé.', 'success')
    showDownloadCvModal.value = false
    adaptedData.value = null
  } catch (e) {
    toastState.addToast('Erreur lors du téléchargement.', 'error')
  } finally {
    isDownloadingPdf.value = false
  }
}

const closeDownloadCvModal = () => {
  showDownloadCvModal.value = false
  adaptedData.value = null
}
"""
content = re.sub(old_logic_pattern, lambda m: new_logic, content, flags=re.DOTALL)


# 4. Replace the old Job Cards grid
old_cards_pattern = r"<!-- Job Cards List \(Bento Box style Solid\) -->.*?</div>\s*<!-- AI CV Adaptation Modal -->"

new_cards = """<!-- Job Cards List (Premium SaaS Style) -->
    <div v-else class="grid grid-cols-1 lg:grid-cols-2 gap-6 pb-20">
       <div 
         v-for="(job, index) in filteredJobs" 
         :key="job.id"
         class="relative bg-surface-900 border border-surface-800 p-6 rounded-3xl transition-all hover:border-surface-600 shadow-xl shadow-black/20 group flex flex-col justify-between overflow-hidden"
         :style="`animation-delay: ${index * 50}ms`"
         style="animation: fadeInUp 0.5s ease-out forwards; opacity: 0;"
       >
          <!-- Subtle glow effect on hover -->
          <div class="absolute inset-0 bg-gradient-to-br from-gold-500/0 to-amber-500/0 group-hover:from-gold-500/5 group-hover:to-amber-500/5 transition-colors pointer-events-none"></div>

          <div class="relative z-10">
              <!-- Header Card -->
              <div class="flex items-start justify-between gap-4 mb-5">
                  <div class="flex-1 min-w-0">
                      <!-- Tags -->
                      <div class="flex flex-wrap gap-2 mb-4">
                        <span class="text-[10px] font-black uppercase tracking-wider text-gold-400 bg-gold-400/10 border border-gold-400/20 px-3 py-1.5 rounded-xl">
                            {{ job.type }}
                        </span>
                        <span class="text-xs font-semibold text-slate-300 bg-surface-800 border border-surface-700 px-3 py-1.5 rounded-xl flex items-center gap-1.5">
                            <MapPinIcon class="w-3.5 h-3.5 text-slate-500" />
                            {{ job.location }}
                        </span>
                      </div>
                      
                      <h3 class="text-2xl font-display font-black text-white leading-tight mb-2 truncate group-hover:text-gold-400 transition-colors" :title="job.title">
                          {{ job.title }}
                      </h3>
                      <div class="flex items-center gap-2.5 text-slate-400 font-medium">
                          <span class="w-7 h-7 rounded-lg bg-surface-800 flex items-center justify-center text-xs font-bold text-white border border-surface-700 shadow-inner">
                              {{ job.company.charAt(0).toUpperCase() }}
                          </span>
                          <span class="truncate">{{ job.company }}</span>
                      </div>
                  </div>
                  
                  <!-- Circular Progress Score -->
                  <div class="shrink-0 relative w-16 h-16 flex items-center justify-center bg-surface-950 rounded-2xl shadow-inner ring-1 ring-surface-800">
                      <!-- SVG Circle Background -->
                      <svg class="absolute inset-0 w-full h-full transform -rotate-90">
                          <circle cx="50%" cy="50%" r="40%" stroke="currentColor" stroke-width="8%" fill="transparent" class="text-surface-800" />
                          <circle cx="50%" cy="50%" r="40%" stroke="currentColor" stroke-width="8%" fill="transparent" 
                                  :stroke-dasharray="2 * Math.PI * 40" 
                                  :stroke-dashoffset="2 * Math.PI * 40 * (1 - job.matchScore / 100)"
                                  stroke-linecap="round"
                                  :class="job.matchScore >= 80 ? 'text-emerald-500' : (job.matchScore >= 50 ? 'text-gold-500' : 'text-slate-500')"
                                  class="transition-all duration-1000 ease-out" />
                      </svg>
                      <div class="text-center z-10 flex flex-col items-center">
                          <span class="block text-lg font-black leading-none" :class="job.matchScore >= 80 ? 'text-white' : 'text-slate-300'">
                              {{ job.matchScore }}<span class="text-[10px] text-slate-500 font-bold">%</span>
                          </span>
                      </div>
                  </div>
              </div>
              
              <!-- Description Snippet -->
              <p class="text-[13px] text-slate-400 line-clamp-3 leading-relaxed mb-6 font-medium">
                {{ job.desc }}
              </p>
          </div>
          
          <!-- Card Footer Actions -->
          <div class="relative z-10 flex items-center gap-3 pt-5 border-t border-surface-800/80 mt-auto">
             <button 
                v-if="job.rawUrl" 
                @click="addToCrmAndApply(job)"
                class="flex-1 flex items-center justify-center gap-2 bg-indigo-500 hover:bg-indigo-400 text-white px-4 py-3.5 rounded-xl font-bold text-sm transition-all shadow-lg shadow-indigo-500/20 active:scale-95 outline-none">
                {{ t('opportunities.apply') }}
             </button>
             <button disabled class="flex-1 bg-surface-800 text-slate-500 px-4 py-3.5 rounded-xl font-bold text-sm cursor-not-allowed" v-else>
                 {{ t('opportunities.dead_link') }}
             </button>
             
             <!-- AI Adapt CV Button -->
             <button 
                @click="openAdaptCvModal(job)"
                class="flex-1 flex items-center justify-center gap-2 bg-gradient-to-r from-gold-500/10 to-amber-500/10 hover:from-gold-500/20 hover:to-amber-500/20 text-gold-400 px-4 py-3.5 rounded-xl font-bold text-sm transition-all border border-gold-500/20 hover:border-gold-500/40 active:scale-95 outline-none group/adapt">
                <SparklesIcon class="w-5 h-5 text-gold-500 group-hover/adapt:scale-110 transition-transform" />
                <span class="hidden sm:inline">{{ t('opportunities.adapt_cv') }}</span>
             </button>
             
             <button 
                @click="runRadar(job)"
                :disabled="loadingRadarFor === job.id"
                class="flex items-center justify-center bg-surface-800 hover:bg-surface-700 disabled:opacity-50 text-slate-300 w-12 h-12 rounded-xl transition-colors border border-surface-700 active:scale-95 outline-none group/radar shrink-0">
                <ArrowPathIcon v-if="loadingRadarFor === job.id" class="w-5 h-5 animate-spin text-gold-400" />
                <svg v-else class="w-5 h-5 text-slate-400 group-hover/radar:text-white transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
             </button>
          </div>
       </div>
    </div>
    
    <!-- AI CV Adaptation Modal -->"""
content = re.sub(old_cards_pattern, lambda m: new_cards, content, flags=re.DOTALL)


# 5. Replace Old AI CV Adaptation Modal with the 2 new Modals
old_modal_pattern = r"<!-- AI CV Adaptation Modal -->.*?</div>\s*</div>\s*</template>"

new_modals = """
    <!-- ═══ POPUP 1 : Adapter le CV – Choix du CV (upload ou profil) ═══ -->
    <div v-if="showAdaptCvModal" class="fixed inset-0 z-[200] flex items-center justify-center p-4">
      <div class="absolute inset-0 bg-black/70 backdrop-blur-sm" @click="closeAdaptCvModal"></div>
      <div class="relative z-10 bg-surface-900 border border-surface-700 rounded-3xl shadow-2xl w-full max-w-md overflow-hidden" style="animation: scale-in 0.2s ease-out forwards;">
        <div class="px-6 pt-6 pb-4 border-b border-surface-800 flex items-center justify-between">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-xl bg-amber-500/10 flex items-center justify-center">
              <SparklesIcon class="w-5 h-5 text-amber-400" />
            </div>
            <div>
              <h3 class="font-bold text-white">Adapter le CV pour cette offre</h3>
              <p class="text-xs text-slate-500 mt-0.5">{{ adaptCvCard?.title }} — {{ adaptCvCard?.company }}</p>
            </div>
          </div>
          <button @click="closeAdaptCvModal" class="p-1.5 text-slate-500 hover:text-white rounded-lg hover:bg-surface-800"><XMarkIcon class="w-5 h-5" /></button>
        </div>
        <div class="p-6">
          <div v-if="isAdaptingCv" class="flex flex-col items-center py-10 gap-4">
            <ArrowPathIcon class="w-12 h-12 text-amber-500 animate-spin" />
            <p class="text-sm font-bold text-white">Adaptation en cours (conformité ~95% à l'offre)...</p>
          </div>
          <div v-else class="space-y-4">
            <p class="text-sm text-slate-400">Choisissez le CV à adapter :</p>
            <input ref="adaptCvFileInput" type="file" accept=".pdf" class="hidden" @change="onAdaptFileSelected" />
            <button type="button" @click="adaptCvFileInput?.click()" class="w-full flex items-center justify-center gap-3 px-5 py-4 rounded-xl border-2 border-dashed border-surface-600 hover:border-amber-500/50 bg-surface-800/50 text-slate-300 hover:text-amber-400 transition-all">
              <ArrowUpTrayIcon class="w-6 h-6" />
              <span class="font-bold">Uploader un CV (PDF)</span>
            </button>
            <button type="button" @click="useProfileCv" class="w-full flex items-center justify-center gap-3 px-5 py-4 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-400 hover:bg-amber-500/20 transition-all font-bold">
              <DocumentTextIcon class="w-6 h-6" />
              Utiliser le CV du profil
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- ═══ POPUP 2 : Choisir le modèle et télécharger le CV adapté ═══ -->
    <div v-if="showDownloadCvModal" class="fixed inset-0 z-[200] flex items-center justify-center p-4">
      <div class="absolute inset-0 bg-black/70 backdrop-blur-sm" @click="closeDownloadCvModal"></div>
      <div class="relative z-10 bg-surface-900 border border-surface-700 rounded-3xl shadow-2xl w-full max-w-lg overflow-hidden" style="animation: scale-in 0.2s ease-out forwards;">
        <div class="px-6 pt-6 pb-4 border-b border-surface-800 flex items-center justify-between">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-xl bg-emerald-500/10 flex items-center justify-center">
              <DocumentTextIcon class="w-5 h-5 text-emerald-400" />
            </div>
            <div>
              <h3 class="font-bold text-white">Télécharger le CV adapté</h3>
              <p class="text-xs text-slate-500 mt-0.5">Choisissez un modèle puis téléchargez le PDF</p>
            </div>
          </div>
          <button @click="closeDownloadCvModal" class="p-1.5 text-slate-500 hover:text-white rounded-lg hover:bg-surface-800"><XMarkIcon class="w-5 h-5" /></button>
        </div>
        <div class="p-6 space-y-6">
          <div v-if="adaptedData?.markdown" class="max-h-32 overflow-y-auto custom-scrollbar rounded-xl bg-surface-950 border border-surface-800 p-4 text-sm text-slate-400 whitespace-pre-wrap">{{ adaptedData.markdown.slice(0, 400) }}{{ adaptedData.markdown.length > 400 ? '…' : '' }}</div>
          <div>
            <p class="text-xs font-bold text-slate-500 uppercase tracking-wider mb-3">Modèle du CV</p>
            <div class="flex flex-wrap gap-2">
              <button v-for="theme in CV_THEMES" :key="theme.id" type="button" @click="selectedCvTheme = theme.id"
                class="h-10 w-10 rounded-lg border-2 transition-all overflow-hidden shrink-0"
                :class="selectedCvTheme === theme.id ? 'border-amber-500 ring-2 ring-amber-500/30' : 'border-surface-700 hover:border-surface-600'">
                <div class="flex w-full h-full">
                  <div class="w-1/2 h-full" :style="{ backgroundColor: theme.colors[0] }"></div>
                  <div class="w-1/2 h-full" :style="{ backgroundColor: theme.colors[1] }"></div>
                </div>
              </button>
            </div>
            <p class="text-[11px] text-slate-500 mt-2">{{ CV_THEMES.find(th => th.id === selectedCvTheme)?.name }}</p>
          </div>
          <button @click="downloadAdaptedPdf" :disabled="isDownloadingPdf"
            class="w-full flex items-center justify-center gap-2 px-5 py-3.5 bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 disabled:opacity-60 text-surface-950 font-bold rounded-xl shadow-lg transition-all">
            <ArrowUpTrayIcon v-if="!isDownloadingPdf" class="w-5 h-5 rotate-180" />
            <ArrowPathIcon v-else class="w-5 h-5 animate-spin" />
            {{ isDownloadingPdf ? 'Génération…' : 'Télécharger le PDF' }}
          </button>
        </div>
      </div>
    </div>
    
  </div>
</template>

<style scoped>
.custom-scrollbar::-webkit-scrollbar { width: 4px; }
.custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: #1e293b; border-radius: 10px; }
.custom-scrollbar::-webkit-scrollbar-thumb:hover { background: #475569; }

@keyframes scale-in {
  from { transform: scale(0.94); opacity: 0; }
  to { transform: scale(1); opacity: 1; }
}
</style>
"""
content = re.sub(old_modal_pattern, lambda m: new_modals, content, flags=re.DOTALL)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print("done")
