import inquirer from 'inquirer';
import chalk from 'chalk';
import { listOllamaModels, listGroqModels } from './utils.js';

export async function setupWizard(settings) {
    console.log(`\n${chalk.magenta('OllamaCode Setup Wizard')}\n`);
    
    const questions = [
        {
            type: 'list',
            name: 'provider',
            message: 'Select AI Provider',
            choices: [
                { name: chalk.yellow('Groq ') + chalk.dim('(Fast Cloud)'), value: 'Groq' },
                { name: chalk.blue('Ollama ') + chalk.dim('(Local)'), value: 'Ollama' }
            ],
            default: settings.provider
        },
        {
            type: 'input',
            name: 'api_key',
            message: 'Enter Groq API Key',
            when: (answers) => answers.provider === 'Groq',
            default: settings.api_key
        },
        {
            type: 'input',
            name: 'ollama_url',
            message: 'Enter Ollama URL',
            when: (answers) => answers.provider === 'Ollama',
            default: settings.ollama_url || 'http://localhost:11434'
        }
    ];

    const answers = await inquirer.prompt(questions);
    
    let models = [];
    try {
        if (answers.provider === 'Groq') {
            models = await listGroqModels(answers.api_key);
        } else {
            models = await listOllamaModels(answers.ollama_url);
        }
    } catch (e) {
        console.log(chalk.red('! Could not fetch models. Manual entry required.'));
        models = [{ id: 'llama3', family: 'default' }];
    }

    const { model } = await inquirer.prompt([{
        type: 'list',
        name: 'model',
        message: 'Select Model',
        choices: models.map(m => ({ name: `${m.id} ${chalk.dim(`(${m.family})`)}`, value: m.id }))
    }]);
    
    const { auto_run, auto_fix } = await inquirer.prompt([
        { type: 'confirm', name: 'auto_run', message: 'Enable Auto-Run?', default: false },
        { type: 'confirm', name: 'auto_fix', message: 'Enable Auto-Fix?', default: true }
    ]);

    return { ...settings, ...answers, model, auto_run, auto_fix };
}

export function showStatus(settings) {
    const p = chalk.bold.magenta('OllamaCode v1.3');
    const model = chalk.yellow(settings.model);
    const provider = chalk.dim(`via ${settings.provider}`);
    const flags = [
        settings.auto_run ? chalk.green('● Auto-Run') : chalk.dim('○ Auto-Run'),
        settings.auto_fix ? chalk.green('● Auto-Fix') : chalk.dim('○ Auto-Fix')
    ].join(' ');

    console.log(`\n${p} ${chalk.dim('—')} ${model} ${provider}\n${flags}\n`);
}

export function showStats(stats, cwd) {
    const path = chalk.cyan(cwd.replace(process.env.HOME, '~'));
    const cpu = stats.cpu > 50 ? chalk.red(`${stats.cpu}%`) : chalk.green(`${stats.cpu}%`);
    const ram = stats.ram > 70 ? chalk.red(`${stats.ram}%`) : chalk.blue(`${stats.ram}%`);
    
    process.stdout.write(`\r${chalk.dim('📁')} ${path} ${chalk.dim('|')} ${chalk.dim('CPU:')} ${cpu} ${chalk.dim('RAM:')} ${ram}  `);
}
