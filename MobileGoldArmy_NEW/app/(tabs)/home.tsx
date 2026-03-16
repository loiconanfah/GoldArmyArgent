/**
 * Home Screen - Professional Dribbble-Inspired UI
 * "Executive Dashboard" style with Bento card layouts, soft shadows & subtle animations
 */

import React, { useEffect, useMemo, useRef } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, Dimensions, Animated, Easing } from 'react-native';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';
import { StatusBar } from 'expo-status-bar';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { useAuthStore } from '../../src/stores/authStore';
import { spacing } from '../../src/theme/spacing';
import { TOOLS, toolTheme } from '../../src/data/tools';
import type { ToolData } from '../../src/types/tool.types';

const { width } = Dimensions.get('window');

const TIPS = [
  { id: 1, title: 'Optimisation CV', desc: 'Analysez votre CV en 30s. Utilisez l\'IA pour intégrer les mots-clés parfaits.', icon: 'document-text', color: '#60A5FA' },
  { id: 2, title: 'Méthode Sniper', desc: 'La qualité bat la quantité. Ciblez 5 candidatures ultra-pertinentes par jour.', icon: 'flame', color: '#F5D061' },
  { id: 3, title: 'Simulation', desc: 'Entraînez-vous avec le Mentor IA pour détruire le stress de l\'entretien.', icon: 'mic', color: '#10B981' },
];

