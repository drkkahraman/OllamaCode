# OllamaCode 1.3


## Overview

OllamaCode is a AI Terminal Assistant designed for modern developers who demand speed, autonomy, and local-first intelligence. By bridging the gap between high-speed cloud inference (via Groq Cloud) and privacy-respecting local models (with Ollama), OllamaCode transforms your terminal into a self repairing, autonomous engineering environment.

Whether you are debugging complex legacy systems, generating boilerplate code, or automating repetitive terminal workflows, OllamaCode provides the cognitive layer your shell has been missing.

---

## Competitive Analysis: OllamaCode vs The Market

In the rapidly evolving landscape of AI-powered developer tools, OllamaCode occupies a unique niche by prioritizing high-speed inference and local autonomy. Below is a detailed comparison with other major players in the field

### Comparison

| Feature | OllamaCode | Aider | OpenDevin | Copilot CLI |
| :--- | :--- | :--- | :--- | :--- |
| **Primary Interface** | Terminal (CLI) | Terminal (CLI) | Web-based / IDE | Terminal (CLI) |
| **Local Model Support** | Native (Ollama) | Via LiteLLM | Native (Docker) | None |
| **Inference Speed** | Extreme (Groq) | Standard (API) | Standard (API) | Standard (API) |
| **Autonomous Operation**| Built-in (Auto-Fix) | Limited | Full (Agentic) | Minimal |
| **Plugin System** | Native (Python/JS) | Minimal | Extensive | None |
| **Resource Monitoring**| Built-in | None | Minimal | None |
| **Privacy Focus** | Local-First | Hybrid | Hybrid | Cloud-Only |

### OllamaCode vs. Aider
Aider is a powerful tool for pair programming, but it often requires complex configuration to use local models via LiteLLM. OllamaCode provides a direct, zero-config integration with Ollama, making it the superior choice for developers who prioritize local-only data processing without the overhead of additional proxies.

### OllamaCode vs. OpenDevin
OpenDevin is a full agentic system that usually runs inside Docker containers. While highly capable, it is often "too heavy" for quick terminal tasks. OllamaCode provides a lightweight, "instant-on" experience that integrates directly with your existing shell environment without the need for containerization or complex virtual networking.

### OllamaCode vs. GitHub Copilot CLI
Copilot CLI is primarily a tool for suggesting shell commands based on natural language. It lacks the ability to read your project structure, analyze system resource usage, or autonomously fix errors through iterative loops. OllamaCode is a full-fledged agent capable of complex reasoning, not just command suggestion.

---

## Technical Architecture

OllamaCode is built on a modular, dual-stack architecture that ensures consistency across Python and Node.js environments.

### Core Components

1. **The Intelligence Router**: 
   This module handles the logic for switching between Groq and Ollama. It manages the formatting of prompts and ensures that the agent follows the system instructions regardless of the model size or provider.

2. **The Execution Engine (Terminal Wrapper)**:
   A secure layer that executes shell commands. It captures STDOUT and STDERR independently, monitors execution time, and passes results back to the agent for analysis.

3. **Context Management System**:
   Dynamically injects system information (OS version, CPU usage, RAM availability) and project context (file tree, current file content) into each request to ensure the AI has situational awareness.

4. **Self-Healing Loop**:
   A deterministic state machine that triggers when a command returns a non-zero exit code. It guides the AI to analyze the error and propose a surgical fix rather than a broad, destructive change.

---

## Key Features in Detail

### 1. Dual-Provider Intelligence
- Groq Cloud Integration: Leverage Llama-3, Mixtral, and Gemma models at blazing ultra-low latency.
- Ollama Local Engine: Run private, local-only models (like DeepSeek-Coder, CodeLlama, or Qwen) without an internet connection.
- Dynamic Switching: Instantly toggle between local and cloud providers based on your privacy needs or performance requirements.

