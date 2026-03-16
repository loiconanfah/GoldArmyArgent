/**
 * Onboarding Screen
 * First-launch onboarding with 4 slides
 */

import React, { useRef, useState, useCallback } from 'react';
import { View, Text, StyleSheet, FlatList, Dimensions, NativeScrollEvent, NativeSyntheticEvent } from 'react-native';
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

// Theme colors
const C = {
  primary: '#FF6B35',
  primarySoft: '#FF8C5A',
  primaryPale: '#FFF0EB',
  primaryDeep: '#E8521A',
  accent: '#FF3D00',
  bg: '#FAFAF8',
  surface: '#FFFFFF',
  surfaceAlt: '#F5F4F0',
  border: '#EAEAE6',
  text: '#1A1A18',
  textMid: '#4A4A46',
  textMuted: '#9A9A94',
  white: '#FFFFFF',
  shadow: 'rgba(255,107,53,0.20)',
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
    badge: '🔍 Recherche intelligente',
    title: 'Trouve ton\nprochain emploi',
    subtitle:
      'Des milliers d\'offres analysées et filtrées selon ton profil, tes compétences et tes ambitions.',
    illustration: <Slide1Illustration colors={{ primary: C.primary, primaryPale: C.primaryPale }} />,
  },
  {
    id: '2',
    badge: '🤖 IA Coach Personnel',
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
    badge: '📋 Suivi Automatisé',
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
    badge: '✉️ Génération par IA',
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
  const flatListRef = useRef<FlatList>(null);
  const [currentIndex, setCurrentIndex] = useState(0);
  const isScrolling = useRef(false);

  const handleNext = useCallback(async () => {
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

  const handleSkip = useCallback(async () => {
    try {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    } catch (error) {
      // Silent fail
    }
    await SecureStore.setItemAsync('onboarding_completed', 'true');
    router.replace('/(auth)/login');
  }, [router]);

  const handleScroll = useCallback((event: NativeSyntheticEvent<NativeScrollEvent>) => {
    if (isScrolling.current) {
      const offsetX = event.nativeEvent.contentOffset.x;
      const index = Math.round(offsetX / SCREEN_WIDTH);
      if (index !== currentIndex && index >= 0 && index < SLIDES.length) {
        setCurrentIndex(index);
      }
    }
  }, [currentIndex]);

  const handleMomentumScrollBegin = useCallback(() => {
    isScrolling.current = true;
  }, []);

  const handleMomentumScrollEnd = useCallback((event: NativeSyntheticEvent<NativeScrollEvent>) => {
    isScrolling.current = false;
    const offsetX = event.nativeEvent.contentOffset.x;
    const index = Math.round(offsetX / SCREEN_WIDTH);
    if (index >= 0 && index < SLIDES.length) {
      setCurrentIndex(index);
    }
  }, []);

  const getItemLayout = useCallback(
    (_: any, index: number) => ({
      length: SCREEN_WIDTH,
      offset: SCREEN_WIDTH * index,
      index,
    }),
    []
  );

  const renderItem = useCallback(
    ({ item, index }: { item: SlideData; index: number }) => (
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
        onScrollToIndexFailed={(info) => {
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
