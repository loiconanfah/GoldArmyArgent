<script setup>
import { ref, onMounted, computed, watch, nextTick } from 'vue'
import { authFetch } from '../utils/auth'
import { toastState } from '../store/toastState'
import gsap from 'gsap'
import { 
    UsersIcon, 
    ChartBarIcon, 
    ShieldCheckIcon, 
    UserPlusIcon,
    ArrowPathIcon,
    MagnifyingGlassIcon,
    XMarkIcon,
    EyeIcon,
    DocumentTextIcon,
    BriefcaseIcon,
    EnvelopeIcon,
    ClockIcon,
    SparklesIcon,
    CheckBadgeIcon,
    QueueListIcon,
    CommandLineIcon,
    ServerIcon,
    BellAlertIcon,
    CpuChipIcon,
    CircleStackIcon,
    BoltIcon,
    ExclamationTriangleIcon,
    ArrowRightIcon,
    SignalIcon,
    WrenchScrewdriverIcon,
    ChevronRightIcon,
    CursorArrowRaysIcon,
    PresentationChartLineIcon
} from '@heroicons/vue/24/outline'

// --- Navigation State ---
const currentSection = ref('overview')
const sidebarItems = [
    { id: 'overview', name: 'Vue d\'ensemble', icon: ChartBarIcon },
    { id: 'agents', name: 'Utilisateurs', icon: UsersIcon },
    { id: 'analytics', name: 'Analytiques', icon: PresentationChartLineIcon },
    { id: 'terminal', name: 'Logs Système', icon: CommandLineIcon },
    { id: 'control', name: 'Configuration', icon: WrenchScrewdriverIcon },
]

// --- Global Data State ---
const isLoading = ref(true)
const isActionLoading = ref(false)
const users = ref([])
const stats = ref({
    total_users: 0,
    tiers: { pro: 0, essential: 0, free: 0 },
    total_applications: 0
})
const systemInfo = ref({
    os: '---',
    python_version: '---',
    cpu_usage: 0,
    memory_usage: 0,
    uptime_seconds: 0
})
const analyticsData = ref({
    total_views: 0,
    total_clicks: 0,
    top_pages: [],
    top_clicks: []
})
const errorLogs = ref([])
const searchQuery = ref('')

// --- Broadcast/Email State ---
const broadcast = ref({
    title: '',
    message: '',
    type: 'info',
    action_url: ''
})
const emailForm = ref({
    subject: '',
    content: '',
    isBroadcast: true,
    toEmail: ''
})

// --- Inspection Panel State ---
const isPanelOpen = ref(false)
const selectedUser = ref(null)
const userDetails = ref({ profile: {}, applications: [] })
const isDetailsLoading = ref(false)

// --- Fetch Data ---
const fetchAllData = async () => {
    isLoading.value = true
    await Promise.all([
        fetchStats(),
        fetchUsers(),
        fetchSystemInfo(),
        fetchErrors(),
        fetchAnalytics()
    ])
    isLoading.value = false
    animateEntrance()
}

const fetchStats = async () => {
    try {
        const res = await authFetch('/api/admin/stats')
        const json = await res.json()
        if (json.status === 'success') stats.value = json.data
    } catch (e) { console.error(e) }
}

const fetchUsers = async () => {
    try {
        const res = await authFetch('/api/admin/users')
        const json = await res.json()
        if (json.status === 'success') users.value = json.data
    } catch (e) { console.error(e) }
}

const fetchSystemInfo = async () => {
    try {
        const res = await authFetch('/api/admin/system-info')
        const json = await res.json()
        if (json.status === 'success') systemInfo.value = json.data
    } catch (e) { console.error(e) }
}

const fetchErrors = async () => {
    try {
        const res = await authFetch('/api/admin/errors?limit=20')
        const json = await res.json()
        if (json.status === 'success') errorLogs.value = json.data
    } catch (e) { console.error(e) }
}

const fetchAnalytics = async () => {
    try {
        const res = await authFetch('/api/admin/analytics')
        const json = await res.json()
        if (json.status === 'success') analyticsData.value = json.data
    } catch (e) { console.error(e) }
}

const fetchUserDetails = async (user) => {
    isDetailsLoading.value = true
    selectedUser.value = user
    isPanelOpen.value = true
    try {
        const userId = user.id || user._id
        const res = await authFetch(`/api/admin/user/${userId}`)
        const json = await res.json()
        if (json.status === 'success') userDetails.value = json.data
    } catch (e) {
        toastState.addToast("Erreur lors de l'inspection", "error")
    } finally {
        isDetailsLoading.value = false
    }
}

