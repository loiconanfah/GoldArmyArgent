/**
 * Splash Onboarding
 * Page d'accueil premium avec deux carrousels
 * 100% compatible Expo Go - utilise l'API Animated native de React Native
 */

import React, { useRef, useEffect, useState, useCallback, useMemo } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  FlatList,
  Dimensions,
  TouchableOpacity,
  Animated,
  Platform,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { BlurView } from 'expo-blur';
import { Image } from 'expo-image';
import * as Haptics from 'expo-haptics';
import { Ionicons } from '@expo/vector-icons';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

// Theme
const C = {
  primary: '#FF6B35',
  primarySoft: '#FF8C5A',
  primaryPale: '#FFF0EB',
  accent: '#FF3D00',
  bg: '#FAFAF8',
  surface: '#FFFFFF',
  surfaceAlt: '#F5F4F0',
  border: '#EBEBE7',
  text: '#1A1A18',
  textMid: '#4A4A46',
  textMuted: '#9A9A94',
  white: '#FFFFFF',
  shadow: 'rgba(255,107,53,0.18)',
  shadowNeutral: 'rgba(0,0,0,0.06)',
};

const SP = { xs: 4, sm: 8, md: 12, lg: 16, xl: 24, xxl: 32, xxxl: 48 };
const R = { sm: 8, md: 14, lg: 20, xl: 28, full: 999 };

const SHADOWS = {
  card: {
    shadowColor: C.shadowNeutral,
    shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 1,
    shadowRadius: 16,
    elevation: 4,
  },
  glow: {
    shadowColor: C.shadow,
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 1,
    shadowRadius: 20,
    elevation: 8,
  },
};

const SCREEN_WIDTH = Dimensions.get('window').width;

// Data
const PARTNERS = [
  { id: '1', name: 'Stripe', color: '#635BFF' },
  { id: '2', name: 'Supabase', color: '#3ECF8E' },
  { id: '3', name: 'Vercel', color: '#000' },
  { id: '4', name: 'Render', color: '#46E3B7' },
  { id: '5', name: 'Expo', color: '#000020' },
  { id: '6', name: 'Firebase', color: '#FFCA28' },
  { id: '7', name: 'AWS', color: '#FF9900' },
  { id: '8', name: 'GitHub', color: '#181717' },
];

const FEATURES = [
  {
    id: '1',
    emoji: '⚡',
    title: 'Ultra Rapide',
    description: 'Performances natives optimisées pour une expérience fluide.',
  },
  {
    id: '2',
    emoji: '🔒',
    title: 'Sécurisé',
    description: 'Chiffrement end-to-end et auth biométrique intégrée.',
  },
  {
    id: '3',
    emoji: '🌍',
    title: 'Multi-plateforme',
    description: 'iOS, Android et Web depuis une seule base de code Expo.',
  },
  {
    id: '4',
    emoji: '📊',
    title: 'Analytics live',
    description: 'Tableaux de bord temps réel pour chaque métrique clé.',
  },
  {
    id: '5',
    emoji: '🤖',
    title: 'IA intégrée',
    description: 'Suggestions intelligentes propulsées par intelligence artificielle.',
  },
  {
    id: '6',
    emoji: '🎨',
    title: 'Personnalisable',
    description: 'Thèmes et composants entièrement adaptables à ta marque.',
  },
];

