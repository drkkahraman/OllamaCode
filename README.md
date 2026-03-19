# OllamaCoder 1.2.3

A high performance AI Terminal Assistant that connects to Groq Cloud and Ollama Local to help you execute shell commands, analyze your system, and automate tasks. This project supports both **Node.js (NPM)** and **Python**.

## Node.js Installation (NPM)

1. **Install the package globally**:
   ```bash
   npm install -g ollamacoder
   ```

2. **Run OllamaCoder**:
   ```bash
   ollamacoder
   ```

---

## Python Installation

1. **Install via pip**:
   ```bash
   git clone https://github.com/drkkahraman/OllamaCoder.git
   cd OllamaCoder
   pip install -e .
   ```

2. **Run Python version**:
   ```bash
   python3 -m ollamacode
   ```

---

## Configuration

OllamaCoder will guide you through a setup wizard on its first run to select your preferred AI provider (Groq or Ollama), model, custom URL (for local models), and autonomous behavior settings. Your settings are securely saved in `~/.ollamacode_settings.json`.

## Error Correction (Auto-Fix)

When enabled, OllamaCoder automatically analyzes terminal errors and suggest corrections. It uses the feedback from the command output to iteratively find the right solution.

## Loop Detection

To ensure safety in autonomous modes, the agent detects if it is repeating the same command with the same outcome and will automatically halt the process to prevent infinite loops.

## Dependencies (NPM)

- axios
- systeminformation
- commander
- inquirer
- chalk
- boxen
- ora
- marked
- marked-terminal

## Dependencies (Python)

- requests
- psutil
- rich
