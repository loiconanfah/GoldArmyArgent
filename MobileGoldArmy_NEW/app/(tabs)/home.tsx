/**
 * Home Screen
 * Dashboard après authentification
 */

import React from 'react';
import { View, Text, StyleSheet, ScrollView } from 'react-native';
import { ScreenWrapper } from '../../src/components/layout/ScreenWrapper';
import { Header } from '../../src/components/layout/Header';
import { Card } from '../../src/components/ui/Card';
import { useTheme } from '../../src/hooks/useTheme';
import { useAuthStore } from '../../src/stores/authStore';
import { spacing } from '../../src/theme/spacing';
import { typography } from '../../src/theme';

export default function HomeScreen() {
  const { theme } = useTheme();
  const { user } = useAuthStore();

  return (
    <ScreenWrapper>
      <Header title="Accueil" />
      <ScrollView
        style={styles.scrollView}
        contentContainerStyle={styles.content}
        showsVerticalScrollIndicator={false}
      >
        <Text style={[styles.welcome, { color: theme.colors.text }]}>
          Bienvenue, {user?.email || 'User'} !
        </Text>

        <Card style={styles.card}>
          <Text style={[styles.cardTitle, { color: theme.colors.text }]}>
            Dashboard
          </Text>
          <Text style={[styles.cardText, { color: theme.colors.textSecondary }]}>
            Votre tableau de bord sera disponible ici.
          </Text>
        </Card>
      </ScrollView>
    </ScreenWrapper>
  );
}

const styles = StyleSheet.create({
  scrollView: {
    flex: 1,
  },
  content: {
    padding: spacing.xl,
    paddingTop: 100, // Account for header
  },
  welcome: {
    ...typography.h2,
    marginBottom: spacing.xl,
  },
  card: {
    marginBottom: spacing.lg,
  },
  cardTitle: {
    ...typography.h3,
    marginBottom: spacing.sm,
  },
  cardText: {
    ...typography.body,
  },
});
