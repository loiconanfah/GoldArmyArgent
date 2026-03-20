import api from './api';

export interface UserProfile {
  id: string;
  email: string;
  cv_text?: string;
  full_name?: string;
  subscription_tier?: string;
}

export const profileService = {
  /**
   * Get the current user's profile, including the extracted CV text
   */
  async getProfile(): Promise<UserProfile> {
    try {
      const response = await api.get('/api/profile');
      if (response.data.status === 'success') {
        return response.data.data;
      }
      throw new Error(response.data.detail || 'Erreur lors du chargement du profil');
    } catch (error: any) {
      console.error('[ProfileService][getProfile]', error);
      throw error;
    }
  },

  async updateProfile(data: Partial<UserProfile>): Promise<UserProfile> {
    try {
      const response = await api.put('/api/profile', data);
      if (response.data.status === 'success') {
        return response.data.data;
      }
      throw new Error(response.data.detail || 'Erreur lors de la mise à jour du profil');
    } catch (error: any) {
      console.error('[ProfileService][updateProfile]', error);
      throw error;
    }
  }
};
