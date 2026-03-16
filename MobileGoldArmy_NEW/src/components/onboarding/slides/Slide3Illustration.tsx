/**
 * Slide 3 Illustration
 * Tableau kanban avec cards qui se déplacent
 */

import React, { useEffect, useRef } from 'react';
import { View, StyleSheet, Animated, Text } from 'react-native';

interface Slide3IllustrationProps {
  colors: {
    primary: string;
    primaryPale: string;
    surface: string;
    text: string;
  };
}

export function Slide3Illustration({ colors }: Slide3IllustrationProps) {
  const card1X = useRef(new Animated.Value(0)).current;
  const card2X = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    // Card qui glisse de colonne en colonne
    const animateCard = (animValue: Animated.Value, delay: number) => {
      return Animated.loop(
        Animated.sequence([
          Animated.delay(delay),
          Animated.timing(animValue, {
            toValue: 1,
            duration: 2000,
            useNativeDriver: true,
          }),
          Animated.timing(animValue, {
            toValue: 2,
            duration: 2000,
            useNativeDriver: true,
          }),
          Animated.timing(animValue, {
            toValue: 0,
            duration: 2000,
            useNativeDriver: true,
          }),
        ])
      );
    };

    const animations = [
      animateCard(card1X, 0),
      animateCard(card2X, 1000),
    ];

    animations.forEach((anim) => anim.start());

    return () => {
      animations.forEach((anim) => anim.stop());
    };
  }, []);

  const card1TranslateX = card1X.interpolate({
    inputRange: [0, 1, 2],
    outputRange: [0, 100, 200],
  });

  const card2TranslateX = card2X.interpolate({
    inputRange: [0, 1, 2],
    outputRange: [0, 100, 200],
  });

  return (
    <View style={styles.container}>
      {/* Fond décoratif */}
      <View style={[styles.backgroundCircle, { backgroundColor: colors.primary }]} />

      {/* Colonnes Kanban */}
      <View style={styles.kanbanContainer}>
        {/* Colonne 1 - Envoyé */}
        <View style={styles.column}>
          <Text style={[styles.columnTitle, { color: colors.text }]}>Envoyé</Text>
          <View style={[styles.columnContent, { backgroundColor: colors.primaryPale }]}>
            <Animated.View
              style={[
                styles.kanbanCard,
                {
                  transform: [{ translateX: card1TranslateX }],
                  backgroundColor: colors.surface,
                },
              ]}
            >
              <View style={[styles.cardDot, { backgroundColor: colors.primary }]} />
              <View style={[styles.cardLine, { backgroundColor: colors.primary }]} />
            </Animated.View>
          </View>
        </View>

        {/* Colonne 2 - Entretien */}
        <View style={styles.column}>
          <Text style={[styles.columnTitle, { color: colors.text }]}>Entretien</Text>
          <View style={[styles.columnContent, { backgroundColor: colors.primaryPale }]}>
            <Animated.View
              style={[
                styles.kanbanCard,
                {
                  transform: [{ translateX: card2TranslateX }],
                  backgroundColor: colors.surface,
                },
              ]}
            >
              <View style={[styles.cardDot, { backgroundColor: colors.primary }]} />
              <View style={[styles.cardLine, { backgroundColor: colors.primary }]} />
            </Animated.View>
          </View>
        </View>

        {/* Colonne 3 - Offre */}
        <View style={styles.column}>
          <Text style={[styles.columnTitle, { color: colors.text }]}>Offre</Text>
          <View style={[styles.columnContent, { backgroundColor: colors.primaryPale }]} />
        </View>
      </View>

      {/* Petits cercles flottants */}
      <View style={[styles.floatingCircle, styles.circle1, { backgroundColor: colors.primary }]} />
      <View style={[styles.floatingCircle, styles.circle2, { backgroundColor: colors.primary }]} />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    width: '100%',
    height: '100%',
    alignItems: 'center',
    justifyContent: 'center',
    position: 'relative',
  },
  backgroundCircle: {
    position: 'absolute',
    width: 200,
    height: 200,
    borderRadius: 100,
    opacity: 0.08,
    top: -50,
    right: -50,
  },
  kanbanContainer: {
    flexDirection: 'row',
    gap: 12,
    width: '90%',
  },
  column: {
    flex: 1,
    alignItems: 'center',
  },
  columnTitle: {
    fontSize: 11,
    fontWeight: '600',
    marginBottom: 8,
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
  columnContent: {
    width: '100%',
    minHeight: 120,
    borderRadius: 12,
    padding: 8,
    position: 'relative',
  },
  kanbanCard: {
    width: '100%',
    padding: 10,
    borderRadius: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 6,
    elevation: 2,
  },
  cardDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    marginBottom: 6,
  },
  cardLine: {
    height: 4,
    borderRadius: 2,
    marginBottom: 4,
    width: '80%',
  },
  floatingCircle: {
    position: 'absolute',
    borderRadius: 999,
    opacity: 0.15,
  },
  circle1: {
    width: 36,
    height: 36,
    top: 40,
    left: 30,
  },
  circle2: {
    width: 24,
    height: 24,
    bottom: 50,
    right: 40,
  },
});
