import { getApiUrl } from '../config';

/**
 * Safe JSON parser — returns null instead of throwing when the
 * response body is empty or not valid JSON (e.g. CORS failures,
 * proxy errors, 204 No Content, etc.)
 */
async function safeJson(response) {
    const text = await response.text();
    if (!text || !text.trim()) return null;
    try { return JSON.parse(text); } catch { return null; }
}

export const authFetch = async (url, options = {}) => {
    const fullUrl = getApiUrl(url);
    const token = localStorage.getItem('token');
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers,
        ...(token ? { 'Authorization': `Bearer ${token}` } : {})
    };

    // Ne pas mettre de Content-Type si c'est un FormData (upload de fichier)
    if (options.body instanceof FormData) {
        delete headers['Content-Type'];
    }

    const response = await fetch(fullUrl, { ...options, headers });

    if (response.status === 401) {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        const publicPages = ['/login', '/register', '/'];
        if (!publicPages.includes(window.location.pathname)) {
            window.location.href = '/login';
        }
    }

    // Verrouillage de fonctionnalité : Gold insuffisant ou forfait requis → popup globale
    if (response.status === 403) {
        try {
            const data = await response.clone().json();
            const detail = (data && (data.detail || data.message)) || '';
            if (/gold insuffisant|insufficient gold/i.test(detail)) {
                const { lockState } = await import('../store/lockState');
                lockState.show({ kind: 'gold', message: detail });
            } else if (/réservé au forfait|reserved for|améliorez|upgrade your/i.test(detail)) {
                const { lockState } = await import('../store/lockState');
                lockState.show({ kind: 'upgrade', message: detail });
            }
        } catch (e) { /* corps non-JSON : on ignore */ }
    }

    // Attach safeJson helper to the response so callers can use it:
    //   const data = await authFetch(...).then(r => r.safeJson())
    response.safeJson = () => safeJson(response);

    return response;
};

/** Standalone helper for non-authFetch calls (login, register, google auth) */
export { safeJson };
