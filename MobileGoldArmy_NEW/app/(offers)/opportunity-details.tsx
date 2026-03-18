import React from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, Linking } from 'react-native';
import { useLocalSearchParams, useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { SniperJob } from '../../src/types/sniper.types';
import { opportunityDetailsStyles as styles } from './styles/opportunity-details.styles';

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


