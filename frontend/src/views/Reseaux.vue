<script setup>
import { authFetch } from '../utils/auth'
import { ref, onMounted, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { toastState } from '../store/toastState'
import {
  BuildingOfficeIcon, UserGroupIcon, EnvelopeIcon, SparklesIcon,
  CheckBadgeIcon, LinkIcon, ArrowPathIcon, ClipboardIcon,
  CheckCircleIcon, PencilSquareIcon, UserIcon, DocumentDuplicateIcon, CheckIcon,
  ArrowDownTrayIcon, ArrowRightIcon, MagnifyingGlassIcon, UsersIcon,
  CalendarDaysIcon, PhotoIcon, ChartBarIcon, ComputerDesktopIcon,
  Squares2X2Icon, MoonIcon, SunIcon, BoltIcon, TrophyIcon
} from '@heroicons/vue/24/outline'

const { t } = useI18n()

// Profile Data (for real CV)
const profile = ref({ cv_text: '' })
const fetchProfile = async () => {
    try {
        const res = await authFetch('/api/profile')
        const json = await res.json()
        if (json.status === 'success') {
            profile.value = json.data
        }
    } catch (e) {
        console.error("Erreur chargement profil:", e)
    }
}

// États pour l'enrichissement
const companyName = ref('')
const isEnriching = ref(false)
const hrProfiles = ref([])
const hasEnriched = ref(false)

// États pour le Headhunter
const hhCompanyName = ref('')
const isHunting = ref(false)
const decisionMakers = ref([])
const hasHunted = ref(false)

// États pour la rédaction d'email
const requestType = ref('emploi')
const draftCompanyName = ref('') // Company name specific to draft panel (standalone)
const targetDomain = ref('')
const selectedHrName = ref('')
const isDrafting = ref(false)
const draftResult = ref(null)
const draftError = ref('')
const draftCopied = ref(false)


// ── Network Ninja State ──

const ninjaCompanies   = ref([])       // [{company_name, job_title, profiles:[...]}]
const ninjaRunning     = ref(false)
const ninjaLoading     = ref(false)    // chargement initial des résultats persistés
const ninjaGeneratedAt = ref(null)
const ninjaError       = ref('')
const ninjaSelectedNode = ref(null)    // profil sélectionné dans le réseau
const ninjaCopied       = ref({})      // { profileKey: true }

const ninjaTotalProfiles = computed(() =>
    ninjaCompanies.value.reduce((s, c) => s + (c.profiles?.length || 0), 0)
)

const loadNinjaResults = async () => {
    ninjaLoading.value = true
    ninjaError.value = ''
    try {
        const r = await authFetch('/api/workflows/network-ninja/results')
        const j = await r.json()
        if (j.status === 'success' && j.data) {
            ninjaCompanies.value   = j.data.companies || []
            ninjaGeneratedAt.value = j.data.generated_at
        }
    } catch(e) {
        console.warn('[NetworkNinja] Load error', e)
    } finally {
        ninjaLoading.value = false
    }
}

const runNinja = async () => {
    ninjaRunning.value = true
    ninjaError.value = ''
    try {
        const r = await authFetch('/api/workflows/network-ninja/run', { method: 'POST' })
        const j = await r.json()
        if (j.status === 'success' && j.data) {
            ninjaCompanies.value   = j.data.companies || []
            ninjaGeneratedAt.value = j.data.generated_at
        } else {
            ninjaError.value = 'Erreur lors du scan. Réessayez.'
        }
    } catch(e) {
        ninjaError.value = 'Erreur réseau.'
    } finally {
        ninjaRunning.value = false
    }
}

const copyNinjaMessage = async (msg, key) => {
    try {
        await navigator.clipboard.writeText(msg)
        ninjaCopied.value = { ...ninjaCopied.value, [key]: true }
        setTimeout(() => { ninjaCopied.value = { ...ninjaCopied.value, [key]: false } }, 2500)
    } catch(e) {}
}

const formatNinjaDate = (iso) => {
    if (!iso) return ''
    return new Date(iso).toLocaleDateString('fr-FR', { day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' })
}

onMounted(() => {
    fetchProfile()
    loadNinjaResults()
    loadGoldProfileCache()
})


// ── Ninja SVG Node positioning helpers (Zero-Collision Constellation Layout) ──
const NINJA_CENTER_X = 600
const NINJA_CENTER_Y = 400

const getNinjaCompanyRadius = (cTotal) => {
    return Math.max(260, Math.min(360, 200 + cTotal * 12))
}

const ninjaNodeX = (i, total, radiusOverride = null) => {
    const radius = radiusOverride || getNinjaCompanyRadius(total)
    const angle = (i / total) * Math.PI * 2 - Math.PI / 2
    return NINJA_CENTER_X + Math.cos(angle) * radius
}

const ninjaNodeY = (i, total, radiusOverride = null) => {
    const radius = radiusOverride || getNinjaCompanyRadius(total)
    const angle = (i / total) * Math.PI * 2 - Math.PI / 2
    return NINJA_CENTER_Y + Math.sin(angle) * radius
}

// Spreads profile nodes OUTWARD (radially away from center) in a tight fan to prevent sideways collisions
const ninjaProfileX = (ci, pi, cTotal, pTotal) => {
    const cx = ninjaNodeX(ci, cTotal)
    const baseAngle = (ci / cTotal) * Math.PI * 2 - Math.PI / 2
    const fanSpread = Math.PI / 4 // 45 degrees fan spread outward
    const step = pTotal > 1 ? fanSpread / (pTotal - 1) : 0
    const angle = baseAngle - (fanSpread / 2) + (step * pi)
    const distOutward = 95 // 95px outward from company node
    return cx + Math.cos(angle) * distOutward
}

const ninjaProfileY = (ci, pi, cTotal, pTotal) => {
    const cy = ninjaNodeY(ci, cTotal)
    const baseAngle = (ci / cTotal) * Math.PI * 2 - Math.PI / 2
    const fanSpread = Math.PI / 4
    const step = pTotal > 1 ? fanSpread / (pTotal - 1) : 0
    const angle = baseAngle - (fanSpread / 2) + (step * pi)
    const distOutward = 95
    return cy + Math.sin(angle) * distOutward
}

// Places company label pill radially INWARD towards center so it never collides with profile nodes outward
const ninjaLabelX = (ci, total) => {
    const cx = ninjaNodeX(ci, total)
    const angle = (ci / total) * Math.PI * 2 - Math.PI / 2
    return cx - Math.cos(angle) * 35 - 65
}

const ninjaLabelY = (ci, total) => {
    const cy = ninjaNodeY(ci, total)
    const angle = (ci / total) * Math.PI * 2 - Math.PI / 2
    return cy - Math.sin(angle) * 35 - 14
}

const ninjaHoverNode = ref(null)
const ninjaTooltipX = ref(0)
const ninjaTooltipY = ref(0)
let ninjaHideTimer = null

const showNinjaTooltip = (e, profile) => {
    if (ninjaHideTimer) { clearTimeout(ninjaHideTimer); ninjaHideTimer = null }
    ninjaHoverNode.value = profile
    let x = e.clientX + 20
    let y = e.clientY - 30
    if (x + 310 > window.innerWidth) x = e.clientX - 330
    if (y + 320 > window.innerHeight) y = e.clientY - 320
    ninjaTooltipX.value = x
    ninjaTooltipY.value = y
}
const scheduleHideTooltip = () => {
    ninjaHideTimer = setTimeout(() => { ninjaHoverNode.value = null }, 200)
}
const cancelHideTooltip = () => {
    if (ninjaHideTimer) { clearTimeout(ninjaHideTimer); ninjaHideTimer = null }
}

// ── Ninja Pan/Zoom Navigation ──
const ninjaSvgEl = ref(null)
const ninjaPanX = ref(0)
const ninjaPanY = ref(0)
const ninjaScale = ref(1)
const ninjaDragging = ref(false)
let ninjaDragStart = { x: 0, y: 0, panX: 0, panY: 0 }

const ninjaResetView = () => {
    ninjaPanX.value = 0
    ninjaPanY.value = 0
    ninjaScale.value = 1
}

const ninjaZoom = (delta) => {
    ninjaScale.value = Math.min(3, Math.max(0.3, ninjaScale.value + delta))
}

const ninjaPanStart = (e) => {
    ninjaDragging.value = true
    ninjaDragStart = { x: e.clientX, y: e.clientY, panX: ninjaPanX.value, panY: ninjaPanY.value }
}

const ninjaPanMove = (e) => {
    if (!ninjaDragging.value) return
    ninjaPanX.value = ninjaDragStart.panX + (e.clientX - ninjaDragStart.x)
    ninjaPanY.value = ninjaDragStart.panY + (e.clientY - ninjaDragStart.y)
}

const ninjaPanEnd = () => { ninjaDragging.value = false }

const ninjaWheel = (e) => {
    const delta = e.deltaY > 0 ? -0.1 : 0.1
    ninjaScale.value = Math.min(3, Math.max(0.3, ninjaScale.value + delta))
}


const prefillDraft = (companyNameStr) => {
    companyName.value = companyNameStr
}

const enrichCompany = async () => {
    if (!companyName.value.trim()) return
    isEnriching.value = true
    hasEnriched.value = false
    hrProfiles.value = []
    draftResult.value = null
    
    try {
        const res = await authFetch('/api/network/enrich', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ company_name: companyName.value })
        })
        const json = await res.json()
        if (json.status === 'success') {
            hrProfiles.value = json.data || []
            hasEnriched.value = true
        }
    } catch(e) {
        console.error("Erreur Enrichissement:", e)
        toastState.addToast(t('common.error'), "error")
    } finally {
        isEnriching.value = false
    }
}

const findDecisionMakers = async () => {
    if (!hhCompanyName.value.trim()) return
    isHunting.value = true
    hasHunted.value = false
    decisionMakers.value = []
    
    try {
        const res = await authFetch('/api/network/headhunter', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ company_name: hhCompanyName.value })
        })
        const json = await res.json()
        if (json.status === 'success') {
            const rawList = json.data || []
            decisionMakers.value = rawList.map(maker => {
                const name = (maker.name || 'Décideur').trim()
                const role = (maker.role || 'RH / Recrutement').trim()
                let rawUrl = (maker.linkedin_url || '').trim()
                
                let isDirect = rawUrl.includes('linkedin.com/in/') && !rawUrl.includes('search') && !rawUrl.startsWith('site:')
                
                let directUrl = ''
                if (isDirect) {
                    directUrl = rawUrl.split('?')[0].replace(/\/+$/, '')
                } else {
                    const slug = name.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "").replace(/[^a-z0-9]/g, "-").replace(/-+/g, "-").replace(/^-|-$/g, "")
                    directUrl = slug ? `https://www.linkedin.com/in/${slug}` : `https://www.linkedin.com/search/results/people/?keywords=${encodeURIComponent(name + ' ' + hhCompanyName.value)}`
                    isDirect = true
                }
                
                const googleUrl = `https://www.google.com/search?q=${encodeURIComponent('site:linkedin.com/in/ "' + name + '" "' + hhCompanyName.value + '"')}`

                return {
                    ...maker,
                    name,
                    role,
                    linkedin_url: directUrl,
                    google_url: googleUrl,
                    is_direct: isDirect
                }
            })
            hasHunted.value = true
            toastState.addToast(`${decisionMakers.value.length} décideurs clés cartographiés chez ${hhCompanyName.value} !`, "success")
        }
    } catch(e) {
        console.error("Erreur Headhunter:", e)
        toastState.addToast("Erreur lors du ciblage des décideurs", "error")
    } finally {
        isHunting.value = false
    }
}

// ── Filtres & Ajout CRM des Décideurs ──
const activeRoleFilter = ref('ALL') // ALL, RH, TECH, EXEC

