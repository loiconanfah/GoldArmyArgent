/**
 * Types for Onboarding feature
 */

import type { ReactElement } from 'react';

export type OnboardingIconName =
  | 'search-outline'
  | 'chatbubbles-outline'
  | 'clipboard-outline'
  | 'mail-outline';

export interface SlideData {
  id: string;
  badge: string;
  title: string;
  subtitle: string;
  illustration: ReactElement;
  icon: OnboardingIconName;
  hasHighlight?: boolean;
  highlightContent?: ReactElement;
  imageUrl?: string;
}

export interface OnboardingSlideProps {
  slide: SlideData;
  isActive: boolean;
  onNext: () => void;
  onSkip: () => void;
  isLast: boolean;
}
