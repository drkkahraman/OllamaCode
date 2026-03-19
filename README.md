# OllamaCode 1.1.5

A high performance AI Terminal Assistant that connects to Groq Cloud and Ollama Local to help you execute shell commands, analyze your system, and automate tasks.

## Quick Start

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
