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
            cmd_fail_counts = {}
            MAX_CMD_RETRIES = 2
            MAX_TOTAL_STEPS = 20
            total_steps = 0
            
            while True:
                if total_steps >= MAX_TOTAL_STEPS:
                    console.print("[bold red]Max steps reached. Stopping to prevent infinite loop.[/bold red]")
                    break

                with Progress(SpinnerColumn(), TextColumn(f"[cyan]{settings['model']} thinking...[/cyan]"), transient=True) as progress:
                    progress.add_task(""); answer = agent.ask_ai(cwd)
                
                console.print(Panel(Markdown(str(answer)), title="🤖 OllamaCode", border_style="cyan"))
                agent.history.append({"role": "assistant", "content": str(answer)})
                
                cmds = agent.get_commands(answer)
                if not cmds: break
                
                any_executed = False
                loop_detected = False
                for cmd in cmds:
                    cmd = cmd.strip()
                    if not cmd: continue

                    if cmd_fail_counts.get(cmd, 0) >= MAX_CMD_RETRIES:
                        console.print(f"[bold red]Loop detected: '{cmd}' has failed {MAX_CMD_RETRIES} times already. Stopping.[/bold red]")
                        loop_detected = True
                        break

                    console.print(Panel(f"Action: [bold yellow]{cmd}[/]\n[dim](Interactive session. You can type input or press Ctrl+C to stop)[/dim]", border_style="yellow"))
                    if settings["auto_run"] or Confirm.ask("Execute?"):
                        any_executed = True
                        total_steps += 1
                        status, stdout, new_cwd = execute_command(cmd, cwd=cwd)
                        cwd = new_cwd
                        recent_actions.append((cmd, stdout))
                        agent.history.append({"role": "user", "content": f"Output (status {status}):\n{stdout}"})
                        if status != 0:
                            cmd_fail_counts[cmd] = cmd_fail_counts.get(cmd, 0) + 1
                            if cmd_fail_counts[cmd] >= MAX_CMD_RETRIES:
                                console.print(f"[bold yellow]Warning: '{cmd}' has now failed {cmd_fail_counts[cmd]} times.[/bold yellow]")
                            if settings["auto_fix"]:
                                agent.history.append({"role": "user", "content": f"Previous command failed (attempt {cmd_fail_counts[cmd]}/{MAX_CMD_RETRIES}). Do NOT repeat it. Try a different approach or stop."})
                                break
                    else: break
                if not any_executed or loop_detected: break
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

def run_plugin(name, args):
    plugin_dir = os.path.join(os.path.expanduser("~"), ".ollamacode", "plugins")
    path = os.path.join(plugin_dir, name)
    if not os.path.exists(path):
        console.print(f"[red]Plugin {name} not found[/red]")
        sys.exit(1)
    
    if name.endswith(".py"):
        sys.exit(subprocess.run([sys.executable, path] + args).returncode)
    elif name.endswith(".js"):
        sys.exit(subprocess.run(["node", path] + args).returncode)
    else:
        sys.exit(subprocess.run([path] + args).returncode)

def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == "update": main_update(); return
        if sys.argv[1] == "settings": run_agent(force_setup=True); return
        if sys.argv[1] == "plugins": list_plugins(); return
        if sys.argv[1] == "add" and len(sys.argv) > 2 and sys.argv[2] == "plugin":
            if len(sys.argv) > 3: add_plugin(sys.argv[3])
            else: console.print("[red]Please specify plugin path[/red]")
            return
        if sys.argv[1] == "--version" or sys.argv[1] == "-v":
            console.print("[bold cyan]OllamaCode 1.2.0[/bold cyan]")
            return
        if sys.argv[1] == "run" and len(sys.argv) > 2:
            name = sys.argv[2]
            if not name.endswith(".py") and not name.endswith(".js"):
                # try finding it with .py first
                plugin_dir = os.path.join(os.path.expanduser("~"), ".ollamacode", "plugins")
                if os.path.exists(os.path.join(plugin_dir, name + ".py")): name += ".py"
                elif os.path.exists(os.path.join(plugin_dir, name + ".js")): name += ".js"
            run_plugin(name, sys.argv[3:])
            return
        if sys.argv[1] == "register":
            # llam register -n my_plugin -f test_plugin.py
            filename = None
            for i in range(len(sys.argv)):
                if sys.argv[i] == "-f" and i+1 < len(sys.argv): filename = sys.argv[i+1]
            if filename: add_plugin(filename)
            else: console.print("[red]Please specify plugin file with -f[/red]")
            return
        if sys.argv[1] == "tree":
            subprocess.run(["find", ".", "-maxdepth", "2", "-not", "-path", "*/.*"])
            return
        if sys.argv[1] == "cat-file" and len(sys.argv) > 2:
            try:
                with open(sys.argv[2], 'r') as f:
                    for i, line in enumerate(f, 1): console.print(f"[dim]{i:3}:[/dim] {line.strip()}")
            except Exception as e: console.print(f"[red]{e}[/red]")
            return
        if sys.argv[1] == "write-file" and len(sys.argv) > 2:
            content = sys.argv[3] if len(sys.argv) > 3 else sys.stdin.read()
            try:
                with open(sys.argv[2], 'w') as f: f.write(content)
                console.print(f"[green]Written to {sys.argv[2]}[/green]")
            except Exception as e: console.print(f"[red]{e}[/red]")
            return
    run_agent()

if __name__ == "__main__":
    main()
