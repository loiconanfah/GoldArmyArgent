<script setup>
import { authFetch } from '../utils/auth'
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { 
  PlayIcon, 
  BoltIcon, 
  PuzzlePieceIcon, 
  MapIcon, 
  TrophyIcon, 
  BriefcaseIcon, 
  ChatBubbleLeftRightIcon, 
  PresentationChartLineIcon, 
  UserGroupIcon, 
  PhoneIcon, 
  ArrowPathIcon, 
  DocumentDuplicateIcon,
  CheckIcon,
  DocumentTextIcon,
  ArrowDownTrayIcon,
  EyeIcon,
  XMarkIcon,
  RocketLaunchIcon, 
  EnvelopeIcon, 
  UsersIcon, 
  LightBulbIcon,
  MagnifyingGlassIcon, 
  MegaphoneIcon, 
  HandThumbUpIcon, 
  InformationCircleIcon,
  StarIcon,
  ShieldCheckIcon,
  SparklesIcon,
  ChevronRightIcon,
  ChevronLeftIcon,
  CheckCircleIcon
} from '@heroicons/vue/24/outline'

// Dimensions pour le graphique principal
const W = 800, H = 250
const PAD = { top: 30, bottom: 40, left: 60, right: 40 }

const chartData = ref([])
const chartData2 = ref([])

// Dropdowns State
const monthDropdownOpen = ref(false)
const yearDropdownOpen = ref(false)
const selectedMonth = ref('Month')
const selectedYear = ref('Year')

// Data for Bar Chart (computed from real data)
const barData = computed(() => {
    if (!chartData.value || chartData.value.length === 0) return Array.from({length: 12}, () => Math.floor(Math.random()*30 + 15))
    let res = []
    for(let i=0; i<12; i++) {
        res.push(chartData.value[i] ? chartData.value[i].count : 0)
    }
    return res
})
const barData2 = computed(() => {
    if (!chartData2.value || chartData2.value.length === 0) return Array.from({length: 12}, () => Math.floor(Math.random()*25 + 5))
    let res = []
    for(let i=0; i<12; i++) {
        res.push(chartData2.value[i] ? chartData2.value[i].count : 0)
    }
    return res
})
const barYMax = computed(() => {
    const max = Math.max(...barData.value, ...barData2.value)
    return Math.max(Math.ceil(max / 10) * 10, 40)
})

const recentActivity = ref([])
const userEmail = ref('')
const { t, locale } = useI18n()

// Jours et dates pour le header
const todayStr = computed(() => {
  const d = new Date()
  const loc = (locale.value && locale.value.includes('fr')) ? 'fr-FR' : 'en-US'
  const dayName = d.toLocaleDateString(loc, { weekday: 'short' })
  const monthName = d.toLocaleDateString(loc, { month: 'long' })
  return `${dayName}, ${monthName}`
})
const dateNum = computed(() => new Date().getDate())

const kpiValues = ref({ applied: '0', cv_analyzed: '0', interviews: '0', network: '0' })

const playbooks = ref([
  { id: 1, name: 'Sniper-to-Apply', desc: 'Candidature Express 1-Clic', fullDesc: "Ce workflow analyse l'offre d'emploi, adapte votre CV spécifiquement pour celle-ci, et remplit automatiquement le formulaire ATS de l'entreprise via l'agent MultiOn.", icon: RocketLaunchIcon, active: false },
  { id: 2, name: 'Ghostbuster', desc: 'Relance Anti-Fantôme', fullDesc: "Détecte automatiquement les candidatures sans réponse depuis plus de 15 jours ouvrables et génère un email de relance + message LinkedIn personnalisé. Mode auto disponible (scan toutes les 48h).", icon: EnvelopeIcon, active: false },
  { id: 3, name: 'Network Ninja', desc: 'Chasseur de Décideurs', fullDesc: "Cherche et identifie les décideurs clés (RH, CEO, Lead Dev) de l'entreprise sur LinkedIn et prépare un message d'accroche personnalisé.", icon: UsersIcon, active: false },
  { id: 4, name: 'Pre-Interview', desc: 'Entraînement Immersif', fullDesc: "Récupère les détails du poste et de l'entreprise pour préparer un simulateur d'entretien avec des questions probables et des conseils de posture.", icon: LightBulbIcon, active: false },
  { id: 5, name: 'Daily Hunt', desc: 'Chasse Matinale (Cron)', fullDesc: "S'exécute tous les matins à 7h00. Scanne le web pour trouver 5 nouvelles offres d'emploi correspondant exactement à votre profil et les ajoute au CRM.", icon: MagnifyingGlassIcon, active: false },
  { id: 6, name: 'Social Sniper', desc: 'Kit d\'Approche Multi-Canal', fullDesc: "Génère un arsenal complet pour infiltrer l'entreprise : Accroche LinkedIn, Commentaire expert, Relance et argument massue personnalisé.", icon: MegaphoneIcon, active: false },
  { id: 7, name: 'Post-Interview', desc: 'Debrief & Remerciement', fullDesc: "S'active après un entretien. Génère un email de remerciement stratégique et met à jour le statut de la candidature dans le CRM.", icon: HandThumbUpIcon, active: false },
  { id: 8, name: 'Gold Profile', desc: 'Personal Branding LinkedIn', fullDesc: "Optimise votre profil LinkedIn à 100% : Bio, champs clés, et stratégie de contenu. Génère un plan de publication sur 30 jours et vous envoie chaque matin votre post prêt-à-publier par email.", icon: SparklesIcon, active: false },
  { id: 9, name: 'Rejection Pivot', desc: 'Rebond & Alternatives', fullDesc: "Suite à un refus, envoie un email demandant du feedback constructif, et trouve instantanément 3 offres similaires pour rebondir.", icon: ArrowPathIcon, active: false },
  { id: 10, name: 'Smart Cover', desc: 'Lettre d\'Actualité', fullDesc: "Rédige une lettre de motivation dynamique en intégrant la dernière actualité pertinente de l'entreprise ciblée.", icon: DocumentTextIcon, active: false }
])

const isSelectionModalOpen = ref(false)
const isExecuting = ref(false)
const execPlaybook = ref(null)
const execStep = ref(0)
const execLogs = ref([])
const selectedOffers = ref([])
const isLetterPreviewOpen = ref(false)
const currentPreviewLetter = ref(null)
const isPremiumUpgradeModalOpen = ref(false)
const isDownloadChoiceModalOpen = ref(false)
const downloadPendingItem = ref(null)

// ── Ghostbuster state ──
const isGhostbusterModalOpen = ref(false)
const isGhostbusterScanning = ref(false)
const ghostbusterResults = ref([])
const ghostbusterTotalScanned = ref(0)
const ghostbusterAutoEnabled = ref(false)
const ghostbusterLastRun = ref(null)
const ghostbusterError = ref('')
const ghostbusterExpandedEmail = ref(null)   // app_id expanded
const ghostbusterExpandedLinkedin = ref(null)
const ghostbusterCopied = ref({})             // { app_id_email: true, ... }
const ghostbusterSent = ref({})               // { app_id: 'email'|'linkedin'|'manual' }
const ghostbusterChainTo = ref('none')        // 'none' | 'network_ninja' | 'post_interview'

const isPremium = computed(() => {
    try {
        const u = localStorage.getItem('user')
        if (u) {
            const userObj = JSON.parse(u)
            const tier = (userObj.subscription_tier || userObj.tier || userObj.plan || '').toUpperCase()
            // Un admin est considéré comme premium, ainsi que tout tier autre que FREE/BASIC
            return tier === 'ADMIN' || (tier !== '' && tier !== 'FREE' && tier !== 'BASIC')
        }
    } catch(e) {}
    return false
})

const executionPhases = [
  { title: "Initialisation", desc: "Connexion aux clusters d'agents GoldArmy..." },
  { title: "Extraction & Analyse", desc: "Collecte de données et analyse contextuelle..." },
  { title: "Exécution de la Mission", desc: "L'Agent est en action sur la cible..." },
  { title: "Vérification", desc: "Contrôle qualité des résultats..." }
]

const realExecutionResult = ref(null)
const bulkResults = ref([])

const togglePlaybook = async (pb) => {
    if (pb.active) {
        pb.active = false
        return
    }
    
    // Reset result
    realExecutionResult.value = null
    bulkResults.value = []
    
    if (pb.id === 10) {
        // Ouvre la sélection pour le Workflow 10
        isSelectionModalOpen.value = true
        execPlaybook.value = pb
        return
    }

    if (pb.id === 8) {
        openGoldProfileModal(pb)
        return
    }

    if (pb.id === 9) {
        // Ghostbuster — vrai workflow
        openGhostbusterModal(pb)
        return
    }

    if (pb.id === 2) {
        // Ghostbuster — vrai workflow
        openGhostbusterModal(pb)
        return
    }

    if (pb.id === 4) {
        openPreInterviewModal(pb)
        return
    }

    if (pb.id === 5) {
        openDailyHuntModal(pb)
        return
    }

    if (pb.id === 6) {
        openSocialSniperModal(pb)
        return
    }

    if (pb.id === 7) {
        openPostInterviewModal(pb)
        return
    }

    if (pb.id === 3) {
        window.location.href = '/network?tab=ninja'
        return
    }
    
    // Start simulation for others
    execPlaybook.value = pb
    isExecuting.value = true
    execStep.value = 0
    execLogs.value = [`[00:00] Initialisation du Playbook: ${pb.name}`]
    
    setTimeout(() => advanceStep(1, `[00:01] Clusters d'agents connectés avec succès.`), 1500)
    setTimeout(() => advanceStep(2, `[00:03] Extraction des données démarrée... OK.`), 3500)
    setTimeout(() => advanceStep(3, `[00:05] Agent en action. Traitement en cours...`), 5500)
    setTimeout(() => advanceStep(4, `[00:07] Contrôle qualité validé. Mission accomplie.`), 7500)
    setTimeout(() => finishExecution(), 9000)
}

// ─── Ghostbuster functions ───

const openGhostbusterModal = async (pb) => {
    execPlaybook.value = pb
    isGhostbusterModalOpen.value = true
    ghostbusterError.value = ''
    // Charger le statut auto
    await fetchGhostbusterStatus()
    // Lancer le scan automatiquement
    await runGhostbusterScan()
}

const fetchGhostbusterStatus = async () => {
    try {
        const r = await authFetch('/api/workflows/ghostbuster/status')
        const j = await r.json()
        if (j.status === 'success') {
            ghostbusterAutoEnabled.value = j.data.auto_enabled
            ghostbusterLastRun.value = j.data.last_run_at
        }
    } catch(e) { console.warn('[Ghostbuster] Status fetch failed', e) }
}

const runGhostbusterScan = async (forceRegenerate = false) => {
    isGhostbusterScanning.value = true
    ghostbusterError.value = ''
    ghostbusterResults.value = []
    try {
        const r = await authFetch('/api/workflows/ghostbuster/scan', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                force_regenerate: forceRegenerate,
                chain_to: ghostbusterChainTo.value === 'none' ? null : ghostbusterChainTo.value
            })
        })
        const j = await r.json()
        if (j.status === 'success') {
            ghostbusterResults.value = j.data.eligible || []
            ghostbusterTotalScanned.value = j.data.total_scanned || 0
            // Marquer le playbook comme actif si des relances ont été trouvées
            if (ghostbusterResults.value.length > 0) {
                const pb = playbooks.value.find(p => p.id === 2)
                if (pb) pb.active = true
            }
        } else {
            ghostbusterError.value = 'Erreur lors du scan. Réessayez.'
        }
    } catch(e) {
        ghostbusterError.value = 'Erreur réseau. Vérifiez votre connexion.'
    } finally {
        isGhostbusterScanning.value = false
    }
}

const toggleGhostbusterAuto = async () => {
    const newState = !ghostbusterAutoEnabled.value
    try {
        const r = await authFetch('/api/workflows/ghostbuster/toggle', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ enabled: newState })
        })
        const j = await r.json()
        if (j.status === 'success') {
            ghostbusterAutoEnabled.value = newState
        }
    } catch(e) { console.warn('[Ghostbuster] Toggle failed', e) }
}

const copyGhostbusterText = async (text, key) => {
    try {
        await navigator.clipboard.writeText(text)
        ghostbusterCopied.value = { ...ghostbusterCopied.value, [key]: true }
        setTimeout(() => {
            ghostbusterCopied.value = { ...ghostbusterCopied.value, [key]: false }
        }, 2500)
    } catch(e) { console.warn('Clipboard failed', e) }
}

const markGhostbusterSent = async (appId, via = 'manual') => {
    try {
        const r = await authFetch('/api/workflows/ghostbuster/send', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ app_id: appId, via })
        })
        const j = await r.json()
        if (j.status === 'success') {
            ghostbusterSent.value = { ...ghostbusterSent.value, [appId]: via }
        }
    } catch(e) { console.warn('[Ghostbuster] Mark sent failed', e) }
}

const closeGhostbusterModal = () => {
    isGhostbusterModalOpen.value = false
    ghostbusterResults.value = []
    ghostbusterExpandedEmail.value = null
    ghostbusterExpandedLinkedin.value = null
    ghostbusterError.value = ''
}

const formatRelativeDate = (isoStr) => {
    if (!isoStr) return ''
    const d = new Date(isoStr)
    return d.toLocaleDateString('fr-FR', { day: '2-digit', month: 'short', year: 'numeric' })
}

const last10RecentApplications = computed(() => {
    return recentActivity.value.slice(0, 10)
})

const startBulkExecution = async () => {
    if (selectedOffers.value.length === 0) return
    isSelectionModalOpen.value = false
    isExecuting.value = true
    execStep.value = 0
    execLogs.value = [`[00:00] Initialisation du traitement groupé (${selectedOffers.value.length} offres)...`]
    
    try {
        advanceStep(1, `[00:01] Connexion aux clusters d'agents GoldArmy...`)
        
        for (const offerId of selectedOffers.value) {
            const offer = recentActivity.value.find(o => o.id === offerId) || { company: "Google", name: "Software Engineer" }
            advanceStep(2, `[00:02] Recherche & Analyse pour ${offer.company}...`)
            
            const response = await authFetch('/api/workflows/smart-cover', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ company_name: offer.company, job_title: offer.name })
            })
            const res = await response.json()
            if (res.status === 'success') {
                bulkResults.value.push({
                    company: offer.company,
                    letter: res.data.letter,
                    news: res.data.news
                })
                execLogs.value.push(`[OK] Lettre générée pour ${offer.company}`)
            }
        }
        
        advanceStep(3, `[00:06] Finalisation des documents...`)
        await new Promise(r => setTimeout(r, 1000))
        advanceStep(4, `[00:08] Mission terminée. ${bulkResults.value.length} lettres disponibles.`)
        realExecutionResult.value = { isBulk: true, items: bulkResults.value }
        finishExecution()
    } catch (e) {
        advanceStep(4, `[ERR] Échec du traitement.`)
    }
}

