import React, { useEffect, useMemo, useRef } from 'react';
import { View, Text, ScrollView, TouchableOpacity, Animated, Easing } from 'react-native';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';
import { StatusBar } from 'expo-status-bar';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { useAuthStore } from '../../src/stores/authStore';
import { spacing } from '../../src/theme/spacing';
import { TOOLS, toolTheme } from '../../src/data/tools';
import type { ToolData } from '../../src/types/tool.types';
import { styles } from './_styles/home.styles';

const TIPS = [
  { id: 1, title: 'Optimisation CV', desc: 'Analysez votre CV en 30s. Utilisez l\'IA pour intégrer les mots-clés parfaits.', icon: 'document-text', color: '#60A5FA' },
  { id: 2, title: 'Méthode Sniper', desc: 'La qualité bat la quantité. Ciblez 5 candidatures ultra-pertinentes par jour.', icon: 'flame', color: '#F5D061' },
  { id: 3, title: 'Simulation', desc: 'Entraînez-vous avec le Mentor IA pour détruire le stress de l\'entretien.', icon: 'mic', color: '#10B981' },
];

export default function HomeScreen() {
  const { user } = useAuthStore();
  const router = useRouter();
  const insets = useSafeAreaInsets();

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
        <View style={styles.abstractGlow1} />
        <View style={styles.abstractGlow2} />

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
              <Text style={styles.heroDate}>VOTRE DASHBOARD</Text>
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
            <Text style={styles.sectionTitle}>Suite d'outils</Text>
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

        <Animated.View style={[styles.tipsSection, { opacity: toolsAnim }]}>
          <View style={styles.sectionHeader}>
            <Text style={styles.sectionTitle}>Conseils Stratégiques</Text>
            <TouchableOpacity>
              <Text style={styles.seeAllText}>Voir tout</Text>
            </TouchableOpacity>
          </View>
          <ScrollView 
            horizontal 
            showsHorizontalScrollIndicator={false}
            contentContainerStyle={{ paddingRight: spacing.lg }}
            decelerationRate="fast"
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

function ToolCard({ tool, onPress }: { tool: ToolData; onPress: () => void }) {
  const { color } = toolTheme(tool.id);
  const scale = useRef(new Animated.Value(1)).current;
  const arrowAnim = useRef(new Animated.Value(0)).current;
  const flashAnim = useRef(new Animated.Value(0.3)).current;

  useEffect(() => {
    Animated.loop(
      Animated.sequence([
        Animated.timing(flashAnim, { toValue: 1, duration: 800, useNativeDriver: true }),
        Animated.timing(flashAnim, { toValue: 0.3, duration: 800, useNativeDriver: true }),
      ])
    ).start();
  }, [flashAnim]);

  const handlePressIn = () => {
    Animated.parallel([
      Animated.spring(scale, { toValue: 0.96, useNativeDriver: true, speed: 20, bounciness: 6 }),
      Animated.spring(arrowAnim, { toValue: 6, useNativeDriver: true, speed: 20 })
    ]).start();
  };

  const handlePressOut = () => {
    Animated.parallel([
      Animated.spring(scale, { toValue: 1, useNativeDriver: true, speed: 20, bounciness: 6 }),
      Animated.spring(arrowAnim, { toValue: 0, useNativeDriver: true, speed: 20 })
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

        <View style={styles.toolActionArea}>
          <Text style={styles.toolActionText}>Ouvrir l'outil</Text>
          <Animated.View style={{ transform: [{ translateX: arrowAnim }] }}>
            <Ionicons name="arrow-forward" size={16} color="#A0A0A0" />
          </Animated.View>
        </View>

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

function hexToRgb(hex: string) {
  var result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  return result ? 
    `${parseInt(result[1], 16)}, ${parseInt(result[2], 16)}, ${parseInt(result[3], 16)}` 
    : '255, 255, 255';
}
