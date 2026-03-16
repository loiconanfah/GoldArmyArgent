/**
 * Slide 4 Illustration
 * Réseau de connexions avec lignes qui se tracent progressivement
 */

import React, { useEffect, useRef } from 'react';
import { View, StyleSheet, Animated } from 'react-native';

interface Slide4IllustrationProps {
  colors: {
    primary: string;
    primaryPale: string;
    surface: string;
  };
}

export function Slide4Illustration({ colors }: Slide4IllustrationProps) {
  const line1Width = useRef(new Animated.Value(0)).current;
  const line2Width = useRef(new Animated.Value(0)).current;
  const line3Width = useRef(new Animated.Value(0)).current;
  const line4Width = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    // Lignes qui se tracent progressivement en séquence
    const animateLine = (animValue: Animated.Value, delay: number) => {
      return Animated.sequence([
        Animated.delay(delay),
        Animated.timing(animValue, {
          toValue: 1,
          duration: 800,
          useNativeDriver: false,
        }),
      ]);
    };

    Animated.sequence([
      animateLine(line1Width, 0),
      animateLine(line2Width, 200),
      animateLine(line3Width, 400),
      animateLine(line4Width, 600),
    ]).start();

    // Loop après 3 secondes
    const loop = setInterval(() => {
      line1Width.setValue(0);
      line2Width.setValue(0);
      line3Width.setValue(0);
      line4Width.setValue(0);

      Animated.sequence([
        animateLine(line1Width, 0),
        animateLine(line2Width, 200),
        animateLine(line3Width, 400),
        animateLine(line4Width, 600),
      ]).start();
    }, 3000);

    return () => clearInterval(loop);
  }, []);

  const line1AnimatedWidth = line1Width.interpolate({
    inputRange: [0, 1],
    outputRange: ['0%', '100%'],
  });

  const line2AnimatedWidth = line2Width.interpolate({
    inputRange: [0, 1],
    outputRange: ['0%', '100%'],
  });

  const line3AnimatedWidth = line3Width.interpolate({
    inputRange: [0, 1],
    outputRange: ['0%', '100%'],
  });

  const line4AnimatedWidth = line4Width.interpolate({
    inputRange: [0, 1],
    outputRange: ['0%', '100%'],
  });

  return (
    <View style={styles.container}>
      {/* Fond décoratif */}
      <View style={[styles.backgroundCircle, { backgroundColor: colors.primary }]} />

      {/* Nœuds du réseau */}
      <View style={styles.networkContainer}>
        {/* Nœud central */}
        <View style={[styles.node, styles.nodeCenter, { backgroundColor: colors.primary }]}>
          <View style={[styles.nodeInner, { backgroundColor: colors.surface }]} />
        </View>

        {/* Nœud 1 (haut gauche) */}
        <View style={[styles.node, styles.node1, { backgroundColor: colors.primaryPale }]}>
          <View style={[styles.nodeInner, { backgroundColor: colors.primary }]} />
        </View>

        {/* Nœud 2 (haut droite) */}
        <View style={[styles.node, styles.node2, { backgroundColor: colors.primaryPale }]}>
          <View style={[styles.nodeInner, { backgroundColor: colors.primary }]} />
        </View>

        {/* Nœud 3 (bas gauche) */}
        <View style={[styles.node, styles.node3, { backgroundColor: colors.primaryPale }]}>
          <View style={[styles.nodeInner, { backgroundColor: colors.primary }]} />
        </View>

        {/* Nœud 4 (bas droite) */}
        <View style={[styles.node, styles.node4, { backgroundColor: colors.primaryPale }]}>
          <View style={[styles.nodeInner, { backgroundColor: colors.primary }]} />
        </View>

        {/* Lignes de connexion */}
        <View style={[styles.lineContainer, styles.line1]}>
          <Animated.View
            style={[
              styles.line,
              {
                width: line1AnimatedWidth,
                backgroundColor: colors.primary,
              },
            ]}
          />
        </View>

        <View style={[styles.lineContainer, styles.line2]}>
          <Animated.View
            style={[
              styles.line,
              {
                width: line2AnimatedWidth,
                backgroundColor: colors.primary,
              },
            ]}
          />
        </View>

        <View style={[styles.lineContainer, styles.line3]}>
          <Animated.View
            style={[
              styles.line,
              {
                width: line3AnimatedWidth,
                backgroundColor: colors.primary,
              },
            ]}
          />
        </View>

        <View style={[styles.lineContainer, styles.line4]}>
          <Animated.View
            style={[
              styles.line,
              {
                width: line4AnimatedWidth,
                backgroundColor: colors.primary,
              },
            ]}
          />
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
    width: 220,
    height: 220,
    borderRadius: 110,
    opacity: 0.08,
    top: -60,
    left: -60,
  },
  networkContainer: {
    width: 200,
    height: 200,
    position: 'relative',
  },
  node: {
    width: 48,
    height: 48,
    borderRadius: 24,
    position: 'absolute',
    alignItems: 'center',
    justifyContent: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 3,
  },
  nodeInner: {
    width: 24,
    height: 24,
    borderRadius: 12,
  },
  nodeCenter: {
    top: 76,
    left: 76,
  },
  node1: {
    top: 0,
    left: 20,
  },
  node2: {
    top: 0,
    right: 20,
  },
  node3: {
    bottom: 0,
    left: 20,
  },
  node4: {
    bottom: 0,
    right: 20,
  },
  lineContainer: {
    position: 'absolute',
    overflow: 'hidden',
  },
  line: {
    height: 2,
    borderRadius: 1,
  },
  line1: {
    top: 24,
    left: 44,
    width: 60,
    transform: [{ rotate: '-45deg' }],
  },
  line2: {
    top: 24,
    right: 44,
    width: 60,
    transform: [{ rotate: '45deg' }],
  },
  line3: {
    bottom: 24,
    left: 44,
    width: 60,
    transform: [{ rotate: '45deg' }],
  },
  line4: {
    bottom: 24,
    right: 44,
    width: 60,
    transform: [{ rotate: '-45deg' }],
  },
  floatingCircle: {
    position: 'absolute',
    borderRadius: 999,
    opacity: 0.15,
  },
  circle1: {
    width: 40,
    height: 40,
    top: 50,
    left: 30,
  },
  circle2: {
    width: 28,
    height: 28,
    bottom: 50,
    right: 30,
  },
});
