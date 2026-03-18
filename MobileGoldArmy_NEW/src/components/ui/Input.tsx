/**
 * Input Component
 * Text input with animated label and error states (using React Native Animated)
 */

import React, { useState, useRef, useEffect } from 'react';
import { View, TextInput, Text, StyleSheet, TextInputProps, Animated } from 'react-native';
import { useTheme } from '@hooks/useTheme';
import { spacing } from '@theme/spacing';
import { inputStyles as styles } from './styles/Input.styles';

interface InputProps extends TextInputProps {
  label?: string;
  error?: string;
  helperText?: string;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}

export function Input({
  label,
  error,
  helperText,
  leftIcon,
  rightIcon,
  value,
  onFocus,
  onBlur,
  style,
  ...props
}: InputProps) {
  const { theme } = useTheme();
  const [isFocused, setIsFocused] = useState(false);
  const [hasValue, setHasValue] = useState(!!value);

  const borderColor = useRef(new Animated.Value(0)).current;
  const labelPosition = useRef(new Animated.Value(hasValue ? 1 : 0)).current;
  const labelScale = useRef(new Animated.Value(hasValue ? 0.85 : 1)).current;

  useEffect(() => {
    const hasContent = !!value && value.length > 0;
    setHasValue(hasContent);

    Animated.parallel([
      Animated.timing(labelPosition, {
        toValue: hasContent || isFocused ? 1 : 0,
        duration: 200,
        useNativeDriver: false,
      }),
      Animated.timing(labelScale, {
        toValue: hasContent || isFocused ? 0.85 : 1,
        duration: 200,
        useNativeDriver: false,
      }),
    ]).start();
  }, [value, isFocused]);

  useEffect(() => {
    let toValue = 0;
    if (error) toValue = 2;
    else if (isFocused) toValue = 1;

    Animated.timing(borderColor, {
      toValue,
      duration: 200,
      useNativeDriver: false,
    }).start();
  }, [isFocused, error]);

  const handleFocus = (e: any) => {
    setIsFocused(true);
    onFocus?.(e);
  };

  const handleBlur = (e: any) => {
    setIsFocused(false);
    onBlur?.(e);
  };

  const borderColorInterpolate = borderColor.interpolate({
    inputRange: [0, 1, 2],
    outputRange: [theme.colors.border, theme.colors.primary, theme.colors.error],
  });

  const labelTop = labelPosition.interpolate({
    inputRange: [0, 1],
    outputRange: [12, -8],
  });

  const labelLeft = labelPosition.interpolate({
    inputRange: [0, 1],
    outputRange: [spacing.lg, spacing.md],
  });

  return (
    <View style={styles.container}>
      <Animated.View
        style={[
          styles.inputContainer,
          {
            borderColor: borderColorInterpolate,
            backgroundColor: '#F1E4D7', // beige légèrement plus foncé que la page pour bien détacher le champ
          },
          error && styles.inputError,
        ]}
      >
        {leftIcon && <View style={styles.leftIcon}>{leftIcon}</View>}

        <TextInput
          {...props}
          value={value}
          onFocus={handleFocus}
          onBlur={handleBlur}
          placeholder={isFocused || hasValue ? undefined : label}
          // Placeholder gris foncé (légèrement plus doux que le texte plein)
          placeholderTextColor="#555555"
          style={[
            styles.input,
            leftIcon && styles.inputWithLeftIcon,
            rightIcon && styles.inputWithRightIcon,
            { color: theme.colors.text },
            style,
          ]}
        />

        {label && (isFocused || hasValue || !!error) && (
          <Animated.View
            style={[
              styles.labelContainer,
              {
                top: labelTop,
                left: labelLeft,
                transform: [{ scale: labelScale }],
              },
            ]}
            pointerEvents="none"
          >
            <Animated.Text
              style={[
                styles.label,
                {
                  // Label noir légèrement adouci (ou rouge en erreur)
                  color: error ? theme.colors.error : '#222222',
                  backgroundColor: 'transparent',
                },
              ]}
            >
              {label}
            </Animated.Text>
          </Animated.View>
        )}

        {rightIcon && <View style={styles.rightIcon}>{rightIcon}</View>}
      </Animated.View>

      {(error || helperText) && (
        <Text
          style={[
            styles.helperText,
            { color: error ? theme.colors.error : theme.colors.textMuted },
          ]}
        >
          {error || helperText}
        </Text>
      )}
    </View>
  );
}

