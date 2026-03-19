import os
import json
import base64

CONFIG_FILE = os.path.join(os.path.expanduser("~"), ".ollamacode_settings.json")

def load_settings():
    defaults = {
        "provider": "Groq",
        "api_key": "",
        "model": "llama-3.3-70b-versatile",
        "auto_run": False,
        "auto_fix": False,
        "ollama_url": "http://localhost:11434"
    }
    if not os.path.exists(CONFIG_FILE): return defaults
    try:
        with open(CONFIG_FILE, 'r') as f:
            data = json.load(f)
            if "api_key" in data and data["api_key"]:
                try: data["api_key"] = base64.b64decode(data["api_key"].encode()).decode()
                except: pass
            return {**defaults, **data}
    except: return defaults

def save_settings(settings):
    try:
        data = settings.copy()
        if "api_key" in data and data["api_key"]:
            data["api_key"] = base64.b64encode(data["api_key"].encode()).decode()
        with open(CONFIG_FILE, 'w') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Error saving config: {e}")