### 2. Autonomous "Auto-Pilot" Mode
- Self-Execution: Enable auto_run to let the AI execute its proposed shell commands automatically.
- Loop Prevention: Advanced algorithms detect repetitive command patterns and halt execution before infinite loops occur.
- Intelligent Feedback: The agent reads the standard output (STDOUT) and error (STDERR) of every command to verify success.

### 3. Self-Healing "Auto-Fix" System
- Error Analysis: When a command fails, OllamaCode automatically analyzes the exit code and error logs.
- Iterative Repair: The AI proposes and executes a fix, then checks again if the issue is resolved.
- Contextual Debugging: It looks at your environment, file structure, and history to find the most logical solution to developer errors (dependency issues, syntax errors, path conflicts, etc.).

### 4. Universal Plugin Architecture
- Language Agnostic: Extend the agent's capabilities using standard Python (.py) or Node.js (.js) scripts.
- Fast Registration: Simple one-command registration to make your custom tools instantly available to the AI.
- Standardized Execution: Arguments are passed seamlessly from the natural language interface to your custom logic.

### 5. Advanced Coding Utilities
- tree: Visualize your project structure instantly to provide the AI with a navigation map.
- cat-file: Read files with precise line numbers, allowing for surgical code edits and discussions.
- write-file: Create or overwrite entire modules with a single prompt, eliminating manual copy-pasting.

---

## Installation Guide

OllamaCode is truly cross-platform and supports both Python and Node.js environments.

### Python Installation (Recommended)

1. Clone the repository:
   ```bash
   git clone https://github.com/drkkahraman/OllamaCode.git
   cd OllamaCode
   ```

2. Install in editable mode:
   ```bash
   pip install -e .
   ```

3. Verify installation:
   ```bash
   ollamacode --version
   ```

### Node.js / NPM Installation

You can install OllamaCode globally to use it as a standalone CLI tool.

1. Install from GitHub:
   ```bash
   npm install -g github:drkkahraman/OllamaCode
   ```

2. Run the assistant:
   ```bash
   ollamacode
   ```

---

## Configuration & First Run

When you launch ollamacode for the first time, you will be guided through an interactive setup wizard.

