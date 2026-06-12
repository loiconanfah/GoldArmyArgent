<script setup>
import { ref, onMounted } from 'vue'
import { authFetch } from '../utils/auth'
import { toastState } from '../store/toastState'
import { 
    UserIcon, 
    LinkIcon, 
    DocumentTextIcon, 
    SparklesIcon,
    PencilSquareIcon,
    ArrowLeftIcon,
    CameraIcon,
    CloudArrowUpIcon,
    ShieldCheckIcon,
    BriefcaseIcon
} from '@heroicons/vue/24/outline'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'

const router = useRouter()
const { t } = useI18n()
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
        const res = await authFetch('/api/profile')
        const json = await res.json()
        if (json.status === 'success') {
            profile.value = { ...profile.value, ...json.data }
        }
    } catch (e) {
        toastState.addToast(t('profile.toast_load_error'), "error")
    } finally {
        isLoading.value = false
    }
}

const saveProfile = async () => {
    isSaving.value = true
    try {
        const res = await authFetch('/api/profile', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(profile.value)
        })
        const json = await res.json()
        if (json.status === 'success') {
            toastState.addToast(t('profile.toast_save_success'))
        } else {
            toastState.addToast(json.detail || t('profile.toast_save_error'), "error")
        }
    } catch (e) {
        toastState.addToast(t('profile.toast_connect_error'), "error")
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
        const res = await authFetch('/api/profile/upload-cv', {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` },
            body: formData
        })
        const json = await res.json()
        if (json.status === 'success') {
            profile.value.cv_text = json.text
            toastState.addToast(t('profile.toast_cv_success'))
        } else {
            toastState.addToast(json.detail || t('profile.toast_cv_upload_error'), "error")
        }
    } catch (e) {
        toastState.addToast(t('profile.toast_cv_send_error'), "error")
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
        const res = await authFetch('/api/profile/upload-avatar', {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` },
            body: formData
        })
        const json = await res.json()
        if (json.status === 'success') {
            profile.value.avatar_url = json.avatar_url
            toastState.addToast(t('profile.toast_avatar_success'))
        } else {
            toastState.addToast(json.detail || t('profile.toast_avatar_error'), "error")
        }
    } catch (e) {
        toastState.addToast(t('profile.toast_avatar_send_error'), "error")
    } finally {
        isUploadingAvatar.value = false
    }
}

onMounted(fetchProfile)

const goBack = () => router.push('/dashboard')

const downloadZip = async () => {
    try {
        const token = localStorage.getItem('token')
        const res = await fetch('http://127.0.0.1:8000/api/portfolio/download-zip', {
            headers: token ? { Authorization: `Bearer ${token}` } : {}
        })
        if (!res.ok) throw new Error("Download error")
        const blob = await res.blob()
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = 'goldarmy_portfolio.zip'
        a.click()
    } catch (e) {
        toastState.addToast(t('profile.download_error'), 'error')
    }
}

const promoteUser = async () => {
    if (!adminEmailToPromote.value) return
    isPromoting.value = true
    try {
        const res = await authFetch('/api/admin/promote-user', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email: adminEmailToPromote.value, tier: 'PRO' })
        })
        const data = await res.json()
        if (res.ok) {
            toastState.addToast(t('profile.toast_promote_success', [adminEmailToPromote.value]), 'success')
            adminEmailToPromote.value = ''
        } else {
            toastState.addToast(data.detail || t('profile.toast_promote_error'), 'error')
        }
    } catch (e) {
        toastState.addToast(t('profile.toast_admin_error'), 'error')
    } finally {
        isPromoting.value = false
    }
}
</script>

