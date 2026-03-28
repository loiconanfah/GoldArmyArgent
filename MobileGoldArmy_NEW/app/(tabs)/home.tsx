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
import { Image } from 'expo-image';
import LottieView from 'lottie-react-native';
import { notificationService, Notification } from '../../src/services/notificationService';
import { styles } from './_styles/home.styles';
import * as Notifications from 'expo-notifications';
import { useUIStore } from '../../src/stores/uiStore';
import { TutorialOverlay } from '../../src/components/ui/TutorialOverlay';

const CAROUSEL_DATA = [
  {
    id: 1,
    title: '5 Outils IA',
    desc: 'L\'arsenal complet',
    color: '#F5D061',
    bgColor: 'rgba(245, 208, 97, 0.15)',
    icon: 'rocket',
  },
  {
    id: 2,
    title: '50+ Sources',
    desc: 'Scan en temps réel',
    color: '#60A5FA',
    bgColor: 'rgba(96, 165, 250, 0.15)',
    icon: 'scan',
  },
  {
    id: 3,
    title: 'Audit CV',
    desc: 'En 30 secondes',
    color: '#10B981',
    bgColor: 'rgba(16, 185, 129, 0.15)',
    icon: 'flash',
  },
  {
    id: 4,
    title: 'Candidatures',
    desc: 'Sans limite',
    color: '#BB86FC',
    bgColor: 'rgba(187, 134, 252, 0.15)',
    icon: 'infinite',
  }
];

const TIPS = [
  { id: 1, title: 'Optimisation CV', desc: 'Analysez votre CV en 30s. Utilisez l\'IA pour intégrer les mots-clés parfaits.', icon: 'document-text', color: '#60A5FA' },
  { id: 2, title: 'Méthode Sniper', desc: 'La qualité bat la quantité. Ciblez 5 candidatures ultra-pertinentes par jour.', icon: 'flame', color: '#F5D061' },
  { id: 3, title: 'Simulation', desc: 'Entraînez-vous avec le Mentor IA pour détruire le stress de l\'entretien.', icon: 'mic', color: '#10B981' },
];

export default function HomeScreen() {
  const { user } = useAuthStore();
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const [unreadCount, setUnreadCount] = React.useState(0);
  const { hasSeenTutorial, initializeTutorialState } = useUIStore();

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

    // Fetch notifications
    const fetchNotifs = async () => {
      const notifs = await notificationService.getNotifications();
      const unread = notifs.filter(n => !n.is_read).length;
      setUnreadCount(unread);
      Notifications.setBadgeCountAsync(unread).catch(console.error);
    };
    fetchNotifs();
    initializeTutorialState();
  }, [heroAnim, statsAnim, toolsAnim]);

  const firstName = useMemo(() => {
    if (user?.firstName) return user.firstName;
    if (!user?.email) return 'Toi';
    const beforeAt = user.email.split('@')[0];
    const clean = beforeAt.split(/[.\s_-]/)[0];
    return clean.charAt(0).toUpperCase() + clean.slice(1);
  }, [user?.firstName, user?.email]);

  const photoUrl = useMemo(() => {
    const rawUrl = (user as any)?.photo_url || (user as any)?.user_metadata?.photo_url || (user as any)?.user_metadata?.avatar_url || (user as any)?.avatar_url;
    return typeof rawUrl === 'string' && rawUrl.startsWith('http') ? rawUrl : null;
  }, [user]);

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
            <View style={{ flexDirection: 'row', alignItems: 'center', gap: spacing.md }}>
              <TouchableOpacity
                onPress={() => router.push('/notifications' as any)}
                style={{ position: 'relative', width: 44, height: 44, borderRadius: 22, backgroundColor: 'rgba(255,255,255,0.1)', justifyContent: 'center', alignItems: 'center' }}
              >
                <Ionicons name="notifications-outline" size={22} color="#1A1A1A" />
                {unreadCount > 0 && (
                  <View style={{ position: 'absolute', top: 10, right: 10, width: 8, height: 8, borderRadius: 4, backgroundColor: '#EF4444' }} />
                )}
              </TouchableOpacity>
              <TouchableOpacity onPress={() => router.push('/(tabs)/profile' as any)}>
                {photoUrl ? (
                  <Image source={{ uri: photoUrl }} style={{ width: 44, height: 44, borderRadius: 22, borderWidth: 2, borderColor: '#fff' }} contentFit="cover" />
                ) : (
                  <View style={styles.avatarPlaceholder}>
                    <Text style={{ color: '#FFF', fontSize: 16, fontWeight: '700' }}>{firstName.charAt(0)}</Text>
                  </View>
                )}
              </TouchableOpacity>
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
          <StatsCarousel />
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

          {TOOLS.map((tool) =>
            tool.id === 'sniper' ? (
              <SniperSearchCard
                key={tool.id}
                onPress={() => handleOpenTool(tool)}
              />
            ) : (
              <ToolCard
                key={tool.id}
                tool={tool}
                onPress={() => handleOpenTool(tool)}
              />
            )
          )}
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

      </ScrollView>
      
      {!hasSeenTutorial && <TutorialOverlay />}
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