const updateTier = async (email, newTier) => {
    isActionLoading.value = true
    try {
        const res = await authFetch('/api/admin/promote-user', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, tier: newTier })
        })
        const json = await res.json()
        if (json.status === 'success') {
            toastState.addToast(`Statut mis à jour`, "success")
            await fetchUsers(); await fetchStats()
            if (selectedUser.value?.email === email) userDetails.value.profile.subscription_tier = newTier
        }
    } catch (e) { toastState.addToast("Échec de la mise à jour", "error") } finally { isActionLoading.value = false }
}

const sendBroadcast = async () => {
    if (!broadcast.value.title || !broadcast.value.message) return
    isActionLoading.value = true
    try {
        const res = await authFetch('/api/admin/broadcast', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(broadcast.value)
        })
        const json = await res.json()
        if (json.status === 'success') {
            toastState.addToast("Diffusion Push réussie", "success")
            broadcast.value = { title: '', message: '', type: 'info', action_url: '' }
        }
    } catch (e) { toastState.addToast("Échec de diffusion", "error") } finally { isActionLoading.value = false }
}

const sendEmail = async () => {
    if (!emailForm.value.subject || !emailForm.value.content) return
    isActionLoading.value = true
    try {
        const payload = {
            subject: emailForm.value.subject,
            content: emailForm.value.content,
            to_email: emailForm.value.isBroadcast ? null : emailForm.value.toEmail
        }
        const res = await authFetch('/api/admin/send-email', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        })
        const json = await res.json()
        if (json.status === 'success') {
            toastState.addToast(emailForm.value.isBroadcast ? "Email envoyé à toute la flotte" : "Email envoyé à l'agent", "success")
            emailForm.value.subject = ''
            emailForm.value.content = ''
        }
    } catch (e) { toastState.addToast("Échec de l'envoi email", "error") } finally { isActionLoading.value = false }
}

const openDirectEmail = (email) => {
    emailForm.value.isBroadcast = false
    emailForm.value.toEmail = email
    currentSection.value = 'control'
    isPanelOpen.value = false
}

const resolveError = async (id) => {
    try {
        const res = await authFetch(`/api/admin/errors/${id}/resolve`, { method: 'PATCH' })
        const json = await res.json()
        if (json.status === 'success') { toastState.addToast("Résolu", "success"); await fetchErrors() }
    } catch (e) { console.error(e) }
}

// --- Computed ---
const filteredUsers = computed(() => {
    if (!searchQuery.value) return users.value
    const q = searchQuery.value.toLowerCase()
    return users.value.filter(u => u.email?.toLowerCase().includes(q) || u.full_name?.toLowerCase().includes(q))
})

const uptimeFormatted = computed(() => {
    const sec = systemInfo.value.uptime_seconds
    const d = Math.floor(sec / 86400), h = Math.floor((sec % 86400) / 3600), m = Math.floor((sec % 3600) / 60)
    return `${d}d ${h}h ${m}m`
})

// --- Animations ---
const animateEntrance = () => {
    nextTick(() => {
        gsap.from('.fade-up', { y: 20, opacity: 0, duration: 0.6, stagger: 0.05, ease: 'power2.out' })
    })
}

watch(currentSection, () => {
    nextTick(() => {
        gsap.from('.section-anim', { x: 10, opacity: 0, duration: 0.4, ease: 'power2.out' })
    })
})

onMounted(fetchAllData)
</script>

