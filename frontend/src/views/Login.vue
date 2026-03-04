<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useHead } from '@unhead/vue'
import { ArrowLeftIcon } from '@heroicons/vue/24/outline'
import { useGoogleAuth } from '@/composables/useGoogleAuth'
import { safeJson } from '@/utils/auth'
import { getApiUrl } from '@/config'

const { t } = useI18n()
const router = useRouter()
const email = ref('')
const password = ref('')
const errorMsg = ref('')
const isLoading = ref(false)

useHead({
  title: computed(() => t('auth.login_title') + ' | GoldArmy'),
  meta: [
    { name: 'description', content: computed(() => t('auth.login_subtitle') || t('auth.login_title')) }
  ]
})

const { googleLoading, googleError, initGoogle, googleSignIn } = useGoogleAuth()
onMounted(() => initGoogle('google-btn-login'))

const handleLogin = async () => {
  errorMsg.value = ''
  isLoading.value = true
  try {
    const formData = new URLSearchParams()
    formData.append('username', email.value)
    formData.append('password', password.value)

    const res = await fetch(getApiUrl('/api/auth/login'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: formData
    })
    
    const data = await safeJson(res)
    if (!res.ok) {
      errorMsg.value = data?.detail || (t('common.error') + ': ' + t('auth.invalid_credentials'))
    } else if (!data) {
      errorMsg.value = t('common.error') + ': ' + t('auth.invalid_response')
    } else {
      localStorage.setItem('token', data.access_token)
      localStorage.setItem('user', JSON.stringify(data.user))
      router.push('/home')
    }
  } catch (err) {
    errorMsg.value = t('common.error') + ': Connexion au serveur.'
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen bg-[#1c1c24] flex items-center justify-center p-4 font-sans selection:bg-violet-500/30">
    <div class="w-full max-w-[1020px] h-[700px] bg-[#25252f] rounded-[3rem] overflow-hidden shadow-[0_50px_100px_-20px_rgba(0,0,0,0.6)] flex flex-col md:flex-row border border-white/[0.05]">
      
      <!-- Left Panel: Cinematic Visual -->
      <div class="relative w-full md:w-[48%] h-full overflow-hidden hidden md:block">
        <img src="/og-banner.png" alt="GoldArmy Visual" class="absolute inset-0 w-full h-full object-cover opacity-90 scale-110" />
        <div class="absolute inset-0 bg-gradient-to-t from-[#1c1c24] via-transparent to-black/20"></div>
        
        <!-- Navbar Overlay -->
        <div class="absolute top-10 left-10 right-10 flex justify-between items-center text-white">
          <div class="flex items-center gap-3">
            <div class="w-9 h-9 rounded-xl bg-surface-950 flex items-center justify-center border border-white/10 shadow-xl overflow-hidden">
                <img src="/logo.png" alt="Logo" class="w-full h-full object-cover" />
            </div>
            <span class="text-xl font-display font-bold tracking-tight">GoldArmy</span>
          </div>
          <router-link to="/" class="px-5 py-2.5 bg-white/10 hover:bg-white/20 backdrop-blur-xl rounded-full text-xs font-bold transition-all flex items-center gap-2 border border-white/10 ring-1 ring-white/5">
            {{ t('common.back_to_site') }} <ArrowLeftIcon class="w-3 h-3 rotate-180" />
          </router-link>
        </div>

        <!-- Bottom Text Section -->
        <div class="absolute bottom-16 left-12 right-12">
          <h2 class="text-3xl lg:text-4xl font-display font-bold text-white leading-[1.15] mb-6" v-html="t('auth.slogan')"></h2>
          <div class="flex gap-2.5">
            <div class="w-10 h-1.5 bg-white rounded-full"></div>
            <div class="w-10 h-1.5 bg-white/20 rounded-full"></div>
            <div class="w-10 h-1.5 bg-white/20 rounded-full"></div>
          </div>
        </div>
      </div>

      <!-- Right Panel: Elegant Form -->
      <div class="flex-1 flex flex-col justify-center px-10 sm:px-16 lg:px-24 py-12">
        <div class="mb-10 text-left">
          <h1 class="text-4xl font-display font-bold text-white mb-3">{{ t('auth.login_title') }}</h1>
          <p class="text-slate-400 font-medium text-sm">
            {{ t('auth.no_account') }} 
            <router-link to="/register" class="text-violet-400 hover:text-violet-300 font-bold transition-colors">{{ t('auth.register_link') }}</router-link>
          </p>
        </div>

        <div v-if="errorMsg" class="mb-8 p-4 bg-rose-500/10 border border-rose-500/20 rounded-2xl text-rose-400 text-xs font-bold text-center animate-pulse">
          {{ errorMsg }}
        </div>

        <form @submit.prevent="handleLogin" class="space-y-5">
          <div class="space-y-1.5">
            <input 
              v-model="email" 
              type="email" 
              required 
              :placeholder="t('auth.email_label')"
              class="w-full bg-[#1c1c24] border border-[#32323f] rounded-2xl px-5 py-3.5 text-white placeholder-slate-600 focus:outline-none focus:border-violet-500/50 focus:ring-1 focus:ring-violet-500/50 transition-all font-medium text-sm"
            />
          </div>

          <div class="space-y-1.5 relative group">
            <input 
              v-model="password" 
              type="password" 
              required 
              :placeholder="t('auth.password_label')"
              class="w-full bg-[#1c1c24] border border-[#32323f] rounded-2xl px-5 py-3.5 text-white placeholder-slate-600 focus:outline-none focus:border-violet-500/50 focus:ring-1 focus:ring-violet-500/50 transition-all font-medium pr-12 text-sm"
            />
             <button type="button" class="absolute right-4 top-1/2 -translate-y-1/2 text-slate-600 hover:text-slate-400 transition-colors p-2">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-4.5 h-4.5">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M2.036 12.322a1.012 1.012 0 010-.644m17.928.644a1.012 1.012 0 010-.644M11.999 4.021c2.757 0 5.337 1.077 7.218 3.033M11.999 4.021C9.242 4.021 6.662 5.098 4.781 7.054M4.781 7.054C3.212 8.682 2.148 10.741 1.701 13m15.517 7.054C15.658 21.099 13.6 22 11.999 22c-1.601 0-3.659-.901-5.219-2.946M11.999 4.021c.642 0 1.258.115 1.83.326v.001M11.999 4.021c-.642 0-1.258.115-1.83.326m13.43 14.28a1.011 1.011 0 11-1.332-1.521 15.694 15.694 0 00.32-2.175c0-.986-.184-1.93-.526-2.793M22.036 12.322a1.01 1.01 0 11-1.99.27m-4.529 7.462a15.7 15.7 0 01-3.518.411c-1.601 0-3.659-.901-5.219-2.946m11.237-7.228a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0z" />
                </svg>
            </button>
          </div>

          <div class="flex items-center justify-between pb-2">
            <label class="flex items-center gap-2.5 cursor-pointer group">
              <input type="checkbox" class="w-4.5 h-4.5 rounded border-[#32323f] bg-[#1c1c24] text-violet-500 focus:ring-violet-500/20 transition-all cursor-pointer" />
              <span class="text-xs font-bold text-slate-500 group-hover:text-slate-400 transition-colors uppercase tracking-widest">{{ t('auth.remember_me') }}</span>
            </label>
            <a href="#" class="text-xs font-bold text-violet-400 hover:text-violet-300 transition-colors uppercase tracking-widest">{{ t('auth.forgot_password') }}</a>
          </div>

          <button 
            type="submit" 
            :disabled="isLoading"
            class="w-full py-4 mt-2 bg-violet-600 hover:bg-violet-500 text-white font-bold rounded-2xl shadow-xl shadow-violet-600/10 active:scale-[0.98] transition-all flex items-center justify-center gap-3 disabled:opacity-50 h-[58px]"
          >
            <span v-if="isLoading" class="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
            <span class="text-sm uppercase tracking-widest">{{ isLoading ? t('common.loading') : t('auth.login_button') }}</span>
          </button>

          <div class="relative py-6">
            <div class="absolute inset-0 flex items-center"><div class="w-full border-t border-white/[0.05]"></div></div>
            <div class="relative flex justify-center text-[10px] uppercase tracking-[0.2em]"><span class="bg-[#25252f] px-4 font-black text-slate-600">{{ t('auth.or_connect_with') }}</span></div>
          </div>

          <div class="grid grid-cols-1 gap-4">
            <!-- Offical Google Button Container -->
            <div id="google-btn-login" class="flex justify-center"></div>
            
            <div class="grid grid-cols-2 gap-4">
              <button type="button" class="flex items-center justify-center gap-3 py-3 px-4 bg-transparent border border-[#32323f] rounded-2xl hover:bg-white/5 transition-all font-bold text-white text-[10px] uppercase tracking-widest opacity-50 cursor-not-allowed" title="Arrive bientôt">
                  <!-- Apple icon inline — no external CDN -->
                  <svg class="w-4 h-4 fill-white" viewBox="0 0 814 1000" xmlns="http://www.w3.org/2000/svg"><path d="M788.1 340.9c-5.8 4.5-108.2 62.2-108.2 190.5 0 148.4 130.3 200.9 134.2 202.2-.6 3.2-20.7 71.9-68.7 141.9-42.8 61.6-87.5 123.1-155.5 123.1s-85.5-39.5-164-39.5c-76 0-103.7 40.8-165.9 40.8s-105-57.8-155.5-127.4C46 376.2 0 293.8 0 213.5c0-84.1 53.4-128.5 106.1-128.5 77.5 0 98.1 49.7 167.5 49.7 67.9 0 103.2-50 167.5-50 59.7 0 121.4 37.8 160.6 109.8zM642 94.1c0 44.7-16.2 89.5-47.7 123.5-32.2 35.3-76.5 58.2-119.7 58.2-1.4 0-2.8 0-4.1-.1 1.2-43.8 19.1-86.2 48.9-118.7 31-33.1 77.3-55.7 119.8-56.9 1.5-.1 2.8-.1 2.8-.1z"/></svg>
                  Apple
              </button>
              <button type="button" class="flex items-center justify-center gap-3 py-3 px-4 bg-transparent border border-[#32323f] rounded-2xl hover:bg-white/5 transition-all font-bold text-white text-[10px] uppercase tracking-widest opacity-50 cursor-not-allowed" title="Arrive bientôt">
                  <!-- Meta/Facebook icon inline — no external CDN -->
                  <svg class="w-4 h-4" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z" fill="#1877F2"/></svg>
                  Meta
              </button>
            </div>
          </div>
          <p v-if="googleError" class="text-rose-400 text-xs font-bold text-center mt-2">{{ googleError }}</p>
        </form>
      </div>

    </div>
  </div>
</template>