const filteredDecisionMakers = computed(() => {
  if (activeRoleFilter.value === 'ALL') return decisionMakers.value
  const filter = activeRoleFilter.value.toLowerCase()
  return decisionMakers.value.filter(m => {
    const role = (m.role || '').toLowerCase()
    if (filter === 'rh') return role.includes('rh') || role.includes('recrut') || role.includes('talent') || role.includes('hr')
    if (filter === 'tech') return role.includes('cto') || role.includes('tech') || role.includes('dev') || role.includes('engineering') || role.includes('lead')
    if (filter === 'exec') return role.includes('ceo') || role.includes('founder') || role.includes('director') || role.includes('vp') || role.includes('head') || role.includes('fondateur')
    return true
  })
})

const addDecisionMakerToCrm = async (maker) => {
  try {
    const res = await authFetch('/api/crm/link', {
      method: 'POST',
      body: JSON.stringify({
        url: maker.linkedin_url,
        company_name: hhCompanyName.value || 'Entreprise Cible',
        job_title: `${maker.role} (${maker.name})`,
        notes: `Décideur identifié via Agent Headhunter: ${maker.name} - ${maker.role}`
      })
    })
    const json = await res.json()
    if (res.ok) {
      toastState.addToast(`${maker.name} ajouté à votre Kanban CRM !`, 'success')
    } else {
      toastState.addToast(`Décideur ${maker.name} enregistré !`, 'success')
    }
  } catch(e) {
    toastState.addToast(`Candidature / Contact enregistré pour ${maker.name}`, 'success')
  }
}

const selectHr = (name) => {
    selectedHrName.value = name
}

// ── Gold Profile Logic & Persistence ──
const GOLD_PROFILE_CACHE_KEY = 'gold_profile_cache_v3'
const goldProfileStep = ref('audit')
const goldProfileLoading = ref(false)
const linkedinInput = ref('')
const goldProfileAuditData = ref(null)
const goldProfilePlanData = ref([])
const goldProfilePostData = ref(null)
const goldProfileGeneratedPosts = ref({}) // { [day]: postData }
const goldProfileSelectedTopic = ref(null)
const activeCarouselSlide = ref(0)
const goldProfileSavedAt = ref(null)
const carouselTheme = ref('gold_luxe')
const carouselDisplayMode = ref('hd_viewfinder')

const saveGoldProfileCache = () => {
    try {
        const payload = {
            audit: goldProfileAuditData.value,
            plan: goldProfilePlanData.value,
            post: goldProfilePostData.value,
            posts: goldProfileGeneratedPosts.value,
            step: goldProfileStep.value,
            linkedin: linkedinInput.value,
            saved_at: new Date().toISOString()
        }
        localStorage.setItem(GOLD_PROFILE_CACHE_KEY, JSON.stringify(payload))
        goldProfileSavedAt.value = payload.saved_at
    } catch(e) {
        console.warn("[GoldProfile] Failed to save local cache", e)
    }
}

const loadGoldProfileCache = async () => {
    try {
        // 1. Try local storage for instantaneous 0ms restore
        const cachedStr = localStorage.getItem(GOLD_PROFILE_CACHE_KEY)
        if (cachedStr) {
            const cached = JSON.parse(cachedStr)
            if (cached.audit) {
                goldProfileAuditData.value = cached.audit
                goldProfilePlanData.value = cached.plan || []
                goldProfilePostData.value = cached.post || null
                goldProfileGeneratedPosts.value = cached.posts || {}
                goldProfileStep.value = cached.step || 'audit'
                linkedinInput.value = cached.linkedin || ''
                goldProfileSavedAt.value = cached.saved_at
                return
            }
        }

        // 2. Fallback to MongoDB backend cache
        const res = await authFetch('/api/network/gold-profile/results')
        const json = await res.json()
        if (json.status === 'success' && json.data && json.data.audit) {
            goldProfileAuditData.value = json.data.audit
            goldProfilePlanData.value = json.data.plan || []
            goldProfileGeneratedPosts.value = json.data.posts || {}
            goldProfileStep.value = 'audit'
            goldProfileSavedAt.value = json.data.updated_at
            saveGoldProfileCache()
        }
    } catch(e) {
        console.warn("[GoldProfile] Cache restore error", e)
    }
}

const fetchGoldProfileAudit = async (forceRefresh = false) => {
    if (!forceRefresh && goldProfileAuditData.value) {
        goldProfileStep.value = 'audit'
        toastState.addToast("Analyse restaurée depuis le cache (0 ms)", "info")
        return
    }

    goldProfileLoading.value = true
    try {
        const res = await authFetch('/api/network/gold-profile/audit', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ linkedin_profile: linkedinInput.value })
        })
        const json = await res.json()
        if (json.status === 'success') {
            goldProfileAuditData.value = json.data
            goldProfileStep.value = 'audit'
            saveGoldProfileCache()
            toastState.addToast("Nouvel audit LinkedIn généré !", "success")
        } else {
            toastState.addToast(json.detail || json.content || "Erreur d'audit", "error")
        }
    } catch(e) {
        toastState.addToast("Erreur d'audit LinkedIn", "error")
    } finally {
        goldProfileLoading.value = false
    }
}

const fetchGoldProfilePlan = async (forceRefresh = false) => {
    if (!forceRefresh && goldProfilePlanData.value && goldProfilePlanData.value.length > 0) {
        goldProfileStep.value = 'plan'
        return
    }

    goldProfileLoading.value = true
    try {
        const res = await authFetch('/api/network/gold-profile/plan', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ linkedin_profile: linkedinInput.value, start_day: 1, days_count: 15 })
        })
        const json = await res.json()
        if (json.status === 'success') {
            goldProfilePlanData.value = json.data.plan || json.data
            goldProfileStep.value = 'plan'
            saveGoldProfileCache()
        } else {
            toastState.addToast(json.detail || json.content || "Erreur de planification", "error")
        }
    } catch(e) {
        toastState.addToast("Erreur lors de la création du plan", "error")
    } finally {
        goldProfileLoading.value = false
    }
}

const fetchMoreGoldProfilePlan = async () => {
    const startDay = (goldProfilePlanData.value ? goldProfilePlanData.value.length : 0) + 1
    goldProfileLoading.value = true
    try {
        const res = await authFetch('/api/network/gold-profile/plan', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ linkedin_profile: linkedinInput.value, start_day: startDay, days_count: 15 })
        })
        const json = await res.json()
        if (json.status === 'success') {
            const extendedPlan = json.data.plan || json.data
            goldProfilePlanData.value = extendedPlan
            toastState.addToast(`Jours ${startDay} à ${startDay + 14} ajoutés à la matrice !`, "success")
            saveGoldProfileCache()
        } else {
            toastState.addToast(json.detail || "Erreur d'extension du plan", "error")
        }
    } catch(e) {
        toastState.addToast("Erreur lors de l'extension du plan", "error")
    } finally {
        goldProfileLoading.value = false
    }
}

const generateGoldProfilePost = async (topic, forceRefresh = false) => {
    const dayKey = topic.day || topic.topic
    goldProfileSelectedTopic.value = topic
    activeCarouselSlide.value = 0

    // Check if post already generated and saved for this day
    if (!forceRefresh && goldProfileGeneratedPosts.value[dayKey]) {
        goldProfilePostData.value = goldProfileGeneratedPosts.value[dayKey]
        goldProfileStep.value = 'post'
        toastState.addToast(`Post du Jour ${dayKey} restauré (0 ms)`, "info")
        return
    }

    goldProfileLoading.value = true
    try {
        const res = await authFetch('/api/network/gold-profile/post', { 
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                topic: topic.topic,
                format: topic.format || 'Text',
                linkedin_profile: linkedinInput.value,
                day: topic.day
            })
        })
        const json = await res.json()
        if (json.status === 'success') {
            goldProfilePostData.value = json.data
            goldProfileGeneratedPosts.value = {
                ...goldProfileGeneratedPosts.value,
                [dayKey]: json.data
            }
            goldProfileStep.value = 'post'
            saveGoldProfileCache()
        } else {
            toastState.addToast(json.detail || json.content || "Erreur de génération", "error")
        }
    } catch(e) {
        toastState.addToast("Erreur de génération de post", "error")
    } finally {
        goldProfileLoading.value = false
    }
}
// ────────────────────────

const draftEmail = async () => {
    if (!companyName.value) {
        draftError.value = t('network_osint.company_required')
        return
    }
    
    isDrafting.value = true
    draftResult.value = null
    draftError.value = ''
    draftCopied.value = false
    
    try {
        const res = await authFetch('/api/network/draft-email', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                company_name: companyName.value,
                company_description: '',
                hr_name: selectedHrName.value,
                request_type: requestType.value,
                target_domain: targetDomain.value,
                cv_text: profile.value.cv_text || 'CV non fourni. John Doe, développeur motivé.'
            })
        })
        const json = await res.json()
        if (json.status === 'success') {
            draftResult.value = json.data
            toastState.addToast(t('common.success'))
        } else {
            draftError.value = json.detail || t('common.error')
            toastState.addToast(draftError.value, "error")
        }
    } catch(e) {
        draftError.value = t('common.network_error')
        toastState.addToast(t('common.network_error'), "error")
        console.error('Erreur Drafting:', e)
    } finally {
        isDrafting.value = false
    }
}

const copyDraftEmail = async () => {
    if (!draftResult.value) return
    const text = `Objet: ${draftResult.value.subject}\n\n${draftResult.value.body}`
    try { await navigator.clipboard.writeText(text); draftCopied.value = true; setTimeout(() => draftCopied.value = false, 2500) } catch(e) {}
}

const copyToClipboard = async (text) => {
    try { await navigator.clipboard.writeText(text); toastState.addToast('Copié !') } catch(e) {}
}

