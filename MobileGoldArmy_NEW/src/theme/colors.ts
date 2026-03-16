/**
 * Color palette for the application
 * Supports both light and dark modes
 */

export const lightColors = {
  // Primary colors
  primary: '#F5D061',
  primaryDark: '#E6A32F',
  primaryLight: '#F8DC8A',
  
  // Secondary colors
  secondary: '#3B82F6',
  secondaryDark: '#2563EB',
  secondaryLight: '#60A5FA',
  
  // Accent colors
  accent: '#9B59B6',
  accentDark: '#8E44AD',
  accentLight: '#BB86FC',
  
  // Background colors
  background: '#FFFFFF',
  backgroundSecondary: '#F5F5F5',
  surface: '#FFFFFF',
  surfaceElevated: '#FFFFFF',
  
  // Text colors
  text: '#1A1A1A',
  textSecondary: '#666666',
  textMuted: '#999999',
  textInverse: '#FFFFFF',
  
  // Border colors
  border: '#E0E0E0',
  borderLight: '#F0F0F0',
  
  // Status colors
  success: '#10B981',
  error: '#EF4444',
  warning: '#F59E0B',
  info: '#3B82F6',
  
  // Overlay
  overlay: 'rgba(0, 0, 0, 0.5)',
  overlayLight: 'rgba(0, 0, 0, 0.1)',
};

export const darkColors = {
  // Primary colors
  primary: '#F5D061',
  primaryDark: '#E6A32F',
  primaryLight: '#F8DC8A',
  
  // Secondary colors
  secondary: '#60A5FA',
  secondaryDark: '#3B82F6',
  secondaryLight: '#93C5FD',
  
  // Accent colors
  accent: '#BB86FC',
  accentDark: '#9B59B6',
  accentLight: '#D4B5FF',
  
  // Background colors
  background: '#0A0A0F',
  backgroundSecondary: '#1A1A1F',
  surface: 'rgba(255, 255, 255, 0.06)',
  surfaceElevated: 'rgba(255, 255, 255, 0.12)',
  
  // Text colors
  text: '#FFFFFF',
  textSecondary: 'rgba(255, 255, 255, 0.7)',
  textMuted: 'rgba(255, 255, 255, 0.5)',
  textInverse: '#1A1A1A',
  
  // Border colors
  border: 'rgba(255, 255, 255, 0.1)',
  borderLight: 'rgba(255, 255, 255, 0.05)',
  
  // Status colors
  success: '#10B981',
  error: '#EF4444',
  warning: '#F59E0B',
  info: '#3B82F6',
  
  // Overlay
  overlay: 'rgba(0, 0, 0, 0.7)',
  overlayLight: 'rgba(0, 0, 0, 0.3)',
};

export type ColorScheme = 'light' | 'dark';

export const getColors = (scheme: ColorScheme) => {
  return scheme === 'dark' ? darkColors : lightColors;
};
