import React, { useMemo, useRef, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  Modal,
  Pressable,
} from 'react-native';
import { ScreenWrapper } from '../../src/components/layout/ScreenWrapper';
import { Header } from '../../src/components/layout/Header';
import { useTheme } from '../../src/hooks/useTheme';
import { spacing } from '../../src/theme/spacing';
import { typography } from '../../src/theme';
import { Ionicons } from '@expo/vector-icons';

type ColumnId = 'to_apply' | 'sent' | 'follow_up' | 'interview';

interface ApplicationCard {
  id: string;
  initials: string;
  name: string;
  company: string;
  date: string;
  note?: string;
  column: ColumnId;
}

const COLUMN_META: Record<ColumnId, { label: string; accent: string; soft: string; description: string }> = {
  to_apply: {
    label: 'À postuler',
    accent: '#F5D061',
    soft: '#FFF8E1',
    description: 'Offres repérées mais où tu n’as pas encore envoyé ton CV.',
  },
  sent: {
    label: 'Candidatures envoyées',
    accent: '#4F46E5',
    soft: '#EEF2FF',
    description: 'Candidatures parties, en attente d’un premier retour.',
  },
  follow_up: {
    label: 'Relance requise',
    accent: '#F97373',
    soft: '#FEF2F2',
    description: 'Candidatures silencieuses à relancer stratégiquement.',
  },
  interview: {
    label: 'Entretiens',
    accent: '#22C55E',
    soft: '#ECFDF3',
    description: 'Entretiens programmés ou déjà passés à mieux préparer.',
  },
};

