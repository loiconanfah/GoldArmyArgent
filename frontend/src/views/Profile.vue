<script setup>
import { ref, onMounted } from 'vue'
import { authFetch } from '../utils/auth'
import { toastState } from '../store/toastState'
import { 
    UserIcon, 
    EnvelopeIcon, 
    BriefcaseIcon, 
    LinkIcon, 
    DocumentTextIcon, 
    SparklesIcon,
    PencilSquareIcon,
    ArrowLeftIcon,
    CameraIcon,
    CloudArrowUpIcon
} from '@heroicons/vue/24/outline'
import { useRouter } from 'vue-router'

const router = useRouter()
const isLoading = ref(true)
const isSaving = ref(false)
const isUploadingCv = ref(false)
const isUploadingAvatar = ref(false)

const cvFileInput = ref(null)
const avatarFileInput = ref(null)

const profile = ref({
    full_name: '',
    email: '',
    bio: '',
    cv_text: '',
    portfolio_url: '',
    avatar_url: '',
    subscription_tier: 'FREE'
})

const adminEmailToPromote = ref('')
const isPromoting = ref(false)

const fetchProfile = async () => {
    isLoading.value = true
    try {
        const res = await authFetch('http://localhost:8000/api/profile')
        const json = await res.json()
        if (json.status === 'success') {
            profile.value = { ...profile.value, ...json.data }
        }
    } catch (e) {
        toastState.addToast("Impossible de charger le profil.", "error")
    } finally {
        isLoading.value = false
    }
}

const saveProfile = async () => {
    isSaving.value = true
    try {
        const res = await authFetch('http://localhost:8000/api/profile', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(profile.value)
        })
        const json = await res.json()
        if (json.status === 'success') {
            toastState.addToast("Profil mis à jour avec succès !")
        } else {
            toastState.addToast(json.detail || "Erreur lors de la sauvegarde.", "error")
        }
    } catch (e) {
        toastState.addToast("Erreur de connexion au serveur.", "error")
    } finally {
        isSaving.value = false
    }
}

const triggerCvUpload = () => cvFileInput.value.click()
const onCvFileChange = async (event) => {
    const file = event.target.files[0]
    if (!file) return
    
    isUploadingCv.value = true
    const formData = new FormData()
    formData.append('file', file)
    
    try {
        const res = await fetch('http://localhost:8000/api/profile/upload-cv', {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` },
            body: formData
        })
        const json = await res.json()
        if (json.status === 'success') {
            profile.value.cv_text = json.text
            toastState.addToast("CV extrait et enregistré avec succès !")
        } else {
            toastState.addToast(json.detail || "Erreur lors de l'upload.", "error")
        }
    } catch (e) {
        toastState.addToast("Erreur lors de l'envoi du CV.", "error")
    } finally {
        isUploadingCv.value = false
    }
}

const triggerAvatarUpload = () => avatarFileInput.value.click()
const onAvatarFileChange = async (event) => {
    const file = event.target.files[0]
    if (!file) return
    
    isUploadingAvatar.value = true
    const formData = new FormData()
    formData.append('file', file)
    
    try {
        const res = await fetch('http://localhost:8000/api/profile/upload-avatar', {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` },
            body: formData
        })
        const json = await res.json()
        if (json.status === 'success') {
            profile.value.avatar_url = json.avatar_url
            toastState.addToast("Photo de profil mise à jour !")
        } else {
            toastState.addToast(json.detail || "Erreur de photo.", "error")
        }
    } catch (e) {
        toastState.addToast("Erreur lors de l'envoi de la photo.", "error")
    } finally {
        isUploadingAvatar.value = false
    }
}

onMounted(fetchProfile)

const goBack = () => router.push('/dashboard')
const editPortfolio = () => {
    router.push({ path: '/chat', query: { action: 'edit_last_portfolio' } })
}

const downloadZip = async () => {
    try {
        const token = localStorage.getItem('token')
        const res = await fetch('http://localhost:8000/api/portfolio/download-zip', {
            headers: token ? { Authorization: `Bearer ${token}` } : {}
        })
        if (!res.ok) throw new Error("Erreur de téléchargement")
        const blob = await res.blob()
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = 'goldarmy_portfolio.zip'
        a.click()
    } catch (e) {
        toastState.addToast('Erreur lors du téléchargement du ZIP.', 'error')
    }
}

