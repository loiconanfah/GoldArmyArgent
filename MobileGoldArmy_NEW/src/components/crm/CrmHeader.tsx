import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Animated } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { spacing } from '../../theme/spacing';
import { useTheme } from '../../hooks/useTheme';

interface Props {
  onRefresh?: () => void;
}

export const CrmHeader: React.FC<Props> = () => {
  const { theme } = useTheme();

  return (
    <View style={styles.container}>
      <View>
        <View style={styles.badgeRow}>
          <View style={styles.pillDot} />
          <Text style={styles.badgeText}>KANBAN BOARD</Text>
        </View>
        <View style={styles.titleRow}>
          <Text style={[styles.titleBase, { color: theme.colors.text }]}>
            Central CRM{' '}
          </Text>
          <Text style={styles.titleAccent}>Candidatures</Text>
        </View>
        <Text style={styles.subtitle}>Glisse une carte pour changer son statut.</Text>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    paddingHorizontal: spacing.lg,
    paddingTop: spacing.lg,
    paddingBottom: spacing.sm,
  },
  badgeRow: {
    flexDirection: 'row',
    alignItems: 'center',
    alignSelf: 'flex-start',
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.xs,
    borderRadius: 999,
    backgroundColor: '#FFFBEB',
    marginBottom: spacing.xs,
  },
  pillDot: {
    width: 6,
    height: 6,
    borderRadius: 3,
    backgroundColor: '#F59E0B',
    marginRight: 6,
  },
  badgeText: {
    fontSize: 10,
    fontWeight: '700',
    letterSpacing: 1,
    textTransform: 'uppercase',
    color: '#92400E',
  },
  titleRow: {
    flexDirection: 'row',
    alignItems: 'baseline',
  },
  titleBase: {
    fontSize: 26,
    fontWeight: '800',
  },
  titleAccent: {
    fontSize: 26,
    fontWeight: '800',
    color: '#FF6B35',
  },
  subtitle: {
    marginTop: 4,
    fontSize: 12,
    color: '#9A9A94',
  },
  refreshButton: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.xs,
    borderRadius: 999,
    backgroundColor: '#F5F4F0',
    borderWidth: 1,
    borderColor: '#E2E0DA',
    marginTop: spacing.xs,
  },
  refreshText: {
    marginLeft: 6,
    fontSize: 13,
    color: '#4A4A46',
    fontWeight: '500',
  },
});

