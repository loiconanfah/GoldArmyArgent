/**
 * Auth Provider
 * Handles authentication state and token management
 */

import React, { useEffect, useState } from 'react';
import { useRouter, useSegments, useRootNavigationState } from 'expo-router';
import { useAuthStore } from '../stores/authStore';
import { getAccessToken, getRefreshToken, setAccessToken, setRefreshToken, clearTokens } from '../utils/storage';
import { authService } from '../services/authService';
import { notificationService } from '../services/notificationService';
import { useUIStore } from '../stores/uiStore';
import { usePushNotifications } from '../hooks/usePushNotifications';

interface AuthProviderProps {
  children: React.ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const router = useRouter();
  const segments = useSegments();
  const rootNavigationState = useRootNavigationState();
  const [isInitialized, setIsInitialized] = useState(false);
  const { expoPushToken } = usePushNotifications();
  
  const { 
    user, 
    isAuthenticated, 
    setUser, 
    setTokens, 
    setLoading,
    logout: logoutStore 
  } = useAuthStore();
  
  const { showToast } = useUIStore();

  /**
   * Initialize auth state from storage
   */
  useEffect(() => {
    const initializeAuth = async () => {
      console.log('[AuthProvider] Initializing auth...');
      try {
        setLoading(true);
        
        const accessToken = await getAccessToken();
        const refreshToken = await getRefreshToken();
        console.log('[AuthProvider] Tokens from storage:', !!accessToken, !!refreshToken);

        if (accessToken && refreshToken) {
          try {
            console.log('[AuthProvider] Fetching current user...');
            const currentUser = await authService.getCurrentUser();
            console.log('[AuthProvider] User fetched:', !!currentUser);
            setUser(currentUser);
            setTokens(accessToken, refreshToken);
          } catch (error) {
            console.warn('[AuthProvider] Failed to fetch current user, clearing tokens');
            await clearTokens();
            logoutStore();
          }
        }
      } catch (error) {
        console.error('[AuthProvider] Global initialization error:', error);
        await clearTokens();
        logoutStore();
      } finally {
        setLoading(false);
        setIsInitialized(true);
        console.log('[AuthProvider] Initialized.');
      }
    };

    initializeAuth();
  }, []);

  /**
   * Sync push token when authenticated
   */
  useEffect(() => {
    if (isAuthenticated && expoPushToken) {
      console.log('[AuthProvider] Registering push token:', expoPushToken);
      // notificationService.registerPushToken(expoPushToken)
      //   .catch(err => console.error('Failed to sync push token:', err));
    }
  }, [isAuthenticated, expoPushToken]);

  /**
   * Handle navigation based on auth state
   * Note: Landing page (index) and onboarding are always accessible
   * IMPORTANT: Don't block rendering of index/onboarding routes
   */
  useEffect(() => {
    if (!isInitialized || !rootNavigationState?.key) return;

    const isProtectedRoute = 
      segments[0] === '(tabs)' || 
      segments[0] === '(mentor)' || 
      segments[0] === '(offers)' ||
      segments[0] === 'settings' ||
      segments[0] === 'notifications';
    
    const isPublicRoute = 
      segments[0] === '(auth)' || 
      segments[0] === 'onboarding' || 
      (segments as string[]).length === 0;

    // Logic: If logged in, don't stay on public/intro pages
    if (isAuthenticated) {
      if (!isProtectedRoute) {
        router.replace('/(tabs)/home');
      }
    } 
    // Logic: If not logged in, don't allow protected regions
    else {
      if (isProtectedRoute) {
        router.replace('/(auth)/login');
      }
    }
  }, [isAuthenticated, segments, isInitialized, router, rootNavigationState?.key]);

  // Always render children - don't block index/onboarding routes
  return <>{children}</>;
}