const openLetterPreview = (item) => {
    currentPreviewLetter.value = item
    isLetterPreviewOpen.value = true
}

const downloadPDF = async (item) => {
    downloadPendingItem.value = item
    if (!isPremium.value) {
        isPremiumUpgradeModalOpen.value = true
    } else {
        isDownloadChoiceModalOpen.value = true
    }
}

const triggerDownload = async (isPremiumVersion) => {
    const item = downloadPendingItem.value
    if (!item) return
    
    isPremiumUpgradeModalOpen.value = false
    isDownloadChoiceModalOpen.value = false
    
    try {
        const response = await authFetch('/api/workflows/smart-cover/download', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                company: item.company, 
                letter: item.letter,
                force_standard: !isPremiumVersion
            })
        })
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `lettre_${item.company}${!isPremiumVersion ? '_standard' : ''}.pdf`
        document.body.appendChild(a)
        a.click()
        a.remove()
    } catch (e) {
        console.error("Erreur PDF", e)
    }
}

const advanceStep = (stepIdx, logMsg) => {
    if(!isExecuting.value) return; 
    execStep.value = stepIdx
    execLogs.value.push(logMsg)
}

const finishExecution = () => {
    if(!isExecuting.value) return;
    execStep.value = 4 // Montre l'overlay de succès
    execPlaybook.value.active = true
}

const cancelExecution = () => {
    isExecuting.value = false
    execPlaybook.value = null
}

const selectedPlaybookInfo = ref(null)
const isPreInterviewModalOpen = ref(false)
const preInterviewPending = ref([])
const preInterviewLoading = ref(false)
const preInterviewSelections = ref({}) // { [appId]: { date: '', type: 'both' } }
const preInterviewScheduling = ref(false)

const openPreInterviewModal = async (pb) => {
    execPlaybook.value = pb
    isPreInterviewModalOpen.value = true
    preInterviewSelections.value = {}
    await fetchPreInterviewPending()
}

const isDailyHuntModalOpen = ref(false)
const dailyHuntLoading = ref(false)
const dailyHuntConfig = ref({ enabled: false, query: 'Développeur', location: 'Montreal, QC' })

const openDailyHuntModal = async (pb) => {
    execPlaybook.value = pb
    isDailyHuntModalOpen.value = true
    dailyHuntLoading.value = true
    try {
        const r = await authFetch('/api/workflows/daily-hunt/config')
        const j = await r.json()
        if (j.status === 'success') {
            dailyHuntConfig.value = j.data
        }
    } catch (e) {}
    finally { dailyHuntLoading.value = false }
}

const isSocialSniperModalOpen = ref(false)
const socialSniperLoading = ref(false)
const socialSniperResult = ref(null)
const socialSniperForm = ref({ company: '', job: '' })
const socialSniperApps = ref([])

const openSocialSniperModal = async (pb) => {
    execPlaybook.value = pb
    isSocialSniperModalOpen.value = true
    socialSniperResult.value = null
    socialSniperLoading.value = true
    try {
        const r = await authFetch('/api/crm') // Fetch all apps
        const j = await r.json()
        if (j.status === 'success') {
            socialSniperApps.value = j.data.applications.slice(0, 5) // Last 5
        }
    } catch (e) {}
    finally { socialSniperLoading.value = false }
}

const selectAppForSniper = (app) => {
    socialSniperForm.value.company = app.company_name
    socialSniperForm.value.job = app.job_title
}

const runSocialSniper = async () => {
    socialSniperLoading.value = true
    try {
        const r = await authFetch('/api/workflows/social-sniper/generate', {
            method: 'POST',
            body: JSON.stringify(socialSniperForm.value)
        })
        const j = await r.json()
        if (j.status === 'success') {
            socialSniperResult.value = j.data
        }
    } catch (e) {}
    finally { socialSniperLoading.value = false }
}

const isPostInterviewModalOpen = ref(false)
const postInterviewApps = ref([])
const postInterviewLoading = ref(false)
const postInterviewGenerating = ref(false)
const postInterviewSelectedApp = ref(null)
const postInterviewResult = ref(null)
const postInterviewDebrief = ref({ feel: 'Neutre', hard_question: '', key_need: '' })

const openPostInterviewModal = async (pb) => {
    execPlaybook.value = pb
    isPostInterviewModalOpen.value = true
    postInterviewLoading.value = true
    postInterviewResult.value = null
    postInterviewSelectedApp.value = null
    try {
        const r = await authFetch('/api/workflows/post-interview/apps')
        const j = await r.json()
        if (j.status === 'success') {
            postInterviewApps.value = j.data
        }
    } catch (e) {}
    finally { postInterviewLoading.value = false }
}

const runPostInterview = async () => {
    if (!postInterviewSelectedApp.value) return
    postInterviewGenerating.value = true
    try {
        const r = await authFetch('/api/workflows/post-interview/generate', {
            method: 'POST',
            body: JSON.stringify({
                app_id: postInterviewSelectedApp.value.id,
                company: postInterviewSelectedApp.value.company_name,
                job: postInterviewSelectedApp.value.job_title,
                debrief: postInterviewDebrief.value
            })
        })
        const j = await r.json()
        if (j.status === 'success') {
            postInterviewResult.value = j.data
        }
    } catch (e) {}
    finally { postInterviewGenerating.value = false }
}

const isGoldProfileModalOpen = ref(false)
const goldProfileStep = ref('audit') // 'audit', 'plan', 'post'
const goldProfileLoading = ref(false)
const goldProfileAuditData = ref(null)
const goldProfilePlanData = ref(null)
const goldProfilePostData = ref(null)
const goldProfileSelectedTopic = ref(null)

const openGoldProfileModal = async (pb) => {
    execPlaybook.value = pb
    isGoldProfileModalOpen.value = true
    goldProfileStep.value = 'audit'
    goldProfileLoading.value = true
    try {
        const r = await authFetch('/api/workflows/gold-profile/audit')
        const j = await r.json()
        if (j.status === 'success') {
            goldProfileAuditData.value = j.data
        }
    } catch (e) {}
    finally { goldProfileLoading.value = false }
}

const fetchGoldProfilePlan = async () => {
    goldProfileStep.value = 'plan'
    if (goldProfilePlanData.value) return
    goldProfileLoading.value = true
    try {
        const r = await authFetch('/api/workflows/gold-profile/plan')
        const j = await r.json()
        if (j.status === 'success') {
            goldProfilePlanData.value = j.data.plan
        }
    } catch (e) {}
    finally { goldProfileLoading.value = false }
}

const generateGoldProfilePost = async (topic) => {
    goldProfileSelectedTopic.value = topic
    goldProfileStep.value = 'post'
    goldProfileLoading.value = true
    try {
        const r = await authFetch('/api/workflows/gold-profile/post', {
            method: 'POST',
            body: JSON.stringify({ topic: topic.topic })
        })
        const j = await r.json()
        if (j.status === 'success') {
            goldProfilePostData.value = j.data.post_content
        }
    } catch (e) {}
    finally { goldProfileLoading.value = false }
}

const toggleDailyHunt = async () => {
    try {
        const r = await authFetch('/api/workflows/daily-hunt/toggle', {
            method: 'POST',
            body: JSON.stringify(dailyHuntConfig.value)
        })
        const j = await r.json()
        if (j.status === 'success') {
            isDailyHuntModalOpen.value = false
            if (execPlaybook.value) execPlaybook.value.active = dailyHuntConfig.value.enabled
            
            // Notification de succès
            if ("Notification" in window && Notification.permission === "granted") {
                new Notification("Daily Hunt", {
                    body: `Configuration enregistrée ! La chasse démarrera à 07h00 pour : ${dailyHuntConfig.value.query}`,
                    icon: "/favicon.ico"
                })
            }
        }
    } catch (e) {}
}

const fetchPreInterviewPending = async () => {
    preInterviewLoading.value = true
    try {
        const r = await authFetch('/api/workflows/pre-interview/pending')
        const j = await r.json()
        if (j.status === 'success') {
            preInterviewPending.value = j.data
        }
    } catch (e) {
        console.warn('[Pre-Interview] Fetch pending failed', e)
    } finally {
        preInterviewLoading.value = false
    }
}

const togglePreInterviewApp = (appId) => {
    if (preInterviewSelections.value[appId]) {
        delete preInterviewSelections.value[appId]
    } else {
        preInterviewSelections.value[appId] = { date: '', type: 'both' }
    }
}

const schedulePreInterview = async () => {
    const items = Object.entries(preInterviewSelections.value).map(([appId, config]) => ({
        application_id: appId,
        simulation_date: config.date,
        prep_type: config.type
    }))

    if (items.length === 0 || items.some(i => !i.simulation_date)) {
        return
    }
    preInterviewScheduling.value = true
    try {
        const r = await authFetch('/api/workflows/pre-interview/schedule', {
            method: 'POST',
            body: JSON.stringify({ items })
        })
        const j = await r.json()
        if (j.status === 'success') {
            isPreInterviewModalOpen.value = false
            if (execPlaybook.value) {
                execPlaybook.value.active = true
            }
            preInterviewSelections.value = {}
            
            // Notification Browser (Push)
            if ("Notification" in window) {
                Notification.requestPermission().then(permission => {
                    if (permission === "granted") {
                        new Notification("Simulation Planifiée", {
                            body: "GoldArmy vous enverra un rappel 15 min avant l'entretien.",
                            icon: "/favicon.ico"
                        })
                    }
                })
            }
        }
    } catch (e) {
        console.warn('[Pre-Interview] Scheduling failed', e)
    } finally {
        preInterviewScheduling.value = false
    }
}
const showInfo = (pb) => {
    selectedPlaybookInfo.value = pb
}
const closeInfo = () => {
    selectedPlaybookInfo.value = null
}

// Génération de fausses données pour les sparklines (mini graphiques des KPIs)
const generateSparkline = () => {
    let pts = []
    let val = 50
    for(let i=0; i<10; i++) {
        pts.push(val)
        val += (Math.random() - 0.5) * 20
    }
    return pts
}

const sparklines = ref({
    applied: generateSparkline(),
    cv: generateSparkline(),
    interviews: generateSparkline(),
    network: generateSparkline()
})

const getSparklinePath = (data) => {
    if(!data || data.length === 0) return ''
    const w = 100, h = 40
    const min = Math.min(...data), max = Math.max(...data)
    const range = max - min || 1
    
    let path = `M 0 ${h - ((data[0] - min)/range)*h}`
    for(let i=1; i<data.length; i++) {
        path += ` L ${(i/(data.length-1))*w} ${h - ((data[i] - min)/range)*h}`
    }
    return path
}

const kpiStats = computed(() => [
  { id: 'applied', label: t('dashboard.smart_score'), value: kpiValues.value.cv_analyzed || '0', suffix: ' / 100', trend: '+18', trendUp: true, chartType: 'gauge' },
  { id: 'cv', label: t('dashboard.applications'), value: kpiValues.value.applied || '0', trend: '+20%', trendUp: true, chartType: 'line', sparkline: sparklines.value.cv },
  { id: 'interviews', label: t('dashboard.interviews'), value: kpiValues.value.interviews || '0', trend: '+12%', trendUp: true, chartType: 'line', sparkline: sparklines.value.interviews },
  { id: 'network', label: t('dashboard.network'), value: kpiValues.value.network || '0', trend: '+34%', trendUp: true, chartType: 'line', sparkline: sparklines.value.network },
])

// État pour le tooltip du graphique
const activePoint = ref(null)
const activePoint2 = ref(null)

// Total des opportunités
const totalOpportunities = computed(() => {
    const total = parseInt(kpiValues.value.applied || 0) + parseInt(kpiValues.value.cv_analyzed || 0);
    return new Intl.NumberFormat('fr-FR').format(total > 0 ? total : 248);
})

const formatYLabel = (val) => {
    if (val >= 1000000) return (val/1000000).toFixed(1).replace('.0','') + 'm'
    if (val >= 1000) return (val/1000).toFixed(1).replace('.0','') + 'k'
    return val
}

const yMax = computed(() => {
    const max1 = Math.max(...chartData.value.map(d => d.count), 0)
    const max2 = Math.max(...chartData2.value.map(d => d.count), 0)
    return Math.max(Math.ceil(Math.max(max1, max2) / 10) * 10, 120)
})

const pts = computed(() => {
  return chartData.value.map((d, i) => {
    const x = PAD.left + (i / (chartData.value.length - 1 || 1)) * (W - PAD.left - PAD.right)
    const y = H - PAD.bottom - (d.count / yMax.value) * (H - PAD.top - PAD.bottom)
    return { x, y, count: d.count, label: d.label }
  })
})

const pts2 = computed(() => {
  return chartData2.value.map((d, i) => {
    const x = PAD.left + (i / (chartData2.value.length - 1 || 1)) * (W - PAD.left - PAD.right)
    const y = H - PAD.bottom - (d.count / yMax.value) * (H - PAD.top - PAD.bottom)
    return { x, y, count: d.count, label: d.label }
  })
})

const linePath = computed(() => {
  if (pts.value.length === 0) return ''
  return 'M ' + pts.value.map(p => `${p.x},${p.y}`).join(' L ')
})

const areaPath = computed(() => {
  if (pts.value.length === 0) return ''
  const p = pts.value
  return 'M ' + p.map(p => `${p.x},${p.y}`).join(' L ') + ` L ${p[p.length-1].x},${H - PAD.bottom} L ${p[0].x},${H - PAD.bottom} Z`
})

const linePath2 = computed(() => {
  if (pts2.value.length === 0) return ''
  return 'M ' + pts2.value.map(p => `${p.x},${p.y}`).join(' L ')
})

const fetchDashboardData = async () => {
  try { const u = localStorage.getItem('user'); if (u) userEmail.value = JSON.parse(u).full_name || JSON.parse(u).email.split('@')[0] } catch(e){}
  try {
    const r = await authFetch('/api/dashboard/stats'), j = await r.json()
    if (j.data) {
      const k = j.data.kpis
      kpiValues.value = { applied: k.applied.toString(), cv_analyzed: k.cv_analyzed.toString(), interviews: k.interviews.toString(), network: k.network.toString() }
      if(j.data.chart && j.data.chart.length > 0) {
          chartData.value = j.data.chart
      } else {
          chartData.value = Array.from({length: 31}, (_, i) => ({ label: `Day ${i+1}`, count: Math.floor(Math.random()*60 + 40) }))
      }
      chartData2.value = chartData.value.map(d => ({ label: d.label, count: Math.max(10, d.count - Math.floor(Math.random()*30 + 10)) }))
    }
  } catch(e){}
  try {
    const r2 = await authFetch('/api/crm'), j2 = await r2.json()
    if (j2.data) {
      recentActivity.value = j2.data.slice(0, 10).map(app => {
        let score = 20;
        if(app.status==='APPLIED') score = 40;
        else if(app.status==='FOLLOW_UP') score = 60;
        else if(app.status==='INTERVIEW') score = 85;
        else if(app.status==='OFFER') score = 100;
        
        return { 
          id: app.id || Math.random().toString(36),
          name: app.job_title, 
          company: app.company_name, 
          score, 
          initial: (app.company_name||app.job_title||'?').charAt(0).toUpperCase(), 
          status: app.status,
          date: app.created_at ? new Date(app.created_at).toLocaleDateString() : 'Récent'
        }
      })
    }
  } catch(e){}
}
onMounted(async () => {
    await fetchDashboardData()
    await syncWorkflowStatuses()
})

