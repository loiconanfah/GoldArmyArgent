import React, { useRef, useEffect, useState } from 'react';
import { View, Text, ScrollView, Animated, TouchableOpacity, RefreshControl, ActivityIndicator } from 'react-native';
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
import { styles } from './_styles/analytics.styles';
import { crmService } from '../../src/services/crmService';
import { networkService } from '../../src/services/networkService';
import { mentorService } from '../../src/services/mentorService';

export default function AnalyticsScreen() {
  const insets = useSafeAreaInsets();
  const { user } = useAuthStore();
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [key, setKey] = useState(0);
  const [selectedPeriod, setSelectedPeriod] = useState<'7j' | '30j' | '90j'>('30j');

  // Stats State
  const [stats, setStats] = useState<{
    kpis: KpiData[];
    growth: any[];
    statuses: any[];
    activity: ActivityItem[];
    globalScore: number;
  } | null>(null);

  const cardsAnim = useRef(new Animated.Value(0)).current;
  const chartsAnim = useRef(new Animated.Value(0)).current;

  const fetchData = async () => {
    try {
      const [candidatures, contacts, interviewHistory] = await Promise.all([
        crmService.fetchCandidatures(),
        networkService.getContacts(),
        mentorService.getInterviewHistory(5).catch(() => ({ data: [] })),
      ]);

      // Calculate KPIs
      const totalApps = candidatures.length;
      const sentApps = candidatures.filter(c => c.status !== 'a_postuler').length;
      const interviewsCount = candidatures.filter(c => c.status === 'entretien').length;
      const contactsCount = contacts.length;

      // Mock growth based on real created_at if possible, otherwise keep mock for now
      const mockGrowth = [
        { month: 'Oct', value: Math.max(2, Math.floor(totalApps * 0.2)) },
        { month: 'Nov', value: Math.max(5, Math.floor(totalApps * 0.4)) },
        { month: 'Déc', value: Math.max(10, Math.floor(totalApps * 0.6)) },
        { month: 'Jan', value: Math.max(15, Math.floor(totalApps * 0.8)) },
        { month: 'Fév', value: totalApps },
      ];

      // Status Distribution
      const statusCounts = candidatures.reduce((acc: any, curr) => {
        acc[curr.status] = (acc[curr.status] || 0) + 1;
        return acc;
      }, {});

      const statuses = [
        { status: 'a_postuler' as ApplicationStatus, label: 'À Postuler', count: statusCounts['a_postuler'] || 0 },
        { status: 'envoye' as ApplicationStatus, label: 'Envoyée', count: statusCounts['envoye'] || 0 },
        { status: 'entretien' as ApplicationStatus, label: 'Entretien', count: statusCounts['entretien'] || 0 },
        { status: 'relance' as ApplicationStatus, label: 'Relance req.', count: statusCounts['relance'] || 0 },
        { status: 'offre' as ApplicationStatus, label: 'Offre reçue', count: statusCounts['offre'] || 0 },
      ];

      const kpis: KpiData[] = [
        { id: '1', label: 'Candidatures envoyées', subLabel: 'Indicateur temps réel', value: sentApps, trend: 15, color: KPI_COLORS.candidatures.text, colorPale: KPI_COLORS.candidatures.bg, icon: 'briefcase-outline', progress: Math.min(100, Math.round((sentApps / 20) * 100)) },
        { id: '2', label: 'CV Analysés / Audits', subLabel: 'Historique Mentor', value: totalApps + 5, trend: 8, color: KPI_COLORS.cv_analyses.text, colorPale: KPI_COLORS.cv_analyses.bg, icon: 'document-text-outline', progress: 85 },
        { id: '3', label: 'Entretiens obtenus', subLabel: 'Taux conversion', value: interviewsCount, trend: 200, color: KPI_COLORS.entretiens.text, colorPale: KPI_COLORS.entretiens.bg, icon: 'mic-outline', progress: Math.min(100, Math.round((interviewsCount / 5) * 100)) },
        { id: '4', label: 'Contacts Réseau', subLabel: 'Network Address Book', value: contactsCount, trend: 5, color: KPI_COLORS.reseau.text, colorPale: KPI_COLORS.reseau.bg, icon: 'people-outline', progress: Math.min(100, Math.round((contactsCount / 50) * 100)) },
      ];

      const activity: ActivityItem[] = candidatures.slice(0, 5).map(c => ({
        id: c.id,
        title: c.title,
        company: c.company,
        status: (c.status === 'a_postuler' ? 'a_postuler' : 
                 c.status === 'envoye' ? 'envoye' : 
                 c.status === 'entretien' ? 'entretien' : 
                 c.status === 'relance' ? 'relance' : 
                 c.status === 'offre' ? 'offre' : 'refuse') as any,
        progress: c.status === 'offre' ? 100 : c.status === 'entretien' ? 75 : c.status === 'relance' ? 50 : 25,
        date: c.created_at ? new Date(c.created_at).toISOString().split('T')[0] : '2026-03-19',
      }));

      setStats({
        kpis,
        growth: mockGrowth,
        statuses,
        activity,
        globalScore: Math.round(((sentApps * 2) + (interviewsCount * 5) + (contactsCount / 2)) / 2 + 50),
      });

    } catch (error) {
      console.error('[Analytics] Error fetching data:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [key]);

  useEffect(() => {
    if (!loading && stats) {
      cardsAnim.setValue(0);
      chartsAnim.setValue(0);
      Animated.parallel([
        Animated.timing(cardsAnim, { toValue: 1, duration: 600, delay: 100, useNativeDriver: true }),
        Animated.timing(chartsAnim, { toValue: 1, duration: 700, delay: 300, useNativeDriver: true })
      ]).start();
    }
  }, [loading, stats]);

  const onRefresh = React.useCallback(() => {
    setRefreshing(true);
    setKey(prev => prev + 1);
  }, []);

  if (loading && !refreshing) {
    return (
      <View style={[styles.root, { justifyContent: 'center', alignItems: 'center' }]}>
        <ActivityIndicator size="large" color="#F5D061" />
        <Text style={{ marginTop: 12, color: '#666', fontWeight: '600' }}>Chargement du dashboard...</Text>
      </View>
    );
  }

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
          <View style={{ flexDirection: 'row', alignItems: 'center' }}>
            <Ionicons name="flash" size={20} color="#F5D061" style={{ marginRight: 4 }} />
            <Text style={{ fontFamily: 'Inter-Black', fontSize: 16, color: '#1A1A1A' }}>GoldArmy</Text>
          </View>
        </View>

        {stats && (
          <>
            <Animated.View style={[styles.section, { opacity: cardsAnim, transform: [{ translateY: cardsAnim.interpolate({ inputRange: [0, 1], outputRange: [20, 0] }) }] }]}>
              <View style={styles.sectionHeader}>
                <Text style={styles.sectionTitle}>Vue d'ensemble</Text>
                <TouchableOpacity>
                  <Text style={styles.seeAllLink}>Détails →</Text>
                </TouchableOpacity>
              </View>
              <KpiCardRow data={stats.kpis} />
            </Animated.View>

            <Animated.View style={[styles.section, { opacity: chartsAnim, transform: [{ translateY: chartsAnim.interpolate({ inputRange: [0, 1], outputRange: [20, 0] }) }] }]}>
              <GlobalScore 
                score={stats.globalScore} 
                activityScore={Math.min(100, 60 + stats.kpis[0].value)} 
                networkScore={Math.min(100, 40 + stats.kpis[3].value)} 
                prepScore={75} 
              />
              <View style={{ marginVertical: spacing.lg }}>
                <GrowthChart data={stats.growth} />
              </View>
              <StatusChart data={stats.statuses} />
            </Animated.View>

            <Animated.View style={{ opacity: chartsAnim }}>
              <AdBanner />
            </Animated.View>

            <Animated.View style={[styles.section, { opacity: chartsAnim, marginTop: spacing.lg }]}>
              <View style={styles.sectionHeader}>
                <Text style={styles.sectionTitle}>Activités récentes</Text>
              </View>
              <ActivityList data={stats.activity} />
            </Animated.View>
          </>
        )}
      </ScrollView>
    </View>
  );
}
