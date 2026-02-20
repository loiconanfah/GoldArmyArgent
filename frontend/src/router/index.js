import { createRouter, createWebHistory } from 'vue-router'

const routes = [
    {
        path: '/',
        name: 'Dashboard',
        component: () => import('../views/Dashboard.vue')
    },
    {
        path: '/chat',
        name: 'AgentChat',
        component: () => import('../views/AgentChat.vue')
    },
    {
        path: '/opportunities',
        name: 'Opportunities',
        component: () => import('../views/Opportunities.vue')
    },
    {
        path: '/mentor',
        name: 'Mentor',
        component: () => import('../views/Mentor.vue')
    },
    {
        path: '/crm',
        name: 'CRM',
        component: () => import('../views/CRM.vue')
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

export default router
