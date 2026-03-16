/**
 * Forgot Password Screen
 */

import React from 'react';
import { View, Text, StyleSheet, ScrollView } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { ScreenWrapper } from '../../src/components/layout/ScreenWrapper';
import { Button } from '../../src/components/ui/Button';
import { Input } from '../../src/components/ui/Input';
import { useTheme } from '../../src/hooks/useTheme';
import { spacing } from '../../src/theme/spacing';
import { typography } from '../../src/theme';
import { Ionicons } from '@expo/vector-icons';

export default function ForgotPasswordScreen() {
  const { theme } = useTheme();
  const [email, setEmail] = React.useState('');

  const handleSubmit = () => {
    // TODO: Implement forgot password
    console.log('Forgot password for:', email);
  };

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
            Mot de passe oublié
          </Text>
          <Text style={[styles.subtitle, { color: theme.colors.textSecondary }]}>
            Entrez votre email pour recevoir un lien de réinitialisation
          </Text>

          <Input
            label="Email"
            value={email}
            onChangeText={setEmail}
            keyboardType="email-address"
            autoCapitalize="none"
            autoComplete="email"
            leftIcon={<Ionicons name="mail-outline" size={20} color={theme.colors.textMuted} />}
            style={styles.input}
          />

          <Button
            title="Envoyer le lien"
            onPress={handleSubmit}
            fullWidth
            style={styles.button}
          />
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
  input: {
    marginBottom: spacing.lg,
  },
  button: {
    marginTop: spacing.lg,
  },
});
