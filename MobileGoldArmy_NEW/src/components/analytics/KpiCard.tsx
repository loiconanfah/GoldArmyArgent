import React, { useEffect, useRef, useState } from 'react';
import { View, Text, StyleSheet, Animated } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { spacing } from '../../theme/spacing';
import type { KpiData } from '../../types/analytics.types';

export function KpiCard({ data, delay = 0 }: { data: KpiData; delay?: number }) {
  // Animations
  const scaleAnim = useRef(new Animated.Value(0.92)).current;
  const opacityAnim = useRef(new Animated.Value(0)).current;
  const progressAnim = useRef(new Animated.Value(0)).current;
  const countAnim = useRef(new Animated.Value(0)).current;

  // Local state for the animated integer
  const [currentValue, setCurrentValue] = useState(0);

  useEffect(() => {
    // Listener to update the text value as the animation runs
    const listener = countAnim.addListener(({ value }) => {
      setCurrentValue(Math.floor(value));
    });

    Animated.sequence([
      Animated.delay(delay),
      Animated.parallel([
        Animated.spring(scaleAnim, {
          toValue: 1,
          useNativeDriver: true,
          bounciness: 6,
          speed: 12,
        }),
        Animated.timing(opacityAnim, {
          toValue: 1,
          duration: 400,
          useNativeDriver: true,
        }),
        Animated.timing(countAnim, {
          toValue: data.value,
          duration: 1200,
          useNativeDriver: false, // Cannot use native driver when listening to value for Text
        }),
        Animated.timing(progressAnim, {
          toValue: data.progress,
          duration: 1000,
          delay: 300, // Staggered progress bar filling
          useNativeDriver: false, // Cannot use native driver for width interpolation
        }),
      ])
    ]).start();

    return () => countAnim.removeListener(listener);
  }, [data.value, delay]);

  // Interpolate progress width
  const progressWidth = progressAnim.interpolate({
    inputRange: [0, 100],
    outputRange: ['0%', '100%'],
  });

  // Trend visual logic
  const isUp = data.trend > 0;
  const isDown = data.trend < 0;
  const trendColor = isUp ? '#10B981' : isDown ? '#EF4444' : '#9A9A94';
  const trendBg = isUp ? '#E6FAF4' : isDown ? '#FEF2F2' : '#F5F4F0';
  const trendPrefix = isUp ? '↑ +' : isDown ? '↓ ' : '→ ';

  return (
    <Animated.View style={[
      styles.card,
      {
        opacity: opacityAnim,
        transform: [{ scale: scaleAnim }],
        shadowColor: data.color,
      }
    ]}>
      {/* HEADER: Icon Circle - Large & Prominent */}
      <View style={styles.header}>
        <View style={[styles.iconCircle, { backgroundColor: data.colorPale }]}>
          <Ionicons name={data.icon as any} size={24} color={data.color} />
        </View>
        <View style={[styles.trendBadge, { backgroundColor: trendBg }]}>
          <Ionicons 
            name={isUp ? 'trending-up' : isDown ? 'trending-down' : 'remove'} 
            size={10} 
            color={trendColor} 
            style={{ marginRight: 2 }}
          />
          <Text style={[styles.trendText, { color: trendColor }]}>
            {Math.abs(data.trend)}%
          </Text>
        </View>
      </View>

      {/* BODY: Value & Label - Better Typography */}
      <View style={styles.body}>
        <Text style={styles.value}>{currentValue}</Text>
        <Text style={styles.label}>{data.label}</Text>
      </View>

      {/* FOOTER: Progress Indicator & SubLabel */}
      <View style={styles.footer}>
        <View style={styles.progressContainer}>
          <View style={[styles.progressBarBg, { backgroundColor: data.colorPale }]}>
            <Animated.View 
              style={[
                styles.progressBarFill, 
                { 
                  backgroundColor: data.color, 
                  width: progressWidth 
                }
              ]} 
            />
          </View>
          <Text style={styles.progressPercent}>{data.progress}%</Text>
        </View>
        <Text style={styles.subLabel}>{data.subLabel}</Text>
      </View>
    </Animated.View>
  );
}

const styles = StyleSheet.create({
  card: {
    width: 170,
    backgroundColor: '#FFFFFF',
    borderRadius: 32,
    padding: 24,
    marginRight: spacing.md,
    // Premium soft float shadow
    shadowOffset: { width: 0, height: 12 },
    shadowOpacity: 0.08,
    shadowRadius: 32,
    elevation: 4,
    borderWidth: 1,
    borderColor: 'rgba(0,0,0,0.02)',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.lg,
  },
  iconCircle: {
    width: 56,
    height: 56,
    borderRadius: 28,
    justifyContent: 'center',
    alignItems: 'center',
    // Subtle inner shadow effect
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.08,
    shadowRadius: 8,
    elevation: 2,
  },
  trendBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  trendText: {
    fontSize: 11,
    fontWeight: '800',
    letterSpacing: 0.3,
  },
  body: {
    marginBottom: spacing.lg,
  },
  value: {
    fontSize: 42,
    fontWeight: '900',
    letterSpacing: -1.5,
    color: '#1A1A18',
    marginBottom: spacing.xs,
    lineHeight: 48,
  },
  label: {
    fontSize: 14,
    fontWeight: '700',
    color: '#4A4A46',
    lineHeight: 20,
  },
  footer: {
    marginTop: 'auto',
  },
  progressContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: spacing.sm,
  },
  progressBarBg: {
    flex: 1,
    height: 4,
    borderRadius: 2,
    marginRight: spacing.xs,
    overflow: 'hidden',
  },
  progressBarFill: {
    height: '100%',
    borderRadius: 2,
  },
  progressPercent: {
    fontSize: 11,
    fontWeight: '800',
    color: '#1A1A18',
    minWidth: 32,
    textAlign: 'right',
  },
  subLabel: {
    fontSize: 11,
    fontWeight: '600',
    color: '#9A9A94',
    letterSpacing: 0.2,
  },
});
