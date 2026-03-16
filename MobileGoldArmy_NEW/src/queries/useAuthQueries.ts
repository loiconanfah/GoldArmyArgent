/**
 * Auth Queries
 * React Query hooks for authentication
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { authService } from '@services/authService';
import type { User } from '@types/api.types';

/**
 * Get current user query
 */
export function useCurrentUser() {
  return useQuery({
    queryKey: ['auth', 'me'],
    queryFn: () => authService.getCurrentUser(),
    staleTime: 1000 * 60 * 5, // 5 minutes
    retry: 1,
  });
}

/**
 * Login mutation
 */
export function useLoginMutation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: authService.login,
    onSuccess: (data) => {
      // Invalidate and refetch user data
      queryClient.setQueryData(['auth', 'me'], data.user);
    },
  });
}

/**
 * Register mutation
 */
export function useRegisterMutation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: authService.register,
    onSuccess: (data) => {
      // Invalidate and refetch user data
      queryClient.setQueryData(['auth', 'me'], data.user);
    },
  });
}
