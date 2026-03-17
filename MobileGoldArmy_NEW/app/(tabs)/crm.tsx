import React, { useMemo, useState } from 'react';
import { View, StyleSheet, FlatList, TouchableOpacity, Text } from 'react-native';
import { ScreenWrapper } from '../../src/components/layout/ScreenWrapper';
import { StatusBar } from 'expo-status-bar';
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

const INITIAL_DATA: Candidature[] = [
  {
    id: '1',
    url: '',
    title: 'Backend Developer Intern - Summer 2026',
    company: 'Blaise Transit',
    status: 'a_postuler',
    description: 'Stage été 2026, stack Node.js / TypeScript, équipe remote-friendly.',
    notes: null,
    date: '16/03',
    created_at: new Date().toISOString(),
  },
  {
    id: '2',
    url: '',
    title: 'Software Engineer Intern',
    company: 'Google',
    status: 'a_postuler',
    description: 'Offre repérée via Google Jobs, bureau Paris / Zurich.',
    notes: null,
    date: '07/03',
    created_at: new Date().toISOString(),
  },
  {
    id: '3',
    url: '',
    title: 'Développeur Java',
    company: 'Ezo',
    status: 'envoye',
    description: 'En attente de retour, première candidature envoyée cette semaine.',
    notes: null,
    date: '01/03',
    created_at: new Date().toISOString(),
  },
  {
    id: '4',
    url: '',
    title: 'Stagiaire développement',
    company: 'Airbus Canada',
    status: 'relance',
    description: 'Relance à prévoir après 10 jours sans réponse.',
    notes: null,
    date: '24/02',
    created_at: new Date().toISOString(),
  },
  {
    id: '5',
    url: '',
    title: 'Développeur logiciel senior',
    company: 'Triton Digital',
    status: 'entretien',
    description: 'Entretien technique prévu, préparer questions système distribué.',
    notes: null,
    date: '22/02',
    created_at: new Date().toISOString(),
  },
];

export default function CrmScreen() {
  const [candidatures, setCandidatures] = useState<Candidature[]>(INITIAL_DATA);
  const [activeStatus, setActiveStatus] = useState<StatusKey>('a_postuler');
  const [url, setUrl] = useState('');
  const [adding, setAdding] = useState(false);
  const [bottomVisible, setBottomVisible] = useState(false);
  const [selected, setSelected] = useState<Candidature | null>(null);
  const [addModalVisible, setAddModalVisible] = useState(false);

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
      base[c.status] += 1;
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

  const updateStatus = (id: string, status: StatusKey) => {
    setCandidatures((prev) => prev.map((c) => (c.id === id ? { ...c, status } : c)));
  };

  const handleSwipePrev = (item: Candidature) => {
    const target = getPrevStatus(item.status);
    if (target) {
      updateStatus(item.id, target);
    }
  };

  const handleSwipeNext = (item: Candidature) => {
    const target = getNextStatus(item.status);
    if (target) {
      updateStatus(item.id, target);
    }
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

  const handleQuickAdd = () => {
    if (!url) return;
    const now = new Date();
    const newCard: Candidature = {
      id: String(now.getTime()),
      url,
      title: 'Nouvelle offre',
      company: 'À définir',
      status: 'a_postuler',
      description: null,
      notes: null,
      date: `${now.getDate().toString().padStart(2, '0')}/${(now.getMonth() + 1)
        .toString()
        .padStart(2, '0')}`,
      created_at: now.toISOString(),
    };
    setAdding(true);
    setTimeout(() => {
      setCandidatures((prev) => [newCard, ...prev]);
      setUrl('');
      setAdding(false);
    }, 400);
  };

  const handleAddModalSubmit = (data: {
    url: string;
    title: string;
    company: string;
    status: StatusKey;
    notes: string;
  }) => {
    const now = new Date();
    const card: Candidature = {
      id: String(now.getTime()),
      url: data.url,
      title: data.title,
      company: data.company,
      status: data.status,
      description: null,
      notes: data.notes,
      date: `${now.getDate().toString().padStart(2, '0')}/${(now.getMonth() + 1)
        .toString()
        .padStart(2, '0')}`,
      created_at: now.toISOString(),
    };
    setCandidatures((prev) => [card, ...prev]);
    setAddModalVisible(false);
  };

  const handleRefresh = () => {
    // Placeholder for future API refresh; currently no-op
  };

  return (
    <ScreenWrapper>
      <StatusBar style="dark" />
      <View style={styles.root}>
        <CrmHeader onRefresh={handleRefresh} />
        <CrmUrlInput url={url} onChangeUrl={setUrl} onSubmit={handleQuickAdd} loading={adding} />
        <CrmStatsBand counts={counts} />
        <CrmStatusTabs active={activeStatus} onChange={setActiveStatus} counts={counts} />

        <FlatList
          data={filtered}
          keyExtractor={(item) => item.id}
          contentContainerStyle={styles.listContent}
          ItemSeparatorComponent={() => <View style={{ height: spacing.sm }} />}
          ListEmptyComponent={<CrmEmptyState status={activeStatus} />}
          renderItem={({ item }) => (
            <CandidatureCard
              item={item}
              onPressStatus={() => handleOpenStatusSheet(item)}
              onSwipePrev={() => handleSwipePrev(item)}
              onSwipeNext={() => handleSwipeNext(item)}
            />
          )}
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
          />
        )}

        <AddCandidatureModal
          visible={addModalVisible}
          onClose={() => setAddModalVisible(false)}
          onSubmit={handleAddModalSubmit}
        />
      </View>
    </ScreenWrapper>
  );
}

const styles = StyleSheet.create({
  root: {
    flex: 1,
    backgroundColor: '#FAFAF8',
  },
  listContent: {
    paddingHorizontal: spacing.md,
    paddingBottom: spacing.xl,
    paddingTop: spacing.sm,
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

