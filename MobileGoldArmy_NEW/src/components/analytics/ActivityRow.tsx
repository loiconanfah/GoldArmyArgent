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
  const slideAnim = useRef(new Animated.Value(-16)).current;
  const opacityAnim = useRef(new Animated.Value(0)).current;
  const progressAnim = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    Animated.sequence([
      Animated.delay(delay),
      Animated.parallel([
        Animated.timing(opacityAnim, {
          toValue: 1,
          duration: 350,
          useNativeDriver: true,
        }),
        Animated.spring(slideAnim, {
          toValue: 0,
          useNativeDriver: true,
          tension: 50,
          friction: 7,
        }),
        Animated.timing(progressAnim, {
          toValue: item.progress,
          duration: 900,
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
        transform: [{ translateX: slideAnim }]
      }
    ]}>
      {/* Left side: Avatar */}
      <View style={[styles.avatar, { backgroundColor: `${avatarBgColor}20` }]}>
        <Text style={[styles.avatarInitial, { color: avatarBgColor }]}>{initial}</Text>
      </View>

      {/* Center: Info */}
      <View style={styles.infoCol}>
        <View style={styles.titleRow}>
          <Text style={styles.title} numberOfLines={1}>{item.title}</Text>
          {/* Status Pill on the far right */}
          <View style={[styles.statusPill, { backgroundColor: statusInfo.bg }]}>
            <View style={[styles.statusDot, { backgroundColor: statusInfo.text }]} />
            <Text style={[styles.statusText, { color: statusInfo.text }]}>
              {item.status.replace('_', ' ').toUpperCase()}
            </Text>
          </View>
        </View>

        <View style={styles.companyRow}>
          <Ionicons name="business-outline" size={11} color="#A0A0A0" />
          <Text style={styles.companyText} numberOfLines={1}>{item.company}</Text>
        </View>

        {/* Dynamic Progress Bar */}
        <View style={styles.progressRow}>
          <View style={styles.progressBg}>
            <Animated.View style={[styles.progressFill, { width: progressWidth, backgroundColor: statusInfo.text }]} />
          </View>
          <Text style={[styles.progressValue, { color: statusInfo.text }]}>{item.progress}%</Text>
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
    borderBottomColor: 'rgba(0,0,0,0.1)',
  },
  avatar: {
    width: 40,
    height: 40,
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: spacing.md,
  },
  avatarInitial: {
    fontSize: 15,
    fontWeight: '700',
  },
  infoCol: {
    flex: 1,
    justifyContent: 'center',
  },
  titleRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 2,
  },
  title: {
    fontSize: 14,
    fontWeight: '700',
    color: '#1A1A1A',
    letterSpacing: -0.2,
    flex: 1,
    marginRight: spacing.sm,
  },
  companyRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  companyText: {
    fontSize: 12,
    color: '#A0A0A0',
    marginLeft: 4,
  },
  statusPill: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 999,
  },
  statusDot: {
    width: 6,
    height: 6,
    borderRadius: 3,
    marginRight: 4,
  },
  statusText: {
    fontSize: 9,
    fontWeight: '800',
    letterSpacing: 0.5,
  },
  progressRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  progressBg: {
    flex: 1,
    height: 4,
    borderRadius: 2,
    backgroundColor: '#F5F4F0',
    marginRight: spacing.sm,
    overflow: 'hidden',
  },
  progressFill: {
    height: '100%',
    borderRadius: 2,
  },
  progressValue: {
    fontSize: 12,
    fontWeight: '800',
    width: 32, // Fixed width so text doesn't jump
    textAlign: 'right',
  },
});
