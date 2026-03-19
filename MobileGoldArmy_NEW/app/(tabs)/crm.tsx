import React, { useEffect, useMemo, useState } from 'react';
import { View, StyleSheet, FlatList, TouchableOpacity, Text, ActivityIndicator, RefreshControl, Linking, Alert } from 'react-native';
import { StatusBar } from 'expo-status-bar';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { spacing } from '../../src/theme/spacing';
import { CrmHeader } from '../../src/components/crm/CrmHeader';
import { CrmUrlInput } from '../../src/components/crm/CrmUrlInput';
import { CrmStatsBand } from '../../src/components/crm/CrmStatsBand';
import { CrmStatusTabs } from '../../src/components/crm/CrmStatusTabs';
import { CandidatureCard } from '../../src/components/crm/CandidatureCard';
import { CrmEmptyState } from '../../src/components/crm/CrmEmptyState';
import { StatusBottomSheet } from '../../src/components/crm/StatusBottomSheet';
import { AddCandidatureModal } from '../../src/components/crm/AddCandidatureModal';
import { Candidature, CrmCounts, StatusKey, STATUS_THEME } from '../../src/types/crm.types';
import { crmService } from '../../src/services/crmService';
import api from '../../src/services/api';
import { API_ENDPOINTS } from '../../src/utils/constants';