export default function HomeScreen() {
  const { user } = useAuthStore();
  const router = useRouter();
  const insets = useSafeAreaInsets();

  // Simple mount animations for hero, stats and tools sections
  const heroAnim = useRef(new Animated.Value(0)).current;
  const statsAnim = useRef(new Animated.Value(0)).current;
  const toolsAnim = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    Animated.stagger(120, [
      Animated.timing(heroAnim, {
        toValue: 1,
        duration: 550,
        easing: Easing.out(Easing.ease),
        useNativeDriver: true,
      }),
      Animated.timing(statsAnim, {
        toValue: 1,
        duration: 550,
        easing: Easing.out(Easing.ease),
        useNativeDriver: true,
      }),
      Animated.timing(toolsAnim, {
        toValue: 1,
        duration: 550,
        easing: Easing.out(Easing.ease),
        useNativeDriver: true,
      }),
    ]).start();
  }, [heroAnim, statsAnim, toolsAnim]);

  const firstName = useMemo(() => {
    if (user?.firstName) return user.firstName;
    if (!user?.email) return 'Toi';
    const beforeAt = user.email.split('@')[0];
    const clean = beforeAt.split(/[.\s_-]/)[0];
    return clean.charAt(0).toUpperCase() + clean.slice(1);
  }, [user?.firstName, user?.email]);

  const handleOpenTool = (tool: ToolData) => {
    router.push(tool.route as any);
  };

  return (
    <View style={styles.root}>
      <StatusBar style="dark" />
      <ScrollView
        style={styles.scrollView}
        contentContainerStyle={[
          styles.content,
          { paddingTop: insets.top + spacing['2xl'] }
        ]}
        showsVerticalScrollIndicator={false}
      >
        {/* DÉCORATION D'ARRIÈRE PLAN ABSTRAITE */}
        <View style={styles.abstractGlow1} />
        <View style={styles.abstractGlow2} />

        {/* HERO SECTION - EXECUTIVE GREETING */}
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
          <View style={styles.heroRow}>
            <View>
              <Text style={styles.heroDate}>
                VOTRE DASHBOARD
              </Text>
              <Text style={styles.heroTitle}>
                Bonjour, <Text style={styles.heroName}>{firstName}</Text>
              </Text>
            </View>
            <View style={styles.avatarPlaceholder}>
              <Ionicons name="person" size={20} color="#FFFFFF" />
            </View>
          </View>
          <Text style={styles.heroSubtitle}>
            Votre arsenal IA est prêt. Préparez-vous à décrocher votre prochain challenge.
          </Text>
        </Animated.View>

        {/* STATS BENTO GRID */}
        <Animated.View
          style={[
            styles.statsContainer,
            {
              opacity: statsAnim,
              transform: [
                {
                  translateY: statsAnim.interpolate({
                    inputRange: [0, 1],
                    outputRange: [24, 0],
                  }),
                },
              ],
            },
          ]}
        >
          <View style={styles.statBox}>
            <View style={[styles.statIconBox, { backgroundColor: 'rgba(245, 208, 97, 0.15)' }]}>
              <Ionicons name="rocket" size={18} color="#F5D061" />
            </View>
            <Text style={styles.statValue}>5</Text>
            <Text style={styles.statLabel}>Outils IA</Text>
          </View>
          
          <View style={styles.statBox}>
            <View style={[styles.statIconBox, { backgroundColor: 'rgba(96, 165, 250, 0.15)' }]}>
              <Ionicons name="scan" size={18} color="#60A5FA" />
            </View>
            <Text style={styles.statValue}>50+</Text>
            <Text style={styles.statLabel}>Sources</Text>
          </View>
          
          <View style={styles.statBox}>
            <View style={[styles.statIconBox, { backgroundColor: 'rgba(16, 185, 129, 0.15)' }]}>
              <Ionicons name="flash" size={18} color="#10B981" />
            </View>
            <Text style={styles.statValue}>30s</Text>
            <Text style={styles.statLabel}>Audit CV</Text>
          </View>
          
          <View style={styles.statBox}>
            <View style={[styles.statIconBox, { backgroundColor: 'rgba(187, 134, 252, 0.15)' }]}>
              <Ionicons name="infinite" size={18} color="#BB86FC" />
            </View>
            <Text style={styles.statValue}>∞</Text>
            <Text style={styles.statLabel}>Candidatures</Text>
          </View>
        </Animated.View>

        {/* OUTILS IA - LISTE PREMIUM */}
        <Animated.View
          style={[
            styles.toolsSection,
            {
              opacity: toolsAnim,
              transform: [
                {
                  translateY: toolsAnim.interpolate({
                    inputRange: [0, 1],
                    outputRange: [32, 0],
                  }),
                },
              ],
            },
          ]}
        >
          <View style={styles.sectionHeader}>
            <Text style={styles.sectionTitle}>
              Suite d'outils
            </Text>
            <TouchableOpacity hitSlop={{ top: 10, bottom: 10, left: 10, right: 10 }}>
              <Ionicons name="ellipsis-horizontal" size={24} color="#A0A0A0" />
            </TouchableOpacity>
          </View>

          {TOOLS.map((tool) => (
            <ToolCard
              key={tool.id}
              tool={tool}
              onPress={() => handleOpenTool(tool)}
            />
          ))}
        </Animated.View>

        {/* NOUVELLE SECTION - CONSEILS & STRATÉGIE */}
        <Animated.View style={[styles.tipsSection, { opacity: toolsAnim }]}>
          <View style={styles.sectionHeader}>
            <Text style={styles.sectionTitle}>
              Conseils Stratégiques
            </Text>
            <TouchableOpacity>
              <Text style={styles.seeAllText}>Voir tout</Text>
            </TouchableOpacity>
          </View>
          <ScrollView 
            horizontal 
            showsHorizontalScrollIndicator={false}
            contentContainerStyle={styles.tipsScrollContainer}
            decelerationRate="fast"
            snapToInterval={width * 0.75 + spacing.md}
          >
            {TIPS.map((tip) => (
              <TouchableOpacity activeOpacity={0.9} key={tip.id} style={styles.tipCard}>
                <View style={[styles.tipIconBox, { backgroundColor: `rgba(${hexToRgb(tip.color)}, 0.1)` }]}>
                  <Ionicons name={tip.icon as any} size={20} color={tip.color} />
                </View>
                <Text style={styles.tipTitle}>{tip.title}</Text>
                <Text style={styles.tipDesc} numberOfLines={3}>{tip.desc}</Text>
              </TouchableOpacity>
            ))}
          </ScrollView>
        </Animated.View>

        {/* CTA FINAL DE CONVERSION */}
        <View style={styles.ctaWrapper}>
          <LinearGradient
            colors={['rgba(245, 208, 97, 0.9)', 'rgba(230, 163, 47, 1)']}
            start={{ x: 0, y: 0 }}
            end={{ x: 1, y: 1 }}
            style={styles.ctaGradient}
          >
            <View style={styles.ctaContent}>
              <View style={styles.ctaIconRing}>
                <Ionicons name="search" size={28} color="#1A1A1A" />
              </View>
              <View style={styles.ctaTexts}>
                <Text style={styles.ctaTitle}>Lancer Sniper Search</Text>
                <Text style={styles.ctaSubtitle}>Trouvez votre futur employeur dès aujourd'hui.</Text>
              </View>
              <TouchableOpacity
                activeOpacity={0.8}
                style={styles.ctaAction}
                onPress={() => router.push('/(tabs)/sniper' as any)}
              >
                <Ionicons name="arrow-forward" size={24} color="#FFFFFF" />
              </TouchableOpacity>
            </View>
          </LinearGradient>
        </View>
      </ScrollView>
    </View>
  );
}

