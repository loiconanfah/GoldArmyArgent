import { createRouter, createWebHistory, createMemoryHistory } from 'vue-router'
import Interview from '../views/Interview.vue'

const routes = [
    {
        path: '/login',
        name: 'Login',
        component: () => import('../views/Login.vue')
    },
    {
        path: '/register',
        name: 'Register',
        component: () => import('../views/Register.vue')
    },
    {
        path: '/',
        name: 'Landing',
        component: () => import('../views/Landing.vue')
    },
    {
        path: '/blog',
        name: 'Blog',
        component: () => import('../views/Blog.vue')
    },
    {
        path: '/free-cv-roast',
        name: 'FreeCVRoast',
        component: () => import('../views/FreeCVRoast.vue')
    },
    {
        path: '/free-interview',
        name: 'FreeInterview',
        component: () => import('../views/FreeInterview.vue')
    },
    {
        path: '/blog/:id',
        name: 'Article',
        component: () => import('../views/Article.vue'),
        props: true
    },
    // ── Pages SEO publiques ────────────────────────────────────────────────────
    {
        path: '/sniper-search',
        name: 'SniperSearch',
        component: () => import('../views/SniperSearch.vue')
    },
    {
        path: '/mentor-ia',
        name: 'MentorIA',
        component: () => import('../views/MentorIA.vue')
    },
    {
        path: '/simulation-entretien',
        name: 'SimulationEntretien',
        component: () => import('../views/SimulationEntretien.vue')
    },
    {
        path: '/crm-emploi',
        name: 'CrmEmploi',
        component: () => import('../views/CrmEmploi.vue')
    },
    {
        path: '/tarifs',
        name: 'Tarifs',
        component: () => import('../views/Tarifs.vue')
    },
    {
        path: '/pour-les-organisations',
        name: 'PourOrganisations',
        component: () => import('../views/PourOrganisations.vue')
    },
    {
        path: '/mentorat-a-la-demande',
        name: 'MentoratADemande',
        component: () => import('../views/MentoratADemande.vue')
    },
    {
        path: '/communaute-goldarmy',
        name: 'CommunauteGoldArmy',
        component: () => import('../views/CommunauteGoldArmy.vue')
    },
    {
        path: '/economie-gold',
        name: 'EconomieGold',
        component: () => import('../views/EconomieGold.vue')
    },
    // ── Accueil (post-login home page) ────────────────────────────────────
    {
        path: '/home',
        name: 'Home',
        component: () => import('../views/Home.vue'),
        meta: { requiresAuth: true }
    },
    {
        path: '/dashboard',
        name: 'Dashboard',
        component: () => import('../views/Dashboard.vue'),
        meta: { requiresAuth: true }
    },
    {
        path: '/chat',
        name: 'AgentChat',
        component: () => import('../views/AgentChat.vue'),
        meta: { requiresAuth: true }
    },
    {
        path: '/opportunities',
        name: 'Opportunities',
        component: () => import('../views/Opportunities.vue'),
        meta: { requiresAuth: true }
    },
    {
        path: '/mentor',
        name: 'Mentor',
        component: () => import('../views/Mentor.vue'),
        meta: { requiresAuth: true }
    },
    {
        path: '/crm',
        name: 'CRM',
        component: () => import('../views/CRM.vue'),
        meta: { requiresAuth: true }
    },
    {
        path: '/network',
        name: 'Network',
        component: () => import('../views/Reseaux.vue'),
        meta: { requiresAuth: true }
    },
    {
        path: '/communaute',
        name: 'Community',
        component: () => import('../views/Community.vue'),
        meta: { requiresAuth: true }
    },
    {
        path: '/hub-mentors',
        name: 'MentorHub',
        component: () => import('../views/MentorHub.vue'),
        meta: { requiresAuth: true }
    },
    {
        path: '/interview',
        name: 'Interview',
        component: Interview,
        meta: { requiresAuth: true }
    },
    {
        path: '/interview/history',
        name: 'InterviewHistory',
        component: () => import('../views/InterviewHistory.vue'),
        meta: { requiresAuth: true }
    },
    {
        path: '/profile',
        name: 'Profile',
        component: () => import('../views/Profile.vue'),
        meta: { requiresAuth: true }
    },
    {
        path: '/boutique',
        name: 'Boutique',
        component: () => import('../views/Boutique.vue'),
        meta: { requiresAuth: true }
    },
    {
        path: '/settings',
        name: 'Settings',
        component: () => import('../views/Settings.vue'),
        meta: { requiresAuth: true }
    },
    {
        path: '/admin-goldarmy',
        name: 'AdminDashboard',
        component: () => import('../views/AdminDashboard.vue'),
        meta: { requiresAuth: true, requiresAdmin: true }
    },
    {
        path: '/organisation',
        component: () => import('../views/org/OrgLayout.vue'),
        meta: { requiresAuth: true, requiresOrgAdmin: true },
        children: [
            { path: '', name: 'OrgDashboard', component: () => import('../views/org/OrgHome.vue') },
            { path: 'membres', name: 'OrgMembers', component: () => import('../views/org/OrgMembers.vue') },
            { path: 'mentors', name: 'OrgMentors', component: () => import('../views/org/OrgMentors.vue') },
            { path: 'reseau', name: 'OrgNetwork', component: () => import('../views/org/OrgNetwork.vue') },
            { path: 'communaute', name: 'OrgCommunity', component: () => import('../views/org/OrgCommunity.vue') },
            { path: 'facturation', name: 'OrgBilling', component: () => import('../views/org/OrgBilling.vue') },
            { path: 'parametres', name: 'OrgSettings', component: () => import('../views/org/OrgSettings.vue') },
        ]
    },
    {
        path: '/support',
        name: 'Support',
        component: () => import('../views/Support.vue')
    },
    {
        path: '/privacy',
        name: 'Privacy',
        component: () => import('../views/Privacy.vue')
    }
]

