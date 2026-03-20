/**
 * Application constants
 * Global constants used throughout the app
 */

import { Platform } from 'react-native';
import Constants from 'expo-constants';

const envApiUrl = process.env.EXPO_PUBLIC_API_URL;
const CLOUD_API_BASE_URL = 'https://goldarmy.onrender.com';
export const APP_ENV = process.env.EXPO_PUBLIC_APP_ENV || 'development';

function inferDevApiBaseUrl(): string {
  // Expo exposes the Metro host (ex: 192.168.1.10:8081), useful for physical devices.
  const hostUri = Constants.expoConfig?.hostUri ?? '';
  const host = hostUri.split(':')[0];

  // Android emulator cannot reach localhost directly; use the emulator loopback.
  if (Platform.OS === 'android') {
    return 'http://10.0.2.2:8000';
  }

  // iOS simulator / web can access local loopback.
  if (Platform.OS === 'ios' || Platform.OS === 'web') {
    return 'http://127.0.0.1:8000';
  }

  // Physical devices should call the machine IP running Uvicorn.
  if (host) {
    return `http://${host}:8000`;
  }

  return 'http://127.0.0.1:8000';
}

// Priority:
// 1) explicit env override
// 2) reliable cloud backend (prevents mobile timeouts when local backend is unreachable)
// 3) local inference fallback
export const API_BASE_URL = envApiUrl || CLOUD_API_BASE_URL || inferDevApiBaseUrl();

export const IS_DEV = APP_ENV === 'development';
export const IS_PROD = APP_ENV === 'production';

// API endpoints
export const API_ENDPOINTS = {
  AUTH: {
    LOGIN: '/auth/login',
    REGISTER: '/auth/register',
    REFRESH: '/auth/refresh',
    LOGOUT: '/auth/logout',
    FORGOT_PASSWORD: '/auth/forgot-password',
    RESET_PASSWORD: '/auth/reset-password',
    ME: '/auth/me',
  },
  CRM: {
    FETCH: '/api/crm',
    CREATE: '/api/crm',
    UPDATE: (id: string) => `/api/crm/${id}`,
    DELETE: (id: string) => `/api/crm/${id}`,
    LINK: '/api/crm/link',
    FOLLOWUP: (id: string) => `/api/crm/applications/${id}/followup`,
  },
} as const;

// Storage keys
export const STORAGE_KEYS = {
  ACCESS_TOKEN: 'access_token',
  REFRESH_TOKEN: 'refresh_token',
  USER: 'user',
  THEME: 'theme',
} as const;

// Animation durations (ms)
export const ANIMATION_DURATION = {
  FAST: 200,
  NORMAL: 300,
  SLOW: 500,
} as const;

// Debounce delays (ms)
export const DEBOUNCE_DELAY = {
  SEARCH: 300,
  INPUT: 500,
} as const;

// Pagination defaults
export const PAGINATION = {
  DEFAULT_PAGE: 1,
  DEFAULT_LIMIT: 20,
  MAX_LIMIT: 100,
} as const;
