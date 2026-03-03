/**
 * useMeta — simple composable to set page title & meta description per route.
 *
 * Usage in any .vue page component:
 *   import { useMeta } from '@/composables/useMeta'
 *   useMeta({
 *     title: 'Sniper Search — GoldArmy AI',
 *     description: 'Recherchez des offres d\'emploi avec l\'IA la plus puissante du marché.'
 *   })
 */
export function useMeta({ title, description } = {}) {
    if (title) {
        document.title = title
    }

    if (description) {
        let el = document.querySelector('meta[name="description"]')
        if (el) {
            el.setAttribute('content', description)
        }
    }
}
