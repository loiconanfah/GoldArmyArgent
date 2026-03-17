import React, { useState, useRef, useEffect } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, Animated, KeyboardAvoidingView, Platform } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { StatusBar } from 'expo-status-bar';
import { Ionicons } from '@expo/vector-icons';
import { useRouter } from 'expo-router';
import { spacing } from '../src/theme/spacing';

type CvSource = 'profile' | 'upload';

export default function MentorAuditCvScreen() {
  const insets = useSafeAreaInsets();
  const router = useRouter();
  const [cvSource, setCvSource] = useState<CvSource | null>(null);
  const [cvFileName, setCvFileName] = useState<string | null>(null);

  const overlayAnim = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    Animated.timing(overlayAnim, {
      toValue: 1,
      duration: 250,
      useNativeDriver: true,
    }).start();
  }, [overlayAnim]);

  const closeOverlay = () => {
    Animated.timing(overlayAnim, {
      toValue: 0,
      duration: 200,
      useNativeDriver: true,
    }).start();
  };

  const handleChooseProfileCv = () => {
    setCvSource('profile');
    setCvFileName('CV du profil');
    closeOverlay();
  };

  const handleChooseNewCv = () => {
    setCvSource('upload');
    setCvFileName('nouveau_cv.pdf');
    closeOverlay();
  };

  return (
    <KeyboardAvoidingView
      style={styles.root}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
    >
      <StatusBar style="dark" />
      <View style={[styles.container, { paddingTop: insets.top, paddingBottom: insets.bottom + 80 }]}>
        {/* HEADER */}
        <View style={styles.header}>
          <TouchableOpacity style={styles.backButton} onPress={() => router.back()}>
            <Ionicons name="chevron-back" size={22} color="#1A1A1A" />
          </TouchableOpacity>
          <View style={styles.headerText}>
            <Text style={styles.headerTitle}>Audit de CV</Text>
            <Text style={styles.headerSubtitle}>Prépare ton CV pour passer les filtres ATS.</Text>
          </View>
        </View>

        {/* SELECTED CV SUMMARY */}
        {cvSource && (
          <View style={styles.cvSummary}>
            <View style={styles.cvSummaryLeft}>
              <View style={styles.cvSummaryIcon}>
                <Ionicons name="document-text-outline" size={20} color="#1A1A1A" />
              </View>
              <View style={styles.cvSummaryInfo}>
                <Text style={styles.cvSummaryLabel}>
                  {cvSource === 'profile' ? 'CV du profil Yayzoy' : 'CV importé'}
                </Text>
                <Text style={styles.cvSummaryFile}>{cvFileName}</Text>
              </View>
            </View>
            <TouchableOpacity
              style={styles.cvChangeButton}
              onPress={() => {
                overlayAnim.setValue(0);
                setCvSource(null);
                setCvFileName(null);
                Animated.timing(overlayAnim, {
                  toValue: 1,
                  duration: 250,
                  useNativeDriver: true,
                }).start();
              }}
            >
              <Text style={styles.cvChangeText}>Changer</Text>
            </TouchableOpacity>
          </View>
        )}

        {/* MAIN CONTENT */}
        <ScrollView
          style={styles.scroll}
          contentContainerStyle={styles.scrollContent}
          showsVerticalScrollIndicator={false}
        >
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Résumé de l’audit</Text>
            <Text style={styles.sectionBody}>
              Lorsque ton CV sera analysé par le backend, cette section affichera un résumé clair des
              forces, des faiblesses et des recommandations prioritaires. Pour l’instant, elle est prête
              à recevoir les données de l’API.
            </Text>
          </View>

          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Forces détectées</Text>
            <View style={styles.chipRow}>
              <View style={styles.chip}>
                <Ionicons name="checkmark-circle" size={14} color="#16A34A" style={{ marginRight: 6 }} />
                <Text style={styles.chipText}>Expérience cohérente</Text>
              </View>
              <View style={styles.chip}>
                <Ionicons name="checkmark-circle" size={14} color="#16A34A" style={{ marginRight: 6 }} />
                <Text style={styles.chipText}>Mots-clés présents</Text>
              </View>
            </View>
          </View>

          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Points à corriger</Text>
            <View style={styles.todoItem}>
              <View style={styles.todoBullet} />
              <Text style={styles.todoText}>Ajouter plus de résultats chiffrés dans les expériences récentes.</Text>
            </View>
            <View style={styles.todoItem}>
              <View style={styles.todoBullet} />
              <Text style={styles.todoText}>Réduire les paragraphes longs en listes à puces plus lisibles.</Text>
            </View>
          </View>
        </ScrollView>

        {/* OVERLAY DE CHOIX DE CV */}
        {cvSource === null && (
          <Animated.View
            pointerEvents="auto"
            style={[
              styles.overlay,
              {
                opacity: overlayAnim,
                transform: [
                  {
                    translateY: overlayAnim.interpolate({
                      inputRange: [0, 1],
                      outputRange: [40, 0],
                    }),
                  },
                ],
              },
            ]}
          >
            <View style={styles.overlayBackdrop} />
            <View style={styles.overlayCard}>
              <View style={styles.overlayHeader}>
                <View style={styles.overlayIcon}>
                  <Ionicons name="document-text-outline" size={22} color="#1A1A1A" />
                </View>
                <View style={styles.overlayHeaderText}>
                  <Text style={styles.overlayTitle}>Quel CV utiliser ?</Text>
                  <Text style={styles.overlaySubtitle}>
                    Choisis le CV à analyser. Tu pourras ensuite lancer l’audit détaillé côté backend.
                  </Text>
                </View>
              </View>

              <TouchableOpacity
                style={styles.choiceCard}
                activeOpacity={0.9}
                onPress={handleChooseProfileCv}
              >
                <View style={styles.choiceLeft}>
                  <Ionicons name="person-circle-outline" size={22} color="#1A1A1A" style={{ marginRight: 10 }} />
                  <View>
                    <Text style={styles.choiceTitle}>CV du profil</Text>
                    <Text style={styles.choiceSubtitle}>Utiliser le CV déjà associé à ton compte.</Text>
                  </View>
                </View>
                <Ionicons name="chevron-forward" size={18} color="#A1A1AA" />
              </TouchableOpacity>

              <TouchableOpacity
                style={styles.choiceCard}
                activeOpacity={0.9}
                onPress={handleChooseNewCv}
              >
                <View style={styles.choiceLeft}>
                  <Ionicons name="cloud-upload-outline" size={22} color="#1A1A1A" style={{ marginRight: 10 }} />
                  <View>
                    <Text style={styles.choiceTitle}>Importer un nouveau CV</Text>
                    <Text style={styles.choiceSubtitle}>Uploader un PDF différent juste pour cet audit.</Text>
                  </View>
                </View>
                <Ionicons name="chevron-forward" size={18} color="#A1A1AA" />
              </TouchableOpacity>
            </View>
          </Animated.View>
        )}
      </View>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  root: {
    flex: 1,
    backgroundColor: '#FAFAF8',
  },
  container: {
    flex: 1,
    paddingHorizontal: spacing.xl,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: spacing.lg,
    marginBottom: spacing.lg,
  },
  backButton: {
    width: 36,
    height: 36,
    borderRadius: 18,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    borderWidth: 1,
    borderColor: '#EAEAE6',
    marginRight: spacing.md,
  },
  headerText: {
    flex: 1,
  },
  headerTitle: {
    fontSize: 20,
    fontWeight: '800',
    color: '#1A1A1A',
  },
  headerSubtitle: {
    fontSize: 13,
    color: '#666666',
    marginTop: 2,
  },
  cvSummary: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
    borderWidth: 1,
    borderColor: '#EAEAE6',
    marginBottom: spacing.lg,
  },
  cvSummaryLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
    marginRight: spacing.md,
  },
  cvSummaryIcon: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: '#F5F5F3',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: spacing.md,
  },
  cvSummaryInfo: {
    flex: 1,
  },
  cvSummaryLabel: {
    fontSize: 13,
    fontWeight: '600',
    color: '#1A1A1A',
    marginBottom: 2,
  },
  cvSummaryFile: {
    fontSize: 12,
    color: '#666666',
  },
  cvChangeButton: {
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    borderRadius: 999,
    borderWidth: 1,
    borderColor: '#EAEAE6',
  },
  cvChangeText: {
    fontSize: 12,
    fontWeight: '600',
    color: '#1A1A1A',
  },
  scroll: {
    flex: 1,
  },
  scrollContent: {
    paddingBottom: spacing['2xl'],
    gap: spacing.xl,
  },
  section: {
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    padding: spacing.lg,
    borderWidth: 1,
    borderColor: '#EAEAE6',
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '700',
    color: '#1A1A1A',
    marginBottom: spacing.sm,
  },
  sectionBody: {
    fontSize: 13,
    color: '#666666',
    lineHeight: 18,
  },
  chipRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.sm,
  },
  chip: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#ECFDF5',
    borderRadius: 999,
    paddingHorizontal: spacing.md,
    paddingVertical: 6,
  },
  chipText: {
    fontSize: 12,
    fontWeight: '600',
    color: '#047857',
  },
  todoItem: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: spacing.xs,
  },
  todoBullet: {
    width: 4,
    height: 4,
    borderRadius: 2,
    backgroundColor: '#F5D061',
    marginTop: 7,
    marginRight: spacing.sm,
  },
  todoText: {
    fontSize: 13,
    color: '#666666',
    flex: 1,
  },
  overlay: {
    ...StyleSheet.absoluteFillObject,
    justifyContent: 'center',
    alignItems: 'center',
  },
  overlayBackdrop: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: 'rgba(0,0,0,0.15)',
  },
  overlayCard: {
    width: '88%',
    backgroundColor: '#FFFFFF',
    borderRadius: 20,
    padding: spacing.xl,
    borderWidth: 1,
    borderColor: '#EAEAE6',
  },
  overlayHeader: {
    flexDirection: 'row',
    marginBottom: spacing.lg,
  },
  overlayIcon: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#F5F5F3',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: spacing.md,
  },
  overlayHeaderText: {
    flex: 1,
  },
  overlayTitle: {
    fontSize: 17,
    fontWeight: '700',
    color: '#1A1A1A',
    marginBottom: 4,
  },
  overlaySubtitle: {
    fontSize: 13,
    color: '#666666',
  },
  choiceCard: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingVertical: spacing.md,
    borderTopWidth: StyleSheet.hairlineWidth,
    borderTopColor: '#EAEAE6',
  },
  choiceLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  choiceTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#1A1A1A',
  },
  choiceSubtitle: {
    fontSize: 12,
    color: '#666666',
    marginTop: 2,
  },
});