function ToolCard({
  tool,
  onPress,
}: {
  tool: ToolData;
  onPress: () => void;
}) {
  const { color } = toolTheme(tool.id);

  // Press feedback animation for each card
  const scale = useRef(new Animated.Value(1)).current;
  const arrowAnim = useRef(new Animated.Value(0)).current;
  const flashAnim = useRef(new Animated.Value(0.3)).current;

  useEffect(() => {
    Animated.loop(
      Animated.sequence([
        Animated.timing(flashAnim, {
          toValue: 1,
          duration: 800,
          useNativeDriver: true,
        }),
        Animated.timing(flashAnim, {
          toValue: 0.3,
          duration: 800,
          useNativeDriver: true,
        }),
      ])
    ).start();
  }, [flashAnim]);

  const handlePressIn = () => {
    Animated.parallel([
      Animated.spring(scale, {
        toValue: 0.96,
        useNativeDriver: true,
        speed: 20,
        bounciness: 6,
      }),
      Animated.spring(arrowAnim, {
        toValue: 6,
        useNativeDriver: true,
        speed: 20,
      })
    ]).start();
  };

  const handlePressOut = () => {
    Animated.parallel([
      Animated.spring(scale, {
        toValue: 1,
        useNativeDriver: true,
        speed: 20,
        bounciness: 6,
      }),
      Animated.spring(arrowAnim, {
        toValue: 0,
        useNativeDriver: true,
        speed: 20,
      })
    ]).start();
  };

  return (
    <Animated.View style={[styles.toolCard, { transform: [{ scale }] }]}>
      <TouchableOpacity
        activeOpacity={0.8}
        onPressIn={handlePressIn}
        onPressOut={handlePressOut}
        onPress={onPress}
      >
        {/* En-tête de l'outil ultra-premium clair */}
        <View style={styles.toolHeroContent}>
          <View style={styles.toolHeroLeft}>
            <View style={[styles.toolHeroIconBubble, { backgroundColor: `rgba(${hexToRgb(color)}, 0.12)` }]}>
              <Ionicons name={tool.icon as any} size={20} color={color} />
            </View>
            <View style={styles.toolTitleWrapper}>
              <Text style={styles.toolHeroTitle}>{(tool as any).shortLabel ?? tool.title}</Text>
              <Text style={styles.toolHeroSubtitle} numberOfLines={1}>{tool.description}</Text>
            </View>
          </View>
          <View style={[styles.toolHeroChip, { backgroundColor: `rgba(${hexToRgb(color)}, 0.08)` }]}>
            <Animated.View style={{ opacity: flashAnim }}>
              <Ionicons name="flash" size={10} color={color} />
            </Animated.View>
            <Text style={[styles.toolHeroChipText, { color }]}>{tool.badge}</Text>
          </View>
        </View>

        {/* Action Button */}
        <View style={styles.toolActionArea}>
          <Text style={styles.toolActionText}>Ouvrir l'outil</Text>
          <Animated.View style={{ transform: [{ translateX: arrowAnim }] }}>
            <Ionicons name="arrow-forward" size={16} color="#A0A0A0" />
          </Animated.View>
        </View>

        {/* Footer Metrics */}
        <View style={styles.toolMetrics}>
          {tool.stats.slice(0, 2).map((s) => (
            <View key={s.label} style={styles.toolMetricItem}>
              <Text style={styles.toolMetricValue}>{s.value}</Text>
              <Text style={styles.toolMetricLabel}>{s.label}</Text>
            </View>
          ))}
        </View>
      </TouchableOpacity>
    </Animated.View>
  );
}

