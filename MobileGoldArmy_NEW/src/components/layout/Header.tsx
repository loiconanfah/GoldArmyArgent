/**
 * Header Component
 * Animated header with blur effect on scroll (using React Native Animated)
 */

import React, { useRef, useEffect } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Animated } from 'react-native';
import { BlurView } from 'expo-blur';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '@hooks/useTheme';
import { spacing } from '@theme/spacing';

interface HeaderProps {
  title?: string;
  scrollY?: Animated.Value;
  rightAction?: {
    icon: keyof typeof Ionicons.glyphMap;
    onPress: () => void;
  };
  showBack?: boolean;
  onBackPress?: () => void;
}

export function Header({ 
  title, 
  scrollY, 
  rightAction,
  showBack = false,
  onBackPress,
}: HeaderProps) {
  const { theme, colorScheme } = useTheme();
  const insets = useSafeAreaInsets();
  const opacity = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    if (scrollY) {
      const listener = scrollY.addListener(({ value }) => {
        const newOpacity = Math.min(value / 80, 1);
        opacity.setValue(newOpacity);
      });

      return () => {
        scrollY.removeListener(listener);
      };
    }
  }, [scrollY]);

  if (scrollY) {
    return (
      <Animated.View
        style={[
          styles.header,
          {
            paddingTop: insets.top + spacing.md,
            opacity,
          },
        ]}
      >
        <BlurView intensity={25} tint={colorScheme} style={StyleSheet.absoluteFill} />
        <View style={styles.content}>
          {showBack && (
            <TouchableOpacity onPress={onBackPress} style={styles.backButton}>
              <Ionicons name="arrow-back" size={24} color={theme.colors.text} />
            </TouchableOpacity>
          )}
          {title && (
            <Text style={[styles.title, { color: theme.colors.text }]}>{title}</Text>
          )}
          {rightAction && (
            <TouchableOpacity onPress={rightAction.onPress} style={styles.rightButton}>
              <Ionicons name={rightAction.icon} size={24} color={theme.colors.text} />
            </TouchableOpacity>
          )}
        </View>
      </Animated.View>
    );
  }

  // Static header (no scroll animation)
  return (
    <View
      style={[
        styles.header,
        {
          paddingTop: insets.top + spacing.md,
          backgroundColor: theme.colors.surface,
        },
      ]}
    >
      <View style={styles.content}>
        {showBack && (
          <TouchableOpacity onPress={onBackPress} style={styles.backButton}>
            <Ionicons name="arrow-back" size={24} color={theme.colors.text} />
          </TouchableOpacity>
        )}
        {title && (
          <Text style={[styles.title, { color: theme.colors.text }]}>{title}</Text>
        )}
        {rightAction && (
          <TouchableOpacity onPress={rightAction.onPress} style={styles.rightButton}>
            <Ionicons name={rightAction.icon} size={24} color={theme.colors.text} />
          </TouchableOpacity>
        )}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  header: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    zIndex: 100,
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(255,255,255,0.05)',
  },
  content: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: spacing.lg,
    paddingBottom: spacing.md,
    minHeight: 44,
  },
  backButton: {
    marginRight: spacing.md,
  },
  title: {
    flex: 1,
    fontSize: 18,
    fontWeight: '700',
  },
  rightButton: {
    marginLeft: spacing.md,
  },
});
