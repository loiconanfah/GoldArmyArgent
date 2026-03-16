/**
 * Storage utilities
 * Wrappers around expo-secure-store for secure token storage
 */

import * as SecureStore from 'expo-secure-store';

const TOKEN_KEYS = {
  ACCESS_TOKEN: 'access_token',
  REFRESH_TOKEN: 'refresh_token',
} as const;

/**
 * Store access token securely
 */
export const setAccessToken = async (token: string): Promise<void> => {
  try {
    await SecureStore.setItemAsync(TOKEN_KEYS.ACCESS_TOKEN, token);
  } catch (error) {
    console.error('[Storage][setAccessToken]', error);
    throw error;
  }
};

/**
 * Get access token from secure storage
 */
export const getAccessToken = async (): Promise<string | null> => {
  try {
    return await SecureStore.getItemAsync(TOKEN_KEYS.ACCESS_TOKEN);
  } catch (error) {
    console.error('[Storage][getAccessToken]', error);
    return null;
  }
};

/**
 * Store refresh token securely
 */
export const setRefreshToken = async (token: string): Promise<void> => {
  try {
    await SecureStore.setItemAsync(TOKEN_KEYS.REFRESH_TOKEN, token);
  } catch (error) {
    console.error('[Storage][setRefreshToken]', error);
    throw error;
  }
};

/**
 * Get refresh token from secure storage
 */
export const getRefreshToken = async (): Promise<string | null> => {
  try {
    return await SecureStore.getItemAsync(TOKEN_KEYS.REFRESH_TOKEN);
  } catch (error) {
    console.error('[Storage][getRefreshToken]', error);
    return null;
  }
};

/**
 * Remove all tokens from secure storage
 */
export const clearTokens = async (): Promise<void> => {
  try {
    await Promise.all([
      SecureStore.deleteItemAsync(TOKEN_KEYS.ACCESS_TOKEN),
      SecureStore.deleteItemAsync(TOKEN_KEYS.REFRESH_TOKEN),
    ]);
  } catch (error) {
    console.error('[Storage][clearTokens]', error);
    throw error;
  }
};

/**
 * Store any value securely (generic)
 */
export const setSecureItem = async (key: string, value: string): Promise<void> => {
  try {
    await SecureStore.setItemAsync(key, value);
  } catch (error) {
    console.error('[Storage][setSecureItem]', error);
    throw error;
  }
};

/**
 * Get any value from secure storage (generic)
 */
export const getSecureItem = async (key: string): Promise<string | null> => {
  try {
    return await SecureStore.getItemAsync(key);
  } catch (error) {
    console.error('[Storage][getSecureItem]', error);
    return null;
  }
};

/**
 * Remove item from secure storage
 */
export const removeSecureItem = async (key: string): Promise<void> => {
  try {
    await SecureStore.deleteItemAsync(key);
  } catch (error) {
    console.error('[Storage][removeSecureItem]', error);
    throw error;
  }
};