export default function SplashOnboarding() {
  const insets = useSafeAreaInsets();
  const scrollViewRef = useRef<ScrollView>(null);
  const scrollY = useRef(new Animated.Value(0)).current;
  const [navbarBlur, setNavbarBlur] = useState(0);
  const [showNavbarButton, setShowNavbarButton] = useState(false);
  const [activeFeatureIndex, setActiveFeatureIndex] = useState(0);
  const partnersListRef = useRef<FlatList>(null);
  const featuresListRef = useRef<FlatList>(null);
  const autoScrollTimer = useRef<NodeJS.Timeout | null>(null);
  const isDragging = useRef(false);
  const partnersScrollOffset = useRef(0);

  // Navbar blur animation
  useEffect(() => {
    let listenerId: string | number | undefined;
    
    // Utiliser addListener si disponible, sinon utiliser une approche alternative
    if (scrollY.addListener) {
      listenerId = scrollY.addListener(({ value }) => {
        const blurIntensity = Math.min((value / 60) * 20, 20);
        setNavbarBlur(blurIntensity);
        setShowNavbarButton(value > 150);
      });
    }

    return () => {
      if (listenerId !== undefined && scrollY.removeListener) {
        scrollY.removeListener(listenerId);
      }
    };
  }, []);

  // Auto-scroll partners carousel (infinite loop)
  useEffect(() => {
    const itemWidth = 120 + 12; // width + marginRight
    const scrollInterval = setInterval(() => {
      if (partnersListRef.current && !isDragging.current) {
        partnersScrollOffset.current += itemWidth;
        partnersListRef.current.scrollToOffset({
          offset: partnersScrollOffset.current,
          animated: true,
        });
        
        // Reset pour boucle infinie (après 2x la longueur des données)
        if (partnersScrollOffset.current >= PARTNERS.length * 2 * itemWidth) {
          partnersScrollOffset.current = PARTNERS.length * itemWidth;
          partnersListRef.current.scrollToOffset({
            offset: partnersScrollOffset.current,
            animated: false,
          });
        }
      }
    }, 2200);

    return () => clearInterval(scrollInterval);
  }, []);

  // Auto-scroll features carousel
  useEffect(() => {
    const scrollFeature = () => {
      if (!isDragging.current && featuresListRef.current) {
        const nextIndex = (activeFeatureIndex + 1) % FEATURES.length;
        setActiveFeatureIndex(nextIndex);
        featuresListRef.current.scrollToIndex({
          index: nextIndex,
          animated: true,
        });
      }
    };

    autoScrollTimer.current = setInterval(scrollFeature, 3500);

    return () => {
      if (autoScrollTimer.current) {
        clearInterval(autoScrollTimer.current);
      }
    };
  }, [activeFeatureIndex]);

  const handleHaptic = useCallback((type: 'light' | 'medium' | 'heavy' = 'medium') => {
    try {
      if (type === 'heavy') {
        Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Heavy);
      } else if (type === 'medium') {
        Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
      } else {
        Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
      }
    } catch (error) {
      // Silent fail
    }
  }, []);

  const handleDownload = useCallback(() => {
    handleHaptic('light');
    // Navigate to download or open app store
  }, [handleHaptic]);

  // Duplicate partners for infinite scroll
  const duplicatedPartners = useMemo(() => [...PARTNERS, ...PARTNERS, ...PARTNERS], []);

  return (
    <View style={styles.container}>
      {/* Navbar */}
      <Navbar
        blurIntensity={navbarBlur}
        showButton={showNavbarButton}
        onDownload={handleDownload}
        insets={insets}
      />

      <Animated.ScrollView
        ref={scrollViewRef}
        scrollEventThrottle={16}
        onScroll={Animated.event(
          [{ nativeEvent: { contentOffset: { y: scrollY } } }],
          { useNativeDriver: false }
        )}
        showsVerticalScrollIndicator={false}
        style={styles.scrollView}
      >
        {/* Hero Section */}
        <HeroSection onDownload={handleDownload} />

        {/* Stats Band */}
        <StatsBand />

        {/* Partners Carousel */}
        <PartnersCarousel
          ref={partnersListRef}
          data={duplicatedPartners}
          onDragStart={() => (isDragging.current = true)}
          onDragEnd={() => (isDragging.current = false)}
        />

        {/* Features Carousel */}
        <FeaturesCarousel
          ref={featuresListRef}
          data={FEATURES}
          activeIndex={activeFeatureIndex}
          onIndexChange={setActiveFeatureIndex}
          onDragStart={() => {
            isDragging.current = true;
            if (autoScrollTimer.current) {
              clearInterval(autoScrollTimer.current);
            }
          }}
          onDragEnd={() => {
            isDragging.current = false;
            autoScrollTimer.current = setInterval(() => {
              const nextIndex = (activeFeatureIndex + 1) % FEATURES.length;
              setActiveFeatureIndex(nextIndex);
              featuresListRef.current?.scrollToIndex({
                index: nextIndex,
                animated: true,
              });
            }, 3500);
          }}
        />

        {/* Testimonial */}
        <Testimonial />

        {/* CTA Final */}
        <CTAFinal onDownload={handleDownload} />

        {/* Footer */}
        <Footer />
      </Animated.ScrollView>
    </View>
  );
}

