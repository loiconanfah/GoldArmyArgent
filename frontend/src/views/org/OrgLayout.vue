<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { authFetch } from '@/utils/auth'
import {
  ChartBarIcon, UsersIcon, AcademicCapIcon, UserGroupIcon,
  ChatBubbleLeftRightIcon, Cog6ToothIcon, ArrowLeftOnRectangleIcon,
  BuildingOffice2Icon, Bars3Icon, XMarkIcon, CreditCardIcon
} from '@heroicons/vue/24/outline'

const { t } = useI18n()
const router = useRouter()
const route = useRoute()

const orgName = ref('')
const menuOpen = ref(false)
const adminName = ref('')
const adminEmail = ref('')

const groups = computed(() => [
  {
    label: t('org.nav.group_pilot'),
    links: [
      { name: t('org.tabs.overview'), to: '/organisation', icon: ChartBarIcon, exact: true },
      { name: t('org.tabs.members'), to: '/organisation/membres', icon: UsersIcon },
    ],
  },
  {
    label: t('org.nav.group_community'),
    links: [
      { name: t('org.nav.mentors'), to: '/organisation/mentors', icon: AcademicCapIcon },
      { name: t('org.nav.network'), to: '/organisation/reseau', icon: UserGroupIcon },
      { name: t('org.nav.community'), to: '/organisation/communaute', icon: ChatBubbleLeftRightIcon },
    ],
  },
  {
    label: t('org.nav.group_manage'),
    links: [
      { name: t('org.nav.billing'), to: '/organisation/facturation', icon: CreditCardIcon },
      { name: t('org.tabs.settings'), to: '/organisation/parametres', icon: Cog6ToothIcon },
    ],
  },
])

function isActive(l) {
  return l.exact ? route.path === l.to : route.path.startsWith(l.to)
}

function backToApp() { router.push('/home') }
function logout() {
  localStorage.removeItem('token'); localStorage.removeItem('user'); router.push('/login')
}

const adminInitial = computed(() => (adminName.value || adminEmail.value || 'A')[0].toUpperCase())

onMounted(async () => {
  try {
    const u = JSON.parse(localStorage.getItem('user') || '{}')
    adminName.value = u.full_name || (u.email ? u.email.split('@')[0] : '')
    adminEmail.value = u.email || ''
  } catch (e) {}
  try {
    const res = await authFetch('/api/org/me')
    const json = await res.safeJson()
    if (json?.status === 'success') orgName.value = json.data.name
  } catch (e) {}
})
</script>

<template>
  <div class="olayout">
    <!-- Sidebar -->
    <aside :class="['olayout__side', { 'olayout__side--open': menuOpen }]">
      <div class="olayout__brand">
        <div class="olayout__brand-icon"><BuildingOffice2Icon class="w-6 h-6" /></div>
        <div class="olayout__brand-text">
          <div class="olayout__brand-name">{{ orgName || t('org.dashboard.title') }}</div>
          <div class="olayout__brand-tag">{{ t('org.dashboard.subtitle') }}</div>
        </div>
        <button class="olayout__close" @click="menuOpen = false"><XMarkIcon class="w-5 h-5" /></button>
      </div>

      <nav class="olayout__nav">
        <div v-for="g in groups" :key="g.label" class="olayout__group">
          <p class="olayout__group-label">{{ g.label }}</p>
          <router-link
            v-for="l in g.links" :key="l.to" :to="l.to"
            :class="['olayout__link', { 'olayout__link--active': isActive(l) }]"
            @click="menuOpen = false"
          >
            <component :is="l.icon" class="olayout__link-icon w-5 h-5 shrink-0" />
            <span>{{ l.name }}</span>
          </router-link>
        </div>
      </nav>

      <!-- Profile footer -->
      <div class="olayout__profile">
        <div class="olayout__avatar">{{ adminInitial }}</div>
        <div class="olayout__profile-info">
          <div class="olayout__profile-name">{{ adminName || '—' }}</div>
          <div class="olayout__profile-badge">{{ t('org.nav.admin_badge') }}</div>
        </div>
        <button class="olayout__logout" :title="t('org.nav.logout')" @click="logout">
          <ArrowLeftOnRectangleIcon class="w-4 h-4" />
        </button>
      </div>
      <button class="olayout__back" @click="backToApp">
        <BuildingOffice2Icon class="w-4 h-4" /> {{ t('org.nav.back_to_app') }}
      </button>
    </aside>

    <!-- Mobile top bar -->
    <div class="olayout__topbar">
      <button class="olayout__burger" @click="menuOpen = true"><Bars3Icon class="w-6 h-6" /></button>
      <span class="olayout__topbar-name">{{ orgName || t('org.dashboard.title') }}</span>
    </div>

    <div v-if="menuOpen" class="olayout__overlay" @click="menuOpen = false"></div>

    <!-- Content -->
    <main class="olayout__main">
      <router-view v-slot="{ Component }">
        <transition name="ofade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
  </div>
</template>

<style scoped>
.olayout {
  display: flex;
  min-height: 100vh;
  background:
    radial-gradient(1200px 500px at 100% -10%, rgba(245,158,11,0.06), transparent 60%),
    #F8FAFC;
  color: #1E293B;
}

