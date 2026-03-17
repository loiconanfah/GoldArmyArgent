/**
 * Tabs Layout
 * Bottom tab navigation with custom tab bar
 */

import { Tabs } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { StyleSheet, Platform } from 'react-native';
import { BlurView } from 'expo-blur';
import { useTheme } from '../../src/hooks/useTheme';

export default function TabsLayout() {
  const { theme } = useTheme();

  return (
    <Tabs
      screenOptions={{
        sceneStyle: { backgroundColor: 'transparent' },
        headerShown: false,
        tabBarActiveTintColor: '#FF6B35', // GoldArmy Primary
        tabBarInactiveTintColor: '#A0A0A0',
        tabBarShowLabel: true,
        tabBarLabelStyle: {
          fontSize: 10,
          fontWeight: '600',
          marginTop: -4,
          marginBottom: 4,
        },
        tabBarStyle: {
          position: 'absolute',
          bottom: Platform.OS === 'ios' ? 24 : 16,
          left: 20,
          right: 20,
          backgroundColor: 'rgba(255, 255, 255, 0.85)',
          borderRadius: 32,
          borderTopWidth: 0,
          elevation: 20, // Android shadow
          shadowColor: '#000000',
          shadowOffset: { width: 0, height: 10 },
          shadowOpacity: 0.15,
          shadowRadius: 20,
          height: 64,
          paddingTop: 12,
          paddingBottom: 12, // Equal padding so icons center properly in rounded pill
        },
        tabBarBackground: () => (
          <BlurView
            tint="light"
            intensity={60}
            style={{
              ...StyleSheet.absoluteFillObject,
              borderRadius: 32,
              overflow: 'hidden',
            }}
          />
        ),
      }}
    >
      <Tabs.Screen
        name="home"
        options={{
          title: 'Accueil',
          tabBarIcon: ({ color, focused, size }) => (
            <Ionicons name={focused ? 'home' : 'home-outline'} size={size} color={color} />
          ),
        }}
      />
      {/* Cacher le Dashboard générique car l'Accueil est le nouveau Dashboard */}
      <Tabs.Screen
        name="dashboard"
        options={{
          href: null, // Cache cet onglet de la barre, mais la route existe toujours
        }}
      />
      <Tabs.Screen
        name="sniper"
        options={{
          title: 'Sniper',
          tabBarIcon: ({ color, focused, size }) => (
            <Ionicons name={focused ? 'search' : 'search-outline'} size={size} color={color} />
          ),
        }}
      />
      <Tabs.Screen
        name="mentor"
        options={{
          title: 'Mentor',
          tabBarIcon: ({ color, focused, size }) => (
            <Ionicons name={focused ? 'sparkles' : 'sparkles-outline'} size={size} color={color} />
          ),
        }}
      />
      <Tabs.Screen
        name="reseaux"
        options={{
          title: 'Réseaux',
          tabBarIcon: ({ color, focused, size }) => (
            <Ionicons name={focused ? 'share-social' : 'share-social-outline'} size={size} color={color} />
          ),
        }}
      />
      <Tabs.Screen
        name="crm"
        options={{
          title: 'Suivi',
          tabBarIcon: ({ color, focused, size }) => (
            <Ionicons name={focused ? 'briefcase' : 'briefcase-outline'} size={size} color={color} />
          ),
        }}
      />
      {/* Cacher les onglets les moins importants de la tab bar principale pour la clarté (5 onglets max) */}
      <Tabs.Screen
        name="entretien"
        options={{
          href: null,
        }}
      />
    </Tabs>
  );
}
