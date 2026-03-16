/**
 * Screen Wrapper
 * Universal wrapper with safe area and theme
 */

import React from 'react';
import { View, StyleSheet, ViewStyle } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { StatusBar } from 'expo-status-bar';
import { useTheme } from '@hooks/useTheme';

interface ScreenWrapperProps {
  children: React.ReactNode;
  style?: ViewStyle;
  safeAreaTop?: boolean;
  safeAreaBottom?: boolean;
}

export function ScreenWrapper({ 
  children, 
  style,
  safeAreaTop = true,
  safeAreaBottom = true,
}: ScreenWrapperProps) {
  const { theme, colorScheme } = useTheme();
  const insets = useSafeAreaInsets();

  return (
    <>
      <StatusBar style={colorScheme === 'dark' ? 'light' : 'dark'} />
      <View
        style={[
          styles.container,
          {
            backgroundColor: theme.colors.background,
            paddingTop: safeAreaTop ? insets.top : 0,
            paddingBottom: safeAreaBottom ? insets.bottom : 0,
          },
          style,
        ]}
      >
        {children}
      </View>
    </>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
});