// Format Helper to convert Hex to rgb values for glassy opacity
function hexToRgb(hex: string) {
  var result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  return result ? 
    `${parseInt(result[1], 16)}, ${parseInt(result[2], 16)}, ${parseInt(result[3], 16)}` 
    : '255, 255, 255';
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
    paddingHorizontal: spacing.lg,
    paddingBottom: 140, // Extreme padding to scroll past absolute Navbar
  },
  // Abstract background decor
  abstractGlow1: {
    position: 'absolute',
    top: -100,
    right: -100,
    width: 300,
    height: 300,
    borderRadius: 150,
    backgroundColor: '#F5D061',
    opacity: 0.04,
    transform: [{ scale: 1.5 }],
  },
  abstractGlow2: {
    position: 'absolute',
    top: 200,
    left: -150,
    width: 350,
    height: 350,
    borderRadius: 175,
    backgroundColor: '#60A5FA',
    opacity: 0.03,
    transform: [{ scale: 1.2 }],
  },
  // Hero
  hero: {
    marginBottom: spacing['2xl'],
    marginTop: spacing.md,
  },
  heroRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.sm,
  },
  heroDate: {
    fontSize: 10,
    fontWeight: '800',
    letterSpacing: 2,
    marginBottom: 6,
    color: '#A0A0A0',
  },
  heroTitle: {
    fontSize: 28,
    fontWeight: '800',
    letterSpacing: -0.5,
    color: '#1A1A1A',
  },
  heroName: {
    color: '#F5D061',
  },
  avatarPlaceholder: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: '#333333',
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 2,
    borderColor: '#F5D061',
    shadowColor: '#F5D061',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.5,
    shadowRadius: 10,
  },
  heroSubtitle: {
    fontSize: 14,
    lineHeight: 22,
    maxWidth: '85%',
    color: '#6A6A64',
  },
  // Bento Stats
  statsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
    marginBottom: spacing['xl'],
  },
  statBox: {
    width: (width - spacing.xl * 2 - spacing.md) / 2,
    padding: spacing.md,
    borderRadius: 24,
    backgroundColor: '#FFFFFF',
    marginBottom: spacing.md,
    // Soft Dribbble-style shadow
    shadowColor: '#000000',
    shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 0.04,
    shadowRadius: 16,
    elevation: 2,
  },
  statIconBox: {
    width: 36,
    height: 36,
    borderRadius: 10,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: spacing.sm,
  },
  statValue: {
    fontSize: 24,
    fontWeight: '800',
    letterSpacing: -0.5,
    color: '#1A1A1A',
  },
  statLabel: {
    fontSize: 12,
    fontWeight: '600',
    marginTop: 2,
    color: '#9A9A94',
  },
  // Tools Section
  toolsSection: {
    marginBottom: spacing.xl,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.lg,
  },
  sectionTitle: {
    fontSize: 22,
    fontWeight: '800',
    letterSpacing: -0.5,
    color: '#1A1A1A',
  },
  // Tool Cards - Exquisite Light Dribbble UI
  toolCard: {
    borderRadius: 24,
    marginBottom: spacing.xl,
    backgroundColor: '#FFFFFF',
    borderWidth: 1,
    borderColor: '#F0F0EA',
    // Douce ombre luxueuse sur fond clair
    shadowColor: '#000000',
    shadowOffset: { width: 0, height: 16 },
    shadowOpacity: 0.04,
    shadowRadius: 32,
    elevation: 6,
    overflow: 'hidden',
  },
  toolHeroContent: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: spacing.lg,
    paddingBottom: spacing.md,
  },
  toolHeroLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  toolHeroIconBubble: {
    width: 44,
    height: 44,
    borderRadius: 16,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: spacing.md,
  },
  toolTitleWrapper: {
    flex: 1,
    paddingRight: spacing.md,
  },
  toolHeroTitle: {
    color: '#1A1A1A',
    fontSize: 17,
    fontWeight: '800',
    letterSpacing: -0.3,
    marginBottom: 2,
  },
  toolHeroSubtitle: {
    color: '#9A9A94',
    fontSize: 13,
    fontWeight: '500',
  },
  toolHeroChip: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 999,
  },
  toolHeroChipText: {
    fontSize: 11,
    fontWeight: '800',
    marginLeft: 6,
    letterSpacing: 0.5,
    textTransform: 'uppercase',
  },
  toolActionArea: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: spacing.lg,
    paddingBottom: spacing.lg,
  },
  toolActionText: {
    fontSize: 13,
    fontWeight: '700',
    color: '#1A1A1A',
    marginRight: 6,
  },
  toolMetrics: {
    flexDirection: 'row',
    borderTopWidth: 1,
    borderTopColor: '#F4F4F0',
    paddingVertical: spacing.md,
    paddingHorizontal: spacing.lg,
    backgroundColor: '#FDFDFD',
  },
  toolMetricItem: {
    marginRight: spacing.xl,
    flexDirection: 'row',
    alignItems: 'baseline',
  },
  toolMetricValue: {
    fontSize: 15,
    fontWeight: '800',
    color: '#1A1A1A',
    marginRight: 4,
  },
  toolMetricLabel: {
    fontSize: 11,
    fontWeight: '700',
    color: '#A0A0A0',
    letterSpacing: 0.5,
    textTransform: 'uppercase',
  },
  // Conseils Section
  tipsSection: {
    marginBottom: spacing['3xl'],
  },
  tipsScrollContainer: {
    paddingRight: spacing.lg, // Margin for end of scroll
  },
  seeAllText: {
    fontSize: 13,
    fontWeight: '700',
    color: '#FF6B35',
  },
  tipCard: {
    width: width * 0.75,
    backgroundColor: '#FFFFFF',
    borderRadius: 24,
    padding: spacing.lg,
    marginRight: spacing.md,
    borderWidth: 1,
    borderColor: '#F0F0EA',
    shadowColor: '#000000',
    shadowOffset: { width: 0, height: 12 },
    shadowOpacity: 0.03,
    shadowRadius: 20,
    elevation: 4,
  },
  tipIconBox: {
    width: 40,
    height: 40,
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: spacing.md,
  },
  tipTitle: {
    fontSize: 16,
    fontWeight: '800',
    color: '#1A1A1A',
    marginBottom: spacing.xs,
  },
  tipDesc: {
    fontSize: 13,
    color: '#6A6A64',
    lineHeight: 20,
  },
  // CTA
  ctaWrapper: {
    marginBottom: spacing['3xl'],
    marginTop: spacing.md,
    borderRadius: 24,
    shadowColor: '#F5D061',
    shadowOffset: { width: 0, height: 12 },
    shadowOpacity: 0.2,
    shadowRadius: 24,
    elevation: 8,
  },
  ctaGradient: {
    borderRadius: 24,
    padding: spacing.xl,
  },
  ctaContent: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  ctaIconRing: {
    width: 56,
    height: 56,
    borderRadius: 28,
    backgroundColor: 'rgba(255,255,255,0.25)',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: spacing.md,
  },
  ctaTexts: {
    flex: 1,
  },
  ctaTitle: {
    fontSize: 18,
    fontWeight: '800',
    color: '#1A1A1A',
    marginBottom: 4,
  },
  ctaSubtitle: {
    fontSize: 13,
    color: 'rgba(0,0,0,0.6)',
    lineHeight: 18,
  },
  ctaAction: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: '#1A1A1A',
    justifyContent: 'center',
    alignItems: 'center',
    marginLeft: spacing.md,
  },
});
