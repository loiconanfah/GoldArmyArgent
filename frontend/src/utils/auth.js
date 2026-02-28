import { getApiUrl } from '../config';

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
        // Éviter la boucle infinie si on est déjà sur une page publique
        const publicPages = ['/login', '/register', '/'];
        if (!publicPages.includes(window.location.pathname)) {
            window.location.href = '/login';
        }
    }
    return response;
};
