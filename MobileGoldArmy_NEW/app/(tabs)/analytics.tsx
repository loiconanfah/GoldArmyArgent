import React, { useRef, useEffect, useState, useMemo } from 'react';
import { View, Text, StyleSheet, ScrollView, Animated, TouchableOpacity, RefreshControl, Dimensions } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { StatusBar } from 'expo-status-bar';
import { Ionicons } from '@expo/vector-icons';
import { useAuthStore } from '../../src/stores/authStore';
import { spacing } from '../../src/theme/spacing';

import { KPI_COLORS, KpiData, ActivityItem, ApplicationStatus } from '../../src/types/analytics.types';
import { KpiCardRow } from '../../src/components/analytics/KpiCardRow';
import { GrowthChart } from '../../src/components/analytics/GrowthChart';
import { StatusChart } from '../../src/components/analytics/StatusChart';
import { GlobalScore } from '../../src/components/analytics/GlobalScore';
import { ActivityList } from '../../src/components/analytics/ActivityList';
import { AdBanner } from '../../src/components/ui/AdBanner';

const { width: SCREEN_WIDTH } = Dimensions.get('window');

// -- MOCK DATA --
const MOCK_KPIS: KpiData[] = [
  { id: '1', label: 'Candidatures envoyées', subLabel: 'Dans les 30 derniers jours', value: 42, trend: 15, color: KPI_COLORS.candidatures.text, colorPale: KPI_COLORS.candidatures.bg, icon: 'briefcase-outline', progress: 85 },
  { id: '2', label: 'CV Analysés avec IA', subLabel: 'Dans les 30 derniers jours', value: 128, trend: 8, color: KPI_COLORS.cv_analyses.text, colorPale: KPI_COLORS.cv_analyses.bg, icon: 'document-text-outline', progress: 92 },
  { id: '3', label: 'Entretiens obtenus', subLabel: 'Dans les 30 derniers jours', value: 5, trend: 200, color: KPI_COLORS.entretiens.text, colorPale: KPI_COLORS.entretiens.bg, icon: 'mic-outline', progress: 40 },
  { id: '4', label: 'Contacts Réseau', subLabel: 'Dans les 30 derniers jours', value: 18, trend: -5, color: KPI_COLORS.reseau.text, colorPale: KPI_COLORS.reseau.bg, icon: 'people-outline', progress: 65 },
];

const MOCK_GROWTH = [
  { month: 'Oct', value: 4 },
  { month: 'Nov', value: 12 },
  { month: 'Déc', value: 15 },
  { month: 'Jan', value: 28 },
  { month: 'Fév', value: 42 },
];

const MOCK_STATUSES = [
  { status: 'a_postuler' as ApplicationStatus, label: 'À Postuler', count: 12 },
  { status: 'envoye' as ApplicationStatus, label: 'Envoyée', count: 42 },
  { status: 'entretien' as ApplicationStatus, label: 'Entretien', count: 5 },
  { status: 'relance' as ApplicationStatus, label: 'Relance req.', count: 8 },
  { status: 'offre' as ApplicationStatus, label: 'Offre reçue', count: 1 },
];

const MOCK_ACTIVITY: ActivityItem[] = [
  { id: 'a1', title: 'Product Designer Senior', company: 'Google', status: 'entretien', progress: 80, date: '2026-03-16' },
  { id: 'a2', title: 'UX/UI Designer', company: 'Stripe', status: 'envoye', progress: 30, date: '2026-03-15' },
  { id: 'a3', title: 'Lead Designer', company: 'Spotify', status: 'relance', progress: 45, date: '2026-03-14' },
  { id: 'a4', title: 'Product Designer', company: 'Airbnb', status: 'a_postuler', progress: 10, date: '2026-03-12' },
  { id: 'a5', title: 'Directeur Créatif', company: 'Apple', status: 'refuse', progress: 100, date: '2026-03-10' },
];

