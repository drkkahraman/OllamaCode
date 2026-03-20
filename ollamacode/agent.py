import requests
import re
from .utils import get_system_context

class OllamaCodeAgent:
    def __init__(self, settings):
        self.settings = settings
        self.history = []
        self.groq_url = "https://api.groq.com/openai/v1/chat/completions"

    def clip_history(self, max_words=4000):
        total_words = 0
        clipped = []
        for msg in reversed(self.history):
            words = len(msg['content'].split())
            if total_words + words > max_words: break
            clipped.insert(0, msg)
            total_words += words
        self.history = clipped

    def ask_ai(self, cwd):
        from .utils import list_installed_plugins
        plugins = list_installed_plugins()
        plugin_info = f"Available Plugins: {', '.join(plugins)}. To run a plugin, use: ````ollamacode run <plugin_name> <args> ````" if plugins else ""
        system_msg = (
            "You are 'OllamaCode', an autonomous terminal agent. "
            f"Context: {get_system_context(cwd)} "
            f"{plugin_info} "
            "Coding Tools: Use 'ollamacode tree' to see files, 'ollamacode cat-file <file>' to read with line numbers, and 'ollamacode write-file <file> <content>' to write code. "
            "Suggest bash commands in ```bash ... ``` blocks. "
            "If the task is complete, STOP."
        )
        self.clip_history()
        messages = [{"role": "system", "content": system_msg}] + self.history

        try:
            if self.settings["provider"] == "Groq":
                headers = {"Authorization": f"Bearer {self.settings['api_key']}", "Content-Type": "application/json"}
                response = requests.post(self.groq_url, headers=headers, json={"messages": messages, "model": self.settings["model"]}, timeout=30)
                if response.status_code == 200: return response.json()['choices'][0]['message']['content']
            else:
                response = requests.post(f"{self.settings['ollama_url']}/api/chat", json={"model": self.settings["model"], "messages": messages, "stream": False}, timeout=150)
                if response.status_code == 200: return response.json()['message']['content']
            return f"Error: {response.status_code}"
        except Exception as e: return f"Connection Error: {str(e)}"

    def get_commands(self, answer):
        return re.findall(r'```(?:bash|sh|shell)\n(.*?)```', str(answer), re.DOTALL | re.IGNORECASE)
