/**
 * Login Screen
 * UI premium selon la spec (logo, fond ivoire, cercle décoratif, Google, liens)
 */

import React, { useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import { Link } from 'expo-router';
import * as WebBrowser from 'expo-web-browser';
import * as Google from 'expo-auth-session/providers/google';
import * as AppleAuthentication from 'expo-apple-authentication';
import { LinearGradient } from 'expo-linear-gradient';
import { ScreenWrapper } from '../../src/components/layout/ScreenWrapper';
import { LoginForm } from '../../src/components/features/auth/LoginForm';
import { Image } from 'expo-image';
import { useAuth } from '../../src/hooks/useAuth';
import { styles } from './_styles/login.styles';

// Constants C, SP, R are now in the styles file.

WebBrowser.maybeCompleteAuthSession();

export default function LoginScreen() {
  const { loginWithGoogle, loginWithApple, isLoading } = useAuth();

  // Load platform-specific client IDs if they exist in .env
  const webClientId = process.env.EXPO_PUBLIC_GOOGLE_CLIENT_ID;
  const iosClientId = process.env.EXPO_PUBLIC_GOOGLE_IOS_CLIENT_ID;
  const androidClientId = process.env.EXPO_PUBLIC_GOOGLE_ANDROID_CLIENT_ID;

  const [request, response, promptAsync] = Google.useAuthRequest({
    webClientId: webClientId,
    iosClientId: iosClientId || webClientId,
    androidClientId: androidClientId || webClientId,
  });

  useEffect(() => {
    const handleGoogleResponse = async () => {
      if (response?.type === 'success') {
        const idToken = response.authentication?.idToken;
        if (idToken && !isLoading) {
          await loginWithGoogle(idToken);
        }
      }
    };
    void handleGoogleResponse();
  }, [response]);

  return (
    <ScreenWrapper>
      {/* Fond ivoire + cercle décoratif orange pâle */}
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
            {/* Logo + nom app */}
            <View style={styles.logoWrapper}>
              <Image
                source={require('../../assets/logosansfond.png')}
                style={styles.logoImage}
                contentFit="contain"
              />
              <Text style={styles.appName}>GoldArmy</Text>
            </View>

            {/* Titre / sous-titre */}
            <Text style={styles.title}>Bon retour 👋</Text>
            <Text style={styles.subtitle}>
              Connecte-toi pour retrouver tes candidatures et continuer ta recherche d&apos;emploi.
            </Text>

            {/* Formulaire email / mot de passe */}
            <LoginForm />

            {/* Lien mot de passe oublié */}
            <Link href="/(auth)/forgot-password" asChild>
              <TouchableOpacity style={styles.forgotPassword}>
                <Text style={styles.forgotPasswordText}>Mot de passe oublié ?</Text>
              </TouchableOpacity>
            </Link>

            {/* Séparateur */}
            <View style={styles.separator}>
              <View style={styles.separatorLine} />
              <Text style={styles.separatorText}>ou</Text>
              <View style={styles.separatorLine} />
            </View>

            {/* Bouton Google */}
            <TouchableOpacity
              style={[styles.googleButton, (!request || isLoading) && styles.googleButtonDisabled]}
              activeOpacity={0.8}
              disabled={!request || isLoading}
              onPress={() => {
                if (!webClientId && !iosClientId) {
                  console.warn('Google Client IDs manquants dans le .env');
                  return;
                }
                promptAsync();
              }}
            >
              <View style={styles.googleLogo}>
                <View style={[styles.googleCircle, { backgroundColor: '#EA4335' }]} />
                <View style={[styles.googleCircle, { backgroundColor: '#FBBC04' }]} />
                <View style={[styles.googleCircle, { backgroundColor: '#34A853' }]} />
                <View style={[styles.googleCircle, { backgroundColor: '#4285F4' }]} />
              </View>
              <Text style={styles.googleText}>Continuer avec Google</Text>
            </TouchableOpacity>

            {Platform.OS === 'ios' && (
              <AppleAuthentication.AppleAuthenticationButton
                buttonType={AppleAuthentication.AppleAuthenticationButtonType.SIGN_IN}
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

            {/* Lien register */}
            <View style={styles.footer}>
              <Text style={styles.footerText}>Pas encore de compte ? </Text>
              <Link href="/(auth)/register" asChild>
                <TouchableOpacity>
                  <Text style={styles.footerLink}>Créer un compte →</Text>
                </TouchableOpacity>
              </Link>
            </View>
          </View>
        </ScrollView>
      </KeyboardAvoidingView>
    </ScreenWrapper>
  );
}
