<script setup>
// Étape conversationnelle avant génération du CV : l'IA pose des questions
// ciblées (chiffres réels, réalisations, niveau, focus), le candidat répond,
// et ses réponses guident une rédaction juste, sans invention.
import { ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { authFetch } from '../utils/auth'
import { XMarkIcon, SparklesIcon, ChartBarIcon, TrophyIcon, AcademicCapIcon, FlagIcon } from '@heroicons/vue/24/outline'

const { t } = useI18n()
const props = defineProps({
  show: { type: Boolean, default: false },
  jobTitle: { type: String, default: '' },
  jobDescription: { type: String, default: '' },
  cvText: { type: String, default: '' },
})
const emit = defineEmits(['close', 'submit'])

const loading = ref(false)
const questions = ref([])
const answers = ref({})
const errorMsg = ref('')

// Étape 2 : compétences proposées (détectées dans le CV, à cocher)
const step = ref('questions')          // 'questions' | 'skills'
const skillsLoading = ref(false)
const skillCats = ref([])              // [{ category, skills: [...] }]
const skillChecked = ref({})           // { "Compétence": true/false }

const CAT_ICON = { metrics: ChartBarIcon, achievement: TrophyIcon, seniority: AcademicCapIcon, focus: FlagIcon }
function catIcon(c) { return CAT_ICON[c] || SparklesIcon }
function catLabel(c) { return t('cvq.cat_' + (CAT_ICON[c] ? c : 'focus')) }

async function loadQuestions() {
  loading.value = true
  errorMsg.value = ''
  questions.value = []
  answers.value = {}
  step.value = 'questions'
  skillCats.value = []
  skillChecked.value = {}
  try {
    const res = await authFetch('/api/adapt-cv/questions', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ job_title: props.jobTitle, job_description: props.jobDescription, cv_text: props.cvText }),
    })
    const json = await res.json()
    if (json?.status === 'success' && json.data?.questions?.length) {
      questions.value = json.data.questions
    } else {
      errorMsg.value = json?.detail || t('common.error')
    }
  } catch (e) {
    errorMsg.value = t('common.network_error')
  } finally {
    loading.value = false
  }
}

watch(() => props.show, (v) => { if (v) loadQuestions() })

// Passe à l'étape "compétences" : détecte les compétences réelles du CV et les propose.
async function goToSkills() {
  skillsLoading.value = true
  step.value = 'skills'
  try {
    const res = await authFetch('/api/adapt-cv/skills', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ job_title: props.jobTitle, job_description: props.jobDescription, cv_text: props.cvText }),
    })
    const json = await res.json()
    const cats = (json?.status === 'success' && json.data?.categories) ? json.data.categories : []
    skillCats.value = cats
    const checked = {}
    for (const c of cats) for (const s of (c.skills || [])) checked[s] = true  // pré-cochées
    skillChecked.value = checked
    // Aucune compétence détectée → on génère directement, pas d'étape vide.
    if (!cats.length) generate()
  } catch (e) {
    skillCats.value = []
    generate()
  } finally {
    skillsLoading.value = false
  }
}

function buildAnswers() {
  return questions.value
    .map(q => ({ question: q.question, answer: (answers.value[q.id] || '').trim() }))
    .filter(a => a.answer)
}
function buildConfirmedSkills() {
  const out = []
  for (const c of skillCats.value) for (const s of (c.skills || [])) if (skillChecked.value[s]) out.push(s)
  return out
}
function generate() { emit('submit', { answers: buildAnswers(), confirmedSkills: buildConfirmedSkills() }) }
function skip() { emit('submit', { answers: [], confirmedSkills: [] }) }
</script>