/* Sidebar — dark, aligned with the base app chrome (surface-900) */
.olayout__side {
  width: 264px;
  flex-shrink: 0;
  background: #0F172A;
  border-right: 1px solid #1E293B;
  display: flex;
  flex-direction: column;
  padding: 1.1rem 0.85rem;
  position: sticky;
  top: 0;
  height: 100vh;
}
.olayout__brand { display: flex; align-items: center; gap: 0.7rem; padding: 0.25rem 0.4rem 1.25rem; margin-bottom: 0.5rem; border-bottom: 1px solid #1E293B; }
.olayout__brand-icon {
  width: 2.6rem; height: 2.6rem; border-radius: 0.8rem; flex-shrink: 0;
  background: linear-gradient(135deg, #FBBF24, #F59E0B);
  color: #0F172A; display: flex; align-items: center; justify-content: center;
  box-shadow: 0 6px 16px -4px rgba(245,158,11,0.5);
}
.olayout__brand-name { font-weight: 800; font-size: 0.95rem; line-height: 1.1; color: #fff; }
.olayout__brand-tag { font-size: 0.68rem; color: #64748B; margin-top: 0.15rem; }
.olayout__close { display: none; margin-left: auto; background: none; border: none; color: #64748B; cursor: pointer; }

.olayout__nav { display: flex; flex-direction: column; gap: 0.4rem; flex: 1; padding-top: 0.5rem; overflow-y: auto; }
.olayout__group { display: flex; flex-direction: column; gap: 0.15rem; }
.olayout__group + .olayout__group { margin-top: 0.7rem; }
.olayout__group-label { font-size: 0.62rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.1em; color: #475569; margin: 0 0 0.35rem 0.8rem; }
.olayout__link-icon { color: #64748B; transition: color 0.15s; }
.olayout__link:hover .olayout__link-icon { color: #E2E8F0; }
.olayout__link--active .olayout__link-icon { color: #B45309; }

.olayout__profile { display: flex; align-items: center; gap: 0.6rem; padding: 0.6rem; margin-top: 0.75rem; border-radius: 0.8rem; background: #1E293B; border: 1px solid #334155; }
.olayout__avatar { width: 2.2rem; height: 2.2rem; border-radius: 50%; flex-shrink: 0; background: linear-gradient(135deg, #FBBF24, #F59E0B); color: #0F172A; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 0.85rem; }
.olayout__profile-info { flex: 1; min-width: 0; }
.olayout__profile-name { font-size: 0.8rem; font-weight: 700; color: #F1F5F9; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.olayout__profile-badge { font-size: 0.6rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.05em; color: #FBBF24; }
.olayout__logout { flex-shrink: 0; background: none; border: none; color: #64748B; cursor: pointer; padding: 0.35rem; border-radius: 0.4rem; transition: color 0.15s, background 0.15s; }
.olayout__logout:hover { color: #FCA5A5; background: rgba(239,68,68,0.1); }
.olayout__link {
  position: relative;
  display: flex; align-items: center; gap: 0.75rem;
  padding: 0.68rem 0.8rem; border-radius: 0.7rem;
  color: #94A3B8; font-size: 0.875rem; font-weight: 600;
  text-decoration: none; transition: background 0.15s, color 0.15s;
}
.olayout__link:hover { background: #1E293B; color: #E2E8F0; }
.olayout__link--active {
  background: #F1F5F9;
  color: #0F172A;
  font-weight: 700;
}
.olayout__link--active::before {
  content: ''; position: absolute; left: 0; top: 50%; transform: translateY(-50%);
  width: 4px; height: 1.4rem; border-radius: 0 4px 4px 0;
  background: #F59E0B; box-shadow: 0 0 10px rgba(245,158,11,0.5);
}

.olayout__back {
  display: flex; align-items: center; gap: 0.6rem; justify-content: center;
  margin-top: 1rem; padding: 0.7rem; border-radius: 0.7rem;
  background: none; border: 1px solid #1E293B; color: #94A3B8;
  font-size: 0.8rem; font-weight: 600; cursor: pointer; transition: all 0.15s;
}
.olayout__back:hover { color: #fff; border-color: #334155; background: #1E293B; }

.olayout__main { flex: 1; min-width: 0; padding: 2.25rem; }

.olayout__topbar { display: none; }
.olayout__overlay { display: none; }

@media (max-width: 860px) {
  .olayout { flex-direction: column; }
  .olayout__side {
    position: fixed; z-index: 60; left: 0; top: 0; height: 100vh;
    transform: translateX(-100%); transition: transform 0.25s ease;
  }
  .olayout__side--open { transform: translateX(0); }
  .olayout__close { display: block; }
  .olayout__topbar {
    display: flex; align-items: center; gap: 0.75rem;
    padding: 0.9rem 1rem; background: #fff; border-bottom: 1px solid #E2E8F0;
    position: sticky; top: 0; z-index: 40;
  }
  .olayout__burger { background: none; border: none; color: #0F172A; cursor: pointer; }
  .olayout__topbar-name { font-weight: 800; font-size: 0.95rem; }
  .olayout__overlay { display: block; position: fixed; inset: 0; background: rgba(15,23,42,0.5); z-index: 55; }
  .olayout__main { padding: 1.25rem; }
}

.ofade-enter-active, .ofade-leave-active { transition: opacity 0.22s, transform 0.22s; }
.ofade-enter-from { opacity: 0; transform: translateY(8px); }
.ofade-leave-to { opacity: 0; transform: translateY(-8px); }
</style>
