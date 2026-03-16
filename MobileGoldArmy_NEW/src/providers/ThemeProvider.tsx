/**
 * Theme Provider
 * Provides theme context and utilities
 */

import React, { createContext, useContext, useEffect } from 'react';
import { useColorScheme as useRNColorScheme } from 'react-native';
import { useThemeStore } from '../stores/themeStore';
import { getTheme, type Theme } from '../theme';

interface ThemeContextValue {
  theme: Theme;
  colorScheme: 'light' | 'dark';
  toggleTheme: () => void;
}

const ThemeContext = createContext<ThemeContextValue | undefined>(undefined);

interface ThemeProviderProps {
  children: React.ReactNode;
}

export function ThemeProvider({ children }: ThemeProviderProps) {
  const systemColorScheme = useRNColorScheme();
  const { colorScheme, isSystemTheme, setColorScheme, toggleTheme } = useThemeStore();

  // Use system theme if enabled
  const effectiveColorScheme = isSystemTheme && systemColorScheme
    ? systemColorScheme
    : colorScheme;

  // Get theme based on effective color scheme
  const theme = getTheme(effectiveColorScheme);

  const value: ThemeContextValue = {
    theme,
    colorScheme: effectiveColorScheme,
    toggleTheme,
  };

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  );
}

/**
 * Hook to access theme
 */
export function useTheme(): ThemeContextValue {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within ThemeProvider');
  }
  return context;
}
