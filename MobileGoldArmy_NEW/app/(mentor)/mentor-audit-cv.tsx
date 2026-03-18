import React, { useState, useRef, useEffect } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, Animated, KeyboardAvoidingView, Platform, ActivityIndicator } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { StatusBar } from 'expo-status-bar';
import { Ionicons } from '@expo/vector-icons';
import { useRouter } from 'expo-router';
import { spacing } from '../../src/theme/spacing';
import { mentorAuditCvStyles as styles } from './styles/mentor-audit-cv.styles';
import { mentorService } from '../../src/services/mentorService';
import { cvService, CvUploadError } from '../../src/services/cvService';
import { useUIStore } from '../../src/stores/uiStore';
import * as Haptics from 'expo-haptics';
import * as Print from 'expo-print';
import * as Sharing from 'expo-sharing';

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

  const handleExportPdf = async () => {
    if (!rewriteContent) {
      showToast('Aucune version réécrite disponible pour générer le PDF.', 'warning');
      return;
    }

    try {
      await Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);

      // Parser le JSON du CV réécrit
      let cvData: any = {};
      try {
        cvData = JSON.parse(rewriteContent);
      } catch {
        // Si ce n'est pas du JSON, on utilise le texte brut comme fallback
        cvData = { profile: rewriteContent, experience: [] };
      }

      // Extraire les données du CV (structure complète)
      const firstName = (cvData.firstName || cvData.full_name?.split(' ')[0] || parsedAudit?.candidate_name?.split(' ')[0] || 'PRENOM').toUpperCase();
      const lastName = (cvData.lastName || cvData.full_name?.split(' ').slice(1).join(' ') || parsedAudit?.candidate_name?.split(' ').slice(1).join(' ') || 'NOM').toUpperCase();
      const title = cvData.title || parsedAudit?.candidate_title || 'Titre professionnel';
      const location = cvData.location || 'Localisation';
      const phone = cvData.phone || cvData.contact?.phone || '';
      const email = cvData.email || cvData.contact?.email || '';
      const linkedin = cvData.linkedin || '';
      const github = cvData.github || '';
      const profile = cvData.profile || cvData.summary || '';
      const education = Array.isArray(cvData.education) ? cvData.education : [];
      const skills = Array.isArray(cvData.skills) ? cvData.skills : (typeof cvData.skills === 'object' && cvData.skills !== null ? Object.values(cvData.skills).flat() : []);
      const experience = Array.isArray(cvData.experiences) ? cvData.experiences : (Array.isArray(cvData.experience) ? cvData.experience : []);
      const projects = Array.isArray(cvData.projects) ? cvData.projects : [];
      const languages = Array.isArray(cvData.languages) ? cvData.languages : [];
      const certifications = Array.isArray(cvData.certifications) ? cvData.certifications : [];
      const yearsExperience = cvData.yearsExperience || '10+';
      const rating = parsedAudit?.ats_score ? (parsedAudit.ats_score / 20).toFixed(1) : '4.9';

      const html = `
        <!DOCTYPE html>
        <html>
          <head>
            <meta charset="utf-8" />
            <style>
              * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
              }
              body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
                background-color: #F0EFEA;
                padding: 20px;
                color: #1a1a1a;
              }
              .page {
                max-width: 800px;
                margin: 0 auto;
                background: #F0EFEA;
                padding: 20px;
              }
              
              /* ── HEADER ────────────────────────────────────────── */
              .header {
                display: flex;
                align-items: flex-end;
                margin-bottom: 24px;
                gap: 16px;
              }
              .photo-area {
                width: 170px;
                height: 200px;
                position: relative;
                margin-right: 8px;
                flex-shrink: 0;
              }
              .rating-badge {
                position: absolute;
                top: 0;
                right: 0;
                display: flex;
                align-items: center;
                z-index: 10;
                background-color: #F0EFEA;
                padding: 2px 4px;
                border-radius: 4px;
                font-size: 11px;
              }
              .rating-label { color: #555; }
              .rating-value { font-size: 12px; font-weight: 700; color: #1a1a1a; }
              .rating-star { font-size: 12px; color: #F5C518; }
              
              .photo-decor-container {
                position: absolute;
                top: 14px;
                left: 0;
                width: 170px;
                height: 180px;
                z-index: 1;
              }
              .diamond {
                position: absolute;
                background-color: #F5C518;
                transform: rotate(45deg);
              }
              .diamond-large {
                width: 80px;
                height: 80px;
                top: 20px;
                left: 10px;
                border-radius: 6px;
              }
              .diamond-small {
                width: 44px;
                height: 44px;
                top: 0;
                left: 70px;
                border-radius: 4px;
              }
              .exp-badge {
                position: absolute;
                bottom: 0;
                left: 0;
                background-color: #1a1a1a;
                width: 60px;
                height: 60px;
                border-radius: 4px;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                z-index: 5;
              }
              .exp-number {
                color: #fff;
                font-size: 20px;
                font-weight: 900;
                line-height: 22px;
              }
              .exp-label {
                color: #e8e8e8;
                font-size: 6px;
                text-align: center;
                margin-top: 2px;
                line-height: 8px;
              }
              .arrow-circle {
                position: absolute;
                bottom: 10px;
                left: 68px;
                width: 26px;
                height: 26px;
                border-radius: 13px;
                border: 1.5px solid #1a1a1a;
                display: flex;
                justify-content: center;
                align-items: center;
                z-index: 5;
              }
              .arrow-text { font-size: 12px; color: #1a1a1a; }
              
              .photo-circle {
                position: absolute;
                right: 0;
                top: 18px;
                width: 110px;
                height: 140px;
                border-radius: 8px;
                background-color: #c9bfb5;
                display: flex;
                justify-content: center;
                align-items: center;
                z-index: 3;
                overflow: hidden;
              }
              .photo-placeholder { font-size: 60px; }
              
              /* ── NAME / TITLE ────────────────────────────────── */
              .name-area {
                flex: 1;
                display: flex;
                flex-direction: column;
                justify-content: flex-end;
                padding-bottom: 4px;
              }
              .first-name {
                font-size: 18px;
                letter-spacing: 6px;
                color: #1a1a1a;
                font-weight: 300;
                text-transform: uppercase;
              }
              .last-name {
                font-size: 52px;
                font-weight: 900;
                color: #1a1a1a;
                letter-spacing: 10px;
                line-height: 56px;
                text-transform: uppercase;
              }
              .title-row {
                display: flex;
                align-items: center;
                margin-top: 6px;
                gap: 6px;
              }
              .snowflake-icon {
                width: 20px;
                height: 20px;
                background-color: #1a1a1a;
                border-radius: 10px;
                display: flex;
                justify-content: center;
                align-items: center;
              }
              .snowflake-text { color: #fff; font-size: 10px; }
              .job-title {
                font-size: 14px;
                font-style: italic;
                color: #1a1a1a;
                letter-spacing: 1px;
              }
              .location {
                font-size: 12px;
                color: #555;
                margin-top: 4px;
                letter-spacing: 0.5px;
              }
              
              /* ── BODY ────────────────────────────────────────── */
              .body {
                display: flex;
                flex-direction: row;
                gap: 24px;
              }
              
              /* ── SIDEBAR ─────────────────────────────────────── */
              .sidebar {
                width: 170px;
                flex-shrink: 0;
              }
              .contact-block {
                margin-bottom: 12px;
                display: flex;
                flex-direction: column;
                gap: 8px;
              }
              .contact-row {
                display: flex;
                align-items: center;
                gap: 6px;
              }
              .contact-icon { font-size: 12px; color: #1a1a1a; }
              .contact-text { font-size: 11px; color: #555; }
              
              .divider {
                height: 1px;
                background-color: #e8e8e8;
                margin: 14px 0;
              }
              
              .section-title {
                font-size: 13px;
                font-weight: 800;
                letter-spacing: 3px;
                color: #1a1a1a;
                text-transform: uppercase;
                margin-bottom: 10px;
              }
              
              .edu-block { margin-bottom: 12px; }
              .edu-period { font-size: 10px; color: #555; }
              .edu-degree { font-size: 11px; font-weight: 700; color: #1a1a1a; margin-top: 2px; }
              .edu-school { font-size: 11px; color: #555; }
              
              .skills-cat {
                font-size: 10px;
                font-weight: 700;
                letter-spacing: 1.5px;
                color: #1a1a1a;
                margin-bottom: 6px;
              }
              .skill-row {
                display: flex;
                align-items: center;
                gap: 6px;
                margin-bottom: 5px;
              }
              .bullet {
                width: 5px;
                height: 5px;
                border-radius: 1px;
                background-color: #1a1a1a;
                flex-shrink: 0;
              }
              .skill-text { font-size: 11px; color: #555; }
              
              /* ── MAIN CONTENT ───────────────────────────────── */
              .main { flex: 1; }
              .profile-text {
                font-size: 12px;
                color: #555;
                line-height: 18px;
                margin-bottom: 4px;
              }
              
              .exp-block { margin-bottom: 20px; }
              .exp-period { font-size: 10px; color: #555; margin-bottom: 2px; }
              .exp-title {
                font-size: 12px;
                font-weight: 800;
                letter-spacing: 1.5px;
                color: #1a1a1a;
                margin-bottom: 6px;
                text-transform: uppercase;
              }
              .exp-desc { font-size: 11px; color: #555; line-height: 17px; margin-bottom: 6px; }
              .bullet-row {
                display: flex;
                align-items: flex-start;
                gap: 6px;
                margin-bottom: 4px;
              }
              .bullet-text { font-size: 11px; color: #555; flex: 1; line-height: 16px; }
            </style>
          </head>
          <body>
            <div class="page">
              <!-- ── HEADER ── -->
              <div class="header">
                <!-- Left: photo area -->
                <div class="photo-area">
                  <div class="rating-badge">
                    <span class="rating-label">Rated </span>
                    <span class="rating-value">${rating}</span>
                    <span class="rating-star"> ★</span>
                  </div>
                  <div class="photo-decor-container">
                    <div class="diamond diamond-large"></div>
                    <div class="diamond diamond-small"></div>
                    <div class="exp-badge">
                      <div class="exp-number">${yearsExperience}</div>
                      <div class="exp-label">Years Experience<br/>In this Field.</div>
                    </div>
                    <div class="arrow-circle">
                      <div class="arrow-text">↓</div>
                    </div>
                  </div>
                  <div class="photo-circle">
                    <div class="photo-placeholder">👤</div>
                  </div>
                </div>
                
                <!-- Right: name + title -->
                <div class="name-area">
                  <div class="first-name">${firstName}</div>
                  <div class="last-name">${lastName}</div>
                  <div class="title-row">
                    <div class="snowflake-icon">
                      <div class="snowflake-text">✳</div>
                    </div>
                    <div class="job-title">${title}</div>
                  </div>
                  <div class="location">~ ${location}</div>
                </div>
              </div>
              
              <!-- ── BODY (sidebar + main) ── -->
              <div class="body">
                <div class="sidebar">
                  <!-- Contact -->
                  <div class="contact-block">
                    ${phone ? `<div class="contact-row"><span class="contact-icon">📞</span><span class="contact-text">${phone}</span></div>` : ''}
                    ${email ? `<div class="contact-row"><span class="contact-icon">✉</span><span class="contact-text">${email}</span></div>` : ''}
                  </div>
                  
                  ${(phone || email) && (education.length > 0 || skills.length > 0) ? '<div class="divider"></div>' : ''}
                  
                  <!-- Education -->
                  ${education.length > 0 ? `
                    <div class="section-title">EDUCATION</div>
                    ${education.map((ed: any) => `
                      <div class="edu-block">
                        <div class="edu-period">${ed.period || ''}</div>
                        <div class="edu-degree">${ed.degree || ''}</div>
                        <div class="edu-school">${ed.school || ''}</div>
                      </div>
                    `).join('')}
                    ${skills.length > 0 ? '<div class="divider"></div>' : ''}
                  ` : ''}
                  
                  <!-- Skills -->
                  ${skills.length > 0 ? `
                    <div class="section-title">SKILLS</div>
                    <div class="skills-cat">PROFESSIONAL</div>
                    ${skills.map((skill: string) => `
                      <div class="skill-row">
                        <div class="bullet"></div>
                        <div class="skill-text">${skill}</div>
                      </div>
                    `).join('')}
                  ` : ''}
                </div>
                
                <div class="main">
                  <!-- Profile -->
                  ${profile ? `
                    <div class="section-title">PROFILE</div>
                    <div class="profile-text">${profile}</div>
                    <div class="divider"></div>
                  ` : ''}
                  
                  <!-- Experience -->
                  ${experience.length > 0 ? `
                    <div class="section-title">EXPERIENCE</div>
                    ${experience.map((exp: any) => `
                      <div class="exp-block">
                        <div class="exp-period">${exp.period || ''}</div>
                        <div class="exp-title">${exp.title || ''}</div>
                        ${exp.description ? `<div class="exp-desc">${exp.description}</div>` : ''}
                        ${Array.isArray(exp.bullets) && exp.bullets.length > 0 ? exp.bullets.map((b: string) => `
                          <div class="bullet-row">
                            <div class="bullet"></div>
                            <div class="bullet-text">${b}</div>
                          </div>
                        `).join('') : ''}
                      </div>
                    `).join('')}
                  ` : ''}
                </div>
              </div>
            </div>
          </body>
        </html>
      `;

      const { uri } = await Print.printToFileAsync({ html });

      const canShare = await Sharing.isAvailableAsync();
      if (canShare) {
        await Sharing.shareAsync(uri, {
          mimeType: 'application/pdf',
          dialogTitle: 'Partager le CV optimisé',
        });
      } else {
        showToast('Partage de fichier non disponible sur cet appareil.', 'warning');
      }
    } catch (error) {
      console.error('[Mentor][Export PDF]', error);
      showToast('Erreur lors de la génération du PDF.', 'error');
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

                {/* Bloc export PDF de la version réécrite */}
                {rewriteContent && (
                  <View style={{ marginTop: spacing.lg }}>
                    <Text style={styles.subSectionTitle}>Version réécrite proposée</Text>
                    <Text style={styles.sectionBody}>
                      Ta version optimisée a été générée. Télécharge le PDF pour obtenir un CV propre et prêt à être envoyé.
                    </Text>
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
                  Une version optimisée de ton CV est prête. Utilise le bouton ci-dessous pour la télécharger en PDF.
                </Text>
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


