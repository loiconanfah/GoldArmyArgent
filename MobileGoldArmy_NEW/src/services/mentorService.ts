import api from './api';
import { notificationService } from './notificationService';

type MentorAuditResponse = {
  type?: string;
  content?: string;
  audit?: string;
};

interface AuditCvPayload {
  message: string;
  cv_text: string;
  cv_filename: string;
}

export const mentorService = {
  /**
   * Récupère le profil utilisateur pour récupérer le CV stocké
   */
  async getProfileCv(): Promise<{ cv_text: string | null }> {
    const res = await api.get('/api/profile');
    const data = res.data?.data || res.data;
    return {
      cv_text: (data && typeof data.cv_text === 'string') ? data.cv_text : null,
    };
  },

  /**
   * Lance un audit de CV via l'orchestrateur (/api/chat)
   */
  async auditCv(payload: AuditCvPayload): Promise<MentorAuditResponse> {
    const body = {
      message: payload.message,
      cv_text: payload.cv_text,
      cv_filename: payload.cv_filename,
      // Important: ne pas forcer nb_results quand un CV est présent,
      // pour éviter de déclencher le mode job_search.
      nb_results: null,
      location: '',
      session_id: 'mentor-audit',
      image_data: null,
    };

    const res = await api.post('/api/chat', body, {
      // L'audit de CV peut être long : on augmente le timeout pour éviter les erreurs 30s
      timeout: 120000,
    });
    const data = res.data;
    const responseData = data.data || data;

    // Fire audit completion notification
    notificationService.createNotification({
      title: 'Audit CV Terminé',
      message: 'Votre CV a été analysé avec succès par notre IA. Consultez vos scores et recommandations.',
      type: 'success'
    }).catch((e) => console.error('[Notification] Failed to create audit notif', e));

    // Sécuriser les champs pour qu'ils soient toujours des chaînes affichables dans des <Text>
    const rawContent = responseData.content;
    const rawAudit = responseData.audit;

    const safeContent =
      typeof rawContent === 'string'
        ? rawContent
        : rawContent
        ? JSON.stringify(rawContent, null, 2)
        : undefined;

    const safeAudit =
      typeof rawAudit === 'string'
        ? rawAudit
        : rawAudit
        ? JSON.stringify(rawAudit, null, 2)
        : undefined;

    return {
      type: responseData.type,
      content: safeContent,
      audit: safeAudit,
    };
  },

  /**
   * GET User interview history 
   */
  async getInterviewHistory(limit: number = 50): Promise<any> {
    const res = await api.get(`/api/interview/history?limit=${limit}`);
    return res.data;
  },
};

