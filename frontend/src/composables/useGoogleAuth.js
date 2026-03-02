/**
 * useGoogleAuth — composable for Google Identity Services OAuth
 *
 * The Google SDK is loaded DYNAMICALLY with error handling.
 * This prevents the app from stalling in countries where accounts.google.com
 * is blocked (China, Russia, Iran, etc.).
 */
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID ?? ''
import { API_URL } from '../config'

// Track SDK load state globally to avoid multiple script injections
let sdkLoadPromise = null

/**
 * Loads the Google Identity Services SDK dynamically.
 * Resolves to true if loaded, false if blocked/failed.
 */
function loadGoogleSDK() {
    if (sdkLoadPromise) return sdkLoadPromise

    sdkLoadPromise = new Promise((resolve) => {
        // Already loaded
        if (window.google) {
            resolve(true)
            return
        }

        const script = document.createElement('script')
        script.src = 'https://accounts.google.com/gsi/client'
        script.async = true
        script.defer = true

        // Failure (network block, firewall, etc.)
        script.onerror = () => {
            console.warn('[GoldArmy] Google SDK unavailable (blocked by network/firewall).')
            resolve(false)
        }

        // Timeout failsafe — in some countries the request hangs indefinitely
        const timeout = setTimeout(() => {
            console.warn('[GoldArmy] Google SDK timeout — likely blocked by network.')
            resolve(false)
        }, 8000)

        // Success
        script.onload = () => {
            clearTimeout(timeout)
            resolve(true)
        }

        document.head.appendChild(script)
    })

    return sdkLoadPromise
}

export function useGoogleAuth() {
    const router = useRouter()
    const googleLoading = ref(false)
    const googleError = ref('')
    const googleAvailable = ref(true) // optimistic, updated after SDK check

    /** Initialize Google GIS — loads SDK dynamically, handles failures gracefully */
    async function initGoogle(elementId = null) {
        if (!GOOGLE_CLIENT_ID) {
            console.warn('[GoldArmy] Google Client ID missing. Set VITE_GOOGLE_CLIENT_ID.')
            googleAvailable.value = false
            return
        }

        const loaded = await loadGoogleSDK()

        if (!loaded || !window.google) {
            googleAvailable.value = false
            googleError.value = 'Connexion Google non disponible depuis votre region.'
            return
        }

        googleAvailable.value = true

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

    /** Trigger One Tap prompt (fallback) */
    function googleSignIn() {
        if (!window.google) {
            googleError.value = 'Google non disponible depuis votre region.'
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
            if (!res.ok) throw new Error(data.detail ?? 'Echec connexion Google')

            localStorage.setItem('token', data.access_token)
            localStorage.setItem('user', JSON.stringify(data.user))
            router.push('/')
        } catch (err) {
            googleError.value = err.message
        } finally {
            googleLoading.value = false
        }
    }

    return { googleLoading, googleError, googleAvailable, initGoogle, googleSignIn }
}
