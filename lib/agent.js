import axios from 'axios';
import { getSystemContext } from './utils.js';

export class OllamaCodeAgent {
    constructor(settings) {
        this.settings = settings;
        this.history = [];
        this.groqUrl = "https://api.groq.com/openai/v1/chat/completions";
    }

    clipHistory(maxWords = 4000) {
        let totalWords = 0;
        let clipped = [];
        for (let i = this.history.length - 1; i >= 0; i--) {
            const msg = this.history[i];
            const words = msg.content.split(/\s+/).length;
            if (totalWords + words > maxWords) break;
            clipped.unshift(msg);
            totalWords += words;
        }
        this.history = clipped;
    }

    async askAi(cwd) {
        const { listInstalledPlugins } = await import('./utils.js');
        const plugins = await listInstalledPlugins();
        const pluginInfo = plugins.length > 0 ? `Installed Plugins: ${plugins.join(', ')}` : "No custom plugins installed.";
        
        const systemMsg = `
# Role: OllamaCode v1.2.1
You are an expert autonomous terminal agent. Your goal is to help the user with coding, debugging, and system administration tasks directly from the shell.

## Context:
- Working Directory: ${cwd}
- System Info: ${getSystemContext(cwd)}
- ${pluginInfo}

## Capabilities:
1. **Explore**: Use \`ollamacode tree\` to see the project structure.
2. **Analyze**: Use \`ollamacode cat-file <file_path>\` to read files with line numbers.
3. **Execute**: Suggest shell commands in \`\`\`bash ... \`\`\` blocks.
4. **Modify**: Use \`ollamacode write-file <file_path> <content>\` for surgical edits.
5. **Plugins**: Run custom tools via \`ollamacode run <plugin_name> [args]\`.

## Guidelines:
- **Action-First**: NEVER just print code. You MUST write it to a file using \`ollamacode write-file\`.
- **Command Blocks**: All commands MUST be inside \`\`\`bash ... \`\`\` blocks to be executed.
- **Step-by-Step**: If a folder is requested, 1. \`mkdir <name>\`, 2. \`cd <name>\`, 3. \`ollamacode write-file ...\`.
- **Precision**: Use the exact folder/file names requested by the user.
- **Be Brief**: Minimize talk. Execute first, explain only if necessary.
- If the task is finished, state "Task complete."
`.trim();
        this.clipHistory();
        const messages = [{ role: "system", content: systemMsg }, ...this.history];

        try {
            if (this.settings.provider === "Groq") {
                const response = await axios.post(this.groqUrl, {
                    messages,
                    model: this.settings.model
                }, {
                    headers: {
                        Authorization: `Bearer ${this.settings.api_key}`,
                        'Content-Type': 'application/json'
                    },
                    timeout: 30000
                });
                let content = response.data.choices[0].message.content;
                let filtered = content.replace(/<think>[\s\S]*?<\/think>/gi, '').trim();
                return filtered || "I have analyzed the situation. Let me suggest a command.";
            } else {
                const response = await axios.post(`${this.settings.ollama_url}/api/chat`, {
                    messages,
                    model: this.settings.model,
                    stream: false
                }, { timeout: 150000 });
                let content = response.data.message.content;
                let filtered = content.replace(/<think>[\s\S]*?<\/think>/gi, '').trim();
                return filtered || "I have analyzed the situation. Let me suggest a command.";
            }
        } catch (e) {
            return `Connection Error: ${e.response?.data?.error?.message || e.message}`;
        }
    }

    getCommands(answer) {
        const matches = [...answer.matchAll(/```(?:bash|sh|shell)\n([\s\S]*?)```/gi)];
        return matches.map(m => m[1].trim());
    }
}
