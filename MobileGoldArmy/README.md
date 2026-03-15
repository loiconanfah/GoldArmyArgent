# MobileGoldArmy – Version mobile Expo

Application mobile **Expo (React Native)** pour GoldArmy, branchée sur la même API que le frontend web.

## Prérequis

- **Node.js >= 20.19.4** (requis par Expo 55). Vérifier avec `node -v`. Si tu as une version plus ancienne, installe la [LTS depuis nodejs.org](https://nodejs.org/en/download).
- Backend GoldArmy démarré (par défaut `http://localhost:8000`)

## Installation

```bash
cd MobileGoldArmy
npm install
```

## Configuration API

- **Développement** : l’app utilise par défaut  
  - `http://localhost:8000` (iOS simulateur)  
  - `http://10.0.2.2:8000` (Android émulateur)
- **Production** : définir la variable d’environnement `EXPO_PUBLIC_API_URL` (ex. `https://goldarmy.onrender.com`).

Fichier de config : `src/config.js`.

**CORS** : si le backend rejette les requêtes depuis l’app mobile, ajoute l’origine Expo dans ton backend (variable `CORS_ORIGIN` ou dans `api/main.py`), par ex. `exp://192.168.1.x:8081` pour Expo Go en dev.

## Lancer l’app

```bash
npx expo start
```

Puis :
- **iOS** : `i` dans le terminal ou scan du QR code avec l’app Expo Go
- **Android** : `a` dans le terminal ou scan du QR code avec Expo Go

## Structure

```
MobileGoldArmy/
├── App.js                 # Point d’entrée (AuthProvider + navigation)
├── src/
│   ├── config.js          # URL de l’API (dev / prod)
│   ├── api/
│   │   └── client.js      # Appels API (auth, chat, etc.)
│   ├── context/
│   │   └── AuthContext.js # État auth (user, token)
│   ├── navigation/
│   │   └── AppNavigator.js # Stack : Login, Register, Home
│   └── screens/
│       ├── LoginScreen.js
│       ├── RegisterScreen.js
│       └── HomeScreen.js  # Exemple chat avec l’API
└── README.md
```

## API utilisée

- **Auth** : `POST /api/auth/login`, `POST /api/auth/register`, `GET /api/auth/me`
- **Chat** : `POST /api/chat` (exemple dans Home)
- Token stocké dans **expo-secure-store**, envoyé en `Authorization: Bearer <token>` sur les routes protégées.

Tu peux étendre `src/api/client.js` avec les mêmes endpoints que le frontend (opportunités, CRM, interview, profil, etc.) et ajouter les écrans correspondants dans `src/screens/` et la navigation.

## Prochaines étapes possibles

- Écrans : Opportunités, CRM, Interview, Profil, Paramètres
- Navigation par onglets (bottom tabs) pour Home / Opportunités / CRM / Profil
- WebSockets pour le chat ou l’interview en temps réel (voir `getWsUrl` dans `config.js`)
