/**
 * API Client
 * Axios instance with JWT interceptors for authentication
 */

import axios, { AxiosError, AxiosInstance, InternalAxiosRequestConfig } from 'axios';
import { API_BASE_URL } from '@utils/constants';
import { getAccessToken, getRefreshToken, setAccessToken, setRefreshToken, clearTokens } from '@utils/storage';
import type { ApiError, RefreshTokenResponse } from '@types/api.types';
import { authService } from './authService';

/**
 * Create axios instance
 */
const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Request interceptor: Inject access token
 */
api.interceptors.request.use(
  async (config: InternalAxiosRequestConfig) => {
    try {
      const token = await getAccessToken();
      if (token && config.headers) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    } catch (error) {
      console.error('[API][Request Interceptor]', error);
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

/**
 * Response interceptor: Handle 401 errors and refresh token
 */
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError<ApiError>) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

    // If error is 401 and we haven't retried yet
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        // Get refresh token
        const refreshToken = await getRefreshToken();
        
        if (!refreshToken) {
          // No refresh token, logout user
          await clearTokens();
          // Redirect to login will be handled by auth guard
          return Promise.reject(error);
        }

        // Attempt to refresh access token using separate axios instance to avoid loop
        const refreshApi = axios.create({
          baseURL: API_BASE_URL,
          timeout: 30000,
        });
        
        const response = await refreshApi.post<ApiResponse<RefreshTokenResponse>>(
          API_ENDPOINTS.AUTH.REFRESH,
          { refreshToken }
        );
        
        const tokenData = response.data.data;
        
        // Store new tokens
        await setAccessToken(tokenData.accessToken);
        await setRefreshToken(tokenData.refreshToken);

        // Update authorization header and retry original request
        if (originalRequest.headers) {
          originalRequest.headers.Authorization = `Bearer ${tokenData.accessToken}`;
        }

        return api(originalRequest);
      } catch (refreshError) {
        // Refresh failed, logout user
        console.error('[API][Refresh Token Failed]', refreshError);
        await clearTokens();
        // Redirect to login will be handled by auth guard
        return Promise.reject(refreshError);
      }
    }

    // Return error for non-401 or already retried requests
    return Promise.reject(error);
  }
);

export default api;
