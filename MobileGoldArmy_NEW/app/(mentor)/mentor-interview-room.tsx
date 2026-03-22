import React, { useEffect, useRef, useState } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  ActivityIndicator,
  ScrollView,
  Platform,
  Image,
} from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { StatusBar } from 'expo-status-bar';
import { Ionicons } from '@expo/vector-icons';
import { useRouter } from 'expo-router';
import { Audio } from 'expo-av';
import * as FileSystem from 'expo-file-system/legacy';
import { CameraView, useCameraPermissions } from 'expo-camera';
import { BlurView } from 'expo-blur';

import { getAccessToken } from '../../src/utils/storage';
import { API_BASE_URL } from '../../src/utils/constants';
import { useUIStore } from '../../src/stores/uiStore';
import { useInterviewStore } from '../../src/stores/interviewStore';
import { styles } from './_styles/mentor-interview-room.styles';

type WsInterviewRole = 'recruiter' | 'user' | 'system';

type WsMessage =
  | { type: 'recruiter_response'; text: string; recruiter_name: string }
  | { type: 'voice'; audio: string }
  | { type: 'thinking' }
  | { type: 'error'; message: string; recruiter_name?: string }
  | { type: 'paywall'; message: string; count: number; limit: number };

const RECRUITERS = {
  tech: {
    name: 'Sophie - Tech Lead',
    role: 'Expertise Technique',
    photo: require('../../assets/recruiters/sophie.png'),
  },
  hr: {
    name: 'Marc - HR Manager',
    role: 'Culture & Soft Skills',
    photo: require('../../assets/recruiters/marc.png'),
  },
  ceo: {
    name: 'Alice - CEO',
    role: 'Vision & Stratégie',
    photo: require('../../assets/recruiters/alice.png'),
  },
};

