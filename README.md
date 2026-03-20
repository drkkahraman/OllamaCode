# OllamaCode 1.1.7

A high performance AI Terminal Assistant that connects to Groq Cloud and Ollama Local to help you execute shell commands, analyze your system, and automate tasks.

## Key Features

- **Dual Provider Support**: Seamlessly switch between Groq (Cloud) and Ollama (Local) models.
- **Autonomous Operations**: Enable auto-run and auto-fix to let the AI solve complex terminal tasks for you.
- **Cross-Platform Compatibility**: Works on Linux, macOS, and Windows with both Python and Node.js environments.
- **Plugin Architecture**: Easily extend capabilities by adding custom Python (.py) or JavaScript (.js) plugins.
- **Advanced Coding Assistant**: Built-in tools for the AI to navigate projects, read files with line numbers, and write code accurately.
- **Resource Monitoring**: Real-time system stats (CPU, RAM) displayed directly in your terminal.
- **Secure Configuration**: Settings and API keys are stored locally and never shared.

## Complete Feature List

OllamaCode is designed to be the ultimate developer companion:
1. **Interactive Shell**: Natural language interface for your terminal.
2. **Auto-Pilot**: Enable `auto-run` to let the AI execute commands autonomously.
3. **Auto-Heal**: Enable `auto-fix` to let the AI fix terminal errors on its own.
4. **Context-Aware**: Automatically includes OS and current directory information in every request.
5. **Project Insight**: Uses specialized tools to see your code and project structure.

## Quick Start

### Installation

---

1. **Clone the repository**:
   ```bash
   git clone https://github.com/drkkahraman/OllamaCode.git
   cd OllamaCode
   ```

2. **Install the package**:
   ```bash
   pip install -e .
   ```

3. **Run OllamaCode**:
   ```bash
   ollamacode
   ```

---

## NPM Installation (via GitHub)

```bash
npm install -g github:drkkahraman/OllamaCode
```
![Kooha-2026-03-20-00-06-48](https://github.com/user-attachments/assets/ebffb402-6dd9-463b-ae2c-cfecc0b4145c)

```bash
ollamacode
```

---

## Configuration

OllamaCode will guide you through a setup wizard on its first run to select your preferred AI provider (Groq or Ollama), model, custom URL (for local models), and autonomous behavior settings. Your settings are securely saved in `~/.ollamacode_settings.json`.

## Error Correction (Auto-Fix)

When enabled, OllamaCode automatically analyzes terminal errors and suggest corrections. It uses the feedback from the command output to iteratively find the right solution.

## Loop Detection

To ensure safety in autonomous modes, the agent detects if it is repeating the same command with the same outcome and will automatically halt the process to prevent infinite loops.

## Plugins

OllamaCode supports custom plugins to extend its functionality.

### Adding a Plugin
Python plugins (.py):
```bash
ollamacode add plugin /path/to/plugin.py
```

Node.js plugins (.js):
```bash
ollamacode add plugin /path/to/plugin.js
```

### Listing Plugins
```bash
ollamacode plugins
```

### Running a Plugin
```bash
ollamacode run <plugin_name> [args]
```

### How to Create a Plugin

A plugin is simply a script (Python or Node.js) that can take arguments from the command line.

**Python Plugin Example (`hello.py`):**
```python
import sys
if __name__ == "__main__":
    name = sys.argv[1] if len(sys.argv) > 1 else "World"
    print(f"Hello from Plugin: {name}")
```

**Node.js Plugin Example (`hello.js`):**
```javascript
const name = process.argv[2] || "World";
console.log(`Hello from Node Plugin: ${name}`);
```

After creating your script, add it using:
```bash
ollamacode add plugin path/to/your_script.py
```
OllamaCode will then automatically list it as an available tool during your AI sessions.

### Coding Tools

To make code development easier, OllamaCode provides built-in utilities for the AI:
- `ollamacode tree`: Displays the project structure.
- `ollamacode cat-file <file>`: Reads a file with line numbers for precise reference.
- `ollamacode write-file <file> "<content>"`: Quickly writes or overwrites code files.

### Why these tools?
- **Better Context**: The AI can see all your files using `tree`, so it doesn't get lost.
- **Precise Editing**: By using `cat-file`, the AI sees line numbers, allowing it to give you perfect instructions for specific lines.
- **Fast Automation**: The `write-file` command allows the AI to generate entire modules for you in a single step.

## CLI Reference

- `ollamacode`: Launches the main AI assistant.
- `ollamacode settings`: Opens the configuration wizard to change models or providers.
- `ollamacode update`: Automatically pulls the latest version and updates dependencies.
- `ollamacode plugins`: Displays all currently installed plugins.
- `ollamacode add plugin <path>`: Registers a new plugin for use.
- `ollamacode run <name> [args]`: Executes a specific plugin.
- `ollamacode tree`: Shows the current directory structure (max-depth 2).
- `ollamacode cat-file <file>`: Displays file content with line numbers.
- `ollamacode write-file <file> <content>`: Writes content to a specified file.

## Dependencies

- requests
- psutil
- rich
- commander (JS)
- inquirer (JS)
- chalk (JS)
- boxen (JS)
- ora (JS)
- marked (JS)
- marked-terminal (JS)
