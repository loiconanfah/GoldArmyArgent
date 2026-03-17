import React from 'react';
import { View, Text, StyleSheet, ScrollView, Pressable } from 'react-native';
import { spacing } from '../../theme/spacing';
import { STATUS_THEME, StatusKey, CrmCounts } from '../../types/crm.types';

interface Props {
  active: StatusKey;
  onChange: (status: StatusKey) => void;
  counts: CrmCounts;
}

const ORDER: StatusKey[] = [
  'a_postuler',
  'envoye',
  'entretien',
  'relance',
  'offre',
  'refuse',
];

export const CrmStatusTabs: React.FC<Props> = ({ active, onChange, counts }) => {
  return (
    <View>
      <ScrollView
        horizontal
        showsHorizontalScrollIndicator={false}
        contentContainerStyle={styles.row}
      >
        {ORDER.map((status) => {
          const meta = STATUS_THEME[status];
          const isActive = status === active;
          const countValue = counts[status] ?? 0;
          return (
            <Pressable
              key={status}
              onPress={() => onChange(status)}
              style={[
                styles.tab,
                {
                  backgroundColor: isActive ? meta.color : meta.pale,
                  borderColor: isActive ? meta.color : meta.pale,
                },
              ]}
            >
              <Text
                style={[
                  styles.label,
                  { color: isActive ? '#FFFFFF' : meta.color },
                ]}
              >
                {meta.label}
              </Text>
              <View
                style={[
                  styles.countPill,
                  { backgroundColor: isActive ? '#FFFFFF' : '#FFFFFF' },
                ]}
              >
                <Text
                  style={[
                    styles.countText,
                    { color: isActive ? meta.color : '#4B5563' },
                  ]}
                >
                  {countValue}
                </Text>
              </View>
            </Pressable>
          );
        })}
      </ScrollView>
      <View style={styles.progressRow}>
        <View style={styles.progressTrack} />
        <Text style={styles.progressLabel}>
          {counts.envoye}/{counts.total} envoyées — continue !
        </Text>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  row: {
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.xs,
  },
  tab: {
    flexDirection: 'row',
    alignItems: 'center',
    borderRadius: 999,
    paddingHorizontal: 14,
    paddingVertical: 8,
    marginRight: spacing.sm,
    borderWidth: 1,
  },
  label: {
    fontSize: 12,
    fontWeight: '600',
  },
  countPill: {
    marginLeft: spacing.xs,
    minWidth: 20,
    height: 18,
    borderRadius: 999,
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: 6,
  },
  countText: {
    fontSize: 11,
    fontWeight: '600',
  },
  progressRow: {
    paddingHorizontal: spacing.lg,
    paddingBottom: spacing.sm,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  progressTrack: {
    flex: 1,
    height: 3,
    borderRadius: 999,
    backgroundColor: '#E5E7EB',
    marginRight: spacing.sm,
  },
  progressLabel: {
    fontSize: 11,
    color: '#9A9A94',
  },
});

