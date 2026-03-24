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
    if (fontsLoaded || fontError) {
      setIsReady(true);
    }
  }, [fontsLoaded, fontError]);

  const onLayoutRootView = async () => {
    if (isReady) {
      await SplashScreen.hideAsync();
    }
  };

  if (!isReady) {
    return null;
  }

  // We rely on the Splash Screen to cover the interface while loading.
  // Returning null from Root Layout causes fatal crashes in Production with Expo Router.

  return (
    <GestureHandlerRootView style={{ flex: 1 }} onLayout={onLayoutRootView}>
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
              <Stack.Screen name="(mentor)/mentor-audit-cv" options={{}} />
              <Stack.Screen name="(mentor)/mentor-simulator" options={{}} />
              <Stack.Screen name="(mentor)/mentor-interview-room" options={{}} />
              <Stack.Screen name="(offers)/opportunity-details" options={{}} />
              <Stack.Screen name="settings" options={{ presentation: 'modal' }} />
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
