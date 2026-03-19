import { StyleSheet, Platform } from 'react-native';

export const styles = StyleSheet.create({
  tabBar: {
    position: 'absolute',
    bottom: Platform.OS === 'ios' ? 24 : 16,
    left: 20,
    right: 20,
    backgroundColor: 'rgba(255, 255, 255, 0.85)',
    borderRadius: 32,
    borderTopWidth: 0,
    elevation: 20, // Android shadow
    shadowColor: '#000000',
    shadowOffset: { width: 0, height: 10 },
    shadowOpacity: 0.15,
    shadowRadius: 20,
    height: 64,
    paddingTop: 12,
    paddingBottom: 12,
  },
  tabBarLabel: {
    fontSize: 10,
    fontWeight: '600',
    marginTop: -4,
    marginBottom: 4,
  },
  blurView: {
    ...StyleSheet.absoluteFillObject,
    borderRadius: 32,
    overflow: 'hidden',
  },
});
