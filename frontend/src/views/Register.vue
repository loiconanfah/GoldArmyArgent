<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowLeftIcon } from '@heroicons/vue/24/outline'
import { useGoogleAuth } from '@/composables/useGoogleAuth'
import { getApiUrl } from '@/config'

const router = useRouter()
const email = ref('')
const password = ref('')
const errorMsg = ref('')
const isLoading = ref(false)

const { googleLoading, googleError, initGoogle, googleSignIn } = useGoogleAuth()
onMounted(() => initGoogle('google-btn-register'))

const handleRegister = async () => {
  errorMsg.value = ''
  isLoading.value = true
  try {
    const res = await fetch(getApiUrl('/api/auth/register'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email: email.value,
        password: password.value
      })
    })
    
    const data = await res.json()
    if (!res.ok) {
      errorMsg.value = data.detail || 'Erreur lors de l\'inscription'
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
      
      <!-- Right Panel: Cinematic Visual (Flipped for symmetry) -->
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
          <h2 class="text-3xl lg:text-4xl font-display font-bold text-white leading-[1.15] mb-6">Join the Elite,<br/>Redefine Your Career.</h2>
          <div class="flex gap-2.5">
            <div class="w-10 h-1.5 bg-white/20 rounded-full"></div>
            <div class="w-10 h-1.5 bg-white rounded-full"></div>
            <div class="w-10 h-1.5 bg-white/20 rounded-full"></div>
          </div>
        </div>
      </div>

      <!-- Left Panel: Elegant Form -->
      <div class="flex-1 flex flex-col justify-center px-10 sm:px-16 lg:px-24 py-12">
        <div class="mb-10 text-left">
          <h1 class="text-4xl font-display font-bold text-white mb-3">Create account</h1>
          <p class="text-slate-400 font-medium text-sm">
            Already have an account? 
            <router-link to="/login" class="text-violet-400 hover:text-violet-300 font-bold transition-colors">Log in</router-link>
          </p>
        </div>

        <div v-if="errorMsg" class="mb-8 p-4 bg-rose-500/10 border border-rose-500/20 rounded-2xl text-rose-400 text-xs font-bold text-center animate-pulse">
          {{ errorMsg }}
        </div>

        <form @submit.prevent="handleRegister" class="space-y-4">
          <div class="grid grid-cols-2 gap-3">
             <input 
              type="text" 
              placeholder="First Name"
              class="w-full bg-[#1c1c24] border border-[#32323f] rounded-2xl px-5 py-3.5 text-white placeholder-slate-600 focus:outline-none focus:border-violet-500/50 focus:ring-1 focus:ring-violet-500/50 transition-all font-medium text-sm"
            />
            <input 
              type="text" 
              placeholder="Last Name"
              class="w-full bg-[#1c1c24] border border-[#32323f] rounded-2xl px-5 py-3.5 text-white placeholder-slate-600 focus:outline-none focus:border-violet-500/50 focus:ring-1 focus:ring-violet-500/50 transition-all font-medium text-sm"
            />
          </div>

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
             <button type="button" class="absolute right-4 top-1/2 -translate-y-1/2 text-slate-600 hover:text-slate-400 transition-colors p-2 text-sm uppercase font-bold tracking-widest">
                Show
            </button>
          </div>

          <div class="flex items-start gap-3 pb-2 pt-1">
              <input type="checkbox" required class="mt-1 w-4.5 h-4.5 rounded border-[#32323f] bg-[#1c1c24] text-violet-500 focus:ring-violet-500/20 transition-all cursor-pointer" />
              <span class="text-[11px] font-bold text-slate-500 leading-tight uppercase tracking-wider">I agree to the <a href="#" class="text-violet-400 hover:text-violet-300">Terms & Conditions</a> and <a href="#" class="text-violet-400 hover:text-violet-300">Privacy Policy</a></span>
          </div>

          <button 
            type="submit" 
            :disabled="isLoading"
            class="w-full py-4 mt-2 bg-violet-600 hover:bg-violet-500 text-white font-bold rounded-2xl shadow-xl shadow-violet-600/10 active:scale-[0.98] transition-all flex items-center justify-center gap-3 disabled:opacity-50 h-[58px]"
          >
            <span v-if="isLoading" class="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
            <span class="text-sm uppercase tracking-widest">{{ isLoading ? 'Creating...' : 'Create Account' }}</span>
          </button>

          <div class="relative py-6">
            <div class="absolute inset-0 flex items-center"><div class="w-full border-t border-white/[0.05]"></div></div>
            <div class="relative flex justify-center text-[10px] uppercase tracking-[0.2em]"><span class="bg-[#25252f] px-4 font-black text-slate-600">Or register with</span></div>
          </div>

          <div class="grid grid-cols-1 gap-4">
            <!-- Offical Google Button Container -->
            <div id="google-btn-register" class="flex justify-center"></div>
            
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
