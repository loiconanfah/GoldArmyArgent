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
} from '@types/api.types';

// Types de réponse réels du backend FastAPI (/api/auth/*)
type BackendTokenResponse = {
  access_token: string;
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
        refreshToken: data.access_token,
      };
    } catch (error) {
      console.error('[AuthService][loginWithGoogle]', error);
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
      form.append('username', credentials.email);
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
        // Le backend ne renvoie pas de refresh_token pour l'instant,
        // on réutilise access_token pour rester compatible avec le reste de l'app.
        refreshToken: data.access_token,
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
        refreshToken: backend.access_token,
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
   * Get current user (optionnel)
   * Si besoin, on pourra créer un endpoint backend spécifique.
   */
  async getCurrentUser(): Promise<User> {
    throw new Error('getCurrentUser non implémenté côté backend');
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
}

export const authService = new AuthService();