<template>
  <transition name="cvq-fade">
    <div v-if="show" class="cvq" @click.self="emit('close')">
      <div class="cvq__dialog">
        <header class="cvq__head">
          <div class="cvq__title">
            <SparklesIcon class="w-5 h-5" />
            <div>
              <h2>{{ t('cvq.title') }}</h2>
              <p>{{ t('cvq.subtitle') }}</p>
            </div>
          </div>
          <button class="cvq__x" @click="emit('close')"><XMarkIcon class="w-5 h-5" /></button>
        </header>

        <div class="cvq__body">
          <!-- ÉTAPE 1 : questions ciblées -->
          <template v-if="step === 'questions'">
            <div v-if="loading" class="cvq__loading">
              <span class="cvq__spin"></span>{{ t('cvq.loading') }}
            </div>
            <div v-else-if="errorMsg" class="cvq__error">{{ errorMsg }}</div>
            <template v-else>
              <div v-for="(q, i) in questions" :key="q.id" class="cvq__q">
                <div class="cvq__q-head">
                  <span class="cvq__num">{{ i + 1 }}</span>
                  <component :is="catIcon(q.category)" class="cvq__cat-ic" />
                  <span class="cvq__cat">{{ catLabel(q.category) }}</span>
                </div>
                <label class="cvq__label">{{ q.question }}</label>
                <textarea v-model="answers[q.id]" :placeholder="q.hint || t('cvq.answer_ph')" rows="2" class="cvq__input"></textarea>
              </div>
            </template>
          </template>

          <!-- ÉTAPE 2 : compétences détectées dans le CV, à cocher -->
          <template v-else>
            <div v-if="skillsLoading" class="cvq__loading">
              <span class="cvq__spin"></span>{{ t('cvq.skills_loading') }}
            </div>
            <template v-else>
              <p class="cvq__skills-intro">{{ t('cvq.skills_intro') }}</p>
              <div v-for="c in skillCats" :key="c.category" class="cvq__skill-cat">
                <div class="cvq__skill-cat-name">{{ c.category }}</div>
                <div class="cvq__skill-chips">
                  <label v-for="s in c.skills" :key="s" class="cvq__chip" :class="{ 'is-on': skillChecked[s] }">
                    <input type="checkbox" v-model="skillChecked[s]" />
                    <span>{{ s }}</span>
                  </label>
                </div>
              </div>
            </template>
          </template>
        </div>

        <footer class="cvq__foot">
          <template v-if="step === 'questions'">
            <button class="cvq__skip" @click="skip" :disabled="loading">{{ t('cvq.skip') }}</button>
            <button class="cvq__go" @click="goToSkills" :disabled="loading">
              {{ t('cvq.next_skills') }}
            </button>
          </template>
          <template v-else>
            <button class="cvq__skip" @click="step = 'questions'" :disabled="skillsLoading">{{ t('cvq.back') }}</button>
            <button class="cvq__go" @click="generate" :disabled="skillsLoading">
              <SparklesIcon class="w-4 h-4" /> {{ t('cvq.generate') }}
            </button>
          </template>
        </footer>
      </div>
    </div>
  </transition>
</template>

