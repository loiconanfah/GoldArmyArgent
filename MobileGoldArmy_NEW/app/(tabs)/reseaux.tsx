import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TextInput,
  TouchableOpacity,
  ActivityIndicator,
  Modal,
  Clipboard,
  Alert,
  Image,
} from 'react-native';
import { StatusBar } from 'expo-status-bar';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';
import { BlurView } from 'expo-blur';
import { spacing } from '../../src/theme/spacing';
import { networkService } from '../../src/services/networkService';
import { profileService } from '../../src/services/profileService';
import { 
  HrProfile, 
  DecisionMaker, 
  NetworkContact, 
  EmailDraft 
} from '../../src/types/network.types';

type NetworksTab = 'scout' | 'carnet';

export default function ReseauxScreen() {
  const insets = useSafeAreaInsets();
  const [activeTab, setActiveTab] = useState<NetworksTab>('scout');
  const [cvText, setCvText] = useState('');

  useEffect(() => {
    // Initial load: Profile & Contacts
    const init = async () => {
      try {
        const profile = await profileService.getProfile();
        if (profile.cv_text) setCvText(profile.cv_text);
      } catch (err) {
        console.warn('Erreur chargement profil CV:', err);
      }
    };
    init();
  }, []);

  return (
    <View style={styles.root}>
      <StatusBar style="dark" />
      <ScrollView
        style={styles.scroll}
        contentContainerStyle={[
          styles.content,
          { paddingTop: insets.top + spacing.lg, paddingBottom: spacing.xxxl },
        ]}
        showsVerticalScrollIndicator={false}
      >
        {/* HERO */}
        <View style={styles.heroCard}>
          <LinearGradient colors={['#E5F5FF', '#FFFFFF']} style={StyleSheet.absoluteFill} />
          <View style={styles.heroBadgeRow}>
            <View style={styles.heroDot} />
            <Text style={styles.heroBadgeText}>INTELLIGENCE RÉSEAUX ACTIVE</Text>
          </View>
          <Text style={styles.heroTitle}>
            Levez les barrières du{' '}
            <Text style={styles.heroTitleAccent}>Recrutement.</Text>
          </Text>
          <Text style={styles.heroSubtitle}>
            Utilise l’OSINT pour identifier les décideurs et générer des approches
            percutantes.
          </Text>
        </View>

        {/* TABS */}
        <View style={styles.tabsRow}>
          <TabPill
            label="Scout OSINT"
            icon="sparkles-outline"
            active={activeTab === 'scout'}
            onPress={() => setActiveTab('scout')}
          />
          <TabPill
            label="Agent Headhunter"
            icon="person-search-outline"
            active={false} // Pas encore implémenté en profondeur
            onPress={() => Alert.alert("Agent Headhunter", "Le mode Headhunter Pro sera activé dans la prochaine mise à jour.")}
          />
          <TabPill
            label="Carnet"
            icon="book-outline"
            active={activeTab === 'carnet'}
            onPress={() => setActiveTab('carnet')}
          />
        </View>

        {activeTab === 'scout' ? <ScoutSection cvText={cvText} /> : <CarnetSection />}
      </ScrollView>
    </View>
  );
}

// --- TAB PILL ---
const TabPill: React.FC<{ label: string; icon: any; active: boolean; onPress: () => void }> = ({ label, icon, active, onPress }) => (
  <TouchableOpacity
    style={[styles.tabPill, active && styles.tabPillActive]}
    activeOpacity={0.9}
    onPress={onPress}
  >
    <Ionicons name={icon} size={14} color={active ? '#FFFFFF' : '#4A4A46'} />
    <Text style={[styles.tabPillText, active && styles.tabPillTextActive]}>{label}</Text>
  </TouchableOpacity>
);

