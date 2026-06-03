# Forge

Forge is a lightweight local coding agent powered by Ollama.

It provides a simple CLI for experimenting with local LLM-powered coding workflows, workspace-aware tools, and persistent chat sessions.

## Features

- Local LLM integration through Ollama
- Persistent SQLite-backed sessions
- Interactive chat mode
- Workspace-aware file operations
- File search and content search
- File reading and writing
- Shell command execution
- Git status and diff inspection

## Requirements

- Python 3.11+
- Ollama

Recommended tools:

```bash
fd
rg
```

Recommended model:

```bash
ollama pull qwen2.5-coder:7b
```

## Installation

```bash
git clone https://github.com/mm4cN/forge.git
cd forge

python -m venv .venv
source .venv/bin/activate

pip install -e .

ollama serve
```

## Configuration

Forge stores its data under:

```text
~/.forge/
```

Example:

```toml
ollama_url = "http://127.0.0.1:11434"
default_model = "qwen2.5-coder:7b"
```

## Usage

Interactive chat:

```bash
forge chat
```

Resume session:

```bash
forge chat --session SESSION_ID
```

One-shot prompt:

```bash
forge ask "Create a hello world application in C++"
```

Useful commands:

```bash
forge ls
forge find runtime
forge search run_agent
forge cat src/forge/runtime.py

forge status
forge diff
```

## Current Capabilities

The agent can:

- Inspect directories
- Find files
- Search file contents
- Read files
- Write files
- Replace text in files
- Execute shell commands
- Inspect Git status and diffs

## Limitations

- Tool usage quality depends on the selected model.
- Small models may describe actions instead of executing tools.
- Command execution approval is not implemented yet.

## Roadmap

- Safer command execution
- Tool call logging
- Session summaries
- MCP integration
- Project-specific prompts

## License

MIT
