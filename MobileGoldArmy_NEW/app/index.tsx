import React, { useEffect, useState } from 'react';
import { View, ActivityIndicator } from 'react-native';
import { useRouter } from 'expo-router';
import * as SecureStore from 'expo-secure-store';

export default function Index() {
  const router = useRouter();

  useEffect(() => {
    const checkOnboarding = async () => {
      try {
        const completed = await SecureStore.getItemAsync('onboarding_completed');
        if (completed !== 'true') {
          router.replace('/onboarding');
        } else {
          // Si l'onboarding est fini, on va au login par défaut.
          // L'AuthProvider l'upgradera en /home si l'utilisateur est déjà loggué.
          router.replace('/(auth)/login');
        }
      } catch (err) {
        console.error('[Index] Error checking onboarding:', err);
        router.replace('/onboarding');
      }
    };

    checkOnboarding();
  }, [router]);

  // Affiche un loader pendant la redirection initiale
  return (
    <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#FFFFFF' }}>
      <ActivityIndicator size="small" color="#F5D061" />
    </View>
  );
}
