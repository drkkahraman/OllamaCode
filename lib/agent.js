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
        const pluginInfo = plugins.length > 0 ? `Available Plugins: ${plugins.join(', ')}. To run a plugin, use: \`\`\`ollamacode run <plugin_name> <args>\`\`\`` : "";
        const systemMsg = `You are 'OllamaCoder', an autonomous terminal agent. Context: ${getSystemContext(cwd)} ${pluginInfo} Coding Tools: Use 'ollamacode tree' to see files, 'ollamacode cat-file <file>' to read with line numbers, and 'ollamacode write-file <file> <content>' to write code. Suggest bash commands in \`\`\`bash ... \`\`\` blocks. If you are in the middle of a task, ALWAYS suggest a command. If the task is complete, STOP.`;
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
