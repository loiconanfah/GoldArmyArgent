# Flux de démarrage de l'application

## Organisation du démarrage

### 1. `app/_layout.tsx` (Root Layout)
- **Rôle** : Configuration globale, providers, gestion du splash screen
- **Action** : Cache le splash screen dès que les fonts sont chargées
- **Ne redirige PAS** : La redirection est gérée par `app/index.tsx`

### 2. `app/index.tsx` (Route initiale)
- **Rôle** : Point d'entrée de l'app, vérifie l'onboarding et redirige
- **Logique** :
  1. Vérifie `onboarding_completed` dans SecureStore
  2. Si non complété → redirige vers `/onboarding`
  3. Si complété + token → redirige vers `/(tabs)/home`
  4. Si complété + pas de token → redirige vers `/(auth)/login`

### 3. `app/onboarding.tsx`
- **Rôle** : Affiche l'onboarding au premier lancement
- **Action** : Une fois complété, écrit `onboarding_completed: 'true'` et redirige vers login

### 4. `src/providers/AuthProvider.tsx`
- **Rôle** : Gère l'état d'authentification
- **Ne redirige PAS** depuis l'onboarding ou l'index
- **Redirige** uniquement entre auth et tabs selon l'état de connexion

## Ordre d'exécution

```
1. App démarre
   ↓
2. _layout.tsx charge les fonts
   ↓
3. Splash screen se cache immédiatement
   ↓
4. index.tsx vérifie onboarding_completed
   ↓
5a. Si non complété → /onboarding
5b. Si complété + token → /(tabs)/home
5c. Si complété + pas token → /(auth)/login
```

## Routes accessibles sans authentification

- ✅ `/` (index) - Route initiale
- ✅ `/onboarding` - Onboarding
- ✅ `/(auth)/login` - Login
- ✅ `/(auth)/register` - Register
- ✅ `/(auth)/forgot-password` - Forgot password

## Routes nécessitant une authentification

- 🔒 `/(tabs)/home` - Home
- 🔒 `/(tabs)/explore` - Explore
- 🔒 `/(tabs)/profile` - Profile
- 🔒 `/(tabs)/settings` - Settings

## Test du flux

### Tester l'onboarding
```typescript
// Supprimer la clé onboarding_completed
import * as SecureStore from 'expo-secure-store';
await SecureStore.deleteItemAsync('onboarding_completed');
// Redémarrer l'app
```

### Tester sans onboarding
```typescript
// Marquer l'onboarding comme complété
await SecureStore.setItemAsync('onboarding_completed', 'true');
// Redémarrer l'app
```
