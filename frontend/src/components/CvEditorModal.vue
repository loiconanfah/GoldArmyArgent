<template>
  <div v-if="show" class="fixed inset-0 z-50 flex items-center justify-center p-4">
    <div class="absolute inset-0 bg-slate-900/60 backdrop-blur-sm" @click="close"></div>
    <div class="relative w-full max-w-4xl bg-white rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
      <!-- Header -->
      <div class="flex items-center justify-between px-6 py-4 border-b border-slate-100 bg-slate-50">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-[#F59E0B] to-[#C44A2D] flex items-center justify-center text-white">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
              <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />
            </svg>
          </div>
          <div>
            <h3 class="text-lg font-black text-slate-900">Éditeur de CV</h3>
            <p class="text-xs text-slate-500">Modifiez le contenu avant l'export PDF</p>
          </div>
        </div>
        <button @click="close" class="text-slate-400 hover:text-slate-600 transition-colors p-2">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- Navigation Tabs -->
      <div class="flex overflow-x-auto border-b border-slate-100 bg-white shrink-0 scrollbar-hide">
        <button v-for="tab in tabs" :key="tab.id" @click="activeTab = tab.id"
          class="px-6 py-3 text-sm font-bold border-b-2 transition-colors whitespace-nowrap"
          :class="activeTab === tab.id ? 'border-[#F59E0B] text-[#F59E0B]' : 'border-transparent text-slate-500 hover:text-slate-700'">
          {{ tab.label }}
        </button>
      </div>

      <!-- Content Editor -->
      <div class="flex-1 overflow-y-auto p-6 bg-slate-50/50">
        
        <!-- Informations personnelles -->
        <div v-show="activeTab === 'info'" class="space-y-6">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="space-y-1">
              <label class="text-xs font-bold text-slate-500 uppercase tracking-wider">Nom complet</label>
              <input v-model="localCv.full_name" type="text" class="w-full px-4 py-2 bg-white border border-slate-200 rounded-xl focus:ring-2 focus:ring-[#F59E0B] focus:border-transparent outline-none transition-all">
            </div>
            <div class="space-y-1">
              <label class="text-xs font-bold text-slate-500 uppercase tracking-wider">Titre / Poste</label>
              <input v-model="localCv.title" type="text" class="w-full px-4 py-2 bg-white border border-slate-200 rounded-xl focus:ring-2 focus:ring-[#F59E0B] focus:border-transparent outline-none transition-all">
            </div>
            <div class="space-y-1">
              <label class="text-xs font-bold text-slate-500 uppercase tracking-wider">Email</label>
              <input v-model="localCv.email" type="email" class="w-full px-4 py-2 bg-white border border-slate-200 rounded-xl focus:ring-2 focus:ring-[#F59E0B] focus:border-transparent outline-none transition-all">
            </div>
            <div class="space-y-1">
              <label class="text-xs font-bold text-slate-500 uppercase tracking-wider">Téléphone</label>
              <input v-model="localCv.phone" type="text" class="w-full px-4 py-2 bg-white border border-slate-200 rounded-xl focus:ring-2 focus:ring-[#F59E0B] focus:border-transparent outline-none transition-all">
            </div>
            <div class="space-y-1">
              <label class="text-xs font-bold text-slate-500 uppercase tracking-wider">Localisation</label>
              <input v-model="localCv.location" type="text" class="w-full px-4 py-2 bg-white border border-slate-200 rounded-xl focus:ring-2 focus:ring-[#F59E0B] focus:border-transparent outline-none transition-all">
            </div>
            <div class="space-y-1">
              <label class="text-xs font-bold text-slate-500 uppercase tracking-wider">LinkedIn URL</label>
              <input v-model="localCv.linkedin" type="text" class="w-full px-4 py-2 bg-white border border-slate-200 rounded-xl focus:ring-2 focus:ring-[#F59E0B] focus:border-transparent outline-none transition-all">
            </div>
          </div>
          <div class="space-y-1">
            <label class="text-xs font-bold text-slate-500 uppercase tracking-wider">Résumé / Profil professionnel</label>
            <textarea v-model="localCv.summary" rows="5" class="w-full px-4 py-3 bg-white border border-slate-200 rounded-xl focus:ring-2 focus:ring-[#F59E0B] focus:border-transparent outline-none transition-all resize-y"></textarea>
          </div>
        </div>

        <!-- Expériences -->
        <div v-show="activeTab === 'experiences'" class="space-y-8">
          <div v-if="!localCv.experiences || localCv.experiences.length === 0" class="text-center text-slate-400 py-8">
            Aucune expérience ajoutée.
          </div>
          <div v-for="(exp, index) in localCv.experiences" :key="index" class="p-5 bg-white border border-slate-100 rounded-2xl shadow-sm space-y-4">
            <div class="flex justify-between items-start">
              <h4 class="font-bold text-slate-800">Expérience #{{ index + 1 }}</h4>
              <button @click="removeExperience(index)" class="text-red-400 hover:text-red-600 text-xs font-bold">Retirer</button>
            </div>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4" v-if="typeof exp === 'object'">
              <div class="space-y-1">
                <label class="text-[10px] font-bold text-slate-400 uppercase">Titre du poste</label>
                <input v-model="exp.title" type="text" class="w-full px-3 py-1.5 text-sm bg-slate-50 border border-slate-200 rounded-lg outline-none focus:border-[#F59E0B]">
              </div>
              <div class="space-y-1">
                <label class="text-[10px] font-bold text-slate-400 uppercase">Entreprise</label>
                <input v-model="exp.company" type="text" class="w-full px-3 py-1.5 text-sm bg-slate-50 border border-slate-200 rounded-lg outline-none focus:border-[#F59E0B]">
              </div>
              <div class="space-y-1">
                <label class="text-[10px] font-bold text-slate-400 uppercase">Date début</label>
                <input v-model="exp.start_date" type="text" class="w-full px-3 py-1.5 text-sm bg-slate-50 border border-slate-200 rounded-lg outline-none focus:border-[#F59E0B]">
              </div>
              <div class="space-y-1">
                <label class="text-[10px] font-bold text-slate-400 uppercase">Date fin</label>
                <input v-model="exp.end_date" type="text" class="w-full px-3 py-1.5 text-sm bg-slate-50 border border-slate-200 rounded-lg outline-none focus:border-[#F59E0B]">
              </div>
            </div>
            
            <div class="space-y-2" v-if="typeof exp === 'object' && exp.bullets">
              <label class="text-[10px] font-bold text-slate-400 uppercase">Description (Bullet points)</label>
              <div v-for="(bullet, bIndex) in exp.bullets" :key="bIndex" class="flex gap-2">
                <textarea v-model="exp.bullets[bIndex]" rows="2" class="flex-1 px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-lg outline-none focus:border-[#F59E0B] resize-none"></textarea>
                <button @click="removeBullet(exp, bIndex)" class="p-2 text-slate-400 hover:text-red-500 rounded-lg shrink-0">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" /></svg>
                </button>
              </div>
              <button @click="addBullet(exp)" class="text-xs text-[#F59E0B] font-bold hover:underline">+ Ajouter une ligne</button>
            </div>
          </div>
          <button @click="addExperience" class="w-full py-3 border-2 border-dashed border-[#F59E0B]/30 text-[#F59E0B] rounded-2xl font-bold hover:bg-[#F59E0B]/5 transition-colors">+ Ajouter une expérience</button>
        </div>

        <!-- Formations -->
        <div v-show="activeTab === 'education'" class="space-y-6">
          <div v-for="(edu, index) in localCv.education" :key="index" class="p-5 bg-white border border-slate-100 rounded-2xl shadow-sm space-y-4">
             <div class="flex justify-between items-start">
              <h4 class="font-bold text-slate-800">Formation #{{ index + 1 }}</h4>
              <button @click="removeEducation(index)" class="text-red-400 hover:text-red-600 text-xs font-bold">Retirer</button>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4" v-if="typeof edu === 'object'">
              <div class="space-y-1">
                <label class="text-[10px] font-bold text-slate-400 uppercase">Diplôme / Certificat</label>
                <input v-model="edu.degree" type="text" class="w-full px-3 py-1.5 text-sm bg-slate-50 border border-slate-200 rounded-lg outline-none focus:border-[#F59E0B]">
              </div>
              <div class="space-y-1">
                <label class="text-[10px] font-bold text-slate-400 uppercase">Établissement</label>
                <input v-model="edu.institution" type="text" class="w-full px-3 py-1.5 text-sm bg-slate-50 border border-slate-200 rounded-lg outline-none focus:border-[#F59E0B]">
              </div>
              <div class="space-y-1">
                <label class="text-[10px] font-bold text-slate-400 uppercase">Année</label>
                <input v-model="edu.year" type="text" class="w-full px-3 py-1.5 text-sm bg-slate-50 border border-slate-200 rounded-lg outline-none focus:border-[#F59E0B]">
              </div>
            </div>
          </div>
          <button @click="addEducation" class="w-full py-3 border-2 border-dashed border-[#F59E0B]/30 text-[#F59E0B] rounded-2xl font-bold hover:bg-[#F59E0B]/5 transition-colors">+ Ajouter une formation</button>
        </div>

        <!-- Compétences (JSON Brut pour simplifier vue que la structure varie) -->
        <div v-show="activeTab === 'skills'" class="space-y-6">
           <div class="p-4 bg-amber-50 text-amber-800 rounded-xl text-sm mb-4">
              <p class="font-bold">Mode Édition Avancée (JSON)</p>
              <p>Éditez directement la structure des compétences et des langues ci-dessous.</p>
           </div>
           
           <div class="space-y-2">
             <label class="text-xs font-bold text-slate-500 uppercase tracking-wider">Compétences</label>
             <textarea v-model="skillsJsonStr" rows="8" class="w-full font-mono text-sm px-4 py-3 bg-slate-800 text-emerald-400 rounded-xl focus:ring-2 focus:ring-[#F59E0B] outline-none"></textarea>
             <p v-if="skillsError" class="text-xs text-red-500">{{ skillsError }}</p>
           </div>
           
           <div class="space-y-2">
             <label class="text-xs font-bold text-slate-500 uppercase tracking-wider">Langues</label>
             <textarea v-model="langsJsonStr" rows="5" class="w-full font-mono text-sm px-4 py-3 bg-slate-800 text-emerald-400 rounded-xl focus:ring-2 focus:ring-[#F59E0B] outline-none"></textarea>
             <p v-if="langsError" class="text-xs text-red-500">{{ langsError }}</p>
           </div>
        </div>

      </div>

      <!-- Footer Actions -->
      <div class="p-4 border-t border-slate-100 bg-white flex justify-end gap-3 shrink-0">
        <button @click="close" class="px-6 py-2.5 text-slate-500 font-bold hover:bg-slate-50 rounded-xl transition-colors">Annuler</button>
        <button @click="save" class="px-8 py-2.5 bg-[#F59E0B] text-white font-black rounded-xl shadow-lg shadow-[#F59E0B]/30 hover:bg-[#C44A2D] transition-all transform active:scale-95">
          Enregistrer les modifications
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  show: Boolean,
  cvData: Object
})

