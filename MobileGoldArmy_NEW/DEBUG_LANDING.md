# Debug Landing Page

## Problème : La landing page ne s'affiche pas

### Étapes de diagnostic

1. **Vérifier les erreurs dans la console Metro**
   - Regarder les erreurs rouges dans le terminal
   - Vérifier les warnings

2. **Tester avec la version simplifiée**
   Dans `app/(tabs)/home.tsx`, décommentez temporairement :
   ```typescript
   import LandingPageTest from '../../src/screens/LandingPageTest';
   return <LandingPageTest />;
   ```
   Si ça fonctionne, le problème vient de la landing page complète.

3. **Vérifier les dépendances**
   ```bash
   npx expo install expo-linear-gradient expo-blur expo-image expo-haptics react-native-gesture-handler
   ```

4. **Vérifier les imports**
   - Tous les imports doivent être valides
   - Vérifier que `useSafeAreaInsets` fonctionne

5. **Erreurs courantes**
   - `scrollY.addListener` peut causer des problèmes
   - Les refs forwardRef peuvent avoir des problèmes de typage
   - Les animations peuvent bloquer le rendu

### Corrections appliquées

✅ Corrigé l'auto-scroll du carrousel partenaires (plus d'accès à `_scrollMetrics`)
✅ Ajouté un fallback pour `scrollY.addListener`
✅ Ajouté `onScrollToIndexFailed` pour le carrousel features
✅ Déclaré `partnersScrollOffset` ref

### Prochaines étapes

Si la landing page ne s'affiche toujours pas :
1. Vérifier les logs Metro pour les erreurs exactes
2. Tester avec `LandingPageTest` pour isoler le problème
3. Vérifier que tous les composants sont bien importés
