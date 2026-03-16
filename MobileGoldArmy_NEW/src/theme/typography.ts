/**
 * Typography system
 * Defines font families, sizes, weights, and line heights
 */

export const fontFamilies = {
  regular: 'System',
  medium: 'System',
  semibold: 'System',
  bold: 'System',
};

export const fontSizes = {
  xs: 12,
  sm: 14,
  base: 16,
  lg: 18,
  xl: 20,
  '2xl': 24,
  '3xl': 28,
  '4xl': 32,
  '5xl': 42,
  '6xl': 48,
};

export const fontWeights = {
  regular: '400' as const,
  medium: '500' as const,
  semibold: '600' as const,
  bold: '700' as const,
  extrabold: '800' as const,
  black: '900' as const,
};

export const lineHeights = {
  none: 1,
  tight: 1.25,
  snug: 1.375,
  normal: 1.5,
  relaxed: 1.625,
  loose: 2,
};

export const letterSpacing = {
  tighter: -0.5,
  tight: -0.25,
  normal: 0,
  wide: 0.25,
  wider: 0.5,
  widest: 1,
};

export const typography = {
  // Hero text (landing pages, main titles)
  hero: {
    fontSize: fontSizes['5xl'],
    fontWeight: fontWeights.black,
    lineHeight: lineHeights.tight,
    letterSpacing: letterSpacing.tighter,
  },
  
  // Page titles
  h1: {
    fontSize: fontSizes['4xl'],
    fontWeight: fontWeights.bold,
    lineHeight: lineHeights.tight,
    letterSpacing: letterSpacing.tight,
  },
  
  h2: {
    fontSize: fontSizes['3xl'],
    fontWeight: fontWeights.bold,
    lineHeight: lineHeights.snug,
    letterSpacing: letterSpacing.normal,
  },
  
  h3: {
    fontSize: fontSizes['2xl'],
    fontWeight: fontWeights.semibold,
    lineHeight: lineHeights.snug,
    letterSpacing: letterSpacing.normal,
  },
  
  h4: {
    fontSize: fontSizes.xl,
    fontWeight: fontWeights.semibold,
    lineHeight: lineHeights.normal,
    letterSpacing: letterSpacing.normal,
  },
  
  // Body text
  body: {
    fontSize: fontSizes.base,
    fontWeight: fontWeights.regular,
    lineHeight: lineHeights.relaxed,
    letterSpacing: letterSpacing.normal,
  },
  
  bodyLarge: {
    fontSize: fontSizes.lg,
    fontWeight: fontWeights.regular,
    lineHeight: lineHeights.relaxed,
    letterSpacing: letterSpacing.normal,
  },
  
  // Small text
  small: {
    fontSize: fontSizes.sm,
    fontWeight: fontWeights.regular,
    lineHeight: lineHeights.normal,
    letterSpacing: letterSpacing.wide,
  },
  
  caption: {
    fontSize: fontSizes.xs,
    fontWeight: fontWeights.regular,
    lineHeight: lineHeights.normal,
    letterSpacing: letterSpacing.wide,
  },
  
  // Button text
  button: {
    fontSize: fontSizes.base,
    fontWeight: fontWeights.semibold,
    lineHeight: lineHeights.none,
    letterSpacing: letterSpacing.wide,
  },
  
  buttonLarge: {
    fontSize: fontSizes.lg,
    fontWeight: fontWeights.bold,
    lineHeight: lineHeights.none,
    letterSpacing: letterSpacing.wider,
  },
};
