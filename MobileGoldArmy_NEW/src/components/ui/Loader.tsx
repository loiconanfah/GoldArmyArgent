/**
 * Loader Component
 * Animated loading spinner (using React Native Animated)
 */

import React, { useEffect, useRef } from 'react';
import { View, StyleSheet, ViewStyle, Animated } from 'react-native';
import { useTheme } from '@hooks/useTheme';
import { loaderStyles as styles } from './styles/Loader.styles';

interface LoaderProps {
  size?: number;
  color?: string;
  style?: ViewStyle;
}

export function Loader({ size = 24, color, style }: LoaderProps) {
  const { theme } = useTheme();
  const rotation = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    const rotate = () => {
      Animated.timing(rotation, {
        toValue: 1,
        duration: 1000,
        useNativeDriver: true,
      }).start(() => {
        rotation.setValue(0);
        rotate();
      });
    };
    rotate();
  }, []);

  const spin = rotation.interpolate({
    inputRange: [0, 1],
    outputRange: ['0deg', '360deg'],
  });

  const loaderColor = color || theme.colors.primary;

  return (
    <View style={[styles.container, style]}>
      <Animated.View
        style={[
          styles.spinner,
          {
            width: size,
            height: size,
            borderColor: `${loaderColor}30`,
            borderTopColor: loaderColor,
            borderWidth: size * 0.15,
            borderRadius: size / 2,
            transform: [{ rotate: spin }],
          },
        ]}
      />
    </View>
  );
}

