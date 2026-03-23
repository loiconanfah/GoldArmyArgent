/**
 * Register Screen
 * Aligné visuellement avec Login, plus propre et structuré
 */

import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import { Link, useRouter } from 'expo-router';
import { ScreenWrapper } from '../../src/components/layout/ScreenWrapper';
import { RegisterForm } from '../../src/components/features/auth/RegisterForm';
import { Image } from 'expo-image';
import { Ionicons } from '@expo/vector-icons';
import * as AppleAuthentication from 'expo-apple-authentication';
import { useAuth } from '../../src/hooks/useAuth';
import { styles } from './_styles/register.styles';

// Constants C, SP, R are moved to styles.

export default function RegisterScreen() {
  const router = useRouter();
  const { loginWithApple, isLoading } = useAuth();

  return (
    <ScreenWrapper>
      {/* Fond ivoire + cercle décoratif */}
      <View style={StyleSheet.absoluteFill}>
        <View style={[StyleSheet.absoluteFill, { backgroundColor: '#F3EEE7' }]} />
        <View
          style={{
            position: 'absolute',
            width: 320,
            height: 320,
            borderRadius: 160,
            backgroundColor: '#FFF0EB',
            top: -80,
            right: -40,
            opacity: 0.12,
          }}
        />
      </View>

      <KeyboardAvoidingView
        style={{ flex: 1 }}
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      >
        <ScrollView
          contentContainerStyle={styles.container}
          showsVerticalScrollIndicator={false}
          keyboardShouldPersistTaps="handled"
        >
          <View style={styles.content}>
            {/* Bouton retour */}
            <TouchableOpacity style={styles.backButton} onPress={() => router.back()}>
              <Ionicons name="chevron-back-outline" size={22} color="#1A1A18" />
            </TouchableOpacity>

            {/* Logo + titre */}
            <View style={styles.header}>
              <Image
                source={require('../../assets/logosansfond.png')}
                style={styles.logoImage}
                contentFit="contain"
              />
              <Text style={styles.title}>Créer un compte</Text>
              <Text style={styles.subtitle}>
                Rejoins des milliers de professionnels qui accélèrent leur carrière avec GoldArmy.
              </Text>
            </View>

            {/* Formulaire d'inscription */}
            <RegisterForm />

            {/* Séparateur */}
            <View style={styles.separator}>
              <View style={styles.separatorLine} />
              <Text style={styles.separatorText}>ou</Text>
              <View style={styles.separatorLine} />
            </View>

            {/* Bouton Google (même style que login) */}
            <TouchableOpacity style={styles.googleButton} activeOpacity={0.8}>
              <View style={styles.googleLogo}>
                <View style={[styles.googleCircle, { backgroundColor: '#EA4335' }]} />
                <View style={[styles.googleCircle, { backgroundColor: '#FBBC04' }]} />
                <View style={[styles.googleCircle, { backgroundColor: '#34A853' }]} />
                <View style={[styles.googleCircle, { backgroundColor: '#4285F4' }]} />
              </View>
              <Text style={styles.googleText}>Créer un compte avec Google</Text>
            </TouchableOpacity>

            {Platform.OS === 'ios' && (
              <AppleAuthentication.AppleAuthenticationButton
                buttonType={AppleAuthentication.AppleAuthenticationButtonType.SIGN_UP}
                buttonStyle={AppleAuthentication.AppleAuthenticationButtonStyle.BLACK}
                cornerRadius={999}
                style={{ width: '100%', height: 54, marginTop: 16 }}
                onPress={async () => {
                  try {
                    const credential = await AppleAuthentication.signInAsync({
                      requestedScopes: [
                        AppleAuthentication.AppleAuthenticationScope.FULL_NAME,
                        AppleAuthentication.AppleAuthenticationScope.EMAIL,
                      ],
                    });
                    if (credential.identityToken && !isLoading) {
                      await loginWithApple(credential.identityToken);
                    }
                  } catch (e: any) {
                    if (e.code !== 'ERR_REQUEST_CANCELED') {
                      console.error(e);
                    }
                  }
                }}
              />
            )}

            {/* Lien login */}
            <View style={styles.footer}>
              <Text style={styles.footerText}>Déjà un compte ? </Text>
              <Link href="/(auth)/login" asChild>
                <TouchableOpacity>
                  <Text style={styles.footerLink}>Se connecter →</Text>
                </TouchableOpacity>
              </Link>
            </View>
          </View>
        </ScrollView>
      </KeyboardAvoidingView>
    </ScreenWrapper>
  );
}
