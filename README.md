# Forge

<p align="center">
  <img src="assets/icon.png" width="256" alt="Forge">
</p>

<p align="center">
  Lightweight coding agent for local and hosted LLM workflows.
</p>

Forge provides a simple CLI, persistent sessions, workspace-aware tools, and support for multiple model providers.

## Why Forge?

Forge focuses on:

- Provider independence
- Transparent tool execution
- Local-first workflows
- Lightweight architecture
- Hackability

It aims to provide a simple alternative to larger coding assistants while remaining easy to understand and extend.

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
- Tool execution tracking
- Approval mode for potentially destructive actions

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
approval_mode = true
```

## Architecture

```text
CLI
 ↓
Runtime
 ↓
Provider
 ├── Ollama
 └── Gemini

Runtime
 ↓
Tools
 ├── read_file
 ├── write_file
 ├── search_in_files
 ├── run_command
 └── ...

Runtime
 ↓
SQLite
 ├── sessions
 ├── messages
 ├── model_calls
 └── tool_calls
```

## Safety

Forge requires confirmation before executing potentially destructive actions.

Protected tools:

- write_file
- replace_in_file
- run_command

Example:

```text
Tool approval required: write_file
Approve? (y/N):
```

Approval mode can be enabled or disabled:

```bash
forge approval true
forge approval false
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

### Session tracking

Model usage:

```bash
forge usage SESSION_ID
```

Tool execution history:

```bash
forge tools SESSION_ID
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

## Example

```bash
forge agent \
  "Create a basic CMake project and build it"
```

Forge will:

1. Create the required files
2. Ask for approval before modifying files
3. Execute build commands
4. Report the result

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
- Commands are executed on the host system.
- Full sandboxing is not implemented.

## Roadmap

- Session summaries
- Tool call search
- OpenRouter provider
- MCP integration
- Project-specific prompts

## License

MIT
