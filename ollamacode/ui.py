import os
import time
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm

def setup_wizard(settings, console, list_ollama_fn, list_groq_fn):
    step = 1
    while step <= 5:
        console.clear()
        console.print(Panel("[bold cyan]OLLAMACODE[/]", border_style="cyan", expand=False))
        if step == 1:
            prov_table = Table(show_header=True, header_style="bold magenta")
            prov_table.add_column("Key"); prov_table.add_column("Provider")
            prov_table.add_row("1", "Groq"); prov_table.add_row("2", "Ollama")
            console.print(prov_table)
            p_choice = Prompt.ask("Choice", choices=["1", "2"])
            settings["provider"] = "Groq" if p_choice == "1" else "Ollama"; step = 2
        elif step == 2:
            if settings["provider"] == "Groq": settings["api_key"] = Prompt.ask("Groq Key", password=True, default=settings.get("api_key", "")); step = 4
            else: settings["ollama_url"] = Prompt.ask("Ollama URL", default=settings.get("ollama_url", "http://localhost:11434")); step = 3
        elif step == 3:
            models = list_ollama_fn(settings["ollama_url"])
            if not models: settings["model"] = Prompt.ask("Model Name", default=settings.get("model", "llama3")); step = 4
            else:
                mod_table = Table(show_header=True)
                mod_table.add_column("ID"); mod_table.add_column("Name")
                for i, m in enumerate(models): mod_table.add_row(str(i + 1), m['id'])
                console.print(mod_table)
                m_choice = Prompt.ask("Select Model", choices=[str(i+1) for i in range(len(models))] + ["back"])
                if m_choice == "back": step = 2; continue
                settings["model"] = models[int(m_choice)-1]['id']; step = 4
        elif step == 4:
            if settings["provider"] == "Groq":
                models = list_groq_fn(settings["api_key"])
                mod_table = Table(show_header=True)
                mod_table.add_column("ID"); mod_table.add_column("Name")
                for i, m in enumerate(models): mod_table.add_row(str(i + 1), m['id'])
                console.print(mod_table)
                m_choice = Prompt.ask("Select Model", choices=[str(i+1) for i in range(len(models))] + ["back"])
                if m_choice == "back": step = 2; continue
                settings["model"] = models[int(m_choice)-1]['id']
            step = 5
        elif step == 5:
            settings["auto_run"] = Confirm.ask("Auto-Run?", default=settings.get("auto_run", False))
            settings["auto_fix"] = Confirm.ask("Auto-Fix?", default=settings.get("auto_fix", False))
            step = 6
    console.clear(); console.print("[green]Saved![/]"); time.sleep(1); return settings

def show_status(settings, console):
    status_panel = Panel(
        f"Provider: [cyan]{settings['provider']}[/]\nModel:    [yellow]{settings['model']}[/]\nAuto-Run: [{'green' if settings['auto_run'] else 'red'}]{settings['auto_run']}[/]\nAuto-Fix: [{'green' if settings['auto_fix'] else 'red'}]{settings['auto_fix']}[/]\nOllama:   [blue]{settings['ollama_url']}[/]",
        title="[bold green]Settings[/]", border_style="green", expand=False
    )
    console.print(status_panel)

def show_stats(stats, cwd, console):
    cpu, ram, disk = stats
    line = f"[dim]Stats: CPU %{cpu} | RAM %{ram} | {cwd}[/dim]" if cpu is not None else f"[dim]{cwd}[/dim]"
    console.print(line)
