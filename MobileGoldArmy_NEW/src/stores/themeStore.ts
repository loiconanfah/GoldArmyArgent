/**
 * Theme Store
 * Zustand store for theme (dark/light mode)
 */

import { create } from 'zustand';
import type { ColorScheme } from '../theme/colors';

interface ThemeState {
  colorScheme: ColorScheme;
  isSystemTheme: boolean;
}

interface ThemeActions {
  setColorScheme: (scheme: ColorScheme) => void;
  toggleTheme: () => void;
  setSystemTheme: (enabled: boolean) => void;
}

type ThemeStore = ThemeState & ThemeActions;

export const useThemeStore = create<ThemeStore>()((set) => ({
  colorScheme: 'dark',
  isSystemTheme: false,

  setColorScheme: (scheme) =>
    set((state) => ({
      ...state,
      colorScheme: scheme,
      isSystemTheme: false,
    })),

  toggleTheme: () =>
    set((state) => ({
      ...state,
      colorScheme: state.colorScheme === 'dark' ? 'light' : 'dark',
      isSystemTheme: false,
    })),

  setSystemTheme: (enabled) =>
    set((state) => ({
      ...state,
      isSystemTheme: enabled,
    })),
}));
