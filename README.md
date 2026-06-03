# Forge

Forge is a lightweight local coding agent powered by Ollama.

It is a small, hackable CLI for experimenting with local LLM-based coding workflows. Forge can chat with a local model, keep SQLite-backed sessions, inspect a workspace, read and write files, search through code, and execute shell commands.

## Features

Current capabilities:

- Local LLM integration through Ollama
- Persistent sessions stored in SQLite
- Workspace-aware tool execution
- Interactive chat mode
- One-shot prompt mode
- File and directory inspection
- File search using `fd` with fallback to `find`
- Text search using `rg` with fallback to `grep`
- File reading and writing
- Shell command execution inside the workspace

## Requirements

- Python 3.11+
- Ollama
- A local Ollama model, for example:

```bash
ollama pull qwen2.5-coder:7b
```

Optional but recommended:

```bash
fd
rg
```

Forge falls back to `find` and `grep` if they are not available.

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

Install Forge in editable mode:

```bash
pip install -e .
```

Start Ollama:

```bash
ollama serve
```

## Configuration

Forge creates its local state under:

```text
~/.forge/
├── config.toml
├── forge.db
├── logs/
└── sessions/
```

Example `~/.forge/config.toml`:

```toml
ollama_url = "http://127.0.0.1:11434"
default_model = "qwen2.5-coder:7b"
```

## Usage

### Ask once

```bash
forge ask "Create a hello.cpp file and compile it with clang++"
```

### Interactive chat

```bash
forge chat
```

Resume an existing session:

```bash
forge chat --session SESSION_ID
```

### Sessions

List sessions:

```bash
forge sessions
```

Show session history:

```bash
forge history SESSION_ID
```

### Workspace

Forge uses the current working directory as the active workspace.

```bash
cd ~/Projects/my-project
forge workspace
```

All file tools are restricted to the workspace.

## Direct CLI Tools

Forge also exposes its tools directly, which is useful for debugging and daily use.

### List files

```bash
forge ls
forge ls src/forge
```

### Find files

```bash
forge find runtime
forge find "*.py"
```

### Search in files

```bash
forge search run_agent
forge search "class MyType"
```

### Read a file

```bash
forge cat src/forge/runtime.py
```

## Agent Tools

The agent runtime can use these tools:

### `list_directory`

Lists files and directories inside the workspace.

### `find_files`

Finds files by name or glob-like pattern.

Uses:

- `fd` if available
- `find` as fallback

### `search_in_files`

Searches text inside files.

Uses:

- `rg` if available
- `grep` as fallback

### `read_file`

Reads a file from the workspace.

### `write_file`

Creates or updates a file inside the workspace.

### `run_command`

Executes a shell command inside the workspace.

## Current Limitations

Forge is experimental.

Known limitations:

- Tool calling quality depends heavily on the selected local model.
- Small models may describe actions instead of using tools.
- Tool execution history is not yet stored separately.
- There is no approval system for shell commands yet.
- Long sessions may eventually exceed useful context size.

## Recommended Model

For 16 GB RAM machines, a practical starting point is:

```bash
ollama pull qwen2.5-coder:7b
```

Smaller model:

```bash
ollama pull qwen2.5-coder:3b
```

The 3B model is faster, but weaker for agentic workflows.

## Roadmap

Planned or likely next steps:

- Better interactive chat UX
- Git tools: `git_status`, `git_diff`
- Safer command execution policy
- Tool call logging
- Session summaries
- Project-specific prompts
- MCP integration
- Configurable model profiles

## License

MIT License