const promoteUser = async () => {
    if (!adminEmailToPromote.value) return
    isPromoting.value = true
    try {
        const res = await authFetch('http://localhost:8000/api/admin/promote-user', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email: adminEmailToPromote.value, tier: 'PRO' })
        })
        const data = await res.json()
        if (res.ok) {
            toastState.addToast(`L'utilisateur ${adminEmailToPromote.value} est maintenant Premium !`, 'success')
            adminEmailToPromote.value = ''
        } else {
            toastState.addToast(data.detail || 'Erreur promotion', 'error')
        }
    } catch (e) {
        toastState.addToast('Erreur connexion admin', 'error')
    } finally {
        isPromoting.value = false
    }
}
</script>

<template>
  <div class="px-4 md:px-10 py-8 max-w-[1200px] mx-auto w-full animate-fade-in-up">
    
    <!-- Header -->
    <div class="flex items-center justify-between mb-10 pt-4">
        <div class="flex items-center gap-4">
            <button @click="goBack" class="p-3 bg-surface-900 border border-surface-800 rounded-2xl text-slate-400 hover:text-white transition-all hover:scale-110 active:scale-95">
                <ArrowLeftIcon class="w-5 h-5" />
            </button>
            <div>
                <h1 class="text-3xl font-display font-black text-white tracking-tight">Mon <span class="text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-purple-500">Profil</span></h1>
                <p class="text-slate-400 text-sm font-medium mt-1">Gérez votre identité numérique et vos documents de carrière.</p>
            </div>
        </div>
        
        <button 
            @click="saveProfile"
            :disabled="isSaving"
            class="hidden md:flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-400 hover:to-purple-500 text-white font-bold rounded-2xl shadow-lg shadow-indigo-500/20 transition-all hover:scale-105 active:scale-95 disabled:opacity-50"
        >
            <span v-if="!isSaving">Enregistrer les modifications</span>
            <span v-else class="flex items-center gap-2">
                <svg class="animate-spin h-4 w-4 text-white" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
                Sauvegarde...
            </span>
        </button>
    </div>

    <!-- Hidden Inputs -->
    <input type="file" ref="cvFileInput" class="hidden" accept=".pdf" @change="onCvFileChange" />
    <input type="file" ref="avatarFileInput" class="hidden" accept="image/*" @change="onAvatarFileChange" />

    <div v-if="isLoading" class="flex flex-col items-center justify-center py-32">
        <div class="w-16 h-16 border-4 border-indigo-500/20 border-t-indigo-500 rounded-full animate-spin"></div>
    </div>

    <div v-else class="grid grid-cols-1 lg:grid-cols-12 gap-8 pb-32">
        
        <!-- Sidebar: Info Rapide -->
        <div class="lg:col-span-4 space-y-6">
            <div class="bg-surface-900 border border-surface-800 rounded-[2.5rem] p-8 relative overflow-hidden group shadow-sm">
                <div class="absolute -top-12 -right-12 w-48 h-48 bg-indigo-500/5 rounded-full blur-3xl group-hover:bg-indigo-500/10 transition-all duration-700"></div>
                
                <div class="relative z-10 flex flex-col items-center">
                    <!-- Avatar Area -->
                    <div class="relative mb-6">
                        <div class="w-28 h-28 rounded-[2rem] bg-gradient-to-br from-surface-800 to-surface-950 border-2 border-surface-700 flex items-center justify-center overflow-hidden shadow-2xl rotate-3 group-hover:rotate-0 transition-transform duration-500 bg-surface-950">
                            <img v-if="profile.avatar_url" :src="profile.avatar_url" class="w-full h-full object-cover" />
                            <UserIcon v-else class="w-12 h-12 text-slate-700" />
                            <!-- Loading Overlay -->
                            <div v-if="isUploadingAvatar" class="absolute inset-0 bg-surface-950/80 flex items-center justify-center">
                                <svg class="animate-spin h-6 w-6 text-indigo-500" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
                            </div>
                        </div>
                        <button 
                            @click="triggerAvatarUpload"
                            class="absolute -bottom-2 -right-2 p-3 bg-indigo-500 text-white rounded-2xl shadow-lg hover:bg-indigo-400 transition-all hover:scale-110 active:scale-90 border-4 border-surface-900 group/cam"
                        >
                            <CameraIcon class="w-4 h-4 transition-transform group-hover/cam:rotate-12" />
                        </button>
                    </div>
                    
                    <h2 class="text-xl font-bold text-white mb-1 tracking-tight">{{ profile.full_name || 'Candidat GoldArmy' }}</h2>
                    <p class="text-slate-500 text-sm mb-3 font-medium">{{ profile.email }}</p>

                    <!-- Profile Badge Forfait -->
                    <div class="mb-6">
                        <span v-if="profile.subscription_tier === 'ADMIN'" class="bg-gradient-to-r from-red-500 to-rose-600 text-white text-[10px] uppercase font-black px-3 py-1 rounded-full shadow-lg shadow-rose-500/20">Admin GoldArmy</span>
                        <span v-else-if="profile.subscription_tier === 'PRO'" class="bg-gradient-to-r from-violet-500 to-indigo-500 text-white text-[10px] uppercase font-black px-3 py-1 rounded-full shadow-lg shadow-indigo-500/20">Membre GoldArmy Pro</span>
                        <span v-else-if="profile.subscription_tier === 'ESSENTIAL'" class="bg-gradient-to-r from-amber-400 to-gold-500 text-surface-950 text-[10px] uppercase font-black px-3 py-1 rounded-full shadow-lg shadow-gold-500/20">Membre GoldArmy Essentiel</span>
                        <span v-else class="bg-surface-800 text-slate-400 text-[10px] uppercase font-black px-3 py-1 rounded-full border border-surface-700">Forfait Gratuit</span>
                    </div>
                    
                    <div class="w-full space-y-3 pt-6 border-t border-surface-800">
                        <div class="flex items-center gap-3 text-slate-400 font-medium text-[13px]">
                            <div class="w-2 h-2 rounded-full" :class="profile.cv_text ? 'bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]' : 'bg-slate-700'"></div>
                            {{ profile.cv_text ? 'CV Chargé' : 'Aucun CV' }}
                        </div>
                        <div class="flex items-center gap-3 text-slate-400 font-medium text-[13px]">
                            <LinkIcon class="w-4 h-4" :class="profile.portfolio_url ? 'text-indigo-400' : 'text-slate-700'" />
                            {{ profile.portfolio_url ? 'Portfolio lié' : 'Pas de lien externe' }}
                        </div>
                    </div>
                </div>
            </div>

            <!-- Stats HUD -->
            <div class="bg-surface-900 border border-surface-800 rounded-[2.5rem] p-6 shadow-sm">
                <div class="flex items-center gap-3 mb-4">
                    <SparklesIcon class="w-5 h-5 text-indigo-400" />
                    <h3 class="font-bold text-white text-[11px] uppercase tracking-[0.2em]">Profile Readiness</h3>
                </div>
                <div class="space-y-4">
                    <div class="flex justify-between text-[11px] font-black mb-1 italic">
                        <span class="text-slate-500">OPTIMISATION ALPHA</span>
                        <span class="text-indigo-400">88%</span>
                    </div>
                    <div class="h-1.5 w-full bg-surface-800 rounded-full overflow-hidden p-[1px]">
                        <div class="h-full bg-gradient-to-r from-indigo-600 to-purple-500 rounded-full" style="width: 88%"></div>
                    </div>
                </div>
            </div>

            <!-- Admin Console (Move from Chat) -->
            <div v-if="profile.subscription_tier === 'ADMIN'" class="bg-surface-900 border border-indigo-500/30 rounded-[2.5rem] p-8 shadow-lg shadow-indigo-500/5 animate-fade-in-up">
                <div class="flex items-center gap-3 mb-6">
                    <div class="p-2 bg-indigo-500/10 rounded-xl">
                        <ShieldCheckIcon class="w-5 h-5 text-indigo-400" />
                    </div>
                    <h3 class="text-xl font-bold text-white tracking-tight">Console Admin</h3>
                </div>
                <div class="space-y-4">
                    <p class="text-xs text-slate-400 font-medium leading-relaxed">Promouvoir un utilisateur au rang Premium (PRO) via son e-mail.</p>
                    <div class="flex gap-2">
                        <input 
                            v-model="adminEmailToPromote" 
                            type="email" 
                            placeholder="email@exemple.com"
                            class="flex-1 bg-surface-950 border border-surface-800 rounded-2xl px-5 py-3 text-white focus:outline-none focus:border-indigo-500 transition-all text-xs"
                        />
                        <button 
                            @click="promoteUser"
                            :disabled="isPromoting"
                            class="px-6 py-3 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold rounded-2xl transition-all shadow-lg shadow-indigo-500/20 disabled:opacity-50"
                        >
                            {{ isPromoting ? '...' : 'PROMOUVOIR' }}
                        </button>
                    </div>
                </div>
            </div>
        </div>

        <!-- Main Column: Formulaire -->
        <div class="lg:col-span-8 space-y-8">
            
            <div class="bg-surface-900 border border-surface-800 rounded-[2.5rem] p-8 md:p-10 shadow-sm relative overflow-hidden">
                <div class="flex items-center gap-3 mb-8">
                    <div class="p-2 bg-indigo-500/10 rounded-xl">
                        <PencilSquareIcon class="w-5 h-5 text-indigo-400" />
                    </div>
                    <h3 class="text-xl font-bold text-white tracking-tight">Détails Personnels</h3>
                </div>
                
                <div class="grid grid-cols-1 md:grid-cols-2 gap-7">
                    <div class="space-y-2.5">
                        <label class="text-[11px] font-black text-slate-500 uppercase tracking-widest ml-1">Nom Complet</label>
                        <input 
                            v-model="profile.full_name"
                            type="text" 
                            placeholder="John Doe"
                            class="w-full bg-surface-950 border border-surface-800 rounded-2xl px-5 py-4 text-white focus:outline-none focus:border-indigo-500 transition-all placeholder:text-slate-800 font-medium"
                        />
                    </div>
                    <div class="space-y-2.5">
                        <label class="text-[11px] font-black text-slate-500 uppercase tracking-widest ml-1">Portfolio / LinkedIn</label>
                        <input 
                            v-model="profile.portfolio_url"
                            type="text" 
                            placeholder="https://linkedin.com/in/..."
                            class="w-full bg-surface-950 border border-surface-800 rounded-2xl px-5 py-4 text-white focus:outline-none focus:border-indigo-500 transition-all placeholder:text-slate-800 font-medium"
                        />
                    </div>
                    <div class="md:col-span-2 space-y-2.5">
                        <label class="text-[11px] font-black text-slate-500 uppercase tracking-widest ml-1">Bio / Titre Professionnel</label>
                        <textarea 
                            v-model="profile.bio"
                            rows="3" 
                            placeholder="Développeur Fullstack passionné par l'IA..."
                            class="w-full bg-surface-950 border border-surface-800 rounded-2xl px-5 py-4 text-white focus:outline-none focus:border-indigo-500 transition-all placeholder:text-slate-800 resize-none font-medium leading-relaxed"
                        ></textarea>
                    </div>
                </div>
            </div>

            <!-- CV Management Section -->
            <div class="bg-surface-900 border border-surface-800 rounded-[2.5rem] p-8 md:p-10 shadow-sm relative overflow-hidden group">
                <div class="flex items-center justify-between mb-8">
                    <div class="flex items-center gap-3">
                        <div class="p-2 bg-emerald-500/10 rounded-xl">
                            <DocumentTextIcon class="w-5 h-5 text-emerald-400" />
                        </div>
                        <h3 class="text-xl font-bold text-white tracking-tight">Mon CV Principal</h3>
                    </div>
                    
                    <button 
                        @click="triggerCvUpload"
                        :disabled="isUploadingCv"
                        class="flex items-center gap-2 px-4 py-2 bg-surface-800 border border-surface-700 hover:border-emerald-500/50 text-emerald-400 text-xs font-black rounded-xl transition-all hover:bg-emerald-500/5 disabled:opacity-50"
                    >
                        <CloudArrowUpIcon v-if="!isUploadingCv" class="w-4 h-4" />
                        <svg v-else class="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
                        EXTRAIRE DEPUIS PDF
                    </button>
                </div>
                
                <p class="text-sm text-slate-500 mb-6 font-medium leading-relaxed">C'est la base qu'utilisera l'IA pour le Sniper et les approches réseaux. L'extraction PDF permet de remplir ce champ automatiquement.</p>
                
                <div class="relative group/cv">
                    <textarea 
                        v-model="profile.cv_text"
                        rows="12" 
                        class="w-full bg-surface-950 border border-surface-800 rounded-3xl px-6 py-6 text-slate-300 text-[13px] leading-relaxed focus:outline-none focus:border-emerald-500/50 transition-all font-mono custom-scrollbar"
                        placeholder="Contenu de votre CV..."
                    ></textarea>
                    <!-- Decorative HUD line -->
                    <div class="absolute bottom-4 right-6 text-[10px] font-mono text-slate-700 tracking-tighter pointer-events-none">
                        RAW_DATA_V2 // CV_STORAGE
                    </div>
                </div>
            </div>
            
            <!-- Portfolio IA Section -->
            <div class="bg-surface-900 border border-surface-800 rounded-[2.5rem] p-8 md:p-10 shadow-sm relative overflow-hidden group mb-8">
                <div class="flex items-center justify-between mb-8">
                    <div class="flex items-center gap-3">
                        <div class="p-2 bg-indigo-500/10 rounded-xl">
                            <SparklesIcon class="w-5 h-5 text-indigo-400" />
                        </div>
                        <h3 class="text-xl font-bold text-white tracking-tight">Mon Portfolio IA</h3>
                    </div>
                </div>

                <div v-if="profile.last_portfolio" class="space-y-6">
                    <div class="p-6 bg-surface-950 border border-surface-800 rounded-3xl flex flex-col md:flex-row items-center justify-between gap-6">
                        <div class="flex items-center gap-4">
                            <div class="w-12 h-12 bg-emerald-500/20 rounded-2xl flex items-center justify-center">
                                <DocumentTextIcon class="w-6 h-6 text-emerald-400" />
                            </div>
                            <div>
                                <h4 class="font-bold text-white text-sm">Projet Web Complet</h4>
                                <p class="text-xs text-slate-500">Prêt pour l'édition ou l'export.</p>
                            </div>
                        </div>
                        <div class="flex items-center gap-3">
                            <button @click="editPortfolio" class="px-5 py-2.5 bg-indigo-500 hover:bg-indigo-400 text-white text-xs font-bold rounded-xl transition-all shadow-lg shadow-indigo-500/20">
                                Éditer dans l'IDE
                            </button>
                            <button @click="downloadZip" class="px-5 py-2.5 bg-surface-800 border border-surface-700 hover:border-emerald-500/50 text-emerald-400 text-xs font-bold rounded-xl transition-all">
                                ZIP
                            </button>
                        </div>
                    </div>
                    <p class="text-[11px] text-slate-500 italic px-2 bg-surface-950/50 p-3 rounded-xl border border-surface-800">Analyse IA : {{ profile.last_portfolio.personality_analysis }}</p>
                </div>

                <div v-else class="text-center py-12 border-2 border-dashed border-surface-800 rounded-[2rem] bg-surface-950/30">
                    <p class="text-slate-500 text-sm mb-4">Vous n'avez pas encore généré de portfolio IA.</p>
                    <button @click="router.push('/chat')" class="px-6 py-2 bg-indigo-500/10 hover:bg-indigo-500/20 text-indigo-400 font-bold rounded-xl border border-indigo-500/20 transition-all">
                        Générer avec GoldArmy →
                    </button>
                </div>
            </div>

            <!-- Mobile Only Save Button -->
            <div class="md:hidden pt-4 pb-20">
                <button 
                    @click="saveProfile"
                    :disabled="isSaving"
                    class="w-full flex items-center justify-center gap-2 px-6 py-5 bg-gradient-to-r from-indigo-500 to-purple-600 text-white font-bold rounded-2xl shadow-xl disabled:opacity-50"
                >
                    Enregistrer les modifications
                </button>
            </div>
        </div>
    </div>
  </div>
</template>

<style scoped>
.font-display {
    font-family: 'Outfit', sans-serif;
}
.custom-scrollbar::-webkit-scrollbar {
  width: 5px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #1e293b;
  border-radius: 10px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: #334155;
}
</style>

<style scoped>
.font-display {
    font-family: 'Outfit', sans-serif;
}
</style>
