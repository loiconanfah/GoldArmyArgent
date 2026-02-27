<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowLeftIcon } from '@heroicons/vue/24/outline'
import { useGoogleAuth } from '@/composables/useGoogleAuth'

const router = useRouter()
const email = ref('')
const password = ref('')
const errorMsg = ref('')
const isLoading = ref(false)

const { googleLoading, googleError, initGoogle, googleSignIn } = useGoogleAuth()
onMounted(() => initGoogle('google-btn-login'))

const handleLogin = async () => {
  errorMsg.value = ''
  isLoading.value = true
  try {
    const formData = new URLSearchParams()
    formData.append('username', email.value)
    formData.append('password', password.value)

    const res = await fetch('http://localhost:8000/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: formData
    })
    
    const data = await res.json()
    if (!res.ok) {
      errorMsg.value = data.detail || 'Identifiants incorrects'
    } else {
      localStorage.setItem('token', data.access_token)
      localStorage.setItem('user', JSON.stringify(data.user))
      router.push('/')
    }
  } catch (err) {
    errorMsg.value = 'Erreur de connexion au serveur.'
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
            Back to website <ArrowLeftIcon class="w-3 h-3 rotate-180" />
          </router-link>
        </div>

        <!-- Bottom Text Section -->
        <div class="absolute bottom-16 left-12 right-12">
          <h2 class="text-3xl lg:text-4xl font-display font-bold text-white leading-[1.15] mb-6">Master Your Career,<br/>Reach Your Potential.</h2>
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
          <h1 class="text-4xl font-display font-bold text-white mb-3">Welcome back</h1>
          <p class="text-slate-400 font-medium text-sm">
            Don't have an account? 
            <router-link to="/register" class="text-violet-400 hover:text-violet-300 font-bold transition-colors">Sign up</router-link>
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
              placeholder="Email address"
              class="w-full bg-[#1c1c24] border border-[#32323f] rounded-2xl px-5 py-3.5 text-white placeholder-slate-600 focus:outline-none focus:border-violet-500/50 focus:ring-1 focus:ring-violet-500/50 transition-all font-medium text-sm"
            />
          </div>

          <div class="space-y-1.5 relative group">
            <input 
              v-model="password" 
              type="password" 
              required 
              placeholder="Password"
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
              <span class="text-xs font-bold text-slate-500 group-hover:text-slate-400 transition-colors uppercase tracking-widest">Remember me</span>
            </label>
            <a href="#" class="text-xs font-bold text-violet-400 hover:text-violet-300 transition-colors uppercase tracking-widest">Forgot password?</a>
          </div>

          <button 
            type="submit" 
            :disabled="isLoading"
            class="w-full py-4 mt-2 bg-violet-600 hover:bg-violet-500 text-white font-bold rounded-2xl shadow-xl shadow-violet-600/10 active:scale-[0.98] transition-all flex items-center justify-center gap-3 disabled:opacity-50 h-[58px]"
          >
            <span v-if="isLoading" class="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
            <span class="text-sm uppercase tracking-widest">{{ isLoading ? 'Processing...' : 'Log in' }}</span>
          </button>

          <div class="relative py-6">
            <div class="absolute inset-0 flex items-center"><div class="w-full border-t border-white/[0.05]"></div></div>
            <div class="relative flex justify-center text-[10px] uppercase tracking-[0.2em]"><span class="bg-[#25252f] px-4 font-black text-slate-600">Or connected with</span></div>
          </div>

          <div class="grid grid-cols-1 gap-4">
            <!-- Offical Google Button Container -->
            <div id="google-btn-login" class="flex justify-center"></div>
            
            <div class="grid grid-cols-2 gap-4">
              <button type="button" class="flex items-center justify-center gap-3 py-3 px-4 bg-transparent border border-[#32323f] rounded-2xl hover:bg-white/5 transition-all font-bold text-white text-[10px] uppercase tracking-widest opacity-50 cursor-not-allowed" title="Arrive bientôt">
                  <img src="https://www.svgrepo.com/show/442887/apple-black.svg" class="w-4 h-4 invert" />
                  Apple
              </button>
              <button type="button" class="flex items-center justify-center gap-3 py-3 px-4 bg-transparent border border-[#32323f] rounded-2xl hover:bg-white/5 transition-all font-bold text-white text-[10px] uppercase tracking-widest opacity-50 cursor-not-allowed" title="Arrive bientôt">
                  <img src="https://www.svgrepo.com/show/442938/facebook-color.svg" class="w-4 h-4" />
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
