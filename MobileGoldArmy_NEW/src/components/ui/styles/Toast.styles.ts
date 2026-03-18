import { StyleSheet } from 'react-native';
import { spacing } from '@theme/spacing';
import { shadows } from '@theme/shadows';

export const toastStyles = StyleSheet.create({
  container: {
    marginBottom: spacing.sm,
  },
  blur: {
    borderRadius: 12,
    overflow: 'hidden',
    ...shadows.lg,
  },
  toast: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: spacing.md,
    borderLeftWidth: 4,
    minHeight: 48,
  },
  icon: {
    marginRight: spacing.md,
  },
  message: {
    flex: 1,
    fontSize: 14,
    fontWeight: '500',
  },
  closeButton: {
    padding: spacing.xs,
    marginLeft: spacing.sm,
  },
});

export const toastContainerStyles = StyleSheet.create({
  container: {
    position: 'absolute',
    top: 60,
    left: spacing.lg,
    right: spacing.lg,
    zIndex: 9999,
  },
});
