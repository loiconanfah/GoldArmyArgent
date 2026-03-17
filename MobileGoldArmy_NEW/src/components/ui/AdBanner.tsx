/**
 * Ad Banner Component
 * Displays promotional cards for SplitsPay, Babagame, and other ads
 */

import React, { useRef, useEffect } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, Dimensions, Animated } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';
import { spacing } from '../../theme/spacing';

const { width } = Dimensions.get('window');

interface AdItem {
  id: string;
  title: string;
  subtitle: string;
  icon: string;
  color: string;
  gradient: string[];
  url?: string;
}

const ADS: AdItem[] = [
  {
    id: 'splitspay',
    title: 'SplitsPay',
    subtitle: 'Paiement partagé simplifié',
    icon: 'wallet',
    color: '#F5D061',
    gradient: ['#F5D061', '#E6A32F'],
  },
  {
    id: 'babagame',
    title: 'Babagame',
    subtitle: 'Jeux en ligne premium',
    icon: 'game-controller',
    color: '#60A5FA',
    gradient: ['#60A5FA', '#3B82F6'],
  },
  {
    id: 'premium',
    title: 'Premium',
    subtitle: 'Débloquez toutes les fonctionnalités',
    icon: 'diamond',
    color: '#BB86FC',
    gradient: ['#BB86FC', '#9B59B6'],
  },
];

export function AdBanner() {
  const scrollAnim = useRef(new Animated.Value(0)).current;
  const fadeAnim = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    Animated.timing(fadeAnim, {
      toValue: 1,
      duration: 600,
      delay: 800,
      useNativeDriver: true,
    }).start();
  }, []);

  const handleAdPress = (ad: AdItem) => {
    // TODO: Handle navigation or external link
    console.log('Ad pressed:', ad.id);
  };

  return (
    <Animated.View style={[styles.container, { opacity: fadeAnim }]}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Découvrez nos partenaires</Text>
        <TouchableOpacity>
          <Ionicons name="close" size={18} color="#9A9A94" />
        </TouchableOpacity>
      </View>
      
      <ScrollView
        horizontal
        showsHorizontalScrollIndicator={false}
        contentContainerStyle={styles.scrollContent}
        decelerationRate="fast"
        snapToInterval={width * 0.75 + spacing.md}
      >
        {ADS.map((ad, index) => (
          <TouchableOpacity
            key={ad.id}
            activeOpacity={0.9}
            onPress={() => handleAdPress(ad)}
            style={styles.adCard}
          >
            <LinearGradient
              colors={ad.gradient}
              start={{ x: 0, y: 0 }}
              end={{ x: 1, y: 1 }}
              style={styles.gradient}
            >
              <View style={styles.adContent}>
                <View style={styles.adIconContainer}>
                  <Ionicons name={ad.icon as any} size={32} color="#FFFFFF" />
                </View>
                <View style={styles.adTextContainer}>
                  <Text style={styles.adTitle}>{ad.title}</Text>
                  <Text style={styles.adSubtitle}>{ad.subtitle}</Text>
                </View>
                <View style={styles.adArrow}>
                  <Ionicons name="arrow-forward" size={20} color="#FFFFFF" />
                </View>
              </View>
            </LinearGradient>
          </TouchableOpacity>
        ))}
      </ScrollView>
    </Animated.View>
  );
}

const styles = StyleSheet.create({
  container: {
    marginTop: spacing['2xl'],
    marginBottom: spacing.xl,
    paddingHorizontal: spacing.xl,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.md,
  },
  headerTitle: {
    fontSize: 13,
    fontWeight: '700',
    color: '#4A4A46',
    letterSpacing: 0.3,
  },
  scrollContent: {
    paddingRight: spacing.lg,
  },
  adCard: {
    width: width * 0.75,
    marginRight: spacing.md,
    borderRadius: 20,
    overflow: 'hidden',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.12,
    shadowRadius: 16,
    elevation: 6,
  },
  gradient: {
    padding: spacing.lg,
    minHeight: 100,
  },
  adContent: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  adIconContainer: {
    width: 56,
    height: 56,
    borderRadius: 28,
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: spacing.md,
  },
  adTextContainer: {
    flex: 1,
  },
  adTitle: {
    fontSize: 20,
    fontWeight: '800',
    color: '#FFFFFF',
    marginBottom: 4,
    letterSpacing: -0.5,
  },
  adSubtitle: {
    fontSize: 13,
    color: 'rgba(255, 255, 255, 0.9)',
    fontWeight: '600',
  },
  adArrow: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    justifyContent: 'center',
    alignItems: 'center',
    marginLeft: spacing.sm,
  },
});
