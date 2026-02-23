import { createRouter, createWebHistory } from 'vue-router'
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
        path: '/interview',
        name: 'Interview',
        component: Interview,
        meta: { requiresAuth: true }
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

router.beforeEach((to, from, next) => {
    const isAuthenticated = !!localStorage.getItem('token')
    if (to.meta.requiresAuth && !isAuthenticated) {
        next('/login')
    } else if ((to.name === 'Login' || to.name === 'Register' || to.name === 'Landing') && isAuthenticated) {
        next('/dashboard')
    } else {
        next()
    }
})

export default router
