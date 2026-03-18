import { StyleSheet } from 'react-native';
import { spacing } from '@theme/spacing';

export const cardStyles = StyleSheet.create({
  card: {
    borderRadius: 16,
    borderWidth: 1,
    overflow: 'hidden',
  },
  content: {
    padding: spacing.lg,
  },
});
