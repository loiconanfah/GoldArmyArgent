import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TextInput,
  TouchableOpacity,
} from 'react-native';
import { StatusBar } from 'expo-status-bar';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { spacing } from '../../src/theme/spacing';

type NetworksTab = 'scout' | 'carnet';

export default function ReseauxScreen() {
  const insets = useSafeAreaInsets();
  const [activeTab, setActiveTab] = React.useState<NetworksTab>('scout');

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
            froides percutantes qu’elles ne peuvent pas ignorer.
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
            icon="person-search-outline" as any
            active={false}
            onPress={() => {}}
          />
          <TabPill
            label="Carnet d’adresses"
            icon="book-outline"
            active={activeTab === 'carnet'}
            onPress={() => setActiveTab('carnet')}
          />
        </View>

        {activeTab === 'scout' ? <ScoutSection /> : <CarnetSection />}
      </ScrollView>
    </View>
  );
}

interface TabPillProps {
  label: string;
  icon: keyof typeof Ionicons.glyphMap | any;
  active: boolean;
  onPress: () => void;
}

const TabPill: React.FC<TabPillProps> = ({ label, icon, active, onPress }) => {
  return (
    <TouchableOpacity
      style={[
        styles.tabPill,
        active && styles.tabPillActive,
      ]}
      activeOpacity={0.9}
      onPress={onPress}
    >
      <Ionicons
        name={icon as any}
        size={14}
        color={active ? '#FFFFFF' : '#4A4A46'}
      />
      <Text
        style={[
          styles.tabPillText,
          active && styles.tabPillTextActive,
        ]}
      >
        {label}
      </Text>
    </TouchableOpacity>
  );
};

const ScoutSection: React.FC = () => {
  return (
    <View style={styles.section}>
      {/* Bloc requête principale */}
      <View style={styles.cardWide}>
        <View style={styles.sectionHeaderRow}>
          <View style={styles.sectionHeaderIcon}>
            <Ionicons name="sparkles-outline" size={18} color="#16A34A" />
          </View>
          <Text style={styles.sectionHeaderTitle}>
            Scout OSINT – Trouver les Décideurs RH
          </Text>
        </View>
        <View style={styles.mainRow}>
          <View style={styles.inputMainWrapper}>
            <Ionicons name="business-outline" size={16} color="#9A9A94" />
            <TextInput
              placeholder="Nom de l’entreprise cible..."
              placeholderTextColor="#9A9A94"
              style={styles.inputMain}
            />
          </View>
          <TouchableOpacity style={styles.analyserBtn} activeOpacity={0.9}>
            <Ionicons name="scan-outline" size={18} color="#FFFFFF" />
            <Text style={styles.analyserText}>Analyser</Text>
          </TouchableOpacity>
        </View>
      </View>

      {/* Paramètres IA + état résultat */}
      <View style={styles.twoColumnsRow}>
        <View style={styles.paramsCard}>
          <View style={styles.sectionHeaderRow}>
            <Ionicons name="options-outline" size={16} color="#6366F1" />
            <Text style={styles.paramsTitle}>Paramètres de l’IA</Text>
          </View>

          <View style={styles.fieldBlock}>
            <Text style={styles.fieldLabel}>Type de demande</Text>
            <View style={styles.segmentRow}>
              <View style={styles.segmentActive}>
                <Text style={styles.segmentActiveText}>Emploi</Text>
              </View>
              <View style={styles.segment}>
                <Text style={styles.segmentText}>Stage / Partenariat</Text>
              </View>
            </View>
          </View>

          <View style={styles.fieldBlock}>
            <Text style={styles.fieldLabel}>Statut</Text>
            <View style={styles.inputRow}>
              <Ionicons name="person-outline" size={16} color="#9A9A94" />
              <TextInput
                placeholder="ex: Jean Dupont (RH)"
                placeholderTextColor="#9A9A94"
                style={styles.input}
              />
            </View>
          </View>

          <View style={styles.fieldBlock}>
            <Text style={styles.fieldLabel}>Domaine visé</Text>
            <View style={styles.inputRow}>
              <Ionicons name="code-slash-outline" size={16} color="#9A9A94" />
              <TextInput
                placeholder="ex: Analyste SOC, Dév Frontend..."
                placeholderTextColor="#9A9A94"
                style={styles.input}
              />
            </View>
          </View>

          <TouchableOpacity style={styles.primaryBtn} activeOpacity={0.9}>
            <Ionicons name="sparkles-outline" size={18} color="#FFFFFF" />
            <Text style={styles.primaryBtnText}>Générer l’approche</Text>
          </TouchableOpacity>
        </View>

        <View style={styles.resultCard}>
          <View style={styles.resultIconWrapper}>
            <Ionicons name="mail-outline" size={28} color="#CBD5F5" />
          </View>
          <Text style={styles.resultTitle}>En attente de génération</Text>
          <Text style={styles.resultSubtitle}>
            Renseigne l’entreprise et lance l’analyse pour générer ton premier message
            d’approche.
          </Text>
        </View>
      </View>
    </View>
  );
};

