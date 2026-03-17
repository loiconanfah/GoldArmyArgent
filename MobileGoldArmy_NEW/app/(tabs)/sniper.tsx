import React, { useState, useEffect, useRef } from 'react';
import { View, Text, StyleSheet, ScrollView, KeyboardAvoidingView, Platform, TouchableOpacity, Animated } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { Input } from '../../src/components/ui/Input';
import { spacing } from '../../src/theme/spacing';
import { StatusBar } from 'expo-status-bar';

interface SniperJob {
  id: string;
  title: string;
  company: string;
  location: string;
  source: string;
  match: number;
}

const MOCK_JOBS: SniperJob[] = [
  {
    id: '1',
    title: 'Product Designer Senior',
    company: 'Stripe',
    location: 'Remote · Montréal',
    source: 'LinkedIn',
    match: 92,
  },
  {
    id: '2',
    title: 'UX/UI Designer',
    company: 'Figma',
    location: 'Hybrid · Paris',
    source: 'Indeed',
    match: 88,
  },
  {
    id: '3',
    title: 'Product Designer',
    company: 'Airbnb',
    location: 'Remote · Europe',
    source: 'Direct',
    match: 84,
  },
];

export default function SniperScreen() {
  const insets = useSafeAreaInsets();
  const [query, setQuery] = useState('Product Designer');
  const [location, setLocation] = useState('Montréal');
  const [limit, setLimit] = useState('20');
  const [isSearching, setIsSearching] = useState(false);
  const [cvFileName, setCvFileName] = useState<string | null>(null);

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

  const handleUploadCv = () => {
    setCvFileName('mon_cv.pdf');
  };

  const handleSearch = () => {
    if (isSearching) return;
    setIsSearching(true);
    
    // Press animation
    Animated.sequence([
      Animated.timing(searchBtnAnim, { toValue: 0.95, duration: 100, useNativeDriver: true }),
      Animated.timing(searchBtnAnim, { toValue: 1, duration: 100, useNativeDriver: true })
    ]).start();

    // Hide results, wait, show results
    Animated.timing(resultsAnim, { toValue: 0, duration: 200, useNativeDriver: true }).start(() => {
      setTimeout(() => {
        setIsSearching(false);
        Animated.timing(resultsAnim, { toValue: 1, duration: 400, useNativeDriver: true }).start();
      }, 1500);
    });
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
          { paddingTop: insets.top + spacing.xl, paddingBottom: insets.bottom + 100 }, // Clear absolute tab bar
        ]}
        keyboardShouldPersistTaps="handled"
        showsVerticalScrollIndicator={false}
      >
        {/* HERO / INTRO */}
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

        {/* FORMULAIRE DE RECHERCHE + CV */}
        <Animated.View style={[
          styles.formCard,
          {
            opacity: formAnim,
            transform: [{ translateY: formAnim.interpolate({ inputRange: [0, 1], outputRange: [20, 0] }) }]
          }
        ]}>
          {/* ZONE CV */}
          <TouchableOpacity style={styles.cvArea} onPress={handleUploadCv} activeOpacity={0.7}>
            <View style={[styles.cvIconHolder, cvFileName && styles.cvIconHolderActive]}>
              <Ionicons name={cvFileName ? "document-text" : "cloud-upload-outline"} size={22} color={cvFileName ? "#F5D061" : "#A1A1AA"} />
            </View>
            <View style={styles.cvInfo}>
              <Text style={styles.cvLabel}>CV utilisé par l'IA</Text>
              <Text style={styles.cvSubLabel}>
                {cvFileName ? cvFileName : 'Toucher pour importer un CV (.pdf)'}
              </Text>
            </View>
            {cvFileName && (
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
              style={[styles.searchButton, isSearching && styles.searchButtonDisabled]}
              activeOpacity={0.9}
              onPress={handleSearch}
              disabled={isSearching}
            >
              <Ionicons name={isSearching ? "hourglass-outline" : "search"} size={20} color="#1A1A1A" style={{ marginRight: 8 }} />
              <Text style={styles.searchButtonText}>
                {isSearching ? 'Analyse des offres en cours…' : 'Lancer le Scan Sniper'}
              </Text>
            </TouchableOpacity>
          </Animated.View>
        </Animated.View>

        {/* RÉSULTATS */}
        <Animated.View style={[
          styles.resultsSection,
          {
            opacity: resultsAnim,
            transform: [{ translateY: resultsAnim.interpolate({ inputRange: [0, 1], outputRange: [20, 0] }) }]
          }
        ]}>
          <View style={styles.resultsHeader}>
            <Text style={styles.resultsTitle}>Matchs Potentiels</Text>
            <View style={styles.resultsCountBadge}>
              <Text style={styles.resultsCountText}>{MOCK_JOBS.length}</Text>
            </View>
          </View>

          <View style={styles.resultsList}>
            {MOCK_JOBS.map((job, index) => (
              <Animated.View 
                key={job.id} 
                style={[
                  styles.jobCard,
                  {
                     // Give them a slight stagger delay relative to the main block
                     transform: [{ 
                       translateY: resultsAnim.interpolate({ 
                         inputRange: [0, 1], 
                         outputRange: [10 + (index * 5), 0] 
                       }) 
                     }]
                  }
                ]}
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
                  </View>
                  <View style={styles.jobRight}>
                    {/* Premium Match Badge */}
                    <View style={styles.matchBadge}>
                      <Ionicons name="flash" size={12} color="#D97706" style={{marginRight: 2}} />
                      <Text style={styles.matchText}>{job.match}%</Text>
                    </View>
                    <View style={styles.sourceTag}>
                      <Text style={styles.sourceText}>{job.source}</Text>
                    </View>
                  </View>
                </View>
              </Animated.View>
            ))}
          </View>
        </Animated.View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  root: {
    flex: 1,
    backgroundColor: '#FAFAF8',
  },
  scroll: {
    flex: 1,
  },
  content: {
    paddingHorizontal: spacing.xl,
    gap: spacing.xl, // Spacious look
  },
  hero: {
    marginBottom: spacing.xs,
  },
  heroHeader: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  radarContainer: {
    position: 'relative',
    width: 48,
    height: 48,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: spacing.md,
  },
  radarRing: {
    position: 'absolute',
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: '#F5D061',
  },
  heroIcon: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: '#F5D061',
    justifyContent: 'center',
    alignItems: 'center',
    zIndex: 2,
    shadowColor: '#F5D061',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.4,
    shadowRadius: 8,
    elevation: 4,
  },
  heroTextContainer: {
    flex: 1,
  },
  heroTitle: {
    fontSize: 28,
    fontWeight: '800',
    color: '#1A1A1A',
    letterSpacing: -0.5,
  },
  heroSubtitle: {
    fontSize: 14,
    color: '#666666',
    fontWeight: '500',
    marginTop: 2,
  },
  formCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 24,
    padding: spacing.xl,
    borderWidth: 1,
    borderColor: '#EAEAE6',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 12 },
    shadowOpacity: 0.04,
    shadowRadius: 24,
    elevation: 4,
  },
  cvArea: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FAFAF8',
    padding: spacing.md,
    borderRadius: 16,
    borderWidth: 1,
    borderColor: '#EAEAE6',
    borderStyle: 'dashed',
    marginBottom: spacing.xl,
  },
  cvIconHolder: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#FFFFFF',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: spacing.md,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 4,
    elevation: 2,
  },
  cvIconHolderActive: {
    backgroundColor: '#FFFBEB', // Light gold bg
  },
  cvInfo: {
    flex: 1,
  },
  cvLabel: {
    fontSize: 14,
    fontWeight: '700',
    color: '#1A1A1A',
    marginBottom: 2,
  },
  cvSubLabel: {
    fontSize: 12,
    color: '#999999',
  },
  inputsWrapper: {
    gap: spacing.sm,
    marginBottom: spacing.xl,
  },
  searchButton: {
    flexDirection: 'row',
    borderRadius: 16,
    backgroundColor: '#F5D061',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: spacing.lg,
    shadowColor: '#F5D061',
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.3,
    shadowRadius: 16,
    elevation: 4,
  },
  searchButtonDisabled: {
    opacity: 0.7,
  },
  searchButtonText: {
    fontSize: 16,
    fontWeight: '800',
    color: '#1A1A1A',
  },
  resultsSection: {
    marginTop: spacing.md,
  },
  resultsHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: spacing.lg,
  },
  resultsTitle: {
    fontSize: 20,
    fontWeight: '800',
    color: '#1A1A1A',
    marginRight: spacing.sm,
  },
  resultsCountBadge: {
    backgroundColor: '#EAEAE6',
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 12,
  },
  resultsCountText: {
    fontSize: 12,
    fontWeight: '700',
    color: '#666666',
  },
  resultsList: {
    gap: spacing.md,
  },
  jobCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 20,
    padding: spacing.lg,
    borderWidth: 1,
    borderColor: '#EAEAE6',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.02,
    shadowRadius: 8,
    elevation: 2,
  },
  jobContent: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  jobMain: {
    flex: 1,
    paddingRight: spacing.md,
  },
  jobTitle: {
    fontSize: 16,
    fontWeight: '700',
    color: '#1A1A1A',
    marginBottom: 6,
    letterSpacing: -0.2,
  },
  jobCompanyRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 4,
  },
  jobCompany: {
    fontSize: 14,
    fontWeight: '600',
    color: '#444444',
  },
  jobLocationRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  jobLocation: {
    fontSize: 13,
    color: '#777777',
  },
  jobRight: {
    alignItems: 'flex-end',
    gap: 8,
  },
  matchBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFFBEB',
    borderWidth: 1,
    borderColor: '#FEF3C7',
    borderRadius: 12,
    paddingHorizontal: 10,
    paddingVertical: 6,
  },
  matchText: {
    fontSize: 13,
    fontWeight: '800',
    color: '#D97706',
  },
  sourceTag: {
    backgroundColor: '#F5F5F3',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 8,
  },
  sourceText: {
    fontSize: 11,
    fontWeight: '600',
    color: '#999999',
  },
});