function StatsCarousel() {
  const [currentIndex, setCurrentIndex] = React.useState(0);
  const fadeAnim = useRef(new Animated.Value(1)).current;
  const slideAnim = useRef(new Animated.Value(0)).current;
  const iconScaleAnim = useRef(new Animated.Value(1)).current;

  useEffect(() => {
    // Breathing animation for the icon to simulate Lottie motion
    Animated.loop(
      Animated.sequence([
        Animated.timing(iconScaleAnim, { toValue: 1.15, duration: 1500, useNativeDriver: true }),
        Animated.timing(iconScaleAnim, { toValue: 1, duration: 1500, useNativeDriver: true })
      ])
    ).start();

    const interval = setInterval(() => {
      // Fade out and slide up slightly
      Animated.parallel([
        Animated.timing(fadeAnim, { toValue: 0, duration: 300, useNativeDriver: true }),
        Animated.timing(slideAnim, { toValue: -15, duration: 300, useNativeDriver: true })
      ]).start(() => {
        // Change index instantly
        setCurrentIndex(prev => (prev + 1) % CAROUSEL_DATA.length);
        
        // Reset position to bottom
        slideAnim.setValue(15);
        
        // Fade in and slide up to center
        Animated.parallel([
          Animated.timing(fadeAnim, { toValue: 1, duration: 400, useNativeDriver: true }),
          Animated.spring(slideAnim, { toValue: 0, friction: 8, useNativeDriver: true })
        ]).start();
      });
    }, 3500);

    return () => clearInterval(interval);
  }, [fadeAnim, slideAnim]);

  const currentItem = CAROUSEL_DATA[currentIndex];

  return (
    <View style={{
      width: '100%',
      backgroundColor: '#1E293B',
      borderRadius: 24,
      overflow: 'hidden',
      borderWidth: 1,
      borderColor: '#334155',
      shadowColor: currentItem.color,
      shadowOffset: { width: 0, height: 10 },
      shadowOpacity: 0.15,
      shadowRadius: 20,
      elevation: 8,
      height: 160, // Fixed height for smooth transitions
    }}>
      <LinearGradient
        colors={[currentItem.bgColor, 'transparent']}
        style={{ position: 'absolute', top: 0, left: 0, right: 0, bottom: 0 }}
        start={{ x: 0, y: 0 }}
        end={{ x: 1, y: 1 }}
      />
      
      <Animated.View style={{
        flex: 1,
        flexDirection: 'row',
        alignItems: 'center',
        padding: 20,
        opacity: fadeAnim,
        transform: [{ translateY: slideAnim }]
      }}>
        {/* Left Side: Icon Breathing Animation */}
        <View style={{
          width: 90,
          height: 90,
          borderRadius: 24,
          backgroundColor: '#0F172A',
          justifyContent: 'center',
          alignItems: 'center',
          borderWidth: 1,
          borderColor: currentItem.color,
          marginRight: 20,
          overflow: 'hidden'
        }}>
          <Animated.View style={{ transform: [{ scale: iconScaleAnim }] }}>
            <Ionicons name={currentItem.icon as any} size={42} color={currentItem.color} />
          </Animated.View>
        </View>

        {/* Right Side: Text */}
        <View style={{ flex: 1, justifyContent: 'center' }}>
          <Text style={{
            fontSize: 26,
            fontWeight: '900',
            color: '#FFFFFF',
            marginBottom: 4,
            letterSpacing: -0.5,
          }}>
            {currentItem.title}
          </Text>
          <Text style={{
            fontSize: 14,
            fontWeight: '600',
            color: currentItem.color,
            textTransform: 'uppercase',
            letterSpacing: 1,
          }}>
            {currentItem.desc}
          </Text>
        </View>
      </Animated.View>

      {/* Progress Dots */}
      <View style={{
        position: 'absolute',
        bottom: 12,
        left: 0,
        right: 0,
        flexDirection: 'row',
        justifyContent: 'center',
        alignItems: 'center',
        gap: 6,
      }}>
        {CAROUSEL_DATA.map((_, idx) => (
          <View
             key={idx}
             style={{
               height: 4,
               width: idx === currentIndex ? 16 : 8,
               borderRadius: 2,
               backgroundColor: idx === currentIndex ? currentItem.color : '#475569',
             }}
          />
        ))}
      </View>
    </View>
  );
}

