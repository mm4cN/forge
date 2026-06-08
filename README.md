# Forge

<p align="center">
  <img src="assets/icon.png" width="256" alt="Forge">
</p>

<p align="center">
  Lightweight coding agent for local and hosted LLM workflows.
</p>

Forge is a local-first coding assistant designed for developers who want transparent tool execution, persistent sessions, and full control over their workflow.

## Features

- Multiple providers
  - Ollama
  - Gemini
- Agent and non-agent modes
- Interactive chat sessions
- Persistent SQLite-backed history
- Workspace-aware tools
- File search and editing
- Shell command execution
- Git integration
- Code review command
- Model usage tracking
- Tool execution tracking
- Approval mode for destructive actions

## Installation

```bash
git clone https://github.com/mm4cN/forge.git
cd forge

python -m venv .venv
source .venv/bin/activate

pip install -e .
```

### Ollama

```bash
ollama serve
ollama pull qwen2.5-coder:7b
```

### Gemini

```bash
export GEMINI_AUTH_KEY="..."
```

## Quick Start

Ask a model:

```bash
forge ask "Explain RAII in C++"
```

Run the agent:

```bash
forge agent \
  "Create a basic CMake project and build it"
```

Interactive chat:

```bash
forge chat
```

Review current changes:

```bash
forge review
```

## Model Management

```bash
forge model list
forge model get

forge model use ollama qwen2.5-coder:7b
forge model use gemini gemini-2.5-flash
```

## Tracking

Model usage:

```bash
forge usage SESSION_ID
```

Tool execution history:

```bash
forge tools SESSION_ID
```

## Safety

Forge requires confirmation before executing potentially destructive actions.

Protected tools:

- write_file
- edit_file
- replace_in_file
- run_command

Example:

```text
Tool approval required: write_file
Approve? (y/N):
```

Enable or disable approval mode:

```bash
forge approval true
forge approval false
```

## Configuration

Forge stores its state under:

```text
~/.forge/
```

Example:

```toml
provider = "ollama"
default_model = "qwen2.5-coder:7b"
approval_mode = true
```

## Roadmap

- Project memory
- Approval diff preview
- OpenRouter provider
- Session summaries
- Context builder
- Neovim plugin

## License

MIT
