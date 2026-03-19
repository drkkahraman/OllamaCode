import { execSync } from 'child_process';
import os from 'os';

export function executeCommand(cmd, cwd = process.cwd()) {
    try {
        if (cmd.startsWith('cd ')) {
            const newDir = cmd.slice(3).trim().replace(/^['"]|['"]$/g, '');
            const targetDir = newDir === '~' ? os.homedir() : newDir.startsWith('/') ? newDir : `${cwd}/${newDir}`;
            if (fs.existsSync(targetDir)) {
                return { status: 0, stdout: `Changed directory to ${targetDir}`, newCwd: targetDir };
            }
        }

        const stdout = execSync(cmd, { cwd, encoding: 'utf-8', stdio: 'pipe' });
        return { status: 0, stdout: stdout.trim(), newCwd: cwd };
    } catch (e) {
        return { status: e.status || 1, stdout: (e.stderr || e.stdout || e.message).trim(), newCwd: cwd };
    }
}
