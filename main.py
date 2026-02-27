"""Point d'entrée principal pour GoldArmyArgent."""
import asyncio
import sys
from pathlib import Path

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent))

from loguru import logger
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

from core.orchestrator import orchestrator
from config.settings import settings

# Configuration de loguru
logger.remove()
logger.add(
    sys.stderr,
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    level=settings.log_level
)
logger.add(
    settings.log_file,
    rotation="10 MB",
    retention="1 week",
    level="DEBUG"
)

app = typer.Typer(help="🪖 GoldArmyArgent - Armée d'agents IA autonomes")
console = Console()


@app.command()
def info():
    """Affiche les informations sur le système."""
    console.print(Panel.fit(
        "[bold cyan]🪖 GoldArmyArgent[/bold cyan]\n"
        "[yellow]Armée d'Agents IA Autonomes[/yellow]\n\n"
        f"Version: [green]1.0.0[/green]\n"
        f"Ollama: [green]{settings.ollama_host}[/green]\n"
        f"Modèle par défaut: [green]{settings.ollama_default_model}[/green]\n"
        f"Max agents: [green]{settings.max_agents}[/green]",
        title="Informations Système"
    ))


@app.command()
def test_ollama():
    """Test la connexion à Ollama."""
    console.print("[yellow]Test de la connexion à Ollama...[/yellow]")
    
    async def _test():
        from llm.ollama_client import OllamaClient
        
        async with OllamaClient() as client:
            if not await client.is_available():
                console.print("[red]❌ Ollama n'est pas disponible![/red]")
                console.print(f"[yellow]Vérifiez que Ollama tourne sur {settings.ollama_host}[/yellow]")
                return False
            
            console.print("[green]✅ Ollama est disponible![/green]")
            
            # Lister les modèles
            models = await client.list_models()
            
            if models:
                table = Table(title="Modèles disponibles")
                table.add_column("Nom", style="cyan")
                table.add_column("Taille", style="green")
                
                for model in models:
                    name = model.get("name", "Unknown")
                    size = model.get("size", 0)
                    size_mb = size / (1024 * 1024)
                    table.add_row(name, f"{size_mb:.1f} MB")
                
                console.print(table)
            else:
                console.print("[yellow]Aucun modèle trouvé. Téléchargez un modèle avec:[/yellow]")
                console.print("[cyan]ollama pull llama2[/cyan]")
            
            return True
    
    asyncio.run(_test())


@app.command()
def create_agent(
    agent_type: str = typer.Argument(..., help="Type d'agent (researcher, coder, planner)"),
):
    """Crée un nouvel agent."""
    console.print(f"[yellow]Création d'un agent {agent_type}...[/yellow]")
    
    async def _create():
        await orchestrator.start()
        agent = await orchestrator.create_agent(agent_type)
        
        console.print(f"[green]✅ Agent créé: {agent.name} (ID: {agent.agent_id})[/green]")
        
        await orchestrator.stop()
    
    asyncio.run(_create())


@app.command()
def run_task(
    description: str = typer.Argument(..., help="Description de la tâche"),
    agent_type: str = typer.Option("researcher", help="Type d'agent à utiliser"),
):
    """Exécute une tâche simple."""
    console.print(f"[yellow]Exécution de la tâche avec un agent {agent_type}...[/yellow]")
    
    async def _run():
        await orchestrator.start()
        
        task = {
            "description": description,
            "agent_type": agent_type,
            "context": "Tâche lancée depuis la CLI"
        }
        
        result = await orchestrator.execute_task(task)
        
        console.print(Panel.fit(
            f"[bold]Résultat:[/bold]\n\n{result}",
            title=f"Tâche terminée ({'✅' if result.get('success') else '❌'})"
        ))
        
        await orchestrator.stop()
    
    asyncio.run(_run())


@app.command()
def stats():
    """Affiche les statistiques du système."""
    async def _stats():
        await orchestrator.start()
        
        stats_data = orchestrator.get_stats()
        
        # Table des agents
        table = Table(title="État des Agents")
        table.add_column("ID", style="cyan")
        table.add_column("Nom", style="green")
        table.add_column("Type", style="yellow")
        table.add_column("Statut", style="magenta")
        table.add_column("Tâches", style="blue")
        
        for agent_id, agent_info in stats_data.get("agents", {}).items():
            table.add_row(
                agent_id[:8],
                agent_info["name"],
                agent_info["type"],
                agent_info["status"],
                str(agent_info["stats"]["tasks_completed"])
            )
        
        console.print(table)
        
        # Statistiques globales
        console.print(f"\n[bold]Total agents:[/bold] {stats_data['total_agents']}")
        console.print(f"[bold]File de tâches:[/bold] {stats_data['queue_size']}")
        console.print(f"[bold]Mémoires stockées:[/bold] {stats_data['memory_stats']['ram_memories']}")
        
        await orchestrator.stop()
    
    asyncio.run(_stats())


