<script setup>
import { ref, onMounted, computed } from 'vue'
import { authFetch } from '../utils/auth'
import { toastState } from '../store/toastState'
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
    QueueListIcon
} from '@heroicons/vue/24/outline'

// --- State ---
const isLoading = ref(true)
const isActionLoading = ref(false)
const users = ref([])
const stats = ref({
    total_users: 0,
    tiers: { pro: 0, essential: 0, free: 0 },
    total_applications: 0
})
const searchQuery = ref('')

// --- Inspection Panel State ---
const isPanelOpen = ref(false)
const selectedUser = ref(null)
const userDetails = ref({ profile: {}, applications: [] })
const isDetailsLoading = ref(false)

// --- Fetch Data ---
const fetchStats = async () => {
    try {
        const res = await authFetch('/api/admin/stats')
        const json = await res.json()
        if (json.status === 'success') {
            stats.value = json.data
        } else {
            console.error("Stats Error:", json.detail)
        }
    } catch (e) {
        console.error("Stats connection error", e)
    }
}

const fetchUsers = async () => {
    isLoading.value = true
    try {
        const res = await authFetch('/api/admin/users')
        const json = await res.json()
        if (json.status === 'success') {
            users.value = json.data
        } else {
            toastState.addToast(json.detail || "Échec du scan de la flotte", "error")
        }
    } catch (e) {
        toastState.addToast("Erreur critique de connexion RADAR", "error")
    } finally {
        isLoading.value = false
    }
}

const fetchUserDetails = async (user) => {
    isDetailsLoading.value = true
    selectedUser.value = user
    isPanelOpen.value = true
    try {
        const userId = user.id || user._id
        const res = await authFetch(`/api/admin/user/${userId}`)
        const json = await res.json()
        if (json.status === 'success') {
            userDetails.value = json.data
        }
    } catch (e) {
        toastState.addToast("Impossible de scanner cet agent", "error")
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
            toastState.addToast(`Rang mis à jour : ${newTier}`, "success")
            await fetchUsers()
            await fetchStats()
            // If the user being updated is the one in the panel, refresh details
            if (selectedUser.value && selectedUser.value.email === email) {
                userDetails.value.profile.subscription_tier = newTier
            }
        } else {
            toastState.addToast(json.detail || "Échec de l'upgrade", "error")
        }
    } catch (e) {
        toastState.addToast("Erreur de connexion tactique", "error")
    } finally {
        isActionLoading.value = false
    }
}

// --- Computed ---
const filteredUsers = computed(() => {
    if (!searchQuery.value) return users.value
    const q = searchQuery.value.toLowerCase()
    return users.value.filter(u => 
        (u.email && u.email.toLowerCase().includes(q)) || 
        (u.full_name && u.full_name.toLowerCase().includes(q))
    )
})

const getStatusColor = (status) => {
    const s = status?.toLowerCase() || ''
    if (s.includes('sent') || s.includes('envoyé')) return 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20'
    if (s.includes('refused') || s.includes('refus')) return 'text-rose-400 bg-rose-500/10 border-rose-500/20'
    if (s.includes('wait') || s.includes('attente')) return 'text-amber-400 bg-amber-500/10 border-amber-500/20'
    return 'text-slate-400 bg-slate-500/10 border-slate-500/20'
}

onMounted(() => {
    fetchStats()
    fetchUsers()
})
</script>

