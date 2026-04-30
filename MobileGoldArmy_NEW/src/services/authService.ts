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
  ForgotPasswordRequest,
  ResetPasswordRequest,
  User,
} from '../types/api.types';

// Types de réponse réels du backend FastAPI (/api/auth/*)
type BackendTokenResponse = {
  access_token: string;
  refresh_token: string; // Vrai refresh token (30 jours) depuis la v2 du backend
  token_type: string;
  user: {
    id: string;
    email: string;
    subscription_tier: string;
  };
};

class AuthService {
  /**
   * Login with Google ID token
   * Backend: POST /api/auth/google { credential }
   */
  async loginWithGoogle(credential: string): Promise<LoginResponse> {
    try {
      const response = await axios.post<BackendTokenResponse>(
        `${API_BASE_URL}/api/auth/google`,
        { credential }
      );

      const data = response.data;

      const user: User = {
        id: data.user.id,
        email: data.user.email,
        firstName: undefined,
        lastName: undefined,
        avatar: undefined,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      };

      return {
        user,
        accessToken: data.access_token,
        // Le backend retourne maintenant un vrai refresh_token (30 jours)
        refreshToken: data.refresh_token || data.access_token,
      };
    } catch (error) {
      console.error('[AuthService][loginWithGoogle]', error);
      throw error;
    }
  }

  /**
   * Login with Apple ID token
   * Backend: POST /api/auth/apple { credential }
   */
  async loginWithApple(credential: string): Promise<LoginResponse> {
    try {
      const response = await axios.post<BackendTokenResponse>(
        `${API_BASE_URL}/api/auth/apple`,
        { credential }
      );

      const data = response.data;

      const user: User = {
        id: data.user.id,
        email: data.user.email,
        firstName: undefined,
        lastName: undefined,
        avatar: undefined,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      };

      return {
        user,
        accessToken: data.access_token,
        refreshToken: data.refresh_token || data.access_token,
      };
    } catch (error) {
      console.error('[AuthService][loginWithApple]', error);
      throw error;
    }
  }

  /**
   * Login user (email + mot de passe)
   * Backend: POST /api/auth/login (OAuth2PasswordRequestForm)
   */
  async login(credentials: LoginRequest): Promise<LoginResponse> {
    try {
      const form = new URLSearchParams();
      form.append('username', credentials.email.trim());
      form.append('password', credentials.password);

      const response = await axios.post<BackendTokenResponse>(
        `${API_BASE_URL}/api/auth/login`,
        form.toString(),
        {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
        }
      );

      const data = response.data;

      const user: User = {
        id: data.user.id,
        email: data.user.email,
        firstName: undefined,
        lastName: undefined,
        avatar: undefined,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      };

      const loginResponse: LoginResponse = {
        user,
        accessToken: data.access_token,
        // Le backend retourne maintenant un vrai refresh_token distinct (30 jours)
        refreshToken: data.refresh_token || data.access_token,
      };

      return loginResponse;
    } catch (error) {
      console.error('[AuthService][login]', error);
      throw error;
    }
  }

  /**
   * Register new user
   * Backend: POST /api/auth/register (JSON {email, password})
   */
  async register(data: RegisterRequest): Promise<RegisterResponse> {
    try {
      const payload = {
        email: data.email,
        password: data.password,
      };

      const response = await axios.post<BackendTokenResponse>(
        `${API_BASE_URL}/api/auth/register`,
        payload
      );

      const backend = response.data;

      const user: User = {
        id: backend.user.id,
        email: backend.user.email,
        firstName: data.firstName,
        lastName: data.lastName,
        avatar: undefined,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      };

      const registerResponse: RegisterResponse = {
        user,
        accessToken: backend.access_token,
        refreshToken: backend.refresh_token || backend.access_token,
      };

      return registerResponse;
    } catch (error) {
      console.error('[AuthService][register]', error);
      throw error;
    }
  }

  /**
   * Logout user (optionnel)
   * On n'a pas d'endpoint dédié, on se contente de nettoyer les tokens côté client.
   */
  async logout(): Promise<void> {
    // Pas d'appel backend nécessaire pour l'instant
    return;
  }

  /**
   * Nettoyage du compte et des données (Suppression)
   * Backend: DELETE /api/auth/me
   */
  async deleteAccount(): Promise<void> {
    try {
      await api.delete('/api/auth/me');
    } catch (error) {
      console.error('[AuthService][deleteAccount]', error);
      throw error;
    }
  }

  /**
   * Get current user
   * Backend: GET /api/auth/me
   */
  async getCurrentUser(): Promise<User> {
    try {
      const response = await api.get<BackendTokenResponse['user']>('/api/auth/me');
      const data = response.data;
      
      const user: User = {
        id: data.id,
        email: data.email,
        firstName: undefined,
        lastName: undefined,
        avatar: undefined,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      };
      
      return user;
    } catch (error) {
      console.error('[AuthService][getCurrentUser]', error);
      throw error;
    }
  }

  /**
   * Request password reset (non implémenté côté backend actuel)
   */
  async forgotPassword(_data: ForgotPasswordRequest): Promise<void> {
    throw new Error('forgotPassword non implémenté côté backend');
  }

  /**
   * Reset password with token (non implémenté côté backend actuel)
   */
  async resetPassword(_data: ResetPasswordRequest): Promise<void> {
    throw new Error('resetPassword non implémenté côté backend');
  }

  /**
   * Refresh token — appelle le vrai endpoint backend /api/auth/refresh
   */
  async refreshToken(_data: { refreshToken: string }): Promise<any> {
    try {
      const response = await axios.post(
        `${API_BASE_URL}/api/auth/refresh`,
        { refreshToken: _data.refreshToken }
      );
      return response.data;
    } catch (error) {
      console.error('[AuthService][refreshToken]', error);
      throw error;
    }
  }

  async sendOtp(email: string): Promise<void> {
    await axios.post(`${API_BASE_URL}/api/auth/send-otp`, { email });
  }

  async verifyOtp(email: string, code: string): Promise<void> {
    await axios.post(`${API_BASE_URL}/api/auth/verify-otp`, { email, code });
  }
}

export const authService = new AuthService();
