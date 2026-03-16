# Installation - Étapes Correctes

## Étape 1 : Installer les dépendances npm (non-Expo)

```bash
cd MobileGoldArmy_NEW
npm install
```

## Étape 2 : Installer les packages Expo avec les bonnes versions

```bash
npx expo install expo-router expo-secure-store expo-blur expo-linear-gradient expo-image expo-haptics expo-status-bar expo-splash-screen expo-constants expo-font expo-local-authentication react-native-safe-area-context react-native-screens react-native-gesture-handler react-native-reanimated
```

Cette commande installera automatiquement les versions correctes pour Expo SDK 54.

## Étape 3 : Configurer .env

Créer un fichier `.env` :
```
EXPO_PUBLIC_API_URL=https://your-api.onrender.com
EXPO_PUBLIC_APP_ENV=development
```

## Étape 4 : Démarrer l'application

```bash
npx expo start --clear
```

## Pourquoi cette approche ?

- `npm install` installe les dépendances npm standard
- `npx expo install` installe les packages Expo avec les versions exactes compatibles avec votre SDK
- Cela évite les erreurs de version comme `expo-local-authentication@~15.0.8` qui n'existe pas pour SDK 54
