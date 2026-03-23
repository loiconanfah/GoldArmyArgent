import React, { useState, useRef, useEffect } from 'react';
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  Animated,
  KeyboardAvoidingView,
  Platform,
  ActivityIndicator,
} from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { StatusBar } from 'expo-status-bar';
import { Ionicons } from '@expo/vector-icons';
import { useRouter } from 'expo-router';
import { spacing } from '../../src/theme/spacing';
import { mentorAuditCvStyles as styles } from './_styles/mentor-audit-cv.styles';
import { mentorService } from '../../src/services/mentorService';
import { cvService, CvUploadError } from '../../src/services/cvService';
import { useUIStore } from '../../src/stores/uiStore';
import * as Haptics from 'expo-haptics';
import * as Print from 'expo-print';
import * as Sharing from 'expo-sharing';
import { CV_TEMPLATES } from '../../src/utils/cvTemplates';

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
  const [selectedTemplateId, setSelectedTemplateId] = useState<string>(CV_TEMPLATES[0].id);
  const { showToast } = useUIStore();
  const [loadingStep, setLoadingStep] = useState(0);
  const [loadingProgress, setLoadingProgress] = useState(0);
  const loadingIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

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

  useEffect(() => {
    let interval: ReturnType<typeof setInterval>;
    if (isLoading && loadingStep === 3) {
      interval = setInterval(() => {
        setLoadingProgress((prev) => (prev < 99 ? prev + 1 : prev));
      }, 200);
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [isLoading, loadingStep]);

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
      showToast(`Sélectionne d'abord un CV à auditer.`, 'warning');
      return;
    }

    try {
      setIsLoading(true);
      setAuditSummary(null);
      setRewriteContent(null);
      await Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
      setLoadingStep(0);
      setLoadingProgress(0);
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
        background: true
      });

      if ((response as any).status === 'pending') {
        showToast("Audit lancé en arrière-plan 🚀. Tu recevras une notification dès qu'il sera prêt !", "success", 5000);
        // On peut soit rester sur la page, soit quitter. L'utilisateur voulait que ça continue.
        // On laisse isLoading à false pour que l'utilisateur puisse continuer à naviguer.
        setIsLoading(false);
        return;
      }

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

  // ── parsedAudit must be defined before handleExportPdf so it's available in scope ──
  const parsedAudit = React.useMemo(() => {
    if (!auditSummary) return null;
    try {
      const parsed = JSON.parse(auditSummary);
      return typeof parsed === 'object' && parsed !== null ? parsed : null;
    } catch {
      return null;
    }
  }, [auditSummary]);

  const handleExportPdf = async () => {
    if (!rewriteContent) {
      showToast('Aucune version réécrite disponible pour générer le PDF.', 'warning');
      return;
    }
    try {
      await Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
      let cvData: any = {};
      try { cvData = JSON.parse(rewriteContent); } catch { cvData = { summary: rewriteContent }; }

      const template = CV_TEMPLATES.find(t => t.id === selectedTemplateId) ?? CV_TEMPLATES[0];
      const html = template.build(cvData, parsedAudit);

      const { uri } = await Print.printToFileAsync({ html, base64: false });
      const canShare = await Sharing.isAvailableAsync();
      if (canShare) {
        await Sharing.shareAsync(uri, { mimeType: 'application/pdf', dialogTitle: `CV — ${template.label}` });
      } else {
        showToast('Partage non disponible sur cet appareil.', 'warning');
      }
    } catch (error) {
      console.error('[Mentor][Export PDF]', error);
      showToast('Erreur lors de la génération du PDF.', 'error');
    }
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
            <Text style={styles.sectionTitle}>Résumé de l'audit</Text>
            {isLoading && !auditSummary ? (
              <View style={{ marginTop: spacing.sm }}>
                <View style={{ flexDirection: 'row', alignItems: 'center' }}>
                  <ActivityIndicator size="small" color="#1A1A1A" style={{ marginRight: spacing.sm }} />
                  <Text style={styles.sectionBody}>{LOADING_STEPS[loadingStep]}</Text>
                </View>
                {loadingStep === 3 && (
                  <View style={{ marginTop: spacing.md }}>
                    <View style={{ flexDirection: 'row', justifyContent: 'space-between', marginBottom: 8 }}>
                      <Text style={{ fontSize: 13, color: '#666666' }}>Génération par IA...</Text>
                      <Text style={{ fontSize: 13, fontWeight: '700', color: '#4F46E5' }}>{loadingProgress}%</Text>
                    </View>
                    <View style={{ height: 6, backgroundColor: '#EAEAE6', borderRadius: 3, overflow: 'hidden' }}>
                      <View style={{ height: '100%', width: `${loadingProgress}%`, backgroundColor: '#4F46E5', borderRadius: 3 }} />
                    </View>
                  </View>
                )}
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
                        Avant : {Math.round(parsedAudit.original_ats_score)}% • Après:{' '}
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

                {/* Template picker + export PDF */}
                {rewriteContent && (
                  <View style={{ marginTop: spacing.lg }}>
                    <Text style={styles.subSectionTitle}>Version réécrite proposée</Text>
                    <Text style={styles.sectionBody}>
                      Ta version optimisée a été générée. Choisis un design et télécharge le PDF.
                    </Text>

                    {/* ── Template Picker ── */}
                    <Text style={[styles.subSectionTitle, { marginTop: spacing.md }]}>Design du CV</Text>
                    <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.templatePickerScroll}>
                      {CV_TEMPLATES.map(tpl => (
                        <TouchableOpacity
                          key={tpl.id}
                          onPress={() => setSelectedTemplateId(tpl.id)}
                          style={[
                            styles.templateCard,
                            selectedTemplateId === tpl.id 
                              ? [styles.templateCardActive, { borderColor: tpl.accentColor, backgroundColor: `${tpl.accentColor}18` }]
                              : styles.templateCardInactive
                          ]}
                        >
                          <View style={[styles.templateColorIndicator, { backgroundColor: tpl.accentColor }]} />
                          <Text style={styles.templateLabel}>
                            {tpl.label}
                          </Text>
                          <Text style={styles.templateDescription}>
                            {tpl.description}
                          </Text>
                        </TouchableOpacity>
                      ))}
                    </ScrollView>

                    <TouchableOpacity
                      style={styles.pdfButton}
                      activeOpacity={0.9}
                      onPress={handleExportPdf}
                    >
                      <Ionicons
                        name="download-outline"
                        size={18}
                        color="#FFFFFF"
                        style={{ marginRight: 8 }}
                      />
                      <Text style={styles.pdfButtonText}>Télécharger en PDF</Text>
                    </TouchableOpacity>
                  </View>
                )}
              </>
            ) : rewriteContent ? (
              <View>
                <Text style={styles.sectionBody}>
                  Une version optimisée de ton CV est prête. Choisis un design et télécharge-la en PDF.
                </Text>

                {/* ── Template Picker ── */}
                <Text style={[styles.subSectionTitle, { marginTop: spacing.md }]}>Design du CV</Text>
                <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.templatePickerScroll}>
                  {CV_TEMPLATES.map(tpl => (
                    <TouchableOpacity
                      key={tpl.id}
                      onPress={() => setSelectedTemplateId(tpl.id)}
                      style={[
                        styles.templateCard,
                        selectedTemplateId === tpl.id 
                          ? [styles.templateCardActive, { borderColor: tpl.accentColor, backgroundColor: `${tpl.accentColor}18` }]
                          : styles.templateCardInactive
                      ]}
                    >
                      <View style={[styles.templateColorIndicator, { backgroundColor: tpl.accentColor }]} />
                      <Text style={styles.templateLabel}>
                        {tpl.label}
                      </Text>
                      <Text style={styles.templateDescription}>
                        {tpl.description}
                      </Text>
                    </TouchableOpacity>
                  ))}
                </ScrollView>

                <TouchableOpacity
                  style={styles.pdfButton}
                  activeOpacity={0.9}
                  onPress={handleExportPdf}
                >
                  <Ionicons
                    name="download-outline"
                    size={18}
                    color="#FFFFFF"
                    style={{ marginRight: 8 }}
                  />
                  <Text style={styles.pdfButtonText}>Télécharger en PDF</Text>
                </TouchableOpacity>
              </View>
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
                    Choisis le CV à analyser. Tu pourras ensuite lancer l'audit détaillé côté backend.
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
              {isLoading ? 'Analyse en cours…' : `Lancer l'audit de mon CV`}
            </Text>
          </TouchableOpacity>
        </View>
      </View>
    </KeyboardAvoidingView>
  );
}
