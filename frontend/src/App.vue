<script setup>
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import {
  HomeIcon,
  ChatBubbleBottomCenterTextIcon,
  BriefcaseIcon,
  AcademicCapIcon,
  ChartBarIcon
} from '@heroicons/vue/24/outline'

const router = useRouter()
const route = useRoute()

const navigation = [
  { name: 'Dashboard', href: '/', icon: HomeIcon },
  { name: 'Agent Chat', href: '/chat', icon: ChatBubbleBottomCenterTextIcon },
  { name: 'Opportunités', href: '/opportunities', icon: BriefcaseIcon },
  { name: 'Mentor IA', href: '/mentor', icon: AcademicCapIcon },
  { name: 'CRM Candidatures', href: '/crm', icon: ChartBarIcon },
]

const currentRoute = computed(() => route.path)
</script>

<template>
  <div class="min-h-screen bg-slate-900 text-slate-200 flex">
    
    <!-- Sidebar -->
    <aside class="w-64 bg-slate-800 border-r border-slate-700 hidden md:flex flex-col">
      <!-- Logo -->
      <div class="h-16 flex items-center px-6 border-b border-slate-700">
        <span class="text-2xl mr-3" role="img" aria-label="helmet">🪖</span>
        <h1 class="text-lg font-extrabold bg-gradient-to-r from-amber-400 to-orange-500 bg-clip-text text-transparent tracking-tight">
          GoldArmy Agent
        </h1>
      </div>
      
      <!-- Nav Links -->
      <nav class="flex-1 px-4 py-6 space-y-2">
        <router-link
          v-for="item in navigation"
          :key="item.name"
          :to="item.href"
          :class="[
            item.href === currentRoute
              ? 'bg-amber-500/10 text-amber-500 border border-amber-500/20 shadow-sm'
              : 'text-slate-400 hover:bg-slate-700/50 hover:text-slate-200 border border-transparent',
            'group flex items-center px-3 py-2.5 text-sm font-medium rounded-xl transition-all duration-200 ease-in-out'
          ]"
        >
          <component 
            :is="item.icon" 
            :class="[
              item.href === currentRoute ? 'text-amber-500' : 'text-slate-500 group-hover:text-slate-300',
              'flex-shrink-0 -ml-1 mr-3 h-6 w-6 transition-colors duration-200'
            ]" 
            aria-hidden="true" 
          />
          {{ item.name }}
          <span v-if="item.name === 'Mentor IA'" class="ml-auto bg-gradient-to-r from-purple-500 to-indigo-500 text-white text-[10px] uppercase font-bold px-2 py-0.5 rounded-full">Pro</span>
        </router-link>
      </nav>

      <!-- User Profile mock -->
      <div class="p-4 border-t border-slate-700">
        <div class="flex items-center gap-3">
          <div class="h-10 w-10 rounded-full bg-gradient-to-tr from-amber-500 to-orange-400 flex items-center justify-center text-slate-900 font-bold">
            YD
          </div>
          <div>
            <p class="text-sm font-medium text-slate-200">Yves D.</p>
            <p class="text-xs text-slate-500">Étudiant IA</p>
          </div>
        </div>
      </div>
    </aside>

    <!-- Main Content Area -->
    <div class="flex-1 flex flex-col min-w-0 overflow-hidden">
      <!-- Mobile Header -->
      <header class="md:hidden bg-slate-800 h-16 border-b border-slate-700 flex items-center px-4 justify-between">
        <div class="flex items-center">
            <span class="text-2xl mr-2">🪖</span>
            <h1 class="font-bold text-amber-500">GoldArmy</h1>
        </div>
        <button class="text-slate-400 hover:text-white">
          <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path></svg>
        </button>
      </header>

      <!-- Routing View -->
      <main class="flex-1 overflow-y-auto w-full relative outline-none pb-12" tabindex="0">
        <!-- Route transitions -->
        <router-view v-slot="{ Component }">
          <transition 
            enter-active-class="transition duration-200 ease-out"
            enter-from-class="transform translate-y-4 opacity-0"
            enter-to-class="transform translate-y-0 opacity-100"
            leave-active-class="transition duration-150 ease-in"
            leave-from-class="transform translate-y-0 opacity-100"
            leave-to-class="transform -translate-y-4 opacity-0"
            mode="out-in"
          >
            <component :is="Component" />
          </transition>
        </router-view>
      </main>
    </div>
  </div>
</template>

<style>
/* Custom Scrollbar for the main app */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}
::-webkit-scrollbar-track {
  background: #0f172a; 
}
::-webkit-scrollbar-thumb {
  background: #334155; 
  border-radius: 4px;
}
::-webkit-scrollbar-thumb:hover {
  background: #475569; 
}
</style>
