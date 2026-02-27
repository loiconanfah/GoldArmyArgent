<script setup>
import { computed, ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { 
  HomeIcon, 
  MapIcon,
  ChatBubbleBottomCenterTextIcon, 
  UserGroupIcon, 
  BriefcaseIcon,
  Cog6ToothIcon,
  Bars3Icon,
  XMarkIcon,
  MagnifyingGlassIcon,
  BellIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
  MicrophoneIcon,
  UserIcon
} from '@heroicons/vue/24/outline'
import ToastPortal from './components/ToastPortal.vue'

const route = useRoute()
const router = useRouter()
const currentRoute = computed(() => route.path)
const isPublicRoute = computed(() => ['/', '/login', '/register'].includes(route.path))
const isImmersive = computed(() => route.path === '/interview')
const isMobileMenuOpen = ref(false)
const isSidebarCollapsed = ref(false)
const userEmail = ref('Yves D.')

const userTier = ref('FREE')

onMounted(async () => {
  const userStr = localStorage.getItem('user')
  if (userStr) {
    try {
      const user = JSON.parse(userStr)
      userEmail.value = user.email.split('@')[0]
      userTier.value = user.subscription_tier || 'FREE'
    } catch(e){}
  }

  // Refresh tier from API to be sure
  try {
    const res = await fetch('http://localhost:8000/api/profile', {
      headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
    })
    const json = await res.json()
    if (json.status === 'success') {
      userTier.value = json.data.subscription_tier || 'FREE'
    }
  } catch(e){}
})

const handleLogout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    router.push('/login')
}

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: HomeIcon, exact: false },
  { name: 'Sniper', href: '/opportunities', icon: MapIcon },
  { name: 'Mentor IA', href: '/mentor', icon: ChatBubbleBottomCenterTextIcon },
  { name: 'Entretien (Vocal)', href: '/interview', icon: MicrophoneIcon },
  { name: 'CRM Candidatures', href: '/crm', icon: BriefcaseIcon },
  { name: 'Réseau', href: '/network', icon: UserGroupIcon },
  { name: 'Mon Profil', href: '/profile', icon: UserIcon },
]
</script>

