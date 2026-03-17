import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  Modal,
  TextInput,
  TouchableOpacity,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { spacing } from '../../theme/spacing';
import { STATUS_THEME, StatusKey } from '../../types/crm.types';

interface Props {
  visible: boolean;
  onClose: () => void;
  onSubmit: (data: {
    url: string;
    title: string;
    company: string;
    status: StatusKey;
    notes: string;
  }) => void;
}

export const AddCandidatureModal: React.FC<Props> = ({
  visible,
  onClose,
  onSubmit,
}) => {
  const [url, setUrl] = useState('');
  const [title, setTitle] = useState('');
  const [company, setCompany] = useState('');
  const [notes, setNotes] = useState('');
  const [status, setStatus] = useState<StatusKey>('a_postuler');

  const handleSubmit = () => {
    if (!title || !company) {
      return;
    }
    onSubmit({ url, title, company, status, notes });
    setUrl('');
    setTitle('');
    setCompany('');
    setNotes('');
    setStatus('a_postuler');
  };

  return (
    <Modal visible={visible} animationType="slide">
      <KeyboardAvoidingView
        style={styles.container}
        behavior={Platform.OS === 'ios' ? 'padding' : undefined}
      >
        <View style={styles.headerRow}>
          <TouchableOpacity onPress={onClose} style={styles.closeButton}>
            <Ionicons name="close" size={20} color="#1A1A18" />
          </TouchableOpacity>
          <Text style={styles.headerTitle}>Nouvelle candidature</Text>
          <View style={{ width: 32 }} />
        </View>

        <View style={styles.body}>
          <View style={styles.field}>
            <Text style={styles.label}>URL de l&apos;offre</Text>
            <View style={styles.inputRow}>
              <Ionicons name="link-outline" size={16} color="#9A9A94" />
              <TextInput
                style={styles.input}
                placeholder="https://..."
                placeholderTextColor="#9A9A94"
                value={url}
                onChangeText={setUrl}
                keyboardType="url"
                autoCapitalize="none"
              />
            </View>
          </View>

          <View style={styles.field}>
            <Text style={styles.label}>Titre du poste</Text>
            <View style={styles.inputRow}>
              <Ionicons name="briefcase-outline" size={16} color="#9A9A94" />
              <TextInput
                style={styles.input}
                placeholder="Ex: Backend Developer Intern"
                placeholderTextColor="#9A9A94"
                value={title}
                onChangeText={setTitle}
              />
            </View>
          </View>

          <View style={styles.field}>
            <Text style={styles.label}>Entreprise</Text>
            <View style={styles.inputRow}>
              <Ionicons name="business-outline" size={16} color="#9A9A94" />
              <TextInput
                style={styles.input}
                placeholder="Ex: Stripe, Alan..."
                placeholderTextColor="#9A9A94"
                value={company}
                onChangeText={setCompany}
              />
            </View>
          </View>

          <View style={styles.field}>
            <Text style={styles.label}>Statut initial</Text>
            <View style={styles.statusRow}>
              {(Object.keys(STATUS_THEME) as StatusKey[]).map((key) => {
                const meta = STATUS_THEME[key];
                const isActive = key === status;
                return (
                  <TouchableOpacity
                    key={key}
                    style={[
                      styles.statusPill,
                      {
                        backgroundColor: isActive ? meta.color : meta.pale,
                      },
                    ]}
                    onPress={() => setStatus(key)}
                  >
                    <Text
                      style={[
                        styles.statusText,
                        { color: isActive ? '#FFFFFF' : meta.color },
                      ]}
                    >
                      {meta.label}
                    </Text>
                  </TouchableOpacity>
                );
              })}
            </View>
          </View>

          <View style={styles.field}>
            <Text style={styles.label}>Notes</Text>
            <View style={[styles.inputRow, styles.notesRow]}>
              <TextInput
                style={[styles.input, styles.notesInput]}
                placeholder="Infos complémentaires, lien vers ton CV, etc."
                placeholderTextColor="#9A9A94"
                value={notes}
                onChangeText={setNotes}
                multiline
                numberOfLines={3}
              />
            </View>
          </View>
        </View>

        <View style={styles.footer}>
          <TouchableOpacity
            style={[
              styles.submitButton,
              !(title && company) && { opacity: 0.5 },
            ]}
            onPress={handleSubmit}
            activeOpacity={0.9}
          >
            <Text style={styles.submitText}>Ajouter au CRM</Text>
          </TouchableOpacity>
        </View>
      </KeyboardAvoidingView>
    </Modal>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#FAFAF8',
  },
  headerRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: spacing.lg,
    paddingTop: spacing.lg,
    paddingBottom: spacing.md,
  },
  closeButton: {
    width: 32,
    height: 32,
    borderRadius: 16,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#F5F4F0',
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: '700',
    color: '#1A1A18',
  },
  body: {
    flex: 1,
    paddingHorizontal: spacing.lg,
  },
  field: {
    marginBottom: spacing.lg,
  },
  label: {
    fontSize: 13,
    fontWeight: '600',
    color: '#4A4A46',
    marginBottom: spacing.xs,
  },
  inputRow: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#E2E0DA',
    paddingHorizontal: spacing.md,
    height: 44,
  },
  input: {
    flex: 1,
    marginLeft: spacing.sm,
    fontSize: 13,
    color: '#1A1A18',
  },
  notesRow: {
    height: undefined,
    alignItems: 'flex-start',
    paddingVertical: spacing.sm,
  },
  notesInput: {
    height: 80,
    textAlignVertical: 'top',
  },
  statusRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.xs,
  },
  statusPill: {
    borderRadius: 999,
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.xs,
    marginRight: spacing.xs,
    marginBottom: spacing.xs,
  },
  statusText: {
    fontSize: 11,
    fontWeight: '600',
  },
  footer: {
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.lg,
  },
  submitButton: {
    height: 48,
    borderRadius: 999,
    backgroundColor: '#FF6B35',
    alignItems: 'center',
    justifyContent: 'center',
  },
  submitText: {
    fontSize: 15,
    fontWeight: '700',
    color: '#FFFFFF',
  },
});