function hexToRgb(hex: string) {
  var result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  return result ? 
    `${parseInt(result[1], 16)}, ${parseInt(result[2], 16)}, ${parseInt(result[3], 16)}` 
    : '255, 255, 255';
}

function SniperSearchCard({ onPress }: { onPress: () => void }) {
  const pulseAnim = useRef(new Animated.Value(1)).current;
  const glowAnim = useRef(new Animated.Value(0)).current;
  const scale = useRef(new Animated.Value(1)).current;

  useEffect(() => {
    Animated.loop(
      Animated.sequence([
        Animated.timing(pulseAnim, { toValue: 1.4, duration: 600, useNativeDriver: true }),
        Animated.timing(pulseAnim, { toValue: 1, duration: 600, useNativeDriver: true }),
      ])
    ).start();

    Animated.loop(
      Animated.sequence([
        Animated.timing(glowAnim, { toValue: 1, duration: 1800, useNativeDriver: true }),
        Animated.timing(glowAnim, { toValue: 0, duration: 1800, useNativeDriver: true }),
      ])
    ).start();
  }, []);

  const borderGlow = glowAnim.interpolate({ inputRange: [0, 1], outputRange: ['rgba(245,208,97,0.25)', 'rgba(245,208,97,0.7)'] });
  
  return (
    <TouchableOpacity
      activeOpacity={0.92}
      onPress={onPress}
      onPressIn={() => Animated.spring(scale, { toValue: 0.97, useNativeDriver: true, speed: 30 }).start()}
      onPressOut={() => Animated.spring(scale, { toValue: 1, useNativeDriver: true, speed: 30 }).start()}
    >
      <Animated.View style={{ transform: [{ scale }] }}>
        <View style={sniperStyles.card}>
          {/* Dark gradient background */}
          <LinearGradient
            colors={['#0D1117', '#1A1F2E', '#0F172A']}
            start={{ x: 0, y: 0 }}
            end={{ x: 1, y: 1 }}
            style={StyleSheet.absoluteFill}
          />

          {/* Scope ring overlay — subtle background texture */}
          <View style={sniperStyles.scopeOverlay}>
            <View style={sniperStyles.scopeRingOuter}>
              <View style={sniperStyles.scopeRingInner}>
                <View style={sniperStyles.scopeCrosshairH} />
                <View style={sniperStyles.scopeCrosshairV} />
              </View>
            </View>
          </View>

          {/* Left content column */}
          <View style={sniperStyles.leftCol}>
            {/* Elite badge */}
            <View style={sniperStyles.badge}>
              <Animated.View style={[sniperStyles.pulseDot, { transform: [{ scale: pulseAnim }] }]} />
              <Text style={sniperStyles.badgeText}>MODE ÉLITE</Text>
            </View>

            <Text style={sniperStyles.title}>Sniper{'\n'}Search</Text>
            <Text style={sniperStyles.subtitle}>
              Ciblage IA ultra-précis{'\n'}sur 50+ sources
            </Text>

            {/* Stats row */}
            <View style={sniperStyles.statsRow}>
              <View style={sniperStyles.stat}>
                <Text style={sniperStyles.statValue}>50+</Text>
                <Text style={sniperStyles.statLabel}>Sources</Text>
              </View>
              <View style={sniperStyles.statDivider} />
              <View style={sniperStyles.stat}>
                <Text style={sniperStyles.statValue}>IA</Text>
                <Text style={sniperStyles.statLabel}>Ciblage</Text>
              </View>
            </View>

            {/* CTA button */}
            <TouchableOpacity style={sniperStyles.cta} onPress={onPress} activeOpacity={0.85}>
              <LinearGradient
                colors={['#F5D061', '#E6A32F']}
                start={{ x: 0, y: 0 }}
                end={{ x: 1, y: 0 }}
                style={sniperStyles.ctaGrad}
              >
                <Text style={sniperStyles.ctaText}>Lancer</Text>
                <Ionicons name="arrow-forward" size={14} color="#0D1117" />
              </LinearGradient>
            </TouchableOpacity>
          </View>

          {/* Animated Icon — right side */}
          <View style={sniperStyles.bulletWrapper}>
            {/* Outer rotating ring */}
            <Animated.View style={[sniperStyles.rotatingRing, {
              transform: [{
                rotate: glowAnim.interpolate({ inputRange: [0, 1], outputRange: ['0deg', '360deg'] })
              }]
            }]} />
            {/* Middle pulsing ring */}
            <Animated.View style={[sniperStyles.middleRing, {
              transform: [{ scale: pulseAnim.interpolate({ inputRange: [1, 1.4], outputRange: [1, 1.1] }) }],
              opacity: pulseAnim.interpolate({ inputRange: [1, 1.4], outputRange: [0.6, 1] })
            }]} />
            {/* Center icon */}
            <View style={sniperStyles.centerIcon}>
              <Ionicons name="scan" size={36} color="#F5D061" />
            </View>
            {/* Floating dot top-right */}
            <Animated.View style={[sniperStyles.floatDot, sniperStyles.floatDot1, {
              transform: [{ translateY: glowAnim.interpolate({ inputRange: [0, 1], outputRange: [0, -6] }) }]
            }]} />
            {/* Floating dot bottom-left */}
            <Animated.View style={[sniperStyles.floatDot, sniperStyles.floatDot2, {
              transform: [{ translateY: glowAnim.interpolate({ inputRange: [0, 1], outputRange: [0, 6] }) }]
            }]} />
            {/* Gold glow */}
            <View style={sniperStyles.bulletGlow} />
          </View>

          {/* Corner accent */}
          <View style={sniperStyles.cornerAccent} />
        </View>
      </Animated.View>
    </TouchableOpacity>
  );
}

