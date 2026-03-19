import inquirer from 'inquirer';
import boxen from 'boxen';
import chalk from 'chalk';
import { listOllamaModels, listGroqModels } from './utils.js';

export async function setupWizard(settings) {
    const questions = [
        {
            type: 'list',
            name: 'provider',
            message: 'Select AI Provider:',
            choices: ['Groq', 'Ollama'],
            default: settings.provider
        },
        {
            type: 'input',
            name: 'api_key',
            message: 'Enter Groq API Key:',
            when: (answers) => answers.provider === 'Groq',
            default: settings.api_key
        },
        {
            type: 'input',
            name: 'ollama_url',
            message: 'Enter Ollama URL:',
            when: (answers) => answers.provider === 'Ollama',
            default: settings.ollama_url
        }
    ];

    const answers = await inquirer.prompt(questions);
    
    let models = [];
    if (answers.provider === 'Groq') {
        models = await listGroqModels(answers.api_key);
    } else {
        models = await listOllamaModels(answers.ollama_url);
    }

    const modelQuestion = {
        type: 'list',
        name: 'model',
        message: 'Select Model:',
        choices: models.map(m => ({ name: `${m.id} (${m.family})`, value: m.id }))
    };

    const modelAnswer = await inquirer.prompt([modelQuestion]);
    
    const moreQuestions = [
        {
            type: 'confirm',
            name: 'auto_run',
            message: 'Auto-run commands?',
            default: settings.auto_run
        },
        {
            type: 'confirm',
            name: 'auto_fix',
            message: 'Auto-fix errors?',
            default: settings.auto_fix
        }
    ];

    const finalAnswers = await inquirer.prompt(moreQuestions);

    return { ...settings, ...answers, ...modelAnswer, ...finalAnswers };
}

export function showStatus(settings) {
    const content = `Provider: ${chalk.cyan(settings.provider)}\nModel: ${chalk.green(settings.model)}\nAuto-Run: ${settings.auto_run ? chalk.green('ON') : chalk.red('OFF')}\nAuto-Fix: ${settings.auto_fix ? chalk.green('ON') : chalk.red('OFF')}`;
    console.log(boxen(content, { title: 'Configuration', padding: 1, borderStyle: 'double', borderColor: 'blue' }));
}

export function showStats(stats, cwd) {
    const text = `📁 ${chalk.yellow(cwd)} | CPU: ${chalk.blue(stats.cpu + '%')} | RAM: ${chalk.magenta(stats.ram + '%')} | Disk: ${chalk.cyan(stats.disk + '%')}`;
    console.log(`\n${text}`);
}
