import React, { useEffect, useRef, useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Animated, Platform, Image } from 'react-native';
import { Swipeable } from 'react-native-gesture-handler';
import { Ionicons } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';
import { BlurView } from 'expo-blur';
import { Candidature, STATUS_THEME, StatusKey } from '../../types/crm.types';

interface Props {
  item: Candidature;
  onPressStatus: () => void;
  onSwipePrev: () => void;
  onSwipeNext: () => void;
  onPressAction?: () => void;
  onPressOpen?: () => void;
}

export const CandidatureCard: React.FC<Props> = ({
  item,
  onPressStatus,
  onSwipePrev,
  onSwipeNext,
  onPressAction,
  onPressOpen,
}) => {
  const meta = STATUS_THEME[item.status];
  const [isFlipped, setIsFlipped] = useState(false);
  
  // Animations
  const flipAnim = useRef(new Animated.Value(0)).current;
  const swipeHintAnim = useRef(new Animated.Value(0)).current;
  const scaleAnim = useRef(new Animated.Value(1)).current;
  const pulseAnim = useRef(new Animated.Value(1)).current;

  useEffect(() => {
    // Pulse for waypoints
    Animated.loop(
      Animated.sequence([
        Animated.timing(pulseAnim, { toValue: 1.12, duration: 1600, useNativeDriver: true }),
        Animated.timing(pulseAnim, { toValue: 1, duration: 1600, useNativeDriver: true }),
      ])
    ).start();

    // Swipe hint
    Animated.loop(
      Animated.sequence([
        Animated.timing(swipeHintAnim, { toValue: 1, duration: 2400, useNativeDriver: true }),
        Animated.timing(swipeHintAnim, { toValue: 0, duration: 2400, useNativeDriver: true }),
      ])
    ).start();
  }, []);

  const handleFlip = () => {
    const toValue = isFlipped ? 0 : 1;
    Animated.spring(flipAnim, {
      toValue,
      friction: 8,
      tension: 18,
      useNativeDriver: true,
    }).start();
    setIsFlipped(!isFlipped);
  };

  const frontInterpolate = flipAnim.interpolate({
    inputRange: [0, 1],
    outputRange: ['0deg', '180deg'],
  });

  const backInterpolate = flipAnim.interpolate({
    inputRange: [0, 1],
    outputRange: ['180deg', '360deg'],
  });

  const frontOpacity = flipAnim.interpolate({
    inputRange: [0, 0.48, 0.52, 1],
    outputRange: [1, 1, 0, 0],
  });

  const backOpacity = flipAnim.interpolate({
    inputRange: [0, 0.48, 0.52, 1],
    outputRange: [0, 0, 1, 1],
  });

  const renderLeft = () => (
    <LinearGradient
      colors={['#F5F4F0', '#E2E0DA']}
      start={{ x: 0, y: 0 }} end={{ x: 1, y: 0 }}
      style={styles.swipePanel}
    >
      <Ionicons name="chevron-back" size={24} color="#FF6B35" />
      <Text style={styles.swipeLabel}>RETOUR</Text>
    </LinearGradient>
  );

  const renderRight = () => (
    <LinearGradient
      colors={['#FF6B35', '#F59E0B']}
      start={{ x: 0, y: 0 }} end={{ x: 1, y: 0 }}
      style={[styles.swipePanel, { alignItems: 'flex-end' }]}
    >
      <Text style={[styles.swipeLabel, { color: '#FFFFFF' }]}>AVANCER</Text>
      <Ionicons name="chevron-forward" size={24} color="#FFFFFF" />
    </LinearGradient>
  );

  const pipeline: { key: StatusKey; label: string; icon: keyof typeof Ionicons.glyphMap; x: string; y: number }[] = [
    { key: 'a_postuler', label: 'Départ', icon: 'boat-outline', x: '12%', y: 15 },
    { key: 'envoye', label: 'Signal', icon: 'mail-unread-outline', x: '52%', y: 35 },
    { key: 'entretien', label: 'Escale', icon: 'map-outline', x: '22%', y: 65 },
    { key: 'relance', label: 'Cap', icon: 'compass-outline', x: '62%', y: 95 },
    { key: 'offre', label: 'Trésor', icon: 'trophy-outline', x: '35%', y: 130 },
  ];

  const currentIdx = pipeline.findIndex(s => s.key === item.status);
  const isRefused = item.status === 'refuse';

  return (
    <Swipeable
      renderLeftActions={renderLeft}
      renderRightActions={renderRight}
      onSwipeableLeftOpen={onSwipePrev}
      onSwipeableRightOpen={onSwipeNext}
      friction={1.8}
      enabled={!isFlipped}
    >
      <View style={styles.root}>
        <TouchableOpacity
          activeOpacity={1}
          onPress={handleFlip}
          onPressIn={() => Animated.spring(scaleAnim, { toValue: 0.97, useNativeDriver: true }).start()}
          onPressOut={() => Animated.spring(scaleAnim, { toValue: 1, useNativeDriver: true, friction: 3 }).start()}
        >
          {/* FRONT: CORRECTED ELITE VERSION */}
          <Animated.View style={[styles.card, { transform: [{ perspective: 1800 }, { rotateY: frontInterpolate }, { scale: scaleAnim }], opacity: frontOpacity }]}>
            <LinearGradient colors={['#FFFFFF', '#FDFCF7']} style={StyleSheet.absoluteFill} />
            <BlurView intensity={10} tint="light" style={StyleSheet.absoluteFill} />
            
            <View style={styles.content}>
               <View style={styles.header}>
                 <View style={styles.brandingGroup}>
                   <Image 
                     source={require('../../../assets/logosansfond.png')} 
                     style={styles.lilLogo} 
                     resizeMode="contain"
                   />
                   <Text style={styles.appName}>GOLDARMY</Text>
                 </View>
                 
                 <View style={styles.statusBadge}>
                   <LinearGradient colors={['#FF6B35', '#F59E0B']} style={styles.statusBadgeBg}>
                     <Text style={styles.statusBadgeTxt}>{meta.label.toUpperCase()}</Text>
                   </LinearGradient>
                 </View>
               </View>

               <View style={styles.mainInfo}>
                 <Text style={styles.companyNameSub}>{item.company.toUpperCase()}</Text>
                 <Text style={styles.jobHeading} numberOfLines={2}>{item.title}</Text>
                 
                 <View style={styles.detailsRow}>
                    <View style={styles.detailItem}>
                      <Ionicons name="calendar-outline" size={14} color="#FF6B35" />
                      <Text style={styles.detailTxt}>{item.date}</Text>
                    </View>
                    {item.description && (
                       <View style={styles.detailItem}>
                         <Ionicons name="document-text-outline" size={14} color="#9A9A94" />
                         <Text style={styles.detailTxt} numberOfLines={1}>Description dispo.</Text>
                       </View>
                    )}
                 </View>
               </View>

               <View style={styles.footerRow}>
                 <View style={styles.hologramContainer}>
                   <LinearGradient
                     colors={['#F5D061', '#FFF9E3', '#E6A32F']}
                     style={styles.holoShield}
                   >
                     <Text style={styles.holoChar}>{item.company.charAt(0)}</Text>
                   </LinearGradient>
                 </View>

                 <TouchableOpacity style={styles.eliteStatusBtn} onPress={onPressAction}>
                   <LinearGradient colors={['#F5F4F0', '#E2E0DA']} style={styles.eliteBtnGrad}>
                      <Ionicons name="color-wand-outline" size={20} color="#FF6B35" />
                   </LinearGradient>
                 </TouchableOpacity>
               </View>
            </View>

            <Animated.View style={[styles.swipeIndy, { opacity: swipeHintAnim }]}>
              <Ionicons name="chevron-forward" size={16} color="rgba(0,0,0,0.08)" />
            </Animated.View>
          </Animated.View>

          {/* BACK: TREASURE MAP (FIXED HEIGHT) */}
          <Animated.View style={[styles.card, styles.cardBack, { transform: [{ perspective: 1800 }, { rotateY: backInterpolate }, { scale: scaleAnim }], opacity: backOpacity }]}>
             <LinearGradient colors={['#FFFBEB', '#FFFFFF', '#FDF6E3']} style={StyleSheet.absoluteFill} />
             <View style={styles.content}>
               <View style={styles.mapHeader}>
                 <Text style={styles.journeyTitle}>MISSION DE RECRUTEMENT</Text>
                 <View style={styles.journeyUnderline} />
               </View>
               
               <View style={styles.mapCanvas}>
                  <View style={styles.treasurePath} />
                  
                  {pipeline.map((step, idx) => {
                    const isPast = currentIdx >= idx || (isRefused && idx < pipeline.length - 1);
                    const isCurrent = step.key === item.status;
                    return (
                      <View key={step.key} style={[styles.mapPoint, { left: step.x, top: step.y }]}>
                        <View style={[styles.pointShell, isPast && { borderColor: '#B8860B', backgroundColor: '#FFFFFF' }]}>
                          <Ionicons name={step.icon} size={18} color={isPast ? '#FF6B35' : 'rgba(0,0,0,0.1)'} />
                        </View>
                        {isCurrent && (
                          <Animated.View style={[styles.currentLock, { transform: [{ scale: pulseAnim }] }]}>
                             <Ionicons name={isRefused ? "close-circle" : "close"} size={44} color={isRefused ? "#EF4444" : "#FF6B35"} />
                          </Animated.View>
                        )}
                        <Text style={[styles.pointLabel, isCurrent && { color: '#FF6B35', fontWeight: '900' }]}>{step.label}</Text>
                      </View>
                    );
                  })}
               </View>

               <View style={styles.mapFooter}>
                 <TouchableOpacity style={styles.fullDetailBtn} onPress={onPressOpen}>
                    <Text style={styles.fullDetailTxt}>OUVRIR LE DOSSIER</Text>
                    <Ionicons name="sparkles" size={14} color="#FF6B35" />
                 </TouchableOpacity>
               </View>
            </View>
          </Animated.View>
        </TouchableOpacity>
      </View>
    </Swipeable>
  );
};