// Navbar Component
function Navbar({
  blurIntensity,
  showButton,
  onDownload,
  insets,
}: {
  blurIntensity: number;
  showButton: boolean;
  onDownload: () => void;
  insets: { top: number };
}) {
  const buttonOpacity = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    Animated.spring(buttonOpacity, {
      toValue: showButton ? 1 : 0,
      useNativeDriver: true,
    }).start();
  }, [showButton]);

  return (
    <View style={[styles.navbar, { paddingTop: insets.top + SP.md }]}>
      {blurIntensity > 0 && (
        <BlurView intensity={blurIntensity} tint="light" style={StyleSheet.absoluteFill} />
      )}
      <View style={styles.navbarContent}>
        <View style={styles.logoContainer}>
          <View style={styles.logoCircle} />
          <Text style={styles.logoText}>GoldArmy</Text>
        </View>
        <Animated.View style={{ opacity: buttonOpacity }}>
          <TouchableOpacity onPress={onDownload} style={styles.navbarButton}>
            <Text style={styles.navbarButtonText}>Télécharger</Text>
          </TouchableOpacity>
        </Animated.View>
      </View>
    </View>
  );
}

// Hero Section
function HeroSection({ onDownload }: { onDownload: () => void }) {
  const badgeScale = useRef(new Animated.Value(1)).current;
  const fadeAnim = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    // Badge pulse animation
    const pulse = Animated.loop(
      Animated.sequence([
        Animated.timing(badgeScale, {
          toValue: 1.06,
          duration: 1000,
          useNativeDriver: true,
        }),
        Animated.timing(badgeScale, {
          toValue: 1,
          duration: 1000,
          useNativeDriver: true,
        }),
      ])
    );
    pulse.start();

    // Fade in animation
    Animated.timing(fadeAnim, {
      toValue: 1,
      duration: 600,
      useNativeDriver: true,
    }).start();

    return () => pulse.stop();
  }, []);

  return (
    <View style={styles.hero}>
      <Image
        source={{ uri: 'https://images.unsplash.com/photo-1551650975-87deedd944c3?w=900&q=80' }}
        placeholder={{ blurhash: 'L6PZfSi_.AyE_3t7t7R**0o#DgR4' }}
        contentFit="cover"
        transition={500}
        style={StyleSheet.absoluteFill}
      />
      <LinearGradient
        colors={['transparent', 'rgba(250,250,248,0.95)']}
        style={StyleSheet.absoluteFill}
      />
      <View style={styles.heroContent}>
        <Animated.View style={{ transform: [{ scale: badgeScale }], opacity: fadeAnim }}>
          <View style={styles.badge}>
            <View style={styles.badgeDot} />
            <Text style={styles.badgeText}>Nouveau</Text>
          </View>
        </Animated.View>

        <Animated.View style={{ opacity: fadeAnim }}>
          <Text style={styles.heroTitle}>
            L'intelligence artificielle{'\n'}pour{' '}
            <Text style={styles.heroTitleAccent}>l'élite</Text>
          </Text>
          <Text style={styles.heroSubtitle}>
            Rejoignez des milliers de professionnels qui transforment leur workflow avec notre
            plateforme IA de nouvelle génération.
          </Text>
        </Animated.View>

        <Animated.View style={[styles.heroButtons, { opacity: fadeAnim }]}>
          <TouchableOpacity
            onPress={() => {
              try {
                Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
              } catch {}
              onDownload();
            }}
            style={styles.heroButtonPrimary}
            activeOpacity={0.8}
          >
            <LinearGradient
              colors={[C.primary, C.accent]}
              start={{ x: 0, y: 0 }}
              end={{ x: 1, y: 1 }}
              style={styles.heroButtonGradient}
            >
              <Text style={styles.heroButtonPrimaryText}>Commencer gratuitement</Text>
            </LinearGradient>
          </TouchableOpacity>
          <TouchableOpacity
            onPress={onDownload}
            style={styles.heroButtonSecondary}
            activeOpacity={0.8}
          >
            <Text style={styles.heroButtonSecondaryText}>En savoir plus</Text>
          </TouchableOpacity>
        </Animated.View>
      </View>
    </View>
  );
}

