import React, { useEffect, useRef } from 'react';
import { View, Text, StyleSheet, ScrollView, Dimensions, Animated } from 'react-native';
import { StatusBar } from 'expo-status-bar';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { spacing } from '../../src/theme/spacing';

const { width } = Dimensions.get('window');

export default function AnalyseScreen() {
  const insets = useSafeAreaInsets();

  // Simple reveal animations
  const headerAnim = useRef(new Animated.Value(0)).current;
  const cardsAnim = useRef(new Animated.Value(0)).current;
  const chartsAnim = useRef(new Animated.Value(0)).current;
  const listAnim = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    Animated.stagger(160, [
      Animated.timing(headerAnim, { toValue: 1, duration: 500, useNativeDriver: true }),
      Animated.timing(cardsAnim, { toValue: 1, duration: 500, useNativeDriver: true }),
      Animated.timing(chartsAnim, { toValue: 1, duration: 500, useNativeDriver: true }),
      Animated.timing(listAnim, { toValue: 1, duration: 500, useNativeDriver: true }),
    ]).start();
  }, [headerAnim, cardsAnim, chartsAnim, listAnim]);

  return (
    <View style={styles.root}>
      <StatusBar style="dark" />
      <ScrollView
        style={styles.scroll}
        contentContainerStyle={[styles.content, { paddingTop: insets.top + spacing.xl }]}
        showsVerticalScrollIndicator={false}
      >
        {/* Header */}
        <Animated.View
          style={[
            styles.header,
            {
              opacity: headerAnim,
              transform: [
                {
                  translateY: headerAnim.interpolate({
                    inputRange: [0, 1],
                    outputRange: [16, 0],
                  }),
                },
              ],
            },
          ]}
        >
          <Text style={styles.headerTitle}>Analyse de tes recherches</Text>
          <Text style={styles.headerSubtitle}>
            Visualise la performance de tes candidatures et repère où concentrer tes efforts.
          </Text>
        </Animated.View>

        {/* KPI cards */}
        <Animated.View
          style={[
            styles.kpiRow,
            {
              opacity: cardsAnim,
              transform: [
                {
                  translateY: cardsAnim.interpolate({
                    inputRange: [0, 1],
                    outputRange: [24, 0],
                  }),
                },
              ],
            },
          ]}
        >
          <KpiCard
            icon="send"
            label="Candidatures envoyées"
            value="16"
            helper="Dans les 30 derniers jours"
            color="#4F46E5"
          />
          <KpiCard
            icon="document-text"
            label="CV analysés"
            value="85"
            helper="Analyses effectuées"
            color="#059669"
          />
        </Animated.View>

        <Animated.View
          style={[
            styles.kpiRow,
            {
              opacity: cardsAnim,
              transform: [
                {
                  translateY: cardsAnim.interpolate({
                    inputRange: [0, 1],
                    outputRange: [32, 0],
                  }),
                },
              ],
            },
          ]}
        >
          <KpiCard
            icon="chatbubbles"
            label="Entretiens décrochés"
            value="7"
            helper="En cours / à venir"
            color="#F97316"
          />
          <KpiCard
            icon="people"
            label="Nouveaux contacts"
            value="176"
            helper="Réseau dans les 30j"
            color="#EC4899"
          />
        </Animated.View>

        {/* Charts area */}
        <Animated.View
          style={[
            styles.chartsRow,
            {
              opacity: chartsAnim,
              transform: [
                {
                  translateY: chartsAnim.interpolate({
                    inputRange: [0, 1],
                    outputRange: [32, 0],
                  }),
                },
              ],
            },
          ]}
        >
          {/* Opportunités dans le temps (fake line chart) */}
          <View style={styles.chartCard}>
            <View style={styles.chartHeader}>
              <Text style={styles.chartTitle}>Croissance des opportunités</Text>
              <View style={styles.filterPill}>
                <Ionicons name="funnel-outline" size={14} color="#111827" />
                <Text style={styles.filterText}>Filtrer</Text>
              </View>
            </View>
            <View style={styles.lineChart}>
              <View style={styles.lineTrack} />
              {/* Simple dots representing months */}
              {['Août', 'Sep', 'Oct', 'Nov', 'Déc', 'Jan', 'Fév', 'Mar'].map((m, i) => (
                <View key={m} style={styles.linePointWrapper}>
                  <View style={styles.lineDot} />
                  <Text style={styles.axisLabel}>{m}</Text>
                </View>
              ))}
            </View>
          </View>

          {/* Opportunités par statut (fake bar chart) */}
          <View style={styles.chartCard}>
            <View style={styles.chartHeader}>
              <Text style={styles.chartTitle}>Opportunités par statut</Text>
              <View style={styles.filterPill}>
                <Ionicons name="options-outline" size={14} color="#111827" />
                <Text style={styles.filterText}>Filtrer</Text>
              </View>
            </View>
            <View style={styles.barChart}>
              {[40, 80, 100, 70].map((h, i) => (
                <View key={i} style={styles.barWrapper}>
                  <View style={[styles.bar, { height: 20 + h }]} />
                </View>
              ))}
              <View style={styles.barAxisLabels}>
                <Text style={styles.axisLabel}>À postuler</Text>
                <Text style={styles.axisLabel}>Envoyées</Text>
                <Text style={styles.axisLabel}>Relance</Text>
                <Text style={styles.axisLabel}>Entretiens</Text>
              </View>
            </View>
          </View>
        </Animated.View>

        {/* Recent activity list */}
        <Animated.View
          style={[
            styles.listSection,
            {
              opacity: listAnim,
              transform: [
                {
                  translateY: listAnim.interpolate({
                    inputRange: [0, 1],
                    outputRange: [32, 0],
                  }),
                },
              ],
            },
          ]}
        >
          <Text style={styles.sectionTitle}>Activité récente</Text>
          {SAMPLE_ACTIVITY.map((item) => (
            <ActivityRow key={item.id} item={item} />
          ))}
        </Animated.View>
      </ScrollView>
    </View>
  );
}