### Step 1: Provider Selection
Choose between:
- Groq: Requires a free API key from [Groq Console](https://console.groq.com).
- Ollama: Requires [Ollama](https://ollama.com) installed and running locally on your machine.

### Step 2: Model Selection
- The wizard automatically fetches a list of available models from your chosen provider.
- Recommended for Groq: llama-3.3-70b-versatile or mixtral-8x7b-32768.
- Recommended for Ollama: deepseek-coder:6.7b, codellama, or llama3.

### Step 3: Global Settings
- Custom URL: If your Ollama server is on a different machine or port, specify it here (default: http://localhost:11434).
- Auto-Run: Toggle whether you want to confirm every command or let the AI run wild. (Default: Off for safety).
- Auto-Fix: Toggle autonomous error correction. (Default: On for maximum utility).

Your settings are saved securely in ~/.ollamacode_settings.json. You can re-run the wizard at any time using:
```bash
ollamacode settings
```

---

## Command Line Interface (CLI) Reference

| Command | Argument | Description |
| :--- | :--- | :--- |
| ollamacode | (None) | Starts the interactive AI terminal assistant. |
| ollamacode --version | (None) | Prints the current version (1.3). |
| ollamacode settings | (None) | Launches the interactive configuration wizard. |
| ollamacode update | (None) | Checks for updates and pulls the latest changes from Git. |
| ollamacode plugins | (None) | Lists all installed custom plugins. |
| ollamacode register | -f <script> | Registers a new Python or JS file as a plugin. |
| ollamacode add plugin | <path> | Alias for register. Copies the script to the plugin dir. |
| ollamacode run | <name> [args] | Executes a registered plugin with optional arguments. |
| ollamacode tree | (None) | Displays current directory structure (max-depth 2). |
| ollamacode cat-file | <file> | Prints file content with line numbers for reference. |
| ollamacode write-file| <file> "<txt>" | Writes content directly to a file. |

---

## The Plugin System: Developing Your Own Tools

OllamaCode is designed to be infinitely extensible. A plugin is essentially any executable script that can be triggered by the AI.

### Creating a Python Plugin

Create a file named system_info.py:
```python
import sys
import os
import platform

def main():
    print(f"OS: {platform.system()} {platform.release()}")
    print(f"Python: {sys.version.split()[0]}")
    print(f"Current Directory: {os.getcwd()}")

if __name__ == "__main__":
    main()
```

### Registering and Running

1. Register it:
   ```bash
   ollamacode register -f system_info.py
   ```

2. Run it via the CLI:
   ```bash
   ollamacode run system_info
   ```

3. AI Integration:
   Once registered, the AI assistant is aware of your new plugin and may choose to use it if you ask questions related to its functionality!

---

## Security & Enterprise Features

OllamaCode is built with a security-first mindset, focusing on local data integrity and transparent operations.

### Air-Gapped Environments
For enterprises working with sensitive proprietary code, OllamaCode can be used in fully air-gapped environments by utilizing the Ollama local provider. No telemetry is sent, and all interactions remain within the corporate firewall.

### Permission Control
Unlike some agents that run in the background with unrestricted root access, OllamaCode operates within your current user privileges. Every command is logged, and (unless auto_run is enabled) every action requires explicit human confirmation.

### Credential Handling
Sensitive API keys (like Groq keys) are stored locally and are never embedded in logs or shared across the network. The configuration file is kept in the user's home directory with restrictive permissions.

---

## FAQ (Frequently Asked Questions)

**Q: Is it safe to use auto_run?**
A: We recommend keeping it Off unless you are in a controlled directory or a container. The AI can theoretically run any command, including rm -rf.

**Q: How do I change the theme?**
A: OllamaCode uses the rich library for Python and chalk for JS. It will inherit your terminal's color palette but uses standard ANSI colors for maximum compatibility.

**Q: Why is Ollama slow on my machine?**
A: Ollama performance depends entirely on your GPU and RAM. For best results, use models like mistral or phi3 on machines with limited resources. Use Groq for lightning fast speeds if privacy is not a concern.

**Q: Can I use multiple Groq API keys?**
A: Currently, only one key is supported per configuration. You can switch keys by running ollamacode settings.

---

## Roadmap

### Q2 2026
- [ ] Multi-Agent Mode: Orchestrate multiple models to work together on different parts of a project.
- [ ] RAG Execution: Index your entire codebase locally for even better context awareness.
- [ ] Web Search Integration: Allow the agent to search the web for the latest documentation.

### Q3 2026
- [ ] Native VS Code Extension: Bring the power of OllamaCode directly into your IDE.
- [ ] Advanced Visualization: Interactive maps and graphs of your system performance.

---

## Contributing

We love contributions! Whether you're fixing a bug, adding a feature, or writing better documentation.

1. Fork the repo.
2. Create your feature branch (git checkout -b feature/AmazingFeature).
3. Commit your changes (git commit -m 'Add some AmazingFeature').
4. Push to the branch (git push origin feature/AmazingFeature).
5. Open a Pull Request.

---

## License

Distributed under the MIT License. See LICENSE for more information.

---

## Support the Project

If you find OllamaCode useful, please consider giving it a Star on GitHub!

Author: [@drkkahraman](https://github.com/drkkahraman)

---

### Extended CLI Argument Breakdown and Use Cases

#### ollamacode run
The `run` command is a powerful abstraction that allows the AI to perform complex tasks by leveraging previously written scripts. 
Case Sample: You have a script that tests database connectivity. By registering it as a plugin, the AI can independently verify if a bug is caused by environmental issues or code logic.

#### ollamacode write-file
Unlike standard pipe operators, `write-file` ensures that formatting is preserved and handles internal white-space issues that often plague AI-generated code snippets in standard terminal environments.

---
