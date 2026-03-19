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
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import print as rprint
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt, Confirm

load_dotenv()

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "ollamacode_settings.json")

class OllamaCode:
    def __init__(self):
        self.console = Console()
        self.provider = "Groq"
        self.api_key = os.getenv("GROQ_API_KEY", "")
        self.model = "llama-3.3-70b-versatile"
        self.history = []
        self.ollama_url = "http://localhost:11434"
        self.groq_url = "https://api.groq.com/openai/v1/chat/completions"
        self.cwd = os.getcwd()
        self.load_settings()

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

    def get_detailed_system_info(self):
        try:
            mem = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            cpu_freq = psutil.cpu_freq()
            
            info = [
                f"OS: {platform.system()} {platform.release()} ({platform.machine()})",
                f"CPU: {platform.processor()} ({psutil.cpu_count(logical=True)} cores)",
                f"Memory: {round(mem.total / (1024**3), 1)}GB Total ({round(mem.available / (1024**3), 1)}GB Free)",
                f"Disk: {round(disk.total / (1024**3), 1)}GB Total ({round(disk.free / (1024**3), 1)}GB Free)"
            ]
            return " | ".join(info)
        except:
            return "System info unavailable"

    def list_ollama_models(self):
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                return [m['name'] for m in response.json().get('models', [])]
        except:
            return []
        return []

    def list_groq_models(self):
        if not self.api_key: return ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"]
        try:
            url = "https://api.groq.com/openai/v1/models"
            response = requests.get(url, headers={"Authorization": f"Bearer {self.api_key}"}, timeout=5)
            if response.status_code == 200:
                return [m['id'] for m in response.json().get('data', []) if any(x in m['id'].lower() for x in ['llama', 'qwen', 'mixtral'])]
        except:
            pass
        return ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"]

    def setup(self):
        if os.path.exists(CONFIG_FILE):
            self.console.print(Panel(f"[bold green]Saved Configuration Found:[/bold green]\nProvider: [cyan]{self.provider}[/cyan]\nModel: [yellow]{self.model}[/yellow]", border_style="blue"))
            if not Confirm.ask("Do you want to change these settings?", default=False):
                return

        self.console.clear()
        self.console.print(Panel("[bold cyan]OLLAMACODE v3.0[/bold cyan]\n[dim]High-Performance AI Terminal Assistant[/dim]", style="bold white on blue", expand=False))
        
        provider_table = Table(show_header=True, header_style="bold magenta", border_style="blue")
        provider_table.add_column("ID", justify="center", style="bold cyan")
        provider_table.add_column("Provider", style="bold green")
        provider_table.add_column("Description", style="white")
        provider_table.add_row("1", "Groq Cloud", "Super-fast Llama/Qwen models (API Key required)")
        provider_table.add_row("2", "Ollama Local", "Privacy-focused, runs on your own hardware")
        
        self.console.print(provider_table)
        choice = Prompt.ask("Select your choice", choices=["1", "2"], default="1" if self.provider == "Groq" else "2")
        self.provider = "Groq" if choice == "1" else "Ollama"
        
        if self.provider == "Groq":
            if not self.api_key or "gsk_" not in self.api_key:
                self.api_key = Prompt.ask("Enter Groq API Key (gsk_...)")
            else:
                masked = f"{self.api_key[:8]}...{self.api_key[-4:]}"
                if not Confirm.ask(f"Use existing API key ({masked})?", default=True):
                    self.api_key = Prompt.ask("Enter new Groq API Key")

        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as progress:
            progress.add_task(f"Fetching {self.provider} models...", total=None)
            models = self.list_groq_models() if self.provider == "Groq" else self.list_ollama_models()

        if not models:
            self.model = Prompt.ask("No models found. Enter model name manually", default="llama3")
        else:
            self.model = Prompt.ask("Select model", choices=models, default=self.model if self.model in models else models[0])

        self.save_settings()
        self.console.print(f"\n[bold green]Settings Saved![/bold green] Ready to use [cyan]{self.provider}[/cyan] with [yellow]{self.model}[/yellow].\n")

    def ask_ai(self, prompt):
        sys_info = self.get_detailed_system_info()
        sys_msg = (
            f"You are 'OllamaCode', an expert autonomous AI terminal agent.\n"
            f"SYSTEM CONTEXT: {sys_info} | Current Path: {self.cwd}\n"
            "Suggest terminal commands inside ```bash ... ``` blocks for execution.\n"
            "Be precise and always assume you have sudo privileges if needed (but warn the user)."
        )
        
        messages = [{"role": "system", "content": sys_msg}] + self.history + [{"role": "user", "content": prompt}]

        try:
            if self.provider == "Groq":
                headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
                response = requests.post(self.groq_url, headers=headers, json={"messages": messages, "model": self.model}, timeout=20)
                if response.status_code == 200:
                    content = response.json()['choices'][0]['message']['content']
                else:
                    return f"Error: Groq returned {response.status_code} - {response.text}"
            else:
                response = requests.post(f"{self.ollama_url}/api/chat", json={"model": self.model, "messages": messages, "stream": False}, timeout=90)
                if response.status_code == 200:
                    content = response.json()['message']['content']
                else:
                    return f"Error: Ollama returned {response.status_code} - {response.text}"

            self.history.append({"role": "user", "content": prompt})
            self.history.append({"role": "assistant", "content": content})
            if len(self.history) > 20: self.history = self.history[-20:]
            return content

        except Exception as e:
            return f"Connection Failed: {str(e)}"

    def run(self):
        self.setup()
        while True:
            cpu, ram, disk = self.get_system_stats()
            rprint(f"[dim]Stats: CPU {cpu}% | RAM {ram}% | Disk {disk}% | {self.cwd}[/dim]")
            user_input = Prompt.ask("\n[bold green]OllamaCode >[/bold green]")
            
            if user_input.lower() in ['q', 'exit', 'quit']:
                self.console.print("[bold red]Shutting down OllamaCode. Goodbye![/bold red]")
                break

            with Progress(SpinnerColumn(), TextColumn(f"[cyan]{self.model} is analyzing...[/cyan]"), transient=True) as progress:
                progress.add_task("", total=None)
                answer = self.ask_ai(user_input)
            
            self.console.print(Panel(Markdown(answer), title=f"🤖 {self.model}", border_style="cyan"))
            
            commands = re.findall(r'```(?:bash|sh|shell)\n(.*?)```', answer, re.DOTALL | re.IGNORECASE)
            for cmd in commands:
                cmd = cmd.strip()
                if cmd:
                    self.console.print(Panel(f"[bold yellow]Suggested Action:[/bold yellow]\n{cmd}", border_style="yellow"))
                    if Confirm.ask("Execute this command?"):
                        if cmd.startswith("cd "):
                            try:
                                target = cmd.split(" ", 1)[1]
                                os.chdir(os.path.expanduser(target))
                                self.cwd = os.getcwd()
                                self.console.print(f"[bold blue]Directory changed to: {self.cwd}[/bold blue]")
                            except Exception as e:
                                self.console.print(f"[bold red]Failed to change directory: {e}[/bold red]")
                        else:
                            try:
                                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=self.cwd)
                                if result.stdout: self.console.print(Panel(result.stdout, title="Output", border_style="green"))
                                if result.stderr: self.console.print(Panel(result.stderr, title="Error Record", border_style="red"))
                            except Exception as e:
                                self.console.print(f"[bold red]Execution error: {e}[/bold red]")

def main():
    try:
        OllamaCode().run()
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)

if __name__ == "__main__":
    main()