const syncWorkflowStatuses = async () => {
    try {
        const r = await authFetch('/api/workflows/status')
        const j = await r.json()
        if (j.status === 'success') {
            const statusMap = j.data
            playbooks.value.forEach(pb => {
                if (statusMap[pb.id] !== undefined) {
                    pb.active = statusMap[pb.id]
                }
            })
        }
    } catch (e) {
        console.warn('[Workflows] Failed to sync statuses', e)
    }
}
</script>

<template>
  <div class="db-root">

    <!-- HEADER INSPIRATION 2 -->
    <div class="db-header animate-slide-up" style="animation-delay: 0s;">
      <div class="header-date-box">
          <div class="date-num">{{ dateNum }}</div>
          <div class="date-str">{{ todayStr }}</div>
          <div class="date-divider"></div>
          <button @click="$router.push('/crm')" class="btn-orange">{{ t('dashboard.show_tasks') }} &rarr;</button>
      </div>
      
      <div class="header-greeting">
          <div class="greeting-text">
            <div class="flex items-center gap-3">
                {{ t('dashboard.need_help') }}
                <img src="/logo.png" alt="Logo" class="w-10 h-10 animate-float" />
            </div>
            <span class="greeting-sub">{{ t('dashboard.ask_anything') }}</span>
          </div>
          <button class="btn-icon-white rounded-full"><span class="w-5 h-5 block text-center leading-5">&plus;</span></button>
      </div>
    </div>

    <div class="mb-4 flex items-center justify-between">
      <h2 class="text-lg font-semibold text-slate-800">Playbooks Actifs</h2>
      <span class="text-xs text-slate-500 bg-slate-100 px-2 py-1 rounded-full font-medium border border-slate-200">10 Workflows Disponibles</span>
    </div>

    <div class="grid grid-cols-2 md:grid-cols-5 gap-3 mb-8">
      <button v-for="(pb, index) in playbooks" :key="pb.id" 
          @click="togglePlaybook(pb)"
          class="relative flex flex-col items-start p-3 rounded-xl border text-left transition-all duration-300 group overflow-hidden bg-white animate-slide-up hover:-translate-y-1 active:scale-95 cursor-pointer"
          :class="pb.active ? 'border-indigo-500 shadow-md shadow-indigo-200/50 ring-1 ring-indigo-500/20' : 'border-slate-200 hover:border-indigo-300 hover:shadow-md hover:shadow-indigo-100 opacity-80 hover:opacity-100'"
          :style="`animation-delay: ${0.05 * index}s;`">
        
        <!-- Active indicator -->
        <div class="absolute top-0 right-0 w-8 h-8 flex items-center justify-center">
            <div v-if="pb.active" class="w-2 h-2 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]"></div>
            <div v-else class="w-1.5 h-1.5 rounded-full bg-slate-300 transition-colors duration-300 group-hover:bg-indigo-300"></div>
        </div>

        <div class="mb-2 p-1.5 rounded-lg transition-transform duration-300 group-hover:scale-110" :class="pb.active ? 'bg-indigo-50 text-indigo-600' : 'bg-slate-50 text-slate-500'">
           <component :is="pb.icon" class="w-5 h-5" />
        </div>
        
        <div class="font-semibold text-sm mb-0.5 flex items-center gap-1" :class="pb.active ? 'text-slate-800' : 'text-slate-600'">
            {{ pb.name }}
            <button @click.stop="showInfo(pb)" class="text-slate-400 hover:text-indigo-500 transition-colors bg-white/80 rounded-full hover:bg-indigo-50" title="Plus d'infos">
                <InformationCircleIcon class="w-3.5 h-3.5" />
            </button>
        </div>
        <div class="text-[10px] leading-tight text-slate-500 font-medium">{{ pb.desc }}</div>
        
        <!-- Background subtle glow if active -->
        <div v-if="pb.active" class="absolute -bottom-6 -right-6 w-16 h-16 bg-indigo-50 rounded-full blur-xl -z-10"></div>
      </button>
    </div>

    <!-- ANCIENNES CARTES KPI A LA PLACE DES GRAPHIQUES -->
    <div class="db-kpi-grid mt-2 mb-8">
      <div v-for="(s, index) in kpiStats" :key="s.id" class="kpi-card animate-slide-up" :style="`animation-delay: ${0.2 + index * 0.1}s;`">
        <div class="kpi-content">
            <div class="kpi-info">
                <div class="kpi-label">{{ s.label }}</div>
                <div class="kpi-val-row">
                    <span class="kpi-val">{{ s.value }}</span>
                    <span v-if="s.suffix" class="kpi-suffix">{{ s.suffix }}</span>
                </div>
            </div>
            <div class="kpi-chart" :class="s.chartType === 'gauge' ? 'w-[100px] h-[50px]' : 'w-[80px] h-[40px]'">
                 <svg v-if="s.chartType === 'gauge'" viewBox="0 0 100 50" class="w-full h-full overflow-visible">
                    <path d="M 10 50 A 40 40 0 0 1 90 50" fill="none" stroke="#E5E7EB" stroke-width="5" stroke-linecap="butt"/>
                    <path d="M 10 50 A 40 40 0 0 1 90 50" fill="none" stroke="#10B981" stroke-width="5" stroke-linecap="butt"
                          :stroke-dasharray="`${(Math.min(parseInt(s.value), 100) / 100) * 125.66} 125.66`"
                          style="transition: stroke-dasharray 1s cubic-bezier(0.175, 0.885, 0.32, 1.275);"/>
                    <path d="M 22 50 A 28 28 0 0 1 78 50" fill="none" stroke="#D1D5DB" stroke-width="2" stroke-dasharray="0.5, 2.5"/>
                    <g :style="`transform: rotate(${((Math.min(parseInt(s.value), 100) / 100) * 180) - 90}deg); transform-origin: 50px 50px; transition: transform 1.2s cubic-bezier(0.175, 0.885, 0.32, 1.275);`">
                        <circle cx="50" cy="50" r="3" fill="#111827" />
                        <line x1="50" y1="48" x2="50" y2="28" stroke="#111827" stroke-width="1.5" stroke-linecap="round"/>
                    </g>
                 </svg>
                 <svg v-else viewBox="0 -5 100 50" preserveAspectRatio="none" class="w-full h-full overflow-visible">
                    <path :d="getSparklinePath(s.sparkline)" fill="none" stroke="#111827" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                    <circle v-if="s.sparkline" cx="100" :cy="40 - ((s.sparkline[s.sparkline.length-1] - Math.min(...s.sparkline))/(Math.max(...s.sparkline)-Math.min(...s.sparkline)||1))*40" r="2.5" fill="#111827" />
                 </svg>
            </div>
        </div>
        
        <div class="kpi-footer">
            <span :class="['kpi-trend', s.trendUp ? 'text-emerald-500' : 'text-rose-500']">
                 <ArrowTrendingUpIcon v-if="s.trendUp" class="w-3 h-3 inline mr-1" />
                 <ArrowTrendingDownIcon v-else class="w-3 h-3 inline mr-1" />
                 {{ s.trend }}
            </span>
            <span class="kpi-vs">Last week</span>
            <a href="#" class="kpi-link">Show more &rarr;</a>
        </div>
      </div>
    </div>

    <!-- Efficiency row below -->
    <div class="mt-6 animate-slide-up" style="animation-delay: 0.5s;">
      <div class="efficiency-card">
        <div class="chart-header" style="margin-bottom: 1.5rem;">
          <div class="chart-title">Recent Activity</div>
          <div class="eff-filters">
              <div class="segment-control">
                  <span class="segment-btn">Score</span>
                  <span class="segment-btn active">%</span>
              </div>
          </div>
        </div>
        
        <div class="eff-list">
            <div v-if="!recentActivity || recentActivity.length === 0" class="text-center py-8 text-sm text-gray-400 font-medium bg-gray-50 rounded-xl border border-dashed border-gray-200">
                Aucune activité récente.
            </div>
            <div v-for="(item, i) in recentActivity" :key="i" class="eff-row group animate-slide-up" :style="`animation-delay: ${0.6 + i * 0.05}s;`">
                <div class="eff-user">
                    <div class="eff-avatar-wrapper">
                        <div class="eff-avatar">
                            <img src="/logo.png" alt="GoldArmy" class="w-full h-full object-cover rounded-full" />
                        </div>
                    </div>
                    <div class="eff-user-info">
                        <span class="eff-name">{{ item.name }}</span>
                        <div class="flex items-center gap-1.5 mt-0.5">
                            <span class="eff-company">{{ item.company }}</span>
                            <span class="w-1 h-1 rounded-full bg-gray-300"></span>
                            <span class="eff-status">{{ item.status }}</span>
                        </div>
                    </div>
                </div>
                <div class="eff-score-wrap">
                    <span class="eff-score-txt group-hover:text-[#E85D3E] transition-colors">{{ item.score }}%</span>
                    <div class="eff-track">
                        <!-- Gradient fill for progress -->
                        <div class="eff-fill group-hover:bg-[#E85D3E] transition-colors" :style="`width: ${item.score}%`"></div>
                    </div>
                </div>
            </div>
        </div>
      </div>
    </div>
      
    <!-- Info Modal -->
    <Transition name="fade">
      <div v-if="selectedPlaybookInfo" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm" @click="closeInfo">
        <div class="bg-white rounded-2xl shadow-xl w-full max-w-md overflow-hidden animate-slide-up" style="animation-delay: 0s;" @click.stop>
          <div class="p-6">
            <div class="flex items-start justify-between mb-4">
              <div class="flex items-center gap-3">
                <div class="p-2.5 rounded-xl bg-indigo-50 text-indigo-600">
                  <component :is="selectedPlaybookInfo.icon" class="w-6 h-6" />
                </div>
                <div>
                  <h3 class="text-lg font-bold text-slate-800 leading-tight">{{ selectedPlaybookInfo.name }}</h3>
                  <p class="text-xs font-medium text-slate-500 mt-0.5">{{ selectedPlaybookInfo.desc }}</p>
                </div>
              </div>
              <button @click="closeInfo" class="p-1.5 text-slate-400 hover:text-slate-700 hover:bg-slate-100 rounded-full transition-colors">
                <XMarkIcon class="w-5 h-5" />
              </button>
            </div>
            
            <div class="bg-slate-50/80 p-4 rounded-xl border border-slate-100 mb-6 relative overflow-hidden">
              <div class="absolute top-0 right-0 w-24 h-24 bg-indigo-100 rounded-full blur-2xl opacity-50 -mr-10 -mt-10"></div>
              <h4 class="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-2 relative z-10 flex items-center gap-1.5">
                  <InformationCircleIcon class="w-3.5 h-3.5" />
                  Comment ça marche ?
              </h4>
              <p class="text-sm text-slate-700 leading-relaxed relative z-10">
                {{ selectedPlaybookInfo.fullDesc }}
              </p>
            </div>
            
            <div class="flex justify-end gap-3">
              <button @click="closeInfo" class="px-4 py-2 text-sm font-medium text-slate-600 bg-white border border-slate-200 hover:bg-slate-50 hover:text-slate-800 rounded-lg transition-colors">
                Fermer
              </button>
              <button @click="togglePlaybook(selectedPlaybookInfo); closeInfo()" class="px-4 py-2 text-sm font-medium text-white rounded-lg transition-colors shadow-sm" :class="selectedPlaybookInfo.active ? 'bg-rose-500 hover:bg-rose-600 shadow-rose-200' : 'bg-indigo-600 hover:bg-indigo-700 shadow-indigo-200'">
                {{ selectedPlaybookInfo.active ? 'Désactiver' : 'Activer' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </Transition>

    <!-- Pre-Interview Modal -->
    <Transition name="fade">
      <div v-if="isPreInterviewModalOpen" class="fixed inset-0 z-[65] flex items-center justify-center p-3 bg-slate-900/50 backdrop-blur-sm" @click.self="isPreInterviewModalOpen = false">
        <div class="bg-white rounded-2xl shadow-2xl w-full max-w-2xl flex flex-col overflow-hidden animate-slide-up" style="max-height:90vh; animation-duration:0.35s">
          
          <!-- Header -->
          <div class="flex items-center justify-between px-5 py-4 border-b border-slate-100 bg-gradient-to-r from-slate-50 to-indigo-50/30 shrink-0">
            <div class="flex items-center gap-3">
              <div class="p-2 rounded-xl bg-amber-100 text-amber-600 shadow-inner">
                <LightBulbIcon class="w-5 h-5" />
              </div>
              <div>
                <h2 class="font-extrabold text-slate-800 text-base leading-tight tracking-tight">Pre-Interview Prep</h2>
                <p class="text-[11px] text-slate-500 mt-0.5">Planifiez vos entraînements et STAR methods</p>
              </div>
            </div>
            <button @click="isPreInterviewModalOpen = false" class="p-1.5 rounded-full hover:bg-slate-100 text-slate-400 hover:text-slate-600 transition-colors">
              <XMarkIcon class="w-5 h-5" />
            </button>
          </div>

          <div class="flex-1 overflow-y-auto p-5 custom-scrollbar">
            <div v-if="preInterviewLoading" class="flex flex-col items-center justify-center py-12">
               <div class="w-8 h-8 border-4 border-indigo-500/30 border-t-indigo-600 rounded-full animate-spin mb-3"></div>
               <p class="text-sm text-slate-500 font-medium">Chargement des opportunités...</p>
            </div>

            <div v-else-if="preInterviewPending.length === 0" class="flex flex-col items-center justify-center py-12 text-center">
              <div class="w-16 h-16 bg-slate-50 rounded-full flex items-center justify-center text-slate-300 mb-4">
                 <BriefcaseIcon class="w-8 h-8" />
              </div>
              <h3 class="text-slate-800 font-bold">Aucun entretien en vue ?</h3>
              <p class="text-slate-500 text-xs mt-1 max-w-xs">Ce workflow s'active pour vos candidatures "Applied", "Follow-up" ou "Interview". Continuez à postuler !</p>
            </div>

            <div v-else class="space-y-6">
              <div>
                <label class="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-3 block">Choisissez les entretiens et leurs dates</label>
                <div class="space-y-3">
                  <div v-for="app in preInterviewPending" :key="app.id" 
                    class="flex flex-col p-4 rounded-2xl border transition-all"
                    :class="preInterviewSelections[app.id] ? 'bg-indigo-50 border-indigo-200 shadow-sm' : 'bg-white border-slate-100 hover:border-slate-200'"
                  >
                    <div class="flex items-center justify-between mb-3 cursor-pointer" @click="togglePreInterviewApp(app.id)">
                      <div class="flex items-center gap-3">
                        <div class="w-10 h-10 rounded-xl bg-white border border-slate-100 flex items-center justify-center text-slate-400">
                           <span class="text-xs font-black">{{ app.company_name ? app.company_name.charAt(0) : '?' }}</span>
                        </div>
                        <div class="text-left">
                          <p class="text-sm font-bold text-slate-800">{{ app.company_name }}</p>
                          <p class="text-[10px] text-slate-500">{{ app.job_title }}</p>
                        </div>
                      </div>
                      <div class="w-6 h-6 rounded-lg border flex items-center justify-center transition-colors"
                        :class="preInterviewSelections[app.id] ? 'bg-indigo-600 border-indigo-600 text-white' : 'border-slate-200 bg-white hover:border-indigo-300'"
                      >
                         <CheckIcon v-if="preInterviewSelections[app.id]" class="w-3.5 h-3.5" />
                      </div>
                    </div>

                    <!-- Config for selected item -->
                    <div v-if="preInterviewSelections[app.id]" class="grid grid-cols-2 gap-3 pt-3 border-t border-indigo-100 animate-fade-in">
                       <div>
                         <label class="text-[9px] font-bold text-indigo-400 uppercase mb-1 block">Date Simulation</label>
                         <input type="datetime-local" v-model="preInterviewSelections[app.id].date" 
                           class="w-full bg-white border border-indigo-200 rounded-xl px-3 py-2 text-xs outline-none focus:border-indigo-500 transition-all"
                         />
                       </div>
                       <div>
                         <label class="text-[9px] font-bold text-indigo-400 uppercase mb-1 block">Mode</label>
                         <select v-model="preInterviewSelections[app.id].type" class="w-full bg-white border border-indigo-200 rounded-xl px-3 py-2 text-xs outline-none focus:border-indigo-500 transition-all">
                            <option value="interview">Entretien</option>
                            <option value="star">STAR</option>
                            <option value="both">Complet</option>
                         </select>
                       </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="p-4 bg-slate-50 border-t border-slate-100 flex items-center justify-between shrink-0">
             <p class="text-[10px] text-slate-400 italic">L'IA générera vos questions personnalisées H-2 avant la simulation.</p>
             <button @click="schedulePreInterview" 
               :disabled="Object.keys(preInterviewSelections).length === 0 || Object.values(preInterviewSelections).some(v => !v.date) || preInterviewScheduling"
               class="px-8 py-3 bg-gradient-to-r from-indigo-600 to-indigo-500 text-white rounded-2xl font-extrabold text-sm shadow-lg shadow-indigo-100 hover:shadow-indigo-200 hover:-translate-y-0.5 active:translate-y-0 disabled:opacity-40 disabled:grayscale disabled:translate-y-0 transition-all flex items-center gap-2"
             >
               <span v-if="preInterviewScheduling" class="w-3 h-3 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
               {{ preInterviewScheduling ? 'Planification...' : 'Planifier' }}
             </button>
          </div>

        </div>
      </div>
    </Transition>

    <!-- Gold Profile Modal (Workflow #8) -->
    <Transition name="fade">
      <div v-if="isGoldProfileModalOpen" class="fixed inset-0 z-[65] flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-sm" @click.self="isGoldProfileModalOpen = false">
        <div class="bg-white rounded-[2rem] shadow-2xl w-full max-w-3xl overflow-hidden animate-slide-up flex flex-col max-h-[90vh]">
          <!-- Header -->
          <div class="p-6 border-b border-slate-100 flex items-center justify-between shrink-0 bg-slate-50/50">
            <div class="flex items-center gap-3">
              <div class="w-12 h-12 rounded-2xl bg-indigo-600 flex items-center justify-center text-white shadow-lg shadow-indigo-100">
                <SparklesIcon class="w-6 h-6" />
              </div>
              <div>
                <h2 class="text-lg font-black text-slate-800 tracking-tight">Gold Profile</h2>
                <div class="flex items-center gap-2">
                    <span :class="goldProfileStep === 'audit' ? 'text-indigo-600 font-bold' : 'text-slate-400'" class="text-[10px] uppercase tracking-wider transition-colors">1. Audit</span>
                    <span class="w-1 h-1 rounded-full bg-slate-300"></span>
                    <span :class="goldProfileStep === 'plan' ? 'text-indigo-600 font-bold' : 'text-slate-400'" class="text-[10px] uppercase tracking-wider transition-colors">2. Stratégie</span>
                    <span class="w-1 h-1 rounded-full bg-slate-300"></span>
                    <span :class="goldProfileStep === 'post' ? 'text-indigo-600 font-bold' : 'text-slate-400'" class="text-[10px] uppercase tracking-wider transition-colors">3. Publication</span>
                </div>
              </div>
            </div>
            <button @click="isGoldProfileModalOpen = false" class="p-1.5 rounded-full hover:bg-slate-100 text-slate-400 hover:text-slate-600 transition-colors">
              <XMarkIcon class="w-5 h-5" />
            </button>
          </div>

          <div class="flex-1 overflow-y-auto p-8 space-y-8 custom-scrollbar">
            
            <!-- Loading State -->
            <div v-if="goldProfileLoading" class="py-20 flex flex-col items-center justify-center gap-6">
                <div class="relative">
                    <div class="w-16 h-16 border-4 border-indigo-100 border-t-indigo-600 rounded-full animate-spin"></div>
                    <SparklesIcon class="w-6 h-6 text-indigo-600 absolute inset-0 m-auto animate-pulse" />
                </div>
                <div class="text-center">
                    <p class="text-slate-800 font-black">L'IA façonne votre influence...</p>
                    <p class="text-xs text-slate-400 mt-1">Analyse des algorithmes LinkedIn en cours</p>
                </div>
            </div>

            <!-- STEP 1: AUDIT & OPTIMIZATION -->
            <div v-else-if="goldProfileStep === 'audit'" class="animate-in fade-in slide-in-from-bottom-4 duration-500">
                <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
                    <!-- Headline & About -->
                    <div class="space-y-6">
                        <div class="space-y-2">
                            <label class="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Titre (Headline) Optimisé</label>
                            <div class="p-4 bg-indigo-50/50 border border-indigo-100 rounded-2xl relative group">
                                <p class="text-sm font-bold text-slate-800 leading-snug">{{ goldProfileAuditData?.headline }}</p>
                                <button @click="copyToClipboard(goldProfileAuditData?.headline)" class="absolute top-2 right-2 p-2 bg-white rounded-lg shadow-sm opacity-0 group-hover:opacity-100 transition-opacity">
                                    <DocumentDuplicateIcon class="w-4 h-4 text-indigo-600" />
                                </button>
                            </div>
                        </div>
                        <div class="space-y-2">
                            <label class="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Résumé (About) Storytelling</label>
                            <div class="p-5 bg-slate-900 rounded-2xl relative group">
                                <p class="text-sm text-indigo-50/90 leading-relaxed whitespace-pre-wrap">{{ goldProfileAuditData?.about }}</p>
                                <button @click="copyToClipboard(goldProfileAuditData?.about)" class="absolute top-2 right-2 p-2 bg-slate-800 rounded-lg shadow-sm opacity-0 group-hover:opacity-100 transition-opacity">
                                    <DocumentDuplicateIcon class="w-4 h-4 text-white" />
                                </button>
                            </div>
                        </div>
                    </div>

                    <!-- Score & Fields -->
                    <div class="space-y-6">
                        <div class="bg-white border border-slate-100 rounded-3xl p-6 shadow-sm flex items-center justify-between">
                            <div>
                                <p class="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Score de Profil</p>
                                <p class="text-3xl font-black text-slate-800">{{ goldProfileAuditData?.profile_score }}<span class="text-sm text-slate-300">/100</span></p>
                            </div>
                            <div class="w-16 h-16 rounded-full border-8 border-slate-100 border-t-indigo-600 flex items-center justify-center font-black text-indigo-600">
                                {{ goldProfileAuditData?.profile_score }}%
                            </div>
                        </div>

                        <div class="space-y-3">
                            <label class="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Actions Prioritaires</label>
                            <div v-for="opt in goldProfileAuditData?.field_optimizations" :key="opt.field" class="p-4 bg-slate-50 border border-slate-100 rounded-2xl flex gap-4">
                                <div class="w-8 h-8 rounded-lg bg-white flex items-center justify-center text-slate-400 shadow-sm shrink-0">
                                    <CheckCircleIcon class="w-5 h-5" />
                                </div>
                                <div>
                                    <p class="text-xs font-black text-slate-800 uppercase">{{ opt.field }}</p>
                                    <p class="text-xs text-slate-500 mt-1">{{ opt.suggestion }}</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="mt-10 flex gap-4">
                    <button @click="fetchGoldProfilePlan" class="flex-1 py-4 bg-indigo-600 text-white rounded-2xl font-black text-sm shadow-xl shadow-indigo-100 hover:bg-indigo-700 transition-all flex items-center justify-center gap-2">
                        <span>Établir ma Stratégie de Contenu</span>
                        <ChevronRightIcon class="w-5 h-5" />
                    </button>
                </div>
            </div>

            <!-- STEP 2: CONTENT PLAN -->
            <div v-else-if="goldProfileStep === 'plan'" class="animate-in fade-in slide-in-from-right-4 duration-500">
                <div class="flex items-center justify-between mb-6">
                    <h3 class="text-sm font-black text-slate-800 uppercase tracking-tight">Votre Plan de Publication (30 Jours)</h3>
                    <button @click="goldProfileStep = 'audit'" class="text-[10px] font-bold text-indigo-600 uppercase hover:underline flex items-center gap-1">
                        <ChevronLeftIcon class="w-4 h-4" /> Retour à l'Audit
                    </button>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div v-for="item in goldProfilePlanData" :key="item.day" 
                        @click="generateGoldProfilePost(item)"
                        class="p-4 bg-white border border-slate-100 rounded-2xl hover:border-indigo-500 hover:shadow-md transition-all cursor-pointer group flex items-start gap-4"
                    >
                        <div class="w-10 h-10 rounded-xl bg-slate-50 flex items-center justify-center text-xs font-black text-slate-400 group-hover:bg-indigo-50 group-hover:text-indigo-600 transition-colors">
                            J{{ item.day }}
                        </div>
                        <div class="flex-1 min-w-0">
                            <p class="text-sm font-black text-slate-800 truncate">{{ item.topic }}</p>
                            <p class="text-[10px] text-slate-400 font-medium uppercase mt-1">{{ item.angle }}</p>
                        </div>
                        <ArrowPathIcon class="w-5 h-5 text-slate-200 group-hover:text-indigo-500 transition-colors" />
                    </div>
                </div>
            </div>

            <!-- STEP 3: POST CONTENT -->
            <div v-else-if="goldProfileStep === 'post'" class="animate-in fade-in zoom-in-95 duration-500">
                <div class="max-w-xl mx-auto space-y-6">
                    <div class="flex items-center justify-between">
                        <button @click="goldProfileStep = 'plan'" class="text-[10px] font-bold text-slate-400 uppercase hover:text-slate-600 flex items-center gap-1">
                            <ChevronLeftIcon class="w-4 h-4" /> Retour au Plan
                        </button>
                        <div class="px-3 py-1 bg-indigo-50 text-indigo-600 rounded-full text-[10px] font-black uppercase">Prêt à publier</div>
                    </div>

                    <div class="bg-indigo-50/30 p-4 rounded-2xl border border-indigo-100">
                        <p class="text-[10px] font-bold text-indigo-600 uppercase mb-1">Sujet du Jour :</p>
                        <p class="text-sm font-black text-indigo-900">{{ goldProfileSelectedTopic?.topic }}</p>
                    </div>

                    <div class="space-y-2">
                        <div class="bg-white border border-slate-200 rounded-[2rem] p-8 shadow-2xl shadow-indigo-100/50">
                            <div class="flex items-center gap-3 mb-6">
                                <div class="w-10 h-10 rounded-full bg-indigo-100 flex items-center justify-center text-indigo-600 font-black">
                                    {{ userEmail.charAt(0).toUpperCase() }}
                                </div>
                                <div>
                                    <p class="text-sm font-bold text-slate-900">{{ userEmail.split('@')[0] }}</p>
                                    <p class="text-[10px] text-slate-400">Maintenant • Public</p>
                                </div>
                            </div>
                            <div class="text-sm text-slate-800 leading-relaxed whitespace-pre-wrap font-medium">
                                {{ goldProfilePostData }}
                            </div>
                        </div>
                        <div class="flex gap-4">
                            <button @click="copyToClipboard(goldProfilePostData)" class="flex-1 py-4 bg-slate-900 text-white rounded-2xl font-black text-sm hover:bg-slate-800 transition-all shadow-xl shadow-slate-200 flex items-center justify-center gap-2">
                                <DocumentDuplicateIcon class="w-5 h-5" />
                                <span>Copier le Post</span>
                            </button>
                            <button @click="isGoldProfileModalOpen = false" class="px-8 py-4 bg-white border border-slate-200 rounded-2xl font-black text-sm text-slate-600 hover:bg-slate-50 transition-all">
                                Fermer
                            </button>
                        </div>
                    </div>
                </div>
            </div>

          </div>
          
          <!-- Footer info -->
          <div v-if="goldProfileStep === 'audit'" class="p-6 border-t border-slate-100 bg-slate-50/30 flex items-center justify-between text-[10px] text-slate-400 font-medium">
             <div class="flex items-center gap-2">
                 <div class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></div>
                 Expert Personal Branding actif
             </div>
             <p>Optimisé pour l'algorithme LinkedIn 2024</p>
          </div>
        </div>
      </div>
    </Transition>

    <!-- Post-Interview Modal (Workflow #7) -->
    <Transition name="fade">
      <div v-if="isPostInterviewModalOpen" class="fixed inset-0 z-[65] flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-sm" @click.self="isPostInterviewModalOpen = false">
        <div class="bg-white rounded-[2rem] shadow-2xl w-full max-w-2xl overflow-hidden animate-slide-up flex flex-col max-h-[90vh]">
          <div class="p-6 border-b border-slate-100 flex items-center justify-between shrink-0">
            <div class="flex items-center gap-3">
              <div class="w-12 h-12 rounded-2xl bg-emerald-50 flex items-center justify-center text-emerald-600 shadow-sm shadow-emerald-100">
                <HandThumbUpIcon class="w-6 h-6" />
              </div>
              <div>
                <h2 class="text-lg font-black text-slate-800 tracking-tight">Post-Interview</h2>
                <p class="text-[10px] text-slate-400 font-bold uppercase tracking-wider">Debrief & Remerciement Stratégique</p>
              </div>
            </div>
            <button @click="isPostInterviewModalOpen = false" class="p-1.5 rounded-full hover:bg-slate-100 text-slate-400 hover:text-slate-600 transition-colors">
              <XMarkIcon class="w-5 h-5" />
            </button>
          </div>

          <div class="flex-1 overflow-y-auto p-6 space-y-6">
            <!-- Step 1: Select App -->
            <div v-if="!postInterviewSelectedApp" class="space-y-4">
                <label class="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-2 block">Sélectionnez l'entretien concerné</label>
                <div v-if="postInterviewLoading" class="py-12 flex flex-col items-center justify-center gap-4">
                    <ArrowPathIcon class="w-8 h-8 text-emerald-500 animate-spin" />
                    <p class="text-sm text-slate-400">Chargement de vos entretiens...</p>
                </div>
                <div v-else-if="postInterviewApps.length === 0" class="py-12 text-center bg-slate-50 rounded-2xl border border-dashed border-slate-200">
                    <p class="text-sm text-slate-500 mb-2">Aucun entretien en cours détecté dans le CRM.</p>
                    <p class="text-[10px] text-slate-400 italic">Passez une candidature en statut "Interview" pour l'utiliser ici.</p>
                </div>
                <div v-else class="grid grid-cols-1 gap-3">
                    <button 
                        v-for="app in postInterviewApps" 
                        :key="app.id"
                        @click="postInterviewSelectedApp = app"
                        class="p-4 rounded-xl border border-slate-100 bg-slate-50 hover:border-emerald-500 hover:bg-emerald-50/30 text-left transition-all group"
                    >
                        <div class="flex justify-between items-start">
                            <div>
                                <p class="font-black text-slate-900 text-sm tracking-tight">{{ app.company_name }}</p>
                                <p class="text-xs text-slate-500 font-medium">{{ app.job_title }}</p>
                            </div>
                            <ChevronRightIcon class="w-5 h-5 text-slate-300 group-hover:text-emerald-500 transition-colors" />
                        </div>
                    </button>
                </div>
            </div>

            <!-- Step 2: Debrief Form -->
            <div v-else-if="!postInterviewResult" class="space-y-6">
                <div class="flex items-center gap-3 mb-6">
                    <button @click="postInterviewSelectedApp = null" class="p-2 rounded-lg hover:bg-slate-100 text-slate-400">
                        <ChevronLeftIcon class="w-5 h-5" />
                    </button>
                    <div>
                        <p class="text-xs font-bold text-slate-400 uppercase">Debriefing pour :</p>
                        <p class="text-sm font-black text-slate-800">{{ postInterviewSelectedApp.company_name }}</p>
                    </div>
                </div>

                <div class="space-y-4">
                    <div>
                        <label class="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-2 block">Comment s'est passé l'échange ?</label>
                        <div class="flex gap-2">
                            <button 
                                v-for="mood in ['Excellent', 'Bon', 'Mitigé', 'Difficile']" 
                                :key="mood"
                                @click="postInterviewDebrief.feel = mood"
                                :class="postInterviewDebrief.feel === mood ? 'bg-emerald-600 text-white' : 'bg-slate-50 text-slate-600 hover:bg-slate-100'"
                                class="flex-1 py-2 rounded-lg text-[10px] font-bold transition-all"
                            >{{ mood }}</button>
                        </div>
                    </div>
                    <div>
                        <label class="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-2 block">La question la plus délicate ?</label>
                        <textarea v-model="postInterviewDebrief.hard_question" rows="2" placeholder="Ex: Pourquoi ce trou de 6 mois dans votre CV ?" 
                            class="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-sm focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 outline-none transition-all"
                        ></textarea>
                    </div>
                    <div>
                        <label class="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-2 block">Le besoin n°1 exprimé par le recruteur ?</label>
                        <input v-model="postInterviewDebrief.key_need" type="text" placeholder="Ex: Quelqu'un capable de scaler l'infra rapidement" 
                            class="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-sm focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 outline-none transition-all"
                        />
                    </div>
                </div>

                <button @click="runPostInterview" 
                    :disabled="postInterviewGenerating"
                    class="w-full py-4 bg-emerald-600 text-white rounded-2xl font-black text-sm shadow-xl shadow-emerald-200 hover:bg-emerald-700 transition-all flex items-center justify-center gap-2"
                >
                    <ArrowPathIcon v-if="postInterviewGenerating" class="w-5 h-5 animate-spin" />
                    <span v-if="postInterviewGenerating">Analyse stratégique...</span>
                    <span v-else>Générer mon Debrief & Email</span>
                </button>
            </div>

            <!-- Step 3: Result -->
            <div v-else class="space-y-6">
                <div class="bg-emerald-50 border border-emerald-100 p-4 rounded-2xl">
                    <h3 class="text-xs font-bold text-emerald-800 uppercase mb-2">Analyse GoldArmy :</h3>
                    <p class="text-sm text-emerald-900 leading-relaxed">{{ postInterviewResult.analysis }}</p>
                </div>

                <div class="space-y-2">
                    <div class="flex justify-between items-center px-1">
                        <label class="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Email de Remerciement</label>
                        <button @click="copyToClipboard(postInterviewResult.thank_you_email)" class="text-[10px] font-black text-emerald-600 hover:underline uppercase">Copier l'email</button>
                    </div>
                    <div class="bg-slate-900 rounded-2xl p-6 text-emerald-50/90 text-sm font-medium leading-relaxed font-mono whitespace-pre-wrap max-h-[300px] overflow-y-auto custom-scrollbar">
                        {{ postInterviewResult.thank_you_email }}
                    </div>
                </div>

                <div class="bg-amber-50 border border-amber-100 p-4 rounded-2xl flex gap-3">
                    <InformationCircleIcon class="w-5 h-5 text-amber-500 shrink-0" />
                    <div>
                        <h4 class="text-[10px] font-bold text-amber-800 uppercase">Plan de Relance</h4>
                        <p class="text-xs text-amber-900">{{ postInterviewResult.follow_up_plan }}</p>
                    </div>
                </div>

                <div class="flex gap-4">
                    <button @click="isPostInterviewModalOpen = false" class="flex-1 py-4 bg-slate-900 text-white rounded-2xl font-black text-sm transition-all hover:bg-slate-800 shadow-xl shadow-slate-200">
                        Fermer le Debrief
                    </button>
                </div>
            </div>
          </div>
        </div>
      </div>
    </Transition>
    <Transition name="fade">
      <div v-if="isSocialSniperModalOpen" class="fixed inset-0 z-[65] flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-sm" @click.self="isSocialSniperModalOpen = false">
        <div class="bg-white rounded-[2rem] shadow-2xl w-full max-w-2xl overflow-hidden animate-slide-up flex flex-col max-h-[90vh]">
          <div class="p-6 border-b border-slate-100 flex items-center justify-between shrink-0">
            <div class="flex items-center gap-3">
              <div class="w-12 h-12 rounded-2xl bg-rose-50 flex items-center justify-center text-rose-600 shadow-sm shadow-rose-100">
                <MegaphoneIcon class="w-6 h-6" />
              </div>
              <div>
                <h2 class="text-lg font-black text-slate-800 tracking-tight">Social Sniper</h2>
                <p class="text-[10px] text-slate-400 font-bold uppercase tracking-wider">Arsenal d'Approche Multi-Canal</p>
              </div>
            </div>
            <button @click="isSocialSniperModalOpen = false" class="p-1.5 rounded-full hover:bg-slate-100 text-slate-400 hover:text-slate-600 transition-colors">
              <XMarkIcon class="w-5 h-5" />
            </button>
          </div>

          <div class="flex-1 overflow-y-auto p-6 space-y-6">
            <!-- Form -->
            <div v-if="!socialSniperResult" class="space-y-6">
                <div class="bg-rose-50/50 p-4 rounded-2xl border border-rose-100">
                    <p class="text-[11px] text-rose-700 leading-relaxed">
                        <span class="font-bold">Objectif :</span> Infiltrer le réseau de l'entreprise cible. L'IA génère un kit complet pour vous faire remarquer et obtenir une réponse.
                    </p>
                </div>
                <!-- Quick Select -->
                <div v-if="socialSniperApps.length > 0" class="space-y-2">
                    <label class="text-[9px] font-black text-slate-400 uppercase tracking-widest block mb-2">Sélection Rapide (depuis votre CRM)</label>
                    <div class="flex flex-wrap gap-2">
                        <button 
                            v-for="app in socialSniperApps" 
                            :key="app.id"
                            @click="selectAppForSniper(app)"
                            class="px-3 py-1.5 rounded-full border border-slate-200 bg-white text-[10px] font-bold text-slate-600 hover:border-rose-500 hover:text-rose-600 transition-all"
                        >
                            {{ app.company_name }}
                        </button>
                    </div>
                </div>

                <div class="grid grid-cols-2 gap-4">
                    <div>
                        <label class="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-2 block">Entreprise Cible</label>
                        <input v-model="socialSniperForm.company" type="text" placeholder="Ex: Google" 
                            class="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-sm focus:border-rose-500 focus:ring-1 focus:ring-rose-500 outline-none transition-all"
                        />
                    </div>
                    <div>
                        <label class="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-2 block">Poste Visé</label>
                        <input v-model="socialSniperForm.job" type="text" placeholder="Ex: Senior Dev" 
                            class="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-sm focus:border-rose-500 focus:ring-1 focus:ring-rose-500 outline-none transition-all"
                        />
                    </div>
                </div>
                <button @click="runSocialSniper" 
                    :disabled="socialSniperLoading || !socialSniperForm.company"
                    class="w-full py-4 bg-rose-600 text-white rounded-2xl font-black text-sm shadow-xl shadow-rose-200 hover:bg-rose-700 transition-all flex items-center justify-center gap-2"
                >
                    <ArrowPathIcon v-if="socialSniperLoading" class="w-5 h-5 animate-spin" />
                    <span v-if="socialSniperLoading">Analyse de la cible...</span>
                    <span v-else>Générer mon Kit Sniper</span>
                </button>
            </div>

            <!-- Result Kit -->
            <div v-else class="space-y-6">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <!-- Hook LinkedIn -->
                    <div class="p-4 rounded-2xl bg-slate-50 border border-slate-200 relative group">
                        <span class="absolute -top-2 left-4 px-2 bg-white text-[9px] font-bold text-rose-600 border border-rose-100 rounded-full">#1 HOOK LINKEDIN</span>
                        <p class="text-xs text-slate-600 italic mb-3">Demande de connexion (max 300 chars)</p>
                        <p class="text-sm font-medium text-slate-800 leading-relaxed">{{ socialSniperResult.linkedin_hook }}</p>
                        <button @click="copyToClipboard(socialSniperResult.linkedin_hook)" class="mt-4 text-[10px] font-bold text-rose-600 hover:underline">COPIER LE HOOK</button>
                    </div>

                    <!-- Commentaire Expert -->
                    <div class="p-4 rounded-2xl bg-slate-50 border border-slate-200 relative group">
                        <span class="absolute -top-2 left-4 px-2 bg-white text-[9px] font-bold text-blue-600 border border-blue-100 rounded-full">#2 COMMENTAIRE EXPERT</span>
                        <p class="text-xs text-slate-600 italic mb-3">Sous leur dernier post</p>
                        <p class="text-sm font-medium text-slate-800 leading-relaxed">{{ socialSniperResult.expert_comment }}</p>
                        <button @click="copyToClipboard(socialSniperResult.expert_comment)" class="mt-4 text-[10px] font-bold text-blue-600 hover:underline">COPIER LE COMMENTAIRE</button>
                    </div>

                    <!-- Follow-up -->
                    <div class="p-4 rounded-2xl bg-slate-50 border border-slate-200 relative group">
                        <span class="absolute -top-2 left-4 px-2 bg-white text-[9px] font-bold text-emerald-600 border border-emerald-100 rounded-full">#3 RELANCE STRATÉGIQUE</span>
                        <p class="text-xs text-slate-600 italic mb-3">S'ils acceptent sans répondre</p>
                        <p class="text-sm font-medium text-slate-800 leading-relaxed">{{ socialSniperResult.follow_up }}</p>
                        <button @click="copyToClipboard(socialSniperResult.follow_up)" class="mt-4 text-[10px] font-bold text-emerald-600 hover:underline">COPIER LA RELANCE</button>
                    </div>

                    <!-- Argument Massue -->
                    <div class="p-4 rounded-2xl bg-slate-50 border border-slate-200 relative group">
                        <span class="absolute -top-2 left-4 px-2 bg-white text-[9px] font-bold text-amber-600 border border-amber-100 rounded-full">#4 ARGUMENT MASSUE</span>
                        <p class="text-xs text-slate-600 italic mb-3">Ton "Unfair Advantage"</p>
                        <p class="text-sm font-medium text-slate-800 leading-relaxed">{{ socialSniperResult.power_argument }}</p>
                        <button @click="copyToClipboard(socialSniperResult.power_argument)" class="mt-4 text-[10px] font-bold text-amber-600 hover:underline">COPIER L'ARGUMENT</button>
                    </div>
                </div>

                <div class="bg-slate-900 rounded-2xl p-4 text-center">
                    <p class="text-xs text-slate-400">Conseil : Postez le commentaire <span class="text-white font-bold">AVANT</span> d'envoyer la demande de connexion.</p>
                </div>

                <button @click="socialSniperResult = null" class="w-full text-xs font-bold text-slate-400 hover:text-slate-600 transition-colors uppercase tracking-widest">Recommencer pour une autre cible</button>
            </div>
          </div>
        </div>
      </div>
    </Transition>
    <Transition name="fade">
      <div v-if="isDailyHuntModalOpen" class="fixed inset-0 z-[65] flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-sm" @click.self="isDailyHuntModalOpen = false">
        <div class="bg-white rounded-[2rem] shadow-2xl w-full max-w-md overflow-hidden animate-slide-up flex flex-col max-h-[90vh]">
          <div class="p-6 border-b border-slate-100 flex items-center justify-between shrink-0">
            <div class="flex items-center gap-3">
              <div class="w-12 h-12 rounded-2xl bg-indigo-50 flex items-center justify-center text-indigo-600 shadow-sm shadow-indigo-100">
                <MagnifyingGlassIcon class="w-6 h-6" />
              </div>
              <div>
                <h2 class="text-lg font-black text-slate-800 tracking-tight">Daily Hunt</h2>
                <p class="text-[10px] text-slate-400 font-bold uppercase tracking-wider">Chasse Matinale IA</p>
              </div>
            </div>
            <button @click="isDailyHuntModalOpen = false" class="p-1.5 rounded-full hover:bg-slate-100 text-slate-400 hover:text-slate-600 transition-colors">
              <XMarkIcon class="w-5 h-5" />
            </button>
          </div>

          <div class="flex-1 overflow-y-auto p-6 space-y-6">
            <div class="bg-indigo-50/50 p-4 rounded-2xl border border-indigo-100">
               <p class="text-[11px] text-indigo-700 leading-relaxed">
                 <span class="font-bold">Mode Économique IA :</span> Le système scanne 100+ offres chaque matin. L'IA n'est utilisée que pour valider et scorer les <span class="font-bold">5 meilleures pépites</span> que vous recevrez par mail à 7h00.
               </p>
            </div>

            <div class="space-y-4">
               <div>
                  <label class="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-2 block">Poste Recherché</label>
                  <input v-model="dailyHuntConfig.query" type="text" placeholder="Ex: Développeur Fullstack" 
                    class="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-sm focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 outline-none transition-all"
                  />
               </div>
               <div>
                  <label class="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-2 block">Localisation</label>
                  <input v-model="dailyHuntConfig.location" type="text" placeholder="Ex: Montreal, QC" 
                    class="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-sm focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 outline-none transition-all"
                  />
               </div>
            </div>

            <div class="flex items-center justify-between p-4 rounded-2xl border border-slate-100 bg-slate-50/50">
               <div>
                  <p class="text-sm font-bold text-slate-800">Activation Automatique</p>
                  <p class="text-[10px] text-slate-500">Scan quotidien à 07:00 du matin</p>
               </div>
               <button 
                  @click="dailyHuntConfig.enabled = !dailyHuntConfig.enabled"
                  class="w-12 h-6 rounded-full p-1 transition-colors duration-300"
                  :class="dailyHuntConfig.enabled ? 'bg-indigo-600' : 'bg-slate-300'"
               >
                  <div class="w-4 h-4 bg-white rounded-full transition-transform duration-300"
                    :class="dailyHuntConfig.enabled ? 'translate-x-6' : 'translate-x-0'"
                  ></div>
               </button>
            </div>
          </div>

          <div class="p-6 bg-slate-50 border-t border-slate-100 flex items-center justify-between">
             <p class="text-[10px] text-slate-400 italic italic">Économie : ~120 tokens / jour</p>
             <button @click="toggleDailyHunt" 
               class="px-8 py-3 bg-gradient-to-r from-indigo-600 to-indigo-500 text-white rounded-2xl font-extrabold text-sm shadow-lg shadow-indigo-100 hover:shadow-indigo-200 transition-all"
             >
               Enregistrer
             </button>
          </div>
        </div>
      </div>
    </Transition>
    <Transition name="fade">
      <div v-if="isGhostbusterModalOpen" class="fixed inset-0 z-[65] flex items-center justify-center p-3 bg-slate-900/50 backdrop-blur-sm" @click.self="closeGhostbusterModal">
        <div class="bg-white rounded-2xl shadow-2xl w-full max-w-2xl flex flex-col overflow-hidden animate-slide-up" style="max-height:90vh; animation-duration:0.35s">

          <!-- Header -->
          <div class="flex items-center justify-between px-5 py-4 border-b border-slate-100 bg-gradient-to-r from-slate-50 to-indigo-50/30 shrink-0">
            <div class="flex items-center gap-3">
              <div class="p-2 rounded-xl bg-indigo-100 text-indigo-600 shadow-inner">
                <EnvelopeIcon class="w-5 h-5" />
              </div>
              <div>
                <h2 class="font-extrabold text-slate-800 text-base leading-tight tracking-tight">👻 Ghostbuster — Relances Anti-Fantôme</h2>
                <p class="text-[11px] text-slate-500 mt-0.5">Candidatures sans réponse depuis &gt; 15 jours ouvrables</p>
              </div>
            </div>
            <button @click="closeGhostbusterModal" class="p-1.5 rounded-full hover:bg-slate-100 text-slate-400 hover:text-slate-600 transition-colors">
              <XMarkIcon class="w-5 h-5" />
            </button>
          </div>

          <!-- Controls Bar -->
          <div class="px-5 py-3 border-b border-slate-100 bg-white flex items-center justify-between gap-3 shrink-0 flex-wrap">
            <!-- Stats -->
            <div class="flex items-center gap-3">
              <span class="text-xs text-slate-500 font-medium">
                <span class="font-bold text-slate-800">{{ ghostbusterTotalScanned }}</span> candidatures scannées
              </span>
              <span v-if="ghostbusterResults.length > 0" class="text-xs px-2 py-0.5 bg-amber-50 text-amber-700 font-bold rounded-full border border-amber-200">
                {{ ghostbusterResults.length }} relance(s) à envoyer
              </span>
              <span v-if="ghostbusterLastRun" class="text-[10px] text-slate-400">
                Dernier scan : {{ formatRelativeDate(ghostbusterLastRun) }}
              </span>
            </div>
            <!-- Actions -->
            <div class="flex items-center gap-2">
              <!-- Refresh / Force regenerate -->
              <button @click="runGhostbusterScan(true)" :disabled="isGhostbusterScanning"
                class="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-lg border border-slate-200 bg-white text-slate-600 hover:bg-slate-50 hover:border-indigo-300 hover:text-indigo-600 transition-all disabled:opacity-50">
                <ArrowPathIcon class="w-3.5 h-3.5" :class="isGhostbusterScanning ? 'animate-spin' : ''" />
                Re-générer
              </button>
              <!-- Chain to workflow -->
              <select v-model="ghostbusterChainTo" class="text-[10px] bg-white border border-slate-200 rounded-lg px-2 py-1.5 outline-none font-semibold text-slate-600 cursor-pointer hover:border-indigo-300 transition-colors">
                <option value="none">Aucun chaînage</option>
                <option value="network_ninja">→ Network Ninja (LinkedIn)</option>
                <option value="post_interview">→ Post-Interview (Merci)</option>
              </select>
            </div>
          </div>

          <!-- Mode Auto Toggle Bar -->
          <div class="px-5 py-2.5 border-b border-slate-100 bg-gradient-to-r from-indigo-50/50 to-purple-50/30 flex items-center justify-between shrink-0">
            <div class="flex items-center gap-2">
              <div class="w-1.5 h-1.5 rounded-full animate-pulse" :class="ghostbusterAutoEnabled ? 'bg-emerald-500' : 'bg-slate-300'"></div>
              <span class="text-xs font-semibold text-slate-700">Mode Auto (48h)</span>
              <span class="text-[10px] text-slate-500">— Scan automatique toutes les 48h pour tous tes comptes actifs</span>
            </div>
            <label class="relative inline-flex items-center cursor-pointer">
              <input type="checkbox" :checked="ghostbusterAutoEnabled" @change="toggleGhostbusterAuto" class="sr-only peer">
              <div class="w-10 h-5 bg-slate-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-indigo-600 transition-colors"></div>
            </label>
          </div>

          <!-- Body -->
          <div class="flex-1 overflow-y-auto custom-scrollbar">

            <!-- Loading State -->
            <div v-if="isGhostbusterScanning" class="flex flex-col items-center justify-center py-16 gap-4">
              <div class="relative">
                <div class="w-14 h-14 rounded-full border-4 border-indigo-100 border-t-indigo-500 animate-spin"></div>
                <div class="absolute inset-0 flex items-center justify-center text-xl">👻</div>
              </div>
              <p class="text-sm font-semibold text-slate-600">Scan des candidatures en cours...</p>
              <p class="text-xs text-slate-400">Calcul des jours ouvrables · Génération LLM</p>
            </div>

            <!-- Error State -->
            <div v-else-if="ghostbusterError" class="flex flex-col items-center justify-center py-12 gap-3 text-center px-6">
              <div class="w-12 h-12 rounded-full bg-rose-50 flex items-center justify-center text-2xl">⚠️</div>
              <p class="text-sm font-bold text-rose-600">{{ ghostbusterError }}</p>
              <button @click="runGhostbusterScan()" class="mt-2 px-4 py-2 bg-indigo-600 text-white text-xs font-bold rounded-lg hover:bg-indigo-700 transition-colors">
                Réessayer
              </button>
            </div>

            <!-- Empty State -->
            <div v-else-if="!isGhostbusterScanning && ghostbusterResults.length === 0" class="flex flex-col items-center justify-center py-14 gap-3 text-center px-6">
              <div class="w-16 h-16 rounded-full bg-emerald-50 flex items-center justify-center text-3xl shadow-inner">✅</div>
              <h3 class="text-base font-bold text-slate-800">Aucun fantôme détecté !</h3>
              <p class="text-xs text-slate-500 leading-relaxed max-w-xs">
                Toutes tes candidatures ont reçu une réponse, ou sont envoyées depuis moins de 15 jours ouvrables.
                <br>Scannées : <strong>{{ ghostbusterTotalScanned }}</strong>
              </p>
              <div v-if="ghostbusterTotalScanned === 0" class="mt-2 px-4 py-2 bg-amber-50 border border-amber-200 rounded-xl text-xs text-amber-700 font-medium">
                💡 Ajoute des candidatures dans le CRM avec le statut <strong>APPLIED</strong> pour les suivre ici.
              </div>
            </div>

            <!-- Results List -->
            <div v-else class="p-4 space-y-3">
              <div v-for="item in ghostbusterResults" :key="item.app_id"
                class="rounded-2xl border overflow-hidden transition-all duration-300"
                :class="ghostbusterSent[item.app_id] ? 'border-emerald-200 bg-emerald-50/30' : 'border-slate-200 bg-white hover:border-indigo-200'">

                <!-- Item Header -->
                <div class="flex items-center justify-between px-4 py-3">
                  <div class="flex items-center gap-3 min-w-0">
                    <div class="w-9 h-9 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white font-bold text-sm shadow-sm shrink-0">
                      {{ (item.company_name || '?').charAt(0).toUpperCase() }}
                    </div>
                    <div class="min-w-0">
                      <p class="font-bold text-slate-800 text-sm truncate">{{ item.company_name }}</p>
                      <p class="text-xs text-slate-500 truncate">{{ item.job_title }}</p>
                    </div>
                  </div>
                  <div class="flex items-center gap-2 shrink-0">
                    <!-- Days badge -->
                    <span class="text-[10px] px-2 py-1 rounded-full font-bold"
                      :class="item.working_days_elapsed >= 30 ? 'bg-rose-100 text-rose-600' : 'bg-amber-100 text-amber-700'">
                      {{ item.working_days_elapsed }}j ouv.
                    </span>
                    <!-- Sent badge -->
                    <span v-if="ghostbusterSent[item.app_id]" class="text-[10px] px-2 py-1 bg-emerald-100 text-emerald-700 font-bold rounded-full">
                      ✓ Envoyé
                    </span>
                    <!-- Already generated badge -->
                    <span v-else-if="item.already_generated" class="text-[10px] px-2 py-1 bg-slate-100 text-slate-500 font-medium rounded-full">
                      Existante
                    </span>
                  </div>
                </div>

                <!-- Applied date info -->
                <div class="px-4 pb-2 flex items-center gap-2 text-[10px] text-slate-400">
                  <span>Candidature envoyée le {{ formatRelativeDate(item.applied_at) }}</span>
                </div>

                <!-- Expandable Sections -->
                <div class="border-t border-slate-100 divide-y divide-slate-100">

                  <!-- Email Section -->
                  <div>
                    <button @click="ghostbusterExpandedEmail = ghostbusterExpandedEmail === item.app_id ? null : item.app_id"
                      class="w-full flex items-center justify-between px-4 py-2.5 hover:bg-slate-50 transition-colors text-left">
                      <div class="flex items-center gap-2">
                        <EnvelopeIcon class="w-4 h-4 text-indigo-500" />
                        <span class="text-xs font-semibold text-slate-700">Email de relance</span>
                      </div>
                      <div class="flex items-center gap-2">
                        <button @click.stop="copyGhostbusterText(item.relance_email, item.app_id + '_email')"
                          class="flex items-center gap-1 px-2 py-1 rounded-md text-[10px] font-bold transition-all"
                          :class="ghostbusterCopied[item.app_id + '_email'] ? 'bg-emerald-100 text-emerald-700' : 'bg-indigo-50 text-indigo-600 hover:bg-indigo-100'">
                          <CheckIcon v-if="ghostbusterCopied[item.app_id + '_email']" class="w-3 h-3" />
                          <DocumentDuplicateIcon v-else class="w-3 h-3" />
                          {{ ghostbusterCopied[item.app_id + '_email'] ? 'Copié !' : 'Copier' }}
                        </button>
                        <svg class="w-3.5 h-3.5 text-slate-400 transition-transform duration-200"
                          :class="ghostbusterExpandedEmail === item.app_id ? 'rotate-180' : ''"
                          fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
                        </svg>
                      </div>
                    </button>
                    <Transition name="slide-down">
                      <div v-if="ghostbusterExpandedEmail === item.app_id" class="px-4 pb-3">
                        <pre class="text-[11px] leading-relaxed text-slate-600 bg-slate-50 rounded-xl p-3 whitespace-pre-wrap font-sans border border-slate-100 max-h-48 overflow-y-auto custom-scrollbar">{{ item.relance_email }}</pre>
                      </div>
                    </Transition>
                  </div>

                  <!-- LinkedIn Section -->
                  <div>
                    <button @click="ghostbusterExpandedLinkedin = ghostbusterExpandedLinkedin === item.app_id ? null : item.app_id"
                      class="w-full flex items-center justify-between px-4 py-2.5 hover:bg-slate-50 transition-colors text-left">
                      <div class="flex items-center gap-2">
                        <!-- LinkedIn icon (inline SVG) -->
                        <svg class="w-4 h-4 text-blue-600" fill="currentColor" viewBox="0 0 24 24">
                          <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
                        </svg>
                        <span class="text-xs font-semibold text-slate-700">Message LinkedIn</span>
                      </div>
                      <div class="flex items-center gap-2">
                        <button @click.stop="copyGhostbusterText(item.relance_linkedin, item.app_id + '_linkedin')"
                          class="flex items-center gap-1 px-2 py-1 rounded-md text-[10px] font-bold transition-all"
                          :class="ghostbusterCopied[item.app_id + '_linkedin'] ? 'bg-emerald-100 text-emerald-700' : 'bg-blue-50 text-blue-600 hover:bg-blue-100'">
                          <CheckIcon v-if="ghostbusterCopied[item.app_id + '_linkedin']" class="w-3 h-3" />
                          <DocumentDuplicateIcon v-else class="w-3 h-3" />
                          {{ ghostbusterCopied[item.app_id + '_linkedin'] ? 'Copié !' : 'Copier' }}
                        </button>
                        <svg class="w-3.5 h-3.5 text-slate-400 transition-transform duration-200"
                          :class="ghostbusterExpandedLinkedin === item.app_id ? 'rotate-180' : ''"
                          fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
                        </svg>
                      </div>
                    </button>
                    <Transition name="slide-down">
                      <div v-if="ghostbusterExpandedLinkedin === item.app_id" class="px-4 pb-3">
                        <pre class="text-[11px] leading-relaxed text-slate-600 bg-blue-50/50 rounded-xl p-3 whitespace-pre-wrap font-sans border border-blue-100 max-h-36 overflow-y-auto custom-scrollbar">{{ item.relance_linkedin }}</pre>
                      </div>
                    </Transition>
                  </div>

                  <!-- Mark as Sent -->
                  <div class="px-4 py-2.5 flex items-center justify-between bg-slate-50/50">
                    <span class="text-[10px] text-slate-400">Après envoi, marquer comme :</span>
                    <div class="flex items-center gap-1.5">
                      <button v-if="!ghostbusterSent[item.app_id]"
                        @click="markGhostbusterSent(item.app_id, 'email')"
                        class="px-2.5 py-1 bg-white border border-slate-200 rounded-md text-[10px] font-semibold text-slate-600 hover:border-indigo-300 hover:text-indigo-600 hover:bg-indigo-50 transition-all">
                        ✉️ Email envoyé
                      </button>
                      <button v-if="!ghostbusterSent[item.app_id]"
                        @click="markGhostbusterSent(item.app_id, 'linkedin')"
                        class="px-2.5 py-1 bg-white border border-slate-200 rounded-md text-[10px] font-semibold text-slate-600 hover:border-blue-300 hover:text-blue-600 hover:bg-blue-50 transition-all">
                        💼 LinkedIn envoyé
                      </button>
                      <span v-else class="text-[10px] font-bold text-emerald-600 flex items-center gap-1">
                        <CheckIcon class="w-3.5 h-3.5" /> Relance confirmée
                      </span>
                    </div>
                  </div>

                </div>
              </div>
            </div>
          </div>

          <!-- Footer -->
          <div class="px-5 py-3.5 border-t border-slate-100 bg-slate-50/50 flex items-center justify-between shrink-0">
            <p class="text-[10px] text-slate-400">
              Les relances sont générées par IA et sauvegardées dans le CRM.
            </p>
            <button @click="closeGhostbusterModal" class="px-4 py-2 text-xs font-bold bg-slate-900 text-white rounded-xl hover:bg-black transition-colors shadow-sm">
              Fermer
            </button>
          </div>

        </div>
      </div>
    </Transition>


    <Transition name="fade">
      <div v-if="isSelectionModalOpen" class="fixed inset-0 z-[60] flex items-center justify-center p-4 bg-slate-900/20 backdrop-blur-sm">
        <div class="bg-white border border-slate-200 rounded-2xl shadow-xl w-full max-w-lg overflow-hidden flex flex-col max-h-[80vh]">
          <div class="p-5 border-b border-slate-100 flex items-center justify-between bg-slate-50">
            <h3 class="font-bold text-slate-800 flex items-center gap-2">
              <span class="p-2 rounded-lg bg-indigo-50 text-indigo-500"><DocumentDuplicateIcon class="w-5 h-5"/></span>
              Sélectionner les offres (Max 3)
            </h3>
            <button @click="isSelectionModalOpen = false" class="text-slate-400 hover:text-slate-600">✕</button>
          </div>
          
          <!-- Banner Information -->
          <div class="px-5 py-2.5 bg-indigo-50/50 border-b border-indigo-100/50 flex items-center gap-2">
            <div class="w-1.5 h-1.5 rounded-full bg-indigo-500 animate-pulse"></div>
            <p class="text-[10px] font-bold text-indigo-600 uppercase tracking-tight">Focus : 10 dernières candidatures ajoutées</p>
          </div>

          <div class="flex-1 overflow-y-auto p-4 space-y-3 custom-scrollbar">
            <div v-for="offer in last10RecentApplications" :key="offer.id" 
                 class="flex items-center gap-4 p-4 rounded-xl border border-slate-100 hover:border-indigo-200 hover:bg-indigo-50/30 transition-all cursor-pointer"
                 @click="selectedOffers.includes(offer.id) ? selectedOffers = selectedOffers.filter(id => id !== offer.id) : (selectedOffers.length < 3 && selectedOffers.push(offer.id))">
              <div class="w-5 h-5 rounded border-2 flex items-center justify-center transition-colors" 
                   :class="selectedOffers.includes(offer.id) ? 'bg-indigo-500 border-indigo-500 text-white' : 'border-slate-200'">
                <CheckIcon v-if="selectedOffers.includes(offer.id)" class="w-3 h-3"/>
              </div>
              <div class="flex-1">
                <p class="text-sm font-bold text-slate-800">{{ offer.company }}</p>
                <p class="text-xs text-slate-500">{{ offer.name }}</p>
              </div>
              <span class="text-[10px] px-2 py-1 bg-slate-100 rounded text-slate-500">{{ offer.date }}</span>
            </div>
            <div v-if="last10RecentApplications.length === 0" class="text-center py-10 text-slate-400 text-sm">
              Aucune offre récente disponible dans le CRM.
            </div>
          </div>
          <div class="p-5 border-t border-slate-100 bg-slate-50 flex flex-col gap-4">
             <div class="flex items-center justify-between text-xs font-medium text-slate-500">
                <span>{{ selectedOffers.length }} / 3 sélectionné(s)</span>
                <span v-if="selectedOffers.length === 3" class="text-amber-600">Limite atteinte</span>
             </div>
             <button @click="startBulkExecution" :disabled="selectedOffers.length === 0"
                     class="w-full py-3 bg-indigo-600 text-white rounded-xl font-bold shadow-lg shadow-indigo-100 disabled:opacity-50 disabled:shadow-none hover:bg-indigo-700 transition-all">
               Lancer l'Agent Sniper Smart-Cover
             </button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- Execution Console Modal (Light & Soft Theme) -->
    <Transition name="fade">
      <div v-if="isExecuting" class="fixed inset-0 z-[60] flex items-center justify-center p-4 bg-slate-900/20 backdrop-blur-sm">
        <div class="bg-white border border-slate-200 rounded-2xl shadow-xl w-full max-w-2xl overflow-hidden text-slate-600 flex flex-col h-[550px]">
          
          <!-- Header -->
          <div class="p-4 border-b border-slate-100 flex items-center justify-between bg-slate-50">
            <div class="flex items-center gap-3">
              <div class="p-2 rounded-lg bg-indigo-50 text-indigo-500">
                <component :is="execPlaybook.icon" class="w-5 h-5 animate-pulse" />
              </div>
              <div>
                <h3 class="text-xs font-bold text-slate-800 tracking-wider uppercase">Console d'Exécution</h3>
                <p class="text-xs text-indigo-500 font-medium">WORKFLOW: {{ execPlaybook.name }}</p>
              </div>
            </div>
            <button @click="cancelExecution" class="px-3 py-1.5 text-xs text-slate-400 border border-slate-200 rounded hover:bg-slate-100 hover:text-slate-600 transition-colors">
              Annuler
            </button>
          </div>

          <!-- Body: Stepper and Logs -->
          <div class="flex-1 flex overflow-hidden relative">
            
            <!-- Left Side: Stepper -->
            <div class="w-1/2 p-6 border-r border-slate-100 flex flex-col justify-center gap-6 bg-white">
              <div v-for="(phase, idx) in executionPhases" :key="idx" class="relative flex items-start gap-4 transition-opacity duration-300" :class="execStep >= idx ? 'opacity-100' : 'opacity-40'">
                <!-- Line connector -->
                <div v-if="idx < executionPhases.length - 1" class="absolute left-[11px] top-6 bottom-[-24px] w-[2px] transition-colors duration-500" :class="execStep > idx ? 'bg-indigo-500' : 'bg-slate-100'"></div>
                
                <!-- Circle -->
                <div class="w-6 h-6 rounded-full flex items-center justify-center shrink-0 z-10 transition-all duration-500 bg-white" :class="execStep > idx ? 'bg-indigo-500 border-none text-white shadow-sm shadow-indigo-200' : (execStep === idx ? 'border-2 border-indigo-500 text-indigo-500 bg-indigo-50 animate-pulse' : 'border-2 border-slate-200 text-slate-300')">
                  <svg v-if="execStep > idx" class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
                  <span v-else class="text-[10px] font-bold">{{ idx + 1 }}</span>
                </div>
                
                <div>
                  <h4 class="text-sm font-bold transition-colors duration-300" :class="execStep === idx ? 'text-indigo-600' : 'text-slate-800'">{{ phase.title }}</h4>
                  <p class="text-xs text-slate-500 mt-1 leading-relaxed">{{ phase.desc }}</p>
                </div>
              </div>
            </div>

            <!-- Right Side: Logs -->
            <div class="w-1/2 bg-slate-50/50 p-6 overflow-y-auto font-mono text-[11px] leading-relaxed flex flex-col justify-end custom-scrollbar">
              <div class="flex flex-col gap-3">
                <div v-for="(log, i) in execLogs" :key="i" class="animate-slide-up flex items-start gap-2" style="animation-duration: 0.3s">
                  <span class="text-emerald-500 font-bold shrink-0">→</span>
                  <span class="text-slate-600">{{ log }}</span>
                </div>
                <!-- Typing cursor -->
                <div v-if="execStep < executionPhases.length" class="flex items-center gap-2 text-slate-400 mt-2">
                   <span class="w-1.5 h-3 bg-slate-400 animate-pulse"></span> <span class="font-sans text-xs">Traitement en cours...</span>
                </div>
              </div>
            </div>

            <!-- Success Overlay -->
            <div v-if="execStep >= executionPhases.length" class="absolute inset-0 bg-white/98 backdrop-blur-sm z-20 flex flex-col items-center justify-center p-6 animate-slide-up" style="animation-duration: 0.5s">
              
              <div v-if="!realExecutionResult || !realExecutionResult.isBulk" class="flex flex-col items-center">
                  <div class="w-16 h-16 rounded-full bg-emerald-100 flex items-center justify-center mb-4 border-4 border-white shadow-lg shadow-emerald-100">
                    <div class="w-10 h-10 rounded-full bg-emerald-500 flex items-center justify-center">
                        <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
                    </div>
                  </div>
                  <h2 class="text-2xl font-bold text-slate-800 mb-2">MISSION ACCOMPLIE</h2>
                  <p class="text-slate-500 text-sm">Le Playbook <span class="font-bold text-slate-700">{{ execPlaybook.name }}</span> est maintenant opérationnel.</p>
                  <button @click="isExecuting = false; execPlaybook = null" class="mt-6 px-6 py-2.5 bg-slate-800 text-white rounded-xl font-bold">Quitter</button>
              </div>

              <!-- Résultats Groupés -->
              <div v-else class="w-full h-full flex flex-col overflow-hidden">
                  <div class="mb-6">
                    <h2 class="text-xl font-extrabold text-slate-800">Résultats du Tir Sniper</h2>
                    <p class="text-xs text-slate-500">{{ realExecutionResult.items.length }} documents générés avec succès.</p>
                  </div>

                  <div class="flex-1 overflow-y-auto space-y-4 pr-2 custom-scrollbar">
                    <div v-for="item in realExecutionResult.items" :key="item.company" class="p-4 bg-slate-50 border border-slate-100 rounded-2xl flex items-center justify-between group">
                       <div class="flex items-center gap-4">
                          <div class="w-10 h-10 rounded-xl bg-white border border-slate-100 flex items-center justify-center text-indigo-500 shadow-sm">
                            <DocumentTextIcon class="w-5 h-5"/>
                          </div>
                          <div class="text-left">
                            <p class="text-sm font-bold text-slate-800">Lettre pour {{ item.company }}</p>
                            <p class="text-[10px] text-slate-400">Basé sur {{ item.news.length }} actualités scannées</p>
                          </div>
                       </div>
                       <div class="flex items-center gap-2">
                          <button @click="openLetterPreview(item)" class="p-2.5 rounded-lg bg-white border border-slate-200 text-slate-600 hover:bg-slate-100 transition-all shadow-sm" title="Aperçu">
                             <EyeIcon class="w-5 h-5"/>
                          </button>
                          <button @click="downloadPDF(item)" class="p-2.5 rounded-lg bg-white border border-slate-200 text-indigo-600 hover:bg-indigo-600 hover:text-white hover:border-indigo-600 transition-all shadow-sm" title="Télécharger">
                             <ArrowDownTrayIcon class="w-5 h-5"/>
                          </button>
                       </div>
                    </div>
                  </div>

                  <!-- Options de Persistance & Chaining -->
                  <div class="mt-6 p-4 bg-indigo-50/50 rounded-2xl border border-indigo-100 flex flex-col gap-3">
                     <div class="flex items-center justify-between">
                        <div class="text-left">
                          <p class="text-xs font-bold text-indigo-900">Garder ce Workflow actif ?</p>
                          <p class="text-[10px] text-indigo-600">Génération auto à chaque nouvelle offre détectée.</p>
                        </div>
                        <label class="relative inline-flex items-center cursor-pointer">
                          <input type="checkbox" v-model="execPlaybook.active" class="sr-only peer">
                          <div class="w-9 h-5 bg-slate-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-indigo-600"></div>
                        </label>
                     </div>
                     <div class="flex items-center justify-between border-t border-indigo-100 pt-3">
                        <div class="text-left">
                          <p class="text-xs font-bold text-indigo-900">Brancher à un autre Workflow ?</p>
                          <p class="text-[10px] text-indigo-600">Action suite après génération.</p>
                        </div>
                        <select class="text-[10px] bg-white border border-indigo-200 rounded-lg px-2 py-1 outline-none font-medium text-indigo-700">
                           <option>Aucun</option>
                           <option>Ghostbuster (Relance)</option>
                           <option>Network Ninja (LinkedIn)</option>
                           <option>Daily Hunt (Cron)</option>
                        </select>
                     </div>
                  </div>

                  <button @click="isExecuting = false; execPlaybook = null" class="mt-6 py-3 w-full bg-slate-900 text-white rounded-xl font-bold shadow-lg shadow-slate-200 hover:bg-black transition-all">
                    Terminer la Session
                  </button>
              </div>
            </div>

          </div>
          
        </div>
      </div>
    </Transition>

    <!-- Letter Preview Modal -->
    <Transition name="fade">
      <div v-if="isLetterPreviewOpen" class="fixed inset-0 z-[70] flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-md">
        <div class="bg-white rounded-3xl shadow-2xl w-full max-w-2xl overflow-hidden flex flex-col max-h-[90vh]">
          <div class="p-6 border-b border-slate-100 flex items-center justify-between bg-white sticky top-0 z-10">
            <div class="flex items-center gap-3">
              <div class="p-2 rounded-xl bg-indigo-50 text-indigo-600">
                <DocumentTextIcon class="w-6 h-6"/>
              </div>
              <h3 class="font-bold text-slate-800">Aperçu de la Lettre : {{ currentPreviewLetter?.company }}</h3>
            </div>
            <button @click="isLetterPreviewOpen = false" class="p-2 hover:bg-slate-100 rounded-full transition-colors">
              <XMarkIcon class="w-6 h-6 text-slate-400"/>
            </button>
          </div>
          
          <div class="flex-1 overflow-y-auto p-8 custom-scrollbar bg-slate-50/30">
            <div class="bg-white p-10 shadow-sm border border-slate-100 rounded-lg min-h-[500px] text-slate-700 leading-relaxed font-serif whitespace-pre-wrap">
              {{ currentPreviewLetter?.letter }}
            </div>
          </div>

          <div class="p-6 border-t border-slate-100 bg-white flex items-center justify-between">
             <p v-if="!isPremium" class="text-xs text-amber-600 font-medium flex items-center gap-2">
                <BoltIcon class="w-4 h-4 text-amber-500 animate-pulse"/> Version Standard (Branding GoldArmy inclus)
             </p>
             <div class="flex gap-3 ml-auto">
               <button @click="isLetterPreviewOpen = false" class="px-6 py-2.5 text-slate-600 font-bold hover:bg-slate-50 rounded-xl transition-all">
                 Fermer
               </button>
               <button @click="downloadPDF(currentPreviewLetter); isLetterPreviewOpen = false" 
                       class="px-6 py-2.5 bg-indigo-600 text-white rounded-xl font-bold shadow-lg shadow-indigo-100 hover:bg-indigo-700 transition-all flex items-center gap-2">
                 <ArrowDownTrayIcon class="w-4 h-4"/> Télécharger
               </button>
             </div>
          </div>
        </div>
      </div>
    </Transition>

    <!-- Modal: Premium Upgrade Prompt (For Non-Premium) -->
    <Transition name="fade">
      <div v-if="isPremiumUpgradeModalOpen" class="fixed inset-0 z-[80] flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-md">
        <div class="bg-white rounded-[2rem] shadow-2xl w-full max-w-md overflow-hidden animate-slide-up">
           <div class="p-8 text-center">
              <div class="w-20 h-20 bg-amber-50 rounded-3xl flex items-center justify-center mx-auto mb-6 text-amber-500 shadow-sm">
                <StarIcon class="w-10 h-10 animate-pulse"/>
              </div>
              <h3 class="text-2xl font-black text-slate-800 mb-3">Passez au Niveau Supérieur</h3>
              <p class="text-slate-500 text-sm leading-relaxed mb-8">
                Vous utilisez actuellement la version <b>Standard</b>. Le PDF contiendra le logo GoldArmy et des informations génériques.
                <br><br>
                L'abonnement <b>Premium</b> vous permet d'avoir une lettre 100% propre, sans signature, avec vos vraies coordonnées.
              </p>
              
              <div class="flex flex-col gap-3">
                 <button @click="triggerDownload(false)" class="w-full py-4 rounded-2xl border-2 border-slate-100 text-slate-500 font-bold hover:bg-slate-50 transition-all">
                    Continuer avec Branding
                 </button>
                 <button @click="isPremiumUpgradeModalOpen = false; $router.push('/settings')" class="w-full py-4 rounded-2xl bg-indigo-600 text-white font-bold shadow-xl shadow-indigo-100 hover:bg-indigo-700 transition-all flex items-center justify-center gap-2">
                    <SparklesIcon class="w-5 h-5"/> Devenir Premium
                 </button>
              </div>
              <button @click="isPremiumUpgradeModalOpen = false" class="mt-6 text-xs text-slate-400 font-medium hover:text-slate-600">Peut-être plus tard</button>
           </div>
        </div>
      </div>
    </Transition>

    <!-- Modal: Download Choice (For Premium Users) -->
    <Transition name="fade">
      <div v-if="isDownloadChoiceModalOpen" class="fixed inset-0 z-[80] flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-md">
        <div class="bg-white rounded-[2rem] shadow-2xl w-full max-w-md overflow-hidden animate-slide-up">
           <div class="p-8 text-center">
              <div class="w-20 h-20 bg-indigo-50 rounded-3xl flex items-center justify-center mx-auto mb-6 text-indigo-600 shadow-sm">
                <ShieldCheckIcon class="w-10 h-10"/>
              </div>
              <h3 class="text-2xl font-black text-slate-800 mb-3">Options de Téléchargement</h3>
              <p class="text-slate-500 text-sm mb-8">En tant que membre <b>Premium</b>, vous avez le choix du format de votre lettre.</p>
              
              <div class="grid grid-cols-1 gap-4">
                 <button @click="triggerDownload(true)" class="p-5 rounded-2xl border-2 border-indigo-100 bg-indigo-50/30 text-left hover:border-indigo-500 transition-all group">
                    <div class="flex items-center justify-between mb-1">
                      <span class="font-bold text-indigo-900">Version Professionnelle</span>
                      <CheckIcon class="w-5 h-5 text-indigo-500"/>
                    </div>
                    <p class="text-[10px] text-indigo-600/70 leading-tight">Sans signature GoldArmy, avec vos coordonnées personnelles et logo discret.</p>
                 </button>

                 <button @click="triggerDownload(false)" class="p-5 rounded-2xl border-2 border-slate-100 text-left hover:border-slate-300 transition-all group">
                    <div class="flex items-center justify-between mb-1">
                      <span class="font-bold text-slate-700">Version Standard</span>
                    </div>
                    <p class="text-[10px] text-slate-400 leading-tight">Inclut le branding GoldArmy et les informations génériques.</p>
                 </button>
              </div>

              <button @click="isDownloadChoiceModalOpen = false" class="mt-8 text-sm text-slate-400 hover:text-slate-600">Annuler</button>
           </div>
        </div>
      </div>
    </Transition>

  </div>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
/* ── Variables & Root ── */
.db-root { 
    padding: 2rem; 
    max-width: 1500px; 
    margin: 0 auto; 
    display: flex; 
    flex-direction: column; 
    gap: 1.5rem; 
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    background-color: #F9FAFB; /* Very light gray, almost white */
    min-height: 100vh;
}

/* ── HEADER (Inspiration 2) ── */
.db-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    flex-wrap: wrap;
    gap: 1.5rem;
    background: #FFFFFF;
    padding: 1.5rem;
    border-radius: 1.5rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.02), 0 10px 40px -10px rgba(0,0,0,0.02);
}

.header-date-box {
    display: flex;
    align-items: center;
    gap: 1.2rem;
}

.date-num {
    font-size: 2.5rem;
    font-weight: 300;
    color: #111827;
    line-height: 1;
}

.date-str {
    font-size: 0.9rem;
    color: #6B7280;
    line-height: 1.3;
    max-width: 80px;
}

.date-divider {
    width: 1px;
    height: 40px;
    background-color: #E5E7EB;
    margin: 0 0.5rem;
}

.btn-orange {
    background-color: #E85D3E; /* Warm orange/coral from the mockup */
    color: white;
    padding: 0.7rem 1.2rem;
    border-radius: 999px;
    font-size: 0.85rem;
    font-weight: 500;
    border: none;
    cursor: pointer;
    transition: opacity 0.2s;
}
.btn-orange:hover { opacity: 0.9; }

.btn-icon-white {
    width: 40px;
    height: 40px;
    border-radius: 12px;
    border: 1px solid #E5E7EB;
    background: white;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #4B5563;
    cursor: pointer;
}

.header-greeting {
    display: flex;
    align-items: center;
    gap: 1.5rem;
}

.greeting-text {
    font-size: 2rem;
    font-weight: 500;
    color: #111827;
    line-height: 1.1;
    letter-spacing: -0.02em;
}

/* ── ANIMATIONS GLOBALES ── */
@keyframes floatLogo {
    0%, 100% { transform: translateY(0) scale(1); }
    50% { transform: translateY(-5px) scale(1.05) rotate(3deg); }
}
.animate-float {
    animation: floatLogo 3s ease-in-out infinite;
}

.animate-slide-up {
    opacity: 0;
    animation: slideUpFade 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

@keyframes slideUpFade {
    0% {
        opacity: 0;
        transform: translateY(30px);
    }
    100% {
        opacity: 1;
        transform: translateY(0);
    }
}

.greeting-sub {
    color: #9CA3AF;
}

/* ── KPI GRID (Inspiration 1) ── */
.db-kpi-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
}
@media (max-width: 1024px) { .db-kpi-grid { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 600px) { .db-kpi-grid { grid-template-columns: 1fr; } }

.kpi-card {
    background: #FFFFFF;
    border: 1px solid #F3F4F6;
    border-radius: 16px;
    padding: 1.25rem;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02), 0 2px 4px -1px rgba(0,0,0,0.02);
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    /* Note: on retire transform-origin pour ne pas conflit avec animate-slide-up */
}

.kpi-card:hover {
    transform: translateY(-8px) scale(1.02);
    box-shadow: 0 20px 25px -5px rgba(0,0,0,0.08), 0 10px 10px -5px rgba(0,0,0,0.04);
    border-color: #E5E7EB;
}

.kpi-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
}

.kpi-label {
    font-size: 0.85rem;
    font-weight: 600;
    color: #374151;
    margin-bottom: 0.5rem;
}

.kpi-val-row {
    display: flex;
    align-items: baseline;
    gap: 0.25rem;
}

.kpi-val {
    font-size: 2rem;
    font-weight: 600;
    color: #111827;
    line-height: 1;
}

.kpi-suffix {
    font-size: 0.85rem;
    color: #9CA3AF;
}

.kpi-chart {
    width: 80px;
    height: 40px;
}

.kpi-footer {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    border-top: 1px solid #F3F4F6;
    padding-top: 0.75rem;
    font-size: 0.75rem;
}

.kpi-trend {
    font-weight: 600;
}

.kpi-vs {
    color: #9CA3AF;
}

.kpi-link {
    margin-left: auto;
    color: #4B5563;
    text-decoration: none;
}
.kpi-link:hover { text-decoration: underline; }


/* ── CHARTS ROW ── */
.db-charts-row {
    display: grid;
    grid-template-columns: 1fr;
    gap: 1.5rem;
    margin-top: 1.5rem;
}

@media (min-width: 1024px) {
    .db-charts-row {
        grid-template-columns: repeat(2, 1fr);
    }
}

.chart-main-card, .efficiency-card {
    background: #FFFFFF;
    border: 1px solid #F3F4F6;
    border-radius: 20px;
    padding: 1.5rem;
    box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02), 0 2px 4px -1px rgba(0,0,0,0.02);
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.chart-main-card:hover, .efficiency-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 25px 30px -5px rgba(0,0,0,0.04), 0 15px 15px -5px rgba(0,0,0,0.02);
}

