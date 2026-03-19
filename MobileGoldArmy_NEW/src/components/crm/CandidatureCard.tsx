import React, { useEffect, useRef, useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Animated, Platform, Image, Modal, ScrollView, SafeAreaView } from 'react-native';
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
  const [isModalVisible, setIsModalVisible] = useState(false);
  
  // Animations
  const flipAnim = useRef(new Animated.Value(0)).current;
  const swipeAnim = useRef(new Animated.Value(0)).current;
  const scaleAnim = useRef(new Animated.Value(1)).current;
  const pulseAnim = useRef(new Animated.Value(1)).current;

  useEffect(() => {
    Animated.loop(
      Animated.sequence([
        Animated.timing(pulseAnim, { toValue: 1.15, duration: 1500, useNativeDriver: true }),
        Animated.timing(pulseAnim, { toValue: 1, duration: 1500, useNativeDriver: true }),
      ])
    ).start();

    Animated.loop(
      Animated.sequence([
        Animated.timing(swipeAnim, { toValue: 1, duration: 2500, useNativeDriver: true }),
        Animated.timing(swipeAnim, { toValue: 0, duration: 0, useNativeDriver: true }),
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

  const arrowTranslateX = swipeAnim.interpolate({
    inputRange: [0, 0.5, 1],
    outputRange: [0, 15, 0],
  });

  const arrowOpacity = swipeAnim.interpolate({
    inputRange: [0, 0.2, 0.8, 1],
    outputRange: [0, 1, 1, 0],
  });

  const renderLeft = () => (
    <LinearGradient
      colors={['#F5F4F0', '#E2E0DA']}
      start={{ x: 0, y: 0 }} end={{ x: 1, y: 0 }}
      style={styles.swipePanel}
    >
      <Ionicons name="chevron-back" size={24} color="#FF6B35" />
      <Text style={styles.swipeLabel}>PRÉCÉDENT</Text>
    </LinearGradient>
  );

  const renderRight = () => (
    <LinearGradient
      colors={['#FF6B35', '#F59E0B']}
      start={{ x: 0, y: 0 }} end={{ x: 1, y: 0 }}
      style={[styles.swipePanel, { alignItems: 'flex-end' }]}
    >
      <Text style={[styles.swipeLabel, { color: '#FFFFFF' }]}>SUIVANT</Text>
      <Ionicons name="chevron-forward" size={24} color="#FFFFFF" />
    </LinearGradient>
  );

  const pipeline: { key: StatusKey; label: string; icon: keyof typeof Ionicons.glyphMap; x: string; y: number }[] = [
    { key: 'a_postuler', label: 'Départ', icon: 'boat-outline', x: '12%', y: 15 },
    { key: 'envoye', label: 'Signal', icon: 'mail-unread-outline', x: '52%', y: 35 },
    { key: 'entretien', label: 'Escale', icon: 'people-circle-outline', x: '22%', y: 65 },
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
          {/* FRONT */}
          <Animated.View style={[styles.card, { transform: [{ perspective: 1800 }, { rotateY: frontInterpolate }, { scale: scaleAnim }], opacity: frontOpacity }]}>
            <LinearGradient colors={['#FFFFFF', '#FDFCF7']} style={StyleSheet.absoluteFill} />
            <View style={styles.content}>
               <View style={styles.header}>
                 <View style={styles.brandingBox}>
                   <Image source={require('../../../assets/logosansfond.png')} style={styles.appMiniLogo} resizeMode="contain" />
                   <Text style={styles.brandTitle}>GOLDARMY</Text>
                 </View>
                 <View style={styles.pillBadge}>
                   <LinearGradient colors={['#FF6B35', '#F59E0B']} style={styles.pillBadgeBg}>
                     <Text style={styles.pillBadgeTxt}>{meta.label.toUpperCase()}</Text>
                   </LinearGradient>
                 </View>
               </View>

               <View style={styles.infoArea}>
                 <Text style={styles.companySubHeader}>{item.company.toUpperCase()}</Text>
                 <Text style={styles.jobHeadingTxt} numberOfLines={2}>{item.title}</Text>
                 <View style={styles.metaRow}>
                    <View style={styles.metaBadge}>
                      <Ionicons name="calendar-outline" size={12} color="#FF6B35" />
                      <Text style={styles.metaTxt}>{item.date}</Text>
                    </View>
                 </View>
               </View>

               <View style={styles.footerRow}>
                 <View style={styles.hologramSeal}>
                   <LinearGradient colors={['#F5D061', '#FFF9E3', '#E6A32F']} style={styles.sealCircle}>
                     <Text style={styles.sealChar}>{item.company.charAt(0)}</Text>
                   </LinearGradient>
                 </View>
                 <View style={styles.frontActions}>
                    <TouchableOpacity style={styles.iconicBtn} onPress={() => setIsModalVisible(true)}>
                      <LinearGradient colors={['#F5F4F0', '#E2E0DA']} style={styles.iconicBtnGrad}>
                        <Ionicons name="information-circle-outline" size={24} color="#FF6B35" />
                      </LinearGradient>
                    </TouchableOpacity>
                    <TouchableOpacity style={styles.eliteStatusBtn} onPress={onPressAction}>
                      <LinearGradient colors={['#FF6B35', '#FF8835']} style={styles.eliteBtnGrad}>
                        <Ionicons name="flash" size={20} color="#FFFFFF" />
                      </LinearGradient>
                    </TouchableOpacity>
                 </View>
               </View>
            </View>
            <Animated.View style={[styles.swipeCatcher, { transform: [{ translateX: arrowTranslateX }], opacity: arrowOpacity }]}>
               <LinearGradient colors={['transparent', 'rgba(255, 107, 53, 0.1)']} start={{x:0,y:0}} end={{x:1,y:0}} style={styles.swipeTrail} />
               <Ionicons name="chevron-forward" size={24} color="#FF6B35" />
            </Animated.View>
          </Animated.View>

          {/* BACK */}
          <Animated.View style={[styles.card, styles.cardBack, { transform: [{ perspective: 1800 }, { rotateY: backInterpolate }, { scale: scaleAnim }], opacity: backOpacity }]}>
             <LinearGradient colors={['#FFFBEB', '#FFFFFF', '#FDF6E3']} style={StyleSheet.absoluteFill} />
             <View style={styles.content}>
               <View style={styles.mapHeader}>
                 <Text style={styles.adventureTitle}>QUÊTE DU RECRUTEMENT</Text>
                 <View style={styles.goldLine} />
               </View>
               <View style={styles.mapCanvas}>
                  <View style={styles.missionTrace} />
                  {pipeline.map((step, idx) => {
                    const isPast = currentIdx >= idx || (isRefused && idx < pipeline.length - 1);
                    const isCurrent = step.key === item.status;
                    return (
                      <View key={step.key} style={[styles.mapNode, { left: step.x, top: step.y }]}>
                        <View style={[styles.nodeShell, isPast && { borderColor: '#B8860B', backgroundColor: '#FFFFFF' }]}>
                          <Ionicons name={step.icon} size={18} color={isPast ? '#FF6B35' : 'rgba(0,0,0,0.1)'} />
                        </View>
                        {isCurrent && (
                          <Animated.View style={[styles.lockMarker, { transform: [{ scale: pulseAnim }] }]}>
                             <Ionicons name={isRefused ? "close-circle" : "close"} size={44} color={isRefused ? "#EF4444" : "#FF6B35"} />
                          </Animated.View>
                        )}
                        <Text style={[styles.nodeLabel, isCurrent && { color: '#FF6B35', fontWeight: '900' }]}>{step.label}</Text>
                      </View>
                    );
                  })}
               </View>
               <View style={styles.mapFooter}>
                 <TouchableOpacity style={styles.viewDossierBtn} onPress={() => setIsModalVisible(true)}>
                    <Text style={styles.viewDossierTxt}>VOIR LES DÉTAILS</Text>
                    <Ionicons name="document-text" size={16} color="#FF6B35" />
                 </TouchableOpacity>
               </View>
            </View>
          </Animated.View>
        </TouchableOpacity>

        {/* DETAIL POPUP MODAL (FIXED) */}
        <Modal
          visible={isModalVisible}
          transparent={true}
          animationType="slide"
          onRequestClose={() => setIsModalVisible(false)}
        >
          <View style={styles.modalOverlay}>
             <BlurView intensity={60} tint="dark" style={StyleSheet.absoluteFill} />
             <TouchableOpacity style={StyleSheet.absoluteFill} activeOpacity={1} onPress={() => setIsModalVisible(false)} />
             
             <View style={styles.modalContent}>
                <View style={styles.modalHeader}>
                   <View style={styles.modalBranding}>
                      <Image source={require('../../../assets/logosansfond.png')} style={styles.modalLogo} resizeMode="contain" />
                      <Text style={styles.modalBrandTxt}>GOLDARMY DOSSIER</Text>
                   </View>
                   <TouchableOpacity 
                     onPress={() => setIsModalVisible(false)} 
                     style={styles.closeBtn}
                     hitSlop={{ top: 20, bottom: 20, left: 20, right: 20 }}
                   >
                      <Ionicons name="close-circle" size={32} color="#1A1A1F" />
                   </TouchableOpacity>
                </View>

                <ScrollView showsVerticalScrollIndicator={false} contentContainerStyle={styles.modalScroll}>
                   <Text style={styles.modalJobTitle}>{item.title}</Text>
                   <Text style={styles.modalCompany}>{item.company}</Text>
                   
                   <View style={styles.modalMetaRow}>
                      <View style={styles.modalMetaItem}>
                         <Ionicons name="calendar-outline" size={16} color="#FF6B35" />
                         <Text style={styles.modalMetaTxt}>{item.date}</Text>
                      </View>
                      <View style={styles.modalMetaItem}>
                         <Ionicons name="ribbon-outline" size={16} color={meta.color} />
                         <Text style={[styles.modalMetaTxt, { color: meta.color }]}>{meta.label}</Text>
                      </View>
                   </View>

                   <View style={styles.modalSection}>
                      <Text style={styles.modalSectionTitle}>MISSION ET DESCRIPTION</Text>
                      <View style={styles.descriptionBox}>
                        <Text style={styles.modalPara}>{item.description || "Aucune description détaillée."}</Text>
                      </View>
                   </View>

                   {item.notes && (
                     <View style={styles.modalSection}>
                        <Text style={styles.modalSectionTitle}>NOTES STRATÉGIQUES</Text>
                        <View style={styles.notesBox}>
                          <Text style={styles.modalPara}>{item.notes}</Text>
                        </View>
                     </View>
                   )}

                   <TouchableOpacity style={styles.fullActionBtn} onPress={onPressOpen}>
                      <LinearGradient colors={['#FF6B35', '#F59E0B']} style={styles.fullActionGrad}>
                         <Text style={styles.fullActionTxt}>ACCÉDER À L'ORIGINAL</Text>
                         <Ionicons name="arrow-redo-outline" size={20} color="#FFFFFF" />
                      </LinearGradient>
                   </TouchableOpacity>
                   
                   {/* Bottom Close for ease of use */}
                   <TouchableOpacity style={styles.bottomClose} onPress={() => setIsModalVisible(false)}>
                      <Text style={styles.bottomCloseTxt}>FERMER LE DOSSIER</Text>
                   </TouchableOpacity>
                </ScrollView>
             </View>
          </View>
        </Modal>
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
    minHeight: 280,
    overflow: 'hidden',
    backfaceVisibility: 'hidden',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 12 },
    shadowOpacity: 0.1,
    shadowRadius: 20,
    elevation: 8,
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
  brandingBox: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#F5F4F0',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 12,
  },
  appMiniLogo: {
    width: 18,
    height: 18,
    marginRight: 6,
  },
  brandTitle: {
    fontSize: 9,
    fontWeight: '900',
    color: '#D4AF37',
    letterSpacing: 2,
  },
  pillBadge: {
    borderRadius: 10,
    overflow: 'hidden',
  },
  pillBadgeBg: {
    paddingHorizontal: 10,
    paddingVertical: 4,
  },
  pillBadgeTxt: {
    fontSize: 8,
    fontWeight: '900',
    color: '#FFFFFF',
    letterSpacing: 1,
  },
  infoArea: {
    marginTop: 10,
  },
  companySubHeader: {
    fontSize: 12,
    fontWeight: '800',
    color: '#9A9A94',
    letterSpacing: 3,
    marginBottom: 6,
  },
  jobHeadingTxt: {
    fontSize: 20,
    fontWeight: '900',
    color: '#1A1A1F',
    letterSpacing: -0.5,
    lineHeight: 26,
    marginBottom: 10,
  },
  metaRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  metaBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFFBEB',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: 'rgba(212, 175, 55, 0.1)',
  },
  metaTxt: {
    fontSize: 11,
    fontWeight: '700',
    color: '#D4AF37',
    marginLeft: 6,
  },
  footerRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingTop: 10,
  },
  hologramSeal: {
    alignItems: 'center',
    justifyContent: 'center',
  },
  sealCircle: {
    width: 52,
    height: 52,
    borderRadius: 18,
    alignItems: 'center',
    justifyContent: 'center',
    shadowColor: '#F5D061',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.2,
    shadowRadius: 8,
  },
  sealChar: {
    fontSize: 24,
    fontWeight: '900',
    color: '#0A0A0F',
  },
  frontActions: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  iconicBtn: {
    borderRadius: 16,
    overflow: 'hidden',
    marginRight: 12,
    borderWidth: 1,
    borderColor: '#E2E0DA',
  },
  iconicBtnGrad: {
    width: 52,
    height: 52,
    alignItems: 'center',
    justifyContent: 'center',
  },
  eliteStatusBtn: {
    borderRadius: 16,
    overflow: 'hidden',
    shadowColor: '#FF6B35',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 10,
    elevation: 4,
  },
  eliteBtnGrad: {
    width: 52,
    height: 52,
    alignItems: 'center',
    justifyContent: 'center',
  },
  swipeCatcher: {
    position: 'absolute',
    right: 0,
    top: '45%',
    flexDirection: 'row',
    alignItems: 'center',
    paddingRight: 10,
  },
  swipeTrail: {
    width: 40,
    height: 30,
    marginRight: -10,
  },
  mapHeader: {
    alignItems: 'center',
  },
  adventureTitle: {
    fontSize: 10,
    fontWeight: '900',
    color: '#B8860B',
    letterSpacing: 3,
    marginBottom: 8,
  },
  goldLine: {
    width: 40,
    height: 2,
    backgroundColor: '#FF6B35',
    borderRadius: 1,
    opacity: 0.3,
  },
  mapCanvas: {
    height: 160,
    position: 'relative',
    marginVertical: 5,
  },
  missionTrace: {
    position: 'absolute',
    left: '15%',
    right: '25%',
    top: 20,
    bottom: 20,
    borderWidth: 2,
    borderColor: 'rgba(184, 134, 11, 0.1)',
    borderStyle: 'dotted',
    borderRadius: 100,
    transform: [{ rotate: '12deg' }],
  },
  mapNode: {
    position: 'absolute',
    alignItems: 'center',
    zIndex: 10,
  },
  nodeShell: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: '#F9F7F0',
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 1.5,
    borderColor: '#E2E0DA',
  },
  nodeLabel: {
    fontSize: 9,
    fontWeight: '800',
    color: '#9A9A94',
    marginTop: 6,
    letterSpacing: 1,
  },
  lockMarker: {
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
  viewDossierBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#FFFBEB',
    paddingVertical: 12,
    borderRadius: 12,
  },
  viewDossierTxt: {
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
  modalOverlay: {
    flex: 1,
    justifyContent: 'flex-end',
    backgroundColor: 'rgba(0,0,0,0.5)',
  },
  modalContent: {
    backgroundColor: '#FFFFFF',
    borderTopLeftRadius: 36,
    borderTopRightRadius: 36,
    minHeight: '80%', // INCREASED FOR MORE VISIBILITY
    marginTop: 60, // SAFE AREA MARGIN
    marginHorizontal: 10, // KEEP AWAY FROM EDGES
    padding: 24,
    paddingTop: 30,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: -10 },
    shadowOpacity: 0.15,
    shadowRadius: 25,
    elevation: 20,
    flex: 1,
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 20,
    paddingHorizontal: 4,
  },
  modalBranding: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  modalLogo: {
    width: 24,
    height: 24,
    marginRight: 10,
  },
  modalBrandTxt: {
    fontSize: 11,
    fontWeight: '900',
    color: '#D4AF37',
    letterSpacing: 2,
  },
  closeBtn: {
    padding: 8,
    backgroundColor: '#F5F4F0',
    borderRadius: 20,
  },
  modalScroll: {
    paddingBottom: 60,
    paddingHorizontal: 4,
  },
  modalJobTitle: {
    fontSize: 26,
    fontWeight: '900',
    color: '#1A1A1F',
    letterSpacing: -0.8,
    lineHeight: 32,
    marginBottom: 6,
  },
  modalCompany: {
    fontSize: 16,
    fontWeight: '800',
    color: '#FF6B35',
    marginBottom: 16,
    letterSpacing: 1,
  },
  modalMetaRow: {
    flexDirection: 'row',
    marginBottom: 24,
    flexWrap: 'wrap',
  },
  modalMetaItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginRight: 12,
    marginBottom: 8,
    backgroundColor: '#F5F4F0',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 10,
  },
  modalMetaTxt: {
    fontSize: 12,
    fontWeight: '700',
    color: '#4A4A46',
    marginLeft: 8,
  },
  modalSection: {
    marginBottom: 20,
  },
  modalSectionTitle: {
    fontSize: 10,
    fontWeight: '900',
    color: '#AAA9A4',
    letterSpacing: 2,
    marginBottom: 10,
  },
  descriptionBox: {
    backgroundColor: '#FAFAFA',
    padding: 16,
    borderRadius: 16,
    borderWidth: 1,
    borderColor: '#F0F0F0',
  },
  notesBox: {
    backgroundColor: '#FFFBEB',
    padding: 16,
    borderRadius: 16,
    borderWidth: 1,
    borderColor: '#FEF3C7',
  },
  modalPara: {
    fontSize: 14,
    color: '#4A4A46',
    lineHeight: 22,
    fontWeight: '500',
  },
  fullActionBtn: {
    marginTop: 10,
    borderRadius: 16,
    overflow: 'hidden',
    shadowColor: '#FF6B35',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.2,
    shadowRadius: 8,
    elevation: 4,
  },
  fullActionGrad: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 16,
  },
  fullActionTxt: {
    fontSize: 12,
    fontWeight: '900',
    color: '#FFFFFF',
    marginRight: 12,
    letterSpacing: 1,
  },
  bottomClose: {
    marginTop: 25,
    alignItems: 'center',
    paddingVertical: 12,
  },
  bottomCloseTxt: {
    fontSize: 11,
    fontWeight: '800',
    color: '#AAA9A4',
    letterSpacing: 2,
    textDecorationLine: 'underline',
  },
});
