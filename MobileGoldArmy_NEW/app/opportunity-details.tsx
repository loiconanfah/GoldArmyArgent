import React from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, Linking } from 'react-native';
import { useLocalSearchParams, useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { SniperJob } from '../src/types/sniper.types';
import { spacing } from '../src/theme/spacing';

export default function OpportunityDetailsScreen() {
  const router = useRouter();
  const params = useLocalSearchParams<{ job?: string }>();

  let job: Partial<SniperJob> = {};
  try {
    if (params.job) {
      job = JSON.parse(params.job) as SniperJob;
    }
  } catch {
    // ignore parse errors
  }

  const handleOpenUrl = () => {
    if (job.url) {
      Linking.openURL(job.url).catch(() => {
        // Optionally, could hook into a toast here
      });
    }
  };

  return (
    <View style={styles.root}>
      <ScrollView
        contentContainerStyle={styles.content}
        showsVerticalScrollIndicator={false}
      >
        <View style={styles.headerRow}>
          <TouchableOpacity onPress={() => router.back()} style={styles.backButton}>
            <Ionicons name="chevron-back" size={22} color="#111827" />
          </TouchableOpacity>
          <Text style={styles.headerTitle}>Détail de l'offre</Text>
        </View>

        <View style={styles.card}>
          <View style={styles.titleRow}>
            <Text style={styles.title}>{job.title}</Text>
            {typeof job.match_score === 'number' && (
              <View style={styles.matchBadge}>
                <Ionicons name="flash" size={14} color="#D97706" style={{ marginRight: 4 }} />
                <Text style={styles.matchText}>{Math.round(job.match_score)}%</Text>
              </View>
            )}
          </View>

          {job.company && (
            <View style={styles.row}>
              <Ionicons name="business-outline" size={16} color="#4B5563" style={styles.rowIcon} />
              <Text style={styles.rowText}>{job.company}</Text>
            </View>
          )}

          {job.location && (
            <View style={styles.row}>
              <Ionicons name="location-outline" size={16} color="#6B7280" style={styles.rowIcon} />
              <Text style={styles.rowText}>{job.location}</Text>
            </View>
          )}

          {job.salary && (
            <View style={styles.row}>
              <Ionicons name="cash-outline" size={16} color="#15803D" style={styles.rowIcon} />
              <Text style={[styles.rowText, styles.salaryText]}>{job.salary}</Text>
            </View>
          )}

          <View style={styles.metaRow}>
            {job.type && (
              <View style={styles.metaPill}>
                <Ionicons name="briefcase-outline" size={12} color="#4B5563" style={{ marginRight: 4 }} />
                <Text style={styles.metaText}>{job.type}</Text>
              </View>
            )}
            {job.posted_date && (
              <View style={styles.metaPill}>
                <Ionicons name="time-outline" size={12} color="#4B5563" style={{ marginRight: 4 }} />
                <Text style={styles.metaText}>{job.posted_date}</Text>
              </View>
            )}
            {job.source && (
              <View style={styles.metaPill}>
                <Ionicons name="globe-outline" size={12} color="#4B5563" style={{ marginRight: 4 }} />
                <Text style={styles.metaText}>{job.source}</Text>
              </View>
            )}
          </View>

          {job.description && (
            <View style={styles.section}>
              <Text style={styles.sectionTitle}>Description</Text>
              <Text style={styles.sectionBody}>{job.description}</Text>
            </View>
          )}
        </View>

        <View style={styles.actionsCard}>
          <TouchableOpacity
            style={[styles.primaryButton, !job.url && styles.buttonDisabled]}
            activeOpacity={0.9}
            disabled={!job.url}
            onPress={handleOpenUrl}
          >
            <Ionicons name="paper-plane-outline" size={18} color="#FFFFFF" style={{ marginRight: 8 }} />
            <Text style={styles.primaryButtonText}>Postuler à cette offre</Text>
          </TouchableOpacity>

          {job.url && (
            <TouchableOpacity
              style={styles.secondaryButton}
              activeOpacity={0.85}
              onPress={handleOpenUrl}
            >
              <Text style={styles.secondaryButtonText}>Voir l'offre originale</Text>
            </TouchableOpacity>
          )}
        </View>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  root: {
    flex: 1,
    backgroundColor: '#F9FAFB',
  },
  content: {
    paddingHorizontal: spacing.xl,
    paddingTop: spacing.xl,
    paddingBottom: spacing.xxxl,
    gap: spacing.lg,
  },
  headerRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: spacing.md,
  },
  backButton: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: '#E5E7EB',
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: spacing.md,
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: '700',
    color: '#111827',
  },
  card: {
    backgroundColor: '#FFFFFF',
    borderRadius: 24,
    padding: spacing.xl,
    borderWidth: 1,
    borderColor: '#E5E7EB',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.04,
    shadowRadius: 16,
    elevation: 3,
  },
  titleRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: spacing.sm,
  },
  title: {
    flex: 1,
    fontSize: 20,
    fontWeight: '800',
    color: '#111827',
    marginRight: spacing.md,
  },
  matchBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderRadius: 999,
    backgroundColor: '#FEF3C7',
    borderWidth: 1,
    borderColor: '#FDE68A',
  },
  matchText: {
    fontSize: 13,
    fontWeight: '700',
    color: '#D97706',
  },
  row: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 4,
  },
  rowIcon: {
    marginRight: 6,
  },
  rowText: {
    fontSize: 14,
    color: '#4B5563',
  },
  salaryText: {
    fontWeight: '600',
    color: '#15803D',
  },
  metaRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 6,
    marginTop: spacing.md,
  },
  metaPill: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 999,
    backgroundColor: '#F3F4F6',
  },
  metaText: {
    fontSize: 11,
    color: '#4B5563',
    fontWeight: '500',
  },
  section: {
    marginTop: spacing.lg,
  },
  sectionTitle: {
    fontSize: 15,
    fontWeight: '700',
    color: '#111827',
    marginBottom: spacing.xs,
  },
  sectionBody: {
    fontSize: 13,
    lineHeight: 20,
    color: '#4B5563',
  },
  actionsCard: {
    marginTop: spacing.md,
    backgroundColor: '#FFFFFF',
    borderRadius: 20,
    padding: spacing.lg,
    borderWidth: 1,
    borderColor: '#E5E7EB',
    gap: spacing.sm,
  },
  primaryButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#F97316',
    borderRadius: 999,
    paddingVertical: 12,
    paddingHorizontal: spacing.lg,
  },
  primaryButtonText: {
    fontSize: 15,
    fontWeight: '700',
    color: '#FFFFFF',
  },
  buttonDisabled: {
    opacity: 0.5,
  },
  secondaryButton: {
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 10,
    borderRadius: 999,
    borderWidth: 1,
    borderColor: '#D1D5DB',
  },
  secondaryButtonText: {
    fontSize: 13,
    fontWeight: '500',
    color: '#4B5563',
  },
});