// --- SCOUT SECTION ---
const ScoutSection: React.FC<{ cvText: string }> = ({ cvText }) => {
  const [companyName, setCompanyName] = useState('');
  const [isEnriching, setIsEnriching] = useState(false);
  const [hrProfiles, setHrProfiles] = useState<HrProfile[]>([]);
  const [hasEnriched, setHasEnriched] = useState(false);

  // Draft states
  const [selectedHr, setSelectedHr] = useState<string>('');
  const [requestType, setRequestType] = useState<'emploi' | 'stage'>('emploi');
  const [targetDomain, setTargetDomain] = useState('');
  const [isDrafting, setIsDrafting] = useState(false);
  const [draftResult, setDraftResult] = useState<EmailDraft | null>(null);
  const [isDraftModalVisible, setIsDraftModalVisible] = useState(false);

  const handleEnrich = async () => {
    if (!companyName.trim()) return;
    setIsEnriching(true);
    setHasEnriched(false);
    setHrProfiles([]);
    try {
      const data = await networkService.enrichCompany(companyName);
      setHrProfiles(data);
      setHasEnriched(true);
    } catch (err: any) {
      Alert.alert("Erreur Scout", err.message || "Impossible de trouver des profils.");
    } finally {
      setIsEnriching(false);
    }
  };

  const handleGenerateDraft = async () => {
    if (!companyName.trim()) {
       Alert.alert("Info manquante", "Précise d'abord l'entreprise dans la recherche Scout.");
       return;
    }
    setIsDrafting(true);
    try {
      const draft = await networkService.generateDraft({
        company_name: companyName,
        hr_name: selectedHr,
        request_type: requestType,
        target_domain: targetDomain,
        cv_text: cvText
      });
      setDraftResult(draft);
      setIsDraftModalVisible(true);
    } catch (err: any) {
      Alert.alert("Erreur IA", err.message || "La génération a échoué.");
    } finally {
      setIsDrafting(false);
    }
  };

  const copyToClipboard = () => {
    if (draftResult) {
      const fullText = `Objet: ${draftResult.subject}\n\n${draftResult.body}`;
      Clipboard.setString(fullText);
      Alert.alert("Copié !", "L'approche a été copiée dans ton presse-papier.");
    }
  };

  return (
    <View style={styles.section}>
      {/* Scout Module */}
      <View style={styles.cardWide}>
        <View style={styles.sectionHeaderRow}>
          <View style={styles.sectionHeaderIcon}>
            <Ionicons name="sparkles-outline" size={18} color="#16A34A" />
          </View>
          <Text style={styles.sectionHeaderTitle}>Scout OSINT – Cibles Stratégiques</Text>
        </View>
        <View style={styles.mainSearchRow}>
          <View style={styles.inputMainWrapper}>
            <Ionicons name="business-outline" size={16} color="#9A9A94" />
            <TextInput
              placeholder="Nom de l’entreprise cible..."
              placeholderTextColor="#9CA3AF"
              style={styles.inputMain}
              value={companyName}
              onChangeText={setCompanyName}
            />
          </View>
          <TouchableOpacity 
            style={styles.analyserBtn} 
            activeOpacity={0.8}
            onPress={handleEnrich}
            disabled={isEnriching}
          >
            {isEnriching ? <ActivityIndicator color="#FFF" size="small" /> : <Ionicons name="scan-outline" size={18} color="#FFFFFF" />}
            <Text style={styles.analyserText}>{isEnriching ? '...' : 'Analyser'}</Text>
          </TouchableOpacity>
        </View>

        {/* Identified Profiles */}
        {hasEnriched && (
          <View style={styles.hrScrollArea}>
            <Text style={styles.hrListTitle}>{hrProfiles.length} DÉCIDEURS IDENTIFIÉS</Text>
            <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.hrScrollContent}>
              {hrProfiles.map((hr, idx) => (
                <TouchableOpacity 
                  key={idx} 
                  style={[styles.hrMiniCard, selectedHr === hr.name && styles.hrMiniCardActive]}
                  onPress={() => setSelectedHr(hr.name)}
                >
                  <View style={styles.hrIconCircle}>
                    <Ionicons name="person-outline" size={16} color="#111827" />
                  </View>
                  <Text style={styles.hrName} numberOfLines={1}>{hr.name}</Text>
                  {selectedHr === hr.name && <View style={styles.checkDot} />}
                </TouchableOpacity>
              ))}
              {hrProfiles.length === 0 && (
                <Text style={styles.emptyHr}>Aucun profil identifié pour le moment.</Text>
              )}
            </ScrollView>
          </View>
        )}
      </View>

      {/* IA Parameters & Generation */}
      <View style={styles.paramsCard}>
        <View style={styles.sectionHeaderRow}>
          <Ionicons name="options-outline" size={16} color="#6366F1" />
          <Text style={styles.paramsTitle}>Configuration de l’approche</Text>
        </View>

        <View style={styles.fieldBlock}>
          <Text style={styles.fieldLabel}>Objectif de la quête</Text>
          <View style={styles.segmentRow}>
            <TouchableOpacity 
              style={requestType === 'emploi' ? styles.segmentActive : styles.segment}
              onPress={() => setRequestType('emploi')}
            >
              <Text style={requestType === 'emploi' ? styles.segmentActiveText : styles.segmentText}>Emploi</Text>
            </TouchableOpacity>
            <TouchableOpacity 
              style={requestType === 'stage' ? styles.segmentActive : styles.segment}
              onPress={() => setRequestType('stage')}
            >
              <Text style={requestType === 'stage' ? styles.segmentActiveText : styles.segmentText}>Stage / Alternance</Text>
            </TouchableOpacity>
          </View>
        </View>

        <View style={styles.fieldBlock}>
          <Text style={styles.fieldLabel}>Domaine visé</Text>
          <View style={styles.inputRow}>
            <Ionicons name="code-slash-outline" size={16} color="#9A9A94" />
            <TextInput
              placeholder="ex: SOC Analyst, Dev Python..."
              placeholderTextColor="#9CA3AF"
              style={styles.input}
              value={targetDomain}
              onChangeText={setTargetDomain}
            />
          </View>
        </View>

        <TouchableOpacity 
          style={styles.primaryBtn} 
          activeOpacity={0.8}
          onPress={handleGenerateDraft}
          disabled={isDrafting}
        >
          {isDrafting ? <ActivityIndicator color="#FFF" /> : (
            <>
              <Ionicons name="sparkles-outline" size={18} color="#FFFFFF" />
              <Text style={styles.primaryBtnText}>Générer l’approche personnalisée</Text>
            </>
          )}
        </TouchableOpacity>
      </View>

      {/* DRAFT MODAL */}
      <Modal
        visible={isDraftModalVisible}
        transparent={true}
        animationType="slide"
        onRequestClose={() => setIsDraftModalVisible(false)}
      >
        <View style={styles.modalOverlay}>
          <BlurView intensity={80} tint="dark" style={StyleSheet.absoluteFill} />
          <View style={[styles.modalContent, { marginTop: 80 }]}>
             <View style={styles.modalHeader}>
                <View style={styles.modalBranding}>
                   <Image source={require('../../assets/logosansfond.png')} style={styles.modalLogo} resizeMode="contain" />
                   <Text style={styles.modalBrandTxt}>GOLDARMY AI APPROACH</Text>
                </View>
                <TouchableOpacity onPress={() => setIsDraftModalVisible(false)} style={styles.closeModalBtn}>
                   <Ionicons name="close-circle" size={32} color="#1A1A1F" />
                </TouchableOpacity>
             </View>

             <ScrollView showsVerticalScrollIndicator={false} contentContainerStyle={styles.draftScroll}>
                <View style={styles.subjectBox}>
                   <Text style={styles.subjectLabel}>OBJET:</Text>
                   <Text style={styles.subjectText}>{draftResult?.subject}</Text>
                </View>

                <View style={styles.bodyBox}>
                   <Text style={styles.bodyText}>{draftResult?.body}</Text>
                   <Text style={styles.aiTag}>GENÉRÉ PAR GEMINI 2.0 FLASH // GOLDARMY INTELLIGENCE</Text>
                </View>

                <TouchableOpacity style={styles.copyBtn} onPress={copyToClipboard}>
                   <LinearGradient colors={['#FF6B35', '#F59E0B']} style={styles.copyBtnGrad}>
                      <Ionicons name="clipboard-outline" size={20} color="#FFFFFF" />
                      <Text style={styles.copyBtnTxt}>COPIER LE MESSAGE</Text>
                   </LinearGradient>
                </TouchableOpacity>

                <TouchableOpacity style={styles.cancelLink} onPress={() => setIsDraftModalVisible(false)}>
                   <Text style={styles.cancelLinkText}>RETOUR</Text>
                </TouchableOpacity>
             </ScrollView>
          </View>
        </View>
      </Modal>
    </View>
  );
};

