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

      // Parse the rewritten CV JSON
      let cvData: any = {};
      try {
        cvData = JSON.parse(rewriteContent);
      } catch {
        cvData = { summary: rewriteContent };
      }

      // ── Field extraction with fallbacks ───────────────────────────────
      const fullName   = cvData.full_name || parsedAudit?.candidate_name || 'Prénom Nom';
      const nameParts  = fullName.trim().split(' ');
      const firstName  = nameParts[0] || '';
      const lastName   = nameParts.slice(1).join(' ') || '';
      const jobTitle   = cvData.title || parsedAudit?.candidate_title || '';
      const email      = cvData.email || '';
      const phone      = cvData.phone || '';
      const location   = cvData.location || '';
      const linkedin   = cvData.linkedin || '';
      const github     = cvData.github || '';
      const summary    = cvData.summary || '';
      const atsScore   = parsedAudit?.ats_score ? `${Math.round(parsedAudit.ats_score)}` : null;
      const origScore  = parsedAudit?.original_ats_score ? `${Math.round(parsedAudit.original_ats_score)}` : null;

      // experiences: [{title, company, location, start_date, end_date, bullets:[]}]
      const experiences: any[] = Array.isArray(cvData.experiences) ? cvData.experiences : [];
      // projects: [{name, description, bullets:[]}]
      const projects: any[] = Array.isArray(cvData.projects) ? cvData.projects : [];
      // education: [{degree, institution, location, year}]
      const education: any[] = Array.isArray(cvData.education) ? cvData.education : [];
      // skills: {Category: [item, ...]} or [item, ...]
      let skillsHtml = '';
      if (cvData.skills && typeof cvData.skills === 'object' && !Array.isArray(cvData.skills)) {
        skillsHtml = Object.entries(cvData.skills as Record<string, string[]>)
          .filter(([, items]) => Array.isArray(items) && items.length > 0)
          .map(([cat, items]) => `
            <div class="skill-cat">${escHtml(cat)}</div>
            <div class="skill-pills">${(items as string[]).map(s => `<span class="pill">${escHtml(s)}</span>`).join('')}</div>
          `).join('');
      } else if (Array.isArray(cvData.skills)) {
        skillsHtml = `<div class="skill-pills">${(cvData.skills as string[]).map(s => `<span class="pill">${escHtml(s)}</span>`).join('')}</div>`;
      }
      const languages: string[]      = Array.isArray(cvData.languages) ? cvData.languages : [];
      const certifications: string[] = Array.isArray(cvData.certifications) ? cvData.certifications : [];

      // ── Helper ────────────────────────────────────────────────────────
      function escHtml(s: any): string {
        return String(s ?? '').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
      }
      function sectionHeader(label: string) {
        return `<div class="section-head"><span class="section-line"></span><span class="section-label">${label}</span><span class="section-line"></span></div>`;
      }

      // ── HTML Template ─────────────────────────────────────────────────
      const html = `
<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="utf-8"/>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    *{margin:0;padding:0;box-sizing:border-box;}

    body{
      font-family:'Inter',system-ui,sans-serif;
      background:#F0EFEA;
      color:#1a1a1a;
      font-size:11px;
      line-height:1.5;
      -webkit-print-color-adjust:exact;
      print-color-adjust:exact;
    }

    .page{
      max-width:860px;
      margin:0 auto;
      background:#FAFAF8;
      padding:0;
      box-shadow:0 8px 40px rgba(0,0,0,0.12);
    }

    /* ── TOP BANNER ── */
    .banner{
      background:#1a1a1a;
      color:#fff;
      padding:36px 40px 28px;
      position:relative;
      overflow:hidden;
    }
    .banner::before{
      content:'';
      position:absolute;
      top:-40px;right:-40px;
      width:200px;height:200px;
      background:rgba(255,107,53,0.15);
      border-radius:50%;
    }
    .banner::after{
      content:'';
      position:absolute;
      bottom:-30px;right:80px;
      width:120px;height:120px;
      background:rgba(255,107,53,0.08);
      border-radius:50%;
    }
    .banner-inner{
      display:flex;
      justify-content:space-between;
      align-items:flex-end;
      position:relative;
      z-index:1;
    }
    .name-block{}
    .first-name{
      font-size:13px;
      font-weight:400;
      letter-spacing:6px;
      color:rgba(255,255,255,0.65);
      text-transform:uppercase;
      margin-bottom:2px;
    }
    .last-name{
      font-size:42px;
      font-weight:800;
      letter-spacing:4px;
      line-height:1;
      text-transform:uppercase;
      color:#fff;
    }
    .job-title{
      font-size:13px;
      font-weight:400;
      color:rgba(255,255,255,0.75);
      letter-spacing:2px;
      margin-top:8px;
    }
    .ats-badge{
      text-align:right;
    }
    .ats-label{
      font-size:9px;
      letter-spacing:2px;
      color:rgba(255,255,255,0.5);
      text-transform:uppercase;
    }
    .ats-value{
      font-size:44px;
      font-weight:800;
      color:#FF6B35;
      line-height:1;
    }
    .ats-suffix{
      font-size:18px;
      color:rgba(255,107,53,0.7);
    }
    .ats-orig{
      font-size:10px;
      color:rgba(255,255,255,0.4);
      margin-top:2px;
    }

    /* ── CONTACT BAR ── */
    .contact-bar{
      background:#FF6B35;
      padding:10px 40px;
      display:flex;
      flex-wrap:wrap;
      gap:14px;
      align-items:center;
    }
    .contact-item{
      display:flex;
      align-items:center;
      gap:5px;
      font-size:10px;
      color:#fff;
      font-weight:500;
      letter-spacing:0.3px;
    }
    .contact-icon{font-size:11px;}

    /* ── BODY ── */
    .body-layout{
      display:flex;
      gap:0;
    }

    /* ── SIDEBAR ── */
    .sidebar{
      width:240px;
      flex-shrink:0;
      background:#F3EEE6;
      padding:28px 22px;
    }

    .section-head{
      display:flex;
      align-items:center;
      gap:8px;
      margin:20px 0 10px;
    }
    .section-head:first-child{margin-top:0;}
    .section-line{
      flex:1;
      height:1px;
      background:#ccc;
    }
    .section-label{
      font-size:9px;
      font-weight:700;
      letter-spacing:2.5px;
      text-transform:uppercase;
      color:#888;
      white-space:nowrap;
    }

    /* Education */
    .edu-block{margin-bottom:12px;}
    .edu-degree{font-size:11px;font-weight:700;color:#1a1a1a;margin-bottom:2px;}
    .edu-school{font-size:10px;color:#555;}
    .edu-meta{font-size:10px;color:#888;margin-top:1px;}

    /* Skills */
    .skill-cat{
      font-size:9px;
      font-weight:700;
      letter-spacing:1.5px;
      text-transform:uppercase;
      color:#FF6B35;
      margin:10px 0 5px;
    }
    .skill-pills{display:flex;flex-wrap:wrap;gap:4px;margin-bottom:4px;}
    .pill{
      background:#fff;
      border:1px solid #ddd;
      border-radius:3px;
      padding:2px 7px;
      font-size:10px;
      color:#333;
      font-weight:500;
    }

    /* Languages */
    .lang-item{
      display:flex;
      align-items:center;
      gap:6px;
      margin-bottom:5px;
      font-size:10px;
      color:#333;
    }
    .lang-dot{
      width:6px;height:6px;
      border-radius:50%;
      background:#FF6B35;
      flex-shrink:0;
    }

    /* Certs */
    .cert-item{
      font-size:10px;
      color:#444;
      margin-bottom:5px;
      padding-left:10px;
      border-left:2px solid #FF6B35;
    }

    /* ── MAIN ── */
    .main{
      flex:1;
      padding:28px 32px;
    }

    /* Summary */
    .summary-text{
      font-size:11px;
      line-height:1.7;
      color:#444;
      margin-bottom:4px;
    }

    /* Experience */
    .exp-block{margin-bottom:22px;}
    .exp-header{
      display:flex;
      justify-content:space-between;
      align-items:baseline;
      margin-bottom:2px;
    }
    .exp-title{
      font-size:12px;
      font-weight:700;
      color:#1a1a1a;
      letter-spacing:0.5px;
    }
    .exp-dates{
      font-size:9px;
      color:#888;
      font-weight:500;
      letter-spacing:0.5px;
      white-space:nowrap;
      margin-left:8px;
    }
    .exp-company{
      font-size:11px;
      color:#FF6B35;
      font-weight:600;
      margin-bottom:6px;
    }
    .exp-loc{color:#888;font-weight:400;}
    .bullet-row{
      display:flex;
      align-items:flex-start;
      gap:7px;
      margin-bottom:4px;
    }
    .bullet-dot{
      width:5px;height:5px;
      border-radius:1px;
      background:#FF6B35;
      margin-top:4px;
      flex-shrink:0;
    }
    .bullet-text{font-size:11px;color:#444;flex:1;line-height:1.55;}

    /* Projects */
    .proj-block{margin-bottom:16px;}
    .proj-name{font-size:12px;font-weight:700;color:#1a1a1a;margin-bottom:3px;}
    .proj-desc{font-size:11px;color:#555;margin-bottom:5px;line-height:1.55;}

    /* ── PAGE BREAK ── */
    @media print{
      .page{box-shadow:none;}
      body{background:#fff;}
    }
  </style>
</head>
<body>
<div class="page">

  <!-- BANNER -->
  <div class="banner">
    <div class="banner-inner">
      <div class="name-block">
        <div class="first-name">${escHtml(firstName)}</div>
        <div class="last-name">${escHtml(lastName)}</div>
        ${jobTitle ? `<div class="job-title">— ${escHtml(jobTitle)}</div>` : ''}
      </div>
      ${atsScore ? `
      <div class="ats-badge">
        <div class="ats-label">Score ATS</div>
        <div class="ats-value">${escHtml(atsScore)}<span class="ats-suffix">%</span></div>
        ${origScore ? `<div class="ats-orig">avant : ${escHtml(origScore)}%</div>` : ''}
      </div>` : ''}
    </div>
  </div>

  <!-- CONTACT BAR -->
  ${(email || phone || location || linkedin || github) ? `
  <div class="contact-bar">
    ${email    ? `<div class="contact-item"><span class="contact-icon">✉</span>${escHtml(email)}</div>` : ''}
    ${phone    ? `<div class="contact-item"><span class="contact-icon">☎</span>${escHtml(phone)}</div>` : ''}
    ${location ? `<div class="contact-item"><span class="contact-icon">⌖</span>${escHtml(location)}</div>` : ''}
    ${linkedin ? `<div class="contact-item"><span class="contact-icon">in</span>${escHtml(linkedin)}</div>` : ''}
    ${github   ? `<div class="contact-item"><span class="contact-icon">⌾</span>${escHtml(github)}</div>` : ''}
  </div>` : ''}

  <!-- BODY -->
  <div class="body-layout">

    <!-- SIDEBAR -->
    <div class="sidebar">

      ${education.length > 0 ? `
      ${sectionHeader('Formation')}
      ${education.map((ed: any) => `
        <div class="edu-block">
          <div class="edu-degree">${escHtml(ed.degree || '')}</div>
          <div class="edu-school">${escHtml(ed.institution || ed.school || '')}</div>
          <div class="edu-meta">${[ed.location, ed.year].filter(Boolean).map(escHtml).join(' · ')}</div>
        </div>
      `).join('')}` : ''}

      ${skillsHtml ? `
      ${sectionHeader('Compétences')}
      ${skillsHtml}` : ''}

      ${languages.length > 0 ? `
      ${sectionHeader('Langues')}
      ${languages.map((l: string) => `<div class="lang-item"><div class="lang-dot"></div>${escHtml(l)}</div>`).join('')}` : ''}

      ${certifications.length > 0 ? `
      ${sectionHeader('Certifications')}
      ${certifications.map((c: string) => `<div class="cert-item">${escHtml(c)}</div>`).join('')}` : ''}

    </div>

    <!-- MAIN -->
    <div class="main">

      ${summary ? `
      ${sectionHeader('Profil')}
      <p class="summary-text">${escHtml(summary)}</p>` : ''}

      ${experiences.length > 0 ? `
      ${sectionHeader('Expériences')}
      ${experiences.map((exp: any) => `
        <div class="exp-block">
          <div class="exp-header">
            <div class="exp-title">${escHtml(exp.title || '')}</div>
            <div class="exp-dates">${[exp.start_date, exp.end_date].filter(Boolean).map(escHtml).join(' – ')}</div>
          </div>
          <div class="exp-company">
            ${escHtml(exp.company || '')}${exp.location ? ` <span class="exp-loc">· ${escHtml(exp.location)}</span>` : ''}
          </div>
          ${Array.isArray(exp.bullets) && exp.bullets.length > 0 ? exp.bullets.map((b: string) => `
            <div class="bullet-row">
              <div class="bullet-dot"></div>
              <div class="bullet-text">${escHtml(b)}</div>
            </div>`).join('') : ''}
        </div>
      `).join('')}` : ''}

      ${projects.length > 0 ? `
      ${sectionHeader('Projets')}
      ${projects.map((p: any) => `
        <div class="proj-block">
          <div class="proj-name">${escHtml(p.name || '')}</div>
          ${p.description ? `<div class="proj-desc">${escHtml(p.description)}</div>` : ''}
          ${Array.isArray(p.bullets) && p.bullets.length > 0 ? p.bullets.map((b: string) => `
            <div class="bullet-row">
              <div class="bullet-dot"></div>
              <div class="bullet-text">${escHtml(b)}</div>
            </div>`).join('') : ''}
        </div>
      `).join('')}` : ''}

    </div>
  </div>
</div>
</body>
</html>`;

      const { uri } = await Print.printToFileAsync({ html, base64: false });

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


