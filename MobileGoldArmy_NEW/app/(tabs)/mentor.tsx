import React, { useRef } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, Animated, KeyboardAvoidingView, Platform } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { StatusBar } from 'expo-status-bar';
import { spacing } from '../../src/theme/spacing';
import { useRouter } from 'expo-router';

interface InterviewItem {
  id: string;
  title: string;
  company: string;
  date: string;
  status: 'planifie' | 'termine' | 'annule';
  score?: number; // optionnel
}

const MOCK_INTERVIEWS: InterviewItem[] = [
  {
    id: '1',
    title: 'Entretien Product Designer',
    company: 'Stripe',
    date: 'Hier • 15:30',
    status: 'termine',
    score: 86,
  },
  {
    id: '2',
    title: 'Screening UX/UI',
    company: 'Figma',
    date: 'Demain • 10:00',
    status: 'planifie',
  },
  {
    id: '3',
    title: 'Entretien technique',
    company: 'Airbnb',
    date: 'Lundi • 14:00',
    status: 'planifie',
  },
];

const MENTOR_TIPS = [
  {
    id: 'tip-1',
    title: 'Structure STAR',
    desc: 'Situe le Contexte, explique la Tâche, détaille les Actions et termine par les Résultats.',
    icon: 'trail-sign-outline' as const,
  },
  {
    id: 'tip-2',
    title: 'Gérer le stress',
    desc: 'Prépare 3 histoires fortes à raconter, le reste de l’entretien devient plus fluide.',
    icon: 'sparkles-outline' as const,
  },
  {
    id: 'tip-3',
    title: 'Questions à poser',
    desc: 'Note 3 questions sur le poste, l’équipe et les prochains défis avant chaque entretien.',
    icon: 'help-circle-outline' as const,
  },
];

