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
        // Adding a very subtle colored shadow matching the metric
        shadowColor: data.color,
      }
    ]}>
      {/* HEADER: Icon & Trend */}
      <View style={styles.header}>
        <View style={[styles.iconBox, { backgroundColor: data.colorPale }]}>
          <Ionicons name={data.icon as any} size={20} color={data.color} />
        </View>
        <View style={[styles.trendPill, { backgroundColor: trendBg }]}>
          <Text style={[styles.trendText, { color: trendColor }]}>
            {trendPrefix}{data.trend}%
          </Text>
        </View>
      </View>

      {/* BODY: Value & Label */}
      <View style={styles.body}>
        <Text style={[styles.value, { color: data.color }]}>{currentValue}</Text>
        <Text style={[styles.label, { color: data.color }]}>{data.label}</Text>
      </View>

      {/* FOOTER: Progress Bar & SubLabel */}
      <View style={styles.footer}>
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
        <Text style={styles.subLabel}>{data.subLabel}</Text>
      </View>
    </Animated.View>
  );
}

const styles = StyleSheet.create({
  card: {
    width: 160,
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    padding: 16,
    marginRight: 12,
    borderWidth: 1,
    borderColor: 'rgba(0,0,0,0.05)',
    // Neutral shadow combined with the dynamic colored shadow injected inline
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.08, // Very subtle colorful glow
    shadowRadius: 12,
    elevation: 3,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: spacing.md,
  },
  iconBox: {
    width: 40,
    height: 40,
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
  },
  trendPill: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 999,
  },
  trendText: {
    fontSize: 10,
    fontWeight: '800',
  },
  body: {
    marginBottom: spacing.lg,
  },
  value: {
    fontSize: 36,
    fontWeight: '900',
    letterSpacing: -1,
    marginBottom: 2,
  },
  label: {
    fontSize: 12,
    fontWeight: '600',
  },
  footer: {
    marginTop: 'auto',
  },
  progressBarBg: {
    height: 3,
    borderRadius: 1.5,
    width: '100%',
    marginBottom: 8,
    overflow: 'hidden',
  },
  progressBarFill: {
    height: '100%',
    borderRadius: 1.5,
  },
  subLabel: {
    fontSize: 9,
    fontWeight: '700',
    textTransform: 'uppercase',
    letterSpacing: 1,
    color: '#A0A0A0',
  },
});
