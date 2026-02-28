/**
 * useGoogleAuth — composable for Google Identity Services OAuth
 *
 * Usage:
 *   const { initGoogle, googleSignIn } = useGoogleAuth()
 *   onMounted(() => initGoogle())
 *   // then call googleSignIn() on button click
 */
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID ?? ''
import { API_URL } from '../config'

export function useGoogleAuth() {
    const router = useRouter()
    const googleLoading = ref(false)
    const googleError = ref('')

    /** Initialize Google GIS */
    function initGoogle(elementId = null) {
        if (!GOOGLE_CLIENT_ID) return

        const renderInterval = setInterval(() => {
            if (window.google) {
                clearInterval(renderInterval)
                window.google.accounts.id.initialize({
                    client_id: GOOGLE_CLIENT_ID,
                    callback: handleGoogleCredential,
                    auto_select: false,
                })

                if (elementId && document.getElementById(elementId)) {
                    window.google.accounts.id.renderButton(
                        document.getElementById(elementId),
                        {
                            theme: 'outline',
                            size: 'large',
                            shape: 'pill',
                            width: '240',
                            locale: 'fr',
                            text: 'signin_with',
                            logo_alignment: 'left'
                        }
                    )
                }
            }
        }, 100)

        // Stop polling after 10s
        setTimeout(() => clearInterval(renderInterval), 10000)
    }

    /** Trigger One Tap prompt (fallback) */
    function googleSignIn() {
        if (!window.google) {
            googleError.value = 'SDK Google non chargé. Rafraîchissez.'
            return
        }
        googleError.value = ''
        googleLoading.value = true
        window.google.accounts.id.prompt((notification) => {
            if (notification.isNotDisplayed() || notification.isSkippedMoment()) {
                googleLoading.value = false
                googleError.value = 'Utilisez le bouton "Continuer avec Google" ci-dessous.'
            }
        })
    }

    /** Called by Google with the ID token credential */
    async function handleGoogleCredential(response) {
        googleLoading.value = true
        googleError.value = ''
        try {
            const res = await fetch(`${API_URL}/api/auth/google`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ credential: response.credential }),
            })
            const data = await res.json()
            if (!res.ok) throw new Error(data.detail ?? 'Échec connexion Google')

            localStorage.setItem('token', data.access_token)
            localStorage.setItem('user', JSON.stringify(data.user))
            router.push('/')
        } catch (err) {
            googleError.value = err.message
        } finally {
            googleLoading.value = false
        }
    }

    return { googleLoading, googleError, initGoogle, googleSignIn }
}
