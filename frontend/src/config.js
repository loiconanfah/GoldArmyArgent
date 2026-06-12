const getBaseUrl = () => {
    if (import.meta.env.VITE_API_URL) return import.meta.env.VITE_API_URL;
    
    // En mode local, on utilise une URL relative (vide) pour passer par le proxy Vite.
    // Le proxy Vite (vite.config.js) redirige /api/* vers http://127.0.0.1:8000
    // Cela évite tout conflit Docker/WSL sur le port 8000 (IPv6 vs IPv4).
    const isLocal = window.location.hostname === 'localhost' || 
                    window.location.hostname === '127.0.0.1' ||
                    window.location.hostname.startsWith('192.168.') ||
                    window.location.hostname.startsWith('10.') ||
                    window.location.hostname.startsWith('172.');

    if (isLocal) {
        // URL relative = le proxy Vite gère la redirection vers le backend
        return '';
    }
    
    return window.location.origin;
};

export const API_URL = getBaseUrl();

export const getApiUrl = (path) => {
    if (path.startsWith('http')) return path;
    const cleanPath = path.startsWith('/') ? path : `/${path}`;
    return `${API_URL}${cleanPath}`;
};

export const getWsUrl = (path) => {
    const cleanPath = path.startsWith('/') ? path : `/${path}`;

    const isLocal = window.location.hostname === 'localhost' || 
                    window.location.hostname === '127.0.0.1' ||
                    window.location.hostname.startsWith('192.168.') ||
                    window.location.hostname.startsWith('10.') ||
                    window.location.hostname.startsWith('172.');

    // Vercel Serverless Functions NE PEUVENT PAS proxifier les WebSockets persistants.
    // On doit attaquer Render directement.
    if (!isLocal) {
        return `wss://goldarmy.onrender.com${cleanPath}`;
    }

    // En local: passer par le proxy Vite WebSocket (ws://localhost:5173/ws/...)
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    return `${wsProtocol}//${window.location.host}${cleanPath}`;
};
