<script setup>
import { computed, ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { authFetch } from './utils/auth'
import Clarity from '@microsoft/clarity'
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
  UserIcon,
  SparklesIcon,
  ShieldCheckIcon,
  SunIcon,
  MoonIcon
} from '@heroicons/vue/24/outline'
import { useTheme } from './composables/useTheme'
import ToastPortal from './components/ToastPortal.vue'

const route = useRoute()
const router = useRouter()
const currentRoute = computed(() => route.path)
const isPublicRoute = computed(() => {
  return ['/', '/login', '/register', '/blog', '/free-cv-roast', '/free-interview', '/support', '/privacy'].includes(route.path) || route.path.startsWith('/blog/')
})
const isImmersive = computed(() => route.path === '/interview')
const isMobileMenuOpen = ref(false)
const isSidebarCollapsed = ref(false)

const { t, locale } = useI18n()
const { theme, toggleTheme } = useTheme()

const toggleLanguage = () => {
  const nextLocale = locale.value === 'fr' ? 'en' : 'fr'
  locale.value = nextLocale
  localStorage.setItem('language', nextLocale)
}
const userEmail = ref('')
const userTier = ref('FREE')

onMounted(async () => {
  userEmail.value = t('common.loading')
  const userStr = localStorage.getItem('user')
  if (userStr) {
    try {
      const user = JSON.parse(userStr)
      userEmail.value = user.email.split('@')[0]
      userTier.value = user.subscription_tier || 'FREE'
    } catch(e){}
  }

  // Refresh tier from API to be sure if logged in
  if (localStorage.getItem('token')) {
    try {
      const res = await authFetch('/api/profile')
      const json = await res.json()
      if (json.status === 'success') {
        userTier.value = json.data.subscription_tier || 'FREE'
        userEmail.value = json.data.full_name || json.data.email.split('@')[0]
        
        // Identify user in Clarity
        Clarity.identify(json.data.id || json.data.email, undefined, undefined, json.data.full_name || json.data.email)
      }
    } catch(e){}
  }
})

watch(locale, (newLocale) => {
  document.documentElement.lang = newLocale
}, { immediate: true })

const handleLogout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    router.push('/login')
}

const navigation = computed(() => [
  { name: t('nav.home'), href: '/home', icon: SparklesIcon },
  { name: t('nav.dashboard'), href: '/dashboard', icon: HomeIcon, exact: false },
  { name: t('nav.sniper'), href: '/opportunities', icon: MapIcon },
  { name: t('nav.mentor'), href: '/mentor', icon: ChatBubbleBottomCenterTextIcon },
  { name: t('nav.interview'), href: '/interview', icon: MicrophoneIcon },
  { name: t('nav.crm'), href: '/crm', icon: BriefcaseIcon },
  { name: t('nav.network'), href: '/network', icon: UserGroupIcon },
  { name: t('nav.profile'), href: '/profile', icon: UserIcon },
])

// --- Notification Center ---
const notifications = ref([])
const isNotificationsOpen = ref(false)
const unreadCount = computed(() => notifications.value.filter(n => !n.is_read).length)

const fetchNotifications = async () => {
    if (!localStorage.getItem('token')) return
    try {
        const r = await authFetch('/api/notifications')
        const j = await r.json()
        if (Array.isArray(j)) {
            notifications.value = j
        }
    } catch (e) {
        console.warn('[Notifications] Fetch failed', e)
    }
}

const markAllAsRead = async () => {
    try {
        await authFetch('/api/notifications/read-all', { method: 'PUT' })
        notifications.value.forEach(n => n.is_read = true)
    } catch (e) {}
}

const toggleNotifications = () => {
    isNotificationsOpen.value = !isNotificationsOpen.value
    if (isNotificationsOpen.value) {
        // Optionnel: on marque tout comme lu quand on ouvre ?
    }
}

onMounted(() => {
    fetchNotifications()
    const timer = setInterval(fetchNotifications, 60000 * 5) // Toutes les 5 min
    return () => clearInterval(timer)
})
</script>