<style scoped>
.cvq { position: fixed; inset: 0; z-index: 300; background: rgba(15,23,42,0.55); backdrop-filter: blur(4px); display: flex; align-items: center; justify-content: center; padding: 1rem; }
.cvq__dialog { width: 100%; max-width: 620px; max-height: 90vh; display: flex; flex-direction: column; background: #fff; border-radius: 1.4rem; overflow: hidden; box-shadow: 0 30px 60px -20px rgba(16,24,40,0.55); }
.cvq__head { display: flex; align-items: flex-start; justify-content: space-between; gap: 1rem; padding: 1.3rem 1.4rem; background: linear-gradient(135deg, #FEF6E7, #FFFFFF); border-bottom: 1px solid #EEF0F3; }
.cvq__title { display: flex; gap: 0.7rem; color: #B45309; }
.cvq__title h2 { font-size: 1.1rem; font-weight: 800; margin: 0; color: #101828; }
.cvq__title p { font-size: 0.82rem; color: #667085; margin: 0.2rem 0 0; }
.cvq__x { background: none; border: none; color: #98A2B3; cursor: pointer; }
.cvq__x:hover { color: #101828; }
.cvq__body { padding: 1.2rem 1.4rem; overflow-y: auto; display: flex; flex-direction: column; gap: 1.1rem; }
.cvq__loading { display: flex; align-items: center; gap: 0.6rem; justify-content: center; padding: 2.5rem; color: #667085; font-weight: 600; }
.cvq__spin { width: 1.1rem; height: 1.1rem; border: 2px solid #F1F3F6; border-top-color: #F59E0B; border-radius: 50%; animation: cvq-spin 0.7s linear infinite; }
@keyframes cvq-spin { to { transform: rotate(360deg); } }
.cvq__error { text-align: center; color: #DC2626; padding: 2rem; }
.cvq__q { display: flex; flex-direction: column; gap: 0.4rem; }
.cvq__q-head { display: flex; align-items: center; gap: 0.45rem; }
.cvq__num { width: 1.4rem; height: 1.4rem; border-radius: 50%; background: #FEF3C7; color: #B45309; font-size: 0.72rem; font-weight: 800; display: flex; align-items: center; justify-content: center; }
.cvq__cat-ic { width: 0.9rem; height: 0.9rem; color: #D97706; }
.cvq__cat { font-size: 0.64rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.06em; color: #D97706; }
.cvq__label { font-size: 0.9rem; font-weight: 650; color: #1E293B; line-height: 1.35; }
.cvq__input { width: 100%; padding: 0.6rem 0.75rem; border-radius: 0.7rem; background: #F9FAFB; border: 1px solid #EEF0F3; font-size: 0.86rem; color: #101828; outline: none; resize: vertical; font-family: inherit; }
.cvq__input:focus { border-color: #F59E0B; box-shadow: 0 0 0 3px rgba(245,158,11,0.12); background: #fff; }
.cvq__foot { display: flex; align-items: center; justify-content: space-between; gap: 0.8rem; padding: 1rem 1.4rem; border-top: 1px solid #EEF0F3; background: #FCFCFD; }
.cvq__skip { background: none; border: none; color: #667085; font-weight: 600; font-size: 0.85rem; cursor: pointer; }
.cvq__skip:hover { color: #101828; }
.cvq__go { display: inline-flex; align-items: center; gap: 0.45rem; padding: 0.7rem 1.4rem; border-radius: 0.8rem; background: linear-gradient(135deg, #FBBF24, #F59E0B); color: #fff; border: none; font-weight: 800; font-size: 0.88rem; cursor: pointer; box-shadow: 0 10px 22px -12px rgba(245,158,11,0.7); }
.cvq__go:disabled, .cvq__skip:disabled { opacity: 0.5; cursor: not-allowed; }
/* Étape compétences */
.cvq__skills-intro { font-size: 0.85rem; color: #475569; margin: 0 0 0.4rem; line-height: 1.45; }
.cvq__skill-cat { display: flex; flex-direction: column; gap: 0.5rem; }
.cvq__skill-cat-name { font-size: 0.66rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.06em; color: #D97706; }
.cvq__skill-chips { display: flex; flex-wrap: wrap; gap: 0.4rem; }
.cvq__chip { display: inline-flex; align-items: center; gap: 0.4rem; padding: 0.35rem 0.7rem; border-radius: 999px; border: 1px solid #E5E7EB; background: #F9FAFB; color: #64748B; font-size: 0.82rem; font-weight: 600; cursor: pointer; transition: all 0.15s; user-select: none; }
.cvq__chip.is-on { border-color: #F59E0B; background: #FEF3C7; color: #92400E; }
.cvq__chip input { accent-color: #F59E0B; width: 0.9rem; height: 0.9rem; cursor: pointer; }
.cvq-fade-enter-active, .cvq-fade-leave-active { transition: opacity 0.2s; }
.cvq-fade-enter-from, .cvq-fade-leave-to { opacity: 0; }
</style>
