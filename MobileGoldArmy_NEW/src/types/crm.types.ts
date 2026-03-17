export const STATUS_THEME = {
  a_postuler: { color: '#F59E0B', pale: '#FFFBEB', label: 'À Postuler' },
  envoye: { color: '#4A9EFF', pale: '#EBF4FF', label: 'Candidature Envoyée' },
  entretien: { color: '#10B981', pale: '#E6FAF4', label: 'Entretien' },
  relance: { color: '#EC4899', pale: '#FEF0F7', label: 'Relance Requise' },
  offre: { color: '#FF6B35', pale: '#FFF0EB', label: 'Offre Reçue' },
  refuse: { color: '#9A9A94', pale: '#F5F4F0', label: 'Refusé' },
} as const;

export type StatusKey = keyof typeof STATUS_THEME;

export interface Candidature {
  id: string;
  url: string;
  title: string;
  company: string;
  status: StatusKey;
  description: string | null;
  notes: string | null;
  date: string;
  created_at: string;
}

export interface CrmCounts {
  total: number;
  a_postuler: number;
  envoye: number;
  entretien: number;
  relance: number;
  offre: number;
  refuse: number;
}

