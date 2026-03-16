/**
 * Onboarding Screen
 * First-launch onboarding with 4 slides
 */

import * as React from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  Dimensions,
  type NativeScrollEvent,
  type NativeSyntheticEvent,
  type ListRenderItemInfo,
} from 'react-native';
import { useRouter } from 'expo-router';
import * as SecureStore from 'expo-secure-store';
import * as Haptics from 'expo-haptics';
import { OnboardingSlide } from '../src/components/onboarding/OnboardingSlide';
import { OnboardingDots } from '../src/components/onboarding/OnboardingDots';
import { Slide1Illustration } from '../src/components/onboarding/slides/Slide1Illustration';
import { Slide2Illustration } from '../src/components/onboarding/slides/Slide2Illustration';
import { Slide3Illustration } from '../src/components/onboarding/slides/Slide3Illustration';
import { Slide4Illustration } from '../src/components/onboarding/slides/Slide4Illustration';
import type { SlideData } from '../src/types/onboarding.types';

const { width: SCREEN_WIDTH, height: SCREEN_HEIGHT } = Dimensions.get('window');

// Couleurs alignées sur le thème global de l'app (voir src/theme/colors.ts)
const C = {
  primary: '#F5D061', // gold / couleur principale du logo
  primarySoft: '#F8DC8A',
  primaryPale: '#FFF8DC',
  primaryDeep: '#E6A32F',
  accent: '#3B82F6', // bleu secondaire de l'app
  bg: '#FFFFFF',
  surface: '#FFFFFF',
  surfaceAlt: '#F5F5F5',
  border: '#E0E0E0',
  text: '#1A1A1A',
  textMid: '#666666',
  textMuted: '#999999',
  white: '#FFFFFF',
  shadow: 'rgba(0,0,0,0.10)',
  shadowNeutral: 'rgba(0,0,0,0.07)',
};

// Helper function to create highlight content
const createHighlightContent = (type: 'confidence' | 'applications') => {
  if (type === 'confidence') {
    return (
      <View style={{ alignItems: 'center' }}>
        <Text style={{ fontSize: 18, fontWeight: '700', color: C.text, marginBottom: 8 }}>
          Confiance : 94%
        </Text>
        <View
          style={{
            width: '100%',
            height: 8,
            backgroundColor: C.primaryPale,
            borderRadius: 4,
            overflow: 'hidden',
          }}
        >
          <View
            style={{
              width: '94%',
              height: '100%',
              backgroundColor: C.primary,
              borderRadius: 4,
            }}
          />
        </View>
      </View>
    );
  } else {
    return (
      <View style={{ alignItems: 'center' }}>
        <Text style={{ fontSize: 18, fontWeight: '700', color: C.text, marginBottom: 8 }}>
          12 candidatures actives
        </Text>
        <Text style={{ fontSize: 13, color: C.textMid }}>3 en entretien • 2 offres reçues</Text>
      </View>
    );
  }
};

// Slides data
const SLIDES: SlideData[] = [
  {
    id: '1',
    badge: 'Recherche intelligente',
    icon: 'search-outline',
    title: 'Trouve ton\nprochain emploi',
    subtitle:
      'Des milliers d\'offres analysées et filtrées selon ton profil, tes compétences et tes ambitions.',
    illustration: <Slide1Illustration colors={{ primary: C.primary, primaryPale: C.primaryPale }} />,
  },
  {
    id: '2',
    badge: 'IA Coach Personnel',
    icon: 'chatbubbles-outline',
    title: 'Prépare chaque\nentretien',
    subtitle:
      'Simule des entretiens réels avec notre IA. Reçois un feedback instantané sur tes réponses et ta posture.',
    illustration: (
      <Slide2Illustration
        colors={{ primary: C.primary, primaryPale: C.primaryPale, surface: C.surface }}
      />
    ),
    hasHighlight: true,
    highlightContent: createHighlightContent('confidence'),
  },
  {
    id: '3',
    badge: 'Suivi Automatisé',
    icon: 'clipboard-outline',
    title: 'Tes candidatures,\ntout en ordre',
    subtitle:
      'Suis chaque candidature en temps réel. Relances automatiques, rappels et historique complet inclus.',
    illustration: (
      <Slide3Illustration
        colors={{
          primary: C.primary,
          primaryPale: C.primaryPale,
          surface: C.surface,
          text: C.text,
        }}
      />
    ),
    hasHighlight: true,
    highlightContent: createHighlightContent('applications'),
  },
  {
    id: '4',
    badge: 'Génération par IA',
    icon: 'mail-outline',
    title: 'Construis ton\nréseau LinkedIn',
    subtitle:
      'Messages de connexion personnalisés, mails de candidature percutants et profil LinkedIn optimisé générés par IA en quelques secondes.',
    illustration: (
      <Slide4Illustration
        colors={{ primary: C.primary, primaryPale: C.primaryPale, surface: C.surface }}
      />
    ),
  },
];

