import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { Swipeable } from 'react-native-gesture-handler';
import { Ionicons } from '@expo/vector-icons';
import { spacing } from '../../theme/spacing';
import { Candidature, STATUS_THEME, StatusKey } from '../../types/crm.types';

interface Props {
  item: Candidature;
  onPressStatus: () => void;
  onSwipePrev: () => void;
  onSwipeNext: () => void;
}

export const CandidatureCard: React.FC<Props> = ({
  item,
  onPressStatus,
  onSwipePrev,
  onSwipeNext,
}) => {
  const meta = STATUS_THEME[item.status];

  const renderLeft = () => (
    <View style={[styles.swipePanel, { backgroundColor: '#9CA3AF', alignItems: 'flex-start' }]}>
      <View style={styles.swipeContent}>
        <Ionicons name="arrow-back-outline" size={18} color="#FFFFFF" />
        <Text style={styles.swipeLabel}>Statut précédent</Text>
      </View>
    </View>
  );

  const renderRight = () => (
    <View style={[styles.swipePanel, { backgroundColor: meta.color, alignItems: 'flex-end' }]}>
      <View style={styles.swipeContent}>
        <Text style={styles.swipeLabel}>Statut suivant</Text>
        <Ionicons name="arrow-forward-outline" size={18} color="#FFFFFF" />
      </View>
    </View>
  );

  const statusActionLabel: Partial<Record<StatusKey, string>> = {
    a_postuler: '✦ ADAPTER CV IA',
    envoye: '⏳ En attente',
    entretien: '🎤 PRÉPARER',
    relance: '♺ GÉNÉRER RELANCE',
    offre: '🎉 VOIR L’OFFRE',
    refuse: '↺ RE-POSTULER',
  };

  const shortDesc =
    item.description && item.description.length > 0
      ? item.description
      : "Aucune description fournie.";

  const avatarBg = meta.pale;

  return (
    <Swipeable
      renderLeftActions={renderLeft}
      renderRightActions={renderRight}
      onSwipeableLeftOpen={onSwipePrev}
      onSwipeableRightOpen={onSwipeNext}
      friction={2}
      leftThreshold={60}
      rightThreshold={60}
    >
      <View style={styles.card}>
        <View style={styles.headerRow}>
          <View style={[styles.avatar, { backgroundColor: avatarBg }]}>
            <Text style={styles.avatarText}>
              {item.company.charAt(0).toUpperCase()}
            </Text>
          </View>
          <View style={styles.companyWrapper}>
            <Text style={styles.company} numberOfLines={1}>
              {item.company}
            </Text>
            <Text style={styles.date}>{item.date}</Text>
          </View>
          <Ionicons name="open-outline" size={16} color="#9A9A94" />
        </View>

        <Text style={styles.title} numberOfLines={2}>
          {item.title}
        </Text>

        <View style={styles.descWrapper}>
          <Text
            style={[
              styles.description,
              !item.description && styles.descriptionEmpty,
            ]}
            numberOfLines={2}
          >
            {shortDesc}
          </Text>
        </View>

        <View style={styles.footerRow}>
          <TouchableOpacity
            style={[
              styles.statusPill,
              { backgroundColor: meta.pale, borderColor: meta.color },
            ]}
            onPress={onPressStatus}
            activeOpacity={0.9}
          >
            <View
              style={[styles.statusDot, { backgroundColor: meta.color }]}
            />
            <Text style={[styles.statusText, { color: meta.color }]}>
              {meta.label}
            </Text>
          </TouchableOpacity>

          <View style={styles.actionPill}>
            <Text style={styles.actionText}>
              {statusActionLabel[item.status] ?? 'Action IA'}
            </Text>
          </View>
        </View>
      </View>
    </Swipeable>
  );
};

const styles = StyleSheet.create({
  card: {
    borderRadius: 18,
    backgroundColor: '#FFFFFF',
    padding: spacing.md,
    shadowColor: 'rgba(15,23,42,0.06)',
    shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 1,
    shadowRadius: 12,
    elevation: 3,
  },
  headerRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: spacing.sm,
  },
  avatar: {
    width: 40,
    height: 40,
    borderRadius: 20,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: spacing.sm,
  },
  avatarText: {
    fontSize: 16,
    fontWeight: '700',
    color: '#1A1A18',
  },
  companyWrapper: {
    flex: 1,
  },
  company: {
    fontSize: 13,
    fontWeight: '600',
    color: '#1A1A18',
  },
  date: {
    fontSize: 11,
    color: '#9A9A94',
  },
  title: {
    fontSize: 16,
    fontWeight: '700',
    color: '#111827',
    marginBottom: spacing.xs,
  },
  descWrapper: {
    borderRadius: 10,
    backgroundColor: '#F5F4F0',
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.xs,
    marginBottom: spacing.sm,
  },
  description: {
    fontSize: 13,
    color: '#4A4A46',
  },
  descriptionEmpty: {
    fontStyle: 'italic',
    color: '#9A9A94',
  },
  footerRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  statusPill: {
    flexDirection: 'row',
    alignItems: 'center',
    borderRadius: 999,
    paddingHorizontal: spacing.sm,
    paddingVertical: 4,
    borderWidth: 1,
  },
  statusDot: {
    width: 6,
    height: 6,
    borderRadius: 3,
    marginRight: 6,
  },
  statusText: {
    fontSize: 11,
    fontWeight: '600',
  },
  actionPill: {
    borderRadius: 999,
    paddingHorizontal: spacing.md,
    paddingVertical: 6,
    backgroundColor: '#FFF0EB',
  },
  actionText: {
    fontSize: 11,
    fontWeight: '600',
    color: '#FF6B35',
  },
  swipePanel: {
    flex: 1,
    justifyContent: 'center',
    paddingHorizontal: spacing.lg,
  },
  swipeContent: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  swipeLabel: {
    fontSize: 12,
    fontWeight: '600',
    color: '#FFFFFF',
    marginHorizontal: 6,
  },
});

