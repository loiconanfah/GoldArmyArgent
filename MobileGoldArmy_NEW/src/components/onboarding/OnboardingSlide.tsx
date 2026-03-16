/**
 * Onboarding Slide Component
 * Individual slide with animated content
 */

import React, { useEffect, useRef } from 'react';
import { View, Text, StyleSheet, Animated, Dimensions, TouchableOpacity } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { OnboardingSlideProps } from '../../types/onboarding.types';
import { Image } from 'expo-image';
import { Ionicons } from '@expo/vector-icons';

const { width: SCREEN_WIDTH, height: SCREEN_HEIGHT } = Dimensions.get('window');

// Couleurs alignées sur le thème global de l'app (même palette que onboarding.tsx)
const C = {
  primary: '#F5D061', // gold / couleur principale du logo
  primarySoft: '#F8DC8A',
  primaryPale: '#FFF8DC',
  primaryDeep: '#E6A32F',
  accent: '#F5D061', // même teinte que le logo (pas de bleu)
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

const SP = { xs: 4, sm: 8, md: 12, lg: 16, xl: 24, xxl: 32, xxxl: 48, hero: 64 };
const R = { sm: 8, md: 14, lg: 20, xl: 28, full: 999 };

export function OnboardingSlide({
  slide,
  isActive,
  onNext,
  onSkip,
  isLast,
}: OnboardingSlideProps) {
  const badgeOpacity = useRef(new Animated.Value(0)).current;
  const badgeScale = useRef(new Animated.Value(0.85)).current;
  const titleOpacity = useRef(new Animated.Value(0)).current;
  const titleTranslateY = useRef(new Animated.Value(20)).current;
  const subtitleOpacity = useRef(new Animated.Value(0)).current;
  const subtitleTranslateY = useRef(new Animated.Value(20)).current;
  const highlightOpacity = useRef(new Animated.Value(0)).current;
  const highlightTranslateY = useRef(new Animated.Value(16)).current;
  const buttonOpacity = useRef(new Animated.Value(0)).current;
  const buttonScale = useRef(new Animated.Value(0.92)).current;

  useEffect(() => {
    if (isActive) {
      // Reset animations
      badgeOpacity.setValue(0);
      badgeScale.setValue(0.85);
      titleOpacity.setValue(0);
      titleTranslateY.setValue(20);
      subtitleOpacity.setValue(0);
      subtitleTranslateY.setValue(20);
      highlightOpacity.setValue(0);
      highlightTranslateY.setValue(16);
      buttonOpacity.setValue(0);
      buttonScale.setValue(0.92);

      // Animate entrance
      Animated.parallel([
        // Badge
        Animated.parallel([
          Animated.timing(badgeOpacity, {
            toValue: 1,
            duration: 400,
            delay: 100,
            useNativeDriver: true,
          }),
          Animated.spring(badgeScale, {
            toValue: 1,
            delay: 100,
            useNativeDriver: true,
            stiffness: 200,
            damping: 15,
          }),
        ]),
        // Title
        Animated.parallel([
          Animated.timing(titleOpacity, {
            toValue: 1,
            duration: 500,
            delay: 200,
            useNativeDriver: true,
          }),
          Animated.timing(titleTranslateY, {
            toValue: 0,
            duration: 500,
            delay: 200,
            useNativeDriver: true,
          }),
        ]),
        // Subtitle
        Animated.parallel([
          Animated.timing(subtitleOpacity, {
            toValue: 1,
            duration: 500,
            delay: 320,
            useNativeDriver: true,
          }),
          Animated.timing(subtitleTranslateY, {
            toValue: 0,
            duration: 500,
            delay: 320,
            useNativeDriver: true,
          }),
        ]),
        // Highlight (if exists)
        slide.hasHighlight
          ? Animated.parallel([
              Animated.timing(highlightOpacity, {
                toValue: 1,
                duration: 500,
                delay: 440,
                useNativeDriver: true,
              }),
              Animated.timing(highlightTranslateY, {
                toValue: 0,
                duration: 500,
                delay: 440,
                useNativeDriver: true,
              }),
            ])
          : Animated.timing(highlightOpacity, { toValue: 0, duration: 0, useNativeDriver: true }),
        // Button
        Animated.parallel([
          Animated.timing(buttonOpacity, {
            toValue: 1,
            duration: 400,
            delay: 500,
            useNativeDriver: true,
          }),
          Animated.spring(buttonScale, {
            toValue: 1,
            delay: 500,
            useNativeDriver: true,
            stiffness: 200,
            damping: 15,
          }),
        ]),
      ]).start();
    }
  }, [isActive, slide.hasHighlight]);

  return (
    <View style={styles.container}>
      {/* Logo en haut, aligné avec l'identité visuelle de l'app */}
      <View style={styles.logoWrapper}>
        <Image
          source={require('../../../assets/logosansfond.png')}
          style={styles.logoImage}
          contentFit="contain"
        />
      </View>

      {/* Skip link (slides 1-3 only) */}
      {!isLast && (
        <TouchableOpacity onPress={onSkip} style={styles.skipButton}>
          <Text style={styles.skipText}>Passer</Text>
        </TouchableOpacity>
      )}

      {/* Illustration zone (45% of screen height) */}
      <View style={styles.illustrationContainer}>
        <LinearGradient
          colors={[C.primaryPale, C.bg]}
          start={{ x: 0.5, y: 0 }}
          end={{ x: 0.5, y: 1 }}
          style={StyleSheet.absoluteFill}
        />
        {slide.illustration}
      </View>

      {/* Content zone */}
      <View style={styles.content}>
        {/* Badge + icône */}
        <Animated.View
          style={[
            styles.badge,
            {
              opacity: badgeOpacity,
              transform: [{ scale: badgeScale }],
            },
          ]}
        >
          <Ionicons
            name={slide.icon}
            size={18}
            color={C.primaryDeep}
            style={styles.badgeIcon}
          />
          <Text style={styles.badgeText}>{slide.badge}</Text>
        </Animated.View>

        {/* Title */}
        <Animated.View
          style={[
            styles.titleContainer,
            {
              opacity: titleOpacity,
              transform: [{ translateY: titleTranslateY }],
            },
          ]}
        >
          <Text style={styles.title}>{slide.title}</Text>
        </Animated.View>

        {/* Subtitle */}
        <Animated.View
          style={[
            styles.subtitleContainer,
            {
              opacity: subtitleOpacity,
              transform: [{ translateY: subtitleTranslateY }],
            },
          ]}
        >
          <Text style={styles.subtitle}>{slide.subtitle}</Text>
        </Animated.View>

        {/* Highlight card (slides 2 and 3) */}
        {slide.hasHighlight && slide.highlightContent && (
          <Animated.View
            style={[
              styles.highlightCard,
              {
                opacity: highlightOpacity,
                transform: [{ translateY: highlightTranslateY }],
              },
            ]}
          >
            {slide.highlightContent}
          </Animated.View>
        )}

        {/* Button */}
        <Animated.View
          style={[
            styles.buttonContainer,
            {
              opacity: buttonOpacity,
              transform: [{ scale: buttonScale }],
            },
          ]}
        >
          <TouchableOpacity onPress={onNext} style={styles.button} activeOpacity={0.8}>
            <LinearGradient
              colors={[C.primaryDeep, C.primary]}
              start={{ x: 0, y: 0 }}
              end={{ x: 1, y: 1 }}
              style={styles.buttonGradient}
            >
              <Text style={styles.buttonText}>
                {isLast ? 'Commencer maintenant' : 'Suivant →'}
              </Text>
            </LinearGradient>
          </TouchableOpacity>
        </Animated.View>

        {/* Login link (slide 4 only) */}
        {isLast && (
          <TouchableOpacity onPress={onSkip} style={styles.loginLink}>
            <Text style={styles.loginLinkText}>J'ai déjà un compte → Se connecter</Text>
          </TouchableOpacity>
        )}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    width: SCREEN_WIDTH,
    height: SCREEN_HEIGHT,
    backgroundColor: C.bg,
  },
  logoWrapper: {
    position: 'absolute',
    top: 48,
    left: SP.xl,
    alignItems: 'center',
    zIndex: 20,
  },
  logoImage: {
    width: 40,
    height: 40,
  },
  skipButton: {
    position: 'absolute',
    top: 60,
    right: SP.xl,
    zIndex: 10,
    padding: SP.sm,
  },
  skipText: {
    fontSize: 13,
    color: C.textMuted,
    fontWeight: '500',
  },
  illustrationContainer: {
    height: SCREEN_HEIGHT * 0.45,
    width: '100%',
    position: 'relative',
    overflow: 'hidden',
  },
  content: {
    flex: 1,
    paddingHorizontal: SP.xl,
    paddingTop: SP.xxl,
    paddingBottom: SP.xxxl,
  },
  badge: {
    alignSelf: 'flex-start',
    backgroundColor: C.primaryPale,
    paddingHorizontal: SP.md,
    paddingVertical: SP.xs,
    borderRadius: R.full,
    marginBottom: SP.lg,
    flexDirection: 'row',
    alignItems: 'center',
  },
  badgeIcon: {
    marginRight: SP.xs,
  },
  badgeText: {
    fontSize: 12,
    fontWeight: '600',
    color: C.primary,
  },
  titleContainer: {
    marginBottom: SP.md,
  },
  title: {
    fontSize: 36,
    fontWeight: '900',
    color: C.text,
    lineHeight: 44,
    letterSpacing: -1,
  },
  subtitleContainer: {
    marginBottom: SP.lg,
  },
  subtitle: {
    fontSize: 15,
    lineHeight: 24,
    color: C.textMid,
  },
  highlightCard: {
    alignSelf: 'center',
    backgroundColor: C.surface,
    borderRadius: R.lg,
    padding: SP.lg,
    marginTop: SP.md,
    marginBottom: SP.lg,
    shadowColor: C.shadow,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 1,
    shadowRadius: 12,
    elevation: 4,
  },
  buttonContainer: {
    marginTop: 'auto',
  },
  button: {
    borderRadius: R.full,
    overflow: 'hidden',
    shadowColor: C.shadow,
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 1,
    shadowRadius: 16,
    elevation: 6,
  },
  buttonGradient: {
    paddingVertical: SP.lg,
    alignItems: 'center',
    justifyContent: 'center',
  },
  buttonText: {
    color: C.white,
    fontSize: 16,
    fontWeight: '700',
    letterSpacing: 0.5,
  },
  loginLink: {
    marginTop: SP.md,
    alignItems: 'center',
  },
  loginLinkText: {
    fontSize: 14,
    color: C.textMuted,
    fontWeight: '500',
  },
});
