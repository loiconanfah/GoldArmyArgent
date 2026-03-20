import { StyleSheet, Dimensions } from 'react-native';
import { spacing } from '../../../src/theme/spacing';

const { width } = Dimensions.get('window');

export const styles = StyleSheet.create({
  root: {
    flex: 1,
    backgroundColor: '#FAFAF8',
  },
  scroll: {
    flex: 1,
  },
  content: {
    paddingHorizontal: 20,
    paddingBottom: 140, // Space for Navbar
  },
  // Hero Header
  heroSection: {
    alignItems: 'center',
    paddingVertical: 30,
    marginBottom: 20,
  },
  avatarContainer: {
    position: 'relative',
    marginBottom: 16,
  },
  avatar: {
    width: 100,
    height: 100,
    borderRadius: 50,
    backgroundColor: '#333',
    borderWidth: 3,
    borderColor: '#F5D061',
    shadowColor: '#F5D061',
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.3,
    shadowRadius: 15,
  },
  editAvatarBtn: {
    position: 'absolute',
    bottom: 0,
    right: 0,
    backgroundColor: '#111',
    width: 32,
    height: 32,
    borderRadius: 16,
    borderWidth: 2,
    borderColor: '#FFF',
    justifyContent: 'center',
    alignItems: 'center',
  },
  userName: {
    fontSize: 24,
    fontWeight: '900',
    color: '#1A1A1A',
    letterSpacing: -0.5,
  },
  userEmail: {
    fontSize: 14,
    color: '#9A9A94',
    fontWeight: '600',
    marginTop: 4,
  },
  tierBadge: {
    marginTop: 12,
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 99,
    backgroundColor: '#111',
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
  },
  tierText: {
    color: '#F5D061',
    fontSize: 10,
    fontWeight: '900',
    letterSpacing: 1,
    textTransform: 'uppercase',
  },
  // Bento Stats
  statsRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 24,
  },
  statCard: {
    width: (width - 40 - 12) / 2,
    backgroundColor: '#FFF',
    borderRadius: 20,
    padding: 16,
    borderWidth: 1,
    borderColor: '#F0F0EA',
  },
  statValue: {
    fontSize: 20,
    fontWeight: '900',
    color: '#1A1A1A',
  },
  statLabel: {
    fontSize: 11,
    color: '#9A9A94',
    fontWeight: '700',
    marginTop: 2,
  },
  // Sections
  section: {
    marginBottom: 24,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
    paddingHorizontal: 4,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '800',
    color: '#1A1A1A',
    letterSpacing: -0.3,
  },
  editLink: {
    fontSize: 13,
    fontWeight: '700',
    color: '#6366F1',
  },
  // Info Card
  infoCard: {
    backgroundColor: '#FFF',
    borderRadius: 24,
    padding: 20,
    borderWidth: 1,
    borderColor: '#F0F0EA',
    gap: 16,
  },
  infoItem: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  infoIconBox: {
    width: 36,
    height: 36,
    borderRadius: 12,
    backgroundColor: '#F9F9F7',
    justifyContent: 'center',
    alignItems: 'center',
  },
  infoLabel: {
    fontSize: 11,
    color: '#9A9A94',
    fontWeight: '700',
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
  infoValue: {
    fontSize: 14,
    color: '#1A1A1A',
    fontWeight: '600',
    marginTop: 1,
  },
  // CV Section
  cvCard: {
    backgroundColor: '#FFF',
    borderRadius: 24,
    padding: 20,
    borderWidth: 1,
    borderColor: '#F0F0EA',
  },
  cvTextContainer: {
    backgroundColor: '#F9F9F7',
    borderRadius: 16,
    padding: 16,
    minHeight: 100,
  },
  cvText: {
    fontSize: 13,
    lineHeight: 20,
    color: '#4B5563',
    fontWeight: '500',
  },
  // Logout
  logoutBtn: {
    marginTop: 12,
    marginBottom: 40,
    height: 56,
    borderRadius: 18,
    backgroundColor: '#FFF1F1',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 10,
    borderWidth: 1,
    borderColor: '#FEE2E2',
  },
  logoutText: {
    color: '#EF4444',
    fontSize: 15,
    fontWeight: '800',
  },
  // Modal Edit
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.5)',
    justifyContent: 'flex-end',
  },
  modalContent: {
    backgroundColor: '#FFF',
    borderTopLeftRadius: 32,
    borderTopRightRadius: 32,
    padding: 24,
    maxHeight: '80%',
  },
  modalTitle: {
    fontSize: 20,
    fontWeight: '900',
    color: '#111',
    marginBottom: 20,
  },
  inputLabel: {
    fontSize: 12,
    fontWeight: '800',
    color: '#9CA3AF',
    marginBottom: 8,
    textTransform: 'uppercase',
  },
  input: {
    backgroundColor: '#F3F4F6',
    borderRadius: 12,
    padding: 16,
    fontSize: 15,
    color: '#111',
    marginBottom: 20,
  },
  textArea: {
    height: 200,
    textAlignVertical: 'top',
  },
  saveBtn: {
    backgroundColor: '#111',
    height: 56,
    borderRadius: 16,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 12,
  },
  saveBtnText: {
    color: '#FFF',
    fontSize: 16,
    fontWeight: '800',
  },
  cancelBtn: {
    height: 56,
    justifyContent: 'center',
    alignItems: 'center',
  },
  cancelBtnText: {
    color: '#9CA3AF',
    fontSize: 15,
    fontWeight: '700',
  },
});

// Expo Router route placeholder to silence route warning for style-only files.
const _RoutePlaceholder = () => null;
export default _RoutePlaceholder;