export default function MentorScreen() {
  const insets = useSafeAreaInsets();
  const router = useRouter();
  const heroAnim = useRef(new Animated.Value(0)).current;
  const cardsAnim = useRef(new Animated.Value(0)).current;
  const listAnim = useRef(new Animated.Value(0)).current;

  React.useEffect(() => {
    Animated.stagger(120, [
      Animated.timing(heroAnim, { toValue: 1, duration: 450, useNativeDriver: true }),
      Animated.timing(cardsAnim, { toValue: 1, duration: 450, useNativeDriver: true }),
      Animated.timing(listAnim, { toValue: 1, duration: 450, useNativeDriver: true }),
    ]).start();
  }, [heroAnim, cardsAnim, listAnim]);

  const handleOpenAuditCv = () => {
    // Page dédiée définie dans app/mentor-audit-cv.tsx
    router.push('/mentor-audit-cv');
  };

  const handleOpenSimulator = () => {
    console.log('[Mentor] Simulateur d’entretien cliqué');
  };

  return (
    <KeyboardAvoidingView
      style={styles.root}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
    >
      <StatusBar style="dark" />
      <ScrollView
        style={styles.scroll}
        contentContainerStyle={[
          styles.content,
          { paddingTop: insets.top + spacing.xl, paddingBottom: insets.bottom + 100 },
        ]}
        showsVerticalScrollIndicator={false}
      >
        {/* HERO */}
        <Animated.View
          style={[
            styles.hero,
            {
              opacity: heroAnim,
              transform: [
                {
                  translateY: heroAnim.interpolate({
                    inputRange: [0, 1],
                    outputRange: [16, 0],
                  }),
                },
              ],
            },
          ]}
        >
          <View style={styles.heroIcon}>
            <Ionicons name="mic-outline" size={24} color="#1A1A1A" />
          </View>
          <View style={styles.heroTextContainer}>
            <Text style={styles.heroEyebrow}>COACH D&apos;ENTRETIEN IA</Text>
            <Text style={styles.heroTitle}>Mentor IA</Text>
            <Text style={styles.heroSubtitle}>
              Rejoue tes entretiens, analyse tes réponses et prépare les prochains en conditions réelles.
            </Text>
          </View>
          <View style={styles.nextBadge}>
            <Text style={styles.nextBadgeLabel}>Prochain</Text>
            <Text style={styles.nextBadgeValue}>Demain • 10:00</Text>
          </View>
        </Animated.View>

        {/* ACTION CARDS */}
        <Animated.View
          style={[
            styles.actionsRow,
            {
              opacity: cardsAnim,
              transform: [
                {
                  translateY: cardsAnim.interpolate({
                    inputRange: [0, 1],
                    outputRange: [16, 0],
                  }),
                },
              ],
            },
          ]}
        >
          <TouchableOpacity style={styles.actionCard} activeOpacity={0.9} onPress={handleOpenAuditCv}>
            <Text style={styles.actionTag}>CV & Branding</Text>
            <View style={styles.actionIconWrapper}>
              <Ionicons name="document-text-outline" size={22} color="#1A1A1A" />
            </View>
            <Text style={styles.actionTitle}>Audit & Correction de CV</Text>
            <Text style={styles.actionSubtitle}>
              Analyse ton CV, détecte les faiblesses et reçois une version optimisée pour les ATS.
            </Text>
            <View style={styles.actionFooter}>
              <Text style={styles.actionCta}>Lancer un audit complet</Text>
              <Ionicons name="arrow-forward" size={16} color="#1A1A1A" />
            </View>
          </TouchableOpacity>

          <TouchableOpacity style={styles.actionCard} activeOpacity={0.9} onPress={handleOpenSimulator}>
            <Text style={styles.actionTag}>Oral & Storytelling</Text>
            <View style={styles.actionIconWrapper}>
              <Ionicons name="chatbubbles-outline" size={22} color="#1A1A1A" />
            </View>
            <Text style={styles.actionTitle}>Simulateur d’entretien</Text>
            <Text style={styles.actionSubtitle}>
              Lance une simulation temps réel avec questions ciblées et feedback structuré.
            </Text>
            <View style={styles.actionFooter}>
              <Text style={styles.actionCta}>Démarrer une simulation</Text>
              <Ionicons name="arrow-forward" size={16} color="#1A1A1A" />
            </View>
          </TouchableOpacity>
        </Animated.View>

        {/* HISTORIQUE ENTRETIENS */}
        <Animated.View
          style={[
            styles.historySection,
            {
              opacity: listAnim,
              transform: [
                {
                  translateY: listAnim.interpolate({
                    inputRange: [0, 1],
                    outputRange: [16, 0],
                  }),
                },
              ],
            },
          ]}
        >
          <View style={styles.historyHeader}>
            <Text style={styles.historyTitle}>Historique des entretiens</Text>
            <Text style={styles.historyCount}>{MOCK_INTERVIEWS.length} sessions</Text>
          </View>

          <View style={styles.filterRow}>
            <Text style={[styles.filterPill, styles.filterPillActive]}>Tous</Text>
            <Text style={styles.filterPill}>À venir</Text>
            <Text style={styles.filterPill}>Passés</Text>
          </View>

          <View style={styles.historyList}>
            {MOCK_INTERVIEWS.map((item) => (
              <View key={item.id} style={styles.historyCard}>
                <View style={styles.historyLeft}>
                  <View style={styles.historyIcon}>
                    <Ionicons name="person-circle-outline" size={22} color="#1A1A1A" />
                  </View>
                  <View style={styles.historyInfo}>
                    <Text style={styles.historyTitleText}>{item.title}</Text>
                    <Text style={styles.historyCompany}>{item.company}</Text>
                    <Text style={styles.historyDate}>{item.date}</Text>
                  </View>
                </View>
                <View style={styles.historyRight}>
                  {item.score != null && (
                    <View style={styles.scoreBadge}>
                      <Text style={styles.scoreText}>{item.score}%</Text>
                    </View>
                  )}
                  <View
                    style={[
                      styles.statusBadge,
                      item.status === 'planifie' && styles.statusPlanned,
                      item.status === 'termine' && styles.statusDone,
                      item.status === 'annule' && styles.statusCancelled,
                    ]}
                  >
                    <Text style={styles.statusText}>
                      {item.status === 'planifie'
                        ? 'Planifié'
                        : item.status === 'termine'
                        ? 'Terminé'
                        : 'Annulé'}
                    </Text>
                  </View>
                </View>
              </View>
            ))}
          </View>
        </Animated.View>

        {/* CONSEILS DU MENTOR */}
        <View style={styles.tipsSection}>
          <Text style={styles.tipsTitle}>Conseils du Mentor</Text>
          <View style={styles.tipsList}>
            {MENTOR_TIPS.map((tip) => (
              <View key={tip.id} style={styles.tipCard}>
                <View style={styles.tipIcon}>
                  <Ionicons name={tip.icon} size={18} color="#1A1A1A" />
                </View>
                <View style={styles.tipContent}>
                  <Text style={styles.tipTitle}>{tip.title}</Text>
                  <Text style={styles.tipDesc}>{tip.desc}</Text>
                </View>
              </View>
            ))}
          </View>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
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
    paddingHorizontal: spacing.xl,
    gap: spacing.xl,
  },
  hero: {
    flexDirection: 'row',
    alignItems: 'flex-start',
  },
  heroIcon: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: '#F5D061',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: spacing.md,
  },
  heroTextContainer: {
    flex: 1,
  },
  heroTitle: {
    fontSize: 24,
    fontWeight: '800',
    color: '#1A1A1A',
  },
  heroSubtitle: {
    fontSize: 13,
    color: '#666666',
    marginTop: 4,
  },
  heroEyebrow: {
    fontSize: 11,
    fontWeight: '600',
    color: '#999999',
    letterSpacing: 0.5,
    textTransform: 'uppercase',
    marginBottom: 2,
  },
  nextBadge: {
    alignItems: 'flex-end',
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    borderRadius: 12,
    backgroundColor: '#FFF7D6',
    marginLeft: spacing.md,
  },
  nextBadgeLabel: {
    fontSize: 10,
    fontWeight: '600',
    color: '#92400E',
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
  nextBadgeValue: {
    fontSize: 12,
    fontWeight: '700',
    color: '#1A1A1A',
  },
  actionsRow: {
    flexDirection: 'row',
    gap: spacing.md,
  },
  actionCard: {
    flex: 1,
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    padding: spacing.lg,
    borderWidth: 1,
    borderColor: '#EAEAE6',
  },
  actionTag: {
    fontSize: 11,
    fontWeight: '600',
    color: '#999999',
    textTransform: 'uppercase',
    marginBottom: spacing.sm,
  },
  actionIconWrapper: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: '#FFF7D6',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: spacing.sm,
  },
  actionTitle: {
    fontSize: 15,
    fontWeight: '700',
    color: '#1A1A1A',
    marginBottom: 4,
  },
  actionSubtitle: {
    fontSize: 12,
    color: '#666666',
    marginBottom: spacing.md,
  },
  actionFooter: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 'auto',
  },
  actionCta: {
    fontSize: 12,
    fontWeight: '600',
    color: '#1A1A1A',
    marginRight: 6,
  },
  historySection: {
    marginTop: spacing.sm,
  },
  historyHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'baseline',
    marginBottom: spacing.sm,
  },
  historyTitle: {
    fontSize: 18,
    fontWeight: '700',
    color: '#1A1A1A',
  },
  historyCount: {
    fontSize: 12,
    fontWeight: '500',
    color: '#666666',
  },
  filterRow: {
    flexDirection: 'row',
    gap: spacing.sm,
    marginBottom: spacing.sm,
  },
  filterPill: {
    fontSize: 12,
    fontWeight: '500',
    color: '#666666',
  },
  filterPillActive: {
    color: '#1A1A1A',
    textDecorationLine: 'underline',
  },
  historyList: {
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    borderWidth: 1,
    borderColor: '#EAEAE6',
  },
  historyCard: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
    borderBottomWidth: StyleSheet.hairlineWidth,
    borderBottomColor: '#EAEAE6',
  },
  historyLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  historyIcon: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: '#F5F5F3',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: spacing.md,
  },
  historyInfo: {
    flex: 1,
  },
  historyTitleText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#1A1A1A',
    marginBottom: 2,
  },
  historyCompany: {
    fontSize: 12,
    color: '#666666',
    marginBottom: 2,
  },
  historyDate: {
    fontSize: 12,
    color: '#999999',
  },
  historyRight: {
    alignItems: 'flex-end',
    justifyContent: 'space-between',
  },
  scoreBadge: {
    backgroundColor: '#ECFDF5',
    borderRadius: 999,
    paddingHorizontal: 8,
    paddingVertical: 2,
    marginBottom: spacing.xs,
  },
  scoreText: {
    fontSize: 12,
    fontWeight: '700',
    color: '#047857',
  },
  statusBadge: {
    borderRadius: 999,
    paddingHorizontal: 10,
    paddingVertical: 4,
  },
  statusPlanned: {
    backgroundColor: '#EFF6FF',
  },
  statusDone: {
    backgroundColor: '#ECFDF5',
  },
  statusCancelled: {
    backgroundColor: '#FEF2F2',
  },
  statusText: {
    fontSize: 11,
    fontWeight: '600',
    color: '#1A1A1A',
  },
  tipsSection: {
    marginTop: spacing.xl,
    marginBottom: spacing['2xl'],
  },
  tipsTitle: {
    fontSize: 18,
    fontWeight: '700',
    color: '#1A1A1A',
    marginBottom: spacing.sm,
  },
  tipsList: {
    gap: spacing.sm,
  },
  tipCard: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    backgroundColor: '#FFFFFF',
    borderRadius: 14,
    padding: spacing.md,
    borderWidth: 1,
    borderColor: '#EAEAE6',
  },
  tipIcon: {
    width: 28,
    height: 28,
    borderRadius: 14,
    backgroundColor: '#F5F5F3',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: spacing.md,
  },
  tipContent: {
    flex: 1,
  },
  tipTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#1A1A1A',
    marginBottom: 2,
  },
  tipDesc: {
    fontSize: 12,
    color: '#666666',
  },
});

