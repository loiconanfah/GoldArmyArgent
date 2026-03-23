import { StyleSheet } from 'react-native';

const C = {
  primary: '#FF6B35',
  primarySoft: '#FF8C5A',
  primaryPale: '#FFF0EB',
  primaryDeep: '#E8521A',
  accent: '#FF3D00',
  bg: '#FAFAF8',
  surface: '#FFFFFF',
  surfaceAlt: '#F5F4F0',
  border: '#EAEAE6',
  text: '#1A1A18',
  textMid: '#4A4A46',
  textMuted: '#9A9A94',
  white: '#FFFFFF',
  shadow: 'rgba(255,107,53,0.20)',
  shadowNeutral: 'rgba(0,0,0,0.07)',
};

const SP = { xs: 4, sm: 8, md: 12, lg: 16, xl: 24, xxl: 32, xxxl: 48 };
const R = { sm: 8, md: 14, lg: 20, xl: 28, full: 999 };

export const styles = StyleSheet.create({
  container: {
    flexGrow: 1,
    justifyContent: 'center',
    paddingHorizontal: SP.xl,
    paddingBottom: SP.xxxl,
  },
  content: {
    width: '100%',
    maxWidth: 420,
    alignSelf: 'center',
  },
  logoWrapper: {
    alignItems: 'center',
    marginBottom: SP.xl,
  },
  logoImage: {
    width: 64,
    height: 64,
    marginBottom: SP.sm,
  },
  appName: {
    fontSize: 20,
    fontWeight: '700',
    letterSpacing: 0.6,
    color: C.text,
  },
  title: {
    fontSize: 30,
    fontWeight: '800',
    letterSpacing: -0.8,
    color: C.text,
    textAlign: 'center',
    marginBottom: SP.sm,
  },
  subtitle: {
    fontSize: 15,
    lineHeight: 24,
    color: C.text,
    textAlign: 'center',
    marginBottom: SP.xxl,
  },
  forgotPassword: {
    marginTop: SP.sm,
    alignItems: 'flex-end',
  },
  forgotPasswordText: {
    fontSize: 13,
    color: C.textMuted,
  },
  separator: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: SP.xxl,
    marginBottom: SP.lg,
  },
  separatorLine: {
    flex: 1,
    height: 1,
    backgroundColor: C.border,
  },
  separatorText: {
    marginHorizontal: SP.md,
    fontSize: 13,
    color: C.textMuted,
  },
  googleButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    height: 54,
    borderRadius: R.full,
    backgroundColor: C.white,
    borderWidth: 1.5,
    borderColor: C.border,
    shadowColor: C.shadowNeutral,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 1,
    shadowRadius: 12,
    elevation: 3,
  },
  googleLogo: {
    flexDirection: 'row',
    marginRight: SP.sm,
  },
  googleCircle: {
    width: 6,
    height: 6,
    borderRadius: 3,
    marginHorizontal: 1,
  },
  googleText: {
    fontSize: 15,
    fontWeight: '600',
    color: C.text,
  },
  googleButtonDisabled: {
    opacity: 0.6,
  },
  footer: {
    flexDirection: 'row',
    justifyContent: 'center',
    marginTop: SP.xxl,
  },
  footerText: {
    fontSize: 14,
    color: C.textMid,
  },
  footerLink: {
    fontSize: 14,
    fontWeight: '600',
    color: C.primary,
  },
});