type ActivityItem = {
  id: string;
  role: string;
  company: string;
  status: string;
  progress: number;
  initial: string;
};

const SAMPLE_ACTIVITY: ActivityItem[] = [
  {
    id: '1',
    role: "Développeur Logiciel Stagiaire",
    company: 'Google Jobs',
    status: 'À postuler',
    progress: 80,
    initial: 'G',
  },
  {
    id: '2',
    role: 'Ingénieur.e Études et Développement Python (H/F)',
    company: 'Parrot',
    status: 'Candidature envoyée',
    progress: 80,
    initial: 'P',
  },
  {
    id: '3',
    role: 'Business Developer',
    company: "Gozem - Africa's Super App",
    status: 'Relance requise',
    progress: 80,
    initial: 'G',
  },
  {
    id: '4',
    role: 'Software Engineer - Frontend / Fullstack',
    company: 'Vellum',
    status: 'Entretien prévu',
    progress: 80,
    initial: 'V',
  },
];

function KpiCard(props: {
  icon: string;
  label: string;
  value: string;
  helper: string;
  color: string;
}) {
  const { icon, label, value, helper, color } = props;
  return (
    <View style={styles.kpiCard}>
      <View style={[styles.kpiIconCircle, { backgroundColor: `${color}1A` }]}>
        <Ionicons name={icon as any} size={18} color={color} />
      </View>
      <Text style={styles.kpiLabel}>{label}</Text>
      <Text style={[styles.kpiValue, { color }]}>{value}</Text>
      <Text style={styles.kpiHelper}>{helper}</Text>
    </View>
  );
}

