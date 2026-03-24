import { StyleSheet } from 'react-native';
import { spacing } from '../../src/theme/spacing';

export const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: '#FAFAFA' },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: spacing.xl,
    paddingBottom: spacing.md,
    backgroundColor: '#FFF',
    borderBottomWidth: 1,
    borderBottomColor: '#F5F5F0',
  },
  backBtn: { padding: spacing.xs },
  markReadBtn: { padding: spacing.xs },
  headerTitle: { fontSize: 18, fontWeight: '700', color: '#1A1A1A' },
  listContent: { padding: spacing.lg, paddingBottom: 100 },
  notifCard: {
    flexDirection: 'row',
    backgroundColor: '#FFF',
    padding: spacing.md,
    borderRadius: 16,
    marginBottom: spacing.sm,
    borderWidth: 1,
    borderColor: '#EFEFEF',
  },
  notifCardUnread: {
    backgroundColor: '#F8FAFC',
    borderColor: '#E2E8F0',
  },
  notifIcon: { marginRight: spacing.md, paddingTop: 2 },
  notifContent: { flex: 1 },
  notifTitle: { fontSize: 15, fontWeight: '600', color: '#1A1A1A', marginBottom: 2 },
  notifMessage: { fontSize: 13, color: '#4B5563', lineHeight: 18 },
  notifTime: { fontSize: 11, fontWeight: '500', color: '#9CA3AF', marginTop: 6 },
  unreadDot: { width: 8, height: 8, borderRadius: 4, backgroundColor: '#3B82F6', alignSelf: 'center', marginLeft: 8 },
  emptyContainer: { alignItems: 'center', marginTop: 100 },
  emptyText: { marginTop: spacing.md, fontSize: 15, color: '#9CA3AF', fontWeight: '500' }
});
