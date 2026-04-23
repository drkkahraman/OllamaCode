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
        plugin_info = f"Installed Plugins: {', '.join(plugins)}" if plugins else "No custom plugins installed."
        
        system_msg = (
            "# Role: OllamaCode v1.2.1\n"
            "You are an expert autonomous terminal agent. Your goal is to help the user with coding, debugging, and system administration tasks directly from the shell.\n\n"
            "## Context:\n"
            f"- Working Directory: {cwd}\n"
            f"- System Info: {get_system_context(cwd)}\n"
            f"- {plugin_info}\n\n"
            "## Capabilities:\n"
            "1. **Explore**: Use `ollamacode tree` to see the project structure.\n"
            "2. **Analyze**: Use `ollamacode cat-file <file_path>` to read files with line numbers.\n"
            "3. **Execute**: Suggest shell commands in ```bash ... ``` blocks.\n"
            "4. **Modify**: Use `ollamacode write-file <file_path> <content>` for surgical edits.\n"
            "5. **Plugins**: Run custom tools via `ollamacode run <plugin_name> [args]`.\n\n"
            "## Guidelines:\n"
            "- **Action-First**: NEVER just print code snippets. You MUST write them to files using `ollamacode write-file`.\n"
            "- **Command Blocks**: All actions MUST be wrapped in ```bash ... ``` blocks for automatic execution.\n"
            "- **Chaining**: Create directories with `mkdir`, enter them with `cd`, and then write files.\n"
            "- **Precision**: Strictly follow the user's requested names (folders/files).\n"
            "- **Be Brief**: Minimize explanations. Focus on executing the task.\n"
            "- If the task is finished, state \"Task complete.\""
        )
        self.clip_history()
        messages = [{"role": "system", "content": system_msg}] + self.history

        try:
            if self.settings["provider"] == "Groq":
                headers = {"Authorization": f"Bearer {self.settings['api_key']}", "Content-Type": "application/json"}
                response = requests.post(self.groq_url, headers=headers, json={"messages": messages, "model": self.settings["model"]}, timeout=30)
                if response.status_code == 200:
                    content = response.json()['choices'][0]['message']['content']
                    filtered = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL).strip()
                    return filtered if filtered else "I have analyzed the situation. Let me suggest a command."
            else:
                response = requests.post(f"{self.settings['ollama_url']}/api/chat", json={"model": self.settings["model"], "messages": messages, "stream": False}, timeout=150)
                if response.status_code == 200:
                    content = response.json()['message']['content']
                    filtered = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL).strip()
                    return filtered if filtered else "I have analyzed the situation. Let me suggest a command."
            return f"Error: {response.status_code}"
        except Exception as e: return f"Connection Error: {str(e)}"

    def get_commands(self, answer):
        return re.findall(r'```(?:bash|sh|shell)\n(.*?)```', str(answer), re.DOTALL | re.IGNORECASE)