export default function ExploreScreen() {
  const { theme } = useTheme();

  const [cards, setCards] = useState<ApplicationCard[]>(() => [
    {
      id: '1',
      initials: 'B',
      name: 'Backend Developer Intern',
      company: 'Blaise Transit',
      date: '16/03',
      note: 'Stage été 2026 – remote possible',
      column: 'to_apply',
    },
    {
      id: '2',
      initials: 'G',
      name: 'Software Engineer Intern',
      company: 'Google Jobs',
      date: '07/03',
      note: 'Offre trouvée via Google Jobs',
      column: 'to_apply',
    },
    {
      id: '3',
      initials: 'E',
      name: 'Développeur Java',
      company: 'Ezo',
      date: '01/03',
      note: 'En attente de retour',
      column: 'sent',
    },
    {
      id: '4',
      initials: 'A',
      name: 'Stagiaire développement',
      company: 'Airbus Canada',
      date: '24/02',
      note: 'Mail de relance à prévoir',
      column: 'follow_up',
    },
    {
      id: '5',
      initials: 'T',
      name: 'Développeur logiciel senior',
      company: 'Triton Digital',
      date: '22/02',
      note: 'Entretien prévu la semaine prochaine',
      column: 'interview',
    },
  ]);

  const [activeColumn, setActiveColumn] = useState<ColumnId>('to_apply');
  const [moveModalVisible, setMoveModalVisible] = useState(false);
  const [selectedCard, setSelectedCard] = useState<ApplicationCard | null>(null);

  const columns = useMemo(
    () => (Object.keys(COLUMN_META) as ColumnId[]),
    []
  );

  const handleOpenMoveModal = (card: ApplicationCard) => {
    setSelectedCard(card);
    setMoveModalVisible(true);
  };

  const handleMoveTo = (target: ColumnId) => {
    if (!selectedCard) return;
    setCards((prev) =>
      prev.map((c) => (c.id === selectedCard.id ? { ...c, column: target } : c))
    );
    setMoveModalVisible(false);
    setSelectedCard(null);
    setActiveColumn(target);
  };

  return (
    <ScreenWrapper>
      <Header title="CRM Candidatures" />
      <View style={[styles.root, { backgroundColor: '#F3EEE7' }]}>
        {/* Bandeau top + stats */}
        <View style={styles.hero}>
          <View style={styles.heroPill}>
            <Ionicons name="grid-outline" size={14} color="#7C2D12" />
            <Text style={styles.heroPillText}>Tableau Kanban</Text>
          </View>
          <Text style={[styles.heroTitle, { color: theme.colors.text }]}>
            Central CRM Candidatures
          </Text>
          <Text style={styles.heroSubtitle}>
            Visualise ton pipeline, priorise tes relances et suis chaque entretien en un coup
            d’œil.
          </Text>

          {/* Stat cards */}
          <View style={styles.statsRow}>
            <View style={styles.statCard}>
              <Text style={styles.statValue}>{cards.length}</Text>
              <Text style={styles.statLabel}>Candidatures</Text>
            </View>
            <View style={styles.statCard}>
              <Text style={styles.statValue}>
                {cards.filter((c) => c.column === 'follow_up').length}
              </Text>
              <Text style={styles.statLabel}>Relances</Text>
            </View>
            <View style={styles.statCard}>
              <Text style={styles.statValue}>
                {cards.filter((c) => c.column === 'interview').length}
              </Text>
              <Text style={styles.statLabel}>Entretiens</Text>
            </View>
          </View>

          {/* Barre ajout rapide */}
          <View style={styles.heroFilter}>
            <Ionicons name="link-outline" size={16} color="#9CA3AF" />
            <Text style={styles.heroFilterText}>
              Colle l’URL d’une offre pour l’ajouter rapidement au CRM…
            </Text>
          </View>
        </View>

        {/* Tabs d'étapes */}
        <ScrollView
          horizontal
          showsHorizontalScrollIndicator={false}
          contentContainerStyle={styles.tabsRow}
        >
          {columns.map((columnId) => {
            const meta = COLUMN_META[columnId];
            const isActive = columnId === activeColumn;
            const count = cards.filter((c) => c.column === columnId).length;
            return (
              <Pressable
                key={columnId}
                onPress={() => setActiveColumn(columnId)}
                style={[
                  styles.tabPill,
                  isActive && [
                    styles.tabPillActive,
                    { borderColor: meta.accent, backgroundColor: meta.soft },
                  ],
                ]}
              >
                <Text
                  style={[
                    styles.tabLabel,
                    isActive && { color: '#1A1A18' },
                  ]}
                >
                  {meta.label}
                </Text>
                <View
                  style={[
                    styles.tabCount,
                    { backgroundColor: isActive ? '#FFFFFF' : '#E5E7EB' },
                  ]}
                >
                  <Text
                    style={[
                      styles.tabCountText,
                      isActive && { color: '#1A1A18' },
                    ]}
                  >
                    {count}
                  </Text>
                </View>
              </Pressable>
            );
          })}
        </ScrollView>

        {/* Colonne active détaillée */}
        <View style={styles.activeColumnWrapper}>
          {(() => {
            const meta = COLUMN_META[activeColumn];
            const inColumn = cards.filter((c) => c.column === activeColumn);
            return (
              <View style={styles.activeColumnCard}>
                <View style={styles.activeHeaderRow}>
                  <View style={styles.columnTitleRow}>
                    <View
                      style={[styles.columnDot, { backgroundColor: meta.accent }]}
                    />
                    <Text style={styles.activeColumnTitle}>{meta.label}</Text>
                  </View>
                  <View style={[styles.columnBadge, { borderColor: meta.accent }]}>
                    <Text style={styles.columnBadgeText}>{inColumn.length}</Text>
                  </View>
                </View>
                <Text style={styles.activeDescription}>{meta.description}</Text>

                <ScrollView
                  style={styles.cardsScroll}
                  contentContainerStyle={styles.cardsContent}
                  showsVerticalScrollIndicator={false}
                >
                  {inColumn.map((card) => (
                    <Pressable
                      key={card.id}
                      style={styles.cardWrapper}
                      onPress={() => handleOpenMoveModal(card)}
                    >
                      <View style={styles.card}>
                        <View style={styles.cardHeaderRow}>
                          <View style={styles.avatar}>
                            <Text style={styles.avatarText}>{card.initials}</Text>
                          </View>
                          <View style={styles.metaChipsRow}>
                            <View style={styles.chipLight}>
                              <Ionicons
                                name="calendar-outline"
                                size={10}
                                color="#6B7280"
                              />
                              <Text style={styles.chipText}>{card.date}</Text>
                            </View>
                            <View style={styles.chipLight}>
                              <Ionicons
                                name="time-outline"
                                size={10}
                                color="#6B7280"
                              />
                              <Text style={styles.chipText}>
                                {card.column === 'follow_up'
                                  ? 'Relance'
                                  : card.column === 'interview'
                                  ? 'Entretien'
                                  : 'En cours'}
                              </Text>
                            </View>
                          </View>
                        </View>
                        <Text style={styles.cardTitle}>{card.name}</Text>
                        <Text style={styles.cardCompany}>{card.company}</Text>
                        {card.note ? (
                          <View style={styles.notePill}>
                            <Text style={styles.noteText} numberOfLines={2}>
                              {card.note}
                            </Text>
                          </View>
                        ) : null}
                        <View style={styles.cardFooterRow}>
                          <View style={styles.timelineDotRow}>
                            <View
                              style={[
                                styles.timelineDot,
                                { backgroundColor: '#D1D5DB' },
                              ]}
                            />
                            <View
                              style={[
                                styles.timelineLine,
                                {
                                  backgroundColor:
                                    card.column !== 'to_apply'
                                      ? '#F5D061'
                                      : '#E5E7EB',
                                },
                              ]}
                            />
                            <View
                              style={[
                                styles.timelineDot,
                                {
                                  backgroundColor:
                                    card.column === 'sent' ||
                                    card.column === 'follow_up' ||
                                    card.column === 'interview'
                                      ? '#F5D061'
                                      : '#E5E7EB',
                                },
                              ]}
                            />
                            <View
                              style={[
                                styles.timelineLine,
                                {
                                  backgroundColor:
                                    card.column === 'follow_up' ||
                                    card.column === 'interview'
                                      ? '#F97373'
                                      : '#E5E7EB',
                                },
                              ]}
                            />
                            <View
                              style={[
                                styles.timelineDot,
                                {
                                  backgroundColor:
                                    card.column === 'interview'
                                      ? '#22C55E'
                                      : '#E5E7EB',
                                },
                              ]}
                            />
                          </View>
                          <Text style={styles.timelineLabel}>
                            {card.column === 'to_apply'
                              ? 'À postuler'
                              : card.column === 'sent'
                              ? 'Envoyée'
                              : card.column === 'follow_up'
                              ? 'Relance à faire'
                              : 'Préparation entretien'}
                          </Text>
                        </View>
                      </View>
                    </Pressable>
                  ))}
                </ScrollView>
              </View>
            );
          })()}
        </View>

        {/* Modal de déplacement */}
        <Modal
          visible={moveModalVisible}
          transparent
          animationType="fade"
          onRequestClose={() => setMoveModalVisible(false)}
        >
          <Pressable
            style={styles.modalOverlay}
            onPress={() => setMoveModalVisible(false)}
          >
            <View style={styles.modalCard}>
              <Text style={styles.modalTitle}>Déplacer la candidature</Text>
              {selectedCard ? (
                <Text style={styles.modalSubtitle}>{selectedCard.name}</Text>
              ) : null}
              {columns.map((col) => {
                const meta = COLUMN_META[col];
                return (
                  <Pressable
                    key={col}
                    style={styles.modalOption}
                    onPress={() => handleMoveTo(col)}
                  >
                    <View
                      style={[styles.modalDot, { backgroundColor: meta.accent }]}
                    />
                    <Text style={styles.modalOptionText}>{meta.label}</Text>
                  </Pressable>
                );
              })}
            </View>
          </Pressable>
        </Modal>
      </View>
    </ScreenWrapper>
  );
}

