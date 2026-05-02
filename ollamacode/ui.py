import os
import time
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.text import Text
from rich.align import Align
from rich.columns import Columns

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
    console.clear()
    
    # Large Logo ASCII Art
    logo = """
 [bold white]
  ▄▀▀▀▀▄  █       █       ▄▀▀▀▀▄  █▀▄▀█  ▄▀▀▀▀▄  ▄▀▀▀▀▄  ▄▀▀▀▀▄  █▀▀▄  █▀▀▀ 
  █    █  █       █       █▄▄▄▄█  █ █ █  █▄▄▄▄█  █       █    █  █  █  █▀▀▀ 
  ▀▄▄▄▄▀  ▀▀▀▀▀▀  ▀▀▀▀▀▀  ▀    ▀  ▀   ▀  ▀    ▀  ▀▄▄▄▄▀  ▀▄▄▄▄▀  ▀▀▀   ▀▀▀▀ 
 [/bold white]
    """
    console.print(Align.center(logo))

    # Main Info Panel (Simulating the search bar)
    info_text = Text()
    info_text.append("\n  Ask anything... ", style="dim")
    info_text.append('"Fix a TODO in the codebase"', style="italic dim")
    info_text.append("\n\n  ")
    info_text.append("Build", style="bold blue")
    info_text.append(" · ", style="dim")
    info_text.append(f"{settings['model']} ", style="bold white")
    info_text.append(f"[{settings['provider']}] ", style="cyan")
    info_text.append(f"{settings['provider']} (local)" if settings['provider'] == 'Ollama' else "Cloud API", style="dim")
    info_text.append("\n")

    # Simulated left border with a Panel
    panel = Panel(
        info_text,
        border_style="bright_blue",
        box=None, # We'll use a custom padding to simulate the side bar
        padding=(0, 0, 0, 2)
    )
    
    # To get the vertical line on the left, we can use a Table with one column and left border
    info_table = Table(box=None, show_header=False, padding=(0, 1))
    info_table.add_column(style="bright_blue")
    
    # Create the left-bordered effect
    container = Table.grid(padding=(0, 4))
    container.add_column()
    
    content_table = Table(box=None, show_header=False, padding=(0, 0))
    content_table.add_column(style="bright_blue") # Border column
    content_table.add_column() # Content column
    
    # Add a "vertical line" using a string of blocks
    v_line = Text("┃\n┃\n┃\n┃\n┃", style="bold bright_blue")
    content_table.add_row(v_line, info_text)
    
    console.print(Align.center(content_table))
    
    # Shortcuts
    shortcuts = Text.assemble(
        ("tab ", "bold white"), ("agents  ", "dim"),
        ("ctrl+p ", "bold white"), ("commands", "dim")
    )
    console.print(Align.right(shortcuts, pad=True))
    console.print("\n")

    # Bottom status bar
    tip = Text.assemble(
        (" ● ", "orange1"), ("Tip ", "bold white"), 
        ("Use ", "dim"), ("$ARGUMENTS, $1, $2 ", "bold white"), ("in custom commands for dynamic input", "dim")
    )
    version = Text(f"1.3", style="dim")
    
    footer = Table.grid(expand=True)
    footer.add_column(ratio=1)
    footer.add_column(justify="right")
    footer.add_row(tip, version)
    
    console.print(footer)
    console.print("\n")

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
    
    console.print(stats_line)

