import React, { useEffect, useRef, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Animated,
  KeyboardAvoidingView,
  Platform,
  TextInput,
} from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { StatusBar } from 'expo-status-bar';
import { Ionicons } from '@expo/vector-icons';
import { spacing } from '../../src/theme/spacing';
import { useRouter } from 'expo-router';

type CvSource = 'profile' | 'upload';

export default function MentorSimulatorScreen() {
  const insets = useSafeAreaInsets();
  const router = useRouter();

  const [cvSource, setCvSource] = useState<CvSource | null>(null);
  const [cvFileName, setCvFileName] = useState<string | null>(null);
  const [company, setCompany] = useState<string>('');
  const [jobTitle, setJobTitle] = useState<string>('');
  const [jobDetails, setJobDetails] = useState<string>('');
  const [cvText, setCvText] = useState<string>('');
  const [recruiterId, setRecruiterId] = useState<'tech' | 'hr' | 'ceo'>('tech');
  const [interviewType, setInterviewType] = useState<'general' | 'tech'>('general');

  const heroAnim = useRef(new Animated.Value(0)).current;
  const overlayAnim = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    Animated.timing(heroAnim, {
      toValue: 1,
      duration: 450,
      useNativeDriver: true,
    }).start();

    Animated.timing(overlayAnim, {
      toValue: 1,
      duration: 250,
      useNativeDriver: true,
    }).start();
  }, [heroAnim, overlayAnim]);

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

  const handleChooseUploadCv = () => {
    setCvSource('upload');
    setCvFileName('CV_importe.pdf');
    closeOverlay();
  };

  return (
    <KeyboardAvoidingView
      style={styles.root}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
    >
      <StatusBar style="light" />
      <ScrollView
        style={styles.scroll}
        contentContainerStyle={[
          styles.content,
          { paddingTop: insets.top + spacing.xl, paddingBottom: insets.bottom + 80 },
        ]}
        showsVerticalScrollIndicator={false}
      >
        {/* HEADER */}
        <View style={styles.headerRow}>
          <TouchableOpacity onPress={() => router.back()} style={styles.backButton}>
            <Ionicons name="chevron-back" size={22} color="#FFFFFF" />
          </TouchableOpacity>
          <View style={styles.headerTextBlock}>
            <Text style={styles.headerTitle}>Paramètres de l’entretien</Text>
            <Text style={styles.headerSubtitle}>
              Configure le contexte pour que l&apos;IA simule l&apos;entretien parfaitement.
            </Text>
          </View>
        </View>

        {/* HERO / INFO BANDEAU */}
        <Animated.View
          style={[
            styles.hero,
            {
              opacity: heroAnim,
              transform: [
                {
                  translateY: heroAnim.interpolate({
                    inputRange: [0, 1],
                    outputRange: [16, 0],
                  }),
                },
              ],
            },
          ]}
        >
          <View style={styles.heroTextContainer}>
            <View style={styles.heroPill}>
              <Ionicons name="sparkles-outline" size={16} color="#A5B4FC" />
              <Text style={styles.heroPillText}>Simulateur IA temps réel</Text>
            </View>
            <Text style={styles.heroTitle}>Définis le contexte de ton entretien</Text>
            <Text style={styles.heroSubtitle}>
              Entreprise, poste, description de l&apos;offre, CV et type de recruteur : toutes ces
              informations sont envoyées au backend avant de lancer la visioconférence.
            </Text>
          </View>
        </Animated.View>

        {/* FORM PRINCIPAL */}
        <View style={styles.grid}>
          {/* Colonne gauche : Entreprise / Poste / Description */}
          <View style={styles.leftColumn}>
            <View style={styles.fieldBlock}>
              <Text style={styles.fieldLabel}>Entreprise cible</Text>
              <View style={styles.inputWrapper}>
                <Ionicons name="business-outline" size={16} color="#9CA3AF" />
                <TextInput
                  value={company}
                  onChangeText={setCompany}
                  placeholder="Ex: Google, Alan, Startup X…"
                  placeholderTextColor="#6B7280"
                  style={styles.textInput}
                />
              </View>
            </View>

            <View style={styles.fieldBlock}>
              <Text style={styles.fieldLabel}>Poste visé</Text>
              <View style={styles.inputWrapper}>
                <Ionicons name="briefcase-outline" size={16} color="#9CA3AF" />
                <TextInput
                  value={jobTitle}
                  onChangeText={setJobTitle}
                  placeholder="Ex: Développeur Fullstack, Product Manager…"
                  placeholderTextColor="#6B7280"
                  style={styles.textInput}
                />
              </View>
            </View>

            <View style={styles.fieldBlock}>
              <Text style={styles.fieldLabel}>Description de l&apos;offre (détails)</Text>
              <View style={[styles.inputWrapper, styles.textAreaWrapper]}>
                <Ionicons name="document-text-outline" size={16} color="#9CA3AF" />
                <TextInput
                  value={jobDetails}
                  onChangeText={setJobDetails}
                  placeholder="Colle ici les missions principales, la stack, ou les prérequis…"
                  placeholderTextColor="#6B7280"
                  style={[styles.textInput, styles.textArea]}
                  multiline
                />
              </View>
            </View>
          </View>

          {/* Colonne droite : CV + recruteur + format */}
          <View style={styles.rightColumn}>
            {/* CV actuel */}
            <View style={styles.fieldBlock}>
              <View style={styles.fieldHeaderRow}>
                <Text style={styles.fieldLabel}>Votre profil / CV actuel</Text>
                <TouchableOpacity
                  style={styles.importButton}
                  activeOpacity={0.9}
                  onPress={handleChooseUploadCv}
                >
                  <Ionicons name="lock-closed-outline" size={14} color="#E5E7EB" />
                  <Text style={styles.importButtonText}>Importer un PDF</Text>
                </TouchableOpacity>
              </View>
              <View style={[styles.inputWrapper, styles.textAreaWrapper]}>
                <Ionicons name="person-circle-outline" size={16} color="#9CA3AF" />
                <TextInput
                  value={cvText}
                  onChangeText={setCvText}
                  placeholder="Colle le texte brut de ton CV pour que le recruteur puisse réagir dessus…"
                  placeholderTextColor="#6B7280"
                  style={[styles.textInput, styles.textArea]}
                  multiline
                />
              </View>
            </View>

            {/* Choix du recruteur */}
            <View style={styles.fieldBlock}>
              <Text style={styles.fieldLabel}>Choix du recruteur</Text>
              <View style={styles.recruiterRow}>
                {(['tech', 'hr', 'ceo'] as const).map((id) => (
                  <TouchableOpacity
                    key={id}
                    style={[
                      styles.recruiterCard,
                      recruiterId === id && styles.recruiterCardActive,
                    ]}
                    activeOpacity={0.9}
                    onPress={() => setRecruiterId(id)}
                  >
                    <View style={styles.recruiterAvatar} />
                    <View style={styles.recruiterText}>
                      <Text style={styles.recruiterName}>
                        {id === 'tech'
                          ? 'Sophie - Tech Lead'
                          : id === 'hr'
                          ? 'Marc - HR Manager'
                          : 'Alice - CEO'}
                      </Text>
                      <Text style={styles.recruiterRole}>
                        {id === 'tech'
                          ? 'Expertise technique'
                          : id === 'hr'
                          ? 'Culture & soft skills'
                          : 'Vision & stratégie'}
                      </Text>
                    </View>
                    {recruiterId === id && (
                      <View style={styles.recruiterCheck}>
                        <Ionicons name="checkmark" size={14} color="#E5E7EB" />
                      </View>
                    )}
                  </TouchableOpacity>
                ))}
              </View>
            </View>

            {/* Format de l'entretien */}
            <View style={styles.fieldBlock}>
              <Text style={styles.fieldLabel}>Format de l&apos;entretien</Text>
              <View style={styles.formatRow}>
                <TouchableOpacity
                  style={[
                    styles.formatButton,
                    interviewType === 'general' && styles.formatButtonActive,
                  ]}
                  onPress={() => setInterviewType('general')}
                  activeOpacity={0.9}
                >
                  <Text
                    style={[
                      styles.formatButtonText,
                      interviewType === 'general' && styles.formatButtonTextActive,
                    ]}
                  >
                    Général &amp; HR
                  </Text>
                </TouchableOpacity>
                <TouchableOpacity
                  style={[
                    styles.formatButton,
                    interviewType === 'tech' && styles.formatButtonActive,
                  ]}
                  onPress={() => setInterviewType('tech')}
                  activeOpacity={0.9}
                >
                  <Text
                    style={[
                      styles.formatButtonText,
                      interviewType === 'tech' && styles.formatButtonTextActive,
                    ]}
                  >
                    Technique
                  </Text>
                </TouchableOpacity>
              </View>
            </View>
          </View>
        </View>

        {/* FOOTER CTA */}
        <View style={styles.footerRow}>
          <TouchableOpacity style={styles.soundButton} activeOpacity={0.9}>
            <Ionicons name="volume-high-outline" size={18} color="#E5E7EB" />
            <Text style={styles.soundButtonText}>Tester le son</Text>
          </TouchableOpacity>
          <View style={{ flex: 1 }} />
          <TouchableOpacity style={styles.launchButton} activeOpacity={0.9}>
            <Ionicons name="videocam-outline" size={18} color="#FFFFFF" />
            <Text style={styles.launchButtonText}>Lancer la visioconférence</Text>
          </TouchableOpacity>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  root: {
    flex: 1,
    backgroundColor: '#F3EEE7',
  },
  scroll: {
    flex: 1,
  },
  content: {
    paddingHorizontal: spacing.lg,
    paddingBottom: spacing.xxl,
  },
  headerRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: spacing.xl,
  },
  backButton: {
    width: 36,
    height: 36,
    borderRadius: 18,
    borderWidth: 1,
    borderColor: '#C4BDB0',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#1A1A18',
  },
  headerTextBlock: {
    marginLeft: spacing.md,
    flex: 1,
  },
  headerTitle: {
    fontSize: 22,
    fontWeight: '800',
    color: '#151515',
  },
  headerSubtitle: {
    marginTop: 4,
    fontSize: 13,
    color: '#5A554C',
  },
  hero: {
    padding: spacing.lg,
    borderRadius: 24,
    backgroundColor: '#F9E4C4',
    borderWidth: 1,
    borderColor: '#F0C98C',
    marginBottom: spacing.xl,
    shadowColor: 'rgba(0,0,0,0.08)',
    shadowOpacity: 1,
    shadowRadius: 18,
    shadowOffset: { width: 0, height: 10 },
    elevation: 4,
  },
  heroTextContainer: {
    flex: 1,
  },
  heroPill: {
    flexDirection: 'row',
    alignItems: 'center',
    alignSelf: 'flex-start',
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.xs,
    borderRadius: 999,
    backgroundColor: '#F5C58A',
    marginBottom: spacing.sm,
  },
  heroPillText: {
    marginLeft: spacing.xs,
    fontSize: 11,
    letterSpacing: 0.6,
    textTransform: 'uppercase',
    color: '#5C3600',
  },
  heroTitle: {
    fontSize: 20,
    fontWeight: '800',
    color: '#161513',
    marginBottom: spacing.xs,
  },
  heroSubtitle: {
    fontSize: 14,
    color: '#5F584E',
    lineHeight: 20,
  },
  grid: {
    flexDirection: 'column',
    gap: spacing.xl,
    marginTop: spacing.lg,
  },
  leftColumn: {
    flex: 1,
  },
  rightColumn: {
    flex: 1,
  },
  fieldBlock: {
    marginBottom: spacing.lg,
  },
  fieldLabel: {
    fontSize: 13,
    fontWeight: '600',
    color: '#4A4A46',
    marginBottom: spacing.sm,
    textTransform: 'uppercase',
    letterSpacing: 0.8,
  },
  inputWrapper: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    borderRadius: 14,
    backgroundColor: '#F5F4F0',
    borderWidth: 1,
    borderColor: '#EAEAE6',
    shadowColor: 'rgba(0,0,0,0.03)',
    shadowOpacity: 1,
    shadowRadius: 10,
    shadowOffset: { width: 0, height: 4 },
    elevation: 2,
  },
  textInput: {
    flex: 1,
    marginLeft: spacing.sm,
    fontSize: 14,
    color: '#151515',
    paddingVertical: 4,
  },
  textAreaWrapper: {
    alignItems: 'flex-start',
  },
  textArea: {
    height: 96,
    textAlignVertical: 'top',
  },
  fieldHeaderRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: spacing.sm,
  },
  importButton: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.xs,
    borderRadius: 999,
    borderWidth: 1,
    borderColor: '#E2E0DA',
    backgroundColor: '#FFFFFF',
  },
  importButtonText: {
    marginLeft: spacing.xs,
    fontSize: 12,
    fontWeight: '600',
    color: '#1A1A18',
  },
  recruiterRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    gap: spacing.sm,
    marginTop: spacing.xs,
  },
  recruiterCard: {
    flex: 1,
    borderRadius: 18,
    padding: spacing.md,
    backgroundColor: '#F7F4EE',
    borderWidth: 1,
    borderColor: '#EAEAE6',
    shadowColor: 'rgba(0,0,0,0.03)',
    shadowOpacity: 1,
    shadowRadius: 10,
    shadowOffset: { width: 0, height: 4 },
    elevation: 2,
  },
  recruiterCardActive: {
    borderColor: '#FF8C5A',
    backgroundColor: '#FFF0EB',
  },
  recruiterAvatar: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#FFE1B0',
    marginBottom: spacing.sm,
  },
  recruiterText: {
    marginRight: spacing.sm,
  },
  recruiterName: {
    fontSize: 13,
    fontWeight: '600',
    color: '#1A1A18',
    marginBottom: 2,
  },
  recruiterRole: {
    fontSize: 11,
    color: '#6B7280',
  },
  recruiterCheck: {
    position: 'absolute',
    top: spacing.sm,
    right: spacing.sm,
    width: 18,
    height: 18,
    borderRadius: 9,
    backgroundColor: '#FF6B35',
    alignItems: 'center',
    justifyContent: 'center',
  },
  formatRow: {
    flexDirection: 'row',
    gap: spacing.sm,
  },
  formatButton: {
    flex: 1,
    borderRadius: 999,
    paddingVertical: spacing.sm,
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 1,
    borderColor: '#EAEAE6',
    backgroundColor: '#FFFFFF',
  },
  formatButtonActive: {
    borderColor: '#FF6B35',
    backgroundColor: '#FFF0EB',
  },
  formatButtonText: {
    fontSize: 13,
    fontWeight: '600',
    color: '#6B7280',
  },
  formatButtonTextActive: {
    color: '#1A1A18',
  },
  footerRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: spacing.xl,
    paddingTop: spacing.lg,
    borderTopWidth: 1,
    borderTopColor: '#E5E5E0',
  },
  soundButton: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.sm,
    borderRadius: 999,
    borderWidth: 1,
    borderColor: '#EAEAE6',
    backgroundColor: '#FFFFFF',
  },
  soundButtonText: {
    marginLeft: spacing.xs,
    fontSize: 13,
    fontWeight: '500',
    color: '#1A1A18',
  },
  launchButton: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.sm,
    borderRadius: 999,
    backgroundColor: '#FF6B35',
  },
  launchButtonText: {
    marginLeft: spacing.xs,
    fontSize: 14,
    fontWeight: '600',
    color: '#FFFFFF',
  },
});

