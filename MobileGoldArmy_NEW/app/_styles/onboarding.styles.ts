import { StyleSheet, Dimensions } from 'react-native';

const { width: SCREEN_WIDTH } = Dimensions.get('window');

// Couleurs alignées sur le thème global de l'app
const C = {
  primary: '#F5D061', // gold / couleur principale du logo
  primarySoft: '#F8DC8A',
  primaryPale: '#FFF8DC',
  primaryDeep: '#E6A32F',
  accent: '#3B82F6', // bleu secondaire de l'app
  bg: '#FFFFFF',
  surface: '#FFFFFF',
  border: '#E0E0E0',
  text: '#1A1A1A',
  textMid: '#666666',
};

export const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: C.bg,
  },
  dotsContainer: {
    position: 'absolute',
    bottom: 100,
    left: 0,
    right: 0,
    alignItems: 'center',
  },
  highlightWrapper: {
    alignItems: 'center',
  },
  highlightTitle: {
    fontSize: 18,
    fontWeight: '700',
    color: C.text,
    marginBottom: 8,
  },
  progressBarBg: {
    width: '100%',
    height: 8,
    backgroundColor: C.primaryPale,
    borderRadius: 4,
    overflow: 'hidden',
  },
  progressBarFill: {
    width: '94%',
    height: '100%',
    backgroundColor: C.primary,
    borderRadius: 4,
  },
  highlightSubtitle: {
    fontSize: 13,
    color: C.textMid,
  },
});

export { C };
