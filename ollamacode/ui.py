import os
import time
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.text import Text

def setup_wizard(settings, console, list_ollama_fn, list_groq_fn):
    console.clear()
    console.print(f"\n[magenta]OllamaCode Setup Wizard[/magenta]\n")
    
    prov_table = Table(box=None, padding=(0, 2))
    prov_table.add_column("Key", style="dim"); prov_table.add_column("Provider", style="magenta")
    prov_table.add_row("1", "Groq [dim](Fast Cloud)[/]")
    prov_table.add_row("2", "Ollama [dim](Local)[/]")
    console.print(prov_table)
    
    p_choice = Prompt.ask("Select Provider", choices=["1", "2"])
    settings["provider"] = "Groq" if p_choice == "1" else "Ollama"
    
    if settings["provider"] == "Groq":
        settings["api_key"] = Prompt.ask("Enter Groq API Key", password=True, default=settings.get("api_key", ""))
        models = list_groq_fn(settings["api_key"])
    else:
        settings["ollama_url"] = Prompt.ask("Enter Ollama URL", default=settings.get("ollama_url", "http://localhost:11434"))
        models = list_ollama_fn(settings["ollama_url"])
    
    if models:
        mod_table = Table(box=None, padding=(0, 2))
        mod_table.add_column("ID", style="dim"); mod_table.add_column("Name", style="green")
        for i, m in enumerate(models[:10]): mod_table.add_row(str(i + 1), m['id'])
        console.print(mod_table)
        m_choice = Prompt.ask("Select Model", choices=[str(i+1) for i in range(len(models[:10]))])
        settings["model"] = models[int(m_choice)-1]['id']
    else:
        settings["model"] = Prompt.ask("Enter Model Name", default="llama3")

    settings["auto_run"] = Confirm.ask("Enable Auto-Run?", default=False)
    settings["auto_fix"] = Confirm.ask("Enable Auto-Fix?", default=True)
    
    console.print("\n[green]✔ Configuration Saved![/]\n")
    time.sleep(1)
    return settings

def show_status(settings, console):
    p = "[bold magenta]OllamaCode v1.2.2[/bold magenta]"
    model = f"[yellow]{settings['model']}[/yellow]"
    provider = f"[dim]via {settings['provider']}[/dim]"
    flags = (
        f"[{'green' if settings['auto_run'] else 'dim'}]● Auto-Run[/] "
        f"[{'green' if settings['auto_fix'] else 'dim'}]● Auto-Fix[/]"
    )
    console.print(f"\n{p} [dim]—[/] {model} {provider}\n{flags}\n")

def show_stats(stats, cwd, console):
    cpu, ram, disk = stats
    cwd_short = cwd.replace(os.path.expanduser("~"), "~")
    
    cpu_style = "red" if cpu and cpu > 50 else "green"
    ram_style = "red" if ram and ram > 70 else "blue"
    
    if cpu is not None:
        stats_line = Text.assemble(
            (f"📁 ", "dim"), (f"{cwd_short} ", "magenta"),
            (f"| ", "dim"), (f"CPU: ", "dim"), (f"{cpu}% ", cpu_style),
            (f"RAM: ", "dim"), (f"{ram}%", ram_style)
        )
    else:
        stats_line = Text(f"📁 {cwd_short}", style="magenta")
    
    # Use end="" and flush to keep it on one line for a dynamic feel
    console.print(stats_line)
