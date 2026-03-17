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

// Global precise palette using app theme colors (Gold/Orange primary)
export const STATUS_COLORS: Record<ApplicationStatus, { text: string; bg: string }> = {
  a_postuler: { text: '#A1A1AA', bg: 'rgba(161, 161, 170, 0.1)' }, // Muted Grey
  envoye: { text: '#3B82F6', bg: 'rgba(59, 130, 246, 0.1)' },     // Blue (Secondary)
  entretien: { text: '#F5D061', bg: 'rgba(245, 208, 97, 0.15)' },  // Gold (Primary)
  relance: { text: '#E6A32F', bg: 'rgba(230, 163, 47, 0.1)' },    // Gold Dark
  offre: { text: '#F5D061', bg: 'rgba(245, 208, 97, 0.2)' },      // Gold (Primary) - Highlight
  refuse: { text: '#EF4444', bg: 'rgba(239, 68, 68, 0.1)' },     // Error Red
};

export const KPI_COLORS = {
  candidatures: { text: '#F5D061', bg: 'rgba(245, 208, 97, 0.12)' }, // Gold (Primary)
  cv_analyses: { text: '#3B82F6', bg: 'rgba(59, 130, 246, 0.12)' },  // Blue (Secondary)
  entretiens: { text: '#9B59B6', bg: 'rgba(155, 89, 182, 0.12)' },   // Purple (Accent)
  reseau: { text: '#E6A32F', bg: 'rgba(230, 163, 47, 0.12)' },       // Gold Dark
};
