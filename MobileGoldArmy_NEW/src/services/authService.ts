/**
 * Authentication Service
 * Handles all authentication-related API calls
 */

import axios from 'axios';
import api from './api';
import { API_BASE_URL } from '@utils/constants';
import type {
  LoginRequest,
  LoginResponse,
  RegisterRequest,
  RegisterResponse,
  RefreshTokenRequest,
  RefreshTokenResponse,
  ForgotPasswordRequest,
  ResetPasswordRequest,
  User,
  ApiResponse,
} from '@types/api.types';
import { API_ENDPOINTS } from '@utils/constants';

class AuthService {
  /**
   * Login user
   */
  async login(credentials: LoginRequest): Promise<LoginResponse> {
    try {
      const response = await api.post<ApiResponse<LoginResponse>>(
        API_ENDPOINTS.AUTH.LOGIN,
        credentials
      );
      return response.data.data;
    } catch (error) {
      console.error('[AuthService][login]', error);
      throw error;
    }
  }

  /**
   * Register new user
   */
  async register(data: RegisterRequest): Promise<RegisterResponse> {
    try {
      const response = await api.post<ApiResponse<RegisterResponse>>(
        API_ENDPOINTS.AUTH.REGISTER,
        data
      );
      return response.data.data;
    } catch (error) {
      console.error('[AuthService][register]', error);
      throw error;
    }
  }

  /**
   * Refresh access token
   */
  async refreshToken(data: RefreshTokenRequest): Promise<RefreshTokenResponse> {
    try {
      const response = await api.post<ApiResponse<RefreshTokenResponse>>(
        API_ENDPOINTS.AUTH.REFRESH,
        data
      );
      return response.data.data;
    } catch (error) {
      console.error('[AuthService][refreshToken]', error);
      throw error;
    }
  }

  /**
   * Logout user
   */
  async logout(): Promise<void> {
    try {
      await api.post(API_ENDPOINTS.AUTH.LOGOUT);
    } catch (error) {
      console.error('[AuthService][logout]', error);
      // Continue with logout even if API call fails
    }
  }

  /**
   * Get current user
   */
  async getCurrentUser(): Promise<User> {
    try {
      const response = await api.get<ApiResponse<User>>(API_ENDPOINTS.AUTH.ME);
      return response.data.data;
    } catch (error) {
      console.error('[AuthService][getCurrentUser]', error);
      throw error;
    }
  }

  /**
   * Request password reset
   */
  async forgotPassword(data: ForgotPasswordRequest): Promise<void> {
    try {
      await api.post(API_ENDPOINTS.AUTH.FORGOT_PASSWORD, data);
    } catch (error) {
      console.error('[AuthService][forgotPassword]', error);
      throw error;
    }
  }

  /**
   * Reset password with token
   */
  async resetPassword(data: ResetPasswordRequest): Promise<void> {
    try {
      await api.post(API_ENDPOINTS.AUTH.RESET_PASSWORD, data);
    } catch (error) {
      console.error('[AuthService][resetPassword]', error);
      throw error;
    }
  }
}

export const authService = new AuthService();
