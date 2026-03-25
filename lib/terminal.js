import { spawn } from 'child_process';
import os from 'os';
import fs from 'fs';

let currentProcess = null;

export function killCurrentCommand() {
    if (currentProcess) {
        currentProcess.kill('SIGKILL');
        currentProcess = null;
    }
}

export function executeCommand(cmd, cwd = process.cwd()) {
    return new Promise((resolve) => {
        if (cmd.startsWith('cd ')) {
            const newDir = cmd.slice(3).trim().replace(/^['"]|['"]$/g, '');
            const targetDir = newDir === '~' ? os.homedir() : newDir.startsWith('/') ? newDir : `${cwd}/${newDir}`;
            if (fs.existsSync(targetDir)) {
                resolve({ status: 0, stdout: `Changed directory to ${targetDir}`, newCwd: targetDir });
            } else {
                resolve({ status: 1, stdout: `Directory not found: ${targetDir}`, newCwd: cwd });
            }
            return;
        }

        const [command, ...args] = cmd.split(' ');
        const child = spawn(command, args, { cwd, shell: true });
        currentProcess = child;

        let stdout = '';
        let stderr = '';

        child.stdout.on('data', (data) => {
            stdout += data.toString();
        });

        child.stderr.on('data', (data) => {
            stderr += data.toString();
        });

        child.on('close', (code) => {
            currentProcess = null;
            if (code === 0) {
                resolve({ status: 0, stdout: stdout.trim(), newCwd: cwd });
            } else {
                resolve({ status: code, stdout: (stderr || stdout).trim(), newCwd: cwd });
            }
        });

        child.on('error', (err) => {
            currentProcess = null;
            resolve({ status: 1, stdout: err.message, newCwd: cwd });
        });
    });
}
