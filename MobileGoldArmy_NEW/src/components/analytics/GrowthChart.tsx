import React, { useEffect, useRef } from 'react';
import { View, Text, StyleSheet, Animated } from 'react-native';
import Svg, { Path, Defs, LinearGradient as SvgGradient, Stop, Circle } from 'react-native-svg';
import { spacing } from '../../theme/spacing';

const AnimatedPath = Animated.createAnimatedComponent(Path);

interface DataPoint {
  month: string;
  value: number;
}

interface GrowthChartProps {
  data: DataPoint[];
}

export function GrowthChart({ data }: GrowthChartProps) {
  const drawAnim = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    // Delay drawing the graph slightly so the cards appear first
    Animated.timing(drawAnim, {
      toValue: 1,
      duration: 1500,
      delay: 450,
      useNativeDriver: true,
    }).start();
  }, [drawAnim]);

  // Chart Dimensions
  const CHART_WIDTH = 300;
  const CHART_HEIGHT = 140;
  const PADDING_X = 20;
  const PADDING_Y = 20;
  const MAX_VALUE = Math.max(...data.map(d => d.value)) * 1.2; // Leave some headroom

  // Helper to map data to SVG coordinates
  const getCoordinates = () => {
    return data.map((point, i) => {
      const x = PADDING_X + (i * ((CHART_WIDTH - PADDING_X * 2) / (data.length - 1)));
      const y = CHART_HEIGHT - PADDING_Y - ((point.value / MAX_VALUE) * (CHART_HEIGHT - PADDING_Y * 2));
      return { x, y, value: point.value, month: point.month };
    });
  };

  const points = getCoordinates();

  // Draw a smooth bezier curve through the points
  const drawSmoothLine = (coords: { x: number, y: number }[]) => {
    if (coords.length === 0) return '';
    let path = `M ${coords[0].x} ${coords[0].y}`;
    
    for (let i = 0; i < coords.length - 1; i++) {
        const x_mid = (coords[i].x + coords[i + 1].x) / 2;
        const y_mid = (coords[i].y + coords[i + 1].y) / 2;
        const cp_x1 = (x_mid + coords[i].x) / 2;
        const cp_x2 = (x_mid + coords[i + 1].x) / 2;

        path += ` Q ${cp_x1} ${coords[i].y}, ${x_mid} ${y_mid}`;
        path += ` T ${coords[i + 1].x} ${coords[i + 1].y}`;
    }
    return path;
  };

  const linePath = drawSmoothLine(points);
  const areaPath = `${linePath} L ${points[points.length - 1].x} ${CHART_HEIGHT} L ${points[0].x} ${CHART_HEIGHT} Z`;

  // Estimate total path length for throwing the drawing animation
  // (A rough overestimation is fine for strokeDasharray drawing)
  const pathLength = 1000; 

  const strokeDashoffset = drawAnim.interpolate({
    inputRange: [0, 1],
    outputRange: [pathLength, 0],
  });

  return (
    <View style={styles.card}>
      <View style={styles.header}>
        <View>
          <Text style={styles.eyebrow}>GRAPHIQUES</Text>
          <View style={styles.titleRow}>
            <Text style={styles.title}>Croissance</Text>
            <View style={styles.badge}>
              <Text style={styles.badgeText}>30 derniers jours</Text>
            </View>
          </View>
        </View>
      </View>

      <View style={styles.chartWrapper}>
        <Svg width="100%" height={CHART_HEIGHT} viewBox={`0 0 ${CHART_WIDTH} ${CHART_HEIGHT}`}>
          <Defs>
            <SvgGradient id="grad" x1="0" y1="0" x2="0" y2="1">
              <Stop offset="0" stopColor="#F5D061" stopOpacity="0.2" />
              <Stop offset="1" stopColor="#F5D061" stopOpacity="0.0" />
            </SvgGradient>
          </Defs>

          {/* Area under the curve */}
          <Path 
            d={areaPath} 
            fill="url(#grad)" 
          />

          {/* The Stroke Line animated */}
          <AnimatedPath
            d={linePath}
            fill="none"
            stroke="#F5D061"
            strokeWidth={3}
            strokeLinecap="round"
            strokeDasharray={pathLength}
            strokeDashoffset={strokeDashoffset}
          />

          {/* Data Points */}
          {points.map((p, i) => (
             <Animated.View 
               key={i} 
               style={{
                 position: 'absolute',
                 left: p.x - 4, // Center the 8px dot
                 top: p.y - 4,
                 opacity: drawAnim,
                 width: 8,
                 height: 8,
                 borderRadius: 4,
                 backgroundColor: '#F5D061',
                 borderWidth: 2,
                 borderColor: '#FFFFFF',
                 shadowColor: '#F5D061',
                 shadowOffset: { width: 0, height: 2 },
                 shadowOpacity: 0.5,
                 shadowRadius: 4,
                 elevation: 2,
               }}
             />
          ))}

          {/* X Axis Labels */}
          {points.map((p, i) => (
            <Text 
              key={`label-${i}`}
              style={[styles.axisLabel, { position: 'absolute', left: p.x - 10, top: CHART_HEIGHT - 10 }]}
            >
              {p.month}
            </Text>
          ))}
        </Svg>
      </View>

      <View style={styles.footer}>
        <Text style={styles.footerText}>📈 <Text style={styles.footerHighlight}>+47%</Text> vs période précédente</Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: '#FFFFFF',
    borderRadius: 32,
    padding: 24,
    marginHorizontal: spacing.xl,
    marginBottom: spacing.xl,
    borderWidth: 1,
    borderColor: 'rgba(0,0,0,0.02)',
    shadowColor: '#000000',
    shadowOffset: { width: 0, height: 12 },
    shadowOpacity: 0.06,
    shadowRadius: 32,
    elevation: 4,
  },
  header: {
    marginBottom: spacing.lg,
  },
  eyebrow: {
    fontSize: 11,
    fontWeight: '700',
    letterSpacing: 1,
    color: '#F5D061',
    textTransform: 'uppercase',
    marginBottom: 4,
  },
  titleRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  title: {
    fontSize: 22,
    fontWeight: '800',
    letterSpacing: -0.5,
    color: '#1A1A1A',
    marginRight: spacing.sm,
  },
  badge: {
    backgroundColor: '#FFF8DC',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 999,
  },
  badgeText: {
    fontSize: 10,
    fontWeight: '700',
    color: '#F5D061',
  },
  chartWrapper: {
    height: 140,
    width: '100%',
    position: 'relative',
  },
  axisLabel: {
    fontSize: 11,
    color: '#A0A0A0',
    fontWeight: '600',
  },
  footer: {
    marginTop: spacing.md,
    paddingTop: spacing.md,
    borderTopWidth: 1,
    borderTopColor: '#F5F4F0',
  },
  footerText: {
    fontSize: 13,
    color: '#6A6A64',
  },
  footerHighlight: {
    color: '#F5D061',
    fontWeight: '800',
  },
});
