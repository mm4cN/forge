# Forge
<p align="center">
  <img src="assets/icon.png" width="256" alt="Forge">
</p>

<p align="center">
  Lightweight coding agent for local and hosted LLM workflows.
</p>

It provides a simple CLI, persistent sessions, workspace-aware tools, and support for multiple model providers.

## Features

- Multiple model providers
  - Ollama
  - Gemini
- Persistent SQLite-backed sessions
- Agent and non-agent execution modes
- Interactive chat sessions
- Workspace-aware tool execution
- File and code search
- File reading and writing
- Text replacement inside files
- Shell command execution
- Git status and diff inspection
- Model usage tracking

## Requirements

- Python 3.11+

Recommended tools:

```bash
fd
rg
```

## Installation

```bash
git clone https://github.com/mm4cN/forge.git
cd forge

python -m venv .venv
source .venv/bin/activate

pip install -e .
```

### Ollama

Install and start Ollama:

```bash
ollama serve
```

Pull a model:

```bash
ollama pull qwen2.5-coder:7b
```

### Gemini

Export your API key:

```bash
export GEMINI_AUTH_KEY="..."
```

## Configuration

Forge stores its state under:

```text
~/.forge/
```

Example configuration:

```toml
provider = "ollama"
default_model = "qwen2.5-coder:7b"
ollama_url = "http://127.0.0.1:11434"
```

## Usage

### Simple model call

Single request without tool execution:

```bash
forge ask "Explain RAII in C++"
```

### Agent mode

Run the tool-enabled agent loop:

```bash
forge agent "Find run_agent and explain how tool execution works"
```

### Interactive chat

```bash
forge chat
```

Resume an existing session:

```bash
forge chat --session SESSION_ID
```

### Model management

```bash
forge model list
forge model get

forge model use ollama qwen2.5-coder:7b
forge model use gemini gemini-2.5-flash
```

### Usage tracking

```bash
forge usage SESSION_ID
```

### Workspace tools

```bash
forge ls
forge find runtime
forge search run_agent
forge cat src/forge/runtime.py
```

### Git helpers

```bash
forge status
forge diff
```

## Agent Capabilities

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

- Tool-calling quality depends on the selected model.
- Some models are better suited for agent workflows than others.
- Command approval and sandboxing are not implemented yet.

## Roadmap

- Session summaries
- Tool call analytics
- Safer command execution
- MCP integration
- Project-specific prompts

## License

MIT