<template>
  <div class="profile-root">
    
    <!-- Header -->
    <header class="profile-header animate-slide-up" style="animation-delay: 0s;">
        <div class="flex items-center gap-6">
            <button @click="goBack" class="btn-icon-white">
                <ArrowLeftIcon class="w-5 h-5" />
            </button>
            <div>
                <h1 class="text-3xl font-bold text-[#111827] tracking-tight">
                    {{ t('profile.title').split(' ')[0] }} <span class="text-[#F59E0B]">{{ t('profile.title').split(' ').slice(1).join(' ') }}</span>
                </h1>
                <p class="text-[#6B7280] text-sm font-medium mt-1">{{ t('profile.subtitle') }}</p>
            </div>
        </div>
        
        <div class="flex items-center gap-4">
            <button 
                v-if="profile.subscription_tier === 'ADMIN'"
                @click="router.push('/admin-goldarmy')"
                class="btn-admin hidden md:flex"
            >
                <ShieldCheckIcon class="w-4 h-4" />
                {{ t('profile.admin_console_btn') }}
            </button>

            <button 
                @click="saveProfile"
                :disabled="isSaving"
                class="btn-gold"
            >
                <span v-if="!isSaving">{{ t('profile.save_btn') }}</span>
                <span v-else class="flex items-center gap-2">
                    <svg class="animate-spin h-4 w-4 text-white" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
                    {{ t('profile.saving') }}
                </span>
            </button>
        </div>
    </header>

    <!-- Hidden Inputs -->
    <input type="file" ref="cvFileInput" class="hidden" accept=".pdf" @change="onCvFileChange" />
    <input type="file" ref="avatarFileInput" class="hidden" accept="image/*" @change="onAvatarFileChange" />

    <div v-if="isLoading" class="flex flex-col items-center justify-center py-32">
        <div class="w-12 h-12 border-4 border-gray-100 border-t-[#F59E0B] rounded-full animate-spin"></div>
    </div>

    <div v-else class="profile-grid">
        
        <!-- Sidebar: User Snapshot -->
        <div class="lg:col-span-4 space-y-6">
            <div class="profile-card user-snapshot animate-slide-up" style="animation-delay: 0.1s;">
                <div class="flex flex-col items-center">
                    <!-- Avatar Area -->
                    <div class="relative mb-6">
                        <div class="avatar-wrapper shadow-xl">
                            <img v-if="profile.avatar_url" :src="profile.avatar_url" class="w-full h-full object-cover" />
                            <UserIcon v-else class="w-12 h-12 text-[#D1D5DB]" />
                            <!-- Loading Overlay -->
                            <div v-if="isUploadingAvatar" class="absolute inset-0 bg-white/80 flex items-center justify-center">
                                <svg class="animate-spin h-6 w-6 text-[#F59E0B]" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
                            </div>
                        </div>
                        <button 
                            @click="triggerAvatarUpload"
                            class="avatar-upload-btn"
                        >
                            <CameraIcon class="w-4 h-4" />
                        </button>
                    </div>
                    
                    <h2 class="text-xl font-bold text-[#111827] mb-1 tracking-tight">{{ profile.full_name || t('profile.candidate_fallback') }}</h2>
                    <p class="text-[#6B7280] text-sm mb-4 font-medium">{{ profile.email }}</p>

                    <!-- Profile Badge -->
                    <div class="mb-6">
                        <span v-if="profile.subscription_tier === 'ADMIN'" class="badge badge-admin">{{ t('profile.badge_admin') }}</span>
                        <span v-else-if="profile.subscription_tier === 'PRO'" class="badge badge-pro">{{ t('profile.badge_pro') }}</span>
                        <span v-else-if="profile.subscription_tier === 'ESSENTIAL'" class="badge badge-essential">{{ t('profile.badge_essential') }}</span>
                        <span v-else class="badge badge-free">{{ t('profile.badge_free') }}</span>
                    </div>
                    
                    <div class="w-full space-y-4 pt-6 border-t border-[#F3F4F6]">
                        <div class="info-row">
                            <div class="status-dot" :class="profile.cv_text ? 'bg-emerald-500 shadow-emerald' : 'bg-gray-300'"></div>
                            <span class="text-sm font-medium text-[#4B5563]">{{ profile.cv_text ? t('profile.cv_loaded') : t('profile.cv_empty') }}</span>
                        </div>
                        <div class="info-row">
                            <LinkIcon class="w-4 h-4" :class="profile.portfolio_url ? 'text-[#F59E0B]' : 'text-gray-300'" />
                            <span class="text-sm font-medium text-[#4B5563]">{{ profile.portfolio_url ? t('profile.portfolio_linked') : t('profile.portfolio_none') }}</span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Readiness HUD -->
            <div class="profile-card animate-slide-up" style="animation-delay: 0.2s;">
                <div class="flex items-center gap-3 mb-6">
                    <SparklesIcon class="w-5 h-5 text-[#F59E0B]" />
                    <h3 class="font-bold text-[#111827] text-[11px] uppercase tracking-[0.2em]">{{ t('profile.readiness') }}</h3>
                </div>
                <div class="space-y-4">
                    <div class="flex justify-between text-[11px] font-bold mb-1">
                        <span class="text-[#9CA3AF]">OPTIMISATION ALPHA</span>
                        <span class="text-[#F59E0B]">88%</span>
                    </div>
                    <div class="progress-track">
                        <div class="progress-fill" style="width: 88%"></div>
                    </div>
                </div>
            </div>

            <!-- Admin Console Short -->
            <div v-if="profile.subscription_tier === 'ADMIN'" class="profile-card admin-mini animate-slide-up" style="animation-delay: 0.3s;">
                <div class="flex items-center gap-3 mb-4">
                    <ShieldCheckIcon class="w-5 h-5 text-rose-500" />
                    <h3 class="text-sm font-bold text-[#111827]">{{ t('profile.admin_panel_title') }}</h3>
                </div>
                <div class="space-y-3">
                    <p class="text-xs text-[#6B7280] leading-relaxed">{{ t('profile.admin_promote_desc') }}</p>
                    <div class="flex flex-col gap-2">
                        <input 
                            v-model="adminEmailToPromote" 
                            type="email" 
                            placeholder="email@exemple.com"
                            class="input-clean text-xs"
                        />
                        <button 
                            @click="promoteUser"
                            :disabled="isPromoting"
                            class="btn-gold text-xs py-2 w-full justify-center"
                        >
                            {{ isPromoting ? '...' : t('profile.promote_btn') }}
                        </button>
                    </div>
                </div>
            </div>
        </div>

        <!-- Main Column -->
        <div class="lg:col-span-8 space-y-8">
            
            <!-- Personal Details -->
            <div class="profile-card animate-slide-up" style="animation-delay: 0.2s;">
                <div class="flex items-center gap-3 mb-8">
                    <PencilSquareIcon class="w-5 h-5 text-[#F59E0B]" />
                    <h3 class="text-xl font-bold text-[#111827] tracking-tight">{{ t('profile.personal_details') }}</h3>
                </div>
                
                <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
                    <div class="form-group">
                        <label>{{ t('profile.full_name_label') }}</label>
                        <input v-model="profile.full_name" type="text" placeholder="John Doe" class="input-clean" />
                    </div>
                    <div class="form-group">
                        <label>{{ t('profile.portfolio_label') }}</label>
                        <input v-model="profile.portfolio_url" type="text" placeholder="https://linkedin.com/in/..." class="input-clean" />
                    </div>
                    <div class="md:col-span-2 form-group">
                        <label>{{ t('profile.bio_label') }}</label>
                        <textarea v-model="profile.bio" rows="3" :placeholder="t('profile.bio_placeholder')" class="input-clean resize-none"></textarea>
                    </div>
                </div>
            </div>

            <!-- CV Management -->
            <div class="profile-card animate-slide-up" style="animation-delay: 0.3s;">
                <div class="flex items-center justify-between mb-8">
                    <div class="flex items-center gap-3">
                        <DocumentTextIcon class="w-5 h-5 text-[#111827]" />
                        <h3 class="text-xl font-bold text-[#111827] tracking-tight">{{ t('profile.cv_section_title') }}</h3>
                    </div>
                    
                    <button 
                        @click="triggerCvUpload"
                        :disabled="isUploadingCv"
                        class="btn-secondary"
                    >
                        <CloudArrowUpIcon v-if="!isUploadingCv" class="w-4 h-4" />
                        <svg v-else class="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
                        {{ t('profile.cv_extract_btn') }}
                    </button>
                </div>
                
                <p class="text-sm text-[#6B7280] mb-6 font-medium leading-relaxed">{{ t('profile.cv_desc') }}</p>
                
                <div class="relative group">
                    <textarea 
                        v-model="profile.cv_text"
                        rows="12" 
                        class="cv-textarea"
                        :placeholder="t('profile.cv_placeholder')"
                    ></textarea>
                    <div class="cv-hud-line">
                        RAW_DATA_V2 // CV_STORAGE
                    </div>
                </div>
            </div>
            
            <!-- Portfolio Section -->
            <div class="profile-card animate-slide-up" style="animation-delay: 0.4s;">
                <div class="flex items-center gap-3 mb-8">
                    <BriefcaseIcon class="w-5 h-5 text-[#111827]" />
                    <h3 class="text-xl font-bold text-[#111827] tracking-tight">{{ t('profile.portfolio_section_title') }}</h3>
                </div>

                <div v-if="profile.last_portfolio" class="space-y-6">
                    <div class="portfolio-item">
                        <div class="flex items-center gap-4">
                            <div class="icon-box">
                                <DocumentTextIcon class="w-6 h-6 text-[#F59E0B]" />
                            </div>
                            <div>
                                <h4 class="font-bold text-[#111827] text-sm">{{ t('profile.portfolio_project') }}</h4>
                                <p class="text-xs text-[#6B7280]">{{ t('profile.portfolio_ready') }}</p>
                            </div>
                        </div>
                        <div class="flex items-center gap-3">
                            <button disabled class="btn-disabled">
                                {{ t('profile.portfolio_edit_soon') }}
                            </button>
                            <button @click="downloadZip" class="btn-secondary px-4">
                                ZIP
                            </button>
                        </div>
                    </div>
                    <div class="analysis-box">
                        Analyse IA : {{ profile.last_portfolio.personality_analysis }}
                    </div>
                </div>

                <div v-else class="portfolio-empty">
                    <p class="text-[#6B7280] text-sm mb-4">{{ t('profile.portfolio_empty') }}</p>
                    <button disabled class="btn-disabled px-8 py-2.5">
                        {{ t('profile.portfolio_coming_soon') }}
                    </button>
                </div>
            </div>

            <!-- Mobile Only Save Button -->
            <div class="md:hidden pt-4 pb-20">
                <button 
                    @click="saveProfile"
                    :disabled="isSaving"
                    class="btn-gold w-full py-4 text-base shadow-xl"
                >
                    {{ t('profile.save_btn') }}
                </button>
            </div>
        </div>
    </div>
  </div>