import { StyleSheet } from 'react-native';

const sniperStyles = StyleSheet.create({
  card: {
    borderRadius: 24,
    overflow: 'hidden',
    minHeight: 200,
    borderWidth: 1,
    borderColor: 'rgba(245,208,97,0.25)',
    shadowColor: '#F5D061',
    shadowOffset: { width: 0, height: 16 },
    shadowOpacity: 0.3,
    shadowRadius: 32,
    elevation: 16,
    flexDirection: 'row',
    alignItems: 'center',
    paddingLeft: 24,
    paddingVertical: 24,
    position: 'relative',
    marginBottom: 4,
  },
  scopeOverlay: {
    position: 'absolute',
    right: 30,
    top: -30,
    width: 220,
    height: 220,
    opacity: 0.06,
    justifyContent: 'center',
    alignItems: 'center',
  },
  scopeRingOuter: {
    width: 200,
    height: 200,
    borderRadius: 100,
    borderWidth: 2,
    borderColor: '#F5D061',
    justifyContent: 'center',
    alignItems: 'center',
  },
  scopeRingInner: {
    width: 140,
    height: 140,
    borderRadius: 70,
    borderWidth: 1,
    borderColor: '#F5D061',
    justifyContent: 'center',
    alignItems: 'center',
    position: 'relative',
  },
  scopeCrosshairH: {
    position: 'absolute',
    width: 140,
    height: 1,
    backgroundColor: '#F5D061',
  },
  scopeCrosshairV: {
    position: 'absolute',
    width: 1,
    height: 140,
    backgroundColor: '#F5D061',
  },
  leftCol: {
    flex: 1,
    zIndex: 2,
  },
  badge: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    backgroundColor: 'rgba(245,208,97,0.12)',
    borderRadius: 100,
    paddingHorizontal: 10,
    paddingVertical: 4,
    alignSelf: 'flex-start',
    borderWidth: 1,
    borderColor: 'rgba(245,208,97,0.3)',
    marginBottom: 12,
  },
  pulseDot: {
    width: 6,
    height: 6,
    borderRadius: 3,
    backgroundColor: '#F5D061',
  },
  badgeText: {
    color: '#F5D061',
    fontSize: 9,
    fontWeight: '800',
    letterSpacing: 1.5,
  },
  title: {
    fontSize: 36,
    fontWeight: '900',
    color: '#FFFFFF',
    lineHeight: 38,
    letterSpacing: -0.5,
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 12,
    color: 'rgba(255,255,255,0.45)',
    lineHeight: 18,
    marginBottom: 16,
  },
  statsRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 20,
    gap: 12,
  },
  stat: {
    alignItems: 'center',
  },
  statValue: {
    fontSize: 18,
    fontWeight: '800',
    color: '#F5D061',
  },
  statLabel: {
    fontSize: 9,
    color: 'rgba(255,255,255,0.4)',
    letterSpacing: 0.5,
    textTransform: 'uppercase',
  },
  statDivider: {
    width: 1,
    height: 28,
    backgroundColor: 'rgba(255,255,255,0.1)',
  },
  cta: {
    alignSelf: 'flex-start',
    borderRadius: 100,
    overflow: 'hidden',
  },
  ctaGrad: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    paddingHorizontal: 18,
    paddingVertical: 10,
  },
  ctaText: {
    color: '#0D1117',
    fontWeight: '800',
    fontSize: 13,
    letterSpacing: 0.3,
  },
  bulletWrapper: {
    width: 120,
    height: 120,
    position: 'absolute',
    right: 16,
    top: '50%',
    marginTop: -60,
    zIndex: 3,
    alignItems: 'center',
    justifyContent: 'center',
  },
  rotatingRing: {
    position: 'absolute',
    width: 110,
    height: 110,
    borderRadius: 55,
    borderWidth: 1.5,
    borderColor: 'rgba(245,208,97,0.4)',
    borderStyle: 'dashed',
  },
  middleRing: {
    position: 'absolute',
    width: 80,
    height: 80,
    borderRadius: 40,
    borderWidth: 2,
    borderColor: 'rgba(245,208,97,0.6)',
  },
  centerIcon: {
    width: 56,
    height: 56,
    borderRadius: 28,
    backgroundColor: 'rgba(245,208,97,0.15)',
    borderWidth: 1,
    borderColor: 'rgba(245,208,97,0.4)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  floatDot: {
    position: 'absolute',
    width: 7,
    height: 7,
    borderRadius: 3.5,
    backgroundColor: '#F5D061',
  },
  floatDot1: {
    top: 8,
    right: 8,
    opacity: 0.8,
  },
  floatDot2: {
    bottom: 8,
    left: 8,
    opacity: 0.5,
  },
  bulletGlow: {
    position: 'absolute',
    bottom: 10,
    width: 80,
    height: 30,
    backgroundColor: '#F5D061',
    borderRadius: 40,
    opacity: 0.15,
    shadowColor: '#F5D061',
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: 1,
    shadowRadius: 20,
  },
  cornerAccent: {
    position: 'absolute',
    top: 16,
    right: 16,
    width: 8,
    height: 8,
    borderTopWidth: 2,
    borderRightWidth: 2,
    borderColor: 'rgba(245,208,97,0.5)',
  },
});
