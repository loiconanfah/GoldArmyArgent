import React, { useEffect, useState } from 'react';
import { 
  View, 
  Text, 
  ScrollView, 
  TouchableOpacity, 
  ActivityIndicator, 
  RefreshControl,
  Modal,
  TextInput,
  Alert,
  Image
} from 'react-native';
import { StatusBar } from 'expo-status-bar';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';
import { BlurView } from 'expo-blur';
import { spacing } from '../../src/theme/spacing';
import { profileService, UserProfile } from '../../src/services/profileService';
import { taskService } from '../../src/services/taskService';
import { useAuth } from '../../src/hooks/useAuth';
import { styles } from './_styles/profile.styles';
import * as ImagePicker from 'expo-image-picker';
import * as DocumentPicker from 'expo-document-picker';
import * as Haptics from 'expo-haptics';
import { useRouter } from 'expo-router';

export default function ProfileScreen() {
  const insets = useSafeAreaInsets();
  const router = useRouter();
  const { logout } = useAuth();
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  
  // Edit states
  const [isEditModalVisible, setIsEditModalVisible] = useState(false);
  const [editType, setEditType] = useState<'info' | 'cv'>('info');
  const [tempName, setTempName] = useState('');
  const [tempCv, setTempCv] = useState('');
  const [isSaving, setIsSaving] = useState(false);

  const fetchProfile = async () => {
    try {
      const data = await profileService.getProfile();
      setProfile(data);
    } catch (err) {
      console.error('[ProfileScreen] Fetch error:', err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchProfile();
    
    // Check for pending CV analysis on mount
    const checkActiveTasks = async () => {
      const recent = await taskService.getRecentTasks();
      const pending = recent.find(t => t.type === 'cv_analysis' && t.status === 'pending');
      if (pending) {
        setIsSaving(true);
        startCvPolling(pending.id);
      }
    };
    checkActiveTasks();
  }, []);

  const onRefresh = () => {
    setRefreshing(true);
    fetchProfile();
  };

  const openEdit = (type: 'info' | 'cv') => {
    setEditType(type);
    setTempName(profile?.full_name || '');
    setTempCv(profile?.cv_text || '');
    setIsEditModalVisible(true);
  };

  const pickImage = async () => {
    try {
      let result = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: ['images'],
        allowsEditing: true,
        aspect: [1, 1],
        quality: 1,
      });

      if (!result.canceled) {
        const selectedUri = result.assets[0].uri;
        setIsSaving(true);
        try {
          // Use proper fastAPI file upload instead of sending JSON with local URI
          const res = await profileService.uploadAvatar(selectedUri);
          setProfile(prev => prev ? { ...prev, avatar_url: res.avatar_url } : null);
        } catch (err: any) {
          // Fallback to local state if backend doesn't support it yet
          setProfile(prev => prev ? { ...prev, avatar_url: selectedUri } : null);
        } finally {
          setIsSaving(false);
        }
      }
    } catch (error) {
       Alert.alert("Erreur", "Impossible d'ouvrir la galerie.");
    }
  };

  const pickAndUploadCV = async () => {
    try {
      const result = await DocumentPicker.getDocumentAsync({
        type: 'application/pdf',
        copyToCacheDirectory: true,
      });

      if (!result.canceled && result.assets && result.assets.length > 0) {
        setIsSaving(true);
        const fileUri = result.assets[0].uri;
        try {
          const res = await profileService.uploadCv(fileUri, true); // Use background mode
          if (res.status === 'pending' && res.task_id) {
            startCvPolling(res.task_id);
            showToast('Analyse lancée en arrière-plan', 'info');
          } else if (res.text) {
            setProfile(prev => prev ? { ...prev, cv_text: res.text } : null);
            Alert.alert("Succès", "Ton CV a été mis à jour.");
            setIsSaving(false);
          }
        } catch (err: any) {
          Alert.alert("Erreur", "Impossible d'uploader le CV.");
          setIsSaving(false);
        }
      }
    } catch (err) {
      console.error(err);
      Alert.alert("Erreur", "Oups, une erreur est survenue.");
      setIsSaving(false);
    }
  };

  const startCvPolling = (taskId: string) => {
    const interval = setInterval(async () => {
      const task = await taskService.getTask(taskId);
      if (!task) return;

      if (task.status === 'completed') {
        clearInterval(interval);
        setProfile(prev => prev ? { ...prev, cv_text: task.result?.text } : null);
        setIsSaving(false);
        showToast('Analyse CV terminée !', 'success');
        Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
      } else if (task.status === 'failed') {
        clearInterval(interval);
        setIsSaving(false);
        showToast('L\'analyse du CV a échoué', 'error');
      }
    }, 3000);
  };

  const showToast = (msg: string, type: 'success' | 'error' | 'info') => {
    // Basic toast mock if no global toast, though UIStore usually handles it
    Alert.alert(type.toUpperCase(), msg);
  };

  const handleSave = async () => {
    setIsSaving(true);
    try {
      const payload: Partial<UserProfile> = editType === 'info' 
        ? { full_name: tempName } 
        : { cv_text: tempCv };
      
      const updated = await profileService.updateProfile(payload);
      setProfile(updated);
      setIsEditModalVisible(false);
      Alert.alert("Succès", "Ton profil a été mis à jour.");
    } catch (err: any) {
      Alert.alert("Erreur", err.message || "Impossible de sauvegarder.");
    } finally {
      setIsSaving(false);
    }
  };

  if (loading && !refreshing) {
    return (
      <View style={[styles.root, { justifyContent: 'center', alignItems: 'center' }]}>
        <ActivityIndicator size="large" color="#F5D061" />
      </View>
    );
  }

  return (
    <View style={styles.root}>
      <StatusBar style="dark" />
      <ScrollView
        style={styles.scroll}
        contentContainerStyle={[
          styles.content,
          { paddingTop: insets.top + spacing.lg }
        ]}
        showsVerticalScrollIndicator={false}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor="#F5D061" />
        }
      >
        {/* HERO SECTION */}
        <View style={styles.heroSection}>
          <View style={{ width: '100%', alignItems: 'flex-end', paddingRight: 10, zIndex: 999 }}>
            <TouchableOpacity 
              style={{ padding: 10 }}
              hitSlop={{ top: 15, bottom: 15, left: 15, right: 15 }}
              onPress={() => router.push('/settings' as any)}
            >
              <Ionicons name="settings-outline" size={32} color="#1A1A1A" />
            </TouchableOpacity>
          </View>

          <View style={styles.avatarContainer}>
            <View style={styles.avatar}>
               {profile?.avatar_url ? (
                 <Image source={{ uri: profile.avatar_url }} style={{ width: '100%', height: '100%', borderRadius: 50, resizeMode: 'cover' }} />
               ) : (
                 <Ionicons name="person" size={60} color="#666" style={{ marginTop: 20, alignSelf: 'center' }} />
               )}
            </View>
            <TouchableOpacity style={styles.editAvatarBtn} activeOpacity={0.8} onPress={pickImage}>
              <Ionicons name="camera" size={16} color="#FFF" />
            </TouchableOpacity>
          </View>
          <Text style={styles.userName}>{profile?.full_name || "Agent GoldArmy"}</Text>
          <Text style={styles.userEmail}>{profile?.email}</Text>
          
          <View style={styles.tierBadge}>
            <Ionicons name="shield-checkmark" size={14} color="#F5D061" />
            <Text style={styles.tierText}>{profile?.subscription_tier || 'Recrue'}</Text>
          </View>
        </View>

        {/* BENTO STATS (Mocked for UI) */}
        <View style={styles.statsRow}>
          <View style={styles.statCard}>
            <Text style={styles.statValue}>12</Text>
            <Text style={styles.statLabel}>Quêtes Actives</Text>
          </View>
          <View style={styles.statCard}>
            <Text style={styles.statValue}>85%</Text>
            <Text style={styles.statLabel}>Fiabilité CV</Text>
          </View>
        </View>

        {/* ACCOUNT INFO */}
        <View style={styles.section}>
          <View style={styles.sectionHeader}>
            <Text style={styles.sectionTitle}>Identité & Accès</Text>
            <TouchableOpacity onPress={() => openEdit('info')}>
              <Text style={styles.editLink}>Modifier</Text>
            </TouchableOpacity>
          </View>
          <View style={styles.infoCard}>
            <View style={styles.infoItem}>
              <View style={styles.infoIconBox}>
                <Ionicons name="person-outline" size={18} color="#6366F1" />
              </View>
              <View>
                <Text style={styles.infoLabel}>Nom complet</Text>
                <Text style={styles.infoValue}>{profile?.full_name || 'Non renseigné'}</Text>
              </View>
            </View>
            <View style={styles.infoItem}>
              <View style={styles.infoIconBox}>
                <Ionicons name="mail-outline" size={18} color="#10B981" />
              </View>
              <View>
                <Text style={styles.infoLabel}>E-mail de secours</Text>
                <Text style={styles.infoValue}>{profile?.email}</Text>
              </View>
            </View>
          </View>
        </View>

        {/* CV TEXT SECTION */}
        <View style={styles.section}>
          <View style={styles.sectionHeader}>
            <Text style={styles.sectionTitle}>Cœur de Profil (CV Alpha)</Text>
            <TouchableOpacity onPress={pickAndUploadCV}>
              <Text style={styles.editLink}>Uploader un PDF</Text>
            </TouchableOpacity>
          </View>
          <View style={styles.cvCard}>
            <View style={styles.cvTextContainer}>
              <Text style={styles.cvText} numberOfLines={8}>
                {profile?.cv_text || "Aucun texte de CV extrait pour le moment. Télécharge ton CV dans le Sniper pour activer l'IA."}
              </Text>
            </View>
          </View>
        </View>

        {/* LOGOUT */}
        <TouchableOpacity style={styles.logoutBtn} onPress={logout} activeOpacity={0.8}>
          <Ionicons name="log-out-outline" size={20} color="#EF4444" />
          <Text style={styles.logoutText}>Déconnexion</Text>
        </TouchableOpacity>
      </ScrollView>

      {/* EDIT MODAL */}
      <Modal
        visible={isEditModalVisible}
        transparent={true}
        animationType="slide"
        onRequestClose={() => setIsEditModalVisible(false)}
      >
        <View style={styles.modalOverlay}>
          <TouchableOpacity 
             style={{ flex: 1 }} 
             activeOpacity={1} 
             onPress={() => setIsEditModalVisible(false)} 
          />
          <View style={styles.modalContent}>
            <Text style={styles.modalTitle}>
               {editType === 'info' ? "Modifier l'identité" : "Mise à jour CV"}
            </Text>
            
            {editType === 'info' && (
              <>
                <Text style={styles.inputLabel}>Nom complet</Text>
                <TextInput
                  style={styles.input}
                  value={tempName}
                  onChangeText={setTempName}
                  placeholder="Jean Dupont"
                />
              </>
            )}

            <TouchableOpacity 
              style={styles.saveBtn} 
              onPress={handleSave}
              disabled={isSaving}
            >
              {isSaving ? (
                <ActivityIndicator color="#FFF" />
              ) : (
                <Text style={styles.saveBtnText}>Sauvegarder</Text>
              )}
            </TouchableOpacity>
            
            <TouchableOpacity 
              style={styles.cancelBtn} 
              onPress={() => setIsEditModalVisible(false)}
            >
              <Text style={styles.cancelBtnText}>Annuler</Text>
            </TouchableOpacity>
          </View>
        </View>
      </Modal>
    </View>
  );
}
