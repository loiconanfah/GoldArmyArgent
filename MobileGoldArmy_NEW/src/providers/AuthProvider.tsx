/**
 * Auth Provider
 * Handles authentication state and token management
 */

import React, { useEffect, useState } from 'react';
import { useRouter, useSegments } from 'expo-router';
import { useAuthStore } from '../stores/authStore';
import { getAccessToken, getRefreshToken, setAccessToken, setRefreshToken, clearTokens } from '../utils/storage';
import { authService } from '../services/authService';
import { useUIStore } from '../stores/uiStore';

interface AuthProviderProps {
  children: React.ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const router = useRouter();
  const segments = useSegments();
  const [isInitialized, setIsInitialized] = useState(false);
  
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
      try {
        setLoading(true);
        
        const accessToken = await getAccessToken();
        const refreshToken = await getRefreshToken();

        if (accessToken && refreshToken) {
          // Try to get current user
          try {
            const currentUser = await authService.getCurrentUser();
            setUser(currentUser);
            setTokens(accessToken, refreshToken);
          } catch (error) {
            // Token invalid, clear storage
            await clearTokens();
            logoutStore();
          }
        }
      } catch (error) {
        console.error('[AuthProvider][initializeAuth]', error);
        await clearTokens();
        logoutStore();
      } finally {
        setLoading(false);
        setIsInitialized(true);
      }
    };

    initializeAuth();
  }, []);

  /**
   * Handle navigation based on auth state
   * Note: Landing page (index) and onboarding are always accessible
   * IMPORTANT: Don't block rendering of index/onboarding routes
   */
  useEffect(() => {
    if (!isInitialized) return;

    const inAuthGroup = segments[0] === '(auth)';
    const inTabsGroup = segments[0] === '(tabs)';
    const isOnLanding = segments.length === 0 || segments[0] === 'index';
    const isOnOnboarding = segments[0] === 'onboarding';

    // Allow landing page (index) and onboarding to be accessible - NEVER redirect from these
    if (isOnLanding || isOnOnboarding) {
      return; // Stay on landing page or onboarding
    }

    // Only redirect if we're in a protected route and not authenticated
    if (!isAuthenticated && inTabsGroup) {
      router.replace('/(auth)/login');
    } else if (isAuthenticated && inAuthGroup) {
      router.replace('/(tabs)/home');
    }
  }, [isAuthenticated, segments, isInitialized, router]);

  // Always render children - don't block index/onboarding routes
  return <>{children}</>;
}
