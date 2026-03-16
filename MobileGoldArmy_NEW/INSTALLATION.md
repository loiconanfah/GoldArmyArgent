# Guide d'Installation

## Étape 1 : Installation des dépendances

```bash
cd MobileGoldArmy_NEW

# Installer toutes les dépendances
npm install

# Installer les dépendances Expo avec les bonnes versions
npx expo install --fix
```

## Étape 2 : Configuration

### Variables d'environnement

Créer un fichier `.env` à la racine :

```env
EXPO_PUBLIC_API_URL=https://your-api.onrender.com
EXPO_PUBLIC_APP_ENV=development
```

### Assets

Copier les assets depuis l'ancien projet si nécessaire :
- `assets/icon.png`
- `assets/splash-icon.png`
- `assets/android-icon-foreground.png`
- `assets/android-icon-background.png`
- `assets/favicon.png`

## Étape 3 : Démarrer l'application

```bash
# Démarrer Expo
npx expo start

# Ou avec cache clear
npx expo start --clear
```

## Étape 4 : Tester sur Expo Go

1. Installer Expo Go sur votre appareil iOS/Android
2. Scanner le QR code affiché dans le terminal
3. L'application devrait se charger

## 🔧 Dépannage

### Erreur "Cannot find module"
→ Exécuter `npm install` puis `npx expo install --fix`

### Erreur TypeScript
→ Vérifier que `tsconfig.json` est correct
→ Exécuter `npm run type-check` pour voir les erreurs

### Erreur Metro
→ Nettoyer le cache : `npx expo start --clear`
→ Supprimer `node_modules` et réinstaller

### Erreur Babel
→ Vérifier que `react-native-reanimated/plugin` est en dernier dans `babel.config.js`

## 📦 Dépendances principales

Toutes installées via `npx expo install` pour garantir la compatibilité :

- `expo-router` - Navigation file-based
- `@tanstack/react-query` - Server state
- `zustand` - State management
- `axios` - HTTP client
- `react-hook-form` + `zod` - Formulaires
- `react-native-reanimated` - Animations
- `moti` - Animations déclaratives
- `expo-secure-store` - Stockage sécurisé
- `expo-blur` - Effets blur
- `expo-linear-gradient` - Dégradés
- `expo-image` - Images optimisées
