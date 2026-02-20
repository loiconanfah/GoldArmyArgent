# 🚀 Guide d'Installation - GoldArmyArgent

## ✅ Ce qui a été créé

Votre projet **GoldArmyArgent** est maintenant complètement structuré avec:

### 📁 Structure du Projet
```
GoldArmyArgent/
├── core/                    ✅ Système central
│   ├── agent_base.py       ✅ Classe de base des agents
│   ├── orchestrator.py     ✅ Orchestrateur principal
│   ├── memory.py           ✅ Système de mémoire
│   ├── communication.py    ✅ Bus de communication
│   └── __init__.py         ✅
├── agents/                  ✅ Agents spécialisés
│   ├── researcher.py       ✅ Agent de recherche
│   ├── coder.py            ✅ Agent développeur
│   ├── planner.py          ✅ Agent planificateur
│   └── __init__.py         ✅
├── llm/                     ✅ Interface Ollama
│   ├── ollama_client.py    ✅ Client Ollama async
│   ├── prompt_templates.py ✅ Templates de prompts
│   └── __init__.py         ✅
├── config/                  ✅ Configuration
│   ├── settings.py         ✅ Configuration Pydantic
│   ├── agents_config.yaml  ✅ Config des agents
│   └── __init__.py         ✅
├── main.py                  ✅ Point d'entrée CLI
├── requirements.txt         ✅ Dépendances
├── .env.example            ✅ Template d'environnement
├── .gitignore              ✅
└── README.md               ✅ Documentation
```

## 🔧 Prochaines Étapes - Installation

### 1. ✅ Vérifier Python

Vous devez avoir Python 3.11+ installé. Vérifiez avec:

```powershell
python --version
# OU
py --version
# OU
python3 --version
```

**Si Python n'est pas installé:**
1. Téléchargez Python depuis https://www.python.org/downloads/
2. ⚠️ **IMPORTANT**: Cochez "Add Python to PATH" pendant l'installation
3. Redémarrez votre terminal

### 2. 📦 Installer les Dépendances

Une fois Python installé, dans le dossier `GoldArmyArgent`:

```powershell
# Avec python
python -m pip install -r requirements.txt

# OU avec py
py -m pip install -r requirements.txt
```

### 3. 🦙 Vérifier Ollama

Ollama doit être en cours d'exécution. Testez:

```powershell
# Dans un nouveau terminal
ollama list
```

**Si Ollama n'est pas dans le PATH:**
- Vérifiez que le service Ollama tourne (cherchez dans la barre des tâches)
- Ou démarrez-le manuellement

### 4. 📥 Télécharger les Modèles

Téléchargez les modèles nécessaires:

```powershell
ollama pull llama2
ollama pull codellama  # Pour l'agent Coder (optionnel)
```

### 5. ⚙️ Configuration (Optionnel)

Créez un fichier `.env` à partir du template:

```powershell
copy .env.example .env
```

Éditez `.env` si vous voulez changer les paramètres par défaut.

### 6. 🧪 Tester l'Installation

```powershell
# Tester Ollama
python main.py test-ollama

# Voir les infos système
python main.py info

# Mode interactif
python main.py interactive
```

## 🎮 Utilisation

### Mode Interactif (Recommandé pour débuter)

```powershell
python main.py interactive
```

Tapez vos tâches et appuyez sur Entrée:
- "Recherche sur l'intelligence artificielle"
- "Écris une fonction Python pour trier une liste"
- "Crée un plan pour développer une application web"

### Commandes Disponibles

```powershell
# Informations
python main.py info

# Tester Ollama
python main.py test-ollama

# Créer un agent spécifique
python main.py create-agent researcher
python main.py create-agent coder
python main.py create-agent planner

# Exécuter une tâche
python main.py run-task "Ta tâche ici" --agent-type researcher

# Voir les statistiques
python main.py stats

# Mode interactif
python main.py interactive
```

## 🐛 Dépannage

### Python n'est pas reconnu
- Réinstallez Python en cochant "Add to PATH"
- Ou utilisez `py` au lieu de `python`

### Ollama n'est pas disponible
- Vérifiez que le service Ollama tourne
- Vérifiez l'URL dans `.env`: `OLLAMA_HOST=http://localhost:11434`

### Erreur d'import de modules
- Réinstallez les dépendances: `python -m pip install -r requirements.txt --upgrade`

### ChromaDB ne s'installe pas
- ChromaDB est optionnel pour la mémoire vectorielle
- Le système fonctionnera avec la mémoire RAM uniquement

## 📚 Documentation Complète

Consultez `README.md` pour:
- Architecture détaillée
- Utilisation programmatique
- Création de nouveaux agents
- Configuration avancée

## 🎯 Exemples de Tâches

Une fois installé, essayez:

```
🔍 Researcher:
- "Analyse les tendances de l'IA en 2024"
- "Recherche sur les meilleures pratiques Python"

💻 Coder:
- "Écris une fonction pour calculer Fibonacci"
- "Crée un script pour lire un fichier CSV"

📊 Planner:
- "Décompose la création d'une API REST"
- "Planifie le développement d'un chatbot"
```

## ✨ Prochaines Améliorations

- [ ] Dashboard Streamlit
- [ ] Outils de recherche web
- [ ] Agent Executor pour exécution de commandes
- [ ] Tests unitaires
- [ ] Plus de modèles Ollama supportés

---

**Besoin d'aide?** Consultez le README.md ou demandez-moi ! 🚀
