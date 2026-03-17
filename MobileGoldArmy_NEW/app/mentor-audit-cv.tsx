import React, { useState, useRef, useEffect } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, Animated, KeyboardAvoidingView, Platform, ActivityIndicator } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { StatusBar } from 'expo-status-bar';
import { Ionicons } from '@expo/vector-icons';
import { useRouter } from 'expo-router';
import { spacing } from '../src/theme/spacing';
import { mentorService } from '../src/services/mentorService';
import { cvService, CvUploadError } from '../src/services/cvService';
import { useUIStore } from '../src/stores/uiStore';
import * as Haptics from 'expo-haptics';

type CvSource = 'profile' | 'upload';

export default function MentorAuditCvScreen() {
  const insets = useSafeAreaInsets();
  const router = useRouter();
  const [cvSource, setCvSource] = useState<CvSource | null>(null);
  const [cvFileName, setCvFileName] = useState<string | null>(null);
  const [cvText, setCvText] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [auditSummary, setAuditSummary] = useState<string | null>(null);
  const [rewriteContent, setRewriteContent] = useState<string | null>(null);
  const { showToast } = useUIStore();
  const [loadingStep, setLoadingStep] = useState(0);
  const loadingIntervalRef = useRef<NodeJS.Timeout | null>(null);

  const LOADING_STEPS = [
    '1/4 – Préparation du CV…',
    '2/4 – Lecture détaillée des expériences…',
    '3/4 – Analyse des mots-clés ATS…',
    '4/4 – Génération des recommandations…',
  ];

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
    const loadProfileCv = async () => {
      try {
        setIsLoading(true);
        await Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
        const res = await mentorService.getProfileCv();
        if (res.cv_text) {
          setCvSource('profile');
          setCvFileName('CV du profil');
          setCvText(res.cv_text);
          showToast('CV du profil chargé', 'success');
          closeOverlay();
        } else {
          showToast('Aucun CV enregistré dans ton profil.', 'warning');
        }
      } catch (error) {
        console.error('[Mentor][Profile CV]', error);
        showToast('Impossible de charger le CV du profil.', 'error');
      } finally {
        setIsLoading(false);
      }
    };
    void loadProfileCv();
  };

  const handleChooseNewCv = () => {
    const pickNewCv = async () => {
      try {
        setIsLoading(true);
        await Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
        const result = await cvService.pickAndUploadCv();
        setCvSource('upload');
        setCvFileName(result.filename);
        setCvText(result.text);
        showToast('CV importé avec succès', 'success');
        closeOverlay();
      } catch (error: any) {
        console.error('[Mentor][Upload CV]', error);
        if (error instanceof CvUploadError) {
          if (error.code === 'CANCELLED') {
            return;
          }
          showToast(error.message, 'error');
        } else {
          showToast("Erreur lors de l'import du CV.", 'error');
        }
      } finally {
        setIsLoading(false);
      }
    };
    void pickNewCv();
  };

  const handleRunAudit = async () => {
    if (!cvText || !cvFileName) {
      showToast('Sélectionne d’abord un CV à auditer.', 'warning');
      return;
    }

    try {
      setIsLoading(true);
      setAuditSummary(null);
      setRewriteContent(null);
      await Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
      setLoadingStep(0);
      if (loadingIntervalRef.current) {
        clearInterval(loadingIntervalRef.current);
      }
      loadingIntervalRef.current = setInterval(() => {
        setLoadingStep((prev) => (prev < LOADING_STEPS.length - 1 ? prev + 1 : prev));
      }, 2500);

      const message =
        "Audite mon CV en profondeur (structure, clarté, mots-clés, ATS) et propose une version réécrite optimisée.";

      const response = await mentorService.auditCv({
        message,
        cv_text: cvText,
        cv_filename: cvFileName,
      });

      setAuditSummary(response.audit || response.content || null);
      if (response.type === 'cv_audit_rewrite' || response.type === 'cv_rewrite') {
        setRewriteContent(response.content || null);
      }
      showToast('Audit de CV terminé ✅', 'success');
    } catch (error) {
      console.error('[Mentor][Audit CV]', error);
      showToast("Erreur lors de l'audit du CV.", 'error');
    } finally {
      setIsLoading(false);
      if (loadingIntervalRef.current) {
        clearInterval(loadingIntervalRef.current);
        loadingIntervalRef.current = null;
      }
    }
  };

  // Essaie de parser l'audit JSON pour un rendu plus riche
  const parsedAudit = React.useMemo(() => {
    if (!auditSummary) return null;
    try {
      const parsed = JSON.parse(auditSummary);
      return typeof parsed === 'object' && parsed !== null ? parsed : null;
    } catch {
      return null;
    }
  }, [auditSummary]);

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
            {isLoading && !auditSummary ? (
              <View style={{ flexDirection: 'row', alignItems: 'center', marginTop: spacing.sm }}>
                <ActivityIndicator size="small" color="#1A1A1A" style={{ marginRight: spacing.sm }} />
                <Text style={styles.sectionBody}>{LOADING_STEPS[loadingStep]}</Text>
              </View>
            ) : parsedAudit ? (
              <>
                {/* Score principal ATS */}
                <View style={styles.scoreRow}>
                  <View style={styles.scoreCircle}>
                    <Text style={styles.scoreValue}>
                      {typeof parsedAudit.ats_score === 'number'
                        ? `${Math.round(parsedAudit.ats_score)}%`
                        : '--%'}
                    </Text>
                    <Text style={styles.scoreLabel}>Score ATS</Text>
                  </View>
                  <View style={styles.scoreInfo}>
                    {parsedAudit.candidate_name && (
                      <Text style={styles.scoreName}>{parsedAudit.candidate_name}</Text>
                    )}
                    {parsedAudit.candidate_title && (
                      <Text style={styles.scoreTitle}>{parsedAudit.candidate_title}</Text>
                    )}
                    {typeof parsedAudit.original_ats_score === 'number' && (
                      <Text style={styles.scoreDelta}>
                        Avant : {Math.round(parsedAudit.original_ats_score)}% • Après :{' '}
                        {typeof parsedAudit.ats_score === 'number'
                          ? `${Math.round(parsedAudit.ats_score)}%`
                          : '--%'}
                      </Text>
                    )}
                  </View>
                </View>

                {/* Sous-scores éventuels */}
                {parsedAudit.scores && typeof parsedAudit.scores === 'object' && (
                  <View style={styles.subScoresRow}>
                    {Object.entries(parsedAudit.scores as Record<string, number>).map(
                      ([key, value]) => (
                        <View key={key} style={styles.subScoreCard}>
                          <Text style={styles.subScoreLabel}>{key}</Text>
                          <Text style={styles.subScoreValue}>{Math.round(value)}%</Text>
                        </View>
                      )
                    )}
                  </View>
                )}

                {/* Technologies ajoutées */}
                {Array.isArray(parsedAudit.tech_ajoutees) && parsedAudit.tech_ajoutees.length > 0 && (
                  <View style={styles.techSection}>
                    <Text style={styles.techTitle}>Technologies mises en avant</Text>
                    <View style={styles.techChipsRow}>
                      {parsedAudit.tech_ajoutees.map((t: string) => (
                        <View key={t} style={styles.techChip}>
                          <Ionicons
                            name="sparkles-outline"
                            size={12}
                            color="#1D4ED8"
                            style={{ marginRight: 4 }}
                          />
                          <Text style={styles.techChipText}>{t}</Text>
                        </View>
                      ))}
                    </View>
                  </View>
                )}
              </>
            ) : auditSummary ? (
              <Text style={styles.sectionBody}>{auditSummary}</Text>
            ) : (
              <Text style={styles.sectionBody}>
                Lorsque ton CV sera analysé par le backend, cette section affichera un résumé clair des
                forces, des faiblesses et des recommandations prioritaires.
              </Text>
            )}
          </View>

          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Forces détectées</Text>
            <View style={styles.chipRow}>
              <View style={styles.chip}>
                <Ionicons name="checkmark-circle" size={14} color="#16A34A" style={{ marginRight: 6 }} />
                <Text style={styles.chipText}>
                  {cvSource === 'profile' ? 'CV lié à ton profil chargé' : 'CV PDF importé analysé'}
                </Text>
              </View>
              {rewriteContent && (
                <View style={styles.chip}>
                  <Ionicons name="sparkles-outline" size={14} color="#2563EB" style={{ marginRight: 6 }} />
                  <Text style={styles.chipText}>Version optimisée générée</Text>
                </View>
              )}
            </View>
          </View>

          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Points à corriger</Text>
            {parsedAudit && (parsedAudit.failles || parsedAudit.mot_cles_manquants || parsedAudit.correction_mapping) ? (
              <>
                {/* Failles principales */}
                {Array.isArray(parsedAudit.failles) && parsedAudit.failles.length > 0 && (
                  <View style={{ marginBottom: spacing.md }}>
                    <Text style={styles.subSectionTitle}>Faiblesses détectées</Text>
                    {parsedAudit.failles.map((f: string, idx: number) => (
                      <View key={`faille-${idx}`} style={styles.todoItem}>
                        <View style={styles.todoBullet} />
                        <Text style={styles.todoText}>{f}</Text>
                      </View>
                    ))}
                  </View>
                )}

                {/* Mots-clés manquants */}
                {Array.isArray(parsedAudit.mot_cles_manquants) &&
                  parsedAudit.mot_cles_manquants.length > 0 && (
                    <View style={{ marginBottom: spacing.md }}>
                      <Text style={styles.subSectionTitle}>Mots-clés manquants</Text>
                      <View style={styles.keywordsRow}>
                        {parsedAudit.mot_cles_manquants.map((k: string) => (
                          <View key={k} style={styles.keywordChip}>
                            <Text style={styles.keywordChipText}>{k}</Text>
                          </View>
                        ))}
                      </View>
                    </View>
                  )}

                {/* Corrections suggérées */}
                {parsedAudit.correction_mapping &&
                  typeof parsedAudit.correction_mapping === 'object' && (
                    <View>
                      <Text style={styles.subSectionTitle}>Suggestions de reformulation</Text>
                      {Object.entries(
                        parsedAudit.correction_mapping as Record<string, string>
                      ).map(([from, to]) => (
                        <View key={from} style={styles.correctionCard}>
                          <Text style={styles.correctionLabel}>Avant</Text>
                          <Text style={styles.correctionTextOriginal}>{from}</Text>
                          <Text style={styles.correctionLabel}>Après</Text>
                          <Text style={styles.correctionTextNew}>{to}</Text>
                        </View>
                      ))}
                    </View>
                  )}

                {/* Optionnel : bloc texte réécrit complet */}
                {rewriteContent && (
                  <View style={{ marginTop: spacing.lg }}>
                    <Text style={styles.subSectionTitle}>Version réécrite proposée</Text>
                    <Text style={styles.sectionBody}>{rewriteContent}</Text>
                  </View>
                )}
              </>
            ) : rewriteContent ? (
              <Text style={styles.sectionBody}>{rewriteContent}</Text>
            ) : (
              <>
                <View style={styles.todoItem}>
                  <View style={styles.todoBullet} />
                  <Text style={styles.todoText}>
                    Ajoute plus de résultats chiffrés dans tes expériences récentes (ex : +35 % de leads, -20 % de
                    bugs…).
                  </Text>
                </View>
                <View style={styles.todoItem}>
                  <View style={styles.todoBullet} />
                  <Text style={styles.todoText}>
                    Réduis les paragraphes longs en listes à puces plus lisibles pour les recruteurs.
                  </Text>
                </View>
              </>
            )}
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
        <View style={styles.footerActions}>
          <TouchableOpacity
            style={[styles.runAuditButton, (!cvText || isLoading) && styles.runAuditButtonDisabled]}
            activeOpacity={0.9}
            disabled={!cvText || isLoading}
            onPress={handleRunAudit}
          >
            {isLoading ? (
              <ActivityIndicator size="small" color="#FFFFFF" style={{ marginRight: 8 }} />
            ) : (
              <Ionicons name="sparkles-outline" size={18} color="#FFFFFF" style={{ marginRight: 8 }} />
            )}
            <Text style={styles.runAuditButtonText}>
              {isLoading ? 'Analyse en cours…' : 'Lancer l’audit de mon CV'}
            </Text>
          </TouchableOpacity>
        </View>
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
  scoreRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: spacing.sm,
    marginBottom: spacing.md,
  },
  scoreCircle: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: '#FFF0EB',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: spacing.lg,
  },
  scoreValue: {
    fontSize: 22,
    fontWeight: '800',
    color: '#FF6B35',
  },
  scoreLabel: {
    fontSize: 11,
    color: '#9A9A94',
  },
  scoreInfo: {
    flex: 1,
  },
  scoreName: {
    fontSize: 15,
    fontWeight: '700',
    color: '#1A1A1A',
  },
  scoreTitle: {
    fontSize: 13,
    color: '#4A4A46',
    marginTop: 2,
  },
  scoreDelta: {
    fontSize: 11,
    color: '#16A34A',
    marginTop: 6,
  },
  subScoresRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.sm,
    marginTop: spacing.sm,
  },
  subScoreCard: {
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    borderRadius: 999,
    backgroundColor: '#F5F4F0',
  },
  subScoreLabel: {
    fontSize: 11,
    color: '#4A4A46',
  },
  subScoreValue: {
    fontSize: 13,
    fontWeight: '700',
    color: '#1A1A1A',
  },
  techSection: {
    marginTop: spacing.md,
  },
  techTitle: {
    fontSize: 13,
    fontWeight: '600',
    color: '#1A1A1A',
    marginBottom: spacing.xs,
  },
  techChipsRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.xs,
  },
  techChip: {
    flexDirection: 'row',
    alignItems: 'center',
    borderRadius: 999,
    backgroundColor: '#EFF6FF',
    paddingHorizontal: spacing.sm,
    paddingVertical: 4,
  },
  techChipText: {
    fontSize: 11,
    color: '#1D4ED8',
    fontWeight: '500',
  },
  subSectionTitle: {
    fontSize: 13,
    fontWeight: '600',
    color: '#1A1A1A',
    marginBottom: spacing.xs,
  },
  keywordsRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.xs,
  },
  keywordChip: {
    borderRadius: 999,
    borderWidth: 1,
    borderColor: '#FFE0D1',
    paddingHorizontal: spacing.sm,
    paddingVertical: 4,
    backgroundColor: '#FFF7ED',
  },
  keywordChipText: {
    fontSize: 11,
    color: '#9A3412',
    fontWeight: '500',
  },
  correctionCard: {
    marginTop: spacing.sm,
    padding: spacing.md,
    borderRadius: 12,
    backgroundColor: '#F9FAFB',
    borderWidth: 1,
    borderColor: '#E5E7EB',
  },
  correctionLabel: {
    fontSize: 11,
    fontWeight: '600',
    color: '#6B7280',
    marginTop: 2,
  },
  correctionTextOriginal: {
    fontSize: 12,
    color: '#9A9A94',
    marginTop: 2,
  },
  correctionTextNew: {
    fontSize: 12,
    color: '#111827',
    marginTop: 2,
    fontWeight: '600',
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
  footerActions: {
    position: 'absolute',
    left: spacing.xl,
    right: spacing.xl,
    bottom: spacing.xl,
  },
  runAuditButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#111827',
    borderRadius: 999,
    paddingVertical: 14,
    shadowColor: '#111827',
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.25,
    shadowRadius: 16,
    elevation: 4,
  },
  runAuditButtonDisabled: {
    opacity: 0.5,
  },
  runAuditButtonText: {
    fontSize: 15,
    fontWeight: '700',
    color: '#FFFFFF',
  },
});

