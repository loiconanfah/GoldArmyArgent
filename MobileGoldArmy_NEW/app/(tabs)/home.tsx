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