// Stats Band
function StatsBand() {
  const [isVisible, setIsVisible] = useState(false);
  const opacity = useRef(new Animated.Value(0)).current;
  const translateY = useRef(new Animated.Value(30)).current;

  useEffect(() => {
    // Trigger when component mounts (simulate scroll trigger)
    setTimeout(() => {
      setIsVisible(true);
      Animated.parallel([
        Animated.timing(opacity, {
          toValue: 1,
          duration: 600,
          useNativeDriver: true,
        }),
        Animated.timing(translateY, {
          toValue: 0,
          duration: 600,
          useNativeDriver: true,
        }),
      ]).start();
    }, 500);
  }, []);

  const stats = [
    { value: '10K+', label: 'Utilisateurs' },
    { value: '99.9%', label: 'Uptime' },
    { value: '24/7', label: 'Support' },
  ];

  return (
    <Animated.View
      style={[
        styles.statsBand,
        {
          opacity,
          transform: [{ translateY }],
        },
      ]}
    >
      <BlurView intensity={30} tint="light" style={styles.statsBlur}>
        {stats.map((stat, index) => (
          <React.Fragment key={stat.label}>
            <View style={styles.statItem}>
              <Text style={styles.statValue}>{stat.value}</Text>
              <Text style={styles.statLabel}>{stat.label}</Text>
            </View>
            {index < stats.length - 1 && <View style={styles.statDivider} />}
          </React.Fragment>
        ))}
      </BlurView>
    </Animated.View>
  );
}

// Partners Carousel
const PartnersCarousel = React.forwardRef<
  FlatList,
  {
    data: typeof PARTNERS;
    onDragStart: () => void;
    onDragEnd: () => void;
  }
>(({ data, onDragStart, onDragEnd }, ref) => {
  const renderItem = useCallback(
    ({ item }: { item: typeof PARTNERS[0] }) => (
      <View style={styles.partnerCard}>
        <View style={[styles.partnerCircle, { backgroundColor: item.color }]} />
        <Text style={styles.partnerName}>{item.name}</Text>
      </View>
    ),
    []
  );

  const getItemLayout = useCallback(
    (_: any, index: number) => ({
      length: 120 + 12,
      offset: (120 + 12) * index,
      index,
    }),
    []
  );

  return (
    <View style={styles.partnersSection}>
      <Text style={styles.sectionTitle}>Ils nous font confiance</Text>
      <FlatList
        ref={ref}
        data={data}
        renderItem={renderItem}
        keyExtractor={(item, index) => `${item.id}-${index}`}
        horizontal
        showsHorizontalScrollIndicator={false}
        contentContainerStyle={styles.partnersList}
        getItemLayout={getItemLayout}
        scrollEnabled={true}
        onScrollBeginDrag={onDragStart}
        onScrollEndDrag={onDragEnd}
      />
    </View>
  );
});

// Features Carousel
const FeaturesCarousel = React.forwardRef<
  FlatList,
  {
    data: typeof FEATURES;
    activeIndex: number;
    onIndexChange: (index: number) => void;
    onDragStart: () => void;
    onDragEnd: () => void;
  }
>(({ data, activeIndex, onIndexChange, onDragStart, onDragEnd }, ref) => {
  const renderItem = useCallback(
    ({ item }: { item: typeof FEATURES[0] }) => (
      <View style={styles.featureCard}>
        <View style={styles.featureIconContainer}>
          <Text style={styles.featureEmoji}>{item.emoji}</Text>
        </View>
        <Text style={styles.featureTitle}>{item.title}</Text>
        <Text style={styles.featureDescription}>{item.description}</Text>
        <TouchableOpacity style={styles.featureLink}>
          <Text style={styles.featureLinkText}>En savoir plus →</Text>
        </TouchableOpacity>
      </View>
    ),
    []
  );

  const getItemLayout = useCallback(
    (_: any, index: number) => ({
      length: SCREEN_WIDTH - 32,
      offset: (SCREEN_WIDTH - 32) * index,
      index,
    }),
    []
  );

  const onViewableItemsChanged = useRef(
    ({ viewableItems }: { viewableItems: any[] }) => {
      if (viewableItems.length > 0) {
        onIndexChange(viewableItems[0].index || 0);
      }
    }
  ).current;

  const viewabilityConfig = useRef({
    itemVisiblePercentThreshold: 50,
  }).current;

  return (
    <View style={styles.featuresSection}>
      <Text style={styles.sectionTitle}>Fonctionnalités</Text>
      <FlatList
        ref={ref}
        data={data}
        renderItem={renderItem}
        keyExtractor={(item) => item.id}
        horizontal
        pagingEnabled
        snapToInterval={SCREEN_WIDTH - 32}
        snapToAlignment="start"
        decelerationRate="fast"
        showsHorizontalScrollIndicator={false}
        contentContainerStyle={styles.featuresList}
        getItemLayout={getItemLayout}
        onScrollBeginDrag={onDragStart}
        onScrollEndDrag={onDragEnd}
        onViewableItemsChanged={onViewableItemsChanged}
        viewabilityConfig={viewabilityConfig}
        onScrollToIndexFailed={(info) => {
          const wait = new Promise((resolve) => setTimeout(resolve, 500));
          wait.then(() => {
            ref.current?.scrollToIndex({ index: info.index, animated: false });
          });
        }}
      />
      <View style={styles.dotsContainer}>
        {data.map((_, index) => (
          <Dot key={index} active={index === activeIndex} />
        ))}
      </View>
    </View>
  );
});

