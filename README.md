# OllamaCode 1.0.3

A high-performance AI Terminal Assistant that connects to **Groq Cloud** and **Ollama Local** to help you execute shell commands, analyze your system, and automate tasks.



https://github.com/user-attachments/assets/11be32ea-8771-4bb4-b4e9-ab9b8f362a53



## Features

- **Multi-Provider**: Use blazing fast models from Groq or private local models via Ollama.
- **Agentic Loop**: Feedback loops for terminal command execution and error correction.
- **Hardware Aware**: Monitors CPU, RAM, and Disk stats in real-time.
- **Beautiful UI**: Powered by `rich` for stylish tables, panels, and markdown.

## Quick Start

1. **Clone the repository**:
   ```bash
   git clone https://github.com/drkkahraman/OllamaCode.git
   cd ollamacode
   ```

2. **Install the package**:
   ```bash
   pip install .
   ```

3. **Run OllamaCode**:
   ```bash
   ollamacode
   ```
   
4. **Update OllamaCode**:
   ```bash
   ollamacode update
   ```

## Configuration

OllamaCode will guide you through a setup wizard on its first run to select your preferred AI provider (Groq or Ollama) and model. Your settings are saved locally in `ollamacode_settings.json`.

## Dependencies

- `requests`
- `psutil`
- `python-dotenv`
- `rich`
