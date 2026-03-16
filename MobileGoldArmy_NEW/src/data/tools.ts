/**
 * Données des 5 outils IA pour la page d'accueil
 */

import type { ToolData, ToolId } from '../types/tool.types';
import { lightColors as C } from '../theme/colors';

export const TOOL_IDS: ToolId[] = ['sniper', 'mentor', 'vocal', 'crm', 'reseau'];

export const toolTheme = (id: ToolId) => {
  switch (id) {
    case 'sniper':
      return { color: '#4A9EFF', bg: '#EBF4FF' };
    case 'mentor':
      return { color: '#8B5CF6', bg: '#F3EFFE' };
    case 'vocal':
      return { color: '#10B981', bg: '#E6FAF4' };
    case 'crm':
      return { color: '#F59E0B', bg: '#FFFBEB' };
    case 'reseau':
      return { color: '#EC4899', bg: '#FEF0F7' };
    default:
      return { color: C.primary, bg: C.primaryLight };
  }
};

export const TOOLS: ToolData[] = [
  {
    id: 'sniper',
    badge: 'IA PUISSANTE',
    ...toolTheme('sniper'),
    icon: 'search-outline',
    miniIcons: [
      { icon: 'earth-outline', label: 'CARTE' },
      { icon: 'bar-chart-outline', label: 'STATS' },
      { icon: 'scan-outline', label: 'SCAN' },
      { icon: 'briefcase-outline', label: 'OFFRE' },
      { icon: 'git-network-outline', label: 'MATCH' },
    ],
    title: 'Sniper Search',
    description:
      "Recherche ultra-précise d'offres d'emploi. L'IA analyse 50+ sources pour trouver les opportunités parfaitement adaptées à ton profil et ta localisation.",
    features: [
      'Filtres Smart',
      'Scoring d’affinité avec ton CV',
      'Alertes en temps réel',
    ],
    stats: [
      { value: '50+', label: 'SOURCES' },
      { value: '94%', label: 'PRÉCISION IA' },
      { value: '< 5s', label: 'RÉSULTATS' },
    ],
    tip: 'Utilise des mots-clés précis : poste + ville + niveau.',
    cta: 'Accéder à Sniper Search',
    route: '/(tabs)/sniper',
  },
  {
    id: 'mentor',
    badge: 'PRO',
    ...toolTheme('mentor'),
    icon: 'sparkles-outline',
    miniIcons: [
      { icon: 'document-outline', label: 'CV' },
      { icon: 'flask-outline', label: 'ANALYSE' },
      { icon: 'create-outline', label: 'EDIT' },
      { icon: 'star-outline', label: 'SCORE' },
      { icon: 'mail-outline', label: 'LETTRE' },
    ],
    title: 'Mentor IA',
    description:
      'Ton coach carrière personnel. Analyse ton CV en 30s, identifie les lacunes et génère des lettres de motivation sur mesure.',
    features: ['Audit CV', 'Adaptation candidature', 'Générateur de lettre'],
    stats: [
      { value: '< 30s', label: 'AUDIT' },
      { value: '+40%', label: 'SUCCÈS' },
      { value: '100%', label: 'PERSONNALISÉ' },
    ],
    tip: 'Upload ton PDF — l’IA fait un audit complet en quelques secondes.',
    cta: 'Accéder à Mentor IA',
    route: '/(tabs)/mentor',
  },
  {
    id: 'vocal',
    badge: 'VOCAL IA',
    ...toolTheme('vocal'),
    icon: 'mic-outline',
    miniIcons: [
      { icon: 'chatbubbles-outline', label: 'DIALOG' },
      { icon: 'mic-outline', label: 'VOIX' },
      { icon: 'phone-portrait-outline', label: 'IA' },
      { icon: 'trending-up-outline', label: 'SCORE' },
      { icon: 'trophy-outline', label: 'SUCCÈS' },
    ],
    title: 'Entretien Vocal',
    description:
      'Simulation d’entretien avec un recruteur IA vocal. Parle à voix haute, affine tes réponses et construis ta confiance.',
    features: ['Simulation réaliste', 'Feedback instantané', 'Analyse du discours'],
    stats: [
      { value: '98%', label: 'RÉALISME' },
      { value: '+60%', label: 'CONFIANCE' },
      { value: '24/7', label: 'DISPONIBLE' },
    ],
    tip: 'Fais au moins 3 simulations avant un vrai entretien.',
    cta: 'Accéder à Entretien Vocal',
    route: '/(tabs)/vocal',
  },
  {
    id: 'crm',
    badge: 'KANBAN',
    ...toolTheme('crm'),
    icon: 'briefcase-outline',
    miniIcons: [
      { icon: 'apps-outline', label: 'BOARD' },
      { icon: 'checkmark-done-outline', label: 'DONE' },
      { icon: 'arrow-forward-outline', label: 'AVANCE' },
      { icon: 'mail-outline', label: 'EMAIL' },
      { icon: 'calendar-outline', label: 'RELANCE' },
    ],
    title: 'CRM Candidatures',
    description:
      'Tableau Kanban intelligent pour gérer toutes tes candidatures. Relances automatiques et historique complet.',
    features: ['Kanban drag & drop', 'Relances automatiques', 'Historique complet'],
    stats: [
      { value: '∞', label: 'CANDIDATURES' },
      { value: '0', label: 'OUBLI' },
      { value: 'AUTO', label: 'RELANCE' },
    ],
    tip: 'Ajoute chaque candidature dès l’envoi pour un suivi parfait.',
    cta: 'Accéder à CRM',
    route: '/(tabs)/crm',
  },
  {
    id: 'reseau',
    badge: 'RÉSEAU',
    ...toolTheme('reseau'),
    icon: 'people-outline',
    miniIcons: [
      { icon: 'person-add-outline', label: 'CONNECT' },
      { icon: 'logo-linkedin', label: 'LINKEDIN' },
      { icon: 'mail-outline', label: 'MESSAGE' },
      { icon: 'star-outline', label: 'PROFIL' },
      { icon: 'share-social-outline', label: 'PARTAGE' },
    ],
    title: 'Réseau IA',
    description:
      'Construction de réseau LinkedIn par IA : messages de connexion, posts optimisés et stratégie de visibilité.',
    features: ['Messages LinkedIn IA', 'Posts optimisés', 'Stratégie de visibilité'],
    stats: [
      { value: '+300%', label: 'VISIBILITÉ' },
      { value: 'IA', label: 'RÉDACTION' },
      { value: '< 10s', label: 'GÉNÉRATION' },
    ],
    tip: 'Personnalise chaque message, l’IA s’adapte à ton interlocuteur.',
    cta: 'Accéder à Réseau IA',
    route: '/(tabs)/reseau',
  },
];

