import os from 'os';
import axios from 'axios';
import si from 'systeminformation';
import { execSync } from 'child_process';

export async function getSystemStats() {
    try {
        const cpu = await si.currentLoad();
        const ram = await si.mem();
        const disk = await si.fsSize();
        return {
            cpu: cpu.currentLoad.toFixed(1),
            ram: ((ram.used / ram.total) * 100).toFixed(1),
            disk: disk[0].use.toFixed(1)
        };
    } catch (e) {
        return { cpu: 0, ram: 0, disk: 0 };
    }
}

export function getSystemContext(cwd) {
    const osInfo = `${os.type()} ${os.release()}`;
    return `Operating System: ${osInfo}\nCurrent Directory: ${cwd}`;
}

export async function listOllamaModels(ollamaUrl) {
    try {
        const response = await axios.get(`${ollamaUrl}/api/tags`, { timeout: 5000 });
        if (response.status === 200) {
            return response.data.models.map(m => ({
                id: m.name,
                family: m.details?.family || 'N/A'
            }));
        }
    } catch (e) {}
    return [];
}

export async function listGroqModels(apiKey) {
    if (!apiKey) return [{ id: "llama-3.3-70b-versatile", family: "Llama 3.3" }];
    try {
        const url = "https://api.groq.com/openai/v1/models";
        const response = await axios.get(url, {
            headers: { Authorization: `Bearer ${apiKey}` },
            timeout: 5000
        });
        if (response.status === 200) {
            const data = response.data.data;
            const refined = [];
            for (const m of data) {
                const id = m.id.toLowerCase();
                if (['llama', 'qwen', 'mixtral', 'gemma'].some(x => id.includes(x))) {
                    const family = id.includes('llama') ? 'Llama' : id.includes('qwen') ? 'Qwen' : id.includes('mixtral') ? 'Mixtral' : id.includes('gemma') ? 'Gemma' : 'N/A';
                    refined.push({ id: m.id, family });
                }
            }
            return refined;
        }
    } catch (e) {}
    return [{ id: "llama-3.3-70b-versatile", family: "Llama 3.3" }];
}

export async function listInstalledPlugins() {
    const os = await import('os');
    const fs = await import('fs');
    const path = await import('path');
    const pluginDir = path.join(os.homedir(), '.ollamacode', 'plugins');
    if (!fs.existsSync(pluginDir)) return [];
    return fs.readdirSync(pluginDir).filter(f => f.endsWith('.js') || f.endsWith('.py'));
}

export async function checkUpdate(repoPath) {
    try {
        execSync('git fetch origin main', { cwd: repoPath, stdio: 'ignore' });
        const local = execSync('git rev-parse HEAD', { cwd: repoPath }).toString().trim();
        const remote = execSync('git rev-parse origin/main', { cwd: repoPath }).toString().trim();
        return { local, remote, error: null };
    } catch (e) {
        return { local: null, remote: null, error: e.message };
    }
}
