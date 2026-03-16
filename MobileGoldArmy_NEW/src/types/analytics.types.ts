export type ApplicationStatus =
  | 'a_postuler'
  | 'envoye'
  | 'entretien'
  | 'relance'
  | 'offre'
  | 'refuse';

export interface KpiData {
  id: string;
  label: string;
  value: number;
  subLabel: string;
  trend: number; // % variation vs previous period
  color: string;
  colorPale: string;
  icon: string; // Ionicons name
  progress: number; // 0 to 100
}

export interface ActivityItem {
  id: string;
  title: string;
  company: string;
  status: ApplicationStatus;
  progress: number; // 0 to 100
  date: string;
}

// Global precise palette requested by the user
export const STATUS_COLORS: Record<ApplicationStatus, { text: string; bg: string }> = {
  a_postuler: { text: '#F59E0B', bg: '#FFFBEB' }, // Ambre
  envoye: { text: '#4A9EFF', bg: '#EBF4FF' },     // Bleu
  entretien: { text: '#10B981', bg: '#E6FAF4' },  // Vert
  relance: { text: '#EC4899', bg: '#FEF0F7' },    // Rose
  offre: { text: '#F5D061', bg: '#FFF8DC' },      // Gold primary (logo color)
  refuse: { text: '#9A9A94', bg: '#F5F4F0' },     // Gris
};

export const KPI_COLORS = {
  candidatures: { text: '#F5D061', bg: '#FFF8DC' }, // Gold primary (logo color)
  cv_analyses: { text: '#60A5FA', bg: '#EBF4FF' },  // Bleu (comme home)
  entretiens: { text: '#10B981', bg: '#E6FAF4' },   // Vert
  reseau: { text: '#BB86FC', bg: '#F3EFFE' },       // Violet (comme home)
};
