/**
 * Slide 1 Illustration
 * Personnage devant un écran avec des offres d'emploi
 */

import React, { useEffect, useRef } from 'react';
import { View, StyleSheet, Animated, Dimensions } from 'react-native';

const { width: SCREEN_WIDTH } = Dimensions.get('window');

interface Slide1IllustrationProps {
  colors: {
    primary: string;
    primaryPale: string;
  };
}

export function Slide1Illustration({ colors }: Slide1IllustrationProps) {
  const card1Y = useRef(new Animated.Value(0)).current;
  const card2Y = useRef(new Animated.Value(0)).current;
  const card3Y = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    // Cards qui tombent doucement en boucle
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
            toValue: 0,
            duration: 2000,
            useNativeDriver: true,
          }),
        ])
      );
    };

    const animations = [
      animateCard(card1Y, 0),
      animateCard(card2Y, 400),
      animateCard(card3Y, 800),
    ];

    animations.forEach((anim) => anim.start());

    return () => {
      animations.forEach((anim) => anim.stop());
    };
  }, []);

  const card1TranslateY = card1Y.interpolate({
    inputRange: [0, 1],
    outputRange: [0, 20],
  });

  const card2TranslateY = card2Y.interpolate({
    inputRange: [0, 1],
    outputRange: [0, 25],
  });

  const card3TranslateY = card3Y.interpolate({
    inputRange: [0, 1],
    outputRange: [0, 18],
  });

  return (
    <View style={styles.container}>
      {/* Fond décoratif */}
      <View style={[styles.backgroundCircle, { backgroundColor: colors.primary }]} />
      
      {/* Écran central */}
      <View style={styles.screen}>
        <View style={styles.screenContent}>
          {/* Cards d'offres qui tombent */}
          <Animated.View
            style={[
              styles.jobCard,
              {
                transform: [{ translateY: card1TranslateY }],
                backgroundColor: colors.primaryPale,
              },
            ]}
          >
            <View style={[styles.cardLine, { backgroundColor: colors.primary }]} />
            <View style={[styles.cardLine, { backgroundColor: colors.primary }]} />
          </Animated.View>

          <Animated.View
            style={[
              styles.jobCard,
              styles.jobCard2,
              {
                transform: [{ translateY: card2TranslateY }],
                backgroundColor: colors.primaryPale,
              },
            ]}
          >
            <View style={[styles.cardLine, { backgroundColor: colors.primary }]} />
            <View style={[styles.cardLine, { backgroundColor: colors.primary }]} />
          </Animated.View>

          <Animated.View
            style={[
              styles.jobCard,
              styles.jobCard3,
              {
                transform: [{ translateY: card3TranslateY }],
                backgroundColor: colors.primaryPale,
              },
            ]}
          >
            <View style={[styles.cardLine, { backgroundColor: colors.primary }]} />
            <View style={[styles.cardLine, { backgroundColor: colors.primary }]} />
          </Animated.View>
        </View>
      </View>

      {/* Petits cercles flottants */}
      <Animated.View style={[styles.floatingCircle, styles.circle1, { backgroundColor: colors.primary }]} />
      <Animated.View style={[styles.floatingCircle, styles.circle2, { backgroundColor: colors.primary }]} />
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
  screen: {
    width: 200,
    height: 240,
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    padding: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.1,
    shadowRadius: 12,
    elevation: 4,
  },
  screenContent: {
    flex: 1,
    position: 'relative',
  },
  jobCard: {
    position: 'absolute',
    width: '90%',
    height: 50,
    borderRadius: 8,
    padding: 8,
    left: '5%',
  },
  jobCard2: {
    top: 60,
  },
  jobCard3: {
    top: 120,
  },
  cardLine: {
    height: 6,
    borderRadius: 3,
    marginBottom: 6,
    width: '80%',
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
    width: 24,
    height: 24,
    bottom: 40,
    right: 20,
  },
});
