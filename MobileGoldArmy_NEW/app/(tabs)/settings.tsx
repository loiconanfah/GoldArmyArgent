/**
 * Settings Screen
 */

import React from 'react';
import { View, Text, StyleSheet, ScrollView, Switch } from 'react-native';
import { ScreenWrapper } from '../../src/components/layout/ScreenWrapper';
import { Header } from '../../src/components/layout/Header';
import { Card } from '../../src/components/ui/Card';
import { useTheme } from '../../src/hooks/useTheme';
import { useThemeStore } from '../../src/stores/themeStore';
import { spacing } from '../../src/theme/spacing';
import { typography } from '../../src/theme';

export default function SettingsScreen() {
  const { theme, toggleTheme, colorScheme } = useTheme();
  const { isSystemTheme, setSystemTheme } = useThemeStore();

  return (
    <ScreenWrapper>
      <Header title="Paramètres" />
      <ScrollView
        style={styles.scrollView}
        contentContainerStyle={styles.content}
        showsVerticalScrollIndicator={false}
      >
        <Card style={styles.card}>
          <View style={styles.settingRow}>
            <View style={styles.settingInfo}>
              <Text style={[styles.settingTitle, { color: theme.colors.text }]}>
                Mode sombre
              </Text>
              <Text style={[styles.settingDescription, { color: theme.colors.textSecondary }]}>
                Activer le thème sombre
              </Text>
            </View>
            <Switch
              value={colorScheme === 'dark'}
              onValueChange={toggleTheme}
              trackColor={{ false: theme.colors.border, true: theme.colors.primary }}
              thumbColor={theme.colors.textInverse}
            />
          </View>
        </Card>

        <Card style={styles.card}>
          <View style={styles.settingRow}>
            <View style={styles.settingInfo}>
              <Text style={[styles.settingTitle, { color: theme.colors.text }]}>
                Utiliser le thème système
              </Text>
              <Text style={[styles.settingDescription, { color: theme.colors.textSecondary }]}>
                Suivre les préférences du système
              </Text>
            </View>
            <Switch
              value={isSystemTheme}
              onValueChange={setSystemTheme}
              trackColor={{ false: theme.colors.border, true: theme.colors.primary }}
              thumbColor={theme.colors.textInverse}
            />
          </View>
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
    paddingTop: 100,
  },
  card: {
    marginBottom: spacing.lg,
  },
  settingRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  settingInfo: {
    flex: 1,
    marginRight: spacing.lg,
  },
  settingTitle: {
    ...typography.h4,
    marginBottom: spacing.xs,
  },
  settingDescription: {
    ...typography.small,
  },
});