// Dot Indicator
function Dot({ active }: { active: boolean }) {
  const width = useRef(new Animated.Value(6)).current;

  useEffect(() => {
    Animated.spring(width, {
      toValue: active ? 20 : 6,
      useNativeDriver: false,
    }).start();
  }, [active]);

  return (
    <Animated.View
      style={[
        styles.dot,
        {
          width,
          opacity: active ? 1 : 0.4,
          backgroundColor: active ? C.primary : C.textMuted,
        },
      ]}
    />
  );
}

// Testimonial
function Testimonial() {
  return (
    <View style={styles.testimonial}>
      <View style={styles.testimonialCard}>
        <Text style={styles.testimonialQuote}>
          "Cette plateforme a complètement transformé notre façon de travailler. L'IA est
          incroyablement puissante et intuitive."
        </Text>
        <View style={styles.testimonialAuthor}>
          <View style={styles.testimonialAvatar}>
            <Text style={styles.testimonialInitials}>JD</Text>
          </View>
          <View>
            <Text style={styles.testimonialName}>Jean Dupont</Text>
            <Text style={styles.testimonialRole}>CEO, TechStart</Text>
            <Text style={styles.testimonialStars}>★★★★★</Text>
          </View>
        </View>
      </View>
    </View>
  );
}

// CTA Final
function CTAFinal({ onDownload }: { onDownload: () => void }) {
  return (
    <View style={styles.ctaFinal}>
      <View style={styles.ctaGlow} />
      <Text style={styles.ctaEyebrow}>PRÊT À COMMENCER ?</Text>
      <Text style={styles.ctaTitle}>
        Rejoignez l'élite de{'\n'}l'intelligence artificielle
      </Text>
      <Text style={styles.ctaSubtitle}>
        Démarrez votre essai gratuit aujourd'hui. Aucune carte bancaire requise.
      </Text>
      <TouchableOpacity
        onPress={() => {
          try {
            Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Heavy);
          } catch {}
          onDownload();
        }}
        style={styles.ctaButton}
        activeOpacity={0.8}
      >
        <LinearGradient
          colors={[C.primary, C.accent]}
          start={{ x: 0, y: 0 }}
          end={{ x: 1, y: 1 }}
          style={styles.ctaButtonGradient}
        >
          <Text style={styles.ctaButtonText}>Commencer maintenant</Text>
        </LinearGradient>
      </TouchableOpacity>
      <Text style={styles.ctaNote}>Aucune carte requise · Gratuit 14 jours</Text>
    </View>
  );
}

// Footer
function Footer() {
  return (
    <View style={styles.footer}>
      <View style={styles.footerLogo}>
        <View style={styles.footerLogoCircle} />
        <Text style={styles.footerLogoText}>GoldArmy</Text>
      </View>
      <Text style={styles.footerCopyright}>© 2024 GoldArmy. Tous droits réservés.</Text>
      <View style={styles.footerLinks}>
        <Text style={styles.footerLink}>Confidentialité</Text>
        <Text style={styles.footerLink}>·</Text>
        <Text style={styles.footerLink}>CGU</Text>
        <Text style={styles.footerLink}>·</Text>
        <Text style={styles.footerLink}>Contact</Text>
      </View>
    </View>
  );
}