const CarnetSection: React.FC = () => {
  return (
    <View style={styles.section}>
      <View style={styles.carnetHeaderRow}>
        <View>
          <Text style={styles.carnetTitle}>
            Mon <Text style={styles.carnetTitleAccent}>Carnet d’adresses</Text>
          </Text>
          <Text style={styles.carnetSubtitle}>177 entreprises collectées</Text>
        </View>
        <TouchableOpacity style={styles.actualiserBtn} activeOpacity={0.9}>
          <Ionicons name="refresh-outline" size={16} color="#111827" />
          <Text style={styles.actualiserText}>Actualiser</Text>
        </TouchableOpacity>
      </View>

      <View style={styles.carnetGrid}>
        {['Explorai', 'Mirego', 'LinkedIn Jobs', 'Google Jobs'].map((name, index) => (
          <View key={name} style={styles.carnetCard}>
            <View style={styles.carnetCardHeader}>
              <View style={styles.carnetIconWrapper}>
                <Ionicons name="business-outline" size={18} color="#4B5563" />
              </View>
              <View style={{ flex: 1 }}>
                <Text style={styles.carnetCompany}>{name}</Text>
                <Text style={styles.carnetSync}>SYNC: 3/{16 - index}/2026</Text>
              </View>
            </View>
            <View style={styles.tagRow}>
              <View style={[styles.tag, { backgroundColor: '#EEF2FF' }]}>
                <Text style={[styles.tagText, { color: '#4F46E5' }]}>SNIPER RECHERCHE</Text>
              </View>
              <View style={[styles.tag, { backgroundColor: '#FEF3C7' }]}>
                <Text style={[styles.tagText, { color: '#92400E' }]}>TEL</Text>
              </View>
            </View>
            <View style={styles.inputRow}>
              <Ionicons name="link-outline" size={14} color="#9A9A94" />
              <TextInput
                style={styles.input}
                placeholder="URL de la fiche entreprise..."
                placeholderTextColor="#9A9A94"
              />
            </View>
            <View style={styles.inputRow}>
              <Ionicons name="call-outline" size={14} color="#16A34A" />
              <TextInput
                style={styles.input}
                placeholder="Numéro de téléphone..."
                placeholderTextColor="#9A9A94"
              />
            </View>
            <View style={styles.inputRow}>
              <Ionicons name="mail-outline" size={14} color="#4B5563" />
              <TextInput
                style={styles.input}
                placeholder="Email de contact..."
                placeholderTextColor="#9A9A94"
              />
            </View>
            <TouchableOpacity style={styles.secondaryBtn} activeOpacity={0.9}>
              <Ionicons name="sparkles-outline" size={16} color="#111827" />
              <Text style={styles.secondaryBtnText}>Générer l’approche</Text>
            </TouchableOpacity>
          </View>
        ))}
      </View>
    </View>
  );
};

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
  },
  heroCard: {
    borderRadius: 32,
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.lg,
    backgroundColor: '#E5F5FF',
    marginBottom: spacing.lg,
    shadowColor: 'rgba(15,23,42,0.12)',
    shadowOffset: { width: 0, height: 16 },
    shadowOpacity: 1,
    shadowRadius: 24,
    elevation: 4,
  },
  heroBadgeRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: spacing.sm,
  },
  heroDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: '#22C55E',
    marginRight: 6,
  },
  heroBadgeText: {
    fontSize: 11,
    fontWeight: '700',
    letterSpacing: 1,
    color: '#16A34A',
  },
  heroTitle: {
    fontSize: 24,
    fontWeight: '800',
    color: '#111827',
    marginBottom: spacing.xs,
  },
  heroTitleAccent: {
    color: '#22C55E',
  },
  heroSubtitle: {
    fontSize: 13,
    color: '#4B5563',
    lineHeight: 20,
  },
  tabsRow: {
    flexDirection: 'row',
    backgroundColor: '#111827',
    borderRadius: 20,
    padding: 4,
    marginBottom: spacing.lg,
  },
  tabPill: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    borderRadius: 16,
    paddingVertical: 8,
  },
  tabPillActive: {
    backgroundColor: '#F3F4F6',
  },
  tabPillText: {
    marginLeft: 6,
    fontSize: 13,
    fontWeight: '600',
    color: '#E5E7EB',
  },
  tabPillTextActive: {
    color: '#111827',
  },
  section: {
    marginBottom: spacing.xxxl,
  },
  cardWide: {
    borderRadius: 22,
    backgroundColor: '#FFFFFF',
    padding: spacing.lg,
    marginBottom: spacing.lg,
    shadowColor: 'rgba(15,23,42,0.06)',
    shadowOffset: { width: 0, height: 10 },
    shadowOpacity: 1,
    shadowRadius: 20,
    elevation: 3,
  },
  sectionHeaderRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: spacing.md,
  },
  sectionHeaderIcon: {
    width: 28,
    height: 28,
    borderRadius: 14,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#DCFCE7',
    marginRight: spacing.sm,
  },
  sectionHeaderTitle: {
    fontSize: 15,
    fontWeight: '700',
    color: '#111827',
  },
  mainRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: spacing.sm,
  },
  inputMainWrapper: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#F9FAFB',
    borderRadius: 999,
    paddingHorizontal: spacing.md,
    height: 48,
    borderWidth: 1,
    borderColor: '#E5E7EB',
  },
  inputMain: {
    flex: 1,
    marginLeft: spacing.sm,
    fontSize: 13,
    color: '#111827',
  },
  analyserBtn: {
    marginLeft: spacing.sm,
    borderRadius: 999,
    paddingHorizontal: spacing.lg,
    height: 48,
    backgroundColor: '#16A34A',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
  },
  analyserText: {
    marginLeft: 6,
    fontSize: 14,
    fontWeight: '700',
    color: '#FFFFFF',
  },
  twoColumnsRow: {
    flexDirection: 'row',
    marginTop: spacing.lg,
  },
  paramsCard: {
    flex: 1,
    borderRadius: 22,
    backgroundColor: '#FFFFFF',
    padding: spacing.lg,
    marginRight: spacing.sm,
    shadowColor: 'rgba(15,23,42,0.06)',
    shadowOffset: { width: 0, height: 10 },
    shadowOpacity: 1,
    shadowRadius: 20,
    elevation: 3,
  },
  paramsTitle: {
    marginLeft: spacing.xs,
    fontSize: 14,
    fontWeight: '700',
    color: '#111827',
  },
  fieldBlock: {
    marginTop: spacing.md,
  },
  fieldLabel: {
    fontSize: 11,
    fontWeight: '600',
    color: '#9A9A94',
    marginBottom: spacing.xs,
  },
  segmentRow: {
    flexDirection: 'row',
    backgroundColor: '#F5F4F0',
    borderRadius: 999,
    padding: 3,
  },
  segment: {
    flex: 1,
    borderRadius: 999,
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 6,
  },
  segmentActive: {
    flex: 1,
    borderRadius: 999,
    backgroundColor: '#FFFFFF',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 6,
    shadowColor: 'rgba(15,23,42,0.1)',
    shadowOpacity: 1,
    shadowRadius: 8,
    shadowOffset: { width: 0, height: 3 },
    elevation: 2,
  },
  segmentText: {
    fontSize: 11,
    color: '#6B7280',
    fontWeight: '500',
  },
  segmentActiveText: {
    fontSize: 11,
    color: '#111827',
    fontWeight: '700',
  },
  inputRow: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#F9FAFB',
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#E5E7EB',
    paddingHorizontal: spacing.md,
    height: 44,
  },
  input: {
    flex: 1,
    marginLeft: spacing.sm,
    fontSize: 13,
    color: '#111827',
  },
  primaryBtn: {
    marginTop: spacing.lg,
    borderRadius: 999,
    height: 46,
    backgroundColor: '#4F46E5',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
  },
  primaryBtnText: {
    marginLeft: 6,
    fontSize: 14,
    fontWeight: '700',
    color: '#FFFFFF',
  },
  resultCard: {
    flex: 1,
    borderRadius: 22,
    backgroundColor: '#FFFFFF',
    padding: spacing.lg,
    marginLeft: spacing.sm,
    alignItems: 'center',
    justifyContent: 'center',
  },
  resultIconWrapper: {
    width: 64,
    height: 64,
    borderRadius: 32,
    backgroundColor: '#EEF2FF',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: spacing.sm,
  },
  resultTitle: {
    fontSize: 14,
    fontWeight: '700',
    color: '#4B5563',
    marginBottom: 4,
    textAlign: 'center',
  },
  resultSubtitle: {
    fontSize: 12,
    color: '#9CA3AF',
    textAlign: 'center',
    lineHeight: 18,
  },
  carnetHeaderRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.md,
  },
  carnetTitle: {
    fontSize: 18,
    fontWeight: '800',
    color: '#111827',
  },
  carnetTitleAccent: {
    color: '#22C55E',
  },
  carnetSubtitle: {
    fontSize: 12,
    color: '#9CA3AF',
  },
  actualiserBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    borderRadius: 999,
    paddingHorizontal: spacing.md,
    paddingVertical: 6,
    backgroundColor: '#FFFFFF',
    borderWidth: 1,
    borderColor: '#E5E7EB',
  },
  actualiserText: {
    marginLeft: 6,
    fontSize: 13,
    fontWeight: '500',
    color: '#111827',
  },
  carnetGrid: {
    rowGap: spacing.md,
  },
  carnetCard: {
    borderRadius: 22,
    backgroundColor: '#FFFFFF',
    padding: spacing.lg,
    shadowColor: 'rgba(15,23,42,0.06)',
    shadowOffset: { width: 0, height: 10 },
    shadowOpacity: 1,
    shadowRadius: 20,
    elevation: 3,
    marginBottom: spacing.sm,
  },
  carnetCardHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: spacing.sm,
  },
  carnetIconWrapper: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: '#F5F4F0',
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: spacing.sm,
  },
  carnetCompany: {
    fontSize: 14,
    fontWeight: '700',
    color: '#111827',
  },
  carnetSync: {
    fontSize: 11,
    color: '#9CA3AF',
  },
  tagRow: {
    flexDirection: 'row',
    marginBottom: spacing.sm,
    columnGap: spacing.xs,
  },
  tag: {
    borderRadius: 999,
    paddingHorizontal: spacing.sm,
    paddingVertical: 4,
  },
  tagText: {
    fontSize: 10,
    fontWeight: '600',
  },
  secondaryBtn: {
    marginTop: spacing.sm,
    borderRadius: 999,
    height: 40,
    backgroundColor: '#F5F4F0',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
  },
  secondaryBtnText: {
    marginLeft: 6,
    fontSize: 13,
    fontWeight: '600',
    color: '#111827',
  },
});