const styles = StyleSheet.create({
  root: {
    flex: 1,
  },
  hero: {
    paddingHorizontal: spacing.lg,
    paddingTop: spacing.lg,
    paddingBottom: spacing.lg,
  },
  heroPill: {
    flexDirection: 'row',
    alignItems: 'center',
    alignSelf: 'flex-start',
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.xs,
    borderRadius: 999,
    backgroundColor: '#FFF0EB',
    marginBottom: spacing.sm,
  },
  heroPillText: {
    marginLeft: 6,
    fontSize: 11,
    fontWeight: '600',
    color: '#7C2D12',
    textTransform: 'uppercase',
  },
  heroTitle: {
    ...typography.h2,
    marginBottom: 4,
  },
  heroSubtitle: {
    fontSize: 13,
    color: '#5A554C',
    marginBottom: spacing.lg,
  },
  heroFilter: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    borderRadius: 999,
    backgroundColor: '#F7F4EE',
    borderWidth: 1,
    borderColor: '#E5E7EB',
  },
  heroFilterText: {
    marginLeft: spacing.sm,
    fontSize: 13,
    color: '#6B7280',
  },
  statsRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: spacing.md,
    marginBottom: spacing.lg,
    gap: spacing.sm,
  },
  statCard: {
    flex: 1,
    paddingVertical: spacing.sm,
    paddingHorizontal: spacing.md,
    borderRadius: 16,
    backgroundColor: '#FFFFFF',
    shadowColor: 'rgba(15,23,42,0.06)',
    shadowOpacity: 1,
    shadowRadius: 10,
    shadowOffset: { width: 0, height: 4 },
    elevation: 2,
  },
  statValue: {
    fontSize: 18,
    fontWeight: '800',
    color: '#1A1A18',
  },
  statLabel: {
    marginTop: 2,
    fontSize: 12,
    color: '#6B7280',
  },
  boardContent: {
    paddingHorizontal: spacing.lg,
    paddingBottom: spacing.xl,
  },
  tabsRow: {
    paddingHorizontal: spacing.lg,
    paddingBottom: spacing.sm,
    paddingTop: 4,
    gap: spacing.sm,
  },
  tabPill: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    borderRadius: 999,
    borderWidth: 1,
    borderColor: '#E5E7EB',
    backgroundColor: '#F9FAFB',
    marginRight: spacing.sm,
  },
  tabPillActive: {},
  tabLabel: {
    fontSize: 13,
    fontWeight: '600',
    color: '#6B7280',
  },
  tabCount: {
    marginLeft: spacing.xs,
    minWidth: 22,
    height: 20,
    borderRadius: 999,
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: 6,
  },
  tabCountText: {
    fontSize: 11,
    fontWeight: '600',
    color: '#4B5563',
  },
  column: {
    width: 0,
    marginRight: 0,
  },
  columnHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: spacing.sm,
  },
  columnTitleRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  columnDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    marginRight: 6,
  },
  columnTitle: {
    fontSize: 14,
    fontWeight: '700',
    color: '#111827',
  },
  columnBadge: {
    minWidth: 26,
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 999,
    backgroundColor: '#FFFFFF',
    borderWidth: 1,
    borderColor: '#E5E7EB',
    alignItems: 'center',
    justifyContent: 'center',
  },
  columnBadgeText: {
    fontSize: 11,
    fontWeight: '600',
    color: '#4B5563',
  },
  columnBody: {
    borderRadius: 18,
    padding: spacing.sm,
  },
  cardWrapper: {
    marginBottom: spacing.sm,
  },
  card: {
    borderRadius: 16,
    backgroundColor: '#FFFFFF',
    padding: spacing.md,
    shadowColor: 'rgba(15,23,42,0.08)',
    shadowOpacity: 1,
    shadowRadius: 12,
    shadowOffset: { width: 0, height: 6 },
    elevation: 3,
  },
  cardHeaderRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: spacing.sm,
  },
  avatar: {
    width: 28,
    height: 28,
    borderRadius: 14,
    backgroundColor: '#FFE4D5',
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: spacing.sm,
  },
  avatarText: {
    fontSize: 13,
    fontWeight: '700',
    color: '#9A3412',
  },
  metaChipsRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  chipLight: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 999,
    backgroundColor: '#F3F4F6',
    marginLeft: 4,
  },
  chipText: {
    marginLeft: 4,
    fontSize: 10,
    fontWeight: '500',
    color: '#4B5563',
  },
  cardTitle: {
    fontSize: 13,
    fontWeight: '700',
    color: '#111827',
    marginBottom: 2,
  },
  cardCompany: {
    fontSize: 12,
    fontWeight: '500',
    color: '#6B7280',
    marginBottom: spacing.xs,
  },
  notePill: {
    borderRadius: 10,
    backgroundColor: '#F3F4F6',
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.xs,
  },
  noteText: {
    fontSize: 11,
    color: '#4B5563',
  },
  activeColumnWrapper: {
    flex: 1,
    paddingHorizontal: spacing.lg,
    paddingBottom: spacing.xl,
  },
  activeColumnCard: {
    flex: 1,
    borderRadius: 20,
    backgroundColor: '#FDFBF7',
    padding: spacing.md,
    shadowColor: 'rgba(15,23,42,0.06)',
    shadowOpacity: 1,
    shadowRadius: 14,
    shadowOffset: { width: 0, height: 6 },
    elevation: 3,
  },
  activeHeaderRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: spacing.xs,
  },
  activeColumnTitle: {
    fontSize: 16,
    fontWeight: '700',
    color: '#111827',
  },
  activeDescription: {
    fontSize: 12,
    color: '#6B7280',
    marginBottom: spacing.sm,
  },
  cardsScroll: {
    flex: 1,
  },
  cardsContent: {
    paddingTop: spacing.sm,
    paddingBottom: spacing.sm,
  },
  cardFooterRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: spacing.sm,
    justifyContent: 'space-between',
  },
  timelineDotRow: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
    marginRight: spacing.sm,
  },
  timelineDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
  },
  timelineLine: {
    flex: 1,
    height: 2,
    marginHorizontal: 2,
    borderRadius: 1,
  },
  timelineLabel: {
    fontSize: 11,
    color: '#6B7280',
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.3)',
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: spacing.lg,
  },
  modalCard: {
    width: '100%',
    borderRadius: 20,
    backgroundColor: '#FFFFFF',
    padding: spacing.lg,
  },
  modalTitle: {
    fontSize: 16,
    fontWeight: '700',
    color: '#111827',
    marginBottom: 4,
  },
  modalSubtitle: {
    fontSize: 13,
    color: '#6B7280',
    marginBottom: spacing.md,
  },
  modalOption: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: spacing.sm,
  },
  modalDot: {
    width: 10,
    height: 10,
    borderRadius: 5,
    marginRight: spacing.sm,
  },
  modalOptionText: {
    fontSize: 14,
    color: '#111827',
    fontWeight: '500',
  },
});
