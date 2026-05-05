import { getApiUrl } from '../config';

/**
 * Service de tracking pour les analytiques internes.
 */
export const trackEvent = async (eventName, metadata = {}) => {
    try {
        const fullUrl = getApiUrl('/api/analytics/track');
        const payload = {
            event_name: eventName,
            page_url: window.location.pathname,
            metadata: metadata
        };

        // On utilise fetch direct (pas authFetch) car le tracking peut être public
        await fetch(fullUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
    } catch (e) {
        // Silently fail analytics
        console.warn("[Analytics] Failed to track event:", eventName, e);
    }
};

/**
 * Hook automatique pour traquer les vues de page.
 * À appeler dans le setup d'un composant ou globalement.
 */
export const trackPageView = () => {
    trackEvent('page_view');
};
