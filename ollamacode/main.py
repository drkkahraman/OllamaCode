#!/usr/bin/env python3
import os
import sys
import subprocess
import traceback
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, TextColumn

from ollamacode.config import load_settings, save_settings
from ollamacode.utils import get_system_stats, list_ollama_models, list_groq_models, check_update
from ollamacode.ui import setup_wizard, show_status, show_stats
from ollamacode.terminal import execute_command
from ollamacode.agent import OllamaCodeAgent

console = Console()

def main_update():
    repo_path = os.path.dirname(os.path.abspath(__file__))
    local, remote, err = check_update(repo_path)
    if err: console.print(f"[red]{err}[/red]"); return
    if local == remote: console.print("[green]OllamaCode is already up to date.[/green]"); return
    console.print("[yellow]Updating...[/yellow]")
    subprocess.run(["git", "pull"], cwd=repo_path)
    subprocess.run([sys.executable, "-m", "pip", "install", "-e", "."], cwd=repo_path)

def run_agent(force_setup=False):
    settings = load_settings()
    if force_setup or not os.path.exists(os.path.join(os.path.expanduser("~"), ".ollamacode_settings.json")):
        settings = setup_wizard(settings, console, list_ollama_models, list_groq_models)
        save_settings(settings)
    
    show_status(settings, console)
    agent = OllamaCodeAgent(settings)
    cwd = os.getcwd()

    while True:
        try:
            show_stats(get_system_stats(), cwd, console)
            user_input = Prompt.ask("[bold green]OllamaCode >[/bold green]")
            if user_input.lower() in ['q', 'exit', 'quit']: break
            if user_input.lower() == "clear": console.clear(); agent.history = []; continue
            
            agent.history.append({"role": "user", "content": user_input})
            recent_actions = []
            
            while True:
                with Progress(SpinnerColumn(), TextColumn(f"[cyan]{settings['model']} thinking...[/cyan]"), transient=True) as progress:
                    progress.add_task(""); answer = agent.ask_ai(cwd)
                
                console.print(Panel(Markdown(str(answer)), title="🤖 OllamaCode", border_style="cyan"))
                agent.history.append({"role": "assistant", "content": str(answer)})
                
                cmds = agent.get_commands(answer)
                if not cmds: break
                
                any_executed = False
                for cmd in cmds:
                    cmd = cmd.strip()
                    if not cmd: continue
                    console.print(Panel(f"Action:\n{cmd}", border_style="yellow"))
                    if settings["auto_run"] or Confirm.ask("Execute?"):
                        any_executed = True
                        status, stdout, new_cwd = execute_command(cmd, cwd=cwd)
                        cwd = new_cwd
                        if (cmd, stdout) in recent_actions: console.print("[red]Loop detected![/red]"); break
                        recent_actions.append((cmd, stdout))
                        agent.history.append({"role": "user", "content": f"Output (status {status}):\n{stdout}"})
                        if status != 0 and settings["auto_fix"]:
                            agent.history.append({"role": "user", "content": "Previous command failed. Fix it."}); break
                    else: break
                if not any_executed: break
        except Exception:
            console.print("[bold red]Fatal Error:[/bold red]"); console.print(traceback.format_exc()); break

def list_plugins():
    plugin_dir = os.path.join(os.path.expanduser("~"), ".ollamacode", "plugins")
    if not os.path.exists(plugin_dir):
        os.makedirs(plugin_dir, exist_ok=True)
    plugins = [f for f in os.listdir(plugin_dir) if f.endswith('.py')]
    console.print(Panel("\n".join(plugins) if plugins else "No plugins found", title="Plugins", border_style="blue"))

def add_plugin(path):
    plugin_dir = os.path.join(os.path.expanduser("~"), ".ollamacode", "plugins")
    if not os.path.exists(plugin_dir):
        os.makedirs(plugin_dir, exist_ok=True)
    if not os.path.exists(path):
        console.print(f"[red]File {path} not found[/red]")
        return
    import shutil
    shutil.copy(path, os.path.join(plugin_dir, os.path.basename(path)))
    console.print(f"[green]Added plugin: {os.path.basename(path)}[/green]")

def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == "update": main_update(); return
        if sys.argv[1] == "settings": run_agent(force_setup=True); return
        if sys.argv[1] == "plugins": list_plugins(); return
        if sys.argv[1] == "add" and len(sys.argv) > 2 and sys.argv[2] == "plugin":
            if len(sys.argv) > 3: add_plugin(sys.argv[3])
            else: console.print("[red]Please specify plugin path[/red]")
            return
    run_agent()

if __name__ == "__main__":
    main()
