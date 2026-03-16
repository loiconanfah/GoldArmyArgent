/**
 * useAuth Hook
 * Custom hook for authentication operations
 */

import { useAuthStore } from '../stores/authStore';
import { authService } from '../services/authService';
import { setAccessToken, setRefreshToken, clearTokens } from '../utils/storage';
import { useUIStore } from '../stores/uiStore';
import { useRouter } from 'expo-router';

export function useAuth() {
  const router = useRouter();
  const { 
    user, 
    isAuthenticated, 
    isLoading,
    setUser, 
    setTokens,
    setLoading,
    logout: logoutStore 
  } = useAuthStore();
  
  const { showToast } = useUIStore();

  /**
   * Login user
   */
  const login = async (email: string, password: string) => {
    try {
      setLoading(true);

      // TEMP: backend inactif → on crée une session locale mockée
      const fakeUser = {
        id: 'local-user',
        full_name: email,
        email,
        avatar_url: undefined,
        created_at: new Date().toISOString(),
      } as any;

      const fakeAccessToken = 'local-access-token';
      const fakeRefreshToken = 'local-refresh-token';

      await setAccessToken(fakeAccessToken);
      await setRefreshToken(fakeRefreshToken);

      setUser(fakeUser);
      setTokens(fakeAccessToken, fakeRefreshToken);

      showToast('Connecté (session locale)', 'success');
      router.replace('/(tabs)/home');
    } finally {
      setLoading(false);
    }
  };

  /**
   * Register user
   */
  const register = async (email: string, password: string, firstName?: string, lastName?: string) => {
    try {
      setLoading(true);
      const response = await authService.register({ email, password, firstName, lastName });
      
      await setAccessToken(response.accessToken);
      await setRefreshToken(response.refreshToken);
      
      setUser(response.user);
      setTokens(response.accessToken, response.refreshToken);
      
      showToast('Registration successful', 'success');
      router.replace('/(tabs)/home');
    } catch (error: any) {
      const message = error.response?.data?.message || 'Registration failed';
      showToast(message, 'error');
      throw error;
    } finally {
      setLoading(false);
    }
  };

  /**
   * Logout user
   */
  const logout = async () => {
    try {
      setLoading(true);
      await authService.logout();
    } catch (error) {
      console.error('[useAuth][logout]', error);
    } finally {
      await clearTokens();
      logoutStore();
      router.replace('/(auth)/login');
      setLoading(false);
    }
  };

  /**
   * Refresh tokens
   */
  const refreshToken = async () => {
    try {
      const refreshToken = await authService.refreshToken({ refreshToken: '' });
      // This is handled by the API interceptor, but we can expose it if needed
      return refreshToken;
    } catch (error) {
      console.error('[useAuth][refreshToken]', error);
      await logout();
      throw error;
    }
  };

  return {
    user,
    isAuthenticated,
    isLoading,
    login,
    register,
    logout,
    refreshToken,
  };
}