const styles = StyleSheet.create({
  root: {
    paddingHorizontal: 16,
    paddingVertical: 12,
  },
  card: {
    borderRadius: 36,
    backgroundColor: '#FFFFFF',
    minHeight: 280, // INCREASED HEIGHT TO PREVENT CLIPPING
    overflow: 'hidden',
    backfaceVisibility: 'hidden',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 10 },
    shadowOpacity: 0.1,
    shadowRadius: 20,
    elevation: 12,
    borderWidth: 1,
    borderColor: '#E2E0DA',
  },
  cardBack: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    width: '100%',
  },
  content: {
    flex: 1,
    padding: 24,
    justifyContent: 'space-between',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  brandingGroup: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(0,0,0,0.02)',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 12,
  },
  lilLogo: {
    width: 18,
    height: 18,
    marginRight: 8,
  },
  appName: {
    fontSize: 9,
    fontWeight: '900',
    color: '#D4AF37',
    letterSpacing: 2,
  },
  statusBadge: {
    borderRadius: 10,
    overflow: 'hidden',
  },
  statusBadgeBg: {
    paddingHorizontal: 12,
    paddingVertical: 4,
  },
  statusBadgeTxt: {
    fontSize: 9,
    fontWeight: '900',
    color: '#FFFFFF',
    letterSpacing: 1,
  },
  mainInfo: {
    marginTop: 10,
  },
  companyNameSub: {
    fontSize: 12,
    fontWeight: '800',
    color: '#9A9A94',
    letterSpacing: 3,
    marginBottom: 6,
  },
  jobHeading: {
    fontSize: 20, // REDUCED FONT SIZE AS REQUESTED
    fontWeight: '900',
    color: '#1A1A1F',
    letterSpacing: -0.5,
    marginBottom: 10,
  },
  detailsRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  detailItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginRight: 20,
    backgroundColor: '#F5F4F0',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 8,
  },
  detailTxt: {
    fontSize: 11,
    fontWeight: '700',
    color: '#4A4A46',
    marginLeft: 6,
  },
  footerRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingTop: 10,
  },
  hologramContainer: {
    alignItems: 'center',
    justifyContent: 'center',
  },
  holoShield: {
    width: 52,
    height: 52,
    borderRadius: 16,
    alignItems: 'center',
    justifyContent: 'center',
    shadowColor: '#F5D061',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.2,
    shadowRadius: 8,
  },
  holoChar: {
    fontSize: 24,
    fontWeight: '900',
    color: '#0A0A0F',
  },
  eliteStatusBtn: {
    borderRadius: 16,
    overflow: 'hidden',
    borderWidth: 1,
    borderColor: '#E2E0DA',
  },
  eliteBtnGrad: {
    width: 52,
    height: 52,
    alignItems: 'center',
    justifyContent: 'center',
  },
  swipeIndy: {
    position: 'absolute',
    right: 10,
    top: '48%',
  },
  mapHeader: {
    alignItems: 'center',
  },
  journeyTitle: {
    fontSize: 10,
    fontWeight: '900',
    color: '#B8860B',
    letterSpacing: 3,
    marginBottom: 8,
  },
  journeyUnderline: {
    width: 40,
    height: 2,
    backgroundColor: '#FF6B35',
    borderRadius: 1,
    opacity: 0.3,
  },
  mapCanvas: {
    height: 160, // REDUCED TO FIT WITHIN CARD WITHOUT CLIPPING
    position: 'relative',
    marginVertical: 5,
  },
  treasurePath: {
    position: 'absolute',
    left: '15%',
    right: '20%',
    top: 20,
    bottom: 20,
    borderWidth: 2,
    borderColor: 'rgba(184, 134, 11, 0.1)',
    borderStyle: 'dotted',
    borderRadius: 100,
    transform: [{ rotate: '12deg' }],
  },
  mapPoint: {
    position: 'absolute',
    alignItems: 'center',
    zIndex: 10,
  },
  pointShell: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: '#F9F7F0',
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 1.5,
    borderColor: '#E2E0DA',
  },
  pointLabel: {
    fontSize: 9,
    fontWeight: '800',
    color: '#9A9A94',
    marginTop: 6,
    letterSpacing: 1,
  },
  currentLock: {
    position: 'absolute',
    top: -24,
    right: -24,
    zIndex: 20,
  },
  mapFooter: {
    borderTopWidth: 1,
    borderTopColor: '#E2E0DA',
    paddingTop: 15,
  },
  fullDetailBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#FFFBEB',
    paddingVertical: 12,
    borderRadius: 12,
  },
  fullDetailTxt: {
    fontSize: 11,
    fontWeight: '900',
    color: '#FF6B35',
    marginRight: 10,
    letterSpacing: 2,
  },
  swipePanel: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 35,
    borderRadius: 36,
    marginVertical: 12,
    marginHorizontal: 16,
  },
  swipeLabel: {
    fontSize: 18,
    fontWeight: '900',
    color: '#4A4A46',
    marginHorizontal: 15,
    letterSpacing: 2,
  },
});