</template>

<style scoped>
.profile-root {
    padding: 2rem;
    max-width: 1200px;
    margin: 0 auto;
    background-color: #F9FAFB;
    min-height: 100vh;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
}

.profile-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 3rem;
    padding-top: 1rem;
}

.profile-grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 2rem;
    padding-bottom: 5rem;
}
@media (min-width: 1024px) {
    .profile-grid { grid-template-columns: repeat(12, 1fr); }
}

.profile-card {
    background: #FFFFFF;
    border: 1px solid #F3F4F6;
    border-radius: 1.5rem;
    padding: 2rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.02), 0 4px 6px -1px rgba(0,0,0,0.01);
}

.user-snapshot {
    text-align: center;
}

.avatar-wrapper {
    width: 7rem;
    height: 7rem;
    border-radius: 2rem;
    background-color: #F9FAFB;
    border: 4px solid #FFFFFF;
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;
    margin: 0 auto;
    transition: transform 0.3s ease;
}
.avatar-wrapper:hover { transform: scale(1.02); }

.avatar-upload-btn {
    position: absolute;
    bottom: -0.5rem;
    right: -0.5rem;
    padding: 0.6rem;
    background-color: #F59E0B;
    color: white;
    border-radius: 1rem;
    border: 3px solid #FFFFFF;
    box-shadow: 0 4px 10px rgba(232, 93, 62, 0.2);
    transition: all 0.2s;
}
.avatar-upload-btn:hover { transform: scale(1.1); background-color: #d14d31; }

.badge {
    font-size: 10px;
    font-weight: 800;
    text-transform: uppercase;
    padding: 0.25rem 0.75rem;
    border-radius: 9999px;
    letter-spacing: 0.05em;
}
.badge-admin { background: #FEF2F2; color: #EF4444; border: 1px solid #FEE2E2; }
.badge-pro { background: #EEF2FF; color: #4F46E5; border: 1px solid #E0E7FF; }
.badge-essential { background: #FFFBEB; color: #D97706; border: 1px solid #FEF3C7; }
.badge-free { background: #F9FAFB; color: #6B7280; border: 1px solid #F3F4F6; }

.info-row {
    display: flex;
    align-items: center;
    gap: 0.75rem;
}

.status-dot {
    width: 0.5rem;
    height: 0.5rem;
    border-radius: 9999px;
}
.shadow-emerald { box-shadow: 0 0 8px rgba(16, 185, 129, 0.4); }

.progress-track {
    height: 0.4rem;
    width: 100%;
    background-color: #F3F4F6;
    border-radius: 9999px;
    overflow: hidden;
}

.progress-fill {
    height: 100%;
    background-color: #F59E0B;
    border-radius: 9999px;
    transition: width 1s cubic-bezier(0.16, 1, 0.3, 1);
}

.btn-gold {
    background-color: #F59E0B;
    color: white;
    padding: 0.75rem 1.5rem;
    border-radius: 1rem;
    font-size: 0.875rem;
    font-weight: 700;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    transition: all 0.2s;
    border: none;
    cursor: pointer;
}
.btn-gold:hover { opacity: 0.9; transform: translateY(-1px); }
.btn-gold:active { transform: translateY(0); }
.btn-gold:disabled { opacity: 0.5; cursor: not-allowed; }

.btn-secondary {
    background-color: #FFFFFF;
    border: 1px solid #E5E7EB;
    color: #4B5563;
    padding: 0.5rem 1rem;
    border-radius: 0.75rem;
    font-size: 0.75rem;
    font-weight: 700;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    transition: all 0.2s;
    cursor: pointer;
}
.btn-secondary:hover { background-color: #F9FAFB; border-color: #D1D5DB; }

.btn-icon-white {
    width: 2.75rem;
    height: 2.75rem;
    background: white;
    border: 1px solid #E5E7EB;
    border-radius: 1rem;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #6B7280;
    transition: all 0.2s;
}
.btn-icon-white:hover { color: #111827; border-color: #D1D5DB; transform: translateX(-2px); }

.btn-admin {
    background-color: #FEF2F2;
    color: #EF4444;
    border: 1px solid #FEE2E2;
    padding: 0.75rem 1.25rem;
    border-radius: 1rem;
    font-size: 0.75rem;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    transition: all 0.2s;
}
.btn-admin:hover { background-color: #FEE2E2; }

.input-clean {
    width: 100%;
    background-color: #F9FAFB;
    border: 1px solid #F3F4F6;
    border-radius: 1rem;
    padding: 1rem 1.25rem;
    color: #111827;
    font-weight: 500;
    font-size: 0.9rem;
    transition: all 0.2s;
}
.input-clean:focus {
    outline: none;
    border-color: #F59E0B;
    background-color: #FFFFFF;
    box-shadow: 0 0 0 4px rgba(232, 93, 62, 0.05);
}
.input-clean::placeholder { color: #D1D5DB; }

.form-group label {
    display: block;
    font-size: 11px;
    font-weight: 800;
    color: #9CA3AF;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 0.75rem;
    margin-left: 0.25rem;
}

.cv-textarea {
    width: 100%;
    background-color: #F9FAFB;
    border: 1px solid #F3F4F6;
    border-radius: 1.5rem;
    padding: 1.5rem;
    color: #374151;
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
    font-size: 13px;
    line-height: 1.6;
    transition: all 0.2s;
}
.cv-textarea:focus {
    outline: none;
    border-color: #F59E0B;
    background-color: #FFFFFF;
}

.cv-hud-line {
    position: absolute;
    bottom: 1rem;
    right: 1.5rem;
    font-family: monospace;
    font-size: 9px;
    color: #D1D5DB;
    pointer-events: none;
}

.portfolio-item {
    padding: 1.5rem;
    background-color: #F9FAFB;
    border: 1px solid #F3F4F6;
    border-radius: 1.25rem;
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
}
@media (min-width: 768px) {
    .portfolio-item { flex-direction: row; align-items: center; justify-content: space-between; }
}

.icon-box {
    width: 3rem;
    height: 3rem;
    background-color: #FFFFFF;
    border-radius: 1rem;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 2px 4px rgba(0,0,0,0.02);
}

.btn-disabled {
    padding: 0.6rem 1rem;
    background-color: #F3F4F6;
    color: #9CA3AF;
    border-radius: 0.75rem;
    font-size: 0.75rem;
    font-weight: 700;
    cursor: not-allowed;
}

.analysis-box {
    padding: 1rem;
    background-color: #F9FAFB;
    border: 1px solid #F3F4F6;
    border-radius: 1rem;
    font-size: 11px;
    font-style: italic;
    color: #6B7280;
}

.portfolio-empty {
    text-align: center;
    padding: 3rem 0;
    border: 2px dashed #F3F4F6;
    border-radius: 1.5rem;
    background-color: #F9FAFB/30;
}

@keyframes slideUpFade {
    0% { opacity: 0; transform: translateY(20px); }
    100% { opacity: 1; transform: translateY(0); }
}
.animate-slide-up {
    animation: slideUpFade 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    opacity: 0;
}

.admin-mini {
    border: 1px solid #FEE2E2;
}
</style>
