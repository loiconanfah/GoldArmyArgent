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

    const isProtectedRoute = 
      segments[0] === '(tabs)' || 
      segments[0] === '(mentor)' || 
      segments[0] === '(offers)' ||
      segments[0] === 'settings';
    
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
  }, [isAuthenticated, segments, isInitialized, router]);

  // Always render children - don't block index/onboarding routes
  return <>{children}</>;
}
