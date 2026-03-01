// Configuration dynamique de l'URL de l'API mission 16.1
const getBaseUrl = () => {
    if (import.meta.env.VITE_API_URL) return import.meta.env.VITE_API_URL;
    // En production sur Render, le backend est souvent sur le même domaine ou un sous-domaine
    if (window.location.hostname !== 'localhost') {
        const origin = window.location.origin;
        // Si on est sur Render, l'API est souvent sur le même domaine (ou configurée via VITE_API_URL)
        return origin;
    }
    return 'http://localhost:8000';
};

export const API_URL = getBaseUrl();

export const getApiUrl = (path) => {
    if (path.startsWith('http')) return path;
    const cleanPath = path.startsWith('/') ? path : `/${path}`;
    return `${API_URL}${cleanPath}`;
};

export const getWsUrl = (path) => {
    const wsBase = API_URL.replace(/^http/, 'ws');
    const cleanPath = path.startsWith('/') ? path : `/${path}`;
    return `${wsBase}${cleanPath}`;
};
