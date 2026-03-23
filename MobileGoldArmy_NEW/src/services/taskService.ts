import api from './api';

export interface TaskResult {
  id: string;
  user_id: string;
  type: 'sniper' | 'cv_analysis' | 'mentor';
  status: 'pending' | 'completed' | 'failed';
  result?: any;
  error?: string;
  created_at: string;
  updated_at: string;
}

export const taskService = {
  getTask: async (taskId: string): Promise<TaskResult | null> => {
    try {
      const response = await api.get(`/api/tasks/${taskId}`);
      if (response.data.status === 'success') {
        return response.data.data;
      }
      return null;
    } catch (error) {
      console.error('[TaskService] Error fetching task:', error);
      return null;
    }
  },

  getRecentTasks: async (): Promise<TaskResult[]> => {
    try {
      const response = await api.get('/api/tasks');
      if (response.data.status === 'success') {
        return response.data.data;
      }
      return [];
    } catch (error) {
      console.error('[TaskService] Error fetching recent tasks:', error);
      return [];
    }
  }
};