<template>
  <!-- Global Wrapper: Lock height and prevent window-level scroll -->
  <div class="h-screen w-screen overflow-hidden bg-surface-950 text-slate-200 flex font-sans selection:bg-gold-500/30 fixed inset-0">
    <!-- Mobile Menu Overlay -->
    <div v-show="isMobileMenuOpen && !isPublicRoute" class="fixed inset-0 bg-surface-950/80 backdrop-blur-sm z-40 md:hidden" @click="isMobileMenuOpen = false"></div>

    <!-- Sidebar (Left Col) -->
    <aside v-if="!isPublicRoute && !isImmersive" :class="[
      'fixed inset-y-0 left-0 bg-surface-900 border-r border-surface-800 flex flex-col z-50 transition-all duration-300 ease-in-out md:static',
      isMobileMenuOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0',
      isSidebarCollapsed ? 'w-20' : 'w-64'
    ]">
      <!-- Logo Section -->
      <div class="h-16 flex items-center justify-between px-4 border-b border-surface-800 shrink-0">
        <div class="flex items-center gap-3 overflow-hidden whitespace-nowrap">
            <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-gold-400 to-amber-600 flex shrink-0 items-center justify-center shadow-lg shadow-gold-500/20">
                <span class="text-sm leading-none" role="img" aria-label="helmet">🪖</span>
            </div>
            <h1 v-if="!isSidebarCollapsed" class="text-lg font-display font-bold text-white tracking-tight transition-opacity duration-300">
                GoldArmy
            </h1>
        </div>
        
        <div class="flex items-center">
            <!-- Toggle Sidebar Desktop -->
            <button @click="isSidebarCollapsed = !isSidebarCollapsed" class="hidden md:flex p-1.5 text-slate-500 hover:text-white rounded-lg hover:bg-surface-800 transition-colors">
                <ChevronRightIcon v-if="isSidebarCollapsed" class="w-5 h-5" />
                <ChevronLeftIcon v-else class="w-5 h-5" />
            </button>
            <!-- Close Mobile Menu -->
            <button @click="isMobileMenuOpen = false" class="md:hidden text-slate-400 hover:text-white">
                <XMarkIcon class="w-6 h-6" />
            </button>
        </div>
      </div>
      
      <!-- Nav Links -->
      <nav class="flex-1 px-3 py-8 space-y-2 overflow-y-auto overflow-x-hidden">
        <p v-if="!isSidebarCollapsed" class="px-3 text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-4 transition-opacity duration-300">Core</p>
        
        <router-link 
          v-for="item in navigation" 
          :key="item.name" 
          :to="item.href"
          class="flex items-center rounded-xl text-sm font-semibold transition-all group relative overflow-hidden"
          :class="[
             item.href === currentRoute || (item.href !== '/' && currentRoute.startsWith(item.href)) ? 'bg-indigo-500/10 text-indigo-400' : 'text-slate-400 hover:text-slate-200 hover:bg-surface-800',
             isSidebarCollapsed ? 'justify-center py-3 px-0' : 'gap-3 px-3 py-2.5'
          ]"
          :title="isSidebarCollapsed ? item.name : ''"
        >
          <!-- Active Indicator dot -->
          <div v-if="item.href === currentRoute || (item.href !== '/' && currentRoute.startsWith(item.href))" class="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-5 bg-indigo-500 rounded-r-full shadow-[0_0_10px_rgba(99,102,241,0.5)]"></div>
          
          <component :is="item.icon" class="w-5 h-5 shrink-0" :class="item.href === currentRoute || (item.href !== '/' && currentRoute.startsWith(item.href)) ? 'text-indigo-400' : 'text-slate-500 group-hover:text-slate-300'" />
          
          <span v-if="!isSidebarCollapsed" class="whitespace-nowrap transition-opacity duration-300">{{ item.name }}</span>
          
          <div v-if="item.name === 'Mentor IA' && !isSidebarCollapsed" class="ml-auto flex items-center justify-center">
             <span class="bg-gradient-to-r from-violet-500 to-indigo-500 text-white text-[9px] uppercase font-black px-1.5 py-0.5 rounded-full shadow-lg shadow-indigo-500/30">Pro</span>
          </div>
          <div v-if="item.name === 'Mentor IA' && isSidebarCollapsed" class="absolute top-1 right-1">
             <span class="w-2 h-2 rounded-full bg-violet-500 block"></span>
          </div>
        </router-link>
      </nav>

      <!-- Settings / Footer Nav -->
      <div class="p-3 border-t border-surface-800 shrink-0 overflow-hidden">
         <router-link 
          to="/settings"
          class="flex items-center rounded-xl text-sm font-semibold text-slate-400 hover:text-slate-200 hover:bg-surface-800 transition-all group"
          :class="isSidebarCollapsed ? 'justify-center py-3 px-0' : 'gap-3 px-3 py-2.5'"
          :title="isSidebarCollapsed ? 'Settings' : ''"
        >
          <Cog6ToothIcon class="w-5 h-5 shrink-0 text-slate-500 group-hover:text-slate-300" />
          <span v-if="!isSidebarCollapsed" class="whitespace-nowrap transition-opacity duration-300">Settings</span>
        </router-link>
      </div>
    </aside>

    <!-- Main Content Col -->
    <div class="flex-1 flex flex-col min-w-0 min-h-0 overflow-hidden relative w-full" :class="!isImmersive ? 'z-10' : 'z-[100]'">
      
      <!-- Topbar (Header) -->
      <header v-if="!isPublicRoute && !isImmersive" class="h-16 bg-surface-950 w-full border-b border-surface-800 flex items-center justify-between px-4 lg:px-8 relative z-20 shrink-0 gap-4">
        
        <!-- Left: Mobile Toggle & Page Title (Optional) -->
        <div class="flex items-center gap-4">
            <button @click="isMobileMenuOpen = true" class="md:hidden p-2 text-slate-400 hover:text-white rounded-lg hover:bg-surface-800">
                <Bars3Icon class="w-6 h-6" />
            </button>
            <div class="hidden md:flex items-center gap-3 w-64 lg:w-96">
                <!-- Search Input Topbar -->
                <div class="relative w-full group">
                    <MagnifyingGlassIcon class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500 group-focus-within:text-indigo-400 transition-colors" />
                    <input type="text" placeholder="Search anything (ex: CV, Job...)" class="w-full bg-surface-900 border border-surface-700/50 rounded-lg pl-9 pr-4 py-1.5 text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500/50 focus:ring-1 focus:ring-indigo-500/50 transition-all font-medium" />
                    <!-- Keyboard shortcut hint -->
                    <div class="absolute right-2 top-1/2 -translate-y-1/2 hidden lg:flex gap-1">
                        <kbd class="px-1.5 py-0.5 text-[10px] font-mono bg-surface-800 text-slate-400 rounded border border-surface-700">⌘</kbd>
                        <kbd class="px-1.5 py-0.5 text-[10px] font-mono bg-surface-800 text-slate-400 rounded border border-surface-700">K</kbd>
                    </div>
                </div>
            </div>
        </div>

        <!-- Right: Actions & User Profile -->
        <div class="flex items-center gap-3 sm:gap-5">
            <!-- Notifications -->
            <button class="relative p-2 text-slate-400 hover:text-white rounded-full hover:bg-surface-800 transition-colors">
                <BellIcon class="w-5 h-5" />
                <span class="absolute top-1.5 right-1.5 w-2 h-2 bg-rose-500 rounded-full border-2 border-surface-950"></span>
            </button>
            
            <div class="h-6 w-px bg-surface-800 hidden sm:block"></div>

            <!-- Enhanced User Profile Dropdown Trigger -->
            <button @click="handleLogout" title="Se déconnecter" class="flex items-center gap-3 p-1 pr-3 rounded-full hover:bg-surface-800 border border-transparent hover:border-surface-700 transition-all group">
                <div class="relative">
                    <div class="h-8 w-8 rounded-full bg-gradient-to-tr from-indigo-500 to-violet-400 flex items-center justify-center text-white font-bold text-xs ring-2 ring-surface-950 group-hover:ring-indigo-500/30 transition-all uppercase">
                        {{ userEmail.charAt(0) }}
                    </div>
                    <div class="absolute bottom-0 right-0 w-2.5 h-2.5 bg-rose-500 border-2 border-surface-950 rounded-full group-hover:bg-rose-400"></div>
                </div>
                <div class="hidden md:block text-left">
                    <div class="flex items-center gap-2 mb-0.5">
                        <p class="text-[13px] font-bold text-white leading-none group-hover:text-gold-400 transition-colors">{{ userEmail }}</p>
                        <!-- Badge Forfait -->
                        <span v-if="userTier === 'PRO'" class="bg-gradient-to-r from-violet-500 to-indigo-500 text-white text-[8px] uppercase font-black px-1.5 py-0.5 rounded-md shadow-lg shadow-indigo-500/20">PRO</span>
                        <span v-else-if="userTier === 'ESSENTIAL'" class="bg-gradient-to-r from-amber-400 to-gold-500 text-surface-950 text-[8px] uppercase font-black px-1.5 py-0.5 rounded-md shadow-lg shadow-gold-500/20">ESSENTIEL</span>
                        <span v-else class="bg-surface-700 text-slate-300 text-[8px] uppercase font-black px-1.5 py-0.5 rounded-md">GRATUIT</span>
                    </div>
                    <p class="text-[10px] font-semibold text-slate-500 uppercase tracking-wider leading-none">Déconnexion</p>
                </div>
            </button>
        </div>
      </header>

      <!-- Main Content Routing Area -->
      <main class="flex-1 overflow-y-auto w-full relative outline-none bg-surface-950" tabindex="0">
        <!-- Optional: Background ambient glow for the whole app -->
        <div class="absolute top-0 right-0 w-[800px] h-[600px] bg-indigo-500/5 rounded-full blur-[120px] pointer-events-none mix-blend-screen"></div>
        
        <div class="w-full min-h-full">
            <router-view />
        </div>
      </main>
      <ToastPortal />
    </div>
  </div>
</template>

<style>
/* Global Modern Reset & Scrollbar */
html {
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* Global Scrollbar SaaS Style */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}
::-webkit-scrollbar-track {
  background: transparent;
}
::-webkit-scrollbar-thumb {
  background: #334155; 
  border-radius: 4px;
}
::-webkit-scrollbar-thumb:hover {
  background: #475569; 
}
</style>
