import { Tabs } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { BlurView } from 'expo-blur';
import { styles } from './_styles/layout.styles';

export default function TabsLayout() {
  return (
    <Tabs
      screenOptions={{
        sceneStyle: { backgroundColor: 'transparent' },
        headerShown: false,
        tabBarActiveTintColor: '#FF6B35',
        tabBarInactiveTintColor: '#94A3B8',
        tabBarShowLabel: true,
        tabBarLabelStyle: styles.tabBarLabel,
        tabBarStyle: styles.tabBar,
        tabBarHideOnKeyboard: true,
        tabBarBackground: () => (
          <BlurView
            tint="light"
            intensity={80}
            style={styles.blurView}
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
      <Tabs.Screen
        name="analytics"
        options={{
          title: 'Analyse',
          tabBarIcon: ({ color, focused, size }) => (
            <Ionicons name={focused ? 'stats-chart' : 'stats-chart-outline'} size={size} color={color} />
          ),
        }}
      />
    </Tabs>
  );
}
