import api from './api';

export interface UserProfile {
  id: string;
  email: string;
  cv_text?: string;
  full_name?: string;
  subscription_tier?: string;
  avatar_url?: string;
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
      // Backend expects POST for profile updates, not PUT
      const response = await api.post('/api/profile', data);
      if (response.data.status === 'success') {
        return response.data.data;
      }
      throw new Error(response.data.detail || 'Erreur lors de la mise à jour du profil');
    } catch (error: any) {
      console.error('[ProfileService][updateProfile]', error);
      throw error;
    }
  },

  async uploadAvatar(fileUri: string): Promise<{ status: string, avatar_url: string }> {
    try {
      const formData = new FormData();
      const filename = fileUri.split('/').pop() || 'avatar.jpg';
      const match = /\.(\w+)$/.exec(filename);
      const type = match ? `image/${match[1]}` : `image`;

      // @ts-ignore
      formData.append('file', {
        uri: fileUri,
        name: filename,
        type: type
      });

      const response = await api.post('/api/profile/upload-avatar', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      return response.data;
    } catch (error: any) {
      console.error('[ProfileService][uploadAvatar]', error);
      throw error;
    }
  },

  async uploadCv(fileUri: string): Promise<{ status: string, text: string }> {
    try {
      const formData = new FormData();
      const filename = fileUri.split('/').pop() || 'cv.pdf';

      // @ts-ignore
      formData.append('file', {
        uri: fileUri,
        name: filename,
        type: 'application/pdf'
      });

      const response = await api.post('/api/profile/upload-cv', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      return response.data;
    } catch (error: any) {
      console.error('[ProfileService][uploadCv]', error);
      throw error;
    }
  }
};