<template>
  <!-- Global Wrapper: Lock height and prevent window-level scroll -->
  <div class="h-screen w-screen overflow-hidden bg-surface-950 text-slate-900 flex font-sans selection:bg-violet-500/20 fixed inset-0">
    <!-- Mobile Menu Overlay -->
    <div v-show="isMobileMenuOpen && !isPublicRoute" class="fixed inset-0 bg-surface-950/80 backdrop-blur-sm z-40 md:hidden" @click="isMobileMenuOpen = false"></div>

    <!-- Sidebar (Left Col) -->
    <aside v-if="!isPublicRoute && !isImmersive" :class="[
      'fixed inset-y-0 left-0 bg-surface-900 border-r border-surface-800 flex flex-col z-50 transition-all duration-300 ease-in-out md:static shadow-sm',
      isMobileMenuOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0',
      isSidebarCollapsed ? 'w-20' : 'w-64'
    ]">
      <!-- Logo Section -->
      <div class="h-16 flex items-center justify-between px-4 border-b border-surface-800 shrink-0">
        <div class="flex items-center gap-3 overflow-hidden whitespace-nowrap">
            <div class="w-10 h-10 rounded-xl bg-surface-800 flex shrink-0 items-center justify-center shadow-lg border border-surface-700 overflow-hidden">
                <img src="/logo.png" alt="GoldArmy Logo" class="w-full h-full object-cover" />
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
             item.href === currentRoute || (item.href !== '/' && currentRoute.startsWith(item.href)) ? 'bg-slate-100 text-slate-900 font-bold' : 'text-slate-500 hover:text-slate-900 hover:bg-slate-50',
             isSidebarCollapsed ? 'justify-center py-3 px-0' : 'gap-3 px-3 py-2.5'
          ]"
          :title="isSidebarCollapsed ? item.name : ''"
        >
          <!-- Active Indicator dot (Orange/Gold) -->
          <div v-if="item.href === currentRoute || (item.href !== '/' && currentRoute.startsWith(item.href))" class="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-5 bg-[#F59E0B] rounded-r-full shadow-[0_0_10px_rgba(232,93,62,0.3)]"></div>
          
          <component :is="item.icon" class="w-5 h-5 shrink-0" :class="item.href === currentRoute || (item.href !== '/' && currentRoute.startsWith(item.href)) ? 'text-slate-900' : 'text-slate-400 group-hover:text-slate-600'" />
          
          <span v-if="!isSidebarCollapsed" class="whitespace-nowrap transition-opacity duration-300">{{ item.name }}</span>
          
          <div v-if="item.name === 'Mentor IA' && !isSidebarCollapsed" class="ml-auto flex items-center justify-center">
             <span class="bg-gradient-to-r from-gray-700 to-gray-900 text-white text-[9px] uppercase font-black px-1.5 py-0.5 rounded-sm shadow-sm">Pro</span>
          </div>
          <div v-if="item.name === 'Mentor IA' && isSidebarCollapsed" class="absolute top-1 right-1">
             <span class="w-2 h-2 rounded-full bg-violet-500 block"></span>
          </div>
        </router-link>

        <!-- Admin Console Link -->
        <router-link 
          v-if="userTier === 'ADMIN'"
          to="/admin-goldarmy"
          class="flex items-center rounded-xl text-sm font-semibold transition-all group relative overflow-hidden bg-red-500/5 text-red-500 hover:bg-red-500/10 border border-red-500/10"
          :class="[
             currentRoute === '/admin-goldarmy' ? 'bg-red-500/10 border-red-500/30' : '',
             isSidebarCollapsed ? 'justify-center py-3 px-0' : 'gap-3 px-3 py-2.5'
          ]"
          title="Console Admin"
        >
          <ShieldCheckIcon class="w-5 h-5 shrink-0 text-red-500" />
          <span v-if="!isSidebarCollapsed" class="whitespace-nowrap font-black italic uppercase tracking-tighter">{{ t('nav.admin') }}</span>
          <div v-if="currentRoute === '/admin-goldarmy'" class="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-5 bg-red-500 rounded-r-full shadow-[0_0_10px_rgba(239,68,68,0.5)]"></div>
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
          <span v-if="!isSidebarCollapsed" class="whitespace-nowrap transition-opacity duration-300">{{ t('nav.settings') }}</span>
        </router-link>
      </div>
    </aside>

    <!-- Main Content Col -->
    <div class="flex-1 flex flex-col min-w-0 min-h-0 overflow-hidden relative w-full" :class="!isImmersive ? 'z-10' : 'z-[100]'">
      
      <!-- Topbar (Header) -->
      <header v-if="!isPublicRoute && !isImmersive" class="h-16 bg-surface-900 w-full border-b border-surface-800 flex items-center justify-between px-4 lg:px-8 relative z-20 shrink-0 gap-4 shadow-sm">
        
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
            <!-- Language Switcher -->
            <button 
                @click="toggleLanguage" 
                class="flex items-center gap-2 px-3 py-1.5 rounded-full bg-surface-900 border border-surface-800 hover:border-indigo-500/50 transition-all text-xs font-bold text-slate-400 hover:text-white"
            >
                <span :class="locale === 'fr' ? 'text-indigo-400' : ''">FR</span>
                <span class="text-slate-700">|</span>
                <span :class="locale === 'en' ? 'text-indigo-400' : ''">EN</span>
            </button>

            <!-- Notifications -->
            <div class="relative">
                <button 
                    @click="toggleNotifications"
                    class="relative p-2 text-slate-400 hover:text-white rounded-full hover:bg-surface-800 transition-colors"
                >
                    <BellIcon class="w-5 h-5" />
                    <span v-if="unreadCount > 0" class="absolute top-1.5 right-1.5 w-2 h-2 bg-rose-500 rounded-full border-2 border-surface-950"></span>
                </button>

                <!-- Notifications Dropdown -->
                <Transition name="fade">
                  <div v-if="isNotificationsOpen" class="absolute right-0 mt-3 w-80 bg-white rounded-2xl shadow-2xl border border-slate-100 overflow-hidden z-50 animate-slide-up">
                     <div class="p-4 border-b border-slate-50 flex items-center justify-between">
                        <h3 class="text-xs font-bold text-slate-800 uppercase tracking-widest">Notifications</h3>
                        <button @click="markAllAsRead" class="text-[10px] font-bold text-indigo-500 hover:text-indigo-600 uppercase">Tout lire</button>
                     </div>
                     <div class="max-h-[400px] overflow-y-auto">
                        <div v-if="notifications.length === 0" class="p-8 text-center">
                           <BellIcon class="w-8 h-8 text-slate-200 mx-auto mb-2" />
                           <p class="text-[10px] text-slate-400">Aucune notification pour le moment.</p>
                        </div>
                        <div v-else v-for="n in notifications" :key="n.id" 
                          class="p-4 border-b border-slate-50 hover:bg-slate-50 transition-colors cursor-pointer relative"
                          @click="n.action_url ? (router.push(n.action_url), isNotificationsOpen = false) : null"
                        >
                           <div class="flex gap-3">
                              <div :class="[
                                'w-2 h-2 rounded-full mt-1.5 shrink-0',
                                n.is_read ? 'bg-transparent' : 'bg-indigo-500'
                              ]"></div>
                              <div class="flex-1">
                                 <p class="text-xs font-bold text-slate-800">{{ n.title }}</p>
                                 <p class="text-[10px] text-slate-500 mt-0.5 leading-relaxed">{{ n.message }}</p>
                                 <p class="text-[9px] text-slate-300 mt-1 uppercase font-bold">{{ new Date(n.created_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}) }}</p>
                              </div>
                           </div>
                        </div>
                     </div>
                  </div>
                </Transition>
            </div>
            
            <div class="h-6 w-px bg-surface-800 hidden sm:block"></div>

            <!-- Enhanced User Profile Dropdown Trigger -->
            <button @click="handleLogout" title="Se déconnecter" class="flex items-center gap-3 p-1 pr-3 rounded-full hover:bg-surface-800 border border-transparent hover:border-surface-700 transition-all group">
                <div class="relative">
                    <div class="h-8 w-8 rounded-full bg-[#111827] flex items-center justify-center text-white font-bold text-xs ring-2 ring-surface-900 transition-all uppercase">
                        {{ userEmail.charAt(0) }}
                    </div>
                    <div class="absolute bottom-0 right-0 w-2.5 h-2.5 bg-rose-500 border-2 border-surface-950 rounded-full group-hover:bg-rose-400"></div>
                </div>
                <div class="hidden md:block text-left">
                    <div class="flex items-center gap-2 mb-0.5">
                        <p class="text-[13px] font-bold text-white leading-none group-hover:text-gold-400 transition-colors">{{ userEmail }}</p>
                        <!-- Badge Forfait -->
                        <span v-if="userTier === 'ADMIN'" class="bg-gradient-to-r from-red-500 to-rose-600 text-white text-[8px] uppercase font-black px-1.5 py-0.5 rounded-md shadow-lg shadow-rose-500/20">ADMIN</span>
                        <span v-else-if="userTier === 'PRO'" class="bg-gradient-to-r from-violet-500 to-indigo-500 text-white text-[8px] uppercase font-black px-1.5 py-0.5 rounded-md shadow-lg shadow-indigo-500/20">PRO</span>
                        <span v-else-if="userTier === 'ESSENTIAL'" class="bg-gradient-to-r from-amber-400 to-gold-500 text-surface-950 text-[8px] uppercase font-black px-1.5 py-0.5 rounded-md shadow-lg shadow-gold-500/20">ESSENTIEL</span>
                        <span v-else class="bg-surface-700 text-slate-300 text-[8px] uppercase font-black px-1.5 py-0.5 rounded-md">{{ userTier === 'FREE' ? 'GRATUIT' : userTier }}</span>
                    </div>
                    <p class="text-[10px] font-semibold text-slate-500 uppercase tracking-wider leading-none">{{ t('nav.logout') }}</p>
                </div>
            </button>
        </div>
      </header>

      <!-- Main Content Routing Area -->
      <main class="flex-1 overflow-y-auto w-full relative outline-none bg-surface-950 min-h-0" tabindex="0">
        <!-- Optional: Background ambient glow for the whole app -->
        <div class="absolute top-0 right-0 w-[800px] h-[600px] bg-indigo-500/5 rounded-full blur-[120px] pointer-events-none mix-blend-screen"></div>
        
        <div class="w-full h-full relative">
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
  background: #64748b; 
}
</style>
