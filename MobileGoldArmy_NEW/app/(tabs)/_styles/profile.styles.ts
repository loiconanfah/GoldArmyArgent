import { StyleSheet } from 'react-native';
import { spacing } from '../../../src/theme/spacing';
import { typography } from '../../../src/theme';

export const styles = StyleSheet.create({
  scrollView: {
    flex: 1,
  },
  content: {
    padding: spacing.xl,
    paddingTop: 100,
    alignItems: 'center',
  },
  profileHeader: {
    alignItems: 'center',
    marginBottom: spacing['2xl'],
  },
  name: {
    ...typography.h2,
    marginTop: spacing.lg,
  },
  email: {
    ...typography.body,
    marginTop: spacing.xs,
  },
  card: {
    width: '100%',
    marginBottom: spacing.xl,
  },
  cardTitle: {
    ...typography.h3,
    marginBottom: spacing.sm,
  },
  cardText: {
    ...typography.body,
  },
  logoutButton: {
    marginTop: spacing.xl,
  },
});
