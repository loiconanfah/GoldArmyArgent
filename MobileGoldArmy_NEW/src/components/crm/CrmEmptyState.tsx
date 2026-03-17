import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { spacing } from '../../theme/spacing';
import { STATUS_THEME, StatusKey } from '../../types/crm.types';

interface Props {
  status: StatusKey;
}

export const CrmEmptyState: React.FC<Props> = ({ status }) => {
  const meta = STATUS_THEME[status];

  const messages: Partial<Record<StatusKey, string>> = {
    a_postuler: "Ajoute ici les offres que tu souhaites cibler bientôt.",
    envoye: "Aucune candidature envoyée pour l'instant.",
    entretien: "Dès qu'un entretien est planifié, il apparaîtra ici.",
    relance: "Aucune relance à faire pour le moment.",
    offre: "Les offres reçues s'afficheront ici.",
    refuse: "Les refus seront listés ici pour garder l'historique.",
  };

  return (
    <View style={styles.container}>
      <View style={[styles.iconWrapper, { backgroundColor: meta.pale }]}>
        <Ionicons name="trail-sign-outline" size={26} color={meta.color} />
      </View>
      <Text style={styles.title}>{meta.label}</Text>
      <Text style={styles.subtitle}>{messages[status]}</Text>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    padding: spacing.lg,
    alignItems: 'center',
    justifyContent: 'center',
  },
  iconWrapper: {
    width: 70,
    height: 70,
    borderRadius: 35,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: spacing.sm,
  },
  title: {
    fontSize: 15,
    fontWeight: '700',
    color: '#1A1A18',
    marginBottom: 4,
  },
  subtitle: {
    fontSize: 13,
    color: '#6B7280',
    textAlign: 'center',
  },
});