export default function OnboardingScreen() {
  const router = useRouter();
  const flatListRef = React.useRef<FlatList>(null);
  const [currentIndex, setCurrentIndex] = React.useState(0);
  const isScrolling = React.useRef(false);

  const handleNext = React.useCallback(async () => {
    if (currentIndex < SLIDES.length - 1) {
      const nextIndex = currentIndex + 1;
      flatListRef.current?.scrollToIndex({ index: nextIndex, animated: true });
      try {
        Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
      } catch (error) {
        // Silent fail
      }
    } else {
      // Last slide - complete onboarding
      try {
        Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
      } catch (error) {
        // Silent fail
      }
      await SecureStore.setItemAsync('onboarding_completed', 'true');
      router.replace('/(auth)/login');
    }
  }, [currentIndex, router]);

  const handleSkip = React.useCallback(async () => {
    try {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    } catch (error) {
      // Silent fail
    }
    await SecureStore.setItemAsync('onboarding_completed', 'true');
    router.replace('/(auth)/login');
  }, [router]);

  const handleScroll = React.useCallback((event: NativeSyntheticEvent<NativeScrollEvent>) => {
    if (isScrolling.current) {
      const offsetX = event.nativeEvent.contentOffset.x;
      const index = Math.round(offsetX / SCREEN_WIDTH);
      if (index !== currentIndex && index >= 0 && index < SLIDES.length) {
        setCurrentIndex(index);
      }
    }
  }, [currentIndex]);

  const handleMomentumScrollBegin = React.useCallback(() => {
    isScrolling.current = true;
  }, []);

  const handleMomentumScrollEnd = React.useCallback((event: NativeSyntheticEvent<NativeScrollEvent>) => {
    isScrolling.current = false;
    const offsetX = event.nativeEvent.contentOffset.x;
    const index = Math.round(offsetX / SCREEN_WIDTH);
    if (index >= 0 && index < SLIDES.length) {
      setCurrentIndex(index);
    }
  }, []);

  const getItemLayout = React.useCallback(
    (_: any, index: number) => ({
      length: SCREEN_WIDTH,
      offset: SCREEN_WIDTH * index,
      index,
    }),
    []
  );

  const renderItem = React.useCallback(
    ({ item, index }: ListRenderItemInfo<SlideData>) => (
      <OnboardingSlide
        slide={item}
        isActive={index === currentIndex}
        onNext={handleNext}
        onSkip={handleSkip}
        isLast={index === SLIDES.length - 1}
      />
    ),
    [currentIndex, handleNext, handleSkip]
  );

  return (
    <View style={styles.container}>
      <FlatList
        ref={flatListRef}
        data={SLIDES}
        renderItem={renderItem}
        keyExtractor={(item) => item.id}
        horizontal
        pagingEnabled
        snapToInterval={SCREEN_WIDTH}
        snapToAlignment="start"
        decelerationRate="fast"
        showsHorizontalScrollIndicator={false}
        scrollEventThrottle={16}
        onScroll={handleScroll}
        onMomentumScrollBegin={handleMomentumScrollBegin}
        onMomentumScrollEnd={handleMomentumScrollEnd}
        getItemLayout={getItemLayout}
        onScrollToIndexFailed={(info: { index: number }) => {
          const wait = new Promise((resolve) => setTimeout(resolve, 500));
          wait.then(() => {
            flatListRef.current?.scrollToIndex({ index: info.index, animated: false });
          });
        }}
      />
      {/* Dots indicator */}
      <View style={styles.dotsContainer}>
        <OnboardingDots total={SLIDES.length} activeIndex={currentIndex} colors={{ primary: C.primary, border: C.border }} />
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: C.bg,
  },
  dotsContainer: {
    position: 'absolute',
    bottom: 100,
    left: 0,
    right: 0,
    alignItems: 'center',
  },
});
