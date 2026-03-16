/**
 * Tab Bar Component
 * Custom animated tab bar for Expo Router tabs (using React Native Animated)
 */

import React, { useRef, useEffect } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Animated } from 'react-native';
import { BlurView } from 'expo-blur';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '@hooks/useTheme';
import { useHaptics } from '@hooks/useHaptics';
import { spacing } from '@theme/spacing';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

interface Tab {
  name: string;
  label: string;
  icon: keyof typeof Ionicons.glyphMap;
  iconActive: keyof typeof Ionicons.glyphMap;
}

interface TabBarProps {
  tabs: Tab[];
  activeTab: string;
  onTabPress: (tabName: string) => void;
}

function TabButton({ tab, isActive, onPress }: { tab: Tab; isActive: boolean; onPress: () => void }) {
  const { theme } = useTheme();
  const scale = useRef(new Animated.Value(1)).current;
  const opacity = useRef(new Animated.Value(isActive ? 1 : 0.6)).current;

  useEffect(() => {
    Animated.parallel([
      Animated.spring(scale, {
        toValue: isActive ? 1.1 : 1,
        useNativeDriver: true,
      }),
      Animated.timing(opacity, {
        toValue: isActive ? 1 : 0.6,
        duration: 200,
        useNativeDriver: true,
      }),
    ]).start();
  }, [isActive]);

  return (
    <TouchableOpacity
      onPress={onPress}
      style={styles.tabButton}
      activeOpacity={0.7}
    >
      <Animated.View style={{ transform: [{ scale }], opacity }}>
        <Ionicons
          name={isActive ? tab.iconActive : tab.icon}
          size={24}
          color={isActive ? theme.colors.primary : theme.colors.textMuted}
        />
      </Animated.View>
      <Text
        style={[
          styles.tabLabel,
          {
            color: isActive ? theme.colors.primary : theme.colors.textMuted,
          },
        ]}
      >
        {tab.label}
      </Text>
    </TouchableOpacity>
  );
}

export function TabBar({ tabs, activeTab, onTabPress }: TabBarProps) {
  const { theme, colorScheme } = useTheme();
  const { selection } = useHaptics();
  const insets = useSafeAreaInsets();

  return (
    <View
      style={[
        styles.container,
        {
          paddingBottom: insets.bottom + spacing.sm,
        },
      ]}
    >
      <BlurView intensity={30} tint={colorScheme} style={StyleSheet.absoluteFill} />
      <View
        style={[
          styles.tabBar,
          {
            borderTopColor: theme.colors.border,
          },
        ]}
      >
        {tabs.map((tab) => (
          <TabButton
            key={tab.name}
            tab={tab}
            isActive={activeTab === tab.name}
            onPress={() => {
              selection();
              onTabPress(tab.name);
            }}
          />
        ))}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    zIndex: 100,
  },
  tabBar: {
    flexDirection: 'row',
    borderTopWidth: 1,
    paddingTop: spacing.sm,
  },
  tabButton: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: spacing.sm,
  },
  tabLabel: {
    fontSize: 11,
    fontWeight: '600',
    marginTop: spacing.xs,
  },
});
