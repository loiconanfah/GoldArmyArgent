<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const email = ref('')
const password = ref('')
const errorMsg = ref('')
const isLoading = ref(false)

const handleRegister = async () => {
  errorMsg.value = ''
  isLoading.value = true
  try {
    const res = await fetch('http://localhost:8000/api/auth/register', {
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
      <div class="absolute top-1/4 right-1/4 w-96 h-96 bg-indigo-500/20 rounded-full blur-[120px]"></div>
      <div class="absolute bottom-1/4 left-1/4 w-96 h-96 bg-emerald-500/10 rounded-full blur-[120px]"></div>
    </div>

    <div class="w-full max-w-md p-8 relative z-10">
      <div class="text-center mb-10">
        <div class="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-gold-400 to-amber-600 shadow-lg shadow-gold-500/20 mb-6">
          <span class="text-3xl leading-none" role="img" aria-label="helmet">🪖</span>
        </div>
        <h1 class="text-3xl font-display font-bold text-white tracking-tight">Créer un compte</h1>
        <p class="text-slate-400 mt-2">Rejoignez GoldArmy et accélérez votre carrière.</p>
      </div>

      <form @submit.prevent="handleRegister" class="space-y-5 bg-surface-900/50 backdrop-blur-xl border border-surface-800 p-8 rounded-3xl shadow-2xl">
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
          class="w-full py-3.5 mt-2 bg-gradient-to-r from-emerald-500 to-emerald-600 hover:from-emerald-400 hover:to-emerald-500 text-white font-bold rounded-xl shadow-[0_0_20px_rgba(16,185,129,0.3)] transition-all flex items-center justify-center gap-2 disabled:opacity-50"
        >
          <span v-if="isLoading" class="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
          <span>{{ isLoading ? 'Création...' : 'S\'inscrire' }}</span>
        </button>

        <p class="text-center text-sm text-slate-500 font-medium mt-6">
          Déjà un compte ? 
          <router-link to="/login" class="text-emerald-400 hover:text-emerald-300 transition-colors">Se connecter</router-link>
        </p>
      </form>
    </div>
  </div>
</template>
