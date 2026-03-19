#!/usr/bin/env python3
import os
import sys
import psutil
import requests
import json
import time
import subprocess
import re
import platform
import pty
import traceback
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from rich.layout import Layout
from rich import print as rprint
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt, Confirm

load_dotenv()

CONFIG_FILE = os.path.join(os.path.expanduser("~"), ".ollamacode_settings.json")

class OllamaCodeAgent:
    def __init__(self):
        self.console = Console()
        self.provider = "Groq"
        self.api_key = os.getenv("GROQ_API_KEY", "")
        self.model = "llama-3.3-70b-versatile"
        self.auto_run = False
        self.auto_fix = False
        self.history = []
        self.ollama_url = "http://localhost:11434"
        self.groq_url = "https://api.groq.com/openai/v1/chat/completions"
        self.load_settings()
        self.cwd = os.getcwd()

    def load_settings(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    settings = json.load(f)
                    self.provider = settings.get("provider", self.provider)
                    self.api_key = settings.get("api_key", self.api_key)
                    self.model = settings.get("model", self.model)
                    self.auto_run = settings.get("auto_run", self.auto_run)
                    self.auto_fix = settings.get("auto_fix", self.auto_fix)
            except: pass

    def save_settings(self):
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump({
                    "provider": self.provider,
                    "api_key": self.api_key,
                    "model": self.model,
                    "auto_run": self.auto_run,
                    "auto_fix": self.auto_fix
                }, f)
        except: pass

    def get_system_stats(self):
        try:
            cpu = psutil.cpu_percent()
            ram = psutil.virtual_memory().percent
            disk = psutil.disk_usage('/').percent
            return cpu, ram, disk
        except:
            return None, None, None

    def get_system_context(self):
        os_info = f"{platform.system()} {platform.release()}"
        return f"Operating System: {os_info}\nCurrent Directory: {self.cwd}"

    def list_ollama_models(self):
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models_data = response.json().get('models', [])
                refined_models = []
                for m in models_data:
                    details = m.get('details', {})
                    refined_models.append({
                        "id": m['name'],
                        "family": details.get('family', 'N/A')
                    })
                return refined_models
        except: return []
        return []

    def list_groq_models(self):
        if not self.api_key: return [{"id": "llama-3.3-70b-versatile", "family": "Llama 3.3"}]
        try:
            url = "https://api.groq.com/openai/v1/models"
            response = requests.get(url, headers={"Authorization": f"Bearer {self.api_key}"}, timeout=5)
            if response.status_code == 200:
                data = response.json().get('data', [])
                refined_models = []
                for m in data:
                    model_id = m['id']
                    if any(x in model_id.lower() for x in ['llama', 'qwen', 'mixtral', 'gemma']):
                        family = "Llama" if "llama" in model_id.lower() else "Qwen" if "qwen" in model_id.lower() else "Mixtral" if "mixtral" in model_id.lower() else "Gemma" if "gemma" in model_id.lower() else "N/A"
                        refined_models.append({"id": model_id, "family": family})
                return refined_models
        except: pass
        return [{"id": "llama-3.3-70b-versatile", "family": "Llama 3.3"}]

    def setup(self, force=False):
        if not force and os.path.exists(CONFIG_FILE):
            status_panel = Panel(
                f"Provider: [cyan]{self.provider}[/]\nModel:    [yellow]{self.model}[/]\nAuto-Run: [{'green' if self.auto_run else 'red'}]{self.auto_run}[/]\nAuto-Fix: [{'green' if self.auto_fix else 'red'}]{self.auto_fix}[/]",
                title="[bold green]Settings[/]", border_style="green", expand=False
            )
            self.console.print(status_panel)
            return

        step = 1
        while step <= 4:
            self.console.clear()
            self.console.print(Panel("[bold cyan]OLLAMACODE[/]", border_style="cyan", expand=False))
            if step == 1:
                prov_table = Table(show_header=True, header_style="bold magenta")
                prov_table.add_column("Key"); prov_table.add_column("Provider")
                prov_table.add_row("1", "Groq"); prov_table.add_row("2", "Ollama")
                self.console.print(prov_table)
                p_choice = Prompt.ask("Choice", choices=["1", "2"])
                self.provider = "Groq" if p_choice == "1" else "Ollama"
                step = 2
            elif step == 2:
                if self.provider == "Groq":
                    self.api_key = Prompt.ask("Groq Key", password=True, default=self.api_key)
                step = 3
            elif step == 3:
                models = self.list_groq_models() if self.provider == "Groq" else self.list_ollama_models()
                if not models: self.model = Prompt.ask("Model Name", default=self.model); step = 4
                else:
                    mod_table = Table(show_header=True)
                    mod_table.add_column("ID"); mod_table.add_column("Name")
                    for i, m in enumerate(models): mod_table.add_row(str(i + 1), m['id'])
                    self.console.print(mod_table)
                    m_choice = Prompt.ask("Select", choices=[str(i+1) for i in range(len(models))] + ["back"])
                    if m_choice == "back": step = 2; continue
                    self.model = models[int(m_choice)-1]['id']
                    step = 4
            elif step == 4:
                self.auto_run = Confirm.ask("Auto-Run?", default=self.auto_run)
                self.auto_fix = Confirm.ask("Auto-Fix?", default=self.auto_fix)
                step = 5
        self.save_settings(); self.console.clear(); self.console.print("[green]Saved![/]"); time.sleep(1)

    def ask_ai(self):
        system_msg = (
            "You are 'OllamaCode', an autonomous terminal agent. "
            f"Context: {self.get_system_context()} "
            "Suggest bash commands in ```bash ... ``` blocks. "
            "IMPORTANT: If the output shows the task is complete, STOP suggesting commands."
        )
        messages = [{"role": "system", "content": system_msg}] + self.history[-15:]
        try:
            if self.provider == "Groq":
                headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
                response = requests.post(self.groq_url, headers=headers, json={"messages": messages, "model": self.model}, timeout=30)
                if response.status_code == 200: return response.json()['choices'][0]['message']['content']
            else:
                response = requests.post(f"{self.ollama_url}/api/chat", json={"model": self.model, "messages": messages, "stream": False}, timeout=150)
                if response.status_code == 200: return response.json()['message']['content']
            return "Connection error or model refused."
        except Exception as e: return f"Error: {str(e)}"

    def execute_command(self, cmd):
        output_buffer = []
        try:
            if cmd.strip().startswith("cd "):
                new_dir = cmd.strip().split("cd ")[1].strip()
                os.chdir(os.path.expanduser(new_dir)); self.cwd = os.getcwd()
                return 0, f"Changed to {self.cwd}"

            def master_read(master_fd):
                try:
                    data = os.read(master_fd, 1024)
                    if data:
                        decoded = data.decode(errors='ignore')
                        output_buffer.append(decoded); sys.stdout.write(decoded); sys.stdout.flush()
                    return data
                except OSError: return b''

            exit_status = pty.spawn(["/bin/bash", "-c", cmd], master_read)
            return exit_status, "".join(output_buffer)
        except Exception as e: return 1, str(e)

    def run(self, force_setup=False):
        try:
            self.setup(force=force_setup)
            while True:
                cpu, ram, disk = self.get_system_stats()
                stats_line = f"[dim]Stats: CPU %{cpu} | RAM %{ram} | {self.cwd}[/dim]" if cpu is not None else f"[dim]{self.cwd}[/dim]"
                rprint(stats_line)
                user_input = Prompt.ask("[bold green]OllamaCode >[/bold green]")
                if user_input.lower() in ['q', 'exit', 'quit']: break
                if user_input.lower() in ["update", "/update"]:
                    repo_path = os.path.dirname(os.path.abspath(__file__))
                    subprocess.run(["git", "pull"], cwd=repo_path); subprocess.run([sys.executable, "-m", "pip", "install", "-e", "."], cwd=repo_path)
                    sys.exit(0)
                if user_input.lower() == "clear": self.console.clear(); self.history = []; continue
                self.history.append({"role": "user", "content": user_input})
                
                recent_actions = []
                while True:
                    with Progress(SpinnerColumn(), TextColumn(f"[cyan]{self.model}...[/cyan]"), transient=True) as progress:
                        progress.add_task("", total=None)
                        answer = self.ask_ai()
                    self.console.print(Panel(Markdown(str(answer)), title="🤖 OllamaCode", border_style="cyan"))
                    self.history.append({"role": "assistant", "content": str(answer)})
                    
                    commands = re.findall(r'```(?:bash|sh|shell)\n(.*?)```', str(answer), re.DOTALL | re.IGNORECASE)
                    if not commands: break
                    
                    any_executed = False
                    for cmd in commands:
                        cmd = cmd.strip()
                        if not cmd: continue
                        
                        self.console.print(Panel(f"Action:\n{cmd}", border_style="yellow"))
                        if self.auto_run or Confirm.ask("Execute?"):
                            any_executed = True
                            status, stdout = self.execute_command(cmd)
                            
                            current_action = (cmd, stdout)
                            if current_action in recent_actions:
                                self.console.print("[bold red]Loop detected![/bold red] Same command gave same output. Stopping.")
                                break
                            recent_actions.append(current_action)
                            
                            self.history.append({"role": "user", "content": f"Output (status {status}):\n{stdout}"})
                            if status != 0 and self.auto_fix:
                                self.console.print("[red]Failure! Auto-Fixing...[/red]")
                                self.history.append({"role": "user", "content": "Previous command failed. Fix it."})
                                break
                        else: break
                    if not any_executed: break
                    if (cmd, stdout) in recent_actions[:-1]: break
        except Exception:
            self.console.print("[bold red]Fatal Error:[/bold red]")
            self.console.print(traceback.format_exc())

def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == "update":
            repo_path = os.path.dirname(os.path.abspath(__file__))
            subprocess.run(["git", "pull"], cwd=repo_path); subprocess.run([sys.executable, "-m", "pip", "install", "-e", "."], cwd=repo_path)
            return
        if sys.argv[1] == "settings":
            OllamaCodeAgent().run(force_setup=True)
            return
    OllamaCodeAgent().run(force_setup=False)

if __name__ == "__main__":
    main()
