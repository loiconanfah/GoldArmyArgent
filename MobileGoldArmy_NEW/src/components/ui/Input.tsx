/**
 * Input Component
 * Text input with animated label and error states (using React Native Animated)
 */

import React, { useState, useRef, useEffect } from 'react';
import { View, TextInput, Text, StyleSheet, TextInputProps, Animated } from 'react-native';
import { useTheme } from '@hooks/useTheme';
import { spacing } from '@theme/spacing';

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
          { borderColor: borderColorInterpolate },
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
          placeholderTextColor={theme.colors.textMuted}
          style={[
            styles.input,
            leftIcon && styles.inputWithLeftIcon,
            rightIcon && styles.inputWithRightIcon,
            { color: theme.colors.text },
            style,
          ]}
        />
        
        {label && (
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
                  color: error
                    ? theme.colors.error
                    : isFocused
                    ? theme.colors.primary
                    : theme.colors.textMuted,
                  backgroundColor: theme.colors.background,
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

const styles = StyleSheet.create({
  container: {
    marginBottom: spacing.lg,
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    borderWidth: 2,
    borderRadius: 12,
    minHeight: 52,
    position: 'relative',
  },
  inputError: {
    borderWidth: 2,
  },
  input: {
    flex: 1,
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
    fontSize: 16,
  },
  inputWithLeftIcon: {
    paddingLeft: spacing.sm,
  },
  inputWithRightIcon: {
    paddingRight: spacing.sm,
  },
  leftIcon: {
    paddingLeft: spacing.md,
  },
  rightIcon: {
    paddingRight: spacing.md,
  },
  labelContainer: {
    position: 'absolute',
    paddingHorizontal: spacing.xs,
    zIndex: 1,
  },
  label: {
    fontSize: 12,
    fontWeight: '500',
  },
  helperText: {
    fontSize: 12,
    marginTop: spacing.xs,
    marginLeft: spacing.md,
  },
});
