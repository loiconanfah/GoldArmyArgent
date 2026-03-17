/**
 * Index Route
 * Affiche toujours l'onboarding en premier (splash onboarding),
 * puis redirige vers le login depuis l'onboarding lui-même.
 */

import React, { useEffect } from 'react';
import { View } from 'react-native';
import { useRouter } from 'expo-router';

export default function Index() {
  const router = useRouter();

  useEffect(() => {
    router.replace('/onboarding');
  }, [router]);

  // Route de redirection silencieuse
  return <View />;
}
