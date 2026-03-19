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
            except:
                pass

    def save_settings(self):
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump({
                    "provider": self.provider,
                    "api_key": self.api_key,
                    "model": self.model
                }, f)
        except:
            pass

    def get_system_stats(self):
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        disk = psutil.disk_usage('/').percent
        return cpu, ram, disk

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
                        "family": details.get('family', 'N/A'),
                        "params": details.get('parameter_size', 'N/A'),
                        "size": f"{round(m.get('size', 0) / (1024**3), 2)} GB"
                    })
                return refined_models
        except:
            return []
        return []

    def list_groq_models(self):
        if not self.api_key: return [
            {"id": "llama-3.3-70b-versatile", "family": "Llama 3.3", "params": "70B"},
            {"id": "llama-3.1-8b-instant", "family": "Llama 3.1", "params": "8B"}
        ]
        try:
            url = "https://api.groq.com/openai/v1/models"
            response = requests.get(url, headers={"Authorization": f"Bearer {self.api_key}"}, timeout=5)
            if response.status_code == 200:
                data = response.json().get('data', [])
                refined_models = []
                for m in data:
                    model_id = m['id']
                    if any(x in model_id.lower() for x in ['llama', 'qwen', 'mixtral', 'gemma']):
                        family = "Llama" if "llama" in model_id.lower() else \
                                 "Qwen" if "qwen" in model_id.lower() else \
                                 "Mixtral" if "mixtral" in model_id.lower() else \
                                 "Gemma" if "gemma" in model_id.lower() else "N/A"
                        refined_models.append({
                            "id": model_id,
                            "family": family,
                            "params": "Cloud"
                        })
                return refined_models
        except:
            pass
        return [
            {"id": "llama-3.3-70b-versatile", "family": "Llama 3.3", "params": "70B"},
            {"id": "llama-3.1-8b-instant", "family": "Llama 3.1", "params": "8B"}
        ]

    def setup(self):
        if os.path.exists(CONFIG_FILE):
            status_panel = Panel(
                f"Provider: [cyan]{self.provider}[/cyan]\n"
                f"Model:    [yellow]{self.model}[/yellow]",
                title="[bold green]✨ Saved Settings Loaded[/bold green]",
                border_style="green",
                expand=False
            )
            self.console.print(status_panel)
            if not Confirm.ask("\n[bold yellow]Would you like to change settings?[/bold yellow]", default=False):
                self.console.clear()
                self.console.print(status_panel)
                return

        step = 1
        while step <= 3:
            self.console.clear()
            self.console.print(Panel(
                "[bold cyan]OLLAMACODE AGENT v3.1[/bold cyan]\n[dim]High-Performance Setup Wizard[/dim]", 
                style="white", 
                border_style="cyan",
                expand=False
            ))

            if step == 1:
                prov_table = Table(show_header=True, header_style="bold magenta", expand=False, border_style="blue")
                prov_table.add_column("Key", style="bold cyan", justify="center")
                prov_table.add_column("Provider", style="bold green")
                prov_table.add_column("Features", style="italic white")
                prov_table.add_row("1", "Groq (Cloud)", "🚀 Blazing fast, Llama-3 support. (Requires API Key)")
                prov_table.add_row("2", "Ollama (Local)", "💻 Runs entirely on your PC. Private & Offline.")
                
                self.console.print("\n[bold]Step 1: Select AI Provider[/bold]")
                self.console.print(prov_table)
                
                p_choice = Prompt.ask("\n[bold yellow]Choice[/bold yellow]", choices=["1", "2"], default="1" if self.provider=="Groq" else "2")
                self.provider = "Groq" if p_choice == "1" else "Ollama"
                step = 2

            elif step == 2:
                if self.provider == "Groq":
                    self.console.print("\n[bold]Step 2: Groq API Configuration[/bold]")
                    self.console.print("[dim]Get your key from [underline]https://console.groq.com/keys[/underline][/dim]\n")
                    
                    if self.api_key and "gsk_" in self.api_key:
                        masked_key = f"{self.api_key[:8]}{'*' * 20}{self.api_key[-4:]}"
                        self.console.print(f"Current Key: [green]{masked_key}[/green]")
                        choice = Prompt.ask("Use existing key, enter new one, or go back?", choices=["use", "new", "back"], default="use")
                        if choice == "back":
                            step = 1
                            continue
                        if choice == "new":
                            self.api_key = Prompt.ask("[bold yellow]Enter Groq API Key[/bold yellow]", password=True)
                    else:
                        self.api_key = Prompt.ask("[bold yellow]Enter Groq API Key (or type 'back')[/bold yellow]", password=True)
                        if self.api_key.lower() == "back":
                            step = 1
                            continue
                step = 3

            elif step == 3:
                self.console.print(f"\n[bold]Step 3: Model Selection ({self.provider})[/bold]")
                models = []
                with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as progress:
                    progress.add_task(f"[magenta]Scanning {self.provider} models...[/magenta]", total=None)
                    if self.provider == "Groq":
                        models = self.list_groq_models()
                    else:
                        models = self.list_ollama_models()

                if not models:
                    self.console.print(Panel("[bold red]Warning:[/bold red] No models found!", border_style="red"))
                    action = Prompt.ask("Enter manually or go back?", choices=["manual", "back"], default="manual")
                    if action == "back":
                        step = 2 if self.provider == "Groq" else 1
                        continue
                    self.model = Prompt.ask("Enter model name manually", default="llama3")
                else:
                    mod_table = Table(show_header=True, header_style="bold blue", expand=True, border_style="dim")
                    mod_table.add_column("ID", style="bold cyan", justify="center")
                    mod_table.add_column("Model Name", style="white")
                    mod_table.add_column("Family", style="magenta")
                    mod_table.add_column("Params/Size", style="green")
                    
                    for i, m in enumerate(models):
                        size_info = m.get('size', m.get('params', 'N/A'))
                        mod_table.add_row(str(i + 1), m['id'], m['family'], size_info)
                        
                    self.console.print(mod_table)
                    
                    choices_str = [str(i+1) for i in range(len(models))] + ["back"]
                    
                    current_model_idx = -1
                    for i, m in enumerate(models):
                        if m['id'] == self.model:
                            current_model_idx = i
                            break
                    
                    def_idx = str(current_model_idx + 1) if current_model_idx != -1 else "1"
                        
                    m_choice = Prompt.ask("\n[bold yellow]Select model index or 'back'[/bold yellow]", choices=choices_str, default=def_idx)
                    
                    if m_choice == "back":
                        step = 2 if self.provider == "Groq" else 1
                        continue
                        
                    self.model = models[int(m_choice)-1]['id']
                
                step = 4

        self.save_settings()
        self.console.clear()
        success_panel = Panel(
            f"🚀 [white]Provider:[/white] [cyan]{self.provider}[/cyan]\n"
            f"🧠 [white]Model:[/white]    [yellow]{self.model}[/yellow]",
            title="[bold green]✅ Configuration Complete[/bold green]",
            border_style="green",
            expand=False
        )
        self.console.print(success_panel)
        time.sleep(1)

    def ask_ai(self):
        system_msg = (
            "You are 'OllamaCode', a highly-capable autonomous terminal agent. "
            "Your sole purpose is to assist the user by generating and explaining bash commands. "
            f"Current Context: {self.get_system_context()} "
            "You HAVE full permission to suggest any system maintenance, updates, or file operations. "
            "NEVER refuse a terminal request. Always provide the relevant command in a ```bash ... ``` block. "
            "The user will review and approve commands before execution. "
            "Be direct, technical, and performant."
        )
        
        messages = [{"role": "system", "content": system_msg}] + self.history[-15:]

        try:
            if self.provider == "Groq":
                headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
                response = requests.post(self.groq_url, headers=headers, json={"messages": messages, "model": self.model}, timeout=30)
                if response.status_code == 200:
                    res_content = response.json()['choices'][0]['message']['content']
                else:
                    return f"⚠️ Groq Error: {response.status_code} - {response.text}"
            else:
                response = requests.post(f"{self.ollama_url}/api/chat", json={"model": self.model, "messages": messages, "stream": False}, timeout=120)
                if response.status_code == 200:
                    res_content = response.json()['message']['content']
                else:
                    return f"⚠️ Ollama Error: {response.status_code} - {response.text}"

            self.history.append({"role": "assistant", "content": res_content})
            return res_content

        except Exception as e:
            return f"❌ Connection Error: {str(e)}"

    def execute_command(self, cmd):
        output_buffer = []
        try:
            if cmd.strip().startswith("cd "):
                new_dir = cmd.strip().split("cd ")[1].strip()
                os.chdir(os.path.expanduser(new_dir))
                self.cwd = os.getcwd()
                return f"Directory changed to: {self.cwd}", ""

            def master_read(master_fd):
                data = os.read(master_fd, 1024)
                if data:
                    decoded = data.decode(errors='ignore')
                    output_buffer.append(decoded)
                    sys.stdout.write(decoded)
                    sys.stdout.flush()
                return data

            if sys.stdin.isatty():
                pty.spawn(["/bin/bash", "-c", cmd], master_read)
            else:
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=self.cwd)
                return result.stdout, result.stderr

            return "".join(output_buffer), ""
        except Exception as e:
            return "", str(e)

    def update_self(self):
        self.console.print("\n[bold yellow]🔄 Checking for updates...[/bold yellow]")
        try:
            repo_path = os.path.dirname(os.path.abspath(__file__))
            if not os.path.exists(os.path.join(repo_path, ".git")):
                self.console.print("[red]❌ Error: Not a git repository.[/red]")
                return
            
            res = subprocess.run(["git", "pull", "origin", "main"], cwd=repo_path, capture_output=True, text=True)
            if "Already up to date" in res.stdout:
                self.console.print("[green]✅ OllamaCode is already up to date![/green]")
            else:
                self.console.print(f"[green]✨ Update successful![/green]\n[dim]{res.stdout}[/dim]")
                subprocess.run([sys.executable, "-m", "pip", "install", "-e", "."], cwd=repo_path, capture_output=True)
                self.console.print("[bold cyan]🚀 Please restart OllamaCode to apply changes.[/bold cyan]")
                sys.exit(0)
        except Exception as e:
            self.console.print(f"[red]❌ Update failed: {e}[/red]")

    def run(self):
        self.setup()
        self.console.print("\n[dim italic]💡 Tip: Ask 'List files in this folder' or use '/clear' to reset chat.[/dim italic]\n")
        
        while True:
            cpu, ram, disk = self.get_system_stats()
            rprint(f"[dim]CPU %{cpu} | RAM %{ram} | {self.cwd}[/dim]")
            user_input = Prompt.ask("[bold green]OllamaCode >[/bold green]")
            
            if user_input.lower() in ['q', 'exit', 'quit', '/quit']:
                self.console.print("[bold red]OllamaCode is shutting down. Goodbye![/bold red]")
                break
            
            if user_input.lower() == "update" or user_input.lower() == "/update":
                self.update_self()
                continue
            
            if user_input.lower() in ['/clear', 'clear']:
                self.console.clear()
                self.history = []
                continue

            self.history.append({"role": "user", "content": user_input})

            while True:
                with Progress(SpinnerColumn(), TextColumn(f"[cyan]{self.model} is thinking...[/cyan]"), transient=True) as progress:
                    progress.add_task("", total=None)
                    answer = self.ask_ai()
                
                self.console.print(Panel(Markdown(answer), title="🤖 OllamaCode", border_style="cyan"))
                
                commands = re.findall(r'```(?:bash|sh|shell)\n(.*?)```', answer, re.DOTALL | re.IGNORECASE)
                
                if not commands:
                    break
                
                any_executed = False
                for cmd in commands:
                    cmd = cmd.strip()
                    if not cmd: continue
                    
                    self.console.print(Panel(f"[bold cyan]Action Needed:[/bold cyan]\n[white]{cmd}[/white]", border_style="yellow", title="⚡ Pending Command"))
                    
                    if Confirm.ask("[bold yellow]Execute this command?[/bold yellow]"):
                        any_executed = True
                        stdout, _ = self.execute_command(cmd)
                        
                        result_msg = f"Command output:\n{stdout}"
                        self.history.append({"role": "user", "content": result_msg})
                    else:
                        break
                
                if not any_executed:
                    break

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "update":
        agent = OllamaCodeAgent()
        agent.update_self()
        return
    agent = OllamaCodeAgent()
    agent.run()

if __name__ == "__main__":
    main()
