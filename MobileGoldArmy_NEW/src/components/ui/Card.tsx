/**
 * Card Component
 * Glassmorphism card with optional press animation (using React Native Animated)
 */

import React, { useRef } from 'react';
import { View, StyleSheet, ViewStyle, TouchableOpacity, Animated } from 'react-native';
import { BlurView } from 'expo-blur';
import { useTheme } from '@hooks/useTheme';
import { useHaptics } from '@hooks/useHaptics';
import { spacing } from '@theme/spacing';
import { shadows } from '@theme/shadows';
import { cardStyles as styles } from './styles/Card.styles';

interface CardProps {
  children: React.ReactNode;
  onPress?: () => void;
  style?: ViewStyle;
  blurIntensity?: number;
  variant?: 'default' | 'elevated';
}

export function Card({ 
  children, 
  onPress, 
  style, 
  blurIntensity = 20,
  variant = 'default' 
}: CardProps) {
  const { theme, colorScheme } = useTheme();
  const { impact } = useHaptics();
  const scale = useRef(new Animated.Value(1)).current;

  const handlePressIn = () => {
    if (onPress) {
      impact();
      Animated.spring(scale, {
        toValue: 0.98,
        useNativeDriver: true,
      }).start();
    }
  };

  const handlePressOut = () => {
    Animated.spring(scale, {
      toValue: 1,
      useNativeDriver: true,
    }).start();
    onPress?.();
  };

  const animatedStyle = {
    transform: [{ scale }],
  };

  const cardContent = (
    <Animated.View
      style={[
        styles.card,
        {
          backgroundColor: theme.colors.surface,
          borderColor: theme.colors.border,
        },
        variant === 'elevated' && shadows.md,
        animatedStyle,
        style,
      ]}
    >
      <BlurView intensity={blurIntensity} tint={colorScheme} style={StyleSheet.absoluteFill} />
      <View style={styles.content}>{children}</View>
    </Animated.View>
  );

  if (onPress) {
    return (
      <TouchableOpacity
        onPressIn={handlePressIn}
        onPressOut={handlePressOut}
        activeOpacity={1}
      >
        {cardContent}
      </TouchableOpacity>
    );
  }

  return cardContent;
}

