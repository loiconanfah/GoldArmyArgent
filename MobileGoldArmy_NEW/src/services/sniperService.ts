import api from './api';
import { SniperSearchResult } from '../types/sniper.types';

interface SniperSearchPayload {
  query: string;
  location: string;
  limit: number;
  cv_text?: string;
  cv_filename?: string;
}

export class SniperError extends Error {
  constructor(
    message: string,
    public type?: 'limit_reached' | 'network' | 'unknown',
    public content?: string
  ) {
    super(message);
    this.name = 'SniperError';
  }
}

export const sniperService = {
  async searchJobs({ query, location, limit, cv_text, cv_filename }: SniperSearchPayload): Promise<SniperSearchResult> {
    const payload: any = {
      message: `Je cherche des offres d'emploi pour le poste suivant : ${query}. Retourne uniquement des résultats d'offres d'emploi pertinents.`,
      nb_results: limit,
      location,
      session_id: 'sniper-mobile',
    };

    // Ajouter le CV si fourni
    if (cv_text) {
      payload.cv_text = cv_text;
      payload.cv_filename = cv_filename || 'CV_Profil.pdf';
    }

    try {
      const response = await api.post('/api/chat', payload);
      const outer = response.data as { status: string; data?: any; type?: string; content?: string };
      
      // Cas d'erreur directe (ex: quota atteint)
      if (outer.status === 'error') {
        if (outer.type === 'limit_reached') {
          throw new SniperError(
            outer.content || 'Quota de recherche atteint',
            'limit_reached',
            outer.content
          );
        }
        throw new SniperError(
          outer.content || 'Erreur lors de la recherche',
          'unknown',
          outer.content
        );
      }

      // Cas de succès
      if (outer.status !== 'success' || !outer.data) {
        throw new SniperError('Recherche Sniper échouée', 'unknown');
      }

      const inner = outer.data as { status: string; type: string; content: any };
      
      // Vérifier que c'est bien une réponse de recherche d'emploi
      if (inner.type !== 'job_search_results') {
        throw new SniperError(
          `Réponse inattendue du backend: ${inner.type}`,
          'unknown'
        );
      }

      const content = inner.content as SniperSearchResult;
      
      // Valider la structure
      if (!content || !Array.isArray(content.matched_jobs)) {
        throw new SniperError('Format de réponse invalide', 'unknown');
      }

      return content;
    } catch (error: any) {
      // Si c'est déjà une SniperError, la relancer
      if (error instanceof SniperError) {
        throw error;
      }

      // Erreur réseau ou autre
      if (error.response) {
        // Erreur HTTP avec réponse
        const data = error.response.data;
        if (data?.type === 'limit_reached') {
          throw new SniperError(
            data.content || 'Quota de recherche atteint',
            'limit_reached',
            data.content
          );
        }
        throw new SniperError(
          data?.message || data?.detail || 'Erreur serveur',
          'unknown'
        );
      }

      // Erreur réseau (pas de réponse)
      if (error.request) {
        throw new SniperError(
          'Erreur de connexion. Vérifie ta connexion internet.',
          'network'
        );
      }

      // Autre erreur
      throw new SniperError(
        error.message || 'Erreur inconnue',
        'unknown'
      );
    }
  },
};

