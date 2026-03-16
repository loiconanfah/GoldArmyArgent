/**
 * Onboarding Button
 * Animated button for Next/Start actions
 */

import React, { useRef, useEffect } from 'react';
import { TouchableOpacity, Text, StyleSheet, Animated } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import * as Haptics from 'expo-haptics';

interface OnboardingButtonProps {
  label: string;
  onPress: () => void;
  variant?: 'primary' | 'secondary';
  colors: {
    primary: string;
    accent: string;
    white: string;
    text: string;
  };
}

export function OnboardingButton({
  label,
  onPress,
  variant = 'primary',
  colors,
}: OnboardingButtonProps) {
  const scale = useRef(new Animated.Value(1)).current;

  const handlePressIn = () => {
    Animated.spring(scale, {
      toValue: 0.94,
      useNativeDriver: true,
      stiffness: 300,
      damping: 15,
    }).start();
  };

  const handlePressOut = () => {
    Animated.spring(scale, {
      toValue: 1,
      useNativeDriver: true,
      stiffness: 300,
      damping: 15,
    }).start();
  };

  const handlePress = () => {
    try {
      Haptics.impactAsync(
        variant === 'primary' ? Haptics.ImpactFeedbackStyle.Medium : Haptics.ImpactFeedbackStyle.Light
      );
    } catch (error) {
      // Silent fail
    }
    onPress();
  };

  if (variant === 'primary') {
    return (
      <TouchableOpacity
        onPress={handlePress}
        onPressIn={handlePressIn}
        onPressOut={handlePressOut}
        activeOpacity={1}
        style={styles.buttonContainer}
      >
        <Animated.View style={{ transform: [{ scale }] }}>
          <LinearGradient
            colors={[colors.primary, colors.accent]}
            start={{ x: 0, y: 0 }}
            end={{ x: 1, y: 1 }}
            style={styles.gradientButton}
          >
            <Text style={styles.primaryButtonText}>{label}</Text>
          </LinearGradient>
        </Animated.View>
      </TouchableOpacity>
    );
  }

  return (
    <TouchableOpacity
      onPress={handlePress}
      onPressIn={handlePressIn}
      onPressOut={handlePressOut}
      activeOpacity={1}
      style={styles.buttonContainer}
    >
      <Animated.View style={{ transform: [{ scale }] }}>
        <Text style={[styles.secondaryButtonText, { color: colors.text }]}>{label}</Text>
      </Animated.View>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  buttonContainer: {
    width: '100%',
  },
  gradientButton: {
    paddingVertical: 16,
    paddingHorizontal: 32,
    borderRadius: 999,
    alignItems: 'center',
    justifyContent: 'center',
  },
  primaryButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '700',
    letterSpacing: 0.5,
  },
  secondaryButtonText: {
    fontSize: 15,
    fontWeight: '600',
    textAlign: 'center',
    letterSpacing: 0.3,
  },
});
