/**
 * Configuration de l'API GoldArmy
 * En dev: utilise localhost:8000 (backend FastAPI)
 * En prod: définir EXPO_PUBLIC_API_URL ou utiliser l'URL de ton backend (ex: https://goldarmy.onrender.com)
 */
import { Platform } from 'react-native';

const getBaseUrl = () => {
  if (typeof process !== 'undefined' && process.env?.EXPO_PUBLIC_API_URL) {
    return process.env.EXPO_PUBLIC_API_URL.replace(/\/$/, '');
  }
  // Sur simulateur iOS, localhost fonctionne; sur Android émulateur utiliser 10.0.2.2
  if (__DEV__) {
    return Platform.OS === 'android' ? 'http://10.0.2.2:8000' : 'http://localhost:8000';
  }
  return 'https://goldarmy.onrender.com';
};

export const API_BASE_URL = getBaseUrl();

export const getApiUrl = (path) => {
  const cleanPath = path.startsWith('/') ? path : `/${path}`;
  return `${API_BASE_URL}${cleanPath}`;
};

export const getWsUrl = (path) => {
  const cleanPath = path.startsWith('/') ? path : `/${path}`;
  const wsBase = API_BASE_URL.replace(/^http/, 'ws');
  return `${wsBase}${cleanPath}`;
};
