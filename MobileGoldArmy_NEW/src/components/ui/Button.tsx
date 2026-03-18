/**
 * Button Component
 * Reusable button with variants and animations (using React Native Animated)
 */

import React, { useRef } from 'react';
import { TouchableOpacity, Text, StyleSheet, ActivityIndicator, ViewStyle, TextStyle, Animated, View } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { useTheme } from '@hooks/useTheme';
import { useHaptics } from '@hooks/useHaptics';
import { spacing } from '@theme/spacing';
import { shadows } from '@theme/shadows';
import { buttonStyles as styles } from './styles/Button.styles';

export type ButtonVariant = 'primary' | 'secondary' | 'outline' | 'ghost';
export type ButtonSize = 'sm' | 'md' | 'lg';

interface ButtonProps {
  title: string;
  onPress: () => void;
  variant?: ButtonVariant;
  size?: ButtonSize;
  loading?: boolean;
  disabled?: boolean;
  fullWidth?: boolean;
  style?: ViewStyle;
  textStyle?: TextStyle;
}

export function Button({
  title,
  onPress,
  variant = 'primary',
  size = 'md',
  loading = false,
  disabled = false,
  fullWidth = false,
  style,
  textStyle,
}: ButtonProps) {
  const { theme } = useTheme();
  const { impact } = useHaptics();
  const scale = useRef(new Animated.Value(1)).current;

  const isDisabled = disabled || loading;

  const handlePressIn = () => {
    if (!isDisabled) {
      impact();
      Animated.spring(scale, {
        toValue: 0.95,
        useNativeDriver: true,
      }).start();
    }
  };

  const handlePressOut = () => {
    Animated.spring(scale, {
      toValue: 1,
      useNativeDriver: true,
    }).start();
    if (!loading && !isDisabled) {
      onPress();
    }
  };

  const animatedStyle = {
    transform: [{ scale }],
    opacity: isDisabled ? 0.5 : 1,
  };

  // Size styles
  const sizeStyles = {
    sm: {
      paddingVertical: spacing.sm,
      paddingHorizontal: spacing.lg,
      minHeight: 36,
    },
    md: {
      paddingVertical: spacing.md,
      paddingHorizontal: spacing.xl,
      minHeight: 44,
    },
    lg: {
      paddingVertical: spacing.lg,
      paddingHorizontal: spacing['2xl'],
      minHeight: 52,
    },
  };

  // Text size styles
  const textSizeStyles = {
    sm: theme.typography.small,
    md: theme.typography.button,
    lg: theme.typography.buttonLarge,
  };

  // Variant styles
  const getVariantStyles = () => {
    switch (variant) {
      case 'primary':
        return {
          backgroundColor: theme.colors.primary,
          borderWidth: 0,
        };
      case 'secondary':
        return {
          backgroundColor: theme.colors.secondary,
          borderWidth: 0,
        };
      case 'outline':
        return {
          backgroundColor: 'transparent',
          borderWidth: 2,
          borderColor: theme.colors.primary,
        };
      case 'ghost':
        return {
          backgroundColor: 'transparent',
          borderWidth: 0,
        };
      default:
        return {};
    }
  };

  const getTextColor = () => {
    switch (variant) {
      case 'primary':
      case 'secondary':
        // For primary/secondary buttons we force pure white text for maximum contrast
        return '#FFFFFF';
      case 'outline':
      case 'ghost':
        return theme.colors.primary;
      default:
        return theme.colors.text;
    }
  };

  const buttonContent = (
    <Animated.View style={animatedStyle}>
      <TouchableOpacity
        onPressIn={handlePressIn}
        onPressOut={handlePressOut}
        style={[
          styles.button,
          sizeStyles[size],
          getVariantStyles(),
          fullWidth && styles.fullWidth,
          style,
        ]}
        activeOpacity={0.8}
        disabled={isDisabled}
      >
        {variant === 'primary' ? (
          <LinearGradient
            colors={[theme.colors.primary, theme.colors.primaryDark]}
            start={{ x: 0, y: 0 }}
            end={{ x: 1, y: 1 }}
            style={[StyleSheet.absoluteFill, { borderRadius: theme.borderRadius.lg }]}
          />
        ) : null}

        {loading ? (
          <ActivityIndicator
            size="small"
            color={getTextColor()}
          />
        ) : (
          <Text
            style={[
              textSizeStyles[size],
              { color: getTextColor() },
              textStyle,
            ]}
          >
            {title}
          </Text>
        )}
      </TouchableOpacity>
    </Animated.View>
  );

  if (variant === 'primary') {
    return (
      <View style={[shadows.md, fullWidth && styles.fullWidth]}>
        {buttonContent}
      </View>
    );
  }

  return buttonContent;
}

