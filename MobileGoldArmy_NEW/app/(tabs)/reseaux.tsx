import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  ScrollView,
  TextInput,
  TouchableOpacity,
  ActivityIndicator,
  Modal,
  Clipboard,
  Image,
  Linking,
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
  NetworkContact, 
  EmailDraft 
} from '../../src/types/network.types';
import { styles } from './_styles/reseaux.styles';

type NetworksTab = 'scout' | 'carnet';

export default function ReseauxScreen() {
  const insets = useSafeAreaInsets();
  const [activeTab, setActiveTab] = useState<NetworksTab>('scout');
  const [cvText, setCvText] = useState('');

  // Shared AI Draft states
  const [isDrafting, setIsDrafting] = useState(false);
  const [draftResult, setDraftResult] = useState<EmailDraft | null>(null);
  const [isDraftModalVisible, setIsDraftModalVisible] = useState(false);

  useEffect(() => {
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

  const handleGenerateDraft = async (params: { company_name: string, hr_name: string, request_type?: 'emploi' | 'stage', target_domain?: string }) => {
    setIsDrafting(true);
    try {
      const draft = await networkService.generateDraft({
        company_name: params.company_name,
        hr_name: params.hr_name,
        request_type: params.request_type || 'emploi',
        target_domain: params.target_domain || '',
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
      (Clipboard as any).setString(fullText);
      Alert.alert("Copié !", "L'approche a été copiée dans ton presse-papier.");
    }
  };

  return (
    <View style={styles.root}>
      <StatusBar style="dark" />
      <ScrollView
        style={styles.scroll}
        contentContainerStyle={[
          styles.content,
          { paddingTop: insets.top + spacing.lg, paddingBottom: 160 },
        ]}
        showsVerticalScrollIndicator={false}
      >
        {/* HERO */}
        <View style={styles.heroCard}>
          <LinearGradient colors={['#E5F5FF', '#FFFFFF']} style={{ position: 'absolute', left: 0, right: 0, top: 0, bottom: 0 }} />
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
            icon="search-outline"
            active={false}
            onPress={() => Alert.alert("Agent Headhunter", "Le mode Headhunter Pro sera activé dans la prochaine mise à jour.")}
          />
          <TabPill
            label="Carnet"
            icon="book-outline"
            active={activeTab === 'carnet'}
            onPress={() => setActiveTab('carnet')}
          />
        </View>

        {activeTab === 'scout' ? (
          <ScoutSection 
            cvText={cvText} 
            onGenerateDraft={handleGenerateDraft}
            isDrafting={isDrafting}
          />
        ) : (
          <CarnetSection 
            onGenerateDraft={handleGenerateDraft}
            isDrafting={isDrafting}
          />
        )}
      </ScrollView>

      {/* Shared Modal */}
      <Modal
        visible={isDraftModalVisible}
        transparent={true}
        animationType="slide"
        onRequestClose={() => setIsDraftModalVisible(false)}
      >
        <View style={styles.modalOverlay}>
          <BlurView intensity={80} tint="dark" style={{ position: 'absolute', left: 0, right: 0, top: 0, bottom: 0 }} />
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
interface ScoutProps {
  cvText: string;
  onGenerateDraft: (params: any) => Promise<void>;
  isDrafting: boolean;
}

const ScoutSection: React.FC<ScoutProps> = ({ cvText, onGenerateDraft, isDrafting }) => {
  const [companyName, setCompanyName] = useState('');
  const [isEnriching, setIsEnriching] = useState(false);
  const [hrProfiles, setHrProfiles] = useState<HrProfile[]>([]);
  const [hasEnriched, setHasEnriched] = useState(false);

  // Params for draft
  const [selectedHr, setSelectedHr] = useState<string>('');
  const [requestType, setRequestType] = useState<'emploi' | 'stage'>('emploi');
  const [targetDomain, setTargetDomain] = useState('');

  const handleEnrich = async () => {
    if (!companyName.trim()) return;
    setIsEnriching(true);
    setHasEnriched(false);
    setHrProfiles([]);
    try {
      // Redirect to LinkedIn Search
      const encodedName = encodeURIComponent(companyName);
      const linkedInUrl = `https://www.linkedin.com/search/results/all/?keywords=${encodedName}`;
      Linking.openURL(linkedInUrl).catch(() => {
        Alert.alert("Erreur", "Impossible d'ouvrir LinkedIn.");
      });

      const data = await networkService.enrichCompany(companyName);
      setHrProfiles(data);
      setHasEnriched(true);
    } catch (err: any) {
      console.warn("Erreur enrichissement (non bloquante):", err);
    } finally {
      setIsEnriching(false);
    }
  };

  const handleLocalGenerateDraft = () => {
    if (!companyName.trim()) {
      Alert.alert("Info manquante", "Précise d'abord l'entreprise dans la recherche Scout.");
      return;
    }
    onGenerateDraft({
      company_name: companyName,
      hr_name: selectedHr,
      request_type: requestType,
      target_domain: targetDomain
    });
  };


  return (
    <View style={styles.section}>
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

        {hasEnriched && (
          <View style={styles.hrScrollArea}>
            <Text style={styles.hrListTitle}>{hrProfiles.length} DÉCIDEURS IDENTIFIÉS</Text>
            <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.hrScrollContent}>
              {hrProfiles.map((hr, idx) => (
                <TouchableOpacity 
                  key={idx} 
                  style={[styles.hrMiniCard, selectedHr === hr.name && styles.hrMiniCardActive]}
                  onPress={() => {
                    setSelectedHr(hr.name);
                    // Redirect to LinkedIn individual search
                    const encodedName = encodeURIComponent(hr.name + " " + companyName);
                    const lnUrl = `https://www.linkedin.com/search/results/all/?keywords=${encodedName}`;
                    Linking.openURL(lnUrl).catch(() => console.warn("LinkedIn fail"));
                  }}
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
          onPress={handleLocalGenerateDraft}
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

    </View>
  );
};

// --- CARNET SECTION ---
interface CarnetProps {
  onGenerateDraft: (params: any) => Promise<void>;
  isDrafting: boolean;
}

const CarnetSection: React.FC<CarnetProps> = ({ onGenerateDraft, isDrafting }) => {
  const [contacts, setContacts] = useState<NetworkContact[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [localDraftingId, setLocalDraftingId] = useState<string | null>(null);

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

  const handleCarnetGenerate = async (contact: NetworkContact) => {
    setLocalDraftingId(contact.id);
    await onGenerateDraft({ company_name: contact.company_name, hr_name: '' });
    setLocalDraftingId(null);
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
                <TouchableOpacity 
                  style={styles.contactRow}
                  onPress={() => Linking.openURL(contact.site_url).catch(() => Alert.alert("Erreur", "Lien invalide."))}
                >
                  <Ionicons name="globe-outline" size={14} color="#6366F1" />
                  <Text style={[styles.contactVal, styles.linkText]} numberOfLines={1}>{contact.site_url}</Text>
                </TouchableOpacity>
              )}
              {contact.emails.map((email, i) => (
                <TouchableOpacity 
                  key={i} 
                  style={styles.contactRow}
                  onPress={() => Linking.openURL(`mailto:${email}`).catch(() => Alert.alert("Erreur", "Client mail non configuré."))}
                >
                  <Ionicons name="mail-outline" size={14} color="#10B981" />
                  <Text style={[styles.contactVal, styles.linkText]}>{email}</Text>
                </TouchableOpacity>
              ))}
              {contact.phone && (
                <TouchableOpacity 
                  style={styles.contactRow}
                  onPress={() => Linking.openURL(`tel:${contact.phone}`).catch(() => Alert.alert("Erreur", "Impossible d'appeler."))}
                >
                  <Ionicons name="call-outline" size={14} color="#F59E0B" />
                  <Text style={[styles.contactVal, styles.linkText]}>{contact.phone}</Text>
                </TouchableOpacity>
              )}
            </View>

            <TouchableOpacity 
              style={styles.carnetActionBtn}
              onPress={() => handleCarnetGenerate(contact)}
              disabled={isDrafting}
            >
              <LinearGradient colors={['#6366F1', '#4F46E5']} style={styles.carnetActionBtnGrad}>
                {isDrafting && localDraftingId === contact.id ? (
                  <ActivityIndicator size="small" color="#FFFFFF" />
                ) : (
                  <>
                    <Ionicons name="sparkles-outline" size={14} color="#FFFFFF" />
                    <Text style={styles.carnetActionBtnTxt}>Générer l'approche</Text>
                  </>
                )}
              </LinearGradient>
            </TouchableOpacity>
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