<template>
  <div class="relative min-h-screen bg-black text-white selection:bg-red-500/30">
    
    <!-- Hero Background Effects -->
    <div class="fixed inset-0 overflow-hidden pointer-events-none">
        <div class="absolute -top-[10%] -left-[5%] w-[40%] h-[40%] bg-indigo-600/10 blur-[120px] rounded-full animate-pulse"></div>
        <div class="absolute top-[20%] -right-[5%] w-[35%] h-[35%] bg-rose-600/5 blur-[100px] rounded-full"></div>
    </div>

    <div class="relative z-10 px-6 md:px-12 py-10 max-w-[1700px] mx-auto w-full animate-fade-in">
        
        <!-- --- HEADER --- -->
        <header class="flex flex-col lg:flex-row lg:items-end justify-between gap-8 mb-16">
            <div class="space-y-4">
                <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-red-500/10 border border-red-500/20 text-red-500 text-[10px] font-black uppercase tracking-[0.2em] italic shadow-lg shadow-red-500/10">
                    <ShieldCheckIcon class="w-3.5 h-3.5" />
                    Terminal Haute Sécurité
                </div>
                <h1 class="text-5xl md:text-6xl font-display font-black tracking-tighter italic uppercase">
                    Admin <span class="text-transparent bg-clip-text bg-gradient-to-r from-red-500 to-rose-600">Intelligence</span>
                </h1>
                <p class="text-slate-400 max-w-xl font-medium text-base leading-relaxed">
                    Surveillance globale de la flotte GoldArmy. Inspectez les profils, validez les CV et gérez les déploiements Premium en temps réel.
                </p>
            </div>
            
            <div class="flex items-center gap-4">
                 <div class="hidden md:flex flex-col items-right text-right pr-4 border-r border-surface-800">
                    <span class="text-[10px] font-black text-slate-500 uppercase tracking-widest">État du Système</span>
                    <span class="text-xs font-bold text-emerald-500 flex items-center gap-1 justify-end">
                        <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                        OPÉRATIONNEL
                    </span>
                 </div>
                 <button @click="fetchUsers" class="group flex items-center gap-3 px-8 py-4 bg-white text-black font-black rounded-2xl hover:bg-red-500 hover:text-white transition-all active:scale-95 shadow-2xl shadow-white/5">
                    <ArrowPathIcon class="w-5 h-5" :class="isLoading ? 'animate-spin' : ''" />
                    SYNCHRONISER
                </button>
            </div>
        </header>

        <!-- --- STATS CARDS --- -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 mb-16">
            <!-- Total Users -->
            <div class="bg-surface-900/40 backdrop-blur-xl border border-surface-800 p-8 rounded-[2.5rem] hover:border-red-500/40 transition-all group relative overflow-hidden">
                <div class="absolute right-0 top-0 w-32 h-32 bg-red-500/10 blur-[60px] group-hover:bg-red-500/20 transition-all"></div>
                <div class="relative z-10">
                    <div class="p-3 bg-red-500/10 rounded-2xl w-fit mb-6">
                        <UsersIcon class="w-7 h-7 text-red-500" />
                    </div>
                    <div class="text-[10px] font-black text-slate-500 uppercase tracking-[0.2em] mb-1 italic">Effectif Total</div>
                    <div class="text-5xl font-black text-white tracking-tighter">{{ stats.total_users }} <span class="text-lg text-slate-600">Agents</span></div>
                </div>
            </div>

            <!-- Premium Ratio -->
            <div class="bg-surface-900/40 backdrop-blur-xl border border-surface-800 p-8 rounded-[2.5rem] hover:border-violet-500/40 transition-all group relative overflow-hidden">
                <div class="absolute right-0 top-0 w-32 h-32 bg-violet-500/10 blur-[60px] group-hover:bg-violet-500/20 transition-all"></div>
                <div class="relative z-10">
                    <div class="p-3 bg-violet-500/10 rounded-2xl w-fit mb-6">
                        <SparklesIcon class="w-7 h-7 text-violet-400" />
                    </div>
                    <div class="text-[10px] font-black text-slate-500 uppercase tracking-[0.2em] mb-1 italic">Membres Premium</div>
                    <div class="text-5xl font-black text-white tracking-tighter">{{ stats.tiers.pro + stats.tiers.essential }} <span class="text-lg text-slate-600">VIP</span></div>
                </div>
            </div>

            <!-- Applications -->
            <div class="bg-surface-900/40 backdrop-blur-xl border border-surface-800 p-8 rounded-[2.5rem] hover:border-indigo-500/40 transition-all group relative overflow-hidden">
                <div class="absolute right-0 top-0 w-32 h-32 bg-indigo-500/10 blur-[60px] group-hover:bg-indigo-500/20 transition-all"></div>
                <div class="relative z-10">
                    <div class="p-3 bg-indigo-500/10 rounded-2xl w-fit mb-6">
                        <BriefcaseIcon class="w-7 h-7 text-indigo-400" />
                    </div>
                    <div class="text-[10px] font-black text-slate-500 uppercase tracking-[0.2em] mb-1 italic">Missions Lancées</div>
                    <div class="text-5xl font-black text-white tracking-tighter">{{ stats.total_applications }} <span class="text-lg text-slate-600">Apps</span></div>
                </div>
            </div>

            <!-- Conversion Estimate -->
            <div class="bg-surface-900/40 backdrop-blur-xl border border-surface-800 p-8 rounded-[2.5rem] hover:border-emerald-500/40 transition-all group relative overflow-hidden">
                <div class="absolute right-0 top-0 w-32 h-32 bg-emerald-500/10 blur-[60px] group-hover:bg-emerald-500/20 transition-all"></div>
                <div class="relative z-10">
                    <div class="p-3 bg-emerald-500/10 rounded-2xl w-fit mb-6">
                        <ChartBarIcon class="w-7 h-7 text-emerald-400" />
                    </div>
                    <div class="text-[10px] font-black text-slate-500 uppercase tracking-[0.2em] mb-1 italic">Taux de Rétention</div>
                    <div class="text-5xl font-black text-white tracking-tighter">94<span class="text-2xl text-emerald-500/50">%</span></div>
                </div>
            </div>
        </div>

        <!-- --- USER LIST SECTION --- -->
        <div class="bg-surface-900/30 backdrop-blur-2xl border border-surface-800 rounded-[3rem] overflow-hidden shadow-[0_40px_100px_rgba(0,0,0,0.6)]">
            <div class="p-10 border-b border-surface-800 flex flex-col md:flex-row md:items-center justify-between gap-8">
                <div>
                    <h2 class="text-2xl font-black text-white tracking-tight flex items-center gap-3 italic uppercase">
                        Détection de Flotte
                        <span class="bg-white/5 text-slate-500 text-xs px-2 py-0.5 rounded-md not-italic font-mono border border-white/10">{{ filteredUsers.length }}</span>
                    </h2>
                    <p class="text-slate-500 text-sm mt-1">Identifiez et interagissez avec chaque agent déployé.</p>
                </div>
                
                <div class="relative group max-w-lg w-full">
                    <MagnifyingGlassIcon class="absolute left-5 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500 group-focus-within:text-red-500 transition-colors" />
                    <input 
                        v-model="searchQuery"
                        type="text" 
                        placeholder="Scanner par email, nom ou ID tactique..." 
                        class="w-full bg-black/50 border border-surface-800 rounded-[1.2rem] pl-14 pr-6 py-4 text-sm text-white focus:outline-none focus:border-red-500/50 transition-all font-medium placeholder:text-slate-600 shadow-inner"
                    />
                </div>
            </div>

            <div class="overflow-x-auto">
                <table class="w-full text-left border-collapse">
                    <thead>
                        <tr class="bg-black/40 text-[11px] font-black text-slate-600 uppercase tracking-[0.25em]">
                            <th class="px-10 py-6 border-b border-surface-800">AGENT IDENTITÉ</th>
                            <th class="px-10 py-6 border-b border-surface-800">COORDONNÉES</th>
                            <th class="px-10 py-6 border-b border-surface-800 text-center">STATUT DE RANG</th>
                            <th class="px-10 py-6 border-b border-surface-800 text-right">COMMANDES</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-surface-800/50">
                        <tr v-for="user in filteredUsers" :key="user.email" 
                            @click="fetchUserDetails(user)"
                            class="hover:bg-white/[0.03] transition-all group cursor-pointer"
                        >
                            <td class="px-10 py-7">
                                <div class="flex items-center gap-4">
                                    <div class="w-14 h-14 rounded-2xl bg-gradient-to-br from-surface-800 to-surface-700 flex items-center justify-center text-xl text-white font-black border border-surface-600 shadow-xl transition-all group-hover:scale-110 group-hover:rotate-3 group-hover:border-red-500/30">
                                        {{ user.full_name?.charAt(0).toUpperCase() || user.email.charAt(0).toUpperCase() }}
                                    </div>
                                    <div>
                                        <div class="text-lg font-black text-white tracking-tight group-hover:text-red-400 transition-colors">{{ user.full_name || 'Agent Inconnu' }}</div>
                                        <div class="text-[10px] text-slate-500 font-mono tracking-tighter uppercase mt-0.5 bg-white/5 w-fit px-1.5 rounded">ID: {{ user._id?.slice(-12) || user.id?.slice(-8) }}</div>
                                    </div>
                                </div>
                            </td>
                            <td class="px-10 py-7">
                                <div class="flex flex-col gap-1">
                                    <span class="text-sm text-slate-300 font-bold flex items-center gap-2">
                                        <EnvelopeIcon class="w-3.5 h-3.5 text-slate-500" />
                                        {{ user.email }}
                                    </span>
                                    <span class="text-[10px] text-slate-600 font-black uppercase tracking-widest flex items-center gap-2">
                                        <ClockIcon class="w-3.5 h-3.5" />
                                        Inscrit le : 12/02/2024
                                    </span>
                                </div>
                            </td>
                            <td class="px-10 py-7 text-center">
                                <div v-if="user.subscription_tier === 'ADMIN'" class="inline-flex items-center gap-1.5 bg-red-500/10 text-red-500 text-[10px] font-black px-4 py-1.5 rounded-full border border-red-500/20 uppercase tracking-widest italic shadow-lg shadow-red-500/5">
                                    <ShieldCheckIcon class="w-3.5 h-3.5" />
                                    Administrateur
                                </div>
                                <div v-else-if="user.subscription_tier === 'PRO'" class="inline-flex items-center gap-1.5 bg-indigo-500/10 text-indigo-400 text-[10px] font-black px-4 py-1.5 rounded-full border border-indigo-500/20 uppercase tracking-widest italic shadow-lg shadow-indigo-500/5">
                                    <SparklesIcon class="w-3.5 h-3.5" />
                                    Premium Pro
                                </div>
                                <div v-else-if="user.subscription_tier === 'ESSENTIAL'" class="inline-flex items-center gap-1.5 bg-amber-500/10 text-amber-500 text-[10px] font-black px-4 py-1.5 rounded-full border border-amber-500/20 uppercase tracking-widest italic shadow-lg shadow-amber-500/5">
                                    <CheckBadgeIcon class="w-3.5 h-3.5" />
                                    Essentiel
                                </div>
                                <div v-else class="inline-flex items-center gap-1.5 bg-surface-800 text-slate-500 text-[10px] font-black px-4 py-1.5 rounded-full border border-white/5 uppercase tracking-widest italic">
                                    Agent Libre
                                </div>
                            </td>
                            <td class="px-10 py-7 text-right" @click.stop>
                                <div class="flex items-center justify-end gap-3 grayscale opacity-40 group-hover:grayscale-0 group-hover:opacity-100 transition-all">
                                    <button @click="fetchUserDetails(user)" class="p-2.5 bg-surface-800 hover:bg-white hover:text-black rounded-xl border border-white/10 transition-all" title="Inspecter l'agent">
                                        <EyeIcon class="w-5 h-5" />
                                    </button>
                                    <select 
                                        @change="(e) => updateTier(user.email, e.target.value)" 
                                        :value="user.subscription_tier || 'FREE'"
                                        class="bg-black border border-surface-800 text-slate-300 text-[10px] font-black uppercase rounded-xl px-4 py-2.5 focus:outline-none focus:border-red-500 transition-all hover:bg-surface-800 disabled:opacity-50 cursor-pointer shadow-lg"
                                        :disabled="isActionLoading || user.email === stats.admin_email"
                                    >
                                        <option value="FREE">LIBRE (FREE)</option>
                                        <option value="ESSENTIAL">ESSENTIEL</option>
                                        <option value="PRO">MISSION PRO</option>
                                        <option value="ADMIN">COMMANDANT (ADMIN)</option>
                                    </select>
                                </div>
                            </td>
                        </tr>
                    </tbody>
                </table>
                
                <div v-if="isLoading" class="py-32 flex flex-col items-center justify-center gap-6">
                    <div class="relative w-16 h-16">
                        <div class="absolute inset-0 border-4 border-red-500/20 rounded-full"></div>
                        <div class="absolute inset-0 border-4 border-red-500 border-t-transparent rounded-full animate-spin"></div>
                    </div>
                    <span class="text-xs font-black text-slate-500 uppercase tracking-[0.4em] italic animate-pulse">Scan RADAR en cours...</span>
                </div>

                <div v-if="!isLoading && filteredUsers.length === 0" class="py-32 text-center">
                    <div class="text-6xl mb-6 opacity-20">📡</div>
                    <p class="text-slate-500 font-black uppercase tracking-widest italic">Aucun agent détecté sur cette fréquence.</p>
                </div>
            </div>
        </div>
    </div>

    <!-- --- DEEP INSPECTION SIDE PANEL --- -->
    <Transition name="slide-right">
        <aside v-if="isPanelOpen" class="fixed top-0 right-0 h-full w-full lg:w-[600px] bg-black border-l border-surface-800 z-[100] shadow-[-20px_0_60px_rgba(0,0,0,0.8)] overflow-hidden flex flex-col">
            
            <!-- Panel Header -->
            <div class="p-8 border-b border-surface-800 bg-surface-950/50 backdrop-blur-md flex items-center justify-between shrink-0">
                <div class="flex items-center gap-4">
                    <div class="w-12 h-12 rounded-xl bg-red-600 flex items-center justify-center text-white font-black shadow-lg shadow-red-600/20">
                        <ShieldCheckIcon class="w-7 h-7" />
                    </div>
                    <div>
                        <h3 class="text-xl font-black text-white uppercase italic tracking-tight">Rapport d'Agent</h3>
                        <p class="text-[10px] text-slate-500 font-bold uppercase tracking-widest">Niveau d'accès : Maximum</p>
                    </div>
                </div>
                <button @click="isPanelOpen = false" class="p-3 bg-surface-800 hover:bg-rose-500/20 hover:text-rose-500 text-slate-400 rounded-2xl transition-all border border-white/5">
                    <XMarkIcon class="w-6 h-6" />
                </button>
            </div>

            <!-- Panel Content -->
            <div class="flex-1 overflow-y-auto p-10 space-y-12">
                
                <div v-if="isDetailsLoading" class="flex flex-col items-center justify-center h-full py-20 gap-4">
                    <div class="w-10 h-10 border-t-2 border-red-500 rounded-full animate-spin"></div>
                    <p class="text-xs font-black text-slate-600 uppercase tracking-widest italic">Extraction des données cryptées...</p>
                </div>

                <div v-else class="animate-fade-in space-y-12">
                    
                    <!-- Top Info Card -->
                    <div class="bg-surface-900/50 rounded-[2rem] p-8 border border-surface-800 relative overflow-hidden">
                        <div class="absolute -right-10 -bottom-10 w-40 h-40 bg-white/5 blur-3xl rounded-full"></div>
                        <div class="flex items-center gap-6 mb-8 relative z-10">
                            <div class="w-20 h-20 rounded-[1.5rem] bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-3xl text-white font-black shadow-2xl">
                                {{ userDetails.profile.full_name?.charAt(0) || userDetails.profile.email?.charAt(0) }}
                            </div>
                            <div>
                                <h4 class="text-2xl font-black text-white italic truncate">{{ userDetails.profile.full_name || 'Anonyme' }}</h4>
                                <div class="flex items-center gap-2 mt-1">
                                    <span class="text-xs font-bold text-slate-400">{{ userDetails.profile.email }}</span>
                                    <span class="w-1.5 h-1.5 rounded-full bg-slate-700"></span>
                                    <span class="text-[10px] font-black text-indigo-400 uppercase italic">Opérateur de Territoire</span>
                                </div>
                            </div>
                        </div>

                        <div class="grid grid-cols-2 gap-4 relative z-10">
                            <div class="bg-black/50 p-4 rounded-2xl border border-white/5">
                                <span class="text-[10px] font-black text-slate-500 uppercase block mb-1">Forfait Actuel</span>
                                <span class="text-sm font-bold text-white uppercase italic tracking-tight text-red-500">{{ userDetails.profile.subscription_tier || 'FREE' }}</span>
                            </div>
                            <div class="bg-black/50 p-4 rounded-2xl border border-white/5">
                                <span class="text-[10px] font-black text-slate-500 uppercase block mb-1">Candidatures</span>
                                <span class="text-sm font-bold text-white uppercase italic tracking-tight">{{ userDetails.applications.length }} envois</span>
                            </div>
                        </div>
                    </div>

                    <!-- CV SECTION -->
                    <section class="space-y-4">
                        <div class="flex items-center gap-3">
                            <DocumentTextIcon class="w-5 h-5 text-red-500" />
                            <h5 class="text-sm font-black text-white uppercase italic border-b border-red-500/30 pb-1">Analyse du CV (TEXT_RAW)</h5>
                        </div>
                        <div class="bg-surface-900 rounded-3xl p-6 border border-surface-800 max-h-[300px] overflow-y-auto custom-scrollbar">
                           <pre v-if="userDetails.profile.cv_text" class="text-slate-400 text-xs font-mono leading-relaxed whitespace-pre-wrap">{{ userDetails.profile.cv_text }}</pre>
                           <div v-else class="text-slate-600 text-xs italic py-10 text-center">Aucune donnée de curriculum vitae enregistrée pour cet agent.</div>
                        </div>
                    </section>

                    <!-- CRM HISTORY -->
                    <section class="space-y-6">
                        <div class="flex items-center justify-between">
                            <div class="flex items-center gap-3">
                                <QueueListIcon class="w-5 h-5 text-indigo-400" />
                                <h5 class="text-sm font-black text-white uppercase italic border-b border-indigo-500/30 pb-1">Historique des Opérations (CRM)</h5>
                            </div>
                        </div>
                        
                        <div v-if="userDetails.applications.length > 0" class="space-y-3">
                            <div v-for="app in userDetails.applications" :key="app._id" class="p-4 bg-surface-900/50 rounded-2xl border border-white/5 flex items-center justify-between group hover:bg-surface-800 hover:border-white/10 transition-all">
                                <div class="flex items-center gap-4">
                                    <div class="w-10 h-10 rounded-lg bg-black flex items-center justify-center font-black text-indigo-500 border border-white/5">
                                        {{ app.company_name?.charAt(0) }}
                                    </div>
                                    <div>
                                        <div class="text-sm font-bold text-white truncate max-w-[200px]">{{ app.job_title }}</div>
                                        <div class="text-[10px] text-slate-500 uppercase font-black tracking-tighter">{{ app.company_name }}</div>
                                    </div>
                                </div>
                                <div :class="`text-[9px] font-black px-3 py-1 rounded-lg border uppercase tracking-widest ${getStatusColor(app.status)}`">
                                    {{ app.status }}
                                </div>
                            </div>
                        </div>
                        <div v-else class="text-center py-10 bg-surface-900/30 rounded-[2rem] border border-dashed border-surface-800">
                             <p class="text-slate-600 text-xs italic uppercase tracking-widest">Nulle trace d'activité CRM pour cet agent.</p>
                        </div>
                    </section>

                    <!-- ACTIONS BOTTOM -->
                    <div class="pt-10 flex flex-col gap-4">
                        <p class="text-[10px] font-black text-slate-600 uppercase tracking-[0.3em] text-center mb-2">Décisions de la Zone de Commandement</p>
                        <div class="grid grid-cols-2 gap-4">
                            <button @click="updateTier(userDetails.profile.email, 'PRO')" class="flex items-center justify-center gap-2 py-4 bg-white text-black font-black text-xs uppercase rounded-2xl hover:bg-indigo-500 hover:text-white transition-all shadow-xl">
                                <SparklesIcon class="w-4 h-4" />
                                Upgrade PREMIUM PRO
                            </button>
                            <button @click="updateTier(userDetails.profile.email, 'FREE')" class="flex items-center justify-center gap-2 py-4 bg-surface-800 text-slate-400 font-bold text-xs uppercase rounded-2xl hover:bg-rose-500/20 hover:text-rose-500 transition-all border border-white/5">
                                <XMarkIcon class="w-4 h-4" />
                                Révoquer Accès
                            </button>
                        </div>
                        <button @click="updateTier(userDetails.profile.email, 'ADMIN')" class="w-full py-4 bg-red-600 text-white font-black text-xs uppercase tracking-[0.2em] rounded-2xl hover:bg-red-500 transition-all shadow-2xl shadow-red-600/20 flex items-center justify-center gap-2">
                             <ShieldCheckIcon class="w-4 h-4" />
                             Muter vers COMMANDANT (ADMIN)
                        </button>
                    </div>
                </div>
            </div>
        </aside>
    </Transition>

    <!-- Overlay for panel -->
    <div v-if="isPanelOpen" @click="isPanelOpen = false" class="fixed inset-0 bg-black/80 backdrop-blur-sm z-[90] animate-fade-in"></div>

  </div>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@100;400;700;900&display=swap');

:host, :root {
    font-family: 'Outfit', sans-serif;
}

.animate-fade-in {
    animation: fadeIn 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

.slide-right-enter-active, .slide-right-leave-active {
    transition: transform 0.6s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.4s ease;
}

.slide-right-enter-from, .slide-right-leave-to {
    transform: translateX(100%);
    opacity: 0;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(15px); }
    to { opacity: 1; transform: translateY(0); }
}

.custom-scrollbar::-webkit-scrollbar {
    width: 6px;
}
.custom-scrollbar::-webkit-scrollbar-track {
    background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 10px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
    background: rgba(255, 255, 255, 0.2);
}

pre {
    font-family: 'JetBrains Mono', 'Fira Code', monospace;
}
</style>
