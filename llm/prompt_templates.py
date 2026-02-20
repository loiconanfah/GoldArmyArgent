"""Templates de prompts pour les différents agents."""
from typing import Dict, Any
from jinja2 import Template


class PromptTemplates:
    """Gestionnaire de templates de prompts."""
    
    # Template système pour l'agent Researcher
    RESEARCHER_SYSTEM = """Tu es un agent de recherche expert et autonome.
Ta mission est de trouver, analyser et synthétiser des informations pertinentes.

Capacités:
- Rechercher des informations précises
- Analyser et valider des sources
- Synthétiser des données complexes
- Identifier des patterns et tendances

Réponds de manière structurée, factuelle et concise."""

    # Template système pour l'agent Coder
    CODER_SYSTEM = """Tu es un agent développeur expert et autonome.
Ta mission est d'écrire du code de haute qualité, débugger et optimiser.

Capacités:
- Écrire du code propre et maintenable
- Débugger et résoudre des problèmes
- Optimiser les performances
- Suivre les meilleures pratiques

Réponds avec du code fonctionnel et bien commenté."""

    # Template système pour l'agent Planner
    PLANNER_SYSTEM = """Tu es un agent planificateur expert et autonome.
Ta mission est de décomposer des tâches complexes en étapes réalisables.

Capacités:
- Analyser des objectifs complexes
- Créer des plans d'action détaillés
- Identifier les dépendances
- Optimiser les workflows

Réponds avec des plans structurés et actionnables."""

    # Template système pour l'agent Analyst
    ANALYST_SYSTEM = """Tu es un agent analyste expert et autonome.
Ta mission est de traiter, analyser et interpréter des données.

Capacités:
- Analyser des données complexes
- Identifier des patterns
- Générer des insights
- Créer des rapports clairs

Réponds avec des analyses précises et des visualisations quand pertinent."""

    # Template système pour l'agent Executor
    EXECUTOR_SYSTEM = """Tu es un agent exécuteur expert et autonome.
Ta mission est d'exécuter des actions concrètes de manière fiable.

Capacités:
- Exécuter des commandes
- Gérer des processus
- Monitorer l'exécution
- Gérer les erreurs

Réponds avec des résultats d'exécution clairs et des logs détaillés."""

    # Template pour une tâche de recherche
    RESEARCH_TASK = Template("""
Tâche de recherche:
{{ task_description }}

Contexte:
{{ context }}

Instructions:
1. Recherche les informations pertinentes
2. Valide les sources
3. Synthétise les résultats
4. Fournis une réponse structurée

Réponds au format:
## Résultats
[tes résultats]

## Sources
[tes sources]

## Conclusion
[ta synthèse]
""")

    # Template pour une tâche de code
    CODE_TASK = Template("""
Tâche de développement:
{{ task_description }}

Contexte:
{{ context }}

{% if existing_code %}
Code existant:
```{{ language }}
{{ existing_code }}
```
{% endif %}

Instructions:
1. Analyse le besoin
2. Écris le code
3. Ajoute des commentaires
4. Teste mentalement

Réponds au format:
## Code
```{{ language }}
[ton code]
```

## Explication
[ton explication]

## Tests suggérés
[tes suggestions de tests]
""")

    # Template pour une tâche de planification
    PLANNING_TASK = Template("""
Objectif à planifier:
{{ objective }}

Contexte:
{{ context }}

Contraintes:
{{ constraints }}

Instructions:
1. Décompose l'objectif en tâches
2. Identifie les dépendances
3. Estime la complexité
4. Propose un ordre d'exécution

Réponds au format:
## Plan d'action
[ton plan détaillé]

## Dépendances
[les dépendances identifiées]

## Estimation
[ton estimation]
""")

    @classmethod
    def get_system_prompt(cls, agent_type: str) -> str:
        """
        Récupère le prompt système pour un type d'agent.
        
        Args:
            agent_type: Type d'agent (researcher, coder, planner, analyst, executor)
        
        Returns:
            Prompt système
        """
        prompts = {
            "researcher": cls.RESEARCHER_SYSTEM,
            "coder": cls.CODER_SYSTEM,
            "planner": cls.PLANNER_SYSTEM,
            "analyst": cls.ANALYST_SYSTEM,
            "executor": cls.EXECUTOR_SYSTEM,
        }
        return prompts.get(agent_type, "Tu es un agent IA autonome et expert.")
    
    @classmethod
    def render_task_prompt(cls, agent_type: str, **kwargs) -> str:
        """
        Génère un prompt de tâche pour un agent.
        
        Args:
            agent_type: Type d'agent
            **kwargs: Variables pour le template
        
        Returns:
            Prompt rendu
        """
        templates = {
            "researcher": cls.RESEARCH_TASK,
            "coder": cls.CODE_TASK,
            "planner": cls.PLANNING_TASK,
        }
        
        template = templates.get(agent_type)
        if template:
            return template.render(**kwargs)
        
        # Template générique
        return f"Tâche: {kwargs.get('task_description', 'Non spécifiée')}\nContexte: {kwargs.get('context', 'Aucun')}"
