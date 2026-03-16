/**
 * Slide 2 Illustration
 * Simulation de conversation entretien avec bulles de dialogue
 */

import React, { useEffect, useRef } from 'react';
import { View, StyleSheet, Animated } from 'react-native';

interface Slide2IllustrationProps {
  colors: {
    primary: string;
    primaryPale: string;
    surface: string;
  };
}

export function Slide2Illustration({ colors }: Slide2IllustrationProps) {
  const bubble1Opacity = useRef(new Animated.Value(0)).current;
  const bubble1Scale = useRef(new Animated.Value(0.9)).current;
  const bubble2Opacity = useRef(new Animated.Value(0)).current;
  const bubble2Scale = useRef(new Animated.Value(0.9)).current;
  const bubble3Opacity = useRef(new Animated.Value(0)).current;
  const bubble3Scale = useRef(new Animated.Value(0.9)).current;

  useEffect(() => {
    // Bulles qui apparaissent alternativement
    const animateBubble = (
      opacity: Animated.Value,
      scale: Animated.Value,
      delay: number
    ) => {
      return Animated.loop(
        Animated.sequence([
          Animated.delay(delay),
          Animated.parallel([
            Animated.timing(opacity, {
              toValue: 1,
              duration: 400,
              useNativeDriver: true,
            }),
            Animated.spring(scale, {
              toValue: 1,
              useNativeDriver: true,
              stiffness: 200,
              damping: 15,
            }),
          ]),
          Animated.delay(1200),
          Animated.parallel([
            Animated.timing(opacity, {
              toValue: 0,
              duration: 300,
              useNativeDriver: true,
            }),
            Animated.timing(scale, {
              toValue: 0.9,
              duration: 300,
              useNativeDriver: true,
            }),
          ]),
        ])
      );
    };

    const animations = [
      animateBubble(bubble1Opacity, bubble1Scale, 0),
      animateBubble(bubble2Opacity, bubble2Scale, 600),
      animateBubble(bubble3Opacity, bubble3Scale, 1200),
    ];

    animations.forEach((anim) => anim.start());

    return () => {
      animations.forEach((anim) => anim.stop());
    };
  }, []);

  return (
    <View style={styles.container}>
      {/* Fond décoratif */}
      <View style={[styles.backgroundCircle, { backgroundColor: colors.primary }]} />

      {/* Avatar RH */}
      <View style={[styles.avatar, styles.avatarLeft, { backgroundColor: colors.primaryPale }]}>
        <View style={[styles.avatarDot, { backgroundColor: colors.primary }]} />
      </View>

      {/* Bulle RH 1 */}
      <Animated.View
        style={[
          styles.bubble,
          styles.bubbleLeft,
          {
            opacity: bubble1Opacity,
            transform: [{ scale: bubble1Scale }],
            backgroundColor: colors.surface,
          },
        ]}
      >
        <View style={[styles.bubbleLine, { backgroundColor: colors.primary }]} />
        <View style={[styles.bubbleLine, styles.bubbleLineShort, { backgroundColor: colors.primary }]} />
      </Animated.View>

      {/* Avatar Candidat */}
      <View style={[styles.avatar, styles.avatarRight, { backgroundColor: colors.primaryPale }]}>
        <View style={[styles.avatarDot, { backgroundColor: colors.primary }]} />
      </View>

      {/* Bulle Candidat */}
      <Animated.View
        style={[
          styles.bubble,
          styles.bubbleRight,
          {
            opacity: bubble2Opacity,
            transform: [{ scale: bubble2Scale }],
            backgroundColor: colors.primaryPale,
          },
        ]}
      >
        <View style={[styles.bubbleLine, { backgroundColor: colors.primary }]} />
        <View style={[styles.bubbleLine, styles.bubbleLineShort, { backgroundColor: colors.primary }]} />
      </Animated.View>

      {/* Bulle RH 2 */}
      <Animated.View
        style={[
          styles.bubble,
          styles.bubbleLeft,
          styles.bubbleBottom,
          {
            opacity: bubble3Opacity,
            transform: [{ scale: bubble3Scale }],
            backgroundColor: colors.surface,
          },
        ]}
      >
        <View style={[styles.bubbleLine, { backgroundColor: colors.primary }]} />
      </Animated.View>

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
    width: 180,
    height: 180,
    borderRadius: 90,
    opacity: 0.08,
    top: -30,
    left: -30,
  },
  avatar: {
    width: 40,
    height: 40,
    borderRadius: 20,
    position: 'absolute',
    alignItems: 'center',
    justifyContent: 'center',
  },
  avatarLeft: {
    left: 40,
    top: 80,
  },
  avatarRight: {
    right: 40,
    top: 160,
  },
  avatarDot: {
    width: 20,
    height: 20,
    borderRadius: 10,
  },
  bubble: {
    position: 'absolute',
    padding: 12,
    borderRadius: 16,
    maxWidth: 180,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 2,
  },
  bubbleLeft: {
    left: 90,
    top: 70,
  },
  bubbleRight: {
    right: 90,
    top: 150,
  },
  bubbleBottom: {
    top: 220,
  },
  bubbleLine: {
    height: 6,
    borderRadius: 3,
    marginBottom: 4,
    width: '100%',
  },
  bubbleLineShort: {
    width: '70%',
  },
  floatingCircle: {
    position: 'absolute',
    borderRadius: 999,
    opacity: 0.15,
  },
  circle1: {
    width: 32,
    height: 32,
    top: 50,
    right: 50,
  },
  circle2: {
    width: 20,
    height: 20,
    bottom: 60,
    left: 60,
  },
});
