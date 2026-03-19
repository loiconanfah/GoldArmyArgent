import React, { useEffect, useRef, useState } from 'react';
import {
  View,
  Text,
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
import { Audio } from 'expo-av';
import * as FileSystem from 'expo-file-system/legacy';
import { spacing } from '../../src/theme/spacing';
import { API_BASE_URL } from '../../src/utils/constants';
import { getAccessToken } from '../../src/utils/storage';
import { mentorSimulatorStyles as styles } from './styles/mentor-simulator.styles';
import { useRouter } from 'expo-router';
import { useUIStore } from '../../src/stores/uiStore';
import * as DocumentPicker from 'expo-document-picker';
import { useInterviewStore } from '../../src/stores/interviewStore';

type CvSource = 'profile' | 'upload';

type WsInterviewRole = 'recruiter' | 'user' | 'system';

type WsMessage =
  | { type: 'recruiter_response'; text: string; recruiter_name: string }
  | { type: 'voice'; audio: string }
  | { type: 'thinking' }
  | { type: 'error'; message: string; recruiter_name?: string }
  | { type: 'paywall'; message: string; count: number; limit: number };

export default function MentorSimulatorScreen() {
  const insets = useSafeAreaInsets();
  const router = useRouter();
  const { showToast } = useUIStore();

  const [cvSource, setCvSource] = useState<CvSource | null>(null);
  const [cvFileName, setCvFileName] = useState<string | null>(null);
  const [company, setCompany] = useState<string>('');
  const [jobTitle, setJobTitle] = useState<string>('');
  const [jobDetails, setJobDetails] = useState<string>('');
  const [cvText, setCvText] = useState<string>('');
  const [recruiterId, setRecruiterId] = useState<'tech' | 'hr' | 'ceo'>('tech');
  const [interviewType, setInterviewType] = useState<'general' | 'tech'>('general');

  const [isThinking, setIsThinking] = useState(false);
  const audioSoundRef = useRef<Audio.Sound | null>(null);

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

  const handleChooseUploadCv = async () => {
    try {
      const res = await DocumentPicker.getDocumentAsync({ type: 'application/pdf' });
      if (res.canceled || !res.assets || !res.assets[0]) return;
      const file = res.assets[0];

      if (file.size && file.size > 5 * 1024 * 1024) {
        showToast('Fichier trop lourd (5Mo max).', 'error');
        return;
      }

      const token = await getAccessToken();
      if (!token) {
        showToast('Connecte-toi pour uploader un CV.', 'error');
        return;
      }

      showToast('Extraction du CV en cours...', 'info');
      const formData = new FormData();
      formData.append('file', {
        uri: Platform.OS === 'ios' ? file.uri.replace('file://', '') : file.uri,
        name: file.name,
        type: file.mimeType || 'application/pdf',
      } as any);

      const response = await fetch(`${API_BASE_URL}/api/parse-pdf`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
          Accept: 'application/json',
        },
        body: formData,
      });

      const data = await response.json();
      if (response.ok && data.status === 'success' && data.text) {
        setCvText(data.text);
        setCvFileName(file.name);
        setCvSource('upload');
        showToast('CV extrait avec succès !', 'success');
      } else {
        showToast(data.detail || 'Erreur lors de l\'extraction du PDF.', 'error');
      }
    } catch (e) {
      showToast('Impossible d\'importer le CV.', 'error');
    }
    closeOverlay();
  };

  const playVoiceAudioBase64 = async (base64Audio: string) => {
    if (!base64Audio) return;

    if (audioSoundRef.current) {
      try { await audioSoundRef.current.unloadAsync(); } catch {}
      audioSoundRef.current = null;
    }

    try {
      if (Platform.OS !== 'web') {
        await Audio.setAudioModeAsync({
          allowsRecordingIOS: false,
          playsInSilentModeIOS: true,
          staysActiveInBackground: false,
          playThroughEarpieceAndroid: false,
        });
      }

      let fileUri = `data:audio/mp3;base64,${base64Audio}`;

      if (Platform.OS === 'web') {
        const htmlAudio = new globalThis.Audio(fileUri);
        htmlAudio.play().catch(e => {
          console.error("Web audio play blocked:", e);
          const errStr = e && e.message ? e.message : String(e);
          showToast(`Erreur Audio Web: ${errStr}`, 'error', 3000);
        });
        return;
      }

      // NATIVE: data: URIs bug out silently on iOS/Android AVPlayer. We MUST use a real file.
      try {
        const cacheUri = FileSystem.cacheDirectory || FileSystem.documentDirectory || "file:///tmp/";
        const normalizedDir = cacheUri.endsWith('/') ? cacheUri : cacheUri + '/';
        const nativeUri = `${normalizedDir}interview_test_${Date.now()}.mp3`;
        
        await FileSystem.writeAsStringAsync(nativeUri, base64Audio, { encoding: FileSystem.EncodingType.Base64 });
        fileUri = nativeUri; // Successfully saved
        console.log("playVoiceAudioBase64: File saved to", fileUri);
      } catch (fe) {
        console.error("playVoiceAudioBase64: FileSystem write failed, falling back to data URI", fe);
      }

      const { sound } = await Audio.Sound.createAsync(
        { uri: fileUri }, 
        { shouldPlay: true, volume: 1.0 }
      );
      audioSoundRef.current = sound;

      await sound.playAsync().catch(e => console.error("playAsync fallback error", e));

      sound.setOnPlaybackStatusUpdate((status) => {
        if (!status.isLoaded) return;
        if (status.didJustFinish) {
          showToast("Lecture terminée (durée valide) !", "info");
          void sound.unloadAsync().catch(() => undefined);
        }
      });
    } catch (err) {
      console.error("playVoiceAudioBase64 error in simulator:", err);
      throw err;
    }
  };

  const handleTestVoice = async () => {
    try {
      setIsThinking(true);

      const resp = await fetch(`${API_BASE_URL}/api/interview/test-voice`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text: "Bonjour ! Je suis prêt(e) pour l'entretien. Pouvez-vous commencer ?",
          recruiterId,
        }),
      });

      const data = (await resp.json()) as {
        status?: string;
        audio?: string;
        message?: string;
      };

      if (!resp.ok || data.status !== 'success' || !data.audio) {
        showToast(data.message || 'Test audio échoué.', 'error');
        return;
      }

      await playVoiceAudioBase64(data.audio);
      showToast('Test audio OK', 'success', 1500);
    } catch (err) {
      console.error("handleTestVoice error:", err);
      showToast('Impossible de tester le son.', 'error');
    } finally {
      setIsThinking(false);
    }
  };

  const startInterviewRoom = () => {
    if (!company.trim() || !jobTitle.trim()) {
      showToast('Entreprise et poste sont requis.', 'warning');
      return;
    }
    if (!cvText.trim()) {
      showToast('Veuillez fournir un texte de CV.', 'warning');
      return;
    }

    // Sauvegarder dans le store
    useInterviewStore.getState().setConfig({
      company,
      jobTitle,
      jobDetails,
      cvText,
      recruiterId,
      interviewType,
    });

    // Naviguer vers la nouvelle salle de visio
    router.push('/(mentor)/mentor-interview-room');
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
          <TouchableOpacity
            onPress={() => {
              router.back();
            }}
            style={styles.backButton}
          >
            <Ionicons name="chevron-back" size={22} color="#FFFFFF" />
          </TouchableOpacity>
          <View style={[styles.headerTextBlock, { flex: 1 }]}>
            <Text style={styles.headerTitle}>Paramètres de l’entretien</Text>
            <Text style={styles.headerSubtitle}>
              Configure le contexte pour que l&apos;IA simule l&apos;entretien parfaitement.
            </Text>
          </View>
          <TouchableOpacity
            style={{
               flexDirection: 'row', alignItems: 'center', backgroundColor: '#1A1A2E', 
               paddingVertical: 8, paddingHorizontal: 12, borderRadius: 12, 
               borderWidth: 1, borderColor: '#2D2D44', marginLeft: 12
            }}
            onPress={() => router.push('/(tabs)/mentor')}
          >
            <Ionicons name="time-outline" size={16} color="#A5B4FC" style={{ marginRight: 6 }} />
            <Text style={{ color: '#A5B4FC', fontSize: 12, fontWeight: '600' }}>Historique</Text>
          </TouchableOpacity>
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
          <TouchableOpacity
            style={styles.soundButton}
            activeOpacity={0.9}
            disabled={isThinking}
            onPress={handleTestVoice}
          >
            <Ionicons name="volume-high-outline" size={18} color="#E5E7EB" />
            <Text style={styles.soundButtonText}>Tester le son</Text>
          </TouchableOpacity>
          <View style={{ flex: 1 }} />
          <TouchableOpacity
            style={styles.launchButton}
            activeOpacity={0.9}
            onPress={startInterviewRoom}
          >
            <Ionicons name="videocam-outline" size={18} color="#FFFFFF" />
            <Text style={styles.launchButtonText}>Lancer la visioconférence</Text>
          </TouchableOpacity>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}


