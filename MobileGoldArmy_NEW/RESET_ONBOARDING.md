# Réinitialiser l'onboarding pour tester

Si l'onboarding ne s'affiche pas au démarrage, c'est probablement parce que la clé `onboarding_completed` existe déjà dans SecureStore avec la valeur `'true'`.

## Solution rapide : Forcer la suppression temporairement

### Option 1 : Modifier `app/index.tsx` temporairement

Ajoutez cette ligne **au début** de la fonction `checkAndRedirect` dans `app/index.tsx` :

```typescript
// Dans app/index.tsx, ligne ~18, au début de checkAndRedirect
await SecureStore.deleteItemAsync('onboarding_completed'); // ← Ajoutez cette ligne
```

Puis :
1. Redémarrez l'app (reload avec `r` dans le terminal Expo)
2. L'onboarding devrait s'afficher
3. **Supprimez cette ligne** après le test

### Option 2 : Utiliser l'utilitaire (recommandé)

Importez et utilisez la fonction utilitaire :

```typescript
// Dans app/index.tsx, ajoutez en haut :
import { resetOnboarding } from '../src/utils/resetOnboarding';

// Puis dans checkAndRedirect, au début :
await resetOnboarding(); // Force la réinitialisation
```

### Option 3 : Réinstaller l'app complètement

1. Supprimez l'app Expo Go de votre appareil
2. Réinstallez-la
3. Toutes les données SecureStore seront supprimées

## Vérifier l'état actuel

Pour déboguer, ajoutez temporairement dans `app/index.tsx` :

```typescript
const onboardingValue = await SecureStore.getItemAsync('onboarding_completed');
console.log('🔍 [Index] Onboarding value:', onboardingValue);
console.log('🔍 [Index] Should show onboarding?', !onboardingValue || onboardingValue !== 'true');
```

## Logique de redirection (ordre d'exécution)

L'app vérifie dans cet ordre **strict** :

1. **PRIORITÉ 1** : `onboarding_completed` existe et vaut exactement `'true'` ?
   - ❌ NON → Redirige vers `/onboarding` (STOP)
   - ✅ OUI → Continue

2. **PRIORITÉ 2** : `access_token` existe ?
   - ✅ OUI → Redirige vers `/(tabs)/home`
   - ❌ NON → Redirige vers `/(auth)/login`

## Problème courant

Si vous voyez le login au lieu de l'onboarding, c'est que `onboarding_completed` vaut `'true'` dans SecureStore. Utilisez l'Option 1 ci-dessus pour le réinitialiser.
