# Installation Onboarding

## Commandes d'installation

```bash
cd MobileGoldArmy_NEW

# Installer les dépendances Expo (déjà installées)
# expo-linear-gradient, expo-blur, expo-image, expo-haptics sont déjà dans package.json

# Optionnel : Installer react-native-reanimated et moti pour animations avancées
# Si vous voulez utiliser Moti pour les animations déclaratives :
npx expo install react-native-reanimated
npm install moti --legacy-peer-deps

# Note : L'onboarding fonctionne actuellement avec l'API Animated native de React Native
# Les animations sont déjà implémentées sans Moti/Reanimated
```

## Configuration

### babel.config.js

Si vous installez `react-native-reanimated`, ajoutez le plugin en **dernier** :

```javascript
module.exports = function(api) {
  api.cache(true);
  return {
    presets: ['babel-preset-expo'],
    plugins: [
      [
        'module-resolver',
        {
          root: ['./src'],
          alias: {
            '@': './src',
            // ... autres alias
          },
        },
      ],
      'react-native-reanimated/plugin', // ← TOUJOURS EN DERNIER
    ],
  };
};
```

## Fonctionnement

### Logique First-Launch

L'onboarding s'affiche **uniquement à la première ouverture** de l'app :

1. Au démarrage, `app/_layout.tsx` vérifie `onboarding_completed` dans `expo-secure-store`
2. Si la clé n'existe pas → affiche `/onboarding`
3. Si la clé existe et vaut `'true'` → redirige vers login ou home selon l'authentification
4. À la fin du slide 4 (bouton "Commencer") ou sur "Passer" → écrit `onboarding_completed: 'true'` puis redirige vers login

### Structure des fichiers

```
app/
└── onboarding.tsx          ← Route principale (Expo Router)

src/components/onboarding/
├── OnboardingSlide.tsx     ← Composant slide individuel
├── OnboardingDots.tsx      ← Indicateurs de progression
├── OnboardingButton.tsx    ← Bouton Suivant/Commencer
└── slides/
    ├── Slide1Illustration.tsx   ← Illustration slide 1 (recherche emploi)
    ├── Slide2Illustration.tsx   ← Illustration slide 2 (entretiens)
    ├── Slide3Illustration.tsx   ← Illustration slide 3 (candidatures)
    └── Slide4Illustration.tsx   ← Illustration slide 4 (LinkedIn)

src/types/
└── onboarding.types.ts     ← Types TypeScript
```

## Fonctionnalités

✅ 4 slides avec contenu personnalisé
✅ Swipe horizontal natif (FlatList)
✅ Bouton "Suivant" / "Commencer" avec animations
✅ Lien "Passer" sur les slides 1-3
✅ Lien "Se connecter" sur le slide 4
✅ Indicateurs de progression (dots animés)
✅ Animations d'entrée pour chaque élément
✅ Illustrations animées par slide
✅ Highlight cards sur slides 2 et 3
✅ Haptic feedback sur interactions
✅ Logique first-launch avec SecureStore
✅ Thème cohérent (orange/coral, fond ivoire)

## Test

Pour tester l'onboarding à nouveau après l'avoir complété :

```typescript
// Dans votre code de test ou console
import * as SecureStore from 'expo-secure-store';
await SecureStore.deleteItemAsync('onboarding_completed');
// Puis redémarrez l'app
```

## Notes

- L'onboarding utilise l'API `Animated` native de React Native (pas de dépendance externe requise)
- Toutes les animations sont sur le thread UI pour de meilleures performances
- Les illustrations sont des composants React Native animés (pas de Lottie requise, mais peut être ajoutée)
- Le thème est défini localement dans chaque composant (couleurs orange/coral comme spécifié)
