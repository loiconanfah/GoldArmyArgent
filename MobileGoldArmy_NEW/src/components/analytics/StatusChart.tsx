import React, { useEffect, useRef } from 'react';
import { View, Text, StyleSheet, Animated } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { spacing } from '../../theme/spacing';
import { STATUS_COLORS, ApplicationStatus } from '../../types/analytics.types';

interface StatusData {
  status: ApplicationStatus;
  label: string;
  count: number;
}

interface StatusChartProps {
  data: StatusData[];
}

export function StatusChart({ data }: StatusChartProps) {
  const cardAnim = useRef(new Animated.Value(0)).current;
  const totalCount = data.reduce((acc, curr) => acc + curr.count, 0);
  const maxCount = Math.max(...data.map(d => d.count)) || 1;

  useEffect(() => {
    Animated.timing(cardAnim, {
      toValue: 1,
      duration: 500,
      delay: 200,
      useNativeDriver: true,
    }).start();
  }, [cardAnim]);

  return (
    <Animated.View style={[
      styles.card,
      {
        opacity: cardAnim,
        transform: [{ translateY: cardAnim.interpolate({ inputRange: [0, 1], outputRange: [10, 0] }) }]
      }
    ]}>
      <View style={styles.header}>
        <View>
          <Text style={styles.title}>Répartition par statut</Text>
          <Text style={styles.subtitle}>{totalCount} candidatures au total</Text>
        </View>
      </View>

      <View style={styles.statsList}>
        {data.map((item, index) => (
          <StatusItem
            key={item.status}
            item={item}
            maxCount={maxCount}
            totalCount={totalCount}
            delay={index * 80}
          />
        ))}
      </View>
    </Animated.View>
  );
}

function StatusItem({ 
  item, 
  maxCount, 
  totalCount, 
  delay 
}: { 
  item: StatusData; 
  maxCount: number; 
  totalCount: number;
  delay: number;
}) {
  const widthAnim = useRef(new Animated.Value(0)).current;
  const opacityAnim = useRef(new Animated.Value(0)).current;
  const percentage = (item.count / totalCount) * 100;
  const barWidth = (item.count / maxCount) * 100;

  useEffect(() => {
    Animated.parallel([
      Animated.timing(opacityAnim, {
        toValue: 1,
        duration: 400,
        delay: delay,
        useNativeDriver: true,
      }),
      Animated.timing(widthAnim, {
        toValue: barWidth,
        duration: 800,
        delay: delay + 200,
        useNativeDriver: false,
      })
    ]).start();
  }, [delay, barWidth]);

  const statusInfo = STATUS_COLORS[item.status];

  return (
    <Animated.View style={[styles.statusItem, { opacity: opacityAnim }]}>
      <View style={styles.statusHeader}>
        <View style={styles.statusLeft}>
          <View style={[styles.statusIndicator, { backgroundColor: statusInfo.text }]} />
          <View style={styles.statusInfo}>
            <Text style={styles.statusLabel}>{item.label}</Text>
            <Text style={styles.statusCount}>{item.count} candidatures</Text>
          </View>
        </View>
        <View style={styles.statusRight}>
          <Text style={[styles.statusPercentage, { color: statusInfo.text }]}>
            {Math.round(percentage)}%
          </Text>
        </View>
      </View>

      <View style={styles.barContainer}>
        <View style={styles.barBackground}>
          <Animated.View 
            style={[
              styles.barFill, 
              { 
                backgroundColor: statusInfo.text,
                width: widthAnim.interpolate({
                  inputRange: [0, 100],
                  outputRange: ['0%', '100%']
                })
              }
            ]} 
          />
        </View>
      </View>
    </Animated.View>
  );
}

const styles = StyleSheet.create({
  card: {
    marginHorizontal: spacing.xl,
    marginBottom: spacing.xl,
    backgroundColor: '#FFFFFF',
    borderRadius: 20,
    padding: spacing.xl,
    borderWidth: 1,
    borderColor: '#EAEAE6',
  },
  header: {
    marginBottom: spacing.xl,
  },
  title: {
    fontSize: 20,
    fontWeight: '700',
    color: '#1A1A1A',
    marginBottom: 4,
  },
  subtitle: {
    fontSize: 14,
    fontWeight: '500',
    color: '#666666',
  },
  statsList: {
    gap: spacing.lg,
  },
  statusItem: {
    gap: spacing.sm,
  },
  statusHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  statusLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
    gap: spacing.md,
  },
  statusIndicator: {
    width: 12,
    height: 12,
    borderRadius: 6,
  },
  statusInfo: {
    flex: 1,
  },
  statusLabel: {
    fontSize: 15,
    fontWeight: '600',
    color: '#1A1A1A',
    marginBottom: 2,
  },
  statusCount: {
    fontSize: 12,
    fontWeight: '500',
    color: '#999999',
  },
  statusRight: {
    alignItems: 'flex-end',
  },
  statusPercentage: {
    fontSize: 18,
    fontWeight: '700',
  },
  barContainer: {
    marginTop: spacing.xs,
  },
  barBackground: {
    height: 8,
    borderRadius: 4,
    backgroundColor: '#F0F0F0',
    overflow: 'hidden',
  },
  barFill: {
    height: '100%',
    borderRadius: 4,
  },
});
