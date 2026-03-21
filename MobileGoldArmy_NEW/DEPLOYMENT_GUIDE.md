# Guide de Déploiement : App Store & Play Store

Votre application **MobileGoldArmy** est désormais 100% configurée au niveau de son `app.json` et des permissions pour être envoyée sur les Stores.
Voici les étapes pour la compiler et la soumettre.

## Prérequis
1. Avoir un compte **Expo** (gratuit).
2. Avoir un compte **Apple Developer** (99$/an) pour l'App Store.
3. Avoir un compte **Google Play Developer** (25$ à vie) pour le Play Store.
4. Installer l'outil CLI d'EAS : `npm install -g eas-cli`
5. Vous connecter à votre compte Expo dans ce terminal : `eas login`

---

## 🍎 Déploiement iOS (App Store)

### 1. Lancer la compilation (Build)
Exécutez la commande suivante depuis le dossier `MobileGoldArmy_NEW` :
```bash
eas build --platform ios --profile production
```
L'outil vous demandera vos identifiants Apple Developer. EAS s'occupera automatiquement de générer les certificats de distribution et les profils de provisionnement. Patientez (~15 à 30 min) que les serveurs d'Expo complètent le build.

### 2. Soumettre à l'App Store Connect
Une fois le build terminé, soumettez-le avec :
```bash
eas submit -p ios
```
Sélectionnez le build que vous venez de générer. Il sera envoyé sur TestFlight / App Store Connect où vous pourrez remplir les fiches descriptives (captures d'écran, nom, etc.) et le soumettre à la validation par Apple.

---

## 🤖 Déploiement Android (Play Store)

### 1. Lancer la compilation (Build)
Exécutez cette commande :
```bash
eas build --platform android --profile production
```
EAS générera un fichier `.aab` (Android App Bundle), qui est le format obligatoire pour le Play Store. L'outil gérera vos clés de signature (Keystore) automatiquement. Conservez précieusement ces clés sur votre compte Expo.

### 2. Soumettre au Play Store
```bash
eas submit -p android
```
**Attention :** La TOUTE PREMIÈRE FOIS que vous publiez l'application Android, Google oblige l'upload manuel. Vous devrez aller sur la *Google Play Console*, créer l'application, et uploader le fichier `.aab` à la main (le lien de téléchargement vous est fourni par Expo à la fin du `eas build`). 
Les fois suivantes (Mises à jour), la commande `eas submit` fonctionnera automatiquement sans interface web !

---
## 💡 L'avantage de votre configuration (autoIncrement)
Dans le fichier `eas.json` que j'ai créé, j'ai configuré `"autoIncrement": true`. 
Cela signifie qu'à chaque fois que vous lancerez la commande de build, la version interne (ios.buildNumber et android.versionCode) s'incrémentera toute seule. Vous n'aurez jamais d'erreur *"Ce numéro de version existe déjà"* sur les Stores !
