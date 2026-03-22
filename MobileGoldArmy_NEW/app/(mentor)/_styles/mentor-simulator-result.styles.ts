import { StyleSheet, Dimensions } from 'react-native';
import { spacing } from '../../../src/theme/spacing';

const { width } = Dimensions.get('window');

export const styles = StyleSheet.create({
  root: {
    flex: 1,
    backgroundColor: '#0F172A', // Premium dark
  },
  scroll: {
    flex: 1,
  },
  content: {
    paddingHorizontal: spacing.xl,
    paddingBottom: 40,
  },
  
  // Header
  headerRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: spacing['2xl'],
  },
  closeBtn: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: 'rgba(255,255,255,0.1)',
    alignItems: 'center',
    justifyContent: 'center',
  },
  headerTitle: {
    fontFamily: 'Inter-Bold',
    fontSize: 20,
    color: '#FFF',
    marginLeft: spacing.md,
  },

  // Loader
  loaderContainer: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    paddingTop: 100,
  },
  loaderText: {
    marginTop: spacing.md,
    fontFamily: 'Inter-Medium',
    fontSize: 16,
    color: '#94A3B8',
  },

  // Summary Card
  summaryCard: {
    backgroundColor: '#1E293B',
    borderRadius: 24,
    padding: spacing.xl,
    alignItems: 'center',
    marginBottom: spacing.xl,
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.05)',
  },
  decisionBadge: {
    paddingHorizontal: 16,
    paddingVertical: 6,
    borderRadius: 20,
    marginBottom: spacing.lg,
  },
  decisionText: {
    fontFamily: 'Inter-Bold',
    fontSize: 14,
    textTransform: 'uppercase',
  },
  scoreRow: {
    flexDirection: 'row',
    alignItems: 'baseline',
  },
  overallScore: {
    fontFamily: 'Inter-Black',
    fontSize: 56,
    color: '#FFF',
  },
  scoreMax: {
    fontFamily: 'Inter-Medium',
    fontSize: 24,
    color: '#64748B',
    marginLeft: 4,
  },
  rolesText: {
    fontFamily: 'Inter-Regular',
    fontSize: 14,
    color: '#94A3B8',
    marginTop: spacing.sm,
    textAlign: 'center',
  },

  // Grid
  scoresGrid: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: spacing.xl,
  },
  miniScoreBox: {
    flex: 1,
    backgroundColor: '#1E293B',
    borderRadius: 16,
    padding: spacing.md,
    alignItems: 'center',
    marginHorizontal: 4,
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.05)',
  },
  miniScoreVal: {
    fontFamily: 'Inter-Bold',
    fontSize: 24,
    color: '#FFF',
    marginBottom: 4,
  },
  miniScoreLabel: {
    fontFamily: 'Inter-Medium',
    fontSize: 10,
    color: '#94A3B8',
    textAlign: 'center',
    textTransform: 'uppercase',
  },

  // Feedback Sections
  section: {
    marginBottom: spacing.xl,
    backgroundColor: '#1E293B',
    borderRadius: 20,
    padding: spacing.xl,
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.05)',
  },
  sectionHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: spacing.lg,
  },
  sectionTitle: {
    fontFamily: 'Inter-SemiBold',
    fontSize: 18,
    color: '#FFF',
    marginLeft: 8,
  },
  pointItemRow: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: spacing.md,
  },
  pointDotContent: {
    width: 20,
    alignItems: 'center',
    marginRight: 8,
    marginTop: 2,
  },
  pointText: {
    flex: 1,
    fontFamily: 'Inter-Regular',
    fontSize: 14,
    color: '#CBD5E1',
    lineHeight: 22,
  },
  adviceText: {
    fontFamily: 'Inter-Regular',
    fontSize: 15,
    color: '#E2E8F0',
    lineHeight: 24,
    fontStyle: 'italic',
  },

  // Action Base
  bottomBtn: {
    backgroundColor: '#4F46E5', // Indigo
    height: 56,
    borderRadius: 28,
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: spacing.md,
    shadowColor: '#4F46E5',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 4,
  },
  bottomBtnText: {
    fontFamily: 'Inter-Bold',
    fontSize: 16,
    color: '#FFF',
  },
});
