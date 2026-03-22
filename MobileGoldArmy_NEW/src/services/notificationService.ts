import api from './api';
import { API_ENDPOINTS } from '../utils/constants';

export interface Notification {
  id: string;
  user_id: string;
  title: string;
  message: string;
  type: 'info' | 'success' | 'warning' | 'error';
  action_url?: string;
  is_read: boolean;
  created_at: string;
}

export const notificationService = {
  getNotifications: async (): Promise<Notification[]> => {
    try {
      const response = await api.get('/api/notifications');
      return response.data;
    } catch (error) {
      console.error('[NotificationService] Error fetching notifications', error);
      return [];
    }
  },

  createNotification: async (data: { title: string; message: string; type?: string; action_url?: string }): Promise<Notification | null> => {
    try {
      const response = await api.post('/api/notifications', data);
      return response.data;
    } catch (error) {
      console.error('[NotificationService] Error creating notification', error);
      return null;
    }
  },

  markAsRead: async (notifId: string): Promise<boolean> => {
    try {
      await api.put(`/api/notifications/${notifId}/read`);
      return true;
    } catch (error) {
      console.error('[NotificationService] Error marking as read', error);
      return false;
    }
  },

  markAllAsRead: async (): Promise<boolean> => {
    try {
      await api.put('/api/notifications/read-all');
      return true;
    } catch (error) {
      console.error('[NotificationService] Error marking all as read', error);
      return false;
    }
  },

  registerPushToken: async (token: string): Promise<boolean> => {
    try {
      await api.post('/api/users/push-token', { token });
      return true;
    } catch (error) {
      console.error('[NotificationService] Error registering push token', error);
      return false;
    }
  }
};
