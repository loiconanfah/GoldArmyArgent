import React from 'react';
import { View, Text, StyleSheet, ScrollView } from 'react-native';
import { spacing } from '../../theme/spacing';
import { CrmCounts, STATUS_THEME } from '../../types/crm.types';

interface Props {
  counts: CrmCounts;
}

export const CrmStatsBand: React.FC<Props> = ({ counts }) => {
  const items = [
    { key: 'total', label: 'Total', value: counts.total, color: '#FF6B35' },
    { key: 'envoye', label: 'Envoyées', value: counts.envoye, color: STATUS_THEME.envoye.color },
    { key: 'relance', label: 'Relances', value: counts.relance, color: STATUS_THEME.relance.color },
    { key: 'entretien', label: 'Entretiens', value: counts.entretien, color: STATUS_THEME.entretien.color },
  ];

  return (
    <ScrollView
      horizontal
      showsHorizontalScrollIndicator={false}
      contentContainerStyle={styles.container}
    >
      {items.map((item) => (
        <View key={item.key} style={styles.card}>
          <View style={[styles.leftBorder, { backgroundColor: item.color }]} />
          <View style={styles.cardContent}>
            <Text style={[styles.value, { color: item.color }]}>{item.value}</Text>
            <Text style={styles.label}>{item.label.toUpperCase()}</Text>
          </View>
        </View>
      ))}
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    paddingHorizontal: spacing.lg,
    paddingBottom: spacing.sm,
  },
  card: {
    width: 110,
    height: 70,
    borderRadius: 16,
    backgroundColor: '#FFFFFF',
    marginRight: spacing.sm,
    borderWidth: 1,
    borderColor: '#E5E7EB',
    overflow: 'hidden',
    shadowColor: 'rgba(15,23,42,0.06)',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 1,
    shadowRadius: 10,
    elevation: 2,
    flexDirection: 'row',
  },
  leftBorder: {
    width: 3,
    height: '100%',
  },
  cardContent: {
    flex: 1,
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.sm,
    justifyContent: 'center',
  },
  value: {
    fontSize: 20,
    fontWeight: '800',
  },
  label: {
    fontSize: 10,
    color: '#9A9A94',
    letterSpacing: 1,
    marginTop: 2,
  },
});

