import { StyleSheet } from 'react-native';
import { spacing } from '../../../src/theme/spacing';

export const styles = StyleSheet.create({
  root: {
    flex: 1,
    backgroundColor: '#F3EEE7',
  },
  list: {
    flex: 1,
  },
  listContent: {
    paddingHorizontal: spacing.lg,
    paddingBottom: spacing['3xl'],
    paddingTop: spacing.sm,
  },
  center: {
    justifyContent: 'center',
    alignItems: 'center',
  },
  fab: {
    position: 'absolute',
    right: 20,
    bottom: 26,
    width: 56,
    height: 56,
    borderRadius: 28,
    backgroundColor: '#FF6B35',
    alignItems: 'center',
    justifyContent: 'center',
    shadowColor: 'rgba(255,107,53,0.6)',
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 1,
    shadowRadius: 14,
    elevation: 4,
  },
  fabIcon: {
    fontSize: 28,
    color: '#FFFFFF',
    marginTop: -2,
  },
});

// Expo Router route placeholder to silence route warning for style-only files.
const _RoutePlaceholder = () => null;
export default _RoutePlaceholder;

