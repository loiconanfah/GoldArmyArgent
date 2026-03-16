/**
 * Types pour les outils IA de la page d'accueil
 */

export type ToolId = 'sniper' | 'mentor' | 'vocal' | 'crm' | 'reseau';

export interface ToolStat {
  value: string;
  label: string;
}

export interface ToolMiniIcon {
  icon: string;  // nom Ionicons
  label: string;
}

export interface ToolData {
  id: ToolId;
  badge: string;
  color: string;
  colorPale: string;
  icon: string;              // nom Ionicons pour l'icône principale
  miniIcons: ToolMiniIcon[];
  title: string;
  description: string;
  features: string[];
  stats: ToolStat[];
  tip: string;
  cta: string;
  route: string;
}