.chart-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
}

.chart-title {
    font-size: 0.95rem;
    font-weight: 600;
    color: #111827;
    margin-bottom: 0.5rem;
}

.chart-huge-val {
    font-size: 1.75rem;
    font-weight: 700;
    color: #111827;
}

.chart-dropdown {
    border: 1px solid #E5E7EB;
    background: transparent;
    padding: 0.3rem 0.6rem;
    border-radius: 4px;
    font-size: 0.8rem;
    color: #4B5563;
    cursor: pointer;
}

.chart-wrapper {
    margin-top: 2rem;
    height: 250px;
    width: 100%;
}

.chart-svg {
    width: 100%;
    height: 100%;
    overflow: visible;
}

/* Animation for the chart line */
.chart-line-anim {
    stroke-dasharray: 2000;
    stroke-dashoffset: 2000;
    animation: drawLine 1.5s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
}

.chart-area-anim {
    opacity: 0;
    animation: fadeArea 1s ease-out 0.5s forwards;
}

@keyframes drawLine {
    to {
        stroke-dashoffset: 0;
    }
}

@keyframes fadeArea {
    to {
        opacity: 1;
    }
}

.bar-anim {
    transform: scaleY(0);
    transform-origin: bottom;
    animation: growBar 1s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
}
.bar-anim-dark {
    transform: scaleY(0);
    transform-origin: bottom;
    animation: growBar 1s cubic-bezier(0.175, 0.885, 0.32, 1.275) 0.2s forwards;
}
@keyframes growBar {
    to { transform: scaleY(1); }
}

