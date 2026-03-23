import React, { useState, useRef, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Animated,
  Dimensions,
  Platform,
  Modal,
  ScrollView,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { useUIStore } from '../../stores/uiStore';
import { styles } from './styles/TutorialOverlay.styles';

const { width, height } = Dimensions.get('window');

const STEPS = [
  {
    id: 'welcome',
    title: 'Bienvenue sur GoldArmy ! 🚀',
    description: 'Ton arsenal IA complet pour booster ta carrière et décrocher ton prochain job.',
    icon: 'rocket-outline',
    position: 'center',
  },
  {
    id: 'notifs',
    title: 'Tes Notifications 🔔',
    description: 'Reste informé des alertes emploi et des retours de tes audits ici.',
    icon: 'notifications-outline',
    highlight: { top: 0, right: 60, width: 44, height: 44, circle: true },
    position: 'top-right',
  },
  {
    id: 'stats',
    title: 'Analyse du Marché 📊',
    description: 'Consulte les statistiques en temps réel et les opportunités du moment.',
    icon: 'bar-chart-outline',
    highlight: { top: 180, left: 20, width: width - 40, height: 160, borderRadius: 24 },
    position: 'center',
  },
  // OUTILS
  {
    id: 'tool_sniper',
    title: 'Sniper Search 🎯',
    description: 'Le scanneur d\'offres le plus puissant. Trouve le job parfait avec 94% de précision.',
    icon: 'search-outline',
    highlight: { top: 380, left: 16, width: width - 32, height: 160, borderRadius: 24 },
    position: 'center',
  },
  {
    id: 'tool_mentor',
    title: 'Mentor IA ✨',
    description: 'Audit complet de ton CV et personnalisation de tes candidatures en 30 secondes.',
    icon: 'sparkles-outline',
    highlight: { top: 550, left: 16, width: width - 32, height: 160, borderRadius: 24 },
    position: 'center',
  },
  {
    id: 'tool_vocal',
    title: 'Entretien Vocal 🎙️',
    description: 'Simule tes entretiens avec notre IA pour gagner 60% de confiance supplémentaire.',
    icon: 'mic-outline',
    highlight: { top: 720, left: 16, width: width - 32, height: 160, borderRadius: 24 },
    position: 'center',
  },
  // NAVBAR
  {
    id: 'nav_home',
    title: 'Accueil 🏠',
    description: 'Reviens ici pour voir ton tableau de bord et tes outils.',
    icon: 'home-outline',
    highlight: { bottom: 0, left: '12%', width: 50, height: 64, circle: true },
    position: 'bottom-nav',
  },
  {
    id: 'nav_sniper',
    title: 'Recherche Sniper 🔍',
    description: 'Accès direct au moteur de recherche d\'offres IA.',
    icon: 'search-outline',
    highlight: { bottom: 0, left: '25%', width: 50, height: 64, circle: true },
    position: 'bottom-nav',
  },
  {
    id: 'nav_mentor',
    title: 'Espace Mentor 💎',
    description: 'Gère tes CVs et tes préparations d\'entretiens.',
    icon: 'sparkles-outline',
    highlight: { bottom: 0, left: '38%', width: 50, height: 64, circle: true },
    position: 'bottom-nav',
  },
  {
    id: 'nav_crm',
    title: 'Suivi Candidatures 📂',
    description: 'Ton tableau Kanban pour ne jamais oublier une relance.',
    icon: 'briefcase-outline',
    highlight: { bottom: 0, left: '62%', width: 50, height: 64, circle: true },
    position: 'bottom-nav',
  },
  {
    id: 'nav_profile',
    title: 'Ton Profil 👤',
    description: 'Gère tes informations et tes préférences de carrière.',
    icon: 'person-outline',
    highlight: { bottom: 0, left: '88%', width: 50, height: 64, circle: true },
    position: 'bottom-nav',
  },
];

export function TutorialOverlay() {
  const [currentStep, setCurrentStep] = useState(0);
  const { completeTutorial } = useUIStore();
  const insets = useSafeAreaInsets();
  
  const fadeAnim = useRef(new Animated.Value(0)).current;
  const slideAnim = useRef(new Animated.Value(20)).current;

  useEffect(() => {
    showStep();
  }, [currentStep]);

  const showStep = () => {
    fadeAnim.setValue(0);
    slideAnim.setValue(20);
    Animated.parallel([
      Animated.timing(fadeAnim, {
        toValue: 1,
        duration: 400,
        useNativeDriver: true,
      }),
      Animated.spring(slideAnim, {
        toValue: 0,
        tension: 50,
        useNativeDriver: true,
      }),
    ]).start();
  };

  const nextStep = () => {
    if (currentStep < STEPS.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      finish();
    }
  };

  const finish = () => {
    Animated.timing(fadeAnim, {
      toValue: 0,
      duration: 300,
      useNativeDriver: true,
    }).start(() => {
      completeTutorial();
    });
  };

  const step = STEPS[currentStep];

  // Logic for highlight positioning
  const getHighlightStyle = () => {
    if (!step.highlight) return { display: 'none' as const };
    const h = step.highlight;
    const style: any = {
      position: 'absolute',
      width: h.width,
      height: h.height,
      borderRadius: h.circle ? h.width / 2 : (h.borderRadius || 12),
      borderWidth: 2,
      borderColor: '#FF6B35',
      backgroundColor: 'rgba(255, 107, 53, 0.1)',
    };

    if (h.top !== undefined) style.top = h.top + (step.id === 'notifs' ? insets.top : 0);
    if (h.bottom !== undefined) style.bottom = h.bottom + (Platform.OS === 'ios' ? 24 : 16);
    if (h.left !== undefined) {
      if (typeof h.left === 'string' && h.left.endsWith('%')) {
        const percent = parseFloat(h.left) / 100;
        style.left = width * percent - (h.width / 2);
      } else {
        style.left = h.left;
      }
    }
    if (h.right !== undefined) style.right = h.right;

    return style;
  };

  // Content card positioning
  const getCardStyle = () => {
    const style: any = {
      position: 'absolute',
      width: width - 40,
      backgroundColor: '#FFF',
      borderRadius: 24,
      padding: 24,
      alignItems: 'center',
      shadowColor: '#000',
      shadowOffset: { width: 0, height: 10 },
      shadowOpacity: 0.3,
      shadowRadius: 20,
      elevation: 10,
      opacity: fadeAnim,
      transform: [{ translateY: slideAnim }],
    };

    if (step.position === 'center') {
      style.top = height / 2 - 100;
    } else if (step.position === 'bottom-nav') {
      style.bottom = 140;
    } else if (step.position === 'top-right') {
      style.top = insets.top + 80;
    } else {
      style.top = height / 3;
    }

    return style;
  };

  return (
    <Modal transparent visible animationType="none">
      <View style={styles.container}>
        {/* Backdrop */}
        <View style={styles.backdrop} />

        {/* Highlight Zone */}
        <View style={getHighlightStyle()} />

        {/* Content Card */}
        <Animated.View style={getCardStyle()}>
          <View style={styles.iconContainer}>
            <Ionicons name={step.icon as any} size={32} color="#FF6B35" />
          </View>
          <Text style={styles.title}>{step.title}</Text>
          <Text style={styles.description}>{step.description}</Text>
          
          <View style={styles.footer}>
            <Text style={styles.progress}>
              {currentStep + 1} / {STEPS.length}
            </Text>
            <TouchableOpacity style={styles.button} onPress={nextStep}>
              <Text style={styles.buttonText}>
                {currentStep === STEPS.length - 1 ? 'C\'est parti !' : 'Suivant'}
              </Text>
              <Ionicons name="arrow-forward" size={18} color="#FFF" style={{ marginLeft: 8 }} />
            </TouchableOpacity>
          </View>
        </Animated.View>

        {/* Skip button */}
        <TouchableOpacity 
          style={[styles.skipButton, { top: insets.top + 10 }]} 
          onPress={finish}
          activeOpacity={0.7}
        >
          <Text style={styles.skipText}>Passer le tutoriel</Text>
        </TouchableOpacity>
      </View>
    </Modal>
  );
}
