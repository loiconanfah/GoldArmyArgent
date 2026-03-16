import React, { useEffect, useRef } from 'react';
import { View, Text, StyleSheet, Animated } from 'react-native';
import Svg, { Rect } from 'react-native-svg';
import { spacing } from '../../theme/spacing';
import { STATUS_COLORS, ApplicationStatus } from '../../types/analytics.types';

const AnimatedRect = Animated.createAnimatedComponent(Rect);

interface StatusData {
  status: ApplicationStatus;
  label: string;
  count: number;
}

interface StatusChartProps {
  data: StatusData[];
}

export function StatusChart({ data }: StatusChartProps) {
  const growAnim = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    Animated.spring(growAnim, {
      toValue: 1,
      useNativeDriver: false, // SVG props cannot use native driver easily here
      friction: 8,
      tension: 40,
      delay: 550, // Waits for screen and Growth chart to mostly establish
    }).start();
  }, [growAnim]);

  const CHART_WIDTH = 300;
  const CHART_HEIGHT = 160;
  const BAR_MAX_HEIGHT = 120;
  
  const totalCount = data.reduce((acc, curr) => acc + curr.count, 0);
  const maxCount = Math.max(...data.map(d => d.count)) || 1; // Prevent Div0
  
  const barWidth = 32;
  const gap = (CHART_WIDTH - (data.length * barWidth)) / (data.length + 1);

  return (
    <View style={styles.card}>
      <View style={styles.header}>
        <Text style={styles.eyebrow}>PIPELINE</Text>
        <Text style={styles.title}>Par Statut</Text>
      </View>

      {/* Custom Flex Legend replacing the bottom squeezed text */}
      <View style={styles.legendWrapper}>
        {data.map((item) => (
          <View key={`leg-${item.status}`} style={styles.legendItem}>
            <View style={[styles.legendDot, { backgroundColor: STATUS_COLORS[item.status].text }]} />
            <Text style={styles.legendText}>{item.label}</Text>
          </View>
        ))}
      </View>

      <View style={styles.chartWrapper}>
        <Svg width="100%" height={CHART_HEIGHT} viewBox={`0 0 ${CHART_WIDTH} ${CHART_HEIGHT}`}>
          {data.map((item, index) => {
            const x = gap + (index * (barWidth + gap));
            const targetHeight = (item.count / maxCount) * BAR_MAX_HEIGHT;
            
            // Interpolate height and Y position so it grows from the bottom
            const animatedHeight = growAnim.interpolate({
              inputRange: [0, 1],
              outputRange: [0, targetHeight]
            });
            const animatedY = growAnim.interpolate({
              inputRange: [0, 1],
              outputRange: [CHART_HEIGHT, CHART_HEIGHT - targetHeight]
            });

            return (
              <React.Fragment key={`bar-${index}`}>
                {/* The Bar */}
                <AnimatedRect
                  x={x}
                  y={animatedY}
                  width={barWidth}
                  height={animatedHeight}
                  fill={STATUS_COLORS[item.status].text}
                  rx={6} // Border radius top
                />
                
                {/* Value Label above the bar */}
                <Animated.Text
                  style={{
                    position: 'absolute',
                    left: x + (barWidth / 2) - 10,
                    top: Animated.subtract(animatedY, 20) as unknown as number,
                    width: 20,
                    textAlign: 'center',
                    fontSize: 11,
                    fontWeight: '800',
                    color: '#1A1A1A',
                    opacity: growAnim.interpolate({
                      inputRange: [0.5, 1],
                      outputRange: [0, 1]
                    })
                  }}
                >
                  {item.count}
                </Animated.Text>
              </React.Fragment>
            );
          })}
        </Svg>
      </View>

      <View style={styles.footer}>
        <Text style={styles.footerText}>
          Total : <Text style={styles.footerHighlight}>{totalCount}</Text> candidatures suivies
        </Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    padding: spacing.lg,
    marginHorizontal: spacing.xl,
    marginBottom: spacing.xl,
    borderWidth: 1,
    borderColor: 'rgba(0,0,0,0.05)',
    shadowColor: '#000000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.04,
    shadowRadius: 12,
    elevation: 3,
  },
  header: {
    marginBottom: spacing.md,
  },
  eyebrow: {
    fontSize: 11,
    fontWeight: '700',
    letterSpacing: 1,
    color: '#F5D061',
    textTransform: 'uppercase',
    marginBottom: 4,
  },
  title: {
    fontSize: 18,
    fontWeight: '800',
    letterSpacing: -0.4,
    color: '#1A1A1A',
  },
  legendWrapper: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginBottom: spacing.lg,
  },
  legendItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginRight: 12,
    marginBottom: 8,
  },
  legendDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    marginRight: 6,
  },
  legendText: {
    fontSize: 11,
    fontWeight: '600',
    color: '#6A6A64',
  },
  chartWrapper: {
    height: 160,
    width: '100%',
    position: 'relative',
  },
  footer: {
    marginTop: spacing.md,
    paddingTop: spacing.md,
    borderTopWidth: 1,
    borderTopColor: '#F5F4F0',
    alignItems: 'center',
  },
  footerText: {
    fontSize: 11,
    color: '#A0A0A0',
  },
  footerHighlight: {
    color: '#1A1A1A',
    fontWeight: '800',
  },
});
