# OllamaCode 1.1.5

[![PyPI version](https://img.shields.io/pypi/v/ollamacode.svg)](https://pypi.org/project/ollamacode/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

OllamaCode is a high-performance, autonomous AI Terminal Assistant. It bridges the gap between your terminal and powerful LLMs like Groq Cloud and Ollama Local, enabling you to execute shell commands, analyze system health, and automate complex workflows with ease.

---

## Key Features

- **Autonomous Agent**: Executes commands and iterates until the goal is reached.
- **Auto-Fix**: Automatically detects terminal errors and suggests/applies fixes.
- **Plugin System**: Extend functionality with custom Python (.py) or Node.js (.js) scripts.
- **System Insights**: Real-time monitoring of CPU, RAM, and directory context.
- **Loop Protection**: Built-in safety to detect and halt recursive command execution.
- **Dual Provider**: Seamlessly switch between local (Ollama) and cloud (Groq) models.

---

## Installation

### Via PyPI (Recommended)
```bash
pip install ollamacode
```

### From Source
```bash
git clone https://github.com/drkkahraman/OllamaCode.git
cd OllamaCode
pip install -e .
```

---

## Quick Start

Simply type the command to start the interactive session:
```bash
ollamacode
```

### First Run
On the first launch, a setup wizard will guide you through:
1. Choosing your AI provider (Groq or Ollama).
2. Selecting a model (e.g., llama3-70b, mixtral-8x7b).
3. Configuring Autonomous mode (Auto-run & Auto-fix).

Settings are stored in ~/.ollamacode_settings.json.

---

## Commands

| Command | Description |
| :--- | :--- |
| `ollamacode` | Start the AI assistant interactive mode. |
| `ollamacode settings` | Re-run the configuration wizard. |
| `ollamacode plugins` | List all installed plugins. |
| `ollamacode add plugin <path>` | Install a new plugin (.py or .js). |
| `ollamacode update` | Check for the latest version and update. |

---

## Plugins

OllamaCode is highly extensible. You can add custom scripts to automate specific tasks.

- **Python Plugins**: Place .py files in ~/.ollamacode/plugins/.
- **Node.js Plugins**: Place .js files in ~/.ollamacode/plugins/.

**Example: Adding a plugin**
```bash
ollamacode add plugin my_script.py
```

---

## Dependencies

- **Python**: requests, psutil, rich
- **Node.js**: commander, inquirer, chalk, boxen, ora, marked

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

Developed by [drkkahraman](https://github.com/drkkahraman)