// --- CARNET SECTION ---
const CarnetSection: React.FC = () => {
  const [contacts, setContacts] = useState<NetworkContact[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const loadContacts = async () => {
    setIsLoading(true);
    try {
      const data = await networkService.getContacts();
      setContacts(data);
    } catch (err: any) {
      Alert.alert("Erreur Carnet", err.message || "Impossible de charger les contacts.");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => { loadContacts(); }, []);

  return (
    <View style={styles.section}>
      <View style={styles.carnetHeaderRow}>
        <View>
          <Text style={styles.carnetTitle}>
            Mon <Text style={styles.carnetTitleAccent}>Carnet</Text>
          </Text>
          <Text style={styles.carnetSubtitle}>{contacts.length} entreprises collectées</Text>
        </View>
        <TouchableOpacity style={styles.actualiserBtn} activeOpacity={0.8} onPress={loadContacts} disabled={isLoading}>
          {isLoading ? <ActivityIndicator size="small" color="#111827" /> : <Ionicons name="refresh-outline" size={16} color="#111827" />}
          <Text style={styles.actualiserText}>{isLoading ? '...' : 'Actualiser'}</Text>
        </TouchableOpacity>
      </View>

      <View style={styles.carnetGrid}>
        {contacts.map((contact) => (
          <View key={contact.id} style={styles.carnetCard}>
            <View style={styles.carnetCardHeader}>
              <View style={styles.carnetIconWrapper}>
                <Ionicons name="business-outline" size={18} color="#4B5563" />
              </View>
              <View style={{ flex: 1 }}>
                <Text style={styles.carnetCompany}>{contact.company_name}</Text>
                <Text style={styles.carnetSync}>Sync: {new Date(contact.last_updated).toLocaleDateString('fr-FR')}</Text>
              </View>
            </View>
            
            <View style={styles.tagRow}>
              <View style={styles.tagPill}>
                <Text style={styles.tagText}>{contact.category.toUpperCase()}</Text>
              </View>
            </View>

            <View style={styles.contactDetailsArea}>
              {contact.site_url && (
                <View style={styles.contactRow}>
                  <Ionicons name="globe-outline" size={14} color="#6366F1" />
                  <Text style={styles.contactVal} numberOfLines={1}>{contact.site_url}</Text>
                </View>
              )}
              {contact.emails.map((email, i) => (
                <View key={i} style={styles.contactRow}>
                  <Ionicons name="mail-outline" size={14} color="#10B981" />
                  <Text style={styles.contactVal}>{email}</Text>
                </View>
              ))}
              {contact.phone && (
                <View style={styles.contactRow}>
                  <Ionicons name="call-outline" size={14} color="#F59E0B" />
                  <Text style={styles.contactVal}>{contact.phone}</Text>
                </View>
              )}
            </View>
          </View>
        ))}

        {!isLoading && contacts.length === 0 && (
          <View style={styles.emptyCarnet}>
            <Ionicons name="book-outline" size={48} color="rgba(0,0,0,0.05)" />
            <Text style={styles.emptyCarnetText}>Ton carnet est encore vide.</Text>
          </View>
        )}
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  root: {
    flex: 1,
    backgroundColor: '#F9F8F6',
  },
  scroll: {
    flex: 1,
  },
  content: {
    paddingHorizontal: 20,
  },
  heroCard: {
    borderRadius: 32,
    padding: 24,
    marginBottom: 20,
    overflow: 'hidden',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 10 },
    shadowOpacity: 0.05,
    shadowRadius: 20,
    elevation: 4,
  },
  heroBadgeRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  heroDot: {
    width: 6,
    height: 6,
    borderRadius: 3,
    backgroundColor: '#22C55E',
    marginRight: 6,
  },
  heroBadgeText: {
    fontSize: 10,
    fontWeight: '800',
    color: '#16A34A',
    letterSpacing: 1.5,
  },
  heroTitle: {
    fontSize: 26,
    fontWeight: '900',
    color: '#111827',
    marginBottom: 6,
    letterSpacing: -0.5,
  },
  heroTitleAccent: {
    color: '#22C55E',
  },
  heroSubtitle: {
    fontSize: 13,
    color: '#4B5563',
    lineHeight: 18,
    fontWeight: '500',
  },
  tabsRow: {
    flexDirection: 'row',
    backgroundColor: '#111827',
    borderRadius: 20,
    padding: 6,
    marginBottom: 20,
  },
  tabPill: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    borderRadius: 15,
    paddingVertical: 10,
  },
  tabPillActive: {
    backgroundColor: '#374151',
  },
  tabPillText: {
    marginLeft: 6,
    fontSize: 12,
    fontWeight: '800',
    color: '#9CA3AF',
  },
  tabPillTextActive: {
    color: '#FFFFFF',
  },
  section: {
    marginBottom: 40,
  },
  cardWide: {
    borderRadius: 24,
    backgroundColor: '#FFFFFF',
    padding: 20,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: '#E2E0DA',
  },
  sectionHeaderRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
  },
  sectionHeaderIcon: {
    width: 32,
    height: 32,
    borderRadius: 12,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#DCFCE7',
    marginRight: 12,
  },
  sectionHeaderTitle: {
    fontSize: 15,
    fontWeight: '800',
    color: '#111827',
  },
  mainSearchRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  inputMainWrapper: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#F5F4F0',
    borderRadius: 15,
    paddingHorizontal: 16,
    height: 52,
    borderWidth: 1,
    borderColor: '#E2E0DA',
  },
  inputMain: {
    flex: 1,
    marginLeft: 10,
    fontSize: 14,
    color: '#111827',
    fontWeight: '600',
  },
  analyserBtn: {
    marginLeft: 12,
    borderRadius: 15,
    width: 100,
    height: 52,
    backgroundColor: '#16A34A',
    flexDirection: 'col',
    alignItems: 'center',
    justifyContent: 'center',
  },
  analyserText: {
    marginTop: 2,
    fontSize: 11,
    fontWeight: '800',
    color: '#FFFFFF',
  },
  hrScrollArea: {
    marginTop: 20,
    borderTopWidth: 1,
    borderTopColor: '#F5F4F0',
    paddingTop: 16,
  },
  hrListTitle: {
    fontSize: 10,
    fontWeight: '900',
    color: '#9A9A94',
    letterSpacing: 2,
    marginBottom: 12,
  },
  hrScrollContent: {
    paddingBottom: 4,
  },
  hrMiniCard: {
    backgroundColor: '#F9FAFB',
    borderRadius: 12,
    padding: 12,
    marginRight: 10,
    width: 130,
    borderWidth: 1,
    borderColor: '#E5E7EB',
    alignItems: 'center',
  },
  hrMiniCardActive: {
    borderColor: '#22C55E',
    backgroundColor: '#F0FDF4',
  },
  hrIconCircle: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: '#FFFFFF',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 8,
    borderWidth: 1,
    borderColor: '#E2E0DA',
  },
  hrName: {
    fontSize: 12,
    fontWeight: '700',
    color: '#111827',
    textAlign: 'center',
  },
  checkDot: {
    position: 'absolute',
    top: 6,
    right: 6,
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: '#22C55E',
  },
  emptyHr: {
    fontSize: 12,
    color: '#9CA3AF',
    fontStyle: 'italic',
  },
  paramsCard: {
    borderRadius: 24,
    backgroundColor: '#FFFFFF',
    padding: 20,
    borderWidth: 1,
    borderColor: '#E2E0DA',
  },
  paramsTitle: {
    fontSize: 15,
    fontWeight: '800',
    color: '#111827',
    marginLeft: 10,
  },
  fieldBlock: {
    marginTop: 16,
  },
  fieldLabel: {
    fontSize: 11,
    fontWeight: '800',
    color: '#9CA3AF',
    marginBottom: 8,
    textTransform: 'uppercase',
    letterSpacing: 1,
  },
  segmentRow: {
    flexDirection: 'row',
    backgroundColor: '#F5F4F0',
    borderRadius: 12,
    padding: 4,
  },
  segment: {
    flex: 1,
    paddingVertical: 10,
    alignItems: 'center',
    borderRadius: 10,
  },
  segmentActive: {
    flex: 1,
    paddingVertical: 10,
    alignItems: 'center',
    borderRadius: 10,
    backgroundColor: '#FFFFFF',
    shadowColor: '#000',
    shadowOpacity: 0.05,
    shadowRadius: 5,
    elevation: 2,
  },
  segmentText: {
    fontSize: 12,
    color: '#6B7280',
    fontWeight: '700',
  },
  segmentActiveText: {
    fontSize: 12,
    color: '#111827',
    fontWeight: '900',
  },
  inputRow: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#F5F4F0',
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#E2E0DA',
    paddingHorizontal: 16,
    height: 48,
  },
  input: {
    flex: 1,
    marginLeft: 10,
    fontSize: 13,
    color: '#111827',
    fontWeight: '600',
  },
  primaryBtn: {
    marginTop: 24,
    borderRadius: 15,
    height: 56,
    backgroundColor: '#6366F1',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    shadowColor: '#6366F1',
    shadowOpacity: 0.2,
    shadowRadius: 10,
    elevation: 4,
  },
  primaryBtnText: {
    marginLeft: 10,
    fontSize: 14,
    fontWeight: '900',
    color: '#FFFFFF',
    letterSpacing: 0.5,
  },
  modalOverlay: {
    flex: 1,
    justifyContent: 'flex-end',
  },
  modalContent: {
    backgroundColor: '#FFFFFF',
    borderTopLeftRadius: 36,
    borderTopRightRadius: 36,
    flex: 1,
    padding: 24,
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 20,
  },
  modalBranding: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  modalLogo: {
    width: 24,
    height: 24,
    marginRight: 10,
  },
  modalBrandTxt: {
    fontSize: 11,
    fontWeight: '900',
    color: '#D4AF37',
    letterSpacing: 2,
  },
  closeModalBtn: {
    padding: 4,
  },
  draftScroll: {
    paddingBottom: 40,
  },
  subjectBox: {
    backgroundColor: '#F9FAFB',
    borderRadius: 15,
    padding: 16,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: '#E5E7EB',
  },
  subjectLabel: {
    fontSize: 10,
    fontWeight: '900',
    color: '#6366F1',
    marginBottom: 4,
  },
  subjectText: {
    fontSize: 14,
    fontWeight: '800',
    color: '#111827',
  },
  bodyBox: {
    backgroundColor: '#FFFFFF',
    borderRadius: 20,
    padding: 20,
    marginBottom: 24,
    borderWidth: 1,
    borderColor: '#F3F4F6',
    shadowColor: '#000',
    shadowOpacity: 0.02,
    shadowRadius: 10,
  },
  bodyText: {
    fontSize: 15,
    lineHeight: 24,
    color: '#374151',
    fontWeight: '500',
  },
  aiTag: {
    marginTop: 20,
    fontSize: 9,
    fontWeight: '900',
    color: '#D1D5DB',
    textAlign: 'center',
    letterSpacing: 1.5,
  },
  copyBtn: {
    borderRadius: 15,
    overflow: 'hidden',
  },
  copyBtnGrad: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 16,
  },
  copyBtnTxt: {
    fontSize: 13,
    fontWeight: '900',
    color: '#FFFFFF',
    marginLeft: 10,
    letterSpacing: 1,
  },
  cancelLink: {
    marginTop: 20,
    alignItems: 'center',
  },
  cancelLinkText: {
    fontSize: 12,
    fontWeight: '800',
    color: '#9CA3AF',
    textDecorationLine: 'underline',
  },
  carnetHeaderRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 20,
  },
  carnetTitle: {
    fontSize: 22,
    fontWeight: '900',
    color: '#111827',
  },
  carnetTitleAccent: {
    color: '#22C55E',
  },
  carnetSubtitle: {
    fontSize: 13,
    color: '#9CA3AF',
    fontWeight: '600',
  },
  actualiserBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    borderRadius: 12,
    paddingHorizontal: 12,
    paddingVertical: 8,
    backgroundColor: '#FFFFFF',
    borderWidth: 1,
    borderColor: '#E2E0DA',
  },
  actualiserText: {
    marginLeft: 6,
    fontSize: 12,
    fontWeight: '700',
    color: '#111827',
  },
  carnetGrid: {
    rowGap: 16,
  },
  carnetCard: {
    borderRadius: 24,
    backgroundColor: '#FFFFFF',
    padding: 20,
    shadowColor: '#000',
    shadowOpacity: 0.04,
    shadowRadius: 10,
    elevation: 3,
    borderWidth: 1,
    borderColor: '#E2E0DA',
  },
  carnetCardHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  carnetIconWrapper: {
    width: 40,
    height: 40,
    borderRadius: 12,
    backgroundColor: '#F5F4F0',
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 12,
  },
  carnetCompany: {
    fontSize: 16,
    fontWeight: '800',
    color: '#111827',
  },
  carnetSync: {
    fontSize: 11,
    color: '#9CA3AF',
    fontWeight: '600',
  },
  tagRow: {
    flexDirection: 'row',
    marginBottom: 16,
  },
  tagPill: {
    backgroundColor: '#EEF2FF',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 8,
  },
  tagText: {
    fontSize: 10,
    fontWeight: '800',
    color: '#4F46E5',
    letterSpacing: 1,
  },
  contactDetailsArea: {
    borderTopWidth: 1,
    borderTopColor: '#F5F4F0',
    paddingTop: 12,
    gap: 8,
  },
  contactRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  contactVal: {
    fontSize: 13,
    fontWeight: '600',
    color: '#4B5563',
    marginLeft: 10,
  },
  emptyCarnet: {
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 60,
  },
  emptyCarnetText: {
    marginTop: 16,
    fontSize: 14,
    color: '#9CA3AF',
    fontWeight: '600',
  },
});
