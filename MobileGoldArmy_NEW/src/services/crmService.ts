import api from './api';
import { API_ENDPOINTS } from '../utils/constants';
import { Candidature, StatusKey } from '../types/crm.types';

/**
 * Mapping between Backend statuses and Mobile status keys
 */
const BACKEND_TO_MOBILE: Record<string, StatusKey> = {
  'TO_APPLY': 'a_postuler',
  'APPLIED': 'envoye',
  'INTERVIEW': 'entretien',
  'FOLLOW_UP': 'relance',
  'OFFER': 'offre',
  'REJECTED': 'refuse',
};

const MOBILE_TO_BACKEND: Record<StatusKey, string> = {
  'a_postuler': 'TO_APPLY',
  'envoye': 'APPLIED',
  'entretien': 'INTERVIEW',
  'relance': 'FOLLOW_UP',
  'offre': 'OFFER',
  'refuse': 'REJECTED',
};

/**
 * Transforms a backend application object to a mobile Candidature object
 */
const transformApplication = (app: any): Candidature => {
  return {
    id: app.id,
    url: app.url || '',
    title: app.job_title || 'Poste inconnu',
    company: app.company_name || 'Entreprise inconnue',
    status: BACKEND_TO_MOBILE[app.status] || 'a_postuler',
    description: app.notes || null, // notes in backend is description/summary in mobile
    notes: app.notes || null,
    date: app.created_at ? new Date(app.created_at).toLocaleDateString('fr-FR', { day: '2-digit', month: '2-digit' }) : '--/--',
    created_at: app.created_at || new Date().toISOString(),
  };
};

export const crmService = {
  /**
   * Fetches all candidatures for the current user
   */
  async fetchCandidatures(): Promise<Candidature[]> {
    try {
      const response = await api.get(API_ENDPOINTS.CRM.FETCH);
      if (response.data.status === 'success' && Array.isArray(response.data.data)) {
        return response.data.data.map(transformApplication);
      }
      return [];
    } catch (error) {
      console.error('[crmService] fetchCandidatures failed:', error);
      throw error;
    }
  },

  /**
   * Adds a new candidature from a URL link (scraping)
   */
  async addFromLink(url: string): Promise<Candidature> {
    try {
      const response = await api.post(API_ENDPOINTS.CRM.LINK, { url });
      if (response.data.status === 'success') {
        return transformApplication(response.data.data);
      }
      throw new Error('Erreur lors de l’analyse du lien');
    } catch (error) {
      console.error('[crmService] addFromLink failed:', error);
      throw error;
    }
  },

  /**
   * Manually creates a new candidature
   */
  async createCandidature(data: {
    url: string;
    title: string;
    company: string;
    status: StatusKey;
    notes: string;
  }): Promise<string> {
    try {
      const response = await api.post(API_ENDPOINTS.CRM.CREATE, {
        job_title: data.title,
        company_name: data.company,
        url: data.url,
        status: MOBILE_TO_BACKEND[data.status],
        notes: data.notes,
      });
      if (response.data.status === 'success') {
        return response.data.data.id;
      }
      throw new Error('Erreur lors de la création');
    } catch (error) {
      console.error('[crmService] createCandidature failed:', error);
      throw error;
    }
  },

  /**
   * Updates the status of a candidature
   */
  async updateStatus(id: string, status: StatusKey): Promise<void> {
    try {
      // API_ENDPOINTS.CRM.UPDATE is a function (id) => path
      const url = typeof API_ENDPOINTS.CRM.UPDATE === 'function' 
        ? API_ENDPOINTS.CRM.UPDATE(id) 
        : `${API_ENDPOINTS.CRM.UPDATE}/${id}`;
        
      await api.put(url, {
        status: MOBILE_TO_BACKEND[status]
      });
    } catch (error) {
      console.error('[crmService] updateStatus failed:', error);
      throw error;
    }
  },
  
  /**
   * Deletes a candidature
   */
  async deleteCandidature(id: string): Promise<void> {
    try {
       const url = typeof API_ENDPOINTS.CRM.DELETE === 'function' 
        ? API_ENDPOINTS.CRM.DELETE(id) 
        : `${API_ENDPOINTS.CRM.DELETE}/${id}`;
        
      await api.delete(url);
    } catch (error) {
      console.error('[crmService] deleteCandidature failed:', error);
      throw error;
    }
  }
};
