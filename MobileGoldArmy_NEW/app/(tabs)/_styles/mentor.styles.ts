import { StyleSheet } from 'react-native';
import { spacing } from '../../../src/theme/spacing';

export const styles = StyleSheet.create({
  root: {
    flex: 1,
    backgroundColor: '#FAFAF8',
  },
  scroll: {
    flex: 1,
  },
  content: {
    paddingHorizontal: spacing.xl,
    gap: spacing.xl,
  },
  hero: {
    flexDirection: 'row',
    alignItems: 'flex-start',
  },
  heroIcon: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: '#F5D061',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: spacing.md,
  },
  heroTextContainer: {
    flex: 1,
  },
  heroTitle: {
    fontSize: 24,
    fontWeight: '800',
    color: '#1A1A1A',
  },
  heroSubtitle: {
    fontSize: 13,
    color: '#666666',
    marginTop: 4,
  },
  heroEyebrow: {
    fontSize: 11,
    fontWeight: '600',
    color: '#999999',
    letterSpacing: 0.5,
    textTransform: 'uppercase',
    marginBottom: 2,
  },
  nextBadge: {
    alignItems: 'flex-end',
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    borderRadius: 12,
    backgroundColor: '#FFF7D6',
    marginLeft: spacing.md,
  },
  nextBadgeLabel: {
    fontSize: 10,
    fontWeight: '600',
    color: '#92400E',
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
  nextBadgeValue: {
    fontSize: 12,
    fontWeight: '700',
    color: '#1A1A1A',
  },
  actionsRow: {
    flexDirection: 'row',
    gap: spacing.md,
  },
  actionCard: {
    flex: 1,
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    padding: spacing.lg,
    borderWidth: 1,
    borderColor: '#EAEAE6',
  },
  actionTag: {
    fontSize: 11,
    fontWeight: '600',
    color: '#999999',
    textTransform: 'uppercase',
    marginBottom: spacing.sm,
  },
  actionIconWrapper: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: '#FFF7D6',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: spacing.sm,
  },
  actionTitle: {
    fontSize: 15,
    fontWeight: '700',
    color: '#1A1A1A',
    marginBottom: 4,
  },
  actionSubtitle: {
    fontSize: 12,
    color: '#666666',
    marginBottom: spacing.md,
  },
  actionFooter: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 'auto',
    backgroundColor: '#F5F5F0',
    paddingVertical: spacing.sm,
    paddingHorizontal: spacing.md,
    borderRadius: 12,
    justifyContent: 'center',
  },
  actionCta: {
    fontSize: 12,
    fontWeight: '700',
    color: '#1A1A1A',
    marginRight: 6,
  },
  historySection: {
    marginTop: spacing.sm,
  },
  historyHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'baseline',
    marginBottom: spacing.sm,
  },
  historyTitle: {
    fontSize: 18,
    fontWeight: '700',
    color: '#1A1A1A',
  },
  historyCount: {
    fontSize: 12,
    fontWeight: '500',
    color: '#666666',
  },
  filterRow: {
    flexDirection: 'row',
    gap: spacing.sm,
    marginBottom: spacing.sm,
  },
  filterPill: {
    fontSize: 12,
    fontWeight: '500',
    color: '#666666',
  },
  filterPillActive: {
    color: '#1A1A1A',
    textDecorationLine: 'underline',
  },
  historyList: {
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    borderWidth: 1,
    borderColor: '#EAEAE6',
  },
  historyCard: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
    borderBottomWidth: StyleSheet.hairlineWidth,
    borderBottomColor: '#EAEAE6',
  },
  historyLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  historyIcon: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: '#F5F5F3',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: spacing.md,
  },
  historyInfo: {
    flex: 1,
  },
  historyTitleText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#1A1A1A',
    marginBottom: 2,
  },
  historyCompany: {
    fontSize: 12,
    color: '#666666',
    marginBottom: 2,
  },
  historyDate: {
    fontSize: 12,
    color: '#999999',
  },
  historyRight: {
    alignItems: 'flex-end',
    justifyContent: 'space-between',
  },
  scoreBadge: {
    backgroundColor: '#ECFDF5',
    borderRadius: 999,
    paddingHorizontal: 8,
    paddingVertical: 2,
    marginBottom: spacing.xs,
  },
  scoreText: {
    fontSize: 12,
    fontWeight: '700',
    color: '#047857',
  },
  statusBadge: {
    borderRadius: 999,
    paddingHorizontal: 10,
    paddingVertical: 4,
  },
  statusPlanned: {
    backgroundColor: '#EFF6FF',
  },
  statusDone: {
    backgroundColor: '#ECFDF5',
  },
  statusCancelled: {
    backgroundColor: '#FEF2F2',
  },
  statusText: {
    fontSize: 11,
    fontWeight: '600',
    color: '#1A1A1A',
  },
  tipsSection: {
    marginTop: spacing.xl,
    marginBottom: spacing['2xl'],
  },
  tipsTitle: {
    fontSize: 18,
    fontWeight: '700',
    color: '#1A1A1A',
    marginBottom: spacing.sm,
  },
  tipsList: {
    gap: spacing.sm,
  },
  tipCard: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    backgroundColor: '#FFFFFF',
    borderRadius: 14,
    padding: spacing.md,
    borderWidth: 1,
    borderColor: '#EAEAE6',
  },
  tipIcon: {
    width: 28,
    height: 28,
    borderRadius: 14,
    backgroundColor: '#F5F5F3',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: spacing.md,
  },
  tipContent: {
    flex: 1,
  },
  tipTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#1A1A1A',
    marginBottom: 2,
  },
  tipDesc: {
    fontSize: 12,
    color: '#666666',
  },
});

// Expo Router route placeholder to silence route warning for style-only files.
const _RoutePlaceholder = () => null;
export default _RoutePlaceholder;

