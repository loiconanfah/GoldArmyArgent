import { StyleSheet } from 'react-native';
import { spacing } from '@theme/spacing';

export const inputStyles = StyleSheet.create({
  container: {
    marginBottom: spacing.lg,
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    borderWidth: 2,
    borderRadius: 12,
    backgroundColor: '#FFFFFF',
    minHeight: 52,
    position: 'relative',
  },
  inputError: {
    borderWidth: 2,
  },
  input: {
    flex: 1,
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
    fontSize: 16,
    fontWeight: '500',
  },
  inputWithLeftIcon: {
    paddingLeft: spacing.sm,
  },
  inputWithRightIcon: {
    paddingRight: spacing.sm,
  },
  leftIcon: {
    paddingLeft: spacing.md,
  },
  rightIcon: {
    paddingRight: spacing.md,
  },
  labelContainer: {
    position: 'absolute',
    paddingHorizontal: spacing.xs,
    zIndex: 1,
  },
  label: {
    fontSize: 13,
    fontWeight: '600',
  },
  helperText: {
    fontSize: 12,
    marginTop: spacing.xs,
    marginLeft: spacing.md,
  },
});
