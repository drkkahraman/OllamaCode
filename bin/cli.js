#!/usr/bin/env node
import { Command } from 'commander';
import chalk from 'chalk';
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
    if (forceSetup || (!settings.api_key && settings.provider === 'Groq')) {
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
                message: chalk.magenta('OllamaCode') + chalk.dim(' >')
            }]);

            if (['q', 'exit', 'quit'].includes(user_input.toLowerCase())) {
                console.log(chalk.dim('\n👋 Goodbye!\n'));
                break;
            }
            if (user_input.toLowerCase() === 'clear') {
                console.clear();
                showStatus(settings);
                agent.history = [];
                continue;
            }

            agent.history.push({ role: "user", content: user_input });
            let recentActions = [];

            while (true) {
                const spinner = ora({
                    text: `${chalk.dim(settings.model)} thinking...`,
                    color: 'cyan'
                }).start();
                const answer = await agent.askAi(cwd);
                spinner.stop();

                console.log(`\n${chalk.magenta('OllamaCode')}\n${marked(answer)}`);
                agent.history.push({ role: "assistant", content: answer });

                const cmds = agent.getCommands(answer);
                if (!cmds || cmds.length === 0) break;

                let anyExecuted = false;
                for (const cmd of cmds) {
                    console.log(`  ${chalk.magenta('●')} ${chalk.bold.white(cmd)}`);
                    
                    let execute = settings.auto_run;
                    if (!execute) {
                        const { confirm } = await inquirer.prompt([{
                            type: 'confirm',
                            name: 'confirm',
                            message: chalk.dim('  Execute?'),
                            default: true
                        }]);
                        execute = confirm;
                    }

                    if (execute) {
                        anyExecuted = true;
                        const result = await executeCommand(cmd, cwd);
                        cwd = result.newCwd;
                        
                        if (result.stdout) {
                            console.log(chalk.dim(result.stdout.split('\n').map(l => `    ${l}`).join('\n')));
                        }

                        if (recentActions.some(a => a.cmd === cmd && a.stdout === result.stdout)) {
                            console.log(`  ${chalk.red('⚠ Loop detected! Skipping iterative fix.')}`);
                            break;
                        }
                        
                        recentActions.push({ cmd, stdout: result.stdout });
                        agent.history.push({ role: "user", content: `Output (status ${result.status}):\n${result.stdout}` });

                        if (result.status !== 0 && settings.auto_fix) {
                            console.log(`  ${chalk.red('✖ Failed (code ' + result.status + '). Asking for fix...')}`);
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
            console.error(`\n${chalk.bold.red('Error:')} ${e.message}\n`);
            break;
        }
    }
}

program.name('ollamacode').description('AI-Powered Autonomous Terminal Agent').version('1.2.2');
program.command('settings').action(() => runAgent(true));
program.action(() => runAgent());
program.parse();