export default function CrmScreen() {
  const insets = useSafeAreaInsets();
  const router = useRouter();
  const [candidatures, setCandidatures] = useState<Candidature[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [activeStatus, setActiveStatus] = useState<StatusKey>('a_postuler');
  const [url, setUrl] = useState('');
  const [adding, setAdding] = useState(false);
  const [bottomVisible, setBottomVisible] = useState(false);
  const [selected, setSelected] = useState<Candidature | null>(null);
  const [addModalVisible, setAddModalVisible] = useState(false);

  // Load data on mount
  useEffect(() => {
    loadCRM();
  }, []);

  const loadCRM = async (isRefresh = false) => {
    try {
      if (isRefresh) setRefreshing(true);
      else setLoading(true);
      
      const data = await crmService.fetchCandidatures();
      setCandidatures(data);
    } catch (err) {
      console.error('[CrmScreen] Failed to load data:', err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const counts: CrmCounts = useMemo(() => {
    const base: CrmCounts = {
      total: candidatures.length,
      a_postuler: 0,
      envoye: 0,
      entretien: 0,
      relance: 0,
      offre: 0,
      refuse: 0,
    };
    candidatures.forEach((c) => {
      if (base[c.status] !== undefined) {
        base[c.status] += 1;
      }
    });
    return base;
  }, [candidatures]);

  const filtered = candidatures.filter((c) => c.status === activeStatus);

  const pipeline: StatusKey[] = ['a_postuler', 'envoye', 'entretien', 'offre', 'refuse'];

  const getPrevStatus = (status: StatusKey): StatusKey | null => {
    const idx = pipeline.indexOf(status);
    if (idx > 0) return pipeline[idx - 1];
    return null;
  };

  const getNextStatus = (status: StatusKey): StatusKey | null => {
    const idx = pipeline.indexOf(status);
    if (idx >= 0 && idx < pipeline.length - 1) return pipeline[idx + 1];
    if (status === 'entretien') return 'relance';
    if (status === 'relance') return 'entretien';
    return null;
  };

  const updateStatus = async (id: string, status: StatusKey) => {
    // Optimistic update
    const oldCards = [...candidatures];
    setCandidatures((prev) => prev.map((c) => (c.id === id ? { ...c, status } : c)));

    try {
      await crmService.updateStatus(id, status);
    } catch (err) {
      console.error('[CrmScreen] Failed to persist status update:', err);
      // Rollback on failure
      setCandidatures(oldCards);
    }
  };

  const handleSwipePrev = (item: Candidature) => {
    const target = getPrevStatus(item.status);
    if (target) updateStatus(item.id, target);
  };

  const handleSwipeNext = (item: Candidature) => {
    const target = getNextStatus(item.status);
    if (target) updateStatus(item.id, target);
  };

  const handleOpenStatusSheet = (item: Candidature) => {
    setSelected(item);
    setBottomVisible(true);
  };

  const handleSelectStatus = (status: StatusKey) => {
    if (selected) {
      updateStatus(selected.id, status);
    }
    setBottomVisible(false);
    setSelected(null);
  };

  const handleQuickAdd = async () => {
    if (!url) return;
    setAdding(true);
    try {
      const newCard = await crmService.addFromLink(url);
      setCandidatures((prev) => [newCard, ...prev]);
      setUrl('');
    } catch (err) {
      console.error('[CrmScreen] Quick AI Add failed:', err);
    } finally {
      setAdding(false);
    }
  };

  const handleAddModalSubmit = async (data: {
    url: string;
    title: string;
    company: string;
    status: StatusKey;
    notes: string;
  }) => {
    try {
      const newId = await crmService.createCandidature(data);
      setAddModalVisible(false);
      // Reload to ensure we have the full transformed object with proper dates
      await loadCRM();
    } catch (err) {
      console.error('[CrmScreen] Manual Add failed:', err);
    }
  };

  const handleRefresh = () => {
    loadCRM(true);
  };

  const handlePressOpen = (item: Candidature) => {
    if (item.url) {
      Linking.openURL(item.url).catch(() => Alert.alert('Erreur', 'Impossible d’ouvrir le lien.'));
    }
  };

  const handlePressAction = async (item: Candidature) => {
    switch (item.status) {
      case 'a_postuler':
        // Redirect to Mentor CV Audit
        router.push('/(mentor)/mentor-audit-cv');
        break;
      case 'entretien':
        // Redirect to Mentor Simulation
        router.push('/(mentor)/mentor-simulator');
        break;
      case 'relance':
        // AI Follow-up Generation
        setLoading(true);
        try {
          const res = await api.post(API_ENDPOINTS.CRM.FOLLOWUP(item.id));
          if (res.data?.status === 'success' && res.data.email) {
            Alert.alert('E-mail de relance généré', res.data.email, [
              { text: 'OK', style: 'cancel' },
              { text: 'Copier', onPress: () => { /* Add Clipboard logic if needed */ } }
            ]);
          }
        } catch (err) {
          console.error('[CrmScreen] Follow-up failed:', err);
          Alert.alert('Erreur', 'Échec de la génération de l’e-mail.');
        } finally {
          setLoading(false);
        }
        break;
      case 'offre':
        handlePressOpen(item);
        break;
      default:
        // No-op or generic response
        break;
    }
  };

  const handleDelete = async () => {
    if (!selected) return;
    
    Alert.alert(
      'Supprimer',
      `Es-tu sûr de vouloir supprimer la candidature "${selected.title}" chez ${selected.company} ?`,
      [
        { text: 'Annuler', style: 'cancel' },
        { 
          text: 'Supprimer', 
          style: 'destructive',
          onPress: async () => {
            const idToDelete = selected.id;
            setBottomVisible(false);
            // Optimistic update
            setCandidatures(prev => prev.filter(c => c.id !== idToDelete));
            
            try {
              await crmService.deleteCandidature(idToDelete);
              setSelected(null);
            } catch (err) {
              console.error('[CrmScreen] Delete failed:', err);
              Alert.alert('Erreur', 'Impossible de supprimer la candidature.');
              // Reload to fix state
              loadCRM();
            }
          }
        }
      ]
    );
  };

  const renderHeader = () => (
    <View>
      <CrmHeader />
      <CrmUrlInput url={url} onChangeUrl={setUrl} onSubmit={handleQuickAdd} loading={adding} />
      <CrmStatsBand counts={counts} />
      <CrmStatusTabs active={activeStatus} onChange={setActiveStatus} counts={counts} />
    </View>
  );

  if (loading && !refreshing) {
    return (
      <View style={[styles.root, styles.center]}>
        <ActivityIndicator size="large" color="#FF6B35" />
      </View>
    );
  }

  return (
    <View style={styles.root}>
      <StatusBar style="dark" />
      <FlatList
        data={filtered}
        keyExtractor={(item) => item.id}
        style={styles.list}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={handleRefresh} tintColor="#FF6B35" />
        }
        contentContainerStyle={[
          styles.listContent,
          { paddingTop: insets.top + spacing.xl },
        ]}
        ItemSeparatorComponent={() => <View style={{ height: spacing.sm }} />}
        ListHeaderComponent={renderHeader}
        ListEmptyComponent={<CrmEmptyState status={activeStatus} />}
        renderItem={({ item }) => (
          <CandidatureCard
            item={item}
            onPressStatus={() => handleOpenStatusSheet(item)}
            onSwipePrev={() => handleSwipePrev(item)}
            onSwipeNext={() => handleSwipeNext(item)}
            onPressOpen={() => handlePressOpen(item)}
            onPressAction={() => handlePressAction(item)}
          />
        )}
        showsVerticalScrollIndicator={false}
      />

      {/* FAB */}
      <TouchableOpacity
        style={styles.fab}
        activeOpacity={0.9}
        onPress={() => setAddModalVisible(true)}
      >
        <Text style={styles.fabIcon}>＋</Text>
      </TouchableOpacity>

      {selected && (
        <StatusBottomSheet
          visible={bottomVisible}
          onClose={() => setBottomVisible(false)}
          currentStatus={selected.status}
          title={selected.title}
          company={selected.company}
          onSelect={handleSelectStatus}
          onDelete={handleDelete}
        />
      )}

      <AddCandidatureModal
        visible={addModalVisible}
        onClose={() => setAddModalVisible(false)}
        onSubmit={handleAddModalSubmit}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  root: {
    flex: 1,
    backgroundColor: '#F3EEE7',
  },
  list: {
    flex: 1,
  },
  listContent: {
    paddingHorizontal: spacing.lg,
    paddingBottom: spacing['3xl'],
    paddingTop: spacing.sm,
  },
  center: {
    justifyContent: 'center',
    alignItems: 'center',
  },
  fab: {
    position: 'absolute',
    right: 20,
    bottom: 26,
    width: 56,
    height: 56,
    borderRadius: 28,
    backgroundColor: '#FF6B35',
    alignItems: 'center',
    justifyContent: 'center',
    shadowColor: 'rgba(255,107,53,0.6)',
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 1,
    shadowRadius: 14,
    elevation: 4,
  },
  fabIcon: {
    fontSize: 28,
    color: '#FFFFFF',
    marginTop: -2,
  },
});

