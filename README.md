# 🪖 GoldArmy AI

**Plateforme SaaS de chasse à l'emploi propulsée par l'IA** — [goldarmyai.com](https://goldarmyai.com)

GoldArmy AI aide les candidats à décrocher un emploi grâce à une armée d'agents IA spécialisés :
recherche d'offres ciblée, optimisation de CV ATS, simulation d'entretien, CRM de candidatures,
relances automatiques et prospection réseau.

> ⚠️ Ce dépôt a évolué d'un prototype multi-agents Ollama vers un produit SaaS commercial complet
> (backend FastAPI + MongoDB, frontend Vue 3, paiements Stripe, app mobile). L'ancien README
> décrivait le prototype ; ce document reflète le produit réel.

## ✨ Fonctionnalités principales

- **CV Sniper** — recherche d'offres + matching intelligent avec le profil du candidat
- **Adaptation de CV** — réécriture du CV pour une offre précise (Gemini)
- **Générateur ATS** — export PDF (Playwright) et Word, 8 templates
- **Simulateur d'entretien** — préparation et questions personnalisées
- **CRM Kanban** — pipeline de candidatures drag-and-drop + relances auto
- **Réseau / Headhunter** — enrichissement de contacts, décideurs LinkedIn, emails d'approche
- **Gold Profile** — audit de personal branding LinkedIn + plan de contenu
- **Agents autonomes** — Ghostbuster (relance 48h), Daily Hunt, Pre-Interview (schedulers)
- **Comptes & facturation** — Auth JWT + Google, abonnements Stripe, parrainage

## 🏗️ Stack technique

| Couche | Technologies |
|--------|--------------|
| Backend | FastAPI, MongoDB Atlas (motor), JWT + Google Auth |
| IA / LLM | Google Gemini (`gemini-2.0-flash` / `2.5-flash`), client LLM unifié |
| Scraping / PDF | Playwright, BeautifulSoup, PyMuPDF, python-docx |
| Frontend | Vue 3 + Vite, Vue Router, i18n (fr/en) |
| Paiement / Email | Stripe, Resend |
| Mémoire | ChromaDB, sentence-transformers |
| Déploiement | Render (`render.yaml`) |

## 📁 Structure du dépôt

```
GoldArmyArgent/
├── api/                # Routes FastAPI (main.py, auth, interview, stripe, referral…)
├── agents/             # Agents métier (hunter, headhunter, cv_adapter, mentor, ghostbuster…)
├── core/               # Services transverses (database, email, CV gen, schedulers, memory)
├── llm/                # Clients LLM (Gemini, unified client)
├── tools/              # Outils (web_searcher, linkedin_scraper)
├── config/             # settings.py + agents_config.yaml
├── frontend/           # Application Vue 3 (views, components, templates de CV)
├── MobileGoldArmy*/    # Application mobile
├── render.yaml         # Configuration de déploiement Render
└── requirements.txt    # Dépendances Python
```

## 🚀 Développement local

### Prérequis
- Python 3.11+
- Node.js 18+
- Une instance MongoDB (Atlas recommandé)

### Backend
```bash
python -m venv .venv
.venv\Scripts\activate        # Windows  (source .venv/bin/activate sous Unix)
pip install -r requirements.txt
playwright install chromium
cp .env.example .env          # puis renseigner les variables
uvicorn api.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev                   # http://localhost:5173
```

### Lancer les deux
```bash
start_all.bat                 # Windows
./start_all.sh                # Unix
```

## ⚙️ Configuration

Les variables sensibles vivent dans `.env` (jamais commité — voir `.env.example`) :
clés Gemini, MongoDB URI, secret JWT, clés Stripe, clés Resend, Google OAuth.

Les modèles et capacités des agents se règlent dans `config/agents_config.yaml`.

## 📄 Licence

MIT
