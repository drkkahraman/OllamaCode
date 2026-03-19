#!/usr/bin/env node
import { Command } from 'commander';
import chalk from 'chalk';
import boxen from 'boxen';
import inquirer from 'inquirer';
import ora from 'ora';
import { marked } from 'marked';
import { markedTerminal } from 'marked-terminal';
import { loadSettings, saveSettings } from '../lib/config.js';
import { getSystemStats, checkUpdate } from '../lib/utils.js';
import { setupWizard, showStatus, showStats } from '../lib/ui.js';
import { executeCommand } from '../lib/terminal.js';
import { OllamaCodeAgent } from '../lib/agent.js';

marked.use(markedTerminal());

const program = new Command();

async function runAgent(forceSetup = false) {
    let settings = loadSettings();
    if (forceSetup || !settings.api_key && settings.provider === 'Groq') {
        settings = await setupWizard(settings);
        saveSettings(settings);
    }

    showStatus(settings);
    const agent = new OllamaCodeAgent(settings);
    let cwd = process.cwd();

    while (true) {
        try {
            const stats = await getSystemStats();
            showStats(stats, cwd);
            
            const { user_input } = await inquirer.prompt([{
                type: 'input',
                name: 'user_input',
                message: chalk.bold.green('OllamaCode >')
            }]);

            if (['q', 'exit', 'quit'].includes(user_input.toLowerCase())) break;
            if (user_input.toLowerCase() === 'clear') {
                console.clear();
                agent.history = [];
                continue;
            }

            agent.history.push({ role: "user", content: user_input });
            let recentActions = [];

            while (true) {
                const spinner = ora(`${chalk.cyan(settings.model)} thinking...`).start();
                const answer = await agent.askAi(cwd);
                spinner.stop();

                console.log(boxen(marked(answer), { title: '🤖 OllamaCode', borderColor: 'cyan', padding: 1 }));
                agent.history.push({ role: "assistant", content: answer });

                const cmds = agent.getCommands(answer);
                if (!cmds || cmds.length === 0) break;

                let anyExecuted = false;
                for (const cmd of cmds) {
                    console.log(boxen(`Action:\n${chalk.yellow(cmd)}`, { borderStyle: 'single', borderColor: 'yellow' }));
                    
                    let execute = settings.auto_run;
                    if (!execute) {
                        const { confirm } = await inquirer.prompt([{
                            type: 'confirm',
                            name: 'confirm',
                            message: 'Execute?',
                            default: true
                        }]);
                        execute = confirm;
                    }

                    if (execute) {
                        anyExecuted = true;
                        const result = executeCommand(cmd, cwd);
                        cwd = result.newCwd;
                        
                        if (recentActions.some(a => a.cmd === cmd && a.stdout === result.stdout)) {
                            console.log(chalk.red('Loop detected!'));
                            break;
                        }
                        
                        recentActions.push({ cmd, stdout: result.stdout });
                        agent.history.push({ role: "user", content: `Output (status ${result.status}):\n${result.stdout}` });

                        if (result.status !== 0 && settings.auto_fix) {
                            agent.history.push({ role: "user", content: "Previous command failed. Fix it." });
                            break;
                        }
                    } else {
                        break;
                    }
                }
                if (!anyExecuted) break;
            }
        } catch (e) {
            console.error(chalk.bold.red('Fatal Error:'), e.stack);
            break;
        }
    }
}

program
    .name('ollamacode')
    .description('AI-Powered Autonomous Terminal Agent')
    .version('1.2.3');

program
    .command('update')
    .action(async () => {
        const { local, remote, error } = await checkUpdate(process.cwd());
        if (error) { console.error(chalk.red(error)); return; }
        if (local === remote) { console.log(chalk.green('Already up to date.')); return; }
        console.log(chalk.yellow('Update available. Run git pull.'));
    });

program
    .command('plugins')
    .action(async () => {
        const os = await import('os');
        const fs = await import('fs');
        const path = await import('path');
        const pluginDir = path.join(os.homedir(), '.ollamacode', 'plugins');
        if (!fs.existsSync(pluginDir)) fs.mkdirSync(pluginDir, { recursive: true });
        const plugins = fs.readdirSync(pluginDir).filter(f => f.endsWith('.js'));
        console.log(boxen(plugins.join('\n') || 'No plugins found', { title: 'Plugins', borderColor: 'blue', padding: 1 }));
    });

program
    .command('add <type> [path]')
    .action(async (type, pluginPath) => {
        if (type === 'plugin') {
            const os = await import('os');
            const fs = await import('fs');
            const path = await import('path');
            if (!pluginPath || !fs.existsSync(pluginPath)) { console.log(chalk.red('File not found')); return; }
            const pluginDir = path.join(os.homedir(), '.ollamacode', 'plugins');
            if (!fs.existsSync(pluginDir)) fs.mkdirSync(pluginDir, { recursive: true });
            fs.copyFileSync(pluginPath, path.join(pluginDir, path.basename(pluginPath)));
            console.log(chalk.green(`Added plugin: ${path.basename(pluginPath)}`));
        }
    });

program
    .command('settings')
    .action(() => runAgent(true));

program
    .action(() => runAgent());

program.parse();
