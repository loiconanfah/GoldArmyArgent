/**
 * Auth Store
 * Zustand store for authentication state
 */

import { create } from 'zustand';
import type { User } from '../types/api.types';

interface AuthState {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

interface AuthActions {
  setUser: (user: User | null) => void;
  setTokens: (accessToken: string, refreshToken: string) => void;
  setAccessToken: (token: string) => void;
  setRefreshToken: (token: string) => void;
  setLoading: (loading: boolean) => void;
  logout: () => void;
  reset: () => void;
}

type AuthStore = AuthState & AuthActions;

const initialState: AuthState = {
  user: null,
  accessToken: null,
  refreshToken: null,
  isAuthenticated: false,
  isLoading: false,
};

export const useAuthStore = create<AuthStore>()((set) => ({
  ...initialState,

  setUser: (user) =>
    set((state) => ({
      ...state,
      user,
      isAuthenticated: user !== null,
    })),

  setTokens: (accessToken, refreshToken) =>
    set((state) => ({
      ...state,
      accessToken,
      refreshToken,
      isAuthenticated: true,
    })),

  setAccessToken: (token) =>
    set((state) => ({
      ...state,
      accessToken: token,
    })),

  setRefreshToken: (token) =>
    set((state) => ({
      ...state,
      refreshToken: token,
    })),

  setLoading: (loading) =>
    set((state) => ({
      ...state,
      isLoading: loading,
    })),

  logout: () =>
    set((state) => ({
      ...state,
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
    })),

  reset: () =>
    set(() => ({
      ...initialState,
    })),
}));
