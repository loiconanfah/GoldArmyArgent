/**
 * Application constants
 * Global constants used throughout the app
 */

export const API_BASE_URL = process.env.EXPO_PUBLIC_API_URL || 'https://your-api.onrender.com';
export const APP_ENV = process.env.EXPO_PUBLIC_APP_ENV || 'development';

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
