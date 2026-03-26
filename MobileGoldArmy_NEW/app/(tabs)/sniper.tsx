import React, { useState, useEffect, useRef } from 'react';
import { View, Text, ScrollView, KeyboardAvoidingView, Platform, TouchableOpacity, Animated, ActivityIndicator, Linking } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { Input } from '../../src/components/ui/Input';
import { spacing } from '../../src/theme/spacing';
import { StatusBar } from 'expo-status-bar';
import { sniperService, SniperError } from '../../src/services/sniperService';
import { cvService, CvUploadError } from '../../src/services/cvService';
import { taskService } from '../../src/services/taskService';
import { SniperJob } from '../../src/types/sniper.types';
import { useUIStore } from '../../src/stores/uiStore';
import * as Haptics from 'expo-haptics';
import { useRouter } from 'expo-router';
import { crmService } from '../../src/services/crmService';
import { PaywallModal } from '../../src/components/ui/PaywallModal';
import { styles } from './_styles/sniper.styles';

export default function SniperScreen() {
  const insets = useSafeAreaInsets();
  const { showToast } = useUIStore();
  const router = useRouter();
  const [query, setQuery] = useState('');
  const [location, setLocation] = useState('');
  const [limit, setLimit] = useState(20);
  const [isSearching, setIsSearching] = useState(false);
  const [cvFileName, setCvFileName] = useState<string | null>(null);
  const [cvText, setCvText] = useState<string | null>(null);
  const [isUploadingCv, setIsUploadingCv] = useState(false);
  const [jobs, setJobs] = useState<SniperJob[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [hasSearched, setHasSearched] = useState(false);
  const [showPaywall, setShowPaywall] = useState(false);
  const [activeTaskId, setActiveTaskId] = useState<string | null>(null);
  const pollingInterval = useRef<any>(null);
  const isBackgroundMode = useRef(false);
  const progressAnim = useRef(new Animated.Value(0)).current;
  const [loadingProgress, setLoadingProgress] = useState(0);
  const [loadingMessage, setLoadingMessage] = useState('Lancement du scan...');

  // Animations
  const headerAnim = useRef(new Animated.Value(0)).current;
  const formAnim = useRef(new Animated.Value(0)).current;
  const resultsAnim = useRef(new Animated.Value(0)).current;
  const radarAnim = useRef(new Animated.Value(0)).current;
  const searchBtnAnim = useRef(new Animated.Value(1)).current;

  useEffect(() => {
    // Initial Staggered Entrance
    Animated.stagger(150, [
      Animated.timing(headerAnim, { toValue: 1, duration: 500, useNativeDriver: true }),
      Animated.timing(formAnim, { toValue: 1, duration: 500, useNativeDriver: true }),
      Animated.timing(resultsAnim, { toValue: 1, duration: 500, useNativeDriver: true }),
    ]).start();

    // Continuous Radar Pulse
    Animated.loop(
      Animated.sequence([
        Animated.timing(radarAnim, { toValue: 1, duration: 2000, useNativeDriver: true }),
        Animated.timing(radarAnim, { toValue: 0, duration: 2000, useNativeDriver: true })
      ])
    ).start();

    // Check for existing pending tasks on mount
    const checkActiveTasks = async () => {
      const recent = await taskService.getRecentTasks();
      const pending = recent.find(t => t.type === 'sniper' && t.status === 'pending');
      if (pending) {
        setActiveTaskId(pending.id);
        setIsSearching(true);
        startPolling(pending.id);
      }
    };
    checkActiveTasks();

    return () => {
      if (pollingInterval.current) clearInterval(pollingInterval.current);
    };
  }, []);

  const handleUploadCv = async () => {
    if (isUploadingCv) return;
    setIsUploadingCv(true);
    
    try {
      await Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
      const result = await cvService.pickAndUploadCv();
      setCvFileName(result.filename);
      setCvText(result.text);
      showToast('CV uploadé avec succès !', 'success');
      await Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
    } catch (error: any) {
      console.error('[Sniper][CV Upload Error]', error);
      if (error instanceof CvUploadError) {
        if (error.code === 'CANCELLED') return;
        showToast(error.message, 'error');
      } else {
        showToast('Erreur lors de l\'upload du CV', 'error');
      }
      await Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error);
    } finally {
      setIsUploadingCv(false);
    }
  };

  const handleSearch = async () => {
    if (isSearching || !query.trim()) {
      if (!query.trim()) {
        showToast('Veuillez saisir un poste à rechercher', 'warning');
      }
      return;
    }

    setIsSearching(true);
    setError(null);
    setHasSearched(true);
    
    Animated.sequence([
      Animated.timing(searchBtnAnim, { toValue: 0.95, duration: 100, useNativeDriver: true }),
      Animated.timing(searchBtnAnim, { toValue: 1, duration: 100, useNativeDriver: true })
    ]).start();

    Animated.timing(resultsAnim, { toValue: 0, duration: 200, useNativeDriver: true }).start();

    try {
      await Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
      const result = await sniperService.searchJobs({
        query: query.trim(),
        location: location.trim() || 'Montréal',
        limit,
        cv_text: cvText || undefined,
        cv_filename: cvFileName || undefined,
        background: true // Force background mode for persistence
      });
 
      if ('status' in result && result.status === 'pending') {
        isBackgroundMode.current = true;
        setActiveTaskId(result.task_id);
        startPolling(result.task_id);
        showToast('Scan lancé en arrière-plan', 'info');
        // DON'T call setIsSearching(false) - polling will do it
        return;
      } else if ('matched_jobs' in result) {
        setJobs(result.matched_jobs || []);
        if (result.matched_jobs && result.matched_jobs.length > 0) {
          showToast(`${result.total_jobs_found} offres trouvées !`, 'success');
          await Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
        } else {
          showToast('Aucune offre trouvée pour cette recherche', 'info');
        }
        setIsSearching(false);
      }
 
      Animated.timing(resultsAnim, { toValue: 1, duration: 400, useNativeDriver: true }).start();
    } catch (err: any) {
      console.error('[Sniper][Search Error]', err);
      let errorMessage = 'Erreur lors de la recherche';
      let toastType: 'error' | 'warning' = 'error';
      
      if (err instanceof SniperError) {
        errorMessage = err.message;
        if (err.type === 'limit_reached') {
          toastType = 'warning';
        }
      } else if (err.response?.data) {
        const data = err.response.data;
        if (data.type === 'limit_reached') {
          errorMessage = data.content || 'Quota de recherche atteint. Passe à un plan supérieur pour continuer.';
          toastType = 'warning';
        } else if (data.message) {
          errorMessage = data.message;
        }
      } else if (err.message) {
        errorMessage = err.message;
      }

      if (toastType === 'warning') {
        setShowPaywall(true);
        setError(null);
      } else {
        showToast(errorMessage, toastType);
        setError(errorMessage);
      }
      
      setJobs([]);
      await Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error);
      Animated.timing(resultsAnim, { toValue: 1, duration: 400, useNativeDriver: true }).start();
    } finally {
      // Only set isSearching false if NOT in background polling mode
      if (!isBackgroundMode.current) {
        setIsSearching(false);
      }
    }
  };

  const LOADING_MESSAGES = [
    'Scan des offres en cours...',
    'Analyse de votre profil...',
    'Filtrage par pertinence...',
    'Application des critères IA...',
    'Presque terminé...',
  ];

  const startPolling = (taskId: string) => {
    if (pollingInterval.current) clearInterval(pollingInterval.current);
    let tick = 0;
    const maxTicks = 40; // ~2min max

    // Animate progress bar
    const animateProgress = (target: number) => {
      Animated.timing(progressAnim, {
        toValue: target,
        duration: 2800,
        useNativeDriver: false,
      }).start();
    };
    animateProgress(0.15);
    setLoadingProgress(15);
    setLoadingMessage(LOADING_MESSAGES[0]);

    pollingInterval.current = setInterval(async () => {
      tick++;
      // Update progress and message
      const progress = Math.min(0.9, 0.15 + (tick / maxTicks) * 0.75);
      const msgIndex = Math.min(Math.floor(tick / 8), LOADING_MESSAGES.length - 1);
      setLoadingProgress(Math.round(progress * 100));
      setLoadingMessage(LOADING_MESSAGES[msgIndex]);
      animateProgress(progress);

      const task = await taskService.getTask(taskId);
      if (!task) return;

      if (task.status === 'completed') {
        if (pollingInterval.current) clearInterval(pollingInterval.current);
        isBackgroundMode.current = false;
        // Animate to 100%
        Animated.timing(progressAnim, { toValue: 1, duration: 400, useNativeDriver: false }).start();
        setLoadingProgress(100);
        // task.result = { type: "job_search_results", content: { matched_jobs: [...] } }
        const content = task.result?.content || task.result || {};
        const foundJobs = content.matched_jobs || [];
        setJobs(foundJobs);
        setIsSearching(false);
        setActiveTaskId(null);
        showToast(`Scan terminé — ${foundJobs.length} offres trouvées !`, 'success');
        Animated.timing(resultsAnim, { toValue: 1, duration: 400, useNativeDriver: true }).start();
        Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
      } else if (task.status === 'failed') {
        if (pollingInterval.current) clearInterval(pollingInterval.current);
        isBackgroundMode.current = false;
        setIsSearching(false);
        setActiveTaskId(null);
        setError("Le scan a échoué. Réessayez.");
        showToast('Le scan a échoué', 'error');
        Animated.timing(resultsAnim, { toValue: 1, duration: 400, useNativeDriver: true }).start();
      }
    }, 3000);
  };

  return (
    <KeyboardAvoidingView
      style={styles.root}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
    >
      <StatusBar style="dark" />
      <ScrollView
        style={styles.scroll}
        contentContainerStyle={[
          styles.content,
          { paddingTop: insets.top + spacing.xl, paddingBottom: insets.bottom + 100 },
        ]}
        keyboardShouldPersistTaps="handled"
        showsVerticalScrollIndicator={false}
      >
        <Animated.View style={[
          styles.hero,
          {
            opacity: headerAnim,
            transform: [{ translateY: headerAnim.interpolate({ inputRange: [0, 1], outputRange: [20, 0] }) }]
          }
        ]}>
          <View style={styles.heroHeader}>
            <View style={styles.radarContainer}>
              <Animated.View style={[
                styles.radarRing,
                {
                  transform: [{ scale: radarAnim.interpolate({ inputRange: [0, 1], outputRange: [1, 2.5] }) }],
                  opacity: radarAnim.interpolate({ inputRange: [0, 1], outputRange: [0.3, 0] })
                }
              ]} />
              <View style={styles.heroIcon}>
                <Ionicons name="scan-outline" size={24} color="#1A1A1A" />
              </View>
            </View>
            <View style={styles.heroTextContainer}>
              <Text style={styles.heroTitle}>Sniper IA</Text>
              <Text style={styles.heroSubtitle}>Cible les offres les plus pertinentes.</Text>
            </View>
          </View>
        </Animated.View>

        <Animated.View style={[
          styles.formCard,
          {
            opacity: formAnim,
            transform: [{ translateY: formAnim.interpolate({ inputRange: [0, 1], outputRange: [20, 0] }) }]
          }
        ]}>
          <TouchableOpacity 
            style={[styles.cvArea, isUploadingCv && styles.cvAreaDisabled]} 
            onPress={handleUploadCv} 
            activeOpacity={0.7}
            disabled={isUploadingCv}
          >
            {isUploadingCv ? (
              <ActivityIndicator size="small" color="#F5D061" style={{ marginRight: spacing.md }} />
            ) : (
              <View style={[styles.cvIconHolder, cvFileName && styles.cvIconHolderActive]}>
                <Ionicons name={cvFileName ? "document-text" : "cloud-upload-outline"} size={22} color={cvFileName ? "#F5D061" : "#A1A1AA"} />
              </View>
            )}
            <View style={styles.cvInfo}>
              <Text style={styles.cvLabel}>CV utilisé par l'IA</Text>
              <Text style={styles.cvSubLabel}>
                {isUploadingCv 
                  ? 'Upload en cours...' 
                  : cvFileName 
                    ? cvFileName 
                    : 'Toucher pour importer un CV (.pdf)'}
              </Text>
            </View>
            {cvFileName && !isUploadingCv && (
              <Ionicons name="checkmark-circle" size={20} color="#10B981" />
            )}
          </TouchableOpacity>

          <View style={styles.inputsWrapper}>
            <Input
              label="Poste visé"
              value={query}
              onChangeText={setQuery}
              leftIcon={<Ionicons name="briefcase-outline" size={18} color="#A1A1AA" />}
              placeholder="Ex : Product Designer, Dev Frontend…"
            />
            <Input
              label="Localisation"
              value={location}
              onChangeText={setLocation}
              leftIcon={<Ionicons name="location-outline" size={18} color="#A1A1AA" />}
              placeholder="Ville ou pays"
            />
          </View>

          <Animated.View style={{ transform: [{ scale: searchBtnAnim }] }}>
            <TouchableOpacity
              style={[styles.searchButton, (isSearching || !query.trim()) && styles.searchButtonDisabled]}
              activeOpacity={0.9}
              onPress={handleSearch}
              disabled={isSearching || !query.trim()}
            >
              {isSearching ? (
                <ActivityIndicator size="small" color="#1A1A1A" style={{ marginRight: 8 }} />
              ) : (
                <Ionicons name="search" size={20} color="#1A1A1A" style={{ marginRight: 8 }} />
              )}
              <Text style={styles.searchButtonText}>
                {isSearching ? 'Analyse des offres en cours…' : 'Lancer le Scan Sniper'}
              </Text>
            </TouchableOpacity>
          </Animated.View>
        </Animated.View>

        {hasSearched && (
          <Animated.View style={[
            styles.resultsSection,
            {
              opacity: resultsAnim,
              transform: [{ translateY: resultsAnim.interpolate({ inputRange: [0, 1], outputRange: [20, 0] }) }]
            }
          ]}>
            <View style={styles.resultsHeader}>
              <Text style={styles.resultsTitle}>Matchs Potentiels</Text>
              {jobs.length > 0 && (
                <View style={styles.resultsCountBadge}>
                  <Text style={styles.resultsCountText}>{jobs.length}</Text>
                </View>
              )}
            </View>
            {isSearching && (
              <View style={{
                backgroundColor: '#FFFFFF',
                borderRadius: 20,
                padding: 20,
                marginBottom: 16,
                borderWidth: 1,
                borderColor: '#F0F0EA',
                shadowColor: '#F5D061',
                shadowOffset: { width: 0, height: 4 },
                shadowOpacity: 0.15,
                shadowRadius: 12,
                elevation: 4,
              }}>
                <View style={{ flexDirection: 'row', alignItems: 'center', marginBottom: 12 }}>
                  <ActivityIndicator size="small" color="#F5D061" style={{ marginRight: 10 }} />
                  <Text style={{ fontSize: 14, fontWeight: '700', color: '#1A1A1A', flex: 1 }}>{loadingMessage}</Text>
                  <Text style={{ fontSize: 13, fontWeight: '800', color: '#F5D061' }}>{loadingProgress}%</Text>
                </View>
                <View style={{ height: 6, backgroundColor: '#F0F0EA', borderRadius: 3, overflow: 'hidden' }}>
                  <Animated.View style={{
                    height: '100%',
                    borderRadius: 3,
                    backgroundColor: '#F5D061',
                    width: progressAnim.interpolate({ inputRange: [0, 1], outputRange: ['0%', '100%'] }),
                  }} />
                </View>
                <Text style={{ fontSize: 11, color: '#A0A0A0', marginTop: 8 }}>Les résultats s'afficheront automatiquement ici</Text>
              </View>
            )}
            {!isSearching && error && (
              <View style={styles.errorCard}>
                <Ionicons name="alert-circle-outline" size={20} color="#E53935" style={{ marginRight: 8 }} />
                <Text style={styles.errorText}>{error}</Text>
              </View>
            )}
            {!isSearching && jobs.length === 0 && !error && (
              <View style={styles.emptyState}>
                <Ionicons name="search-outline" size={48} color="#CCCCCC" />
                <Text style={styles.emptyTitle}>Aucun résultat</Text>
                <Text style={styles.emptySubtitle}>Essaie avec d'autres mots-clés ou une autre localisation</Text>
              </View>
            )}
            {jobs.length > 0 && (
              <View style={styles.resultsList}>
                {jobs.map((job, index) => (
                  <View key={`${job.id || 'job'}-${index}`} style={styles.jobCard}>
                    <TouchableOpacity 
                      activeOpacity={0.7}
                      onPress={() => {
                        router.push({
                          pathname: '/opportunity-details',
                          params: { job: JSON.stringify(job) },
                        });
                      }}
                    >
                      <View style={styles.jobContent}>
                        <View style={styles.jobMain}>
                          <Text style={styles.jobTitle}>{job.title}</Text>
                          <View style={styles.jobCompanyRow}>
                            <Ionicons name="business-outline" size={14} color="#666666" style={{marginRight: 4}} />
                            <Text style={styles.jobCompany}>{job.company}</Text>
                          </View>
                          <View style={styles.jobLocationRow}>
                            <Ionicons name="location-outline" size={14} color="#999999" style={{marginRight: 4}} />
                            <Text style={styles.jobLocation}>{job.location}</Text>
                          </View>
                          {job.salary && (
                            <View style={styles.jobSalaryRow}>
                              <Ionicons name="cash-outline" size={14} color="#15803D" style={{ marginRight: 4 }} />
                              <Text style={styles.jobSalary}>{job.salary}</Text>
                            </View>
                          )}
                          <View style={styles.jobMetaRow}>
                            {job.type && (
                              <View style={styles.jobMetaPill}>
                                <Ionicons name="briefcase-outline" size={12} color="#4B5563" style={{ marginRight: 4 }} />
                                <Text style={styles.jobMetaText}>{job.type}</Text>
                              </View>
                            )}
                            {job.posted_date && (
                              <View style={styles.jobMetaPill}>
                                <Ionicons name="time-outline" size={12} color="#4B5563" style={{ marginRight: 4 }} />
                                <Text style={styles.jobMetaText}>{job.posted_date}</Text>
                              </View>
                            )}
                          </View>
                          {job.description && (
                            <Text numberOfLines={2} style={styles.jobSnippet}>
                              {job.description}
                            </Text>
                          )}
                        </View>
                        <View style={styles.jobRight}>
                          <View style={styles.matchBadge}>
                            <Ionicons name="flash" size={12} color="#D97706" style={{marginRight: 2}} />
                            <Text style={styles.matchText}>{Math.round(job.match_score)}%</Text>
                          </View>
                          <View style={styles.sourceTag}>
                            <Text style={styles.sourceText}>{job.source || 'N/A'}</Text>
                          </View>
                        </View>
                      </View>
                      <View style={styles.cardActionsRow}>
                        <TouchableOpacity
                          style={styles.applyButton}
                          activeOpacity={0.85}
                          onPress={async () => {
                            if (job.url) {
                              Linking.openURL(job.url).catch(() => {
                                showToast("Impossible d'ouvrir le lien de l'offre.", 'error');
                              });
                              try {
                                await crmService.createCandidature({
                                  url: job.url,
                                  title: job.title,
                                  company: job.company,
                                  status: 'a_postuler',
                                  notes: job.source ? `Sniper AI - Source: ${job.source}` : 'Sniper AI',
                                });
                                showToast("Candidature ajoutée automatiquement au CRM !", 'success');
                              } catch(e) {
                                console.error("[Sniper] Error auto-saving to CRM", e);
                              }
                            } else {
                              showToast("Lien de l'offre indisponible.", 'warning');
                            }
                          }}
                        >
                          <Ionicons name="paper-plane-outline" size={16} color="#FFFFFF" style={{ marginRight: 6 }} />
                          <Text style={styles.applyButtonText}>Postuler</Text>
                        </TouchableOpacity>
                        {job.url && (
                          <TouchableOpacity
                            style={styles.secondaryButton}
                            activeOpacity={0.85}
                            onPress={() => {
                              router.push({
                                pathname: '/opportunity-details',
                                params: { job: JSON.stringify(job) },
                              });
                            }}
                          >
                            <Text style={styles.secondaryButtonText}>Voir l'offre</Text>
                          </TouchableOpacity>
                        )}
                      </View>
                    </TouchableOpacity>
                  </View>
                ))}
              </View>
            )}
          </Animated.View>
        )}
      </ScrollView>
      <PaywallModal 
        visible={showPaywall} 
        onClose={() => setShowPaywall(false)} 
      />
    </KeyboardAvoidingView>
  );
}
