import React, { useMemo, useRef, useEffect, useState } from 'react';
import { View, Text, StyleSheet, ScrollView, Animated, TouchableOpacity, RefreshControl } from 'react-native';
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
  const [key, setKey] = useState(0); // Used to remount everything on refresh

  // Stagger Animations for screen load
  const headerAnim = useRef(new Animated.Value(0)).current;
  const headerSlideAnim = useRef(new Animated.Value(-10)).current;
  const chartsAnim = useRef(new Animated.Value(0)).current;
  const chartsSlideAnim = useRef(new Animated.Value(20)).current;

  // Header dynamic greeting
  const greeting = useMemo(() => {
    const hour = new Date().getHours();
    const name = user?.firstName || (user?.email?.split('@')[0] || 'Toi');
    
    if (hour >= 6 && hour < 12) return `Bonjour, ${name} ☀️`;
    if (hour >= 18 || hour < 6) return `Bonsoir, ${name} 🌙`;
    return `Bon après-midi, ${name} 👋`;
  }, [user]);

  const startAnimations = () => {
    // Reset
    headerAnim.setValue(0);
    headerSlideAnim.setValue(-10);
    chartsAnim.setValue(0);
    chartsSlideAnim.setValue(20);

    // Stagger Sequence
    Animated.stagger(200, [
      Animated.parallel([
        Animated.timing(headerAnim, { toValue: 1, duration: 400, useNativeDriver: true }),
        Animated.spring(headerSlideAnim, { toValue: 0, useNativeDriver: true })
      ]),
      Animated.parallel([
        Animated.timing(chartsAnim, { toValue: 1, duration: 600, delay: 150, useNativeDriver: true }),
        Animated.spring(chartsSlideAnim, { toValue: 0, delay: 150, useNativeDriver: true })
      ])
    ]).start();
  };

  useEffect(() => {
    startAnimations();
  }, [key]);

  const onRefresh = React.useCallback(() => {
    setRefreshing(true);
    // Simulate network request
    setTimeout(() => {
      setRefreshing(false);
      // Change key to remount all subcomponents and trigger their enter animations again
      setKey(prev => prev + 1);
    }, 1000);
  }, []);

  return (
    <View style={styles.root}>
      <StatusBar style="dark" />
      <ScrollView
        key={`scroll-${key}`} // Easy remount
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
        {/* Abstract Background Elements */}
        <View style={styles.bgGlowPurple} />
        <View style={styles.bgGlowOrange} />

        {/* SECTION 1: HEADER */}
        <Animated.View style={[
          styles.headerSection, 
          { 
            opacity: headerAnim,
            transform: [{ translateY: headerSlideAnim }]
          }
        ]}>
          <View style={styles.headerLeft}>
            <View style={styles.headerTitleRow}>
              <Text style={styles.headerTitle}>Organise tes recherches</Text>
              <Ionicons name="flame" size={22} color="#F5D061" style={{ marginLeft: 8 }} />
            </View>
            <Text style={styles.subtitle}>Gère facilement tes candidatures, suis tes entretiens et atteins tes objectifs au même endroit.</Text>
          </View>
          <TouchableOpacity style={styles.periodFilter}>
            <Ionicons name="calendar-outline" size={14} color="#F5D061" />
            <Text style={styles.periodText}>30j</Text>
          </TouchableOpacity>
        </Animated.View>

        {/* SECTION 2: KPIs */}
        <View style={styles.kpiSection}>
          <KpiCardRow data={MOCK_KPIS} />
        </View>

        {/* SECTION 3 & 4: CHARTS */}
        <Animated.View style={{
          opacity: chartsAnim,
          transform: [{ translateY: chartsSlideAnim }]
        }}>
          <GrowthChart data={MOCK_GROWTH} />
          
          {/* SECTION: GLOBAL SCORE (NEW) */}
          <GlobalScore 
             score={74} 
             activityScore={82} 
             networkScore={68} 
             prepScore={71} 
          />
          
          <StatusChart data={MOCK_STATUSES} />
        </Animated.View>

        {/* SECTION 5: AD BANNER */}
        <AdBanner />

        {/* SECTION 6: RECENT ACTIVITY */}
        <ActivityList data={MOCK_ACTIVITY} />

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
    // padding Bottom is handled by ActivityList to clear the Tab bar completely
  },
  bgGlowPurple: {
    position: 'absolute',
    top: 50,
    right: -100,
    width: 300,
    height: 300,
    borderRadius: 150,
    backgroundColor: '#F5D061',
    opacity: 0.04,
    transform: [{ scale: 1.5 }],
  },
  bgGlowOrange: {
    position: 'absolute',
    top: 300,
    left: -150,
    width: 350,
    height: 350,
    borderRadius: 175,
    backgroundColor: '#60A5FA',
    opacity: 0.03,
    transform: [{ scale: 1.2 }],
  },
  headerSection: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    paddingHorizontal: spacing.xl,
    marginBottom: spacing['2xl'],
  },
  headerLeft: {
    flex: 1,
    marginRight: spacing.md,
  },
  headerTitleRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: spacing.sm,
  },
  headerTitle: {
    fontSize: 28,
    fontWeight: '800',
    letterSpacing: -0.5,
    color: '#1A1A18',
  },
  greeting: {
    fontSize: 28,
    fontWeight: '800',
    letterSpacing: -0.8,
    color: '#1A1A1A',
    marginBottom: 2,
  },
  subtitle: {
    fontSize: 15,
    color: '#4A4A46',
    lineHeight: 22,
    maxWidth: '90%',
  },
  periodFilter: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    borderWidth: 1,
    borderColor: '#EAEAE6',
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    borderRadius: 20,
    shadowColor: '#000000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.04,
    shadowRadius: 8,
    elevation: 2,
  },
  periodText: {
    fontSize: 12,
    fontWeight: '700',
    color: '#F5D061',
    marginLeft: 6,
  },
  kpiSection: {
    marginBottom: spacing['2xl'],
    // We do NOT have horizontal padding here because KpiCardRow uses ScrollView padding 
    // to allow cards to bleed to the edge during scroll.
  },
});
