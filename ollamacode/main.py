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
from rich.text import Text

from ollamacode.config import load_settings, save_settings
from ollamacode.utils import get_system_stats, list_ollama_models, list_groq_models, check_update
from ollamacode.ui import setup_wizard, show_status, show_stats
from ollamacode.terminal import execute_command
from ollamacode.agent import OllamaCodeAgent

console = Console()

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
            user_input = Prompt.ask("[magenta]OllamaCode[/magenta] [dim]>[/dim]")
            
            if user_input.lower() in ['q', 'exit', 'quit']:
                console.print("\n[dim]👋 Goodbye![/dim]\n")
                break
            if user_input.lower() == "clear":
                console.clear()
                show_status(settings, console)
                agent.history = []
                continue
            
            agent.history.append({"role": "user", "content": user_input})
            recent_actions = []
            cmd_fail_counts = {}
            MAX_CMD_RETRIES = 2
            total_steps = 0
            
            while True:
                with Progress(SpinnerColumn(style="cyan"), TextColumn(f"[dim]{settings['model']} thinking...[/dim]"), transient=True, console=console) as progress:
                    progress.add_task(""); answer = agent.ask_ai(cwd)
                
                console.print(f"\n[magenta]OllamaCode[/magenta]\n")
                console.print(Markdown(str(answer)))
                console.print("")
                agent.history.append({"role": "assistant", "content": str(answer)})
                
                cmds = agent.get_commands(answer)
                if not cmds: break
                
                any_executed = False
                for cmd in cmds:
                    cmd = cmd.strip()
                    if not cmd: continue

                    if cmd_fail_counts.get(cmd, 0) >= MAX_CMD_RETRIES:
                        console.print(f"  [red]⚠ Loop detected! Skipping iterative fix.[/red]")
                        break

                    console.print(f"  [magenta]●[/magenta] [bold]{cmd}[/bold]")
                    if settings["auto_run"] or Confirm.ask("[dim]  Execute?[/dim]"):
                        any_executed = True
                        status, stdout, new_cwd = execute_command(cmd, cwd=cwd)
                        cwd = new_cwd
                        
                        if stdout:
                            for line in stdout.splitlines():
                                console.print(f"    [dim]{line}[/dim]")

                        recent_actions.append((cmd, stdout))
                        agent.history.append({"role": "user", "content": f"Output (status {status}):\n{stdout}"})
                        if status != 0:
                            cmd_fail_counts[cmd] = cmd_fail_counts.get(cmd, 0) + 1
                            if settings["auto_fix"]:
                                console.print(f"  [red]✖ Failed (code {status}). Asking for fix...[/red]")
                                agent.history.append({"role": "user", "content": f"Previous command failed. Fix it."})
                                break
                    else: break
                if not any_executed: break
        except Exception:
            console.print("[bold red]Fatal Error:[/bold red]"); console.print(traceback.format_exc()); break

def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == "settings": run_agent(force_setup=True); return
        if sys.argv[1] == "--version" or sys.argv[1] == "-v":
            console.print("[bold magenta]OllamaCode 1.3[/bold magenta]"); return
    run_agent()

if __name__ == "__main__":
    main()
