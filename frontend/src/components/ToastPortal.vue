<script setup>
import { toastState } from '../store/toastState'
import { 
    CheckCircleIcon, 
    ExclamationCircleIcon, 
    InformationCircleIcon,
    XMarkIcon
} from '@heroicons/vue/24/outline'

const getIcon = (type) => {
    if (type === 'success') return CheckCircleIcon
    if (type === 'error') return ExclamationCircleIcon
    return InformationCircleIcon
}

const getClasses = (type) => {
    if (type === 'success') return 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400'
    if (type === 'error') return 'bg-rose-500/10 border-rose-500/20 text-rose-400'
    return 'bg-indigo-500/10 border-indigo-500/20 text-indigo-400'
}

const getIconClass = (type) => {
    if (type === 'success') return 'text-emerald-500'
    if (type === 'error') return 'text-rose-500'
    return 'text-indigo-500'
}
</script>

<template>
    <div class="fixed top-6 right-6 z-[9999] flex flex-col gap-3 pointer-events-none w-full max-w-sm">
        <transition-group 
            enter-active-class="transition duration-300 ease-out"
            enter-from-class="translate-x-full opacity-0"
            enter-to-class="translate-x-0 opacity-100"
            leave-active-class="transition duration-200 ease-in"
            leave-from-class="translate-x-0 opacity-100"
            leave-to-class="translate-x-20 opacity-0"
        >
            <div 
                v-for="toast in toastState.toasts" 
                :key="toast.id"
                class="pointer-events-auto flex items-center justify-between gap-4 p-4 rounded-2xl border shadow-2xl backdrop-blur-xl animate-fade-in-right"
                :class="getClasses(toast.type)"
            >
                <div class="flex items-center gap-3">
                    <component :is="getIcon(toast.type)" class="w-6 h-6 shrink-0" :class="getIconClass(toast.type)" />
                    <p class="text-sm font-bold leading-tight">{{ toast.message }}</p>
                </div>
                <button @click="toastState.removeToast(toast.id)" class="p-1 hover:bg-white/5 rounded-lg transition-colors group">
                    <XMarkIcon class="w-4 h-4 text-slate-500 group-hover:text-white" />
                </button>
            </div>
        </transition-group>
    </div>
</template>

<style scoped>
.animate-fade-in-right {
    animation: fadeInRight 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes fadeInRight {
    from {
        opacity: 0;
        transform: translateX(40px);
    }
    to {
        opacity: 1;
        transform: translateX(0);
    }
}
</style>
