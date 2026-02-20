# 🪖 GoldArmyArgent

**Armée d'Agents IA 100% Autonomes** - Système multi-agents utilisant Ollama en local

## 🎯 Description

GoldArmyArgent est une plateforme avancée de gestion d'agents IA autonomes. Chaque agent est spécialisé dans un domaine (recherche, développement, planification) et peut collaborer avec d'autres agents pour accomplir des tâches complexes.

## ✨ Fonctionnalités

- 🤖 **Agents Autonomes** - Cycle think-act-learn pour chaque agent
- 🧠 **Mémoire Partagée** - Base vectorielle ChromaDB pour contexte persistant
- 📡 **Communication Inter-Agents** - Bus de messages asynchrone
- 🎭 **Orchestration Intelligente** - Gestion automatique du pool d'agents
- 🔧 **Agents Spécialisés**:
  - **Researcher** - Recherche et analyse d'informations
  - **Coder** - Génération et débogage de code
  - **Planner** - Décomposition de tâches complexes
- 💻 **Interface CLI** - Interface en ligne de commande riche
- 📊 **Dashboard** - Interface Streamlit (à venir)

## 🚀 Installation

### Prérequis

- Python 3.11+
- Ollama installé et en cours d'exécution

### Étapes

1. **Cloner le projet** (déjà fait !)

2. **Installer les dépendances**:
```bash
pip install -r requirements.txt
```

3. **Configurer l'environnement**:
```bash
cp .env.example .env
# Éditer .env si nécessaire
```

4. **Vérifier Ollama**:
```bash
python main.py test-ollama
```

5. **Télécharger les modèles** (si nécessaire):
```bash
ollama pull llama2
ollama pull codellama  # Pour l'agent Coder
```

## 📖 Utilisation

### Mode Interactif (Recommandé)

```bash
python main.py interactive
```

Tapez vos tâches et l'armée d'agents les exécutera automatiquement !

### Commandes CLI

```bash
# Informations système
python main.py info

# Tester Ollama
python main.py test-ollama

# Créer un agent
python main.py create-agent researcher

# Exécuter une tâche
python main.py run-task "Recherche sur l'IA" --agent-type researcher

# Voir les statistiques
python main.py stats
```

### Utilisation Programmatique

```python
import asyncio
from core.orchestrator import orchestrator

async def main():
    await orchestrator.start()
    
    # Créer un agent
    agent = await orchestrator.create_agent("researcher")
    
    # Soumettre une tâche
    task = {
        "description": "Analyser les tendances IA 2024",
        "agent_type": "researcher"
    }
    
    result = await orchestrator.execute_task(task)
    print(result)
    
    await orchestrator.stop()

asyncio.run(main())
```

## 🏗️ Architecture

```
GoldArmyArgent/
├── core/               # Système central
│   ├── agent_base.py   # Classe de base des agents
│   ├── orchestrator.py # Orchestrateur principal
│   ├── memory.py       # Système de mémoire
│   └── communication.py # Bus de communication
├── agents/             # Agents spécialisés
│   ├── researcher.py
│   ├── coder.py
│   └── planner.py
├── llm/                # Interface Ollama
│   ├── ollama_client.py
│   └── prompt_templates.py
├── config/             # Configuration
│   ├── settings.py
│   └── agents_config.yaml
└── main.py             # Point d'entrée
```

## ⚙️ Configuration

Éditez `config/agents_config.yaml` pour personnaliser les agents:

```yaml
agents:
  researcher:
    model: "llama2"
    temperature: 0.7
    max_tokens: 2048
```

## 🔧 Développement

### Ajouter un Nouvel Agent

1. Créer `agents/mon_agent.py`:
```python
from core.agent_base import BaseAgent

class MonAgent(BaseAgent):
    async def think(self, task):
        # Logique de réflexion
        pass
    
    async def act(self, action_plan):
        # Logique d'action
        pass
```

2. Enregistrer dans `core/orchestrator.py`:
```python
self.agent_types["mon_agent"] = MonAgent
```

## 📝 TODO

- [ ] Dashboard Streamlit
- [ ] Outils de recherche web
- [ ] Exécution de code sécurisée
- [ ] Agents Analyst et Executor
- [ ] Tests unitaires
- [ ] Documentation API complète

## 📄 Licence

MIT

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue ou une PR.

---

**Fait avec ❤️ et Ollama 🦙**
