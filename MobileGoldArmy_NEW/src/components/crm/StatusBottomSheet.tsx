import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  Modal,
  Pressable,
  Platform,
} from 'react-native';
import { spacing } from '../../theme/spacing';
import { STATUS_THEME, StatusKey } from '../../types/crm.types';

interface Props {
  visible: boolean;
  onClose: () => void;
  currentStatus: StatusKey;
  title: string;
  company: string;
  onSelect: (status: StatusKey) => void;
  onDelete?: () => void;
}

export const StatusBottomSheet: React.FC<Props> = ({
  visible,
  onClose,
  currentStatus,
  title,
  company,
  onSelect,
  onDelete,
}) => {
  const ordered: StatusKey[] = [
    'a_postuler',
    'envoye',
    'entretien',
    'relance',
    'offre',
    'refuse',
  ];

  return (
    <Modal
      visible={visible}
      transparent
      animationType="slide"
      onRequestClose={onClose}
    >
      <Pressable style={styles.overlay} onPress={onClose}>
        <Pressable style={styles.sheet}>
          <View style={styles.handle} />
          <Text style={styles.title}>Changer le statut</Text>
          <Text style={styles.subtitle}>
            {title} · {company}
          </Text>
          {ordered.map((key) => {
            const meta = STATUS_THEME[key];
            const isActive = key === currentStatus;
            return (
              <Pressable
                key={key}
                style={[
                  styles.option,
                  isActive && { backgroundColor: meta.pale },
                ]}
                onPress={() => onSelect(key)}
              >
                <View
                  style={[styles.dot, { backgroundColor: meta.color }]}
                />
                <Text style={styles.optionLabel}>{meta.label}</Text>
                {isActive ? <Text style={styles.check}>✓</Text> : null}
              </Pressable>
            );
          })}
          
          {onDelete && (
            <>
              <View style={styles.divider} />
              <Pressable
                style={[styles.option, styles.deleteOption]}
                onPress={onDelete}
              >
                <Text style={styles.deleteText}>Supprimer cette candidature</Text>
              </Pressable>
            </>
          )}
        </Pressable>
      </Pressable>
    </Modal>
  );
};

const styles = StyleSheet.create({
  overlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.4)',
    justifyContent: 'flex-end',
  },
  sheet: {
    backgroundColor: '#FFFFFF',
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
    paddingTop: spacing.sm,
    paddingBottom: Platform.OS === 'ios' ? spacing.xl : spacing.lg,
    paddingHorizontal: spacing.lg,
  },
  handle: {
    alignSelf: 'center',
    width: 42,
    height: 4,
    borderRadius: 2,
    backgroundColor: '#E5E7EB',
    marginBottom: spacing.sm,
  },
  title: {
    fontSize: 16,
    fontWeight: '700',
    color: '#111827',
  },
  subtitle: {
    fontSize: 13,
    color: '#6B7280',
    marginBottom: spacing.md,
  },
  option: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: spacing.sm,
    borderRadius: 12,
    paddingHorizontal: spacing.sm,
    marginBottom: 4,
  },
  dot: {
    width: 12,
    height: 12,
    borderRadius: 6,
    marginRight: spacing.sm,
  },
  optionLabel: {
    fontSize: 14,
    color: '#111827',
    flex: 1,
  },
  check: {
    fontSize: 14,
    fontWeight: '700',
    color: '#111827',
  },
  divider: {
    height: 1,
    backgroundColor: '#F3F4F6',
    marginVertical: spacing.sm,
  },
  deleteOption: {
    justifyContent: 'center',
    marginTop: spacing.xs,
  },
  deleteText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#EF4444',
  },
});