const emit = defineEmits(['close', 'save'])

const activeTab = ref('info')
const tabs = [
  { id: 'info', label: 'Profil & Résumé' },
  { id: 'experiences', label: 'Expériences' },
  { id: 'education', label: 'Formations' },
  { id: 'skills', label: 'Compétences & Langues' }
]

const localCv = ref({})
const skillsJsonStr = ref('')
const langsJsonStr = ref('')
const skillsError = ref('')
const langsError = ref('')

watch(() => props.show, (newVal) => {
  if (newVal && props.cvData) {
    // Clone profond simple
    localCv.value = JSON.parse(JSON.stringify(props.cvData))
    if (!localCv.value.experiences) localCv.value.experiences = []
    if (!localCv.value.education) localCv.value.education = []
    
    // Pour les compétences et langues (structures variables), on utilise un éditeur JSON
    skillsJsonStr.value = JSON.stringify(localCv.value.skills || {}, null, 2)
    langsJsonStr.value = JSON.stringify(localCv.value.languages || [], null, 2)
    skillsError.value = ''
    langsError.value = ''
    activeTab.value = 'info'
  }
})

// Expériences actions
const addExperience = () => {
  localCv.value.experiences.push({
    title: '', company: '', start_date: '', end_date: '', bullets: ['']
  })
}
const removeExperience = (idx) => localCv.value.experiences.splice(idx, 1)
const addBullet = (exp) => {
  if (!exp.bullets) exp.bullets = []
  exp.bullets.push('')
}
const removeBullet = (exp, idx) => exp.bullets.splice(idx, 1)

// Formations actions
const addEducation = () => {
  localCv.value.education.push({ degree: '', institution: '', year: '' })
}
const removeEducation = (idx) => localCv.value.education.splice(idx, 1)


const close = () => {
  emit('close')
}

const save = () => {
  // Validate JSON blocks
  try {
    if (!skillsJsonStr.value.trim()) skillsJsonStr.value = '{}'
    localCv.value.skills = JSON.parse(skillsJsonStr.value)
    skillsError.value = ''
  } catch (e) {
    skillsError.value = "Format JSON invalide pour les compétences. Corrigez-le avant de sauvegarder."
    activeTab.value = 'skills'
    return
  }
  
  try {
    if (!langsJsonStr.value.trim()) langsJsonStr.value = '[]'
    localCv.value.languages = JSON.parse(langsJsonStr.value)
    langsError.value = ''
  } catch (e) {
    langsError.value = "Format JSON invalide pour les langues. Corrigez-le avant de sauvegarder."
    activeTab.value = 'skills'
    return
  }

  // Si tout est ok, on sauvegarde
  emit('save', JSON.parse(JSON.stringify(localCv.value)))
  close()
}
</script>
<style scoped>
.scrollbar-hide::-webkit-scrollbar {
  display: none;
}
</style>
