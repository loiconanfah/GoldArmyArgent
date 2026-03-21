import { StyleSheet, Platform } from 'react-native';

export const styles = StyleSheet.create({
  tabBar: {
    position: 'absolute',
    bottom: Platform.OS === 'ios' ? 22 : 14,
    left: 14,
    right: 14,
    backgroundColor: Platform.OS === 'ios' ? 'transparent' : 'rgba(17, 24, 39, 0.92)', // slate-900
    borderRadius: 22,
    borderWidth: Platform.OS === 'ios' ? 1 : 0,
    borderColor: 'rgba(255, 255, 255, 0.08)',
    elevation: Platform.OS === 'ios' ? 0 : 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.2,
    shadowRadius: 18,
    height: 70,
    paddingTop: 8,
    paddingBottom: Platform.OS === 'ios' ? 2 : 10,
  },
  tabBarLabel: {
    fontSize: 11,
    fontWeight: '700',
    marginTop: 0,
    marginBottom: 0,
  },
  blurView: {
    ...StyleSheet.absoluteFillObject,
    borderRadius: 22,
    overflow: 'hidden',
  },
  iconWrap: {
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: 10,
    paddingVertical: 8,
    borderRadius: 14,
    gap: 4,
  },
  iconWrapActive: {
    backgroundColor: '#F59E0B', // amber-500
  },
  iconLabel: {
    fontSize: 10,
    fontWeight: '700',
    color: '#94A3B8', // slate-400
  },
  iconLabelActive: {
    color: '#111827', // slate-900
  },
});

// Expo Router route placeholder to silence route warning for style-only files.
const _RoutePlaceholder = () => null;
export default _RoutePlaceholder;

