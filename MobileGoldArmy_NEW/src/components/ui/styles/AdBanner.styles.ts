import { StyleSheet, Dimensions } from 'react-native';
import { spacing } from '@theme/spacing';

const { width } = Dimensions.get('window');

export const adBannerStyles = StyleSheet.create({
  container: {
    marginTop: spacing['2xl'],
    marginBottom: spacing.xl,
    paddingHorizontal: spacing.xl,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.md,
  },
  headerTitle: {
    fontSize: 13,
    fontWeight: '700',
    color: '#4A4A46',
    letterSpacing: 0.3,
  },
  scrollContent: {
    paddingRight: spacing.lg,
  },
  adCard: {
    width: width * 0.75,
    marginRight: spacing.md,
    borderRadius: 20,
    overflow: 'hidden',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.12,
    shadowRadius: 16,
    elevation: 6,
  },
  gradient: {
    padding: spacing.lg,
    minHeight: 100,
  },
  adContent: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  adIconContainer: {
    width: 56,
    height: 56,
    borderRadius: 28,
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: spacing.md,
  },
  adTextContainer: {
    flex: 1,
  },
  adTitle: {
    fontSize: 20,
    fontWeight: '800',
    color: '#FFFFFF',
    marginBottom: 4,
    letterSpacing: -0.5,
  },
  adSubtitle: {
    fontSize: 13,
    color: 'rgba(255, 255, 255, 0.9)',
    fontWeight: '600',
  },
  adArrow: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    justifyContent: 'center',
    alignItems: 'center',
    marginLeft: spacing.sm,
  },
});
