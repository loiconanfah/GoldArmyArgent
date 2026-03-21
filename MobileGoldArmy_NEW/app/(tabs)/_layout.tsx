import { Tabs } from 'expo-router';
import { CustomTabBar } from '../../src/components/ui/CustomTabBar';

export default function TabsLayout() {
  return (
    <Tabs
      tabBar={(props) => <CustomTabBar {...props} />}
      screenOptions={{
        headerShown: false,
        sceneStyle: { backgroundColor: 'transparent' },
        tabBarHideOnKeyboard: true,
      }}
    >
      <Tabs.Screen name="home" />
      <Tabs.Screen name="sniper" />
      <Tabs.Screen name="mentor" />
      <Tabs.Screen name="reseaux" />
      <Tabs.Screen name="crm" />
      <Tabs.Screen name="analytics" />
      <Tabs.Screen name="profile" />
    </Tabs>
  );
}
