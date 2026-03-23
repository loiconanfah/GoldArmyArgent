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
import { Ionicons } from '@expo/vector-icons';
import { useAuth } from '../../src/hooks/useAuth';

const C = {
  primary: '#FF6B35',
  primarySoft: '#FF8C5A',
  primaryPale: '#FFF0EB',
  primaryDeep: '#E8521A',
  accent: '#FF3D00',
  bg: '#FAFAF8',
  surface: '#FFFFFF',
  surfaceAlt: '#F5F4F0',
  border: '#EAEAE6',
  text: '#1A1A18',
  textMid: '#4A4A46',
  textMuted: '#9A9A94',
  white: '#FFFFFF',
  shadow: 'rgba(255,107,53,0.20)',
  shadowNeutral: 'rgba(0,0,0,0.07)',
};

const SP = { xs: 4, sm: 8, md: 12, lg: 16, xl: 24, xxl: 32, xxxl: 48 };
const R = { sm: 8, md: 14, lg: 20, xl: 28, full: 999 };

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
            backgroundColor: C.primaryPale,
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
                cornerRadius={R.full}
                style={{ width: '100%', height: 54, marginTop: SP.md }}
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

const styles = StyleSheet.create({
  container: {
    flexGrow: 1,
    justifyContent: 'center',
    paddingHorizontal: SP.xl,
    paddingBottom: SP.xxxl,
  },
  content: {
    width: '100%',
    maxWidth: 420,
    alignSelf: 'center',
  },
  logoWrapper: {
    alignItems: 'center',
    marginBottom: SP.xl,
  },
  logoImage: {
    width: 64,
    height: 64,
    marginBottom: SP.sm,
  },
  appName: {
    fontSize: 20,
    fontWeight: '700',
    letterSpacing: 0.6,
    color: C.text,
  },
  title: {
    fontSize: 30,
    fontWeight: '800',
    letterSpacing: -0.8,
    color: C.text,
    textAlign: 'center',
    marginBottom: SP.sm,
  },
  subtitle: {
    fontSize: 15,
    lineHeight: 24,
    color: C.text,
    textAlign: 'center',
    marginBottom: SP.xxl,
  },
  forgotPassword: {
    marginTop: SP.sm,
    alignItems: 'flex-end',
  },
  forgotPasswordText: {
    fontSize: 13,
    color: C.textMuted,
  },
  separator: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: SP.xxl,
    marginBottom: SP.lg,
  },
  separatorLine: {
    flex: 1,
    height: 1,
    backgroundColor: C.border,
  },
  separatorText: {
    marginHorizontal: SP.md,
    fontSize: 13,
    color: C.textMuted,
  },
  googleButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    height: 54,
    borderRadius: R.full,
    backgroundColor: C.white,
    borderWidth: 1.5,
    borderColor: C.border,
    shadowColor: C.shadowNeutral,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 1,
    shadowRadius: 12,
    elevation: 3,
  },
  googleLogo: {
    flexDirection: 'row',
    marginRight: SP.sm,
  },
  googleCircle: {
    width: 6,
    height: 6,
    borderRadius: 3,
    marginHorizontal: 1,
  },
  googleText: {
    fontSize: 15,
    fontWeight: '600',
    color: C.text,
  },
  googleButtonDisabled: {
    opacity: 0.6,
  },
  footer: {
    flexDirection: 'row',
    justifyContent: 'center',
    marginTop: SP.xxl,
  },
  footerText: {
    fontSize: 14,
    color: C.textMid,
  },
  footerLink: {
    fontSize: 14,
    fontWeight: '600',
    color: C.primary,
  },
});
