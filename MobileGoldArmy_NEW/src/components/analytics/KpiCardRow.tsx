import React from 'react';
import { ScrollView, StyleSheet } from 'react-native';
import { KpiCard } from './KpiCard';
import { spacing } from '../../theme/spacing';
import type { KpiData } from '../../types/analytics.types';

interface KpiCardRowProps {
  data: KpiData[];
}

export function KpiCardRow({ data }: KpiCardRowProps) {
  return (
    <ScrollView
      horizontal
      showsHorizontalScrollIndicator={false}
      contentContainerStyle={styles.container}
      decelerationRate="fast"
      snapToInterval={180 + 16} // Card width (180) + margin right (16)
    >
      {data.map((kpi, index) => (
        <KpiCard 
          key={kpi.id} 
          data={kpi} 
          // Staggered entrance animation delay: 0ms, 80ms, 160ms...
          delay={index * 80} 
        />
      ))}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    paddingHorizontal: spacing.xl, // 20px padding left screen edge
    paddingRight: spacing.md,      // Extra scroll padding right
    paddingVertical: spacing.sm,   // Space for box shadows
  },
});
