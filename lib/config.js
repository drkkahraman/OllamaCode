import fs from 'fs';
import path from 'path';
import os from 'os';

const CONFIG_FILE = path.join(os.homedir(), '.ollamacode_settings.json');

export function loadSettings() {
    const defaults = {
        provider: "Groq",
        api_key: "",
        model: "llama-3.3-70b-versatile",
        auto_run: false,
        auto_fix: false,
        ollama_url: "http://localhost:11434"
    };

    if (!fs.existsSync(CONFIG_FILE)) return defaults;

    try {
        const data = JSON.parse(fs.readFileSync(CONFIG_FILE, 'utf-8'));
        if (data.api_key) {
            try {
                data.api_key = Buffer.from(data.api_key, 'base64').toString('utf-8');
            } catch (e) {}
        }
        return { ...defaults, ...data };
    } catch (e) {
        return defaults;
    }
}

export function saveSettings(settings) {
    try {
        const data = { ...settings };
        if (data.api_key) {
            data.api_key = Buffer.from(data.api_key).toString('base64');
        }
        fs.writeFileSync(CONFIG_FILE, JSON.stringify(data, null, 4));
    } catch (e) {
        console.error(`Error saving config: ${e.message}`);
    }
}
