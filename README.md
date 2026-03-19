# OllamaCode 1.0.4

A high-performance AI Terminal Assistant that connects to **Groq Cloud** and **Ollama Local** to help you execute shell commands, analyze your system, and automate tasks.

## Features

- **Multi-Provider**: Use blazing fast models from Groq or private local models via Ollama.
- **Autonomous Agent**: Features Auto-Run and Auto-Fix modes with intelligent loop detection.
- **PTY Terminal Emulation**: Full interactive support for commands like sudo (sh/bash).
- **Hardware Aware**: Monitors CPU, RAM, and Directory stats in real-time.
- **Modern UI**: Powered by `rich` for professional tables, panels, and markdown.

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

![Kooha-2026-03-19-14-48-08](https://github.com/user-attachments/assets/214678ac-4eb0-4ebf-8a24-0f00d266763c)

   ```bash
   ollamacode
   ```
   
5. **Update OllamaCode**:
   ```bash
   ollamacode update
   ```

6. **Settings & Configuration**:

![Kooha-2026-03-19-14-46-01](https://github.com/user-attachments/assets/24dfe48e-7a20-4312-a890-cc11cdc5cf51)

   ```bash
   ollamacode settings
   ```

## Configuration

OllamaCode will guide you through a setup wizard on its first run to select your preferred AI provider (Groq or Ollama), model, and autonomous behavior. Your settings are saved locally in `~/.ollamacode_settings.json`.

## Error Correction (Auto-Fix)

If a terminal command fails, OllamaCode can automatically analyze the output and suggest fixed commands. This behavior is configurable in the settings.

## Dependencies

- `requests`
- `psutil`
- `python-dotenv`
- `rich`
