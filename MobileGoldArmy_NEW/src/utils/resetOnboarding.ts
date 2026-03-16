/**
 * Utility to reset onboarding status
 * Use this for testing or to allow users to see onboarding again
 */

import * as SecureStore from 'expo-secure-store';

/**
 * Reset onboarding status
 * This will make the onboarding appear again on next app launch
 */
export async function resetOnboarding(): Promise<void> {
  try {
    await SecureStore.deleteItemAsync('onboarding_completed');
    console.log('[resetOnboarding] Onboarding status reset successfully');
  } catch (error) {
    console.error('[resetOnboarding] Error resetting onboarding:', error);
    throw error;
  }
}

/**
 * Check if onboarding is completed
 */
export async function isOnboardingCompleted(): Promise<boolean> {
  try {
    const value = await SecureStore.getItemAsync('onboarding_completed');
    return value === 'true';
  } catch (error) {
    console.error('[isOnboardingCompleted] Error checking onboarding:', error);
    return false;
  }
}

/**
 * Mark onboarding as completed
 */
export async function completeOnboarding(): Promise<void> {
  try {
    await SecureStore.setItemAsync('onboarding_completed', 'true');
    console.log('[completeOnboarding] Onboarding marked as completed');
  } catch (error) {
    console.error('[completeOnboarding] Error completing onboarding:', error);
    throw error;
  }
}
