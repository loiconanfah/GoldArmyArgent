/**
 * Landing Page Test - Version simplifiée pour debug
 */

import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

export default function LandingPageTest() {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Landing Page Test</Text>
      <Text style={styles.subtitle}>Si vous voyez ceci, l'import fonctionne</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#FAFAF8',
    padding: 24,
  },
  title: {
    fontSize: 32,
    fontWeight: '700',
    color: '#1A1A18',
    marginBottom: 16,
  },
  subtitle: {
    fontSize: 16,
    color: '#4A4A46',
  },
});
