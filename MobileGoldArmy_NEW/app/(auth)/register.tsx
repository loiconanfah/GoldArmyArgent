/**
 * Register Screen
 */

import React from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity } from 'react-native';
import { Link } from 'expo-router';
import { LinearGradient } from 'expo-linear-gradient';
import { ScreenWrapper } from '../../src/components/layout/ScreenWrapper';
import { RegisterForm } from '../../src/components/features/auth/RegisterForm';
import { useTheme } from '../../src/hooks/useTheme';
import { spacing } from '../../src/theme/spacing';
import { typography } from '../../src/theme';

export default function RegisterScreen() {
  const { theme } = useTheme();

  return (
    <ScreenWrapper>
      <LinearGradient
        colors={[theme.colors.background, theme.colors.backgroundSecondary]}
        style={StyleSheet.absoluteFill}
      />
      <ScrollView
        contentContainerStyle={styles.container}
        showsVerticalScrollIndicator={false}
        keyboardShouldPersistTaps="handled"
      >
        <View style={styles.content}>
          <Text style={[styles.title, { color: theme.colors.text }]}>
            Créer un compte
          </Text>
          <Text style={[styles.subtitle, { color: theme.colors.textSecondary }]}>
            Rejoignez l'élite de l'Intelligence Artificielle
          </Text>

          <RegisterForm />

          <View style={styles.footer}>
            <Text style={[styles.footerText, { color: theme.colors.textMuted }]}>
              Déjà un compte ?{' '}
            </Text>
            <Link href="/(auth)/login" asChild>
              <TouchableOpacity>
                <Text style={[styles.link, { color: theme.colors.primary }]}>
                  Se connecter
                </Text>
              </TouchableOpacity>
            </Link>
          </View>
        </View>
      </ScrollView>
    </ScreenWrapper>
  );
}

const styles = StyleSheet.create({
  container: {
    flexGrow: 1,
    justifyContent: 'center',
    padding: spacing.xl,
  },
  content: {
    width: '100%',
    maxWidth: 400,
    alignSelf: 'center',
  },
  title: {
    ...typography.h1,
    marginBottom: spacing.sm,
    textAlign: 'center',
  },
  subtitle: {
    ...typography.body,
    marginBottom: spacing['3xl'],
    textAlign: 'center',
  },
  footer: {
    flexDirection: 'row',
    justifyContent: 'center',
    marginTop: spacing.xl,
  },
  footerText: {
    ...typography.body,
  },
  link: {
    ...typography.body,
    fontWeight: '600',
  },
});