export default function AnalyticsScreen() {
  const insets = useSafeAreaInsets();
  const { user } = useAuthStore();
  const [refreshing, setRefreshing] = useState(false);
  const [key, setKey] = useState(0);
  const [selectedPeriod, setSelectedPeriod] = useState<'7j' | '30j' | '90j'>('30j');

  // Animations
  const cardsAnim = useRef(new Animated.Value(0)).current;
  const chartsAnim = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    Animated.parallel([
      Animated.timing(cardsAnim, { toValue: 1, duration: 600, delay: 100, useNativeDriver: true }),
      Animated.timing(chartsAnim, { toValue: 1, duration: 700, delay: 300, useNativeDriver: true })
    ]).start();
  }, [key]);

  const onRefresh = React.useCallback(() => {
    setRefreshing(true);
    setTimeout(() => {
      setRefreshing(false);
      setKey(prev => prev + 1);
    }, 1000);
  }, []);

  return (
    <View style={styles.root}>
      <StatusBar style="dark" />
      

      <ScrollView
        key={`scroll-${key}`}
        style={styles.scrollView}
        contentContainerStyle={[
          styles.content,
          { paddingTop: insets.top + spacing.xl }
        ]}
        showsVerticalScrollIndicator={false}
        refreshControl={
          <RefreshControl
            refreshing={refreshing}
            onRefresh={onRefresh}
            colors={['#F5D061']}
            tintColor="#F5D061"
          />
        }
      >
        {/* Period Selector - Simple Top Bar */}
        <View style={styles.topBar}>
          <View style={styles.periodSelector}>
            {(['7j', '30j', '90j'] as const).map((period) => (
              <TouchableOpacity
                key={period}
                style={[
                  styles.periodBtn,
                  selectedPeriod === period && styles.periodBtnActive
                ]}
                onPress={() => setSelectedPeriod(period)}
              >
                <Text style={[
                  styles.periodBtnText,
                  selectedPeriod === period && styles.periodBtnTextActive
                ]}>
                  {period}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
          <TouchableOpacity style={styles.notificationBtn}>
            <Ionicons name="notifications-outline" size={22} color="#1A1A1A" />
            <View style={styles.badge}>
              <Text style={styles.badgeText}>3</Text>
            </View>
          </TouchableOpacity>
        </View>

        {/* KPIs Section */}
        <Animated.View style={[styles.section, { opacity: cardsAnim }]}>
          <View style={styles.sectionHeader}>
            <Text style={styles.sectionTitle}>Vue d'ensemble</Text>
            <TouchableOpacity>
              <Text style={styles.seeAllLink}>Voir tout →</Text>
            </TouchableOpacity>
          </View>
          <KpiCardRow data={MOCK_KPIS} />
        </Animated.View>

        {/* Charts Section */}
        <Animated.View style={[styles.section, { opacity: chartsAnim }]}>
          <GrowthChart data={MOCK_GROWTH} />
          <GlobalScore 
            score={74} 
            activityScore={82} 
            networkScore={68} 
            prepScore={71} 
          />
          <StatusChart data={MOCK_STATUSES} />
        </Animated.View>

        {/* Ad Banner */}
        <Animated.View style={{ opacity: chartsAnim }}>
          <AdBanner />
        </Animated.View>

        {/* Activity Section */}
        <Animated.View style={[styles.section, { opacity: chartsAnim }]}>
          <ActivityList data={MOCK_ACTIVITY} />
        </Animated.View>

      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  root: {
    flex: 1,
    backgroundColor: '#FAFAF8',
  },
  scrollView: {
    flex: 1,
  },
  content: {
    paddingBottom: 100,
  },
  topBar: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: spacing.xl,
    marginBottom: spacing.xl,
  },
  periodSelector: {
    flexDirection: 'row',
    gap: spacing.sm,
    backgroundColor: '#FFFFFF',
    padding: 4,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#EAEAE6',
  },
  periodBtn: {
    paddingVertical: spacing.sm,
    paddingHorizontal: spacing.md,
    borderRadius: 12,
    alignItems: 'center',
  },
  periodBtnActive: {
    backgroundColor: '#F5D061',
  },
  periodBtnText: {
    fontSize: 13,
    fontWeight: '700',
    color: '#666666',
  },
  periodBtnTextActive: {
    color: '#1A1A1A',
  },
  notificationBtn: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#FFFFFF',
    justifyContent: 'center',
    alignItems: 'center',
    position: 'relative',
    borderWidth: 1,
    borderColor: '#EAEAE6',
  },
  badge: {
    position: 'absolute',
    top: 6,
    right: 6,
    width: 18,
    height: 18,
    borderRadius: 9,
    backgroundColor: '#EF4444',
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 2,
    borderColor: '#FAFAF8',
  },
  badgeText: {
    fontSize: 9,
    fontWeight: '800',
    color: '#FFFFFF',
  },
  section: {
    marginBottom: spacing['2xl'],
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: spacing.xl,
    marginBottom: spacing.lg,
  },
  sectionTitle: {
    fontSize: 24,
    fontWeight: '800',
    letterSpacing: -0.5,
    color: '#1A1A1A',
  },
  seeAllLink: {
    fontSize: 14,
    fontWeight: '700',
    color: '#F5D061',
  },
});
