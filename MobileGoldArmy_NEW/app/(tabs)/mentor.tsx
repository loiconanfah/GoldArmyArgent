import React, { useRef } from 'react';
import { View, Text, ScrollView, TouchableOpacity, Animated, KeyboardAvoidingView, Platform } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { StatusBar } from 'expo-status-bar';
import { spacing } from '../../src/theme/spacing';
import { useFocusEffect, useRouter } from 'expo-router';
import { mentorService } from '../../src/services/mentorService';
import { styles } from './_styles/mentor.styles';

interface InterviewItem {
  id: string;
  title: string;
  company: string;
  date: string;
  status: 'planifie' | 'termine' | 'annule';
  score?: number;
}

const formatDate = (iso: string) => {
  if (!iso) return '';
  const d = new Date(iso);
  const options: Intl.DateTimeFormatOptions = { day: '2-digit', month: 'short', year: 'numeric' };
  return d.toLocaleDateString('fr-FR', options) + ' • ' + d.toLocaleTimeString('fr-FR', {
    hour: '2-digit', minute: '2-digit'
  });
};

const MENTOR_TIPS = [
  { id: 'tip-1', title: 'Structure STAR', desc: 'Situe le Contexte, explique la Tâche, détaille les Actions et termine par les Résultats.', icon: 'trail-sign-outline' as const },
  { id: 'tip-2', title: 'Gérer le stress', desc: 'Prépare 3 histoires fortes à raconter, le reste de l’entretien devient plus fluide.', icon: 'sparkles-outline' as const },
  { id: 'tip-3', title: 'Questions à poser', desc: 'Note 3 questions sur le poste, l’équipe et les prochains défis avant chaque entretien.', icon: 'help-circle-outline' as const },
];

export default function MentorScreen() {
  const insets = useSafeAreaInsets();
  const router = useRouter();
  const heroAnim = useRef(new Animated.Value(0)).current;
  const cardsAnim = useRef(new Animated.Value(0)).current;
  const listAnim = useRef(new Animated.Value(0)).current;

  const [sessions, setSessions] = React.useState<InterviewItem[]>([]);
  const [loadingHistory, setLoadingHistory] = React.useState(true);

  React.useEffect(() => {
    Animated.stagger(120, [
      Animated.timing(heroAnim, { toValue: 1, duration: 450, useNativeDriver: true }),
      Animated.timing(cardsAnim, { toValue: 1, duration: 450, useNativeDriver: true }),
      Animated.timing(listAnim, { toValue: 1, duration: 450, useNativeDriver: true }),
    ]).start();
  }, [heroAnim, cardsAnim, listAnim]);

  useFocusEffect(
    React.useCallback(() => {
      let isActive = true;
      const fetchHistory = async () => {
        setLoadingHistory(true);
        try {
          const res = await mentorService.getInterviewHistory();
          if (isActive && res.sessions) {
            const mapped: InterviewItem[] = res.sessions.map((s: any) => ({
              id: s.session_id || Math.random().toString(),
              title: s.job_title || 'Entretien IA',
              company: s.company || 'Général',
              date: formatDate(s.created_at),
              status: 'termine',
              score: s.scores?.overall ? Math.round(s.scores.overall * 10) : undefined,
            }));
            setSessions(mapped);
          }
        } catch (e) {
          console.error("Failed to fetch mentor history", e);
        } finally {
          if (isActive) setLoadingHistory(false);
        }
      };
      fetchHistory();
      return () => { isActive = false; };
    }, [])
  );

  const handleOpenAuditCv = () => router.push('/mentor-audit-cv');
  const handleOpenSimulator = () => router.push('/mentor-simulator');

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
        <Animated.View
          style={[
            styles.hero,
            {
              opacity: heroAnim,
              transform: [{ translateY: heroAnim.interpolate({ inputRange: [0, 1], outputRange: [16, 0] }) }],
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
        </Animated.View>

        <Animated.View
          style={[
            styles.actionsRow,
            {
              opacity: cardsAnim,
              transform: [{ translateY: cardsAnim.interpolate({ inputRange: [0, 1], outputRange: [16, 0] }) }],
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

        <Animated.View
          style={[
            styles.historySection,
            {
              opacity: listAnim,
              transform: [{ translateY: listAnim.interpolate({ inputRange: [0, 1], outputRange: [16, 0] }) }],
            },
          ]}
        >
          <View style={styles.historyHeader}>
            <Text style={styles.historyTitle}>Historique des entretiens</Text>
            <Text style={styles.historyCount}>{sessions.length} sessions</Text>
          </View>

          <View style={styles.filterRow}>
            <Text style={[styles.filterPill, styles.filterPillActive]}>Tous</Text>
            <Text style={styles.filterPill}>À venir</Text>
            <Text style={styles.filterPill}>Passés</Text>
          </View>

          <View style={styles.historyList}>
            {loadingHistory ? (
              <View style={{ padding: 20, alignItems: 'center' }}>
                <Text style={{ color: '#666' }}>Chargement de l'historique...</Text>
              </View>
            ) : sessions.length === 0 ? (
              <View style={{ padding: 20, alignItems: 'center' }}>
                <Text style={{ color: '#666' }}>Aucun entretien pour l'instant.</Text>
              </View>
            ) : (
              sessions.map((item) => (
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
                    <View style={[styles.statusBadge, styles.statusDone]}>
                      <Text style={styles.statusText}>Terminé</Text>
                    </View>
                  </View>
                </View>
              ))
            )}
          </View>
        </Animated.View>

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
