import { reactive } from 'vue'

export const toastState = reactive({
    toasts: [],

    addToast(message, type = 'success', duration = 4000) {
        const id = Date.now()
        this.toasts.push({ id, message, type })

        setTimeout(() => {
            this.removeToast(id)
        }, duration)
    },

    removeToast(id) {
        this.toasts = this.toasts.filter(t => t.id !== id)
    }
})
