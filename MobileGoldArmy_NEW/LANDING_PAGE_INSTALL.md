# Installation Landing Page

## Commandes d'installation

```bash
cd MobileGoldArmy_NEW

# Installer les dépendances Expo
npx expo install expo-linear-gradient expo-blur expo-image expo-haptics react-native-gesture-handler

# Note: react-native-reanimated et moti ne sont PAS installés
# La landing page utilise l'API Animated native de React Native
```

## Configuration

Aucune modification de `babel.config.js` nécessaire - la landing page utilise uniquement l'API `Animated` native.

## Utilisation

Dans `app/(tabs)/home.tsx` ou `app/index.tsx`, importez et utilisez :

```typescript
import SplashOnboarding from '../../src/screens/SplashOnboarding';

export default function HomeScreen() {
  return <SplashOnboarding />;
}
```

## Fonctionnalités

✅ Navbar avec blur au scroll
✅ Hero section avec image, badge animé, CTA
✅ Stats band avec compteurs animés
✅ Carrousel partenaires (défilement infini automatique)
✅ Carrousel features (auto-scroll + swipe manuel)
✅ Témoignage
✅ CTA final avec haptics
✅ Footer

## Alternatives utilisées

- **Animated API native** au lieu de `react-native-reanimated`
- **Animated.Value** au lieu de `useSharedValue`
- **Animated.timing/spring** au lieu de `withTiming/withSpring`
- **Pas de Moti** - animations déclaratives avec `Animated` directement

Tout fonctionne sur Expo Go sans configuration supplémentaire !
