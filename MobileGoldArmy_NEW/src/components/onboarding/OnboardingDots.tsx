/**
 * Onboarding Dots Indicator
 * Animated dots showing current slide position
 */

import React, { useEffect, useRef } from 'react';
import { View, StyleSheet, Animated } from 'react-native';

interface OnboardingDotsProps {
  total: number;
  activeIndex: number;
  colors: {
    primary: string;
    border: string;
  };
}

export function OnboardingDots({ total, activeIndex, colors }: OnboardingDotsProps) {
  const dots = Array.from({ length: total }, (_, i) => i);

  return (
    <View style={styles.container}>
      {dots.map((index) => (
        <Dot key={index} active={index === activeIndex} colors={colors} />
      ))}
    </View>
  );
}

function Dot({ active, colors }: { active: boolean; colors: { primary: string; border: string } }) {
  // Animations entièrement côté JS pour éviter les conflits natifs
  const scaleX = useRef(new Animated.Value(active ? 3 : 1)).current; // 3x pour simuler 24px vs 8px
  const opacity = useRef(new Animated.Value(active ? 1 : 0.4)).current;

  useEffect(() => {
    Animated.parallel([
      Animated.spring(scaleX, {
        toValue: active ? 3 : 1,
        useNativeDriver: false,
        stiffness: 200,
        damping: 20,
      }),
      Animated.timing(opacity, {
        toValue: active ? 1 : 0.4,
        duration: 200,
        useNativeDriver: false,
      }),
    ]).start();
  }, [active]);

  return (
    <Animated.View
      style={[
        styles.dot,
        {
          opacity,
          backgroundColor: active ? colors.primary : colors.border,
          transform: [{ scaleX }],
        },
      ]}
    />
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    marginVertical: 24,
  },
  dot: {
    width: 8,
    height: 8,
    borderRadius: 4,
  },
});
