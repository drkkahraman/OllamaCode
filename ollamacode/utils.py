import os
import sys
import psutil
import subprocess
import platform
import requests

def get_system_stats():
    try:
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        disk = psutil.disk_usage('/').percent
        return cpu, ram, disk
    except: return None, None, None

def get_system_context(cwd):
    os_info = f"{platform.system()} {platform.release()}"
    return f"Operating System: {os_info}\nCurrent Directory: {cwd}"

def list_ollama_models(ollama_url):
    try:
        response = requests.get(f"{ollama_url}/api/tags", timeout=5)
        if response.status_code == 200:
            models_data = response.json().get('models', [])
            return [{"id": m['name'], "family": m.get('details', {}).get('family', 'N/A')} for m in models_data]
    except: return []
    return []

def list_groq_models(api_key):
    if not api_key: return [{"id": "llama-3.3-70b-versatile", "family": "Llama 3.3"}]
    try:
        url = "https://api.groq.com/openai/v1/models"
        response = requests.get(url, headers={"Authorization": f"Bearer {api_key}"}, timeout=5)
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

def list_installed_plugins():
    plugin_dir = os.path.join(os.path.expanduser("~"), ".ollamacode", "plugins")
    if not os.path.exists(plugin_dir): return []
    return [f for f in os.listdir(plugin_dir) if f.endswith('.py') or f.endswith('.js')]

def check_update(repo_path):
    if not os.path.exists(os.path.join(repo_path, ".git")): return None, None, "Not a git repository."
    try:
        subprocess.run(["git", "fetch", "origin", "main"], cwd=repo_path, capture_output=True)
        local_hash = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo_path, capture_output=True, text=True).stdout.strip()
        remote_hash = subprocess.run(["git", "rev-parse", "origin/main"], cwd=repo_path, capture_output=True, text=True).stdout.strip()
        return local_hash, remote_hash, None
    except Exception as e: return None, None, str(e)