// Styles
const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: C.bg,
  },
  scrollView: {
    flex: 1,
  },
  navbar: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    zIndex: 100,
    borderBottomWidth: 1,
    borderBottomColor: C.border,
  },
  navbarContent: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: SP.xl,
    paddingBottom: SP.md,
  },
  logoContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  logoCircle: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: C.primary,
    marginRight: SP.sm,
  },
  logoText: {
    fontSize: 18,
    fontWeight: '700',
    color: C.text,
  },
  navbarButton: {
    backgroundColor: C.text,
    paddingHorizontal: SP.lg,
    paddingVertical: SP.sm,
    borderRadius: R.full,
  },
  navbarButtonText: {
    color: C.white,
    fontSize: 14,
    fontWeight: '600',
  },
  hero: {
    height: 600,
    position: 'relative',
  },
  heroContent: {
    flex: 1,
    justifyContent: 'flex-end',
    padding: SP.xl,
    paddingBottom: SP.xxxl,
  },
  badge: {
    flexDirection: 'row',
    alignItems: 'center',
    alignSelf: 'flex-start',
    backgroundColor: C.primaryPale,
    paddingHorizontal: SP.md,
    paddingVertical: SP.xs,
    borderRadius: R.full,
    marginBottom: SP.lg,
  },
  badgeDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: C.primary,
    marginRight: SP.xs,
  },
  badgeText: {
    fontSize: 12,
    fontWeight: '600',
    color: C.accent,
  },
  heroTitle: {
    fontSize: 42,
    fontWeight: '900',
    color: C.text,
    lineHeight: 50,
    marginBottom: SP.md,
  },
  heroTitleAccent: {
    color: C.primary,
  },
  heroSubtitle: {
    fontSize: 16,
    color: C.textMid,
    lineHeight: 26,
    marginBottom: SP.xxl,
  },
  heroButtons: {
    flexDirection: 'row',
    gap: SP.md,
  },
  heroButtonPrimary: {
    flex: 1,
    borderRadius: R.full,
    overflow: 'hidden',
    ...SHADOWS.glow,
  },
  heroButtonGradient: {
    paddingVertical: SP.lg,
    alignItems: 'center',
    justifyContent: 'center',
  },
  heroButtonPrimaryText: {
    color: C.white,
    fontSize: 16,
    fontWeight: '700',
  },
  heroButtonSecondary: {
    flex: 1,
    borderWidth: 2,
    borderColor: C.primary,
    borderRadius: R.full,
    paddingVertical: SP.lg,
    alignItems: 'center',
    justifyContent: 'center',
  },
  heroButtonSecondaryText: {
    color: C.primary,
    fontSize: 16,
    fontWeight: '600',
  },
  statsBand: {
    marginHorizontal: SP.xl,
    marginTop: -SP.xxl,
    marginBottom: SP.xxl,
    borderRadius: R.lg,
    overflow: 'hidden',
    ...SHADOWS.card,
  },
  statsBlur: {
    flexDirection: 'row',
    paddingVertical: SP.xl,
    paddingHorizontal: SP.lg,
  },
  statItem: {
    flex: 1,
    alignItems: 'center',
  },
  statValue: {
    fontSize: 28,
    fontWeight: '700',
    color: C.primary,
    marginBottom: SP.xs,
  },
  statLabel: {
    fontSize: 11,
    color: C.textMuted,
  },
  statDivider: {
    width: 1,
    backgroundColor: C.border,
    marginHorizontal: SP.md,
  },
  partnersSection: {
    marginBottom: SP.xxxl,
  },
  sectionTitle: {
    fontSize: 24,
    fontWeight: '700',
    color: C.text,
    marginBottom: SP.lg,
    paddingHorizontal: SP.xl,
  },
  partnersList: {
    paddingHorizontal: SP.xl,
  },
  partnerCard: {
    width: 120,
    marginRight: SP.md,
    backgroundColor: C.surface,
    borderRadius: R.md,
    borderWidth: 1,
    borderColor: C.border,
    padding: SP.lg,
    alignItems: 'center',
    ...SHADOWS.card,
  },
  partnerCircle: {
    width: 28,
    height: 28,
    borderRadius: 14,
    marginBottom: SP.sm,
  },
  partnerName: {
    fontSize: 13,
    fontWeight: '600',
    color: C.text,
  },
  featuresSection: {
    marginBottom: SP.xxxl,
  },
  featuresList: {
    paddingHorizontal: SP.xl,
  },
  featureCard: {
    width: SCREEN_WIDTH - 32,
    backgroundColor: C.surface,
    borderRadius: R.lg,
    padding: SP.xxl,
    marginRight: SP.xl,
    ...SHADOWS.card,
  },
  featureIconContainer: {
    width: 48,
    height: 48,
    borderRadius: R.md,
    backgroundColor: C.primaryPale,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: SP.lg,
  },
  featureEmoji: {
    fontSize: 24,
  },
  featureTitle: {
    fontSize: 18,
    fontWeight: '700',
    color: C.text,
    marginBottom: SP.sm,
  },
  featureDescription: {
    fontSize: 14,
    color: C.textMid,
    lineHeight: 22,
    marginBottom: SP.lg,
  },
  featureLink: {
    alignSelf: 'flex-start',
  },
  featureLinkText: {
    fontSize: 14,
    fontWeight: '600',
    color: C.primary,
  },
  dotsContainer: {
    flexDirection: 'row',
    justifyContent: 'center',
    marginTop: SP.lg,
    gap: SP.xs,
  },
  dot: {
    height: 6,
    borderRadius: 3,
  },
  testimonial: {
    paddingHorizontal: SP.xl,
    marginBottom: SP.xxxl,
  },
  testimonialCard: {
    backgroundColor: C.primaryPale,
    borderRadius: R.lg,
    padding: SP.xxl,
    borderLeftWidth: 3,
    borderLeftColor: C.primary,
  },
  testimonialQuote: {
    fontSize: 15,
    fontStyle: 'italic',
    color: C.text,
    lineHeight: 24,
    marginBottom: SP.lg,
  },
  testimonialAuthor: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  testimonialAvatar: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: C.primary,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: SP.md,
  },
  testimonialInitials: {
    color: C.white,
    fontSize: 18,
    fontWeight: '700',
  },
  testimonialName: {
    fontSize: 16,
    fontWeight: '600',
    color: C.text,
    marginBottom: SP.xs,
  },
  testimonialRole: {
    fontSize: 13,
    color: C.textMuted,
    marginBottom: SP.xs,
  },
  testimonialStars: {
    fontSize: 14,
    color: C.primary,
  },
  ctaFinal: {
    backgroundColor: '#1A1A18',
    marginHorizontal: SP.xl,
    marginBottom: SP.xxxl,
    borderRadius: R.xl,
    padding: SP.xxxl,
    alignItems: 'center',
    position: 'relative',
    overflow: 'hidden',
  },
  ctaGlow: {
    position: 'absolute',
    width: 200,
    height: 200,
    borderRadius: 100,
    backgroundColor: C.primary,
    opacity: 0.2,
    top: -100,
    right: -100,
  },
  ctaEyebrow: {
    fontSize: 12,
    fontWeight: '700',
    color: C.primary,
    textTransform: 'uppercase',
    letterSpacing: 1,
    marginBottom: SP.md,
  },
  ctaTitle: {
    fontSize: 30,
    fontWeight: '700',
    color: C.white,
    textAlign: 'center',
    marginBottom: SP.md,
    lineHeight: 38,
  },
  ctaSubtitle: {
    fontSize: 16,
    color: 'rgba(255,255,255,0.6)',
    textAlign: 'center',
    marginBottom: SP.xxl,
    lineHeight: 24,
  },
  ctaButton: {
    width: '100%',
    borderRadius: R.full,
    overflow: 'hidden',
    marginBottom: SP.md,
    ...SHADOWS.glow,
  },
  ctaButtonGradient: {
    paddingVertical: SP.lg,
    alignItems: 'center',
    justifyContent: 'center',
  },
  ctaButtonText: {
    color: C.white,
    fontSize: 18,
    fontWeight: '700',
  },
  ctaNote: {
    fontSize: 13,
    color: 'rgba(255,255,255,0.4)',
  },
  footer: {
    paddingHorizontal: SP.xl,
    paddingVertical: SP.xxl,
    alignItems: 'center',
    borderTopWidth: 1,
    borderTopColor: C.border,
  },
  footerLogo: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: SP.md,
  },
  footerLogoCircle: {
    width: 24,
    height: 24,
    borderRadius: 12,
    backgroundColor: C.primary,
    marginRight: SP.sm,
  },
  footerLogoText: {
    fontSize: 16,
    fontWeight: '700',
    color: C.text,
  },
  footerCopyright: {
    fontSize: 12,
    color: C.textMuted,
    marginBottom: SP.sm,
  },
  footerLinks: {
    flexDirection: 'row',
    gap: SP.sm,
  },
  footerLink: {
    fontSize: 12,
    color: C.textMuted,
  },
});
