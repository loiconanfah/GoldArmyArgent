/**
 * useHaptics Hook
 * Wrapper for expo-haptics with error handling
 */

import * as Haptics from 'expo-haptics';

export function useHaptics() {
  const impact = async (style: Haptics.ImpactFeedbackStyle = Haptics.ImpactFeedbackStyle.Medium) => {
    try {
      await Haptics.impactAsync(style);
    } catch (error) {
      // Silent fail if haptics not available
      console.debug('[useHaptics] Haptics not available');
    }
  };

  const notification = async (type: Haptics.NotificationFeedbackType) => {
    try {
      await Haptics.notificationAsync(type);
    } catch (error) {
      console.debug('[useHaptics] Haptics not available');
    }
  };

  const selection = async () => {
    try {
      await Haptics.selectionAsync();
    } catch (error) {
      console.debug('[useHaptics] Haptics not available');
    }
  };

  return {
    impact,
    notification,
    selection,
  };
}
