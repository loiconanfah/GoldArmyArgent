/**
 * UI Store
 * Zustand store for UI state (modals, toasts, loading)
 */

import { create } from 'zustand';

export type ToastType = 'success' | 'error' | 'warning' | 'info';

export interface Toast {
  id: string;
  message: string;
  type: ToastType;
  duration?: number;
}

interface UIState {
  toasts: Toast[];
  isLoading: boolean;
  loadingMessage?: string;
}

interface UIActions {
  showToast: (message: string, type?: ToastType, duration?: number) => void;
  hideToast: (id: string) => void;
  clearToasts: () => void;
  setLoading: (loading: boolean, message?: string) => void;
}

type UIStore = UIState & UIActions;

export const useUIStore = create<UIStore>()((set) => ({
  toasts: [],
  isLoading: false,
  loadingMessage: undefined,

  showToast: (message, type = 'info', duration = 3000) =>
    set((state) => {
      const id = Date.now().toString();
      const newToasts = [...state.toasts, { id, message, type, duration }];
      
      // Auto-hide after duration
      if (duration > 0) {
        setTimeout(() => {
          useUIStore.getState().hideToast(id);
        }, duration);
      }
      
      return {
        ...state,
        toasts: newToasts,
      };
    }),

  hideToast: (id) =>
    set((state) => ({
      ...state,
      toasts: state.toasts.filter((toast) => toast.id !== id),
    })),

  clearToasts: () =>
    set((state) => ({
      ...state,
      toasts: [],
    })),

  setLoading: (loading, message) =>
    set((state) => ({
      ...state,
      isLoading: loading,
      loadingMessage: message,
    })),
}));