@app.command()
def interactive():
    """Mode interactif pour soumettre des tâches."""
    console.print(Panel.fit(
        "[bold cyan]🪖 Mode Interactif GoldArmyArgent[/bold cyan]\n\n"
        "Tapez vos tâches et l'armée d'agents les exécutera!\n"
        "Tapez 'quit' pour quitter.",
        title="Mode Interactif"
    ))
    
    async def _interactive():
        await orchestrator.start()
        
        while True:
            try:
                task_desc = console.input("\n[bold cyan]Tâche >[/bold cyan] ")
                
                if task_desc.lower() in ["quit", "exit", "q"]:
                    break
                
                if not task_desc.strip():
                    continue
                
                # Déterminer le type d'agent automatiquement
                agent_type = "researcher"  # Par défaut
                if any(word in task_desc.lower() for word in ["code", "programme", "fonction", "debug"]):
                    agent_type = "coder"
                elif any(word in task_desc.lower() for word in ["plan", "organise", "décompose"]):
                    agent_type = "planner"
                elif any(word in task_desc.lower() for word in ["emploi", "job", "stage", "travail", "recrutement", "carrière", "poste", "work", "offre", "trouve", "cherche"]):
                    agent_type = "job_searcher"
                elif any(word in task_desc.lower() for word in ["linkedin", "profil", "recruteur", "décideur", "headhunter"]):
                    agent_type = "headhunter"
                
                console.print(f"[yellow]→ Utilisation d'un agent {agent_type}...[/yellow]")
                
                task = {
                    "description": task_desc,
                    "agent_type": agent_type,
                }
                
                result = await orchestrator.execute_task(task)
                
                # Affichage spécial pour les résultats de recherche d'emploi
                if result.get("success") and "matched_jobs" in result:
                    jobs = result["matched_jobs"]
                    console.print(f"\n[bold green]✅ {len(jobs)} Offres trouvées et analysées[/bold green]\n")
                    
                    for i, job in enumerate(jobs):
                        # Créer un panneau pour chaque offre
                        job_panel_content = f"[bold size=14]{job.get('title', 'Titre inconnu')}[/bold size]\n"
                        job_panel_content += f"[cyan]🏢 {job.get('company', 'Entreprise inconnue')}   📍 {job.get('location', 'Lieu inconnu')}[/cyan]\n\n"
                        job_panel_content += f"[bold]🎯 Score:[/bold] {job.get('match_score', 0)}%\n"
                        job_panel_content += f"[italic]{job.get('match_justification', '')}[/italic]\n\n"
                        job_panel_content += f"[bold]🛠️ Compétences:[/bold] {', '.join(job.get('required_skills', []))}\n"
                        job_panel_content += f"[blue underline link={job.get('url')}]🔗 Voir l'offre[/blue underline link]"
                        
                        console.print(Panel(
                            job_panel_content,
                            title=f"Offre #{i+1}",
                            border_style="green" if job.get('match_score', 0) >= 60 else "yellow",
                            box=box.ROUNDED
                        ))
                    
                    # --- NOUVEAU: Feature "Apply" ---
                    console.print("\n[bold]🚀 Veux-tu postuler à une offre ?[/bold]")
                    choice = await asyncio.to_thread(console.input, "[cyan]Entre le numéro de l'offre (ou 'non') > [/cyan]")
                    
                    if choice.isdigit():
                        idx = int(choice) - 1
                        if 0 <= idx < len(jobs):
                            target_job = jobs[idx]
                            console.print(f"\n[green]✅ Préparation de la candidature pour {target_job.get('company')}...[/green]")
                            
                            # Récupérer l'agent
                            job_agent = next((a for a in orchestrator.agents.values() if a.agent_type == "job_searcher"), None)
                            
                            if job_agent:
                                # 1. Générer la lettre
                                with console.status("[bold green]✍️ Rédaction de la lettre de motivation (IA)...[/bold green]"):
                                    letter = await job_agent.generate_cover_letter(target_job, result.get("cv_profile", {}))
                                
                                # 2. Sauvegarder
                                safe_company = "".join(x for x in target_job.get('company', 'Entreprise') if x.isalnum())
                                filename = f"lettre_{safe_company}.md"
                                with open(filename, "w", encoding="utf-8") as f:
                                    f.write(letter)
                                
                                console.print(f"[bold]📄 Lettre sauvegardée: {filename}[/bold]")
                                
                                # 3. Ouvrir l'URL
                                import webbrowser
                                if target_job.get('url'):
                                    console.print(f"[yellow]🌐 Ouverture de la page de candidature...[/yellow]")
                                    webbrowser.open(target_job['url'])
                                else:
                                    console.print("[red]Pas d'URL disponible pour cette offre.[/red]")
                                    
                                console.print("\n[bold green]✨ Bonne chance ![/bold green]")
                            else:
                                console.print("[red]Erreur: Agent JobSearcher introuvable.[/red]")
                        else:
                            console.print("[red]Numéro invalide.[/red]")
                else:
                    # Affichage générique pour les autres tâches
                    console.print(Panel.fit(
                        str(result),
                        title=f"Résultat ({'✅' if result.get('success') else '❌'})",
                        border_style="green" if result.get('success') else "red"
                    ))
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                console.print(f"[red]Erreur: {e}[/red]")
        
        await orchestrator.stop()
        console.print("\n[yellow]Au revoir! 👋[/yellow]")
    
    asyncio.run(_interactive())


if __name__ == "__main__":
    app()
