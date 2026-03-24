/**
 * Root Layout
 * Main app layout with all providers
 */

import { useEffect, useState } from 'react';
import { Stack } from 'expo-router';
import { useFonts } from 'expo-font';
import * as SplashScreen from 'expo-splash-screen';
import { QueryProvider } from '../src/providers/QueryProvider';
import { ThemeProvider } from '../src/providers/ThemeProvider';
import { AuthProvider } from '../src/providers/AuthProvider';
import { ToastContainer } from '../src/components/ui/Toast';
import { GestureHandlerRootView } from 'react-native-gesture-handler';

// Prevent splash screen from auto-hiding
SplashScreen.preventAutoHideAsync();

export { ErrorBoundary } from 'expo-router';

export default function RootLayout() {
  const [fontsLoaded, fontError] = useFonts({});
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    console.log('[RootLayout] fontsLoaded:', fontsLoaded, 'fontError:', fontError);
    if (fontsLoaded || fontError) {
      setIsReady(true);
    }
  }, [fontsLoaded, fontError]);

  const onLayoutRootView = async () => {
    console.log('[RootLayout] onLayoutRootView, isReady:', isReady);
    if (isReady) {
      try {
        await SplashScreen.hideAsync();
        console.log('[RootLayout] SplashScreen hidden');
      } catch (e) {
        console.error('[RootLayout] Error hiding splash screen:', e);
      }
    }
  };

  // Don't return null, it can cause crashes on Android with Expo Router.
  // The splash screen is still visible anyway due to preventAutoHideAsync.

  // We rely on the Splash Screen to cover the interface while loading.
  // Returning null from Root Layout causes fatal crashes in Production with Expo Router.

  return (
    <GestureHandlerRootView style={{ flex: 1 }} onLayout={onLayoutRootView}>
      <QueryProvider>
        <ThemeProvider>
          <AuthProvider>
            <Stack screenOptions={{ headerShown: false }}>
              <Stack.Screen name="index" />
              <Stack.Screen name="onboarding" />
              <Stack.Screen name="(auth)" />
              <Stack.Screen name="(tabs)" />
              <Stack.Screen name="(mentor)" />
              <Stack.Screen name="(offers)" />
              <Stack.Screen name="settings" />
              <Stack.Screen name="notifications" />
            </Stack>
            <ToastContainer />
          </AuthProvider>
        </ThemeProvider>
      </QueryProvider>
    </GestureHandlerRootView>
  );
}
