"""Version démo simplifiée de GoldArmyArgent - SANS dépendances externes.

Cette version fonctionne avec Python standard uniquement (pas besoin de pip).
Elle simule le comportement des agents pour démonstration.
"""
import asyncio
import json
from datetime import datetime
from typing import Dict, Any, List


class SimpleAgent:
    """Agent simplifié sans dépendances externes."""
    
    def __init__(self, name: str, agent_type: str):
        self.name = name
        self.agent_type = agent_type
        self.tasks_completed = 0
    
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Exécute une tâche (mode démo)."""
        print(f"\n🤖 {self.name} ({self.agent_type}) commence la tâche...")
        print(f"📝 Description: {task.get('description', 'N/A')}")
        
        # Simulation de réflexion
        print(f"💭 {self.name} réfléchit...")
        await asyncio.sleep(1)
        
        # Simulation d'action
        print(f"⚙️ {self.name} agit...")
        await asyncio.sleep(1)
        
        # Résultat simulé
        result = self._generate_demo_result(task)
        
        self.tasks_completed += 1
        print(f"✅ Tâche terminée!")
        
        return result
    
    def _generate_demo_result(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Génère un résultat de démonstration."""
        description = task.get('description', '').lower()
        
        if self.agent_type == "researcher":
            return {
                "success": True,
                "type": "research",
                "findings": f"Résultats de recherche sur: {task.get('description', 'N/A')}",
                "summary": "Analyse complète effectuée. Plusieurs sources consultées.",
                "confidence": 0.85
            }
        
        elif self.agent_type == "coder":
            return {
                "success": True,
                "type": "code",
                "code": f"# Code généré pour: {task.get('description', 'N/A')}\ndef solution():\n    # Implémentation ici\n    pass",
                "language": "python",
                "explanation": "Code généré selon les meilleures pratiques."
            }
        
        elif self.agent_type == "planner":
            return {
                "success": True,
                "type": "plan",
                "plan": f"Plan pour: {task.get('description', 'N/A')}",
                "tasks": [
                    "1. Analyse des besoins",
                    "2. Conception de la solution",
                    "3. Implémentation",
                    "4. Tests et validation"
                ],
                "estimated_time": "Variable selon complexité"
            }
        
        return {"success": True, "message": "Tâche exécutée"}


class SimpleOrchestrator:
    """Orchestrateur simplifié."""
    
    def __init__(self):
        self.agents: Dict[str, SimpleAgent] = {}
        self._create_default_agents()
    
    def _create_default_agents(self):
        """Crée les agents par défaut."""
        self.agents["researcher"] = SimpleAgent("Researcher", "researcher")
        self.agents["coder"] = SimpleAgent("Coder", "coder")
        self.agents["planner"] = SimpleAgent("Planner", "planner")
    
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Exécute une tâche avec l'agent approprié."""
        agent_type = task.get("agent_type", "researcher")
        agent = self.agents.get(agent_type)
        
        if not agent:
            return {"success": False, "error": f"Agent {agent_type} non trouvé"}
        
        return await agent.execute_task(task)
    
    def get_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques."""
        return {
            "total_agents": len(self.agents),
            "agents": {
                name: {
                    "type": agent.agent_type,
                    "tasks_completed": agent.tasks_completed
                }
                for name, agent in self.agents.items()
            }
        }


async def interactive_mode():
    """Mode interactif simplifié."""
    print("=" * 70)
    print("🪖 GoldArmyArgent - Mode Démo (Sans dépendances)")
    print("=" * 70)
    print("\nCette version fonctionne SANS Ollama ni bibliothèques externes.")
    print("Les agents simulent leur comportement pour démonstration.\n")
    print("Commandes:")
    print("  - Tapez votre tâche et appuyez sur Entrée")
    print("  - 'stats' pour voir les statistiques")
    print("  - 'quit' pour quitter\n")
    print("=" * 70)
    
    orchestrator = SimpleOrchestrator()
    
    while True:
        try:
            task_input = input("\n🎯 Tâche > ").strip()
            
            if not task_input:
                continue
            
            if task_input.lower() in ["quit", "exit", "q"]:
                print("\n👋 Au revoir!")
                break
            
            if task_input.lower() == "stats":
                stats = orchestrator.get_stats()
                print("\n📊 Statistiques:")
                print(json.dumps(stats, indent=2, ensure_ascii=False))
                continue
            
            # Déterminer le type d'agent
            agent_type = "researcher"
            if any(word in task_input.lower() for word in ["code", "programme", "fonction", "script"]):
                agent_type = "coder"
            elif any(word in task_input.lower() for word in ["plan", "organise", "étapes"]):
                agent_type = "planner"
            
            # Exécuter la tâche
            task = {
                "description": task_input,
                "agent_type": agent_type,
                "timestamp": datetime.now().isoformat()
            }
            
            result = await orchestrator.execute_task(task)
            
            # Afficher le résultat
            print("\n" + "=" * 70)
            print("📋 RÉSULTAT:")
            print("=" * 70)
            print(json.dumps(result, indent=2, ensure_ascii=False))
            print("=" * 70)
        
        except KeyboardInterrupt:
            print("\n\n👋 Au revoir!")
            break
        except Exception as e:
            print(f"\n❌ Erreur: {e}")


async def run_single_task(description: str, agent_type: str = "researcher"):
    """Exécute une tâche unique."""
    orchestrator = SimpleOrchestrator()
    
    task = {
        "description": description,
        "agent_type": agent_type,
        "timestamp": datetime.now().isoformat()
    }
    
    result = await orchestrator.execute_task(task)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return result


def show_info():
    """Affiche les informations."""
    print("=" * 70)
    print("🪖 GoldArmyArgent - Version Démo")
    print("=" * 70)
    print("\nVersion: 1.0.0-demo")
    print("Mode: Standalone (sans dépendances)")
    print("\nAgents disponibles:")
    print("  - Researcher: Recherche et analyse")
    print("  - Coder: Génération de code")
    print("  - Planner: Planification de tâches")
    print("\nNote: Cette version est une DÉMO.")
    print("Pour la version complète avec Ollama, installez les dépendances.")
    print("=" * 70)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "info":
            show_info()
        
        elif command == "interactive":
            asyncio.run(interactive_mode())
        
        elif command == "run-task" and len(sys.argv) > 2:
            description = sys.argv[2]
            agent_type = sys.argv[3] if len(sys.argv) > 3 else "researcher"
            asyncio.run(run_single_task(description, agent_type))
        
        else:
            print("Commandes disponibles:")
            print("  python demo.py info")
            print("  python demo.py interactive")
            print("  python demo.py run-task \"Votre tâche\" [agent_type]")
    else:
        # Mode interactif par défaut
        asyncio.run(interactive_mode())
