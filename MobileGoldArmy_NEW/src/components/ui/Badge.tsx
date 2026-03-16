/**
 * Badge Component
 * Small badge for labels and status
 */

import React from 'react';
import { View, Text, StyleSheet, ViewStyle, TextStyle } from 'react-native';
import { useTheme } from '@hooks/useTheme';
import { spacing } from '@theme/spacing';

export type BadgeVariant = 'primary' | 'secondary' | 'success' | 'error' | 'warning' | 'info';

interface BadgeProps {
  label: string;
  variant?: BadgeVariant;
  style?: ViewStyle;
  textStyle?: TextStyle;
}

export function Badge({ label, variant = 'primary', style, textStyle }: BadgeProps) {
  const { theme } = useTheme();

  const getVariantStyles = () => {
    switch (variant) {
      case 'primary':
        return {
          backgroundColor: `${theme.colors.primary}20`,
          borderColor: theme.colors.primary,
          textColor: theme.colors.primary,
        };
      case 'secondary':
        return {
          backgroundColor: `${theme.colors.secondary}20`,
          borderColor: theme.colors.secondary,
          textColor: theme.colors.secondary,
        };
      case 'success':
        return {
          backgroundColor: `${theme.colors.success}20`,
          borderColor: theme.colors.success,
          textColor: theme.colors.success,
        };
      case 'error':
        return {
          backgroundColor: `${theme.colors.error}20`,
          borderColor: theme.colors.error,
          textColor: theme.colors.error,
        };
      case 'warning':
        return {
          backgroundColor: `${theme.colors.warning}20`,
          borderColor: theme.colors.warning,
          textColor: theme.colors.warning,
        };
      case 'info':
        return {
          backgroundColor: `${theme.colors.info}20`,
          borderColor: theme.colors.info,
          textColor: theme.colors.info,
        };
      default:
        return {};
    }
  };

  const variantStyles = getVariantStyles();

  return (
    <View
      style={[
        styles.badge,
        {
          backgroundColor: variantStyles.backgroundColor,
          borderColor: variantStyles.borderColor,
        },
        style,
      ]}
    >
      <Text
        style={[
          styles.label,
          { color: variantStyles.textColor },
          textStyle,
        ]}
      >
        {label}
      </Text>
    </View>
  );
}

const styles = StyleSheet.create({
  badge: {
    alignSelf: 'flex-start',
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.xs,
    borderRadius: 12,
    borderWidth: 1,
  },
  label: {
    fontSize: 12,
    fontWeight: '600',
    letterSpacing: 0.5,
  },
});
