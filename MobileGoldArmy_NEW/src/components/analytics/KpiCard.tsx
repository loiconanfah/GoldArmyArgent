import React, { useEffect, useRef, useState } from 'react';
import { View, Text, StyleSheet, Animated, TouchableOpacity } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { spacing } from '../../theme/spacing';
import type { KpiData } from '../../types/analytics.types';

export function KpiCard({ data, delay = 0 }: { data: KpiData; delay?: number }) {
  const scaleAnim = useRef(new Animated.Value(0.95)).current;
  const opacityAnim = useRef(new Animated.Value(0)).current;
  const progressAnim = useRef(new Animated.Value(0)).current;
  const countAnim = useRef(new Animated.Value(0)).current;
  const [currentValue, setCurrentValue] = useState(0);

  useEffect(() => {
    // Reset animations to 0 before each run to avoid jumping on refresh
    countAnim.setValue(0);
    progressAnim.setValue(0);
    scaleAnim.setValue(0.95);
    opacityAnim.setValue(0);

    const listener = countAnim.addListener(({ value }) => {
      setCurrentValue(Math.floor(value));
    });

    Animated.sequence([
      Animated.delay(delay),
      Animated.parallel([
        Animated.timing(scaleAnim, {
          toValue: 1,
          duration: 400,
          useNativeDriver: true,
        }),
        Animated.timing(opacityAnim, {
          toValue: 1,
          duration: 400,
          useNativeDriver: true,
        }),
        Animated.timing(countAnim, {
          toValue: data.value,
          duration: 1200,
          useNativeDriver: false,
        }),
        Animated.timing(progressAnim, {
          toValue: data.progress,
          duration: 1000,
          delay: 300,
          useNativeDriver: false,
        }),
      ])
    ]).start();

    return () => countAnim.removeListener(listener);
  }, [data.value, data.progress, delay]);

  const progressWidth = progressAnim.interpolate({
    inputRange: [0, 100],
    outputRange: ['0%', '100%'],
  });

  const isUp = data.trend > 0;
  const trendColor = isUp ? '#10B981' : '#EF4444';

  return (
    <TouchableOpacity activeOpacity={0.8}>
      <Animated.View style={[
        styles.card,
        {
          opacity: opacityAnim,
          transform: [{ scale: scaleAnim }],
        }
      ]}>
        {/* Icon */}
        <View style={styles.iconContainer}>
          <View style={[styles.iconCircle, { backgroundColor: '#F5D061' + '15' }]}>
            <Ionicons name={data.icon as any} size={20} color="#F5D061" />
          </View>
          {isUp && (
            <View style={styles.trendBadge}>
              <Ionicons name="arrow-up" size={10} color={trendColor} />
              <Text style={[styles.trendText, { color: trendColor }]}>
                {Math.abs(data.trend)}%
              </Text>
            </View>
          )}
        </View>

        {/* Value */}
        <View style={styles.valueContainer}>
          <Text style={styles.value}>{currentValue}</Text>
          <Text style={styles.label}>{data.label}</Text>
        </View>

        {/* Progress */}
        <View style={styles.progressContainer}>
          <View style={styles.progressBarBg}>
            <Animated.View 
              style={[
                styles.progressBarFill, 
                { 
                  backgroundColor: '#F5D061', 
                  width: progressWidth 
                }
              ]} 
            />
          </View>
        </View>
      </Animated.View>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  card: {
    width: 180,
    marginRight: spacing.md,
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    padding: spacing.lg,
    borderWidth: 1,
    borderColor: '#EAEAE6',
  },
  iconContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.md,
  },
  iconCircle: {
    width: 40,
    height: 40,
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center',
  },
  trendBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 3,
  },
  trendText: {
    fontSize: 11,
    fontWeight: '700',
  },
  valueContainer: {
    marginBottom: spacing.md,
  },
  value: {
    fontSize: 36,
    fontWeight: '800',
    letterSpacing: -1,
    color: '#1A1A1A',
    marginBottom: spacing.xs,
    lineHeight: 40,
  },
  label: {
    fontSize: 13,
    fontWeight: '500',
    color: '#666666',
    lineHeight: 18,
  },
  progressContainer: {
    marginTop: 'auto',
  },
  progressBarBg: {
    height: 4,
    borderRadius: 2,
    backgroundColor: '#F0F0F0',
    overflow: 'hidden',
  },
  progressBarFill: {
    height: '100%',
    borderRadius: 2,
  },
});
