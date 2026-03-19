import React, { useEffect, useRef, useState } from 'react';
import { View, Text, StyleSheet, Animated } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import Svg, { Circle } from 'react-native-svg';
import { spacing } from '../../theme/spacing';

const AnimatedCircle = Animated.createAnimatedComponent(Circle);

interface GlobalScoreProps {
  score: number;
  activityScore: number;
  networkScore: number;
  prepScore: number;
}

export function GlobalScore({ score, activityScore, networkScore, prepScore }: GlobalScoreProps) {
  const arcAnim = useRef(new Animated.Value(0)).current;
  const cardAnim = useRef(new Animated.Value(0)).current;
  const [currentScore, setCurrentScore] = useState(0);

  useEffect(() => {
    const listener = arcAnim.addListener(({ value }) => {
      setCurrentScore(Math.floor(value));
    });

    Animated.parallel([
      Animated.timing(cardAnim, {
        toValue: 1,
        duration: 400,
        delay: 300,
        useNativeDriver: true,
      }),
      Animated.timing(arcAnim, {
        toValue: score,
        duration: 1500,
        delay: 600,
        useNativeDriver: false,
      })
    ]).start();

    return () => arcAnim.removeListener(listener);
  }, [score, arcAnim, cardAnim]);

  const RADIUS = 45;
  const STROKE_WIDTH = 6;
  const CIRCUMFERENCE = 2 * Math.PI * RADIUS;

  const strokeDashoffset = arcAnim.interpolate({
    inputRange: [0, 100],
    outputRange: [CIRCUMFERENCE, 0],
  });

  return (
    <Animated.View style={[
      styles.card,
      {
        opacity: cardAnim,
        transform: [{ scale: cardAnim.interpolate({ inputRange: [0, 1], outputRange: [0.95, 1] }) }]
      }
    ]}>
      <View style={styles.header}>
        <View style={styles.headerTitleRow}>
          <Text style={styles.title}>Score de Performance</Text>
          <Ionicons name="information-circle-outline" size={16} color="#94A3B8" />
        </View>
        <Text style={styles.subtitle}>Basé sur tes activités récentes</Text>
      </View>

      <View style={styles.scoreRow}>
        <View style={styles.circleWrapper}>
          <Svg width="120" height="120" viewBox="0 0 120 120">
            <Circle
              cx="60"
              cy="60"
              r={RADIUS}
              stroke="#F1F5F9"
              strokeWidth={STROKE_WIDTH}
              fill="none"
            />
            <AnimatedCircle
              cx="60"
              cy="60"
              r={RADIUS}
              stroke="#F5D061"
              strokeWidth={STROKE_WIDTH + 2}
              strokeLinecap="round"
              fill="none"
              strokeDasharray={CIRCUMFERENCE}
              strokeDashoffset={strokeDashoffset}
              transform="rotate(-90 60 60)"
            />
          </Svg>
          <View style={styles.centerContent}>
            <Text style={styles.scoreBig}>{currentScore}</Text>
            <Text style={styles.scoreLabel}>OPTIMAL</Text>
          </View>
        </View>

        <View style={styles.subScores}>
          <SubScore label="Activité" value={activityScore} color="#F5D061" />
          <SubScore label="Réseau" value={networkScore} color="#3B82F6" />
          <SubScore label="Préparation" value={prepScore} color="#10B981" />
        </View>
      </View>
    </Animated.View>
  );
}

function SubScore({ label, value, color }: { label: string, value: number, color: string }) {
  const widthAnim = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    Animated.timing(widthAnim, {
      toValue: value,
      duration: 1000,
      delay: 1000,
      useNativeDriver: false,
    }).start();
  }, [value]);

  const width = widthAnim.interpolate({
    inputRange: [0, 100],
    outputRange: ['0%', '100%']
  });

  return (
    <View style={styles.subScoreItem}>
      <View style={styles.subScoreHeader}>
        <Text style={styles.subScoreLabel}>{label}</Text>
        <Text style={styles.subScoreValue}>{value}%</Text>
      </View>
      <View style={styles.subBarBg}>
        <Animated.View style={[styles.subBarFill, { width, backgroundColor: color }]} />
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    marginHorizontal: spacing.xl,
    marginBottom: spacing.xl,
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    padding: spacing.lg,
    borderWidth: 1,
    borderColor: '#EAEAE6',
  },
  header: {
    marginBottom: spacing.xl,
  },
  headerTitleRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    marginBottom: 4,
  },
  title: {
    fontSize: 18,
    fontWeight: '800',
    color: '#1A1A1A',
    letterSpacing: -0.5,
  },
  subtitle: {
    fontSize: 13,
    color: '#64748B',
    fontWeight: '500',
  },
  scoreRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.xl,
  },
  circleWrapper: {
    width: 120,
    height: 120,
    justifyContent: 'center',
    alignItems: 'center',
    position: 'relative',
  },
  centerContent: {
    position: 'absolute',
    alignItems: 'center',
  },
  scoreBig: {
    fontSize: 36,
    fontWeight: '900',
    color: '#1A1A1A',
    lineHeight: 40,
  },
  scoreLabel: {
    fontSize: 10,
    fontWeight: '800',
    color: '#10B981',
    letterSpacing: 1,
    marginTop: -2,
  },
  subScores: {
    flex: 1,
    justifyContent: 'center',
    gap: spacing.md,
  },
  subScoreItem: {
    gap: spacing.xs,
  },
  subScoreHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  subScoreLabel: {
    fontSize: 12,
    fontWeight: '500',
    color: '#666666',
  },
  subScoreValue: {
    fontSize: 14,
    fontWeight: '700',
    color: '#1A1A1A',
  },
  subBarBg: {
    height: 4,
    borderRadius: 2,
    backgroundColor: '#F0F0F0',
    overflow: 'hidden',
  },
  subBarFill: {
    height: '100%',
    borderRadius: 2,
    backgroundColor: '#F5D061',
  },
});