export { routes }

const history = typeof window !== 'undefined' ? createWebHistory() : createMemoryHistory()

const router = createRouter({
    history,
    routes,
    scrollBehavior(to, from, savedPosition) {
        if (to.hash) {
            return { el: to.hash, behavior: 'smooth', top: 80 }
        }
        // Always scroll to top immediately, disabling saved scroll restoration
        return new Promise((resolve) => {
            setTimeout(() => {
                resolve({ top: 0, left: 0, behavior: 'instant' })
            }, 10)
        })
    }
})

router.beforeEach((to, from, next) => {
    const isAuthenticated = typeof localStorage !== 'undefined' ? !!localStorage.getItem('token') : false
    if (to.meta.requiresAuth && !isAuthenticated) {
        next('/login')
    } else if ((to.name === 'Login' || to.name === 'Register' || to.name === 'Landing') && isAuthenticated) {
        next('/home')
    } else if (to.meta.requiresAdmin) {
        const user = typeof localStorage !== 'undefined'
            ? JSON.parse(localStorage.getItem('user') || '{}')
            : {}
        if (user.subscription_tier === 'ADMIN') {
            next()
        } else {
            next('/dashboard')
        }
    } else if (to.meta.requiresOrgAdmin) {
        const user = typeof localStorage !== 'undefined'
            ? JSON.parse(localStorage.getItem('user') || '{}')
            : {}
        if (user.role === 'org_admin') {
            next()
        } else {
            next('/dashboard')
        }
    } else {
        next()
    }
})

router.afterEach((to) => {
    if (typeof window !== 'undefined') {
        // Double security lock: force window view to absolute top after rendering ticks
        setTimeout(() => {
            window.scrollTo({ top: 0, left: 0, behavior: 'instant' })
        }, 50)
        
        import('../utils/analytics').then(({ trackEvent }) => {
            trackEvent('page_view', { name: to.name, path: to.path })
        })
    }
})

export default router
