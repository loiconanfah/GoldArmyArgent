import { StyleSheet, Dimensions } from 'react-native';
import { spacing } from '../../../src/theme/spacing';

const { width } = Dimensions.get('window');

export const styles = StyleSheet.create({
  root: {
    flex: 1,
    backgroundColor: '#FAFAF8',
  },
  scrollView: {
    flex: 1,
  },
  content: {
    paddingHorizontal: spacing.lg,
    paddingBottom: 140, // Extreme padding to scroll past absolute Navbar
  },
  // Abstract background decor
  abstractGlow1: {
    position: 'absolute',
    top: -100,
    right: -100,
    width: 300,
    height: 300,
    borderRadius: 150,
    backgroundColor: '#F5D061',
    opacity: 0.04,
    transform: [{ scale: 1.5 }],
  },
  abstractGlow2: {
    position: 'absolute',
    top: 200,
    left: -150,
    width: 350,
    height: 350,
    borderRadius: 175,
    backgroundColor: '#60A5FA',
    opacity: 0.03,
    transform: [{ scale: 1.2 }],
  },
  // Hero
  hero: {
    marginBottom: spacing['2xl'],
    marginTop: spacing.md,
  },
  heroRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.sm,
  },
  heroDate: {
    fontSize: 10,
    fontWeight: '800',
    letterSpacing: 2,
    marginBottom: 6,
    color: '#A0A0A0',
  },
  heroTitle: {
    fontSize: 28,
    fontWeight: '800',
    letterSpacing: -0.5,
    color: '#1A1A1A',
  },
  heroName: {
    color: '#F5D061',
  },
  avatarPlaceholder: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: '#333333',
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 2,
    borderColor: '#F5D061',
    shadowColor: '#F5D061',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.5,
    shadowRadius: 10,
  },
  heroSubtitle: {
    fontSize: 14,
    lineHeight: 22,
    maxWidth: '85%',
    color: '#6A6A64',
  },
  // Bento Stats
  statsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
    marginBottom: spacing['xl'],
  },
  statBox: {
    width: (width - spacing.xl * 2 - spacing.md) / 2,
    padding: spacing.md,
    borderRadius: 24,
    backgroundColor: '#FFFFFF',
    marginBottom: spacing.md,
    shadowColor: '#000000',
    shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 0.04,
    shadowRadius: 16,
    elevation: 2,
  },
  statIconBox: {
    width: 36,
    height: 36,
    borderRadius: 10,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: spacing.sm,
  },
  statValue: {
    fontSize: 24,
    fontWeight: '800',
    letterSpacing: -0.5,
    color: '#1A1A1A',
  },
  statLabel: {
    fontSize: 12,
    fontWeight: '600',
    marginTop: 2,
    color: '#9A9A94',
  },
  // Tools Section
  toolsSection: {
    marginBottom: spacing.xl,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.lg,
  },
  sectionTitle: {
    fontSize: 22,
    fontWeight: '800',
    letterSpacing: -0.5,
    color: '#1A1A1A',
  },
  // Tool Cards
  toolCard: {
    borderRadius: 24,
    marginBottom: spacing.xl,
    backgroundColor: '#FFFFFF',
    borderWidth: 1,
    borderColor: '#F0F0EA',
    shadowColor: '#000000',
    shadowOffset: { width: 0, height: 16 },
    shadowOpacity: 0.04,
    shadowRadius: 32,
    elevation: 6,
    overflow: 'hidden',
  },
  toolHeroContent: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: spacing.lg,
    paddingBottom: spacing.md,
  },
  toolHeroLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  toolHeroIconBubble: {
    width: 44,
    height: 44,
    borderRadius: 16,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: spacing.md,
  },
  toolTitleWrapper: {
    flex: 1,
    paddingRight: spacing.md,
  },
  toolHeroTitle: {
    color: '#1A1A1A',
    fontSize: 17,
    fontWeight: '800',
    letterSpacing: -0.3,
    marginBottom: 2,
  },
  toolHeroSubtitle: {
    color: '#9A9A94',
    fontSize: 13,
    fontWeight: '500',
  },
  toolHeroChip: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 999,
  },
  toolHeroChipText: {
    fontSize: 11,
    fontWeight: '800',
    marginLeft: 6,
    letterSpacing: 0.5,
    textTransform: 'uppercase',
  },
  toolActionArea: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: spacing.lg,
    paddingBottom: spacing.lg,
  },
  toolActionText: {
    fontSize: 13,
    fontWeight: '700',
    color: '#1A1A1A',
    marginRight: 6,
  },
  toolMetrics: {
    flexDirection: 'row',
    borderTopWidth: 1,
    borderTopColor: '#F4F4F0',
    paddingVertical: spacing.md,
    paddingHorizontal: spacing.lg,
    backgroundColor: '#FDFDFD',
  },
  toolMetricItem: {
    marginRight: spacing.xl,
    flexDirection: 'row',
    alignItems: 'baseline',
  },
  toolMetricValue: {
    fontSize: 15,
    fontWeight: '800',
    color: '#1A1A1A',
    marginRight: 4,
  },
  toolMetricLabel: {
    fontSize: 11,
    fontWeight: '700',
    color: '#A0A0A0',
    letterSpacing: 0.5,
    textTransform: 'uppercase',
  },
  // Conseils Section
  tipsSection: {
    marginBottom: spacing['3xl'],
  },
  tipsScrollContainer: {
    paddingRight: spacing.lg,
  },
  seeAllText: {
    fontSize: 13,
    fontWeight: '700',
    color: '#FF6B35',
  },
  tipCard: {
    width: width * 0.75,
    backgroundColor: '#FFFFFF',
    borderRadius: 24,
    padding: spacing.lg,
    marginRight: spacing.md,
    borderWidth: 1,
    borderColor: '#F0F0EA',
    shadowColor: '#000000',
    shadowOffset: { width: 0, height: 12 },
    shadowOpacity: 0.03,
    shadowRadius: 20,
    elevation: 4,
  },
  tipIconBox: {
    width: 40,
    height: 40,
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: spacing.md,
  },
  tipTitle: {
    fontSize: 16,
    fontWeight: '800',
    color: '#1A1A1A',
    marginBottom: spacing.xs,
  },
  tipDesc: {
    fontSize: 13,
    color: '#6A6A64',
    lineHeight: 20,
  },
  // Sniper Search Card Wrapper
  sniperCardWrapper: {
    marginBottom: spacing['3xl'],
    marginTop: spacing.md,
  },
});

// Expo Router route placeholder to silence route warning for style-only files.
const _RoutePlaceholder = () => null;
export default _RoutePlaceholder;

