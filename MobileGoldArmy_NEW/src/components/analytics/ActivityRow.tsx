import React, { useEffect, useRef } from 'react';
import { View, Text, StyleSheet, Animated } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { spacing } from '../../theme/spacing';
import { ActivityItem, STATUS_COLORS } from '../../types/analytics.types';

// Simple stable hash function to generate consistent pastel colors based on string (company name)
function hashColor(str: string) {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    hash = str.charCodeAt(i) + ((hash << 5) - hash);
  }
  const c = (hash & 0x00FFFFFF).toString(16).toUpperCase();
  const hex = '00000'.substring(0, 6 - c.length) + c;
  return `#${hex}`;
}

export function ActivityRow({ item, delay = 0 }: { item: ActivityItem; delay?: number }) {
  const opacityAnim = useRef(new Animated.Value(0)).current;
  const progressAnim = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    Animated.sequence([
      Animated.delay(delay),
      Animated.parallel([
        Animated.timing(opacityAnim, {
          toValue: 1,
          duration: 300,
          useNativeDriver: true,
        }),
        Animated.timing(progressAnim, {
          toValue: item.progress,
          duration: 800,
          useNativeDriver: false,
        })
      ])
    ]).start();
  }, [item.progress, delay]);

  const initial = item.company.charAt(0).toUpperCase();
  const avatarBgColor = hashColor(item.company);
  const statusInfo = STATUS_COLORS[item.status];

  const progressWidth = progressAnim.interpolate({
    inputRange: [0, 100],
    outputRange: ['0%', '100%']
  });

  return (
    <Animated.View style={[
      styles.row,
      {
        opacity: opacityAnim,
      }
    ]}>
      {/* Left side: Avatar */}
      <View style={[styles.avatar, { backgroundColor: `${avatarBgColor}15` }]}>
        <Text style={[styles.avatarInitial, { color: avatarBgColor }]}>{initial}</Text>
      </View>

      {/* Center: Info */}
      <View style={styles.infoCol}>
        <View style={styles.titleRow}>
          <Text style={styles.title} numberOfLines={1}>{item.title}</Text>
          {/* Status Dot */}
          <View style={[styles.statusDot, { backgroundColor: statusInfo.text }]} />
        </View>

        <Text style={styles.companyText} numberOfLines={1}>{item.company}</Text>

        {/* Progress Bar */}
        <View style={styles.progressRow}>
          <View style={styles.progressBg}>
            <Animated.View style={[styles.progressFill, { width: progressWidth, backgroundColor: '#F5D061' }]} />
          </View>
          <Text style={styles.progressValue}>{item.progress}%</Text>
        </View>
      </View>
    </Animated.View>
  );
}

const styles = StyleSheet.create({
  row: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: spacing.lg,
    borderBottomWidth: StyleSheet.hairlineWidth,
    borderBottomColor: '#EAEAE6',
  },
  avatar: {
    width: 36,
    height: 36,
    borderRadius: 18,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: spacing.md,
  },
  avatarInitial: {
    fontSize: 14,
    fontWeight: '600',
  },
  infoCol: {
    flex: 1,
    justifyContent: 'center',
  },
  titleRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 4,
  },
  title: {
    fontSize: 14,
    fontWeight: '600',
    color: '#1A1A1A',
    flex: 1,
    marginRight: spacing.sm,
  },
  companyText: {
    fontSize: 12,
    color: '#666666',
    marginBottom: spacing.sm,
  },
  statusDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
  },
  progressRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  progressBg: {
    flex: 1,
    height: 4,
    borderRadius: 2,
    backgroundColor: '#F0F0F0',
    marginRight: spacing.sm,
    overflow: 'hidden',
  },
  progressFill: {
    height: '100%',
    borderRadius: 2,
  },
  progressValue: {
    fontSize: 12,
    fontWeight: '600',
    color: '#666666',
    width: 32,
    textAlign: 'right',
  },
});