function ActivityRow({ item }: { item: ActivityItem }) {
  return (
    <View style={styles.activityRow}>
      <View style={styles.activityLeft}>
        <View style={styles.activityAvatar}>
          <Text style={styles.activityAvatarText}>{item.initial}</Text>
        </View>
        <View style={styles.activityTexts}>
          <Text style={styles.activityRole} numberOfLines={1}>
            {item.role}
          </Text>
          <Text style={styles.activityCompany}>{item.company}</Text>
        </View>
      </View>
      <View style={styles.activityRight}>
        <View style={styles.statusPill}>
          <Text style={styles.statusText}>{item.status}</Text>
        </View>
        <View style={styles.progressTrack}>
          <View style={[styles.progressFill, { width: `${item.progress}%` }]} />
        </View>
        <Text style={styles.progressValue}>{item.progress}%</Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  root: {
    flex: 1,
    backgroundColor: '#FAFAF8',
  },
  scroll: {
    flex: 1,
  },
  content: {
    paddingHorizontal: spacing.lg,
    paddingBottom: 120,
  },
  header: {
    marginBottom: spacing['2xl'],
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: '800',
    color: '#111827',
    letterSpacing: -0.5,
    marginBottom: spacing.xs,
  },
  headerSubtitle: {
    fontSize: 13,
    color: '#6B7280',
    lineHeight: 20,
  },
  kpiRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: spacing.md,
  },
  kpiCard: {
    width: (width - spacing.lg * 2 - spacing.md) / 2,
    backgroundColor: '#FFFFFF',
    borderRadius: 18,
    paddingVertical: spacing.md,
    paddingHorizontal: spacing.md,
    borderWidth: 1,
    borderColor: '#F3F4F6',
    shadowColor: '#000000',
    shadowOffset: { width: 0, height: 10 },
    shadowOpacity: 0.04,
    shadowRadius: 20,
    elevation: 3,
  },
  kpiIconCircle: {
    width: 32,
    height: 32,
    borderRadius: 16,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: spacing.sm,
  },
  kpiLabel: {
    fontSize: 11,
    fontWeight: '600',
    letterSpacing: 0.5,
    textTransform: 'uppercase',
    color: '#6B7280',
    marginBottom: spacing.xs,
  },
  kpiValue: {
    fontSize: 22,
    fontWeight: '800',
    marginBottom: 2,
  },
  kpiHelper: {
    fontSize: 11,
    color: '#9CA3AF',
  },
  chartsRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: spacing['2xl'],
  },
  chartCard: {
    width: (width - spacing.lg * 2 - spacing.md) / 2,
    backgroundColor: '#FFFFFF',
    borderRadius: 18,
    padding: spacing.md,
    borderWidth: 1,
    borderColor: '#F3F4F6',
    shadowColor: '#000000',
    shadowOffset: { width: 0, height: 10 },
    shadowOpacity: 0.03,
    shadowRadius: 18,
    elevation: 2,
  },
  chartHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.md,
  },
  chartTitle: {
    fontSize: 13,
    fontWeight: '700',
    color: '#111827',
  },
  filterPill: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 999,
    backgroundColor: '#F9FAFB',
  },
  filterText: {
    fontSize: 11,
    fontWeight: '600',
    marginLeft: 4,
    color: '#111827',
  },
  lineChart: {
    height: 140,
    justifyContent: 'flex-end',
  },
  lineTrack: {
    position: 'absolute',
    left: 0,
    right: 0,
    top: 30,
    bottom: 40,
    borderRadius: 999,
    borderWidth: 1,
    borderColor: '#E5E7EB',
  },
  linePointWrapper: {
    flexDirection: 'column',
    alignItems: 'center',
    flex: 1,
  },
  lineDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: '#4F46E5',
    marginBottom: spacing.xs,
  },
  axisLabel: {
    fontSize: 9,
    color: '#9CA3AF',
  },
  barChart: {
    height: 140,
    justifyContent: 'space-between',
  },
  barWrapper: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    flex: 1,
    marginHorizontal: 4,
  },
  bar: {
    flex: 1,
    borderRadius: 8,
    backgroundColor: '#4F46E5',
  },
  barAxisLabels: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: spacing.sm,
  },
  listSection: {
    marginTop: spacing['2xl'],
  },
  sectionTitle: {
    fontSize: 15,
    fontWeight: '700',
    color: '#111827',
    marginBottom: spacing.md,
  },
  activityRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    paddingVertical: spacing.md,
    paddingHorizontal: spacing.md,
    marginBottom: spacing.sm,
    borderWidth: 1,
    borderColor: '#F3F4F6',
    shadowColor: '#000000',
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.03,
    shadowRadius: 16,
    elevation: 2,
  },
  activityLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
    marginRight: spacing.md,
  },
  activityAvatar: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: '#EEF2FF',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: spacing.md,
  },
  activityAvatarText: {
    fontSize: 13,
    fontWeight: '700',
    color: '#4F46E5',
  },
  activityTexts: {
    flex: 1,
  },
  activityRole: {
    fontSize: 13,
    fontWeight: '700',
    color: '#111827',
    marginBottom: 2,
  },
  activityCompany: {
    fontSize: 11,
    color: '#6B7280',
  },
  activityRight: {
    alignItems: 'flex-end',
  },
  statusPill: {
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 999,
    backgroundColor: '#EEF2FF',
    marginBottom: spacing.xs,
  },
  statusText: {
    fontSize: 10,
    fontWeight: '700',
    color: '#4F46E5',
  },
  progressTrack: {
    width: 90,
    height: 4,
    borderRadius: 999,
    backgroundColor: '#E5E7EB',
    overflow: 'hidden',
    marginBottom: 2,
  },
  progressFill: {
    height: 4,
    borderRadius: 999,
    backgroundColor: '#F59E0B',
  },
  progressValue: {
    fontSize: 10,
    color: '#6B7280',
    fontWeight: '600',
    textAlign: 'right',
  },
});

