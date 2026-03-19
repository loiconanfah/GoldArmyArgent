/**
 * Onboarding Screen
 * First-launch onboarding with 4 slides
 */

import * as React from 'react';
import {
  View,
  Text,
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
import { styles, C } from './styles/onboarding.styles';

const { width: SCREEN_WIDTH } = Dimensions.get('window');

// Helper function to create highlight content
const createHighlightContent = (type: 'confidence' | 'applications') => {
  if (type === 'confidence') {
    return (
      <View style={styles.highlightWrapper}>
        <Text style={styles.highlightTitle}>
          Confiance : 94%
        </Text>
        <View style={styles.progressBarBg}>
          <View style={styles.progressBarFill} />
        </View>
      </View>
    );
  } else {
    return (
      <View style={styles.highlightWrapper}>
        <Text style={styles.highlightTitle}>
          12 candidatures actives
        </Text>
        <Text style={styles.highlightSubtitle}>3 en entretien • 2 offres reçues</Text>
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
        colors={{ primary: C.primary, primaryPale: C.primaryPale, surface: C.bg }}
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
          surface: C.bg,
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
        colors={{ primary: C.primary, primaryPale: C.primaryPale, surface: C.bg }}
      />
    ),
  },
];

export default function OnboardingScreen() {
  const router = useRouter();
  const flatListRef = React.useRef<FlatList>(null);
  const [currentIndex, setCurrentIndex] = React.useState(0);
  const isScrolling = React.useRef(false);

  React.useEffect(() => {
    const checkStatus = async () => {
      try {
        const completed = await SecureStore.getItemAsync('onboarding_completed');
        if (completed === 'true') {
          router.replace('/(auth)/login');
        }
      } catch (err) {
        console.error('[Onboarding] Error checking status:', err);
      }
    };
    checkStatus();
  }, [router]);

  const handleNext = React.useCallback(async () => {
    if (currentIndex < SLIDES.length - 1) {
      const nextIndex = currentIndex + 1;
      flatListRef.current?.scrollToIndex({ index: nextIndex, animated: true });
      try {
        Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
      } catch (error) {}
    } else {
      try {
        Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
      } catch (error) {}
      await SecureStore.setItemAsync('onboarding_completed', 'true');
      router.replace('/(auth)/login');
    }
  }, [currentIndex, router]);

  const handleSkip = React.useCallback(async () => {
    try {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    } catch (error) {}
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
      <View style={styles.dotsContainer}>
        <OnboardingDots total={SLIDES.length} activeIndex={currentIndex} colors={{ primary: C.primary, border: C.border }} />
      </View>
    </View>
  );
}