/* ── EFFICIENCY LIST ── */
.eff-filters {
    display: flex;
    align-items: center;
}

.segment-control {
    display: flex;
    background: #F3F4F6;
    padding: 3px;
    border-radius: 8px;
    gap: 2px;
}

.segment-btn {
    font-size: 0.72rem;
    font-weight: 700;
    color: #6B7280;
    padding: 0.35rem 0.8rem;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.2s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.segment-btn:hover:not(.active) {
    color: #374151;
}

.segment-btn.active {
    background: #FFFFFF;
    color: #111827;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.03);
}

.eff-list {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.eff-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.85rem 1rem;
    border-radius: 16px;
    background: #FFFFFF;
    border: 1px solid transparent;
    transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    cursor: default;
    position: relative;
    overflow: hidden;
}
.eff-row:hover {
    background: #FFFFFF;
    border-color: #E5E7EB;
    box-shadow: 0 10px 15px -3px rgba(0,0,0,0.04), 0 4px 6px -2px rgba(0,0,0,0.02);
    transform: translateY(-2px);
}

.eff-user {
    display: flex;
    align-items: center;
    gap: 1rem;
    width: 60%;
}

.eff-avatar-wrapper {
    position: relative;
    padding: 2px;
    border-radius: 12px;
    background: #FFFFFF;
    transition: transform 0.3s;
}
.eff-row:hover .eff-avatar-wrapper {
    transform: scale(1.08) rotate(2deg);
}

.eff-avatar {
    width: 42px;
    height: 42px;
    border-radius: 50%;
    background: #F3F4F6;
    color: #111827;
    border: 1px solid #E5E7EB;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.1rem;
    font-weight: 700;
}

.eff-user-info {
    display: flex;
    flex-direction: column;
}

.eff-name {
    font-size: 0.9rem;
    font-weight: 700;
    color: #111827;
    line-height: 1.2;
}

.eff-company {
    font-size: 0.75rem;
    font-weight: 500;
    color: #6B7280;
}

.eff-status {
    font-size: 0.65rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: #9CA3AF;
}

.eff-score-wrap {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    width: 35%;
    gap: 0.5rem;
}

.eff-score-txt {
    font-size: 1rem;
    font-weight: 800;
    color: #111827;
}

.eff-track {
    width: 100%;
    height: 6px;
    background: #F3F4F6;
    position: relative;
    border-radius: 99px;
    overflow: hidden;
    box-shadow: inset 0 1px 2px rgba(0,0,0,0.02);
}

.custom-scrollbar::-webkit-scrollbar {
    width: 6px;
}
.custom-scrollbar::-webkit-scrollbar-track {
    background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
    background: #E5E7EB;
    border-radius: 10px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
    background: #D1D5DB;
}

/* For Firefox */
.custom-scrollbar {
    scrollbar-width: thin;
    scrollbar-color: #E5E7EB transparent;
}


.eff-fill {
    height: 100%;
    background: #111827;
    border-radius: 99px;
    transition: width 1.2s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

/* Ghostbuster slide-down accordion transition */
.slide-down-enter-active,
.slide-down-leave-active {
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
    overflow: hidden;
    max-height: 400px;
}
.slide-down-enter-from,
.slide-down-leave-to {
    max-height: 0;
    opacity: 0;
    transform: translateY(-4px);
}
.slide-down-enter-to,
.slide-down-leave-from {
    max-height: 400px;
    opacity: 1;
    transform: translateY(0);
}

</style>