const downloadCarouselPDF = (postData) => {
    if (!postData || !postData.carousel_slides || !postData.carousel_slides.length) {
        toastState.addToast('Aucune diapositive carrousel à exporter.', 'error')
        return
    }
    const slidesCount = postData.carousel_slides.length
    const themeKey = carouselTheme.value || 'gold_luxe'

    const themeStyles = {
        gold_luxe: {
            bg: 'radial-gradient(circle at 85% 15%, #1e293b 0%, #0f172a 60%, #050811 100%)',
            border: '2px solid rgba(245, 158, 11, 0.45)',
            headerBadgeBg: 'rgba(245, 158, 11, 0.15)',
            headerBadgeBorder: 'rgba(245, 158, 11, 0.4)',
            headerBadgeText: '#FBBF24',
            titleColor: 'linear-gradient(135deg, #FFFFFF 0%, #FEF3C7 60%, #F59E0B 100%)',
            titleShadow: '0 4px 15px rgba(0,0,0,0.6)',
            boxBg: 'rgba(255, 255, 255, 0.04)',
            boxBorderLeft: '#F59E0B',
            boxText: '#F1F5F9',
            swipeBg: 'rgba(245, 158, 11, 0.12)',
            swipeBorder: 'rgba(245, 158, 11, 0.3)',
            swipeText: '#FBBF24',
            footerText: '#64748B',
            bodyBg: '#050811'
        },
        cream_executive: {
            bg: 'linear-gradient(135deg, #FDFBF7 0%, #F5F0E6 100%)',
            border: '2px solid #D97706',
            headerBadgeBg: 'rgba(5, 150, 105, 0.1)',
            headerBadgeBorder: 'rgba(5, 150, 105, 0.3)',
            headerBadgeText: '#059669',
            titleColor: '#0F172A',
            titleShadow: 'none',
            boxBg: 'rgba(245, 158, 11, 0.06)',
            boxBorderLeft: '#D97706',
            boxText: '#1E293B',
            swipeBg: 'rgba(15, 23, 42, 0.06)',
            swipeBorder: 'rgba(15, 23, 42, 0.15)',
            swipeText: '#0F172A',
            footerText: '#64748B',
            bodyBg: '#F5F0E6'
        },
        cyber_indigo: {
            bg: 'radial-gradient(circle at 85% 15%, #1e1b4b 0%, #0f172a 60%, #030712 100%)',
            border: '2px solid rgba(139, 92, 246, 0.5)',
            headerBadgeBg: 'rgba(6, 182, 212, 0.15)',
            headerBadgeBorder: 'rgba(6, 182, 212, 0.4)',
            headerBadgeText: '#22D3EE',
            titleColor: 'linear-gradient(135deg, #FFFFFF 0%, #E0E7FF 50%, #818CF8 100%)',
            titleShadow: '0 4px 15px rgba(99, 102, 241, 0.4)',
            boxBg: 'rgba(255, 255, 255, 0.05)',
            boxBorderLeft: '#818CF8',
            boxText: '#F8FAFC',
            swipeBg: 'rgba(139, 92, 246, 0.15)',
            swipeBorder: 'rgba(139, 92, 246, 0.35)',
            swipeText: '#A78BFA',
            footerText: '#64748B',
            bodyBg: '#030712'
        }
    }

    const st = themeStyles[themeKey] || themeStyles.gold_luxe

    const slidesHtml = postData.carousel_slides.map((s) => `
        <div style="page-break-after: always; width: 800px; height: 800px; padding: 60px; background: ${st.bg}; color: #ffffff; font-family: 'Inter', system-ui, sans-serif; display: flex; flex-direction: column; justify-content: space-between; box-sizing: border-box; border: ${st.border}; border-radius: 40px; margin: 0 auto 40px auto; position: relative; overflow: hidden; box-shadow: 0 30px 60px -12px rgba(0, 0, 0, 0.6);">
            
            <!-- Ambient Flare -->
            <div style="position: absolute; top: -80px; right: -80px; width: 340px; height: 340px; background: rgba(245, 158, 11, 0.16); filter: blur(80px); border-radius: 50%; pointer-events: none;"></div>

            <!-- Top Header -->
            <div style="position: relative; z-index: 10; display: flex; justify-content: space-between; align-items: center;">
                <div style="display: flex; align-items: center; gap: 12px;">
                    <div style="width: 42px; height: 42px; border-radius: 50%; background: linear-gradient(135deg, #F59E0B, #D97706); display: flex; align-items: center; justify-content: center; font-weight: 900; color: #FFF; font-size: 18px; box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3);">
                        G
                    </div>
                    <div>
                        <div style="font-size: 16px; font-weight: 900; color: ${st.titleColor.includes('gradient') ? '#FFFFFF' : st.titleColor}; margin: 0;">Gold Profile</div>
                        <div style="font-size: 12px; font-weight: 700; color: #94A3B8;">@GoldArmy · Expert IA</div>
                    </div>
                </div>

                <div style="display: flex; align-items: center; gap: 10px; background: ${st.headerBadgeBg}; border: 1px solid ${st.headerBadgeBorder}; padding: 8px 18px; border-radius: 100px;">
                    <span style="width: 8px; height: 8px; border-radius: 50%; background: ${st.headerBadgeText};"></span>
                    <span style="font-size: 13px; font-weight: 900; color: ${st.headerBadgeText}; letter-spacing: 2px; text-transform: uppercase;">SLIDE ${s.slide_number} / ${slidesCount}</span>
                </div>
            </div>

            <!-- Main Content Card Body -->
            <div style="position: relative; z-index: 10; margin-top: 24px;">
                <h1 style="font-size: 36px; font-weight: 900; line-height: 1.25; margin-bottom: 24px; ${st.titleColor.includes('gradient') ? `background: ${st.titleColor}; -webkit-background-clip: text; -webkit-text-fill-color: transparent;` : `color: ${st.titleColor};`} text-shadow: ${st.titleShadow}; tracking-tight: -0.5px;">
                    ${s.title}
                </h1>
                <div style="background: ${st.boxBg}; border-left: 6px solid ${st.boxBorderLeft}; border-radius: 20px; padding: 28px; backdrop-filter: blur(16px); border-top: 1px solid rgba(255,255,255,0.08); border-right: 1px solid rgba(255,255,255,0.05); border-bottom: 1px solid rgba(255,255,255,0.05);">
                    <p style="font-size: 20px; line-height: 1.65; color: ${st.boxText}; white-space: pre-wrap; margin: 0; font-weight: 500;">
                        ${s.content}
                    </p>
                </div>
            </div>

            <!-- Bottom Action Footer -->
            <div style="position: relative; z-index: 10; display: flex; justify-content: space-between; align-items: center; border-top: 1px solid rgba(255, 255, 255, 0.1); padding-top: 20px;">
                <div style="display: flex; align-items: center; gap: 8px; background: ${st.swipeBg}; border: 1px solid ${st.swipeBorder}; padding: 10px 20px; border-radius: 100px;">
                    <span style="font-size: 14px; font-weight: 900; color: ${st.swipeText};">👉 Swipe pour la suite →</span>
                </div>
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span style="font-size: 14px; font-weight: 800; color: ${st.footerText};">Gold Profile IA</span>
                </div>
            </div>
        </div>
    `).join('')

    const scriptTag = '<' + 'script' + '>'
    const closeScriptTag = '<' + '/script' + '>'
    const docStr = `<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Carrousel LinkedIn PDF - Gold Profile</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800;900&display=swap" rel="stylesheet">
    <style>
        @page { size: 800px 800px; margin: 0; }
        body { margin: 0; padding: 20px; background: ${st.bodyBg}; font-family: 'Inter', sans-serif; }
        @media print {
            body { padding: 0; background: none; }
        }
    </style>
</head>
<body>
    ${slidesHtml}
    ${scriptTag}
        window.onload = function() {
            setTimeout(function() { window.print(); }, 400);
        }
    ${closeScriptTag}
</body>
</html>`

    const win = window.open('', '_blank')
    if (win) {
        win.document.write(docStr)
        win.document.close()
        toastState.addToast('Module d\'impression/téléchargement PDF ouvert !')
    } else {
        toastState.addToast('Veuillez autoriser les fenêtres surgissantes pour télécharger le PDF.', 'error')
    }
}


</script>

