/**
 * Types for Onboarding feature
 */

import { ReactElement } from 'react';

export interface SlideData {
  id: string;
  badge: string;
  title: string;
  subtitle: string;
  illustration: ReactElement;
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
