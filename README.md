# Forge

Forge is a lightweight local coding agent powered by Ollama.

The goal of the project is to provide a simple, hackable foundation for building agentic workflows around local language models without requiring cloud services.

## Features

Current capabilities:

- Local LLM integration through Ollama
- Persistent conversation sessions stored in SQLite
- Workspace-aware execution
- Tool-based agent runtime
- File creation and modification
- File reading
- Command execution
- Directory inspection

## Installation

Clone the repository:

```bash
git clone https://github.com/mm4cN/forge.git
cd forge
```

Create a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install Forge:

```bash
pip install -e .
```

Install and start Ollama:

```bash
ollama serve
```

Download a model:

```bash
ollama pull qwen2.5-coder:3b
```

## Usage

Ask a question:

```bash
forge ask "Create a hello world application in C++"
```

List sessions:

```bash
forge sessions
```

Show session history:

```bash
forge history SESSION_ID
```

Show configuration:

```bash
forge config
```

Show active workspace:

```bash
forge workspace
```

## Workspace

Forge operates inside the current working directory.

Example:

```bash
cd ~/Projects/my-project

forge ask "Create hello.cpp and compile it"
```

The active workspace becomes:

```text
~/Projects/my-project
```

Tools are restricted to this workspace.

## Current Tools

### list_directory

Lists files and directories.

### read_file

Reads a file from the workspace.

### write_file

Creates or updates a file.

### run_command

Executes a shell command inside the workspace.

## Configuration

Forge stores its configuration in:

```text
~/.forge/
├── config.toml
├── forge.db
├── logs/
└── sessions/
```

## Roadmap

Planned features:

- Interactive chat mode
- Git integration
- File search
- Workspace indexing
- MCP integration
- Multi-model support
- Tool execution history
- Project-specific prompts

