import React, { useEffect, useMemo, useRef } from 'react';
import { View, Text, StyleSheet, Animated } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { spacing } from '../../theme/spacing';

interface DataPoint {
  month: string;
  value: number;
}

interface GrowthChartProps {
  data: DataPoint[];
}

export function GrowthChart({ data }: GrowthChartProps) {
  const cardAnim = useRef(new Animated.Value(0)).current;
  const barsAnim = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    Animated.sequence([
      Animated.timing(cardAnim, {
        toValue: 1,
        duration: 400,
        delay: 100,
        useNativeDriver: true,
      }),
      Animated.spring(barsAnim, {
        toValue: 1,
        tension: 50,
        friction: 8,
        useNativeDriver: false, // height/bottom interpolation requires non-native
      }),
    ]).start();
  }, [barsAnim, cardAnim]);

  const maxValue = useMemo(
    () => Math.max(...data.map((d) => d.value)) || 1,
    [data]
  );

  const delta = data.length > 1 ? data[data.length - 1].value - data[0].value : 0;
  const deltaPercent =
    data.length > 1 && data[0].value !== 0
      ? Math.round((delta / data[0].value) * 100)
      : 0;

  const currentMonthValue = data[data.length - 1]?.value || 0;

  const STEM_AREA_HEIGHT = 130;
  const HEAD_SIZE = 28;
  const MAX_STEM_HEIGHT = STEM_AREA_HEIGHT - HEAD_SIZE;

  return (
    <Animated.View
      style={[
        styles.card,
        {
          opacity: cardAnim,
          transform: [
            {
              translateY: cardAnim.interpolate({
                inputRange: [0, 1],
                outputRange: [15, 0],
              }),
            },
          ],
        },
      ]}
    >
      <View style={styles.header}>
        <View style={styles.headerLeft}>
          <Text style={styles.eyebrow}>ÉVOLUTION</Text>
          <View style={styles.metricRow}>
            <Text style={styles.bigMetric}>{currentMonthValue}</Text>
            <Text style={styles.unit}> / mois</Text>
          </View>
          <Text style={styles.subtitle}>Opportunités générées ce mois-ci</Text>
        </View>

        <View style={[styles.deltaBadge, { backgroundColor: delta >= 0 ? '#ECFDF5' : '#FEF2F2' }]}>
          <Ionicons name={delta >= 0 ? 'trending-up' : 'trending-down'} size={14} color={delta >= 0 ? '#10B981' : '#EF4444'} />
          <Text style={[styles.deltaText, { color: delta >= 0 ? '#10B981' : '#EF4444' }]}>
            {Math.abs(deltaPercent)}%
          </Text>
        </View>
      </View>

      <View style={styles.chartWrapper}>
        {data.map((point, i) => {
          const targetHeight = (point.value / maxValue) * MAX_STEM_HEIGHT;
          const animatedHeight = barsAnim.interpolate({
            inputRange: [0, 1],
            outputRange: [0, targetHeight],
          });

          // Highlight the most recent month
          const isLatest = i === data.length - 1;

          return (
            <View key={i} style={styles.lollipopCol}>
              <View style={[styles.stemArea, { height: STEM_AREA_HEIGHT }]}>
                {/* Background dashed stem guide */}
                <View style={styles.stemGuide} />

                {/* Animated colored stem */}
                <Animated.View
                  style={[
                    styles.stem,
                    { height: animatedHeight },
                    isLatest && styles.stemActive
                  ]}
                />

                {/* Animated Value Head */}
                <Animated.View
                  style={[
                    styles.head,
                    { 
                      bottom: animatedHeight,
                      opacity: barsAnim.interpolate({
                        inputRange: [0.5, 1],
                        outputRange: [0, 1]
                      }),
                      transform: [{
                        scale: barsAnim.interpolate({
                          inputRange: [0, 0.5, 1],
                          outputRange: [0.5, 1.2, 1]
                        })
                      }]
                    },
                    isLatest && styles.headActive
                  ]}
                >
                  <Text style={[styles.headText, isLatest && styles.headTextActive]}>
                    {point.value}
                  </Text>
                </Animated.View>
              </View>

              <Text style={[styles.monthLabel, isLatest && styles.monthLabelActive]}>
                {point.month}
              </Text>
            </View>
          );
        })}
      </View>
    </Animated.View>
  );
}

const styles = StyleSheet.create({
  card: {
    marginHorizontal: spacing.xl,
    marginBottom: spacing.lg,
    backgroundColor: '#FFFFFF',
    borderRadius: 20,
    padding: spacing.xl,
    borderWidth: 1,
    borderColor: '#EAEAE6',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: spacing.xl,
  },
  headerLeft: {
    flex: 1,
  },
  eyebrow: {
    fontSize: 12,
    fontWeight: '700',
    color: '#999999',
    textTransform: 'uppercase',
    letterSpacing: 0.5,
    marginBottom: 4,
  },
  metricRow: {
    flexDirection: 'row',
    alignItems: 'baseline',
    marginBottom: 2,
  },
  bigMetric: {
    fontSize: 36,
    fontWeight: '800',
    color: '#1A1A1A',
    letterSpacing: -1,
  },
  unit: {
    fontSize: 16,
    fontWeight: '600',
    color: '#666666',
    marginLeft: 4,
  },
  subtitle: {
    fontSize: 13,
    color: '#666666',
    fontWeight: '500',
  },
  deltaBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderRadius: 12,
    gap: 4,
  },
  deltaText: {
    fontSize: 13,
    fontWeight: '700',
  },
  chartWrapper: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    justifyContent: 'space-between',
    paddingHorizontal: spacing.sm,
  },
  lollipopCol: {
    alignItems: 'center',
    width: 36,
  },
  stemArea: {
    width: '100%',
    alignItems: 'center',
    justifyContent: 'flex-end',
    marginBottom: spacing.sm,
    position: 'relative',
  },
  stemGuide: {
    position: 'absolute',
    width: 2,
    height: '100%',
    backgroundColor: '#F5F5F3',
    bottom: 0,
    borderRadius: 1,
  },
  stem: {
    width: 4,
    backgroundColor: '#EAEAE6',
    borderTopLeftRadius: 2,
    borderTopRightRadius: 2,
  },
  stemActive: {
    backgroundColor: '#F5D061',
  },
  head: {
    position: 'absolute',
    width: 26,
    height: 26,
    borderRadius: 13,
    backgroundColor: '#FFFFFF',
    borderWidth: 2,
    borderColor: '#EAEAE6',
    justifyContent: 'center',
    alignItems: 'center',
    // Push an extra half height down so the stem visually connects to the center
    marginBottom: -13, 
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 4,
    elevation: 2,
  },
  headActive: {
    backgroundColor: '#F5D061',
    borderColor: '#F5D061',
    shadowColor: '#F5D061',
    shadowOpacity: 0.3,
    shadowRadius: 8,
    transform: [{ scale: 1.1 }],
  },
  headText: {
    fontSize: 10,
    fontWeight: '800',
    color: '#666666',
  },
  headTextActive: {
    color: '#1A1A1A',
  },
  monthLabel: {
    fontSize: 12,
    fontWeight: '500',
    color: '#999999',
  },
  monthLabelActive: {
    fontWeight: '700',
    color: '#1A1A1A',
  },
});