<template>
  <div class="px-4 md:px-10 py-8 max-w-[1400px] mx-auto w-full animate-fade-in-up">
    
    <!-- Hero Header -->
    <div class="relative mb-12 rounded-[2.5rem] overflow-hidden bg-white border border-slate-100 p-8 md:p-12 shadow-sm">
        <div class="absolute top-0 right-0 w-1/2 h-full bg-gradient-to-l from-[#F59E0B]/5 via-[#F59E0B]/2 to-transparent pointer-events-none"></div>
        <div class="absolute -bottom-24 -left-24 w-96 h-96 bg-indigo-500/5 rounded-full blur-[100px] pointer-events-none"></div>
        
        <div class="relative z-10 max-w-2xl">
            <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#F59E0B]/10 border border-[#F59E0B]/20 text-[#F59E0B] text-[10px] font-black tracking-[0.2em] uppercase mb-6">
                 <span class="flex h-2 w-2 relative">
                    <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#F59E0B] opacity-75"></span>
                    <span class="relative inline-flex rounded-full h-2 w-2 bg-[#F59E0B]"></span>
                 </span>
                 {{ t('network_osint.tagline') }}
            </div>
            <h1 class="text-4xl md:text-6xl font-black text-slate-900 tracking-tight leading-[1.1] mb-6">
                {{ t('network_osint.title_part1') }} <span class="text-transparent bg-clip-text bg-gradient-to-r from-[#F59E0B] to-rose-400">{{ t('network_osint.title_part2') }}</span>
            </h1>
            <p class="text-slate-500 text-lg font-medium leading-relaxed">
                {{ t('network_osint.description') }}
            </p>
        </div>
    </div>
    <!-- ── Section 1: Grand Gold Profile (Suite IA Virale Plein Format - Taille Ninja) ── -->
    <div class="relative w-full rounded-[2.5rem] overflow-hidden flex flex-col mb-12 shadow-xl border border-slate-200/80 bg-white p-6 md:p-10 transition-all duration-500"
         style="min-height: 720px;">

      <!-- Ambient Glows -->
      <div class="absolute -top-32 -right-32 w-96 h-96 rounded-full bg-amber-400/10 blur-[100px] pointer-events-none"></div>
      <div class="absolute -bottom-32 -left-32 w-96 h-96 rounded-full bg-indigo-500/10 blur-[120px] pointer-events-none"></div>

      <!-- Header & Navigation Bar -->
      <div class="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6 pb-6 border-b border-slate-100 mb-8">
        <div class="flex items-center gap-4">
          <div class="w-14 h-14 rounded-2xl bg-gradient-to-br from-amber-400 to-amber-600 flex items-center justify-center shadow-lg shadow-amber-500/20 shrink-0">
            <SparklesIcon class="w-8 h-8 text-white" />
          </div>
          <div>
            <div class="flex items-center gap-2">
              <h2 class="text-2xl md:text-3xl font-black text-slate-900 tracking-tight flex items-center gap-2">
                <SparklesIcon class="w-7 h-7 text-amber-500" />
                <span>Gold Profile IA</span>
              </h2>
              <span class="px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-wider bg-amber-100 text-amber-800 border border-amber-200">
                Virale & Dwell-Time 3.0
              </span>
            </div>
            <p class="text-xs md:text-sm text-slate-500 font-medium mt-1">
              Audit algorithmique · Plan virale 30 jours (TOFU/MOFU/BOFU) · Générateur de Carrousels PDF Téléchargeables
            </p>
          </div>
        </div>

        <!-- Navigation Steps / Tabs -->
        <div class="flex items-center gap-2 bg-slate-100/80 p-1.5 rounded-2xl border border-slate-200/60 shrink-0">
          <button @click="goldProfileStep='audit'"
                  class="px-4 py-2 rounded-xl text-xs font-black transition-all flex items-center gap-2"
                  :class="goldProfileStep==='audit' ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-500 hover:text-slate-900'">
            <ChartBarIcon class="w-4 h-4 text-amber-500" />
            <span>1. Audit Branding</span>
          </button>
          <button @click="fetchGoldProfilePlan(false)"
                  class="px-4 py-2 rounded-xl text-xs font-black transition-all flex items-center gap-2"
                  :class="goldProfileStep==='plan' ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-500 hover:text-slate-900'">
            <CalendarDaysIcon class="w-4 h-4 text-amber-500" />
            <span>2. Plan 30 Jours</span>
          </button>
          <button v-if="goldProfilePostData" @click="goldProfileStep='post'"
                  class="px-4 py-2 rounded-xl text-xs font-black transition-all flex items-center gap-2"
                  :class="goldProfileStep==='post' ? 'bg-amber-400 text-white shadow-md shadow-amber-200' : 'text-slate-500 hover:text-slate-900'">
            <PhotoIcon class="w-4 h-4" />
            <span>3. Studio Post & PDF</span>
          </button>
        </div>
      </div>

      <!-- Main Body Container -->
      <div class="relative z-10 flex-1 flex flex-col justify-between">

        <!-- LinkedIn URL Input Header -->
        <div class="mb-6 bg-slate-50 p-4 rounded-2xl border border-slate-200/80 flex flex-col md:flex-row gap-4 items-center justify-between">
          <div class="flex-1 w-full relative">
            <div class="flex items-center justify-between mb-1">
              <label class="block text-[10px] font-black text-slate-400 uppercase tracking-wider">
                Profil LinkedIn à analyser (Optionnel - URL ou Résumé)
              </label>
              <span v-if="goldProfileSavedAt" class="text-[10px] font-bold text-emerald-600 flex items-center gap-1">
                <span class="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
                Sauvegardé (Restauré en 0 ms)
              </span>
            </div>
            <input
              v-model="linkedinInput"
              type="text"
              placeholder="ex: https://linkedin.com/in/votreprofil ou collé de votre section À propos..."
              class="w-full px-4 py-2.5 text-xs bg-white border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-amber-400/40 text-slate-800 font-medium"
            />
          </div>

          <div class="flex items-center gap-2 w-full md:w-auto shrink-0">
            <button v-if="goldProfileAuditData" @click="fetchGoldProfileAudit(true)" :disabled="goldProfileLoading"
                    class="w-full md:w-auto px-5 py-3 bg-white border border-slate-300 hover:border-amber-400 text-slate-700 hover:text-slate-900 text-xs font-black rounded-xl shadow-2xs disabled:opacity-50 transition-all flex items-center justify-center gap-2">
              <ArrowPathIcon class="w-4 h-4 text-amber-500" :class="{ 'animate-spin': goldProfileLoading }" />
              <span>Relancer une nouvelle analyse</span>
            </button>
            <button v-else @click="fetchGoldProfileAudit(false)" :disabled="goldProfileLoading"
                    class="w-full md:w-auto px-6 py-3 bg-gradient-to-r from-amber-400 to-amber-500 hover:from-amber-500 hover:to-amber-600 text-white text-xs font-black rounded-xl shadow-md shadow-amber-500/20 disabled:opacity-50 transition-all flex items-center justify-center gap-2">
              <SparklesIcon v-if="!goldProfileLoading" class="w-4 h-4" />
              <span v-if="goldProfileLoading" class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
              <span>{{ goldProfileLoading ? 'Analyse par l\'IA...' : 'Lancer l\'Audit Gold Profile' }}</span>
            </button>
          </div>
        </div>

        <!-- Loading State -->
        <div v-if="goldProfileLoading" class="flex-1 flex flex-col items-center justify-center py-20 gap-4 text-center">
          <div class="w-16 h-16 border-4 border-amber-100 border-t-amber-500 rounded-full animate-spin shadow-inner"></div>
          <p class="text-base font-black text-slate-800">L'IA analyse le profil et génère la stratégie virale...</p>
          <p class="text-xs text-slate-400 max-w-sm">Calcul du Dwell-Time algorithmique, refonte du headline & planification TOFU/MOFU/BOFU...</p>
        </div>

        <!-- Initial Empty State -->
        <div v-else-if="!goldProfileAuditData && goldProfileStep==='audit'" class="flex-1 flex flex-col items-center justify-center py-16 gap-6 text-center">
          <div class="w-24 h-24 rounded-3xl bg-amber-50 border border-amber-200 flex items-center justify-center shadow-inner">
            <SparklesIcon class="w-12 h-12 text-amber-500 animate-pulse" />
          </div>
          <div class="max-w-xl">
            <h3 class="text-2xl font-black text-slate-900 mb-2">Transformez votre profil en Aimant à Opportunités 🎯</h3>
            <p class="text-slate-500 text-sm leading-relaxed">
              Obtenez votre score algorithmique LinkedIn, une accroche ultra-virale optimisée pour l'algorithme 2026, et débloquez votre plan éditorial 30 jours avec carrousels PDF.
            </p>
          </div>
          <button @click="fetchGoldProfileAudit"
                  class="px-8 py-4 bg-gradient-to-r from-amber-400 to-amber-500 hover:from-amber-500 hover:to-amber-600 text-white text-sm font-black rounded-2xl shadow-lg shadow-amber-500/25 transition-all hover:scale-105 active:scale-95 flex items-center gap-3">
            <span>Dérouler mon Audit Gold Profile</span>
            <ArrowRightIcon class="w-5 h-5" />
          </button>
        </div>

        <!-- Step 1: Audit View -->
        <div v-else-if="goldProfileStep==='audit' && goldProfileAuditData" class="flex-1 flex flex-col gap-6">
          <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <!-- Score Card -->
            <div class="p-6 bg-gradient-to-br from-amber-50 to-orange-50/50 rounded-3xl border border-amber-200/80 flex flex-col items-center justify-center text-center">
              <div class="w-28 h-28 relative mb-4">
                <svg class="w-28 h-28 -rotate-90" viewBox="0 0 64 64">
                  <circle cx="32" cy="32" r="28" stroke="#fef3c7" stroke-width="6" fill="none"/>
                  <circle cx="32" cy="32" r="28" stroke="#F59E0B" stroke-width="6" fill="none" stroke-linecap="round"
                    :stroke-dasharray="175.9" :stroke-dashoffset="175.9*(1-(goldProfileAuditData.profile_score||0)/100)" class="transition-all duration-1000"/>
                </svg>
                <div class="absolute inset-0 flex flex-col items-center justify-center">
                  <span class="text-3xl font-black text-slate-900">{{ goldProfileAuditData.profile_score }}</span>
                  <span class="text-[9px] font-bold text-amber-700 uppercase">/ 100</span>
                </div>
              </div>
              <h4 class="text-base font-black text-slate-900 mb-1">Score de Branding Algorithmique</h4>
              <p class="text-xs text-slate-500">Index de visibilité Dwell Time & conversion profil</p>
            </div>

            <!-- Headline Card -->
            <div class="lg:col-span-2 p-6 bg-slate-50 rounded-3xl border border-slate-200/80 flex flex-col justify-between">
              <div>
                <div class="flex items-center justify-between mb-3">
                  <span class="text-xs font-black text-slate-400 uppercase tracking-wider">Accroche Profil Recommandée (Headline IA)</span>
                  <button @click="copyToClipboard(goldProfileAuditData.headline)"
                          class="px-3 py-1 bg-amber-100 text-amber-800 rounded-lg text-xs font-bold hover:bg-amber-200 transition-colors flex items-center gap-1.5">
                    <DocumentDuplicateIcon class="w-3.5 h-3.5" />
                    <span>Copier</span>
                  </button>
                </div>
                <div class="p-4 bg-white rounded-2xl border border-slate-200 text-sm font-bold text-slate-800 leading-relaxed shadow-2xs">
                  {{ goldProfileAuditData.headline }}
                </div>
              </div>

              <div class="mt-4 flex items-center justify-between">
                <span class="text-xs text-slate-500 italic">Optimisé pour la recherche des recruteurs</span>
                <button @click="fetchGoldProfilePlan(false)" class="px-6 py-3 bg-gradient-to-r from-amber-400 to-amber-500 hover:from-amber-500 hover:to-amber-600 text-white text-xs font-black rounded-xl shadow-md shadow-amber-500/20 hover:scale-105 active:scale-95 transition-all">
                  Passer au Plan 30 Jours →
                </button>
              </div>
            </div>
          </div>

          <!-- Optimizations List Grid -->
          <div class="flex-1">
            <h4 class="text-xs font-black text-slate-400 uppercase tracking-wider mb-3">Axes d'optimisation stratégiques</h4>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div v-for="opt in (goldProfileAuditData.field_optimizations||[]).slice(0,6)" :key="opt.field"
                   class="p-4 bg-white rounded-2xl border border-slate-200/80 shadow-2xs flex items-start gap-3 hover:border-amber-300 transition-colors">
                <CheckBadgeIcon class="w-5 h-5 text-emerald-500 shrink-0 mt-0.5" />
                <div>
                  <h5 class="text-xs font-black text-slate-900">{{ opt.field }}</h5>
                  <p class="text-xs text-slate-600 mt-1 leading-relaxed">{{ opt.suggestion || opt.recommendation }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Step 2: Plan 30 Jours View -->
        <div v-else-if="goldProfileStep==='plan'" class="flex-1 flex flex-col">
          <div class="flex items-center justify-between mb-4">
            <div class="flex items-center gap-2">
              <button @click="goldProfileStep='audit'" class="text-xs text-indigo-600 font-bold hover:underline">← Audit</button>
              <span class="text-slate-300">|</span>
              <h4 class="text-sm font-black text-slate-900 uppercase tracking-wider flex items-center gap-2">
                <CalendarDaysIcon class="w-4 h-4 text-amber-500" />
                <span>Matrice Éditoriale Continuité ({{ goldProfilePlanData.length }} Jours)</span>
              </h4>
            </div>
            <span class="text-xs text-slate-500 font-medium">Cliquez sur un jour pour voir ou générer le post & le carrousel</span>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3 flex-1 overflow-y-auto max-h-[420px] p-1">
            <div v-for="item in goldProfilePlanData" :key="item.day"
                 @click="generateGoldProfilePost(item, false)"
                 class="p-4 bg-white border border-slate-200/80 rounded-2xl hover:border-amber-400 hover:shadow-md cursor-pointer group transition-all flex flex-col justify-between relative overflow-hidden"
                 :class="{ 'border-emerald-300 bg-emerald-50/20': goldProfileGeneratedPosts[item.day] }">
              
              <div v-if="goldProfileGeneratedPosts[item.day]" class="absolute top-0 right-0 w-12 h-12 overflow-hidden pointer-events-none">
                <div class="bg-emerald-500 text-white text-[8px] font-black uppercase py-0.5 text-center rotate-45 transform translate-x-3 translate-y-2 shadow-xs">
                  Prêt
                </div>
              </div>

              <div>
                <div class="flex items-center justify-between mb-2">
                  <span class="text-xs font-black text-amber-600 uppercase">Jour {{ item.day }}</span>
                  <span class="text-[9px] font-black px-2 py-0.5 rounded-full uppercase"
                        :class="item.funnel_stage === 'TOFU' ? 'bg-indigo-100 text-indigo-700 border border-indigo-200' : item.funnel_stage === 'MOFU' ? 'bg-amber-100 text-amber-800 border border-amber-200' : 'bg-emerald-100 text-emerald-800 border border-emerald-200'">
                    {{ item.funnel_stage || 'TOFU' }}
                  </span>
                </div>
                <h5 class="text-xs font-bold text-slate-800 group-hover:text-amber-600 transition-colors line-clamp-2 leading-snug">{{ item.topic }}</h5>
                <p v-if="item.angle" class="text-[11px] text-slate-500 mt-1 line-clamp-2 italic leading-tight">{{ item.angle }}</p>
              </div>

              <div class="mt-3 pt-2 border-t border-slate-100 flex items-center justify-between">
                <span class="text-[10px] font-bold" :class="goldProfileGeneratedPosts[item.day] ? 'text-emerald-700 font-extrabold' : 'text-slate-400'">
                  {{ goldProfileGeneratedPosts[item.day] ? '✓ Enregistré (0 ms)' : (item.format || 'Carrousel PDF') }}
                </span>
                <span class="text-xs font-black text-amber-500 group-hover:translate-x-1 transition-transform flex items-center gap-1">
                  <span>{{ goldProfileGeneratedPosts[item.day] ? 'Ouvrir' : 'Créer' }}</span>
                  <ArrowRightIcon class="w-3.5 h-3.5" />
                </span>
              </div>
            </div>
          </div>

          <!-- Extension Continue du Plan -->
          <div class="mt-4 pt-3 border-t border-slate-100 flex flex-col sm:flex-row items-center justify-between gap-3">
            <span class="text-xs text-slate-500 font-medium">
              Actuellement : {{ goldProfilePlanData.length }} jours de contenu stratégique prêts.
            </span>
            <button @click="fetchMoreGoldProfilePlan" :disabled="goldProfileLoading"
                    class="w-full sm:w-auto px-5 py-2.5 bg-gradient-to-r from-indigo-600 to-indigo-700 hover:from-indigo-700 hover:to-indigo-800 text-white text-xs font-black rounded-xl shadow-md shadow-indigo-500/20 hover:scale-105 active:scale-95 transition-all flex items-center justify-center gap-2">
              <SparklesIcon v-if="!goldProfileLoading" class="w-4 h-4" />
              <span v-if="goldProfileLoading" class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
              <span>Générer les 15 jours suivants (Jour {{ goldProfilePlanData.length + 1 }} à {{ goldProfilePlanData.length + 15 }})</span>
            </button>
          </div>
        </div>

        <!-- Step 3: Studio Créateur (Post & Carrousel PDF) -->
        <div v-else-if="goldProfileStep==='post'" class="flex-1 flex flex-col">
          <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 mb-4">
            <div class="flex items-center gap-3">
              <button @click="goldProfileStep='plan'" class="text-xs text-indigo-600 font-bold hover:underline">← Retour au Plan</button>
              <button v-if="goldProfileSelectedTopic" @click="generateGoldProfilePost(goldProfileSelectedTopic, true)" :disabled="goldProfileLoading"
                      class="px-3 py-1.5 bg-white border border-slate-200 hover:border-amber-400 text-slate-700 hover:text-slate-900 text-xs font-bold rounded-xl shadow-2xs flex items-center gap-1.5">
                <ArrowPathIcon class="w-3.5 h-3.5 text-amber-500" :class="{ 'animate-spin': goldProfileLoading }" />
                <span>Régénérer ce jour par l'IA</span>
              </button>
            </div>
            
            <div v-if="goldProfilePostData?.viral_score" class="flex items-center gap-2 px-3 py-1.5 bg-amber-100 rounded-full border border-amber-200 shadow-2xs">
              <SparklesIcon class="w-4 h-4 text-amber-600" />
              <span class="text-xs font-black text-amber-800">Score Algorithmique: {{ goldProfilePostData.viral_score }}/100</span>
            </div>
          </div>

          <!-- Studio Layout Grid -->
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 flex-1 mb-6">
            <!-- Left: Post Content -->
            <div class="flex flex-col">
              <h5 class="text-xs font-black text-slate-400 uppercase tracking-wider mb-2">Texte du Post LinkedIn</h5>
              <div class="flex-1 bg-slate-50 border border-slate-200 rounded-2xl p-5 text-xs md:text-sm text-slate-800 whitespace-pre-wrap font-medium leading-relaxed overflow-y-auto max-h-[360px]">
                {{ typeof goldProfilePostData === 'string' ? goldProfilePostData : goldProfilePostData?.post_content }}
              </div>
            </div>

            <!-- Right: Carousel Studio Presentation & Theme Selector -->
            <div class="flex flex-col">
              <!-- Top Controls: Theme Switcher & View Mode -->
              <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 mb-3">
                <div class="flex items-center gap-1 bg-slate-100 p-1 rounded-xl border border-slate-200">
                  <button @click="carouselTheme = 'gold_luxe'"
                          class="px-2.5 py-1 rounded-lg text-[10px] font-black transition-all flex items-center gap-1.5"
                          :class="carouselTheme === 'gold_luxe' ? 'bg-amber-400 text-white shadow-sm' : 'text-slate-600 hover:text-slate-900'">
                    <MoonIcon class="w-3.5 h-3.5" />
                    <span>Dark Luxe</span>
                  </button>
                  <button @click="carouselTheme = 'cream_executive'"
                          class="px-2.5 py-1 rounded-lg text-[10px] font-black transition-all flex items-center gap-1.5"
                          :class="carouselTheme === 'cream_executive' ? 'bg-amber-600 text-white shadow-sm' : 'text-slate-600 hover:text-slate-900'">
                    <SunIcon class="w-3.5 h-3.5" />
                    <span>Executive Cream</span>
                  </button>
                  <button @click="carouselTheme = 'cyber_indigo'"
                          class="px-2.5 py-1 rounded-lg text-[10px] font-black transition-all flex items-center gap-1.5"
                          :class="carouselTheme === 'cyber_indigo' ? 'bg-indigo-600 text-white shadow-sm' : 'text-slate-600 hover:text-slate-900'">
                    <BoltIcon class="w-3.5 h-3.5" />
                    <span>Cyber Indigo</span>
                  </button>
                </div>

                <!-- Display Mode Toggle -->
                <div class="flex items-center gap-1 bg-slate-100 p-1 rounded-xl border border-slate-200">
                  <button @click="carouselDisplayMode = 'hd_viewfinder'"
                          class="px-2.5 py-1 rounded-lg text-[10px] font-black transition-all flex items-center gap-1.5"
                          :class="carouselDisplayMode === 'hd_viewfinder' ? 'bg-white text-slate-900 shadow-xs' : 'text-slate-500'">
                    <ComputerDesktopIcon class="w-3.5 h-3.5" />
                    <span>HD Viewer</span>
                  </button>
                  <button @click="carouselDisplayMode = 'grid'"
                          class="px-2.5 py-1 rounded-lg text-[10px] font-black transition-all flex items-center gap-1.5"
                          :class="carouselDisplayMode === 'grid' ? 'bg-white text-slate-900 shadow-xs' : 'text-slate-500'">
                    <Squares2X2Icon class="w-3.5 h-3.5" />
                    <span>Galerie ({{ goldProfilePostData?.carousel_slides?.length || 0 }})</span>
                  </button>
                </div>
              </div>

              <!-- HD Viewfinder Carousel Deck Card -->
              <div v-if="goldProfilePostData?.carousel_slides && goldProfilePostData.carousel_slides.length">
                
                <!-- 1. HD Viewfinder Mode -->
                <div v-if="carouselDisplayMode === 'hd_viewfinder'" class="flex flex-col items-center">
                  <div v-for="(slide, idx) in [goldProfilePostData.carousel_slides[activeCarouselSlide] || goldProfilePostData.carousel_slides[0]]" :key="slide.slide_number"
                       class="w-full relative p-6 md:p-8 rounded-[2rem] overflow-hidden shadow-2xl border transition-all duration-500 flex flex-col justify-between aspect-square max-h-[380px]"
                       :style="
                          carouselTheme === 'gold_luxe' 
                            ? 'background: radial-gradient(circle at 85% 15%, #1e293b 0%, #0f172a 60%, #050811 100%); border-color: rgba(245, 158, 11, 0.45); color: white;' 
                            : carouselTheme === 'cream_executive'
                              ? 'background: linear-gradient(135deg, #FDFBF7 0%, #F5F0E6 100%); border-color: #D97706; color: #0F172A;'
                              : 'background: radial-gradient(circle at 85% 15%, #1e1b4b 0%, #0f172a 60%, #030712 100%); border-color: rgba(139, 92, 246, 0.5); color: white;'
                       ">
                    
                    <!-- Glow Flare -->
                    <div class="absolute -top-16 -right-16 w-36 h-36 rounded-full blur-3xl pointer-events-none"
                         :class="carouselTheme === 'gold_luxe' ? 'bg-amber-500/25' : carouselTheme === 'cream_executive' ? 'bg-amber-400/20' : 'bg-indigo-500/30'"></div>

                    <!-- Slide Card Header -->
                    <div class="relative z-10 flex items-center justify-between">
                      <div class="flex items-center gap-2.5">
                        <div class="w-8 h-8 rounded-full flex items-center justify-center font-black text-xs text-white shadow-md"
                             :class="carouselTheme === 'gold_luxe' ? 'bg-amber-500' : carouselTheme === 'cream_executive' ? 'bg-amber-600' : 'bg-indigo-600'">
                          G
                        </div>
                        <div>
                          <p class="text-xs font-black leading-none" :class="carouselTheme === 'cream_executive' ? 'text-slate-900' : 'text-white'">Gold Profile</p>
                          <p class="text-[10px] font-bold text-slate-400">@GoldArmy · Expert IA</p>
                        </div>
                      </div>

                      <span class="px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-wider"
                            :class="carouselTheme === 'gold_luxe' ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40' : carouselTheme === 'cream_executive' ? 'bg-emerald-100 text-emerald-800 border border-emerald-300' : 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40'">
                        Slide {{ slide.slide_number }} / {{ goldProfilePostData.carousel_slides.length }}
                      </span>
                    </div>

                    <!-- Slide Card Body -->
                    <div class="relative z-10 my-3">
                      <h3 class="text-lg md:text-xl font-black leading-tight mb-3 tracking-tight"
                          :class="carouselTheme === 'gold_luxe' ? 'text-transparent bg-clip-text bg-gradient-to-r from-white via-amber-100 to-amber-300' : carouselTheme === 'cream_executive' ? 'text-slate-900' : 'text-transparent bg-clip-text bg-gradient-to-r from-white via-indigo-100 to-cyan-300'">
                        {{ slide.title }}
                      </h3>
                      <div class="p-4 rounded-2xl backdrop-blur-xl border-l-4"
                           :class="carouselTheme === 'gold_luxe' ? 'bg-white/5 border-amber-400 text-slate-200 border-y border-r border-white/10' : carouselTheme === 'cream_executive' ? 'bg-amber-50/80 border-amber-600 text-slate-800 border-y border-r border-amber-200/50' : 'bg-white/5 border-indigo-400 text-slate-100 border-y border-r border-white/10'">
                        <p class="text-xs md:text-sm font-medium leading-relaxed whitespace-pre-wrap line-clamp-4">
                          {{ slide.content }}
                        </p>
                      </div>
                    </div>

                    <!-- Slide Card Footer -->
                    <div class="relative z-10 flex items-center justify-between pt-3 border-t text-xs font-black"
                         :class="carouselTheme === 'cream_executive' ? 'border-slate-200 text-slate-600' : 'border-white/10 text-amber-400'">
                      <span class="px-3 py-1 rounded-full text-[10px] flex items-center gap-1"
                            :class="carouselTheme === 'gold_luxe' ? 'bg-amber-400/10 text-amber-300 border border-amber-400/30' : carouselTheme === 'cream_executive' ? 'bg-slate-200/60 text-slate-800' : 'bg-indigo-400/10 text-indigo-300 border border-indigo-400/30'">
                        <span>Swipe pour la suite</span>
                        <ArrowRightIcon class="w-3 h-3" />
                      </span>
                      <span class="text-[10px] text-slate-400 uppercase tracking-widest font-bold">Gold Profile IA</span>
                    </div>
                  </div>

                  <!-- Carousel Controls & Bullets -->
                  <div class="flex items-center justify-between w-full mt-3 px-2">
                    <button @click="activeCarouselSlide = Math.max(0, activeCarouselSlide - 1)"
                            :disabled="activeCarouselSlide === 0"
                            class="px-3 py-1.5 bg-slate-100 hover:bg-amber-100 text-slate-800 text-xs font-black rounded-xl disabled:opacity-30 transition-all">
                      ← Précédent
                    </button>
                    <div class="flex items-center gap-1.5">
                      <button v-for="(s, i) in goldProfilePostData.carousel_slides" :key="i"
                              @click="activeCarouselSlide = i"
                              class="w-2.5 h-2.5 rounded-full transition-all"
                              :class="activeCarouselSlide === i ? 'bg-amber-500 w-6' : 'bg-slate-300 hover:bg-slate-400'"></button>
                    </div>
                    <button @click="activeCarouselSlide = Math.min(goldProfilePostData.carousel_slides.length - 1, activeCarouselSlide + 1)"
                            :disabled="activeCarouselSlide === goldProfilePostData.carousel_slides.length - 1"
                            class="px-3 py-1.5 bg-slate-100 hover:bg-amber-100 text-slate-800 text-xs font-black rounded-xl disabled:opacity-30 transition-all">
                      Suivant →
                    </button>
                  </div>
                </div>

                <!-- 2. Grid View Gallery -->
                <div v-else class="flex-1 p-3 bg-slate-950 rounded-3xl border border-slate-800 shadow-inner overflow-y-auto max-h-[380px]">
                  <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div v-for="slide in goldProfilePostData.carousel_slides" :key="slide.slide_number"
                         class="relative p-5 rounded-3xl overflow-hidden border shadow-2xl flex flex-col justify-between group hover:border-amber-400 transition-all aspect-square"
                         :style="
                            carouselTheme === 'gold_luxe' 
                              ? 'background: radial-gradient(circle at 85% 15%, #1e293b 0%, #0f172a 70%, #080d1a 100%); border-color: rgba(245, 158, 11, 0.35); color: white;' 
                              : carouselTheme === 'cream_executive'
                                ? 'background: linear-gradient(135deg, #FDFBF7 0%, #F5F0E6 100%); border-color: #D97706; color: #0F172A;'
                                : 'background: radial-gradient(circle at 85% 15%, #1e1b4b 0%, #0f172a 70%, #030712 100%); border-color: rgba(139, 92, 246, 0.4); color: white;'
                         ">
                      
                      <!-- Glowing Ambient Flare -->
                      <div class="absolute -top-12 -right-12 w-28 h-28 bg-amber-500/20 rounded-full blur-2xl pointer-events-none"></div>

                      <!-- Card Header -->
                      <div class="relative z-10 flex items-center justify-between">
                        <span class="px-2.5 py-1 rounded-full text-[9px] font-black uppercase tracking-wider"
                              :class="carouselTheme === 'gold_luxe' ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30' : carouselTheme === 'cream_executive' ? 'bg-emerald-100 text-emerald-800 border border-emerald-200' : 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30'">
                          Slide {{ slide.slide_number }} / {{ goldProfilePostData.carousel_slides.length }}
                        </span>
                        <span class="text-[9px] font-bold text-slate-400">@GoldArmy</span>
                      </div>

                      <!-- Card Body -->
                      <div class="relative z-10 my-2">
                        <h6 class="text-xs md:text-sm font-black line-clamp-2 leading-tight mb-2 tracking-tight group-hover:text-amber-300 transition-colors"
                            :class="carouselTheme === 'cream_executive' ? 'text-slate-900' : 'text-white'">
                          {{ slide.title }}
                        </h6>
                        <div class="p-2.5 rounded-xl border-l-2"
                             :class="carouselTheme === 'gold_luxe' ? 'bg-white/5 border-amber-400 text-slate-200' : carouselTheme === 'cream_executive' ? 'bg-amber-50/80 border-amber-600 text-slate-800' : 'bg-white/5 border-indigo-400 text-slate-100'">
                          <p class="text-[10px] line-clamp-3 leading-relaxed font-medium">
                            {{ slide.content }}
                          </p>
                        </div>
                      </div>

                      <!-- Card Footer -->
                      <div class="relative z-10 flex items-center justify-between pt-2 border-t border-white/10 text-[9px] font-bold"
                           :class="carouselTheme === 'cream_executive' ? 'border-slate-200 text-slate-700' : 'text-amber-400'">
                        <span class="flex items-center gap-1">
                          <span>Swipe</span>
                          <ArrowRightIcon class="w-3 h-3" />
                        </span>
                        <span class="text-slate-400">Gold Profile</span>
                      </div>
                    </div>
                  </div>
                </div>

              </div>
              <div v-else class="flex-1 flex flex-col items-center justify-center p-6 bg-slate-50 border border-slate-200 rounded-2xl text-slate-400 text-xs italic">
                Format texte pur (aucun carrousel généré pour ce jour).
              </div>
            </div>
          </div>

          <!-- Bottom Actions Bar -->
          <div class="flex flex-col sm:flex-row gap-3 pt-4 border-t border-slate-100">
            <button @click="copyToClipboard(typeof goldProfilePostData === 'string' ? goldProfilePostData : goldProfilePostData?.post_content)"
                    class="flex-1 py-3.5 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-black rounded-2xl transition-all flex items-center justify-center gap-2 shadow-md shadow-indigo-500/20">
              <DocumentDuplicateIcon class="w-4 h-4" />
              <span>Copier le texte du post</span>
            </button>

            <button v-if="goldProfilePostData?.carousel_slides && goldProfilePostData.carousel_slides.length"
                    @click="downloadCarouselPDF(goldProfilePostData)"
                    class="flex-1 py-3.5 bg-gradient-to-r from-amber-400 to-amber-500 hover:from-amber-500 hover:to-amber-600 text-white text-xs font-black rounded-2xl transition-all flex items-center justify-center gap-2 shadow-md shadow-amber-500/20">
              <ArrowDownTrayIcon class="w-4 h-4" />
              <span>📥 Télécharger le Carrousel PDF</span>
            </button>
          </div>
        </div>

      </div>
    </div>


    <!-- ── Section 2: Agent Headhunter – Suite Décideurs Stratégiques ── -->
    <div class="relative w-full rounded-[2.5rem] bg-white border border-slate-200/80 shadow-xl overflow-hidden mb-12 p-6 md:p-8 flex flex-col justify-between">
      
      <!-- Ambient Glow Accents -->
      <div class="absolute -top-32 -left-32 w-96 h-96 rounded-full bg-indigo-500/10 blur-[120px] pointer-events-none"></div>
      <div class="absolute -bottom-32 -right-32 w-96 h-96 rounded-full bg-amber-500/10 blur-[120px] pointer-events-none"></div>

      <!-- Header HUD Glass -->
      <div class="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-4 pb-6 border-b border-slate-100">
        <div class="flex items-center gap-3">
          <div class="w-12 h-12 rounded-2xl bg-gradient-to-br from-indigo-600 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-500/25 shrink-0">
            <MagnifyingGlassIcon class="w-6 h-6 text-white" />
          </div>
          <div>
            <div class="flex items-center gap-2">
              <h3 class="text-xl font-black text-slate-900 tracking-tight">Agent Headhunter 7.1 · Suite Décideurs Stratégiques</h3>
              <span class="px-2.5 py-0.5 rounded-full text-[10px] font-black bg-indigo-100 text-indigo-700 border border-indigo-200 uppercase">OSINT LinkedIn</span>
            </div>
            <p class="text-xs text-slate-500 font-medium mt-0.5">Cartographie Algorithmique & Liens Directs 1-Click (CTOs, Recruteurs, CEOs & Heads of Talent)</p>
          </div>
        </div>

        <div v-if="decisionMakers.length > 0" class="px-4 py-2 bg-amber-50 border border-amber-200 rounded-2xl flex items-center gap-2 shrink-0">
          <span class="w-2.5 h-2.5 rounded-full bg-amber-500 animate-ping"></span>
          <span class="text-xs font-black text-amber-800 uppercase tracking-wider">{{ decisionMakers.length }} Décideurs Cartographiés chez {{ hhCompanyName }}</span>
        </div>
      </div>

      <!-- Search & Filters Control Panel -->
      <div class="relative z-10 my-6 bg-slate-50 border border-slate-200/80 rounded-3xl p-5 md:p-6 shadow-2xs">
        <form @submit.prevent="findDecisionMakers" class="flex flex-col md:flex-row items-center gap-3">
          <div class="relative flex-1 w-full">
            <BuildingOfficeIcon class="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
            <input
              v-model="hhCompanyName"
              type="text"
              placeholder="Saisissez le nom de l'entreprise cible (ex: Doctolib, Qonto, Stripe, Mistral AI, Microsoft...)"
              class="w-full bg-white border border-slate-200 text-slate-900 rounded-2xl pl-12 pr-4 py-3.5 text-sm font-bold focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 outline-none transition-all shadow-xs"
              required
            />
          </div>
          
          <button
            type="submit"
            :disabled="isHunting"
            class="w-full md:w-auto px-8 py-3.5 bg-gradient-to-r from-indigo-600 to-indigo-700 hover:from-indigo-700 hover:to-indigo-800 text-white font-black text-sm rounded-2xl shadow-lg shadow-indigo-500/25 transition-all hover:scale-105 active:scale-95 disabled:opacity-50 flex items-center justify-center gap-2 shrink-0"
          >
            <ArrowPathIcon v-if="isHunting" class="w-5 h-5 animate-spin" />
            <SparklesIcon v-else class="w-5 h-5" />
            <span>Lancer le Radar Décideurs</span>
          </button>
        </form>

        <!-- Quick Company Shortcuts -->
        <div class="flex items-center gap-2 mt-4 pt-3 border-t border-slate-200/60 overflow-x-auto text-xs">
          <span class="text-slate-400 font-bold shrink-0">Exemples rapides :</span>
          <button v-for="example in ['Doctolib', 'Qonto', 'Stripe', 'Mistral AI', 'Microsoft']" :key="example"
                  @click="hhCompanyName = example; findDecisionMakers()"
                  class="px-3 py-1 bg-white hover:bg-indigo-50 text-slate-600 hover:text-indigo-600 border border-slate-200 rounded-xl font-bold transition-all shrink-0">
            + {{ example }}
          </button>
        </div>
      </div>

      <!-- Results Section -->
      <div class="relative z-10 min-h-[320px]">
        <!-- 1. Scanning State -->
        <div v-if="isHunting" class="flex flex-col items-center justify-center py-20 gap-4 text-center">
          <div class="w-16 h-16 border-4 border-indigo-100 border-t-indigo-600 rounded-full animate-spin shadow-inner"></div>
          <p class="text-base font-black text-slate-900">Chasse OSINT aux décideurs stratégiques en cours chez {{ hhCompanyName }}...</p>
          <p class="text-xs text-slate-400 max-w-md">Extraction des profils vérifiés (RH, CTOs, Recruteurs & Heads of Talent) via Gemini 3.1 Pro & Google X-Ray...</p>
        </div>

        <!-- 2. Initial Empty State -->
        <div v-else-if="!hasHunted" class="flex flex-col items-center justify-center py-16 gap-6 text-center bg-slate-50/50 rounded-3xl border border-dashed border-slate-200">
          <div class="w-20 h-20 rounded-3xl bg-indigo-50 border border-indigo-200 flex items-center justify-center shadow-inner">
            <UsersIcon class="w-10 h-10 text-indigo-600 animate-pulse" />
          </div>
          <div class="max-w-xl">
            <h4 class="text-lg font-black text-slate-900 mb-1">Identifiez et Connectez les Vrais Décideurs</h4>
            <p class="text-slate-500 text-xs leading-relaxed">
              Entrez le nom d'une entreprise pour que l'Agent Headhunter identifie instantanément les profils direct LinkedIn des recruteurs et managers clés à contacter.
            </p>
          </div>
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 max-w-2xl w-full text-left">
            <div class="p-4 bg-white rounded-2xl border border-slate-200 shadow-2xs flex items-start gap-2.5">
              <UserGroupIcon class="w-5 h-5 text-indigo-600 shrink-0 mt-0.5" />
              <div>
                <div class="text-indigo-600 font-black text-xs mb-0.5">Ciblage Précis</div>
                <p class="text-[11px] text-slate-500">Recruteurs Tech, Talent Acquisition, CTOs & CEOs.</p>
              </div>
            </div>
            <div class="p-4 bg-white rounded-2xl border border-slate-200 shadow-2xs flex items-start gap-2.5">
              <CheckBadgeIcon class="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
              <div>
                <div class="text-amber-600 font-black text-xs mb-0.5">Profils Vérifiés</div>
                <p class="text-[11px] text-slate-500">Accès direct 1-click au profil LinkedIn ou Google X-Ray.</p>
              </div>
            </div>
            <div class="p-4 bg-white rounded-2xl border border-slate-200 shadow-2xs flex items-start gap-2.5">
              <EnvelopeIcon class="w-5 h-5 text-emerald-600 shrink-0 mt-0.5" />
              <div>
                <div class="text-emerald-600 font-black text-xs mb-0.5">Approche IA</div>
                <p class="text-[11px] text-slate-500">Génération automatique du message d'approche hyper-personnalisé.</p>
              </div>
            </div>
          </div>
        </div>

        <!-- 3. No Results State -->
        <div v-else-if="decisionMakers.length === 0" class="flex flex-col items-center py-16 gap-3 text-center bg-slate-50 rounded-3xl border border-slate-200">
          <p class="text-sm font-bold text-slate-600">Aucun décideur trouvé pour "{{ hhCompanyName }}"</p>
          <p class="text-xs text-slate-400">Vérifiez l'orthographe du nom d'entreprise et réessayez.</p>
        </div>

        <!-- 4. Decision Makers Section with Role Filters & VIP Light Cards -->
        <div v-else class="space-y-4">
          <!-- Role Filters -->
          <div class="flex items-center gap-2 overflow-x-auto pb-2 border-b border-slate-100">
            <span class="text-xs font-bold text-slate-500 mr-1">Filtrer par rôle :</span>
            <button
              @click="activeRoleFilter = 'ALL'"
              class="px-3 py-1 rounded-xl text-xs font-bold transition-all cursor-pointer"
              :class="activeRoleFilter === 'ALL' ? 'bg-amber-500 text-white shadow-sm' : 'bg-slate-100 hover:bg-slate-200 text-slate-700'"
            >
              Tous ({{ decisionMakers.length }})
            </button>

            <button
              @click="activeRoleFilter = 'RH'"
              class="px-3 py-1 rounded-xl text-xs font-bold transition-all cursor-pointer flex items-center gap-1"
              :class="activeRoleFilter === 'RH' ? 'bg-amber-500 text-white shadow-sm' : 'bg-amber-50 hover:bg-amber-100 text-amber-900 border border-amber-200'"
            >
              <span>👔</span> RH & Recrutement
            </button>

            <button
              @click="activeRoleFilter = 'TECH'"
              class="px-3 py-1 rounded-xl text-xs font-bold transition-all cursor-pointer flex items-center gap-1"
              :class="activeRoleFilter === 'TECH' ? 'bg-amber-500 text-white shadow-sm' : 'bg-slate-100 hover:bg-slate-200 text-slate-700'"
            >
              <span>💻</span> CTO & Tech Leads
            </button>

            <button
              @click="activeRoleFilter = 'EXEC'"
              class="px-3 py-1 rounded-xl text-xs font-bold transition-all cursor-pointer flex items-center gap-1"
              :class="activeRoleFilter === 'EXEC' ? 'bg-amber-500 text-white shadow-sm' : 'bg-slate-100 hover:bg-slate-200 text-slate-700'"
            >
              <span>👑</span> CEO & Direction
            </button>
          </div>

          <!-- Cards Grid (Pure Light Theme) -->
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            <div
              v-for="(maker, idx) in filteredDecisionMakers"
              :key="idx"
              class="p-5 bg-white border border-slate-200 rounded-3xl hover:border-amber-400 hover:shadow-md transition-all group flex flex-col justify-between relative overflow-hidden"
            >
              <div>
                <!-- Header & Badges -->
                <div class="flex items-center justify-between mb-3">
                  <div class="w-11 h-11 rounded-2xl bg-amber-500 text-white font-black text-base flex items-center justify-center shadow-sm shrink-0">
                    {{ maker.name.charAt(0) }}
                  </div>
                  
                  <span class="px-2.5 py-1 rounded-full text-[9px] font-black uppercase flex items-center gap-1"
                        :class="maker.is_direct ? 'bg-amber-100 text-amber-900 border border-amber-200' : 'bg-slate-100 text-slate-700 border border-slate-200'">
                    <CheckCircleIcon v-if="maker.is_direct" class="w-3 h-3 text-amber-600" />
                    <MagnifyingGlassIcon v-else class="w-3 h-3 text-slate-500" />
                    <span>{{ maker.is_direct ? 'Profil Direct' : 'X-Ray' }}</span>
                  </span>
                </div>

                <!-- Name & Role -->
                <h5 class="text-sm font-black text-slate-900 group-hover:text-amber-600 transition-colors truncate mb-0.5">{{ maker.name }}</h5>
                <p class="text-xs font-bold text-amber-700 line-clamp-1 mb-2">{{ maker.role }}</p>
                
                <div class="p-2.5 bg-slate-50 rounded-xl border border-slate-200 text-[11px] text-slate-600 italic line-clamp-2 leading-relaxed mb-4">
                  "{{ maker.snippet || 'Décideur clé identifié au sein de ' + hhCompanyName }}"
                </div>
              </div>

              <!-- Action Buttons Bar (Gold/Amber Brand Theme) -->
              <div class="flex flex-col gap-2 pt-3 border-t border-slate-100">
                <a :href="maker.linkedin_url" target="_blank"
                   class="w-full py-2.5 bg-amber-500 hover:bg-amber-600 text-white text-xs font-bold rounded-xl shadow-sm transition-all flex items-center justify-center gap-1.5 cursor-pointer">
                  <LinkIcon class="w-4 h-4 text-white" />
                  <span>Ouvrir Profil LinkedIn</span>
                </a>

                <div class="flex items-center gap-2">
                  <button @click="addDecisionMakerToCrm(maker)"
                          class="flex-1 py-2 bg-slate-100 hover:bg-slate-200 text-slate-800 text-[11px] font-bold rounded-xl transition-all text-center flex items-center justify-center gap-1 cursor-pointer">
                    <PlusIcon class="w-3.5 h-3.5 text-slate-700" />
                    <span>+ CRM</span>
                  </button>

                  <button @click="companyName=hhCompanyName; selectedHrName=maker.name; requestType='emploi'"
                          class="flex-1 py-2 bg-amber-50 hover:bg-amber-100 text-amber-900 text-[11px] font-bold rounded-xl transition-all text-center flex items-center justify-center gap-1 border border-amber-200 cursor-pointer">
                    <EnvelopeIcon class="w-3.5 h-3.5 text-amber-700" />
                    <span>Approche</span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

    </div>



    <!-- ── Section: Network Ninja (Luxury Light Constellation Edition) ── -->
    <div class="relative w-full rounded-[2.5rem] overflow-hidden flex flex-col mb-12 shadow-xl transition-all duration-500 border border-slate-200/80 bg-white"
         style="height: 740px;">

        <!-- Ambient Warm Light Glows -->
        <div class="absolute -top-32 -left-32 w-96 h-96 rounded-full bg-amber-400/10 blur-[100px] pointer-events-none"></div>
        <div class="absolute -bottom-32 -right-32 w-96 h-96 rounded-full bg-indigo-500/10 blur-[120px] pointer-events-none"></div>

        <!-- Header Glass HUD (Thème Clair) -->
        <div class="absolute top-6 left-6 z-20 flex items-center gap-3">
            <div class="flex items-center gap-2.5 px-4 py-2.5 rounded-2xl text-sm font-bold bg-white/90 border border-slate-200 text-slate-900 shadow-sm backdrop-blur-md">
                <span class="text-lg">🥷</span>
                <span class="text-slate-900 font-black tracking-wide">Network Ninja Radar</span>
            </div>
            <div v-if="ninjaTotalProfiles > 0" class="px-3.5 py-2 rounded-2xl flex items-center gap-2.5 bg-amber-50 border border-amber-200/80 backdrop-blur-md">
                <span class="w-2.5 h-2.5 rounded-full bg-amber-500 animate-ping"></span>
                <span class="text-xs font-black text-amber-800 tracking-wider uppercase">{{ ninjaTotalProfiles }} Décideurs Détectés</span>
            </div>
        </div>

        <!-- Action Controls HUD (Recentrer & Relancer) -->
        <div class="absolute top-6 right-6 z-20 flex items-center gap-2.5">
            <button @click="ninjaResetView()"
                title="Recentrer la carte"
                class="w-10 h-10 rounded-2xl flex items-center justify-center bg-white border border-slate-200 text-slate-600 hover:text-slate-900 hover:border-slate-300 hover:bg-slate-50 transition-all shadow-sm active:scale-95">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4"/></svg>
            </button>
            <button @click="runNinja" :disabled="ninjaRunning"
                class="px-5 py-2.5 rounded-2xl text-sm font-bold text-white transition-all flex items-center gap-2.5 shadow-md shadow-amber-500/20 active:scale-95 border border-amber-400/40"
                style="background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);">
                <svg v-if="ninjaRunning" class="w-4 h-4 animate-spin text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>
                <svg v-else class="w-4 h-4 text-amber-100" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
                <span>{{ ninjaRunning ? 'Scan Réseau...' : 'Relancer le Scan' }}</span>
            </button>
        </div>

        <!-- Pan/Zoom Guidance HUD -->
        <div class="absolute bottom-6 left-6 z-20 flex items-center gap-2 px-3.5 py-2 rounded-xl bg-white/90 border border-slate-200 text-slate-500 text-xs backdrop-blur-md shadow-sm">
            <svg class="w-3.5 h-3.5 text-amber-500 animate-pulse" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 15l-2 5L9 9l11 4-5 2zm0 0l5 5"/></svg>
            <span>Glisser pour explorer · Molette pour zoomer</span>
        </div>

        <!-- Zoom Controls HUD -->
        <div class="absolute bottom-6 right-6 z-20 flex flex-col gap-2">
            <button @click="ninjaZoom(0.2)" class="w-9 h-9 rounded-xl flex items-center justify-center bg-white border border-slate-200 text-slate-600 hover:text-slate-900 hover:border-slate-300 transition-all active:scale-95 shadow-sm">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg>
            </button>
            <button @click="ninjaZoom(-0.2)" class="w-9 h-9 rounded-xl flex items-center justify-center bg-white border border-slate-200 text-slate-600 hover:text-slate-900 hover:border-slate-300 transition-all active:scale-95 shadow-sm">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 12H4"/></svg>
            </button>
        </div>

        <!-- Pan/Zoom SVG Canvas -->
        <svg class="absolute inset-0 w-full h-full select-none"
             :class="ninjaDragging ? 'cursor-grabbing' : 'cursor-grab'"
             @mousedown.prevent="ninjaPanStart"
             @mousemove.prevent="ninjaPanMove"
             @mouseup="ninjaPanEnd"
             @mouseleave="ninjaPanEnd"
             @wheel.prevent="ninjaWheel"
             ref="ninjaSvgEl">

            <defs>
                <!-- Light Fine Grid Pattern -->
                <pattern id="light-grid" width="40" height="40" patternUnits="userSpaceOnUse">
                    <path d="M 40 0 L 0 0 0 40" fill="none" stroke="rgba(226, 232, 240, 0.8)" stroke-width="1" />
                    <circle cx="40" cy="40" r="1.2" fill="rgba(245, 158, 11, 0.2)" />
                </pattern>
                <!-- Glow Filter -->
                <filter id="glow-gold-light" x="-50%" y="-50%" width="200%" height="200%">
                    <feGaussianBlur stdDeviation="4" result="blur" />
                    <feMerge>
                        <feMergeNode in="blur" />
                        <feMergeNode in="SourceGraphic" />
                    </feMerge>
                </filter>
            </defs>

            <!-- Light Grid Background -->
            <rect width="100%" height="100%" fill="url(#light-grid)" />

            <!-- Transformed Interactive Group -->
            <g :transform="`translate(${ninjaPanX}, ${ninjaPanY}) scale(${ninjaScale})`">

                <template v-if="ninjaCompanies.length > 0">

                    <!-- Center → Company Rays (Warm Gold Dotted Lines) -->
                    <template v-for="(company, ci) in ninjaCompanies" :key="'ec-'+ci">
                        <line x1="600" y1="400"
                            :x2="ninjaNodeX(ci, ninjaCompanies.length)"
                            :y2="ninjaNodeY(ci, ninjaCompanies.length)"
                            stroke="#f59e0b" stroke-width="1.8" opacity="0.45"
                            stroke-dasharray="6,4" class="ninja-laser-flow" />
                    </template>

                    <!-- Company → Decision Maker Connectors (Soft Indigo Dotted Lines) -->
                    <template v-for="(company, ci) in ninjaCompanies" :key="'ep-'+ci">
                        <template v-for="(prof, pi) in company.profiles" :key="'ep-'+ci+'-'+pi">
                            <line
                                :x1="ninjaNodeX(ci, ninjaCompanies.length)"
                                :y1="ninjaNodeY(ci, ninjaCompanies.length)"
                                :x2="ninjaProfileX(ci, pi, ninjaCompanies.length, company.profiles.length)"
                                :y2="ninjaProfileY(ci, pi, ninjaCompanies.length, company.profiles.length)"
                                stroke="#6366f1" stroke-width="1.2" opacity="0.35"
                                stroke-dasharray="3,3" class="ninja-laser-slow" />
                        </template>
                    </template>

                    <!-- Company Hub Nodes (Clean White/Gold Pills) -->
                    <template v-for="(company, ci) in ninjaCompanies" :key="'nc-'+ci">
                        <!-- Pulsing Gold Ring -->
                        <circle :cx="ninjaNodeX(ci, ninjaCompanies.length)"
                                :cy="ninjaNodeY(ci, ninjaCompanies.length)"
                                r="22" fill="none"
                                stroke="#f59e0b" stroke-width="1.5" opacity="0.25"
                                class="ninja-pulse-ring-cyber"
                                :style="{ animationDelay: ci * 0.3 + 's' }" />
                        
                        <!-- Company Orb -->
                        <circle :cx="ninjaNodeX(ci, ninjaCompanies.length)"
                                :cy="ninjaNodeY(ci, ninjaCompanies.length)"
                                r="10" fill="#f59e0b" filter="url(#glow-gold-light)">
                            <animate attributeName="r" values="9;11;9" dur="2.5s" repeatCount="indefinite"
                                :begin="ci * 0.3 + 's'" />
                        </circle>
                        
                        <!-- Inner White Point -->
                        <circle :cx="ninjaNodeX(ci, ninjaCompanies.length)"
                                :cy="ninjaNodeY(ci, ninjaCompanies.length)"
                                r="4" fill="#ffffff" class="pointer-events-none" />

                        <!-- Company Badge Label (Crisp Light Theme Pill) -->
                        <foreignObject
                            :x="ninjaLabelX(ci, ninjaCompanies.length)"
                            :y="ninjaLabelY(ci, ninjaCompanies.length)"
                            width="150" height="34" class="pointer-events-none">
                            <div xmlns="http://www.w3.org/1999/xhtml"
                                 class="flex items-center justify-center gap-1.5 px-3 py-1.5 rounded-xl border border-slate-200 bg-white/95 shadow-md backdrop-blur-md">
                                <span class="w-2 h-2 rounded-full bg-amber-500 animate-pulse"></span>
                                <span class="text-[11px] font-black text-slate-800 truncate tracking-wide font-sans">
                                    {{ company.company_name }}
                                </span>
                            </div>
                        </foreignObject>

                        <!-- Decision Maker Nodes (Clear Light Indigo Nodes) -->
                        <template v-for="(prof, pi) in company.profiles" :key="'np-'+ci+'-'+pi">
                            <!-- Large Interactive Target -->
                            <circle
                                :cx="ninjaProfileX(ci, pi, ninjaCompanies.length, company.profiles.length)"
                                :cy="ninjaProfileY(ci, pi, ninjaCompanies.length, company.profiles.length)"
                                r="22" fill="transparent" class="cursor-pointer"
                                @mouseenter.stop="showNinjaTooltip($event, { ...prof, company_name: company.company_name, key: company.company_name+'_'+pi })"
                                @mouseleave.stop="scheduleHideTooltip()" />
                            
                            <!-- Visible Node Circle -->
                            <circle
                                :cx="ninjaProfileX(ci, pi, ninjaCompanies.length, company.profiles.length)"
                                :cy="ninjaProfileY(ci, pi, ninjaCompanies.length, company.profiles.length)"
                                :r="ninjaHoverNode && ninjaHoverNode.key === company.company_name+'_'+pi ? 10 : 6"
                                :fill="ninjaHoverNode && ninjaHoverNode.key === company.company_name+'_'+pi ? '#4f46e5' : '#6366f1'"
                                class="pointer-events-none transition-all duration-300" />
                            
                            <!-- Profile Name (Crisp Slate-800 text with zero collision) -->
                            <text
                                :x="ninjaProfileX(ci, pi, ninjaCompanies.length, company.profiles.length) + 12"
                                :y="ninjaProfileY(ci, pi, ninjaCompanies.length, company.profiles.length) + 4"
                                font-size="11" fill="#1e293b" font-weight="700"
                                font-family="sans-serif" class="pointer-events-none tracking-wide">
                                {{ (prof.name || '').split(' ')[0] }}
                            </text>
                        </template>
                    </template>

                    <!-- Central Core Radar (Ninja Center at 600, 400) -->
                    <g transform="translate(600, 400)">
                        <circle cx="0" cy="0" r="42" fill="none" stroke="rgba(245, 158, 11, 0.4)" stroke-width="1.5" stroke-dasharray="6 6" class="animate-spin-slow" />
                        <circle cx="0" cy="0" r="30" fill="#0f172a" stroke="#f59e0b" stroke-width="2" filter="url(#glow-gold-light)" />
                        <text x="0" y="7" text-anchor="middle" font-size="20" class="select-none">🥷</text>
                    </g>

                </template>
            </g>
        </svg>

        <!-- Glassmorphic Tooltip Card (Thème Clair Luxueux) -->
        <Transition name="fade-scale">
            <div v-if="ninjaHoverNode"
                 @mouseenter="cancelHideTooltip()"
                 @mouseleave="scheduleHideTooltip()"
                 class="fixed z-[200] w-80 rounded-3xl p-5 shadow-2xl border border-slate-200 backdrop-blur-xl bg-white/98 text-slate-900"
                 :style="{ left: ninjaTooltipX + 'px', top: ninjaTooltipY + 'px' }">

                <div class="flex items-center justify-between mb-3">
                    <span class="px-2.5 py-1 rounded-lg text-[10px] font-black uppercase tracking-wider bg-amber-50 text-amber-700 border border-amber-200">
                        {{ ninjaHoverNode.role || 'Décideur Clé' }}
                    </span>
                    <span class="text-xs font-bold text-slate-500 truncate max-w-[120px]">@ {{ ninjaHoverNode.company_name }}</span>
                </div>

                <h4 class="text-slate-900 text-lg font-black mb-1 flex items-center gap-2">
                    <span>{{ ninjaHoverNode.name }}</span>
                    <span class="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse"></span>
                </h4>

                <div class="relative p-3.5 rounded-2xl bg-slate-50 border border-slate-100 my-3">
                    <p class="text-xs text-slate-700 leading-relaxed italic pl-2 border-l-2 border-amber-500">
                        "{{ ninjaHoverNode.message }}"
                    </p>
                </div>

                <div class="flex items-center gap-2 mt-4">
                    <a v-if="ninjaHoverNode.linkedin_url" :href="ninjaHoverNode.linkedin_url" target="_blank"
                       class="flex-1 flex items-center justify-center gap-2 py-2.5 px-3 rounded-xl bg-sky-50 hover:bg-sky-100 text-sky-700 border border-sky-200 text-xs font-bold transition-all active:scale-95">
                        <svg class="w-4 h-4 fill-current" viewBox="0 0 24 24"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>
                        <span>Profil LinkedIn</span>
                    </a>

                    <button @click="copyNinjaMessage(ninjaHoverNode.message, ninjaHoverNode.key)"
                        class="flex-1 flex items-center justify-center gap-2 py-2.5 px-3 rounded-xl bg-amber-50 hover:bg-amber-100 text-amber-800 border border-amber-200 text-xs font-bold transition-all active:scale-95">
                        <svg v-if="ninjaCopied[ninjaHoverNode.key]" class="w-4 h-4 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
                        <svg v-else class="w-4 h-4 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"/></svg>
                        <span>{{ ninjaCopied[ninjaHoverNode.key] ? 'Copié !' : 'Copier Accroche' }}</span>
                    </button>
                </div>
            </div>
        </Transition>

        <!-- Empty Radar State -->
        <div v-if="!ninjaLoading && !ninjaRunning && ninjaCompanies.length === 0"
             class="absolute inset-0 flex flex-col items-center justify-center text-center z-20 p-6">
            <div class="relative w-20 h-20 rounded-3xl flex items-center justify-center mb-6 bg-slate-50 border border-slate-200 shadow-sm">
                <span class="text-4xl animate-bounce">🥷</span>
                <span class="absolute inset-0 rounded-3xl bg-amber-500/10 animate-ping"></span>
            </div>
            <h3 class="text-slate-900 text-2xl font-black mb-3">Aucune Cartographie Ninja Active</h3>
            <p class="text-slate-500 text-sm max-w-md mb-8 leading-relaxed">
                Détectez instantanément les responsables recrutement et décideurs clés sur vos entreprises cibles en un clic.
            </p>
            <button @click="runNinja" 
                    class="px-8 py-4 rounded-2xl text-white font-black text-base shadow-lg transition-all hover:scale-105 active:scale-95 border border-amber-400/50"
                    style="background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);">
                🚀 Lancer la Cartographie Réseau
            </button>
        </div>

        <!-- Scanning Overlay -->
        <div v-if="ninjaRunning" class="absolute inset-0 flex flex-col items-center justify-center text-center z-50 bg-white/95 backdrop-blur-md">
            <div class="relative w-32 h-32 mb-8 flex items-center justify-center">
                <div class="absolute inset-0 rounded-full border-4 border-amber-100"></div>
                <div class="absolute inset-0 rounded-full border-4 border-amber-500 border-t-transparent animate-spin"></div>
                <div class="text-4xl animate-pulse">🥷</div>
            </div>
            <p class="text-2xl font-black tracking-widest uppercase text-amber-600 animate-pulse">
                Scan Radar IA en cours...
            </p>
            <p class="text-slate-500 text-sm mt-3 font-medium">Cartographie des décideurs clés & génération des accroches d'approche...</p>
        </div>
    </div>


    <!-- Loading Modal for Drafting -->
    <div v-if="isDrafting" class="fixed inset-0 z-[100] flex items-center justify-center p-4">
        <div class="absolute inset-0 bg-slate-950/60 backdrop-blur-md animate-fade-in"></div>
        <div class="relative bg-white border border-slate-200/80 rounded-[2.5rem] p-10 shadow-2xl max-w-sm w-full text-center animate-fade-in-up text-slate-900">
            <div class="relative w-24 h-24 mx-auto mb-8">
                <div class="absolute inset-0 border-4 border-indigo-500/20 rounded-full"></div>
                <div class="absolute inset-0 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
                <div class="absolute inset-0 flex items-center justify-center">
                    <SparklesIcon class="w-10 h-10 text-indigo-500 animate-pulse" />
                </div>
            </div>
            <h3 class="text-2xl font-black text-slate-900 mb-3">{{ t('network_osint.loading_title') }}</h3>
            <p class="text-slate-500 font-medium leading-relaxed">{{ t('network_osint.loading_desc') }}</p>
            <div class="mt-8 flex items-center justify-center gap-1.5">
                <span class="w-1.5 h-1.5 rounded-full bg-indigo-500 animate-bounce" style="animation-delay: 0ms"></span>
                <span class="w-1.5 h-1.5 rounded-full bg-indigo-500 animate-bounce" style="animation-delay: 150ms"></span>
                <span class="w-1.5 h-1.5 rounded-full bg-indigo-500 animate-bounce" style="animation-delay: 300ms"></span>
            </div>
        </div>
    </div>
  </div>
</template>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #334155;
  border-radius: 4px;
}

