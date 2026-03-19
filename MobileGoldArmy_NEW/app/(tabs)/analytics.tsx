import React, { useRef, useEffect, useState } from 'react';
import { View, Text, ScrollView, Animated, TouchableOpacity, RefreshControl } from 'react-native';
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
import { styles } from './styles/analytics.styles';

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

        <Animated.View style={[styles.section, { opacity: cardsAnim }]}>
          <View style={styles.sectionHeader}>
            <Text style={styles.sectionTitle}>Vue d'ensemble</Text>
            <TouchableOpacity>
              <Text style={styles.seeAllLink}>Voir tout →</Text>
            </TouchableOpacity>
          </View>
          <KpiCardRow data={MOCK_KPIS} />
        </Animated.View>

        <Animated.View style={[styles.section, { opacity: chartsAnim }]}>
          <GrowthChart data={MOCK_GROWTH} />
          <GlobalScore score={74} activityScore={82} networkScore={68} prepScore={71} />
          <StatusChart data={MOCK_STATUSES} />
        </Animated.View>

        <Animated.View style={{ opacity: chartsAnim }}>
          <AdBanner />
        </Animated.View>

        <Animated.View style={[styles.section, { opacity: chartsAnim }]}>
          <ActivityList data={MOCK_ACTIVITY} />
        </Animated.View>
      </ScrollView>
    </View>
  );
}
