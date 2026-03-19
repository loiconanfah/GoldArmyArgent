import React, { useState, useEffect, useRef } from 'react';
import { View, Text, ScrollView, KeyboardAvoidingView, Platform, TouchableOpacity, Animated, ActivityIndicator, Linking } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { Input } from '../../src/components/ui/Input';
import { spacing } from '../../src/theme/spacing';
import { StatusBar } from 'expo-status-bar';
import { sniperService, SniperError } from '../../src/services/sniperService';
import { cvService, CvUploadError } from '../../src/services/cvService';
import { SniperJob } from '../../src/types/sniper.types';
import { useUIStore } from '../../src/stores/uiStore';
import * as Haptics from 'expo-haptics';
import { useRouter } from 'expo-router';
import { styles } from './styles/sniper.styles';

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
      });

      setJobs(result.matched_jobs || []);
      
      if (result.matched_jobs && result.matched_jobs.length > 0) {
        showToast(`${result.total_jobs_found} offres trouvées !`, 'success');
        await Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
      } else {
        showToast('Aucune offre trouvée pour cette recherche', 'info');
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

      showToast(errorMessage, toastType);
      setError(errorMessage);
      setJobs([]);
      await Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error);
      Animated.timing(resultsAnim, { toValue: 1, duration: 400, useNativeDriver: true }).start();
    } finally {
      setIsSearching(false);
    }
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
            {error && (
              <View style={styles.errorCard}>
                <Ionicons name="alert-circle-outline" size={20} color="#E53935" style={{ marginRight: 8 }} />
                <Text style={styles.errorText}>{error}</Text>
              </View>
            )}
            {jobs.length === 0 && !error && (
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
                          onPress={() => {
                            if (job.url) {
                              Linking.openURL(job.url).catch(() => {
                                showToast("Impossible d'ouvrir le lien de l'offre.", 'error');
                              });
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
    </KeyboardAvoidingView>
  );
}
