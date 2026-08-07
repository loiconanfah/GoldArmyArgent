import { reactive } from 'vue'

/**
 * État global du verrouillage de fonctionnalité.
 * kind : 'gold' (solde insuffisant) | 'upgrade' (forfait requis) | 'generic'
 */
export const lockState = reactive({
    open: false,
    kind: 'generic',
    message: '',
    requiredTier: null,

    show({ kind = 'generic', message = '', requiredTier = null } = {}) {
        this.kind = kind
        this.message = message
        this.requiredTier = requiredTier
        this.open = true
    },

    close() {
        this.open = false
    }
})