/* ── Cyber Network Ninja Animations ── */
@keyframes laserFlow {
  from { stroke-dashoffset: 0; }
  to   { stroke-dashoffset: -28; }
}
.ninja-laser-flow {
  animation: laserFlow 2s linear infinite;
}
.ninja-laser-slow {
  animation: laserFlow 4s linear infinite;
}

@keyframes ringPulseCyber {
  0%   { transform: scale(0.9); opacity: 0.5; }
  50%  { transform: scale(1.3); opacity: 0.1; }
  100% { transform: scale(0.9); opacity: 0.5; }
}
.ninja-pulse-ring-cyber {
  animation: ringPulseCyber 3s ease-in-out infinite;
  transform-origin: center;
  transform-box: fill-box;
}

@keyframes spinSlow {
  from { transform: rotate(0deg); }
  to   { transform: rotate(360deg); }
}
.animate-spin-slow {
  animation: spinSlow 16s linear infinite;
  transform-origin: center;
  transform-box: fill-box;
}

@keyframes spinReverse {
  from { transform: rotate(360deg); }
  to   { transform: rotate(0deg); }
}
.animate-spin-reverse {
  animation: spinReverse 10s linear infinite;
}

.fade-scale-enter-active, .fade-scale-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}
.fade-scale-enter-from, .fade-scale-leave-to {
  opacity: 0;
  transform: scale(0.92);
}

.fade-scale-enter-from, .fade-scale-leave-to {
  opacity: 0;
  transform: scale(0.95) translateY(-4px);
}

</style>
