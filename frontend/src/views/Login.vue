<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const email = ref('')
const password = ref('')
const errorMsg = ref('')
const isLoading = ref(false)

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
      // Redirect to dashboard
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
  <div class="min-h-screen flex items-center justify-center relative overflow-hidden bg-surface-950">
    <!-- Ambient glowing abstract background -->
    <div class="absolute inset-0 z-0">
      <div class="absolute top-1/4 left-1/4 w-96 h-96 bg-indigo-500/20 rounded-full blur-[120px]"></div>
      <div class="absolute bottom-1/4 right-1/4 w-96 h-96 bg-gold-500/10 rounded-full blur-[120px]"></div>
    </div>

    <div class="w-full max-w-md p-8 relative z-10">
      <div class="text-center mb-10">
        <div class="inline-flex items-center justify-center w-24 h-24 rounded-3xl bg-surface-900 shadow-2xl border border-surface-800 mb-8 overflow-hidden">
          <img src="/logo.png" alt="GoldArmy Logo" class="w-full h-full object-cover" />
        </div>
        <h1 class="text-3xl font-display font-bold text-white tracking-tight">Bienvenue sur GoldArmy</h1>
        <p class="text-slate-400 mt-2">Connectez-vous à votre espace personnel.</p>
      </div>

      <form @submit.prevent="handleLogin" class="space-y-5 bg-surface-900/50 backdrop-blur-xl border border-surface-800 p-8 rounded-3xl shadow-2xl">
        <div v-if="errorMsg" class="p-3 bg-rose-500/10 border border-rose-500/20 rounded-xl text-rose-400 text-sm font-medium text-center">
          {{ errorMsg }}
        </div>

        <div class="space-y-1">
          <label class="text-xs font-bold text-slate-400 uppercase tracking-wider ml-1">Email</label>
          <input 
            v-model="email" 
            type="email" 
            required 
            placeholder="vous@email.com"
            class="w-full bg-surface-950 border border-surface-800 rounded-xl px-4 py-3 text-slate-200 placeholder-slate-600 focus:outline-none focus:border-indigo-500/50 focus:ring-1 focus:ring-indigo-500/50 transition-all font-medium"
          />
        </div>

        <div class="space-y-1">
          <label class="text-xs font-bold text-slate-400 uppercase tracking-wider ml-1">Mot de passe</label>
          <input 
            v-model="password" 
            type="password" 
            required 
            placeholder="••••••••"
            class="w-full bg-surface-950 border border-surface-800 rounded-xl px-4 py-3 text-slate-200 placeholder-slate-600 focus:outline-none focus:border-indigo-500/50 focus:ring-1 focus:ring-indigo-500/50 transition-all font-medium"
          />
        </div>

        <button 
          type="submit" 
          :disabled="isLoading"
          class="w-full py-3.5 mt-2 bg-gradient-to-r from-indigo-500 to-indigo-600 hover:from-indigo-400 hover:to-indigo-500 text-white font-bold rounded-xl shadow-[0_0_20px_rgba(99,102,241,0.3)] transition-all flex items-center justify-center gap-2 disabled:opacity-50"
        >
          <span v-if="isLoading" class="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
          <span>{{ isLoading ? 'Connexion...' : 'Se connecter' }}</span>
        </button>

        <p class="text-center text-sm text-slate-500 font-medium mt-6">
          Pas encore de compte ? 
          <router-link to="/register" class="text-indigo-400 hover:text-indigo-300 transition-colors">Créer un compte</router-link>
        </p>
      </form>
    </div>
  </div>
</template>
