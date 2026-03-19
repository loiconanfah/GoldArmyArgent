import api from './api';
import { 
  HrProfile, 
  DecisionMaker, 
  NetworkContact, 
  EmailDraft, 
  DraftRequest 
} from '../types/network.types';

export const networkService = {
  /**
   * Enrich company with HR profiles (Scout OSINT)
   */
  async enrichCompany(companyName: string): Promise<HrProfile[]> {
    try {
      const response = await api.post('/api/network/enrich', { company_name: companyName });
      if (response.data.status === 'success') {
        return response.data.data || [];
      }
      throw new Error(response.data.detail || 'Erreur lors de l’enrichissement');
    } catch (error: any) {
      console.error('[NetworkService][enrichCompany]', error);
      throw error;
    }
  },

  /**
   * Find decision makers in a company (Headhunter)
   */
  async findDecisionMakers(companyName: string): Promise<DecisionMaker[]> {
    try {
      const response = await api.post('/api/network/headhunter', { company_name: companyName });
      if (response.data.status === 'success') {
        return response.data.data || [];
      }
      throw new Error(response.data.detail || 'Erreur lors de la recherche des décideurs');
    } catch (error: any) {
      console.error('[NetworkService][findDecisionMakers]', error);
      throw error;
    }
  },

  /**
   * Generate an email draft
   */
  async generateDraft(data: DraftRequest): Promise<EmailDraft> {
    try {
      const response = await api.post('/api/network/draft-email', {
        ...data,
        company_description: '', // Optional for now
        cv_text: data.cv_text || 'John Doe, développeur motivé.' // Fallback
      });
      if (response.data.status === 'success') {
        return response.data.data;
      }
      throw new Error(response.data.detail || 'Erreur lors de la génération de l’e-mail');
    } catch (error: any) {
      console.error('[NetworkService][generateDraft]', error);
      throw error;
    }
  },

  /**
   * Get saved contacts from Address Book
   */
  async getContacts(): Promise<NetworkContact[]> {
    try {
      const response = await api.get('/api/network/contacts');
      if (response.data.status === 'success') {
        return response.data.data || [];
      }
      throw new Error(response.data.detail || 'Erreur lors du chargement des contacts');
    } catch (error: any) {
      console.error('[NetworkService][getContacts]', error);
      throw error;
    }
  }
};
