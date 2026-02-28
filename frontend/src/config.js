export const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

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
