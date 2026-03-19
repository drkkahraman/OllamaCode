# OllamaCode 1.1.1

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

![Kooha-2026-03-19-14-48-08](https://github.com/user-attachments/assets/214678ac-4eb0-4ebf-8a24-0f00d266763c)

   ```bash
   ollamacode
   ```
   
4. **Update OllamaCode**:
   ```bash
   ollamacode update
   ```

5. **Settings & Configuration**:

![Kooha-2026-03-19-14-46-01](https://github.com/user-attachments/assets/24dfe48e-7a20-4312-a890-cc11cdc5cf51)

   ```bash
   ollamacode settings
   ```

## Configuration

OllamaCode will guide you through a setup wizard on its first run to select your preferred AI provider (Groq or Ollama), model, custom URL (for local models), and autonomous behavior settings. Your settings are securely saved in `~/.ollamacode_settings.json`.

## Error Correction (Auto-Fix)

When enabled, OllamaCode automatically analyzes terminal errors and suggest corrections. It uses the feedback from the command output to iteratively find the right solution.

## Loop Detection

To ensure safety in autonomous modes, the agent detects if it is repeating the same command with the same outcome and will automatically halt the process to prevent infinite loops.

## Dependencies

- requests
- psutil
- python-dotenv
- rich
