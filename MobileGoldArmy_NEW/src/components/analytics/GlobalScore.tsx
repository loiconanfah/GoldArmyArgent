import React, { useEffect, useRef, useState } from 'react';
import { View, Text, StyleSheet, Animated } from 'react-native';
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
        transform: [{ scale: cardAnim.interpolate({ inputRange: [0, 1], outputRange: [0.98, 1] }) }]
      }
    ]}>
      <View style={styles.header}>
        <Text style={styles.title}>Score Global</Text>
      </View>

      <View style={styles.scoreRow}>
        <View style={styles.circleWrapper}>
          <Svg width="110" height="110" viewBox="0 0 110 110">
            <Circle
              cx="55"
              cy="55"
              r={RADIUS}
              stroke="#F0F0F0"
              strokeWidth={STROKE_WIDTH}
              fill="none"
            />
            <AnimatedCircle
              cx="55"
              cy="55"
              r={RADIUS}
              stroke="#F5D061"
              strokeWidth={STROKE_WIDTH}
              strokeLinecap="round"
              fill="none"
              strokeDasharray={CIRCUMFERENCE}
              strokeDashoffset={strokeDashoffset}
              transform="rotate(-90 55 55)"
            />
          </Svg>
          <View style={styles.centerContent}>
            <Text style={styles.scoreBig}>{currentScore}</Text>
            <Text style={styles.scoreLabel}>/100</Text>
          </View>
        </View>

        <View style={styles.subScores}>
          <SubScore label="Activité" value={activityScore} />
          <SubScore label="Réseau" value={networkScore} />
          <SubScore label="Préparation" value={prepScore} />
        </View>
      </View>
    </Animated.View>
  );
}

function SubScore({ label, value }: { label: string, value: number }) {
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
        <Animated.View style={[styles.subBarFill, { width }]} />
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
    marginBottom: spacing.md,
  },
  title: {
    fontSize: 18,
    fontWeight: '700',
    color: '#1A1A1A',
  },
  scoreRow: {
    flexDirection: 'row',
    gap: spacing.lg,
  },
  circleWrapper: {
    width: 110,
    height: 110,
    justifyContent: 'center',
    alignItems: 'center',
    position: 'relative',
  },
  centerContent: {
    position: 'absolute',
    alignItems: 'center',
  },
  scoreBig: {
    fontSize: 32,
    fontWeight: '800',
    color: '#1A1A1A',
    lineHeight: 36,
  },
  scoreLabel: {
    fontSize: 12,
    fontWeight: '500',
    color: '#666666',
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
