/**
 * Index Route
 * Force l'affichage de l'onboarding en premier, pour simplifier
 */

import React, { useEffect } from 'react';
import { View } from 'react-native';
import { useRouter } from 'expo-router';

export default function Index() {
  const router = useRouter();

  useEffect(() => {
    // Pour l'instant, on force TOUJOURS l'onboarding en premier
    router.replace('/onboarding');
  }, [router]);

  // On ne rend rien ici, c'est juste une route de redirection
  return <View />;
}
