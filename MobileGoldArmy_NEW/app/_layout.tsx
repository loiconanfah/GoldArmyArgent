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

export default function RootLayout() {
  const [fontsLoaded, fontError] = useFonts({
    // Add custom fonts here if needed
    // 'Inter-Regular': require('../assets/fonts/Inter-Regular.ttf'),
  });
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    const prepare = async () => {
      try {
        // Wait for fonts to load
        if (fontsLoaded || fontError) {
          // Hide splash screen immediately after fonts are ready
          await SplashScreen.hideAsync();
          setIsReady(true);
        }
      } catch (error) {
        console.error('[RootLayout] Error preparing app:', error);
        await SplashScreen.hideAsync();
        setIsReady(true);
      }
    };

    prepare();
  }, [fontsLoaded, fontError]);

  if (!isReady) {
    return null;
  }

  return (
    <GestureHandlerRootView style={{ flex: 1 }}>
      <QueryProvider>
        <ThemeProvider>
          <AuthProvider>
            <Stack
              screenOptions={{
                headerShown: false,
                contentStyle: { backgroundColor: 'transparent' },
              }}
            >
              <Stack.Screen name="index" options={{ gestureEnabled: false }} />
              <Stack.Screen name="onboarding" options={{ gestureEnabled: false }} />
              <Stack.Screen name="mentor-audit-cv" options={{}} />
              <Stack.Screen name="mentor-simulator" options={{}} />
              <Stack.Screen name="opportunity-details" options={{}} />
              <Stack.Screen name="(auth)" />
              <Stack.Screen name="(tabs)" />
            </Stack>
            <ToastContainer />
          </AuthProvider>
        </ThemeProvider>
      </QueryProvider>
    </GestureHandlerRootView>
  );
}
