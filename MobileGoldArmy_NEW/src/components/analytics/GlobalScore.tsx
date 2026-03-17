import React, { useEffect, useRef, useState } from 'react';
import { View, Text, StyleSheet, Animated } from 'react-native';
import Svg, { Circle } from 'react-native-svg';
import { LinearGradient } from 'expo-linear-gradient';
import { spacing } from '../../theme/spacing';

const AnimatedCircle = Animated.createAnimatedComponent(Circle);

interface GlobalScoreProps {
  score: number; // 0 to 100
  activityScore: number;
  networkScore: number;
  prepScore: number;
}

export function GlobalScore({ score, activityScore, networkScore, prepScore }: GlobalScoreProps) {
  const arcAnim = useRef(new Animated.Value(0)).current;
  const [currentScore, setCurrentScore] = useState(0);

  useEffect(() => {
    const listener = arcAnim.addListener(({ value }) => {
      setCurrentScore(Math.floor(value));
    });

    Animated.timing(arcAnim, {
      toValue: score,
      duration: 1500,
      delay: 500, // Stagger after line charts
      useNativeDriver: false,
    }).start();

    return () => arcAnim.removeListener(listener);
  }, [score, arcAnim]);

  // SVG Math for Circle
  const RADIUS = 45;
  const STROKE_WIDTH = 10;
  const CIRCUMFERENCE = 2 * Math.PI * RADIUS;

  // Interpolate dashOffset so the circle "fills up"
  const strokeDashoffset = arcAnim.interpolate({
    inputRange: [0, 100],
    outputRange: [CIRCUMFERENCE, 0],
  });

  return (
    <View style={styles.outerWrapper}>
      <LinearGradient
        colors={['rgba(245, 208, 97, 0.03)', 'rgba(255, 255, 255, 1)']}
        style={styles.card}
      >
        <Text style={styles.title}>Ton Score Yayzoy</Text>
        
        <View style={styles.scoreRow}>
          {/* SVG Circular Progress */}
          <View style={styles.circleContainer}>
            <Svg width="120" height="120" viewBox="0 0 120 120">
              {/* Background Track */}
              <Circle
                cx="60"
                cy="60"
                r={RADIUS}
                stroke="#F0F0EA"
                strokeWidth={STROKE_WIDTH}
                fill="none"
              />
              {/* Animated Progress Arc */}
              <AnimatedCircle
                cx="60"
                cy="60"
                r={RADIUS}
                stroke="#F5D061" // Primary Gold (logo color)
                strokeWidth={STROKE_WIDTH}
                strokeLinecap="round"
                fill="none"
                strokeDasharray={CIRCUMFERENCE}
                strokeDashoffset={strokeDashoffset}
                // Rotate to start from top (-90 degrees)
                transform="rotate(-90 60 60)" 
              />
            </Svg>
            {/* Center Text */}
            <View style={styles.scoreTextWrapper}>
              <Text style={styles.scoreBig}>{currentScore}</Text>
              <Text style={styles.scoreSmall}>/100</Text>
            </View>
          </View>

          {/* Sub-Scores right side */}
          <View style={styles.subScoresContainer}>
            <SubScore label="Activité" value={activityScore} color="#F5D061" />
            <SubScore label="Réseau" value={networkScore} color="#8B5CF6" />
            <SubScore label="Préparation" value={prepScore} color="#10B981" />
          </View>
        </View>

        <View style={styles.footer}>
          <Text style={styles.footerText}>🎯 Tu es dans le <Text style={{fontWeight: '700'}}>top 15%</Text> des chercheurs actifs !</Text>
        </View>
      </LinearGradient>
    </View>
  );
}

function SubScore({ label, value, color }: { label: string, value: number, color: string }) {
  const widthAnim = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    Animated.timing(widthAnim, {
      toValue: value,
      duration: 1000,
      delay: 800,
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
        <Text style={[styles.subScoreValue, { color }]}>{value}%</Text>
      </View>
      <View style={styles.subBarBg}>
        <Animated.View style={[styles.subBarFill, { backgroundColor: color, width }]} />
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  outerWrapper: {
    marginHorizontal: spacing.xl,
    marginBottom: spacing.xl,
    borderRadius: 32,
    shadowColor: '#F5D061',
    shadowOffset: { width: 0, height: 12 },
    shadowOpacity: 0.08,
    shadowRadius: 32,
    elevation: 4,
  },
  card: {
    borderRadius: 32,
    padding: 24,
    borderWidth: 1,
    borderColor: 'rgba(245, 208, 97, 0.05)',
  },
  title: {
    fontSize: 22,
    fontWeight: '800',
    letterSpacing: -0.5,
    color: '#1A1A1A',
    marginBottom: spacing.md,
  },
  scoreRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  circleContainer: {
    width: 120,
    height: 120,
    justifyContent: 'center',
    alignItems: 'center',
    position: 'relative',
    marginRight: spacing.lg,
  },
  scoreTextWrapper: {
    position: 'absolute',
    alignItems: 'center',
    justifyContent: 'center',
  },
  scoreBig: {
    fontSize: 42,
    fontWeight: '900',
    letterSpacing: -2,
    color: '#1A1A1A',
    lineHeight: 46, // Tighter
  },
  scoreSmall: {
    fontSize: 14,
    fontWeight: '700',
    color: '#A0A0A0',
    marginTop: -4,
  },
  subScoresContainer: {
    flex: 1,
  },
  subScoreItem: {
    marginBottom: 10,
  },
  subScoreHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 4,
  },
  subScoreLabel: {
    fontSize: 12,
    fontWeight: '600',
    color: '#6A6A64',
  },
  subScoreValue: {
    fontSize: 12,
    fontWeight: '800',
  },
  subBarBg: {
    height: 6,
    borderRadius: 3,
    backgroundColor: '#F0F0EA',
    overflow: 'hidden',
  },
  subBarFill: {
    height: '100%',
    borderRadius: 3,
  },
  footer: {
    marginTop: spacing.md,
    paddingTop: spacing.md,
    borderTopWidth: 1,
    borderTopColor: 'rgba(245, 208, 97, 0.1)',
  },
  footerText: {
    fontSize: 13,
    color: '#6A6A64',
    fontStyle: 'italic',
  },
});
