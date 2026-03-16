/**
 * Theme export
 * Centralized theme configuration
 */

export * from './colors';
export * from './typography';
export * from './spacing';
export * from './shadows';

import { getColors, type ColorScheme } from './colors';
import { typography } from './typography';
import { spacing } from './spacing';
import { shadows } from './shadows';

export const getTheme = (scheme: ColorScheme) => ({
  colors: getColors(scheme),
  typography,
  spacing,
  shadows,
  borderRadius: {
    sm: 8,
    md: 12,
    lg: 16,
    xl: 20,
    '2xl': 24,
    full: 9999,
  },
});

export type Theme = ReturnType<typeof getTheme>;
