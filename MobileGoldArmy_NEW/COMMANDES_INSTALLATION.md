# Commandes d'Installation Complètes

## Installation en une seule commande

```bash
cd MobileGoldArmy_NEW

# Installer toutes les dépendances
npm install

# Installer les dépendances Expo avec les bonnes versions
npx expo install expo-router expo-secure-store expo-blur expo-linear-gradient expo-image expo-haptics expo-status-bar expo-splash-screen expo-constants expo-font expo-local-authentication react-native-safe-area-context react-native-screens react-native-gesture-handler react-native-reanimated

# Installer les dépendances npm (non-Expo)
npm install zustand @tanstack/react-query axios react-hook-form @hookform/resolvers zod moti date-fns
```

## Vérification

```bash
# Vérifier les types TypeScript
npm run type-check

# Démarrer l'application
npx expo start --clear
```

## Configuration requise

1. **Créer `.env`** avec votre API URL :
   ```
   EXPO_PUBLIC_API_URL=https://your-api.onrender.com
   EXPO_PUBLIC_APP_ENV=development
   ```

2. **Copier les assets** depuis l'ancien projet si nécessaire

3. **Tester sur Expo Go** après installation
