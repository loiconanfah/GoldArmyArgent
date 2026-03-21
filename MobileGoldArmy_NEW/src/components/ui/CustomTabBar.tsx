import React, { useEffect, useRef } from 'react';
import { View, TouchableOpacity, StyleSheet, Platform, Animated } from 'react-native';
import { BottomTabBarProps } from '@react-navigation/bottom-tabs';
import { Ionicons } from '@expo/vector-icons';
import { BlurView } from 'expo-blur';

const ICON_MAP: Record<string, keyof typeof Ionicons.glyphMap> = {
  home: 'home',
  sniper: 'search',
  mentor: 'sparkles',
  reseaux: 'share-social',
  crm: 'briefcase',
  analytics: 'stats-chart',
  profile: 'person',
};

// We only want to render tabs that match our explicit mapping.
const ORDERED_TABS = ['home', 'sniper', 'mentor', 'reseaux', 'crm', 'analytics', 'profile'];

function TabIcon({ routeName, isFocused }: { routeName: string; isFocused: boolean }) {
  const scale = useRef(new Animated.Value(isFocused ? 1.2 : 1)).current;
  const opacity = useRef(new Animated.Value(isFocused ? 1 : 0)).current;

  useEffect(() => {
    Animated.parallel([
      Animated.spring(scale, {
        toValue: isFocused ? 1.2 : 1,
        useNativeDriver: true,
        friction: 5,
        tension: 100,
      }),
      Animated.timing(opacity, {
        toValue: isFocused ? 1 : 0,
        duration: 200,
        useNativeDriver: true,
      }),
    ]).start();
  }, [isFocused]);

  const iconName = ICON_MAP[routeName];
  if (!iconName) return null;

  return (
    <View style={styles.iconContainer}>
      <Animated.View style={{ transform: [{ scale }] }}>
        <Ionicons
          name={isFocused ? iconName : (`${iconName}-outline` as any)}
          size={24}
          color={isFocused ? '#FF6B35' : '#94A3B8'}
        />
      </Animated.View>
      {/* Glowing dot for active indicator */}
      <Animated.View style={[styles.activeDot, { opacity }]} />
    </View>
  );
}

export function CustomTabBar({ state, descriptors, navigation }: BottomTabBarProps) {
  // Filter and sort routes according to ORDERED_TABS to strictly prevent _styles or other routes from rendering
  const validRoutes = ORDERED_TABS.map(name => state.routes.find(r => r.name === name)).filter(Boolean) as typeof state.routes;

  return (
    <View style={styles.container}>
      {Platform.OS === 'ios' ? (
        <BlurView tint="light" intensity={80} style={StyleSheet.absoluteFill} />
      ) : (
        <View style={[StyleSheet.absoluteFill, { backgroundColor: 'rgba(255, 255, 255, 0.95)' }]} />
      )}
      
      <View style={styles.content}>
        {validRoutes.map((route) => {
          const { options } = descriptors[route.key];
          
          // Determine if it is actually focused (state.index points to the unified routes array)
          const isFocused = state.routes[state.index].key === route.key;

          const onPress = () => {
            const event = navigation.emit({
              type: 'tabPress',
              target: route.key,
              canPreventDefault: true,
            });

            if (!isFocused && !event.defaultPrevented) {
              navigation.navigate(route.name, route.params);
            }
          };

          return (
            <TouchableOpacity
              key={route.key}
              accessibilityRole="button"
              accessibilityState={isFocused ? { selected: true } : {}}
              accessibilityLabel={options.tabBarAccessibilityLabel}
              onPress={onPress}
              style={styles.tabButton}
            >
              <TabIcon routeName={route.name} isFocused={isFocused} />
            </TouchableOpacity>
          );
        })}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    position: 'absolute',
    bottom: Platform.OS === 'ios' ? 24 : 16,
    left: 12,
    right: 12,
    height: 64,
    borderRadius: 32,
    overflow: 'hidden',
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.5)',
    elevation: Platform.OS === 'ios' ? 0 : 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.1,
    shadowRadius: 12,
  },
  content: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-around',
    paddingHorizontal: 8,
  },
  tabButton: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    height: '100%',
  },
  iconContainer: {
    alignItems: 'center',
    justifyContent: 'center',
    width: 48,
    height: 48,
  },
  activeDot: {
    position: 'absolute',
    bottom: 2,
    width: 4,
    height: 4,
    borderRadius: 2,
    backgroundColor: '#FF6B35',
    shadowColor: '#FF6B35',
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: 0.8,
    shadowRadius: 4,
  },
});
