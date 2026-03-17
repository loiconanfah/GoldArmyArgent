import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { ActivityRow } from './ActivityRow';
import { spacing } from '../../theme/spacing';
import type { ActivityItem } from '../../types/analytics.types';

export function ActivityList({ data }: { data: ActivityItem[] }) {
  // If we had many items, we would use a FlatList here.
  // Given typical dashboard constraints, we map for staggered mounting.
  
  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <View>
          <Text style={styles.eyebrow}>SUIVI</Text>
          <View style={styles.titleRow}>
            <Text style={styles.title}>Activité Récente</Text>
            <Text style={styles.subtitle}>{data.length} candidatures actives</Text>
          </View>
        </View>
        <TouchableOpacity>
          <Text style={styles.seeAll}>Voir tout →</Text>
        </TouchableOpacity>
      </View>

      <View style={styles.listWrapper}>
        {data.map((item, index) => (
          <ActivityRow 
            key={item.id} 
            item={item} 
            delay={600 + (index * 60)} // Staggered entrance after main screen
          />
        ))}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    paddingHorizontal: spacing.xl,
    paddingBottom: 160, // Clear the absolute bottom nav bar completely
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-end',
    marginBottom: spacing.lg,
  },
  eyebrow: {
    fontSize: 11,
    fontWeight: '600',
    letterSpacing: 0.5,
    color: '#999999',
    textTransform: 'uppercase',
    marginBottom: 4,
  },
  titleRow: {
    flexDirection: 'row',
    alignItems: 'baseline',
  },
  title: {
    fontSize: 22,
    fontWeight: '800',
    letterSpacing: -0.5,
    color: '#1A1A1A',
    marginRight: spacing.sm,
  },
  subtitle: {
    fontSize: 12,
    color: '#666666',
    fontWeight: '600',
  },
  seeAll: {
    fontSize: 13,
    fontWeight: '600',
    color: '#666666',
    marginBottom: 2,
  },
  listWrapper: {
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
    borderWidth: 1,
    borderColor: '#EAEAE6',
  },
});