<template>
  <div class="flex min-h-screen bg-[#F8FAFC] text-slate-700 font-sans selection:bg-indigo-100">
    
    <!-- --- SIDEBAR (Minimalist Light) --- -->
    <aside class="w-20 lg:w-64 bg-white border-r border-slate-200 flex flex-col shrink-0 z-50">
        <div class="p-6 lg:p-8 flex items-center gap-3">
            <div class="w-8 h-8 bg-indigo-600 rounded-lg flex items-center justify-center shadow-md">
                <ShieldCheckIcon class="w-5 h-5 text-white" />
            </div>
            <h1 class="hidden lg:block text-lg font-bold tracking-tight text-slate-900 uppercase">Admin<span class="text-indigo-600">Box</span></h1>
        </div>

        <nav class="flex-1 px-3 py-4 space-y-1">
            <button 
                v-for="item in sidebarItems" :key="item.id"
                @click="currentSection = item.id"
                :class="[
                    'w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 group',
                    currentSection === item.id ? 'bg-indigo-50 text-indigo-600 shadow-sm shadow-indigo-100' : 'text-slate-500 hover:bg-slate-50 hover:text-slate-900'
                ]"
            >
                <component :is="item.icon" class="w-5 h-5 shrink-0" />
                <span class="hidden lg:block font-semibold text-sm">{{ item.name }}</span>
            </button>
        </nav>

        <div class="p-6 border-t border-slate-100 hidden lg:block">
            <div class="bg-slate-50 rounded-xl p-4 border border-slate-200">
                <div class="flex items-center gap-2 mb-1">
                    <div class="w-2 h-2 rounded-full bg-emerald-500"></div>
                    <span class="text-[10px] font-bold text-slate-900 uppercase">Live Ops</span>
                </div>
                <div class="text-[10px] text-slate-500 font-medium">Node: Region-West-1</div>
            </div>
        </div>
    </aside>

    <!-- --- MAIN AREA --- -->
    <main class="flex-1 flex flex-col min-w-0">
        
        <!-- Header -->
        <header class="h-16 bg-white border-b border-slate-200 flex items-center justify-between px-8 z-40">
            <div class="flex items-center gap-2">
                <span class="text-xs font-bold text-slate-400 uppercase tracking-widest">{{ sidebarItems.find(i => i.id === currentSection).name }}</span>
            </div>

            <div class="flex items-center gap-6">
                <div class="hidden lg:flex items-center gap-6 text-[10px] font-bold text-slate-400 uppercase tracking-widest">
                    <div class="flex items-center gap-1.5"><CpuChipIcon class="w-3.5 h-3.5" /> {{ systemInfo.cpu_usage }}%</div>
                    <div class="flex items-center gap-1.5"><CircleStackIcon class="w-3.5 h-3.5" /> {{ systemInfo.memory_usage }}%</div>
                    <div class="flex items-center gap-1.5"><BoltIcon class="w-3.5 h-3.5 text-amber-500" /> {{ uptimeFormatted }}</div>
                </div>
                <button @click="fetchAllData" :disabled="isLoading" class="p-2 hover:bg-slate-100 rounded-lg transition-colors text-slate-500">
                    <ArrowPathIcon class="w-5 h-5" :class="isLoading ? 'animate-spin' : ''" />
                </button>
            </div>
        </header>

        <!-- Content -->
        <div class="flex-1 overflow-y-auto p-6 lg:p-10 custom-scrollbar">
            
            <!-- OVERVIEW -->
            <div v-if="currentSection === 'overview'" class="section-anim space-y-10">
                <!-- Stats Row -->
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                    <div v-for="(stat, idx) in [
                        { label: 'Utilisateurs', val: stats.total_users, sub: 'Inscrits', color: 'indigo', icon: UsersIcon },
                        { label: 'Abonnés Pro', val: stats.tiers.pro, sub: 'Tier Premium', color: 'indigo', icon: SparklesIcon },
                        { label: 'Vues Pages', val: analyticsData.total_views, sub: 'Analytiques', color: 'emerald', icon: EyeIcon },
                        { label: 'Interactions', val: analyticsData.total_clicks, sub: 'Clics', color: 'rose', icon: CursorArrowRaysIcon }
                    ]" :key="idx" class="fade-up bg-white p-6 rounded-2xl border border-slate-200 shadow-sm hover:shadow-md transition-shadow">
                        <div class="flex items-center justify-between mb-4">
                            <div :class="`p-2 bg-${stat.color}-50 rounded-lg`"><component :is="stat.icon" :class="`w-5 h-5 text-${stat.color}-600`" /></div>
                            <span class="text-[10px] font-bold text-slate-400 uppercase tracking-wider">{{ stat.sub }}</span>
                        </div>
                        <div class="text-xs font-bold text-slate-500 uppercase tracking-tight mb-1">{{ stat.label }}</div>
                        <div class="text-3xl font-bold text-slate-900">{{ stat.val.toLocaleString() }}</div>
                    </div>
                </div>

                <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
                    <!-- Health -->
                    <div class="lg:col-span-1 bg-white border border-slate-200 rounded-2xl p-8 shadow-sm">
                        <h3 class="text-sm font-bold text-slate-900 uppercase tracking-tight mb-6">Performance Système</h3>
                        <div class="space-y-6">
                            <div v-for="item in [{l:'CPU', v:systemInfo.cpu_usage, c:'indigo'}, {l:'RAM', v:systemInfo.memory_usage, c:'indigo'}]" :key="item.l">
                                <div class="flex justify-between text-[10px] font-bold uppercase mb-2">
                                    <span class="text-slate-500">{{ item.l }}</span>
                                    <span class="text-slate-900">{{ item.v }}%</span>
                                </div>
                                <div class="h-1.5 bg-slate-100 rounded-full overflow-hidden">
                                    <div class="h-full bg-indigo-600 transition-all duration-1000" :style="{ width: `${item.v}%` }"></div>
                                </div>
                            </div>
                            <div class="pt-4 space-y-3">
                                <div v-for="(v, l) in { 'OS': systemInfo.os, 'Python': systemInfo.python_version, 'Uptime': uptimeFormatted }" :key="l" class="flex justify-between text-[10px] border-b border-slate-50 pb-2">
                                    <span class="font-bold text-slate-400 uppercase">{{ l }}</span>
                                    <span class="text-slate-700">{{ v }}</span>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Top Activity Preview -->
                    <div class="lg:col-span-2 bg-white border border-slate-200 rounded-2xl p-8 shadow-sm flex flex-col">
                        <div class="flex items-center justify-between mb-6">
                            <h3 class="text-sm font-bold text-slate-900 uppercase tracking-tight">Vues Populaires</h3>
                            <button @click="currentSection = 'analytics'" class="text-[10px] font-bold text-indigo-600 hover:underline">Voir Analytics</button>
                        </div>
                        <div class="space-y-4 flex-1">
                            <div v-for="page in analyticsData.top_pages.slice(0, 5)" :key="page._id" class="flex items-center gap-4 p-3 hover:bg-slate-50 rounded-xl transition-colors">
                                <div class="p-2 bg-indigo-50 rounded-lg"><EyeIcon class="w-4 h-4 text-indigo-600" /></div>
                                <div class="min-w-0 flex-1">
                                    <div class="text-xs font-bold text-slate-900 truncate">{{ page._id || 'Landing Page' }}</div>
                                    <div class="text-[10px] text-slate-400 uppercase font-bold">{{ page.count }} Vues</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- ANALYTICS -->
            <div v-if="currentSection === 'analytics'" class="section-anim space-y-10">
                <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
                    <!-- Top Pages Table -->
                    <div class="bg-white border border-slate-200 rounded-2xl shadow-sm overflow-hidden">
                        <div class="p-6 border-b border-slate-100 flex items-center gap-3">
                            <PresentationChartLineIcon class="w-5 h-5 text-indigo-600" />
                            <h3 class="text-sm font-bold text-slate-900 uppercase tracking-tight">Pages les plus vues</h3>
                        </div>
                        <div class="divide-y divide-slate-50">
                            <div v-for="(page, i) in analyticsData.top_pages" :key="i" class="px-6 py-4 flex items-center justify-between group hover:bg-slate-50 transition-colors">
                                <div class="flex items-center gap-4 min-w-0">
                                    <span class="text-xs font-bold text-slate-300 w-4">{{ i+1 }}</span>
                                    <span class="text-xs font-semibold text-slate-700 truncate max-w-xs">{{ page._id || '/' }}</span>
                                </div>
                                <div class="px-3 py-1 bg-indigo-50 text-indigo-600 text-[10px] font-bold rounded-full">{{ page.count }}</div>
                            </div>
                        </div>
                    </div>

                    <!-- Top Clicks Table -->
                    <div class="bg-white border border-slate-200 rounded-2xl shadow-sm overflow-hidden">
                        <div class="p-6 border-b border-slate-100 flex items-center gap-3">
                            <CursorArrowRaysIcon class="w-5 h-5 text-rose-600" />
                            <h3 class="text-sm font-bold text-slate-900 uppercase tracking-tight">Boutons les plus cliqués</h3>
                        </div>
                        <div class="divide-y divide-slate-50">
                            <div v-for="(click, i) in analyticsData.top_clicks" :key="i" class="px-6 py-4 flex items-center justify-between group hover:bg-slate-50 transition-colors">
                                <div class="flex items-center gap-4 min-w-0">
                                    <span class="text-xs font-bold text-slate-300 w-4">{{ i+1 }}</span>
                                    <span class="text-xs font-semibold text-slate-700 truncate max-w-xs">{{ click._id || 'Bouton Inconnu' }}</span>
                                </div>
                                <div class="px-3 py-1 bg-rose-50 text-rose-600 text-[10px] font-bold rounded-full">{{ click.count }}</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- AGENTS -->
            <div v-if="currentSection === 'agents'" class="section-anim">
                <div class="bg-white border border-slate-200 rounded-2xl shadow-sm overflow-hidden">
                    <div class="p-8 border-b border-slate-100 flex flex-col sm:flex-row sm:items-center justify-between gap-6">
                        <div>
                            <h2 class="text-lg font-bold text-slate-900 uppercase tracking-tight">Base Utilisateurs</h2>
                            <p class="text-xs text-slate-500 font-medium">Gérer les accès et surveiller l'activité.</p>
                        </div>
                        <div class="relative max-w-sm w-full">
                            <MagnifyingGlassIcon class="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                            <input v-model="searchQuery" type="text" placeholder="Rechercher..." class="w-full bg-slate-50 border border-slate-200 rounded-xl pl-11 pr-4 py-2.5 text-sm outline-none focus:border-indigo-500 transition-all font-medium" />
                        </div>
                    </div>

                    <div class="overflow-x-auto">
                        <table class="w-full text-left">
                            <thead>
                                <tr class="bg-slate-50/50 text-[10px] font-bold text-slate-400 uppercase tracking-widest border-b border-slate-100">
                                    <th class="px-8 py-4">Utilisateur</th>
                                    <th class="px-8 py-4">Statut</th>
                                    <th class="px-8 py-4 text-right">Actions</th>
                                </tr>
                            </thead>
                            <tbody class="divide-y divide-slate-100">
                                <tr v-for="user in filteredUsers" :key="user.email" @click="fetchUserDetails(user)" class="hover:bg-slate-50 transition-colors cursor-pointer group">
                                    <td class="px-8 py-5">
                                        <div class="flex items-center gap-3">
                                            <div class="w-10 h-10 rounded-full bg-slate-100 flex items-center justify-center text-xs font-bold text-slate-600 border border-slate-200 group-hover:bg-white group-hover:shadow-sm transition-all">
                                                {{ (user.full_name || user.email).charAt(0).toUpperCase() }}
                                            </div>
                                            <div>
                                                <div class="text-sm font-bold text-slate-900 group-hover:text-indigo-600 transition-colors">{{ user.full_name || 'Utilisateur' }}</div>
                                                <div class="text-[10px] text-slate-400 font-medium">{{ user.email }}</div>
                                            </div>
                                        </div>
                                    </td>
                                    <td class="px-8 py-5">
                                        <span v-if="user.subscription_tier === 'ADMIN'" class="px-2 py-0.5 bg-indigo-100 text-indigo-700 text-[9px] font-bold rounded-md border border-indigo-200 uppercase">Admin</span>
                                        <span v-else-if="user.subscription_tier === 'PRO'" class="px-2 py-0.5 bg-emerald-50 text-emerald-700 text-[9px] font-bold rounded-md border border-emerald-100 uppercase">Pro</span>
                                        <span v-else class="px-2 py-0.5 bg-slate-100 text-slate-600 text-[9px] font-bold rounded-md border border-slate-200 uppercase">Libre</span>
                                    </td>
                                    <td class="px-8 py-5 text-right" @click.stop>
                                        <div class="flex items-center justify-end gap-2">
                                            <button @click="fetchUserDetails(user)" class="p-2 hover:bg-white hover:shadow-sm rounded-lg border border-transparent hover:border-slate-200 transition-all">
                                                <EyeIcon class="w-4 h-4 text-slate-400" />
                                            </button>
                                            <select 
                                                @change="(e) => updateTier(user.email, e.target.value)" 
                                                :value="user.subscription_tier || 'FREE'"
                                                class="bg-white border border-slate-200 text-[10px] font-bold rounded-lg px-2 py-1.5 outline-none hover:border-indigo-500 transition-colors cursor-pointer"
                                            >
                                                <option value="FREE">Libre</option>
                                                <option value="ESSENTIAL">Essentiel</option>
                                                <option value="PRO">Pro</option>
                                                <option value="ADMIN">Admin</option>
                                            </select>
                                        </div>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            <!-- TERMINAL -->
            <div v-if="currentSection === 'terminal'" class="section-anim">
                <div class="bg-white border border-slate-200 rounded-2xl shadow-sm overflow-hidden">
                    <div class="p-8 border-b border-slate-100 flex items-center justify-between">
                        <h2 class="text-lg font-bold text-slate-900 uppercase tracking-tight">Logs d'Exceptions</h2>
                        <button @click="fetchErrors" class="p-2 hover:bg-slate-50 rounded-lg text-slate-400"><ArrowPathIcon class="w-5 h-5" /></button>
                    </div>
                    <div class="divide-y divide-slate-100">
                        <div v-for="err in errorLogs" :key="err._id" class="p-6 hover:bg-slate-50/50 transition-colors relative group">
                            <div v-if="err.resolved" class="absolute inset-0 bg-white/60 z-10 flex items-center justify-center backdrop-blur-[1px]">
                                <span class="bg-emerald-500 text-white text-[10px] font-bold px-3 py-1 rounded-full uppercase tracking-widest shadow-sm">Résolu</span>
                            </div>
                            <div class="flex items-start justify-between mb-4">
                                <div class="flex items-center gap-3">
                                    <div class="p-2 bg-rose-50 rounded-lg"><ExclamationTriangleIcon class="w-5 h-5 text-rose-600" /></div>
                                    <div>
                                        <h4 class="text-sm font-bold text-slate-900 uppercase tracking-tight">{{ err.error_type }}</h4>
                                        <p class="text-[10px] text-slate-400 font-bold uppercase">{{ new Date(err.timestamp).toLocaleString() }}</p>
                                    </div>
                                </div>
                                <button v-if="!err.resolved" @click="resolveError(err._id)" class="px-4 py-1.5 bg-slate-900 text-white hover:bg-indigo-600 rounded-lg text-[10px] font-bold uppercase tracking-widest transition-colors">Résoudre</button>
                            </div>
                            <div class="bg-slate-50 p-4 rounded-xl border border-slate-200 font-mono text-[11px] text-slate-600 overflow-x-auto whitespace-pre">
                                {{ err.message }}
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- CONTROL -->
            <div v-if="currentSection === 'control'" class="section-anim max-w-4xl mx-auto space-y-12">
                
                <!-- Email Management Tool -->
                <div class="bg-white border border-slate-200 rounded-2xl p-10 shadow-sm space-y-8">
                    <div class="flex items-center gap-3">
                        <div class="p-2 bg-indigo-600 rounded-xl shadow-lg"><EnvelopeIcon class="w-6 h-6 text-white" /></div>
                        <div>
                            <h2 class="text-xl font-bold text-slate-900 uppercase tracking-tight">Gestion des Emails</h2>
                            <p class="text-xs text-slate-500 font-medium">Envoyez des communications ciblées ou globales.</p>
                        </div>
                    </div>

                    <div class="space-y-5">
                        <div class="flex items-center gap-4 bg-slate-50 p-3 rounded-xl border border-slate-200">
                            <button @click="emailForm.isBroadcast = true" :class="[
                                'flex-1 py-2 text-[10px] font-bold uppercase rounded-lg transition-all',
                                emailForm.isBroadcast ? 'bg-white shadow-sm text-indigo-600' : 'text-slate-400 hover:text-slate-600'
                            ]">Envoi Global (Broadcast)</button>
                            <button @click="emailForm.isBroadcast = false" :class="[
                                'flex-1 py-2 text-[10px] font-bold uppercase rounded-lg transition-all',
                                !emailForm.isBroadcast ? 'bg-white shadow-sm text-indigo-600' : 'text-slate-400 hover:text-slate-600'
                            ]">Agent Spécifique</button>
                        </div>

                        <div class="space-y-4">
                            <div v-if="!emailForm.isBroadcast" class="space-y-2">
                                <label class="text-[10px] font-bold text-slate-400 uppercase tracking-widest ml-1">Email Destinataire</label>
                                <input v-model="emailForm.toEmail" type="email" placeholder="agent@goldarmy.com" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-sm focus:border-indigo-500 outline-none transition-all" />
                            </div>
                            <div class="space-y-2">
                                <label class="text-[10px] font-bold text-slate-400 uppercase tracking-widest ml-1">Objet de l'Email</label>
                                <input v-model="emailForm.subject" type="text" placeholder="Ex: Mise à jour de vos services..." class="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-sm focus:border-indigo-500 outline-none transition-all" />
                            </div>
                            <div class="space-y-2">
                                <label class="text-[10px] font-bold text-slate-400 uppercase tracking-widest ml-1">Contenu (HTML accepté)</label>
                                <textarea v-model="emailForm.content" rows="6" placeholder="Rédigez votre message ici..." class="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-sm focus:border-indigo-500 outline-none transition-all resize-none"></textarea>
                            </div>
                            <button @click="sendEmail" :disabled="isActionLoading" class="w-full py-4 bg-slate-900 text-white font-bold uppercase tracking-widest rounded-xl hover:bg-indigo-600 transition-all flex items-center justify-center gap-3 shadow-lg active:scale-95 disabled:opacity-50">
                                <EnvelopeIcon v-if="!isActionLoading" class="w-5 h-5" />
                                <ArrowPathIcon v-else class="w-5 h-5 animate-spin" />
                                {{ emailForm.isBroadcast ? 'Diffuser l\'email à tous' : 'Envoyer l\'email à l\'agent' }}
                            </button>
                        </div>
                    </div>
                </div>

                <!-- Push Broadcast Tool -->
                <div class="bg-white border border-slate-200 rounded-2xl p-10 shadow-sm space-y-8 opacity-60 hover:opacity-100 transition-opacity">
                    <div class="flex items-center gap-3">
                        <div class="p-2 bg-slate-900 rounded-xl shadow-lg"><BellAlertIcon class="w-6 h-6 text-white" /></div>
                        <div>
                            <h2 class="text-xl font-bold text-slate-900 uppercase tracking-tight">Push Notification</h2>
                            <p class="text-xs text-slate-500 font-medium">Alerte instantanée sur le terminal agent.</p>
                        </div>
                    </div>
                    <!-- Reuse broadcast form from before -->
                    <div class="space-y-5">
                        <div class="grid grid-cols-2 gap-5">
                            <div class="space-y-2">
                                <label class="text-[10px] font-bold text-slate-400 uppercase tracking-widest ml-1">Titre Push</label>
                                <input v-model="broadcast.title" type="text" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-sm focus:border-indigo-500 outline-none transition-all" />
                            </div>
                            <div class="space-y-2">
                                <label class="text-[10px] font-bold text-slate-400 uppercase tracking-widest ml-1">Urgence</label>
                                <select v-model="broadcast.type" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-sm focus:border-indigo-500 outline-none transition-all">
                                    <option value="info">Information</option>
                                    <option value="success">Succès</option>
                                    <option value="warning">Attention</option>
                                    <option value="error">Alerte</option>
                                </select>
                            </div>
                        </div>
                        <div class="space-y-2">
                            <label class="text-[10px] font-bold text-slate-400 uppercase tracking-widest ml-1">Message</label>
                            <textarea v-model="broadcast.message" rows="2" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-sm focus:border-indigo-500 outline-none transition-all resize-none"></textarea>
                        </div>
                        <button @click="sendBroadcast" :disabled="isActionLoading" class="w-full py-4 bg-slate-100 text-slate-900 font-bold uppercase tracking-widest rounded-xl hover:bg-indigo-600 hover:text-white transition-all flex items-center justify-center gap-3 active:scale-95 disabled:opacity-50">
                            <BoltIcon v-if="!isActionLoading" class="w-5 h-5" />
                            <ArrowPathIcon v-else class="w-5 h-5 animate-spin" />
                            Diffuser Push
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </main>

    <!-- SIDE PANEL -->
    <Transition name="slide-right">
        <aside v-if="isPanelOpen" class="fixed top-0 right-0 h-full w-full lg:w-[600px] bg-white border-l border-slate-200 z-[100] shadow-2xl flex flex-col">
            <div class="p-8 border-b border-slate-100 flex items-center justify-between shrink-0 bg-slate-50/50">
                <div class="flex items-center gap-4">
                    <div class="w-10 h-10 rounded-xl bg-indigo-600 flex items-center justify-center text-white shadow-lg"><ShieldCheckIcon class="w-6 h-6" /></div>
                    <div>
                        <h3 class="text-base font-bold text-slate-900 uppercase tracking-tight">Détails de l'Agent</h3>
                        <p class="text-[10px] text-slate-400 font-bold uppercase tracking-widest">Contrôle Niveau 3</p>
                    </div>
                </div>
                <button @click="isPanelOpen = false" class="p-2 hover:bg-slate-200 rounded-xl transition-all text-slate-400"><XMarkIcon class="w-6 h-6" /></button>
            </div>

            <div class="flex-1 overflow-y-auto p-8 space-y-10 custom-scrollbar">
                <div v-if="isDetailsLoading" class="flex flex-col items-center justify-center py-40 gap-4">
                    <div class="w-10 h-10 border-2 border-indigo-600 border-t-transparent rounded-full animate-spin"></div>
                    <span class="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Chargement...</span>
                </div>
                <div v-else class="space-y-10">
                    <!-- User Info Card -->
                    <div class="bg-slate-50 border border-slate-200 rounded-2xl p-6 flex items-center gap-6">
                        <div class="w-20 h-20 bg-white border border-slate-200 rounded-2xl flex items-center justify-center text-3xl font-bold text-slate-300 shadow-sm">
                            {{ (userDetails.profile.full_name || userDetails.profile.email).charAt(0).toUpperCase() }}
                        </div>
                        <div class="min-w-0 flex-1">
                            <h4 class="text-xl font-bold text-slate-900 truncate">{{ userDetails.profile.full_name || 'Anonyme' }}</h4>
                            <div class="text-xs text-slate-500 font-medium mb-4">{{ userDetails.profile.email }}</div>
                            <div class="flex flex-wrap gap-3">
                                <button @click="openDirectEmail(userDetails.profile.email)" class="px-3 py-1.5 bg-white border border-slate-200 rounded-lg text-[9px] font-bold uppercase text-indigo-600 hover:border-indigo-600 transition-colors flex items-center gap-2">
                                    <EnvelopeIcon class="w-3.5 h-3.5" /> Mail Direct
                                </button>
                                <div class="px-3 py-1.5 bg-white border border-slate-200 rounded-lg text-[9px] font-bold uppercase text-slate-400">
                                    Missions: <span class="text-slate-900">{{ userDetails.applications.length }}</span>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- CV Content -->
                    <div class="space-y-4">
                        <h5 class="text-[10px] font-bold text-slate-400 uppercase tracking-widest border-b border-slate-100 pb-2">Contenu du CV</h5>
                        <div class="bg-slate-50 rounded-2xl p-6 border border-slate-200 max-h-60 overflow-y-auto font-mono text-[11px] text-slate-600 leading-relaxed custom-scrollbar">
                            <pre v-if="userDetails.profile.cv_text" class="whitespace-pre-wrap">{{ userDetails.profile.cv_text }}</pre>
                            <p v-else class="text-center italic py-4">Aucune donnée.</p>
                        </div>
                    </div>

                    <!-- App History -->
                    <div class="space-y-4">
                        <h5 class="text-[10px] font-bold text-slate-400 uppercase tracking-widest border-b border-slate-100 pb-2">Historique des Missions</h5>
                        <div v-if="userDetails.applications.length" class="space-y-2">
                            <div v-for="app in userDetails.applications" :key="app._id" class="p-4 bg-white border border-slate-100 rounded-xl flex items-center justify-between shadow-sm">
                                <div class="min-w-0 flex-1 mr-4">
                                    <div class="text-xs font-bold text-slate-900 truncate">{{ app.job_title }}</div>
                                    <div class="text-[10px] text-slate-400 font-bold uppercase">{{ app.company_name }}</div>
                                </div>
                                <span class="px-2 py-0.5 bg-slate-50 text-[9px] font-bold rounded border border-slate-100 text-slate-500 uppercase">{{ app.status }}</span>
                            </div>
                        </div>
                    </div>

                    <!-- Decision Center -->
                    <div class="pt-8 border-t border-slate-100 flex flex-col gap-4">
                        <div class="grid grid-cols-2 gap-4">
                            <button @click="updateTier(userDetails.profile.email, 'PRO')" class="flex items-center justify-center gap-2 py-4 bg-indigo-600 text-white font-bold rounded-xl shadow-lg shadow-indigo-100 hover:bg-indigo-700 transition-all active:scale-95 text-xs uppercase tracking-widest">
                                <SparklesIcon class="w-4 h-4" /> Upgrade Pro
                            </button>
                            <button @click="updateTier(userDetails.profile.email, 'FREE')" class="flex items-center justify-center gap-2 py-4 bg-white border border-slate-200 text-slate-500 font-bold rounded-xl hover:bg-slate-50 transition-all active:scale-95 text-xs uppercase tracking-widest">
                                <XMarkIcon class="w-4 h-4" /> Révoquer
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </aside>
    </Transition>

    <div v-if="isPanelOpen" @click="isPanelOpen = false" class="fixed inset-0 bg-slate-900/40 backdrop-blur-[2px] z-[90]"></div>

  </div>
</template>

<style scoped>
.custom-scrollbar::-webkit-scrollbar { width: 5px; }
.custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: #E2E8F0; border-radius: 10px; }
.custom-scrollbar::-webkit-scrollbar-thumb:hover { background: #CBD5E1; }

.slide-right-enter-active, .slide-right-leave-active { transition: transform 0.4s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.3s ease; }
.slide-right-enter-from, .slide-right-leave-to { transform: translateX(100%); opacity: 0; }

pre { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace; }
</style>