export default function MentorInterviewRoom() {
  const insets = useSafeAreaInsets();
  const router = useRouter();
  const { showToast } = useUIStore();
  const config = useInterviewStore((state) => state.config);

  const [hasPermission, requestPermission] = useCameraPermissions();
  const [facing, setFacing] = useState<'front' | 'back'>('front');

  const [wsStatus, setWsStatus] = useState<'idle' | 'connecting' | 'connected' | 'error'>('idle');
  const [isInterviewRunning, setIsInterviewRunning] = useState(false);
  const [isThinking, setIsThinking] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  
  const [callElapsed, setCallElapsed] = useState('00:00');
  const [messages, setMessages] = useState<Array<{ id: string; role: WsInterviewRole; text: string }>>([]);

  const wsRef = useRef<WebSocket | null>(null);
  const audioSoundRef = useRef<Audio.Sound | null>(null);
  const recordingRef = useRef<Audio.Recording | null>(null);
  const manualCloseRef = useRef(false);
  const timerIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const callStartTimeRef = useRef<number | null>(null);
  const scrollViewRef = useRef<ScrollView>(null);
  const [showCalling, setShowCalling] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => setShowCalling(false), 2500);
    return () => clearTimeout(timer);
  }, []);

  useEffect(() => {
    if (!config) {
      showToast('Configuration introuvable.', 'error');
      router.back();
      return;
    }
    
    if (!hasPermission?.granted) {
      requestPermission();
    }
    
    startInterviewWs();

    callStartTimeRef.current = Date.now();
    timerIntervalRef.current = setInterval(() => {
      if (!callStartTimeRef.current) return;
      const s = Math.floor((Date.now() - callStartTimeRef.current) / 1000);
      const m = Math.floor(s / 60);
      setCallElapsed(`${String(m).padStart(2, '0')}:${String(s % 60).padStart(2, '0')}`);
    }, 1000) as any;

    return () => {
      closeWs();
      if (timerIntervalRef.current) clearInterval(timerIntervalRef.current);
    };
  }, []);

  const closeWs = () => {
    manualCloseRef.current = true;
    try { wsRef.current?.close(); } catch {}
    wsRef.current = null;
    try { void audioSoundRef.current?.unloadAsync(); } catch {}
    audioSoundRef.current = null;
    setIsInterviewRunning(false);
    setWsStatus('idle');
    setIsThinking(false);
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
          allowsRecordingIOS: true,
          playsInSilentModeIOS: true,
          staysActiveInBackground: false,
          playThroughEarpieceAndroid: false,
        });
      }

      let fileUri = `data:audio/mp3;base64,${base64Audio}`;
      
      if (Platform.OS === 'web') {
        const htmlAudio = new globalThis.Audio(fileUri);
        htmlAudio.play().catch(e => console.error("Web audio play blocked:", e));
        return;
      }

      try {
        const cacheUri = FileSystem.cacheDirectory || FileSystem.documentDirectory || "file:///tmp/";
        const normalizedDir = cacheUri.endsWith('/') ? cacheUri : cacheUri + '/';
        const nativeUri = `${normalizedDir}interview_voice_${Date.now()}.mp3`;
        
        await FileSystem.writeAsStringAsync(nativeUri, base64Audio, { encoding: FileSystem.EncodingType.Base64 });
        fileUri = nativeUri; 
      } catch (fe) {
        console.error("playVoiceAudioBase64: FileSystem write failed", fe);
      }

      const { sound } = await Audio.Sound.createAsync(
        { uri: fileUri }, 
        { shouldPlay: true, volume: 1.0 }
      );
      audioSoundRef.current = sound;

      await sound.playAsync().catch(e => console.error("playAsync error", e));

      sound.setOnPlaybackStatusUpdate((status) => {
        if (!status.isLoaded) return;
        if (status.didJustFinish) {
          void sound.unloadAsync().catch(() => undefined);
        }
      });
    } catch (err) {
      console.error("playVoiceAudioBase64 error:", err);
    }
  };

  const startInterviewWs = async () => {
    if (wsStatus === 'connecting' || isInterviewRunning) return;
    const token = await getAccessToken();
    if (!token) return router.replace('/(auth)/login');

    setWsStatus('connecting');
    setIsThinking(false);
    setMessages([]);
    setIsInterviewRunning(true);

    const interviewTypeBackend = config!.interviewType === 'tech' ? 'technical' : 'general';
    const wsBase = API_BASE_URL.replace(/^http/, 'ws');
    const wsUrl = `${wsBase}/api/interview/ws?token=${encodeURIComponent(token)}`;

    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;
    manualCloseRef.current = false;

    ws.onopen = () => {
      ws.send(JSON.stringify({
        type: 'setup',
        payload: {
          cv: config!.cvText || 'Non renseigné',
          jobTitle: config!.jobTitle,
          company: config!.company,
          jobDetails: config!.jobDetails || 'Pas de détails',
          interviewType: interviewTypeBackend,
          recruiterId: config!.recruiterId,
        },
      }));
      setWsStatus('connected');
      setMessages([{ id: 'sys-start', role: 'system', text: 'Connexion établie. L\'IA prépare l\'entretien...' }]);
    };

    ws.onerror = () => {
      setWsStatus('error');
      showToast("Connexion WebSocket impossible.", 'error');
      closeWs();
    };

    ws.onmessage = (event) => {
      let msg: WsMessage;
      try { 
        msg = JSON.parse(event.data as string) as WsMessage;
      } catch { return; }

      if (msg.type === 'thinking') {
        setIsThinking(true);
        return;
      }

      if (msg.type === 'recruiter_response') {
        setIsThinking(false);
        setMessages((prev) => [...prev, { id: Date.now().toString(), role: 'recruiter', text: msg.text }]);
        setTimeout(() => scrollViewRef.current?.scrollToEnd({ animated: true }), 100);
        return;
      }

      if (msg.type === 'voice') {
        void playVoiceAudioBase64(msg.audio);
        return;
      }

      if (msg.type === 'error') {
        setIsThinking(false);
        showToast(msg.message || "Erreur entretien.", 'error');
        setMessages((prev) => [...prev, { id: Date.now().toString(), role: 'system', text: msg.message }]);
        return;
      }
    };

    ws.onclose = () => {
      manualCloseRef.current = false;
      setIsInterviewRunning(false);
      setIsThinking(false);
      setWsStatus('idle');
    };
  };

  const startRecording = async () => {
    if (isThinking || !isInterviewRunning) return;
    try {
      const perm = await Audio.requestPermissionsAsync();
      if (perm.status !== 'granted') return showToast('Permission micro refusée.', 'error');

      if (audioSoundRef.current) {
        try { await audioSoundRef.current.stopAsync(); } catch {}
      }

      await Audio.setAudioModeAsync({ 
        allowsRecordingIOS: true, 
        playsInSilentModeIOS: true,
        staysActiveInBackground: false,
        playThroughEarpieceAndroid: false,
      });

      const recording = new Audio.Recording();
      recordingRef.current = recording;
      
      await recording.prepareToRecordAsync(Audio.RecordingOptionsPresets.LOW_QUALITY);
      await recording.startAsync();
      setIsRecording(true);
    } catch (err) {
      showToast('Erreur micro.', 'error');
    }
  };

  const transcribeAndSend = async (audioBase64: string) => {
    try {
      const token = await getAccessToken();
      const resp = await fetch(`${API_BASE_URL}/api/interview/transcribe`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ audio_base64: audioBase64 }),
      });
      
      const data = await resp.json();
      if (!resp.ok || data.status !== 'success' || !data.text) {
         showToast('Transcription impossible.', 'error');
         return;
      }

      const text = String(data.text || '').trim();
      if (!text) {
         showToast('Silence détecté.', 'warning');
         return;
      }

      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({ text }));
        setMessages((prev) => [...prev, { id: Date.now().toString(), role: 'user', text }]);
        setTimeout(() => scrollViewRef.current?.scrollToEnd({ animated: true }), 100);
      } else {
        showToast('Connexion perdue.', 'error');
      }
    } catch (err) {
      showToast('Erreur transcription.', 'error');
    }
  };

  const stopRecording = async () => {
    if (!recordingRef.current) return;
    setIsRecording(false);
    const recording = recordingRef.current;
    recordingRef.current = null;
    try {
      await recording.stopAndUnloadAsync();
      const uri = recording.getURI();
      if (!uri) return;
      setIsThinking(true);
      
      let audioBase64 = '';
      if (Platform.OS === 'web') {
        const res = await fetch(uri);
        const blob = await res.blob();
        audioBase64 = await new Promise<string>((resolve) => {
          const reader = new FileReader();
          reader.onloadend = () => {
             const dataUrl = reader.result as string;
             resolve(dataUrl.split(',')[1] || "");
          };
          reader.readAsDataURL(blob);
        });
      } else {
        audioBase64 = await FileSystem.readAsStringAsync(uri, { encoding: FileSystem.EncodingType.Base64 });
      }
      
      await transcribeAndSend(audioBase64);
    } catch (err) {
      showToast('Erreur arrêt enregistrement.', 'error');
    } finally {
      setIsThinking(false);
    }
  };

  const endCall = async () => {
    closeWs();
    
    // S'il y a trop peu de messages, on quitte sans analyser
    if (messages.length <= 2) {
      router.back();
      return;
    }

    setIsAnalyzing(true);
    try {
      const token = await getAccessToken();
      const payload = {
        history: messages.map(m => ({ role: m.role, content: m.text })),
        jobTitle: config?.jobTitle || '',
        company: config?.company || '',
        interviewType: config?.interviewType || 'general',
        recruiterId: config?.recruiterId || 'tech',
        startedAt: new Date(callStartTimeRef.current || Date.now()).toISOString(),
        endedAt: new Date().toISOString()
      };

      const resp = await fetch(`${API_BASE_URL}/api/interview/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify(payload)
      });
      
      const data = await resp.json();
      if (resp.ok && data.status === 'success' && data.session_id) {
        router.replace(`/(mentor)/mentor-simulator-result?sessionId=${data.session_id}`);
      } else {
        showToast("Erreur lors de l'analyse.", 'error');
        router.back();
      }
    } catch (err) {
      showToast("Impossible d'analyser l'entretien.", 'error');
      router.back();
    } finally {
      setIsAnalyzing(false);
    }
  };

  if (!config) return null;

  const recruiterInfo = RECRUITERS[config.recruiterId];

  return (
    <View style={styles.container}>
      <StatusBar style="light" />

      {showCalling && (
        <View style={styles.callingOverlay}>
          <BlurView intensity={80} tint="dark" style={styles.camera} />
          <View style={styles.callingContent}>
            <Image source={recruiterInfo.photo} style={styles.callingAvatar} />
            <Text style={styles.callingName}>{recruiterInfo.name}</Text>
            <Text style={styles.callingStatus}>Appel entrant...</Text>
          </View>
        </View>
      )}

      {isAnalyzing && (
        <View style={[styles.callingOverlay, { zIndex: 999 }]}>
          <BlurView intensity={90} tint="dark" style={styles.camera} />
          <View style={styles.callingContent}>
            <ActivityIndicator size="large" color="#4F46E5" />
            <Text style={[styles.callingName, { marginTop: 16 }]}>Génération du Bilan...</Text>
            <Text style={styles.callingStatus}>Analyse des compétences en cours</Text>
          </View>
        </View>
      )}

      <View style={styles.recruiterMainView}>
        <Image source={recruiterInfo.photo} style={styles.fullScreenImage} resizeMode="cover" />
        <BlurView intensity={25} tint="dark" style={styles.camera} />
        <View style={styles.vignette} />
        {isThinking && <View style={styles.thinkingGlow} />}
      </View>

      <View style={styles.userCameraPIP}>
        {hasPermission?.granted && Platform.OS !== 'web' ? (
          <CameraView style={styles.cameraFill} facing={facing} />
        ) : (
          <View style={styles.cameraPlaceholder}>
            <Ionicons name="videocam-off-outline" size={24} color="#4B5563" />
          </View>
        )}
      </View>

      <View style={[styles.headerOverlay, { paddingTop: insets.top + 10 }]}>
        <View style={styles.headerTitleContainer}>
          <Image source={recruiterInfo.photo} style={styles.recruiterAvatarSmall} />
          <View>
            <Text style={styles.recruiterName}>{recruiterInfo.name}</Text>
            <View style={styles.callMeta}>
               <View style={styles.liveBadge} />
               <Text style={styles.callTime}>{callElapsed}</Text>
            </View>
          </View>
        </View>
        <TouchableOpacity style={styles.flipButton} onPress={() => setFacing(f => f === 'front' ? 'back' : 'front')}>
          <Ionicons name="camera-reverse-outline" size={24} color="#FFF" />
        </TouchableOpacity>
      </View>

      <View style={styles.chatOverlay}>
        <ScrollView 
          ref={scrollViewRef}
          contentContainerStyle={styles.chatScroll}
          showsVerticalScrollIndicator={false}
        >
          {messages.map((m) => (
            <View key={m.id} style={[styles.messageBubble, m.role === 'user' ? styles.bubbleUser : styles.bubbleRecruiter]}>
              {m.role === 'recruiter' && <Text style={styles.messageName}>{recruiterInfo.name}</Text>}
              <Text style={styles.messageText}>{m.text}</Text>
            </View>
          ))}
          {isThinking && (
             <View style={styles.thinkingIndicator}>
               <ActivityIndicator size="small" color="#A5B4FC" />
               <Text style={styles.thinkingText}>L'IA prépare sa réponse...</Text>
             </View>
          )}
        </ScrollView>
      </View>

      <View style={[styles.bottomControls, { paddingBottom: insets.bottom + 20 }]}>
         <TouchableOpacity style={[styles.controlButton, styles.endCallButton]} onPress={endCall}>
           <Ionicons name="call" size={24} color="#FFF" style={{ transform: [{ rotate: '135deg' }] }} />
         </TouchableOpacity>
         <TouchableOpacity 
           style={[styles.mainMicButton, isRecording && styles.mainMicButtonActive]} 
           onPress={isRecording ? stopRecording : startRecording}
           disabled={isThinking || wsStatus !== 'connected'}
         >
           <Ionicons name={isRecording ? "stop" : "mic"} size={36} color="#FFF" />
           {isRecording && <View style={styles.pulseRing} />}
         </TouchableOpacity>
         <View style={styles.controlButtonDummy} />
      </View>
    </View>
  );
}
