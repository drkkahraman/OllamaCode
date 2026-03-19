# OllamaCode 1.1.1

A modular and high-performance AI Terminal Assistant that connects to Groq Cloud and Ollama Local to help you execute shell commands, analyze your system, and automate tasks.

## Features

- **Modular Architecture**: Rebuilt as a Python package for better maintainability and scalability.
- **Improved Security**: Configuration settings now use obfuscation for API keys.
- **Advanced Context Management**: Intelligent history clipping based on word count to prevent token overflow.
- **Robust Error Handling**: Comprehensive exception management for more stable autonomous runs.
- **Multi-Provider**: Use blazing fast models from Groq or private local models via Ollama.
- **Autonomous Agent**: Features Auto-Run and Auto-Fix modes with intelligent loop detection.
- **PTY Terminal Emulation**: Full interactive support for commands like sudo, ssh, and custom scripts.
- **Hardware Aware**: Monitoring of CPU, RAM, and Disk stats with resilience for Termux.
- **Smart Updates**: Self-update system that checks for changes before downloading.

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
   
4. **Update OllamaCode**:
   ```bash
   ollamacode update
   ```

5. **Settings & Configuration**:
   ```bash
   ollamacode settings
   ```

## Configuration

OllamaCode will guide you through a setup wizard on its first run. Settings are saved securely in `~/.ollamacode_settings.json`.

## Technical Improvements in v1.2.0

- Transitioned from a single 257-line file to a modular package structure.
- Replaced silent error absorption (except: pass) with proper traceback reporting and handled exceptions.
- Added session history clipping (4000-word limit) to avoid AI context window crashes.
- Implemented Base64 obfuscation for stored API keys to improve basic security.

## Dependencies

- requests
- psutil
- python-dotenv
- rich
