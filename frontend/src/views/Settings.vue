<script setup>
import { ArrowLeftIcon } from '@heroicons/vue/24/outline'
import { useRouter } from 'vue-router'

const router = useRouter()
const goBack = () => router.push('/dashboard')
</script>

<template>
  <div class="p-8 max-w-4xl mx-auto">
    <div class="flex items-center gap-4 border-b border-surface-800 pb-6 mb-8 mt-6">
        <button @click="goBack" class="p-2 bg-surface-800 hover:bg-surface-700 rounded-full text-slate-400 hover:text-white transition-colors">
            <ArrowLeftIcon class="w-5 h-5" />
        </button>
        <div>
            <h1 class="text-3xl font-display font-bold text-white tracking-tight">Paramètres</h1>
            <p class="text-slate-400 mt-1">Gérez vos préférences et votre profil.</p>
        </div>
    </div>
    
    <div class="bg-surface-900 border border-surface-800 rounded-2xl p-8 flex flex-col items-center justify-center min-h-[400px] text-center">
        <div class="w-16 h-16 bg-indigo-500/10 rounded-full flex items-center justify-center mb-4">
            <span class="text-2xl">⚙️</span>
        </div>
        <h2 class="text-xl font-bold text-white mb-2">Module en développement</h2>
        <p class="text-slate-400 max-w-md">Cette page sera bientôt disponible pour configurer vos préférences d'IA et vos informations personnelles.</p>
    </div>
  </div>
</template>
