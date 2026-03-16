# MobileGoldArmy - Expo Mobile App

Application mobile React Native / Expo production-ready avec architecture scalable.

## 🚀 Installation

```bash
# Installer les dépendances
npm install

# Installer les dépendances Expo compatibles
npx expo install --fix

# Configurer les variables d'environnement
cp .env.example .env
# Éditer .env et mettre votre API_URL

# Démarrer l'application
npx expo start
```

## 📁 Architecture

```
MobileGoldArmy_NEW/
├── app/                    # Expo Router (file-based routing)
│   ├── _layout.tsx        # Root layout avec providers
│   ├── index.tsx          # Redirect basé sur auth
│   ├── (auth)/            # Routes d'authentification
│   └── (tabs)/            # Routes avec tabs
├── src/
│   ├── components/        # Composants réutilisables
│   │   ├── ui/           # Composants atomiques
│   │   ├── layout/       # Composants de layout
│   │   └── features/     # Composants métier
│   ├── hooks/            # Hooks custom
│   ├── stores/           # Zustand stores
│   ├── services/          # Services API
│   ├── queries/          # React Query hooks
│   ├── providers/         # Providers React
│   ├── theme/            # Système de thème
│   ├── types/             # Types TypeScript
│   └── utils/             # Utilitaires
└── assets/                # Assets statiques
```

## 🛠 Stack Technique

- **Expo SDK 54** - Managed workflow
- **Expo Router** - File-based routing
- **TypeScript** - Strict mode
- **Zustand** - State management UI
- **React Query** - Server state & cache
- **Axios** - HTTP client avec intercepteurs JWT
- **React Hook Form + Zod** - Formulaires & validation
- **React Native Reanimated** - Animations thread UI
- **Moti** - Animations déclaratives

## 🔐 Authentification

- JWT avec access token + refresh token
- Tokens stockés dans `expo-secure-store`
- Intercepteurs Axios pour refresh automatique
- Guard d'authentification via `AuthProvider`

## 🎨 Thème

- Support dark/light mode
- Système de couleurs cohérent
- Typographie hiérarchisée
- Spacing system (4/8/12/16/24/32/48/64)
- Ombres iOS + elevation Android

## 📝 Variables d'environnement

Créer un fichier `.env` :

```
EXPO_PUBLIC_API_URL=https://your-api.onrender.com
EXPO_PUBLIC_APP_ENV=development
```

## 🚦 Scripts

```bash
npm start          # Démarrer Expo
npm run android    # Démarrer sur Android
npm run ios        # Démarrer sur iOS
npm run type-check # Vérifier les types TypeScript
```

## ✅ Compatibilité

- ✅ Expo Go (iOS + Android)
- ✅ Expo managed workflow
- ✅ TypeScript strict
- ✅ Toutes les libs compatibles Expo

## 📚 Documentation

Voir les commentaires dans le code pour plus de détails sur chaque module.
